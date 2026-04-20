"""
money_signal/coupling_base.py

First-principles base coupling matrix K_ij_base.

This module defines the baseline coupling between the four terms of
the money signal equation, before any scope, substrate, or state
modifiers are applied.

K_ij_base[i][j] answers the question:

  "All else equal, when term j changes, how does term i respond?"

Diagonal entries are 1.0 (self-coupling). Off-diagonals are signed
coefficients between -1.0 and +1.0.

The asymmetry of this matrix encodes Minsky-style dynamics: trust
collapses faster than it rebuilds. K[N][R] > K[R][N] because a drop
in reversal reliability triggers network-wide hoarding more strongly
than the reverse.

These base values are first-principles estimates, not empirical fits.
Historical case calibration belongs in historical_cases.py. The base
matrix is the null hypothesis about coupling structure.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import MoneyTerm


# ============================================================================
# BASE COUPLING MATRIX
# ============================================================================

# Convention: K_BASE[i][j] is the coefficient describing how a change
# in term j propagates to term i. Read it as "response of i given
# change in j."
#
# Signs:
#   + : terms move in the SAME direction (R up -> N up)
#   - : terms move in OPPOSITE directions (R up -> C down)
#
# Magnitudes (rough):
#   1.0  : self-coupling (diagonal only)
#   0.7-0.9 : strong coupling, dominant dynamics
#   0.4-0.6 : moderate coupling
#   0.1-0.3 : weak coupling
#   0.0  : no first-order coupling

K_BASE: Dict[MoneyTerm, Dict[MoneyTerm, float]] = {
    MoneyTerm.R: {
        MoneyTerm.R: 1.0,
        MoneyTerm.N: +0.7,   # fewer counterparties -> fewer reversal options
        MoneyTerm.C: -0.5,   # higher cost -> fewer people complete reversal
        MoneyTerm.L: -0.3,   # longer latency -> more timeout failures
    },
    MoneyTerm.N: {
        MoneyTerm.R: +0.8,   # reliability drop -> hoarding -> acceptance drops (reflexive, strongest)
        MoneyTerm.N: 1.0,
        MoneyTerm.C: -0.4,   # rising cost -> people stop accepting tokens they cannot cheaply reverse
        MoneyTerm.L: -0.2,   # latency alone is a weaker driver of acceptance loss
    },
    MoneyTerm.C: {
        MoneyTerm.R: -0.6,   # reliability drop -> desperate reversal -> cost spikes
        MoneyTerm.N: -0.4,   # acceptance drop -> thinner counterparty pool -> higher reversal cost
        MoneyTerm.C: 1.0,
        MoneyTerm.L: +0.5,   # longer latency often correlates with higher cost
    },
    MoneyTerm.L: {
        MoneyTerm.R: -0.4,   # reliability drop -> reversal queue backs up -> latency rises
        MoneyTerm.N: -0.3,   # acceptance drop -> more hops needed to find counterparty -> latency rises
        MoneyTerm.C: +0.3,   # cost spike drags latency up (congestion, throttling)
        MoneyTerm.L: 1.0,
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def get_base_coupling(i: MoneyTerm, j: MoneyTerm) -> float:
    """
    Return the base coupling coefficient K_ij_base.

    Args:
        i: the responding term
        j: the driving term

    Returns:
        Signed coefficient in [-1.0, +1.0]
    """
    return K_BASE[i][j]


def iter_base_coupling() -> Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...]:
    """
    Iterate over all (i, j, coefficient) triples in the base matrix.

    Useful for printing, validation, and for applying factor functions
    in coupling.py.
    """
    return tuple(
        (i, j, K_BASE[i][j])
        for i in MoneyTerm
        for j in MoneyTerm
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_base_matrix() -> None:
    """
    Check the base matrix satisfies structural invariants.

    Raises AssertionError on any violation. These checks encode the
    first-principles constraints the base matrix must satisfy.
    """
    # 1. Diagonal must be exactly 1.0 (self-coupling)
    for term in MoneyTerm:
        assert K_BASE[term][term] == 1.0, (
            f"Self-coupling K[{term.value}][{term.value}] must be 1.0, "
            f"got {K_BASE[term][term]}"
        )

    # 2. All coefficients must be in [-1.0, +1.0]
    for i in MoneyTerm:
        for j in MoneyTerm:
            v = K_BASE[i][j]
            assert -1.0 <= v <= 1.0, (
                f"Coefficient K[{i.value}][{j.value}] = {v} outside [-1, 1]"
            )

    # 3. Minsky asymmetry: N responds to R more strongly than R responds to N.
    #    Trust collapse is faster than trust rebuild.
    k_nr = K_BASE[MoneyTerm.N][MoneyTerm.R]
    k_rn = K_BASE[MoneyTerm.R][MoneyTerm.N]
    assert k_nr > k_rn, (
        f"Minsky asymmetry violated: K[N][R]={k_nr} must be > K[R][N]={k_rn}"
    )

    # 4. R and N must positively couple (same direction).
    #    Reliability and acceptance reinforce each other in both directions.
    assert K_BASE[MoneyTerm.R][MoneyTerm.N] > 0, "R<-N must be positive"
    assert K_BASE[MoneyTerm.N][MoneyTerm.R] > 0, "N<-R must be positive"

    # 5. C and L must positively couple with each other.
    #    Cost and latency co-move: congested systems are both slow and expensive.
    assert K_BASE[MoneyTerm.C][MoneyTerm.L] > 0, "C<-L must be positive"
    assert K_BASE[MoneyTerm.L][MoneyTerm.C] > 0, "L<-C must be positive"

    # 6. R and N must negatively couple with C and L.
    #    Rising cost or latency degrades reliability and acceptance.
    for driver in (MoneyTerm.C, MoneyTerm.L):
        for responder in (MoneyTerm.R, MoneyTerm.N):
            assert K_BASE[responder][driver] < 0, (
                f"K[{responder.value}][{driver.value}] must be negative, "
                f"got {K_BASE[responder][driver]}"
            )


# ============================================================================
# DISPLAY
# ============================================================================

def format_base_matrix() -> str:
    """
    Return a human-readable string of the base matrix.

    Rows = responding term i. Columns = driving term j.
    """
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>6}" for t in terms)
    lines = [header, "        " + "-" * (8 * len(terms))]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            row += f"  {K_BASE[i][j]:+.2f}"
        lines.append(row)
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    validate_base_matrix()
    print("Base coupling matrix K_ij_base:")
    print()
    print(format_base_matrix())
    print()
    print("Validation: all structural invariants hold.")
    print()
    print("Key asymmetries:")
    print(f"  K[N][R] = {K_BASE[MoneyTerm.N][MoneyTerm.R]:+.2f}  (trust collapse rate)")
    print(f"  K[R][N] = {K_BASE[MoneyTerm.R][MoneyTerm.N]:+.2f}  (trust rebuild rate)")
    print(f"  ratio   = {K_BASE[MoneyTerm.N][MoneyTerm.R] / K_BASE[MoneyTerm.R][MoneyTerm.N]:.2f}x  (Minsky coefficient)")
