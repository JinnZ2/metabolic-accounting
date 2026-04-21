"""
money_signal/historical_cases.py

Anchor cases for empirical calibration of the coupling framework.

Core discipline: the framework's factor values are first-principles
estimates. Per README Known Limitations #1, historical-case
calibration is needed before those factors should be read as
quantitative. This module is the structural anchor for that work.

What this module IS:
  - A schema (HistoricalCase) that names events, regimes, and
    observed dynamics in the framework's own dimensional language
    (pre/during/post DimensionalContexts + observed qualitative
    shifts in R, N, C, L)
  - A handful of anchor cases drawn from well-documented monetary
    events (Weimar, Zimbabwe, 2008 GFC, Cyprus 2013, Argentina 2001)
  - A comparison function that runs the framework prediction for a
    case's DURING context and surfaces any mismatch between
    predicted coupling regime and the qualitative dynamics recorded

What this module IS NOT:
  - A source of calibrated quantitative K_ij values. Every case's
    `observed_dynamics` field carries a PLACEHOLDER provenance
    pointing at a retirement path (the literature the real numbers
    would be extracted from). Fabricating numbers under the
    empirical label would be worse than honest placeholders.
  - A fit. The framework's K values are not tuned against these
    cases; they remain first-principles. The cases exist so
    readers can see whether the framework's predictions track the
    qualitative shape of recorded events — and flag where they
    don't.

See docs/AUDIT_12.md for intake, the AUDIT_07 Provenance taxonomy,
and the rationale for marking observed values PLACEHOLDER pending
literature work.

CC0. Stdlib-only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple

from money_signal.dimensions import (
    DimensionalContext,
    TemporalScope, CulturalScope, AttributedValue,
    ObserverPosition, Substrate, StateRegime,
)
from money_signal.coupling import (
    minsky_coefficient, coupling_magnitude, has_sign_flips,
)
from term_audit.provenance import (
    Provenance, empirical, theoretical, placeholder,
)


# ---------------------------------------------------------------------------
# Observed-dynamic vocabulary
# ---------------------------------------------------------------------------

class DynamicShift(Enum):
    """Qualitative direction of a K_ij shift observed historically.

    The READme's falsifiable claims are stated qualitatively
    (K[N][R] amplifies under speculative attribution, etc.). This
    vocabulary lets historical cases record the observed direction
    without pretending to quantify it.
    """
    AMPLIFIED_STRONG = "amplified_strong"   # >>2x baseline
    AMPLIFIED = "amplified"                 # 1.3-2x baseline
    UNCHANGED = "unchanged"                 # within 0.8-1.3x baseline
    DAMPED = "damped"                       # 0.5-0.8x baseline
    DAMPED_STRONG = "damped_strong"         # <<0.5x baseline
    SIGN_FLIPPED = "sign_flipped"           # direction reversed (only valid in near-collapse per README)


@dataclass
class ObservedDynamic:
    """One qualitative dynamic shift observed during a historical case."""
    term_i: str           # e.g. "N" (network acceptance)
    term_j: str           # e.g. "R" (reversal reliability)
    shift: DynamicShift
    evidence: str         # prose account of what was observed
    provenance: Provenance


@dataclass
class HistoricalCase:
    """A documented monetary event usable as a framework anchor."""
    name: str
    period: str                    # e.g. "1921-1923"
    location: str

    # The context pre/during/post the event. These are the framework's
    # own dimensional labels for the system state at each phase.
    context_pre: DimensionalContext
    context_during: DimensionalContext
    context_post: Optional[DimensionalContext]

    # Recorded dynamics. Each entry is one qualitative shift with
    # evidence and provenance. The list may be partial; completeness
    # is not required for a case to anchor.
    observed_dynamics: List[ObservedDynamic] = field(default_factory=list)

    # Canonical literature anchors for the whole case.
    primary_refs: List[str] = field(default_factory=list)

    # How well-established is the case in the literature? 0.0-1.0.
    historical_confidence: float = 0.0

    # Free-form notes on caveats / contested interpretations.
    notes: str = ""


# ---------------------------------------------------------------------------
# Anchor cases
# ---------------------------------------------------------------------------

WEIMAR_1921_1923 = HistoricalCase(
    name="Weimar hyperinflation and Rentenmark stabilization",
    period="1921-1923",
    location="Weimar Germany",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.PAPER,
        state=StateRegime.STRESSED,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.PAPER,
        state=StateRegime.NEAR_COLLAPSE,
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.COMMODITY_BACKED,  # Rentenmark's land-mortgage pseudo-backing
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.PAPER,
        state=StateRegime.RECOVERING,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="N", term_j="R",
            shift=DynamicShift.AMPLIFIED_STRONG,
            evidence=(
                "loss of reversal reliability triggered near-total "
                "acceptance collapse within months; workers demanded "
                "twice-daily wages; employers switched to in-kind"
            ),
            provenance=empirical(
                source_refs=[
                    "Feldman 1993, 'The Great Disorder: Politics, Economics, "
                    "and Society in the German Inflation, 1914-1924'",
                    "Holtfrerich 1986, 'The German Inflation 1914-1923'",
                ],
                rationale=(
                    "shift direction is documented in multiple primary "
                    "sources; specific quantitative K ratio extraction "
                    "remains PLACEHOLDER (see retirement_path)"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="R", term_j="N",
            shift=DynamicShift.DAMPED_STRONG,
            evidence=(
                "reversal reliability continued falling even as network "
                "acceptance stabilized via informal substitutes; hysteresis "
                "outlasted the stabilization"
            ),
            provenance=placeholder(
                rationale="direction documented; magnitude not extracted",
                retirement_path=(
                    "construct monthly K proxy from Ewald 2002 wage-price "
                    "datasets and cross-reference against Holtfrerich"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Feldman 1993",
        "Holtfrerich 1986",
        "Bresciani-Turroni 1937, 'The Economics of Inflation'",
    ],
    historical_confidence=0.95,
    notes=(
        "Canonical near-collapse + recovering example. Post-event "
        "context carries COMMODITY_BACKED attribution because the "
        "Rentenmark's legal backing was theoretical mortgage claims "
        "on land; the backing was symbolic but stabilized expectations."
    ),
)


ZIMBABWE_2007_2009 = HistoricalCase(
    name="Zimbabwe hyperinflation and dollarization",
    period="2007-2009",
    location="Zimbabwe",
    context_pre=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.PAPER,
        state=StateRegime.STRESSED,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.PAPER,
        state=StateRegime.NEAR_COLLAPSE,
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,  # USD adopted
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,                 # dollarized + mobile money
        state=StateRegime.RECOVERING,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="N", term_j="R",
            shift=DynamicShift.AMPLIFIED_STRONG,
            evidence=(
                "ZWL acceptance collapsed as reversal reliability fell; "
                "parallel-market USD, SA rand, ZAR, Pula, and barter "
                "rose as dominant rails"
            ),
            provenance=empirical(
                source_refs=[
                    "Hanke & Kwok 2009, 'On the Measurement of Zimbabwe's "
                    "Hyperinflation', Cato Journal 29(2)",
                    "Noko 2011, 'Dollarization: The Case of Zimbabwe', "
                    "Cato Journal 31(2)",
                ],
                rationale="shift direction well-documented; magnitude not extracted",
            ),
        ),
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.DAMPED_STRONG,
            evidence=(
                "reliability recovery under dollarization substantially "
                "slower than metric-level price stabilization (hysteresis)"
            ),
            provenance=placeholder(
                rationale=(
                    "documented qualitatively; per-sector reliability "
                    "lags quantification deferred"
                ),
                retirement_path=(
                    "extract inter-bank trust proxies from Zimbabwe "
                    "Central Bank reports 2009-2013"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Hanke & Kwok 2009",
        "Noko 2011",
        "Koech 2011 FRB Dallas Globalization Institute working paper",
    ],
    historical_confidence=0.90,
    notes=(
        "Post-event context shifts substrate from PAPER to DIGITAL as "
        "mobile-money and USD-account rails displaced the collapsed "
        "physical currency. An unusually rapid substrate transition."
    ),
)


GFC_2008 = HistoricalCase(
    name="Global Financial Crisis — near-collapse episode",
    period="2007-2009",
    location="US / Europe / global funding markets",
    context_pre=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.SPECULATIVE_CLAIM,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.HEALTHY,  # widely perceived as such
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.SPECULATIVE_CLAIM,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.NEAR_COLLAPSE,
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,  # post-TARP / central-bank backstops
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.RECOVERING,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="N", term_j="R",
            shift=DynamicShift.AMPLIFIED_STRONG,
            evidence=(
                "AIG / Lehman reliability failures triggered immediate "
                "collapse of MMF and repo acceptance; classic Minsky "
                "moment with documented reflexive amplification"
            ),
            provenance=empirical(
                source_refs=[
                    "Gorton 2010, 'Slapped by the Invisible Hand: The "
                    "Panic of 2007'",
                    "Bernanke, Geithner & Paulson 2019, 'Firefighting: "
                    "The Financial Crisis and Its Lessons'",
                    "Krishnamurthy 2010, 'How Debt Markets Have Malfunctioned "
                    "in the Crisis', JEP 24(1)",
                ],
                rationale=(
                    "reflexive K[N][R] dynamics directly named in the "
                    "post-crisis literature; Minsky framing standard"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="N", term_j="C",
            shift=DynamicShift.SIGN_FLIPPED,
            evidence=(
                "in the weeks around Lehman, rising cost of funding "
                "briefly correlated with rising acceptance demand "
                "(treasury rush) — the README claim #7 panic-buying "
                "dynamic"
            ),
            provenance=placeholder(
                rationale="direction widely reported; windowed correlations not re-extracted here",
                retirement_path=(
                    "pull daily LIBOR-OIS spread and T-bill auction bid "
                    "cover from FRED / Treasury data and compute the "
                    "window"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Gorton 2010",
        "Bernanke, Geithner & Paulson 2019",
        "Krishnamurthy 2010",
    ],
    historical_confidence=0.95,
    notes=(
        "Canonical test of README claims #4 (speculative amplification) "
        "and #7 (near-collapse sign flips). Pre-crisis attribution is "
        "SPECULATIVE_CLAIM because the MBS / CDS stack had no substrate, "
        "institutional, or relational floor — exactly the failure mode "
        "the README anticipates."
    ),
)


CYPRUS_2013 = HistoricalCase(
    name="Cyprus bank haircut — observer-asymmetry case",
    period="March 2013",
    location="Cyprus",
    context_pre=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.STRESSED,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.NEAR_COLLAPSE,  # for thin depositors specifically
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.RECOVERING,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="R", term_j="C",
            shift=DynamicShift.AMPLIFIED_STRONG,
            evidence=(
                "bank-levy proposal followed by capital controls: small "
                "depositors experienced sudden loss of reversal reliability "
                "at precisely the moment capital outflow was throttled; "
                "asymmetric with issuer/institution view, which remained "
                "nominally healthy"
            ),
            provenance=empirical(
                source_refs=[
                    "Michaelides 2014, 'Cyprus: From Boom to Bail-In', "
                    "Economic Policy 29(80)",
                    "Zenios 2013, 'The Cyprus Debt: Perfect Crisis and "
                    "a Way Forward', Cyprus Economic Policy Review 7(1)",
                ],
                rationale=(
                    "observer-asymmetry between thin depositors and "
                    "the institutional observer is directly documented"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Michaelides 2014",
        "Zenios 2013",
    ],
    historical_confidence=0.85,
    notes=(
        "Canonical anchor for README claim #5 (observer asymmetry). The "
        "same system-state showed HEALTHY for the institutional observer "
        "and NEAR_COLLAPSE for thin depositors. An aggregate metric "
        "would have missed this entirely."
    ),
)


ARGENTINA_2001_2002 = HistoricalCase(
    name="Argentine peso collapse and pesification",
    period="December 2001 - 2002",
    location="Argentina",
    context_pre=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.COMMODITY_BACKED,  # 1:1 dollar peg = quasi-backing
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.STRESSED,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,  # peg broken, USD-denominated contracts pesified by decree
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.PAPER,  # corralito bank-freeze forced physical use
        state=StateRegime.NEAR_COLLAPSE,
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.RECOVERING,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="N", term_j="R",
            shift=DynamicShift.AMPLIFIED_STRONG,
            evidence=(
                "corralito freeze destroyed reversal reliability overnight; "
                "acceptance of peso-denominated contracts collapsed; "
                "barter clubs and provincial scrip (LECOPs) filled the gap"
            ),
            provenance=empirical(
                source_refs=[
                    "Hornbeck 2002 CRS Report RS21131, 'The Argentine "
                    "Financial Crisis'",
                    "Cibils, Weisbrot & Kar 2002, CEPR working paper",
                ],
                rationale="direction well-documented in English-language sources",
            ),
        ),
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.DAMPED_STRONG,
            evidence=(
                "pre-corralito USD reserve behavior returned as the "
                "dominant norm even after formal stabilization (hysteresis "
                "across multiple years)"
            ),
            provenance=placeholder(
                rationale=(
                    "shift direction clear; long-horizon hysteresis "
                    "metrics not extracted"
                ),
                retirement_path=(
                    "dollar-savings ratio series from BCRA; compare to "
                    "pre-crisis baseline"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Hornbeck 2002",
        "Cibils, Weisbrot & Kar 2002",
    ],
    historical_confidence=0.85,
    notes=(
        "Argentina has had multiple near-collapse episodes (2001-02, "
        "2018-19, 2022-). Only the 2001-02 episode is anchored here. "
        "The repeated pattern is itself a data point for framework "
        "hysteresis claims."
    ),
)


ALL_CASES: List[HistoricalCase] = [
    WEIMAR_1921_1923,
    ZIMBABWE_2007_2009,
    GFC_2008,
    CYPRUS_2013,
    ARGENTINA_2001_2002,
]


# ---------------------------------------------------------------------------
# Framework prediction vs observed shape
# ---------------------------------------------------------------------------

@dataclass
class FrameworkPrediction:
    """What the framework predicts for a given context."""
    minsky: float
    coupling_magnitude: float
    has_sign_flips: bool


def predict(ctx: DimensionalContext) -> FrameworkPrediction:
    """Run the framework diagnostics for a context, returning the
    three top-level indicators the README exposes."""
    return FrameworkPrediction(
        minsky=minsky_coefficient(ctx),
        coupling_magnitude=coupling_magnitude(ctx),
        has_sign_flips=has_sign_flips(ctx),
    )


@dataclass
class CaseComparison:
    """Comparison of a historical case's recorded shape vs the
    framework's prediction for the DURING context."""
    case: HistoricalCase
    prediction: FrameworkPrediction
    # Qualitative agreement check
    observed_n_r_amplified: bool
    predicted_n_r_high: bool
    sign_flip_observed: bool
    sign_flip_predicted: bool

    @property
    def qualitative_match(self) -> bool:
        """True iff the framework's prediction qualitatively aligns
        with the recorded shape.

        Match semantics are asymmetric between the two checks:

        - K[N][R] amplification: a strong README-level claim. The
          framework predicts high K[N][R] during NEAR_COLLAPSE;
          observed amplification must agree.

        - Sign flips: the framework predicts NEAR_COLLAPSE *permits*
          sign flips, not that they always occur. Recorded flips
          are confirming; recorded silence is neither confirming
          nor disconfirming, because most historical accounts do
          not break out windowed correlation sign changes. We
          require only that an observed flip was predicted to be
          possible (implication, not equivalence).

        This treats absence-of-evidence correctly: not evidence of
        absence for sign flips, since measurement of flips requires
        high-resolution dense data that most historical cases lack.
        """
        nr_ok = (self.observed_n_r_amplified == self.predicted_n_r_high)
        # observed flip implies framework predicted flip
        flip_ok = (not self.sign_flip_observed) or self.sign_flip_predicted
        return nr_ok and flip_ok


