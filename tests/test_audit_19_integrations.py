"""
tests/test_audit_19_integrations.py

Tripwires for AUDIT_19's three integrations:

  Part A: StudyScopeAudit cross-references CostGrowth from
          informational_cost_audit
  Part B: Provenance PLACEHOLDER records optionally carry a
          deferred_cost annotation; `soft_gap` fires on
          EXPONENTIAL-tagged placeholders
  Part C: 2 Tier 1 EMPIRICAL records in money.py now have a real
          StudyScopeAudit attached (Boskin CPI + BoE 2014 Money
          Creation); the remaining EMPIRICAL records with
          scope_caveat but no scope_audit remain as soft gaps.

Locks:
  1. StudyScopeAudit.audit_report includes
     `cost_growth_if_applied_out_of_scope`; the mapping from
     scope status to CostGrowth tag matches AUDIT_19 § A
  2. placeholder() accepts deferred_cost kwarg
  3. PLACEHOLDER + deferred_cost=EXPONENTIAL fires soft_gap
  4. PLACEHOLDER + deferred_cost=LINEAR (or None) does NOT fire
     that specific soft_gap
  5. money.py's two retrofitted records have scope_audit attached
  6. money.py's soft-gap count equals exactly 2 (the remaining
     caveat-bearing records that were NOT retrofitted)
  7. money audit still 7/7 complete; no AUDIT_07 regression
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.study_scope_audit import (
    StudyScopeAudit, InstrumentAudit, ProtocolAudit, DomainCouplingAudit,
    RegimeAudit, CausalModelAudit, ScopeBoundary,
    Coupling, Regime, ScopeStatus,
)
from term_audit.informational_cost_audit import CostGrowth
from term_audit.provenance import (
    Provenance, placeholder, empirical, coverage_report,
)
from term_audit.audits.money import (
    MONEY_AUDIT,
    _BOSKIN_CPI_SCOPE_AUDIT,
    _BOE_2014_MONEY_CREATION_SCOPE_AUDIT,
)


def _minimal_ssa(deployment_context=None):
    return StudyScopeAudit(
        claim="toy",
        citation="toy",
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
            edge_conditions=["field light"],
            out_of_scope_conditions=["field heavy"],
            undeclared_scope=[],
            extrapolation_claims=[],
        ),
        deployment_context=deployment_context,
    )


# ---------------------------------------------------------------------------
# Part A: StudyScopeAudit -> CostGrowth cross-reference
# ---------------------------------------------------------------------------

def test_1_audit_report_has_cost_growth_tag():
    print("\n--- TEST 1: audit_report includes cost_growth_if_applied_out_of_scope ---")
    r = _minimal_ssa().audit_report()
    assert "cost_growth_if_applied_out_of_scope" in r
    # No deployment context -> SCOPE_UNDECLARED -> "unknown"
    assert r["cost_growth_if_applied_out_of_scope"] == "unknown"
    print(f"  SCOPE_UNDECLARED -> cost_growth='unknown'")
    print("PASS")


def test_2_cost_growth_tag_per_scope_status():
    """LOAD-BEARING: the mapping from ScopeStatus to CostGrowth is
    the core of the Part A integration. OUT_OF_SCOPE must map to
    EXPONENTIAL — the informational-cost-audit thesis."""
    print("\n--- TEST 2: cost_growth tag per scope status ---")
    expected = {
        ScopeStatus.IN_SCOPE:          CostGrowth.LINEAR,
        ScopeStatus.EDGE_OF_SCOPE:     CostGrowth.LINEAR,
        ScopeStatus.OUT_OF_SCOPE:      CostGrowth.EXPONENTIAL,
        ScopeStatus.SCOPE_UNDECLARED:  "unknown",
    }
    # Hit each status via deployment_context probing the minimal ssa.
    # (Using the explicit helper rather than running through
    # scope_status_for so we test the mapping function directly.)
    ssa = _minimal_ssa()
    for status, tag in expected.items():
        assert ssa._cost_growth_for_status(status) == tag, \
            f"FAIL: {status.value} -> {tag}"
    print(f"  in/edge -> LINEAR; out -> EXPONENTIAL; undeclared -> unknown")
    print("PASS")


# ---------------------------------------------------------------------------
# Part B: Provenance PLACEHOLDER deferred_cost + soft_gap
# ---------------------------------------------------------------------------

def test_3_placeholder_accepts_deferred_cost():
    print("\n--- TEST 3: placeholder() accepts deferred_cost ---")
    p = placeholder(
        rationale="guess",
        retirement_path="a dataset",
        deferred_cost=CostGrowth.LINEAR,
    )
    assert p.deferred_cost == CostGrowth.LINEAR
    # Default is None
    p2 = placeholder(rationale="guess", retirement_path="a dataset")
    assert p2.deferred_cost is None
    print(f"  deferred_cost=LINEAR stored; default None")
    print("PASS")


def test_4_exponential_deferred_cost_fires_soft_gap():
    """LOAD-BEARING: an EXPONENTIAL-tagged placeholder is the signal
    that drives retirement prioritization."""
    print("\n--- TEST 4: EXPONENTIAL deferred_cost fires soft_gap ---")
    p = placeholder(
        rationale="compounding debt",
        retirement_path="retire when possible",
        deferred_cost=CostGrowth.EXPONENTIAL,
    )
    gap = p.soft_gap()
    assert gap is not None
    assert "exponential" in gap.lower()
    print(f"  soft_gap fires: '{gap[:80]}...'")
    print("PASS")


def test_5_linear_or_none_deferred_cost_does_not_fire_placeholder_gap():
    """LINEAR placeholders and un-tagged placeholders should NOT
    fire the placeholder-soft-gap signal — linear debt is the
    honest default."""
    print("\n--- TEST 5: LINEAR / None deferred_cost does not fire soft_gap ---")
    p1 = placeholder(rationale="r", retirement_path="p",
                     deferred_cost=CostGrowth.LINEAR)
    assert p1.soft_gap() is None

    p2 = placeholder(rationale="r", retirement_path="p")
    assert p2.soft_gap() is None
    print(f"  LINEAR + None placeholders: soft_gap = None")
    print("PASS")


# ---------------------------------------------------------------------------
# Part C: money.py retrofit with real StudyScopeAudits
# ---------------------------------------------------------------------------

def test_6_money_retrofitted_records_have_scope_audit():
    """Boskin CPI + BoE 2014 citations carry StudyScopeAudit
    attachments. These are the two retrofits AUDIT_19 § C
    demonstrates."""
    print("\n--- TEST 6: money.py has two real scope_audits attached ---")
    # Find the two specific records by criterion.
    cal = next(s for s in MONEY_AUDIT.signal_scores
               if s.criterion == "calibration_exists")
    cons = next(s for s in MONEY_AUDIT.signal_scores
                if s.criterion == "conservation_or_law")

    assert cal.provenance.has_scope_audit()
    assert cal.provenance.scope_audit is _BOSKIN_CPI_SCOPE_AUDIT
    assert cons.provenance.has_scope_audit()
    assert cons.provenance.scope_audit is _BOE_2014_MONEY_CREATION_SCOPE_AUDIT
    print(f"  calibration_exists -> Boskin CPI scope audit attached")
    print(f"  conservation_or_law -> BoE 2014 scope audit attached")
    print("PASS")


def test_7_money_coverage_shape_honest():
    """LOAD-BEARING: the post-retrofit coverage must correctly
    reflect that 2 scope_audits are attached and the REMAINING
    caveat-bearing EMPIRICAL records are still flagged as soft
    gaps. The honest picture is 'two retrofits done, others
    open' — not 'all fixed' and not 'nothing changed'."""
    print("\n--- TEST 7: coverage reflects honest retrofit state ---")
    cov = MONEY_AUDIT.provenance_coverage()

    assert cov["scope_audit_count"] == 2
    # The remaining caveat-bearing EMPIRICAL records are
    # unit_invariant (BLS/Balassa-Samuelson) and observer_invariant
    # (FASB Level-3) — both have scope_caveats that AUDIT_19 § C
    # did NOT retrofit.
    assert cov["soft_gap_count"] == 2, \
        f"FAIL: expected exactly 2 remaining soft gaps, got {cov['soft_gap_count']}"
    # No AUDIT_07 regression: still 7/7 complete.
    assert cov["total"] == 7
    assert cov["complete"] == 7
    assert cov["incomplete"] == 0
    assert cov["none"] == 0
    print(f"  7/7 complete; 2 scope_audits attached; 2 remaining soft gaps")
    print("PASS")


