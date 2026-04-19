"""
accounting/glucose.py

Glucose-flow accounting.

Money is treated as a flow signal, not a stock. The firm is an organism that:
  - ingests glucose (revenue)
  - burns glucose for direct metabolism (operating cost)
  - burns glucose for basin regeneration (mandatory, forced)
  - burns glucose for cascade failures (unplanned, unavoidable if basins degrade)
  - stores glucose as profit only after ALL of the above are paid

The forced drawdown for regeneration is the key move. In conventional accounting
it lives outside the firm. Here it lives on the PnL as a non-optional line.

Regeneration debt is the accumulated unpaid regeneration cost. A firm with
positive profit and large regeneration debt is consuming its own basin, not
producing value.

Regeneration cost is computed per-metric using the registry in
accounting.regeneration. Infinite cost (irreversible thresholds) propagates
honestly through the pipeline.
"""

from dataclasses import dataclass, field
from math import inf, isinf
from typing import Dict, List, Optional, Tuple

from basin_states.base import BasinState
from cascade.detector import cascade_cost, _degradation_fraction
from cascade.ramp import RampFn
from accounting.regeneration import (
    RegenFn, RegenCost, DEFAULT_REGISTRY, KNOWN_METRICS,
    UnregisteredMetricError,
)


@dataclass
class GlucoseFlow:
    revenue: float = 0.0
    direct_operating_cost: float = 0.0
    regeneration_paid: float = 0.0
    regeneration_required: float = 0.0
    cascade_burn: float = 0.0
    regeneration_debt: float = 0.0
    # reserve-layer additions (see reserves/ and thermodynamics/)
    reserve_drawdown_cost: float = 0.0       # xdu consumed from secondary + tertiary this period
    environment_loss: float = 0.0            # xdu dissipated past recovery THIS period
    cumulative_environment_loss: float = 0.0 # xdu dissipated past recovery ALL periods
    exhausted_reserves: List[Tuple[str, str]] = field(default_factory=list)
    tertiary_past_cliff: List[str] = field(default_factory=list)
    irreversible_metrics: List[str] = field(default_factory=list)
    regen_breakdown: List[RegenCost] = field(default_factory=list)
    registry_warnings: List[str] = field(default_factory=list)

    def has_irreversibility(self) -> bool:
        """Primary irreversibility OR any tertiary pool past cliff.
        Tertiary past cliff means landscape-scale damage the firm cannot
        repair on its own horizon — thermodynamic equivalent of primary
        irreversibility."""
        return (
            len(self.irreversible_metrics) > 0
            or len(self.tertiary_past_cliff) > 0
            or isinf(self.regeneration_required)
        )

    def reported_profit(self) -> float:
        """Conventional profit — operations only, ignores regeneration and
        reserve depletion. Cascade burn is separated for visibility but
        still a real cost."""
        return self.revenue - self.direct_operating_cost - self.cascade_burn

    def metabolic_profit(self) -> float:
        """Operating profit after mandatory regeneration and reserve drawdown.

        Charges ONLY the recurring costs: regen (condition maintenance),
        cascade burn (infrastructure failures), reserve drawdown (stock
        consumed this period from secondary + tertiary).

        Environment loss is EXCLUDED here because it is irreversible and
        nonrecurring — see metabolic_profit_with_loss() for the full
        picture including extraordinary items.

        The distinction follows SEEA/GAAP practice: depreciation-like
        recurring wear is an operating expense; impairments and
        irreversible losses are extraordinary items reported separately.

        Returns -inf when regeneration requirement is infinite — the
        honest signal for an unrecoverable state."""
        if isinf(self.regeneration_required):
            return -inf
        return (
            self.revenue
            - self.direct_operating_cost
            - self.regeneration_required
            - self.cascade_burn
            - self.reserve_drawdown_cost
        )

    def metabolic_profit_with_loss(self) -> float:
        """Metabolic profit after charging environment loss as an
        extraordinary item.

        This is the "full picture" bottom line — what the firm would
        report if irreversible basin losses were treated analogously to
        asset impairments under GAAP (ASC 360-10-35) or extraordinary
        items under GASB 42.

        Environment loss is irreversible exergy dissipation — the
        reserve is gone, no amount of future spending restores it.
        Treating it as an operating cost is wrong (not recurring);
        ignoring it is worse (makes the period look better than it is).
        The honest treatment is to charge it separately and flag it."""
        if isinf(self.regeneration_required) or isinf(self.environment_loss):
            return -inf
        return self.metabolic_profit() - self.environment_loss

    def is_extraordinary_loss_material(
        self,
        revenue_threshold: float = 0.05,
        min_absolute: float = 0.0,
    ) -> bool:
        """Whether this period's environment loss is material enough to
        warrant extraordinary-item classification.

        Default threshold: 5% of revenue (standard GAAP materiality
        heuristic). A firm with $1M revenue and $50k+ irreversible
        environment loss crosses this line.

        min_absolute: lower bound on absolute magnitude regardless of
        revenue ratio. Useful when revenue is near zero or irrelevant
        (e.g., public-sector, early-stage firms)."""
        if self.environment_loss <= 0:
            return False
        if self.environment_loss < min_absolute:
            return False
        if self.revenue <= 0:
            return self.environment_loss >= min_absolute
        return self.environment_loss >= revenue_threshold * self.revenue

    def regeneration_gap(self) -> float:
        """How much the firm under-paid for regeneration this period."""
        if isinf(self.regeneration_required):
            return inf if self.regeneration_paid < inf else 0.0
        return max(0.0, self.regeneration_required - self.regeneration_paid)


