"""
mitigation/actions.py

Risk mitigation and easy-win identification.

The framework already produces signals (GREEN/AMBER/RED/BLACK) and
costs (cascade_burn, regeneration_required, reserve_drawdown_cost,
environment_loss). What was missing: a concrete answer to
"what should the firm actually do next period?"

This module computes that by examining real state:

  - which basin metrics are trending toward cliff (time_to_cliff small)
  - which secondary reserves are near or past their cliff
  - which tertiary pools are under pressure
  - where regeneration spend now would prevent disproportionate future
    cascade or environment loss

It ranks opportunities by LEVERAGE (future cost avoided per unit of
current cost) and URGENCY (time to cliff), not by absolute cost alone.
A cheap action that prevents a very expensive future cost is a better
easy win than an expensive action that prevents a slightly more
expensive future cost.

Output is INFORMATIONAL. It identifies the leverage points; it does
not make the decision. A firm's CFO or operations team still has to
weigh these against other priorities, available budget, and real-world
constraints the framework does not model.
"""

from dataclasses import dataclass, field
from math import isinf, isnan
from typing import Dict, List, Optional, Tuple

from basin_states.base import BasinState


# --- action tiers ---

# Easy wins are high-leverage / low-relative-cost / pre-cliff actions.
TIER_EASY_WIN = "easy_win"
# Urgent actions: at or near cliff, disproportionate cost to defer.
TIER_URGENT = "urgent"
# Systemic actions: tertiary or cumulative signals; landscape-scale.
TIER_SYSTEMIC = "systemic"
# Monitoring: not actionable yet, worth watching.
TIER_MONITORING = "monitoring"


@dataclass
class MitigationAction:
    """One identified mitigation opportunity.

    tier:          easy_win | urgent | systemic | monitoring
    target:        what the action addresses (e.g. "site_soil.carbon_fraction")
    description:   human-readable action summary
    leverage:      future cost avoided / current action cost
                   (>= 1 means worth doing on cost-benefit)
                   (higher = more leverage)
    urgency:       time units before the situation locks in
                   (low number = must act soon)
    estimated_action_cost:   xdu the action would cost this period
    estimated_avoided_cost:  xdu of future damage/drawdown/env-loss
                             avoided if action is taken
    reasons:       list of state-based reasons this action is suggested
    """
    tier: str
    target: str
    description: str
    leverage: float
    urgency: Optional[float]
    estimated_action_cost: float
    estimated_avoided_cost: float
    reasons: List[str] = field(default_factory=list)

    def is_actionable(self) -> bool:
        """Whether there is sufficient leverage AND time window."""
        if self.leverage < 1.0:
            return False
        if self.urgency is not None and self.urgency <= 0:
            # past the window — not preventable, only remediable
            return False
        return True


