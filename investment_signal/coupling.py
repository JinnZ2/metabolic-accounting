"""
investment_signal/coupling.py

Composite investment signal assembly.

This module composes the complete investment signal I from:

  - The input substrate vector (what the investor commits)
  - The expected output substrate vector (what the investor expects)
  - The investment context (attribution, derivative distance, time binding)
  - The money context (inherited from money_signal, via the investment context)

The composition produces five distinct signal components, each
measuring a different failure mode. They are kept separate because
collapsing them to a single "return" number loses the information
that makes the framework diagnostic rather than descriptive.

The five components:

  conversion_reliability: fraction of input substrate that arrives
    as the vehicle. This captures labor-misvalued, attention-extracted,
    time-stolen failure modes.

  realization_reliability: fraction of vehicle that produces the
    expected return. This captures market-collapse, storage-loss,
    and substrate-mismatch failure modes.

  time_binding_integrity: how well the temporal commitment holds
    at the evaluation scope. This captures liquidity-illusion and
    infrastructure-depreciation failure modes.

  derivative_signal: signal reliability and substrate visibility
    at the given derivative distance. This captures financialization
    and cascade-risk failure modes.

  money_coupling: the investment inherits the money signal from its
    dependency. If money is in near-collapse, investment is
    automatically compromised regardless of the other components.

The composite signal is returned as a structured dataclass so no
component can silently disappear. The caller must handle each one
explicitly rather than collapsing them.

CC0. Stdlib-only.
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Tuple, Optional

from .dimensions import (
    InvestmentContext,
    InvestmentSubstrate,
    DerivativeDistance,
    TimeBinding,
)
from .substrate_vectors import SubstrateVector, validate_vector_storage
from .conversion_matrix import (
    apply_conversion,
    apply_conversion_to_vector,
    validate_conversion_matrix,
)
from .realization_matrix import (
    apply_realization,
    apply_realization_to_vector,
    validate_realization_matrix,
)
from .time_binding import (
    base_time_binding_integrity,
    binding_integrity_with_substrate,
    binding_scope_mismatch_severity,
    is_short_binding_long_scope,
    is_long_binding_short_scope,
    validate_time_binding,
)
from .derivative_distance import (
    effective_signal_reliability,
    substrate_visibility,
    cascade_coupling,
    reverse_causation,
    is_financialized,
    is_substrate_invisible,
    substrate_abstraction_breakdown,
    validate_derivative_distance,
)

# Money-signal imports for the dependency relationship.
from money_signal.coupling import (
    coupling_matrix_as_dict as money_coupling_matrix,
    minsky_coefficient as money_minsky_coefficient,
    coupling_magnitude as money_coupling_magnitude,
    has_sign_flips as money_has_sign_flips,
    validate_all_factor_modules as validate_money_factor_modules,
)
from money_signal.dimensions import StateRegime as MoneyStateRegime


# ============================================================================
# INVESTMENT SIGNAL DATACLASS
# ============================================================================

@dataclass(frozen=True)
class InvestmentSignal:
    """
    The complete investment signal for a given context and
    input/output substrate vector pair.

    Every field is a distinct failure-mode diagnostic. Callers must
    handle each field rather than collapsing them to a single score.
    Collapsing is the measurement failure the framework exists to
    prevent.
    """

    # Input and expected output as the caller declared them.
    input_vector: SubstrateVector
    expected_output_vector: SubstrateVector

    # The vehicle vector: input vector fully converted across all
    # possible vehicle substrates. The investor's actual vehicle
    # holding depends on which conversion path is used.
    vehicle_vector: SubstrateVector

    # The realized output vector: vehicle vector fully realized
    # across all possible return substrates, modulated by time
    # binding and derivative distance.
    realized_output_vector: SubstrateVector

    # Per-substrate conversion reliability: for each requested
    # vehicle substrate, the fraction of intended input value that
    # actually arrives.
    conversion_per_vehicle: Tuple[Tuple[InvestmentSubstrate, float], ...]

    # Per-substrate realization reliability: for each expected
    # return substrate, the fraction of vehicle value that arrives
    # as realized return.
    realization_per_return: Tuple[Tuple[InvestmentSubstrate, float], ...]

    # Time binding integrity at the money context's evaluation scope.
    time_binding_integrity: float

    # Derivative distance signal components.
    derivative_signal_reliability: float
    substrate_visibility_at_distance: float
    cascade_coupling_at_distance: float
    reverse_causation_at_distance: float

    # Money dependency flags.
    money_minsky: float
    money_magnitude: float
    money_sign_flips: bool
    money_near_collapse: bool

    # Structural diagnostic flags.
    liquidity_illusion: bool
    infrastructure_depreciation_trap: bool
    is_financialized: bool
    substrate_invisible: bool
    substrate_abstraction_breakdown_any: bool

    # Meta flag: if True, the investment cannot be evaluated as an
    # investment because its dependencies are broken. Any return
    # figures should be treated as unreliable in this case.
    dependency_broken: bool

    def describe(self) -> str:
        """Return a human-readable summary for debugging and logs."""
        lines = [
            "InvestmentSignal:",
            f"  input:                   {self.input_vector.describe()}",
            f"  expected output:         {self.expected_output_vector.describe()}",
            f"  vehicle:                 {self.vehicle_vector.describe()}",
            f"  realized output:         {self.realized_output_vector.describe()}",
            f"  time binding integrity:  {self.time_binding_integrity:.2f}",
            f"  derivative reliability:  {self.derivative_signal_reliability:.2f}",
            f"  substrate visibility:    {self.substrate_visibility_at_distance:.2f}",
            f"  cascade coupling:        {self.cascade_coupling_at_distance:.2f}",
            f"  reverse causation:       {self.reverse_causation_at_distance:.2f}",
            f"  money Minsky:            {self.money_minsky:.2f}x",
            f"  money magnitude:         {self.money_magnitude:.2f}",
            f"  money sign flips:        {self.money_sign_flips}",
            f"  money near collapse:     {self.money_near_collapse}",
            f"  liquidity illusion:      {self.liquidity_illusion}",
            f"  infra depreciation:      {self.infrastructure_depreciation_trap}",
            f"  financialized:           {self.is_financialized}",
            f"  substrate invisible:     {self.substrate_invisible}",
            f"  abstraction breakdown:   {self.substrate_abstraction_breakdown_any}",
            f"  DEPENDENCY BROKEN:       {self.dependency_broken}",
        ]
        return "\n".join(lines)


# ============================================================================
# PRIMARY SUBSTRATE DETERMINATION
# ============================================================================

def primary_substrate(vector: SubstrateVector) -> Optional[InvestmentSubstrate]:
    """
    Return the substrate with the largest magnitude in the vector.

    Used for selecting the abstraction tolerance factor and the
    binding substrate modifier when the investment is multi-substrate.

    If the vector is all zeros, return None.
    """
    best_sub: Optional[InvestmentSubstrate] = None
    best_val = 0.0
    for sub, val in vector.components:
        if val > best_val:
            best_val = val
            best_sub = sub
    return best_sub


# ============================================================================
# ASSEMBLY
# ============================================================================

def assemble_investment_signal(
    input_vector: SubstrateVector,
    expected_output_vector: SubstrateVector,
    context: InvestmentContext,
) -> InvestmentSignal:
    """
    Assemble the complete investment signal from inputs.

    Args:
        input_vector: what the investor commits (seven-dim vector)
        expected_output_vector: what the investor expects back
        context: InvestmentContext including money context

    Returns:
        InvestmentSignal with all components populated
    """
    validate_vector_storage(input_vector)
    validate_vector_storage(expected_output_vector)

    # ----------------------------------------------------------------
    # Conversion: input -> vehicle
    # ----------------------------------------------------------------
    # For each possible vehicle substrate, compute how much arrives
    # if the input vector is converted into it.
    vehicle_vector = apply_conversion_to_vector(input_vector)

    # Per-substrate conversion reliability: ratio of what arrives as
    # this vehicle substrate to what would have arrived with perfect
    # conversion (i.e., the input L1 magnitude). This is crude
    # because substrates are incommensurable -- but the ratio is a
    # useful diagnostic for same-substrate and near-substrate paths.
    conversion_per_vehicle = tuple(
        (
            vehicle,
            _conversion_reliability_for(input_vector, vehicle),
        )
        for vehicle in InvestmentSubstrate
    )

    # ----------------------------------------------------------------
    # Realization: vehicle -> realized return
    # ----------------------------------------------------------------
    realized_output_vector = apply_realization_to_vector(vehicle_vector)

    realization_per_return = tuple(
        (
            return_sub,
            _realization_reliability_for(vehicle_vector, return_sub),
        )
        for return_sub in InvestmentSubstrate
    )

    # ----------------------------------------------------------------
    # Time binding integrity
    # ----------------------------------------------------------------
    eval_scope = context.money_context.temporal

    primary_binding_sub = primary_substrate(vehicle_vector)
    if primary_binding_sub is not None:
        tb_integrity = binding_integrity_with_substrate(
            context.time_binding,
            eval_scope,
            primary_binding_sub,
        )
    else:
        tb_integrity = base_time_binding_integrity(
            context.time_binding,
            eval_scope,
        )

    liquidity_illusion = is_short_binding_long_scope(
        context.time_binding, eval_scope
    )
    infra_trap = is_long_binding_short_scope(
        context.time_binding, eval_scope
    )

    # ----------------------------------------------------------------
    # Derivative distance degradation
    # ----------------------------------------------------------------
    # Use primary vehicle substrate for tolerance calculation.
    if primary_binding_sub is not None:
        derivative_rel = effective_signal_reliability(
            context.derivative_distance,
            primary_binding_sub,
        )
    else:
        derivative_rel = effective_signal_reliability(
            context.derivative_distance,
            InvestmentSubstrate.MONEY,  # fallback; all-zero case
        )

    sub_visibility = substrate_visibility(context.derivative_distance)
    casc_coupling = cascade_coupling(context.derivative_distance)
    rev_causation = reverse_causation(context.derivative_distance)
    financialized_flag = is_financialized(context.derivative_distance)
    sub_invisible_flag = is_substrate_invisible(context.derivative_distance)

    # Check any substrate with nonzero magnitude in the vehicle for
    # abstraction breakdown at this distance.
    abstraction_breakdown_any = False
    if context.derivative_distance != DerivativeDistance.DIRECT:
        for sub, val in vehicle_vector.components:
            if val > 0.0 and substrate_abstraction_breakdown(sub):
                abstraction_breakdown_any = True
                break

    # ----------------------------------------------------------------
    # Money signal coupling (dependency)
    # ----------------------------------------------------------------
    m_minsky = money_minsky_coefficient(context.money_context)
    m_magnitude = money_coupling_magnitude(context.money_context)
    m_sign_flips = money_has_sign_flips(context.money_context)
    m_near_collapse = context.money_context.state == MoneyStateRegime.NEAR_COLLAPSE

    # ----------------------------------------------------------------
    # Dependency broken: if money is in near-collapse, investment
    # cannot be meaningfully evaluated because time binding depends
    # on monetary stability.
    # ----------------------------------------------------------------
    dependency_broken = m_near_collapse

    return InvestmentSignal(
        input_vector=input_vector,
        expected_output_vector=expected_output_vector,
        vehicle_vector=vehicle_vector,
        realized_output_vector=realized_output_vector,
        conversion_per_vehicle=conversion_per_vehicle,
        realization_per_return=realization_per_return,
        time_binding_integrity=tb_integrity,
        derivative_signal_reliability=derivative_rel,
        substrate_visibility_at_distance=sub_visibility,
        cascade_coupling_at_distance=casc_coupling,
        reverse_causation_at_distance=rev_causation,
        money_minsky=m_minsky,
        money_magnitude=m_magnitude,
        money_sign_flips=m_sign_flips,
        money_near_collapse=m_near_collapse,
        liquidity_illusion=liquidity_illusion,
        infrastructure_depreciation_trap=infra_trap,
        is_financialized=financialized_flag,
        substrate_invisible=sub_invisible_flag,
        substrate_abstraction_breakdown_any=abstraction_breakdown_any,
        dependency_broken=dependency_broken,
    )


# ============================================================================
# RELIABILITY HELPERS
# ============================================================================

def _conversion_reliability_for(
    input_vector: SubstrateVector,
    vehicle_substrate: InvestmentSubstrate,
) -> float:
    """
    Per-vehicle conversion reliability.

    Returns the ratio of vehicle substrate produced to the input
    magnitude that could plausibly have produced it. For same-
    substrate paths this is the diagonal of C_BASE. For cross-
    substrate paths it is the convex combination weighted by input
    substrate magnitudes.

    This is a diagnostic ratio, not a physical quantity. It is
    most meaningful for same-substrate and near-substrate
    conversions.
    """
    # If input vector is all zeros, reliability is undefined -> 0.0.
    total_input_mag = input_vector.l1_magnitude()
    if total_input_mag == 0.0:
        return 0.0

    produced = apply_conversion(input_vector, vehicle_substrate)
    return produced / total_input_mag


def _realization_reliability_for(
    vehicle_vector: SubstrateVector,
    return_substrate: InvestmentSubstrate,
) -> float:
    """
    Per-return realization reliability.

    Ratio of realized return substrate to the vehicle magnitude
    that could plausibly have produced it.
    """
    total_vehicle_mag = vehicle_vector.l1_magnitude()
    if total_vehicle_mag == 0.0:
        return 0.0

    realized = apply_realization(vehicle_vector, return_substrate)
    return realized / total_vehicle_mag


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def signal_failure_count(signal: InvestmentSignal) -> int:
    """
    Return the number of structural failure flags that are True.

    Useful as a quick-look summary. A healthy investment should
    have zero failure flags. Each additional flag indicates an
    independent failure mode.
    """
    flags = [
        signal.liquidity_illusion,
        signal.infrastructure_depreciation_trap,
        signal.is_financialized,
        signal.substrate_invisible,
        signal.substrate_abstraction_breakdown_any,
        signal.money_sign_flips,
        signal.money_near_collapse,
        signal.dependency_broken,
    ]
    return sum(1 for f in flags if f)


def signal_failure_reasons(signal: InvestmentSignal) -> Tuple[str, ...]:
    """
    Return the names of failure modes that are flagged in the signal.

    Each name corresponds to a concrete, documented failure mode in
    the framework. Callers can use this list to generate targeted
    diagnostic reports.
    """
    reasons = []
    if signal.dependency_broken:
        reasons.append("money_dependency_broken")
    if signal.money_near_collapse:
        reasons.append("money_near_collapse")
    if signal.money_sign_flips:
        reasons.append("money_reflexive_sign_flips")
    if signal.liquidity_illusion:
        reasons.append("liquidity_illusion")
    if signal.infrastructure_depreciation_trap:
        reasons.append("infrastructure_depreciation_trap")
    if signal.is_financialized:
        reasons.append("financialized_reverse_causation")
    if signal.substrate_invisible:
        reasons.append("substrate_invisible_at_distance")
    if signal.substrate_abstraction_breakdown_any:
        reasons.append("substrate_abstraction_destroys_nature")
    return tuple(reasons)


# ============================================================================
# VALIDATION
# ============================================================================

def validate_all_investment_modules() -> None:
    """
    Run validation on every investment-signal factor module.

    Also runs money-signal validation because investment depends on it.

    Call this at startup to ensure no module has been edited into an
    invalid state since the last successful run.
    """
    validate_money_factor_modules()
    validate_conversion_matrix()
    validate_realization_matrix()
    validate_time_binding()
    validate_derivative_distance()


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    from ..money_signal.dimensions import (
        DimensionalContext as MoneyContext,
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )
    from .dimensions import (
        InvestmentAttribution,
        DerivativeDistance as DDist,
        TimeBinding as TB,
    )

    validate_all_investment_modules()
    print("All investment and money modules validated.")
    print()

    # Case A: paycheck-to-paycheck worker in 401k of index funds,
    # stressed digital fiat, generational scope.
    worker_money = MoneyContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.ATOMIZED_MARKET,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.STRESSED,
    )
    worker_ctx = InvestmentContext(
        money_context=worker_money,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DDist.TWO_LAYER,
        time_binding=TB.IMMEDIATE,  # 401k allows rebalancing -- short binding
    )
    worker_in = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 50000.0,
        InvestmentSubstrate.ATTENTION: 20.0,
    })
    worker_expected = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 150000.0,  # 3x over 30 years nominal
        InvestmentSubstrate.TIME: 1000.0,     # retirement time
    })

    worker_signal = assemble_investment_signal(
        worker_in, worker_expected, worker_ctx
    )
    print("Case A: 401k, thin holder, stressed digital fiat")
    print(worker_signal.describe())
    print(f"  failure count: {signal_failure_count(worker_signal)}")
    print(f"  reasons: {signal_failure_reasons(worker_signal)}")
    print()

    # Case B: farmer with multi-generational land, reciprocity culture,
    # metal substrate, direct substrate ownership.
    farmer_money = MoneyContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    )
    farmer_ctx = InvestmentContext(
        money_context=farmer_money,
        attribution=InvestmentAttribution.RECIPROCAL_OBLIGATION,
        derivative_distance=DDist.DIRECT,
        time_binding=TB.MULTI_GENERATIONAL,
    )
    farmer_in = SubstrateVector.from_dict({
        InvestmentSubstrate.TIME: 400.0,
        InvestmentSubstrate.LABOR: 400.0,
        InvestmentSubstrate.RESOURCE: 50.0,
        InvestmentSubstrate.ENERGY: 8000.0,
        InvestmentSubstrate.RELATIONAL_CAPITAL: 10.0,
    })
    farmer_expected = SubstrateVector.from_dict({
        InvestmentSubstrate.RESOURCE: 2000.0,
        InvestmentSubstrate.RELATIONAL_CAPITAL: 15.0,
    })
    farmer_signal = assemble_investment_signal(
        farmer_in, farmer_expected, farmer_ctx
    )
    print("Case B: farmer, multi-generational, reciprocity, direct substrate")
    print(farmer_signal.describe())
    print(f"  failure count: {signal_failure_count(farmer_signal)}")
    print(f"  reasons: {signal_failure_reasons(farmer_signal)}")
    print()

    # Case C: synthetic financial product in near-collapse monetary regime.
    collapse_money = MoneyContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.ATOMIZED_MARKET,
        attribution=AttributedValue.SPECULATIVE_CLAIM,
        observer=ObserverPosition.TOKEN_INTERMEDIARY,
        substrate=Substrate.DIGITAL,
        state=StateRegime.NEAR_COLLAPSE,
    )
    synth_ctx = InvestmentContext(
        money_context=collapse_money,
        attribution=InvestmentAttribution.SPECULATION_ON_SPECULATION,
        derivative_distance=DDist.SYNTHETIC,
        time_binding=TB.IMMEDIATE,
    )
    synth_in = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 1_000_000.0,
    })
    synth_expected = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 1_500_000.0,
    })
    synth_signal = assemble_investment_signal(
        synth_in, synth_expected, synth_ctx
    )
    print("Case C: synthetic derivative in near-collapse monetary regime")
    print(synth_signal.describe())
    print(f"  failure count: {signal_failure_count(synth_signal)}")
    print(f"  reasons: {signal_failure_reasons(synth_signal)}")
    print()

    # Summary
    print("Summary:")
    print(f"  {'Case':<40}  {'Failures':>10}")
    for name, sig in [
        ("A: thin worker 401k, stressed fiat", worker_signal),
        ("B: farmer, direct multi-gen substrate", farmer_signal),
        ("C: synthetic derivative, near collapse", synth_signal),
    ]:
        print(f"  {name:<40}  {signal_failure_count(sig):>10}")