def required_regeneration_cost_detailed(
    basins: Dict[str, BasinState],
    registry: Optional[Dict] = None,
    strict: bool = False,
    ramp: Optional[RampFn] = None,
) -> tuple:
    """Compute required regeneration cost using per-metric functions.

    Registry is keyed by (basin_type, metric_key), NOT by basin name.
    A basin with basin_type == "soil" and metric "bearing_capacity" will
    find its cost function regardless of whether the basin is named
    "site_soil", "farm_north_soil", or "depot_lot_3_soil".

    Returns (total_cost, breakdown_list, irreversible_metric_names, warnings).

    total_cost may be math.inf if any metric has crossed an irreversible
    threshold. This is NOT a bug — it is the honest signal that the basin
    has passed a state money cannot restore.

    Strict mode raises UnregisteredMetricError when a (basin_type, key) pair
    appears in KNOWN_METRICS but has no function in the active registry.
    This is how the framework refuses to silently under-report cost.
    """
    if registry is None:
        registry = DEFAULT_REGISTRY

    total = 0.0
    breakdown: List[RegenCost] = []
    irreversible: List[str] = []
    warnings: List[str] = []
    any_inf = False

    for basin in basins.values():
        b_type = getattr(basin, "basin_type", "") or ""
        if not b_type:
            warnings.append(
                f"basin '{basin.name}' has no basin_type declared; "
                "regeneration cost cannot be looked up by type. "
                "Set basin.basin_type to one of the known types "
                "('soil', 'air', 'water', 'biology', ...) or pass a custom registry."
            )

        for key in basin.state.keys():
            deg = _degradation_fraction(basin, key, ramp=ramp)
            if deg <= 0:
                continue

            lookup_key = (b_type, key)
            fn = registry.get(lookup_key)

            if fn is None:
                # distinguish "known metric missing a function" (bug / config error)
                # from "unknown metric" (user-defined, no claim to coverage)
                is_known = lookup_key in KNOWN_METRICS
                msg = (
                    f"no regen function for basin_type='{b_type}', "
                    f"metric='{key}' (basin '{basin.name}')"
                )
                if is_known and strict:
                    raise UnregisteredMetricError(msg)
                warnings.append(
                    msg + (" [known metric]" if is_known else " [unknown metric]")
                )
                breakdown.append(RegenCost(
                    basin_name=basin.name, metric_key=key, degradation=deg,
                    base_cost=0.0, nonlinearity_factor=0.0,
                    irreversible=False, total_cost=0.0,
                    notes="No cost function registered; skipped.",
                ))
                continue

            rc = fn(basin, key, deg)
            breakdown.append(rc)
            if rc.irreversible or isinf(rc.total_cost):
                irreversible.append(f"{basin.name}.{key}")
                any_inf = True
            else:
                total += rc.total_cost

    if any_inf:
        total = inf
    return total, breakdown, irreversible, warnings