@dataclass
class MitigationReport:
    """Structured output covering easy wins, urgent actions, and systemic."""
    easy_wins: List[MitigationAction] = field(default_factory=list)
    urgent: List[MitigationAction] = field(default_factory=list)
    systemic: List[MitigationAction] = field(default_factory=list)
    monitoring: List[MitigationAction] = field(default_factory=list)
    summary: str = ""

    def total_actionable_leverage(self) -> float:
        """Sum of leverage ratios across all actionable items.
        A firm with total leverage of 10 has identified 10x-return
        preventive spend available this period."""
        total = 0.0
        for action in (self.easy_wins + self.urgent + self.systemic):
            if action.is_actionable() and not isinf(action.leverage):
                total += action.leverage
        return total

    def top_easy_wins(self, n: int = 3) -> List[MitigationAction]:
        return sorted(
            self.easy_wins,
            key=lambda a: (-a.leverage, a.urgency or float("inf")),
        )[:n]

    def top_urgent(self, n: int = 3) -> List[MitigationAction]:
        return sorted(
            self.urgent,
            key=lambda a: (a.urgency or float("inf"), -a.leverage),
        )[:n]

    def all_actions(self) -> List[MitigationAction]:
        return self.urgent + self.easy_wins + self.systemic + self.monitoring

    def as_text(self) -> str:
        lines = [f"Mitigation report: {self.summary}"]
        if self.urgent:
            lines.append("")
            lines.append(f"URGENT ({len(self.urgent)} items):")
            for a in self.top_urgent(5):
                urg = (f"{a.urgency:.2f} periods" if a.urgency is not None
                       else "no time estimate")
                lines.append(
                    f"  [{a.target}] leverage {a.leverage:.2f}x, "
                    f"urgency {urg}"
                )
                lines.append(f"    {a.description}")
        if self.easy_wins:
            lines.append("")
            lines.append(f"EASY WINS ({len(self.easy_wins)} items):")
            for a in self.top_easy_wins(5):
                lines.append(
                    f"  [{a.target}] leverage {a.leverage:.2f}x, "
                    f"cost {a.estimated_action_cost:.2f}, "
                    f"avoids {a.estimated_avoided_cost:.2f}"
                )
                lines.append(f"    {a.description}")
        if self.systemic:
            lines.append("")
            lines.append(f"SYSTEMIC ({len(self.systemic)} items):")
            for a in self.systemic[:5]:
                lines.append(
                    f"  [{a.target}] {a.description}"
                )
        if self.monitoring:
            lines.append("")
            lines.append(f"MONITORING ({len(self.monitoring)} items):")
            for a in self.monitoring[:3]:
                lines.append(f"  [{a.target}] {a.description}")
        return "\n".join(lines)


# --- core analysis functions ---

def _metric_urgency(basin: BasinState, key: str) -> Optional[float]:
    """Time until this metric crosses its cliff, given current trajectory.
    None if not trending toward cliff. Delegates to BasinState.time_to_cliff."""
    ttc = basin.time_to_cliff(key)
    if ttc is None or isnan(ttc):
        return None
    return ttc


def _reserve_depletion(reserves: Dict, basin_name: str, key: str) -> Optional[float]:
    """Fraction-remaining for a secondary reserve, or None if no reserve."""
    if reserves is None:
        return None
    basin_reserves = reserves.get(basin_name)
    if basin_reserves is None:
        return None
    reserve = basin_reserves.get(key)
    if reserve is None:
        return None
    return reserve.fraction_remaining()


