"""
term_audit/audits/money.py

Audit of the term 'money' against signal-definition criteria and
first-principles purpose.

Companion reading: docs/SCOPING_ECONOMIC_TERMS.md lists the twelve+
distinct referents 'money' collapses, which is why each signal
criterion below scores at or below 0.2. The audit states the failure;
the scoping doc shows the dimensional explosion that causes it.

CC0.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from term_audit.schema import (
    TermAudit, SignalScore, StandardSetter, FirstPrinciplesPurpose,
)
from term_audit.provenance import (
    empirical, theoretical, design_choice, placeholder, stipulative,
)
from term_audit.study_scope_audit import (
    StudyScopeAudit, InstrumentAudit, ProtocolAudit, DomainCouplingAudit,
    RegimeAudit, CausalModelAudit, ScopeBoundary,
    Coupling, Regime,
)


# ---------------------------------------------------------------------------
# AUDIT_19 § C: StudyScopeAudit retrofits for two Tier 1 citations.
#
# These are REAL scope audits grounded in public methodology
# documents (Boskin Commission 1996 final report; McLeay/Radia/Thomas
# 2014 BoE Quarterly Bulletin). They are NOT templates for the
# remaining 72 EMPIRICAL records on this TermAudit tree — those
# require per-citation research that AUDIT_19 explicitly declines
# to fabricate. These two demonstrate the pattern.
# ---------------------------------------------------------------------------

_BOSKIN_CPI_SCOPE_AUDIT = StudyScopeAudit(
    claim=(
        "CPI approximates cost-of-living changes for US urban consumers"
    ),
    citation=(
        "Boskin et al. 1996, 'Toward a More Accurate Measure of the "
        "Cost of Living', Final Report to the Senate Finance Committee"
    ),
    instrument=InstrumentAudit(
        instrument_name="BLS CPI survey + Consumer Expenditure Survey",
        physical_quantity_measured=(
            "monthly weighted price-change index over a basket of "
            "consumer goods and services"
        ),
        measurement_range=(0.0, 10000.0),  # index values, not bounded physically
        resolution=0.1,                     # index point
        noise_floor=0.1,
        sampling_rate_hz=None,              # monthly survey
        spatial_resolution="US urban areas only; rural excluded",
        calibration_source="1982-84 base period re-weighted periodically",
        calibration_traceability="BLS re-weighting against CEX biennially",
        drift_rate=(
            "substitution bias ~0.4%/yr; quality/new-product bias "
            "~0.6%/yr per Boskin Commission estimates"
        ),
    ),
    protocol=ProtocolAudit(
        sample_preparation=(
            "83 strata × 38 pricing areas; price quotes collected from "
            "~23,000 retail establishments monthly"
        ),
        environmental_controls={
            "urban_population": True,
            "fixed_basket_weights": "until biennial re-weight",
        },
        excluded_conditions=[
            "rural consumer baskets",
            "imputed owner-occupied housing inflation (treated via "
            "rental equivalence, not direct)",
            "quality improvements at pace exceeding hedonic adjustment",
            "new-product categories prior to survey inclusion (lag of "
            "years)",
        ],
        control_group_definition="n/a (observational index, not RCT)",
        measurement_duration="monthly publication, continuous since 1913",
        replication_count=1,  # single official series, no independent replication
        blinding=False,
        pre_registration=False,  # methodology public but revised periodically
    ),
    coupling=DomainCouplingAudit(
        physical_domain="consumer price measurement",
        instrument_coupling=Coupling.TIGHT,   # CPI IS the BLS instrument
        protocol_coupling=Coupling.TIGHT,     # survey design determines the output
        substrate_coupling=Coupling.MODERATE, # basket shifts with consumption
        regime_coupling=Coupling.TIGHT,       # 1960s vs 2020s consumption patterns differ
    ),
    regime=RegimeAudit(
        assumed_baseline=(
            "stable consumption composition; representative urban "
            "household; fixed-basket methodology"
        ),
        baseline_validity_window="1913-present, re-weighted periodically",
        regime_state=Regime.DRIFTING,
        regime_drift_indicators=[
            "rise of services share of consumption",
            "digital goods with near-zero marginal cost",
            "housing-as-investment vs housing-as-consumption divergence",
            "quality adjustment outpacing hedonic methodology",
        ],
        extrapolation_horizon=(
            "intended as current-period indicator; long-horizon "
            "extrapolation not a claim of the index"
        ),
    ),
    causal_model=CausalModelAudit(
        causal_frame=(
            "statistical — CPI is not a causal model, it is an "
            "aggregation rule over sampled prices"
        ),
        confounders_identified=[
            "substitution bias",
            "quality bias",
            "new-product bias",
            "outlet/retailer substitution",
        ],
        confounders_controlled=[
            "substitution bias (partially, via geometric mean formula "
            "at lower levels since 1999)",
        ],
        confounders_unmeasured=[
            "housing bubble effects on owner-equivalent rent",
            "financialization of consumer goods categories",
            "observer asymmetry across income strata (deep vs thin "
            "holder per money_signal vocabulary)",
        ],
        unknown_unknowns_acknowledged=True,  # Boskin explicitly flags
        alternative_frames_considered=[
            "true cost-of-living index (theoretical ideal)",
            "PCE deflator (Fed's preferred alternative)",
            "chained CPI (adopted 2002)",
        ],
    ),
    scope=ScopeBoundary(
        in_scope_conditions=[
            "US urban consumer price movements, current period",
            "aggregated measurement across the basket",
        ],
        edge_conditions=[
            "regional sub-index comparison",
            "sub-population cost-of-living comparison",
        ],
        out_of_scope_conditions=[
            "cross-regime dollar-denominated comparison over long "
            "horizons",
            "individual-level purchasing power",
            "rural or non-urban consumer experience",
            "cost-of-living for income strata outside the survey's "
            "representative household",
        ],
        undeclared_scope=[
            "international purchasing-power comparisons",
            "observer-position heterogeneity (different strata "
            "experience different effective inflation)",
        ],
        extrapolation_claims=[
            "multi-decade real-value comparisons frequently made by "
            "downstream users, not by BLS itself",
        ],
    ),
)


_BOE_2014_MONEY_CREATION_SCOPE_AUDIT = StudyScopeAudit(
    claim=(
        "Commercial banks create money in the modern economy through "
        "credit issuance; central bank reserves are a consequence of "
        "that process, not a cause of it"
    ),
    citation=(
        "McLeay, Radia & Thomas 2014, 'Money Creation in the Modern "
        "Economy', Bank of England Quarterly Bulletin 2014 Q1"
    ),
    instrument=InstrumentAudit(
        instrument_name=(
            "BoE monetary-aggregate accounting + banking-sector "
            "balance-sheet analysis"
        ),
        physical_quantity_measured=(
            "broad monetary aggregates (M2, M4), reserves, bank "
            "credit flows at aggregate UK level"
        ),
        measurement_range=(0.0, 1e13),  # £ aggregates, not physically bounded
        resolution=1e6,                  # £1m in reported aggregates
        noise_floor=1e6,
        sampling_rate_hz=None,          # monthly/quarterly publication
        spatial_resolution=(
            "UK banking system aggregate; not cross-jurisdictional"
        ),
        calibration_source=(
            "BoE reporting standards applied to regulated UK banks"
        ),
        calibration_traceability=(
            "statistical returns from commercial banks under BoE "
            "regulatory authority"
        ),
        drift_rate=(
            "methodology generally stable; re-classification of "
            "non-bank financial institutions occasionally moves "
            "aggregates"
        ),
    ),
    protocol=ProtocolAudit(
        sample_preparation=(
            "aggregate UK commercial-banking statistical returns"
        ),
        environmental_controls={
            "regulatory_regime": "BoE reporting standards",
            "currency": "GBP, post-1971",
        },
        excluded_conditions=[
            "shadow-banking credit creation outside the regulated "
            "reporting perimeter (partial)",
            "cross-border bank credit interactions",
            "fintech / stablecoin issuance outside regulated banks",
        ],
        control_group_definition=(
            "comparison with textbook multiplier model and with "
            "pre-QE baseline regime"
        ),
        measurement_duration="continuous monthly/quarterly reporting",
        replication_count=1,  # one central-bank source; not independently replicated
        blinding=False,
        pre_registration=False,
    ),
    coupling=DomainCouplingAudit(
        physical_domain="monetary economics / banking-sector accounting",
        instrument_coupling=Coupling.TIGHT,   # aggregates ARE the instrument
        protocol_coupling=Coupling.TIGHT,     # BoE definitions shape the output
        substrate_coupling=Coupling.MODERATE, # claim about credit creation generalizes
        regime_coupling=Coupling.MODERATE,    # post-gold-standard fiat regime
    ),
    regime=RegimeAudit(
        assumed_baseline=(
            "modern fiat regime; regulated commercial banks with "
            "reserve requirements; central bank as rate-setter"
        ),
        baseline_validity_window="post-Bretton-Woods (1971-present)",
        regime_state=Regime.DRIFTING,
        regime_drift_indicators=[
            "growth of shadow banking outside the direct measurement "
            "perimeter",
            "stablecoin and crypto credit creation outside regulated "
            "reporting",
            "CBDC proposals would restructure the instrument itself",
        ],
        extrapolation_horizon=(
            "current-period structural claim; regime-change scenarios "
            "(CBDC, full-reserve banking) explicitly out of scope"
        ),
    ),
    causal_model=CausalModelAudit(
        causal_frame=(
            "mechanistic — identifies the accounting mechanism by "
            "which commercial-bank loans create deposits, replacing "
            "the textbook 'multiplier' causal frame"
        ),
        confounders_identified=[
            "household deposit demand",
            "regulatory capital constraints",
            "central-bank interest-rate policy",
            "quantitative-easing reserve injections",
        ],
        confounders_controlled=[
            "accounting-level reserve/deposit distinction is explicit",
        ],
        confounders_unmeasured=[
            "non-bank credit channels at full scope",
            "cross-border credit interactions",
            "behavioral-finance feedback on credit demand",
        ],
        unknown_unknowns_acknowledged=True,
        alternative_frames_considered=[
            "textbook money multiplier (explicitly rejected)",
            "full-reserve / positive-money proposals (noted)",
        ],
    ),
    scope=ScopeBoundary(
        in_scope_conditions=[
            "modern regulated-bank fiat regimes with a central bank",
            "current-period aggregate-level claim about causation",
        ],
        edge_conditions=[
            "emerging-market banking systems with weaker regulatory "
            "reporting",
            "economies with large dollarization or foreign-currency "
            "deposits",
        ],
        out_of_scope_conditions=[
            "gold-standard or commodity-backed regimes",
            "CBDC-only regimes (hypothetical)",
            "full-reserve banking regimes",
            "individual firm-level or household-level predictions",
        ],
        undeclared_scope=[
            "shadow-banking credit creation beyond the measurement "
            "perimeter",
            "crypto/stablecoin credit dynamics",
        ],
        extrapolation_claims=[
            "broader claims about how monetary policy transmits to the "
            "real economy often cite this paper but extend its scope",
        ],
    ),
)


MONEY_AUDIT = TermAudit(
    term="money",
    claimed_signal=(
        "a measure of economic value, medium of exchange, store of value, "
        "and unit of account"
    ),
    standard_setters=[
        StandardSetter(
            name="central banks (Fed, ECB, BoJ, etc.)",
            authority_basis="statutory monopoly on currency issuance",
            incentive_structure=(
                "maintain confidence in the unit while retaining discretion "
                "to expand supply; institutional survival depends on money "
                "remaining the default unit of account"
            ),
            independence_from_measured=0.1,
        ),
        StandardSetter(
            name="commercial banking system",
            authority_basis="fractional reserve credit creation under license",
            incentive_structure=(
                "expand credit during profitable periods, contract during "
                "risk; the unit's scope shifts with their balance sheet"
            ),
            independence_from_measured=0.05,
        ),
        StandardSetter(
            name="legislative / regulatory bodies",
            authority_basis="legal tender laws, tax denomination",
            incentive_structure=(
                "fiscal capacity depends on the unit being accepted; "
                "strong incentive to suppress alternative measurement "
                "systems"
            ),
            independence_from_measured=0.2,
        ),
        StandardSetter(
            name="market participants (prices)",
            authority_basis="bilateral agreement in transactions",
            incentive_structure=(
                "each participant prices based on local information, "
                "time preference, coercion level, legal context; the "
                "'same' unit means different things to buyer and seller"
            ),
            independence_from_measured=0.3,
        ),
    ],
    signal_scores=[
        SignalScore(
            criterion="scope_defined",
            score=0.1,
            justification=(
                "money claims to measure exchange value, store value, and "
                "serve as unit of account simultaneously. These are three "
                "different quantities. No bounded domain is declared. A "
                "dollar in a labor contract, a dollar in a derivative, "
                "and a dollar in a tax payment are not asserted to measure "
                "the same thing, yet share the token."
            ),
            source_refs=[
                "Mitchell-Innes 1914, 'The Credit Theory of Money'",
                "Ingham 2004, 'The Nature of Money'",
            ],
            provenance=theoretical(
                rationale=(
                    "money's multi-referent structure is established in "
                    "classical monetary theory (Mitchell-Innes, Ingham); "
                    "the specific 0.1 value is a design choice reflecting "
                    "'some token-level commonality via legal tender status' "
                    "rather than zero, not a measured quantity"
                ),
                source_refs=[
                    "Mitchell-Innes 1914, 'The Credit Theory of Money'",
                    "Ingham 2004, 'The Nature of Money'",
                ],
                falsification_test=(
                    "produce a formal definition of money that asserts a "
                    "single bounded domain and show it accounts for all "
                    "current usage without regime-specific carve-outs"
                ),
            ),
        ),
        SignalScore(
            criterion="unit_invariant",
            score=0.05,
            justification=(
                "one dollar in Tomah WI does not mean one dollar in "
                "Manhattan NY does not mean one dollar in rural Mississippi. "
                "Purchasing power, labor equivalence, legal claim strength "
                "all vary by jurisdiction, time, counterparty, and contract "
                "form. The unit is not invariant across any relevant "
                "measurement context."
            ),
            source_refs=[
                "BLS regional CPI differentials",
                "purchasing power parity literature (Balassa-Samuelson)",
            ],
            provenance=empirical(
                source_refs=[
                    "US BLS regional CPI differentials (published series)",
                    "Balassa 1964, 'The Purchasing Power Parity Doctrine: "
                    "A Reappraisal', Journal of Political Economy 72(6)",
                    "Samuelson 1964, 'Theoretical Notes on Trade "
                    "Problems', Review of Economics and Statistics 46(2)",
                ],
                rationale=(
                    "regional CPI and PPP literature directly measures "
                    "non-invariance of the nominal unit across spatial "
                    "and temporal contexts"
                ),
                scope_caveat=(
                    "BLS/Balassa-Samuelson measure PPP deviations; the "
                    "broader claim here (non-invariance across contract "
                    "form, counterparty, coercion level) extends beyond "
                    "the cited measurements"
                ),
                falsification_test=(
                    "demonstrate a domain in which $1 labor, $1 derivative, "
                    "$1 tax, and $1 consumer purchase are exchangeable at "
                    "parity with bounded tolerance"
                ),
            ),
        ),
        SignalScore(
            criterion="referent_stable",
            score=0.1,
            justification=(
                "the referent (economic value) is itself a contested "
                "construct. Value shifts with the act of pricing "
                "(reflexivity, Soros). The referent also shifts with "
                "legal regime changes, commodity base changes, and "
                "reserve ratio changes without notice."
            ),
            source_refs=[
                "Soros 1987, 'The Alchemy of Finance'",
            ],
            provenance=theoretical(
                rationale=(
                    "reflexivity argument (measurement interacts with "
                    "the measured) is a theoretical claim about market "
                    "systems, established by Soros and formalized in "
                    "later econophysics literature; the regime-shift "
                    "point is historical-empirical (1971 severance of "
                    "USD from gold, various currency reforms)"
                ),
                source_refs=[
                    "Soros 1987, 'The Alchemy of Finance'",
                    "Bordo & Eichengreen 1993, 'A Retrospective on the "
                    "Bretton Woods System', NBER monograph",
                ],
                falsification_test=(
                    "demonstrate a monetary regime with a stable referent "
                    "across at least one legal regime change and one "
                    "commodity-base change without redefinition"
                ),
            ),
        ),
        SignalScore(
            criterion="calibration_exists",
            score=0.15,
            justification=(
                "CPI, PPI, and similar indices attempt calibration but "
                "are themselves constructed with discretionary basket "
                "weights and substitution rules. No reproducible "
                "procedure maps a dollar amount to a fixed physical "
                "or informational referent."
            ),
            source_refs=[
                "Boskin Commission 1996 report on CPI methodology",
            ],
            provenance=empirical(
                source_refs=[
                    "Boskin et al. 1996, 'Toward a More Accurate Measure "
                    "of the Cost of Living', Final Report to the Senate "
                    "Finance Committee",
                    "BLS CPI Handbook of Methods (ongoing updates)",
                ],
                rationale=(
                    "Boskin Commission directly documented discretionary "
                    "basket weights and substitution rules in CPI; BLS "
                    "methods handbook makes those choices publicly "
                    "inspectable"
                ),
                scope_caveat=(
                    "0.15 (not 0.0) acknowledges that CPI-style indices "
                    "are internally reproducible calibrations to themselves; "
                    "they do not calibrate the dollar to a fixed external "
                    "physical referent, which is the stricter claim"
                ),
                falsification_test=(
                    "produce a calibration mapping a dollar amount to a "
                    "fixed physical or informational referent that is "
                    "stable across regime changes"
                ),
                # AUDIT_19 § C: real StudyScopeAudit attached, clearing
                # the soft_gap that the scope_caveat otherwise creates.
                scope_audit=_BOSKIN_CPI_SCOPE_AUDIT,
            ),
        ),
        SignalScore(
            criterion="observer_invariant",
            score=0.1,
            justification=(
                "buyer and seller routinely disagree on the 'value' a "
                "price represents; that disagreement is the precondition "
                "for the trade. Two accountants can book the same "
                "transaction three different ways under GAAP. Two "
                "appraisers value the same asset differently. Observer "
                "invariance fails."
            ),
            source_refs=[
                "FASB ASC 820 fair value hierarchy; level 3 inputs",
            ],
            provenance=empirical(
                source_refs=[
                    "FASB ASC 820, 'Fair Value Measurement' (Level 1/2/3 "
                    "hierarchy; Level 3 = unobservable inputs)",
                    "AICPA appraisal audit literature on inter-appraiser "
                    "variance for illiquid assets",
                ],
                rationale=(
                    "FASB's own hierarchy is evidence: Level 3 exists "
                    "because observer invariance fails for illiquid "
                    "assets. The standard codifies the failure mode."
                ),
                scope_caveat=(
                    "FASB hierarchy is about accounting measurement; the "
                    "buyer/seller disagreement point is bilateral, not "
                    "accounting-specific. Both point to the same failure "
                    "but through different mechanisms."
                ),
                falsification_test=(
                    "show that two independent appraisers applying GAAP "
                    "to the same Level-3 asset agree within 5% on >80% "
                    "of cases"
                ),
            ),
        ),
        SignalScore(
            criterion="conservation_or_law",
            score=0.2,
            justification=(
                "money is not conserved. Credit creation adds units. "
                "Default destroys units. Central bank operations add or "
                "remove units. No conservation law constrains the total "
                "quantity. Double-entry bookkeeping imposes local "
                "conservation only within a single ledger, not across "
                "the system."
            ),
            source_refs=[
                "McLeay, Radia, Thomas 2014, 'Money Creation in the "
                "Modern Economy', Bank of England Quarterly Bulletin",
            ],
            provenance=empirical(
                source_refs=[
                    "McLeay, Radia & Thomas 2014, 'Money Creation in the "
                    "Modern Economy', Bank of England Quarterly Bulletin "
                    "2014 Q1",
                    "Werner 2014, 'Can banks individually create money "
                    "out of nothing?', International Review of Financial "
                    "Analysis 36",
                ],
                rationale=(
                    "central-bank-authored and peer-reviewed evidence that "
                    "commercial credit creation adds money units; no "
                    "conservation law governs aggregate supply"
                ),
                scope_caveat=(
                    "0.2 (not 0.0) acknowledges local per-ledger "
                    "double-entry conservation, which is a weaker "
                    "property than system-level conservation"
                ),
                falsification_test=(
                    "derive aggregate monetary conservation from a "
                    "property of the institutional arrangements that is "
                    "not itself set by those institutions"
                ),
                # AUDIT_19 § C: real StudyScopeAudit attached.
                scope_audit=_BOE_2014_MONEY_CREATION_SCOPE_AUDIT,
            ),
        ),
        SignalScore(
            criterion="falsifiability",
            score=0.2,
            justification=(
                "the claim that money measures value cannot be falsified "
                "in the form it is usually stated, because 'value' is "
                "defined circularly as what money measures. To be "
                "falsifiable, the claimed referent would need an "
                "independent physical or informational definition."
            ),
            source_refs=[],
            provenance=theoretical(
                rationale=(
                    "the circularity is structural: 'value' as conven- "
                    "tionally used is defined by market-clearing prices, "
                    "which are denominated in money. No independent "
                    "physical or informational definition is supplied. "
                    "0.2 (not 0.0) allows that narrow market-clearance "
                    "predictions within a specific market are falsifiable."
                ),
                falsification_test=(
                    "produce a definition of 'value' that money measures, "
                    "stated in units other than money, that is both "
                    "operationally usable and survives regime changes"
                ),
            ),
        ),
    ],
    first_principles=FirstPrinciplesPurpose(
        stated_purpose=(
            "reduce transaction costs in multilateral exchange by providing "
            "a common intermediary token"
        ),
        physical_referent=(
            "originally tied to weights of commodity metal (grain-weight "
            "silver, grain-weight gold); physical referent severed in "
            "1971 for USD"
        ),
        informational_referent=(
            "a bearer claim on future goods and services, carrying "
            "implicit information about issuer solvency and legal "
            "enforceability"
        ),
        drift_score=0.85,
        drift_justification=(
            "current usage treats money as a measurement unit for value, "
            "wealth, productivity, and worth, none of which were part of "
            "the original transaction-cost-reduction purpose. The drift "
            "is from 'exchange lubricant' to 'universal metric of human "
            "activity', which is a category expansion of roughly two "
            "orders of magnitude in scope claim."
        ),
    ),
    correlation_to_real_signal=0.25,
    correlation_justification=(
        "money correlates weakly and non-monotonically with real "
        "physical flows (energy, materials, labor-hours) over short "
        "windows and narrow domains. Correlation breaks down at regime "
        "boundaries (currency reform, legal change, commodity base "
        "shift) and across jurisdictions. Over long timescales the "
        "correlation is dominated by the drift of the unit itself "
        "rather than by the underlying physical quantity."
    ),
    notes=(
        "money fails 7 of 7 signal criteria at threshold 0.7. It is not "
        "a signal. It is a token that occupies a signal-shaped position "
        "in discourse and accounting. This does not mean it is useless; "
        "tokens can coordinate behavior. It means it cannot be used as "
        "a measurement instrument without first declaring which of the "
        "many referents is being invoked in a given context, and what "
        "the calibration procedure is for that specific referent."
    ),
)


if __name__ == "__main__":
    import json
    print(json.dumps(MONEY_AUDIT.summary(), indent=2))
    print()
    print("failure modes:", MONEY_AUDIT.failure_modes())
