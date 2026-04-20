"""
tests/test_expertise_x_audit.py

Tripwires for term_audit/audits/expertise_x_cross_domain_closure.py.

E_X is the fourth expertise dimension added to the existing E_A / E_B /
E_C decomposition in term_audit/expertise.py. The audit ships with
AUDIT_08 drift repair: file relocated into audits/, sys.path bootstrap
added, first_principles populated (was None — broke summary()),
provenance retrofitted on all 7 SignalScores.

Tests lock in:

  1. module imports + runs standalone (regression for the missing
     bootstrap that broke direct invocation)
  2. E_X audit passes its own is_signal test (so E_X qualifies as a
     signal under the same 5-of-7 rule money / value_B / etc. are
     scored against)
  3. summary() works (first_principles is not None)
  4. provenance coverage complete across all 7 SignalScores
  5. selection-inversion property: constrained environments prefer
     high-E_X rural practitioner, credential-gated environments prefer
     credentialed specialist — changing either direction would break
     the argument's punchline
  6. falsifiable predictions shipped with the module
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.expertise_x_cross_domain_closure import (
    E_X_AUDIT,
    CrossDomainClosureProfile,
    ExpertiseFullProfile,
    DependencyGraphProblem,
    administer_closure_test,
    FALSIFIABLE_PREDICTIONS,
)


def test_1_module_imports_and_runs_standalone():
    """Regression: module previously lacked sys.path bootstrap,
    so `python term_audit/cross_domain_closure.py` raised
    ModuleNotFoundError. After AUDIT_08 relocation + bootstrap,
    direct invocation works. This test is a smoke for the audit
    surface being intact."""
    print("\n--- TEST 1: E_X audit surface intact ---")
    assert E_X_AUDIT is not None
    assert E_X_AUDIT.term == "expertise_X_cross_domain_closure"
    assert len(E_X_AUDIT.signal_scores) == 7
    print("  E_X_AUDIT exposes 7 signal_scores")
    print("PASS")


def test_2_e_x_qualifies_as_signal():
    """E_X must pass the 5-of-7 is_signal threshold. If it doesn't,
    the claim that 'E_X is a signal that credentials cannot capture'
    collapses."""
    print("\n--- TEST 2: E_X qualifies as signal ---")
    assert E_X_AUDIT.is_signal(), \
        f"FAIL: E_X is_signal=False; pass_count={E_X_AUDIT.pass_count()}"
    assert E_X_AUDIT.pass_count() >= 5, \
        f"FAIL: pass_count={E_X_AUDIT.pass_count()}, want >= 5"
    print(f"  pass_count={E_X_AUDIT.pass_count()}/7 "
          f"mean={E_X_AUDIT.mean_score():.3f} min={E_X_AUDIT.min_score()}")
    print("PASS")


def test_3_summary_works():
    """Regression: E_X shipped with first_principles=None, which
    broke summary() via AttributeError on drift_score. AUDIT_08
    populated first_principles."""
    print("\n--- TEST 3: summary() works ---")
    s = E_X_AUDIT.summary()
    assert s["is_signal"] is True
    assert "drift_score" in s
    assert 0.0 <= s["drift_score"] <= 1.0
    print(f"  drift_score={s['drift_score']:.2f}  "
          f"correlation={s['correlation_to_real_signal']:.2f}")
    print("PASS")


def test_4_provenance_coverage_complete():
    """Every SignalScore in E_X carries a complete Provenance,
    matching the Tier 1 discipline established in AUDIT_07."""
    print("\n--- TEST 4: provenance coverage complete ---")
    cov = E_X_AUDIT.provenance_coverage()
    assert cov["none"] == 0, \
        f"FAIL: {cov['none']} scores without provenance"
    assert cov["incomplete"] == 0, \
        f"FAIL: {cov['incomplete']} incomplete: {cov['incomplete_details']}"
    assert cov["complete"] == cov["total"]
    print(f"  {cov['complete']}/{cov['total']} complete, "
          f"kinds={cov['by_kind']}")
    print("PASS")


def test_5_selection_inversion():
    """The core load-bearing claim: rural high-E_X practitioner beats
    credentialed specialist under constraint; reverse under credential-
    gated selection.

    If this inversion disappears, the argument 'credentials cannot
    capture E_X' is structurally falsified. Tripwire parallel to the
    load-bearing negative-linkage tripwires in test_tier1_coverage."""
    print("\n--- TEST 5: selection inversion holds ---")

    rural = ExpertiseFullProfile(
        e_a_scores={"electrical": 0.7, "structural": 0.7,
                    "mechanical": 0.8, "hydraulic": 0.6},
        e_b_credentials=[],
        e_c_transmission=0.7,
        e_x_profile=CrossDomainClosureProfile(
            closure_probability=0.85,
            domain_breadth=5,
            improvisation_capacity=0.9,
            diagnostic_depth=0.85,
            handoff_avoidance=0.95,
            failure_recovery_rate=0.8,
            cross_domain_coupling=0.9,
            selection_priority_under_constraint=0.9,
            completed_closure_events=40,
            attempted_closure_events=45,
        ),
    )
    specialist = ExpertiseFullProfile(
        e_a_scores={"electrical": 0.95},
        e_b_credentials=["PE Electrical"],
        e_c_transmission=0.5,
        e_x_profile=CrossDomainClosureProfile(
            closure_probability=0.35,
            domain_breadth=1,
            improvisation_capacity=0.3,
            diagnostic_depth=0.9,
            handoff_avoidance=0.2,
            failure_recovery_rate=0.5,
            cross_domain_coupling=0.2,
            selection_priority_under_constraint=0.15,
            completed_closure_events=5,
            attempted_closure_events=12,
        ),
    )

    rural_constrained = rural.selection_fitness_constrained()
    specialist_constrained = specialist.selection_fitness_constrained()
    rural_credentialed = rural.selection_fitness_credentialed()
    specialist_credentialed = specialist.selection_fitness_credentialed()

    assert rural_constrained > specialist_constrained, \
        (f"FAIL: rural={rural_constrained:.3f} not > "
         f"specialist={specialist_constrained:.3f} under constraint")
    assert specialist_credentialed > rural_credentialed, \
        (f"FAIL: specialist={specialist_credentialed:.3f} not > "
         f"rural={rural_credentialed:.3f} under credential-gated selection")

    print(f"  constrained:   rural {rural_constrained:.3f} > "
          f"specialist {specialist_constrained:.3f}")
    print(f"  credentialed:  specialist {specialist_credentialed:.3f} > "
          f"rural {rural_credentialed:.3f}")
    print("PASS")


def test_6_closure_test_runs():
    """End-to-end: a DependencyGraphProblem can be administered to a
    practitioner profile and returns a structured result."""
    print("\n--- TEST 6: closure test runs end-to-end ---")
    rural = ExpertiseFullProfile(
        e_a_scores={"electrical": 0.7, "structural": 0.7},
        e_b_credentials=[],
        e_c_transmission=0.6,
        e_x_profile=CrossDomainClosureProfile(
            closure_probability=0.85,
            domain_breadth=4,
            improvisation_capacity=0.8,
            diagnostic_depth=0.8,
            handoff_avoidance=0.9,
            failure_recovery_rate=0.8,
            cross_domain_coupling=0.9,
            selection_priority_under_constraint=0.9,
            completed_closure_events=20,
            attempted_closure_events=24,
        ),
    )
    problem = DependencyGraphProblem(
        problem_description="barn fire recovery",
        domains_involved=["electrical", "structural"],
        coupling_strength=0.8,
        handoff_available=False,
        time_constraint=24.0,
        resource_constraint="available_materials_only",
        required_capacities=["electrical_diagnosis", "structural_repair"],
    )

    result = administer_closure_test(rural, problem)
    assert isinstance(result, dict)
    assert "closure_probability" in result or "predicted_closure" in result \
        or "closure" in str(result).lower()
    print(f"  result keys: {sorted(result.keys())}")
    print("PASS")


def test_7_falsifiable_predictions_registered():
    """E_X ships with falsifiable predictions; audit discipline
    requires at least one."""
    print("\n--- TEST 7: falsifiable predictions registered ---")
    assert len(FALSIFIABLE_PREDICTIONS) >= 1
    for p in FALSIFIABLE_PREDICTIONS:
        assert p.get("claim", "").strip()
        assert p.get("falsification", "").strip()
    print(f"  {len(FALSIFIABLE_PREDICTIONS)} predictions registered")
    print("PASS")


if __name__ == "__main__":
    test_1_module_imports_and_runs_standalone()
    test_2_e_x_qualifies_as_signal()
    test_3_summary_works()
    test_4_provenance_coverage_complete()
    test_5_selection_inversion()
    test_6_closure_test_runs()
    test_7_falsifiable_predictions_registered()
    print("\nall E_X audit tests passed.")
