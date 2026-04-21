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

from money_signal.dimensions import (
    DimensionalContext,
    StateRegime,
    TemporalScope,
    CulturalScope,
    AttributedValue,
    ObserverPosition,
    Substrate,
)
from money_signal.coupling import (
    minsky_coefficient,
    coupling_magnitude,
    has_sign_flips,
)
from term_audit.integration.metabolic_accounting_adapter import (
    AssumptionValidatorFlag,
)
from term_audit.provenance import Provenance, design_choice


# ---------------------------------------------------------------------------
# Signal quality scoring
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WeightedThreshold:
    """A threshold + penalty coefficient with typed provenance.

    Every numeric weight in signal_quality() carries one of these
    so the framework can audit itself per AUDIT_07's Provenance
    discipline. All five weights here are DESIGN_CHOICE: structural
    choices with alternatives considered and a falsification test.
    Calibration belongs in money_signal/historical_cases.py; see
    the retirement_path in each provenance.
    """
    value: float
    provenance: Provenance


_BASELINE_QUALITY = WeightedThreshold(
    value=0.92,
    provenance=design_choice(
        rationale=(
            "baseline quality 0.92 rather than 1.0 encodes the claim that "
            "no monetary regime is perfectly reliable; even calibrated "
            "HEALTHY + METAL + STATE_ENFORCED has measurement noise"
        ),
        alternatives_considered=[
            "1.00 (zero baseline noise; overclaims the framework's confidence)",
            "0.85 (heavier baseline discount; understates healthy-regime reliability)",
            "a function of observer position (baseline varies by who is reading)",
        ],
        falsification_test=(
            "calibrate against historical_cases.py: derive observer-weighted "
            "signal-quality series from the 5 anchor cases and check whether "
            "the pre-event HEALTHY contexts average near 0.92"
        ),
    ),
)


_MINSKY_THRESHOLD = WeightedThreshold(
    value=1.3,
    provenance=design_choice(
        rationale=(
            "README baseline Minsky coefficient is ~1.14 (base matrix only). "
            "Observer and cultural factors move the composed ratio; empirically "
            "the healthy+thin+metal context sits at 1.31. Threshold 1.3 sits "
            "just below that baseline so that near-baseline thin-holder contexts "
            "are flagged with near-zero severity (honest) rather than silently "
            "passed (dishonest)."
        ),
        alternatives_considered=[
            "1.5 (avoids edge-case near-baseline flags but silently blesses slightly-above-healthy)",
            "2.0 (only flag pronounced stress; loses granularity)",
            "observer-indexed threshold (right in principle, added complexity)",
        ],
        falsification_test=(
            "run historical_cases.py pre-event contexts through signal_quality "
            "and check whether pre-event Minsky values cluster within the "
            "near-threshold-zero-severity band"
        ),
    ),
)


_MINSKY_PENALTY_PER_STEP = WeightedThreshold(
    value=0.18,
    provenance=design_choice(
        rationale=(
            "0.18 quality loss per unit of Minsky excess means Minsky ratio "
            "2.0 (strong stress) alone produces a ~0.13 quality drop. "
            "Calibrated to make STRESSED regime cluster near 0.87 signal "
            "quality (moderate but not alarming) and NEAR_COLLAPSE cluster "
            "below 0.5 (unreliable)."
        ),
        alternatives_considered=[
            "0.10 (undersells Minsky; NEAR_COLLAPSE would not drop sufficiently)",
            "0.30 (oversensitive; STRESSED would drop near NEAR_COLLAPSE)",
            "nonlinear exponent (right under threshold dynamics, added complexity)",
        ],
        falsification_test=(
            "run the 5 historical anchor cases and check whether the signal "
            "quality gradient across HEALTHY pre -> NEAR_COLLAPSE during "
            "tracks the observed documentation-density gradient (proxy for "
            "operator uncertainty in the period)"
        ),
    ),
)


_MAGNITUDE_THRESHOLD = WeightedThreshold(
    value=0.8,
    provenance=design_choice(
        rationale=(
            "mean off-diagonal |K_ij| < 1.0 is the README's structural "
            "signature of healthy / recovering regimes; 0.8 sits safely "
            "within the healthy range so stressed contexts (which typically "
            "hit ~0.7-1.0) start triggering the flag before full stress is "
            "reached"
        ),
        alternatives_considered=[
            "1.0 (catches only elevated-magnitude cases; loses early warning)",
            "0.5 (over-sensitive; healthy regimes would flag)",
        ],
        falsification_test=(
            "check whether money_signal's HEALTHY example cases (deep + thin) "
            "produce coupling_magnitude below threshold; they do (0.22 and 0.70)"
        ),
    ),
)


