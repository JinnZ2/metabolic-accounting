"""
tests/test_name_set_consistency.py

Tripwires for scripts/name_set_consistency.py (AUDIT_24).

Where counts_consistency is SCALAR (declared count == live count),
name_set_consistency is STRUCTURAL (declared set == live set,
bidirectionally). A pure counts check would miss:
  "set A and set B both have 9 elements but one element differs"

This test asserts every declared pair's sets agree in both
directions. If the Tier 1 audits gain a new term but the morphism
graph builder doesn't know about it (or vice versa), this test
catches the drift before it lands in the codebase.

Locks in:
  1. All 3 declared pairs agree bidirectionally (zero missing in
     either direction).
  2. Each declared pair is tripwired on both directions
     independently — catches the failure mode where one side gains
     a name and the other loses one (same cardinality, different
     content).
  3. Pair labels are unique (copy-paste guard).
  4. main() returns 0 at baseline (command-line contract).
  5. At least one pair has cardinality > 0 (guards the trivial
     empty-set case where both sets are empty and drift is hidden).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.name_set_consistency import (
    PAIRS, build_rows, main, report,
)


def test_1_all_pairs_agree():
    """LOAD-BEARING: every declared pair must agree bidirectionally.
    Drift in either direction => fail with readable message."""
    print("\n--- TEST 1: all declared pairs agree bidirectionally ---")
    rows = build_rows()
    drift = [r for r in rows if not r.ok]
    if drift:
        print(report(rows))
        lines = []
        for r in drift:
            lines.append(f"  {r.pair_label}:")
            if r.missing_from_a:
                lines.append(
                    f"    missing from {r.a_label}: {list(r.missing_from_a)}"
                )
            if r.missing_from_b:
                lines.append(
                    f"    missing from {r.b_label}: {list(r.missing_from_b)}"
                )
        raise AssertionError(
            f"FAIL: {len(drift)} pair(s) drifted:\n" + "\n".join(lines)
        )
    print(f"  {len(rows)}/{len(rows)} pairs agree bidirectionally")
    print("PASS")


def test_2_each_pair_tripwired_both_directions():
    """Catches the 'same cardinality, different content' failure
    mode. For every pair, both `missing_from_a` and `missing_from_b`
    must be empty tuples. Not redundant with test_1 — this test
    asserts the bidirectional guarantee explicitly, one direction
    at a time, so the failure message points at exactly which
    direction drifted."""
    print("\n--- TEST 2: each pair is empty on BOTH directions ---")
    rows = build_rows()
    for r in rows:
        assert r.missing_from_a == (), (
            f"FAIL: {r.pair_label} missing_from_{r.a_label} = "
            f"{list(r.missing_from_a)} — the a-side is stale"
        )
        assert r.missing_from_b == (), (
            f"FAIL: {r.pair_label} missing_from_{r.b_label} = "
            f"{list(r.missing_from_b)} — the b-side is stale"
        )
    print(f"  {len(rows)} pairs pass both directions independently")
    print("PASS")


def test_3_pair_labels_unique():
    """Copy-paste accident guard."""
    print("\n--- TEST 3: pair labels are unique ---")
    labels = [p[0] for p in PAIRS]
    seen = set()
    dupes = []
    for lbl in labels:
        if lbl in seen:
            dupes.append(lbl)
        seen.add(lbl)
    assert not dupes, f"FAIL: duplicate pair labels: {dupes}"
    print(f"  {len(labels)} unique pair labels")
    print("PASS")


def test_4_main_returns_zero_at_baseline():
    """Command-line contract: exit 0 when all pairs agree."""
    print("\n--- TEST 4: main() returns 0 at baseline ---")
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main()
    assert rc == 0, f"FAIL: main() returned {rc} at baseline"
    out = buf.getvalue()
    assert "pairs agree" in out, (
        f"FAIL: report summary line missing"
    )
    print(f"  main() exit 0; summary line present")
    print("PASS")


def test_5_non_trivial_cardinality():
    """Guard against the degenerate-empty-set case: if both sides
    of a pair are empty, `set_a == set_b` trivially holds and the
    tripwire catches nothing. Assert at least one pair has
    cardinality >= 1 on both sides."""
    print("\n--- TEST 5: at least one pair has non-trivial cardinality ---")
    rows = build_rows()
    non_trivial = [r for r in rows if r.size_a >= 1 and r.size_b >= 1]
    assert non_trivial, (
        f"FAIL: every pair has an empty side; checks are vacuous"
    )
    print(f"  {len(non_trivial)}/{len(rows)} pairs have "
          f"cardinality >= 1 on both sides")
    print("PASS")


if __name__ == "__main__":
    test_1_all_pairs_agree()
    test_2_each_pair_tripwired_both_directions()
    test_3_pair_labels_unique()
    test_4_main_returns_zero_at_baseline()
    test_5_non_trivial_cardinality()
    print("\nall name_set_consistency tests passed.")
