"""
verdict/assess.py

Verdict layer.

Emits machine-readable judgments given the full state of basins, systems,
and accounting:

  - sustainable_yield_signal  GREEN / AMBER / RED / BLACK
  - basin_trajectory          aggregate direction
  - time_to_red               shortest time_to_cliff across all basins
  - forced_drawdown           what the PnL should show
  - regeneration_debt         accumulated underpayment

BLACK is reserved for irreversibility: at least one basin metric has
crossed a threshold that money cannot restore. A BLACK firm is not
merely losing money; it is destroying something unrecoverable.

Every verdict is reproducible from inputs. No hidden state.
"""

from dataclasses import dataclass, field
from math import inf, isinf
from typing import Dict, List, Optional

from basin_states.base import BasinState
from accounting.glucose import GlucoseFlow


@dataclass
class Verdict:
    sustainable_yield_signal: str              # GREEN | AMBER | RED | BLACK
    basin_trajectory: str                       # IMPROVING | STABLE | DEGRADING
    time_to_red: Optional[float]
    forced_drawdown: float
    regeneration_debt: float
    metabolic_profit: float
    reported_profit: float
    profit_gap: float
    # extraordinary-item treatment of irreversible environment loss
    # (SEEA-aligned; parallels GAAP impairment / GASB 42 extraordinary item)
    extraordinary_item_flagged: bool = False
    extraordinary_item_amount: float = 0.0
    metabolic_profit_with_loss: float = 0.0
    irreversible_metrics: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def basin_trajectory_verdict(basins: Dict[str, BasinState]) -> str:
    deg_count = 0
    reg_count = 0
    total_count = 0
    for basin in basins.values():
        for key, t in basin.trajectory.items():
            total_count += 1
            if t < 0:
                deg_count += 1
            elif t > 0:
                reg_count += 1
    if total_count == 0:
        return "STABLE"
    if deg_count > reg_count:
        return "DEGRADING"
    if reg_count > deg_count:
        return "IMPROVING"
    return "STABLE"


def min_time_to_red(basins: Dict[str, BasinState]) -> Optional[float]:
    best: Optional[float] = None
    for basin in basins.values():
        for key in basin.state.keys():
            ttf = basin.time_to_cliff(key)
            if ttf is None:
                continue
            if best is None or ttf < best:
                best = ttf
    return best


def yield_signal(flow: GlucoseFlow, ttr: Optional[float]) -> str:
    """GREEN / AMBER / RED / BLACK.

    BLACK  if any basin metric is irreversible.
    RED    if metabolic profit < 0, or ttr <= 1, or debt > reported profit.
    AMBER  if metabolic < half of reported, or ttr <= 5, or regen gap > 0.
    GREEN  otherwise.
    """
    if flow.has_irreversibility():
        return "BLACK"

    mp = flow.metabolic_profit()
    rp = flow.reported_profit()
    gap = flow.regeneration_gap()

    if mp < 0:
        return "RED"
    if ttr is not None and ttr <= 1.0:
        return "RED"
    if flow.regeneration_debt > max(rp, 1.0):
        return "RED"

    # AMBER checks — protect against degenerate comparisons with inf
    if rp > 0 and not isinf(mp) and mp < 0.5 * rp:
        return "AMBER"
    if ttr is not None and ttr <= 5.0:
        return "AMBER"
    if gap > 0:
        return "AMBER"
    return "GREEN"


