"""
tests/test_study_scope_audit.py

Tripwires for term_audit/study_scope_audit.py (AUDIT_15).

Locks in:
  1. module imports; six layer dataclasses + composite + enums exist
  2. InstrumentAudit.blind_spots() returns non-empty structured output
  3. ProtocolAudit.protocol_filters() includes the explicit exclusions
  4. DomainCouplingAudit.coupling_summary() returns all 4 dimensions
     with valid Coupling enum values
  5. RegimeAudit.regime_risk() maps each Regime enum to a distinct
     severity string
  6. CausalModelAudit.frame_fragility() responds monotonically to
     unmeasured-confounder count + unknown-unknown acknowledgment
  7. ScopeBoundary.scope_status_for returns OUT_OF_SCOPE when
     deployment context matches out-of-scope conditions (dominates
     IN_SCOPE and EDGE)
  8. StudyScopeAudit.audit_report returns a verdict that differs
     between "no deployment context declared" and "out-of-scope
     declared"
  9. HISTORICAL_CASES carries the five documented calibration
     examples named in the module header (geocentrism, miasma,
     caloric, steady-state cosmology, low-fat diet)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.study_scope_audit import (
    Coupling, Regime, ScopeStatus,
    InstrumentAudit, ProtocolAudit, DomainCouplingAudit,
    RegimeAudit, CausalModelAudit, ScopeBoundary,
    StudyScopeAudit,
    HISTORICAL_CASES,
    PREMISE, AI_REASONING_RULE, META_INSIGHT,
)


def _minimal_audit(deployment_context=None):
    """Small, complete StudyScopeAudit for structural tests."""
    return StudyScopeAudit(
        claim="toy claim",
        citation="toy ref",
        instrument=InstrumentAudit(
            instrument_name="toy",
            physical_quantity_measured="toy quantity",
            measurement_range=(0.0, 1.0),
            resolution=0.01,
            noise_floor=0.001,
            sampling_rate_hz=10.0,
            spatial_resolution="n/a",
            calibration_source="toy",
            calibration_traceability="toy",
            drift_rate="negligible",
        ),
        protocol=ProtocolAudit(
            sample_preparation="lab bench",
            environmental_controls={"temp": 22},
            excluded_conditions=["dust", "humidity"],
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
            confounders_identified=["A", "B"],
            confounders_controlled=["A"],
            confounders_unmeasured=["C"],
            unknown_unknowns_acknowledged=True,
            alternative_frames_considered=["statistical"],
        ),
        scope=ScopeBoundary(
            in_scope_conditions=["lab bench"],
            edge_conditions=["mild outdoor"],
            out_of_scope_conditions=["dirty urban"],
            undeclared_scope=[],
            extrapolation_claims=[],
        ),
        deployment_context=deployment_context,
    )


def test_1_module_imports_and_shape():
    print("\n--- TEST 1: module imports and public shape ---")
    for enum_cls in (Coupling, Regime, ScopeStatus):
        assert len(list(enum_cls)) >= 3, f"FAIL: {enum_cls.__name__} near-empty"
    for name in ("geocentrism", "miasma_theory", "caloric_theory",
                 "steady_state_cosmology", "low_fat_diet_consensus"):
        assert name in HISTORICAL_CASES, f"FAIL: missing anchor {name}"
    assert PREMISE.strip() and AI_REASONING_RULE.strip() and META_INSIGHT.strip()
    print(f"  3 enums, 5 historical anchors, 3 prose surfaces present")
    print("PASS")


def test_2_instrument_blind_spots_structured():
    print("\n--- TEST 2: instrument blind_spots non-empty + structured ---")
    a = _minimal_audit()
    blind = a.instrument.blind_spots()
    assert len(blind) >= 6
    joined = " ".join(blind).lower()
    assert "noise floor" in joined
    assert "range" in joined
    print(f"  {len(blind)} blind-spot lines, include noise floor + range")
    print("PASS")


def test_3_protocol_filters_include_exclusions():
    """The explicit `excluded_conditions` must appear in the filter
    list — otherwise the user-declared protocol gaps silently
    disappear from the report."""
    print("\n--- TEST 3: protocol filters include explicit exclusions ---")
    a = _minimal_audit()
    filters = a.protocol.protocol_filters()
    assert "dust" in filters and "humidity" in filters
    print(f"  both 'dust' and 'humidity' present in {len(filters)} filter lines")
    print("PASS")


def test_4_coupling_summary_dimensions():
    print("\n--- TEST 4: coupling_summary has all four dimensions ---")
    a = _minimal_audit()
    cs = a.coupling.coupling_summary()
    assert set(cs.keys()) == {"instrument", "protocol", "substrate", "regime"}
    for k, v in cs.items():
        assert v in {c.value for c in Coupling}, \
            f"FAIL: {k}={v!r} not a Coupling value"
    print(f"  {cs}")
    print("PASS")


def test_5_regime_risk_per_state():
    """Each Regime enum value should map to a distinct regime_risk
    string; ambiguity there would mean the regime check collapses
    to uselessness."""
    print("\n--- TEST 5: regime_risk differs per Regime state ---")
    strings = set()
    for state in Regime:
        aud = RegimeAudit(
            assumed_baseline="x",
            baseline_validity_window="y",
            regime_state=state,
            regime_drift_indicators=[],
            extrapolation_horizon="z",
        )
        s = aud.regime_risk()
        assert s.strip()
        strings.add(s)
    assert len(strings) == len(list(Regime)), \
        f"FAIL: regime_risk collisions across {len(list(Regime))} states"
    print(f"  {len(list(Regime))} Regime states yield {len(strings)} distinct strings")
    print("PASS")


def test_6_frame_fragility_monotone():
    """frame_fragility must respond to the two fields it reads
    (confounders_unmeasured count + unknown_unknowns_acknowledged).
    Regressing the monotonicity here would collapse the
    higher-level verdict pipeline."""
    print("\n--- TEST 6: frame_fragility responds to inputs ---")
    clean = CausalModelAudit(
        causal_frame="x",
        confounders_identified=["A"],
        confounders_controlled=["A"],
        confounders_unmeasured=[],
        unknown_unknowns_acknowledged=True,
        alternative_frames_considered=[],
    ).frame_fragility()
    assert "LOW" in clean

    mid = CausalModelAudit(
        causal_frame="x",
        confounders_identified=["A"],
        confounders_controlled=[],
        confounders_unmeasured=["B"],
        unknown_unknowns_acknowledged=True,
        alternative_frames_considered=[],
    ).frame_fragility()
    assert "MEDIUM" in mid

    high = CausalModelAudit(
        causal_frame="x",
        confounders_identified=["A"],
        confounders_controlled=[],
        confounders_unmeasured=["B"],
        unknown_unknowns_acknowledged=False,
        alternative_frames_considered=[],
    ).frame_fragility()
    assert "HIGH" in high

    print(f"  LOW / MEDIUM / HIGH all reachable")
    print("PASS")


def test_7_out_of_scope_dominates():
    """LOAD-BEARING: if a deployment context matches both an
    in-scope and an out-of-scope condition, the audit MUST return
    OUT_OF_SCOPE. Reversing this would silently bless deployments
    that violate declared exclusions."""
    print("\n--- TEST 7: OUT_OF_SCOPE dominates IN_SCOPE and EDGE ---")
    scope = ScopeBoundary(
        in_scope_conditions=["lab bench"],
        edge_conditions=["mild outdoor"],
        out_of_scope_conditions=["dirty urban"],
        undeclared_scope=[],
        extrapolation_claims=[],
    )
    # Pure in-scope.
    assert scope.scope_status_for({"lab_bench": True}) == ScopeStatus.IN_SCOPE
    # Pure out-of-scope.
    assert scope.scope_status_for({"dirty_urban": True}) == ScopeStatus.OUT_OF_SCOPE
    # Pure edge.
    assert scope.scope_status_for({"mild_outdoor": True}) == ScopeStatus.EDGE_OF_SCOPE
    # Conflict: both in and out declared. OUT wins.
    assert scope.scope_status_for(
        {"lab_bench": True, "dirty_urban": True}
    ) == ScopeStatus.OUT_OF_SCOPE
    # Undeclared.
    assert scope.scope_status_for({"mars_surface": True}) == ScopeStatus.SCOPE_UNDECLARED
    print(f"  in / out / edge / conflict / undeclared all route correctly")
    print("PASS")


def test_8_audit_report_differs_with_and_without_context():
    print("\n--- TEST 8: audit_report distinguishes undeclared vs out-of-scope ---")
    without_ctx = _minimal_audit().audit_report()
    assert without_ctx["verdict"].startswith("scope-undeclared")

    with_out = _minimal_audit(deployment_context={"dirty_urban": True}).audit_report()
    assert "category error" in with_out["verdict"]

    with_in = _minimal_audit(deployment_context={"lab_bench": True}).audit_report()
    assert "valid within study's measured scope" in with_in["verdict"]

    print(f"  undeclared, out-of-scope, and in-scope produce distinct verdicts")
    print("PASS")


def test_9_historical_cases_structure():
    """Every anchor must carry at minimum a `lesson`. The anchors
    are there to calibrate the audit framework against cases whose
    scope shift is historically documented."""
    print("\n--- TEST 9: historical anchors all carry a lesson field ---")
    for name, case in HISTORICAL_CASES.items():
        assert "lesson" in case, f"FAIL: {name} missing lesson"
        assert case["lesson"].strip()
    print(f"  {len(HISTORICAL_CASES)} anchors, every one carries a documented lesson")
    print("PASS")


if __name__ == "__main__":
    test_1_module_imports_and_shape()
    test_2_instrument_blind_spots_structured()
    test_3_protocol_filters_include_exclusions()
    test_4_coupling_summary_dimensions()
    test_5_regime_risk_per_state()
    test_6_frame_fragility_monotone()
    test_7_out_of_scope_dominates()
    test_8_audit_report_differs_with_and_without_context()
    test_9_historical_cases_structure()
    print("\nall study_scope_audit tests passed.")
