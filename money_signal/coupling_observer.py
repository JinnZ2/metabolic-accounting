"""
money_signal/coupling_observer.py

Observer factor functions for the money signal coupling matrix.

Money is observer-relative. A billionaire and a paycheck-to-paycheck
worker are not measuring the same signal even when they hold nominally
identical tokens in the same system at the same moment.

Most conventional monetary modeling collapses to a single observer
(the aggregate, the central bank, "the economy"). That collapse is
itself a measurement failure. It hides the fact that the observable
quantity M(t) is a function of observer position.

This module makes observer position a first-class parameter of the
coupling equation. The distributional module downstream will use
this to compute the asymmetry between observer positions for the
same system state.

Core physical intuition:

  Different observers experience different coupling because they
  are in different parts of the flow network. Reversal reliability
  R for a token issuer is nearly 1.0 by definition -- they can
  always redeem their own token. R for a paycheck-to-paycheck
  worker is much lower because they face the cost and latency
  tail, not the mean.

  The observer factor does NOT change the underlying system. It
  changes what the observer MEASURES about the system. Two
  observers looking at the same monetary system at the same moment
  will compute different M(t) values -- and both are correct for
  their position. The system itself is the union of all observer
  experiences.

  This framing makes distributional analysis structural rather than
  tacked-on. The system is not "healthy on average with some
  distributional concerns." The system is healthy for some
  observers and collapsing for others, simultaneously, and both
  states are real.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import MoneyTerm, ObserverPosition


# ============================================================================
# OBSERVER FACTOR MATRIX
# ============================================================================

# Factor > 1.0: this observer experiences AMPLIFIED coupling -- small
#               system changes produce larger shifts in their M(t)
# Factor < 1.0: this observer experiences DAMPED coupling -- they are
#               insulated from system changes
# Factor = 1.0: this observer experiences the system-average coupling
#
# The institutional/aggregate observer is the calibration case.
# Almost no actual human occupies this position. It is a modeling
# fiction, useful only as a reference point against which real
# observer positions can be compared.

_OBSERVER_FACTORS: Dict[ObserverPosition, Dict[MoneyTerm, Dict[MoneyTerm, float]]] = {

    # ----------------------------------------------------------------
    # SUBSTRATE_PRODUCER: makes the physical goods
    #
    # Experiences the R-N coupling strongly because their livelihood
    # depends on being able to reverse tokens back into resources.
    # Latency and cost hit them asymmetrically -- they front the
    # substrate cost before the token clears. Higher coupling in
    # the reliability-cost direction.
    # ----------------------------------------------------------------
    ObserverPosition.SUBSTRATE_PRODUCER: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.1,
            MoneyTerm.C: 1.3,   # cost of reversal hits producers hard -- thin margins
            MoneyTerm.L: 1.4,   # latency is a cash-flow killer for producers
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.2,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 1.2,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.2,
            MoneyTerm.N: 1.1,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.2,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.3,
            MoneyTerm.N: 1.1,
            MoneyTerm.C: 1.2,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # SUBSTRATE_CONSUMER: uses the physical goods
    #
    # Experiences coupling mainly through price -- the cost they pay
    # for substrate is where the money signal reaches them. Less
    # exposed to latency and reversal reliability because they are
    # usually on the demand side, not the liquidity side.
    # ----------------------------------------------------------------
    ObserverPosition.SUBSTRATE_CONSUMER: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.9,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 0.9,
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 0.8,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
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
    # TOKEN_HOLDER_DEEP: deep reserves, long time horizon
    #
    # Damped coupling in every direction. They can wait out latency,
    # absorb cost spikes, ride through reliability dips. Reversal
    # reliability for them approaches the upper bound -- they reverse
    # from the top of the queue, not the tail.
    #
    # This is the observer position that most economic aggregates
    # implicitly privilege, because the aggregate-observer model
    # averages across holdings and the deep holders dominate the
    # stock-weighted average.
    # ----------------------------------------------------------------
    ObserverPosition.TOKEN_HOLDER_DEEP: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.5,
            MoneyTerm.C: 0.4,   # cost spikes absorbed by reserves
            MoneyTerm.L: 0.3,   # latency is survivable with runway
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.5,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.4,
            MoneyTerm.L: 0.3,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.5,
            MoneyTerm.N: 0.5,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.5,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.5,
            MoneyTerm.N: 0.4,
            MoneyTerm.C: 0.5,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # TOKEN_HOLDER_THIN: paycheck-to-paycheck, short time horizon
    #
    # Amplified coupling in every direction. They cannot wait out
    # latency, cannot absorb cost spikes, cannot ride through
    # reliability dips. Reversal reliability for them is the tail
    # of the distribution, not the mean. They experience the system
    # as much more fragile than aggregate metrics suggest.
    #
    # The asymmetry between this observer and TOKEN_HOLDER_DEEP is
    # the core distributional signal the framework is built to make
    # visible.
    # ----------------------------------------------------------------
    ObserverPosition.TOKEN_HOLDER_THIN: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.4,
            MoneyTerm.C: 1.6,   # every cost spike is catastrophic -- no buffer
            MoneyTerm.L: 1.7,   # every latency delay is a missed rent payment
        },
        MoneyTerm.N: {
            MoneyTerm.R: 1.6,   # reliability loss triggers immediate survival response
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.5,
            MoneyTerm.L: 1.4,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.4,
            MoneyTerm.N: 1.3,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.4,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.5,
            MoneyTerm.N: 1.3,
            MoneyTerm.C: 1.4,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # TOKEN_ISSUER: state, central bank, protocol
    #
    # Reversal reliability approaches 1.0 by definition -- issuers
    # can always redeem their own token. They experience near-zero
    # coupling from the reliability side because they cannot be
    # on the losing end of reversal. Coupling from the network
    # side exists but is damped because they can influence network
    # acceptance through policy or protocol change.
    #
    # This observer position is the one most likely to mistake its
    # local coupling experience for the system-wide coupling. Central
    # banks looking at their own view of the system see a much
    # smoother, more manageable system than token holders do.
    # ----------------------------------------------------------------
    ObserverPosition.TOKEN_ISSUER: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.3,   # issuers are insulated from network shifts -- they set acceptance rules
            MoneyTerm.C: 0.2,   # issuers do not bear reversal cost
            MoneyTerm.L: 0.2,   # issuers do not face reversal latency
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.4,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 0.4,
            MoneyTerm.L: 0.4,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 0.3,
            MoneyTerm.N: 0.4,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 0.5,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 0.3,
            MoneyTerm.N: 0.4,
            MoneyTerm.C: 0.5,
            MoneyTerm.L: 1.0,
        },
    },

    # ----------------------------------------------------------------
    # TOKEN_INTERMEDIARY: banks, exchanges, clearinghouses
    #
    # Coupling is amplified in the cost-latency corner because
    # intermediaries profit from the spread, and spread depends on
    # C and L. Damped in the reliability direction because they have
    # privileged access to issuer backstops. Near-collapse regimes
    # invert this -- intermediaries become the fulcrum of cascade
    # failure. That inversion is handled in state regime, not here.
    # ----------------------------------------------------------------
    ObserverPosition.TOKEN_INTERMEDIARY: {
        MoneyTerm.R: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 0.8,
            MoneyTerm.C: 1.2,   # intermediary revenue depends on cost spreads
            MoneyTerm.L: 1.2,   # intermediary revenue depends on latency arbitrage
        },
        MoneyTerm.N: {
            MoneyTerm.R: 0.9,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.1,
            MoneyTerm.L: 1.1,
        },
        MoneyTerm.C: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.0,
            MoneyTerm.L: 1.3,
        },
        MoneyTerm.L: {
            MoneyTerm.R: 1.0,
            MoneyTerm.N: 1.0,
            MoneyTerm.C: 1.3,
            MoneyTerm.L: 1.0,
        },
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def observer_factor(
    i: MoneyTerm, j: MoneyTerm, observer: ObserverPosition
) -> float:
    """
    Return the multiplicative observer factor for coupling K_ij for
    the given observer position.

    Args:
        i: the responding term
        j: the driving term
        observer: whose measurement of M(t) is being computed

    Returns:
        Multiplicative factor >= 0.
    """
    return _OBSERVER_FACTORS[observer][i][j]


def iter_observer_factors(
    observer: ObserverPosition,
) -> Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...]:
    """
    Iterate over all (i, j, factor) triples for the given observer.
    """
    return tuple(
        (i, j, _OBSERVER_FACTORS[observer][i][j])
        for i in MoneyTerm
        for j in MoneyTerm
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_observer_factors() -> None:
    """
    Check structural invariants for the observer factor tables.

    Raises AssertionError on violation.
    """
    # 1. Every observer position must have a full 4x4 factor matrix.
    for observer in ObserverPosition:
        assert observer in _OBSERVER_FACTORS, (
            f"Missing observer factor matrix for {observer.value}"
        )
        for i in MoneyTerm:
            for j in MoneyTerm:
                assert j in _OBSERVER_FACTORS[observer][i], (
                    f"Missing factor K[{i.value}][{j.value}] "
                    f"for observer {observer.value}"
                )

    # 2. Self-coupling factor must be 1.0 for every observer.
    for observer in ObserverPosition:
        for term in MoneyTerm:
            v = _OBSERVER_FACTORS[observer][term][term]
            assert v == 1.0, (
                f"Self-coupling factor for {observer.value} at "
                f"{term.value} must be 1.0, got {v}"
            )

    # 3. All factors must be non-negative.
    for observer in ObserverPosition:
        for i in MoneyTerm:
            for j in MoneyTerm:
                v = _OBSERVER_FACTORS[observer][i][j]
                assert v >= 0.0, (
                    f"Negative observer factor for {observer.value} "
                    f"K[{i.value}][{j.value}] = {v}"
                )

    # 4. Distributional asymmetry invariant: TOKEN_HOLDER_THIN must
    #    experience amplified coupling relative to TOKEN_HOLDER_DEEP
    #    for the reliability-cost and reliability-latency couplings.
    #    This is the core distributional signal.
    thin = _OBSERVER_FACTORS[ObserverPosition.TOKEN_HOLDER_THIN]
    deep = _OBSERVER_FACTORS[ObserverPosition.TOKEN_HOLDER_DEEP]
    for (i, j) in [
        (MoneyTerm.R, MoneyTerm.C),
        (MoneyTerm.R, MoneyTerm.L),
        (MoneyTerm.N, MoneyTerm.R),
    ]:
        assert thin[i][j] > deep[i][j], (
            f"Distributional asymmetry violated: thin holder factor "
            f"K[{i.value}][{j.value}]={thin[i][j]} must exceed deep "
            f"holder factor {deep[i][j]}"
        )

    # 5. Issuer insulation invariant: TOKEN_ISSUER must have damped
    #    coupling relative to TOKEN_HOLDER_THIN for all cost and
    #    latency driving terms. Issuers do not bear reversal cost
    #    the way thin holders do.
    issuer = _OBSERVER_FACTORS[ObserverPosition.TOKEN_ISSUER]
    for i in MoneyTerm:
        for j in (MoneyTerm.C, MoneyTerm.L):
            if i == j:
                continue
            assert issuer[i][j] < thin[i][j], (
                f"Issuer insulation violated: issuer factor "
                f"K[{i.value}][{j.value}]={issuer[i][j]} must be less than "
                f"thin holder factor {thin[i][j]}"
            )

    # 6. Minsky asymmetry direction preserved for every observer.
    #    Even the most insulated observer sees trust collapse faster
    #    than rebuild within their own view of the system.
    for observer in ObserverPosition:
        f_nr = _OBSERVER_FACTORS[observer][MoneyTerm.N][MoneyTerm.R]
        f_rn = _OBSERVER_FACTORS[observer][MoneyTerm.R][MoneyTerm.N]
        assert f_nr >= f_rn, (
            f"Minsky asymmetry violated for observer {observer.value}: "
            f"K[N][R] factor={f_nr} must be >= K[R][N] factor={f_rn}"
        )


# ============================================================================
# DISPLAY
# ============================================================================

def format_observer_factors(observer: ObserverPosition) -> str:
    """
    Return a human-readable string of the observer factor matrix.
    """
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>6}" for t in terms)
    lines = [
        f"Observer factors for {observer.value}:",
        header,
        "        " + "-" * (8 * len(terms)),
    ]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            row += f"  {_OBSERVER_FACTORS[observer][i][j]:.2f}"
        lines.append(row)
    return "\n".join(lines)


def format_distributional_asymmetry() -> str:
    """
    Return a summary of the core distributional asymmetry between
    TOKEN_HOLDER_THIN and TOKEN_HOLDER_DEEP.

    This asymmetry ratio is the primary distributional signal the
    framework makes visible.
    """
    thin = _OBSERVER_FACTORS[ObserverPosition.TOKEN_HOLDER_THIN]
    deep = _OBSERVER_FACTORS[ObserverPosition.TOKEN_HOLDER_DEEP]
    lines = [
        "Distributional asymmetry (thin holder / deep holder):",
        "  (how much more exposed thin holders are to each coupling)",
    ]
    for i in MoneyTerm:
        for j in MoneyTerm:
            if i == j:
                continue
            if deep[i][j] == 0:
                continue
            ratio = thin[i][j] / deep[i][j]
            lines.append(
                f"  K[{i.name}][{j.name}]: thin/deep = {ratio:.2f}x"
            )
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_observer_factors()
    print("Observer coupling factors validated.")
    print()
    for observer in ObserverPosition:
        print(format_observer_factors(observer))
        print()

    print(format_distributional_asymmetry())
