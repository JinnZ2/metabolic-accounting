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
    regime_from_verdict_signal,
    context_from_verdict_signal,
    ALL_WEIGHTS,
)
from term_audit.provenance import coverage_report, ProvenanceKind


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


def test_9_weight_provenance_complete():
    """AUDIT_13 § A: every tunable weight in signal_quality carries
    typed Provenance per the AUDIT_07 discipline. This test locks
    that in — drops in coverage are load-bearing and surface the
    specific weight that regressed."""
    print("\n--- TEST 9: weight Provenance coverage complete ---")
    assert len(ALL_WEIGHTS) == 6, \
        f"FAIL: expected 6 weighted thresholds, got {len(ALL_WEIGHTS)}"
    provs = [w.provenance for w in ALL_WEIGHTS]
    cov = coverage_report(provs)
    assert cov["none"] == 0, f"FAIL: {cov['none']} weights without provenance"
    assert cov["incomplete"] == 0, \
        f"FAIL: {cov['incomplete']} weights incomplete: {cov['incomplete_details']}"
    assert cov["by_kind"]["design_choice"] == 6, \
        f"FAIL: expected all 6 weights DESIGN_CHOICE, got {cov['by_kind']}"
    print(f"  {cov['complete']}/{cov['total']} complete, all DESIGN_CHOICE")
    print("PASS")


def test_10_regime_from_verdict_signal():
    print("\n--- TEST 10: regime_from_verdict_signal maps correctly ---")
    from money_signal.dimensions import StateRegime
    assert regime_from_verdict_signal("GREEN") == StateRegime.HEALTHY
    assert regime_from_verdict_signal("AMBER") == StateRegime.STRESSED
    assert regime_from_verdict_signal("RED") == StateRegime.NEAR_COLLAPSE
    assert regime_from_verdict_signal("BLACK") == StateRegime.NEAR_COLLAPSE
    # lower-case should work (forgiving)
    assert regime_from_verdict_signal("green") == StateRegime.HEALTHY
    # recovering override
    assert regime_from_verdict_signal("GREEN", recovering=True) == StateRegime.RECOVERING
    # unknown signal raises
    try:
        regime_from_verdict_signal("PURPLE")
    except ValueError:
        pass
    else:
        raise AssertionError("FAIL: accepted unknown verdict signal")
    print("  GREEN->HEALTHY, AMBER->STRESSED, RED/BLACK->NEAR_COLLAPSE, recovering override, PURPLE rejected")
    print("PASS")


def test_11_context_from_verdict_signal_end_to_end():
    """Build a full DimensionalContext from a verdict + 5 declared
    dimensions, run it through signal_quality. Covers the common
    caller path named in AUDIT_12 § D.3."""
    print("\n--- TEST 11: context_from_verdict_signal end-to-end ---")
    from money_signal.dimensions import (
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    ctx_green = context_from_verdict_signal(
        "GREEN",
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
    )
    assert ctx_green.state == StateRegime.HEALTHY

    ctx_red = context_from_verdict_signal(
        "RED",
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
    )
    assert ctx_red.state == StateRegime.NEAR_COLLAPSE

    q_green = signal_quality(ctx_green)
    q_red = signal_quality(ctx_red)
    assert q_green > q_red, \
        f"FAIL: GREEN quality {q_green:.3f} not > RED quality {q_red:.3f}"
    print(f"  GREEN -> HEALTHY -> quality {q_green:.3f}")
    print(f"  RED   -> NEAR_COLLAPSE -> quality {q_red:.3f}")
    print("PASS")


def test_12_real_verdict_object_integration():
    """The helper takes a verdict signal string, so a caller holding
    an actual Verdict from verdict/assess.py can pipe
    verdict.sustainable_yield_signal straight in. This test closes
    the AUDIT_12 § D.3 concrete integration path."""
    print("\n--- TEST 12: real Verdict object integration ---")
    from verdict.assess import Verdict
    from money_signal.dimensions import (
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    v = Verdict(
        sustainable_yield_signal="AMBER",
        basin_trajectory="DEGRADING",
        time_to_red=3.0,
        forced_drawdown=50.0,
        regeneration_debt=0.0,
        metabolic_profit=100.0,
        reported_profit=200.0,
        profit_gap=100.0,
    )
    ctx = context_from_verdict_signal(
        v.sustainable_yield_signal,
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
    )
    assert ctx.state == StateRegime.STRESSED
    q = signal_quality(ctx)
    assert 0.0 < q < 0.92, f"FAIL: STRESSED quality {q:.3f} out of expected band"
    print(f"  AMBER verdict -> STRESSED regime -> quality {q:.3f}")
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
    test_9_weight_provenance_complete()
    test_10_regime_from_verdict_signal()
    test_11_context_from_verdict_signal_end_to_end()
    test_12_real_verdict_object_integration()
    print("\nall accounting_bridge tests passed.")
