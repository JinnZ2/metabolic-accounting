"""
tests/test_money_signal.py

Tripwires for the money_signal/ package.

Smoke coverage for the coupling framework landed across AUDIT_10
(merge of dimensions + per-axis factor modules) and AUDIT_11 (merge
of coupling.py composition, coupling_state.py, coupling_substrate.py,
README).

Tests lock in:

  1. all 9 modules import
  2. per-factor validators pass where they currently pass
     (base, temporal, attribution, observer, substrate, state)
  3. DETECTOR test: validate_cultural_factors() currently FAILS on
     COMMUNITY_TRUST pointwise Minsky check. The README's stated
     invariant is at composed-coupling level; the validator's check
     is at factor level, which is stricter. This test fails LOUDLY
     when the bug is resolved — at which point it should be updated
     to assert success. AUDIT_11 § B documents the three fix options.
  4. coupling_matrix_as_dict runs end-to-end under a valid context
  5. Minsky coefficient satisfies README claim #1 at composed level
     in every non-near-collapse regime
  6. Near-collapse permits sign flips (README claim #7)
  7. Issuer insulation: TOKEN_ISSUER observer has damped coupling
     magnitude relative to TOKEN_HOLDER_THIN (README claim #6)

Notes:
  - These are coarse structural tests; the README's falsifiable
    claims (1-9) each warrant their own targeted test in future
    passes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_1_all_modules_import():
    print("\n--- TEST 1: all 9 modules import ---")
    import money_signal.dimensions            # noqa
    import money_signal.coupling_base         # noqa
    import money_signal.coupling_temporal     # noqa
    import money_signal.coupling_cultural     # noqa
    import money_signal.coupling_attribution  # noqa
    import money_signal.coupling_observer     # noqa
    import money_signal.coupling_substrate    # noqa
    import money_signal.coupling_state        # noqa
    import money_signal.coupling              # noqa
    print("  9/9 modules imported")
    print("PASS")


def test_2_passing_validators_still_pass():
    print("\n--- TEST 2: 6 factor validators pass ---")
    from money_signal.coupling_base import validate_base_matrix
    from money_signal.coupling_temporal import validate_temporal_factors
    from money_signal.coupling_attribution import validate_attribution_factors
    from money_signal.coupling_observer import validate_observer_factors
    from money_signal.coupling_substrate import validate_substrate_factors
    from money_signal.coupling_state import validate_state_factors

    for name, fn in [
        ("base", validate_base_matrix),
        ("temporal", validate_temporal_factors),
        ("attribution", validate_attribution_factors),
        ("observer", validate_observer_factors),
        ("substrate", validate_substrate_factors),
        ("state", validate_state_factors),
    ]:
        fn()
        print(f"  {name}: OK")
    print("PASS")


def test_3_cultural_validator_passes_at_composed_level():
    """Formerly a DETECTOR for the pointwise Minsky bug in
    validate_cultural_factors (AUDIT_11 § B). AUDIT_12 applied
    Option 1: the Minsky checks in cultural, attribution, and
    observer validators now run at the COMPOSED coupling level,
    matching the README's claim #1.

    COMMUNITY_TRUST previously tripped the pointwise check
    (f_nr=0.7 < f_rn=0.8). At composed level:
      K_BASE[N][R] * f_nr = 0.8 * 0.7 = 0.56
      K_BASE[R][N] * f_rn = 0.7 * 0.8 = 0.56
    Equal. Satisfies >=. Passes.

    And validate_all_factor_modules() — which the README calls
    out as "Always validate at startup" — now runs clean."""
    print("\n--- TEST 3: cultural validator passes at composed level ---")
    from money_signal.coupling_cultural import validate_cultural_factors
    from money_signal.coupling import validate_all_factor_modules

    validate_cultural_factors()
    validate_all_factor_modules()
    print("  validate_cultural_factors + validate_all_factor_modules pass")
    print("PASS")


def test_3b_validate_composition_passes_on_readme_cases():
    """README § Usage shows four example cases. validate_composition
    must pass on all of them — case_c in particular stacks NEAR_COLLAPSE
    × DIGITAL × THIN_HOLDER amplifiers in the same direction and
    composes K[N][R] ≈ 3.66. The sanity bound must accommodate that
    per README claim #8 (AUDIT_11 § B.5, bound widened from [-3, 3]
    to [-5, 5])."""
    print("\n--- TEST 3b: validate_composition on README example cases ---")
    from money_signal.dimensions import (
        DimensionalContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    from money_signal.coupling import validate_composition, minsky_coefficient

    cases = {
        "A healthy deep":   DimensionalContext(
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_DEEP,
            substrate=Substrate.DIGITAL,
            state=StateRegime.HEALTHY,
        ),
        "B healthy thin":   DimensionalContext(
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_THIN,
            substrate=Substrate.DIGITAL,
            state=StateRegime.HEALTHY,
        ),
        "C collapsing thin": DimensionalContext(
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_THIN,
            substrate=Substrate.DIGITAL,
            state=StateRegime.NEAR_COLLAPSE,
        ),
        "D reciprocity":    DimensionalContext(
            temporal=TemporalScope.GENERATIONAL,
            cultural=CulturalScope.HIGH_RECIPROCITY,
            attribution=AttributedValue.RECIPROCITY_TOKEN,
            observer=ObserverPosition.SUBSTRATE_PRODUCER,
            substrate=Substrate.TRUST_LEDGER,
            state=StateRegime.STRESSED,
        ),
    }
    for name, ctx in cases.items():
        validate_composition(ctx)
        print(f"  {name:<20s} minsky={minsky_coefficient(ctx):.2f}x")
    print("PASS")


def test_4_end_to_end_coupling_matrix():
    print("\n--- TEST 4: coupling_matrix_as_dict runs end-to-end ---")
    from money_signal.dimensions import (
        DimensionalContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime, MoneyTerm,
    )
    from money_signal.coupling import coupling_matrix_as_dict

    # Calibration context: INSTITUTIONAL + SEASONAL + STATE_ENFORCED
    # + METAL + HEALTHY → all factors ≈ 1.0, so composed ≈ K_BASE.
    ctx = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.HEALTHY,
    )
    K = coupling_matrix_as_dict(ctx)

    # 4x4 with diagonals 1.0 (self-coupling invariant, README line 35).
    assert len(K) == 4, f"FAIL: expected 4x4, got {len(K)}"
    for term in MoneyTerm:
        assert K[term][term] == 1.0, \
            f"FAIL: diagonal K[{term.value}][{term.value}] = {K[term][term]}"

    print(f"  4x4 matrix; diagonals = 1.0; sample K[N][R] = {K[MoneyTerm.N][MoneyTerm.R]:+.3f}")
    print("PASS")


def test_5_minsky_holds_at_composed_level():
    """README claim #1: K[N][R] >= K[R][N] in every non-near-collapse
    regime, at the COMPOSED coupling level."""
    print("\n--- TEST 5: Minsky asymmetry at composed level ---")
    from money_signal.dimensions import (
        DimensionalContext, MoneyTerm,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    from money_signal.coupling import coupling_matrix_as_dict

    # Sample across non-near-collapse state regimes.
    for state in (StateRegime.HEALTHY, StateRegime.STRESSED,
                  StateRegime.RECOVERING):
        ctx = DimensionalContext(
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_THIN,
            substrate=Substrate.METAL,
            state=state,
        )
        K = coupling_matrix_as_dict(ctx)
        k_nr = abs(K[MoneyTerm.N][MoneyTerm.R])
        k_rn = abs(K[MoneyTerm.R][MoneyTerm.N])
        assert k_nr >= k_rn - 1e-9, \
            (f"FAIL: Minsky asymmetry violated at state={state.value}: "
             f"|K[N][R]|={k_nr:.3f} < |K[R][N]|={k_rn:.3f}")
        print(f"  {state.value}: |K[N][R]|={k_nr:.3f} >= |K[R][N]|={k_rn:.3f}")
    print("PASS")


def test_6_near_collapse_permits_sign_flips():
    """README claim #7: near-collapse regime permits sign flips
    (in particular K[N][C] can go negative: panic-buying)."""
    print("\n--- TEST 6: near-collapse sign flips permitted ---")
    from money_signal.dimensions import (
        DimensionalContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    from money_signal.coupling import has_sign_flips

    ctx_healthy = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.HEALTHY,
    )
    ctx_collapse = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.NEAR_COLLAPSE,
    )

    healthy_flips = has_sign_flips(ctx_healthy)
    collapse_flips = has_sign_flips(ctx_collapse)

    assert not healthy_flips, \
        f"FAIL: HEALTHY regime has sign flips (should not)"
    # Collapse MAY have sign flips; it is allowed, not required.
    print(f"  HEALTHY sign_flips={healthy_flips}  NEAR_COLLAPSE sign_flips={collapse_flips}")
    print("PASS")


def test_7_issuer_insulation():
    """README claim #6: TOKEN_ISSUER experiences damped coupling on
    cost/latency-driving terms relative to thin holders. Central
    banks reading their own experience of the system systematically
    underestimate fragility."""
    print("\n--- TEST 7: issuer insulation vs thin holder ---")
    from money_signal.dimensions import (
        DimensionalContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    from money_signal.coupling import coupling_magnitude

    thin_ctx = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.STRESSED,
    )
    issuer_ctx = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_ISSUER,
        substrate=Substrate.METAL,
        state=StateRegime.STRESSED,
    )

    thin_mag = coupling_magnitude(thin_ctx)
    issuer_mag = coupling_magnitude(issuer_ctx)

    assert issuer_mag < thin_mag, \
        (f"FAIL: issuer insulation violated: issuer mag={issuer_mag:.3f} "
         f"must be < thin holder mag={thin_mag:.3f}")
    print(f"  thin holder mag={thin_mag:.3f}, issuer mag={issuer_mag:.3f}  "
          f"(issuer experiences damped coupling)")
    print("PASS")


def _helper_ctx(**overrides):
    """Build a DimensionalContext with baseline defaults, allowing
    a caller to vary one or more dimensions. Baseline is the calibration
    regime (INSTITUTIONAL + SEASONAL + STATE_ENFORCED + METAL + HEALTHY)
    with a THIN holder observer as the default (no observer calibration
    case exists per README)."""
    from money_signal.dimensions import (
        DimensionalContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    defaults = dict(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.HEALTHY,
    )
    defaults.update(overrides)
    return DimensionalContext(**defaults)


def test_8_hysteresis_recovering_damped_vs_healthy():
    """README claim #2: RECOVERING state has off-diagonal coupling
    factors strictly less than HEALTHY. Post-collapse systems operate
    with damped coupling regardless of nominal metric recovery."""
    print("\n--- TEST 8: README claim #2 hysteresis ---")
    from money_signal.dimensions import StateRegime, MoneyTerm
    from money_signal.coupling import coupling_matrix_as_dict

    k_healthy = coupling_matrix_as_dict(_helper_ctx(state=StateRegime.HEALTHY))
    k_recovering = coupling_matrix_as_dict(_helper_ctx(state=StateRegime.RECOVERING))

    for i in MoneyTerm:
        for j in MoneyTerm:
            if i == j:
                continue
            h, r = abs(k_healthy[i][j]), abs(k_recovering[i][j])
            assert r < h, \
                (f"FAIL: |K[{i.value}][{j.value}]| recovering={r:.3f} "
                 f"must be < healthy={h:.3f}")
    print("  all 12 off-diagonals: recovering < healthy")
    print("PASS")


def test_9_reciprocity_damping_trust_and_token():
    """README claim #3: TRUST_LEDGER substrate and RECIPROCITY_TOKEN
    attribution both damp K[N][R] below the metal/state-enforced
    baseline. Relational substrates carry repair protocols physical
    substrates lack."""
    print("\n--- TEST 9: README claim #3 reciprocity damping ---")
    from money_signal.dimensions import (
        Substrate, AttributedValue, MoneyTerm,
    )
    from money_signal.coupling import coupling_matrix_as_dict

    N, R = MoneyTerm.N, MoneyTerm.R
    baseline = coupling_matrix_as_dict(_helper_ctx())
    trust = coupling_matrix_as_dict(_helper_ctx(substrate=Substrate.TRUST_LEDGER))
    recip = coupling_matrix_as_dict(
        _helper_ctx(attribution=AttributedValue.RECIPROCITY_TOKEN)
    )

    base_nr = abs(baseline[N][R])
    assert abs(trust[N][R]) < base_nr, \
        f"FAIL: trust_ledger |K[N][R]|={abs(trust[N][R]):.3f} not < baseline {base_nr:.3f}"
    assert abs(recip[N][R]) < base_nr, \
        f"FAIL: reciprocity_token |K[N][R]|={abs(recip[N][R]):.3f} not < baseline {base_nr:.3f}"

    print(f"  baseline K[N][R]={base_nr:.3f}  "
          f"trust={abs(trust[N][R]):.3f}  recip={abs(recip[N][R]):.3f}")
    print("PASS")


def test_10_speculative_amplification():
    """README claim #4: SPECULATIVE_CLAIM attribution amplifies K[N][R]
    above baseline. Pure financialization has no substrate floor,
    institutional floor, relational floor, or sacred floor to catch
    collapse."""
    print("\n--- TEST 10: README claim #4 speculative amplification ---")
    from money_signal.dimensions import AttributedValue, MoneyTerm
    from money_signal.coupling import coupling_matrix_as_dict

    N, R = MoneyTerm.N, MoneyTerm.R
    baseline = coupling_matrix_as_dict(_helper_ctx())
    spec = coupling_matrix_as_dict(
        _helper_ctx(attribution=AttributedValue.SPECULATIVE_CLAIM)
    )

    assert abs(spec[N][R]) > abs(baseline[N][R]), \
        (f"FAIL: speculative |K[N][R]|={abs(spec[N][R]):.3f} "
         f"not > baseline {abs(baseline[N][R]):.3f}")
    print(f"  baseline K[N][R]={abs(baseline[N][R]):.3f}  "
          f"speculative={abs(spec[N][R]):.3f}  "
          f"amplification={abs(spec[N][R])/abs(baseline[N][R]):.2f}x")
    print("PASS")


def test_11_observer_asymmetry_thin_amplified():
    """README claim #5: TOKEN_HOLDER_THIN experiences amplified
    coupling on K[R][C], K[R][L], and K[N][R] relative to
    TOKEN_HOLDER_DEEP. Thin holders see more fragility than aggregate
    metrics reveal."""
    print("\n--- TEST 11: README claim #5 observer asymmetry ---")
    from money_signal.dimensions import ObserverPosition, MoneyTerm
    from money_signal.coupling import coupling_matrix_as_dict

    R, N, C, L = MoneyTerm.R, MoneyTerm.N, MoneyTerm.C, MoneyTerm.L
    thin = coupling_matrix_as_dict(
        _helper_ctx(observer=ObserverPosition.TOKEN_HOLDER_THIN)
    )
    deep = coupling_matrix_as_dict(
        _helper_ctx(observer=ObserverPosition.TOKEN_HOLDER_DEEP)
    )

    for (i, j) in [(R, C), (R, L), (N, R)]:
        a_thin, a_deep = abs(thin[i][j]), abs(deep[i][j])
        assert a_thin > a_deep, \
            (f"FAIL: |K[{i.value}][{j.value}]| "
             f"thin={a_thin:.3f} not > deep={a_deep:.3f}")
        print(f"  K[{i.value[:3]}][{j.value[:3]}]: thin={a_thin:.3f} > deep={a_deep:.3f}")
    print("PASS")


def test_12_minsky_dominance_in_collapse():
    """README claim #8: In NEAR_COLLAPSE, |K[N][R]| dominates all
    other off-diagonal coefficients in magnitude. Trust collapse
    becomes the only thing that matters; every other dynamic is
    second-order."""
    print("\n--- TEST 12: README claim #8 Minsky dominance in collapse ---")
    from money_signal.dimensions import StateRegime, Substrate, MoneyTerm
    from money_signal.coupling import coupling_matrix_as_dict

    # Use DIGITAL + TOKEN_HOLDER_THIN + NEAR_COLLAPSE per the README
    # case_c example. This is where claim #8 should show most clearly.
    K = coupling_matrix_as_dict(_helper_ctx(
        state=StateRegime.NEAR_COLLAPSE,
        substrate=Substrate.DIGITAL,
    ))
    N, R = MoneyTerm.N, MoneyTerm.R
    dominant = abs(K[N][R])

    for i in MoneyTerm:
        for j in MoneyTerm:
            if i == j:
                continue
            if i == N and j == R:
                continue
            v = abs(K[i][j])
            assert dominant > v, \
                (f"FAIL: |K[N][R]|={dominant:.3f} does not dominate "
                 f"|K[{i.value}][{j.value}]|={v:.3f}")
    print(f"  |K[N][R]|={dominant:.3f} dominates all 11 other off-diagonals")
    print("PASS")


def test_13_digital_amplifies_reliability_on_network():
    """README claim #9: DIGITAL substrate amplifies K[R][N] above
    metal baseline. Reliability is coupled to infrastructure
    continuity in a way physical substrates never were."""
    print("\n--- TEST 13: README claim #9 digital infrastructure coupling ---")
    from money_signal.dimensions import Substrate, MoneyTerm
    from money_signal.coupling import coupling_matrix_as_dict

    R, N = MoneyTerm.R, MoneyTerm.N
    metal = coupling_matrix_as_dict(_helper_ctx(substrate=Substrate.METAL))
    digital = coupling_matrix_as_dict(_helper_ctx(substrate=Substrate.DIGITAL))

    assert abs(digital[R][N]) > abs(metal[R][N]), \
        (f"FAIL: digital |K[R][N]|={abs(digital[R][N]):.3f} "
         f"not > metal {abs(metal[R][N]):.3f}")
    print(f"  metal K[R][N]={abs(metal[R][N]):.3f}  "
          f"digital={abs(digital[R][N]):.3f}")
    print("PASS")


if __name__ == "__main__":
    test_1_all_modules_import()
    test_2_passing_validators_still_pass()
    test_3_cultural_validator_passes_at_composed_level()
    test_3b_validate_composition_passes_on_readme_cases()
    test_4_end_to_end_coupling_matrix()
    test_5_minsky_holds_at_composed_level()
    test_6_near_collapse_permits_sign_flips()
    test_7_issuer_insulation()
    test_8_hysteresis_recovering_damped_vs_healthy()
    test_9_reciprocity_damping_trust_and_token()
    test_10_speculative_amplification()
    test_11_observer_asymmetry_thin_amplified()
    test_12_minsky_dominance_in_collapse()
    test_13_digital_amplifies_reliability_on_network()
    print("\nall money_signal tests passed.")
