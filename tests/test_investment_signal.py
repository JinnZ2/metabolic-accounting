"""
tests/test_investment_signal.py

Tripwires for the investment_signal/ subsystem (AUDIT_13 intake).

Locks in:

  1. all 7 modules import (regression for the ..money_signal
     relative-import bug fixed at intake)
  2. validate_all_investment_modules passes
  3. README usage example runs end-to-end and produces the expected
     failure modes
  4-12. targeted tripwires for 9 of the 23 README falsifiable claims
     (the rest are covered indirectly by the validators)

AUDIT_13 documents the import-convention bug and the intake context.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_1_all_modules_import():
    """Regression: three files shipped with `..money_signal` relative
    imports that fail because investment_signal/ and money_signal/
    are sibling top-level packages. Fixed at intake."""
    print("\n--- TEST 1: all 7 modules import ---")
    import investment_signal.dimensions
    import investment_signal.substrate_vectors
    import investment_signal.conversion_matrix
    import investment_signal.realization_matrix
    import investment_signal.time_binding
    import investment_signal.derivative_distance
    import investment_signal.coupling
    print("  7/7 modules imported")
    print("PASS")


def test_2_validate_all_passes():
    print("\n--- TEST 2: validate_all_investment_modules() passes ---")
    from investment_signal.coupling import validate_all_investment_modules
    validate_all_investment_modules()
    print("  all factor validators pass")
    print("PASS")


def test_3_readme_usage_example_runs():
    """The README usage example runs verbatim and returns the
    documented failure modes (liquidity_illusion from IMMEDIATE
    binding on GENERATIONAL scope + substrate_abstraction_destroys_nature
    from trying to derivatize ATTENTION at TWO_LAYER distance)."""
    print("\n--- TEST 3: README usage example runs end-to-end ---")
    from investment_signal.dimensions import (
        InvestmentContext, InvestmentSubstrate,
        InvestmentAttribution, DerivativeDistance, TimeBinding,
    )
    from investment_signal.substrate_vectors import SubstrateVector
    from investment_signal.coupling import (
        assemble_investment_signal, signal_failure_count,
        signal_failure_reasons,
    )
    from money_signal.dimensions import (
        DimensionalContext as MoneyContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    money = MoneyContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.STRESSED,
    )
    ctx = InvestmentContext(
        money_context=money,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.TWO_LAYER,
        time_binding=TimeBinding.IMMEDIATE,
    )
    input_vec = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 50000.0,
        InvestmentSubstrate.ATTENTION: 20.0,
    })
    expected_vec = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 150000.0,
        InvestmentSubstrate.TIME: 1000.0,
    })
    signal = assemble_investment_signal(input_vec, expected_vec, ctx)
    reasons = set(signal_failure_reasons(signal))
    assert "liquidity_illusion" in reasons, \
        f"FAIL: liquidity_illusion not in {reasons}"
    assert "substrate_abstraction_destroys_nature" in reasons, \
        f"FAIL: substrate_abstraction_destroys_nature not in {reasons}"
    assert signal_failure_count(signal) >= 2
    print(f"  failures: {sorted(reasons)}")
    print("PASS")


def test_4_monetizing_relational_destroys_it():
    """README claim #1: C[RELATIONAL_CAPITAL][MONEY] <= 0.3."""
    print("\n--- TEST 4: README claim #1 monetizing relational destroys ---")
    from investment_signal.conversion_matrix import base_conversion
    from investment_signal.dimensions import InvestmentSubstrate as S
    v = base_conversion(S.RELATIONAL_CAPITAL, S.MONEY)
    assert v <= 0.3, f"FAIL: C[REL][MONEY]={v} not <= 0.3"
    print(f"  C[RELATIONAL][MONEY]={v:.2f} <= 0.3")
    print("PASS")


def test_5_money_cannot_buy_relational():
    """README claim #2: C[MONEY][RELATIONAL_CAPITAL] <= 0.3."""
    print("\n--- TEST 5: README claim #2 money cannot buy relational ---")
    from investment_signal.conversion_matrix import base_conversion
    from investment_signal.dimensions import InvestmentSubstrate as S
    v = base_conversion(S.MONEY, S.RELATIONAL_CAPITAL)
    assert v <= 0.3, f"FAIL: C[MONEY][REL]={v} not <= 0.3"
    print(f"  C[MONEY][RELATIONAL]={v:.2f} <= 0.3")
    print("PASS")


def test_6_same_substrate_realization_bounded():
    """README claim #5: 0.5 <= R[i][i] < 1.0 for every substrate."""
    print("\n--- TEST 6: README claim #5 same-substrate realization bounded ---")
    from investment_signal.realization_matrix import base_realization
    from investment_signal.dimensions import InvestmentSubstrate
    for s in InvestmentSubstrate:
        v = base_realization(s, s)
        assert 0.5 <= v < 1.0, f"FAIL: R[{s.value}][{s.value}]={v} not in [0.5, 1.0)"
    print(f"  all 7 substrates: R[i][i] in [0.5, 1.0)")
    print("PASS")


def test_7_money_nominal_realization_high():
    """README claim #9: R[MONEY][MONEY] >= 0.85 nominal."""
    print("\n--- TEST 7: README claim #9 money nominal realization ---")
    from investment_signal.realization_matrix import base_realization
    from investment_signal.dimensions import InvestmentSubstrate as S
    v = base_realization(S.MONEY, S.MONEY)
    assert v >= 0.85, f"FAIL: R[MONEY][MONEY]={v} not >= 0.85"
    print(f"  R[MONEY][MONEY]={v:.2f} >= 0.85 (nominal)")
    print("PASS")