def assess(
    basins: Dict[str, BasinState],
    flow: GlucoseFlow,
    extraordinary_revenue_threshold: float = 0.05,
    extraordinary_min_absolute: float = 0.0,
) -> Verdict:
    """Produce a verdict for this period.

    extraordinary_revenue_threshold: fraction of revenue above which
      environment loss is flagged as a material extraordinary item.
      Default 5% (standard GAAP materiality heuristic).
    extraordinary_min_absolute: lower bound on absolute environment
      loss regardless of revenue ratio. Useful when revenue is near
      zero or irrelevant.
    """
    traj = basin_trajectory_verdict(basins)
    ttr = min_time_to_red(basins)
    signal = yield_signal(flow, ttr)
    rp = flow.reported_profit()
    mp = flow.metabolic_profit()
    mp_full = flow.metabolic_profit_with_loss()

    if isinf(mp):
        profit_gap = inf
    else:
        profit_gap = rp - mp

    extraordinary_flagged = flow.is_extraordinary_loss_material(
        revenue_threshold=extraordinary_revenue_threshold,
        min_absolute=extraordinary_min_absolute,
    )

    warnings: List[str] = []
    # surface any registry configuration warnings first — these are
    # framework-configuration issues, not basin-state issues
    for w in flow.registry_warnings:
        warnings.append(f"[registry] {w}")

    # tertiary pools past cliff — landscape-scale damage
    if flow.tertiary_past_cliff:
        warnings.append(
            "TERTIARY PAST CLIFF: " + ", ".join(flow.tertiary_past_cliff) +
            " — site-shared reserves past recovery threshold; "
            "environment loss rate is now accelerated."
        )

    # exhausted secondary reserves — primary damage will accelerate
    if flow.exhausted_reserves:
        names = [f"{b}.{k}" for b, k in flow.exhausted_reserves]
        warnings.append(
            "EXHAUSTED RESERVES: " + ", ".join(names) +
            " — these metrics have no secondary buffer; stress now "
            "flows directly to primary damage."
        )

    # environment loss — separate from reserve drawdown because it is
    # irreversible; materiality-flagged as an extraordinary item
    if flow.environment_loss > 0:
        base_msg = (
            f"environment loss this period: {flow.environment_loss:.2f} xdu "
            "(irreversible, nonrecurring)"
        )
        if extraordinary_flagged:
            pct = (flow.environment_loss / flow.revenue * 100.0
                   if flow.revenue > 0 else float('inf'))
            pct_str = f"{pct:.1f}%" if flow.revenue > 0 else "n/a"
            warnings.append(
                f"EXTRAORDINARY ITEM: {base_msg}, {pct_str} of revenue — "
                "report separately from operating results per "
                "SEEA / GAAP impairment treatment."
            )
        else:
            warnings.append(base_msg)

    # cumulative environment loss — cross-period memory of irreversible damage
    if flow.cumulative_environment_loss > 0:
        warnings.append(
            f"cumulative environment loss to date: "
            f"{flow.cumulative_environment_loss:.2f} xdu (unrecoverable)"
        )

    if flow.irreversible_metrics:
        warnings.append(
            "IRREVERSIBLE: " + ", ".join(flow.irreversible_metrics) +
            " — no amount of glucose spend restores these basins."
        )
    if flow.regeneration_gap() > 0:
        gap_val = flow.regeneration_gap()
        gap_str = "infinite" if isinf(gap_val) else f"{gap_val:.2f}"
        warnings.append(f"regeneration underpaid by {gap_str}")
    if traj == "DEGRADING":
        warnings.append("basin trajectory is degrading across majority of metrics")
    if ttr is not None and ttr <= 1.0:
        warnings.append(f"cliff crossing imminent: time_to_red = {ttr:.2f}")
    if rp > 0 and (isinf(mp) or mp < 0):
        warnings.append(
            "reported profit is positive but metabolic profit is non-positive — "
            "firm is consuming its own basin"
        )

    if isinf(flow.regeneration_required):
        forced = inf
    else:
        forced = flow.regeneration_required + flow.cascade_burn

    return Verdict(
        sustainable_yield_signal=signal,
        basin_trajectory=traj,
        time_to_red=ttr,
        forced_drawdown=forced,
        regeneration_debt=flow.regeneration_debt,
        metabolic_profit=mp,
        reported_profit=rp,
        profit_gap=profit_gap,
        extraordinary_item_flagged=extraordinary_flagged,
        extraordinary_item_amount=flow.environment_loss,
        metabolic_profit_with_loss=mp_full,
        irreversible_metrics=list(flow.irreversible_metrics),
        warnings=warnings,
    )
