"""
money_signal/coupling_substrate.py

Substrate factor functions for the money signal coupling matrix.

The physical or informational substrate of the token itself changes
coupling. A shell cannot be counterfeited at scale but can be
inflated by new discovery. A digital token cannot be inflated by
discovery but can be terminated by infrastructure collapse. Same
four terms (R, N, C, L), different coupling signatures.

This is NOT the cultural substrate of the network using the token
(see coupling_cultural.py). This is the substrate of the token
carrier itself.

Core physical intuition:

  BIOLOGICAL substrate (shells, rare organic materials): slow
  degradation, physical scarcity enforced by biology and geography.
  Latency is high because physical transport is the reversal path.
  Reliability is high because counterfeiting requires matching a
  biological process. Network acceptance is geographically bounded.
  Discovery shocks (new shell bed) are the primary reliability risk.

  METAL substrate (gold, silver, specie coinage): durable, portable,
  thermodynamically expensive to produce. Coupling is close to base
  matrix values -- this is the historical calibration substrate for
  most monetary theory. Reliability is high, latency moderate,
  counterfeiting requires energy investment comparable to legitimate
  production.

  PAPER substrate (printed fiat, bearer notes): cheap to produce,
  requires enforcement substrate to maintain value. Coupling amplifies
  because the substrate itself provides no floor -- the paper is
  nearly worthless without the enforcement attribution. Reliability
  depends entirely on the enforcement system, not on the substrate.

  DIGITAL substrate (modern fiat ledgers, crypto): near-zero marginal
  cost per token, requires infrastructure substrate (power, compute,
  network). Latency approaches zero in normal operation. Reliability
  is coupled to infrastructure continuity in a way earlier substrates
  were not. Infrastructure collapse is the primary existential risk.

  TRUST_LEDGER substrate (hawala, indigenous reciprocity networks):
  the token is the ledger entry, not a physical object. Coupling
  heavily damped because the substrate itself is the social network.
  Reversal is a relational operation, not a mechanical one. Minsky
  asymmetry is reduced because the substrate contains repair
  protocols that physical substrates lack.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import MoneyTerm, Substrate


# ============================================================================
# SUBSTRATE FACTOR MATRIX
# ============================================================================

_SUBSTRATE_FACTORS: Dict[Substrate, Dict[MoneyTerm, Dict[MoneyTerm, float]]] = {

    # ----------------------------------------------------------------
    # BIOLOGICAL: shells, rare organic materials
    #
    # Physical substrate with biological scarcity. High reliability
    # against counterfeiting. Latency is high -- physical transport
    # is the reversal path. Network acceptance is geographically
    # bounded by where the biological substrate is known and
    # recognized.
    # ----------------------------------------------------------------
    Substrate.BIOLOGICAL: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.8,
            MoneyTerm.C: 0.9,
            MoneyTerm.L: 1.1,   # latency more strongly degrades reliability for physical substrates
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.8,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.9,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # METAL: gold, silver, specie
    #
    # Calibration substrate for most monetary theory. Factors close
    # to 1.0 across the board. Durable, portable, thermodynamically
    # expensive to counterfeit.
    # ----------------------------------------------------------------
    Substrate.METAL: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # PAPER: printed fiat, bearer notes
    #
    # Substrate provides no floor. Coupling amplifies because value
    # depends entirely on enforcement attribution, not on the paper
    # itself. When attribution weakens, coupling snaps tight in all
    # directions.
    # ----------------------------------------------------------------
    Substrate.PAPER: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.1,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.2,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.1,
            MoneyTerm.N: 1.1,
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
    # DIGITAL: modern fiat ledgers, crypto
    #
    # Latency near zero in normal operation. Reliability coupled to
    # infrastructure continuity. Infrastructure collapse propagates
    # through all four terms simultaneously because the substrate
    # literally stops existing if power, compute, or network fail.
    # This is a new failure mode not present in physical substrates.
    # ----------------------------------------------------------------
    Substrate.DIGITAL: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.2,   # infrastructure is the network -- coupling tight
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.7,   # normal-op latency is low, coupling less critical
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.3,   # infrastructure outage propagates instantly to network
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 0.8,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.1,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.2,   # when latency spikes digitally, it indicates infrastructure stress
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # TRUST_LEDGER: hawala, indigenous reciprocity networks
    #
    # The token IS the ledger entry. Coupling heavily damped because
    # the substrate is the social network itself, which contains
    # repair protocols. Reversal is a relational operation. Minsky
    # asymmetry approaches parity because broken trust has named
    # repair paths in relational systems that physical substrates
    # lack.
    # ----------------------------------------------------------------
    Substrate.TRUST_LEDGER: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.6,
            MoneyTerm.C: 0.6,
            MoneyTerm.L: 0.5,   # latency is relationally flexible
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.7,   # reliability loss does not collapse network -- repair protocols exist
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.6,
            MoneyTerm.L: 0.5,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.6,
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

def substrate_factor(
    i: MoneyTerm, j: MoneyTerm, substrate: Substrate
) -> float:
    """
    Return the multiplicative substrate factor for coupling K_ij for
    the given token substrate.

    Args:
        i: the responding term
        j: the driving term
        substrate: the physical or informational substrate of the token

    Returns:
        Multiplicative factor >= 0.
    """
    return _SUBSTRATE_FACTORS[substrate][i][j]


def iter_substrate_factors(
    substrate: Substrate,
) -> Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...]:
    """
    Iterate over all (i, j, factor) triples for the given substrate.
    """
    return tuple(
        (i, j, _SUBSTRATE_FACTORS[substrate][i][j])
        for i in MoneyTerm
        for j in MoneyTerm
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_substrate_factors() -> None:
    """
    Check structural invariants for the substrate factor tables.

    Raises AssertionError on violation.
    """
    # 1. Every substrate must have a full 4x4 factor matrix.
    for substrate in Substrate:
        assert substrate in _SUBSTRATE_FACTORS, (
            f"Missing substrate factor matrix for {substrate.value}"
        )
        for i in MoneyTerm:
            for j in MoneyTerm:
                assert j in _SUBSTRATE_FACTORS[substrate][i], (
                    f"Missing factor K[{i.value}][{j.value}] "
                    f"for substrate {substrate.value}"
                )

    # 2. Self-coupling factor must be 1.0 for every substrate.
    for substrate in Substrate:
        for term in MoneyTerm:
            v = _SUBSTRATE_FACTORS[substrate][term][term]
            assert v == 1.0, (
                f"Self-coupling factor for {substrate.value} at "
                f"{term.value} must be 1.0, got {v}"
            )

    # 3. All factors must be non-negative.
    for substrate in Substrate:
        for i in MoneyTerm:
            for j in MoneyTerm:
                v = _SUBSTRATE_FACTORS[substrate][i][j]
                assert v >= 0.0, (
                    f"Negative substrate factor for {substrate.value} "
                    f"K[{i.value}][{j.value}] = {v}"
                )

    # 4. METAL is the calibration substrate for most monetary theory.
    #    Factors must be close to 1.0 (within +/- 0.15).
    for i in MoneyTerm:
        for j in MoneyTerm:
            v = _SUBSTRATE_FACTORS[Substrate.METAL][i][j]
            assert 0.85 <= v <= 1.15, (
                f"METAL substrate factor K[{i.value}][{j.value}]={v} "
                f"outside calibration range [0.85, 1.15]"
            )

    # 5. Minsky asymmetry direction preserved for every substrate.
    for substrate in Substrate:
        f_nr = _SUBSTRATE_FACTORS[substrate][MoneyTerm.N][MoneyTerm.R]
        f_rn = _SUBSTRATE_FACTORS[substrate][MoneyTerm.R][MoneyTerm.N]
        assert f_nr >= f_rn, (
            f"Minsky asymmetry violated for substrate {substrate.value}: "
            f"K[N][R] factor={f_nr} must be >= K[R][N] factor={f_rn}"
        )

    # 6. TRUST_LEDGER must damp R<->N coupling relative to METAL.
    #    Relational substrates contain repair protocols that physical
    #    substrates lack.
    assert _SUBSTRATE_FACTORS[Substrate.TRUST_LEDGER][MoneyTerm.N][MoneyTerm.R] < \
           _SUBSTRATE_FACTORS[Substrate.METAL][MoneyTerm.N][MoneyTerm.R], (
        "TRUST_LEDGER must damp K[N][R] below METAL -- "
        "relational repair protocols are the distinguishing feature"
    )

    # 7. PAPER must amplify R<->N coupling relative to METAL.
    #    Paper substrate provides no floor; coupling snaps tight when
    #    attribution weakens.
    assert _SUBSTRATE_FACTORS[Substrate.PAPER][MoneyTerm.N][MoneyTerm.R] > \
           _SUBSTRATE_FACTORS[Substrate.METAL][MoneyTerm.N][MoneyTerm.R], (
        "PAPER must amplify K[N][R] above METAL -- "
        "no substrate floor means coupling tightens when attribution weakens"
    )

    # 8. DIGITAL must show infrastructure-coupled reliability signature.
    #    K[R][N] factor must exceed K[R][N] factor for METAL -- the
    #    infrastructure-as-network coupling is the distinguishing
    #    failure mode of digital substrates.
    assert _SUBSTRATE_FACTORS[Substrate.DIGITAL][MoneyTerm.R][MoneyTerm.N] > \
           _SUBSTRATE_FACTORS[Substrate.METAL][MoneyTerm.R][MoneyTerm.N], (
        "DIGITAL must amplify K[R][N] above METAL -- "
        "infrastructure continuity is the reliability story for digital substrates"
    )


# ============================================================================
# DISPLAY
# ============================================================================

def format_substrate_factors(substrate: Substrate) -> str:
    """
    Return a human-readable string of the substrate factor matrix.
    """
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>6}" for t in terms)
    lines = [
        f"Substrate factors for {substrate.value}:",
        header,
        "        " + "-" * (8 * len(terms)),
    ]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            row += f"  {_SUBSTRATE_FACTORS[substrate][i][j]:.2f}"
        lines.append(row)
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_substrate_factors()
    print("Substrate coupling factors validated.")
    print()
    for substrate in Substrate:
        print(format_substrate_factors(substrate))
        print()

    # Show how substrate alone changes Minsky asymmetry.
    from .coupling_base import K_BASE
    print("Minsky coefficient across substrates")
    print("  (seasonal timescale, institutional culture, state-enforced attribution,")
    print("   substrate factor only):")
    for substrate in Substrate:
        f_nr = _SUBSTRATE_FACTORS[substrate][MoneyTerm.N][MoneyTerm.R]
        f_rn = _SUBSTRATE_FACTORS[substrate][MoneyTerm.R][MoneyTerm.N]
        eff_nr = K_BASE[MoneyTerm.N][MoneyTerm.R] * f_nr
        eff_rn = K_BASE[MoneyTerm.R][MoneyTerm.N] * f_rn
        if eff_rn != 0:
            ratio = eff_nr / eff_rn
            print(f"  {substrate.value:>14}: {ratio:.2f}x")
        else:
            print(f"  {substrate.value:>14}: undefined")