def identify_basin_actions(
    basins: Dict[str, BasinState],
    secondary_reserves: Optional[Dict] = None,
    easy_win_leverage_min: float = 2.0,
    urgent_ttc_max: float = 5.0,
) -> List[MitigationAction]:
    """Scan basins for metrics where preventive action has leverage.

    For each metric with negative trajectory:
      - compute time_to_cliff (urgency)
      - compute fraction_remaining of secondary reserve (if available)
      - estimate action cost (proportional to current gap to full)
      - estimate avoided cost (proportional to proximity to cliff)
      - leverage = avoided / action

    Rank into tiers:
      urgent:   ttc <= urgent_ttc_max (short time window)
      easy_win: leverage >= easy_win_leverage_min AND ttc > urgent_ttc_max
      monitoring: small leverage or degrading slowly

    The cost estimates are in xdu and are first-order estimates, not
    engineering quotes. They provide ranking signal; real budgeting
    requires site-specific cost data.
    """
    actions: List[MitigationAction] = []

    for basin_name, basin in basins.items():
        for key in basin.state.keys():
            trajectory = basin.trajectory.get(key, 0.0)
            if trajectory >= 0:
                continue  # not degrading

            # urgency: time until cliff
            ttc = _metric_urgency(basin, key)
            if ttc is None:
                continue

            # current degradation fraction (0 healthy, 1 at cliff)
            frac = basin.fraction_remaining(key)
            if isnan(frac):
                continue

            # secondary reserve status (if we have it)
            reserve_frac = _reserve_depletion(
                secondary_reserves, basin_name, key
            )

            # cost estimates (first-order, in xdu)
            # action cost: addressing the negative trajectory.
            #   proportional to current trajectory magnitude.
            action_cost = max(abs(trajectory) * 10.0, 1.0)

            # avoided cost: if we don't act, damage accumulates.
            # scales with trajectory magnitude and inverse time to cliff
            # (closer to cliff = more leverage in acting now).
            if ttc > 0:
                avoided_cost = abs(trajectory) * 10.0 * (1.0 + 10.0 / ttc)
            else:
                avoided_cost = abs(trajectory) * 100.0

            # if the secondary reserve is also depleted, avoided cost
            # amplifies because there's no buffer to cushion cascade
            if reserve_frac is not None and reserve_frac < 0.5:
                avoided_cost *= 2.0

            leverage = (avoided_cost / action_cost
                        if action_cost > 0 else float("inf"))

            target = f"{basin_name}.{key}"
            reasons = [
                f"trajectory {trajectory:.4g}/period",
                f"fraction_remaining {frac:.2f}",
                f"time_to_cliff {ttc:.2f} periods",
            ]
            if reserve_frac is not None:
                reasons.append(
                    f"secondary reserve at {reserve_frac:.2f} of capacity"
                )

            if ttc <= urgent_ttc_max:
                tier = TIER_URGENT
                desc = (f"Cliff approach in {ttc:.1f} periods — "
                        "preventive action required now.")
            elif leverage >= easy_win_leverage_min:
                tier = TIER_EASY_WIN
                desc = (f"{leverage:.1f}x leverage: {action_cost:.2f} xdu "
                        f"action avoids ~{avoided_cost:.2f} xdu future cost.")
            else:
                tier = TIER_MONITORING
                desc = (f"Slow degradation, {leverage:.1f}x leverage. "
                        "Worth tracking but not yet actionable.")

            actions.append(MitigationAction(
                tier=tier,
                target=target,
                description=desc,
                leverage=leverage,
                urgency=ttc,
                estimated_action_cost=action_cost,
                estimated_avoided_cost=avoided_cost,
                reasons=reasons,
            ))

    return actions


