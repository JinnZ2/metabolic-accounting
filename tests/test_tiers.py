"""
tests/test_tiers.py

Locks in the term-tier structure from term_audit/tiers.py and the
human-facing list in docs/TERMS_TO_AUDIT.md.

Anyone quietly removing or reorganizing a tier silently weakens the
framework's coverage of the known-drift vocabulary. These tests
catch the drift.

Run:  python -m tests.test_tiers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.tiers import (
    ALL_TIERS, find_tier, all_terms, duplicate_terms,
    TIER_1_FOUNDATIONAL, TIER_2_LABOR_AND_HUMAN_WORTH,
    TIER_3_ORGANIZATIONAL_LEGITIMACY, TIER_4_CAPACITY_MEASUREMENTS,
    TIER_5_SOCIAL_AND_BEHAVIORAL, TIER_6_KNOWLEDGE_AND_TRUTH,
    TIER_7_ENVIRONMENTAL_AND_RESOURCE,
)


def test_1_seven_tiers_present():
    """Seven tiers registered. If a tier is added or removed, update
    this count and docs/TERMS_TO_AUDIT.md together."""
    print("\n--- TEST 1: seven tiers registered ---")
    assert len(ALL_TIERS) == 7, \
        f"FAIL: expected 7 tiers, got {len(ALL_TIERS)}"
    numbers = [t.number for t in ALL_TIERS]
    assert numbers == [1, 2, 3, 4, 5, 6, 7], \
        f"FAIL: tier numbers out of order: {numbers}"
    print(f"  tiers: {numbers}")
    print("PASS")


def test_2_tier_1_is_foundational():
    """Tier 1 is structurally load-bearing for tiers 2-5. The eight
    terms registered here must include the currency / money / capital
    core because cracking those is what propagates upward."""
    print("\n--- TEST 2: Tier 1 foundational content ---")
    assert TIER_1_FOUNDATIONAL.number == 1
    required = {"money", "currency", "capital", "value"}
    missing = required - set(TIER_1_FOUNDATIONAL.terms)
    assert not missing, f"FAIL: Tier 1 missing {missing}"
    assert len(TIER_1_FOUNDATIONAL.terms) == 8, \
        f"FAIL: Tier 1 should have 8 terms, got " \
        f"{len(TIER_1_FOUNDATIONAL.terms)}"
    print(f"  Tier 1 terms ({len(TIER_1_FOUNDATIONAL.terms)}): "
          f"{TIER_1_FOUNDATIONAL.terms}")
    print("PASS")


def test_3_tiers_are_disjoint():
    """No term may appear in more than one tier. Duplication would
    hide which tier's framing applies to a given audit."""
    print("\n--- TEST 3: tiers are disjoint ---")
    dups = duplicate_terms()
    assert not dups, f"FAIL: duplicate terms across tiers: {dups}"
    print(f"  no duplicates across {len(ALL_TIERS)} tiers")
    print("PASS")


def test_4_find_tier_works_for_known_terms():
    """find_tier() returns the correct tier for known members, None
    for unknown terms. Case-insensitive, tolerant of space/hyphen
    normalization."""
    print("\n--- TEST 4: find_tier lookup ---")
    cases = [
        ("money",                  TIER_1_FOUNDATIONAL),
        ("MONEY",                  TIER_1_FOUNDATIONAL),
        ("productivity",           TIER_2_LABOR_AND_HUMAN_WORTH),
        ("best practices",         TIER_3_ORGANIZATIONAL_LEGITIMACY),
        ("best-practices",         TIER_3_ORGANIZATIONAL_LEGITIMACY),
        ("adhd",                   TIER_4_CAPACITY_MEASUREMENTS),
        ("misinformation",         TIER_5_SOCIAL_AND_BEHAVIORAL),
        ("peer_reviewed",          TIER_6_KNOWLEDGE_AND_TRUTH),
        ("externality",            TIER_7_ENVIRONMENTAL_AND_RESOURCE),
    ]
    for term, expected in cases:
        got = find_tier(term)
        assert got is expected, \
            f"FAIL: find_tier({term!r}) = {got!r}, expected {expected!r}"
    assert find_tier("bearing_capacity") is None, \
        "FAIL: basin metric should not be in the audit-tier list"
    print(f"  {len(cases)} lookups correct; unknowns return None")
    print("PASS")


def test_5_tier_4_framing_is_preserved():
    """The Tier 4 description must carry the environment-vs-person
    distinction. This is the framing observation that must not be
    silently dropped — see docs/TERMS_TO_AUDIT.md."""
    print("\n--- TEST 4: Tier 4 framing preserved ---")
    desc = TIER_4_CAPACITY_MEASUREMENTS.description
    # the load-bearing phrase — if rewritten, the test fails and forces
    # a deliberate decision
    required_phrases = [
        "disability does not exist",
        "environment",
        "person",
    ]
    for phrase in required_phrases:
        assert phrase in desc, \
            f"FAIL: Tier 4 description missing required phrase: {phrase!r}"
    print(f"  Tier 4 description carries environment-vs-person framing")
    print("PASS")


def test_6_tier_6_ai_drift_note_preserved():
    """The Tier 6 description must carry the AI-drift warning —
    this is the handoff to future AI sessions and must not be
    silently removed."""
    print("\n--- TEST 6: Tier 6 AI-drift note preserved ---")
    desc = TIER_6_KNOWLEDGE_AND_TRUTH.description
    required_phrases = [
        "sacred",    # near-sacred in training corpora
        "pull",      # the pull toward softening
    ]
    for phrase in required_phrases:
        assert phrase in desc, \
            f"FAIL: Tier 6 description missing AI-drift phrase: {phrase!r}"
    print(f"  Tier 6 description carries AI-drift warning")
    print("PASS")


def test_7_every_tier_has_terms():
    """No empty tiers — an empty tier is a vestigial category that
    should be either populated or removed with a note."""
    print("\n--- TEST 7: every tier has terms ---")
    for t in ALL_TIERS:
        assert len(t.terms) > 0, \
            f"FAIL: Tier {t.number} ({t.name}) is empty"
    total = len(all_terms())
    print(f"  {len(ALL_TIERS)} tiers, {total} terms total")
    assert total >= 60, f"FAIL: total terms dropped to {total}; " \
        "audit-coverage has thinned, investigate"
    print("PASS")


if __name__ == "__main__":
    test_1_seven_tiers_present()
    test_2_tier_1_is_foundational()
    test_3_tiers_are_disjoint()
    test_4_find_tier_works_for_known_terms()
    test_5_tier_4_framing_is_preserved()
    test_6_tier_6_ai_drift_note_preserved()
    test_7_every_tier_has_terms()
    print("\nall tier tests passed.")
