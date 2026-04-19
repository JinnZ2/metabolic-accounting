"""
tests/test_productivity_audit.py

Tripwires for term_audit/audits/productivity.py.

Locks in the load-bearing findings:
  - conventional productivity fails 7 of 7 signal criteria
  - the long-haul driver worked example shows pay < true_input
  - drawdown routes to organism/public/family/deferred as expected
  - five falsifiable predictions and six attack responses registered
  - 'productivity' remains in Tier 2 of the audit registry

Run: python -m tests.test_productivity_audit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.productivity import (
    CONVENTIONAL_PRODUCTIVITY_AUDIT,
    DEPENDENCY_CATEGORIES,
    DependencyItem,
    JobDependencyProfile,
    long_haul_driver_example,
    FALSIFIABLE_PREDICTIONS,
    ATTACK_RESPONSES,
)
from term_audit.tiers import find_tier, TIER_2_LABOR_AND_HUMAN_WORTH


def test_1_conventional_productivity_is_not_a_signal():
    """7 of 7 signal criteria fail at threshold 0.7."""
    print("\n--- TEST 1: conventional productivity fails 7/7 ---")
    assert not CONVENTIONAL_PRODUCTIVITY_AUDIT.is_signal(), \
        "FAIL: should not qualify as a signal"
    passing = sum(
        1 for s in CONVENTIONAL_PRODUCTIVITY_AUDIT.signal_scores
        if s.score >= 0.7
    )
    assert passing == 0, \
        f"FAIL: notes claim 0/7 passing at 0.7, got {passing}"
    modes = set(CONVENTIONAL_PRODUCTIVITY_AUDIT.failure_modes())
    from term_audit.schema import SIGNAL_CRITERIA
    assert modes == set(SIGNAL_CRITERIA), \
        f"FAIL: all seven criteria should be failure_modes, got {modes}"
    print(f"  passing at 0.7: {passing} / 7")
    print("PASS")


def test_2_drift_and_correlation_match_notes():
    """Audit claims drift_score 0.85 and correlation 0.2."""
    print("\n--- TEST 2: drift + correlation match notes ---")
    assert CONVENTIONAL_PRODUCTIVITY_AUDIT.first_principles.drift_score \
        >= 0.8
    assert CONVENTIONAL_PRODUCTIVITY_AUDIT.correlation_to_real_signal \
        <= 0.3
    print(f"  drift:       "
          f"{CONVENTIONAL_PRODUCTIVITY_AUDIT.first_principles.drift_score}")
    print(f"  correlation: "
          f"{CONVENTIONAL_PRODUCTIVITY_AUDIT.correlation_to_real_signal}")
    print("PASS")


def test_3_dependency_categories_are_ten():
    """DEPENDENCY_CATEGORIES enumerates the ten categories the
    audit claims. Removing one silently weakens the accounting
    surface."""
    print("\n--- TEST 3: ten dependency categories registered ---")
    assert len(DEPENDENCY_CATEGORIES) == 10, \
        f"FAIL: expected 10 categories, got {len(DEPENDENCY_CATEGORIES)}"
    required = {
        "caloric", "sleep", "shelter", "transport", "equipment",
        "medical", "social", "knowledge", "recovery", "replacement",
    }
    assert required.issubset(set(DEPENDENCY_CATEGORIES))
    print(f"  categories: {DEPENDENCY_CATEGORIES}")
    print("PASS")


def test_4_long_haul_driver_is_extractive():
    """The worked example has pay $1600/week vs true_input $2070/week,
    producing $470/week extraction. Lock in the numbers so they cannot
    drift without a deliberate change."""
    print("\n--- TEST 4: long-haul driver extractive ---")
    profile = long_haul_driver_example()
    assert abs(profile.pay_per_time_basis - 1600.0) < 1e-9
    true_in = profile.true_input()
    assert abs(true_in - 2070.0) < 1e-9, \
        f"FAIL: expected true_input 2070, got {true_in}"
    verdict = profile.productivity_verdict()
    assert verdict["is_productive"] is False
    assert abs(verdict["gap"] - (-470.0)) < 1e-9
    assert abs(verdict["extraction_rate"] - 470.0) < 1e-9
    print(f"  pay={verdict['pay']}, true_input={verdict['true_input']}, "
          f"gap={verdict['gap']}, extraction={verdict['extraction_rate']}")
    print("PASS")


def test_5_drawdown_breakdown_routes_correctly():
    """The $470 gap splits: organism ~224.78, public ~45.41,
    family ~90.82, deferred ~108.99. Shares are proportional to
    the cost-of-dependency-items-with-drawdown-source."""
    print("\n--- TEST 5: drawdown breakdown by source ---")
    profile = long_haul_driver_example()
    bd = profile.drawdown_breakdown()
    assert set(bd) == {"organism", "public", "family", "deferred"}, \
        f"FAIL: unexpected drawdown keys: {set(bd)}"
    # proportions derived from the example dependency costs
    assert abs(bd["organism"] - 224.78) < 0.01
    assert abs(bd["public"] - 45.41) < 0.01
    assert abs(bd["family"] - 90.82) < 0.01
    assert abs(bd["deferred"] - 108.99) < 0.01
    # shares must sum to the gap
    assert abs(sum(bd.values()) - 470.0) < 0.01, \
        f"FAIL: drawdown total mismatch: {sum(bd.values())}"
    print(f"  {bd}")
    print("PASS")


def test_6_productive_job_has_empty_drawdown():
    """If pay >= true_input the drawdown_breakdown should be empty
    (nothing is being externalized)."""
    print("\n--- TEST 6: productive job has empty drawdown ---")
    profile = JobDependencyProfile(
        job_name="hypothetical_paid_adequately",
        output_description="test",
        time_basis="week",
        pay_per_time_basis=3000.0,
        dependencies=[
            DependencyItem(
                name="caloric", category="caloric",
                cost_per_unit_output=500.0,
                drawdown_source="organism",
            ),
        ],
    )
    verdict = profile.productivity_verdict()
    assert verdict["is_productive"] is True
    assert verdict["extraction_rate"] == 0.0
    assert profile.drawdown_breakdown() == {}
    print(f"  pay=3000, true_input={profile.true_input()}, no drawdown")
    print("PASS")


def test_7_falsifiable_predictions_schema():
    """Five falsifiable predictions registered, each with id/claim/
    falsification."""
    print("\n--- TEST 7: five falsifiable predictions ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 5
    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}
        assert p["claim"].strip() and p["falsification"].strip()
    assert [p["id"] for p in FALSIFIABLE_PREDICTIONS] == [1, 2, 3, 4, 5]
    print(f"  {len(FALSIFIABLE_PREDICTIONS)} predictions with valid schema")
    print("PASS")


def test_8_attack_response_matrix_present():
    """Six attack-response pairs registered; each has non-empty
    attack and response strings. This is the surface the Tier 2
    critic must push against."""
    print("\n--- TEST 8: attack-response matrix ---")
    assert len(ATTACK_RESPONSES) == 6, \
        f"FAIL: expected 6 entries, got {len(ATTACK_RESPONSES)}"
    for item in ATTACK_RESPONSES:
        assert set(item) == {"attack", "response"}
        assert item["attack"].strip() and item["response"].strip()
    print(f"  {len(ATTACK_RESPONSES)} attack-response entries")
    print("PASS")


def test_9_productivity_registered_in_tier_2():
    """'productivity' is in Tier 2 of the audit registry."""
    print("\n--- TEST 9: 'productivity' in Tier 2 ---")
    tier = find_tier("productivity")
    assert tier is TIER_2_LABOR_AND_HUMAN_WORTH, \
        f"FAIL: expected Tier 2, got {tier}"
    print(f"  tier: {tier.number} ({tier.name})")
    print("PASS")


if __name__ == "__main__":
    test_1_conventional_productivity_is_not_a_signal()
    test_2_drift_and_correlation_match_notes()
    test_3_dependency_categories_are_ten()
    test_4_long_haul_driver_is_extractive()
    test_5_drawdown_breakdown_routes_correctly()
    test_6_productive_job_has_empty_drawdown()
    test_7_falsifiable_predictions_schema()
    test_8_attack_response_matrix_present()
    test_9_productivity_registered_in_tier_2()
    print("\nall productivity audit tests passed.")