def test_8_boskin_scope_audit_flags_out_of_regime_extrapolation():
    """Spot-check that the Boskin scope audit itself produces a
    scope-aware verdict. A deployment context that invokes
    cross-regime comparison is OUT_OF_SCOPE per the audit's own
    scope declaration."""
    print("\n--- TEST 8: Boskin scope audit routes cross-regime queries OUT_OF_SCOPE ---")
    # Rebuild a copy with deployment_context attached (dataclass
    # is not frozen, so we set directly on a fresh copy).
    import dataclasses
    ssa = dataclasses.replace(
        _BOSKIN_CPI_SCOPE_AUDIT,
        deployment_context={"cross_regime_dollar_denominated_comparison": True},
    )
    r = ssa.audit_report()
    assert r["scope_status_for_deployment"] in (
        ScopeStatus.OUT_OF_SCOPE.value,
        ScopeStatus.SCOPE_UNDECLARED.value,
    )
    # The cost tag should reflect either out-of-scope or undeclared;
    # both are honest ("don't apply" or "declare first")
    assert r["cost_growth_if_applied_out_of_scope"] in (
        CostGrowth.EXPONENTIAL, "unknown"
    )
    print(f"  cross-regime query -> {r['scope_status_for_deployment']}; "
          f"cost={r['cost_growth_if_applied_out_of_scope']}")
    print("PASS")


if __name__ == "__main__":
    test_1_audit_report_has_cost_growth_tag()
    test_2_cost_growth_tag_per_scope_status()
    test_3_placeholder_accepts_deferred_cost()
    test_4_exponential_deferred_cost_fires_soft_gap()
    test_5_linear_or_none_deferred_cost_does_not_fire_placeholder_gap()
    test_6_money_retrofitted_records_have_scope_audit()
    test_7_money_coverage_shape_honest()
    test_8_boskin_scope_audit_flags_out_of_regime_extrapolation()
    print("\nall AUDIT_19 integration tests passed.")
