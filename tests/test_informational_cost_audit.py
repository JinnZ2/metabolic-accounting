"""
tests/test_informational_cost_audit.py

Tripwires for term_audit/informational_cost_audit.py (AUDIT_16).

Tests lock:
  1. module imports; the nine documented knowledge structures are
     all present and non-empty
  2. ANOMALIES_UNDER_GEOCENTRISM covers four canonical anomalies,
     each with observation / problem / solution / cost fields
  3. INFORMATION_COST_ACCUMULATION has exactly four stages in the
     documented order (comfort → first anomaly → more anomalies →
     collapse)
  4. VERDICT declares comfort as expensive + uncertainty as cheap
     (load-bearing: if these flip, the module has lost its thesis)
  5. CostLedger ships with both canonical strategies
     (geocentric_comfort, scope_bounded_uncertainty); the
     geocentric ledger has exponential per-anomaly cost and
     catastrophic regime-shift cost; the scope-bounded ledger has
     linear and flat
  6. compare() refuses to collapse to a scalar (returns a dict of
     per-dimension strings, not a number) — this is the anti-
     false-certainty discipline the module warns against
  7. the module cross-references study_scope_audit in its CLI
     output (pair invariant)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.informational_cost_audit import (
    GEOCENTRIC_COMFORT_STATE,
    ANOMALIES_UNDER_GEOCENTRISM,
    INFORMATION_COST_ACCUMULATION,
    HELIOCENTRIC_UNCERTAINTY_STATE,
    INFORMATION_COST_AUDIT,
    INFORMATION_THEORY_INSIGHT,
    AI_IMPLICATIONS,
    HISTORICAL_PATTERN,
    VERDICT,
    CostGrowth, CostLedger,
    GEOCENTRIC_LEDGER, HELIOCENTRIC_LEDGER,
    compare,
)


def test_1_all_knowledge_structures_present():
    print("\n--- TEST 1: nine knowledge structures present + non-empty ---")
    for name, obj in [
        ("GEOCENTRIC_COMFORT_STATE", GEOCENTRIC_COMFORT_STATE),
        ("ANOMALIES_UNDER_GEOCENTRISM", ANOMALIES_UNDER_GEOCENTRISM),
        ("INFORMATION_COST_ACCUMULATION", INFORMATION_COST_ACCUMULATION),
        ("HELIOCENTRIC_UNCERTAINTY_STATE", HELIOCENTRIC_UNCERTAINTY_STATE),
        ("INFORMATION_COST_AUDIT", INFORMATION_COST_AUDIT),
        ("INFORMATION_THEORY_INSIGHT", INFORMATION_THEORY_INSIGHT),
        ("AI_IMPLICATIONS", AI_IMPLICATIONS),
        ("HISTORICAL_PATTERN", HISTORICAL_PATTERN),
        ("VERDICT", VERDICT),
    ]:
        assert obj, f"FAIL: {name} empty"
    print(f"  9/9 knowledge structures present")
    print("PASS")


def test_2_four_canonical_anomalies():
    print("\n--- TEST 2: four canonical geocentric anomalies present ---")
    expected = {
        "retrograde_motion_of_planets",
        "venus_phases",
        "stellar_parallax",
        "moons_of_jupiter",
    }
    assert set(ANOMALIES_UNDER_GEOCENTRISM.keys()) == expected
    for name, entry in ANOMALIES_UNDER_GEOCENTRISM.items():
        assert "observation" in entry and entry["observation"].strip()
        assert "geocentric_problem" in entry and entry["geocentric_problem"].strip()
        assert "geocentric_solution" in entry and entry["geocentric_solution"].strip()
        assert "cost" in entry and entry["cost"].strip()
    print(f"  4 anomalies, each with observation/problem/solution/cost")
    print("PASS")


def test_3_cost_accumulation_four_stages_in_order():
    """LOAD-BEARING: the spiral has four documented stages in the
    order comfort → first anomaly → more anomalies → collapse.
    The narrative sequence is the module's argument structure."""
    print("\n--- TEST 3: four-stage accumulation in documented order ---")
    expected_order = [
        "stage_1_comfort",
        "stage_2_first_anomaly",
        "stage_3_more_anomalies",
        "stage_4_system_collapse",
    ]
    assert list(INFORMATION_COST_ACCUMULATION.keys()) == expected_order
    print(f"  4 stages in order: {' -> '.join(expected_order)}")
    print("PASS")