def required_regeneration_cost(
    basins: Dict[str, BasinState],
    rate_per_unit_degradation: float = 100.0,   # legacy, ignored
    registry: Optional[Dict] = None,
    strict: bool = False,
) -> float:
    """Compatibility wrapper. Ignores the legacy scalar; uses the registry."""
    total, _, _, _ = required_regeneration_cost_detailed(
        basins, registry=registry, strict=strict,
    )
    return total


def compute_flow(
    revenue: float,
    direct_operating_cost: float,
    regeneration_paid: float,
    basins: Dict[str, BasinState],
    systems,
    horizon: float = 1.0,
    prior_debt: float = 0.0,
    registry: Optional[Dict] = None,
    strict: bool = False,
    ramp: Optional[RampFn] = None,
    # site coupling: if either is provided, reserve drawdown is
    # incorporated into the metabolic profit calculation
    site=None,                          # reserves.Site (optional)
    step_result=None,                   # reserves.SiteStepResult (optional)
    rate_per_unit_degradation: Optional[float] = None,   # legacy, ignored
) -> GlucoseFlow:
    """Compute the glucose flow for one period.

    If `site` and `step_result` are both provided, the flow includes
    reserve_drawdown_cost (secondary + tertiary kept, in xdu) and
    environment_loss from the site's step, and the verdict signal
    will surface exhausted reserves and tertiary pools past cliff.

    If only `site` is provided (no step_result), the current reserve
    status is read but no drawdown cost is charged (useful when the
    caller drives step() separately and wants compute_flow to just
    report reserve status).

    If neither is provided, behavior is identical to the pre-reserve
    compute_flow.
    """
    required, breakdown, irreversible, regen_warnings = (
        required_regeneration_cost_detailed(
            basins, registry=registry, strict=strict, ramp=ramp,
        )
    )
    burn = cascade_cost(systems, basins, horizon=horizon, ramp=ramp)

    # reserve coupling
    reserve_drawdown_cost = 0.0
    env_loss = 0.0
    cumulative_env_loss = 0.0
    exhausted: List[Tuple[str, str]] = []
    tertiary_past: List[str] = []

    if step_result is not None:
        # reserve drawdown = secondary kept + tertiary kept (xdu
        # consumed from storage this period). environment loss is
        # reported separately because it is irreversible.
        reserve_drawdown_cost = (
            step_result.total_secondary_kept
            + step_result.total_tertiary_kept
        )
        env_loss = step_result.total_environment

    if site is not None:
        exhausted = list(site.exhausted_reserves())
        tertiary_past = list(site.tertiary_past_cliff())
        cumulative_env_loss = site.cumulative_environment_loss

    if isinf(required):
        gap = inf
    else:
        gap = max(0.0, required - regeneration_paid)

    if isinf(prior_debt) or isinf(gap):
        new_debt = inf
    else:
        new_debt = prior_debt + gap

    return GlucoseFlow(
        revenue=revenue,
        direct_operating_cost=direct_operating_cost,
        regeneration_paid=regeneration_paid,
        regeneration_required=required,
        cascade_burn=burn,
        regeneration_debt=new_debt,
        reserve_drawdown_cost=reserve_drawdown_cost,
        environment_loss=env_loss,
        cumulative_environment_loss=cumulative_env_loss,
        exhausted_reserves=exhausted,
        tertiary_past_cliff=tertiary_past,
        irreversible_metrics=irreversible,
        regen_breakdown=breakdown,
        registry_warnings=regen_warnings,
    )
