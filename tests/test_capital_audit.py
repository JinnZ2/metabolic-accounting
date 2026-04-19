"""
tests/test_capital_audit.py

Tripwires for term_audit/audits/capital.py.

Locks in:
  - collapsed 'capital' token fails 7 of 7 signal criteria
  - K_A productive, K_B financial, K_C institutional kept separate
    with namespaced terms
  - K_A passes 7/7 (clean signal when scoped to physical plant);
    K_B and K_C fail as single-scalar signals
  - six linkages documented, with the LOAD-BEARING NEGATIVE K_B -> K_A
    (financial-claim accumulation substitutes for productive-capital
    growth) and the LOAD-BEARING NEGATIVE K_B -> K_C preserved
  - collapsed_usage_diagnosis carries the Tier-1-inheritance framing
  - 6 falsifiable predictions, 7 attack responses
  - 'capital' registered in Tier 1

Run: python -m tests.test_capital_audit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.capital import (
    COLLAPSED_CAPITAL_AUDIT, ALL_CAPITAL_AUDITS, CAPITAL_LINKAGES,
    collapsed_usage_diagnosis,
    FALSIFIABLE_PREDICTIONS, ATTACK_RESPONSES,
)
from term_audit.tiers import find_tier, TIER_1_FOUNDATIONAL


def test_1_collapsed_fails_7_of_7():
    """The collapsed 'capital' token fails every signal criterion."""
    print("\n--- TEST 1: collapsed capital fails 7/7 ---")
    assert not COLLAPSED_CAPITAL_AUDIT.is_signal()
    passing = sum(1 for s in COLLAPSED_CAPITAL_AUDIT.signal_scores
                  if s.score >= 0.7)
    assert passing == 0
    from term_audit.schema import SIGNAL_CRITERIA
    assert set(COLLAPSED_CAPITAL_AUDIT.failure_modes()) == set(SIGNAL_CRITERIA)
    print(f"  0/7 passing; all seven in failure_modes")
    print("PASS")


def test_2_three_separated_measurements():
    """ALL_CAPITAL_AUDITS exposes collapsed plus three namespaced
    measurements. Bare 'capital' must never appear as a term."""
    print("\n--- TEST 2: three separated measurements ---")
    expected = {"collapsed", "K_A_productive", "K_B_financial",
                "K_C_institutional"}
    assert set(ALL_CAPITAL_AUDITS) == expected
    for key in ("K_A_productive", "K_B_financial", "K_C_institutional"):
        term = ALL_CAPITAL_AUDITS[key].term
        assert term.startswith("capital_"), \
            f"FAIL: {key} term should be namespaced, got {term}"
        assert term != "capital"
    print(f"  namespaces: {sorted(ALL_CAPITAL_AUDITS)}")
    print("PASS")


def test_3_signal_qualification():
    """K_A (physical plant) passes 7/7; K_B and K_C fail as
    single-scalar signals."""
    print("\n--- TEST 3: signal qualification per measurement ---")
    passing = {
        k: sum(1 for s in a.signal_scores if s.score >= 0.7)
        for k, a in ALL_CAPITAL_AUDITS.items()
    }
    assert passing["K_A_productive"] == 7
    assert ALL_CAPITAL_AUDITS["K_A_productive"].is_signal()
    assert not ALL_CAPITAL_AUDITS["K_B_financial"].is_signal()
    assert not ALL_CAPITAL_AUDITS["K_C_institutional"].is_signal()
    print(f"  K_A={passing['K_A_productive']}, "
          f"K_B={passing['K_B_financial']}, "
          f"K_C={passing['K_C_institutional']}")
    print("PASS")


def test_4_six_linkages_documented():
    """Six linkages cover every ordered pair across {K_A, K_B, K_C}."""
    print("\n--- TEST 4: six linkages documented ---")
    assert len(CAPITAL_LINKAGES) == 6
    pairs = {(L.source, L.target) for L in CAPITAL_LINKAGES}
    expected = {("K_A", "K_B"), ("K_B", "K_A"), ("K_A", "K_C"),
                ("K_C", "K_A"), ("K_B", "K_C"), ("K_C", "K_B")}
    assert pairs == expected
    print(f"  pairs: {sorted(pairs)}")
    print("PASS")


def test_5_K_B_to_K_A_negative_preserved():
    """LOAD-BEARING: K_B -> K_A must remain NEGATIVE. Financial-claim
    accumulation is typically accompanied by productive-capital
    extraction. If anyone flips this to positive, they are asserting
    that financial growth adds to physical plant — which is the
    exact category error the audit exists to surface."""
    print("\n--- TEST 5: K_B -> K_A negative preserved ---")
    link = next(L for L in CAPITAL_LINKAGES
                if L.source == "K_B" and L.target == "K_A")
    assert link.relation == "negative", \
        f"FAIL: K_B -> K_A must be 'negative', got '{link.relation}'. " \
        "If you change this, you are asserting financial-claim growth " \
        "adds to productive capital rather than substituting for it. " \
        "That is the collapsed-token error this audit exists to name."
    assert link.strength_estimate < 0
    print(f"  K_B -> K_A: relation={link.relation}, "
          f"strength={link.strength_estimate:+.2f}")
    print("PASS")


def test_6_K_B_to_K_C_negative_preserved():
    """Second LOAD-BEARING negative: K_B -> K_C. Financial extraction
    erodes institutional coordination capacity (public-good
    defunding, regulatory capture, community disinvestment).
    Preserving this together with K_B -> K_A is what makes the
    audit's Tier 1 inheritance argument hold."""
    print("\n--- TEST 6: K_B -> K_C negative preserved ---")
    link = next(L for L in CAPITAL_LINKAGES
                if L.source == "K_B" and L.target == "K_C")
    assert link.relation == "negative", \
        f"FAIL: K_B -> K_C must be 'negative', got '{link.relation}'"
    assert link.strength_estimate < 0
    print(f"  K_B -> K_C: relation={link.relation}, "
          f"strength={link.strength_estimate:+.2f}")
    print("PASS")


