"""
investment_signal/historical_cases.py

Anchor cases for the investment_signal framework — parallel to
money_signal/historical_cases.py, using the same honest-placeholder
discipline.

What this module IS:
  - A schema for documented investment-regime cases with
    pre/during/post InvestmentContexts and recorded qualitative
    failure modes drawn from the framework's own tag vocabulary
    (signal_failure_reasons).
  - Five anchor cases spanning different failure signatures:
    Enron 2001 (SYNTHETIC reverse causation), MBS 2008 (multi-layer
    substrate opacity), ZIRP 2009-2021 (investment under stressed
    money), Gig economy (TIME/ATTENTION extraction), and Community
    Land Trusts (counter-example: relational capital preserved
    under monetary pressure).
  - A comparison function that runs the framework's predicted
    failure-tag set for each case's DURING context against the
    observed tags.

What this module IS NOT:
  - A source of calibrated quantitative factor values. Every
    ObservedInvestmentFailure carries a typed Provenance
    (EMPIRICAL with source_refs, or PLACEHOLDER with a named
    retirement_path). Fabricating numeric C[i][j] or R[i][j]
    values under the empirical label would be exactly the failure
    mode the AUDIT_07 Provenance taxonomy was built to prevent.

See docs/AUDIT_14.md Part B for the intake rationale.

CC0. Stdlib-only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from investment_signal.dimensions import (
    InvestmentContext, InvestmentSubstrate, InvestmentAttribution,
    DerivativeDistance, TimeBinding,
)
from investment_signal.substrate_vectors import SubstrateVector
from investment_signal.coupling import (
    assemble_investment_signal, signal_failure_reasons,
)
from money_signal.dimensions import (
    DimensionalContext as MoneyContext,
    TemporalScope, CulturalScope, AttributedValue,
    ObserverPosition, Substrate, StateRegime,
)
from term_audit.provenance import (
    Provenance, empirical, theoretical, placeholder,
)


# ---------------------------------------------------------------------------
# Failure-tag vocabulary
# ---------------------------------------------------------------------------

# The eight tags produced by signal_failure_reasons(). Reproduced here
# so that ObservedInvestmentFailure entries can be validated against
# the canonical set without a runtime import cycle.
VALID_FAILURE_TAGS: Tuple[str, ...] = (
    "money_dependency_broken",
    "money_near_collapse",
    "money_reflexive_sign_flips",
    "liquidity_illusion",
    "infrastructure_depreciation_trap",
    "financialized_reverse_causation",
    "substrate_invisible_at_distance",
    "substrate_abstraction_destroys_nature",
)


@dataclass(frozen=True)
class ObservedInvestmentFailure:
    """One historically-documented failure mode for a case, in the
    framework's own tag vocabulary."""
    failure_tag: str
    evidence: str
    provenance: Provenance

    def __post_init__(self):
        if self.failure_tag not in VALID_FAILURE_TAGS:
            raise ValueError(
                f"unknown failure tag {self.failure_tag!r}; "
                f"expected one of {VALID_FAILURE_TAGS}"
            )


@dataclass
class HistoricalInvestmentCase:
    """A documented investment regime usable as a framework anchor."""
    name: str
    period: str
    location: str

    context_pre: InvestmentContext
    context_during: InvestmentContext
    context_post: Optional[InvestmentContext]

    # Characteristic input/expected vectors for the case — used by
    # `compare_case()` to run the framework's signal pipeline.
    # These are qualitative shapes ("MONEY-in expecting MONEY-out",
    # "TIME+LABOR expecting MONEY"), not fit quantities.
    characteristic_input: SubstrateVector
    characteristic_expected: SubstrateVector

    observed_failures: Tuple[ObservedInvestmentFailure, ...] = ()
    primary_refs: List[str] = field(default_factory=list)
    historical_confidence: float = 0.0
    notes: str = ""


# ---------------------------------------------------------------------------
# Anchor cases
# ---------------------------------------------------------------------------

_HEALTHY_FIAT = MoneyContext(
    temporal=TemporalScope.SEASONAL,
    cultural=CulturalScope.INSTITUTIONAL,
    attribution=AttributedValue.STATE_ENFORCED,
    observer=ObserverPosition.TOKEN_HOLDER_THIN,
    substrate=Substrate.DIGITAL,
    state=StateRegime.HEALTHY,
)
_STRESSED_FIAT = MoneyContext(
    temporal=TemporalScope.SEASONAL,
    cultural=CulturalScope.INSTITUTIONAL,
    attribution=AttributedValue.STATE_ENFORCED,
    observer=ObserverPosition.TOKEN_HOLDER_THIN,
    substrate=Substrate.DIGITAL,
    state=StateRegime.STRESSED,
)
_NEAR_COLLAPSE_FIAT = MoneyContext(
    temporal=TemporalScope.TRANSACTION,
    cultural=CulturalScope.INSTITUTIONAL,
    attribution=AttributedValue.STATE_ENFORCED,
    observer=ObserverPosition.TOKEN_HOLDER_THIN,
    substrate=Substrate.DIGITAL,
    state=StateRegime.NEAR_COLLAPSE,
)
# ZIRP-era: unit not in crisis, but investment horizons extended while
# policy rate at zero → evaluate at generational temporal scope to
# surface the binding-vs-scope mismatch claim #11 predicts.
_ZIRP_MONEY = MoneyContext(
    temporal=TemporalScope.GENERATIONAL,
    cultural=CulturalScope.INSTITUTIONAL,
    attribution=AttributedValue.STATE_ENFORCED,
    observer=ObserverPosition.TOKEN_HOLDER_THIN,
    substrate=Substrate.DIGITAL,
    state=StateRegime.STRESSED,
)


