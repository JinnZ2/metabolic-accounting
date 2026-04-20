"""
term_audit/audits/capital.py

Audit of the term 'capital' against signal-definition criteria, and
separation of the collapsed term into three distinct measurements.

Core finding: 'capital' as currently used collapses at least three
measurements into one token:

K_A  productive capital     physical means of production; substrate
that produces future output
K_B  financial capital      claims on future flows; instruments
denominated in exchange-value units
K_C  institutional capital  trust networks, legal frameworks,
coordination capacity

K_A inherits from V_C (substrate-value).
K_B inherits from V_B (exchange-value).
K_C is orthogonal to both; closest to V_A (use-value) in signal properties.

The dominant failure: K_A and K_B are reported in the same units
(dollars) and treated as interchangeable. They systematically
anti-correlate. Extracting K_A to produce K_B is the operational
definition of most modern capital 'accumulation'. The accounting
registers this as growth.

CC0. Stdlib only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from term_audit.schema import (
TermAudit, SignalScore, StandardSetter, FirstPrinciplesPurpose,
)
from term_audit.provenance import (
Provenance, empirical, theoretical, design_choice, placeholder, stipulative,
)

# ===========================================================================

# Part 1. Audit of collapsed 'capital' as a signal

# ===========================================================================

COLLAPSED_CAPITAL_AUDIT = TermAudit(
term="capital_collapsed_current_usage",
claimed_signal=(
"accumulated resources used to produce future output, whether "
"physical, financial, or institutional, treated as a single "
"quantity"
),
standard_setters=[
StandardSetter(
name="accounting profession under GAAP / IFRS",
authority_basis="credentialed practice",
incentive_structure=(
"collapsed measurement is the profession's product; "
"distinguishing K_A, K_B, K_C would require three "
"parallel balance sheets and expose where reported "
"capital is substrate conversion"
),
independence_from_measured=0.1,
),
StandardSetter(
name="financial markets and exchanges",
authority_basis="market infrastructure",
incentive_structure=(
"K_B is the tradable product; collapsing K_A into K_B "
"lets physical substrate be traded without separate "
"substrate accounting"
),
independence_from_measured=0.05,
),
StandardSetter(
name="capital owners and shareholders",
authority_basis="ownership position",
incentive_structure=(
"collapsed measurement lets K_B claims on K_A "
"substrate be treated as equivalent to K_A itself; "
"extraction of K_A registers as K_B growth without "
"recording the substrate loss"
),
independence_from_measured=0.05,
),
StandardSetter(
name="macroeconomics profession",
authority_basis="academic credentialing",
incentive_structure=(
"canonical capital theory treats capital as aggregatable "
"in dollar units; Cambridge capital controversy "
"(1950s-70s) showed this aggregation requires circular "
"assumptions; profession did not update"
),
independence_from_measured=0.15,
),
StandardSetter(
name="tax and regulatory frameworks",
authority_basis="statutory",
incentive_structure=(
"capital gains, depreciation, and capitalization rules "
"are denominated in K_B units; separating K_A would "
"require parallel assessment infrastructure"
),
independence_from_measured=0.2,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.1,
justification=(
"no bounded domain declared. A factory, a bond "
"portfolio, a patent, a watershed, a trust network, "
"and a trained workforce are all called 'capital'. "
"No scope separates them."
),
provenance=theoretical(
rationale=(
"structural scope-failure parallel to value audit: "
"categorically distinct referents share one token. The "
"term's extension to 'natural', 'human', 'social' capital "
"is evidence of the collapse, not resolution of it."
),
source_refs=[
"Harcourt 1972, 'Some Cambridge Controversies in the "
"Theory of Capital'",
],
falsification_test=(
"produce a scope definition for 'capital' that covers "
"K_A, K_B, K_C and whose boundary is not post-hoc "
"redrawn per challenge"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.1,
justification=(
"dollar units mask that K_A (physical substrate) and "
"K_B (financial claim) are not commensurable. A dollar "
"of topsoil and a dollar of derivatives do not behave "
"the same under conservation, regeneration, or "
"liquidity."
),
source_refs=[
"Cambridge capital controversy; Robinson 1953; "
"Sraffa 1960"
],
provenance=theoretical(
rationale=(
"the Cambridge capital controversy established that "
"aggregating heterogeneous physical capital in dollar "
"units requires circular assumptions; the profession "
"consolidated around aggregation for computational "
"convenience, not because Robinson/Sraffa were refuted"
),
source_refs=[
"Robinson 1953, 'The Production Function and the "
"Theory of Capital', Review of Economic Studies 21(2)",
"Sraffa 1960, 'Production of Commodities by Means of "
"Commodities'",
"Harcourt 1972, op. cit.",
],
falsification_test=(
"exhibit a non-circular aggregation procedure that "
"commensurates K_A and K_B under conservation"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.15,
justification=(
"referent shifts between K_A, K_B, and K_C depending "
"on speaker and context. 'Human capital', 'natural "
"capital', 'social capital' are recent attempts to "
"paper over the collapse without separating the "
"measurements."
),
provenance=theoretical(
rationale=(
"referent-shift is a structural consequence of the scope "
"failure. The proliferation of prefixed terms ('human', "
"'natural', 'social') is itself evidence: each prefix "
"reveals a referent the unprefixed term does not cover."
),
falsification_test=(
"find speaker-independent usage of 'capital' that "
"consistently selects one referent among K_A/K_B/K_C "
"across domains"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.15,
justification=(
"no calibration procedure maps a dollar figure for "
"capital to any physical or institutional referent. "
"K_B has market-clearing procedures within narrow "
"scopes; K_A and K_C do not have monetary calibration "
"that is not circular."
),
provenance=theoretical(
rationale=(
"calibration to K_A via replacement cost requires "
"substitutability at scale within relevant timescales — "
"false for topsoil, aquifers, mature forests, and "
"transmitted knowledge. NPV-based calibration assumes "
"marginal substitutability that fails near carrying "
"capacity thresholds."
),
falsification_test=(
"exhibit a monetary calibration of K_A that remains valid "
"as carrying capacity approaches its threshold"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.2,
justification=(
"the 'capital' of a firm varies by orders of magnitude "
"depending on whether the observer uses book value, "
"market value, replacement cost, or substrate-inclusive "
"accounting"
),
provenance=empirical(
source_refs=[
"Fama & French 1993, 'Common risk factors in returns on "
"stocks and bonds', JFE 33 (book-to-market variance)",
"FASB ASC 820 Level 3 inputs literature",
],
rationale=(
"book vs market value divergences are routinely measured "
"in finance; FASB Level 3 codifies observer variance for "
"illiquid assets. Inter-observer variance for the "
"collapsed 'capital' token inherits and compounds these."
),
scope_caveat=(
"cited studies measure book-vs-market and Level-3 "
"variance; the broader orders-of-magnitude claim across "
"substrate-inclusive accounting extends beyond the cited "
"literature"
),
falsification_test=(
"conduct matched valuations of the same firm under all "
"four accounting methods and show agreement within 2x "
"in >80% of cases"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.1,
justification=(
"collapsed capital does not obey any conservation law. "
"K_A obeys physical conservation; K_B can be created "
"and destroyed by legal and market action; K_C changes "
"with institutional trust dynamics. Collapsing them "
"obscures all three conservation structures."
),
provenance=theoretical(
rationale=(
"K_A conservation (thermodynamic) is masked by "
"aggregation with non-conserved K_B. Summing conserved "
"and non-conserved quantities yields a non-conserved "
"total; this is a structural property of aggregation, "
"not a contingent fact."
),
falsification_test=(
"derive a conservation law for the aggregate 'capital' "
"whose constraints are not already present in K_A alone"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.2,
justification=(
"collapsed capital is not falsifiable because scope "
"can be redrawn. Challenges to K_B valuations are "
"deflected to K_A replacement-cost claims; challenges "
"to K_A are deflected to K_B market-value claims."
),
provenance=theoretical(
rationale=(
"deflection structure is a direct consequence of the "
"scope failure; with no declared scope, any challenge "
"can be re-scoped. 0.2 (not 0.0) reflects that narrow "
"K_B claims within specific liquid markets remain "
"falsifiable."
),
falsification_test=(
"pre-register a falsifiable claim stated in 'capital' "
"and show no scope-redrawing occurs during three "
"independent audits"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"identify accumulated resources that enable future "
"production, so they can be maintained, invested in, "
"and allocated"
),
physical_referent=(
"the set of physical substrates, financial claims, and "
"institutional structures that together enable future "
"output; three distinct referents"
),
informational_referent=(
"three distinct informational quantities: substrate stock "
"(K_A), claim-on-flow (K_B), and coordination capacity (K_C)"
),
drift_score=0.9,
drift_justification=(
"the drift is collapse of three referents into one token "
"dominated by K_B. Decisions made on the collapsed "
"measurement systematically convert K_A into K_B and "
"register the conversion as K_B growth. K_C is usually "
"unmeasured."
),
),
correlation_to_real_signal=0.2,
correlation_justification=(
"weakly correlated with any one of the three underlying "
"referents. Correlation is dominated by K_B because K_B is "
"what the accounting infrastructure is optimized to produce."
),
notes=(
"collapsed capital fails 7 of 7 signal criteria. It inherits "
"its failure from 'value' and propagates it to 'investment', "
"'wealth', and every aggregate that depends on capital "
"measurement."
),
)

# ===========================================================================

# Part 2. K_A - productive capital (substrate)

# ===========================================================================

PRODUCTIVE_CAPITAL_AUDIT = TermAudit(
term="capital_A_productive",
claimed_signal=(
"stock of physical means of production: tools, infrastructure, "
"trained skill capacity, topsoil, breeding stock, knowledge "
"bases, and other substrates that directly enable future output"
),
standard_setters=[
StandardSetter(
name="industrial engineering and operations research",
authority_basis="credentialed practice with physical "
"instrumentation",
incentive_structure=(
"incentive aligned with accurate substrate measurement "
"within narrow operational scope"
),
independence_from_measured=0.65,
),
StandardSetter(
name="agronomy, forestry, ecosystem ecology",
authority_basis="scientific discipline",
incentive_structure=(
"aligned with accurate substrate measurement; external "
"physical constraint provides discipline"
),
independence_from_measured=0.75,
),
StandardSetter(
name="practitioner domain experts (craftspeople, "
"farmers, operators)",
authority_basis="first-person operational knowledge",
incentive_structure=(
"incentive fully aligned with accurate measurement; "
"substrate failure falls directly on the practitioner"
),
independence_from_measured=0.9,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.75,
justification=(
"scope bounded once the operation and the substrate "
"type are specified (tools for this shop, soil on this "
"parcel, breeding stock of this herd)"
),
provenance=stipulative(
rationale=(
"K_A is defined as substrate-for-a-specific-operation; "
"scope-definedness follows from the (operation, substrate) "
"pairing. Score 0.75 rather than 1.0 because aggregation "
"across operations is where the scope weakens."
),
definition_ref=(
"K_A = stock of physical means of production for a "
"specified operation"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.7,
justification=(
"physical units (mass, volume, area, functional "
"capacity, organism count) are invariant within "
"substrate type"
),
provenance=theoretical(
rationale=(
"physical units are invariant by metrological definition "
"within substrate type. Cross-substrate aggregation "
"requires a superordinate unit (exergy is one candidate); "
"the intra-substrate invariance is what the score reflects."
),
source_refs=["BIPM SI unit definitions"],
falsification_test=(
"demonstrate intra-substrate variance in physical units "
"under the same metrological protocol"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.8,
justification=(
"referent is stable: the substrate exists independent "
"of the measurement"
),
provenance=theoretical(
rationale=(
"K_A's referent is a physical property of the operation's "
"substrate; measurement does not perturb the substrate in "
"the reflexive way market pricing perturbs K_B"
),
falsification_test=(
"exhibit a K_A measurement procedure that measurably "
"alters the substrate it measures"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.7,
justification=(
"calibration exists in engineering, agronomy, forestry, "
"and animal husbandry. Each domain has reproducible "
"measurement procedures."
),
provenance=empirical(
source_refs=[
"ISO engineering and metrology standards",
"FAO/IPCC soil-carbon measurement protocols",
"USDA soil survey procedures",
],
rationale=(
"credentialed technical domains publish calibrated "
"measurement procedures with documented uncertainty"
),
scope_caveat=(
"calibration is mature for material substrate (soil, "
"timber, tools); weaker for biological-capacity and "
"knowledge-substrate measurements"
),
falsification_test=(
"identify a K_A substrate type where no reproducible "
"measurement procedure exists in the relevant domain"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.7,
justification=(
"two observers applying the same domain protocol agree "
"within documented tolerance"
),
provenance=empirical(
source_refs=[
"ISO/IEC 17025 inter-laboratory comparison framework",
"NIST key comparison database",
],
rationale=(
"inter-observer variance under standardized protocols is "
"directly measured across metrology and domain sciences"
),
scope_caveat=(
"applies when standardized protocols are followed; field "
"and practitioner knowledge without standardized protocols "
"has higher variance"
),
falsification_test=(
"run a round-robin measurement across multiple labs on a "
"defined K_A quantity and show agreement outside the "
"declared tolerance"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.85,
justification=(
"productive capital obeys physical conservation and "
"degradation laws. Soil erodes, tools wear, organisms "
"age, knowledge decays without transmission."
),
provenance=theoretical(
rationale=(
"K_A is governed by thermodynamic conservation laws "
"(first and second law) and by specific domain laws "
"(soil carbon dynamics, material wear, biological "
"senescence, knowledge-decay models). Score of 0.85 "
"(not 1.0) reflects that emergent coupling effects are "
"not captured by single-component laws."
),
source_refs=[
"First and second laws of thermodynamics",
"Gouy-Stodola theorem",
"thermodynamics/exergy.py (framework enforcement)",
],
falsification_test=(
"exhibit a sustained K_A measurement trajectory that "
"violates the framework's first-law closure checks"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.85,
justification=(
"strongly falsifiable: measure the substrate, run the "
"operation, measure the substrate again"
),
provenance=stipulative(
rationale=(
"K_A falsifiability is operationally bound to the before/"
"after substrate measurement, which is part of the K_A "
"definition. 0.85 (not 1.0) allows for cases where the "
"operation itself is contested."
),
definition_ref=(
"K_A operational definition: before/after substrate "
"measurement relative to the operation"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"maintain and expand the physical substrate that enables "
"future operations"
),
physical_referent=(
"measurable stocks of tools, infrastructure, biological "
"capacity, soil, water, and skilled practitioners"
),
informational_referent=(
"system carrying capacity expressed in operation-specific "
"units"
),
drift_score=0.3,
drift_justification=(
"drifts when productive capital is translated into dollar "
"units for comparability with K_B. The translation loses "
"the conservation structure and invites treating K_A as "
"interchangeable with K_B."
),
),
correlation_to_real_signal=0.85,
correlation_justification=(
"high correlation with actual productive capacity when "
"measured in physical units. Drops sharply when translated "
"to dollars for comparability."
),
notes=(
"K_A is the measurement closest to thermodynamic reality in "
"the capital family. It is routinely undervalued in the "
"collapsed token because its dollar translation excludes "
"substrate regeneration cost and threshold nonlinearities."
),
)

# ===========================================================================

# Part 3. K_B - financial capital (claims)

# ===========================================================================

FINANCIAL_CAPITAL_AUDIT = TermAudit(
term="capital_B_financial",
claimed_signal=(
"stock of financial claims on future flows: equity, debt, "
"derivatives, and other instruments denominated in monetary "
"units"
),
standard_setters=[
StandardSetter(
name="financial accounting (GAAP / IFRS)",
authority_basis="credentialed practice",
incentive_structure=(
"K_B measurement is the profession's product; "
"incentive to maintain K_B as the primary capital "
"measurement"
),
independence_from_measured=0.15,
),
StandardSetter(
name="securities exchanges and clearinghouses",
authority_basis="market infrastructure",
incentive_structure=(
"K_B pricing is the product; infrastructure optimized "
"for K_B measurement continuously"
),
independence_from_measured=0.1,
),
StandardSetter(
name="central banks and monetary authorities",
authority_basis="statutory monopoly",
incentive_structure=(
"K_B is denominated in the units they issue; their "
"authority depends on K_B remaining the operative "
"capital measurement"
),
independence_from_measured=0.1,
),
StandardSetter(
name="rating agencies and credit analysts",
authority_basis="credentialed practice with market "
"recognition",
incentive_structure=(
"paid by the rated entities (structural conflict); "
"captured by measurement continuity"
),
independence_from_measured=0.1,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.55,
justification=(
"scope defined within a specific legal and market "
"jurisdiction for a specific instrument type. "
"Aggregation across jurisdictions and instrument types "
"breaks scope."
),
provenance=stipulative(
rationale=(
"K_B is defined by the legal-market scope in which the "
"instrument clears. Within-scope definedness is stipulative; "
"the 0.55 score reflects that cross-jurisdiction aggregation "
"is routine and where the scope breaks."
),
definition_ref=(
"K_B = financial claim on future flow under a specified "
"legal and market jurisdiction"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.3,
justification=(
"monetary unit is itself not a signal (see money "
"audit). K_B inherits that failure. Same nominal claim "
"represents different real quantities across "
"jurisdictions and time."
),
provenance=theoretical(
rationale=(
"K_B inherits money's unit_invariant failure by "
"denomination. 0.3 (above money's 0.05) because K_B "
"occasionally admits non-monetary instrument forms "
"(commodity-denominated contracts) that escape the "
"worst of the money-unit failure."
),
source_refs=[
"money audit, unit_invariant criterion",
"Balassa 1964; Samuelson 1964",
],
falsification_test=(
"exhibit a K_B aggregate whose cross-jurisdiction "
"invariance exceeds that of its monetary denominator"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.35,
justification=(
"referent shifts with reflexivity (pricing moves "
"price), with legal regime change, and with "
"counterparty solvency changes without notice"
),
provenance=theoretical(
rationale=(
"reflexivity in financial markets is a structural "
"property: price discovery perturbs the referent. Regime "
"and solvency changes are historical-empirical additions. "
"0.35 matches V_B's score via the K_B⊇V_B correspondence."
),
source_refs=[
"Soros 1987, 'The Alchemy of Finance'",
"Bouchaud & Potters 2003 (econophysics formalization)",
],
falsification_test=(
"identify a K_B instrument whose referent is stable "
"across a counterparty-solvency change without "
"re-pricing"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.55,
justification=(
"mark-to-market calibration exists for liquid "
"instruments. Level 3 instruments under FASB ASC 820 "
"are not externally calibrated."
),
provenance=empirical(
source_refs=[
"FASB ASC 820, 'Fair Value Measurement', Level 1/2/3 "
"hierarchy",
"IFRS 13 Fair Value Measurement",
],
rationale=(
"accounting standards explicitly document the calibration-"
"coverage gradient: Level 1 = direct market clearing, "
"Level 3 = unobservable inputs. The score's two-regime "
"structure comes directly from the standards."
),
scope_caveat=(
"FASB/IFRS framework calibrates K_B to itself "
"(mark-to-market); it does not calibrate K_B to K_A "
"substrate backing"
),
falsification_test=(
"exhibit a K_B calibration procedure that successfully "
"references K_A substrate backing rather than market "
"consensus"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.6,
justification=(
"for liquid instruments in a functioning market, "
"observers agree. Agreement collapses for illiquid "
"or distressed instruments."
),
provenance=empirical(
source_refs=[
"SEC Rule 605 order-execution quality data",
"FINRA TRACE inter-dealer corporate-bond quote variance",
],
rationale=(
"regulatory data directly measures inter-observer "
"agreement across liquid / illiquid strata"
),
scope_caveat=(
"0.6 averages across liquidity tiers; observer invariance "
"is high for Level 1 and low for Level 3"
),
falsification_test=(
"show that observer agreement for Level 3 instruments "
"matches Level 1 within 10% on representative samples"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.15,
justification=(
"K_B is not conserved. Credit creation adds units. "
"Default destroys them. Central bank operations add "
"or remove them. No conservation law constrains "
"aggregate K_B."
),
provenance=theoretical(
rationale=(
"K_B inherits money's non-conservation by denomination. "
"Score matches money's conservation_or_law (0.2) "
"modulo local ledger-level double-entry conservation."
),
source_refs=[
"money audit, conservation_or_law criterion",
"McLeay, Radia & Thomas 2014, BoE Q1 Bulletin",
],
falsification_test=(
"derive an aggregate K_B conservation law that holds "
"across credit cycles and default events"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.6,
justification=(
"falsifiable within a specific liquid market: attempt "
"the trade at the stated price. Not falsifiable as a "
"general measurement of capital because K_B's claimed "
"backing by K_A is not audited."
),
provenance=stipulative(
rationale=(
"K_B falsifiability is operationally bound to market-"
"clearing, which is part of the K_B definition. 0.6 "
"(not 0.8) reflects that the broader capital-measurement "
"claim (K_B stands in for K_A) is not falsifiable."
),
definition_ref=(
"K_B operational definition: market-clearance test for "
"the instrument"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"coordinate claims on future output and allocate them "
"across savers, investors, and producers"
),
physical_referent=(
"legal claims on specific future flows from specific "
"productive operations"
),
informational_referent=(
"distributed ledger of claims, with associated counterparty "
"risk and time preferences"
),
drift_score=0.75,
drift_justification=(
"drifts from 'claim on a specific future flow' to "
"'universal measure of capital accumulation'. The drift "
"is what lets K_B stand in for K_A in aggregate "
"statistics, hiding substrate conversion."
),
),
correlation_to_real_signal=0.4,
correlation_justification=(
"correlated with market-clearing prices within liquid "
"markets. Weakly correlated with the underlying K_A claimed "
"as backing. Decouples entirely during credit expansions and "
"asset bubbles."
),
notes=(
"K_B is a valid signal for its narrow referent (claim on a "
"specific future flow within a specific legal regime) and a "
"failed signal for the broader referent (capital as "
"accumulated productive resource) that it is usually invoked "
"for."
),
)

# ===========================================================================

# Part 4. K_C - institutional capital (coordination)

# ===========================================================================

INSTITUTIONAL_CAPITAL_AUDIT = TermAudit(
term="capital_C_institutional",
claimed_signal=(
"coordination capacity of a society or organization: trust "
"networks, legal frameworks, institutional competence, "
"transmission of knowledge, capacity for collective action"
),
standard_setters=[
StandardSetter(
name="sociology, political science, anthropology",
authority_basis="academic credentialing",
incentive_structure=(
"moderately aligned with accurate measurement; less "
"captured than economics because K_C is not the "
"tradable product"
),
independence_from_measured=0.55,
),
StandardSetter(
name="community and practitioner observers",
authority_basis="first-person domain knowledge",
incentive_structure=(
"incentive aligned with accurate measurement; "
"institutional failure falls directly on community"
),
independence_from_measured=0.85,
),
StandardSetter(
name="institutional economics",
authority_basis="academic sub-discipline",
incentive_structure=(
"partially captured; tries to translate K_C into K_B "
"units for comparability, which undermines the "
"measurement"
),
independence_from_measured=0.4,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.5,
justification=(
"scope bounded once the institution or community and "
"the coordination task are specified. Aggregation "
"across societies breaks scope."
),
provenance=stipulative(
rationale=(
"K_C is defined by the (institution, coordination task) "
"pairing. 0.5 reflects that cross-institution aggregation "
"is where the scope starts to fail, and such aggregation "
"is routine in social capital literature."
),
definition_ref=(
"K_C = coordination capacity of an institution or "
"community for a specified collective task"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.4,
justification=(
"units depend on the specific coordination capacity "
"measured (trust density, legal enforcement reliability, "
"knowledge transmission rate). No universal scalar."
),
provenance=theoretical(
rationale=(
"K_C is inherently multi-dimensional (trust, enforcement, "
"transmission, etc.). A single-scalar unit cannot be "
"invariant across these dimensions; the 0.4 reflects "
"within-dimension invariance with cross-dimensional "
"aggregation lacking a common unit."
),
falsification_test=(
"exhibit a single scalar K_C that preserves invariance "
"across trust, enforcement, and transmission dimensions "
"without information loss"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.6,
justification=(
"referent is stable within specified institution and "
"task; shifts across contexts as expected for a "
"relational quantity"
),
provenance=stipulative(
rationale=(
"K_C's referent is a property of the (institution, task) "
"pairing; shifts across contexts are features of the "
"definition, not failures of stability"
),
definition_ref=(
"K_C referent: coordination capacity within a specified "
"(institution, task) context"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.45,
justification=(
"partial calibration through observable coordination "
"outcomes (contract enforcement rates, participation "
"in mutual aid, knowledge transmission across "
"generations)"
),
provenance=empirical(
source_refs=[
"World Bank Worldwide Governance Indicators methodology",
"Ostrom 1990, 'Governing the Commons' (institutional-"
"outcome measurement)",
"Putnam 1993, 'Making Democracy Work' (civic-association "
"density measures)",
],
rationale=(
"outcome-based calibration procedures exist (contract "
"enforcement, commons governance, civic participation) "
"but are partial and contested"
),
scope_caveat=(
"calibrations are outcome-based rather than process-based; "
"they measure what K_C produces, not K_C itself"
),
falsification_test=(
"produce a direct (non-outcome-proxied) K_C calibration "
"that predicts coordination outcomes better than the "
"outcome-based proxies"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.5,
justification=(
"moderate agreement among observers using the same "
"coordination-outcome protocol; disagreement when "
"observers use different frameworks"
),
provenance=design_choice(
rationale=(
"0.5 reflects framework-dependence of K_C measurement "
"— different social-science traditions (Putnam vs Ostrom "
"vs Bourdieu) yield different quantities. Within-"
"framework agreement is higher, cross-framework agreement "
"is lower."
),
alternatives_considered=[
"0.7 (favoring within-framework agreement)",
"0.3 (favoring cross-framework disagreement)",
"a vector of per-framework scores",
],
falsification_test=(
"assemble measurements of the same institution from "
"three independent social-science traditions and show "
"cross-framework agreement above 0.7"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.35,
justification=(
"no strict conservation, but K_C exhibits measurable "
"decay when not actively maintained, and grows only "
"through repeated successful coordination"
),
provenance=theoretical(
rationale=(
"K_C follows a maintenance-and-accumulation dynamic "
"(decay without upkeep, growth through iteration) "
"rather than a conservation law. Score 0.35 reflects "
"that the dynamic is constrained but not conserved."
),
source_refs=[
"Ostrom 1990, op. cit. (design principles for "
"persistence of institutional capacity)",
],
falsification_test=(
"find an institutional setting where K_C persists "
"unchanged with no maintenance activity"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.65,
justification=(
"falsifiable through coordination-outcome testing: "
"can the institution or community execute a "
"specified collective task within stated parameters"
),
provenance=stipulative(
rationale=(
"K_C falsifiability is operationally bound to the "
"coordination-outcome test, which is part of the K_C "
"definition. 0.65 acknowledges observer-dependence of "
"what counts as successful execution."
),
definition_ref=(
"K_C operational definition: outcome of a specified "
"collective task within stated parameters"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"maintain the coordination infrastructure on which "
"productive and financial capital depend for their "
"function"
),
physical_referent=(
"the information-theoretic and social substrate that "
"enables groups to coordinate actions across time"
),
informational_referent=(
"network density, trust decay rate, knowledge transmission "
"rate, enforcement reliability"
),
drift_score=0.4,
drift_justification=(
"drifts when K_C is translated into K_B units via "
"'social capital' monetization, or when K_C is measured "
"only through outcomes visible to credentialed observers "
"(which misses practitioner-domain coordination)"
),
),
correlation_to_real_signal=0.65,
correlation_justification=(
"moderate correlation with observable coordination outcomes "
"when measured directly. Correlation drops when K_C is "
"proxied through K_B measurements like GDP-per-capita or "
"institutional-quality indices built on captured signals."
),
notes=(
"K_C is the measurement most often invisible in the collapsed "
"token. When it collapses, K_A and K_B both become "
"unrecoverable: the substrate cannot be maintained without "
"coordination, and the claims cannot be enforced without "
"institutional capacity."
),
)

# ===========================================================================

# Part 5. Linkage analysis

# ===========================================================================

@dataclass
class CapitalLinkage:
    """A documented relationship between two capital measurements.

    `strength_estimate` is a numeric claim and carries a Provenance.
    """
    source: str                         # 'K_A', 'K_B', 'K_C'
    target: str
    relation: str                       # 'positive', 'negative',
    # 'conditional', 'none'
    mechanism: str
    conditions: str
    falsification_test: str
    strength_estimate: float            # -1.0 to +1.0
    strength_justification: str
    provenance: Optional[Provenance] = None

CAPITAL_LINKAGES = [
CapitalLinkage(
source="K_A", target="K_B",
relation="conditional",
mechanism=(
"productive capital can be monetized into financial claims "
"when markets, legal frameworks, and liquidity exist. "
"The monetization does not increase K_A; it creates a K_B "
"claim on it."
),
conditions=(
"functioning market; legal enforceability; liquidity "
"sufficient to price"
),
falsification_test=(
"find cases where K_A is high and K_B is persistently zero "
"despite conditions being met"
),
strength_estimate=0.5,
strength_justification=(
"moderate positive when conditions hold; zero otherwise"
),
provenance=placeholder(
rationale=(
"0.5 is the auditor's estimate conditional on the named "
"preconditions. Sign is structural; magnitude is a guess."
),
retirement_path=(
"sector-stratified studies of K_A monetization events "
"(e.g., IPO pricing of land-based operations; valuation "
"multiples for substrate-rich firms)"
),
),
),
CapitalLinkage(
source="K_B", target="K_A",
relation="negative",
mechanism=(
"financial claims grow by demanding returns from productive "
"substrate; without substrate regeneration, K_B growth is "
"K_A extraction. The faster K_B grows, the faster K_A is "
"drawn down absent regeneration investment."
),
conditions=(
"K_B return expectations exceed K_A regeneration rate"
),
falsification_test=(
"measure K_A trajectory in sectors with highest K_B growth; "
"show positive K_A trajectory in the majority"
),
strength_estimate=-0.6,
strength_justification=(
"moderate to strong negative under current return "
"expectations; weaker where regulation forces K_A "
"regeneration"
),
provenance=design_choice(
rationale=(
"LOAD-BEARING negative linkage: the sign of K_B → K_A is "
"the argument's punchline — financial-claim growth "
"without substrate regeneration is substrate extraction. "
"Changing sign to positive would break the Tier-1-"
"inheritance argument. -0.6 is a design choice reflecting "
"sectoral averaging under current return expectations."
),
alternatives_considered=[
"-0.9 (treating extractive sectors as default)",
"-0.3 (counting regulated sectors in the average)",
"a sector × regulatory-regime matrix rather than a scalar",
],
falsification_test=(
"sample highest-K_B-growth sectors across 30 years; "
"measure K_A trajectory in physical units; show >50% with "
"positive trajectories"
),
),
),
CapitalLinkage(
source="K_A", target="K_C",
relation="positive",
mechanism=(
"shared productive substrate creates reasons for "
"coordination; practitioners of the same craft or operators "
"of the same infrastructure develop trust and knowledge "
"transmission"
),
conditions=(
"the substrate is operated by multiple practitioners with "
"ongoing contact"
),
falsification_test=(
"find high-K_A settings with persistently low K_C despite "
"conditions being met"
),
strength_estimate=0.5,
strength_justification=(
"moderate positive; strength depends on operational "
"proximity and knowledge transmission practices"
),
provenance=placeholder(
rationale=(
"0.5 is the auditor's estimate. Sign is supported by "
"commons-governance literature; magnitude is not anchored "
"to a specific study."
),
retirement_path=(
"meta-analysis of commons-governance studies (Ostrom "
"corpus; subak, alpine commons, fishery co-management) "
"on the correlation between shared-substrate operations "
"and institutional-capacity outcomes"
),
),
),
CapitalLinkage(
source="K_C", target="K_A",
relation="positive",
mechanism=(
"institutional capacity enables long-horizon investment in "
"productive substrate, including regeneration that would "
"not be rewarded by K_B alone"
),
conditions=(
"institutions have time horizon and enforcement capacity "
"to protect K_A regeneration"
),
falsification_test=(
"find sustained K_A regeneration in settings with low K_C"
),
strength_estimate=0.7,
strength_justification=(
"strong positive; K_A regeneration over long horizons is "
"rarely sustained without supporting institutional capacity"
),
provenance=theoretical(
rationale=(
"long-horizon K_A regeneration requires time preferences "
"longer than market discount rates support; K_C is the "
"only mechanism that provides this. This is an argument "
"from discount-rate structure, not a measurement."
),
source_refs=[
"Ostrom 1990, 'Governing the Commons' (design principles "
"for long-horizon commons persistence)",
"Heinberg 2019 on substrate-regeneration time horizons",
],
falsification_test=(
"document sustained (>30 year) K_A regeneration under "
"market-only incentives in the absence of commons "
"governance or equivalent institutional structure"
),
),
),
CapitalLinkage(
source="K_B", target="K_C",
relation="negative",
mechanism=(
"financialization substitutes transactional coordination "
"for trust-based coordination; crowds out institutional "
"capacity by making short-horizon financial incentive the "
"primary coordination signal"
),
conditions=(
"K_B expansion into domains previously coordinated by K_C"
),
falsification_test=(
"measure K_C trajectory in domains undergoing rapid "
"financialization; show stable or rising K_C"
),
strength_estimate=-0.55,
strength_justification=(
"moderate negative when financialization enters "
"previously non-market domains; weaker when K_B operates "
"within explicitly bounded domains"
),
provenance=design_choice(
rationale=(
"secondary negative linkage supporting the K_B-dominance "
"thesis: financialization crowds out trust-based "
"coordination. -0.55 is a design choice averaging across "
"domains; the sign is load-bearing."
),
alternatives_considered=[
"-0.8 (treating healthcare / education financialization "
"as default)",
"-0.3 (treating bounded-domain financialization cases)",
"a domain × boundedness matrix",
],
falsification_test=(
"measure civic-participation or trust-density before and "
"after financialization events in matched domains; show "
"stable or rising K_C in the majority"
),
),
),
CapitalLinkage(
source="K_C", target="K_B",
relation="conditional",
mechanism=(
"strong institutional capacity enables K_B markets to "
"function at lower risk premiums; enforcement reliability "
"reduces required K_B returns"
),
conditions=(
"K_B operates within the institution's enforcement domain"
),
falsification_test=(
"measure K_B risk premiums across institutional-capacity "
"strata; show no negative correlation"
),
strength_estimate=0.4,
strength_justification=(
"moderate positive; strong K_C supports K_B function but "
"does not directly grow K_B"
),
provenance=empirical(
source_refs=[
"La Porta et al. 1998, 'Law and Finance', JPE 106 "
"(legal-origin vs financial-market depth)",
"World Bank Governance Indicators vs sovereign spread "
"literature",
],
rationale=(
"cross-country governance-vs-risk-premium studies "
"directly measure the correlation between institutional "
"capacity and K_B functioning"
),
scope_caveat=(
"cited studies use legal-origin and governance-indicator "
"proxies for K_C; direct K_C measurement is weaker. The "
"0.4 reflects correlation strength in these studies."
),
falsification_test=(
"measure sovereign-spread or corporate-risk-premium "
"response to governance-indicator changes at matched "
"K_B scale and show no negative correlation"
),
),
),
]

# ===========================================================================

# Part 6. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
"id": 1,
"claim": (
"K_B and K_A anti-correlate in extractive sectors over "
"decadal timescales"
),
"falsification": (
"measure both across extractive sector sample over 30 "
"years; show positive correlation in the majority"
),
},
{
"id": 2,
"claim": (
"reported 'capital accumulation' in GDP and balance sheet "
"statistics is dominated by K_B growth accompanied by "
"stable or declining K_A"
),
"falsification": (
"decompose capital accumulation metrics across 1970-2025 "
"into K_A and K_B components; show K_A keeps pace with K_B"
),
},
{
"id": 3,
"claim": (
"K_C declines accelerate when K_B expands into domains "
"previously coordinated by K_C (healthcare, education, "
"community services)"
),
"falsification": (
"measure K_C before and after financialization of matched "
"domains; show K_C stable or rising"
),
},
{
"id": 4,
"claim": (
"sustained K_A regeneration occurs only in settings with "
"non-trivial K_C; K_B alone does not produce regeneration"
),
"falsification": (
"find sustained K_A regeneration over 30+ years in "
"settings with low K_C"
),
},
{
"id": 5,
"claim": (
"separating K_A, K_B, K_C in accounting produces "
"measurably different allocation decisions than the "
"collapsed measurement, with greater allocation to K_A "
"regeneration"
),
"falsification": (
"run parallel accounting on matched operation; show "
"allocation decisions do not differ"
),
},
{
"id": 6,
"claim": (
"K_A scores higher on signal-criteria audit than K_B, "
"because it is anchored by physical law rather than "
"market infrastructure"
),
"falsification": (
"apply signal criteria to matched K_A and K_B cases; "
"show K_B scores higher on the aggregate"
),
},
]

# ===========================================================================

# Part 7. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
"attack": (
"K_A can be translated into K_B units via replacement "
"cost or NPV of future flows, so the separation is "
"unnecessary"
),
"response": (
"replacement cost assumes replacement is possible at scale "
"within relevant timescales; for topsoil, aquifers, mature "
"forests, and transmitted knowledge, it is not. NPV "
"assumes marginal substitutability that fails near "
"carrying-capacity thresholds. Both translations are "
"exactly what hides the substrate conversion."
),
},
{
"attack": (
"financial markets allocate capital efficiently; K_B "
"measurement is therefore sufficient"
),
"response": (
"financial markets allocate K_B efficiently within their "
"own scope. This is a statement about internal consistency, "
"not about tracking K_A. A market that allocates K_B "
"toward K_A extraction is efficient by K_B metrics and "
"destructive by K_A metrics. Efficiency claims require "
"the scope declaration that the collapsed measurement "
"hides."
),
},
{
"attack": (
"K_C is not real capital because it cannot be owned, "
"traded, or measured in monetary units"
),
"response": (
"K_C meets the first-principles definition of capital "
"(stock of resources enabling future output) even though "
"it cannot be owned or traded. The objection defines "
"capital as what can be financialized, which is circular. "
"A measurement infrastructure that excludes K_C because "
"K_C is not tradable is optimized for K_B, not for "
"capital."
),
},
{
"attack": (
"the Cambridge capital controversy was resolved in favor "
"of aggregation; separating K_A, K_B, K_C relitigates a "
"settled question"
),
"response": (
"the controversy was not resolved on substance; the "
"profession consolidated around aggregation for "
"computational convenience. Robinson's and Sraffa's "
"objections to aggregating heterogeneous physical capital "
"in dollar units remain unanswered. The separation "
"proposed here is structurally the same point the Cambridge "
"(UK) side made, now formalized with modern signal-"
"criteria tools."
),
"source_refs": [
"Harcourt 1972, 'Some Cambridge Controversies in the "
"Theory of Capital'"
],
},
{
"attack": (
"productive capital is already tracked in national "
"accounts as fixed capital formation"
),
"response": (
"fixed capital formation is denominated in K_B units and "
"excludes biological, knowledge, and institutional "
"substrate. It measures K_A translated into K_B and "
"filtered through the K_B measurement infrastructure. The "
"translation loses the conservation structure."
),
},
{
"attack": (
"without a single aggregatable capital measure, macro-"
"economic analysis becomes impossible"
),
"response": (
"this defends current analysis on convenience grounds. "
"Convenience is not validity. Macroeconomic analysis "
"based on a measurement that systematically hides "
"substrate conversion is not producing accurate models; "
"it is producing models that look accurate because the "
"conversion is invisible to them."
),
},
{
"attack": (
"the three-way separation ignores human capital, which "
"is a well-established concept"
),
"response": (
"human capital in its current usage is an attempted "
"translation of trained skill (K_A) and social "
"embeddedness (K_C) into K_B units via lifetime earnings "
"or similar proxies. The translation inherits K_B's "
"failures. Under the three-way separation, the skill "
"component belongs to K_A and the embeddedness component "
"belongs to K_C. 'Human capital' is not a fourth category; "
"it is a misclassified composite."
),
},
]

# ===========================================================================

# Part 8. Summary

# ===========================================================================

def collapsed_usage_diagnosis() -> Dict:
    return {
    "term": "capital_collapsed_current_usage",
    "claim": (
    "one word denoting productive capital, financial claims, "
    "and institutional coordination as if they were one "
    "measurement"
    ),
    "failure": (
    "three referents with different signal properties fused "
    "into one token. K_B dominates the fusion because "
    "accounting and market infrastructure produce K_B "
    "measurements continuously. K_A is translated into K_B "
    "units, losing its conservation structure. K_C is usually "
    "unmeasured."
    ),
    "consequence": (
    "reported capital accumulation is dominated by K_B growth "
    "accompanied by K_A extraction; this is recorded as "
    "growth. The measurement hides the trade. GDP, wealth, "
    "and investment statistics all inherit this failure."
    ),
    "remediation": (
    "report K_A in physical units, K_B in monetary units, "
    "K_C in coordination-outcome units. Use the linkage "
    "matrix to expose where K_B growth is K_A extraction. "
    "Make substrate trade-offs explicit in investment and "
    "policy decisions."
    ),
    }

ALL_CAPITAL_AUDITS = {
"collapsed": COLLAPSED_CAPITAL_AUDIT,
"K_A_productive": PRODUCTIVE_CAPITAL_AUDIT,
"K_B_financial": FINANCIAL_CAPITAL_AUDIT,
"K_C_institutional": INSTITUTIONAL_CAPITAL_AUDIT,
}

if __name__ == "__main__":
    import json
    print("=== collapsed capital audit ===")
    print(json.dumps(COLLAPSED_CAPITAL_AUDIT.summary(), indent=2))
    print()
    print("=== separated audits ===")
    for key, audit in ALL_CAPITAL_AUDITS.items():
        if key == "collapsed":
            continue
        print(f"- {key} -")
        print(json.dumps(audit.summary(), indent=2))
        print()
    print("=== linkages ===")
    for link in CAPITAL_LINKAGES:
        print(f"  {link.source} -> {link.target}  "
              f"({link.relation:11s}, strength={link.strength_estimate:+.2f})")
    print()
    print("=== collapsed-usage diagnosis ===")
    print(json.dumps(collapsed_usage_diagnosis(), indent=2))
    print()
    print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
    print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
