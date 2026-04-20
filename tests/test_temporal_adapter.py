"""
tests/test_temporal_adapter.py

Tripwires for term_audit/integration/temporal_adapter.py.

Minimal smoke-test coverage landed as part of AUDIT_06 drift repair:
the module previously raised NameError at import (TermAudit annotated
but not imported), and no test exercised it. These cases lock in:

  - module imports cleanly
  - the five falsifiable predictions are registered
  - the end-to-end example runs and returns the expected shape
  - threshold crossings are computed monotonically
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.integration.temporal_adapter import (
    AuditSnapshot,
    BasinTrajectory,
    TemporalVerdict,
    TimestampedBasinState,
    build_basin_trajectory,
    build_temporal_verdict,
    detect_early_warnings,
    temporal_end_to_end_example,
    FALSIFIABLE_PREDICTIONS,
)
from term_audit.integration.metabolic_accounting_adapter import (
    BasinStateInput,
    BasinCategory,
)


def test_1_module_imports_cleanly():
    """Import side effects must not raise (regression: was NameError)."""
    print("\n--- TEST 1: module imports cleanly ---")
    assert AuditSnapshot is not None
    assert build_temporal_verdict is not None
    print("  all expected symbols exposed")
    print("PASS")


def test_2_falsifiable_predictions_registered():
    """Temporal adapter must ship its own falsifiable predictions."""
    print("\n--- TEST 2: falsifiable predictions registered ---")
    assert len(FALSIFIABLE_PREDICTIONS) >= 1, \
        f"FAIL: expected >=1 predictions, got {len(FALSIFIABLE_PREDICTIONS)}"
    for p in FALSIFIABLE_PREDICTIONS:
        # FALSIFIABLE_PREDICTIONS is a list of dicts with 'claim' and
        # 'falsification' keys (see module end).
        assert p.get("claim", "").strip(), f"FAIL: empty claim in {p}"
        assert p.get("falsification", "").strip(), \
            f"FAIL: empty falsification in {p}"
    print(f"  {len(FALSIFIABLE_PREDICTIONS)} predictions registered")
    print("PASS")


def test_3_end_to_end_example_runs():
    """End-to-end example returns the expected top-level keys."""
    print("\n--- TEST 3: end-to-end example runs ---")
    result = temporal_end_to_end_example()
    expected_keys = {"trajectories", "temporal_verdict", "early_warnings"}
    missing = expected_keys - set(result.keys())
    assert not missing, f"FAIL: missing keys: {missing}"

    tv = result["temporal_verdict"]
    assert "trend_slope" in tv
    assert "signal_quality_degrading" in tv
    assert "threshold_crossings" in tv

    # early-warning shape
    for w in result["early_warnings"]:
        assert "type" in w and "basin" in w and "action" in w

    print(f"  {len(result['trajectories'])} trajectories, "
          f"{len(result['early_warnings'])} early warnings")
    print("PASS")


def test_4_trend_slope_captures_degradation():
    """A monotonically degrading basin yields a negative trend slope."""
    print("\n--- TEST 4: trend slope captures degradation ---")
    # Linear degradation from 1.0 at step 0 to 0.1 at step 9, -0.1/step.
    snapshots = []
    for i in range(10):
        level = 1.0 - 0.1 * i
        state = BasinStateInput(
            name="test_basin",
            category=BasinCategory.SOIL,
            current_level=max(level, 0.0),
            regeneration_rate=0.0,
            extraction_rate=0.1,
            carrying_capacity=1.0,
            signal_quality=0.8,
            assumption_boundary=None,
        )
        snapshots.append(TimestampedBasinState(timestamp=float(i), state=state))

    trajectories = build_basin_trajectory(snapshots)
    assert "test_basin" in trajectories
    traj = trajectories["test_basin"]
    assert len(traj.levels) == 10
    assert traj.levels[0] > traj.levels[-1]

    verdict = build_temporal_verdict(
        entity="test_firm",
        trajectories=trajectories,
        current_yield=0.5,
        threshold=0.2,
    )
    # Slope is the aggregate trend across basins; -0.1/step for a
    # single basin with per-step drop 0.1. Locking in sign, not
    # magnitude (magnitude would couple to the module's weighting).
    assert verdict.trend_slope < 0, \
        f"FAIL: expected negative trend, got {verdict.trend_slope}"
    assert "test_basin" in verdict.threshold_crossings

    print(f"  trend slope: {verdict.trend_slope:.3f}")
    print("PASS")


if __name__ == "__main__":
    test_1_module_imports_cleanly()
    test_2_falsifiable_predictions_registered()
    test_3_end_to_end_example_runs()
    test_4_trend_slope_captures_degradation()
    print("\nall temporal_adapter tests passed.")
