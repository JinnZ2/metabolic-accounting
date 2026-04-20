"""
tests/test_provenance.py

Tripwires for term_audit/provenance.py.

Locks in:
  - five kinds exist (EMPIRICAL, THEORETICAL, DESIGN_CHOICE,
    PLACEHOLDER, STIPULATIVE)
  - constructor validators reject under-specified provenance
  - missing_fields() reports the right gaps per kind
  - knowledge_dna is a pass-through field (framework does not
    interpret)
  - coverage_report aggregates correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.provenance import (
    Provenance,
    ProvenanceKind,
    empirical,
    theoretical,
    design_choice,
    placeholder,
    stipulative,
    coverage_report,
)


def test_1_five_kinds_exist():
    """Provenance must have exactly five kinds."""
    print("\n--- TEST 1: five provenance kinds ---")
    kinds = {k.value for k in ProvenanceKind}
    expected = {
        "empirical", "theoretical", "design_choice",
        "placeholder", "stipulative",
    }
    assert kinds == expected, f"FAIL: got {kinds}, expected {expected}"
    print(f"  kinds: {sorted(kinds)}")
    print("PASS")


def test_2_empirical_requires_source_refs():
    """empirical() constructor must reject empty source_refs."""
    print("\n--- TEST 2: empirical requires source_refs ---")
    try:
        empirical(source_refs=[])
    except ValueError as e:
        print(f"  correctly rejected: {e}")
        print("PASS")
        return
    assert False, "FAIL: empirical() accepted empty source_refs"


def test_3_design_choice_requires_alternatives_and_falsification():
    """design_choice() must require both alternatives and falsification."""
    print("\n--- TEST 3: design_choice enforcement ---")
    try:
        design_choice(rationale="r", alternatives_considered=[],
                      falsification_test="t")
    except ValueError:
        pass
    else:
        assert False, "FAIL: design_choice accepted no alternatives"

    try:
        design_choice(rationale="r", alternatives_considered=["a"],
                      falsification_test="")
    except ValueError:
        pass
    else:
        assert False, "FAIL: design_choice accepted empty falsification_test"

    p = design_choice(
        rationale="because",
        alternatives_considered=["additive", "saturating"],
        falsification_test="sample and measure",
    )
    assert p.is_complete()
    print("  both required fields enforced")
    print("PASS")


def test_4_placeholder_requires_retirement_path():
    """placeholder() must reject empty retirement_path."""
    print("\n--- TEST 4: placeholder requires retirement_path ---")
    try:
        placeholder(rationale="guess", retirement_path="")
    except ValueError:
        print("  correctly rejected empty retirement_path")
        print("PASS")
        return
    assert False, "FAIL: placeholder accepted empty retirement_path"


def test_5_theoretical_requires_derivation_or_rationale():
    """theoretical() must require rationale (derivation name)."""
    print("\n--- TEST 5: theoretical requires rationale ---")
    try:
        theoretical(rationale="")
    except ValueError:
        print("  correctly rejected empty rationale")
        print("PASS")
        return
    assert False, "FAIL: theoretical accepted empty rationale"


def test_6_stipulative_requires_def_ref_or_rationale():
    """stipulative() must require at least one of definition_ref/rationale."""
    print("\n--- TEST 6: stipulative requires def_ref or rationale ---")
    try:
        stipulative(rationale="", definition_ref="")
    except ValueError:
        print("  correctly rejected empty fields")
        print("PASS")
        return
    assert False, "FAIL: stipulative accepted both empty"


def test_7_missing_fields_reports_gaps():
    """missing_fields() must report the right fields per kind."""
    print("\n--- TEST 7: missing_fields reports gaps ---")
    # A hand-built EMPIRICAL with no source_refs (bypassing constructor)
    p = Provenance(kind=ProvenanceKind.EMPIRICAL)
    assert "source_refs" in p.missing_fields()

    p = Provenance(kind=ProvenanceKind.DESIGN_CHOICE)
    missing = p.missing_fields()
    assert "alternatives_considered" in missing
    assert "falsification_test" in missing

    p = Provenance(kind=ProvenanceKind.PLACEHOLDER)
    assert "retirement_path" in p.missing_fields()

    p = Provenance(kind=ProvenanceKind.STIPULATIVE)
    assert "definition_ref_or_rationale" in p.missing_fields()

    p = Provenance(kind=ProvenanceKind.THEORETICAL)
    assert "source_refs_or_rationale" in p.missing_fields()

    print("  all five kinds surface their required fields")
    print("PASS")


def test_8_knowledge_dna_is_pass_through():
    """knowledge_dna must be accepted on every kind and never interpreted."""
    print("\n--- TEST 8: knowledge_dna pass-through ---")
    dna = "kdna://audit/v1/sha256:abc123"
    p1 = empirical(source_refs=["Smith 2021"], knowledge_dna=dna)
    p2 = design_choice(
        rationale="r",
        alternatives_considered=["a"],
        falsification_test="t",
        knowledge_dna=dna,
    )
    p3 = placeholder(rationale="r", retirement_path="p", knowledge_dna=dna)
    p4 = theoretical(rationale="Gouy-Stodola", knowledge_dna=dna)
    p5 = stipulative(rationale="by construction", knowledge_dna=dna)

    for p in [p1, p2, p3, p4, p5]:
        assert p.knowledge_dna == dna, \
            f"FAIL: dna not preserved on {p.kind.value}"
        assert p.is_complete(), f"FAIL: {p.kind.value} not complete"
    print(f"  dna preserved across all 5 kinds")
    print("PASS")


def test_9_coverage_report_aggregates():
    """coverage_report must count complete, incomplete, and none."""
    print("\n--- TEST 9: coverage_report aggregation ---")
    items = [
        empirical(source_refs=["A"]),                              # complete
        design_choice(                                              # complete
            rationale="r",
            alternatives_considered=["a"],
            falsification_test="t",
        ),
        Provenance(kind=ProvenanceKind.PLACEHOLDER),               # incomplete
        None,                                                       # none
        None,                                                       # none
        stipulative(rationale="r", knowledge_dna="kd://x"),        # complete
    ]
    rep = coverage_report(items)
    assert rep["total"] == 6
    assert rep["with_provenance"] == 4
    assert rep["complete"] == 3
    assert rep["incomplete"] == 1
    assert rep["none"] == 2
    assert rep["knowledge_dna_count"] == 1
    assert rep["by_kind"]["empirical"] == 1
    assert rep["by_kind"]["design_choice"] == 1
    assert rep["by_kind"]["placeholder"] == 1
    assert rep["by_kind"]["stipulative"] == 1
    assert len(rep["incomplete_details"]) == 1
    idx, kind, missing = rep["incomplete_details"][0]
    assert idx == 2 and kind == "placeholder"
    assert "retirement_path" in missing
    print(f"  6 items: 3 complete, 1 incomplete, 2 none, 1 with dna")
    print("PASS")


if __name__ == "__main__":
    test_1_five_kinds_exist()
    test_2_empirical_requires_source_refs()
    test_3_design_choice_requires_alternatives_and_falsification()
    test_4_placeholder_requires_retirement_path()
    test_5_theoretical_requires_derivation_or_rationale()
    test_6_stipulative_requires_def_ref_or_rationale()
    test_7_missing_fields_reports_gaps()
    test_8_knowledge_dna_is_pass_through()
    test_9_coverage_report_aggregates()
    print("\nall provenance tests passed.")
