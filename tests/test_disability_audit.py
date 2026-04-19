"""
tests/test_disability_audit.py

Locks in the disability audit's three-measurement decomposition.

Per docs/TERMS_TO_AUDIT.md (Tier 4 framing): the audit targets the
measurement, not the person. The three measurements (A: environment
mismatch, B: bounded capacity, C: substrate damage) must remain
separable, and the load-bearing asymmetry — bounded-capacity failure
does NOT imply substrate damage — must be preserved.

If anyone collapses the three back into one TermAudit, edits the
B->C linkage to imply causation, or softens the
collapsed_usage_audit's environment-vs-person language, this test
catches it.

Run: python -m tests.test_disability_audit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.disability import (
    DISABILITY_A, DISABILITY_B, DISABILITY_C,
    ALL_DISABILITY_AUDITS, DISABILITY_LINKAGES,
    collapsed_usage_audit,
)
from term_audit.tiers import find_tier, TIER_4_CAPACITY_MEASUREMENTS


def test_1_three_measurements_kept_separate():
    """ALL_DISABILITY_AUDITS exposes exactly three audits, each with
    its own term namespace so they don't shadow the bare 'disability'
    token."""
    print("\n--- TEST 1: three measurements kept separate ---")
    assert len(ALL_DISABILITY_AUDITS) == 3, \
        f"FAIL: expected 3 audits, got {len(ALL_DISABILITY_AUDITS)}"
    expected = {"A_mismatch", "B_bounded_capacity", "C_substrate_damage"}
    assert set(ALL_DISABILITY_AUDITS) == expected
    # Each audit's term must be namespaced (not just 'disability')
    for key, audit in ALL_DISABILITY_AUDITS.items():
        assert audit.term.startswith("disability_"), \
            f"FAIL: {key} term '{audit.term}' should be namespaced"
        assert audit.term != "disability", \
            f"FAIL: {key} cannot use the bare collapsed token"
    print(f"  three audits: {sorted(ALL_DISABILITY_AUDITS)}")
    print("PASS")


def test_2_A_does_not_qualify_as_signal():
    """The relational mismatch measurement does not qualify as a
    signal because units vary across dimensions and there is no
    conservation law. This is correct — it is a relational geometry,
    not a conserved quantity."""
    print("\n--- TEST 2: A (mismatch) does not qualify as signal ---")
    assert not DISABILITY_A.is_signal(), \
        "FAIL: A should not qualify as a single-scalar signal"
    modes = set(DISABILITY_A.failure_modes())
    # the load-bearing failures: vector not scalar, no conservation
    assert "unit_invariant" in modes, \
        f"FAIL: A must fail unit_invariant, got {modes}"
    assert "conservation_or_law" in modes, \
        f"FAIL: A must fail conservation_or_law, got {modes}"
    print(f"  is_signal:     {DISABILITY_A.is_signal()}")
    print(f"  failure_modes: {sorted(modes)}")
    print("PASS")


def test_3_B_qualifies_as_signal():
    """The bounded-capacity measurement IS a signal when task and
    conditions are specified. This is the narrow legitimate
    operational use."""
    print("\n--- TEST 3: B (bounded capacity) qualifies as signal ---")
    assert DISABILITY_B.is_signal(), \
        "FAIL: B should qualify as a signal when scoped"
    print(f"  is_signal:     {DISABILITY_B.is_signal()}")
    print(f"  notes:         {DISABILITY_B.notes[:80]}...")
    print("PASS")


def test_4_C_qualifies_as_signal():
    """The substrate-damage measurement IS a signal when an
    individual baseline exists. The audit notes this collapses when
    population averages are substituted."""
    print("\n--- TEST 4: C (substrate damage) qualifies as signal ---")
    assert DISABILITY_C.is_signal(), \
        "FAIL: C should qualify as a signal when baselined"
    # the substitution warning must remain in the notes
    assert "baseline" in DISABILITY_C.notes.lower(), \
        "FAIL: C notes must keep the within-subject baseline caveat"
    assert "population" in DISABILITY_C.notes.lower(), \
        "FAIL: C notes must call out population-average substitution"
    print(f"  is_signal:     {DISABILITY_C.is_signal()}")
    print("PASS")


def test_5_linkages_documented():
    """Five linkages between A, B, C are documented."""
    print("\n--- TEST 5: linkages documented ---")
    assert len(DISABILITY_LINKAGES) == 5, \
        f"FAIL: expected 5 linkages, got {len(DISABILITY_LINKAGES)}"
    pairs = {(L.source, L.target) for L in DISABILITY_LINKAGES}
    expected = {("A", "B"), ("C", "B"), ("B", "C"), ("A", "C"), ("C", "A")}
    assert pairs == expected, \
        f"FAIL: linkage pairs mismatch.\n  got: {pairs}\n  exp: {expected}"
    print(f"  pairs: {sorted(pairs)}")
    print("PASS")


def test_6_B_does_not_imply_C():
    """LOAD-BEARING ASYMMETRY: bounded-capacity failure (B) does not
    imply substrate damage (C). The B->C linkage must remain
    relation='none' with strength_estimate=0.0. This is the assertion
    that prevents the collapsed token from sneaking back through the
    linkage layer."""
    print("\n--- TEST 6: B -> C asymmetry preserved ---")
    b_to_c = [L for L in DISABILITY_LINKAGES
              if L.source == "B" and L.target == "C"]
    assert len(b_to_c) == 1, \
        f"FAIL: expected exactly one B->C linkage, got {len(b_to_c)}"
    link = b_to_c[0]
    assert link.relation == "none", \
        f"FAIL: B->C must be relation='none', got '{link.relation}'. " \
        "If you change this, you are asserting that capacity failure " \
        "implies substrate damage — which is the exact category error " \
        "the audit exists to prevent."
    assert link.strength_estimate == 0.0, \
        f"FAIL: B->C strength must be 0.0, got {link.strength_estimate}"
    assert "asymmetry" in link.strength_justification.lower(), \
        "FAIL: B->C justification must keep the asymmetry callout"
    print(f"  B -> C: relation='{link.relation}', strength={link.strength_estimate}")
    print("PASS")


def test_7_collapsed_usage_audit_carries_framing():
    """The collapsed-usage audit must surface the environment-vs-person
    relocation in its 'consequence' field. This is the Tier 4 framing
    requirement from docs/TERMS_TO_AUDIT.md."""
    print("\n--- TEST 7: collapsed_usage_audit carries Tier 4 framing ---")
    audit = collapsed_usage_audit()
    expected_keys = {"term", "claim", "failure", "consequence", "remediation"}
    assert set(audit) == expected_keys, \
        f"FAIL: keys mismatch {set(audit)}"
    consequence = audit["consequence"].lower()
    # the load-bearing phrases — environment, structural, individuals
    for phrase in ("environment", "individual"):
        assert phrase in consequence, \
            f"FAIL: consequence must keep phrase '{phrase}' " \
            f"(Tier 4 framing); got: {audit['consequence']!r}"
    # remediation must say 'separate the three' or equivalent
    assert "separate" in audit["remediation"].lower(), \
        "FAIL: remediation must say to separate the measurements"
    print(f"  framing preserved: environment, individual, separate")
    print("PASS")


def test_8_disability_is_in_tier_4():
    """The bare 'disability' token belongs to Tier 4 in the
    audit-priority registry. Confirms the cross-reference between
    this audit and the tier system is consistent."""
    print("\n--- TEST 8: 'disability' registered in Tier 4 ---")
    tier = find_tier("disability")
    assert tier is TIER_4_CAPACITY_MEASUREMENTS, \
        f"FAIL: expected Tier 4, got {tier}"
    print(f"  tier: {tier.number} ({tier.name})")
    print("PASS")


if __name__ == "__main__":
    test_1_three_measurements_kept_separate()
    test_2_A_does_not_qualify_as_signal()
    test_3_B_qualifies_as_signal()
    test_4_C_qualifies_as_signal()
    test_5_linkages_documented()
    test_6_B_does_not_imply_C()
    test_7_collapsed_usage_audit_carries_framing()
    test_8_disability_is_in_tier_4()
    print("\nall disability audit tests passed.")
