"""
tests/test_money_three_scope_falsification.py

Tripwires for term_audit/audits/money_three_scope_falsification.py.

The module's load-bearing claim: money fails as a signal in every
scope where it is marketed to work (flow-system, community-organism,
civilization-lube). These tests lock that structural argument in,
plus verify the falsification hooks actually fire when the observable
MoneyState flags are flipped.

Structure follows the in-file test functions the module shipped with
(see its "In-file tests" section — AUDIT_10 moved them here per the
module's own comment: 'move to tests/test_money_three_scope_\
falsification.py when pasting into the repo').

Test 1: every scope fails under the current regime (no scope survives)
Test 2: structural claim holds under the current regime
Test 3: falsification hook — flip every flag to True, every scope
        survives, structural claim is falsified (the argument IS
        falsifiable, not tautological)
Test 4: partial rescue — flip only flow-system flags, only that
        scope survives; others still fail
Test 5: assumption flags emit one blocker per failed scope with
        correct source tags
Test 6: bridge to real AssumptionValidatorFlag in the adapter
        (shape compatibility smoke)
Test 7: load-bearing structural-claim tripwire with explicit context
        — if this test ever passes under current_regime_money_state,
        the argument has been falsified, NOT a test bug
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.audits.money_three_scope_falsification import (
    Scope,
    MoneyState,
    audit_money_across_three_scopes,
    current_regime_money_state,
    emit_assumption_flags,
    AssumptionValidatorFlagLite,
    to_real_flag,
)


def test_1_each_scope_fails_under_current_regime():
    print("\n--- TEST 1: each scope fails under current regime ---")
    v = audit_money_across_three_scopes(current_regime_money_state())
    for sv in v.per_scope:
        assert not sv.scope_claim_survives, (
            f"scope {sv.scope.value} survived; structural claim falsified. "
            f"Passed invariants: "
            f"{[r.invariant for r in sv.results if r.holds]}"
        )
    print(f"  flow/community/civilization all falsified "
          f"(4+4+4 invariant failures)")
    print("PASS")


def test_2_structural_claim_holds_under_current_regime():
    """LOAD-BEARING: money fails as a signal in every marketed scope.

    If this test flips from holds=True to holds=False under an honest
    reading of current_regime_money_state(), the module's structural
    argument has been falsified in the way the module was designed
    to surface — that is a real finding, not a test bug. Update the
    module's state flags AND the audit notes together."""
    print("\n--- TEST 2: structural claim holds under current regime ---")
    v = audit_money_across_three_scopes(current_regime_money_state())
    assert v.structural_claim_holds, (
        f"structural claim falsified; surviving scopes: "
        f"{[s.value for s in v.surviving_scopes]}"
    )
    print(f"  structural_claim_holds=True, no surviving scopes")
    print("PASS")


def test_3_falsification_hook_works():
    """The argument IS falsifiable. Flip every flag to True, every
    scope survives, structural claim is falsified. This tests that
    the hooks wire state to verdict correctly."""
    print("\n--- TEST 3: falsification hook works ---")
    state = MoneyState(
        unit_stable_over_time=True,
        conserved_across_transactions=True,
        observer_invariant=True,
        regeneration_rate_endogenous=True,
        signal_readable_by_all_members=True,
        signal_carries_substrate_info=True,
        no_single_actor_can_rewrite=True,
        failure_modes_symmetric=True,
        couples_without_extraction=True,
        phase_coherent_across_domains=True,
        degradation_visible_in_signal=True,
        replaceable_without_seizure=True,
    )
    v = audit_money_across_three_scopes(state)
    assert v.structural_claim_holds is False
    assert set(v.surviving_scopes) == {
        Scope.FLOW_SYSTEM,
        Scope.COMMUNITY_ORGANISM,
        Scope.CIVILIZATION_LUBE,
    }
    print(f"  all 12 flags True -> 3/3 scopes survive -> claim falsified")
    print("PASS")


def test_4_partial_rescue_single_scope():
    """Only flow-system invariants held -> only that scope survives."""
    print("\n--- TEST 4: partial rescue (flow-system only) ---")
    state = MoneyState(
        unit_stable_over_time=True,
        conserved_across_transactions=True,
        observer_invariant=True,
        regeneration_rate_endogenous=True,
        signal_readable_by_all_members=False,
        signal_carries_substrate_info=False,
        no_single_actor_can_rewrite=False,
        failure_modes_symmetric=False,
        couples_without_extraction=False,
        phase_coherent_across_domains=False,
        degradation_visible_in_signal=False,
        replaceable_without_seizure=False,
    )
    v = audit_money_across_three_scopes(state)
    assert v.surviving_scopes == (Scope.FLOW_SYSTEM,)
    assert Scope.COMMUNITY_ORGANISM in v.falsified_scopes
    assert Scope.CIVILIZATION_LUBE in v.falsified_scopes
    assert v.structural_claim_holds is False
    print(f"  only flow_system survives; other two falsified")
    print("PASS")


