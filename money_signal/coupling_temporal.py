"""
money_signal/coupling_temporal.py

Temporal factor functions for the money signal coupling matrix.

At different time horizons, coupling coefficients shift. The same
monetary system has different dynamics when evaluated at transaction
scope versus generational scope.

Core physical intuition:

  At TRANSACTION scope, only fast terms matter. Latency and cost
  dominate. Reliability and network acceptance look stable because
  they move slowly.

  At SEASONAL scope, all four terms have comparable timescales and
  full coupling is visible.

  At GENERATIONAL scope, slow terms dominate. Substrate and
  institutional decay matter. Transaction-level metrics become noise
  against the longer trend.

  At EPOCHAL scope, the attributed value of the token itself can
  shift. What was "money" in one epoch becomes commodity or artifact
  in another. Coupling becomes dominated by substrate survival.

Scope mismatch is the core failure mode in monetary modeling. A
coupling coefficient correctly calibrated at one temporal scope will
mislead at another. This module makes that explicit.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import MoneyTerm, TemporalScope


# ============================================================================
# TEMPORAL FACTOR MATRIX
# ============================================================================

# For each temporal scope, a matrix of multiplicative factors that
# modify K_ij_base. A factor of 1.0 means the base coupling applies
# unchanged at this scope. A factor > 1.0 amplifies the base coupling.
# A factor < 1.0 damps it. A factor of 0.0 means this coupling is
# invisible at this scope.
#
# The matrices are structured so that row = responding term i,
# column = driving term j, matching K_BASE.

_TEMPORAL_FACTORS: Dict[TemporalScope, Dict[MoneyTerm, Dict[MoneyTerm, float]]] = {

    # ----------------------------------------------------------------
    # TRANSACTION scope: seconds to days
    #
    # Fast terms (C, L) dominate. Slow terms (R, N) look approximately
    # constant, so their coupling to other terms is damped.
    # ----------------------------------------------------------------
    TemporalScope.TRANSACTION: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.3,   # network drift invisible at this scope
            MoneyTerm.C: 0.6,   # cost spikes are visible but reliability response lags
            MoneyTerm.L: 0.8,   # latency failures are the dominant reliability hit
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.3,   # reliability shifts do not propagate to acceptance in one transaction
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.5,   # cost matters but acceptance lags
            MoneyTerm.L: 0.3,   # latency rarely flips acceptance in a single transaction
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.4,   # reliability effects on cost lag
            MoneyTerm.N: 0.2,   # acceptance effects on cost are slow
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.2,   # latency and cost very tightly coupled at transaction scope
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.4,   # reliability effects on latency lag
            MoneyTerm.N: 0.2,   # acceptance effects on latency are slow
            MoneyTerm.C: 1.2,   # cost and latency very tightly coupled at transaction scope
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # SEASONAL scope: weeks to ~1 year
    #
    # Base coupling applies approximately as-is. All four terms move
    # on comparable timescales. This is the scope the base matrix was
    # calibrated for.
    # ----------------------------------------------------------------
    TemporalScope.SEASONAL: {
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
    # GENERATIONAL scope: ~20-30 years
    #
    # Slow terms (R, N) dominate. Transaction-level cost and latency
    # fluctuations average out. Institutional decay and trust erosion
    # become visible. Minsky asymmetry amplifies because rebuild is
    # slower over long horizons.
    # ----------------------------------------------------------------
    TemporalScope.GENERATIONAL: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.3,   # network erosion over decades degrades reliability
            MoneyTerm.C: 0.7,   # short-term cost noise damps out
            MoneyTerm.L: 0.5,   # latency noise damps out
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.5,   # multi-decade reliability trends drive acceptance strongly
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.6,   # cost noise damps
            MoneyTerm.L: 0.3,   # latency noise damps almost entirely
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.2,   # reliability trend drives long-term cost structure
            MoneyTerm.N: 1.1,   # acceptance trend affects long-term cost
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.8,   # latency-cost coupling weaker over decades
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 0.8,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # EPOCHAL scope: centuries
    #
    # The attributed value of the token itself can shift. Substrate
    # survival dominates. Networks using the token may not exist at
    # start and end of the window. Coupling becomes dominated by
    # whether the token persists as a carrier at all.
    # ----------------------------------------------------------------
    TemporalScope.EPOCHAL: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.6,   # network continuity over centuries is the reliability story
            MoneyTerm.C: 0.3,   # cost fluctuations are noise at this scope
            MoneyTerm.L: 0.2,   # latency fluctuations are noise at this scope
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.8,   # reliability over centuries is the acceptance story
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.3,
            MoneyTerm.L: 0.1,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.4,
            MoneyTerm.N: 1.3,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.5,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.2,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.5,
            MoneyTerm.L: 1.0,
        },
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def temporal_factor(i: MoneyTerm, j: MoneyTerm, scope: TemporalScope) -> float:
    """
    Return the multiplicative temporal factor for coupling K_ij at the
    given temporal scope.

    Args:
        i: the responding term
        j: the driving term
        scope: the temporal evaluation scope

    Returns:
        Multiplicative factor >= 0. Applied as K_ij(scope) = K_ij_base * factor.
    """
    return _TEMPORAL_FACTORS[scope][i][j]


def iter_temporal_factors(
    scope: TemporalScope,
) -> Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...]:
    """
    Iterate over all (i, j, factor) triples at the given temporal scope.
    """
    return tuple(
        (i, j, _TEMPORAL_FACTORS[scope][i][j])
        for i in MoneyTerm
        for j in MoneyTerm
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_temporal_factors() -> None:
    """
    Check structural invariants for the temporal factor tables.

    Raises AssertionError on violation.
    """
    # 1. Every temporal scope must have a full 4x4 factor matrix.
    for scope in TemporalScope:
        assert scope in _TEMPORAL_FACTORS, (
            f"Missing temporal factor matrix for scope {scope.value}"
        )
        for i in MoneyTerm:
            for j in MoneyTerm:
                assert j in _TEMPORAL_FACTORS[scope][i], (
                    f"Missing factor K[{i.value}][{j.value}] at scope {scope.value}"
                )

    # 2. Self-coupling factor must be 1.0 at every scope.
    #    Diagonal does not scale with scope; the base value IS the self-term.
    for scope in TemporalScope:
        for term in MoneyTerm:
            v = _TEMPORAL_FACTORS[scope][term][term]
            assert v == 1.0, (
                f"Self-coupling factor at {scope.value} for {term.value} "
                f"must be 1.0, got {v}"
            )

    # 3. All factors must be non-negative.
    #    A factor cannot flip the sign of the base coupling. Sign changes
    #    belong to the state regime factor (near-collapse), not temporal scope.
    for scope in TemporalScope:
        for i in MoneyTerm:
            for j in MoneyTerm:
                v = _TEMPORAL_FACTORS[scope][i][j]
                assert v >= 0.0, (
                    f"Negative temporal factor at {scope.value} "
                    f"K[{i.value}][{j.value}] = {v}"
                )

    # 4. SEASONAL is the calibration scope. All factors must be exactly 1.0.
    for i in MoneyTerm:
        for j in MoneyTerm:
            v = _TEMPORAL_FACTORS[TemporalScope.SEASONAL][i][j]
            assert v == 1.0, (
                f"SEASONAL scope must have all factors = 1.0 "
                f"(calibration scope), got K[{i.value}][{j.value}] = {v}"
            )

    # 5. Minsky asymmetry must hold or amplify at every scope.
    #    The ratio K[N][R] / K[R][N] (post-factor) should not drop below 1.0.
    #    Trust never rebuilds faster than it collapses at any scope.
    for scope in TemporalScope:
        f_nr = _TEMPORAL_FACTORS[scope][MoneyTerm.N][MoneyTerm.R]
        f_rn = _TEMPORAL_FACTORS[scope][MoneyTerm.R][MoneyTerm.N]
        # Only check when both are nonzero; at TRANSACTION scope both
        # are heavily damped but the asymmetry direction is preserved.
        if f_nr > 0 and f_rn > 0:
            assert f_nr >= f_rn, (
                f"Minsky asymmetry violated at {scope.value}: "
                f"temporal factor K[N][R]={f_nr} must be >= K[R][N]={f_rn}"
            )


# ============================================================================
# DISPLAY
# ============================================================================

def format_temporal_factors(scope: TemporalScope) -> str:
    """
    Return a human-readable string of the temporal factor matrix at
    the given scope.
    """
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>6}" for t in terms)
    lines = [
        f"Temporal factors at {scope.value}:",
        header,
        "        " + "-" * (8 * len(terms)),
    ]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            row += f"  {_TEMPORAL_FACTORS[scope][i][j]:.2f}"
        lines.append(row)
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_temporal_factors()
    print("Temporal coupling factors validated.")
    print()
    for scope in TemporalScope:
        print(format_temporal_factors(scope))
        print()

    # Show how Minsky coefficient evolves across temporal scopes.
    from .coupling_base import K_BASE
    print("Minsky coefficient across temporal scopes:")
    print("  (ratio of effective K[N][R] to effective K[R][N])")
    for scope in TemporalScope:
        f_nr = _TEMPORAL_FACTORS[scope][MoneyTerm.N][MoneyTerm.R]
        f_rn = _TEMPORAL_FACTORS[scope][MoneyTerm.R][MoneyTerm.N]
        eff_nr = K_BASE[MoneyTerm.N][MoneyTerm.R] * f_nr
        eff_rn = K_BASE[MoneyTerm.R][MoneyTerm.N] * f_rn
        if eff_rn != 0:
            ratio = eff_nr / eff_rn
            print(f"  {scope.value:>14}: {ratio:.2f}x")
        else:
            print(f"  {scope.value:>14}: undefined (rebuild coupling = 0)")