_MAGNITUDE_PENALTY_PER_STEP = WeightedThreshold(
    value=0.22,
    provenance=design_choice(
        rationale=(
            "0.22 makes a magnitude-1.25 regime (NEAR_COLLAPSE characteristic) "
            "contribute a ~0.10 penalty, complementing the Minsky contribution "
            "so the two stressors sum to a meaningful quality drop"
        ),
        alternatives_considered=[
            "0.15 (undersells magnitude effect)",
            "0.35 (compounds with Minsky too aggressively)",
        ],
        falsification_test=(
            "cross-check against historical_cases.py: a case whose recorded "
            "coupling is known to have high magnitude but low Minsky should "
            "still produce signal_quality degradation on the magnitude axis"
        ),
    ),
)


_SIGN_FLIP_PENALTY = WeightedThreshold(
    value=0.35,
    provenance=design_choice(
        rationale=(
            "sign flips are a discrete phenomenon (README claim #7: only "
            "permitted in NEAR_COLLAPSE). Their presence is a qualitatively "
            "different signal from elevated magnitudes — panic-buying-like "
            "dynamics. A 0.35 penalty makes their presence drop quality "
            "below the stressed-without-flips case without single-handedly "
            "zeroing quality."
        ),
        alternatives_considered=[
            "0.20 (too gentle; sign flips are the README's hardest collapse signature)",
            "0.50 (too heavy; would dominate every other stressor)",
            "scale with number of sign flips (right in principle, discretize for now)",
        ],
        falsification_test=(
            "GFC 2008 recorded sign flip in K[N][C] windowed correlations "
            "(Krishnamurthy 2010); check whether the signal_quality for GFC "
            "during-context (which has sign_flips=True) drops the expected "
            "delta below a matched no-flips context"
        ),
    ),
)


def signal_quality(ctx: DimensionalContext) -> float:
    """Scalar reliability of monetary denomination in [0, 1].

    A quantity denominated in money is assumed to translate to
    metabolic (xdu) reality with fidelity = signal_quality. When the
    coupling regime is healthy, the translation is reliable; when
    the regime is stressed or collapsing, the translation distorts
    more.

    All weights used here are DESIGN_CHOICE under the AUDIT_07
    Provenance taxonomy — see the WeightedThreshold records above.
    Calibration belongs in money_signal/historical_cases.py (see
    each weight's retirement_path).
    """
    q = _BASELINE_QUALITY.value

    minsky = minsky_coefficient(ctx)
    if minsky > _MINSKY_THRESHOLD.value:
        q -= (minsky - _MINSKY_THRESHOLD.value) * _MINSKY_PENALTY_PER_STEP.value

    mag = coupling_magnitude(ctx)
    if mag > _MAGNITUDE_THRESHOLD.value:
        q -= (mag - _MAGNITUDE_THRESHOLD.value) * _MAGNITUDE_PENALTY_PER_STEP.value

    if has_sign_flips(ctx):
        q -= _SIGN_FLIP_PENALTY.value

    return max(0.0, min(1.0, q))


# Exposed aggregator for the provenance-coverage audit.
ALL_WEIGHTS: Tuple[WeightedThreshold, ...] = (
    _BASELINE_QUALITY,
    _MINSKY_THRESHOLD,
    _MINSKY_PENALTY_PER_STEP,
    _MAGNITUDE_THRESHOLD,
    _MAGNITUDE_PENALTY_PER_STEP,
    _SIGN_FLIP_PENALTY,
)


