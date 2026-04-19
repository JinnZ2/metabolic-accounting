"""
cascade/aggregation.py

Pluggable aggregation rules for combining multiple basin degradation
contributions into a single failure rate multiplier.

Each rule takes a list of (sensitivity, degradation) pairs and returns
a multiplier M such that:

    effective_rate = nominal_rate * M

All rules satisfy:
  - M >= 1.0 always (degradation can only increase rate, never decrease it)
  - M == 1.0 when all degradations are zero (healthy basins)
  - M is monotonic non-decreasing in each degradation

Rules differ in how they handle MULTIPLE simultaneous degradations:

  multiplicative:  M = product (1 + s_i * d_i)
                   compounds across dependencies; aggressive.
                   Appropriate when failures genuinely chain
                   (one mechanism triggers another).

  dominant:        M = 1 + max(s_i * d_i)
                   only the worst single contribution counts.
                   Appropriate when one mechanism dominates
                   and others are redundant paths.

  additive:        M = 1 + sum(s_i * d_i)
                   linear superposition of independent stressors.
                   Appropriate when mechanisms are parallel and
                   each adds a share to failure probability.

  saturating:      M = 1 + S_max * (1 - exp(-sum(s_i * d_i) / S_max))
                   additive in the limit of small degradation,
                   saturates at 1 + S_max for severe degradation.
                   Appropriate for bounded-response systems where
                   additional stress has diminishing marginal impact.

Default is additive. This is a significant change from the original
multiplicative default.
"""

from dataclasses import dataclass
from math import exp
from typing import Callable, List, Tuple

# A single dependency contribution: (sensitivity, degradation_fraction)
Contribution = Tuple[float, float]
AggregationRule = Callable[[List[Contribution]], float]


def multiplicative(contribs: List[Contribution]) -> float:
    """Original rule. Compounds across dependencies. Aggressive."""
    m = 1.0
    for s, d in contribs:
        m *= (1.0 + s * d)
    return m


def dominant(contribs: List[Contribution]) -> float:
    """Only the worst single contribution counts."""
    if not contribs:
        return 1.0
    worst = max(s * d for s, d in contribs)
    return 1.0 + worst


def additive(contribs: List[Contribution]) -> float:
    """Linear superposition. Each stressor adds its share."""
    return 1.0 + sum(s * d for s, d in contribs)


def saturating(s_max: float = 10.0) -> AggregationRule:
    """Additive in the small-degradation limit, saturates at 1 + s_max.

    Returns a configured rule. Use as:

        rule = saturating(s_max=8.0)
        multiplier = rule(contribs)
    """
    def _rule(contribs: List[Contribution]) -> float:
        total = sum(s * d for s, d in contribs)
        if total <= 0:
            return 1.0
        return 1.0 + s_max * (1.0 - exp(-total / s_max))
    return _rule


# Default rule used by the cascade detector unless overridden.
DEFAULT_RULE: AggregationRule = additive


@dataclass
class AggregationAudit:
    """Diagnostic output showing how each rule would score the same
    set of contributions. Useful for comparing rule behavior on
    identical inputs."""
    multiplicative: float
    dominant: float
    additive: float
    saturating_default: float


def audit_contributions(contribs: List[Contribution]) -> AggregationAudit:
    sat = saturating(s_max=10.0)
    return AggregationAudit(
        multiplicative=multiplicative(contribs),
        dominant=dominant(contribs),
        additive=additive(contribs),
        saturating_default=sat(contribs),
    )
