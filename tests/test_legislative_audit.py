"""
tests/test_legislative_audit.py

Tripwires for term_audit/legislative_audit/first_principles_legislative_audit.py.

The module audits rules/regulations/legislation against their declared
purpose, assumed context, and actual consequences — not compliance with
them. Skeleton landed in AUDIT_09.

Tests lock in:

  1. module imports cleanly
  2. both example audits construct without error (intake regression
     for the `alternative_mechanchanisms` typo fixed at skeleton time)
  3. scores stay in [0, 1]; summary + AI context render non-empty
  4. `context_validity` correctly differentiates valid / invalid /
     undeclared contexts
  5. bridge-permit audit surfaces the contradiction (rule causes the
     harm it was meant to prevent) — load-bearing: if this flips,
     the skeleton has stopped doing what it was designed for
  6. Good-Samaritan audit surfaces the transmission / chilling effect
  7. the scoring functions respond monotonically to the contradiction
     and transmission fields they depend on
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import replace

from term_audit.legislative_audit.first_principles_legislative_audit import (
    EnvironmentType,
    ConsequenceBearer,
    LegislativeAudit,
    audit_bridge_permit_constrained,
    audit_good_samaritan_chilling_effect,
)


def test_1_module_imports():
    print("\n--- TEST 1: module imports ---")
    assert EnvironmentType is not None
    assert LegislativeAudit is not None
    assert audit_bridge_permit_constrained is not None
    assert audit_good_samaritan_chilling_effect is not None
    print("  all expected symbols exposed")
    print("PASS")


def test_2_example_audits_construct():
    """Regression: the supplied spec had a typo
    (`alternative_mechanchanisms`) in the bridge audit that would
    have raised TypeError at construction. Skeleton intake fixed it."""
    print("\n--- TEST 2: example audits construct ---")
    bridge = audit_bridge_permit_constrained()
    gs = audit_good_samaritan_chilling_effect()
    assert isinstance(bridge, LegislativeAudit)
    assert isinstance(gs, LegislativeAudit)
    print("  bridge + Good Samaritan audits construct")
    print("PASS")


def test_3_scores_and_rendering():
    print("\n--- TEST 3: scores bounded and rendering non-empty ---")
    for audit in (audit_bridge_permit_constrained(),
                  audit_good_samaritan_chilling_effect()):
        a = audit.purpose_alignment_score()
        h = audit.harm_score()
        assert 0.0 <= a <= 1.0, f"FAIL: alignment={a} out of [0,1]"
        assert 0.0 <= h <= 1.0, f"FAIL: harm={h} out of [0,1]"

        s = audit.summary()
        c = audit.to_ai_context()
        assert s.strip() and audit.rule_name in s
        assert c.strip() and audit.rule_name in c
    print("  both audits: scores in [0,1], summary + AI context render")
    print("PASS")


def test_4_context_validity():
    print("\n--- TEST 4: context_validity discriminates ---")
    bridge = audit_bridge_permit_constrained()

    # Declared valid
    assert bridge.context_validity(EnvironmentType.BUFFERED_STABLE) == 0.9
    assert bridge.context_validity(EnvironmentType.THIN_BUFFER) == 0.9

    # Declared invalid
    assert bridge.context_validity(EnvironmentType.CONSTRAINED) == 0.2
    assert bridge.context_validity(EnvironmentType.AUSTERE) == 0.2
    assert bridge.context_validity(EnvironmentType.COLLAPSE) == 0.2

    print(f"  BUFFERED_STABLE -> 0.9  CONSTRAINED -> 0.2")
    print("PASS")


def test_5_bridge_audit_surfaces_contradiction():
    """LOAD-BEARING: the bridge-permit example is the framework's
    canonical worked case. If the contradiction analysis stops
    surfacing the rule as self-contradictory, the skeleton has
    regressed on its own purpose."""
    print("\n--- TEST 5: bridge audit surfaces contradiction ---")
    bridge = audit_bridge_permit_constrained()

    assert bridge.contradiction.contradicts_purpose is True, \
        "FAIL: bridge audit no longer flags contradiction"
    assert bridge.contradiction.prevents_intended_outcome is True
    assert bridge.contradiction.harms_intended_beneficiary is True
    assert EnvironmentType.CONSTRAINED in bridge.contradiction.contradiction_contexts
    assert bridge.exception_pathway.functions_in_practice is False, \
        "FAIL: bridge exception pathway should fail in practice"

    alignment = bridge.purpose_alignment_score()
    harm = bridge.harm_score()
    assert alignment <= 0.4, f"FAIL: bridge alignment={alignment} too high for a contradicting rule"
    assert harm >= 0.6, f"FAIL: bridge harm={harm} too low for out-of-scope application"

    print(f"  contradicts_purpose=True  alignment={alignment:.2f}  harm={harm:.2f}")
    print("PASS")


def test_6_good_samaritan_surfaces_chilling_effect():
    """LOAD-BEARING: the chilling effect is what the Good Samaritan
    audit exists to name. If discourages_transmission or
    knowledge_dies_with_holder regress to False, the audit has
    stopped being the audit."""
    print("\n--- TEST 6: Good Samaritan surfaces chilling effect ---")
    gs = audit_good_samaritan_chilling_effect()

    assert gs.transmission_effect.discourages_transmission is True, \
        "FAIL: Good Samaritan audit no longer flags transmission chill"
    assert gs.transmission_effect.knowledge_dies_with_holder is True
    assert gs.transmission_effect.chilling_effect_observed is True
    assert gs.transmission_effect.teaching_becomes_liability is True

    assert gs.contradiction.contradicts_purpose is True
    assert gs.exception_pathway.functions_in_practice is False

    print(f"  discourages_transmission=True  knowledge_dies_with_holder=True")
    print("PASS")


def test_7_scoring_responds_to_contradiction_and_transmission():
    """purpose_alignment_score and harm_score must respond monotonically
    to the fields they read. Bridge + Good Samaritan both saturate at
    the [0,1] clamp, so this test builds a clean baseline via replace()
    where the raw score isn't pinned, then flips inputs one at a time
    and verifies the clamp-free scoring responds correctly."""
    print("\n--- TEST 7: scoring responds to its inputs ---")
    bridge = audit_bridge_permit_constrained()

    # Build a clean baseline: strip contradiction, transmission chill,
    # purpose drift, exception-pathway failure. Raw score should be
    # near 1.0.
    clean = replace(
        bridge,
        first_principles=replace(bridge.first_principles, purpose_drift=None),
        scope=replace(bridge.scope, scope_declared=True),
        contradiction=replace(
            bridge.contradiction,
            contradicts_purpose=False,
            prevents_intended_outcome=False,
            harms_intended_beneficiary=False,
        ),
        transmission_effect=replace(
            bridge.transmission_effect,
            discourages_transmission=False,
            knowledge_dies_with_holder=False,
        ),
        exception_pathway=replace(
            bridge.exception_pathway,
            functions_in_practice=True,
        ),
    )
    clean_score = clean.purpose_alignment_score()
    assert clean_score > 0.9, \
        f"FAIL: clean baseline alignment={clean_score}, want > 0.9"

    # Flip contradiction ON: score should drop.
    with_contradiction = replace(
        clean,
        contradiction=replace(clean.contradiction, contradicts_purpose=True),
    )
    assert with_contradiction.purpose_alignment_score() < clean_score, \
        "FAIL: adding contradiction did not drop alignment"

    # Flip transmission chill ON: score should drop.
    with_chill = replace(
        clean,
        transmission_effect=replace(
            clean.transmission_effect,
            discourages_transmission=True,
            knowledge_dies_with_holder=True,
        ),
    )
    assert with_chill.purpose_alignment_score() < clean_score, \
        "FAIL: adding transmission chill did not drop alignment"

    # harm_score responds to unintended + contradiction.
    no_unintended = replace(
        bridge,
        consequences_of_having=replace(
            bridge.consequences_of_having,
            primary_unintended=[],
            secondary=[],
        ),
        contradiction=replace(
            bridge.contradiction,
            prevents_intended_outcome=False,
            harms_intended_beneficiary=False,
        ),
        transmission_effect=replace(
            bridge.transmission_effect,
            knowledge_dies_with_holder=False,
        ),
    )
    assert no_unintended.harm_score() < bridge.harm_score(), \
        "FAIL: removing harm drivers did not lower harm score"

    print(f"  clean baseline={clean_score:.2f}  "
          f"+contradiction={with_contradiction.purpose_alignment_score():.2f}  "
          f"+chill={with_chill.purpose_alignment_score():.2f}")
    print(f"  bridge harm={bridge.harm_score():.2f}  "
          f"minus drivers={no_unintended.harm_score():.2f}")
    print("PASS")


if __name__ == "__main__":
    test_1_module_imports()
    test_2_example_audits_construct()
    test_3_scores_and_rendering()
    test_4_context_validity()
    test_5_bridge_audit_surfaces_contradiction()
    test_6_good_samaritan_surfaces_chilling_effect()
    test_7_scoring_responds_to_contradiction_and_transmission()
    print("\nall legislative_audit tests passed.")
