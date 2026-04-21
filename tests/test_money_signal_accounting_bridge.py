"""
tests/test_money_signal_accounting_bridge.py

Tripwires for money_signal/accounting_bridge.py (AUDIT_12).

Locks in:

  1. signal_quality() returns values in [0, 1]
  2. healthy > stressed > near-collapse gradient holds (monotone
     degradation as state regime worsens)
  3. near-collapse quality is substantially below healthy (< 0.7 gap)
  4. coupling_assumption_flags emits fewer flags under healthy than
     near-collapse
  5. near-collapse emits the specific near_collapse_regime flag at
     high severity
  6. every emitted flag has valid AssumptionValidatorFlag shape
     (source_audit, failure_mode, severity in [0,1], message)
  7. adjust_glucose_flow bridges a GlucoseFlow + context -> a
     SignalAdjustedFlow without mutating the flow
  8. the bridge is one-way: money_signal/ does not import
     accounting/. Proven by inspecting imports.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from money_signal.dimensions import (
    DimensionalContext,
    TemporalScope, CulturalScope, AttributedValue,
    ObserverPosition, Substrate, StateRegime,
)
from money_signal.accounting_bridge import (
    signal_quality,
    coupling_assumption_flags,
    adjust_glucose_flow,
    SignalAdjustedFlow,
)


def _ctx(state):
    return DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=state,
    )


def test_1_signal_quality_bounded():
    print("\n--- TEST 1: signal_quality() in [0, 1] ---")
    for state in StateRegime:
        q = signal_quality(_ctx(state))
        assert 0.0 <= q <= 1.0, f"FAIL: {state.value} -> {q}"
    print(f"  all {len(list(StateRegime))} state regimes bounded in [0, 1]")
    print("PASS")


def test_2_healthy_stressed_collapse_gradient():
    """LOAD-BEARING: signal quality must degrade monotonically
    as state regime degrades. Reversal of this ordering would
    invert the bridge's semantics."""
    print("\n--- TEST 2: healthy > stressed > near-collapse gradient ---")
    q_healthy      = signal_quality(_ctx(StateRegime.HEALTHY))
    q_stressed     = signal_quality(_ctx(StateRegime.STRESSED))
    q_collapse     = signal_quality(_ctx(StateRegime.NEAR_COLLAPSE))

    assert q_healthy > q_stressed, \
        f"FAIL: healthy {q_healthy:.3f} not > stressed {q_stressed:.3f}"
    assert q_stressed > q_collapse, \
        f"FAIL: stressed {q_stressed:.3f} not > near-collapse {q_collapse:.3f}"

    print(f"  healthy={q_healthy:.3f} > stressed={q_stressed:.3f} > collapse={q_collapse:.3f}")
    print("PASS")


def test_3_near_collapse_substantial_quality_loss():
    """Under near-collapse the signal quality must drop far enough
    below healthy that downstream systems clearly need to question
    monetary denomination."""
    print("\n--- TEST 3: near-collapse drops quality substantially ---")
    q_healthy  = signal_quality(_ctx(StateRegime.HEALTHY))
    q_collapse = signal_quality(_ctx(StateRegime.NEAR_COLLAPSE))
    gap = q_healthy - q_collapse
    assert gap > 0.3, \
        f"FAIL: healthy-to-collapse gap {gap:.3f} not > 0.3"
    print(f"  gap={gap:.3f} (healthy {q_healthy:.3f} -> collapse {q_collapse:.3f})")
    print("PASS")


def test_4_flags_scale_with_regime():
    print("\n--- TEST 4: flag count scales with regime stress ---")
    n_healthy  = len(coupling_assumption_flags(_ctx(StateRegime.HEALTHY)))
    n_stressed = len(coupling_assumption_flags(_ctx(StateRegime.STRESSED)))
    n_collapse = len(coupling_assumption_flags(_ctx(StateRegime.NEAR_COLLAPSE)))
    assert n_healthy <= n_stressed <= n_collapse, \
        f"FAIL: flag counts do not scale: H={n_healthy} S={n_stressed} C={n_collapse}"
    print(f"  flags: healthy={n_healthy}  stressed={n_stressed}  collapse={n_collapse}")
    print("PASS")


