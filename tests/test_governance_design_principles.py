"""
tests/test_governance_design_principles.py

Tripwires for term_audit/governance_design_principles.py.

Locks in:
  - 13 principles across 6 categories
  - each principle has required fields
  - falsifiable predictions registered
  - compliance assessment structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.governance_design_principles import (
    DESIGN_PRINCIPLES,
    PrincipleCategory,
    FALSIFIABLE_PREDICTIONS,
    CURRENT_FINANCIAL_ACCOUNTING_ASSESSMENT,
    assess_system_compliance,
)


def test_1_thirteen_principles_registered():
    """Exactly 13 design principles across 6 categories."""
    print("\n--- TEST 1: 13 principles registered ---")
    assert len(DESIGN_PRINCIPLES) == 13, \
        f"FAIL: expected 13 principles, got {len(DESIGN_PRINCIPLES)}"

    categories = set(p.category for p in DESIGN_PRINCIPLES)
    assert len(categories) == 6, \
        f"FAIL: expected 6 categories, got {len(categories)}"

    print(f"  {len(DESIGN_PRINCIPLES)} principles in {len(categories)} categories")
    print("PASS")


def test_2_principle_ids_are_unique():
    """Each principle must have a unique ID."""
    print("\n--- TEST 2: principle IDs unique ---")
    ids = [p.id for p in DESIGN_PRINCIPLES]
    assert len(ids) == len(set(ids)), \
        f"FAIL: duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"

    # IDs should follow REF-x, SET-x, SCA-x, FEE-x, AUT-x, PRE-x pattern
    for pid in ids:
        assert pid[:3] in {"REF", "SET", "SCA", "FEE", "AUT", "PRE"}, \
            f"FAIL: invalid ID prefix: {pid}"
        assert pid[3] == "-"
        assert pid[4:].isdigit()

    print(f"  {len(ids)} unique IDs")
    print("PASS")


def test_3_all_principles_have_required_fields():
    """Each principle must have all eight required fields."""
    print("\n--- TEST 3: principles have required fields ---")
    required = {
        "id", "category", "principle", "derived_from",
        "rationale", "falsification_test", "implementation_constraint",
        "violation_example",
    }

    for p in DESIGN_PRINCIPLES:
        missing = required - set(p.__dict__.keys())
        assert not missing, f"FAIL: {p.id} missing fields: {missing}"
        # All string fields should be non-empty
        for field in ["principle", "rationale", "falsification_test",
                      "implementation_constraint", "violation_example"]:
            val = getattr(p, field)
            assert val and val.strip(), \
                f"FAIL: {p.id} has empty {field}"

    print(f"  all {len(DESIGN_PRINCIPLES)} principles have required fields")
    print("PASS")


def test_4_derived_from_references_valid_audits():
    """Each principle's derived_from should reference actual audits."""
    print("\n--- TEST 4: derived_from references valid audits ---")
    known_audits = {
        "money", "productivity", "efficiency", "expertise", "value",
        "disability", "incentive_analysis", "systemic_necessity",
        "civilization_scaling", "collapse_propensity", "recovery_pathways",
        "metabolic_accounting", "thermodynamics",
    }

    for p in DESIGN_PRINCIPLES:
        for audit in p.derived_from:
            assert audit in known_audits, \
                f"FAIL: {p.id} references unknown audit '{audit}'"

    print(f"  all derived_from references are valid")
    print("PASS")


def test_5_category_distribution():
    """Each category should have at least one principle."""
    print("\n--- TEST 5: category distribution ---")
    cat_counts = {}
    for p in DESIGN_PRINCIPLES:
        cat_counts[p.category] = cat_counts.get(p.category, 0) + 1

    for cat in PrincipleCategory:
        assert cat in cat_counts, \
            f"FAIL: category {cat.value} has no principles"

    print(f"  category counts: {dict(cat_counts)}")
    print("PASS")


def test_6_falsifiable_predictions_registered():
    """Five falsifiable predictions with correct schema."""
    print("\n--- TEST 6: falsifiable predictions registered ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 5, \
        f"FAIL: expected 5 predictions, got {len(FALSIFIABLE_PREDICTIONS)}"

    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}
        assert p["claim"].strip() and p["falsification"].strip()

    ids = [p["id"] for p in FALSIFIABLE_PREDICTIONS]
    assert ids == list(range(1, 6)), f"FAIL: expected IDs 1-5, got {ids}"

    print(f"  {len(FALSIFIABLE_PREDICTIONS)} predictions")
    print("PASS")


def test_7_financial_accounting_compliance_assessment():
    """The example assessment of GAAP/IFRS should produce valid scores."""
    print("\n--- TEST 7: financial accounting compliance assessment ---")
    result = assess_system_compliance(
        "GAAP/IFRS",
        CURRENT_FINANCIAL_ACCOUNTING_ASSESSMENT,
    )

    assert result["system"] == "GAAP/IFRS"
    assert 0.0 <= result["overall_compliance"] <= 1.0
    assert len(result["category_scores"]) > 0
    assert result["assessment_count"] == len(CURRENT_FINANCIAL_ACCOUNTING_ASSESSMENT)

    # Current system should score poorly (this is the audit's claim)
    assert result["overall_compliance"] < 0.4, \
        f"FAIL: GAAP/IFRS compliance {result['overall_compliance']} should be < 0.4"

    print(f"  overall compliance: {result['overall_compliance']:.2f}")
    print(f"  critical violations: {len(result['critical_violations'])}")
    print("PASS")


def test_8_principle_falsifiability():
    """Each falsification test should describe what would falsify the principle."""
    print("\n--- TEST 8: falsification tests are actionable ---")
    for p in DESIGN_PRINCIPLES:
        test = p.falsification_test
        # Should contain action verbs indicating what to measure
        action_words = ["identify", "measure", "track", "compare", "show", "demonstrate"]
        has_action = any(word in test.lower() for word in action_words)
        assert has_action, \
            f"FAIL: {p.id} falsification test lacks action verb: {test[:50]}"

    print(f"  all {len(DESIGN_PRINCIPLES)} principles have actionable falsification tests")
    print("PASS")


def test_9_implementation_constraints_are_specific():
    """Implementation constraints should be specific enough to build from."""
    print("\n--- TEST 9: implementation constraints are specific ---")
    for p in DESIGN_PRINCIPLES:
        constraint = p.implementation_constraint
        # Should contain "must" or "shall" or "requires"
        assert any(word in constraint.lower() for word in ["must", "shall", "require"]), \
            f"FAIL: {p.id} constraint lacks requirement language"

    print(f"  all {len(DESIGN_PRINCIPLES)} constraints are specific")
    print("PASS")


if __name__ == "__main__":
    test_1_thirteen_principles_registered()
    test_2_principle_ids_are_unique()
    test_3_all_principles_have_required_fields()
    test_4_derived_from_references_valid_audits()
    test_5_category_distribution()
    test_6_falsifiable_predictions_registered()
    test_7_financial_accounting_compliance_assessment()
    test_8_principle_falsifiability()
    test_9_implementation_constraints_are_specific()
    print("\nall governance_design_principles tests passed.")
