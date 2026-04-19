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
),
SignalScore(
criterion="unit_invariant",
score=0.7,
justification=(
"physical units (mass, volume, area, functional "
"capacity, organism count) are invariant within "
"substrate type"
),
),
SignalScore(
criterion="referent_stable",
score=0.8,
justification=(
"referent is stable: the substrate exists independent "
"of the measurement"
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
),
SignalScore(
criterion="observer_invariant",
score=0.7,
justification=(
"two observers applying the same domain protocol agree "
"within documented tolerance"
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
),
SignalScore(
criterion="falsifiability",
score=0.85,
justification=(
"strongly falsifiable: measure the substrate, run the "
"operation, measure the substrate again"
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
),
SignalScore(
criterion="referent_stable",
score=0.35,
justification=(
"referent shifts with reflexivity (pricing moves "
"price), with legal regime change, and with "
"counterparty solvency changes without notice"
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
),
SignalScore(
criterion="observer_invariant",
score=0.6,
justification=(
"for liquid instruments in a functioning market, "
"observers agree. Agreement collapses for illiquid "
"or distressed instruments."
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
),
SignalScore(
criterion="unit_invariant",
score=0.4,
justification=(
"units depend on the specific coordination capacity "
"measured (trust density, legal enforcement reliability, "
"knowledge transmission rate). No universal scalar."
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
),
SignalScore(
criterion="observer_invariant",
score=0.5,
justification=(
"moderate agreement among observers using the same "
"coordination-outcome protocol; disagreement when "
"observers use different frameworks"
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
),
SignalScore(
criterion="falsifiability",
score=0.65,
justification=(
"falsifiable through coordination-outcome testing: "
"can the institution or community execute a "
"specified collective task within stated parameters"
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
    source: str                         # 'K_A', 'K_B', 'K_C'
    target: str
    relation: str                       # 'positive', 'negative',
    # 'conditional', 'none'
    mechanism: str
    conditions: str
    falsification_test: str
    strength_estimate: float            # -1.0 to +1.0
    strength_justification: str

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
