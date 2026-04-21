"""
tests/test_signal_asymmetry.py

Tripwires for distributional/signal_asymmetry.py (AUDIT_14 Part C).

This is an interface stub — tests lock the shape, not an implementation.
Production cross-observer analysis lives in the sister repo per
Todo.md priority 2.

Tests lock:
  1. module imports; LITERATURE_ANCHORS carries the four documented
     strands (DNA, HANK, stratification, incidence)
  2. every LITERATURE_ANCHORS entry has complete typed Provenance
  3. observer_delta builds a structurally valid report
  4. observer_delta rejects an unknown literature_anchor_key
  5. asymmetry_ratio is None when value_a == 0 (no silent ZeroDivision)
  6. the sister-repo pointer is non-empty and names both target repos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distributional.signal_asymmetry import (
    ObserverAsymmetryReport,
    observer_delta,
    LITERATURE_ANCHORS,
    SISTER_REPO_IMPLEMENTATION_NOTE,
)
from term_audit.provenance import Provenance


def test_1_four_literature_anchors_present():
    print("\n--- TEST 1: four literature anchors registered ---")
    expected = {
        "distributional_national_accounts",
        "heterogeneous_agent_macro",
        "stratification_economics",
        "fiscal_incidence",
    }
    keys = set(LITERATURE_ANCHORS.keys())
    assert keys == expected, f"FAIL: expected {expected}, got {keys}"
    print(f"  {len(keys)} anchors: {sorted(keys)}")
    print("PASS")


def test_2_every_anchor_has_complete_provenance():
    """LOAD-BEARING: each literature anchor must be a complete
    Provenance record so the coverage-report surface (AUDIT_07)
    can see it. Regressing this erases the epistemic grounding
    the stub depends on."""
    print("\n--- TEST 2: every anchor carries complete Provenance ---")
    for key, prov in LITERATURE_ANCHORS.items():
        assert isinstance(prov, Provenance)
        missing = prov.missing_fields()
        assert not missing, f"FAIL: {key} incomplete: {missing}"
    print(f"  {len(LITERATURE_ANCHORS)}/{len(LITERATURE_ANCHORS)} anchors complete")
    print("PASS")


def test_3_observer_delta_builds_valid_report():
    print("\n--- TEST 3: observer_delta builds structurally valid report ---")
    r = observer_delta(
        subject="toy",
        observer_a="A",
        value_a=1.0,
        observer_b="B",
        value_b=3.0,
        caveats=("illustrative",),
        literature_anchor_key="heterogeneous_agent_macro",
    )
    assert isinstance(r, ObserverAsymmetryReport)
    assert r.subject == "toy"
    assert r.observers == ("A", "B")
    assert r.values == (1.0, 3.0)
    assert r.delta == 2.0
    assert r.asymmetry_ratio == 3.0
    assert r.literature_anchor_key == "heterogeneous_agent_macro"
    assert r.caveats == ("illustrative",)
    print(f"  delta=2.0, ratio=3.0 computed correctly")
    print("PASS")


def test_4_unknown_literature_anchor_key_rejected():
    print("\n--- TEST 4: unknown literature_anchor_key rejected ---")
    try:
        observer_delta(
            subject="toy", observer_a="A", value_a=1.0,
            observer_b="B", value_b=2.0,
            literature_anchor_key="astrology",
        )
    except ValueError as e:
        assert "astrology" in str(e)
        print(f"  rejected 'astrology' with named error")
        print("PASS")
        return
    raise AssertionError("FAIL: accepted unknown literature_anchor_key")


def test_5_asymmetry_ratio_handles_zero_baseline():
    """value_a == 0 must produce asymmetry_ratio = None, not
    ZeroDivisionError and not silent infinity."""
    print("\n--- TEST 5: asymmetry_ratio = None when value_a = 0 ---")
    r = observer_delta(
        subject="zero-baseline",
        observer_a="A", value_a=0.0,
        observer_b="B", value_b=1.0,
    )
    assert r.asymmetry_ratio is None
    assert r.delta == 1.0
    print(f"  delta=1.0, ratio=None (no silent infinity)")
    print("PASS")


def test_6_sister_repo_pointer_non_empty():
    """The whole point of the stub is to route users to the sister
    repo. If the pointer goes missing, the stub has lost its
    purpose."""
    print("\n--- TEST 6: sister-repo pointer names both target repos ---")
    assert "money_distribution" in SISTER_REPO_IMPLEMENTATION_NOTE
    assert "investment_distribution" in SISTER_REPO_IMPLEMENTATION_NOTE
    assert "thermodynamic-accountability-framework" in SISTER_REPO_IMPLEMENTATION_NOTE
    print(f"  both sister-repo targets named in pointer")
    print("PASS")


if __name__ == "__main__":
    test_1_four_literature_anchors_present()
    test_2_every_anchor_has_complete_provenance()
    test_3_observer_delta_builds_valid_report()
    test_4_unknown_literature_anchor_key_rejected()
    test_5_asymmetry_ratio_handles_zero_baseline()
    test_6_sister_repo_pointer_non_empty()
    print("\nall signal_asymmetry tests passed.")