ENRON_2001 = HistoricalInvestmentCase(
    name="Enron — synthetic mark-to-market collapse",
    period="2000-2001",
    location="United States",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.SPECULATION_ON_SPECULATION,
        derivative_distance=DerivativeDistance.DERIVATIVE,
        time_binding=TimeBinding.SHORT_CYCLE,
    ),
    context_during=InvestmentContext(
        money_context=_STRESSED_FIAT,
        attribution=InvestmentAttribution.SPECULATION_ON_SPECULATION,
        derivative_distance=DerivativeDistance.SYNTHETIC,
        time_binding=TimeBinding.SHORT_CYCLE,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 100000.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 150000.0,
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="financialized_reverse_causation",
            evidence=(
                "mark-to-market accounting on projections of projections "
                "came to govern operational decisions; SPE structures "
                "existed to meet financial-layer targets that had no "
                "underlying substrate"
            ),
            provenance=empirical(
                source_refs=[
                    "McLean & Elkind 2003, 'The Smartest Guys in the Room'",
                    "Powers Report 2002 (Special Investigative Committee)",
                    "Benston & Hartgraves 2002, 'Enron: what happened and "
                    "what we can learn from it', JAE 21(2)",
                ],
                rationale=(
                    "documented in the Special Investigative Committee "
                    "report and independent academic analyses of the "
                    "SPE structure"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="substrate_invisible_at_distance",
            evidence=(
                "Arthur Andersen + Enron executives + outside investors "
                "all operated with different views of what the SPE "
                "vehicles actually held; the substrate (real energy-"
                "trading positions and asset values) was opaque to at "
                "least the latter two"
            ),
            provenance=empirical(
                source_refs=[
                    "Powers Report 2002",
                    "SEC 2002 Cease and Desist Order",
                ],
                rationale=(
                    "substrate invisibility is the explicit finding of "
                    "both the internal committee and the SEC enforcement "
                    "actions"
                ),
            ),
        ),
    ),
    primary_refs=[
        "McLean & Elkind 2003",
        "Powers Report 2002",
        "Benston & Hartgraves 2002",
    ],
    historical_confidence=0.95,
    notes=(
        "Canonical SYNTHETIC derivative-distance failure case. The "
        "SPE structure routed around substrate visibility on purpose; "
        "the reverse-causation claim (financial layer governing "
        "substrate) is documented directly in the internal reports."
    ),
)


