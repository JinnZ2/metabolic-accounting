"""
investment_signal/derivative_distance.py

Derivative distance degradation.

Every layer of abstraction between an investment and the real
substrate producing returns reduces the reliability of the signal.
This module quantifies that degradation.

At direct substrate ownership, the investor's fate is coupled
directly to the substrate's productive behavior. At synthetic
distance, the investment behaves independently of any underlying
substrate -- it is priced by reference to other abstract instruments
rather than to any physical reality.

Key failure modes captured by this module:

  Signal attenuation: each abstraction layer introduces noise and
  loss. A claim on a claim on a claim responds to substrate
  changes with lag, attenuation, and occasional sign flips.

  Correlation illusion: at high derivative distance, two
  investments may appear correlated because both are priced by
  the same meta-system, not because their underlying substrates
  are coupled. Portfolios built on this illusion fail under stress.

  Substrate invisibility: at derivative and synthetic distances,
  the investor cannot see what substrate (if any) they are
  actually invested in. Information about substrate state cannot
  reach them in time to matter.

  Cascade amplification: synthetic-distance investments can
  propagate failure across substrates that have no physical
  coupling, because the meta-pricing system couples them. This
  is how a housing crisis becomes a global financial crisis --
  the coupling is in the derivative layer, not the substrates.

  Reverse causation: at high derivative distance, the derivative
  can move the substrate rather than the other way around. Price
  discovery inverts. Substrate producers begin optimizing for
  what the derivative rewards rather than for substrate function.
  This is the financialization failure mode at its extreme.

Derivative distance is NOT simply a function of product type.
A direct equity stake in a productive farm is DIRECT distance.
An ETF that holds equity in a productive farm is ONE_LAYER. An
ETF that tracks an index of ETFs is TWO_LAYER. A credit default
swap on an ETF of ETFs is DERIVATIVE or SYNTHETIC depending on
how reference-chain length is counted.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import DerivativeDistance, InvestmentSubstrate


# ============================================================================
# PER-DISTANCE SIGNAL DEGRADATION
# ============================================================================
#
# At each distance, the investment signal retains some fraction of
# its reliability. This is a scalar multiplier applied to the
# combined realization output.
#
# Calibration:
#   DIRECT       = 1.00  (no signal loss -- investor sees substrate directly)
#   ONE_LAYER    = 0.85  (modest loss through legal/institutional wrapper)
#   TWO_LAYER    = 0.65  (significant loss through double wrapping)
#   DERIVATIVE   = 0.40  (major loss; price can decouple from substrate)
#   SYNTHETIC    = 0.15  (near-total loss; signal is about other signals)
#
# The nonlinearity matters. Each layer is not equally costly.
# DIRECT to ONE_LAYER costs 0.15 of signal. ONE_LAYER to TWO_LAYER
# costs 0.20. TWO_LAYER to DERIVATIVE costs 0.25. DERIVATIVE to
# SYNTHETIC costs 0.25. The degradation accelerates because each
# layer introduces its own failure modes on top of prior layers.

_SIGNAL_RELIABILITY: Dict[DerivativeDistance, float] = {
    DerivativeDistance.DIRECT: 1.00,
    DerivativeDistance.ONE_LAYER: 0.85,
    DerivativeDistance.TWO_LAYER: 0.65,
    DerivativeDistance.DERIVATIVE: 0.40,
    DerivativeDistance.SYNTHETIC: 0.15,
}


# ============================================================================
# PER-DISTANCE SUBSTRATE VISIBILITY
# ============================================================================
#
# How much of the underlying substrate state is visible to the
# investor at each distance. This is separate from signal
# reliability -- the investor might receive reliable returns at
# ONE_LAYER distance but still have limited visibility into
# substrate state.
#
# Values in [0, 1]. 1.0 = perfect visibility; 0.0 = substrate is
# completely opaque.

_SUBSTRATE_VISIBILITY: Dict[DerivativeDistance, float] = {
    DerivativeDistance.DIRECT: 1.00,     # investor IS the substrate observer
    DerivativeDistance.ONE_LAYER: 0.70,  # regular reports but not direct observation
    DerivativeDistance.TWO_LAYER: 0.40,  # aggregate reports about aggregated investments
    DerivativeDistance.DERIVATIVE: 0.15, # pricing signal only, not substrate signal
    DerivativeDistance.SYNTHETIC: 0.02,  # substrate effectively invisible
}


# ============================================================================
# PER-DISTANCE CASCADE COUPLING RISK
# ============================================================================
#
# At higher derivative distance, an investment becomes more likely
# to propagate failure to other investments that share no substrate
# coupling. This is the 2008-style cascade: the derivative layer
# couples investments across uncorrelated substrates, so failure in
# one can propagate to all.
#
# Values are cascade coupling coefficients in [0, 1]. 0.0 means
# failure at this investment does not propagate beyond its own
# substrate chain. 1.0 means failure propagates to every investment
# sharing the derivative layer.
#
# The relationship is opposite to signal reliability: lower
# reliability, higher cascade risk.

_CASCADE_COUPLING: Dict[DerivativeDistance, float] = {
    DerivativeDistance.DIRECT: 0.05,      # failure stays in this substrate chain
    DerivativeDistance.ONE_LAYER: 0.15,
    DerivativeDistance.TWO_LAYER: 0.35,
    DerivativeDistance.DERIVATIVE: 0.65,
    DerivativeDistance.SYNTHETIC: 0.90,   # failure propagates across the meta-layer
}


# ============================================================================
# PER-DISTANCE REVERSE-CAUSATION TENDENCY
# ============================================================================
#
# At high derivative distance, the financial layer can exert
# pressure back on the underlying substrate. Producers optimize
# for derivative rewards rather than substrate function.
#
# Values in [0, 1]. 0.0 means the derivative layer cannot influence
# the substrate. 1.0 means the substrate is effectively controlled
# by the derivative layer.
#
# This is the financialization signature. When this value exceeds
# ~0.5 for a given investment domain, that domain's substrate is
# no longer self-governing; the financial layer has inverted the
# causal flow.

_REVERSE_CAUSATION: Dict[DerivativeDistance, float] = {
    DerivativeDistance.DIRECT: 0.0,       # no reverse causation
    DerivativeDistance.ONE_LAYER: 0.10,
    DerivativeDistance.TWO_LAYER: 0.30,
    DerivativeDistance.DERIVATIVE: 0.60,
    DerivativeDistance.SYNTHETIC: 0.85,
}


# ============================================================================
# PER-SUBSTRATE DERIVATIVE VULNERABILITY
# ============================================================================
#
# Some substrates tolerate abstraction layers better than others.
# MONEY tolerates derivatization fairly well because it is already
# abstract. RELATIONAL_CAPITAL cannot be meaningfully derivatized at
# all -- a derivative of relational capital is not relational
# capital any more. TIME and ATTENTION likewise resist abstraction.
#
# Values multiply with per-distance signal reliability. A substrate
# with high vulnerability (low tolerance) has its signal reliability
# degraded faster as derivative distance increases.
#
# Values in [0, 1]. 1.0 = substrate tolerates abstraction well;
# 0.0 = substrate cannot be abstracted without losing its nature.

_SUBSTRATE_ABSTRACTION_TOLERANCE: Dict[InvestmentSubstrate, float] = {
    InvestmentSubstrate.TIME: 0.30,                   # time cannot be meaningfully abstracted
    InvestmentSubstrate.RESOURCE: 0.65,               # resource can be warehoused and claimed
    InvestmentSubstrate.ENERGY: 0.55,
    InvestmentSubstrate.LABOR: 0.45,                  # labor abstraction loses skill specificity
    InvestmentSubstrate.ATTENTION: 0.20,              # attention cannot be abstracted
    InvestmentSubstrate.MONEY: 0.90,                  # money is already abstract
    InvestmentSubstrate.RELATIONAL_CAPITAL: 0.05,     # abstracting a relationship destroys it
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def signal_reliability(distance: DerivativeDistance) -> float:
    """
    Return the base signal reliability at the given derivative
    distance. Value in [0, 1].
    """
    return _SIGNAL_RELIABILITY[distance]


def substrate_visibility(distance: DerivativeDistance) -> float:
    """
    Return the base substrate visibility at the given derivative
    distance. Value in [0, 1].
    """
    return _SUBSTRATE_VISIBILITY[distance]


def cascade_coupling(distance: DerivativeDistance) -> float:
    """
    Return the cascade coupling risk at the given derivative
    distance. Value in [0, 1].
    """
    return _CASCADE_COUPLING[distance]


def reverse_causation(distance: DerivativeDistance) -> float:
    """
    Return the reverse-causation tendency at the given derivative
    distance. Value in [0, 1].
    """
    return _REVERSE_CAUSATION[distance]


def substrate_abstraction_tolerance(substrate: InvestmentSubstrate) -> float:
    """
    Return how well a substrate tolerates abstraction layers.
    Value in [0, 1].
    """
    return _SUBSTRATE_ABSTRACTION_TOLERANCE[substrate]


def effective_signal_reliability(
    distance: DerivativeDistance,
    primary_substrate: InvestmentSubstrate,
) -> float:
    """
    Return the effective signal reliability combining base distance
    degradation with substrate-specific abstraction tolerance.

    This is the scalar multiplier to apply to realization outputs
    before they are reported as the investment's effective return.
    """
    base = _SIGNAL_RELIABILITY[distance]
    if distance == DerivativeDistance.DIRECT:
        # No abstraction layer exists; substrate tolerance does not apply.
        return base

    tolerance = _SUBSTRATE_ABSTRACTION_TOLERANCE[primary_substrate]
    # Tolerance modifies how much the abstraction costs. A high-tolerance
    # substrate (e.g. MONEY) retains close to the base reliability. A
    # low-tolerance substrate (e.g. RELATIONAL_CAPITAL) degrades much
    # faster through the same abstraction layers.
    #
    # The formula blends base reliability toward zero as tolerance
    # decreases. Perfect tolerance (1.0) preserves base. Zero tolerance
    # collapses to near-zero reliability regardless of distance.
    return base * tolerance + (1.0 - tolerance) * 0.0


def iter_per_distance() -> Tuple[
    Tuple[DerivativeDistance, float, float, float, float], ...
]:
    """
    Iterate over all distances yielding
    (distance, signal_reliability, substrate_visibility,
     cascade_coupling, reverse_causation).
    """
    return tuple(
        (
            d,
            _SIGNAL_RELIABILITY[d],
            _SUBSTRATE_VISIBILITY[d],
            _CASCADE_COUPLING[d],
            _REVERSE_CAUSATION[d],
        )
        for d in DerivativeDistance
    )


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def is_financialized(distance: DerivativeDistance) -> bool:
    """
    Return True if reverse causation is strong enough to indicate
    the substrate domain is being governed by the financial layer
    rather than by substrate function.

    Threshold of 0.5 is the boundary at which the derivative layer
    exerts more influence on substrate behavior than the substrate's
    own dynamics. Above this threshold, producers optimize for
    derivative rewards rather than substrate function.
    """
    return _REVERSE_CAUSATION[distance] >= 0.5


def is_substrate_invisible(distance: DerivativeDistance) -> bool:
    """
    Return True if substrate visibility is below 0.2, meaning the
    investor can no longer see substrate state in time for it to
    matter. At this level, the investment is effectively operating
    blind to its own underlying reality.
    """
    return _SUBSTRATE_VISIBILITY[distance] < 0.2


def substrate_abstraction_breakdown(substrate: InvestmentSubstrate) -> bool:
    """
    Return True if abstracting this substrate destroys the substrate
    itself. Threshold at 0.15 tolerance: below this, the substrate
    cannot survive the abstraction layer and emerges as something
    structurally different.

    TIME, ATTENTION, and RELATIONAL_CAPITAL all fall below this
    threshold. Derivative contracts on attention are not attention.
    Derivative contracts on relational capital are not relational
    capital. Derivative contracts on time are not time.
    """
    return _SUBSTRATE_ABSTRACTION_TOLERANCE[substrate] < 0.15


# ============================================================================
# VALIDATION
# ============================================================================

def validate_derivative_distance() -> None:
    """
    Check structural invariants for derivative distance tables.

    Raises AssertionError on violation.
    """
    # 1. Every distance must have values in each table.
    for d in DerivativeDistance:
        assert d in _SIGNAL_RELIABILITY, (
            f"Missing signal reliability for {d.value}"
        )
        assert d in _SUBSTRATE_VISIBILITY, (
            f"Missing substrate visibility for {d.value}"
        )
        assert d in _CASCADE_COUPLING, (
            f"Missing cascade coupling for {d.value}"
        )
        assert d in _REVERSE_CAUSATION, (
            f"Missing reverse causation for {d.value}"
        )

    # 2. Every substrate must have abstraction tolerance.
    for sub in InvestmentSubstrate:
        assert sub in _SUBSTRATE_ABSTRACTION_TOLERANCE, (
            f"Missing abstraction tolerance for {sub.value}"
        )

    # 3. All values must be in [0, 1].
    for d in DerivativeDistance:
        for table, name in [
            (_SIGNAL_RELIABILITY, "signal_reliability"),
            (_SUBSTRATE_VISIBILITY, "substrate_visibility"),
            (_CASCADE_COUPLING, "cascade_coupling"),
            (_REVERSE_CAUSATION, "reverse_causation"),
        ]:
            v = table[d]
            assert 0.0 <= v <= 1.0, (
                f"{name}[{d.value}] = {v} outside [0, 1]"
            )
    for sub in InvestmentSubstrate:
        v = _SUBSTRATE_ABSTRACTION_TOLERANCE[sub]
        assert 0.0 <= v <= 1.0, (
            f"abstraction_tolerance[{sub.value}] = {v} outside [0, 1]"
        )

    # 4. Signal reliability must be monotonically decreasing with distance.
    #    Every additional layer must reduce signal reliability; no
    #    layer can accidentally improve the signal.
    prev = None
    for d in DerivativeDistance:
        current = _SIGNAL_RELIABILITY[d]
        if prev is not None:
            assert current < prev, (
                f"Signal reliability must decrease monotonically with distance; "
                f"{d.value}={current} not less than previous {prev}"
            )
        prev = current

    # 5. Substrate visibility must be monotonically decreasing.
    prev = None
    for d in DerivativeDistance:
        current = _SUBSTRATE_VISIBILITY[d]
        if prev is not None:
            assert current < prev, (
                f"Substrate visibility must decrease monotonically with distance; "
                f"{d.value}={current} not less than previous {prev}"
            )
        prev = current

    # 6. Cascade coupling must be monotonically INCREASING.
    #    More abstraction = more cross-substrate contagion risk.
    prev = None
    for d in DerivativeDistance:
        current = _CASCADE_COUPLING[d]
        if prev is not None:
            assert current > prev, (
                f"Cascade coupling must increase monotonically with distance; "
                f"{d.value}={current} not greater than previous {prev}"
            )
        prev = current

    # 7. Reverse causation must be monotonically increasing.
    prev = None
    for d in DerivativeDistance:
        current = _REVERSE_CAUSATION[d]
        if prev is not None:
            assert current >= prev, (
                f"Reverse causation must not decrease with distance; "
                f"{d.value}={current} < previous {prev}"
            )
        prev = current

    # 8. DIRECT must have zero reverse causation and near-perfect
    #    substrate visibility.
    assert _REVERSE_CAUSATION[DerivativeDistance.DIRECT] == 0.0, (
        "DIRECT distance must have zero reverse causation"
    )
    assert _SUBSTRATE_VISIBILITY[DerivativeDistance.DIRECT] >= 0.95, (
        "DIRECT distance must have near-perfect substrate visibility"
    )

    # 9. SYNTHETIC must be financialized by definition.
    assert _REVERSE_CAUSATION[DerivativeDistance.SYNTHETIC] >= 0.5, (
        "SYNTHETIC distance must be financialized (reverse causation >= 0.5)"
    )

    # 10. RELATIONAL_CAPITAL, ATTENTION, and TIME must have very low
    #     abstraction tolerance -- these substrates cannot survive
    #     derivatization without losing their nature.
    for sub in (
        InvestmentSubstrate.RELATIONAL_CAPITAL,
        InvestmentSubstrate.ATTENTION,
        InvestmentSubstrate.TIME,
    ):
        v = _SUBSTRATE_ABSTRACTION_TOLERANCE[sub]
        assert v < 0.35, (
            f"{sub.value} abstraction tolerance must be < 0.35; "
            f"got {v}. Derivatizing these substrates destroys their nature."
        )

    # 11. MONEY must have the highest abstraction tolerance.
    money_tol = _SUBSTRATE_ABSTRACTION_TOLERANCE[InvestmentSubstrate.MONEY]
    for sub in InvestmentSubstrate:
        if sub == InvestmentSubstrate.MONEY:
            continue
        other = _SUBSTRATE_ABSTRACTION_TOLERANCE[sub]
        assert money_tol >= other, (
            f"MONEY must have highest abstraction tolerance; "
            f"{sub.value}={other} >= MONEY={money_tol}"
        )


# ============================================================================
# DISPLAY
# ============================================================================

def format_distance_table() -> str:
    """Return a human-readable table of distance-indexed values."""
    lines = [
        "Derivative distance characteristics:",
        "",
        f"  {'distance':<14}  {'signal':>7}  {'visible':>7}  {'cascade':>7}  {'reverse':>7}",
        f"  {'-'*14}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*7}",
    ]
    for d, sig, vis, casc, rev in iter_per_distance():
        lines.append(
            f"  {d.value:<14}  {sig:>7.2f}  {vis:>7.2f}  {casc:>7.2f}  {rev:>7.2f}"
        )
    return "\n".join(lines)


def format_substrate_tolerance() -> str:
    """Return substrate abstraction tolerance table."""
    lines = [
        "Substrate abstraction tolerance:",
        f"  (low tolerance = derivatizing destroys substrate nature)",
        "",
    ]
    for sub in InvestmentSubstrate:
        v = _SUBSTRATE_ABSTRACTION_TOLERANCE[sub]
        marker = " <-- cannot be meaningfully abstracted" if v < 0.15 else ""
        lines.append(f"  {sub.value:>24}  {v:.2f}{marker}")
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_derivative_distance()
    print("Derivative distance tables validated.")
    print()
    print(format_distance_table())
    print()
    print(format_substrate_tolerance())
    print()

    # Demonstration: direct farm investment vs. index-of-funds
    print("Case comparison: direct farm vs. multi-layer financial product")
    print()

    direct_reliability = effective_signal_reliability(
        DerivativeDistance.DIRECT,
        InvestmentSubstrate.RESOURCE,
    )
    print(f"  DIRECT in RESOURCE substrate:")
    print(f"    effective signal reliability: {direct_reliability:.2f}")
    print(f"    financialized:                {is_financialized(DerivativeDistance.DIRECT)}")
    print(f"    substrate invisible:          {is_substrate_invisible(DerivativeDistance.DIRECT)}")
    print()

    two_layer_reliability = effective_signal_reliability(
        DerivativeDistance.TWO_LAYER,
        InvestmentSubstrate.MONEY,
    )
    print(f"  TWO_LAYER in MONEY substrate:")
    print(f"    effective signal reliability: {two_layer_reliability:.2f}")
    print(f"    financialized:                {is_financialized(DerivativeDistance.TWO_LAYER)}")
    print(f"    substrate invisible:          {is_substrate_invisible(DerivativeDistance.TWO_LAYER)}")
    print()

    synthetic_reliability = effective_signal_reliability(
        DerivativeDistance.SYNTHETIC,
        InvestmentSubstrate.MONEY,
    )
    print(f"  SYNTHETIC in MONEY substrate:")
    print(f"    effective signal reliability: {synthetic_reliability:.2f}")
    print(f"    financialized:                {is_financialized(DerivativeDistance.SYNTHETIC)}")
    print(f"    substrate invisible:          {is_substrate_invisible(DerivativeDistance.SYNTHETIC)}")
    print()

    # Cannot-derivatize demonstration
    print("Substrates that cannot survive derivatization:")
    for sub in InvestmentSubstrate:
        if substrate_abstraction_breakdown(sub):
            print(f"  - {sub.value}")
