"""
money_signal/coupling_state.py

State regime factor functions for the money signal coupling matrix.

The current dynamic regime of the monetary system shifts coupling
coefficients. Healthy, stressed, and near-collapse regimes each have
distinct coupling signatures. Recovering is a distinct regime from
healthy because of hysteresis -- post-collapse systems do not return
to pre-collapse coupling even after nominal metrics recover.

This is the ONLY factor module allowed to produce sign flips. All
other factors (temporal, cultural, attribution, observer, substrate)
are non-negative multipliers that can damp or amplify but cannot
invert direction. State regime can invert because near-collapse
dynamics include reflexive sign-flipping: rising cost can briefly
increase acceptance (panic buying to secure tokens before they fail)
before snapping back to the normal negative coupling.

Core physical intuition:

  HEALTHY: base coupling applies. All invariants hold. The system
  can absorb normal fluctuations. This is the calibration regime.

  STRESSED: margins thin. Off-diagonal coupling amplifies because
  there is less slack in every term to absorb shocks. Reliability
  drops propagate faster through the network. Cost and latency
  co-move more tightly. Minsky asymmetry strengthens.

  NEAR_COLLAPSE: nonlinear regime. Coupling coefficients may
  saturate (hit max amplitude) or flip sign (reflexive panic
  behavior). Trust collapse becomes self-reinforcing: K[N][R]
  no longer just amplifies -- it dominates every other term.
  System enters an attractor basin that cannot be escaped through
  normal parameter changes. Requires external intervention or
  substrate replacement.

  RECOVERING: hysteresis regime. Distinct from healthy because
  trust rebuilds asymmetrically. Coupling is damped rather than
  amplified -- the system is moving slowly, carefully. Minsky
  asymmetry is reduced in magnitude but takes the opposite form:
  rebuild is slow but collapse is also dampened because scar
  tissue prevents full re-engagement. The system does not forget
  what happened. Reliability metrics can recover long before
  network acceptance does. Cost and latency coupling is dampened
  because the system is operating with safety margins that were
  absent in healthy regime.

External calibration anchor (informational, not imported):

  OSDI -- the Overall Socialist Dependence Index from
  Mathematic-economics @ equations-v1 -- composes SID, MSI, ISR,
  BSC, MM into a [0, 1] structural-context scalar describing how
  much of the institutional substrate is collectively-funded vs
  privately-funded. It is NOT a state regime, but it constrains
  which regime is possible: a system with OSDI ~0.77 (the
  current US baseline math-econ reports) cannot enter HEALTHY
  with the same coupling matrix as a system with OSDI ~0.3, even
  if the named state matches. A future calibration of this module
  may consume an external OSDI score per regime; today the
  HEALTHY/STRESSED/NEAR_COLLAPSE/RECOVERING enum is the only
  context input. See docs/EXTERNAL_OPERATIONALIZATIONS.md for the
  citation and the signal-quality discount caveat that applies to
  every money-denominated math-econ equation.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import MoneyTerm, StateRegime


# ============================================================================
# STATE FACTOR MATRIX
# ============================================================================

# Signed multipliers. Unlike other factor modules, state regime
# factors can be negative. A negative factor inverts the base
# coupling direction for that specific coefficient. This is reserved
# for near-collapse dynamics where reflexive behavior produces
# direction changes that are physically real.

_STATE_FACTORS: Dict[StateRegime, Dict[MoneyTerm, Dict[MoneyTerm, float]]] = {

    # ----------------------------------------------------------------
    # HEALTHY: base coupling applies
    #
    # All factors = 1.0. This is the calibration regime.
    # ----------------------------------------------------------------
    StateRegime.HEALTHY: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # STRESSED: margins thin, off-diagonals amplify
    #
    # Amplification is uniform but modest. Minsky asymmetry strengthens
    # because rebuild mechanisms slow down under stress while collapse
    # pathways remain fast or accelerate. No sign flips yet -- those
    # are reserved for near-collapse.
    # ----------------------------------------------------------------
    StateRegime.STRESSED: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.3,
            MoneyTerm.C: 1.4,
            MoneyTerm.L: 1.3,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.5,   # reliability loss propagates faster under stress
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.3,
            MoneyTerm.L: 1.2,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.4,
            MoneyTerm.N: 1.3,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.4,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.3,
            MoneyTerm.N: 1.2,
            MoneyTerm.C: 1.4,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # NEAR_COLLAPSE: nonlinear regime, sign flips allowed
    #
    # The system is in a reflexive attractor basin. Trust collapse
    # is self-reinforcing. Some coupling coefficients invert because
    # panic behavior produces the opposite of the normal response:
    #
    #   K[N][C] flips negative:
    #     In healthy regime, rising cost reduces acceptance.
    #     In panic regime, rising cost INCREASES acceptance briefly
    #     as holders rush to secure tokens before they fail further.
    #     This is the "bank run" dynamic.
    #
    #   K[C][N] amplifies extremely:
    #     Acceptance loss drives cost spikes at extreme rates because
    #     counterparty pools collapse nonlinearly.
    #
    # All other couplings amplify toward saturation. Minsky asymmetry
    # becomes extreme (K[N][R] dominates the dynamics).
    # ----------------------------------------------------------------
    StateRegime.NEAR_COLLAPSE: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.8,
            MoneyTerm.C: 1.7,
            MoneyTerm.L: 1.6,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 2.2,    # trust collapse dominates everything in near-collapse
            MoneyTerm.N: 1.0,
            MoneyTerm.C: -0.5,   # SIGN FLIP: panic buying briefly inverts normal cost-acceptance coupling
            MoneyTerm.L: 1.5,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.9,
            MoneyTerm.N: 2.0,    # acceptance loss drives cost spikes nonlinearly
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.8,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.8,
            MoneyTerm.N: 1.7,
            MoneyTerm.C: 1.8,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # RECOVERING: hysteresis regime
    #
    # Coupling is damped in both directions. The system has scar
    # tissue. Trust rebuild is slow -- K[R][N] factor < K[N][R]
    # factor still holds, but both are below 1.0. The system does
    # not forget.
    #
    # This is structurally different from HEALTHY. Metrics may look
    # healthy again but coupling signatures reveal the hysteresis.
    # This is how you distinguish "recovered to normal" from
    # "settled into a new lower-amplitude equilibrium after trauma."
    #
    # Many real monetary systems are in RECOVERING state without
    # anyone noticing because the nominal metrics look healthy. The
    # coupling signature is the only way to tell.
    # ----------------------------------------------------------------
    StateRegime.RECOVERING: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.6,    # network signal is muted -- trust has not fully returned
            MoneyTerm.C: 0.7,
            MoneyTerm.L: 0.6,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.7,    # rebuild still slower than collapse, but both damped
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.6,
            MoneyTerm.L: 0.5,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.7,
            MoneyTerm.N: 0.6,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.7,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.6,
            MoneyTerm.N: 0.5,
            MoneyTerm.C: 0.7,
            MoneyTerm.L: 1.0,
        },
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def state_factor(
    i: MoneyTerm, j: MoneyTerm, state: StateRegime
) -> float:
    """
    Return the multiplicative state factor for coupling K_ij in the
    given state regime.

    Args:
        i: the responding term
        j: the driving term
        state: the current dynamic regime

    Returns:
        Signed multiplicative factor. May be negative only in
        NEAR_COLLAPSE regime to encode reflexive panic dynamics.
    """
    return _STATE_FACTORS[state][i][j]


def iter_state_factors(
    state: StateRegime,
) -> Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...]:
    """
    Iterate over all (i, j, factor) triples for the given state.
    """
    return tuple(
        (i, j, _STATE_FACTORS[state][i][j])
        for i in MoneyTerm
        for j in MoneyTerm
    )


def is_sign_flipped(
    i: MoneyTerm, j: MoneyTerm, state: StateRegime
) -> bool:
    """
    Return True if the state factor for K_ij in this state inverts
    the base coupling sign.

    This is a diagnostic. Sign flips are allowed only in NEAR_COLLAPSE
    and indicate reflexive nonlinear dynamics.
    """
    return _STATE_FACTORS[state][i][j] < 0.0


# ============================================================================
# VALIDATION
# ============================================================================

def validate_state_factors() -> None:
    """
    Check structural invariants for the state factor tables.

    Raises AssertionError on violation.
    """
    # 1. Every state regime must have a full 4x4 factor matrix.
    for state in StateRegime:
        assert state in _STATE_FACTORS, (
            f"Missing state factor matrix for {state.value}"
        )
        for i in MoneyTerm:
            for j in MoneyTerm:
                assert j in _STATE_FACTORS[state][i], (
                    f"Missing factor K[{i.value}][{j.value}] "
                    f"for state {state.value}"
                )

    # 2. Self-coupling factor must be 1.0 for every state.
    for state in StateRegime:
        for term in MoneyTerm:
            v = _STATE_FACTORS[state][term][term]
            assert v == 1.0, (
                f"Self-coupling factor for {state.value} at "
                f"{term.value} must be 1.0, got {v}"
            )

    # 3. HEALTHY is the calibration regime. All factors must be 1.0.
    for i in MoneyTerm:
        for j in MoneyTerm:
            v = _STATE_FACTORS[StateRegime.HEALTHY][i][j]
            assert v == 1.0, (
                f"HEALTHY must have all factors = 1.0 (calibration regime), "
                f"got K[{i.value}][{j.value}] = {v}"
            )

    # 4. Sign flips allowed ONLY in NEAR_COLLAPSE.
    #    Any negative factor in HEALTHY, STRESSED, or RECOVERING is a bug.
    for state in (StateRegime.HEALTHY, StateRegime.STRESSED, StateRegime.RECOVERING):
        for i in MoneyTerm:
            for j in MoneyTerm:
                v = _STATE_FACTORS[state][i][j]
                assert v >= 0.0, (
                    f"Sign flip not permitted in {state.value}: "
                    f"K[{i.value}][{j.value}] = {v}. "
                    f"Sign flips are reserved for NEAR_COLLAPSE."
                )

    # 5. STRESSED must have off-diagonal factors >= HEALTHY factors.
    #    Stress amplifies coupling, never damps it.
    for i in MoneyTerm:
        for j in MoneyTerm:
            if i == j:
                continue
            stressed = _STATE_FACTORS[StateRegime.STRESSED][i][j]
            healthy = _STATE_FACTORS[StateRegime.HEALTHY][i][j]
            assert stressed >= healthy, (
                f"STRESSED must amplify K[{i.value}][{j.value}]: "
                f"stressed={stressed} < healthy={healthy}"
            )

    # 6. RECOVERING must have off-diagonal factors < HEALTHY factors.
    #    Hysteresis means the system moves more cautiously than
    #    pre-collapse. This is the defining signature of recovery.
    for i in MoneyTerm:
        for j in MoneyTerm:
            if i == j:
                continue
            recovering = _STATE_FACTORS[StateRegime.RECOVERING][i][j]
            healthy = _STATE_FACTORS[StateRegime.HEALTHY][i][j]
            assert recovering < healthy, (
                f"RECOVERING must damp K[{i.value}][{j.value}]: "
                f"recovering={recovering} >= healthy={healthy}. "
                f"Hysteresis requires post-collapse coupling below pre-collapse."
            )

    # 7. NEAR_COLLAPSE Minsky dominance: K[N][R] factor must exceed
    #    all other factors in the matrix (except self-couplings).
    #    Trust collapse dominates all other dynamics in near-collapse.
    nc = _STATE_FACTORS[StateRegime.NEAR_COLLAPSE]
    k_nr = nc[MoneyTerm.N][MoneyTerm.R]
    for i in MoneyTerm:
        for j in MoneyTerm:
            if i == j:
                continue
            if (i, j) == (MoneyTerm.N, MoneyTerm.R):
                continue
            # Compare magnitudes since one coefficient may be negative.
            assert abs(k_nr) >= abs(nc[i][j]), (
                f"NEAR_COLLAPSE Minsky dominance violated: "
                f"|K[N][R]|={abs(k_nr)} must dominate all other couplings, "
                f"but |K[{i.value}][{j.value}]|={abs(nc[i][j])}"
            )

    # 8. Minsky asymmetry direction preserved in HEALTHY, STRESSED, and
    #    RECOVERING regimes. (NEAR_COLLAPSE may have sign flips that
    #    make this check undefined for specific coupling pairs.)
    for state in (StateRegime.HEALTHY, StateRegime.STRESSED, StateRegime.RECOVERING):
        f_nr = _STATE_FACTORS[state][MoneyTerm.N][MoneyTerm.R]
        f_rn = _STATE_FACTORS[state][MoneyTerm.R][MoneyTerm.N]
        assert f_nr >= f_rn, (
            f"Minsky asymmetry violated in {state.value}: "
            f"K[N][R] factor={f_nr} must be >= K[R][N] factor={f_rn}"
        )

    # 9. Recovering asymmetry: rebuild factor must still be less than
    #    or equal to collapse factor even in recovery, BUT both must
    #    be dampened below HEALTHY values. Scar tissue is bidirectional.
    recovering = _STATE_FACTORS[StateRegime.RECOVERING]
    assert recovering[MoneyTerm.N][MoneyTerm.R] < 1.0, (
        "RECOVERING collapse factor must be < 1.0 -- "
        "scar tissue dampens even the collapse pathway"
    )
    assert recovering[MoneyTerm.R][MoneyTerm.N] < 1.0, (
        "RECOVERING rebuild factor must be < 1.0 -- "
        "trust rebuilds slower than it did before collapse"
    )


# ============================================================================
# DISPLAY
# ============================================================================

def format_state_factors(state: StateRegime) -> str:
    """
    Return a human-readable string of the state factor matrix.
    Sign-flipped entries are marked with an asterisk.
    """
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>7}" for t in terms)
    lines = [
        f"State factors for {state.value}:",
        header,
        "        " + "-" * (9 * len(terms)),
    ]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            v = _STATE_FACTORS[state][i][j]
            marker = "*" if v < 0.0 else " "
            row += f" {v:+.2f}{marker}"
        lines.append(row)
    if any(is_sign_flipped(i, j, state) for i in terms for j in terms):
        lines.append("  * = sign flip (reflexive nonlinear dynamics)")
    return "\n".join(lines)


def format_regime_comparison() -> str:
    """
    Return a summary comparing coupling signatures across regimes.

    This is the diagnostic that distinguishes RECOVERING from HEALTHY
    using coupling signatures rather than nominal metrics.
    """
    terms = list(MoneyTerm)
    lines = ["Regime comparison (off-diagonal coupling signatures):"]
    for state in StateRegime:
        factors = _STATE_FACTORS[state]
        off_diag = [
            factors[i][j]
            for i in terms
            for j in terms
            if i != j
        ]
        mean = sum(abs(v) for v in off_diag) / len(off_diag)
        signed_sum = sum(off_diag)
        lines.append(
            f"  {state.value:>14}: "
            f"mean|factor|={mean:.2f}  "
            f"signed_sum={signed_sum:+.2f}"
        )
    lines.append("")
    lines.append("  Diagnostic: if mean|factor| < 1.0 the system is RECOVERING,")
    lines.append("  not HEALTHY, regardless of what nominal metrics suggest.")
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_state_factors()
    print("State regime factors validated.")
    print()
    for state in StateRegime:
        print(format_state_factors(state))
        print()
    print(format_regime_comparison())
    print()

    # Minsky coefficient across regimes.
    from .coupling_base import K_BASE
    print("Minsky coefficient across state regimes:")
    for state in StateRegime:
        f_nr = _STATE_FACTORS[state][MoneyTerm.N][MoneyTerm.R]
        f_rn = _STATE_FACTORS[state][MoneyTerm.R][MoneyTerm.N]
        eff_nr = K_BASE[MoneyTerm.N][MoneyTerm.R] * f_nr
        eff_rn = K_BASE[MoneyTerm.R][MoneyTerm.N] * f_rn
        if eff_rn != 0:
            ratio = eff_nr / eff_rn
            print(f"  {state.value:>14}: {ratio:+.2f}x")
        else:
            print(f"  {state.value:>14}: undefined (rebuild coupling = 0)")