def test_8_liquidity_illusion_severe():
    """README claim #11: short binding + long scope = severity >= 0.5."""
    print("\n--- TEST 8: README claim #11 liquidity illusion severity ---")
    from investment_signal.time_binding import binding_scope_mismatch_severity
    from investment_signal.dimensions import TimeBinding
    from money_signal.dimensions import TemporalScope
    for binding in (TimeBinding.IMMEDIATE, TimeBinding.SHORT_CYCLE):
        for scope in (TemporalScope.GENERATIONAL, TemporalScope.EPOCHAL):
            sev = binding_scope_mismatch_severity(binding, scope)
            assert sev >= 0.5, \
                f"FAIL: {binding.value}×{scope.value} severity={sev} not >= 0.5"
    print(f"  (IMMEDIATE, SHORT_CYCLE) × (GENERATIONAL, EPOCHAL): severity >= 0.5 in all 4")
    print("PASS")


def test_9_signal_monotone_in_distance():
    """README claim #15: signal reliability decreases monotonically
    with derivative distance."""
    print("\n--- TEST 9: README claim #15 signal monotone in distance ---")
    from investment_signal.derivative_distance import signal_reliability
    from investment_signal.dimensions import DerivativeDistance
    ordered = [
        DerivativeDistance.DIRECT,
        DerivativeDistance.ONE_LAYER,
        DerivativeDistance.TWO_LAYER,
        DerivativeDistance.DERIVATIVE,
        DerivativeDistance.SYNTHETIC,
    ]
    vals = [signal_reliability(d) for d in ordered]
    for a, b in zip(vals, vals[1:]):
        assert a > b, f"FAIL: reliability not monotone: {vals}"
    print(f"  reliability: {[f'{v:.2f}' for v in vals]}")
    print("PASS")


def test_10_synthetic_financialized():
    """README claim #20: SYNTHETIC reverse causation >= 0.5."""
    print("\n--- TEST 10: README claim #20 SYNTHETIC financialized ---")
    from investment_signal.derivative_distance import reverse_causation, is_financialized
    from investment_signal.dimensions import DerivativeDistance
    v = reverse_causation(DerivativeDistance.SYNTHETIC)
    assert v >= 0.5, f"FAIL: SYNTHETIC reverse_causation={v} not >= 0.5"
    assert is_financialized(DerivativeDistance.SYNTHETIC) is True
    print(f"  SYNTHETIC reverse_causation={v:.2f} >= 0.5, is_financialized=True")
    print("PASS")


def test_11_money_highest_abstraction_tolerance():
    """README claim #22: MONEY has the highest abstraction tolerance."""
    print("\n--- TEST 11: README claim #22 money highest abstraction tolerance ---")
    from investment_signal.derivative_distance import substrate_abstraction_tolerance
    from investment_signal.dimensions import InvestmentSubstrate
    tolerances = {
        s: substrate_abstraction_tolerance(s) for s in InvestmentSubstrate
    }
    money_tol = tolerances[InvestmentSubstrate.MONEY]
    for s, t in tolerances.items():
        if s == InvestmentSubstrate.MONEY:
            continue
        assert money_tol >= t, \
            f"FAIL: MONEY tol={money_tol} not >= {s.value} tol={t}"
    print(f"  MONEY tolerance={money_tol:.2f} is max across substrates")
    print("PASS")


def test_12_near_collapse_breaks_evaluation():
    """README claim #23: investment cannot be evaluated when money
    is in near-collapse. dependency_broken=True."""
    print("\n--- TEST 12: README claim #23 near-collapse breaks evaluation ---")
    from investment_signal.dimensions import (
        InvestmentContext, InvestmentSubstrate,
        InvestmentAttribution, DerivativeDistance, TimeBinding,
    )
    from investment_signal.substrate_vectors import SubstrateVector
    from investment_signal.coupling import assemble_investment_signal
    from money_signal.dimensions import (
        DimensionalContext as MoneyContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    money = MoneyContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.NEAR_COLLAPSE,
    )
    ctx = InvestmentContext(
        money_context=money,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.DIRECT,
        time_binding=TimeBinding.MULTI_YEAR,
    )
    input_vec = SubstrateVector.from_dict({InvestmentSubstrate.MONEY: 1000.0})
    expected_vec = SubstrateVector.from_dict({InvestmentSubstrate.MONEY: 2000.0})
    signal = assemble_investment_signal(input_vec, expected_vec, ctx)
    assert signal.dependency_broken is True, \
        "FAIL: dependency_broken should be True under NEAR_COLLAPSE money"
    print(f"  dependency_broken=True under NEAR_COLLAPSE money; all returns unreliable")
    print("PASS")


if __name__ == "__main__":
    test_1_all_modules_import()
    test_2_validate_all_passes()
    test_3_readme_usage_example_runs()
    test_4_monetizing_relational_destroys_it()
    test_5_money_cannot_buy_relational()
    test_6_same_substrate_realization_bounded()
    test_7_money_nominal_realization_high()
    test_8_liquidity_illusion_severe()
    test_9_signal_monotone_in_distance()
    test_10_synthetic_financialized()
    test_11_money_highest_abstraction_tolerance()
    test_12_near_collapse_breaks_evaluation()
    print("\nall investment_signal tests passed.")