def compare_case(case: HistoricalCase) -> CaseComparison:
    """Run the framework against a case's DURING context and build
    a structured comparison. This is the anchor the empirical work
    loads into.

    No numerics are compared against extracted historical K values
    because those values are placeholders. Only qualitative shape.
    """
    pred = predict(case.context_during)

    # Did the case record K[N][R] amplification during the event?
    observed_n_r_amplified = any(
        o.term_i == "N" and o.term_j == "R"
        and o.shift in (DynamicShift.AMPLIFIED, DynamicShift.AMPLIFIED_STRONG)
        for o in case.observed_dynamics
    )
    # Framework: predicts "high K[N][R]" when Minsky coefficient is
    # elevated (>= 1.5) OR we are in NEAR_COLLAPSE regime.
    predicted_n_r_high = (
        pred.minsky >= 1.5
        or case.context_during.state == StateRegime.NEAR_COLLAPSE
    )

    sign_flip_observed = any(
        o.shift == DynamicShift.SIGN_FLIPPED
        for o in case.observed_dynamics
    )

    return CaseComparison(
        case=case,
        prediction=pred,
        observed_n_r_amplified=observed_n_r_amplified,
        predicted_n_r_high=predicted_n_r_high,
        sign_flip_observed=sign_flip_observed,
        sign_flip_predicted=pred.has_sign_flips,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_case_report(c: CaseComparison) -> None:
    case = c.case
    print(f"\n{'=' * 78}")
    print(f"{case.name}")
    print(f"  period:     {case.period}")
    print(f"  location:   {case.location}")
    print(f"  confidence: {case.historical_confidence:.2f}")
    print(f"{'-' * 78}")
    print(f"  framework prediction for DURING context:")
    print(f"    Minsky:   {c.prediction.minsky:.2f}x")
    print(f"    Magnitude:{c.prediction.coupling_magnitude:.2f}")
    print(f"    Sign flips:{c.prediction.has_sign_flips}")
    print(f"  observed:")
    print(f"    K[N][R] amplified:        {c.observed_n_r_amplified}")
    print(f"    sign flip recorded:       {c.sign_flip_observed}")
    print(f"  framework qualitative match:  {c.qualitative_match}")


if __name__ == "__main__":
    print("=" * 78)
    print("money_signal / historical_cases")
    print("=" * 78)
    matches = 0
    for case in ALL_CASES:
        cmp = compare_case(case)
        _print_case_report(cmp)
        if cmp.qualitative_match:
            matches += 1
    print(f"\n{'=' * 78}")
    print(f"qualitative match: {matches}/{len(ALL_CASES)} cases")
    print("=" * 78)