MBS_2008 = HistoricalInvestmentCase(
    name="Mortgage-backed securities — multi-layer opacity",
    period="2004-2008",
    location="United States / global",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.SPECULATIVE_BET,
        derivative_distance=DerivativeDistance.TWO_LAYER,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_during=InvestmentContext(
        # DURING classification covers the Sep 2008 terminal phase
        # where money_near_collapse was recorded — cross-references
        # money_signal/historical_cases.py::GFC_2008 context_during.
        money_context=_NEAR_COLLAPSE_FIAT,
        attribution=InvestmentAttribution.SPECULATIVE_BET,
        derivative_distance=DerivativeDistance.DERIVATIVE,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 1_000_000.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 1_080_000.0,
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="substrate_invisible_at_distance",
            evidence=(
                "tranche holders could not see individual mortgage "
                "quality; originators could not see ultimate holder "
                "concerns; ratings agencies methodologies did not "
                "adequately decompose into the underlying substrate"
            ),
            provenance=empirical(
                source_refs=[
                    "Gorton 2010, 'Slapped by the Invisible Hand: The "
                    "Panic of 2007'",
                    "FCIC 2011, 'The Financial Crisis Inquiry Report'",
                    "Levitin & Wachter 2012, 'The Great American Housing "
                    "Bubble', LHR",
                ],
                rationale=(
                    "substrate opacity is named directly in the FCIC "
                    "report findings and in Gorton's analysis of repo "
                    "market behavior"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="financialized_reverse_causation",
            evidence=(
                "secondary-market demand for MBS product drove "
                "origination standards down (ninja loans, stated "
                "income); the derivative demand governed the "
                "underlying-substrate sourcing"
            ),
            provenance=empirical(
                source_refs=[
                    "Mian & Sufi 2014, 'House of Debt'",
                    "Acharya et al. 2011, 'Guaranteed to Fail'",
                ],
                rationale=(
                    "reverse-causation from securitization demand to "
                    "origination standards is the central empirical "
                    "finding of Mian-Sufi"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="money_near_collapse",
            evidence=(
                "MBS price collapse triggered the broader 2008 "
                "liquidity-collapse cycle; by Sep 2008 the monetary "
                "layer itself was in near-collapse regime"
            ),
            provenance=empirical(
                source_refs=[
                    "FCIC 2011",
                    "Gorton 2010",
                ],
                rationale="cross-referenced with money_signal/historical_cases.py GFC_2008",
            ),
        ),
    ),
    primary_refs=[
        "Gorton 2010",
        "FCIC 2011",
        "Mian & Sufi 2014",
    ],
    historical_confidence=0.95,
    notes=(
        "Claims #16 (visibility monotone), #17 (cascade monotone), #18 "
        "(reverse causation monotone) all in play here. MBS 2008 is "
        "the canonical case where multi-layer derivative distance "
        "produced both the visibility failure and the reverse-causation "
        "failure simultaneously."
    ),
)


# ---------------------------------------------------------------------------
# ZIRP decomposition (AUDIT_20 § B): splitting the single ZIRP_2009_2021
# anchor into three sub-cases by investor type. AUDIT_14 Part B had
# documented ZIRP as the single framework-match outlier because a
# single-case encoding could not simultaneously fire liquidity_illusion
# (retail side) AND financialized_reverse_causation (firm/structured
# side). Three sub-cases each match their own internally consistent
# failure set.
# ---------------------------------------------------------------------------

ZIRP_RETAIL_DIVERSIFIED = HistoricalInvestmentCase(
    name="ZIRP era — retail diversified portfolio (liquidity illusion)",
    period="2009-2021",
    location="United States / developed world",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.ONE_LAYER,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_during=InvestmentContext(
        # Retail side of ZIRP: SHORT_CYCLE binding against generational
        # money scope is exactly claim #11's liquidity-illusion shape.
        # TWO_LAYER distance reflects the retail fund-of-funds pattern
        # where the investor interacts with a broker interacting with
        # a fund — below the 0.5 reverse-causation threshold.
        money_context=_ZIRP_MONEY,
        attribution=InvestmentAttribution.SPECULATIVE_BET,
        derivative_distance=DerivativeDistance.TWO_LAYER,
        time_binding=TimeBinding.SHORT_CYCLE,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 100000.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 170000.0,
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="liquidity_illusion",
            evidence=(
                "retail open-ended funds, target-date funds, and "
                "brokerage-tier products present daily/weekly "
                "liquidity while holding multi-year underlyings that "
                "would take quarters to unwind at scale without "
                "price impact"
            ),
            provenance=placeholder(
                rationale=(
                    "qualitative pattern documented; retail-side "
                    "quantified fund-vs-underlying liquidity-gap "
                    "series not extracted here"
                ),
                retirement_path=(
                    "ICI fund-flow data + SEC Form N-PORT liquidity "
                    "classification series 2018-present"
                ),
                deferred_cost="linear",
            ),
        ),
    ),
    primary_refs=[
        "Borio 2019 BIS Annual Economic Report",
        "Summers 2014 secular stagnation series",
    ],
    historical_confidence=0.80,
    notes=(
        "Retail-side sub-case of the ZIRP era. Isolates the "
        "liquidity-illusion failure so the framework's prediction "
        "matches cleanly at TWO_LAYER distance. See ZIRP_PRIVATE_EQUITY "
        "and ZIRP_CLO_STRUCTURED for the firm-level and structured "
        "sub-cases that carry the reverse-causation failure the "
        "retail case cannot."
    ),
)


ZIRP_PRIVATE_EQUITY = HistoricalInvestmentCase(
    name="ZIRP era — private equity / buyback-driven reverse causation",
    period="2009-2021",
    location="United States / developed world",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.TWO_LAYER,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_during=InvestmentContext(
        # PE firm at DERIVATIVE distance: the fund-of-funds-of-firm
        # structure crosses the 0.5 reverse-causation threshold.
        # Attribution shifts to RENT_SEEKING because the
        # value-creation mechanism is increasingly buybacks, tax
        # arbitrage, and fee extraction rather than productive
        # operations — the Lazonick/Borio pattern.
        money_context=_ZIRP_MONEY,
        attribution=InvestmentAttribution.RENT_SEEKING,
        derivative_distance=DerivativeDistance.DERIVATIVE,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 10_000_000.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 22_000_000.0,
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="financialized_reverse_causation",
            evidence=(
                "asset prices drove firm capital-allocation decisions "
                "more tightly than fundamentals; buybacks at elevated "
                "multiples financed by cheap debt are the "
                "characteristic pattern, documented across S&P 500 "
                "constituents and mid-market PE portfolio companies"
            ),
            provenance=empirical(
                source_refs=[
                    "Lazonick 2014, 'Profits Without Prosperity', HBR",
                    "Borio 2019, BIS Annual Economic Report",
                    "Caballero, Farhi & Gourinchas 2017, 'Rents, "
                    "Technical Change, and Risk Premia', AER P&P",
                    "Appelbaum & Batt 2014, 'Private Equity at Work: "
                    "When Wall Street Manages Main Street'",
                ],
                rationale=(
                    "Lazonick/Borio document the market-to-operational "
                    "reverse causation at public-equity level; "
                    "Appelbaum & Batt extend the finding to the PE "
                    "portfolio-company level"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="substrate_invisible_at_distance",
            evidence=(
                "LP investors in PE funds receive aggregated quarterly "
                "reports; fund-level performance cannot be decomposed "
                "to portfolio-company-level substrate trajectories by "
                "the LP; the LP-GP information asymmetry is "
                "structural"
            ),
            provenance=empirical(
                source_refs=[
                    "Phalippou 2020, 'An Inconvenient Fact: Private "
                    "Equity Returns & The Billionaire Factory'",
                    "ILPA Reporting Template (private equity industry "
                    "standard, 2011 onward)",
                ],
                rationale=(
                    "LP-GP information asymmetry is the primary "
                    "subject of Phalippou's analysis"
                ),
            ),
        ),
    ),
    primary_refs=[
        "Lazonick 2014",
        "Appelbaum & Batt 2014",
        "Phalippou 2020",
    ],
    historical_confidence=0.85,
    notes=(
        "Firm-level sub-case of ZIRP, isolates the reverse-causation "
        "failure at DERIVATIVE distance. Complements "
        "ZIRP_RETAIL_DIVERSIFIED (which carries liquidity illusion "
        "but not financialization) and ZIRP_CLO_STRUCTURED (which "
        "carries multiple failures at SYNTHETIC distance)."
    ),
)


ZIRP_CLO_STRUCTURED = HistoricalInvestmentCase(
    name="ZIRP era — leveraged-loan CLO (synthetic derivative distance)",
    period="2013-2021 (post-crisis CLO 2.0 era)",
    location="United States / global",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.SPECULATIVE_BET,
        derivative_distance=DerivativeDistance.DERIVATIVE,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_during=InvestmentContext(
        # CLO 2.0 at SYNTHETIC distance: tranche slices of collateral
        # pools of corporate loans held at stressed-money context.
        # Crosses every failure-mode threshold the framework defines.
        money_context=_ZIRP_MONEY,
        attribution=InvestmentAttribution.SPECULATION_ON_SPECULATION,
        derivative_distance=DerivativeDistance.SYNTHETIC,
        time_binding=TimeBinding.SHORT_CYCLE,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 50_000_000.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 58_000_000.0,
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="substrate_invisible_at_distance",
            evidence=(
                "equity-tranche holders of CLO 2.0 structures cannot "
                "see individual loan-level credit quality; originator "
                "covenants-lite documentation pushed originator-level "
                "substrate visibility further below investor horizon"
            ),
            provenance=empirical(
                source_refs=[
                    "Fitch 2019, 'Leveraged Finance Weekly' series "
                    "(covenants-lite documentation trend data)",
                    "Griffin & Nickerson 2023, 'Are CLO Collateral and "
                    "Tranche Ratings Disconnected?', RFS 36(6)",
                ],
                rationale=(
                    "Griffin & Nickerson directly document ratings-"
                    "methodology disconnection from underlying loan "
                    "credit performance"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="financialized_reverse_causation",
            evidence=(
                "demand for CLO collateral pushed originators toward "
                "looser underwriting to supply the tranche market "
                "— same reverse-causation pattern as 2006-era MBS but "
                "at the leveraged-loan layer"
            ),
            provenance=empirical(
                source_refs=[
                    "Griffin & Nickerson 2023",
                    "BIS 2018 Quarterly Review, 'The rise of "
                    "leveraged loans'",
                ],
                rationale=(
                    "BIS and Griffin & Nickerson both document the "
                    "demand-to-supply-standards causation"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="substrate_abstraction_destroys_nature",
            evidence=(
                "attention and time substrates of corporate management "
                "teams at acquired portfolio companies are compressed "
                "into quarterly IRR-optimization targets; long-horizon "
                "productive-capacity decisions foregone"
            ),
            provenance=placeholder(
                rationale=(
                    "qualitative pattern reported but cross-sector "
                    "productive-capacity-decision-delay metrics not "
                    "extracted here"
                ),
                retirement_path=(
                    "match PE-portfolio-company R&D spend against "
                    "industry-peer R&D over hold-period; Compustat + "
                    "Capital IQ linked datasets"
                ),
                deferred_cost="linear",
            ),
        ),
    ),
    primary_refs=[
        "Griffin & Nickerson 2023",
        "BIS 2018 Quarterly Review",
        "Fitch Leveraged Finance Weekly",
    ],
    historical_confidence=0.85,
    notes=(
        "Structured-credit sub-case of ZIRP at SYNTHETIC distance. "
        "Carries multiple failure modes simultaneously — the "
        "framework's claim #20 (SYNTHETIC is_financialized by "
        "definition) is directly visible."
    ),
)


GIG_ECONOMY = HistoricalInvestmentCase(
    name="Platform gig economy — TIME/ATTENTION extraction",
    period="2013-present",
    location="Global (Uber, DoorDash, Mechanical Turk, TaskRabbit, etc.)",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.DIRECT,
        time_binding=TimeBinding.IMMEDIATE,
    ),
    context_during=InvestmentContext(
        # DERIVATIVE distance captures platform algorithmic pricing
        # as a genuine financial layer on top of the platform-layer
        # above the actual service — the reverse-causation threshold
        # (claim #18) fires at reverse_causation >= 0.5, which
        # matches DERIVATIVE (0.60) not TWO_LAYER (0.30).
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.EXTRACTIVE_CLAIM,
        derivative_distance=DerivativeDistance.DERIVATIVE,
        time_binding=TimeBinding.IMMEDIATE,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.TIME: 40.0,          # hours/week
        InvestmentSubstrate.LABOR: 40.0,
        InvestmentSubstrate.ATTENTION: 20.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 800.0,        # weekly take-home
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="substrate_abstraction_destroys_nature",
            evidence=(
                "platform algorithms price TIME and ATTENTION as if "
                "they were commodities; TIME tolerance 0.30 and "
                "ATTENTION tolerance 0.20 in the framework match the "
                "documented erosion of worker autonomy and attentional "
                "load under algorithmic management"
            ),
            provenance=empirical(
                source_refs=[
                    "Rosenblat 2018, 'Uberland: How Algorithms Are "
                    "Rewriting the Rules of Work'",
                    "Rani & Furrer 2021, 'Digital Labour Platforms and "
                    "New Forms of Flexible Work', ILO",
                    "Dubal 2017, 'The Drive to Precarity: A Political "
                    "History of Work', Calif. L. Rev.",
                ],
                rationale=(
                    "direct empirical documentation of TIME/ATTENTION "
                    "extraction at the individual-worker level"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="financialized_reverse_causation",
            evidence=(
                "dynamic pricing algorithms govern when and where "
                "workers can earn; worker decisions are responses to "
                "the financial-layer signal rather than vice versa"
            ),
            provenance=empirical(
                source_refs=[
                    "Rosenblat 2018",
                    "Scholz 2016, 'Uberworked and Underpaid'",
                ],
                rationale=(
                    "reverse-causation from platform pricing to worker "
                    "action is the central claim of the algorithmic-"
                    "management literature"
                ),
            ),
        ),
    ),
    primary_refs=[
        "Rosenblat 2018",
        "Rani & Furrer 2021 ILO",
        "Dubal 2017",
    ],
    historical_confidence=0.85,
    notes=(
        "Tests claim #21 (time/attention cannot be derivatized without "
        "losing their nature) at the societal scale. The claim predicts "
        "that extending derivative distance over TIME and ATTENTION "
        "investments should produce measurable extraction; the gig-"
        "economy literature documents exactly that pattern. Money "
        "context is HEALTHY — the failure is in the investment layer, "
        "not monetary regime."
    ),
)


COMMUNITY_LAND_TRUSTS = HistoricalInvestmentCase(
    name="Community Land Trusts — relational capital preserved through time",
    period="1970-present",
    location="Global (New Communities 1969 US → ~300 CLTs in US + international)",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.DIRECT,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_during=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.RECIPROCAL_OBLIGATION,
        derivative_distance=DerivativeDistance.DIRECT,
        time_binding=TimeBinding.MULTI_GENERATIONAL,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.RELATIONAL_CAPITAL: 10.0,
        InvestmentSubstrate.RESOURCE: 1.0,       # land + housing stock
        InvestmentSubstrate.LABOR: 5.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.RELATIONAL_CAPITAL: 15.0,  # compounds in own substrate
        InvestmentSubstrate.RESOURCE: 1.0,             # stewarded, not depreciated
    }),
    observed_failures=(),  # counter-example: framework predicts few/no failures
    primary_refs=[
        "Davis 2010, 'The Community Land Trust Reader'",
        "DeFilippis 2004, 'Unmaking Goliath: Community Control in the "
        "Face of Global Capital'",
        "Grounded Solutions Network 2019, 'CLT Technical Manual'",
        "Swack 1997, 'Community Land Trusts', in Rethinking Housing",
    ],
    historical_confidence=0.80,
    notes=(
        "COUNTER-EXAMPLE. The framework's positive case: when "
        "derivative distance is DIRECT, time binding is MULTI_"
        "GENERATIONAL, and attribution is RECIPROCAL_OBLIGATION, "
        "no structural failure modes should fire. CLTs are the "
        "documented working example of this combination — claim #14 "
        "(relational capital has the highest binding modifier) and "
        "claim #8 (relational compounds in own substrate) are the "
        "direct theoretical basis for why CLTs persist under "
        "monetary-pressure conditions that wreck most long-horizon "
        "investment structures. Historical confidence reflects CLT "
        "survival data across the US over 50+ years."
    ),
)


# ---------------------------------------------------------------------------
# Extended anchor cases (AUDIT_18)
# ---------------------------------------------------------------------------

COLONIAL_RESOURCE_EXTRACTION = HistoricalInvestmentCase(
    name="Colonial resource-extraction investment (Dutch East India Company era)",
    period="1602-1799",
    location="Dutch / British / Iberian colonial networks",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.ONE_LAYER,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_during=InvestmentContext(
        # The DURING context models the chartered company at peak
        # derivative distance: investors in Amsterdam / London could
        # not see conditions in Banda, Ambon, or Bengal. SPECULATIVE_BET
        # attribution captures that shareholder-position returns were
        # bet on extraction outcomes the shareholders never directly
        # observed.
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.EXTRACTIVE_CLAIM,
        derivative_distance=DerivativeDistance.DERIVATIVE,
        time_binding=TimeBinding.MULTI_YEAR,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 1000.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 2500.0,
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="substrate_invisible_at_distance",
            evidence=(
                "VOC / EIC shareholders in Europe had zero direct view of "
                "the substrate being extracted (nutmeg monopoly enforced "
                "by Banda massacres 1621; opium cultivation in Bengal; "
                "spice plantations on Ambon). Factor-ship reports reached "
                "home months to years late; auditing was effectively "
                "impossible."
            ),
            provenance=empirical(
                source_refs=[
                    "De Vries & van der Woude 1997, 'The First Modern "
                    "Economy: Success, Failure, and Perseverance of the "
                    "Dutch Economy, 1500-1815'",
                    "Hanna 1978, 'Indonesian Banda: Colonialism and Its "
                    "Aftermath in the Nutmeg Islands'",
                    "Robins 2006, 'The Corporation that Changed the "
                    "World: How the East India Company Shaped the "
                    "Modern Multinational'",
                ],
                rationale=(
                    "colonial chartered-company substrate invisibility "
                    "is a canonical case in the history of finance; the "
                    "Banda massacres are the cleanest single-event "
                    "anchor for the substrate-extraction failure mode"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="financialized_reverse_causation",
            evidence=(
                "VOC dividend pressure drove quota increases on Banda "
                "nutmeg and Bengal opium — the financial-layer demand "
                "governed the substrate production level, not the "
                "substrate's capacity to produce sustainably"
            ),
            provenance=empirical(
                source_refs=[
                    "Adas 1974, 'The Burma Delta: Economic Development "
                    "and Social Change on an Asian Rice Frontier, "
                    "1852-1941'",
                    "Washbrook 1988, 'Progress and Problems: South "
                    "Asian Economic and Social History c. 1720-1860', "
                    "Modern Asian Studies 22(1)",
                ],
                rationale=(
                    "historiography directly documents dividend-pressure "
                    "→ extraction-rate causation from Amsterdam / "
                    "London board decisions to on-the-ground quotas"
                ),
            ),
        ),
    ),
    primary_refs=[
        "De Vries & van der Woude 1997",
        "Hanna 1978",
        "Robins 2006",
    ],
    historical_confidence=0.85,
    notes=(
        "The canonical DERIVATIVE-distance + EXTRACTIVE_CLAIM anchor. "
        "Attribution shifts from PRODUCTIVE_CAPACITY (early voyage "
        "financing) to EXTRACTIVE_CLAIM (established quota-driven "
        "extraction) as the chartered companies matured. Tests "
        "framework claim #16 (substrate visibility falls monotonically "
        "with derivative distance) and claim #18 (reverse causation "
        "rises monotonically with distance) across multi-century "
        "historical span."
    ),
)


RETIREMENT_401K_GENERATIONAL = HistoricalInvestmentCase(
    name="US 401(k) system — generational realization-rate divergence",
    period="1978 (Revenue Act) - present",
    location="United States",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.ONE_LAYER,
        time_binding=TimeBinding.GENERATIONAL,
    ),
    context_during=InvestmentContext(
        # Money at GENERATIONAL temporal (retirement horizon);
        # investor/fund binding at SHORT_CYCLE (quarterly redemption,
        # quarterly manager review). The binding × scope mismatch
        # is exactly claim #11's liquidity-illusion signature.
        money_context=_ZIRP_MONEY,
        attribution=InvestmentAttribution.SPECULATIVE_BET,
        derivative_distance=DerivativeDistance.TWO_LAYER,
        time_binding=TimeBinding.SHORT_CYCLE,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 50000.0,    # cumulative worker contribution
        InvestmentSubstrate.TIME: 40.0,        # decades of labor-time committed
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 500000.0,   # expected retirement balance
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="liquidity_illusion",
            evidence=(
                "401(k) presents as 'retirement security' (generational "
                "horizon) while operating at quarterly-redemption, "
                "quarterly-disclosure, quarterly-manager-review rhythm. "
                "Boomers benefited from 40+ years of institutional bull "
                "market that masked the structural mismatch; Millennials "
                "face higher valuations at entry and lower realized "
                "returns. The divergence is the mismatch surfacing."
            ),
            provenance=empirical(
                source_refs=[
                    "Munnell & Webb 2015, 'The Impact of Leakages from "
                    "401(k)s and IRAs', CRR WP 2015-2",
                    "Ghilarducci 2020, 'When I'm Sixty-Four: The Plot "
                    "Against Pensions and the Plan to Save Them'",
                    "Center for Retirement Research 2022, 'How Have "
                    "401(k)s Fared Across Cohorts?'",
                ],
                rationale=(
                    "CRR at Boston College publishes cohort-specific "
                    "realization data; Ghilarducci's analysis of the DB "
                    "→ DC pension shift documents the horizon mismatch"
                ),
                scope_caveat=(
                    "generational realization rates are heavily "
                    "confounded by individual contribution patterns, "
                    "early withdrawals, fee structures, and cohort-"
                    "specific labor-market conditions — this anchor "
                    "locks in the direction of the failure mode, not "
                    "a single summary number"
                ),
            ),
        ),
    ),
    primary_refs=[
        "Munnell & Webb 2015 CRR",
        "Ghilarducci 2020",
        "CRR cohort reports 2022",
    ],
    historical_confidence=0.75,
    notes=(
        "Tests claim #11 (liquidity illusion from short-binding / "
        "long-scope mismatch) at generational scale. 401(k) is an "
        "investment system DECLARED to serve a generational horizon "
        "(retirement security) while OPERATING at quarterly "
        "redemption, quarterly disclosure, quarterly manager-review "
        "rhythm. The boomer/millennial realization divergence is the "
        "empirical surfaced form of that mismatch."
    ),
)


# ---------------------------------------------------------------------------
# Extended anchor case (AUDIT_20)
# ---------------------------------------------------------------------------

CONGO_RUBBER_1885_1908 = HistoricalInvestmentCase(
    name="Congo Free State rubber extraction — extreme derivative distance",
    period="1885 (Berlin Conference) - 1908 (Belgian state takeover)",
    location="Congo Free State (Leopold II personal property regime)",
    context_pre=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.TWO_LAYER,
        time_binding=TimeBinding.SEASONAL,
    ),
    context_during=InvestmentContext(
        money_context=_HEALTHY_FIAT,
        attribution=InvestmentAttribution.EXTRACTIVE_CLAIM,
        derivative_distance=DerivativeDistance.SYNTHETIC,
        time_binding=TimeBinding.SHORT_CYCLE,
    ),
    context_post=None,
    characteristic_input=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 1000.0,
    }),
    characteristic_expected=SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 4000.0,
    }),
    observed_failures=(
        ObservedInvestmentFailure(
            failure_tag="substrate_invisible_at_distance",
            evidence=(
                "Belgian / European bondholders received returns on "
                "Congo rubber concessions without direct visibility "
                "of enforcement methods. The forced-labor / "
                "severed-hand enforcement regime was documented only "
                "after 1904 by Casement and Morel; prior to that, "
                "the financial layer operated with near-zero "
                "substrate visibility."
            ),
            provenance=empirical(
                source_refs=[
                    "Hochschild 1998, 'King Leopold's Ghost: A Story "
                    "of Greed, Terror, and Heroism in Colonial Africa'",
                    "Casement 1904, 'Report to Parliament on the "
                    "Conditions in the Congo Free State' (published "
                    "in Parliamentary Papers)",
                    "Morel 1906, 'Red Rubber: The Story of the Rubber "
                    "Slave Trade Flourishing on the Congo in the "
                    "Year of Grace 1906'",
                ],
                rationale=(
                    "Hochschild's synthesis is the canonical modern "
                    "account; Casement and Morel are the primary "
                    "contemporary exposés; mortality estimates range "
                    "~5-15 million over the regime's 23 years"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="financialized_reverse_causation",
            evidence=(
                "concession quotas set by Brussels drove enforcement "
                "levels on the ground; each upward quota revision "
                "produced predictable mortality spikes in the Leopold "
                "administrative records. Financial-layer demand "
                "governed substrate extraction directly and "
                "linearly."
            ),
            provenance=empirical(
                source_refs=[
                    "Vansina 2010, 'Being Colonized: The Kuba "
                    "Experience in Rural Congo, 1880-1960'",
                    "Nelson 1994, 'Colonialism in the Congo Basin, "
                    "1880-1940'",
                ],
                rationale=(
                    "reverse-causation from Brussels quota decisions "
                    "to on-the-ground enforcement is documented in "
                    "the administrative archive analysis"
                ),
            ),
        ),
        ObservedInvestmentFailure(
            failure_tag="substrate_abstraction_destroys_nature",
            evidence=(
                "human TIME + LABOR substrate were abstracted into "
                "rubber-quota-dollar — the extraction was so complete "
                "that the substrate population was physically destroyed "
                "at ~5-15M-person scale"
            ),
            provenance=empirical(
                source_refs=[
                    "Hochschild 1998",
                    "Vansina 2010",
                ],
                rationale=(
                    "mass-mortality is the extreme end of claim #21's "
                    "prediction: TIME/ATTENTION/RELATIONAL_CAPITAL "
                    "cannot be derivatized without losing their "
                    "nature"
                ),
            ),
        ),
    ),
    primary_refs=[
        "Hochschild 1998",
        "Casement 1904",
        "Morel 1906",
        "Vansina 2010",
    ],
    historical_confidence=0.95,
    notes=(
        "The cleanest historical SYNTHETIC-distance + EXTRACTIVE_CLAIM "
        "anchor. Stretches the VOC/EIC pattern to an extreme: single-"
        "person (Leopold II) ownership + extreme derivative distance "
        "(European bondholder to African forced laborer) + explicit "
        "quota-driven financial pressure produced mass-mortality "
        "scale. Tests claims #16 (substrate visibility), #17 (cascade "
        "coupling), #18 (reverse causation), and #21 (substrate "
        "abstraction destroys nature) simultaneously. Heavy case; "
        "the framework's ability to encode it structurally — with "
        "all failure modes firing under a single context — is "
        "itself a calibration signal."
    ),
)


ALL_CASES: List[HistoricalInvestmentCase] = [
    ENRON_2001,
    MBS_2008,
    # AUDIT_20 § B: ZIRP_2009_2021 decomposed into three sub-cases
    # by investor type. The former single case matched only
    # liquidity_illusion and could not simultaneously fire
    # financialized_reverse_causation (below the DERIVATIVE-distance
    # threshold). Each sub-case now matches its own internally
    # consistent failure set.
    ZIRP_RETAIL_DIVERSIFIED,
    ZIRP_PRIVATE_EQUITY,
    ZIRP_CLO_STRUCTURED,
    GIG_ECONOMY,
    COMMUNITY_LAND_TRUSTS,
    # AUDIT_18 extensions:
    COLONIAL_RESOURCE_EXTRACTION,
    RETIREMENT_401K_GENERATIONAL,
    # AUDIT_20 extension:
    CONGO_RUBBER_1885_1908,
]


# ---------------------------------------------------------------------------
# Framework prediction vs observed failure-tag set
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CaseComparison:
    case: HistoricalInvestmentCase
    observed_tags: Tuple[str, ...]
    predicted_tags: Tuple[str, ...]

    @property
    def predicted_contains_observed(self) -> bool:
        """True iff every historically-observed failure tag is ALSO
        in the framework's predicted set for the DURING context.

        This is the asymmetric match discipline established in
        money_signal/historical_cases.py: the framework predicting
        MORE tags than were recorded is permitted (absence of
        evidence in historical accounts is not evidence of absence),
        but the framework failing to predict a recorded failure
        would be a real finding.
        """
        return set(self.observed_tags).issubset(set(self.predicted_tags))

    @property
    def extra_predicted(self) -> Tuple[str, ...]:
        """Predicted tags not in the observed set. Diagnostic only
        — their presence is not a failure; their absence does not
        prove the framework wrong."""
        return tuple(sorted(set(self.predicted_tags) - set(self.observed_tags)))


def compare_case(case: HistoricalInvestmentCase) -> CaseComparison:
    """Run the framework against a case's DURING context + characteristic
    vectors and build a structured comparison."""
    signal = assemble_investment_signal(
        case.characteristic_input,
        case.characteristic_expected,
        case.context_during,
    )
    predicted = signal_failure_reasons(signal)
    observed = tuple(f.failure_tag for f in case.observed_failures)
    return CaseComparison(
        case=case,
        observed_tags=observed,
        predicted_tags=predicted,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_case_report(c: CaseComparison) -> None:
    print(f"\n{'=' * 78}")
    print(f"{c.case.name}")
    print(f"  period:     {c.case.period}")
    print(f"  location:   {c.case.location}")
    print(f"  confidence: {c.case.historical_confidence:.2f}")
    print(f"{'-' * 78}")
    print(f"  observed failures   ({len(c.observed_tags)}): {list(c.observed_tags)}")
    print(f"  predicted failures  ({len(c.predicted_tags)}): {list(c.predicted_tags)}")
    print(f"  framework covers observed: {c.predicted_contains_observed}")
    if c.extra_predicted:
        print(f"  extra predicted (diagnostic): {list(c.extra_predicted)}")


if __name__ == "__main__":
    print("=" * 78)
    print("investment_signal / historical_cases")
    print("=" * 78)
    matches = 0
    for case in ALL_CASES:
        cmp = compare_case(case)
        _print_case_report(cmp)
        if cmp.predicted_contains_observed:
            matches += 1
    print(f"\n{'=' * 78}")
    print(f"framework predicted-covers-observed: {matches}/{len(ALL_CASES)} cases")
    print("=" * 78)
