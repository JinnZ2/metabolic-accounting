"""
tests/test_historical_cases.py

Tripwires for money_signal/historical_cases.py (AUDIT_12).

Locks in:
  1. all 5 anchor cases construct with the expected period/location
  2. each case has at least one ObservedDynamic with a complete
     Provenance (EMPIRICAL or PLACEHOLDER with retirement_path)
  3. every DURING context has state = NEAR_COLLAPSE (the module's
     selection criterion is "well-documented monetary events where
     coupling broke down")
  4. predict() returns finite values on every anchor context
  5. compare_case() runs on every anchor without error
  6. the framework qualitatively matches 4 of the 5 anchors. Cyprus
     is the expected outlier (observer-asymmetry case, not primary
     K[N][R] amplification). If the match count changes, the change
     is load-bearing and requires either factor-value work or case
     re-curation — not silent test adjustment.
  7. no case fabricates numeric K_ij values — every ObservedDynamic
     uses a qualitative DynamicShift enum, not a float
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from money_signal.historical_cases import (
    ALL_CASES, HistoricalCase, ObservedDynamic, DynamicShift,
    FrameworkPrediction, CaseComparison,
    predict, compare_case,
    WEIMAR_1921_1923, ZIMBABWE_2007_2009, GFC_2008,
    CYPRUS_2013, ARGENTINA_2001_2002,
    BITCOIN_FLASH_CRASHES, ROMAN_DENARIUS_DEBASEMENT,
    YAP_RAI_STONES, KULA_RING_EXCHANGE,
)

# AUDIT_18 added 4 anchor cases (Bitcoin, Roman denarius, Yap,
# Kula). Yap and Kula are counter-examples — DURING state is
# HEALTHY, not NEAR_COLLAPSE — so the "every DURING is
# NEAR_COLLAPSE" claim no longer holds across the full set. Tests
# below partition the anchors by role.
NEAR_COLLAPSE_CASES = [
    WEIMAR_1921_1923, ZIMBABWE_2007_2009, GFC_2008,
    CYPRUS_2013, ARGENTINA_2001_2002,
    BITCOIN_FLASH_CRASHES,
]
STRESSED_CASES = [ROMAN_DENARIUS_DEBASEMENT]
COUNTER_EXAMPLES = [YAP_RAI_STONES, KULA_RING_EXCHANGE]
from money_signal.dimensions import StateRegime
from term_audit.provenance import Provenance, ProvenanceKind


def test_1_all_anchor_cases():
    """AUDIT_12 shipped 5 anchor cases; AUDIT_18 extended to 9.
    Load-bearing: the registered set must match exactly, with
    partitioning by role (near-collapse, stressed, counter-example)."""
    print("\n--- TEST 1: nine anchor cases registered + partitioned ---")
    assert len(ALL_CASES) == 9
    expected = {
        "Weimar hyperinflation and Rentenmark stabilization",
        "Zimbabwe hyperinflation and dollarization",
        "Global Financial Crisis — near-collapse episode",
        "Cyprus bank haircut — observer-asymmetry case",
        "Argentine peso collapse and pesification",
        "Bitcoin flash crashes — digital speculative cascades",
        "Roman denarius debasement — multi-generational metal slide",
        "Yap rai stones — trust-ledger substrate, multi-generational",
        "Kula ring — Melanesian reciprocity network",
    }
    names = {c.name for c in ALL_CASES}
    assert names == expected, f"FAIL: expected {expected}, got {names}"
    partitioned_names = {c.name for c in NEAR_COLLAPSE_CASES} \
        | {c.name for c in STRESSED_CASES} \
        | {c.name for c in COUNTER_EXAMPLES}
    assert partitioned_names == expected, \
        "FAIL: test-time partitioning must cover every anchor case"
    print(f"  {len(ALL_CASES)} anchors: "
          f"{len(NEAR_COLLAPSE_CASES)} near-collapse, "
          f"{len(STRESSED_CASES)} stressed, "
          f"{len(COUNTER_EXAMPLES)} counter-examples")
    print("PASS")


def test_2_observed_dynamics_have_provenance():
    """Per AUDIT_07 discipline: every numeric or structural claim
    carries typed Provenance. ObservedDynamic's shift is qualitative
    but it is still a claim about history — provenance required."""
    print("\n--- TEST 2: observed dynamics carry complete Provenance ---")
    total_dynamics = 0
    for case in ALL_CASES:
        assert case.observed_dynamics, f"FAIL: {case.name} has no observed_dynamics"
        for dyn in case.observed_dynamics:
            total_dynamics += 1
            assert isinstance(dyn.provenance, Provenance), \
                f"FAIL: {case.name}/{dyn.term_i}-{dyn.term_j} lacks Provenance"
            missing = dyn.provenance.missing_fields()
            assert not missing, (
                f"FAIL: {case.name}/{dyn.term_i}-{dyn.term_j} has incomplete "
                f"{dyn.provenance.kind.value} provenance; missing: {missing}"
            )
    print(f"  {total_dynamics} ObservedDynamics across {len(ALL_CASES)} cases, "
          f"all with complete Provenance")
    print("PASS")


def test_3_during_state_matches_case_role():
    """Selection discipline by role:
      - near-collapse anchors: DURING state = NEAR_COLLAPSE
      - stressed anchors (Roman denarius): DURING state = STRESSED
      - counter-examples (Yap, Kula): DURING state = HEALTHY
    If a case drifts across these roles, the anchor partitioning is
    lost and the framework-vs-observed comparison stops being
    meaningful."""
    print("\n--- TEST 3: DURING state matches case role ---")
    for case in NEAR_COLLAPSE_CASES:
        assert case.context_during.state == StateRegime.NEAR_COLLAPSE, \
            (f"FAIL: {case.name} should be NEAR_COLLAPSE, got "
             f"{case.context_during.state.value}")
    for case in STRESSED_CASES:
        assert case.context_during.state == StateRegime.STRESSED, \
            (f"FAIL: {case.name} should be STRESSED, got "
             f"{case.context_during.state.value}")
    for case in COUNTER_EXAMPLES:
        assert case.context_during.state == StateRegime.HEALTHY, \
            (f"FAIL: {case.name} counter-example should be HEALTHY, got "
             f"{case.context_during.state.value}")
    print(f"  6 NEAR_COLLAPSE + 1 STRESSED + 2 HEALTHY anchors partition cleanly")
    print("PASS")


def test_4_predict_returns_finite():
    print("\n--- TEST 4: predict() returns finite on every anchor ---")
    import math
    for case in ALL_CASES:
        p = predict(case.context_during)
        assert isinstance(p, FrameworkPrediction)
        assert math.isfinite(p.minsky)
        assert math.isfinite(p.coupling_magnitude)
        assert isinstance(p.has_sign_flips, bool)
        print(f"  {case.name[:40]:<40s}  minsky={p.minsky:.2f} mag={p.coupling_magnitude:.2f}")
    print("PASS")


def test_5_compare_case_runs():
    print("\n--- TEST 5: compare_case runs on every anchor ---")
    for case in ALL_CASES:
        cmp = compare_case(case)
        assert isinstance(cmp, CaseComparison)
        assert cmp.case is case
        assert isinstance(cmp.qualitative_match, bool)
    print(f"  {len(ALL_CASES)} comparisons complete")
    print("PASS")


def test_6_expected_match_distribution():
    """LOAD-BEARING: AUDIT_18 tightened the `predicted_n_r_high`
    criterion to require both elevated Minsky AND elevated
    coupling_magnitude (not just the ratio). This correctly
    classifies Yap/Kula as non-amplification counter-examples.

    Expected post-AUDIT_18 match: 8 of 9 anchors. Cyprus remains
    the single outlier — it is primarily an observer-asymmetry
    case (claim #5), not a K[N][R] amplification case.

    If this count changes, either factor values moved, observed
    dynamics were edited, or the match criteria drifted. All three
    warrant explicit review."""
    print("\n--- TEST 6: expected qualitative match distribution (8/9) ---")
    results = {c.name: compare_case(c) for c in ALL_CASES}
    match_count = sum(1 for r in results.values() if r.qualitative_match)
    assert match_count == 8, \
        f"FAIL: expected 8/9 qualitative matches, got {match_count}/9"

    # Cyprus is the documented outlier
    assert not results[CYPRUS_2013.name].qualitative_match, \
        "FAIL: Cyprus is the expected observer-asymmetry outlier"

    # The counter-examples must match (framework predicts LOW magnitude
    # → no amplification, observed no amplification → match).
    assert results[YAP_RAI_STONES.name].qualitative_match, \
        "FAIL: Yap counter-example must match under the tightened criterion"
    assert results[KULA_RING_EXCHANGE.name].qualitative_match, \
        "FAIL: Kula counter-example must match under the tightened criterion"

    # The near-collapse + Roman stressed cases must all match.
    for case in (WEIMAR_1921_1923, ZIMBABWE_2007_2009, GFC_2008,
                 ARGENTINA_2001_2002, BITCOIN_FLASH_CRASHES,
                 ROMAN_DENARIUS_DEBASEMENT):
        assert results[case.name].qualitative_match, \
            f"FAIL: {case.name} expected to match but didn't"

    print(f"  8/9 qualitative matches; Cyprus correctly flagged as outlier")
    print(f"  counter-examples (Yap, Kula) classified correctly under tightened criterion")
    print("PASS")


def test_7_no_fabricated_numeric_kij_values():
    """The module explicitly refuses to fabricate quantitative K_ij
    values. Every ObservedDynamic's shift is a DynamicShift enum
    (qualitative direction), not a float. This is the honesty hook
    — if someone adds a float-valued shift, the test catches it."""
    print("\n--- TEST 7: no fabricated numeric K_ij values ---")
    for case in ALL_CASES:
        for dyn in case.observed_dynamics:
            assert isinstance(dyn.shift, DynamicShift), \
                (f"FAIL: {case.name}/{dyn.term_i}-{dyn.term_j} shift is "
                 f"{type(dyn.shift).__name__}, expected DynamicShift enum")
    print(f"  all shifts use qualitative DynamicShift enum (no fabricated floats)")
    print("PASS")


if __name__ == "__main__":
    test_1_all_anchor_cases()
    test_2_observed_dynamics_have_provenance()
    test_3_during_state_matches_case_role()
    test_4_predict_returns_finite()
    test_5_compare_case_runs()
    test_6_expected_match_distribution()
    test_7_no_fabricated_numeric_kij_values()
    print("\nall historical_cases tests passed.")