def identify_reserve_actions(
    secondary_reserves: Optional[Dict] = None,
    tertiary_pools: Optional[Dict] = None,
    near_cliff_fraction: float = 0.3,
) -> List[MitigationAction]:
    """Scan reserves directly for pressure signals.

    Secondary reserves at or near cliff:
      urgent action to reduce stress or increase regen on that metric

    Tertiary pools at or near cliff:
      systemic action — no single-metric fix; calls for site-level
      intervention (reduced operations, landscape restoration,
      institutional reform depending on which pool)
    """
    actions: List[MitigationAction] = []

    if secondary_reserves:
        for basin_name, reserves in secondary_reserves.items():
            for key, reserve in reserves.items():
                frac = reserve.fraction_remaining()
                target = f"reserve:{basin_name}.{key}"
                if reserve.is_exhausted():
                    # past cliff — damage now flows directly to primary
                    actions.append(MitigationAction(
                        tier=TIER_URGENT,
                        target=target,
                        description=(
                            f"Secondary reserve EXHAUSTED "
                            f"({frac:.2f} of capacity). "
                            "Stress now flows directly to primary damage and "
                            "spreads to tertiary pools. Reduce stress "
                            "on this metric immediately."
                        ),
                        leverage=float("inf"),   # action prevents uncapped loss
                        urgency=0.0,              # already past
                        estimated_action_cost=abs(reserve.capacity) * 0.5,
                        estimated_avoided_cost=float("inf"),
                        reasons=[
                            f"reserve stock {reserve.stock:.2f}",
                            f"reserve cliff {reserve.cliff:.2f}",
                            f"fraction_remaining {frac:.3f}",
                        ],
                    ))
                elif frac < near_cliff_fraction:
                    # approaching cliff
                    actions.append(MitigationAction(
                        tier=TIER_URGENT,
                        target=target,
                        description=(
                            f"Secondary reserve near cliff "
                            f"({frac:.2f} of capacity). "
                            "Increase regeneration or reduce stress on this "
                            "metric to prevent full exhaustion."
                        ),
                        leverage=5.0,
                        urgency=frac * 10.0,  # rough estimate of periods left
                        estimated_action_cost=reserve.capacity * 0.2,
                        estimated_avoided_cost=reserve.capacity * 1.0,
                        reasons=[
                            f"fraction_remaining {frac:.3f} (cliff at "
                            f"{reserve.cliff/reserve.capacity:.2f})",
                        ],
                    ))

    if tertiary_pools:
        for name, pool in tertiary_pools.items():
            frac = pool.fraction_remaining()
            target = f"tertiary:{name}"
            if pool.past_cliff():
                actions.append(MitigationAction(
                    tier=TIER_SYSTEMIC,
                    target=target,
                    description=(
                        f"Tertiary pool PAST CLIFF "
                        f"({frac:.2f} of capacity). "
                        "Landscape-scale damage signature. Single-metric "
                        "actions are insufficient; site-level intervention "
                        "required (reduced operations, habitat restoration, "
                        "institutional change, or managed retreat "
                        "depending on pool type)."
                    ),
                    leverage=float("inf"),
                    urgency=0.0,
                    estimated_action_cost=pool.capacity * 0.8,
                    estimated_avoided_cost=float("inf"),
                    reasons=[
                        f"pool stock {pool.stock:.2f}",
                        f"pool cliff {pool.cliff:.2f}",
                        f"fraction_remaining {frac:.3f}",
                    ],
                ))
            elif frac < near_cliff_fraction:
                actions.append(MitigationAction(
                    tier=TIER_SYSTEMIC,
                    target=target,
                    description=(
                        f"Tertiary pool approaching cliff "
                        f"({frac:.2f} of capacity). "
                        "Begin site-level planning now; tertiary pools "
                        "respond slowly to intervention."
                    ),
                    leverage=8.0,
                    urgency=frac * 20.0,
                    estimated_action_cost=pool.capacity * 0.15,
                    estimated_avoided_cost=pool.capacity * 1.5,
                    reasons=[
                        f"fraction_remaining {frac:.3f}",
                    ],
                ))

    return actions


def build_mitigation_report(
    basins: Dict[str, BasinState],
    secondary_reserves: Optional[Dict] = None,
    tertiary_pools: Optional[Dict] = None,
    easy_win_leverage_min: float = 2.0,
    urgent_ttc_max: float = 5.0,
    near_cliff_fraction: float = 0.3,
) -> MitigationReport:
    """Build the full mitigation report.

    Inputs mirror what a Site already carries:
      basins: the basin dict from Site
      secondary_reserves: Site.secondary (optional)
      tertiary_pools: Site.tertiary (optional)

    Returns a MitigationReport with actions sorted into tiers.
    """
    basin_actions = identify_basin_actions(
        basins=basins,
        secondary_reserves=secondary_reserves,
        easy_win_leverage_min=easy_win_leverage_min,
        urgent_ttc_max=urgent_ttc_max,
    )
    reserve_actions = identify_reserve_actions(
        secondary_reserves=secondary_reserves,
        tertiary_pools=tertiary_pools,
        near_cliff_fraction=near_cliff_fraction,
    )

    report = MitigationReport()
    for a in basin_actions + reserve_actions:
        if a.tier == TIER_EASY_WIN:
            report.easy_wins.append(a)
        elif a.tier == TIER_URGENT:
            report.urgent.append(a)
        elif a.tier == TIER_SYSTEMIC:
            report.systemic.append(a)
        else:
            report.monitoring.append(a)

    # summary text
    parts = []
    if report.urgent:
        parts.append(f"{len(report.urgent)} urgent")
    if report.easy_wins:
        parts.append(f"{len(report.easy_wins)} easy wins")
    if report.systemic:
        parts.append(f"{len(report.systemic)} systemic")
    if report.monitoring:
        parts.append(f"{len(report.monitoring)} monitoring")
    report.summary = ("; ".join(parts)
                      if parts else "no actionable opportunities identified")

    return report
