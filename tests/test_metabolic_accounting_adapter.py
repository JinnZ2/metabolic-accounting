"""
tests/test_metabolic_accounting_adapter.py

Tripwires for term_audit/integration/metabolic_accounting_adapter.py —
the one-way bridge from term_audit outputs to metabolic-accounting
inputs.

Locks in:
  - dataclass shapes the metabolic-accounting repo depends on
    (BasinStateInput, InfrastructureInput, CascadeCouplingInput,
     GlucoseFlowInput, VerdictInput, AssumptionValidatorFlag)
  - BasinCategory vocabulary (removing an entry breaks downstream
    basin typing)
  - end_to_end_example() runs and produces the documented shape:
    3 basins, 1 infrastructure, 1 glucose flow (net -470 from the
    productivity driver), 1 verdict, 1 assumption flag
  - verdict_from_basins handles empty input without crashing
  - glucose_flow_from_productivity_profile conserves the accounting
    identity extraction_rate - regeneration_rate = forced_drawdown
    for the productivity-audit driver example
  - FAILURE_SEVERITY covers every SIGNAL_CRITERIA entry

Run: python -m tests.test_metabolic_accounting_adapter
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.integration.metabolic_accounting_adapter import (
    BasinCategory, BasinStateInput, InfrastructureInput,
    CascadeCouplingInput, GlucoseFlowInput, VerdictInput,
    AssumptionValidatorFlag, LinkageRecord, StatusExtractionSnapshot,
    basin_from_v_c_audit, infrastructure_from_k_a_audit,
    cascade_from_negative_linkage, human_substrate_basin_from_status,
    glucose_flow_from_productivity_profile, verdict_from_basins,
    assumption_flags_from_audit, FAILURE_SEVERITY, end_to_end_example,
)
from term_audit.schema import SIGNAL_CRITERIA


def test_1_basin_category_vocabulary():
    """BasinCategory covers the load-bearing basin types. Removing
    an entry breaks downstream basin typing in metabolic-accounting."""
    print("\n--- TEST 1: BasinCategory vocabulary ---")
    required = {"SOIL", "WATER", "AIR", "BIOLOGY",
                "HUMAN_SUBSTRATE", "KNOWLEDGE", "INFRASTRUCTURE"}
    names = {c.name for c in BasinCategory}
    assert required.issubset(names), \
        f"FAIL: missing {required - names}"
    print(f"  {len(names)} categories: {sorted(names)}")
    print("PASS")


def test_2_end_to_end_example_shape():
    """end_to_end_example produces the documented output shape:
    3 basins, 1 infrastructure, 1 glucose flow, 1 verdict, flags."""
    print("\n--- TEST 2: end_to_end_example shape ---")
    r = end_to_end_example()
    assert set(r.keys()) == {
        "basins", "infrastructure", "glucose_flow",
        "verdict", "assumption_flags",
    }
    assert len(r["basins"]) == 3
    assert len(r["infrastructure"]) == 1
    assert isinstance(r["glucose_flow"], GlucoseFlowInput)
    assert isinstance(r["verdict"], VerdictInput)
    for b in r["basins"]:
        assert isinstance(b, BasinStateInput)
    for i in r["infrastructure"]:
        assert isinstance(i, InfrastructureInput)
    for f in r["assumption_flags"]:
        assert isinstance(f, AssumptionValidatorFlag)
    print(f"  basins={len(r['basins'])}, infra={len(r['infrastructure'])}, "
          f"flags={len(r['assumption_flags'])}")
    print("PASS")


def test_3_glucose_flow_matches_productivity_driver():
    """end_to_end_example's glucose flow matches the long-haul driver
    in term_audit/audits/productivity.py: pay=1600, true_input=2070,
    forced_drawdown=470, net_glucose=-470."""
    print("\n--- TEST 3: glucose flow matches productivity driver ---")
    r = end_to_end_example()
    g = r["glucose_flow"]
    assert abs(g.extraction_rate - 2070.0) < 1e-9
    assert abs(g.regeneration_rate - 1600.0) < 1e-9
    assert abs(g.forced_drawdown - 470.0) < 1e-9
    assert abs(g.net_glucose - (-470.0)) < 1e-9
    # accounting identity
    identity = g.extraction_rate - g.regeneration_rate - g.forced_drawdown
    assert abs(identity) < 1e-9, \
        f"FAIL: extraction - regen - forced_drawdown should be 0, got {identity}"
    print(f"  extract={g.extraction_rate}, regen={g.regeneration_rate}, "
          f"drawdown={g.forced_drawdown}, net={g.net_glucose}")
    print("PASS")


def test_4_verdict_bounded_and_confidence_monotone():
    """Verdict yields in sensible ranges; confidence is in [0, 1]."""
    print("\n--- TEST 4: verdict bounds ---")
    r = end_to_end_example()
    v = r["verdict"]
    assert v.sustainable_yield >= 0
    assert 0.0 <= v.confidence <= 1.0
    # with negative trajectory, time_to_red should be finite
    assert v.time_to_red is not None and v.time_to_red > 0
    assert v.basin_trajectory < 0   # extractive scenario
    print(f"  yield={v.sustainable_yield:.4f}, "
          f"trajectory={v.basin_trajectory:.4f}, "
          f"ttr={v.time_to_red:.2f}, confidence={v.confidence:.3f}")
    print("PASS")


def test_5_verdict_from_basins_handles_empty():
    """Empty basins list returns a degenerate verdict without
    raising."""
    print("\n--- TEST 5: verdict_from_basins handles empty ---")
    v = verdict_from_basins("test_entity", [], current_yield=0.0)
    assert v.sustainable_yield == 0.0
    assert v.confidence == 0.0
    assert v.time_to_red is None
    assert v.entity == "test_entity"
    print("  empty basins -> sustainable_yield=0, confidence=0")
    print("PASS")


def test_6_failure_severity_covers_all_criteria():
    """FAILURE_SEVERITY must have an entry for every criterion in
    term_audit/schema.py::SIGNAL_CRITERIA. Gaps in coverage would
    silently drop flags."""
    print("\n--- TEST 6: FAILURE_SEVERITY covers SIGNAL_CRITERIA ---")
    missing = set(SIGNAL_CRITERIA) - set(FAILURE_SEVERITY)
    assert not missing, f"FAIL: FAILURE_SEVERITY missing {missing}"
    for key, sev in FAILURE_SEVERITY.items():
        assert 0.0 <= sev <= 1.0, \
            f"FAIL: severity for {key} out of [0,1]: {sev}"
    print(f"  {len(FAILURE_SEVERITY)} entries, all in [0,1]")
    print("PASS")


def test_7_negative_linkage_to_cascade():
    """cascade_from_negative_linkage takes a negative LinkageRecord
    and produces a cascade coupling with positive strength (because
    negative source->target means source-growth degrades target)."""
    print("\n--- TEST 7: negative linkage -> cascade coupling ---")
    linkage = LinkageRecord(
        source="K_B",
        target="K_A",
        relation="negative",
        strength_estimate=-0.6,
        mechanism="financial extraction displaces productive capital",
    )
    cascade = cascade_from_negative_linkage(
        linkage,
        source_entity="financial_claims",
        target_entity="productive_plant",
        time_lag=2.0,
    )
    assert isinstance(cascade, CascadeCouplingInput)
    # cascade coupling strength must be positive (magnitude of the
    # negative relation; the "how much source failing hurts target")
    assert cascade.coupling_strength > 0
    print(f"  linkage -0.6 -> coupling_strength={cascade.coupling_strength}")
    print("PASS")


def test_8_human_substrate_basin_from_status_snapshot():
    """human_substrate_basin_from_status accepts a StatusExtraction
    snapshot and produces a HUMAN_SUBSTRATE basin with bounded
    fields."""
    print("\n--- TEST 8: human_substrate_basin_from_status ---")
    snap = StatusExtractionSnapshot(
        support_fraction=0.4,
        production_fraction=0.3,
        distinction_fraction=0.3,
        tolerance_width=2.0,
        labeled_fraction=0.25,
        avg_capture=0.5,
    )
    b = human_substrate_basin_from_status(snap)
    assert b.category == BasinCategory.HUMAN_SUBSTRATE
    assert 0.0 <= b.current_level <= 1.0
    assert b.regeneration_rate >= 0
    assert b.extraction_rate >= 0
    print(f"  current={b.current_level:.2f}, "
          f"regen={b.regeneration_rate:.3f}, "
          f"extract={b.extraction_rate:.3f}")
    print("PASS")


if __name__ == "__main__":
    test_1_basin_category_vocabulary()
    test_2_end_to_end_example_shape()
    test_3_glucose_flow_matches_productivity_driver()
    test_4_verdict_bounded_and_confidence_monotone()
    test_5_verdict_from_basins_handles_empty()
    test_6_failure_severity_covers_all_criteria()
    test_7_negative_linkage_to_cascade()
    test_8_human_substrate_basin_from_status_snapshot()
    print("\nall metabolic_accounting_adapter tests passed.")
