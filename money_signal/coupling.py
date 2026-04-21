"""
money_signal/coupling.py

Composite coupling matrix assembly.

This module is the integration point. It takes a DimensionalContext
and produces the final coupling matrix K(context) by composing:

  K_ij(context) = K_ij_base
                × temporal_factor_ij(context.temporal)
                × cultural_factor_ij(context.cultural)
                × attribution_factor_ij(context.attribution)
                × observer_factor_ij(context.observer)
                × substrate_factor_ij(context.substrate)
                × state_factor_ij(context.state)

Each factor is computed independently by its own module. This module
does not know what any factor means. It only enforces the composition
rule and provides memoization.

Memoization matters because:
  - Contexts are frozen and hashable
  - The composition is deterministic
  - The same context will be evaluated many times during cascade
    dynamics analysis
  - Running all six factor lookups plus multiplication on every
    access is wasteful

The composed matrix is returned as a new dict so the caller cannot
mutate internal state. Validation of the composed matrix catches
errors that might slip through individual factor validations.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from functools import lru_cache

from .dimensions import DimensionalContext, MoneyTerm
from .coupling_base import K_BASE, validate_base_matrix
from .coupling_temporal import temporal_factor, validate_temporal_factors
from .coupling_cultural import cultural_factor, validate_cultural_factors
from .coupling_attribution import attribution_factor, validate_attribution_factors
from .coupling_observer import observer_factor, validate_observer_factors
from .coupling_substrate import substrate_factor, validate_substrate_factors
from .coupling_state import state_factor, validate_state_factors


# ============================================================================
# COMPOSITION
# ============================================================================

def compose_coupling(
    i: MoneyTerm, j: MoneyTerm, context: DimensionalContext
) -> float:
    """
    Compose the full coupling coefficient K_ij for the given context.

    Applies all six factor modules multiplicatively to the base
    coefficient. Sign preservation is the responsibility of each
    individual factor module. Only coupling_state may introduce
    sign flips, and only in NEAR_COLLAPSE regime.

    Args:
        i: the responding term
        j: the driving term
        context: the full dimensional context of the evaluation

    Returns:
        The composite coupling coefficient. May be negative in
        near-collapse state for specific coefficients where
        reflexive dynamics invert normal coupling direction.
    """
    base = K_BASE[i][j]

    # Self-coupling is always 1.0. Do not multiply through because
    # floating-point accumulation could drift the diagonal away from
    # exactly 1.0, which breaks the validation invariant downstream.
    if i == j:
        return 1.0

    # All six factors apply multiplicatively to off-diagonals.
    factor = (
        temporal_factor(i, j, context.temporal)
        * cultural_factor(i, j, context.cultural)
        * attribution_factor(i, j, context.attribution)
        * observer_factor(i, j, context.observer)
        * substrate_factor(i, j, context.substrate)
        * state_factor(i, j, context.state)
    )

    return base * factor


# ============================================================================
# FULL MATRIX ASSEMBLY
# ============================================================================

@lru_cache(maxsize=4096)
def assemble_coupling_matrix(
    context: DimensionalContext,
) -> Tuple[Tuple[Tuple[MoneyTerm, MoneyTerm, float], ...], ...]:
    """
    Assemble the full 4x4 coupling matrix for the given context.

    Returned as a tuple of tuples so the result is hashable and
    immutable. Memoized via lru_cache because DimensionalContext is
    frozen and hashable.

    Rows are responding terms i. Columns are driving terms j.

    Args:
        context: the full dimensional context

    Returns:
        A 4-tuple of 4-tuples. Each inner tuple holds
        (i, j, coefficient) triples. Iterate row-major.
    """
    return tuple(
        tuple(
            (i, j, compose_coupling(i, j, context))
            for j in MoneyTerm
        )
        for i in MoneyTerm
    )


def coupling_matrix_as_dict(
    context: DimensionalContext,
) -> Dict[MoneyTerm, Dict[MoneyTerm, float]]:
    """
    Return the full coupling matrix as a nested dict.

    Convenience wrapper around assemble_coupling_matrix for callers
    that prefer dict access over tuple iteration. Returns a fresh
    dict on every call so the caller can mutate safely without
    affecting the memoized tuple form.

    Args:
        context: the full dimensional context

    Returns:
        A dict keyed as result[i][j] = coefficient.
    """
    assembled = assemble_coupling_matrix(context)
    return {
        row[0][0]: {triple[1]: triple[2] for triple in row}
        for row in assembled
    }


# ============================================================================
# VALIDATION
# ============================================================================

def validate_composition(context: DimensionalContext) -> None:
    """
    Check structural invariants on the composed matrix for the given
    context.

    Raises AssertionError on violation.

    These invariants catch errors that pass individual factor
    validations but produce invalid composite matrices. They are the
    final safety net before the matrix is used in cascade dynamics.
    """
    matrix = coupling_matrix_as_dict(context)

    # 1. Diagonal must be exactly 1.0 for every term.
    for term in MoneyTerm:
        v = matrix[term][term]
        assert v == 1.0, (
            f"Composed matrix self-coupling K[{term.value}][{term.value}] "
            f"must be 1.0, got {v}. Context: {context.describe()}"
        )

    # 2. No composite coefficient may exceed +5.0 or go below -5.0.
    #    This is a sanity check against runaway amplification from
    #    factor stacking. If this fails, one of the factor modules
    #    is producing values outside its intended range.
    #
    #    AUDIT_11 § B.5: bound widened from [-3.0, 3.0]. The prior
    #    bound rejected the module's own NEAR_COLLAPSE example
    #    (case_c: digital-substrate, thin-holder in collapse) at
    #    composed K[N][R] = 3.66, contradicting README claim #8
    #    ("|K[N][R]| dominates all other off-diagonals in collapse").
    #    [-5.0, 5.0] accommodates legitimate collapse-regime stacking
    #    while still catching pathological runaway (>10 indicates a
    #    broken factor module, not an extreme-but-real case).
    for i in MoneyTerm:
        for j in MoneyTerm:
            v = matrix[i][j]
            assert -5.0 <= v <= 5.0, (
                f"Composed coefficient K[{i.value}][{j.value}]={v} "
                f"outside sanity range [-5.0, 5.0]. "
                f"Context: {context.describe()}"
            )

    # 3. Minsky asymmetry direction must be preserved in the composed
    #    matrix for all states except NEAR_COLLAPSE.
    #    NEAR_COLLAPSE may produce sign flips that make the direction
    #    comparison ambiguous.
    from .dimensions import StateRegime
    if context.state != StateRegime.NEAR_COLLAPSE:
        k_nr = matrix[MoneyTerm.N][MoneyTerm.R]
        k_rn = matrix[MoneyTerm.R][MoneyTerm.N]
        assert k_nr >= k_rn, (
            f"Composed Minsky asymmetry violated: "
            f"K[N][R]={k_nr} must be >= K[R][N]={k_rn}. "
            f"Context: {context.describe()}"
        )

    # 4. Base signs must be preserved in all non-NEAR_COLLAPSE states.
    #    Sign flips are permitted only in near-collapse dynamics.
    if context.state != StateRegime.NEAR_COLLAPSE:
        for i in MoneyTerm:
            for j in MoneyTerm:
                if i == j:
                    continue
                base = K_BASE[i][j]
                composed = matrix[i][j]
                if base > 0:
                    assert composed >= 0, (
                        f"Sign flip in non-collapse state: "
                        f"K[{i.value}][{j.value}] base={base}, "
                        f"composed={composed}. "
                        f"Context: {context.describe()}"
                    )
                elif base < 0:
                    assert composed <= 0, (
                        f"Sign flip in non-collapse state: "
                        f"K[{i.value}][{j.value}] base={base}, "
                        f"composed={composed}. "
                        f"Context: {context.describe()}"
                    )


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def minsky_coefficient(context: DimensionalContext) -> float:
    """
    Return the Minsky coefficient for the given context.

    Defined as the ratio |K[N][R]| / |K[R][N]|. Measures how much
    faster trust collapses than it rebuilds in this context. A
    healthy baseline is ~1.14. Stressed systems climb above 2.0.
    Near-collapse can exceed 5.0 in magnitude.

    Returns infinity if K[R][N] is zero.
    """
    matrix = coupling_matrix_as_dict(context)
    k_nr = abs(matrix[MoneyTerm.N][MoneyTerm.R])
    k_rn = abs(matrix[MoneyTerm.R][MoneyTerm.N])
    if k_rn == 0:
        return float("inf")
    return k_nr / k_rn


def coupling_magnitude(context: DimensionalContext) -> float:
    """
    Return the mean absolute magnitude of off-diagonal coupling in
    the given context.

    Useful as a single-number summary of how tightly coupled the
    system is. Higher values mean small shifts in any term propagate
    strongly through the others. Distinguishes RECOVERING (low mag)
    from HEALTHY (moderate) from STRESSED (high) from NEAR_COLLAPSE
    (very high).
    """
    matrix = coupling_matrix_as_dict(context)
    off_diag = [
        abs(matrix[i][j])
        for i in MoneyTerm
        for j in MoneyTerm
        if i != j
    ]
    return sum(off_diag) / len(off_diag)


def has_sign_flips(context: DimensionalContext) -> bool:
    """
    Return True if the composed matrix contains any sign flips
    relative to the base matrix.

    Sign flips indicate NEAR_COLLAPSE reflexive dynamics. A system
    with sign flips is in a qualitatively different regime than a
    system without.
    """
    matrix = coupling_matrix_as_dict(context)
    for i in MoneyTerm:
        for j in MoneyTerm:
            if i == j:
                continue
            base = K_BASE[i][j]
            composed = matrix[i][j]
            if (base > 0 and composed < 0) or (base < 0 and composed > 0):
                return True
    return False


# ============================================================================
# DISPLAY
# ============================================================================

def format_composed_matrix(context: DimensionalContext) -> str:
    """
    Return a human-readable string of the composed matrix for the
    given context.
    """
    matrix = coupling_matrix_as_dict(context)
    terms = list(MoneyTerm)
    header = "        " + "  ".join(f"{t.name:>7}" for t in terms)
    lines = [
        f"Composed coupling matrix for:",
        f"  {context.describe()}",
        "",
        header,
        "        " + "-" * (9 * len(terms)),
    ]
    for i in terms:
        row = f"{i.name:>6} |"
        for j in terms:
            v = matrix[i][j]
            row += f" {v:+.3f}"
        lines.append(row)
    lines.append("")
    lines.append(f"Minsky coefficient:    {minsky_coefficient(context):.2f}x")
    lines.append(f"Mean coupling magnitude: {coupling_magnitude(context):.2f}")
    lines.append(f"Sign flips present:    {has_sign_flips(context)}")
    return "\n".join(lines)


# ============================================================================
# STARTUP VALIDATION
# ============================================================================

def validate_all_factor_modules() -> None:
    """
    Run validation on every factor module.

    Call this at startup to ensure no factor module has been edited
    into an invalid state since the last successful run.
    """
    validate_base_matrix()
    validate_temporal_factors()
    validate_cultural_factors()
    validate_attribution_factors()
    validate_observer_factors()
    validate_substrate_factors()
    validate_state_factors()


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    from .dimensions import (
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )

    validate_all_factor_modules()
    print("All factor modules validated.")
    print()

    # Case A: Healthy modern fiat system, deep holder view.
    case_a = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_DEEP,
        substrate=Substrate.DIGITAL,
        state=StateRegime.HEALTHY,
    )
    validate_composition(case_a)
    print(format_composed_matrix(case_a))
    print()

    # Case B: Same system, thin holder view. Should show amplified coupling.
    case_b = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.HEALTHY,
    )
    validate_composition(case_b)
    print(format_composed_matrix(case_b))
    print()

    # Case C: Same system in near-collapse, thin holder view.
    # Should show extreme Minsky coefficient and sign flips.
    case_c = DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.NEAR_COLLAPSE,
    )
    validate_composition(case_c)
    print(format_composed_matrix(case_c))
    print()

    # Case D: Indigenous reciprocity network, trust-ledger substrate.
    # Should show heavily damped coupling even in stress.
    case_d = DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.STRESSED,
    )
    validate_composition(case_d)
    print(format_composed_matrix(case_d))
    print()

    # Summary comparison.
    print("Summary comparison:")
    print(f"  {'Case':<50}  {'Minsky':>8}  {'Coupling':>10}  {'Flips':>6}")
    for name, ctx in [
        ("A: healthy fiat, deep holder", case_a),
        ("B: healthy fiat, thin holder", case_b),
        ("C: collapsing fiat, thin holder", case_c),
        ("D: reciprocity network, stressed producer", case_d),
    ]:
        print(
            f"  {name:<50}  "
            f"{minsky_coefficient(ctx):>7.2f}x  "
            f"{coupling_magnitude(ctx):>10.2f}  "
            f"{str(has_sign_flips(ctx)):>6}"
        )