def coupling_assumption_flags(ctx: DimensionalContext) -> List[AssumptionValidatorFlag]:
    """Flags for the assumption_validator describing which coupling
    stressors are driving quality loss under this context.

    Severity is the deficit contribution of that specific stressor,
    clipped to [0, 1]. A flag is emitted only when its stressor is
    active.
    """
    flags: List[AssumptionValidatorFlag] = []
    src = f"money_signal.accounting_bridge:{ctx.describe()}"

    minsky = minsky_coefficient(ctx)
    if minsky > _MINSKY_THRESHOLD.value:
        sev = min(
            1.0,
            (minsky - _MINSKY_THRESHOLD.value) * _MINSKY_PENALTY_PER_STEP.value,
        )
        flags.append(AssumptionValidatorFlag(
            source_audit=src,
            failure_mode="minsky_asymmetry_elevated",
            severity=sev,
            message=(
                f"Minsky coefficient = {minsky:.2f}x (threshold "
                f"{_MINSKY_THRESHOLD.value}). Trust-collapse asymmetry is "
                f"amplified; money-denominated reported profit likely "
                f"overstates metabolic profit."
            ),
        ))

    mag = coupling_magnitude(ctx)
    if mag > _MAGNITUDE_THRESHOLD.value:
        sev = min(
            1.0,
            (mag - _MAGNITUDE_THRESHOLD.value) * _MAGNITUDE_PENALTY_PER_STEP.value,
        )
        flags.append(AssumptionValidatorFlag(
            source_audit=src,
            failure_mode="coupling_magnitude_elevated",
            severity=sev,
            message=(
                f"Mean coupling magnitude = {mag:.2f} (threshold "
                f"{_MAGNITUDE_THRESHOLD.value}). Monetary variables couple "
                f"strongly to each other; a shock in any one propagates "
                f"quickly across the signal."
            ),
        ))

    if has_sign_flips(ctx):
        flags.append(AssumptionValidatorFlag(
            source_audit=src,
            failure_mode="sign_flips_present",
            severity=_SIGN_FLIP_PENALTY.value,
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
# StateRegime inference from an accounting Verdict
# ---------------------------------------------------------------------------

# GREEN / AMBER / RED / BLACK map to HEALTHY / STRESSED / NEAR_COLLAPSE
# by severity. RECOVERING is NOT inferable from a single-period verdict
# — a firm that is post-collapse but currently GREEN is in RECOVERING,
# but the verdict at this period alone cannot distinguish that from a
# steady-state HEALTHY firm. Callers must pass `recovering=True`
# explicitly when they know the firm is post-event.
_VERDICT_SIGNAL_TO_STATE = {
    "GREEN":  StateRegime.HEALTHY,
    "AMBER":  StateRegime.STRESSED,
    "RED":    StateRegime.NEAR_COLLAPSE,
    "BLACK":  StateRegime.NEAR_COLLAPSE,
}


def regime_from_verdict_signal(signal: str, *, recovering: bool = False) -> StateRegime:
    """Map a sustainable_yield_signal string to a StateRegime.

    `signal` is one of GREEN / AMBER / RED / BLACK — the string form
    produced by verdict/assess.py::yield_signal. RECOVERING cannot be
    inferred from a single-period signal; pass `recovering=True`
    explicitly when the firm is known post-collapse.

    BLACK maps to NEAR_COLLAPSE rather than introducing a new
    "irreversible" regime here. BLACK is the main stack's signal for
    irreversibility; the money_signal framework's dimensional model
    doesn't add a matching regime because irreversibility is a basin
    property, not a monetary-coupling property.
    """
    if recovering:
        return StateRegime.RECOVERING
    state = _VERDICT_SIGNAL_TO_STATE.get(signal.upper() if signal else "")
    if state is None:
        raise ValueError(
            f"unknown verdict signal: {signal!r} "
            f"(expected one of GREEN/AMBER/RED/BLACK)"
        )
    return state


def context_from_verdict_signal(
    signal: str,
    *,
    temporal: TemporalScope,
    cultural: CulturalScope,
    attribution: AttributedValue,
    observer: ObserverPosition,
    substrate: Substrate,
    recovering: bool = False,
) -> DimensionalContext:
    """Build a DimensionalContext from a verdict signal plus the five
    dimensions the caller must declare.

    Five of the six dimensions describe the MONETARY regime the firm
    operates in (what currency, what institutional context, what
    substrate); these cannot be inferred from the firm's basin state
    and must be declared. The sixth — StateRegime — CAN be inferred
    from the firm's verdict. This helper makes that the only dimension
    the caller does not have to supply by hand.

    Usage:

        ctx = context_from_verdict_signal(
            verdict.sustainable_yield_signal,
            temporal=TemporalScope.SEASONAL,
            cultural=CulturalScope.INSTITUTIONAL,
            attribution=AttributedValue.STATE_ENFORCED,
            observer=ObserverPosition.TOKEN_HOLDER_THIN,
            substrate=Substrate.DIGITAL,
        )
        q = signal_quality(ctx)
    """
    state = regime_from_verdict_signal(signal, recovering=recovering)
    return DimensionalContext(
        temporal=temporal,
        cultural=cultural,
        attribution=attribution,
        observer=observer,
        substrate=substrate,
        state=state,
    )


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
