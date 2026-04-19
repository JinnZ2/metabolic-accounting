"""
tests/test_value_audit.py

Tripwires for term_audit/audits/value.py.

Locks in:
  - collapsed 'value' token fails 7 of 7 signal criteria
  - V_A use-value, V_B exchange-value, V_C substrate-value are
    kept separate, each with its own term namespace
  - V_C is the clean signal (7/7 pass at 0.7); V_B is the heavily
    captured one (1/7 pass); V_A sits in between (3/7 pass)
  - five linkages with the LOAD-BEARING NEGATIVE B -> C
    (exchange-value substitutes for substrate-value)
  - collapsed_usage_diagnosis preserves the Tier-1-inheritance
    framing
  - 6 falsifiable predictions, 7 attack responses
  - 'value' registered in Tier 1

Run: python -m tests.test_value_audit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.value import (
    COLLAPSED_VALUE_AUDIT, ALL_VALUE_AUDITS, VALUE_LINKAGES,
    collapsed_usage_diagnosis,
    FALSIFIABLE_PREDICTIONS, ATTACK_RESPONSES,
)
from term_audit.tiers import find_tier, TIER_1_FOUNDATIONAL


def test_1_collapsed_fails_7_of_7():
    """The collapsed 'value' token fails every signal criterion."""
    print("\n--- TEST 1: collapsed value fails 7/7 ---")
    assert not COLLAPSED_VALUE_AUDIT.is_signal()
    passing = sum(1 for s in COLLAPSED_VALUE_AUDIT.signal_scores
                  if s.score >= 0.7)
    assert passing == 0
    from term_audit.schema import SIGNAL_CRITERIA
    assert set(COLLAPSED_VALUE_AUDIT.failure_modes()) == set(SIGNAL_CRITERIA)
    print(f"  0/7 passing at 0.7; all seven in failure_modes")
    print("PASS")


def test_2_three_separated_measurements():
    """ALL_VALUE_AUDITS exposes the collapsed token plus three
    namespaced measurements. Each has its own term string so the
    bare 'value' token is never used as a measurement."""
    print("\n--- TEST 2: three separated measurements ---")
    expected = {"collapsed", "V_A_use_value", "V_B_exchange_value",
                "V_C_substrate_value"}
    assert set(ALL_VALUE_AUDITS) == expected
    for key in ("V_A_use_value", "V_B_exchange_value",
                "V_C_substrate_value"):
        term = ALL_VALUE_AUDITS[key].term
        assert term.startswith("value_"), \
            f"FAIL: {key} term should be namespaced, got {term}"
        assert term != "value", \
            f"FAIL: {key} must not use the bare collapsed token"
    print(f"  namespaces: {sorted(ALL_VALUE_AUDITS)}")
    print("PASS")


def test_3_signal_qualification_by_measurement():
    """V_C clean (7/7 pass), V_A partial (3/7), V_B mostly captured
    (1/7)."""
    print("\n--- TEST 3: signal qualification per measurement ---")
    passing = {}
    for k, a in ALL_VALUE_AUDITS.items():
        passing[k] = sum(1 for s in a.signal_scores if s.score >= 0.7)
    assert passing["V_C_substrate_value"] == 7, \
        f"FAIL: V_C should pass 7/7, got {passing['V_C_substrate_value']}"
    assert ALL_VALUE_AUDITS["V_C_substrate_value"].is_signal()
    assert passing["V_B_exchange_value"] <= 2, \
        f"FAIL: V_B should barely pass any criterion, got {passing['V_B_exchange_value']}"
    assert passing["V_A_use_value"] >= 2, \
        f"FAIL: V_A should pass a handful, got {passing['V_A_use_value']}"
    print(f"  passing at 0.7: V_A={passing['V_A_use_value']}, "
          f"V_B={passing['V_B_exchange_value']}, "
          f"V_C={passing['V_C_substrate_value']}")
    print("PASS")


def test_4_five_linkages_documented():
    """Five linkages cover A-B, C-B, B-C, A-C, C-A."""
    print("\n--- TEST 4: five linkages documented ---")
    assert len(VALUE_LINKAGES) == 5
    pairs = {(L.source, L.target) for L in VALUE_LINKAGES}
    expected = {("V_A", "V_B"), ("V_C", "V_B"), ("V_B", "V_C"),
                ("V_A", "V_C"), ("V_C", "V_A")}
    assert pairs == expected
    print(f"  pairs: {sorted(pairs)}")
    print("PASS")


def test_5_B_to_C_negative_preserved():
    """LOAD-BEARING: V_B -> V_C must remain NEGATIVE. Exchange-value
    growth substitutes for substrate-value; if anyone changes this
    linkage to positive, the entire Tier 1 inheritance argument
    breaks."""
    print("\n--- TEST 5: B -> C negative linkage preserved ---")
    link = next(L for L in VALUE_LINKAGES
                if L.source == "V_B" and L.target == "V_C")
    assert link.relation == "negative", \
        f"FAIL: B -> C must be 'negative', got '{link.relation}'. " \
        "If you change this, you are asserting exchange-value growth " \
        "adds to substrate-value rather than substituting for it — " \
        "which breaks the Tier 1 inheritance argument."
    assert link.strength_estimate < 0, \
        f"FAIL: strength must be negative, got {link.strength_estimate}"
    print(f"  B -> C: relation={link.relation}, "
          f"strength={link.strength_estimate:+.2f}")
    print("PASS")


def test_6_collapsed_diagnosis_carries_tier1_framing():
    """collapsed_usage_diagnosis must surface the Tier 1 inheritance
    argument: money, capital, investment, wealth, GDP, growth all
    claim to measure value and all operate on the exchange-value-
    dominated collapsed token."""
    print("\n--- TEST 6: collapsed diagnosis carries Tier 1 framing ---")
    d = collapsed_usage_diagnosis()
    expected_keys = {"term", "claim", "failure", "consequence",
                     "remediation"}
    assert set(d) == expected_keys
    # load-bearing phrase: the consequence must mention the Tier 1
    # inheritance mechanism
    text = (d["failure"] + " " + d["consequence"]).lower()
    for phrase in ("exchange", "substrate"):
        assert phrase in text, \
            f"FAIL: diagnosis missing phrase '{phrase}'"
    print("  diagnosis carries exchange-vs-substrate framing")
    print("PASS")


def test_7_predictions_and_attacks_schema():
    """6 falsifiable predictions, 7 attack-response entries."""
    print("\n--- TEST 7: predictions + attacks ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 6
    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}
        assert p["claim"].strip() and p["falsification"].strip()
    assert len(ATTACK_RESPONSES) == 7
    for item in ATTACK_RESPONSES:
        assert set(item) == {"attack", "response"}
    print(f"  predictions={len(FALSIFIABLE_PREDICTIONS)}, "
          f"attacks={len(ATTACK_RESPONSES)}")
    print("PASS")


def test_8_value_registered_in_tier_1():
    """'value' is Tier 1 (foundational) per term_audit/tiers.py."""
    print("\n--- TEST 8: 'value' in Tier 1 ---")
    tier = find_tier("value")
    assert tier is TIER_1_FOUNDATIONAL, \
        f"FAIL: expected Tier 1, got {tier}"
    print(f"  tier: {tier.number} ({tier.name})")
    print("PASS")


if __name__ == "__main__":
    test_1_collapsed_fails_7_of_7()
    test_2_three_separated_measurements()
    test_3_signal_qualification_by_measurement()
    test_4_five_linkages_documented()
    test_5_B_to_C_negative_preserved()
    test_6_collapsed_diagnosis_carries_tier1_framing()
    test_7_predictions_and_attacks_schema()
    test_8_value_registered_in_tier_1()
    print("\nall value audit tests passed.")