def test_7_collapsed_diagnosis_carries_tier1_framing():
    """collapsed_usage_diagnosis must surface that GDP, wealth, and
    investment inherit the failure — they all operate on the
    K_B-dominated collapsed capital token."""
    print("\n--- TEST 7: collapsed diagnosis carries Tier 1 framing ---")
    d = collapsed_usage_diagnosis()
    assert set(d) == {"term", "claim", "failure", "consequence",
                      "remediation"}
    text = (d["failure"] + " " + d["consequence"]).lower()
    for phrase in ("k_b", "k_a", "extract"):
        assert phrase in text, \
            f"FAIL: diagnosis missing phrase '{phrase}'"
    print("  diagnosis carries K_B-dominates-K_A extraction framing")
    print("PASS")


def test_8_predictions_and_attacks_schema():
    """6 predictions, 7 attack-response entries."""
    print("\n--- TEST 8: predictions + attacks ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 6
    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}
        assert p["claim"].strip() and p["falsification"].strip()
    assert len(ATTACK_RESPONSES) == 7
    for item in ATTACK_RESPONSES:
        # attack + response required; source_refs optional
        assert {"attack", "response"}.issubset(set(item))
        assert item["attack"].strip() and item["response"].strip()
    print(f"  predictions={len(FALSIFIABLE_PREDICTIONS)}, "
          f"attacks={len(ATTACK_RESPONSES)}")
    print("PASS")


def test_9_capital_registered_in_tier_1():
    """'capital' is Tier 1."""
    print("\n--- TEST 9: 'capital' in Tier 1 ---")
    tier = find_tier("capital")
    assert tier is TIER_1_FOUNDATIONAL, \
        f"FAIL: expected Tier 1, got {tier}"
    print(f"  tier: {tier.number} ({tier.name})")
    print("PASS")


if __name__ == "__main__":
    test_1_collapsed_fails_7_of_7()
    test_2_three_separated_measurements()
    test_3_signal_qualification()
    test_4_six_linkages_documented()
    test_5_K_B_to_K_A_negative_preserved()
    test_6_K_B_to_K_C_negative_preserved()
    test_7_collapsed_diagnosis_carries_tier1_framing()
    test_8_predictions_and_attacks_schema()
    test_9_capital_registered_in_tier_1()
    print("\nall capital audit tests passed.")
