"""
cascade/ramp.py

Pluggable degradation ramp shapes.

The degradation fraction maps a basin metric's current state (relative to
its capacity and cliff threshold) into a 0..1 damage signal.

Old equation 3 used a linear ramp. That underestimates near-cliff risk
because real systems have reserves that absorb early damage and then
fail sharply when reserves are exhausted.

This module provides four ramp shapes. All satisfy:
  - ramp(0.0) == 0.0        (healthy: no degradation)
  - ramp(1.0) == 1.0        (at cliff: fully degraded)
  - monotonically non-decreasing on [0, 1]
  - ramp(x) returns 1.0 for x > 1.0 (past cliff: capped at 1)

The INPUT x is a "cliff distance" normalized to [0, 1]:
  x = 0  means healthy (state == capacity for low-bad metrics,
                         state == 0 for high-bad metrics)
  x = 1  means at cliff (state == cliff threshold)
  x > 1  means past cliff (caller clamps to 1.0)


                           SHAPE COMPARISON
                              (ramp output)
      1.0 +                                           *   linear
          |                                       *  /
          |                                   * / /
          |                                *  / /
          |                             * /  /
          |                           */   /              power (p=2)
      0.5 +                         */   /
          |                       */   /
          |                     */  /
          |                   */  /
          |                 /* /
          |               /** /
          |            / *  /
          |        / *  /                   logistic (k=8)
          |   /  *  /                     exponential (k=3)
      0.0 +********----------------------------> cliff distance
          0.0        0.25      0.5      0.75      1.0

The x-axis is "how far from healthy toward cliff." Linear treats this as
evenly damaging. Power and exponential treat early damage as absorbable.
Logistic adds an inflection point — absorbable early, catastrophic mid,
saturating late.


Default is power with exponent 2.0 — simple, defensible, significantly
more honest than linear near the cliff.
"""

from math import exp
from typing import Callable

RampFn = Callable[[float], float]


def _clamp01(x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    return x


def linear() -> RampFn:
    """Original ramp. ramp(x) = x.
    Retained for comparison and for metrics that genuinely degrade linearly
    (rare in real systems)."""
    def _rule(x: float) -> float:
        return _clamp01(x)
    return _rule


def power(exponent: float = 2.0) -> RampFn:
    """Power-law convex ramp. ramp(x) = x^exponent.

    exponent=1.0 reduces to linear.
    exponent=2.0 is the default — mild convexity, defensible as a first
    replacement for linear.
    exponent=3.0 or higher for systems with heavy reserve buffering."""
    if exponent <= 0:
        raise ValueError("power exponent must be positive")
    def _rule(x: float) -> float:
        x = _clamp01(x)
        return x ** exponent
    return _rule


def exponential(steepness: float = 3.0) -> RampFn:
    """Exponential convex ramp.
    ramp(x) = (exp(k*x) - 1) / (exp(k) - 1)

    Small degradation is nearly invisible; accelerates sharply near cliff.
    steepness=3.0: moderate acceleration.
    steepness=5.0: sharp elbow near cliff.
    Use for systems with strong reserves but sudden failure (e.g. aquifer
    with subsidence, apex species with minimum viable population)."""
    if steepness <= 0:
        raise ValueError("exponential steepness must be positive")
    denom = exp(steepness) - 1.0
    def _rule(x: float) -> float:
        x = _clamp01(x)
        return (exp(steepness * x) - 1.0) / denom
    return _rule


def logistic(midpoint: float = 0.6, steepness: float = 10.0) -> RampFn:
    """Logistic ramp with an inflection point.
    ramp(x) = normalized 1 / (1 + exp(-k*(x - x0)))

    Shape: slow damage accumulation early, fast acceleration through
    midpoint, saturation approaching cliff. Models systems where failure
    is a transition between stable states rather than a smooth ramp.

    midpoint  (0,1): where the inflection happens. 0.6 default — damage
                     absorbs well until 60% of cliff distance.
    steepness  > 0:  sharpness of the transition. 10 default.

    Normalized so ramp(0) == 0 and ramp(1) == 1 exactly."""
    if not (0.0 < midpoint < 1.0):
        raise ValueError("logistic midpoint must be in (0,1)")
    if steepness <= 0:
        raise ValueError("logistic steepness must be positive")

    def raw(x: float) -> float:
        return 1.0 / (1.0 + exp(-steepness * (x - midpoint)))

    y0 = raw(0.0)
    y1 = raw(1.0)
    span = y1 - y0
    # span can be very small for extreme steepness; guard against it
    if span <= 0:
        return linear()

    def _rule(x: float) -> float:
        x = _clamp01(x)
        return (raw(x) - y0) / span
    return _rule


# Default rule. Power with exponent 2.0 is the honest first-pass
# replacement for linear: mild convexity, zero extra calibration burden.
DEFAULT_RAMP: RampFn = power(2.0)


# --- audit helper ---

from dataclasses import dataclass
from typing import Dict

@dataclass
class RampAudit:
    """Score each ramp shape at a given cliff distance so the difference
    is visible."""
    distance: float
    linear: float
    power_2: float
    power_3: float
    exponential_3: float
    logistic_default: float


def audit_distance(x: float) -> RampAudit:
    return RampAudit(
        distance=x,
        linear=linear()(x),
        power_2=power(2.0)(x),
        power_3=power(3.0)(x),
        exponential_3=exponential(3.0)(x),
        logistic_default=logistic()(x),
    )
