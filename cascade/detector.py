"""
cascade/detector.py

Cascade failure detector.

Given a set of basin states and infrastructure systems, computes:
  - effective failure rate for each system (nominal * basin multipliers)
  - expected damage accumulation per unit time
  - ordered failure sequence (which system fails first, second, third)
  - time lag between failures
  - total unplanned glucose burn (cascade cost)

The core claim: infrastructure failures arrive in a predictable sequence
when basin coupling is modeled. This is the falsifiable output.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from basin_states.base import BasinState
from infrastructure.systems import InfrastructureSystem
from cascade.aggregation import (
    AggregationRule, DEFAULT_RULE, audit_contributions, AggregationAudit,
)
from cascade.ramp import RampFn, DEFAULT_RAMP


# Legacy global set. Retained as fallback only — basins that declare
# high_is_bad on themselves take precedence. New basins should use the
# per-basin field instead.
HIGH_IS_BAD = {
    "particulate_load",
    "chemical_load",
    "filter_burden",
    "contamination_load",
    "temperature_anomaly",
}


def _is_high_is_bad(basin: BasinState, key: str) -> bool:
    """Prefer the per-basin declaration; fall back to legacy global set."""
    decl = getattr(basin, "high_is_bad", None)
    if decl:
        return key in decl
    return key in HIGH_IS_BAD


def _cliff_distance(basin: BasinState, key: str) -> float:
    """Return a 0..1 cliff-distance for a basin metric, BEFORE ramp shaping.
    0.0 = healthy, 1.0 = at cliff, >1.0 = past cliff.

    This is the raw geometric distance from healthy to failure threshold.
    The ramp function then shapes how that distance translates into
    damage signal."""
    s = basin.state.get(key)
    c = basin.cliff_thresholds.get(key)
    cap = basin.capacity.get(key)
    if s is None or c is None or cap is None:
        return 0.0
    if _is_high_is_bad(basin, key):
        # healthy at s=0, at cliff when s=c
        if s <= 0:
            return 0.0
        if s >= c:
            return 1.0
        return s / c
    else:
        # healthy at s=cap, at cliff when s=c
        if s >= cap:
            return 0.0
        if s <= c:
            return 1.0
        if cap == c:
            return 1.0
        return 1.0 - (s - c) / (cap - c)


def _degradation_fraction(
    basin: BasinState,
    key: str,
    ramp: Optional[RampFn] = None,
) -> float:
    """Return a 0..1 degradation fraction for a basin metric after
    applying the chosen ramp shape.

    0.0 = healthy, 1.0 = past cliff.

    Default ramp is power(2.0). Pass ramp=linear() for the old behavior,
    or any other shape from cascade.ramp."""
    if ramp is None:
        ramp = DEFAULT_RAMP
    x = _cliff_distance(basin, key)
    return ramp(x)


def _contributions_for(
    system: InfrastructureSystem,
    basins: Dict[str, BasinState],
    ramp: Optional[RampFn] = None,
) -> List[Tuple[float, float]]:
    """Return list of (sensitivity, degradation) for each active dependency."""
    contribs: List[Tuple[float, float]] = []
    for basin_name, key, sensitivity in system.dependencies:
        basin = basins.get(basin_name)
        if basin is None:
            continue
        deg = _degradation_fraction(basin, key, ramp=ramp)
        contribs.append((sensitivity, deg))
    return contribs


def effective_failure_rate(
    system: InfrastructureSystem,
    basins: Dict[str, BasinState],
    rule: Optional[AggregationRule] = None,
    ramp: Optional[RampFn] = None,
) -> float:
    """Compute effective failure rate given current basin states.
    Default aggregation rule is additive, default ramp is power(2.0)."""
    if rule is None:
        rule = DEFAULT_RULE
    contribs = _contributions_for(system, basins, ramp=ramp)
    multiplier = rule(contribs)
    return system.nominal_failure_rate * multiplier


def audit_system(
    system: InfrastructureSystem,
    basins: Dict[str, BasinState],
    ramp: Optional[RampFn] = None,
) -> AggregationAudit:
    """Compare all aggregation rules side-by-side on the same system."""
    contribs = _contributions_for(system, basins, ramp=ramp)
    return audit_contributions(contribs)


@dataclass
class FailurePrediction:
    system_name: str
    effective_rate: float
    time_to_failure: float
    expected_cost: float
    dominant_basin: Tuple[str, str, float]


def predict_failures(
    systems: List[InfrastructureSystem],
    basins: Dict[str, BasinState],
    rule: Optional[AggregationRule] = None,
    ramp: Optional[RampFn] = None,
) -> List[FailurePrediction]:
    """Return predictions sorted by time_to_failure ascending (first first)."""
    predictions = []
    for sys in systems:
        rate = effective_failure_rate(sys, basins, rule=rule, ramp=ramp)
        ttf = 1.0 / rate if rate > 0 else float("inf")
        dominant = ("", "", 0.0)
        max_contrib = 0.0
        for basin_name, key, sensitivity in sys.dependencies:
            basin = basins.get(basin_name)
            if basin is None:
                continue
            deg = _degradation_fraction(basin, key, ramp=ramp)
            contrib = sensitivity * deg
            if contrib > max_contrib:
                max_contrib = contrib
                dominant = (basin_name, key, contrib)
        predictions.append(
            FailurePrediction(
                system_name=sys.name,
                effective_rate=rate,
                time_to_failure=ttf,
                expected_cost=rate * sys.baseline_repair_cost,
                dominant_basin=dominant,
            )
        )
    predictions.sort(key=lambda p: p.time_to_failure)
    return predictions


def cascade_cost(
    systems: List[InfrastructureSystem],
    basins: Dict[str, BasinState],
    horizon: float = 1.0,
    rule: Optional[AggregationRule] = None,
    ramp: Optional[RampFn] = None,
) -> float:
    """Total expected unplanned glucose burn over the given horizon."""
    total = 0.0
    for sys in systems:
        rate = effective_failure_rate(sys, basins, rule=rule, ramp=ramp)
        total += rate * horizon * sys.baseline_repair_cost
    return total
