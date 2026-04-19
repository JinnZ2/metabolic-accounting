"""
tests/test_status_extraction.py

Locks in the load-bearing invariants of the status-extraction model.

Most important: total energy is conserved across every step. The
model claims a physical accounting (support + production + distinction
= total) and that conservation must hold exactly in floating-point
within tolerance. This is the same first-law-closure discipline
thermodynamics/exergy.py enforces on the basin side.

Run: python -m tests.test_status_extraction
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math

from term_audit.status_extraction import (
    EnergyFlows, ToleranceBand, MeasurementSystem,
    StatusExtractionModel, FALSIFIABLE_PREDICTIONS, example_run,
)


def _fresh_model() -> StatusExtractionModel:
    """Identical setup to example_run, but ready to step manually."""
    return StatusExtractionModel(
        flows=EnergyFlows(support=50.0, production=40.0, distinction=10.0),
        tolerance=ToleranceBand(
            baseline_support=50.0, baseline_width=4.0,
            contraction_exponent=1.2,
        ),
        systems=[
            MeasurementSystem(
                name="credentialing",
                intended_purpose="verify task-specific skills",
                capture_rate_constant=0.15, resistance=0.05,
            ),
            MeasurementSystem(
                name="clinical_diagnosis",
                intended_purpose="identify substrate damage",
                capture_rate_constant=0.12, resistance=0.10,
            ),
            MeasurementSystem(
                name="performance_review",
                intended_purpose="assess task outcomes",
                capture_rate_constant=0.18, resistance=0.03,
            ),
            MeasurementSystem(
                name="physical_instrumentation",
                intended_purpose="measure physical quantities",
                capture_rate_constant=0.08, resistance=0.30,
            ),
        ],
        profile_distribution_std=2.0,
        amplification_per_labeled=0.08,
    )


def test_1_energy_conservation():
    """LOAD-BEARING. Total energy must be conserved across every step.
    The model only redirects flows; it does not create or destroy
    energy. If this test fails, the same class of error that would
    fail thermodynamics/exergy.py::check_closure has occurred."""
    print("\n--- TEST 1: energy conservation across all steps ---")
    m = _fresh_model()
    initial_total = m.flows.total
    assert abs(initial_total - 100.0) < 1e-9
    for i in range(50):
        m.step()
        total = m.flows.support + m.flows.production + m.flows.distinction
        assert abs(total - initial_total) < 1e-9, \
            f"FAIL: energy non-conservation at step {i}: " \
            f"{total} vs {initial_total} (drift {total - initial_total})"
    print(f"  initial total: {initial_total}")
    print(f"  final total:   "
          f"{m.flows.support + m.flows.production + m.flows.distinction}")
    print(f"  conserved across 50 steps")
    print("PASS")


def test_2_capture_monotone_and_bounded():
    """Capture fractions only increase per step (assuming distinction
    pressure exceeds resistance) and saturate at 1.0."""
    print("\n--- TEST 2: capture monotone and bounded ---")
    m = _fresh_model()
    prev = {s.name: s.capture_fraction for s in m.systems}
    for _ in range(40):
        m.step()
        for s in m.systems:
            assert 0.0 <= s.capture_fraction <= 1.0, \
                f"FAIL: {s.name} capture out of bounds: {s.capture_fraction}"
            assert s.capture_fraction >= prev[s.name] - 1e-12, \
                f"FAIL: {s.name} capture decreased: " \
                f"{prev[s.name]} -> {s.capture_fraction}"
            prev[s.name] = s.capture_fraction
    print(f"  all {len(m.systems)} systems monotone and within [0, 1]")
    print("PASS")


def test_3_low_resistance_captures_first():
    """PREDICTION 3: low-resistance measurement systems capture before
    high-resistance ones. example_run is constructed to make this
    visible — performance_review (resistance 0.03) should end with the
    highest capture fraction; physical_instrumentation (resistance
    0.30) should end lowest."""
    print("\n--- TEST 3: low resistance captures first (Prediction 3) ---")
    m = example_run()
    by_name = {s.name: s for s in m.systems}
    perf = by_name["performance_review"].capture_fraction
    cred = by_name["credentialing"].capture_fraction
    clin = by_name["clinical_diagnosis"].capture_fraction
    instr = by_name["physical_instrumentation"].capture_fraction

    assert perf > cred > clin > instr, \
        f"FAIL: capture order does not match resistance order. " \
        f"perf={perf:.3f} cred={cred:.3f} clin={clin:.3f} instr={instr:.3f}"
    print(f"  performance_review ({perf:.3f}) > credentialing ({cred:.3f})")
    print(f"  > clinical_diagnosis ({clin:.3f}) > "
          f"physical_instrumentation ({instr:.3f})")
    print("PASS")


def test_4_distinction_grows_under_default_dynamics():
    """PREDICTION 1: distinction flow grows monotonically when no
    structural resistance is added beyond the per-system resistances.
    The example_run setup matches that condition."""
    print("\n--- TEST 4: distinction grows monotonically (Prediction 1) ---")
    m = example_run()
    distinctions = [h["distinction"] for h in m.history]
    for i in range(1, len(distinctions)):
        assert distinctions[i] >= distinctions[i-1] - 1e-12, \
            f"FAIL: distinction decreased at step {i}: " \
            f"{distinctions[i-1]} -> {distinctions[i]}"
    assert distinctions[-1] > distinctions[0], \
        "FAIL: distinction did not grow over the full run"
    print(f"  distinction: {distinctions[0]:.2f} -> {distinctions[-1]:.2f}")
    print("PASS")


def test_5_tolerance_band_contracts_with_support_drop():
    """ToleranceBand.width must drop monotonically as support drops.
    With contraction_exponent > 1 the contraction is super-linear."""
    print("\n--- TEST 5: tolerance band contracts with support ---")
    band = ToleranceBand(
        baseline_support=50.0, baseline_width=4.0,
        contraction_exponent=1.2,
    )
    widths = [band.width(s) for s in (50.0, 40.0, 30.0, 20.0, 10.0)]
    for i in range(1, len(widths)):
        assert widths[i] < widths[i-1], \
            f"FAIL: width did not contract: {widths[i-1]} -> {widths[i]}"
    # zero or negative support produces zero width
    assert band.width(0.0) == 0.0
    assert band.width(-5.0) == 0.0
    # super-linear: dropping support to 50% should drop width below 50%
    assert band.width(25.0) < 0.5 * band.width(50.0), \
        "FAIL: contraction_exponent > 1 should be super-linear"
    print(f"  widths at support 50,40,30,20,10: "
          f"{[round(w, 3) for w in widths]}")
    print("PASS")


def test_6_fraction_inside_in_unit_interval():
    """ToleranceBand.fraction_inside must always be in [0, 1]."""
    print("\n--- TEST 6: fraction_inside in [0, 1] ---")
    band = ToleranceBand(
        baseline_support=50.0, baseline_width=4.0,
        contraction_exponent=1.2,
    )
    for support in (50.0, 30.0, 10.0, 1.0, 0.0):
        for std in (0.5, 2.0, 10.0):
            f = band.fraction_inside(support, std)
            assert 0.0 <= f <= 1.0, \
                f"FAIL: fraction_inside out of bounds: " \
                f"support={support}, std={std}, f={f}"
    # zero std: should give 1.0 if width > 0, else 0.0
    assert band.fraction_inside(50.0, 0.0) == 1.0
    assert band.fraction_inside(0.0, 0.0) == 0.0
    print("PASS")


def test_7_history_records_each_step():
    """history grows by one entry per step() call and contains the
    documented keys."""
    print("\n--- TEST 7: history records each step ---")
    m = _fresh_model()
    assert m.history == []
    m.run(steps=10)
    assert len(m.history) == 10, \
        f"FAIL: expected 10 history entries, got {len(m.history)}"
    expected_keys = {
        "support", "production", "distinction", "tolerance_width",
        "fraction_inside", "labeled_fraction", "avg_capture",
    }
    assert set(m.history[-1]) == expected_keys, \
        f"FAIL: history keys mismatch {set(m.history[-1])}"
    print(f"  10 entries, keys: {sorted(expected_keys)}")
    print("PASS")


def test_8_falsifiable_predictions_schema():
    """The five predictions documented in the module docstring must
    appear in FALSIFIABLE_PREDICTIONS as dicts with id/claim/
    falsification keys."""
    print("\n--- TEST 8: five falsifiable predictions documented ---")
    assert len(FALSIFIABLE_PREDICTIONS) == 5, \
        f"FAIL: expected 5 predictions, got {len(FALSIFIABLE_PREDICTIONS)}"
    for p in FALSIFIABLE_PREDICTIONS:
        assert set(p) == {"id", "claim", "falsification"}, \
            f"FAIL: prediction {p.get('id')} key mismatch: {set(p)}"
        assert p["claim"].strip() and p["falsification"].strip(), \
            f"FAIL: prediction {p['id']} has empty claim or falsification"
    ids = [p["id"] for p in FALSIFIABLE_PREDICTIONS]
    assert ids == [1, 2, 3, 4, 5], f"FAIL: prediction ids out of order"
    print(f"  five predictions registered with id/claim/falsification")
    print("PASS")


def test_9_pressure_below_resistance_is_a_no_op():
    """A measurement system with resistance higher than current
    distinction_share must not capture at all."""
    print("\n--- TEST 9: high-resistance system stays uncaptured ---")
    s = MeasurementSystem(
        name="high_resistance",
        intended_purpose="test",
        capture_rate_constant=1.0,
        resistance=0.9,
    )
    for _ in range(50):
        s.step(distinction_share=0.5)   # below 0.9 resistance
    assert s.capture_fraction == 0.0, \
        f"FAIL: should not capture when distinction_share < resistance, " \
        f"got {s.capture_fraction}"
    # raising distinction_share above resistance starts capture
    for _ in range(10):
        s.step(distinction_share=0.95)
    assert s.capture_fraction > 0.0, \
        "FAIL: should capture once distinction_share > resistance"
    print(f"  pressure < resistance: capture stayed at 0.0")
    print(f"  pressure > resistance: capture rose to "
          f"{s.capture_fraction:.4f}")
    print("PASS")


if __name__ == "__main__":
    test_1_energy_conservation()
    test_2_capture_monotone_and_bounded()
    test_3_low_resistance_captures_first()
    test_4_distinction_grows_under_default_dynamics()
    test_5_tolerance_band_contracts_with_support_drop()
    test_6_fraction_inside_in_unit_interval()
    test_7_history_records_each_step()
    test_8_falsifiable_predictions_schema()
    test_9_pressure_below_resistance_is_a_no_op()
    print("\nall status_extraction tests passed.")
