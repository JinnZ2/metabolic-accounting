"""
term_audit/audits/money.py

Audit of the term 'money' against signal-definition criteria and
first-principles purpose.

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
