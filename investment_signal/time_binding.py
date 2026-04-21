"""
investment_signal/time_binding.py

Time binding integrity.

Every investment binds resources across time. The commitment has
two ends: a start (when substrate is committed) and a realization
(when return is expected). The integrity of this binding depends
on whether the monetary unit, the substrate, and the network
between them all remain stable across the binding period.

Time binding is DISTINCT from time scope. Scope is the horizon
of evaluation. Binding is the structural commitment duration of
the specific investment instrument. A farmer with a generational
land investment may evaluate it at any scope; the binding itself
is generational regardless.

Mismatch failure modes:

  Short binding, long realization: investor commits with a short
  binding (daily liquidity), but the underlying substrate takes a
  long cycle to produce. Result: realization timeline is longer
  than binding, so the investor can exit before realization,
  creating a liquidity illusion. Modern financial markets are
  largely built on this mismatch.

  Long binding, short realization: investor commits capital for
  generations but the underlying substrate produces seasonally
  and decays. Result: capital is locked against decaying returns.
  This is the infrastructure-depreciation trap.

  Time binding scope mismatch with monetary temporal scope: a
  generational binding on a digital fiat substrate evaluated at
  epochal scope has integrity near zero -- the monetary substrate
  itself is not reliable across epochs. This is the core failure
  mode of retirement accounts denominated in national currencies
  evaluated across civilizational collapse scenarios.

  Binding monetization destroys the substrate: an investment with
  generational binding in RELATIONAL_CAPITAL whose vehicle is
  converted to MONEY realization loses most integrity because
  monetizing relational capital destroys it. This is a
  binding-to-realization mismatch.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple

from .dimensions import (
    InvestmentSubstrate,
    TimeBinding,
)
# Money-signal temporal scope enters here because the binding must
# be evaluated against the monetary stability horizon.
from ..money_signal.dimensions import TemporalScope


# ============================================================================
# TIME BINDING INTEGRITY TABLE
# ============================================================================
#
# Integrity = probability that the temporal commitment of the
# investment holds across its binding period, in the calibration
# case (institutional culture, state-enforced attribution, healthy
# monetary state).
#
# Values are in [0, 1]. 1.0 = perfect binding integrity. 0.0 =
# binding is effectively broken.
#
# The first axis is the investment's time binding.
# The second axis is the monetary temporal scope used for evaluation.
#
# A short binding evaluated at a long scope has LOW integrity
# because the investment is repeatedly rolled over, each rollover
# introducing risk. A long binding evaluated at a short scope has
# HIGH integrity for short-scope purposes but the long-scope
# resolution is not yet visible.
#
# Diagonal (binding matches scope) is the most favorable case and
# the calibration anchor.

_BINDING_INTEGRITY: Dict[TimeBinding, Dict[TemporalScope, float]] = {

    # ----------------------------------------------------------------
    # IMMEDIATE binding: return expected within days.
    # Integrity is high at transaction scope, degrades rapidly at
    # longer scopes because the investment is repeatedly rolled
    # over across those horizons.
    # ----------------------------------------------------------------
    TimeBinding.IMMEDIATE: {
        TemporalScope.TRANSACTION: 0.95,
        TemporalScope.SEASONAL: 0.6,       # rollover risk accumulates
        TemporalScope.GENERATIONAL: 0.2,   # many rollovers, high accumulated risk
        TemporalScope.EPOCHAL: 0.05,       # essentially no integrity across epochs
    },

    # ----------------------------------------------------------------
    # SHORT_CYCLE binding: weeks to a quarter.
    # ----------------------------------------------------------------
    TimeBinding.SHORT_CYCLE: {
        TemporalScope.TRANSACTION: 0.9,    # short-cycle is longer than transaction, strong
        TemporalScope.SEASONAL: 0.85,      # close to natural cycle
        TemporalScope.GENERATIONAL: 0.3,
        TemporalScope.EPOCHAL: 0.1,
    },

    # ----------------------------------------------------------------
    # SEASONAL binding: one production cycle.
    # The natural calibration point for most biological and
    # traditional productive systems.
    # ----------------------------------------------------------------
    TimeBinding.SEASONAL: {
        TemporalScope.TRANSACTION: 0.85,
        TemporalScope.SEASONAL: 0.9,       # strong match
        TemporalScope.GENERATIONAL: 0.5,
        TemporalScope.EPOCHAL: 0.15,
    },

    # ----------------------------------------------------------------
    # MULTI_YEAR binding: 2-10 years.
    # Typical institutional investment horizon. Works well within
    # seasonal and generational scopes, weak at epochal.
    # ----------------------------------------------------------------
    TimeBinding.MULTI_YEAR: {
        TemporalScope.TRANSACTION: 0.7,    # short scope cannot see return yet
        TemporalScope.SEASONAL: 0.85,
        TemporalScope.GENERATIONAL: 0.8,
        TemporalScope.EPOCHAL: 0.2,
    },

    # ----------------------------------------------------------------
    # GENERATIONAL binding: 20+ years, inherited.
    # Land, infrastructure, long-duration institutional commitments.
    # ----------------------------------------------------------------
    TimeBinding.GENERATIONAL: {
        TemporalScope.TRANSACTION: 0.4,
        TemporalScope.SEASONAL: 0.7,
        TemporalScope.GENERATIONAL: 0.9,   # strong match
        TemporalScope.EPOCHAL: 0.35,
    },

    # ----------------------------------------------------------------
    # MULTI_GENERATIONAL binding: knowledge, land across generations.
    # Traditional ecological knowledge, inherited farmland under
    # continuous care, intergenerational crafts. Integrity holds
    # at longest scopes, weak at shortest because the return does
    # not materialize at short scope.
    # ----------------------------------------------------------------
    TimeBinding.MULTI_GENERATIONAL: {
        TemporalScope.TRANSACTION: 0.2,
        TemporalScope.SEASONAL: 0.5,
        TemporalScope.GENERATIONAL: 0.85,
        TemporalScope.EPOCHAL: 0.6,        # longer integrity than any other binding
    },
}


# ============================================================================
# SUBSTRATE-SPECIFIC BINDING MODIFIERS
# ============================================================================
#
# Some substrates hold binding integrity better than others across
# long periods. RELATIONAL_CAPITAL binding holds across generations
# if the network persists. MONEY binding degrades under inflation
# and monetary regime change. RESOURCE binding depends on decay.
#
# These modifiers are multiplied with the base integrity. A modifier
# > 1.0 is capped at 1.0 by min() in the access function.

_SUBSTRATE_BINDING_MODIFIER: Dict[InvestmentSubstrate, float] = {
    # Time as binding substrate: time is consumed, not preserved.
    # Low modifier for long bindings.
    InvestmentSubstrate.TIME: 0.7,

    # Resource: physical decay is the main integrity loss path.
    # Baseline modifier of 1.0; specific decay profiles belong in
    # the coupling module.
    InvestmentSubstrate.RESOURCE: 1.0,

    # Energy: stored energy decays. Low modifier.
    InvestmentSubstrate.ENERGY: 0.6,

    # Labor: embodied skill degrades if unused, improves if used.
    # Baseline neutral; context-dependent.
    InvestmentSubstrate.LABOR: 1.0,

    # Attention: attention is flow, not stock. Cannot meaningfully
    # be bound over long periods. Low modifier.
    InvestmentSubstrate.ATTENTION: 0.5,

    # Money: institutionally the easiest to bind temporally, but
    # vulnerable to inflation and regime change. Baseline 1.0 in
    # nominal terms; real integrity handled via money context.
    InvestmentSubstrate.MONEY: 1.0,

    # Relational capital: compounds and persists across generations
    # when the network persists. Highest modifier.
    InvestmentSubstrate.RELATIONAL_CAPITAL: 1.15,
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def base_time_binding_integrity(
    binding: TimeBinding,
    evaluation_scope: TemporalScope,
) -> float:
    """
    Return the base time binding integrity for the given binding
    evaluated at the given temporal scope.

    Returns a value in [0, 1]. 1.0 = perfect integrity; 0.0 =
    binding is structurally broken at this scope.

    Baseline calibration: institutional cultural scope, state-
    enforced monetary attribution, healthy monetary state. Context
    modifiers in coupling.py modify this based on full investment
    and monetary context.
    """
    return _BINDING_INTEGRITY[binding][evaluation_scope]


def binding_integrity_with_substrate(
    binding: TimeBinding,
    evaluation_scope: TemporalScope,
    primary_binding_substrate: InvestmentSubstrate,
) -> float:
    """
    Return binding integrity adjusted for the primary substrate the
    binding is denominated in.

    Most investments have a primary binding substrate -- the one
    that dominates the value stored across time. Land-based
    investment has RESOURCE as primary binding substrate. A bond
    has MONEY. An apprenticeship has LABOR and RELATIONAL_CAPITAL.

    The caller chooses which substrate to treat as primary based on
    where the majority of the vehicle's stored value sits.

    Returns a value in [0, 1], clipped at 1.0.
    """
    base = _BINDING_INTEGRITY[binding][evaluation_scope]
    modifier = _SUBSTRATE_BINDING_MODIFIER[primary_binding_substrate]
    return min(1.0, base * modifier)


def iter_binding_integrity() -> Tuple[
    Tuple[TimeBinding, TemporalScope, float], ...
]:
    """Iterate over all (binding, scope, integrity) triples."""
    return tuple(
        (b, s, _BINDING_INTEGRITY[b][s])
        for b in TimeBinding
        for s in TemporalScope
    )


def iter_substrate_modifiers() -> Tuple[
    Tuple[InvestmentSubstrate, float], ...
]:
    """Iterate over substrate binding modifiers."""
    return tuple(
        (sub, _SUBSTRATE_BINDING_MODIFIER[sub])
        for sub in InvestmentSubstrate
    )


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def binding_scope_mismatch_severity(
    binding: TimeBinding,
    evaluation_scope: TemporalScope,
) -> float:
    """
    Return the severity of binding-scope mismatch.

    Defined as 1.0 minus the base integrity. Higher values indicate
    the binding does not hold at this scope. A severity above 0.5
    indicates the binding is effectively decorative at this scope.

    This is the primary diagnostic for detecting scope-inflation
    errors in investment analysis: "I am planning retirement" is a
    generational-scope question, and short-cycle or immediate
    bindings have severe mismatch with it even though they feel
    responsive on a daily basis.
    """
    return 1.0 - _BINDING_INTEGRITY[binding][evaluation_scope]


def is_short_binding_long_scope(
    binding: TimeBinding,
    evaluation_scope: TemporalScope,
) -> bool:
    """
    Return True if this is a short-binding / long-scope mismatch.

    This is the liquidity-illusion failure mode: investors feel
    safe because they can exit quickly, but the substrate they are
    invested in takes much longer to produce or resolve, so exit
    liquidity is decoupled from actual substrate state. Many
    financial products operate in this regime.
    """
    short_bindings = {
        TimeBinding.IMMEDIATE,
        TimeBinding.SHORT_CYCLE,
    }
    long_scopes = {
        TemporalScope.GENERATIONAL,
        TemporalScope.EPOCHAL,
    }
    return binding in short_bindings and evaluation_scope in long_scopes


def is_long_binding_short_scope(
    binding: TimeBinding,
    evaluation_scope: TemporalScope,
) -> bool:
    """
    Return True if this is a long-binding / short-scope mismatch.

    This is the infrastructure-depreciation trap: capital committed
    generationally but evaluated at short scope, where the return
    has not yet materialized and the decay has already begun. Many
    municipal infrastructure financing decisions fail in this
    regime.
    """
    long_bindings = {
        TimeBinding.GENERATIONAL,
        TimeBinding.MULTI_GENERATIONAL,
    }
    short_scopes = {
        TemporalScope.TRANSACTION,
        TemporalScope.SEASONAL,
    }
    return binding in long_bindings and evaluation_scope in short_scopes


# ============================================================================
# VALIDATION
# ============================================================================

def validate_time_binding() -> None:
    """
    Check structural invariants for the time binding tables.

    Raises AssertionError on violation.
    """
    # 1. Every binding must have entries for every temporal scope.
    for binding in TimeBinding:
        assert binding in _BINDING_INTEGRITY, (
            f"Missing binding integrity row for {binding.value}"
        )
        for scope in TemporalScope:
            assert scope in _BINDING_INTEGRITY[binding], (
                f"Missing integrity B[{binding.value}][{scope.value}]"
            )

    # 2. All integrity values must be in [0, 1].
    for binding in TimeBinding:
        for scope in TemporalScope:
            v = _BINDING_INTEGRITY[binding][scope]
            assert 0.0 <= v <= 1.0, (
                f"Binding integrity B[{binding.value}][{scope.value}] = {v} "
                f"outside [0, 1]"
            )

    # 3. Every substrate must have a binding modifier.
    for sub in InvestmentSubstrate:
        assert sub in _SUBSTRATE_BINDING_MODIFIER, (
            f"Missing substrate binding modifier for {sub.value}"
        )

    # 4. Substrate modifiers must be positive.
    for sub in InvestmentSubstrate:
        v = _SUBSTRATE_BINDING_MODIFIER[sub]
        assert v > 0.0, (
            f"Substrate binding modifier for {sub.value} = {v} "
            f"must be positive"
        )

    # 5. Short-binding / long-scope mismatch must have severity >= 0.5.
    #    This encodes the liquidity-illusion claim that short bindings
    #    cannot meaningfully address long-scope questions.
    for binding in (TimeBinding.IMMEDIATE, TimeBinding.SHORT_CYCLE):
        for scope in (TemporalScope.GENERATIONAL, TemporalScope.EPOCHAL):
            severity = binding_scope_mismatch_severity(binding, scope)
            assert severity >= 0.5, (
                f"Short-binding ({binding.value}) / long-scope ({scope.value}) "
                f"must have severity >= 0.5, got {severity:.2f}. "
                f"Liquidity illusion claim requires this invariant."
            )

    # 6. Multi-generational binding at epochal scope must have
    #    higher integrity than any non-multi-generational binding
    #    at epochal scope. Only multi-generational commitments can
    #    meaningfully address epochal horizons.
    multi_gen_epochal = _BINDING_INTEGRITY[TimeBinding.MULTI_GENERATIONAL][TemporalScope.EPOCHAL]
    for binding in TimeBinding:
        if binding == TimeBinding.MULTI_GENERATIONAL:
            continue
        other_epochal = _BINDING_INTEGRITY[binding][TemporalScope.EPOCHAL]
        assert multi_gen_epochal > other_epochal, (
            f"MULTI_GENERATIONAL binding at EPOCHAL scope must have "
            f"integrity higher than {binding.value}; got "
            f"{multi_gen_epochal} vs {other_epochal}"
        )

    # 7. Attention and Time substrate modifiers must be less than 1.0.
    #    Neither can be meaningfully bound over long periods without
    #    substantial degradation.
    assert _SUBSTRATE_BINDING_MODIFIER[InvestmentSubstrate.ATTENTION] < 1.0, (
        "Attention cannot be bound across long periods; modifier must be < 1.0"
    )
    assert _SUBSTRATE_BINDING_MODIFIER[InvestmentSubstrate.TIME] < 1.0, (
        "Time is consumed not preserved; modifier must be < 1.0"
    )

    # 8. Relational capital must have the highest binding modifier.
    #    Trust networks are the only substrate that compounds across
    #    generations when the network persists.
    rel_modifier = _SUBSTRATE_BINDING_MODIFIER[InvestmentSubstrate.RELATIONAL_CAPITAL]
    for sub in InvestmentSubstrate:
        if sub == InvestmentSubstrate.RELATIONAL_CAPITAL:
            continue
        assert rel_modifier >= _SUBSTRATE_BINDING_MODIFIER[sub], (
            f"RELATIONAL_CAPITAL must have highest substrate binding modifier; "
            f"got {rel_modifier} vs {sub.value}={_SUBSTRATE_BINDING_MODIFIER[sub]}"
        )


# ============================================================================
# DISPLAY
# ============================================================================

def format_binding_integrity() -> str:
    """
    Return a human-readable string of the binding integrity matrix.
    """
    scopes = list(TemporalScope)
    header = "              " + "  ".join(f"{s.name:>12}" for s in scopes)
    lines = [
        "Binding integrity B[binding][scope]:",
        header,
        "              " + "-" * (14 * len(scopes)),
    ]
    for binding in TimeBinding:
        row = f"{binding.name:>16} |"
        for scope in scopes:
            row += f" {_BINDING_INTEGRITY[binding][scope]:>12.2f}"
        lines.append(row)
    return "\n".join(lines)


def format_substrate_modifiers() -> str:
    """Return a human-readable string of substrate binding modifiers."""
    lines = ["Substrate binding modifiers:"]
    for sub in InvestmentSubstrate:
        mod = _SUBSTRATE_BINDING_MODIFIER[sub]
        marker = " <<" if mod >= 1.15 else (" (low)" if mod < 0.8 else "")
        lines.append(f"  {sub.value:>24}  {mod:.2f}{marker}")
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_time_binding()
    print("Time binding tables validated.")
    print()
    print(format_binding_integrity())
    print()
    print(format_substrate_modifiers())
    print()

    # Demonstration: retirement account with immediate liquidity
    # evaluated at generational scope.
    print("Case: liquid retirement account evaluated at generational scope")
    integrity = base_time_binding_integrity(
        TimeBinding.IMMEDIATE, TemporalScope.GENERATIONAL
    )
    severity = binding_scope_mismatch_severity(
        TimeBinding.IMMEDIATE, TemporalScope.GENERATIONAL
    )
    illusion = is_short_binding_long_scope(
        TimeBinding.IMMEDIATE, TemporalScope.GENERATIONAL
    )
    print(f"  binding integrity:    {integrity:.2f}")
    print(f"  mismatch severity:    {severity:.2f}")
    print(f"  liquidity illusion:   {illusion}")
    print()

    # Traditional ecological knowledge across an epochal horizon.
    print("Case: multi-generational knowledge evaluated at epochal scope")
    integrity = base_time_binding_integrity(
        TimeBinding.MULTI_GENERATIONAL, TemporalScope.EPOCHAL
    )
    with_relational = binding_integrity_with_substrate(
        TimeBinding.MULTI_GENERATIONAL,
        TemporalScope.EPOCHAL,
        InvestmentSubstrate.RELATIONAL_CAPITAL,
    )
    print(f"  base integrity:              {integrity:.2f}")
    print(f"  with relational substrate:   {with_relational:.2f}")
    print(f"  (only multi-generational bindings with relational or")
    print(f"   resource substrate survive epochal evaluation)")
    print()

    # Municipal bond at generational binding, evaluated at seasonal
    # political cycle.
    print("Case: generational municipal bond evaluated at seasonal scope")
    integrity = base_time_binding_integrity(
        TimeBinding.GENERATIONAL, TemporalScope.SEASONAL
    )
    trap = is_long_binding_short_scope(
        TimeBinding.GENERATIONAL, TemporalScope.SEASONAL
    )
    print(f"  binding integrity:            {integrity:.2f}")
    print(f"  infrastructure-depreciation:  {trap}")
