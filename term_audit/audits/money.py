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
