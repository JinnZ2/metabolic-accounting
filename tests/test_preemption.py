"""
tests/test_preemption.py

Tripwires for the seven preempts in docs/PREEMPTING_ATTACKS.md.

Each preempt is verified concretely. If a future change quietly drops
the falsifiability check, contradiction-checker, schema extensions,
or counter-hypothesis runners, this test catches it.

Run: python -m tests.test_preemption
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.falsification import (
    BoundaryCondition, FalsifiablePrediction, PredictionRegistry,
    PREDICTION_STATUS_VALUES,
)
from term_audit.contradictions import (
    Claim, Contradiction, check_contradictions,
    MUTUALLY_EXCLUSIVE, KNOWN_CONTRADICTIONS, known_contradictions_check,
)
from term_audit.counter_hypotheses import (
    CounterHypothesis, ALL_COUNTER_HYPOTHESES,
    DISTINCTION_AS_COORDINATION, CAPTURE_REVERSIBLE_BY_DESIGN,
)
from term_audit.schema import (
    StandardSetter, TermAudit, SignalScore, FirstPrinciplesPurpose,
)


# ---------------------------------------------------------------------------
# Preempt #1 + #6: falsifiability and boundary conditions
# ---------------------------------------------------------------------------

def test_1_falsifiable_prediction_validators():
    """A FalsifiablePrediction is_falsifiable() only when all three
    load-bearing fields are present."""
    print("\n--- TEST 1: FalsifiablePrediction.is_falsifiable ---")
    full = FalsifiablePrediction(
        claim="distinction grows monotonically",
        conditions=["no structural resistance", "default amplification"],
        predicted_observation="distinction share increases each step",
        falsification_test="run example_run, check monotonicity",
    )
    assert full.is_falsifiable()
    # missing test
    no_test = FalsifiablePrediction(
        claim="x", conditions=["c"], predicted_observation="o",
        falsification_test="",
    )
    assert not no_test.is_falsifiable()
    # missing observation
    no_obs = FalsifiablePrediction(
        claim="x", conditions=["c"], predicted_observation="",
        falsification_test="t",
    )
    assert not no_obs.is_falsifiable()
    # missing conditions
    no_cond = FalsifiablePrediction(
        claim="x", conditions=[], predicted_observation="o",
        falsification_test="t",
    )
    assert not no_cond.is_falsifiable()
    print("  three load-bearing fields enforced")
    print("PASS")


def test_2_prediction_status_validation():
    """Unknown status values must be rejected at construction."""
    print("\n--- TEST 2: prediction status validation ---")
    try:
        FalsifiablePrediction(
            claim="x", conditions=["c"], predicted_observation="o",
            falsification_test="t",
            last_run_result="probably_true",   # not in vocabulary
        )
    except ValueError as e:
        assert "probably_true" in str(e)
    else:
        assert False, "FAIL: bad status should raise"
    # all valid statuses accept
    for s in PREDICTION_STATUS_VALUES:
        FalsifiablePrediction(
            claim="x", conditions=["c"], predicted_observation="o",
            falsification_test="t", last_run_result=s,
        )
    print(f"  validated statuses: {sorted(PREDICTION_STATUS_VALUES)}")
    print("PASS")


def test_3_boundary_condition_documentation():
    """BoundaryCondition.is_documented requires regime, valid_when,
    breaks_when, and breakdown_signal."""
    print("\n--- TEST 3: BoundaryCondition.is_documented ---")
    full = BoundaryCondition(
        regime_description="closed system, fixed total energy",
        valid_when=["energy is conserved", "no external input"],
        breaks_when=["external energy injection", "energy leak"],
        breakdown_signal="total energy drifts more than 1e-9",
    )
    assert full.is_documented()
    partial = BoundaryCondition(
        regime_description="something",
        valid_when=[], breaks_when=[], breakdown_signal="",
    )
    assert not partial.is_documented()
    print("PASS")


def test_4_prediction_registry():
    """Registry tracks predictions and surfaces unfalsifiable ones."""
    print("\n--- TEST 4: PredictionRegistry ---")
    reg = PredictionRegistry()
    reg.register(FalsifiablePrediction(
        claim="a", conditions=["c"], predicted_observation="o",
        falsification_test="t", last_run_result="supported",
    ))
    reg.register(FalsifiablePrediction(
        claim="b", conditions=["c"], predicted_observation="o",
        falsification_test="t", last_run_result="falsified",
    ))
    reg.register(FalsifiablePrediction(
        claim="c", conditions=[], predicted_observation="",
        falsification_test="",   # all three missing
    ))
    summary = reg.summary()
    assert summary["supported"] == 1
    assert summary["falsified"] == 1
    assert summary["untested"] == 1
    assert summary["unfalsifiable"] == 1
    assert summary["total"] == 3
    assert len(reg.by_status("supported")) == 1
    assert len(reg.unfalsifiable()) == 1
    print(f"  summary: {summary}")
    print("PASS")


# ---------------------------------------------------------------------------
# Preempt #2: separation of measurement and incentive layers
# ---------------------------------------------------------------------------

def test_5_measurement_and_incentive_layers_separable():
    """TermAudit.measurement_layer() returns only math-side fields;
    incentive_layer() returns only incentive-side fields. They must
    not overlap on the load-bearing fields."""
    print("\n--- TEST 5: measurement / incentive layer separation ---")
    audit = TermAudit(
        term="test",
        claimed_signal="signal claim",
        standard_setters=[StandardSetter(
            name="setter", authority_basis="basis",
            incentive_structure="gain",
            independence_from_measured=0.5,
            loss_if_audited="loss",
        )],
        signal_scores=[],
        first_principles=FirstPrinciplesPurpose(
            stated_purpose="purpose",
            physical_referent=None, informational_referent=None,
            drift_score=0.5, drift_justification="j",
        ),
        correlation_to_real_signal=0.5,
        correlation_justification="j",
    )
    m = audit.measurement_layer()
    i = audit.incentive_layer()
    # math layer must NOT include standard_setters
    assert "standard_setters" not in m
    # incentive layer must NOT include signal_scores or
    # correlation_to_real_signal
    assert "signal_scores" not in i
    assert "correlation_to_real_signal" not in i
    # math layer must include the falsifiability machinery hooks
    for k in ("signal_scores", "is_signal", "boundary_conditions",
              "predictions"):
        assert k in m, f"FAIL: math layer missing {k}"
    # incentive layer must include the standard-setter machinery
    for k in ("standard_setters", "first_principles"):
        assert k in i, f"FAIL: incentive layer missing {k}"
    print("  math fields and incentive fields are disjoint surfaces")
    print("PASS")


# ---------------------------------------------------------------------------
# Preempt #5: standard-setter loss field
# ---------------------------------------------------------------------------

def test_6_loss_if_audited_optional_but_surfaceable():
    """loss_if_audited defaults to empty (backward-compat) but
    is_loss_documented and incomplete_loss_documentation surface the gap."""
    print("\n--- TEST 6: loss_if_audited surfaceable when missing ---")
    documented = StandardSetter(
        name="X", authority_basis="b", incentive_structure="i",
        independence_from_measured=0.5, loss_if_audited="loss",
    )
    undocumented = StandardSetter(
        name="Y", authority_basis="b", incentive_structure="i",
        independence_from_measured=0.5,
    )
    assert documented.is_loss_documented()
    assert not undocumented.is_loss_documented()

    audit = TermAudit(
        term="t", claimed_signal="s",
        standard_setters=[documented, undocumented],
        signal_scores=[],
        first_principles=FirstPrinciplesPurpose(
            stated_purpose="p", physical_referent=None,
            informational_referent=None,
            drift_score=0, drift_justification="j",
        ),
        correlation_to_real_signal=0, correlation_justification="j",
    )
    incomplete = audit.incomplete_loss_documentation()
    assert incomplete == ["Y"], \
        f"FAIL: expected ['Y'], got {incomplete}"
    print(f"  incomplete loss documentation: {incomplete}")
    print("PASS")


# ---------------------------------------------------------------------------
# Preempt #7: contradiction checker
# ---------------------------------------------------------------------------

def test_7_direct_contradiction_detected():
    """Two claims about the same referent with mutually-exclusive
    properties trigger a direct contradiction."""
    print("\n--- TEST 7: direct contradiction detected ---")
    a = Claim(referent="money", asserted_property="stable",
              text="money is stable")
    b = Claim(referent="money", asserted_property="varying",
              text="money varies")
    contradictions = check_contradictions([a, b])
    assert len(contradictions) == 1
    assert contradictions[0].kind == "direct"
    # same referent required: claims about different referents do not contradict
    c = Claim(referent="GDP", asserted_property="varying",
              text="GDP varies")
    assert check_contradictions([a, c]) == []
    print("  direct contradiction detector working")
    print("PASS")


def test_8_known_contradictions_all_surface():
    """Every pre-registered KNOWN contradiction must be detected by
    the checker. If any registered pair stops being detected, the
    detector has regressed."""
    print("\n--- TEST 8: KNOWN_CONTRADICTIONS all detected ---")
    detected = known_contradictions_check()
    assert len(detected) == len(KNOWN_CONTRADICTIONS), \
        f"FAIL: expected {len(KNOWN_CONTRADICTIONS)} contradictions " \
        f"detected, got {len(detected)}"
    print(f"  {len(detected)} / {len(KNOWN_CONTRADICTIONS)} known "
          "contradictions detected")
    print("PASS")


def test_9_mutually_exclusive_registry_symmetric():
    """Mutually-exclusive properties must work in both directions."""
    print("\n--- TEST 9: MUTUALLY_EXCLUSIVE symmetric ---")
    # build claims in both orders for one pair
    a1 = Claim(referent="x", asserted_property="stable", text="")
    b1 = Claim(referent="x", asserted_property="varying", text="")
    a2 = Claim(referent="x", asserted_property="varying", text="")
    b2 = Claim(referent="x", asserted_property="stable", text="")
    assert len(check_contradictions([a1, b1])) == 1
    assert len(check_contradictions([a2, b2])) == 1
    print("  symmetric exclusion works")
    print("PASS")


# ---------------------------------------------------------------------------
# Preempt #4: counter-hypotheses
# ---------------------------------------------------------------------------

def test_10_counter_hypothesis_distinction_as_coordination_falsified():
    """The strongest defense (distinction-seeking is adaptive
    coordination) must be falsified within the model regime. If this
    test starts passing the hypothesis instead, either the model or
    the test thresholds have drifted — investigate before merging."""
    print("\n--- TEST 10: distinction_as_coordination falsified ---")
    result = DISTINCTION_AS_COORDINATION.run()
    assert result["result"] == "falsified", \
        f"FAIL: expected falsified, got {result['result']}. " \
        "If you intend the framework to support this hypothesis, " \
        "you must update the model AND the audit notes — this is " \
        "not a soft change."
    print(f"  result: {result['result']}")
    print(f"  growth_in_second_half: "
          f"{result['growth_in_second_half']:.3f} of "
          f"{result['total_energy']:.3f} total")
    print("PASS")


def test_11_counter_hypothesis_capture_reversible_by_design_supported():
    """The 'capture is fixable by adding resistance' hypothesis is
    SUPPORTED at the math layer. The framework does not claim capture
    is inevitable for arbitrary resistance. The interesting question
    is then who sets the resistance — an incentive-layer question."""
    print("\n--- TEST 11: capture_reversible_by_design supported ---")
    result = CAPTURE_REVERSIBLE_BY_DESIGN.run()
    assert result["result"] == "supported"
    assert result["final_capture"] == 0.0
    print(f"  result: {result['result']} (math layer)")
    print(f"  routes question to incentive layer per preempt #2")
    print("PASS")


def test_12_all_counter_hypotheses_runnable():
    """Every CounterHypothesis in ALL_COUNTER_HYPOTHESES must have a
    runnable test_function and produce a result with a 'result' key
    in {supported, falsified, ambiguous}."""
    print("\n--- TEST 12: all counter-hypotheses runnable ---")
    for h in ALL_COUNTER_HYPOTHESES:
        assert h.test_function is not None, \
            f"FAIL: {h.name} has no test_function"
        result = h.run()
        assert "result" in result
        assert result["result"] in {"supported", "falsified", "ambiguous"}, \
            f"FAIL: {h.name} returned unexpected result {result['result']!r}"
    print(f"  {len(ALL_COUNTER_HYPOTHESES)} counter-hypotheses runnable")
    print("PASS")


if __name__ == "__main__":
    test_1_falsifiable_prediction_validators()
    test_2_prediction_status_validation()
    test_3_boundary_condition_documentation()
    test_4_prediction_registry()
    test_5_measurement_and_incentive_layers_separable()
    test_6_loss_if_audited_optional_but_surfaceable()
    test_7_direct_contradiction_detected()
    test_8_known_contradictions_all_surface()
    test_9_mutually_exclusive_registry_symmetric()
    test_10_counter_hypothesis_distinction_as_coordination_falsified()
    test_11_counter_hypothesis_capture_reversible_by_design_supported()
    test_12_all_counter_hypotheses_runnable()
    print("\nall preemption tests passed.")
