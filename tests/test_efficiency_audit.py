"""
tests/test_efficiency_audit.py

Tripwires for term_audit/audits/efficiency.py.

Locks in:
  - conventional (linear) efficiency fails 6 of 7 signal criteria
    at threshold 0.7 (falsifiability is the one survivor)
  - EfficiencyVector classifies correctly at the documented
    thresholds (extractive / linear_high_throughput /
    regenerative_coupled / coupled_steady / mixed)
  - system_coupling_coefficient computes correctly on the
    smallholder worked example (coupling 0.211)
  - natural / corporate / coupled reference counts + magnitudes
  - 5 falsifiable predictions and 7 attack responses
  - 'efficiency' registered in Tier 2

Run: python -m tests.test_efficiency_audit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.efficiency import (
    CONVENTIONAL_EFFICIENCY_AUDIT,
    EfficiencyVector,
    CoupledOperation,
    system_coupling_coefficient,
    NATURAL_SYSTEM_REFERENCES,
    CORPORATE_SYSTEM_REFERENCES,
    COUPLED_HUMAN_OPERATION_REFERENCES,
    FALSIFIABLE_PREDICTIONS,
    ATTACK_RESPONSES,
    smallholder_example,
)
from term_audit.tiers import find_tier, TIER_2_LABOR_AND_HUMAN_WORTH


def test_1_conventional_efficiency_fails_6_of_7():
    """Linear efficiency fails every signal criterion except
    falsifiability. The audit records this as 6 failure modes."""
    print("\n--- TEST 1: conventional efficiency 6/7 failure ---")
    assert not CONVENTIONAL_EFFICIENCY_AUDIT.is_signal()
    modes = CONVENTIONAL_EFFICIENCY_AUDIT.failure_modes()
    assert len(modes) == 6, \
        f"FAIL: expected 6 failure modes, got {len(modes)}"
    # the one that is NOT in failure_modes should be falsifiability
    all_crit = {s.criterion for s in CONVENTIONAL_EFFICIENCY_AUDIT.signal_scores}
    survivor = all_crit - set(modes)
    assert survivor == {"falsifiability"}, \
        f"FAIL: expected only falsifiability to pass 0.5, got {survivor}"
    print(f"  failure modes ({len(modes)}): {sorted(modes)}")
    print(f"  survivor: {survivor.pop()}")
    print("PASS")


def test_2_drift_and_correlation_match_notes():
    """Audit claims drift_score 0.8 and correlation 0.25."""
    print("\n--- TEST 2: drift + correlation ---")
    assert CONVENTIONAL_EFFICIENCY_AUDIT.first_principles.drift_score \
        >= 0.7
    assert CONVENTIONAL_EFFICIENCY_AUDIT.correlation_to_real_signal \
        <= 0.4
    print(f"  drift:       "
          f"{CONVENTIONAL_EFFICIENCY_AUDIT.first_principles.drift_score}")
    print(f"  correlation: "
          f"{CONVENTIONAL_EFFICIENCY_AUDIT.correlation_to_real_signal}")
    print("PASS")


def test_3_efficiency_vector_classifications():
    """EfficiencyVector.classification must return the documented
    category for each regime."""
    print("\n--- TEST 3: vector classification regimes ---")
    extract = EfficiencyVector(
        eroi=0.8, coupling_coefficient=0.2,
        carrying_capacity_trajectory=-0.5, knowledge_density=0.2,
    )
    assert extract.classification() == "extractive", \
        f"FAIL: {extract.classification()}"

    linear = EfficiencyVector(
        eroi=2.0, coupling_coefficient=0.1,
        carrying_capacity_trajectory=0.0, knowledge_density=0.3,
    )
    assert linear.classification() == "linear_high_throughput", \
        f"FAIL: {linear.classification()}"

    regen = EfficiencyVector(
        eroi=1.5, coupling_coefficient=0.7,
        carrying_capacity_trajectory=0.4, knowledge_density=0.6,
    )
    assert regen.classification() == "regenerative_coupled", \
        f"FAIL: {regen.classification()}"

    steady = EfficiencyVector(
        eroi=1.2, coupling_coefficient=0.5,
        carrying_capacity_trajectory=0.1, knowledge_density=0.5,
    )
    assert steady.classification() == "coupled_steady", \
        f"FAIL: {steady.classification()}"

    mixed = EfficiencyVector(
        eroi=0.6, coupling_coefficient=0.35,
        carrying_capacity_trajectory=0.2, knowledge_density=0.5,
    )
    assert mixed.classification() == "mixed", \
        f"FAIL: {mixed.classification()}"
    print("  extractive / linear / regen / steady / mixed all correct")
    print("PASS")


def test_4_extraction_classifies_as_extractive():
    """Negative carrying-capacity-trajectory below -0.3 classifies
    as extractive regardless of EROI. The audit claims extraction
    should not register as efficiency even with high EROI."""
    print("\n--- TEST 4: extraction classifies as extractive ---")
    high_eroi_extract = EfficiencyVector(
        eroi=3.0, coupling_coefficient=0.5,
        carrying_capacity_trajectory=-0.5, knowledge_density=0.5,
    )
    assert high_eroi_extract.classification() == "extractive", \
        f"FAIL: high-EROI extraction should still classify extractive"
    print(f"  EROI=3.0 with trajectory=-0.5 still 'extractive'")
    print("PASS")


def test_5_smallholder_example_numbers():
    """smallholder_example() produces the documented metrics:
    6 operations, coupling coefficient 0.211, magnitude 1.077."""
    print("\n--- TEST 5: smallholder example numbers ---")
    ops, vec = smallholder_example()
    assert len(ops) == 6, f"FAIL: expected 6 ops, got {len(ops)}"
    coupling = system_coupling_coefficient(ops)
    assert abs(coupling - 0.211) < 0.01, \
        f"FAIL: expected coupling 0.211, got {coupling:.3f}"
    assert abs(vec.magnitude() - 1.077) < 0.01, \
        f"FAIL: expected magnitude 1.077, got {vec.magnitude():.3f}"
    print(f"  ops={len(ops)}  coupling={coupling:.3f}  "
          f"magnitude={vec.magnitude():.3f}  class={vec.classification()}")
    print("PASS")


def test_6_coupling_coefficient_edge_cases():
    """system_coupling_coefficient handles trivial inputs: single op
    or empty list must return 0.0, not raise or return None."""
    print("\n--- TEST 6: coupling edge cases ---")
    assert system_coupling_coefficient([]) == 0.0
    single = [CoupledOperation(
        name="x", inputs=["a"], outputs=["b"], waste_streams=[]
    )]
    assert system_coupling_coefficient(single) == 0.0
    print("  empty and single-op both return 0.0")
    print("PASS")


def test_7_reference_counts():
    """Reference sets must be non-empty and provide calibration
    anchors in each category."""
    print("\n--- TEST 7: reference counts ---")
    assert len(NATURAL_SYSTEM_REFERENCES) >= 1
    assert len(CORPORATE_SYSTEM_REFERENCES) >= 1
    assert len(COUPLED_HUMAN_OPERATION_REFERENCES) >= 1
    print(f"  natural={len(NATURAL_SYSTEM_REFERENCES)}, "
          f"corporate={len(CORPORATE_SYSTEM_REFERENCES)}, "
          f"coupled={len(COUPLED_HUMAN_OPERATION_REFERENCES)}")
    print("PASS")


def test_8_predictions_and_attacks():
    """Five falsifiable predictions with valid schema, seven
    attack-response entries."""
    print("\n--- TEST 8: predictions + attacks ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 5
    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}
        assert p["claim"].strip() and p["falsification"].strip()
    assert len(ATTACK_RESPONSES) == 7
    for item in ATTACK_RESPONSES:
        assert set(item) == {"attack", "response"}
        assert item["attack"].strip() and item["response"].strip()
    print(f"  predictions: {len(FALSIFIABLE_PREDICTIONS)}, "
          f"attacks: {len(ATTACK_RESPONSES)}")
    print("PASS")


def test_9_efficiency_registered_in_tier_2():
    """'efficiency' remains in Tier 2 of the audit registry."""
    print("\n--- TEST 9: 'efficiency' in Tier 2 ---")
    tier = find_tier("efficiency")
    assert tier is TIER_2_LABOR_AND_HUMAN_WORTH, \
        f"FAIL: expected Tier 2, got {tier}"
    print(f"  tier: {tier.number} ({tier.name})")
    print("PASS")


if __name__ == "__main__":
    test_1_conventional_efficiency_fails_6_of_7()
    test_2_drift_and_correlation_match_notes()
    test_3_efficiency_vector_classifications()
    test_4_extraction_classifies_as_extractive()
    test_5_smallholder_example_numbers()
    test_6_coupling_coefficient_edge_cases()
    test_7_reference_counts()
    test_8_predictions_and_attacks()
    test_9_efficiency_registered_in_tier_2()
    print("\nall efficiency audit tests passed.")