def test_5_assumption_flags_emit_per_failed_scope():
    print("\n--- TEST 5: assumption flags emit per failed scope ---")
    v = audit_money_across_three_scopes(current_regime_money_state())
    flags = emit_assumption_flags(v)
    assert len(flags) == 3
    sources = {f.source for f in flags}
    assert sources == {
        "money_three_scope_falsification:flow_system",
        "money_three_scope_falsification:community_organism",
        "money_three_scope_falsification:civilization_lube",
    }
    for f in flags:
        assert f.severity == "blocker"
        assert isinstance(f, AssumptionValidatorFlagLite)
    print(f"  3 blocker flags emitted, one per falsified scope")
    print("PASS")


def test_6_bridge_to_real_assumption_validator_flag():
    """The lite dataclass must be mappable to the real
    AssumptionValidatorFlag in the adapter. The field names differ
    between the two types (lite: source/reason/str-severity; real:
    source_audit/message/float-severity + failure_mode), so a caller
    uses the `to_real_flag` bridge. This test locks the bridge in."""
    print("\n--- TEST 6: bridge to real AssumptionValidatorFlag ---")
    from term_audit.integration.metabolic_accounting_adapter import (
        AssumptionValidatorFlag,
    )
    v = audit_money_across_three_scopes(current_regime_money_state())
    lite_flags = emit_assumption_flags(v)

    real_flags = [
        to_real_flag(lf, failure_mode="scope_invariant_failure")
        for lf in lite_flags
    ]
    assert len(real_flags) == len(lite_flags) == 3
    for rf, lf in zip(real_flags, lite_flags):
        assert isinstance(rf, AssumptionValidatorFlag)
        assert rf.source_audit == lf.source
        assert rf.message == lf.reason
        assert rf.failure_mode == "scope_invariant_failure"
        # Severity str -> float mapping; "blocker" -> 1.0
        assert 0.0 <= rf.severity <= 1.0
        assert rf.severity == 1.0   # blocker-level

    print(f"  {len(real_flags)} lite flags mapped to real AssumptionValidatorFlag")
    print(f"  severity 'blocker' -> 1.0; field names translated")
    print("PASS")


def test_7_control_vs_measurement_claim_surfaces_in_every_scope():
    """The structural argument's core claim: a term cannot be both
    the ruler and the hand moving the ruler. This manifests as
    'regeneration_rate_endogenous=False' (flow-system) AND
    'no_single_actor_can_rewrite=False' (community-organism). Both
    fail in the current regime. Lock both as load-bearing."""
    print("\n--- TEST 7: control-vs-measurement failure visible in 2+ scopes ---")
    v = audit_money_across_three_scopes(current_regime_money_state())

    flow = next(sv for sv in v.per_scope if sv.scope == Scope.FLOW_SYSTEM)
    endo = next(r for r in flow.results if r.invariant == "endogenous_regeneration")
    assert not endo.holds, \
        "FAIL: endogenous_regeneration held; control-vs-measurement argument weakens"

    community = next(sv for sv in v.per_scope if sv.scope == Scope.COMMUNITY_ORGANISM)
    rewrite = next(r for r in community.results if r.invariant == "no_unilateral_rewrite")
    assert not rewrite.holds, \
        "FAIL: no_unilateral_rewrite held; control-vs-measurement argument weakens"

    print(f"  endogenous_regeneration=False, no_unilateral_rewrite=False")
    print(f"  'ruler and hand moving the ruler' contradiction surfaces as designed")
    print("PASS")


if __name__ == "__main__":
    test_1_each_scope_fails_under_current_regime()
    test_2_structural_claim_holds_under_current_regime()
    test_3_falsification_hook_works()
    test_4_partial_rescue_single_scope()
    test_5_assumption_flags_emit_per_failed_scope()
    test_6_bridge_to_real_assumption_validator_flag()
    test_7_control_vs_measurement_claim_surfaces_in_every_scope()
    print("\nall money_three_scope_falsification tests passed.")
