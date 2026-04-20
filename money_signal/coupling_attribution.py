"""
money_signal/coupling_attribution.py

Attribution factor functions for the money signal coupling matrix.

Attribution changes behavior. Behavior changes coupling. Two tokens
with identical physical and institutional properties can have
different coupling signatures if the attributed value differs.

This is the most contested dimension in monetary theory. Economists
often deny attribution matters -- "money is money, regardless of
what people think it is." The historical and behavioral evidence
says otherwise. A gold coin believed to be divinely sanctioned
behaves differently under stress than the same metal content
believed to be pure commodity.

Core physical intuition:

  LABOR_STORED: attribution to embodied work hours. Coupling is
  moderate and substrate-bound. Reliability is calibrated against
  whether work can be re-extracted. Network acceptance is stable
  when labor markets are stable. Breaks down when labor cannot be
  priced (care work, traditional knowledge, ecological function).

  COMMODITY_BACKED: attribution to physical scarce material.
  Reliability tracks substrate availability. Latency is low because
  physical delivery is the backstop. Minsky asymmetry is damped
  because the commodity floor provides a lower bound on collapse.

  STATE_ENFORCED: attribution to sovereign enforcement power.
  Coupling is amplified because trust in the token IS trust in the
  state. Reliability collapse propagates to full system collapse.
  No floor beneath the attribution.

  NETWORK_AGREED: attribution to collective agreement protocol.
  Coupling is highly nonlinear. Healthy regime shows damped coupling
  (protocol integrity absorbs noise). Stressed regime shows amplified
  coupling (agreement itself becomes the question). The switch is
  abrupt.

  RECIPROCITY_TOKEN: attribution to relational obligation. Coupling
  is heavily damped because the token is a ledger of relationship,
  not a carrier of stored value. Reversal reliability is a social
  question, not a mechanical one. Minsky asymmetry can invert in
  small networks -- broken trust actually rebuilds through repair
  protocols that have no monetary equivalent.

  DIVINE_SANCTIONED: attribution to sacred or cosmological authority.
  Coupling is damped while the sanctification holds, amplified
  catastrophically when it does not. Historically rare today but
  not absent -- modern analogs exist in protocol worship, algorithm
  worship, and certain state cults of currency.

  SPECULATIVE_CLAIM: attribution to future price appreciation only.
  Coupling is maximally amplified in all directions. No substrate
  floor, no institutional floor, no relational floor, no sacred
  floor. Minsky asymmetry is extreme because there is nothing to
  catch the fall.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import MoneyTerm, AttributedValue


# ============================================================================
# ATTRIBUTION FACTOR MATRIX
# ============================================================================

_ATTRIBUTION_FACTORS: Dict[AttributedValue, Dict[MoneyTerm, Dict[MoneyTerm, float]]] = {

    # ----------------------------------------------------------------
    # LABOR_STORED: embodied work hours, sweat equity
    #
    # Moderate coupling. Reliability calibrated against ability to
    # re-extract stored labor. Stable under labor-market stability,
    # unstable when labor cannot be priced cleanly.
    # ----------------------------------------------------------------
    AttributedValue.LABOR_STORED: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.95,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # COMMODITY_BACKED: gold, silver, physical scarce material
    #
    # Commodity floor provides a lower bound on collapse. Reliability
    # tracks substrate availability. Minsky asymmetry damped because
    # even in full trust collapse the metal retains use-value.
    # ----------------------------------------------------------------
    AttributedValue.COMMODITY_BACKED: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.7,   # acceptance loss is partially absorbed by metal value floor
            MoneyTerm.C: 0.9,
            MoneyTerm.L: 0.8,   # physical delivery is a slow but reliable backstop
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.8,   # reliability collapse does not fully destroy acceptance -- metal still valuable
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.9,
            MoneyTerm.L: 0.7,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 0.8,
            MoneyTerm.C: 0.9,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # STATE_ENFORCED: fiat, legal tender
    #
    # Calibration case. Trust in the token IS trust in the state.
    # Base matrix assumes this attribution. No floor beneath the
    # attribution -- if state enforcement fails, nothing remains.
    # ----------------------------------------------------------------
    AttributedValue.STATE_ENFORCED: {
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
    # NETWORK_AGREED: crypto, community currency, protocol-based
    #
    # Healthy regime shows damped coupling because the protocol
    # absorbs noise. Stressed regime shows amplified coupling. The
    # regime switch itself happens in the state factor, so here we
    # encode the healthy-case damping only. The state factor will
    # amplify on top if the system is stressed or near collapse.
    # ----------------------------------------------------------------
    AttributedValue.NETWORK_AGREED: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.1,   # network agreement IS the reliability story -- coupling is tight
            MoneyTerm.C: 0.95,
            MoneyTerm.L: 1.0,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.2,   # reliability loss propagates fast through agreement protocols
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
    # RECIPROCITY_TOKEN: gift economy ledger, trust-ledger
    #
    # Token is a ledger of relationship, not a carrier of stored
    # value. Coupling heavily damped. Reversal is a social question.
    # Minsky asymmetry reduced almost to parity because repair
    # protocols exist for broken trust that monetary systems lack.
    # ----------------------------------------------------------------
    AttributedValue.RECIPROCITY_TOKEN: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.6,
            MoneyTerm.C: 0.5,   # cost is relational, not monetary -- damped heavily
            MoneyTerm.L: 0.5,   # latency is relationally flexible
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.6,   # reliability loss does not collapse network -- repair protocols exist
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.5,
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
            MoneyTerm.N: 0.6,
            MoneyTerm.C: 0.7,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # DIVINE_SANCTIONED: temple economies, sacred obligation
    #
    # Coupling damped while sanctification holds. Catastrophic
    # amplification when sanctification breaks, but that break
    # is encoded in the state factor (near-collapse regime). Here
    # we encode the sanctified-healthy case.
    #
    # Modern analogs: protocol worship, algorithm worship, certain
    # state cults of currency. Any system where questioning the
    # attribution itself is taboo.
    # ----------------------------------------------------------------
    AttributedValue.DIVINE_SANCTIONED: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.6,
            MoneyTerm.C: 0.7,
            MoneyTerm.L: 0.7,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.6,   # reliability does not propagate to acceptance -- sanctification holds network
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.7,
            MoneyTerm.L: 0.6,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.7,
            MoneyTerm.N: 0.7,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.8,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.7,
            MoneyTerm.N: 0.6,
            MoneyTerm.C: 0.8,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # SPECULATIVE_CLAIM: pure financialization, no underlying
    #
    # No substrate floor. No institutional floor. No relational
    # floor. No sacred floor. Coupling maximally amplified in all
    # directions. Minsky asymmetry extreme.
    # ----------------------------------------------------------------
    AttributedValue.SPECULATIVE_CLAIM: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.4,
            MoneyTerm.C: 1.3,
            MoneyTerm.L: 1.3,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.7,   # reliability loss triggers immediate full-network exit
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.4,
            MoneyTerm.L: 1.3,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.4,
            MoneyTerm.N: 1.3,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.2,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.3,
            MoneyTerm.N: 1.2,
            MoneyTerm.C: 1.2,
            MoneyTerm.L: 1.0,
        },
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def attribution_factor(
    i: MoneyTerm, j: MoneyTerm, attribution: AttributedValue
) -> float:
    """
    Return the multiplicative attribution factor for coupling K_ij
    for the given attributed value.

    Args:
        i: the responding term
        j: the driving term
        attribution: what the culture believes the token represents

    Returns:
        Multiplicative factor >= 0.
    """
    return _ATTRIBUTION_FACTORS[attribution][i][j]


def iter_attribution_factors(
    attribution: AttributedValue,
) -> Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...]:
    """
    Iterate over all (i, j, factor) triples for the given attribution.
    """
    return tuple(
        (i, j, _ATTRIBUTION_FACTORS[attribution][i][j])
        for i in MoneyTerm
        for j in MoneyTerm
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_attribution_factors() -> None:
    """
    Check structural invariants for the attribution factor tables.

    Raises AssertionError on violation.
    """
    # 1. Every attribution must have a full 4x4 factor matrix.
    for attribution in AttributedValue:
        assert attribution in _ATTRIBUTION_FACTORS, (
            f"Missing attribution factor matrix for {attribution.value}"
        )
        for i in MoneyTerm:
            for j in MoneyTerm:
                assert j in _ATTRIBUTION_FACTORS[attribution][i], (
                    f"Missing factor K[{i.value}][{j.value}] "
                    f"for attribution {attribution.value}"
                )

    # 2. Self-coupling factor must be 1.0 for every attribution.
    for attribution in AttributedValue:
        for term in MoneyTerm:
            v = _ATTRIBUTION_FACTORS[attribution][term][term]
            assert v == 1.0, (
                f"Self-coupling factor for {attribution.value} at "
                f"{term.value} must be 1.0, got {v}"
            )

    # 3. All factors must be non-negative.
    for attribution in AttributedValue:
        for i in MoneyTerm:
            for j in MoneyTerm:
                v = _ATTRIBUTION_FACTORS[attribution][i][j]
                assert v >= 0.0, (
                    f"Negative attribution factor for {attribution.value} "
                    f"K[{i.value}][{j.value}] = {v}"
                )

    # 4. STATE_ENFORCED is the calibration attribution. All factors = 1.0.
    for i in MoneyTerm:
        for j in MoneyTerm:
            v = _ATTRIBUTION_FACTORS[AttributedValue.STATE_ENFORCED][i][j]
            assert v == 1.0, (
                f"STATE_ENFORCED must have all factors = 1.0 "
                f"(calibration attribution), got K[{i.value}][{j.value}] = {v}"
            )

    # 5. Minsky asymmetry direction preserved for every attribution.
    for attribution in AttributedValue:
        f_nr = _ATTRIBUTION_FACTORS[attribution][MoneyTerm.N][MoneyTerm.R]
        f_rn = _ATTRIBUTION_FACTORS[attribution][MoneyTerm.R][MoneyTerm.N]
        assert f_nr >= f_rn, (
            f"Minsky asymmetry violated for {attribution.value}: "
            f"K[N][R] factor={f_nr} must be >= K[R][N] factor={f_rn}"
        )

    # 6. SPECULATIVE_CLAIM must amplify coupling relative to STATE_ENFORCED.
    #    Pure financialization has no floor to catch the fall.
    assert _ATTRIBUTION_FACTORS[AttributedValue.SPECULATIVE_CLAIM][MoneyTerm.N][MoneyTerm.R] > 1.0, (
        "SPECULATIVE_CLAIM must amplify K[N][R] above 1.0 -- "
        "no floor to catch collapse"
    )

    # 7. RECIPROCITY_TOKEN must damp coupling relative to STATE_ENFORCED.
    #    Relational ledgers have repair protocols that monetary systems lack.
    assert _ATTRIBUTION_FACTORS[AttributedValue.RECIPROCITY_TOKEN][MoneyTerm.N][MoneyTerm.R] < 1.0, (
        "RECIPROCITY_TOKEN must damp K[N][R] below 1.0 -- "
        "repair protocols exist that monetary systems lack"
    )

    # 8. COMMODITY_BACKED must damp R<->N coupling relative to STATE_ENFORCED.
    #    Metal value floor absorbs part of the collapse.
    assert _ATTRIBUTION_FACTORS[AttributedValue.COMMODITY_BACKED][MoneyTerm.N][MoneyTerm.R] < 1.0, (
        "COMMODITY_BACKED must damp K[N][R] below 1.0 -- "
        "commodity floor absorbs collapse"
    )


# ============================================================================
# DISPLAY
# ============================================================================

def format_attribution_factors(attribution: AttributedValue) -> str:
    """
    Return a human-readable string of the attribution factor matrix.
    """
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>6}" for t in terms)
    lines = [
        f"Attribution factors for {attribution.value}:",
        header,
        "        " + "-" * (8 * len(terms)),
    ]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            row += f"  {_ATTRIBUTION_FACTORS[attribution][i][j]:.2f}"
        lines.append(row)
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_attribution_factors()
    print("Attribution coupling factors validated.")
    print()
    for attribution in AttributedValue:
        print(format_attribution_factors(attribution))
        print()

    # Show how attribution alone changes Minsky asymmetry.
    from .coupling_base import K_BASE
    print("Minsky coefficient across attributions")
    print("  (seasonal timescale, institutional culture, attribution factor only):")
    for attribution in AttributedValue:
        f_nr = _ATTRIBUTION_FACTORS[attribution][MoneyTerm.N][MoneyTerm.R]
        f_rn = _ATTRIBUTION_FACTORS[attribution][MoneyTerm.R][MoneyTerm.N]
        eff_nr = K_BASE[MoneyTerm.N][MoneyTerm.R] * f_nr
        eff_rn = K_BASE[MoneyTerm.R][MoneyTerm.N] * f_rn
        if eff_rn != 0:
            ratio = eff_nr / eff_rn
            print(f"  {attribution.value:>22}: {ratio:.2f}x")
        else:
            print(f"  {attribution.value:>22}: undefined")
