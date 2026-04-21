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
)
from money_signal.dimensions import StateRegime
from term_audit.provenance import Provenance, ProvenanceKind


def test_1_five_anchor_cases():
    print("\n--- TEST 1: five anchor cases registered ---")
    assert len(ALL_CASES) == 5
    expected = {
        "Weimar hyperinflation and Rentenmark stabilization",
        "Zimbabwe hyperinflation and dollarization",
        "Global Financial Crisis — near-collapse episode",
        "Cyprus bank haircut — observer-asymmetry case",
        "Argentine peso collapse and pesification",
    }
    names = {c.name for c in ALL_CASES}
    assert names == expected, f"FAIL: expected {expected}, got {names}"
    print(f"  {len(ALL_CASES)} anchor cases registered")
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


def test_3_every_during_context_near_collapse():
    """Selection criterion: anchor cases are NEAR_COLLAPSE episodes.
    If a case's DURING state drifts away, the anchor discipline is
    lost."""
    print("\n--- TEST 3: every DURING context is NEAR_COLLAPSE ---")
    for case in ALL_CASES:
        assert case.context_during.state == StateRegime.NEAR_COLLAPSE, \
            (f"FAIL: {case.name} DURING state = "
             f"{case.context_during.state.value}, not NEAR_COLLAPSE")
    print(f"  all {len(ALL_CASES)} cases have DURING state = NEAR_COLLAPSE")
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
    """LOAD-BEARING: 4 of 5 anchors qualitatively match the framework's
    K[N][R]-amplification-in-NEAR_COLLAPSE prediction. Cyprus is the
    expected non-match because it is primarily an observer-asymmetry
    case (claim #5), not a K[N][R] amplification case (claim #4).

    If this count changes, either the framework's factor values
    moved, the cases' observed_dynamics were edited, or the match
    criteria drifted. All three warrant explicit review."""
    print("\n--- TEST 6: expected qualitative match distribution ---")
    match_count = sum(1 for c in ALL_CASES if compare_case(c).qualitative_match)
    assert match_count == 4, \
        f"FAIL: expected 4/5 qualitative matches, got {match_count}/5"

    cyprus_cmp = compare_case(CYPRUS_2013)
    assert not cyprus_cmp.qualitative_match, \
        "FAIL: Cyprus is the expected observer-asymmetry outlier"

    for case in (WEIMAR_1921_1923, ZIMBABWE_2007_2009, GFC_2008, ARGENTINA_2001_2002):
        assert compare_case(case).qualitative_match, \
            f"FAIL: {case.name} expected to match but didn't"

    print(f"  4/5 qualitative matches; Cyprus correctly flagged as outlier")
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
    test_1_five_anchor_cases()
    test_2_observed_dynamics_have_provenance()
    test_3_every_during_context_near_collapse()
    test_4_predict_returns_finite()
    test_5_compare_case_runs()
    test_6_expected_match_distribution()
    test_7_no_fabricated_numeric_kij_values()
    print("\nall historical_cases tests passed.")