def test_4_verdict_invariants():
    """LOAD-BEARING: VERDICT declares comfort expensive + uncertainty
    cheap. Flipping either boolean would invert the module's thesis.
    The one_liner must also be present (the module's compressed
    statement)."""
    print("\n--- TEST 4: VERDICT invariants ---")
    assert VERDICT.get("comfort_is_expensive") is True
    assert VERDICT.get("uncertainty_is_cheap") is True
    assert VERDICT.get("but_only_if_measured_over_sufficient_time_horizon") is True
    assert "one_liner" in VERDICT and "false certainty" in VERDICT["one_liner"]
    print(f"  comfort=expensive, uncertainty=cheap, time-horizon caveat present")
    print("PASS")


def test_5_canonical_cost_ledgers():
    print("\n--- TEST 5: canonical CostLedgers carry expected growth tags ---")
    assert isinstance(GEOCENTRIC_LEDGER, CostLedger)
    assert isinstance(HELIOCENTRIC_LEDGER, CostLedger)

    assert GEOCENTRIC_LEDGER.cost_per_anomaly == CostGrowth.EXPONENTIAL
    assert GEOCENTRIC_LEDGER.cost_at_regime_shift == CostGrowth.CATASTROPHIC
    assert GEOCENTRIC_LEDGER.short_horizon_apparent_cost == "cheap"
    assert GEOCENTRIC_LEDGER.long_horizon_actual_cost == "ruinous"

    assert HELIOCENTRIC_LEDGER.cost_per_anomaly == CostGrowth.LINEAR
    assert HELIOCENTRIC_LEDGER.cost_at_regime_shift == CostGrowth.FLAT
    assert HELIOCENTRIC_LEDGER.short_horizon_apparent_cost == "expensive"
    assert HELIOCENTRIC_LEDGER.long_horizon_actual_cost == "manageable"

    print(f"  geocentric:    anomaly=EXPONENTIAL, regime=CATASTROPHIC")
    print(f"  scope-bounded: anomaly=LINEAR,      regime=FLAT")
    print("PASS")


def test_6_compare_refuses_scalar_collapse():
    """LOAD-BEARING: `compare()` must return a per-dimension dict,
    not a single scalar score. Collapsing to a scalar is exactly
    the false-certainty compression the module warns against; if
    someone adds a 'total_score' field, this test catches it."""
    print("\n--- TEST 6: compare() refuses scalar collapse ---")
    result = compare(GEOCENTRIC_LEDGER, HELIOCENTRIC_LEDGER)
    assert isinstance(result, dict)
    # expected per-dimension keys
    for key in ("initial_cost", "cost_per_anomaly", "cost_at_regime_shift",
                "short_horizon_apparent", "long_horizon_actual"):
        assert key in result, f"FAIL: missing dimension {key}"
        assert isinstance(result[key], str)
    # no scalar/numeric keys sneak in
    forbidden = {"total_score", "overall", "score", "verdict_scalar"}
    assert not (set(result.keys()) & forbidden), \
        f"FAIL: scalar-collapse key detected in {result.keys()}"
    print(f"  5 dimensions returned as strings; no scalar collapse")
    print("PASS")


def test_7_cross_reference_to_study_scope_audit():
    """The module's value is partly in being the PAIR to
    study_scope_audit. The CLI demo must reference it explicitly
    so downstream readers see the pairing."""
    print("\n--- TEST 7: CLI cross-references study_scope_audit ---")
    import io
    import contextlib
    from term_audit.informational_cost_audit import _demo
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _demo()
    out = buf.getvalue()
    assert "study_scope_audit" in out, \
        "FAIL: CLI output does not reference study_scope_audit"
    print(f"  CLI output references study_scope_audit (pair invariant)")
    print("PASS")


if __name__ == "__main__":
    test_1_all_knowledge_structures_present()
    test_2_four_canonical_anomalies()
    test_3_cost_accumulation_four_stages_in_order()
    test_4_verdict_invariants()
    test_5_canonical_cost_ledgers()
    test_6_compare_refuses_scalar_collapse()
    test_7_cross_reference_to_study_scope_audit()
    print("\nall informational_cost_audit tests passed.")
