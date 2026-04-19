"""
tests/test_term_audit.py

Smoke tests for the term_audit schema. Exercises:
  1. SignalScore validators reject unknown criteria and out-of-bounds scores
  2. A term with >= 5 criteria scored >= 0.7 registers as a signal
  3. A term with < 5 passing criteria does not
  4. failure_modes() returns criteria scored below 0.5
  5. summary() returns the expected keys

Run:  python -m tests.test_term_audit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit import (
    SIGNAL_CRITERIA, SignalScore, StandardSetter,
    FirstPrinciplesPurpose, TermAudit,
)


def _full_score_set(scores):
    """Build one SignalScore per criterion with the supplied score values."""
    assert len(scores) == len(SIGNAL_CRITERIA)
    return [
        SignalScore(
            criterion=c,
            score=s,
            justification=f"test score for {c}",
            source_refs=["test"],
        )
        for c, s in zip(SIGNAL_CRITERIA, scores)
    ]


def _fp(drift: float = 0.0) -> FirstPrinciplesPurpose:
    return FirstPrinciplesPurpose(
        stated_purpose="test",
        physical_referent="joules",
        informational_referent="bits",
        drift_score=drift,
        drift_justification="test",
    )


def test_1_signal_score_validators():
    """Unknown criterion names and out-of-bounds scores are rejected."""
    print("\n--- TEST 1: SignalScore validators ---")
    # valid
    s = SignalScore(
        criterion="scope_defined", score=0.5,
        justification="ok", source_refs=["ref"],
    )
    assert s.score == 0.5
    # unknown criterion
    try:
        SignalScore(criterion="not_a_criterion", score=0.5, justification="x")
    except ValueError as e:
        assert "unknown criterion" in str(e)
    else:
        assert False, "FAIL: unknown criterion should raise"
    # out-of-bounds
    for bad in (-0.1, 1.5):
        try:
            SignalScore(criterion="scope_defined", score=bad, justification="x")
        except ValueError as e:
            assert "out of bounds" in str(e)
        else:
            assert False, f"FAIL: score {bad} should raise"
    print("PASS")


def test_2_term_qualifies_as_signal():
    """A term with >= 5 criteria at score >= 0.7 qualifies."""
    print("\n--- TEST 2: term qualifies as signal ---")
    # 6 passing, 1 low
    scores = _full_score_set([0.9, 0.8, 0.8, 0.75, 0.7, 0.7, 0.3])
    audit = TermAudit(
        term="exergy",
        claimed_signal="available work in xdu",
        standard_setters=[StandardSetter(
            name="Gouy-Stodola theorem",
            authority_basis="physical law",
            incentive_structure="none",
            independence_from_measured=1.0,
        )],
        signal_scores=scores,
        first_principles=_fp(drift=0.0),
        correlation_to_real_signal=0.95,
        correlation_justification="tracks thermodynamic availability",
    )
    assert audit.is_signal(), "FAIL: 6 passing should qualify"
    assert audit.failure_modes() == ["falsifiability"], \
        f"FAIL: unexpected failure modes {audit.failure_modes()}"
    print(f"  is_signal:     {audit.is_signal()}")
    print(f"  failure_modes: {audit.failure_modes()}")
    print("PASS")


def test_3_term_fails_signal_threshold():
    """A term with < 5 passing criteria does not qualify."""
    print("\n--- TEST 3: term fails signal threshold ---")
    # 4 passing, 3 below 0.7 (two of those also below 0.5)
    scores = _full_score_set([0.9, 0.85, 0.8, 0.75, 0.6, 0.4, 0.3])
    audit = TermAudit(
        term="GDP",
        claimed_signal="aggregate economic output",
        standard_setters=[StandardSetter(
            name="BEA / SNA 2008",
            authority_basis="statute + international convention",
            incentive_structure="funded by measured states",
            independence_from_measured=0.2,
        )],
        signal_scores=scores,
        first_principles=_fp(drift=0.7),
        correlation_to_real_signal=0.4,
        correlation_justification=(
            "tracks monetary transaction volume, not wellbeing or "
            "physical throughput"
        ),
    )
    assert not audit.is_signal(), \
        "FAIL: 4 passing should not qualify as signal"
    assert set(audit.failure_modes()) == {
        "conservation_or_law", "falsifiability",
    }, f"FAIL: unexpected failure_modes {audit.failure_modes()}"
    print(f"  is_signal:     {audit.is_signal()}")
    print(f"  failure_modes: {audit.failure_modes()}")
    print("PASS")


def test_4_summary_shape():
    """summary() returns the expected keys and values."""
    print("\n--- TEST 4: summary shape ---")
    scores = _full_score_set([0.8] * 7)
    audit = TermAudit(
        term="test_term",
        claimed_signal="test",
        standard_setters=[],
        signal_scores=scores,
        first_principles=_fp(drift=0.1),
        correlation_to_real_signal=0.7,
        correlation_justification="test",
    )
    s = audit.summary()
    expected_keys = {
        "term", "claimed_signal", "is_signal",
        "failure_modes", "drift_score", "correlation_to_real_signal",
    }
    assert set(s.keys()) == expected_keys, \
        f"FAIL: unexpected summary keys {set(s.keys())}"
    assert s["is_signal"] is True
    assert s["failure_modes"] == []
    assert abs(s["drift_score"] - 0.1) < 1e-9
    print(f"  summary keys: {sorted(s.keys())}")
    print("PASS")


def test_5_threshold_is_tunable():
    """is_signal accepts a stricter threshold."""
    print("\n--- TEST 5: threshold is tunable ---")
    scores = _full_score_set([0.9, 0.9, 0.9, 0.9, 0.9, 0.6, 0.6])
    audit = TermAudit(
        term="test",
        claimed_signal="test",
        standard_setters=[],
        signal_scores=scores,
        first_principles=_fp(drift=0.0),
        correlation_to_real_signal=0.8,
        correlation_justification="test",
    )
    assert audit.is_signal(threshold=5)
    assert not audit.is_signal(threshold=7)
    print(f"  threshold=5: {audit.is_signal(threshold=5)}")
    print(f"  threshold=7: {audit.is_signal(threshold=7)}")
    print("PASS")


if __name__ == "__main__":
    test_1_signal_score_validators()
    test_2_term_qualifies_as_signal()
    test_3_term_fails_signal_threshold()
    test_4_summary_shape()
    test_5_threshold_is_tunable()
    print("\nall term_audit tests passed.")
