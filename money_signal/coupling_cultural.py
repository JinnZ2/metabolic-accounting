"""
money_signal/coupling_cultural.py

Cultural factor functions for the money signal coupling matrix.

The same token in two different cultural contexts has different
coupling dynamics. A fiat dollar in a high-reciprocity kin network
couples differently than the same dollar in an atomized consumer
market. This module encodes those differences.

This is NOT the substrate of the token itself. It is the substrate
of the social network USING the token. Substrate of the token is
handled in coupling_substrate.py.

Core physical intuition:

  HIGH_RECIPROCITY networks have strong non-monetary exchange channels
  in parallel with monetary ones. When the money signal degrades, the
  reciprocity channel absorbs load. This damps the coupling from
  reliability loss to acceptance loss -- people can still transact
  even when the token is failing. Minsky asymmetry is reduced because
  collapse has an exit valve.

  COMMUNITY_TRUST networks rely on face-to-face accountability.
  Monetary coupling is moderate and slow. Reputation effects dominate
  over price signals. Network acceptance is sticky both ways -- slow
  to collapse, slow to rebuild.

  INSTITUTIONAL networks are contract-enforced. Coupling is close to
  base matrix values because the system was designed for monetary
  exchange as the primary mode. This is the default calibration case.

  ATOMIZED_MARKET networks have no parallel exchange channel. When
  the money signal degrades, there is nothing else. Coupling is
  amplified in every direction. Minsky asymmetry is magnified because
  there is no exit valve when trust collapses.

  MIXED networks have heterogeneous subpopulations. Coupling is
  intermediate. Variance across the network is high even when the
  mean coupling looks moderate.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import MoneyTerm, CulturalScope


# ============================================================================
# CULTURAL FACTOR MATRIX
# ============================================================================

# For each cultural scope, a matrix of multiplicative factors that
# modify K_ij_base after temporal factors have applied.
#
# Factor of 1.0 means base coupling applies.
# Factor > 1.0 amplifies coupling.
# Factor < 1.0 damps coupling.
#
# Factors are non-negative. Sign flips are reserved for state regime.

_CULTURAL_FACTORS: Dict[CulturalScope, Dict[MoneyTerm, Dict[MoneyTerm, float]]] = {

    # ----------------------------------------------------------------
    # HIGH_RECIPROCITY: kin/gift economies, strong obligation networks
    #
    # Parallel non-monetary exchange absorbs load when money fails.
    # Coupling from monetary distress to network acceptance is damped
    # because people keep exchanging through reciprocity channels even
    # as the token degrades. Minsky asymmetry is reduced.
    # ----------------------------------------------------------------
    CulturalScope.HIGH_RECIPROCITY: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.5,   # network weakness does not fully degrade reliability -- reciprocity backstops
            MoneyTerm.C: 0.7,   # cost pressure partially absorbed by non-monetary exchange
            MoneyTerm.L: 0.6,   # latency tolerance is higher -- people wait for each other
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.5,   # reliability loss does not collapse acceptance -- other channels carry load
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.5,
            MoneyTerm.L: 0.4,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.8,
            MoneyTerm.N: 0.7,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.7,
            MoneyTerm.N: 0.6,
            MoneyTerm.C: 0.9,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # COMMUNITY_TRUST: small-scale, face-to-face accountability
    #
    # Reputation dominates over price signals. Acceptance is sticky
    # in both directions. Coupling is moderate but slow.
    # ----------------------------------------------------------------
    CulturalScope.COMMUNITY_TRUST: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.8,   # network matters but reputation partially decouples
            MoneyTerm.C: 0.9,
            MoneyTerm.L: 0.7,   # latency matters less -- trust extends patience
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.7,   # reliability loss damped by reputation capital
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.8,
            MoneyTerm.L: 0.6,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.8,
            MoneyTerm.N: 0.7,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # INSTITUTIONAL: formal enforcement, contract-based
    #
    # This is the calibration case. Factors are all 1.0. The base
    # matrix assumes institutional coupling by default. Modern
    # fiat-in-market-economy falls here.
    # ----------------------------------------------------------------
    CulturalScope.INSTITUTIONAL: {
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
    # ATOMIZED_MARKET: transactional, low relational binding
    #
    # No parallel exchange channel. When the token fails there is
    # nothing else. Coupling is amplified everywhere. Minsky asymmetry
    # is magnified because there is no exit valve for trust collapse.
    # ----------------------------------------------------------------
    CulturalScope.ATOMIZED_MARKET: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.3,   # network loss has no backstop -- reliability hit is full
            MoneyTerm.C: 1.2,
            MoneyTerm.L: 1.2,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.5,   # reliability loss triggers full-network hoarding -- no parallel channel
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.3,
            MoneyTerm.L: 1.2,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.2,
            MoneyTerm.N: 1.2,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.1,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.2,
            MoneyTerm.N: 1.1,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # MIXED: heterogeneous network, multiple modes simultaneously
    #
    # Intermediate coupling. Mean values look moderate but variance
    # across the network is high. The mean is what this matrix
    # encodes; subpopulation analysis belongs in the distributional
    # module.
    # ----------------------------------------------------------------
    CulturalScope.MIXED: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 0.95,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.95,
            MoneyTerm.L: 0.85,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.95,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.95,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def cultural_factor(i: MoneyTerm, j: MoneyTerm, scope: CulturalScope) -> float:
    """
    Return the multiplicative cultural factor for coupling K_ij at
    the given cultural scope.

    Args:
        i: the responding term
        j: the driving term
        scope: the cultural scope of the network using the token

    Returns:
        Multiplicative factor >= 0. Applied as part of the composite
        coupling calculation in coupling.py.
    """
    return _CULTURAL_FACTORS[scope][i][j]


def iter_cultural_factors(
    scope: CulturalScope,
) -> Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...]:
    """
    Iterate over all (i, j, factor) triples at the given cultural scope.
    """
    return tuple(
        (i, j, _CULTURAL_FACTORS[scope][i][j])
        for i in MoneyTerm
        for j in MoneyTerm
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_cultural_factors() -> None:
    """
    Check structural invariants for the cultural factor tables.

    Raises AssertionError on violation.
    """
    # 1. Every cultural scope must have a full 4x4 factor matrix.
    for scope in CulturalScope:
        assert scope in _CULTURAL_FACTORS, (
            f"Missing cultural factor matrix for scope {scope.value}"
        )
        for i in MoneyTerm:
            for j in MoneyTerm:
                assert j in _CULTURAL_FACTORS[scope][i], (
                    f"Missing factor K[{i.value}][{j.value}] at cultural "
                    f"scope {scope.value}"
                )

    # 2. Self-coupling factor must be 1.0 at every scope.
    for scope in CulturalScope:
        for term in MoneyTerm:
            v = _CULTURAL_FACTORS[scope][term][term]
            assert v == 1.0, (
                f"Self-coupling factor at cultural scope {scope.value} for "
                f"{term.value} must be 1.0, got {v}"
            )

    # 3. All factors must be non-negative. Sign flips belong to state regime.
    for scope in CulturalScope:
        for i in MoneyTerm:
            for j in MoneyTerm:
                v = _CULTURAL_FACTORS[scope][i][j]
                assert v >= 0.0, (
                    f"Negative cultural factor at {scope.value} "
                    f"K[{i.value}][{j.value}] = {v}"
                )

    # 4. INSTITUTIONAL is the calibration scope. All factors must be 1.0.
    for i in MoneyTerm:
        for j in MoneyTerm:
            v = _CULTURAL_FACTORS[CulturalScope.INSTITUTIONAL][i][j]
            assert v == 1.0, (
                f"INSTITUTIONAL scope must have all factors = 1.0 "
                f"(calibration scope), got K[{i.value}][{j.value}] = {v}"
            )

    # 5. Minsky asymmetry direction must be preserved at every scope,
    #    at the COMPOSED coupling level (README claim #1). The factor
    #    matrix may reduce or amplify asymmetry relative to base, but
    #    the composed K[N][R] must not fall below composed K[R][N].
    #
    #    AUDIT_11 § B: this check was previously pointwise on factors
    #    (f_nr >= f_rn), which is strictly stronger than the README
    #    invariant and rejected COMMUNITY_TRUST, whose factors
    #    (f_nr=0.7, f_rn=0.8) are deliberately set to damp asymmetry
    #    — composed K[N][R] = 0.8 * 0.7 = 0.56 = 0.7 * 0.8 = K[R][N].
    #    The composed check matches the documented invariant exactly.
    from .coupling_base import K_BASE
    base_nr = K_BASE[MoneyTerm.N][MoneyTerm.R]
    base_rn = K_BASE[MoneyTerm.R][MoneyTerm.N]
    for scope in CulturalScope:
        f_nr = _CULTURAL_FACTORS[scope][MoneyTerm.N][MoneyTerm.R]
        f_rn = _CULTURAL_FACTORS[scope][MoneyTerm.R][MoneyTerm.N]
        composed_nr = base_nr * f_nr
        composed_rn = base_rn * f_rn
        assert composed_nr + 1e-9 >= composed_rn, (
            f"Minsky asymmetry violated at cultural scope {scope.value}: "
            f"composed K[N][R]={composed_nr:.4f} must be >= "
            f"composed K[R][N]={composed_rn:.4f} "
            f"(factors: f_nr={f_nr}, f_rn={f_rn})"
        )

    # 6. HIGH_RECIPROCITY must damp the R<->N coupling relative to
    #    INSTITUTIONAL. Reciprocity networks have parallel channels
    #    that prevent full monetary collapse from propagating to
    #    acceptance loss.
    assert _CULTURAL_FACTORS[CulturalScope.HIGH_RECIPROCITY][MoneyTerm.N][MoneyTerm.R] < 1.0, (
        "HIGH_RECIPROCITY must damp K[N][R] below 1.0 -- reciprocity backstops "
        "monetary trust collapse"
    )

    # 7. ATOMIZED_MARKET must amplify the R<->N coupling relative to
    #    INSTITUTIONAL. No parallel channel, so monetary distress
    #    propagates fully and faster.
    assert _CULTURAL_FACTORS[CulturalScope.ATOMIZED_MARKET][MoneyTerm.N][MoneyTerm.R] > 1.0, (
        "ATOMIZED_MARKET must amplify K[N][R] above 1.0 -- no parallel "
        "exchange channel means monetary distress propagates fully"
    )


# ============================================================================
# DISPLAY
# ============================================================================

def format_cultural_factors(scope: CulturalScope) -> str:
    """
    Return a human-readable string of the cultural factor matrix at
    the given scope.
    """
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>6}" for t in terms)
    lines = [
        f"Cultural factors at {scope.value}:",
        header,
        "        " + "-" * (8 * len(terms)),
    ]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            row += f"  {_CULTURAL_FACTORS[scope][i][j]:.2f}"
        lines.append(row)
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_cultural_factors()
    print("Cultural coupling factors validated.")
    print()
    for scope in CulturalScope:
        print(format_cultural_factors(scope))
        print()

    # Show how the cultural context alone changes Minsky asymmetry.
    from .coupling_base import K_BASE
    print("Minsky coefficient across cultural scopes")
    print("  (seasonal timescale, cultural factor only):")
    for scope in CulturalScope:
        f_nr = _CULTURAL_FACTORS[scope][MoneyTerm.N][MoneyTerm.R]
        f_rn = _CULTURAL_FACTORS[scope][MoneyTerm.R][MoneyTerm.N]
        eff_nr = K_BASE[MoneyTerm.N][MoneyTerm.R] * f_nr
        eff_rn = K_BASE[MoneyTerm.R][MoneyTerm.N] * f_rn
        if eff_rn != 0:
            ratio = eff_nr / eff_rn
            print(f"  {scope.value:>20}: {ratio:.2f}x")
        else:
            print(f"  {scope.value:>20}: undefined")