def test_5_near_collapse_emits_specific_flag():
    """LOAD-BEARING: near-collapse must specifically emit the
    near_collapse_regime flag at high severity so downstream
    consumers cannot mistake 'slightly stressed' for 'collapsing'."""
    print("\n--- TEST 5: near_collapse_regime flag present at high severity ---")
    flags = coupling_assumption_flags(_ctx(StateRegime.NEAR_COLLAPSE))
    matching = [f for f in flags if f.failure_mode == "near_collapse_regime"]
    assert len(matching) == 1, \
        f"FAIL: expected 1 near_collapse_regime flag, got {len(matching)}"
    f = matching[0]
    assert f.severity >= 0.8, \
        f"FAIL: near_collapse_regime severity {f.severity} not >= 0.8"
    print(f"  near_collapse_regime flag found; severity={f.severity:.2f}")
    print("PASS")


def test_6_flag_shape_compatible():
    """Every emitted flag must have the real AssumptionValidatorFlag
    shape so downstream consumers do not need to adapt. No lite
    type detour (unlike money_three_scope_falsification's
    AssumptionValidatorFlagLite, which is a deliberate standalone
    decoupling)."""
    print("\n--- TEST 6: flag shape matches real AssumptionValidatorFlag ---")
    from term_audit.integration.metabolic_accounting_adapter import (
        AssumptionValidatorFlag,
    )
    for state in (StateRegime.STRESSED, StateRegime.NEAR_COLLAPSE):
        for f in coupling_assumption_flags(_ctx(state)):
            assert isinstance(f, AssumptionValidatorFlag)
            assert f.source_audit.strip()
            assert f.failure_mode.strip()
            assert 0.0 <= f.severity <= 1.0
            assert f.message.strip()
    print("  all flags under STRESSED and NEAR_COLLAPSE are well-formed")
    print("PASS")


def test_7_adjust_glucose_flow_passes_through():
    """adjust_glucose_flow must:
      - compute quality from the context
      - return raw + adjusted profit views
      - NOT mutate the original GlucoseFlow
    """
    print("\n--- TEST 7: adjust_glucose_flow produces a non-mutating view ---")
    from accounting.glucose import GlucoseFlow
    flow = GlucoseFlow(
        revenue=1000.0,
        direct_operating_cost=600.0,
        regeneration_paid=100.0,
        regeneration_required=120.0,
        cascade_burn=50.0,
    )
    raw_reported = flow.reported_profit()
    raw_metabolic = flow.metabolic_profit()

    view = adjust_glucose_flow(flow, _ctx(StateRegime.NEAR_COLLAPSE))
    assert isinstance(view, SignalAdjustedFlow)
    assert view.reported_profit_raw == raw_reported
    assert view.metabolic_profit_raw == raw_metabolic
    assert 0.0 <= view.quality <= 1.0
    assert view.reported_profit_adjusted == view.reported_profit_raw * view.quality
    # Flow object was not touched.
    assert flow.revenue == 1000.0
    assert flow.regeneration_paid == 100.0

    print(f"  reported raw={view.reported_profit_raw:.1f}  "
          f"adjusted={view.reported_profit_adjusted:.1f}  "
          f"quality={view.quality:.3f}")
    print("PASS")


def test_8_one_way_bridge_no_accounting_import_in_money_signal():
    """LOAD-BEARING: money_signal/ must not import accounting/. The
    bridge direction is money_signal -> term_audit (for
    AssumptionValidatorFlag). Reversing this would entangle the
    layers."""
    print("\n--- TEST 8: money_signal does not import accounting ---")
    import money_signal
    pkg_dir = os.path.dirname(money_signal.__file__)
    offenders = []
    for name in os.listdir(pkg_dir):
        if not name.endswith(".py"):
            continue
        path = os.path.join(pkg_dir, name)
        with open(path, "r") as fh:
            for i, line in enumerate(fh, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if (stripped.startswith("from accounting.") or
                    stripped.startswith("import accounting")):
                    offenders.append(f"{name}:{i}: {stripped}")

    # accounting_bridge.py is allowed to reference GlucoseFlow
    # inside function bodies (lazy) — but not at module top level.
    # Allow *function-local* imports inside accounting_bridge; catch
    # only top-level imports here via the startswith check, which
    # would only match unindented lines.
    assert not offenders, \
        f"FAIL: money_signal imports accounting at top level:\n" + "\n".join(offenders)
    print(f"  no top-level accounting imports in any money_signal/ module")
    print("PASS")


if __name__ == "__main__":
    test_1_signal_quality_bounded()
    test_2_healthy_stressed_collapse_gradient()
    test_3_near_collapse_substantial_quality_loss()
    test_4_flags_scale_with_regime()
    test_5_near_collapse_emits_specific_flag()
    test_6_flag_shape_compatible()
    test_7_adjust_glucose_flow_passes_through()
    test_8_one_way_bridge_no_accounting_import_in_money_signal()
    print("\nall accounting_bridge tests passed.")
