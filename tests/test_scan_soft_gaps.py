"""
tests/test_scan_soft_gaps.py

Tripwires for scripts/scan_soft_gaps.py (AUDIT_21 Part A).

Locks:
  1. scan() walks 9 Tier 1 audits (money + 4 value + 4 capital)
  2. each row has the expected shape + consistent internal arithmetic
  3. aggregate() totals match per-row sums
  4. the specific post-AUDIT_19 soft-gap map is stable:
     - money: unit_invariant + observer_invariant (2 gaps)
     - money has the two attached scope_audits from AUDIT_19 § C
     - total 14 soft gaps across 63 provenance records
     - 2 scope_audits attached tree-wide
  5. every Tier 1 audit still shows 7/7 complete (AUDIT_07 preserved)

If any of these invariants shift, callers have either retrofitted
scope_audits (good — update the expected counts) or regressed
AUDIT_07 coverage (bad — investigate).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scan_soft_gaps import scan, aggregate, AuditSoftGapRow


def test_1_scan_walks_nine_tier_one_audits():
    print("\n--- TEST 1: scan walks 9 Tier 1 audits ---")
    rows = scan()
    assert len(rows) == 9, f"FAIL: expected 9 rows, got {len(rows)}"
    labels = {r.audit_term for r in rows}
    expected = {
        "money",
        "value::collapsed",
        "value::V_A_use_value",
        "value::V_B_exchange_value",
        "value::V_C_substrate_value",
        "capital::collapsed",
        "capital::K_A_productive",
        "capital::K_B_financial",
        "capital::K_C_institutional",
    }
    assert labels == expected, f"FAIL: got {labels}"
    print(f"  9 audits: {sorted(labels)}")
    print("PASS")


def test_2_row_shape_and_internal_consistency():
    print("\n--- TEST 2: row shape + internal consistency ---")
    rows = scan()
    for r in rows:
        assert isinstance(r, AuditSoftGapRow)
        assert r.total_provenances >= 0
        assert r.complete >= 0
        assert r.scope_audit_count >= 0
        assert r.soft_gap_count >= 0
        assert r.complete <= r.total_provenances
        assert r.scope_audit_count <= r.total_provenances
        # the number of tripped-criterion strings must equal the
        # recorded soft_gap_count (no double-counting)
        assert len(r.soft_gap_criteria) == r.soft_gap_count
    print(f"  all 9 rows internally consistent")
    print("PASS")


def test_3_aggregate_matches_per_row_sums():
    print("\n--- TEST 3: aggregate matches per-row sums ---")
    rows = scan()
    agg = aggregate(rows)
    assert agg["n_audits"] == len(rows)
    assert agg["total_provenances"] == sum(r.total_provenances for r in rows)
    assert agg["total_complete"] == sum(r.complete for r in rows)
    assert agg["total_scope_audits_attached"] == \
        sum(r.scope_audit_count for r in rows)
    assert agg["total_soft_gaps"] == sum(r.soft_gap_count for r in rows)
    print(f"  aggregate totals consistent with per-row sums")
    print("PASS")


def test_4_post_audit_19_soft_gap_map_stable():
    """LOAD-BEARING: the specific soft-gap map as of AUDIT_19 § C is
    the honest baseline. If a retrofit happens (good — attach a
    StudyScopeAudit), the counts move; if a score moves without a
    retrofit, something structural shifted.

    Post-AUDIT_19 state:
      - money has 2 attached scope_audits (Boskin + BoE 2014) and
        2 remaining soft gaps (unit_invariant + observer_invariant
        EMPIRICAL records with scope_caveat but no audit)
      - all other Tier 1 audits have 0 attached scope_audits
      - total soft gaps across tree: 14
      - total scope_audits attached: 2
      - total provenance records: 63
    """
    print("\n--- TEST 4: post-AUDIT_19 soft-gap map stable ---")
    rows = scan()
    agg = aggregate(rows)

    # money's specific shape
    money_row = next(r for r in rows if r.audit_term == "money")
    assert money_row.scope_audit_count == 2, \
        f"FAIL: money scope_audit_count = {money_row.scope_audit_count}"
    assert money_row.soft_gap_count == 2, \
        f"FAIL: money soft_gap_count = {money_row.soft_gap_count}"
    assert set(money_row.soft_gap_criteria) == \
        {"unit_invariant", "observer_invariant"}

    # Tree-wide totals
    assert agg["total_scope_audits_attached"] == 2
    assert agg["total_soft_gaps"] == 14, \
        f"FAIL: expected 14 tree-wide soft gaps, got {agg['total_soft_gaps']}"
    assert agg["total_provenances"] == 63

    print(f"  money: 2 scope_audits attached, 2 remaining gaps")
    print(f"  tree-wide: 2 attached / 14 remaining / 63 total provenances")
    print("PASS")


def test_5_audit_07_preservation():
    """AUDIT_07's completeness discipline must survive every retrofit
    cycle. The scanner surfaces SignalScore-level coverage across
    the 9 Tier 1 audits (63 scores total — AUDIT_07's 74-figure
    also included linkage strength_estimates, a separate surface
    not scanned here). For each audit row, complete must equal
    total_provenances."""
    print("\n--- TEST 5: per-row Tier 1 completeness preserved ---")
    rows = scan()
    for r in rows:
        assert r.complete == r.total_provenances, \
            (f"FAIL: {r.audit_term} has complete={r.complete} but "
             f"total={r.total_provenances} — AUDIT_07 regression")
    agg = aggregate(rows)
    assert agg["total_complete"] == agg["total_provenances"]
    assert agg["total_provenances"] == 63, \
        "FAIL: Tier 1 SignalScore count changed; inspect schema drift"
    print(f"  {agg['total_complete']}/{agg['total_provenances']} "
          f"Tier-1 SignalScores complete")
    print("PASS")


if __name__ == "__main__":
    test_1_scan_walks_nine_tier_one_audits()
    test_2_row_shape_and_internal_consistency()
    test_3_aggregate_matches_per_row_sums()
    test_4_post_audit_19_soft_gap_map_stable()
    test_5_audit_07_preservation()
    print("\nall scan_soft_gaps tests passed.")
