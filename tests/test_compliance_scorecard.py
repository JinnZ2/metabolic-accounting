"""
tests/test_compliance_scorecard.py

Tripwire for the ComplianceScorecard data structure introduced in
AUDIT_25. The structure mirrors math-econ's worked Smith-compliance
scorecard pattern (current US system: 0/8 criteria met against
Adam-Smith-style capitalism). The strict falsification boundary --
is_falsified() is True iff at least one criterion is `not_met` AND
zero are `met` -- is the load-bearing semantic.

Run: python -m tests.test_compliance_scorecard
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.falsification import (
    ComplianceCriterion, ComplianceScorecard, CRITERION_RESULT_VALUES,
)


def _criterion(name: str, result: str = "untested") -> ComplianceCriterion:
    return ComplianceCriterion(
        name=name,
        expected_indicator="theory predicts indicator I",
        observed_indicator="observed value O",
        threshold_description="met iff O within bounds of I",
        source_refs=["primary source for theory"],
        result=result,
    )


def test_1_unknown_result_value_rejected():
    """Constructing a criterion with a result outside CRITERION_RESULT_VALUES
    raises ValueError. The valid set must remain {met, not_met, ambiguous,
    untested}."""
    assert CRITERION_RESULT_VALUES == {"met", "not_met", "ambiguous", "untested"}
    raised = False
    try:
        ComplianceCriterion(
            name="x",
            expected_indicator="e",
            observed_indicator="o",
            threshold_description="t",
            result="passed",  # not a valid status
        )
    except ValueError:
        raised = True
    assert raised, "ComplianceCriterion accepted unknown result value"


def test_2_empty_scorecard_summary_is_well_defined():
    """A scorecard with no criteria reports zero on every count and
    None on fraction_met; is_falsified() is False (nothing to falsify)."""
    sc = ComplianceScorecard(
        claim="the empty system is X",
        theory_name="empty theory",
        theory_source_refs=[],
    )
    assert sc.n_total() == 0
    assert sc.n_met() == 0
    assert sc.n_not_met() == 0
    assert sc.n_ambiguous() == 0
    assert sc.n_untested() == 0
    assert sc.fraction_met() is None
    assert sc.is_falsified() is False
    summary = sc.summary()
    assert summary["claim"] == "the empty system is X"
    assert summary["fraction_met"] is None
    assert summary["is_falsified"] is False


def test_3_all_untested_does_not_falsify():
    """Untested criteria flag axes that *could* be tested but have not
    been; they cannot falsify the claim. fraction_met() is None when
    no criteria are decided."""
    sc = ComplianceScorecard(
        claim="claim X holds",
        theory_name="theory T",
        theory_source_refs=["T 1776"],
        criteria=[
            _criterion("c1", "untested"),
            _criterion("c2", "untested"),
            _criterion("c3", "ambiguous"),
        ],
    )
    assert sc.n_total() == 3
    assert sc.n_untested() == 2
    assert sc.n_ambiguous() == 1
    assert sc.n_met() == 0 and sc.n_not_met() == 0
    assert sc.fraction_met() is None
    assert sc.is_falsified() is False


def test_4_all_not_met_falsifies():
    """The Smith-0/8 worked example shape: every criterion measured,
    every criterion failing. is_falsified() must be True; fraction_met
    must be 0.0."""
    sc = ComplianceScorecard(
        claim="the system is Smith-style capitalism",
        theory_name="Smith-style capitalism",
        theory_source_refs=["Smith 1776, Wealth of Nations"],
        criteria=[_criterion(f"c{i}", "not_met") for i in range(8)],
    )
    assert sc.n_total() == 8
    assert sc.n_not_met() == 8
    assert sc.n_met() == 0
    assert sc.fraction_met() == 0.0
    assert sc.is_falsified() is True


def test_5_all_met_does_not_falsify():
    """Symmetric to test_4: every criterion met -> claim survives the
    test. fraction_met == 1.0; is_falsified() False."""
    sc = ComplianceScorecard(
        claim="the system is X",
        theory_name="theory T",
        theory_source_refs=["T 1776"],
        criteria=[_criterion(f"c{i}", "met") for i in range(5)],
    )
    assert sc.n_total() == 5
    assert sc.n_met() == 5
    assert sc.n_not_met() == 0
    assert sc.fraction_met() == 1.0
    assert sc.is_falsified() is False


def test_6_strict_falsification_boundary():
    """The load-bearing rule: a single `met` blocks falsification, even
    if every other decided criterion is `not_met`. This is intentional;
    partial compliance is a different finding than total failure, and
    the framework distinguishes them."""
    sc = ComplianceScorecard(
        claim="the system is X",
        theory_name="theory T",
        theory_source_refs=["T 1776"],
        criteria=[
            _criterion("c1", "met"),
            _criterion("c2", "not_met"),
            _criterion("c3", "not_met"),
            _criterion("c4", "not_met"),
            _criterion("c5", "ambiguous"),
            _criterion("c6", "untested"),
        ],
    )
    assert sc.n_met() == 1
    assert sc.n_not_met() == 3
    assert sc.fraction_met() == 1 / 4   # 1 met out of 4 decided
    assert sc.is_falsified() is False, (
        "is_falsified() must be False when any criterion is met, even "
        "if not_met outnumbers met -- partial compliance != falsification"
    )


def test_7_summary_keys_complete():
    """summary() must surface every count and the two derived fields,
    so a downstream consumer reading the dict does not silently miss
    a category."""
    sc = ComplianceScorecard(
        claim="claim",
        theory_name="theory",
        theory_source_refs=[],
        criteria=[
            _criterion("a", "met"),
            _criterion("b", "not_met"),
            _criterion("c", "ambiguous"),
            _criterion("d", "untested"),
        ],
    )
    s = sc.summary()
    expected_keys = {
        "claim", "theory_name",
        "n_total", "n_met", "n_not_met", "n_ambiguous", "n_untested",
        "fraction_met", "is_falsified",
    }
    assert expected_keys.issubset(set(s.keys())), (
        f"summary() missing keys: {expected_keys - set(s.keys())}"
    )
    assert s["n_total"] == 4
    assert s["n_met"] == 1
    assert s["n_not_met"] == 1
    assert s["n_ambiguous"] == 1
    assert s["n_untested"] == 1
    assert s["fraction_met"] == 0.5
    assert s["is_falsified"] is False


if __name__ == "__main__":
    test_1_unknown_result_value_rejected()
    test_2_empty_scorecard_summary_is_well_defined()
    test_3_all_untested_does_not_falsify()
    test_4_all_not_met_falsifies()
    test_5_all_met_does_not_falsify()
    test_6_strict_falsification_boundary()
    test_7_summary_keys_complete()
    print("test_compliance_scorecard PASS (7 tests)")
