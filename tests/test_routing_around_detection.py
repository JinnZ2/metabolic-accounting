"""
tests/test_routing_around_detection.py

Tripwires for term_audit/signals/routing_around_detection.py.

Module was originally shipped as embedded Python inside a design-
doc markdown file (the commit message "Implement routing detection
module for AI systems" on 7a64005 described the intent but added
only the spec doc, not the module). AUDIT_08 extracted the code
to a real module, fixed one dataclass field-ordering bug along
the way, and deleted the spec doc once the code was in place.

Tests lock in:

  1. module imports cleanly (regression for sys.path bootstrap +
     dataclass-field ordering)
  2. canary detection fires on a constrained + low-credential +
     functional region (the load-bearing inference: absence of
     formal documentation in a working region = routing-around)
  3. canary detection does NOT fire on a buffered region with same
     credential density (the inference is environment-conditional)
  4. AI routing guidance discriminates between constrained and
     buffered regions
  5. substrate evidence renders as AI-consumable context
  6. five falsifiable predictions shipped
  7. rural-Midwest-county example runs end-to-end
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.signals.routing_around_detection import (
    EnvironmentType,
    CanarySignal,
    SubstrateEvidenceType,
    SubstrateEvidenceRecord,
    InvisibleCapacityRegion,
    detect_routing_around,
    example_rural_midwest_county,
    generate_ai_context_for_region,
    FALSIFIABLE_PREDICTIONS,
)


def test_1_module_imports_cleanly():
    print("\n--- TEST 1: module imports cleanly ---")
    assert CanarySignal is not None
    assert detect_routing_around is not None
    print("  all expected symbols exposed")
    print("PASS")


def test_2_canary_fires_on_constrained_functional_low_credential():
    """A constrained region with functional infrastructure and low
    credential density should trip the canary with high confidence."""
    print("\n--- TEST 2: canary fires on routing-around pattern ---")
    signal = detect_routing_around(
        region_name="test constrained",
        environment_type=EnvironmentType.CONSTRAINED,
        credential_density=0.1,
        infrastructure_functional=True,
        formal_service_utilization=0.05,
        known_routers=["Linda"],
        substrate_records=[],
    )
    assert signal.likely_routed_around is True, \
        f"FAIL: canary did not fire; confidence={signal.confidence}"
    assert signal.confidence >= 0.7, \
        f"FAIL: confidence {signal.confidence} too low"
    print(f"  likely_routed_around=True  confidence={signal.confidence:.2f}")
    print("PASS")


def test_3_canary_does_not_fire_on_buffered():
    """Buffered region with the same low credential density should NOT
    fire the canary — the inference requires constraint."""
    print("\n--- TEST 3: canary does not fire on buffered ---")
    signal = detect_routing_around(
        region_name="test buffered",
        environment_type=EnvironmentType.BUFFERED,
        credential_density=0.1,
        infrastructure_functional=True,
        formal_service_utilization=0.05,
        known_routers=[],
        substrate_records=[],
    )
    assert signal.likely_routed_around is False, \
        "FAIL: canary fired in buffered environment"
    print("  likely_routed_around=False in buffered environment")
    print("PASS")


def test_4_ai_routing_guidance_discriminates():
    """Guidance should differ substantively between constrained-low-
    credential and buffered-with-credentials regions."""
    print("\n--- TEST 4: AI routing guidance discriminates ---")
    constrained = InvisibleCapacityRegion(
        region_name="rural",
        environment_type=EnvironmentType.CONSTRAINED,
        credential_density=0.15,
        infrastructure_functional=True,
        formal_service_calls_per_capita=0.1,
        known_routers=["Linda"],
        known_closers=["Dale"],
        invisible_capacity_level=0.8,
        confidence=0.85,
    )
    buffered = InvisibleCapacityRegion(
        region_name="urban",
        environment_type=EnvironmentType.BUFFERED,
        credential_density=0.9,
        infrastructure_functional=True,
        formal_service_calls_per_capita=0.8,
        known_routers=[],
        known_closers=[],
        invisible_capacity_level=0.2,
        confidence=0.8,
    )
    g1 = constrained.ai_routing_guidance()
    g2 = buffered.ai_routing_guidance()
    assert g1 != g2, "FAIL: guidance did not discriminate"
    assert "route" in g1.lower() or "local" in g1.lower() or \
           "router" in g1.lower()
    print("  guidance differs between constrained and buffered regions")
    print("PASS")


def test_5_substrate_evidence_renders_as_ai_context():
    """Each SubstrateEvidenceType should produce non-empty AI context."""
    print("\n--- TEST 5: substrate evidence renders ---")
    for etype in SubstrateEvidenceType:
        rec = SubstrateEvidenceRecord(
            practitioner_identifier="Test",
            evidence_type=etype,
            observer_relationship="peer",
            domains_demonstrated=["test_domain"],
            closure_observed=True,
        )
        ctx = rec.as_ai_context()
        assert ctx and len(ctx) > 20, \
            f"FAIL: empty/short context for {etype}"
    print(f"  all {len(list(SubstrateEvidenceType))} evidence types render")
    print("PASS")


def test_6_five_falsifiable_predictions():
    """The spec shipped 5 falsifiable predictions; changing this count
    without updating the audit trail is the drift pattern AUDIT_06
    flagged on governance principles."""
    print("\n--- TEST 6: falsifiable predictions count ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 5, \
        f"FAIL: expected 5, got {len(FALSIFIABLE_PREDICTIONS)}"
    for p in FALSIFIABLE_PREDICTIONS:
        assert p.get("claim", "").strip()
        assert p.get("falsification", "").strip()
    print(f"  {len(FALSIFIABLE_PREDICTIONS)} predictions, all with claim + falsification")
    print("PASS")


def test_7_rural_midwest_example_runs():
    """The canonical example region + AI context generation must
    produce structured, non-empty output."""
    print("\n--- TEST 7: rural-Midwest example runs ---")
    region = example_rural_midwest_county()
    assert region.environment_type == EnvironmentType.CONSTRAINED
    assert region.infrastructure_functional is True
    assert len(region.substrate_records) >= 1
    context = generate_ai_context_for_region(region)
    assert "ROUTING" in context or "ROUTE" in context.upper() \
        or "router" in context.lower()
    assert region.region_name in context
    print(f"  region={region.region_name!r} records={len(region.substrate_records)}")
    print("PASS")


if __name__ == "__main__":
    test_1_module_imports_cleanly()
    test_2_canary_fires_on_constrained_functional_low_credential()
    test_3_canary_does_not_fire_on_buffered()
    test_4_ai_routing_guidance_discriminates()
    test_5_substrate_evidence_renders_as_ai_context()
    test_6_five_falsifiable_predictions()
    test_7_rural_midwest_example_runs()
    print("\nall routing-around detection tests passed.")
