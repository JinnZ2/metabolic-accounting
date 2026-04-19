"""
tests/test_money_audit.py

Locks in the summary claims of term_audit/audits/money.py.

MONEY_AUDIT.notes asserts "money fails 7 of 7 signal criteria at
threshold 0.7". If anyone edits the individual scores without
updating the notes, this test catches the drift.

Run: python -m tests.test_money_audit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.schema import SIGNAL_CRITERIA
from term_audit.audits.money import MONEY_AUDIT


def test_1_money_is_not_a_signal():
    """The notes claim: fails 7 of 7 at threshold 0.7. Lock it in."""
    print("\n--- TEST 1: money fails all signal criteria ---")
    assert not MONEY_AUDIT.is_signal(threshold=5), \
        "FAIL: money should not qualify as a signal"
    assert not MONEY_AUDIT.is_signal(threshold=1), \
        "FAIL: no single criterion should pass at 0.7"
    passing = sum(1 for s in MONEY_AUDIT.signal_scores if s.score >= 0.7)
    assert passing == 0, \
        f"FAIL: notes claim 7-of-7 failure, but {passing} passed"
    print(f"  passing criteria at 0.7: {passing} / 7")
    print("PASS")


def test_2_failure_modes_cover_all_criteria():
    """failure_modes() (score < 0.5) should include every criterion."""
    print("\n--- TEST 2: failure_modes covers all seven criteria ---")
    modes = set(MONEY_AUDIT.failure_modes())
    assert modes == set(SIGNAL_CRITERIA), \
        f"FAIL: failure_modes={modes} vs expected={set(SIGNAL_CRITERIA)}"
    print(f"  failure_modes: {sorted(modes)}")
    print("PASS")


def test_3_every_score_has_justification():
    """Repo discipline: no numeric claim without justification + source refs
    where applicable. Justifications must be non-empty."""
    print("\n--- TEST 3: every score has a justification ---")
    for s in MONEY_AUDIT.signal_scores:
        assert s.justification.strip(), \
            f"FAIL: empty justification for {s.criterion}"
    assert MONEY_AUDIT.correlation_justification.strip()
    assert MONEY_AUDIT.first_principles.drift_justification.strip()
    print(f"  {len(MONEY_AUDIT.signal_scores)} scores, "
          f"all with justifications")
    print("PASS")


def test_4_high_drift_and_low_correlation():
    """The audit claims high drift (0.85) from original purpose and low
    correlation (0.25) to real physical signals. Lock in the direction."""
    print("\n--- TEST 4: drift and correlation match notes ---")
    assert MONEY_AUDIT.first_principles.drift_score >= 0.7, \
        f"FAIL: drift_score should be high, got " \
        f"{MONEY_AUDIT.first_principles.drift_score}"
    assert MONEY_AUDIT.correlation_to_real_signal <= 0.5, \
        f"FAIL: correlation should be low, got " \
        f"{MONEY_AUDIT.correlation_to_real_signal}"
    print(f"  drift_score:              "
          f"{MONEY_AUDIT.first_principles.drift_score}")
    print(f"  correlation_to_real:      "
          f"{MONEY_AUDIT.correlation_to_real_signal}")
    print("PASS")


def test_5_summary_matches_spec():
    """summary() returns the documented shape."""
    print("\n--- TEST 5: summary shape ---")
    s = MONEY_AUDIT.summary()
    assert s["term"] == "money"
    assert s["is_signal"] is False
    assert len(s["failure_modes"]) == 7
    assert s["drift_score"] == MONEY_AUDIT.first_principles.drift_score
    assert s["correlation_to_real_signal"] == \
        MONEY_AUDIT.correlation_to_real_signal
    print(f"  is_signal:            {s['is_signal']}")
    print(f"  len(failure_modes):   {len(s['failure_modes'])}")
    print("PASS")


if __name__ == "__main__":
    test_1_money_is_not_a_signal()
    test_2_failure_modes_cover_all_criteria()
    test_3_every_score_has_justification()
    test_4_high_drift_and_low_correlation()
    test_5_summary_matches_spec()
    print("\nall money_audit tests passed.")
