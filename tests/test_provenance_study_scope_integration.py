"""
tests/test_provenance_study_scope_integration.py

Tripwires for AUDIT_17: Provenance can carry a StudyScopeAudit
attachment on EMPIRICAL records.

Tests lock:
  1. Provenance.scope_audit defaults to None; existing records
     stay is_complete() and missing_fields() == []
  2. empirical() constructor accepts a scope_audit kwarg and
     stores it unchanged (object identity)
  3. has_scope_audit() returns True when attached, False when not
  4. soft_gap() returns None when scope_caveat is empty OR
     scope_audit is present
  5. soft_gap() returns a descriptive string when EMPIRICAL has
     a scope_caveat but no scope_audit (the load-bearing
     coverage signal)
  6. coverage_report surfaces scope_audit_count, soft_gap_count,
     and soft_gap_details
  7. existing Tier 1 audits still pass provenance_coverage() with
     zero incomplete — AUDIT_17 must not regress AUDIT_07's 74/74
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.provenance import (
    Provenance, ProvenanceKind,
    empirical, theoretical, design_choice, placeholder, stipulative,
    coverage_report,
)
from term_audit.study_scope_audit import (
    StudyScopeAudit, InstrumentAudit, ProtocolAudit, DomainCouplingAudit,
    RegimeAudit, CausalModelAudit, ScopeBoundary,
    Coupling, Regime,
)


def _toy_study_scope_audit():
    return StudyScopeAudit(
        claim="toy",
        citation="toy ref",
        instrument=InstrumentAudit(
            instrument_name="toy",
            physical_quantity_measured="toy",
            measurement_range=(0.0, 1.0),
            resolution=0.01,
            noise_floor=0.001,
            sampling_rate_hz=None,
            spatial_resolution=None,
            calibration_source="toy",
            calibration_traceability="toy",
            drift_rate=None,
        ),
        protocol=ProtocolAudit(
            sample_preparation="lab",
            environmental_controls={"temp": 22},
            excluded_conditions=[],
            control_group_definition="untreated",
            measurement_duration="100 hr",
            replication_count=3,
            blinding=False,
            pre_registration=False,
        ),
        coupling=DomainCouplingAudit(
            physical_domain="toy",
            instrument_coupling=Coupling.TIGHT,
            protocol_coupling=Coupling.TIGHT,
            substrate_coupling=Coupling.MODERATE,
            regime_coupling=Coupling.LOOSE,
        ),
        regime=RegimeAudit(
            assumed_baseline="stable",
            baseline_validity_window="100 hr",
            regime_state=Regime.STATIONARY,
            regime_drift_indicators=[],
            extrapolation_horizon="100 hr",
        ),
        causal_model=CausalModelAudit(
            causal_frame="mechanistic",
            confounders_identified=[],
            confounders_controlled=[],
            confounders_unmeasured=[],
            unknown_unknowns_acknowledged=True,
            alternative_frames_considered=[],
        ),
        scope=ScopeBoundary(
            in_scope_conditions=["lab bench"],
            edge_conditions=[],
            out_of_scope_conditions=[],
            undeclared_scope=[],
            extrapolation_claims=[],
        ),
    )


def test_1_default_scope_audit_none():
    """AUDIT_17 must not regress AUDIT_07. Existing Provenance
    records with no scope_audit arg stay complete."""
    print("\n--- TEST 1: scope_audit defaults None; is_complete unchanged ---")
    p = empirical(source_refs=["Some Ref"])
    assert p.scope_audit is None
    assert p.is_complete()
    assert p.missing_fields() == []
    assert p.has_scope_audit() is False
    print("  default=None; is_complete=True; missing_fields=[]")
    print("PASS")


def test_2_empirical_accepts_scope_audit():
    print("\n--- TEST 2: empirical() accepts + stores scope_audit ---")
    ssa = _toy_study_scope_audit()
    p = empirical(
        source_refs=["Some Ref"],
        scope_caveat="measured in lab; applied in field",
        scope_audit=ssa,
    )
    assert p.scope_audit is ssa    # identity, not just equality
    assert p.has_scope_audit() is True
    assert p.is_complete()
    print("  scope_audit stored by identity; has_scope_audit=True")
    print("PASS")


def test_3_soft_gap_is_none_without_caveat():
    """No scope_caveat → no soft gap regardless of whether a
    scope_audit is attached. The gap is specifically triggered
    by the author acknowledging the stretch but not attaching
    the machine-readable record."""
    print("\n--- TEST 3: soft_gap is None with empty scope_caveat ---")
    p1 = empirical(source_refs=["ref"])
    assert p1.soft_gap() is None

    ssa = _toy_study_scope_audit()
    p2 = empirical(source_refs=["ref"], scope_audit=ssa)
    assert p2.soft_gap() is None   # has audit but no caveat to flag
    print("  no caveat -> no soft gap (with or without scope_audit)")
    print("PASS")


def test_4_soft_gap_fires_on_caveat_without_audit():
    """LOAD-BEARING: EMPIRICAL + scope_caveat + no scope_audit =
    soft gap. This is the signal AUDIT_17 exists to produce."""
    print("\n--- TEST 4: soft_gap fires on caveat without scope_audit ---")
    p = empirical(
        source_refs=["ref"],
        scope_caveat="lab polymer coupons, applied to field weathering",
    )
    gap = p.soft_gap()
    assert gap is not None
    assert "scope_caveat" in gap or "caveat" in gap
    assert "scope_audit" in gap
    print(f"  gap surfaced: '{gap[:80]}...'")
    print("PASS")


def test_5_soft_gap_cleared_by_attaching_audit():
    """Attaching a scope_audit to a caveat-bearing EMPIRICAL
    clears the soft gap. This is the repair pathway the soft-gap
    signal points at."""
    print("\n--- TEST 5: attaching scope_audit clears soft gap ---")
    ssa = _toy_study_scope_audit()
    p = empirical(
        source_refs=["ref"],
        scope_caveat="lab polymer coupons, applied to field weathering",
        scope_audit=ssa,
    )
    assert p.soft_gap() is None
    print("  caveat + scope_audit -> no soft gap (repair complete)")
    print("PASS")


def test_6_coverage_report_surfaces_new_fields():
    print("\n--- TEST 6: coverage_report reports scope_audit + soft_gap ---")
    ssa = _toy_study_scope_audit()
    provs = [
        empirical(source_refs=["a"]),                               # plain
        empirical(source_refs=["b"], scope_caveat="gap", ),         # soft gap
        empirical(source_refs=["c"], scope_audit=ssa),              # audited, no caveat
        empirical(source_refs=["d"], scope_caveat="ok", scope_audit=ssa),  # audited + caveat
        None,                                                        # unprov
    ]
    r = coverage_report(provs)
    assert r["total"] == 5
    assert r["with_provenance"] == 4
    assert r["none"] == 1
    assert r["scope_audit_count"] == 2
    assert r["soft_gap_count"] == 1
    assert len(r["soft_gap_details"]) == 1
    idx, kind, msg = r["soft_gap_details"][0]
    assert idx == 1 and kind == "empirical"
    print(f"  scope_audit_count=2, soft_gap_count=1 (index 1)")
    print("PASS")


def test_7_no_regression_on_tier1_coverage():
    """AUDIT_07's Tier 1 retrofit landed 74/74 complete provenance
    coverage. AUDIT_17 must not break that — existing audits don't
    attach scope_audit yet, and they shouldn't be required to.
    This test runs the same coverage assertion that
    tests/test_tier1_coverage.py does and confirms nothing moved."""
    print("\n--- TEST 7: Tier 1 coverage unchanged by AUDIT_17 ---")
    from term_audit.audits.money import MONEY_AUDIT
    from term_audit.audits.value import ALL_VALUE_AUDITS
    from term_audit.audits.capital import ALL_CAPITAL_AUDITS

    audits = [MONEY_AUDIT]
    audits.extend(ALL_VALUE_AUDITS.values())
    audits.extend(ALL_CAPITAL_AUDITS.values())
    for a in audits:
        cov = a.provenance_coverage()
        assert cov["none"] == 0, f"FAIL: {a.term} has {cov['none']} none"
        assert cov["incomplete"] == 0, \
            f"FAIL: {a.term} has {cov['incomplete']} incomplete: {cov['incomplete_details']}"
    print(f"  {len(audits)} Tier 1 audits: 0 none, 0 incomplete (AUDIT_07 preserved)")
    print("PASS")


if __name__ == "__main__":
    test_1_default_scope_audit_none()
    test_2_empirical_accepts_scope_audit()
    test_3_soft_gap_is_none_without_caveat()
    test_4_soft_gap_fires_on_caveat_without_audit()
    test_5_soft_gap_cleared_by_attaching_audit()
    test_6_coverage_report_surfaces_new_fields()
    test_7_no_regression_on_tier1_coverage()
    print("\nall provenance_study_scope_integration tests passed.")
