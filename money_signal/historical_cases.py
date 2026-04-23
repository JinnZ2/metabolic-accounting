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


# ---------------------------------------------------------------------------
# Extended anchor cases (AUDIT_18)
# ---------------------------------------------------------------------------

BITCOIN_FLASH_CRASHES = HistoricalCase(
    name="Bitcoin flash crashes — digital speculative cascades",
    period="2013 / 2017 / 2021-22 (selected episodes)",
    location="global crypto markets",
    context_pre=DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.ATOMIZED_MARKET,
        attribution=AttributedValue.SPECULATIVE_CLAIM,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.STRESSED,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.ATOMIZED_MARKET,
        attribution=AttributedValue.SPECULATIVE_CLAIM,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.NEAR_COLLAPSE,
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.ATOMIZED_MARKET,
        attribution=AttributedValue.SPECULATIVE_CLAIM,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.RECOVERING,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="N", term_j="R",
            shift=DynamicShift.AMPLIFIED_STRONG,
            evidence=(
                "reversal reliability shocks (exchange outages, stablecoin "
                "de-peg, Terra/UST collapse) trigger near-total acceptance "
                "collapse on minute-scale; no substrate floor, no sacred "
                "floor, no institutional backstop"
            ),
            provenance=empirical(
                source_refs=[
                    "Gandal, Hamrick, Moore & Oberman 2018, 'Price "
                    "Manipulation in the Bitcoin Ecosystem', JME 95",
                    "Liu, Tsyvinski & Wu 2022, 'Common Risk Factors in "
                    "Cryptocurrency', Journal of Finance 77(3)",
                    "Gorton & Zhang 2023, 'Taming Wildcat Stablecoins', "
                    "University of Chicago Law Review 90(3)",
                ],
                rationale=(
                    "reflexive K[N][R] dynamics directly documented in "
                    "the crypto-microstructure literature; Terra/UST 2022 "
                    "is the cleanest anchor for a substrate-less speculative "
                    "collapse"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.AMPLIFIED_STRONG,
            evidence=(
                "infrastructure coupling: exchange hot-wallet compromises, "
                "chain reorganizations, and stablecoin-reserve opacity all "
                "map directly to README claim #9 (DIGITAL substrate "
                "amplifies K[R][N])"
            ),
            provenance=placeholder(
                rationale=(
                    "qualitative pattern widely reported; extraction of "
                    "specific infrastructure-failure → acceptance-drop "
                    "windows not performed here"
                ),
                retirement_path=(
                    "event-study around Mt. Gox 2014, Binance outages, "
                    "USDC March 2023 de-peg with orderbook + on-chain "
                    "settlement data"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Gandal, Hamrick, Moore & Oberman 2018",
        "Liu, Tsyvinski & Wu 2022",
        "Gorton & Zhang 2023",
    ],
    historical_confidence=0.75,
    notes=(
        "Short-period anchors rather than a sustained regime. Each "
        "flash crash is its own near-collapse episode. Tests README "
        "claim #4 (SPECULATIVE_CLAIM amplifies K[N][R]) and claim #9 "
        "(DIGITAL substrate amplifies K[R][N]) in the same context. "
        "CulturalScope is ATOMIZED_MARKET, not INSTITUTIONAL — crypto "
        "markets have no shared institutional coordination mechanism."
    ),
)


ROMAN_DENARIUS_DEBASEMENT = HistoricalCase(
    name="Roman denarius debasement — multi-generational metal slide",
    period="~200 BCE - 270 CE",
    location="Roman Empire",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.COMMODITY_BACKED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.HEALTHY,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.STRESSED,
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.METAL,
        state=StateRegime.NEAR_COLLAPSE,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.DAMPED_STRONG,
            evidence=(
                "silver content in the denarius fell from ~95% under "
                "Augustus to ~50% by 200 CE to ~5% by 268 CE; reversal "
                "reliability declined continuously across that arc"
            ),
            provenance=empirical(
                source_refs=[
                    "Harl 1996, 'Coinage in the Roman Economy, 300 BC-700 AD'",
                    "Duncan-Jones 1994, 'Money and Government in the "
                    "Roman Empire'",
                    "Butcher & Ponting 2014, 'The Metallurgy of Roman "
                    "Silver Coinage: From the Reform of Nero to the Reform "
                    "of Trajan'",
                ],
                rationale=(
                    "silver-content series from X-ray fluorescence studies "
                    "is the gold standard for this case"
                ),
                scope_caveat=(
                    "silver content is a proxy for monetary reliability; "
                    "the actual reliability dynamic involves taxation "
                    "policy, legion pay, and tributary economics that the "
                    "metal-content alone does not capture"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="N", term_j="R",
            shift=DynamicShift.AMPLIFIED,
            evidence=(
                "provincial markets increasingly refused denarii or "
                "demanded payment by weight rather than face count; the "
                "Crisis of the Third Century (235-284 CE) is the "
                "near-collapse episode"
            ),
            provenance=empirical(
                source_refs=[
                    "Harper 2017, 'The Fate of Rome: Climate, Disease, "
                    "and the End of an Empire'",
                    "Temin 2013, 'The Roman Market Economy'",
                ],
                rationale=(
                    "network-acceptance collapse documented in the "
                    "Crisis of the Third Century literature"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Harl 1996",
        "Butcher & Ponting 2014",
        "Harper 2017",
    ],
    historical_confidence=0.85,
    notes=(
        "Centuries-long slow stress rather than a discrete event — "
        "useful as a counter-anchor to the rapid-onset cases (Weimar, "
        "GFC) and as the canonical pre-modern example of "
        "COMMODITY_BACKED → STATE_ENFORCED attribution drift. "
        "Diocletian's 301 CE Edict on Maximum Prices is the best-"
        "documented exception-pathway attempt under Roman money."
    ),
)


YAP_RAI_STONES = HistoricalCase(
    name="Yap rai stones — trust-ledger substrate, multi-generational",
    period="~1400 CE - present",
    location="Yap (Federated States of Micronesia)",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_post=None,
    observed_dynamics=[
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.UNCHANGED,
            evidence=(
                "rai stones frequently do not move physically; ownership "
                "is tracked in collective memory; one stone lies at the "
                "bottom of a lagoon and its value is unimpaired. The "
                "substrate is the community ledger, not the stone."
            ),
            provenance=empirical(
                source_refs=[
                    "Friedman 1991, 'The Island of Stone Money', "
                    "Federal Reserve Bank of San Francisco working paper",
                    "Gillilland 1975, 'The Stone Money of Yap: A "
                    "Numismatic Survey', Smithsonian Contributions to "
                    "Anthropology 23",
                ],
                rationale=(
                    "Friedman's monograph is the canonical economic "
                    "reading of Yap monetary structure"
                ),
                scope_caveat=(
                    "the case is an anchor for TRUST_LEDGER substrate; "
                    "extrapolating quantitative K values from Yap to "
                    "other reciprocity systems requires independent "
                    "confirmation per system"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Friedman 1991 (FRBSF WP)",
        "Gillilland 1975 Smithsonian",
    ],
    historical_confidence=0.80,
    notes=(
        "COUNTER-EXAMPLE. The canonical TRUST_LEDGER + "
        "RECIPROCITY_TOKEN + HIGH_RECIPROCITY anchor. Stable across "
        "multiple centuries without a near-collapse episode. Tests "
        "README claim #3 (reciprocity damping) directly: the composed "
        "Minsky coefficient for this context is the highest across "
        "the cases in this file, but the coupling MAGNITUDE is the "
        "lowest. Form preserved, amplitude damped — the signature of "
        "substrate-grounded reciprocity."
    ),
)


KULA_RING_EXCHANGE = HistoricalCase(
    name="Kula ring — Melanesian reciprocity network",
    period="documented 1915 onward, antecedents pre-contact",
    location="Trobriand Islands and surrounding archipelago",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_post=None,
    observed_dynamics=[
        ObservedDynamic(
            term_i="N", term_j="N",
            shift=DynamicShift.UNCHANGED,
            evidence=(
                "soulava necklaces and mwali armshells circulate in fixed "
                "directions around the ring; the carriers' prestige is "
                "the substrate. Direct commodity exchange (gimwali) is "
                "explicitly separated from kula exchange."
            ),
            provenance=empirical(
                source_refs=[
                    "Malinowski 1922, 'Argonauts of the Western Pacific'",
                    "Damon 1980, 'The Kula and Generalised Exchange: "
                    "Considering Some Unconsidered Aspects of The "
                    "Elementary Structures of Kinship', Man 15(2)",
                    "Leach & Leach eds. 1983, 'The Kula: New Perspectives "
                    "on Massim Exchange'",
                ],
                rationale=(
                    "Malinowski's ethnography is the foundational source; "
                    "the 1983 volume updates the analysis through the "
                    "1980s."
                ),
                scope_caveat=(
                    "indigenous-system data; cross-cultural extrapolation "
                    "of framework K values would misread the source "
                    "ethnography. The case anchors the existence of "
                    "TRUST_LEDGER monetary systems, not quantitative "
                    "calibration of them."
                ),
            ),
        ),
    ],
    primary_refs=[
        "Malinowski 1922",
        "Damon 1980",
        "Leach & Leach 1983",
    ],
    historical_confidence=0.80,
    notes=(
        "COUNTER-EXAMPLE (paired with YAP_RAI_STONES). Separates the "
        "claim that RECIPROCITY_TOKEN attribution + TRUST_LEDGER "
        "substrate CAN exist stably for generations — refuting any "
        "implicit framework bias that 'money must be commodity-backed "
        "or state-enforced to persist.' Cross-cultural corroboration "
        "for README claim #3 (reciprocity damping)."
    ),
)


# ---------------------------------------------------------------------------
# Extended anchor cases (AUDIT_20 — additional reciprocity counter-examples)
# ---------------------------------------------------------------------------

HAUDENOSAUNEE_WAMPUM = HistoricalCase(
    name="Haudenosaunee wampum — diplomatic + ledger substrate",
    period="~1450 CE (Great Law) - present",
    location="Haudenosaunee Confederacy (Six Nations)",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_post=None,
    observed_dynamics=[
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.UNCHANGED,
            evidence=(
                "wampum belts served simultaneously as treaty records, "
                "condolence protocol instruments, and mnemonic "
                "structure for clan governance. Value was in the "
                "recorded relationship, not the shell beads."
            ),
            provenance=empirical(
                source_refs=[
                    "Fenton 1998, 'The Great Law and the Longhouse: A "
                    "Political History of the Iroquois Confederacy'",
                    "Muller 2008, 'Recovering Wampum as a Living "
                    "Tradition', Ethnohistory 55(1)",
                    "Williams 1997, 'Linking Arms Together: American "
                    "Indian Treaty Visions of Law and Peace, 1600-1800'",
                ],
                rationale=(
                    "Fenton's political history is the canonical "
                    "English-language source; Muller and Williams "
                    "track the diplomatic-ledger function through "
                    "colonial-treaty contact"
                ),
                scope_caveat=(
                    "source literature is primarily English-language "
                    "secondary scholarship; Haudenosaunee primary "
                    "sources (oral tradition, Condolence Council "
                    "records) carry information not fully captured "
                    "in the cited works"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="N", term_j="N",
            shift=DynamicShift.UNCHANGED,
            evidence=(
                "belts were regularly re-read at Confederacy meetings "
                "to refresh network acceptance of treaty terms; the "
                "reading protocol IS the maintenance mechanism"
            ),
            provenance=placeholder(
                rationale=(
                    "the maintenance protocol is documented "
                    "qualitatively; K-structure quantification has "
                    "not been extracted"
                ),
                retirement_path=(
                    "ethnohistorical analysis of Condolence Council "
                    "protocol frequency vs. treaty stability in the "
                    "1600-1800 archival record"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Fenton 1998",
        "Muller 2008",
        "Williams 1997",
    ],
    historical_confidence=0.75,
    notes=(
        "COUNTER-EXAMPLE. A TRUST_LEDGER + RECIPROCITY_TOKEN + "
        "HIGH_RECIPROCITY anchor alongside Yap rai and Kula ring. "
        "The wampum case is distinctive for carrying an explicit "
        "political-governance function on the same substrate that "
        "carries the economic-exchange function — the two are not "
        "separated. This is a feature of the attribution, not a "
        "failure mode: RECIPROCITY_TOKEN substrates can be "
        "multi-functional in a way STATE_ENFORCED ones are not."
    ),
)


POTLATCH_SUPPRESSION = HistoricalCase(
    name="Potlatch ceremony — legal suppression and post-repeal recovery",
    period="1884 (Canada) / 1885 (US Indian Affairs) - 1951 repeal",
    location="Pacific Northwest Coast (Kwakwaka'wakw, Haida, Tlingit et al.)",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_during=DimensionalContext(
        # DURING context = the suppression period. Colonial
        # prohibition acts as an external regime that attempts
        # to invalidate the substrate ledger entirely — no
        # near-collapse in the monetary-dynamics sense, but the
        # enforcement regime was near-collapse for the
        # substrate-producer observer.
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.STRESSED,
    ),
    context_post=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.RECOVERING,
    ),
    observed_dynamics=[
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.DAMPED_STRONG,
            evidence=(
                "overt ceremonial potlatch was criminalized; the "
                "ledger-refreshment function moved underground or "
                "partial (smaller-scale gifts, disguised rituals); "
                "confiscated regalia was catalogued into museum "
                "collections without ledger-context metadata"
            ),
            provenance=empirical(
                source_refs=[
                    "Cole & Chaikin 1990, 'An Iron Hand Upon the "
                    "People: The Law Against the Potlatch on the "
                    "Northwest Coast'",
                    "Bracken 1997, 'The Potlatch Papers: A Colonial "
                    "Case History'",
                    "U'mista Cultural Society 1975-present, "
                    "Repatriation Archive Project",
                ],
                rationale=(
                    "Cole & Chaikin is the canonical legal and "
                    "administrative history; Bracken centers the "
                    "colonial archive itself; U'mista provides the "
                    "primary-source repatriation record"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="R", term_j="N",
            shift=DynamicShift.DAMPED_STRONG,
            evidence=(
                "post-1951 repeal, recovery of the ceremony proceeded "
                "unevenly; multi-generational gap in active practice "
                "is visible in elder-led revival efforts since the "
                "1970s. README hysteresis claim #2 is directly "
                "visible — the recovering regime does not restore "
                "the pre-suppression coupling."
            ),
            provenance=empirical(
                source_refs=[
                    "Harkin 1997, 'The Heiltsuks: Dialogues of Culture "
                    "and History on the Northwest Coast'",
                    "U'mista Cultural Society reports on ceremonial "
                    "revival, 1975-present",
                ],
                rationale=(
                    "direct ethnohistorical observation of hysteresis "
                    "between pre-suppression and post-repeal regimes"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Cole & Chaikin 1990",
        "Bracken 1997",
        "U'mista Cultural Society",
    ],
    historical_confidence=0.85,
    notes=(
        "Third counter-example, but NOT a clean steady-state case "
        "like Yap or Kula — this one documents what happens when an "
        "external regime criminalizes the substrate ledger. Tests "
        "README claim #2 (hysteresis: recovering regime has damped "
        "coupling vs pre-suppression) at a political-regime-induced "
        "scale rather than a monetary-dynamics scale. The suppression "
        "period is encoded as STRESSED to distinguish from "
        "NEAR_COLLAPSE monetary events; the state of the substrate "
        "ledger itself approached collapse for substrate-producer "
        "observers, and that experience remains in living memory."
    ),
)


# ---------------------------------------------------------------------------
# Extended anchor cases (AUDIT_22 — additional reciprocity + shell-money)
# ---------------------------------------------------------------------------

ANDEAN_AYNI = HistoricalCase(
    name="Andean ayni — labor-reciprocity ledger across generations",
    period="pre-Inca antecedents - present",
    location="Andean highlands (Peru, Bolivia, Ecuador)",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_during=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_post=None,
    observed_dynamics=[
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.UNCHANGED,
            evidence=(
                "ayni labor debt tracks symmetric reciprocal work "
                "obligations at household and community levels; "
                "obligations persist across generations, with the "
                "ledger held in collective memory and confirmed at "
                "agricultural-cycle events (planting, harvest, "
                "house-building)"
            ),
            provenance=empirical(
                source_refs=[
                    "Alberti & Mayer 1974, 'Reciprocidad e intercambio "
                    "en los Andes peruanos', Instituto de Estudios "
                    "Peruanos",
                    "Mayer 2002, 'The Articulated Peasant: Household "
                    "Economies in the Andes', Westview Press",
                    "Harris 1985, 'Ecological Duality and the Role of "
                    "the Center: Northern Potosi', in Masuda ed., "
                    "Andean Ecology and Civilization",
                ],
                rationale=(
                    "Alberti & Mayer established the canonical "
                    "analytical framing; Mayer 2002 synthesizes 30 "
                    "years of field data"
                ),
                scope_caveat=(
                    "Spanish-language primary literature carries "
                    "detail not fully captured in English secondary "
                    "sources; framework quantitative claims about "
                    "ayni should cite the Spanish-language corpus"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="N", term_j="N",
            shift=DynamicShift.UNCHANGED,
            evidence=(
                "minka communal-labor mobilization (larger-scale than "
                "ayni) and ayni pairwise-labor reciprocity coexist; "
                "acceptance network expands and contracts with "
                "seasonal work cycles"
            ),
            provenance=placeholder(
                rationale=(
                    "pattern documented qualitatively; quantification "
                    "of the acceptance-network expansion/contraction "
                    "cycle not extracted here"
                ),
                retirement_path=(
                    "cross-reference IEP (Instituto de Estudios "
                    "Peruanos) household-labor panel data with "
                    "seasonal agricultural cycle records"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Alberti & Mayer 1974",
        "Mayer 2002",
        "Harris 1985",
    ],
    historical_confidence=0.80,
    notes=(
        "COUNTER-EXAMPLE (fourth in the set, paired with Yap rai, "
        "Kula ring, Haudenosaunee wampum). Distinctive for tracking "
        "labor-reciprocity rather than shell/object-reciprocity. "
        "Ayni demonstrates that the RECIPROCITY_TOKEN + TRUST_LEDGER "
        "+ HIGH_RECIPROCITY combination works for LABOR substrate "
        "directly, not only for material tokens. Tests framework "
        "claim #3 (reciprocity damping) on a distinct substrate "
        "type from the object-based counter-examples."
    ),
)


TAMBU_TOLAI = HistoricalCase(
    name="Tambu shell-money — Tolai community persistence under dual regime",
    period="pre-contact - present (documented intensively 1960s-2000s)",
    location="Tolai communities, New Britain (Papua New Guinea)",
    context_pre=DimensionalContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_during=DimensionalContext(
        # Dual-currency regime: tambu coexists with PNG kina
        # (official currency) in Tolai communities. The tambu
        # substrate is TRUST_LEDGER, kina is the DIGITAL fiat layer.
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.HIGH_RECIPROCITY,
        attribution=AttributedValue.RECIPROCITY_TOKEN,
        observer=ObserverPosition.SUBSTRATE_PRODUCER,
        substrate=Substrate.TRUST_LEDGER,
        state=StateRegime.HEALTHY,
    ),
    context_post=None,
    observed_dynamics=[
        ObservedDynamic(
            term_i="R", term_j="R",
            shift=DynamicShift.UNCHANGED,
            evidence=(
                "tambu strings (loloi) are prepared for major life "
                "events — marriages, deaths, matambu (distribution "
                "ceremonies) — and accumulate across decades; the "
                "reversal reliability is anchored to community "
                "witness, not to the physical shells themselves"
            ),
            provenance=empirical(
                source_refs=[
                    "Epstein 1969, 'Matupit: Land, Politics, and "
                    "Change among the Tolai of New Britain'",
                    "Errington & Gewertz 1987, 'Cultural Alternatives "
                    "and a Feminist Anthropology'",
                    "Martin 2013, 'The Death of the Big Men and the "
                    "Rise of the Big Shots: Custom and Conflict in "
                    "East New Britain', Berghahn",
                ],
                rationale=(
                    "Epstein 1969 is the foundational long-term "
                    "study; Martin 2013 updates through the 2000s "
                    "dual-regime era"
                ),
                scope_caveat=(
                    "Tolai case specifically; other PNG shell-money "
                    "systems (kina in other groups, bakia, abudenit) "
                    "have overlapping but distinct dynamics"
                ),
            ),
        ),
        ObservedDynamic(
            term_i="N", term_j="R",
            shift=DynamicShift.DAMPED,
            evidence=(
                "dual-regime stability: tambu acceptance persists "
                "within Tolai ceremonial contexts while kina "
                "(national fiat) handles inter-group trade. Each "
                "substrate damps the other's coupling dynamics in "
                "its own domain — the two-substrate arrangement "
                "itself is a stability mechanism"
            ),
            provenance=placeholder(
                rationale=(
                    "dual-currency stability is documented "
                    "qualitatively; formal K-coupling decomposition "
                    "between tambu-domain and kina-domain transactions "
                    "not extracted here"
                ),
                retirement_path=(
                    "Bank of PNG regional monetary reports + "
                    "anthropological field studies on tambu/kina "
                    "conversion rates during the 2008-2012 "
                    "commodity-boom period"
                ),
            ),
        ),
    ],
    primary_refs=[
        "Epstein 1969",
        "Errington & Gewertz 1987",
        "Martin 2013",
    ],
    historical_confidence=0.75,
    notes=(
        "COUNTER-EXAMPLE with a twist: tambu coexists WITH modern "
        "fiat (PNG kina) rather than standing alone. The dual-regime "
        "context is structurally informative — it demonstrates that "
        "TRUST_LEDGER substrates do not require monopoly to persist; "
        "they can occupy a coordination niche alongside a different-"
        "substrate instrument. Relevant to README observations about "
        "reciprocity systems in contact with fiat economies."
    ),
)


ALL_CASES: List[HistoricalCase] = [
    WEIMAR_1921_1923,
    ZIMBABWE_2007_2009,
    GFC_2008,
    CYPRUS_2013,
    ARGENTINA_2001_2002,
    # AUDIT_18 extensions:
    BITCOIN_FLASH_CRASHES,
    ROMAN_DENARIUS_DEBASEMENT,
    YAP_RAI_STONES,
    KULA_RING_EXCHANGE,
    # AUDIT_20 extensions:
    HAUDENOSAUNEE_WAMPUM,
    POTLATCH_SUPPRESSION,
    # AUDIT_22 extensions:
    ANDEAN_AYNI,
    TAMBU_TOLAI,
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
    # Framework predicts "K[N][R] amplified" when:
    #   - state is NEAR_COLLAPSE, OR
    #   - Minsky ratio is elevated (>= 1.5) AND coupling_magnitude
    #     is non-trivial (>= 0.3).
    #
    # The magnitude filter prevents counter-examples like Yap rai
    # stones and the Kula ring (reciprocity damping, Minsky ~ 1.68
    # with magnitude ~ 0.13) from being mis-labeled as "amplified."
    # High Minsky ratio under low magnitude means "asymmetry form
    # preserved but damped," which is the README's claim #3 signature,
    # not the claim #4 amplification signature.
    predicted_n_r_high = (
        case.context_during.state == StateRegime.NEAR_COLLAPSE
        or (pred.minsky >= 1.5 and pred.coupling_magnitude >= 0.3)
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
