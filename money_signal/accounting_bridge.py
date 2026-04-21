"""
money_signal/accounting_bridge.py

One-way bridge from money_signal/ diagnostics to the metabolic-
accounting assumption-validator surface.

The README (line 134) claims money-as-signal couples directly into
the glucose-flow metaphor: reversal reliability is the metabolic
signal. This module makes that claim operational without entangling
the two layers:

  - accounting/glucose.py operates in xdu (exergy-destruction units).
    Its numbers are physical.
  - money_signal/ operates on dimensionless coupling coefficients
    indexed by a DimensionalContext. Its numbers are relational.
  - When the firm uses money-denominated quantities (revenue, opex,
    regen payments) as inputs to the metabolic-accounting pipeline,
    the reliability of the monetary DENOMINATION bounds how much
    to trust the translation $ -> xdu.

This module produces:

  - signal_quality(ctx) : float in [0,1]. 1.0 = fully reliable
    monetary denomination. 0.0 = unreliable.
  - coupling_assumption_flags(ctx) : list of AssumptionValidatorFlag
    suitable for emit into the assumption_validator pipeline. Flags
    the stressors that drove signal_quality below thresholds.
  - flows-with-discount helpers that accept a GlucoseFlow and a
    DimensionalContext and compute how much of the reported $ figure
    should be trusted under the current coupling regime.

This is a ONE-WAY bridge. Nothing in money_signal/ imports
accounting/. accounting/ does not need to import this module; it
can if it wants to consume signal_quality, or it can ignore the
bridge entirely. Both layers stay independently testable.

CC0. Stdlib-only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass
from typing import List, Tuple

from money_signal.dimensions import DimensionalContext, StateRegime
from money_signal.coupling import (
    minsky_coefficient,
    coupling_magnitude,
    has_sign_flips,
)
from term_audit.integration.metabolic_accounting_adapter import (
    AssumptionValidatorFlag,
)


# ---------------------------------------------------------------------------
# Signal quality scoring
# ---------------------------------------------------------------------------

# Design choices per AUDIT_12 Part D:
#   HEALTHY baseline yields quality ≈ 0.92 (never 1.0 — no monetary
#     regime is perfectly reliable)
#   STRESSED drops quality by the Minsky-excess and magnitude-excess
#     penalties
#   NEAR_COLLAPSE with sign flips yields quality ≈ 0.1
#   thresholds are DESIGN_CHOICE per the AUDIT_07 Provenance taxonomy
_BASELINE_QUALITY        = 0.92
_MINSKY_THRESHOLD        = 1.3
_MINSKY_PENALTY_PER_STEP = 0.18
_MAGNITUDE_THRESHOLD     = 0.8
_MAGNITUDE_PENALTY_PER_STEP = 0.22
_SIGN_FLIP_PENALTY       = 0.35


def signal_quality(ctx: DimensionalContext) -> float:
    """Scalar reliability of monetary denomination in [0, 1].

    A quantity denominated in money is assumed to translate to
    metabolic (xdu) reality with fidelity = signal_quality. When the
    coupling regime is healthy, the translation is reliable; when
    the regime is stressed or collapsing, the translation distorts
    more.

    Not a measurement — a heuristic whose weights are DESIGN_CHOICE
    provenance. Calibration belongs in money_signal/historical_cases.py
    (see retirement path in AUDIT_12 § D).
    """
    q = _BASELINE_QUALITY

    minsky = minsky_coefficient(ctx)
    if minsky > _MINSKY_THRESHOLD:
        q -= (minsky - _MINSKY_THRESHOLD) * _MINSKY_PENALTY_PER_STEP

    mag = coupling_magnitude(ctx)
    if mag > _MAGNITUDE_THRESHOLD:
        q -= (mag - _MAGNITUDE_THRESHOLD) * _MAGNITUDE_PENALTY_PER_STEP

    if has_sign_flips(ctx):
        q -= _SIGN_FLIP_PENALTY

    return max(0.0, min(1.0, q))


def coupling_assumption_flags(ctx: DimensionalContext) -> List[AssumptionValidatorFlag]:
    """Flags for the assumption_validator describing which coupling
    stressors are driving quality loss under this context.

    Severity is the deficit vs baseline quality (`_BASELINE_QUALITY -
    quality_if_only_this_stressor_applied`), clipped to [0, 1]. A
    flag is emitted only when its stressor is active.
    """
    flags: List[AssumptionValidatorFlag] = []
    src = f"money_signal.accounting_bridge:{ctx.describe()}"

    minsky = minsky_coefficient(ctx)
    if minsky > _MINSKY_THRESHOLD:
        sev = min(1.0, (minsky - _MINSKY_THRESHOLD) * _MINSKY_PENALTY_PER_STEP)
        flags.append(AssumptionValidatorFlag(
            source_audit=src,
            failure_mode="minsky_asymmetry_elevated",
            severity=sev,
            message=(
                f"Minsky coefficient = {minsky:.2f}x (threshold "
                f"{_MINSKY_THRESHOLD}). Trust-collapse asymmetry is "
                f"amplified; money-denominated reported profit likely "
                f"overstates metabolic profit."
            ),
        ))

    mag = coupling_magnitude(ctx)
    if mag > _MAGNITUDE_THRESHOLD:
        sev = min(1.0, (mag - _MAGNITUDE_THRESHOLD) * _MAGNITUDE_PENALTY_PER_STEP)
        flags.append(AssumptionValidatorFlag(
            source_audit=src,
            failure_mode="coupling_magnitude_elevated",
            severity=sev,
            message=(
                f"Mean coupling magnitude = {mag:.2f} (threshold "
                f"{_MAGNITUDE_THRESHOLD}). Monetary variables couple "
                f"strongly to each other; a shock in any one propagates "
                f"quickly across the signal."
            ),
        ))

    if has_sign_flips(ctx):
        flags.append(AssumptionValidatorFlag(
            source_audit=src,
            failure_mode="sign_flips_present",
            severity=_SIGN_FLIP_PENALTY,
            message=(
                "Sign flips present in the composed coupling matrix. "
                "Monetary causation is temporarily inverted (e.g. "
                "panic-buying: rising cost correlates with rising "
                "acceptance). $ -> xdu translation is unreliable."
            ),
        ))

    if ctx.state == StateRegime.NEAR_COLLAPSE:
        flags.append(AssumptionValidatorFlag(
            source_audit=src,
            failure_mode="near_collapse_regime",
            severity=0.9,
            message=(
                "StateRegime.NEAR_COLLAPSE: monetary denomination is "
                "unreliable by construction. Accounting should fall "
                "back to in-kind / xdu-direct measurement where "
                "possible; money-denominated figures should be "
                "reported as extraordinary-item-flagged."
            ),
        ))

    return flags


# ---------------------------------------------------------------------------
# GlucoseFlow adjustment helper (lazy import of accounting/ so this
# module remains standalone-testable)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SignalAdjustedFlow:
    """A view on a GlucoseFlow with monetary quantities discounted
    by signal_quality. This is not a new accounting concept; it is
    a presentation that shows what the reported and metabolic
    profits look like when we stop trusting the monetary
    denomination.

    Leaves the original GlucoseFlow untouched. Consumers decide
    whether to use the adjusted view or the raw one.
    """
    quality: float
    reported_profit_raw: float
    reported_profit_adjusted: float
    metabolic_profit_raw: float
    metabolic_profit_adjusted: float
    minsky: float
    magnitude: float
    sign_flips: bool


def adjust_glucose_flow(flow, ctx: DimensionalContext) -> SignalAdjustedFlow:
    """Produce a signal-adjusted view of a GlucoseFlow.

    The adjustment discounts the MONETARY (reported) profit by
    signal_quality. The METABOLIC profit is reported both raw (in
    xdu) and adjusted (scaled by signal_quality so readers can see
    how much the physical accounting depends on the monetary
    translation for the regen_paid / cascade_burn inputs).

    This is the cheapest, most defensible bridge: it does not
    modify accounting, does not change the xdu closure invariants,
    and surfaces the signal-quality discount as an adjunct view.
    """
    q = signal_quality(ctx)
    return SignalAdjustedFlow(
        quality=q,
        reported_profit_raw=flow.reported_profit(),
        reported_profit_adjusted=flow.reported_profit() * q,
        metabolic_profit_raw=flow.metabolic_profit(),
        metabolic_profit_adjusted=flow.metabolic_profit() * q,
        minsky=minsky_coefficient(ctx),
        magnitude=coupling_magnitude(ctx),
        sign_flips=has_sign_flips(ctx),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _demo() -> None:
    from money_signal.dimensions import (
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate,
    )
    scenarios = [
        ("healthy fiat, deep holder", DimensionalContext(
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_DEEP,
            substrate=Substrate.METAL,
            state=StateRegime.HEALTHY,
        )),
        ("healthy fiat, thin holder", DimensionalContext(
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_THIN,
            substrate=Substrate.METAL,
            state=StateRegime.HEALTHY,
        )),
        ("stressed fiat, thin holder", DimensionalContext(
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_THIN,
            substrate=Substrate.METAL,
            state=StateRegime.STRESSED,
        )),
        ("near-collapse fiat, thin holder", DimensionalContext(
            temporal=TemporalScope.TRANSACTION,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_THIN,
            substrate=Substrate.DIGITAL,
            state=StateRegime.NEAR_COLLAPSE,
        )),
    ]
    print("=" * 72)
    print("money_signal.accounting_bridge — signal quality per context")
    print("=" * 72)
    for name, ctx in scenarios:
        q = signal_quality(ctx)
        flags = coupling_assumption_flags(ctx)
        print(f"\n  {name}")
        print(f"    quality:      {q:.3f}")
        print(f"    flags:        {len(flags)}")
        for f in flags:
            print(f"      [{f.severity:.2f}] {f.failure_mode}")


if __name__ == "__main__":
    _demo()
