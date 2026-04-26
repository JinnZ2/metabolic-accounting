"""
term_audit/audits/value.py

Audit of the term 'value' against signal-definition criteria, and
separation of the collapsed term into three distinct measurements with
independent referents.

Core finding: 'value' as currently used collapses at least three
measurements into one token:

V_A  use-value         functional capacity to meet a need in context
V_B  exchange-value    ratio at which a thing trades in a market
V_C  substrate-value   thermodynamic contribution to carrying capacity

These three have different referents, different calibration procedures,
and different observer-invariance properties. Critically, V_B can be
negatively correlated with V_C: a thing can have high exchange-value
and negative substrate-value simultaneously. Collapsing them into one
token is the measurement failure that underwrites most of Tier 1
(money, capital, investment, wealth, GDP, economic growth).

External operationalizations: docs/EXTERNAL_OPERATIONALIZATIONS.md
maps the load-bearing NEGATIVE V_B → V_C linkage to math-econ's ER
(Labor Value Extraction Rate) and LWR (Labor Wealth Ratio) at
population scale (pinned at Mathematic-economics @ equations-v1).
Both are scalar projections of the linkage, not the full vector.

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

# Part 1. Audit of collapsed 'value' as a signal

# ===========================================================================

COLLAPSED_VALUE_AUDIT = TermAudit(
term="value_collapsed_current_usage",
claimed_signal=(
"the worth of a thing, measured as what it provides, what it "
"trades for, or what it contributes, treated as a single "
"quantity"
),
standard_setters=[
StandardSetter(
name="accounting and auditing profession",
authority_basis="credentialed practice under GAAP / IFRS",
incentive_structure=(
"the collapsed measurement is the profession's product; "
"distinguishing V_A, V_B, V_C would require three "
"parallel accounting systems and would reveal where "
"reported 'value' is substrate drawdown"
),
independence_from_measured=0.1,
),
StandardSetter(
name="economics profession",
authority_basis="academic credentialing",
incentive_structure=(
"canonical economics treats exchange-value as the "
"measurement and use-value as psychological; "
"substrate-value is largely absent. Separating them "
"invalidates decades of modeling."
),
independence_from_measured=0.15,
),
StandardSetter(
name="financial markets",
authority_basis="trading activity",
incentive_structure=(
"exchange-value is the tradable signal; collapsing "
"use-value and substrate-value into it lets those "
"quantities be traded without separate accounting"
),
independence_from_measured=0.05,
),
StandardSetter(
name="legal and tax frameworks",
authority_basis="statutory",
incentive_structure=(
"tax base and legal claims are denominated in "
"exchange-value; distinguishing substrate-value would "
"require a parallel assessment system"
),
independence_from_measured=0.2,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.05,
justification=(
"no bounded domain is declared. 'Value' is applied to "
"stock prices, paintings, water rights, topsoil, a "
"child's education, a patent, and a friendship without "
"scope separation. These do not share a referent."
),
provenance=theoretical(
rationale=(
"structural claim: the term is applied across categorically "
"distinct referents without scope separation. Falsification "
"would be exhibiting a bounded domain the collapsed term "
"actually respects."
),
source_refs=[
"Ingham 2004, 'The Nature of Money'",
"Graeber 2011, 'Debt: The First 5,000 Years' (ch. 3)",
],
falsification_test=(
"produce a definition of 'value' with a declared bounded "
"domain that covers all current usage without cross-category "
"collapse"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.05,
justification=(
"dollar units mask the fact that exchange-value units "
"are non-commensurable with use-value (need-meeting) "
"and substrate-value (carrying-capacity units). The "
"invariance is an artifact of the unit, not the "
"quantity."
),
provenance=theoretical(
rationale=(
"non-commensurability is a structural-algebraic property: "
"need-meeting (context-indexed), market-ratio (jurisdiction-"
"indexed) and carrying-capacity (physical-unit) live in "
"different metric spaces. Collapsing them under 'dollar' "
"is a unit relabel, not a unit invariance."
),
falsification_test=(
"exhibit a transformation that maps between the three "
"measurement spaces preserving the claimed invariant"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.1,
justification=(
"referent shifts silently between V_A, V_B, and V_C "
"depending on context and speaker. The 'value of a "
"forest' means ecosystem services to one speaker, "
"timber revenue to another, and carrying capacity to "
"a third. Same token, different referents."
),
provenance=theoretical(
rationale=(
"referent-shift is an instance of the scope-defined failure; "
"once scope is not declared, referent selection is a "
"free parameter of the speaker. 0.1 (not 0.0) allows for "
"contexts where speaker conventions stabilize the referent."
),
falsification_test=(
"audit 100 uses of 'value' across sources; show >=80% "
"select the same referent among {V_A, V_B, V_C} without "
"explicit scope declaration"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.1,
justification=(
"no calibration procedure maps a dollar amount to a "
"use-value or substrate-value referent. Exchange-value "
"has market-clearing procedures, but those procedures "
"do not calibrate to the other two."
),
provenance=theoretical(
rationale=(
"calibration requires a reproducible procedure mapping the "
"measurement to the referent. Market-clearing procedures "
"calibrate V_B to itself (a tautology at the system level); "
"no analogous procedure exists for the collapsed term "
"because its referent is not singular."
),
falsification_test=(
"exhibit a calibration procedure from dollar amounts to a "
"non-money referent that is stable across regime changes"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.15,
justification=(
"two observers measuring the 'value' of the same thing "
"routinely disagree by orders of magnitude depending "
"on which referent they are silently invoking"
),
provenance=empirical(
source_refs=[
"FASB ASC 820 fair-value hierarchy; Level-3 unobservable "
"inputs literature",
"AICPA inter-appraiser variance studies for illiquid assets",
],
rationale=(
"FASB's own Level-3 category empirically codifies observer "
"variance for illiquid assets; appraisal studies measure "
"variance directly"
),
scope_caveat=(
"FASB/AICPA studies measure accounting observer variance; "
"the broader orders-of-magnitude claim across V_A/V_B/V_C "
"extends beyond the cited measurement domain"
),
falsification_test=(
"assemble matched pairs of independent appraisers applying "
"the collapsed 'value' to the same asset and show agreement "
"within 10% on >80% of cases"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.1,
justification=(
"no conservation law; 'value' can be created by "
"speculation, destroyed by default, transferred without "
"physical flow. Substrate-value does obey conservation, "
"but the collapsed measurement does not expose that."
),
provenance=theoretical(
rationale=(
"collapsed term inherits money's non-conservation (see "
"money audit, conservation_or_law provenance). V_C obeys "
"thermodynamic conservation but is masked by the collapse."
),
source_refs=[
"McLeay, Radia & Thomas 2014, Bank of England Q1 Bulletin "
"(money-creation evidence)",
],
falsification_test=(
"derive a conservation law for the collapsed term that is "
"not already satisfied by the V_C component alone"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.15,
justification=(
"the collapsed term is not falsifiable because scope "
"can always be redrawn. A challenge to exchange-value "
"is deflected to use-value; a challenge to use-value "
"is deflected to exchange-value; substrate-value is "
"rarely acknowledged."
),
provenance=theoretical(
rationale=(
"deflection structure is a consequence of the scope failure. "
"0.15 (not 0.0) allows that narrow claims (V_B market-"
"clearing) remain falsifiable within their scope; what fails "
"is falsifiability of the collapsed token."
),
falsification_test=(
"pre-register a prediction phrased in 'value' and a "
"disconfirming observation schedule; run three audit "
"attempts and show no post-hoc scope redrawing occurs"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"communicate the worth of a thing across contexts to enable "
"exchange, allocation, and preservation decisions"
),
physical_referent=(
"properties of a thing that determine its ability to meet "
"needs, trade for other things, or contribute to system "
"carrying capacity; these are three distinct referents"
),
informational_referent=(
"three distinct informational quantities: need-fit (V_A), "
"market-ratio (V_B), and substrate-contribution (V_C)"
),
drift_score=0.9,
drift_justification=(
"the drift is collapse rather than translation: three "
"referents fused into one token, with exchange-value "
"dominating the fusion. Decisions made on the collapsed "
"measurement systematically trade substrate-value for "
"exchange-value because the measurement hides the trade."
),
),
correlation_to_real_signal=0.15,
correlation_justification=(
"correlation to any one of the three underlying referents is "
"weak because the measurement is dominated by exchange-value "
"while being reported as if it captured all three"
),
notes=(
"collapsed value fails 7 of 7 signal criteria. It is the "
"foundational measurement failure of Tier 1. Money, capital, "
"investment, wealth, GDP, and economic growth all inherit "
"their failure from this term."
),
)

# ===========================================================================

# Part 2. V_A - use-value

# ===========================================================================

USE_VALUE_AUDIT = TermAudit(
term="value_A_use_value",
claimed_signal=(
"functional capacity of a thing to meet a specified need in a "
"specified context"
),
standard_setters=[
StandardSetter(
name="the person with the need",
authority_basis="first-person experience of need-meeting",
incentive_structure=(
"incentive to accurately assess whether the thing "
"meets the need, because the cost of misassessment "
"falls on the assessor"
),
independence_from_measured=0.9,
),
StandardSetter(
name="domain practitioners (engineers, doctors, craftspeople)",
authority_basis="technical knowledge",
incentive_structure=(
"incentive aligned with accuracy in narrow technical "
"domains; weaker outside their domain"
),
independence_from_measured=0.7,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.8,
justification=(
"scope is bounded once the thing, the need, and the "
"context are specified"
),
provenance=stipulative(
rationale=(
"V_A is defined by construction as need-fit in context; "
"scope-definedness is built into the definition via the "
"(thing, need, context) triple. 0.8 rather than 1.0 "
"reflects that in practice, 'the need' often needs further "
"disambiguation (survival vs status-display)."
),
definition_ref=(
"module docstring: V_A = functional capacity to meet a "
"specified need in context"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.5,
justification=(
"within a specific need, units are well-defined "
"(liters of water during drought, calories during "
"famine, hours of shelter). Cross-need comparison "
"requires separate accounting."
),
provenance=empirical(
source_refs=[
"Institute of Medicine DRI reports (water, calorie, "
"protein requirements by demographic)",
"ASHRAE thermal-comfort standards (shelter-hours equivalents)",
],
rationale=(
"within a specific need, physiology and physics provide "
"unit invariants (liters, calories, kWh). Across-need "
"aggregation lacks a common unit — correctly scored 0.5"
),
scope_caveat=(
"DRI and ASHRAE standards cover a subset of human needs "
"(nutrition, thermal); extension to other need-domains "
"requires their own calibrated units"
),
falsification_test=(
"find a need-context pair where the physiological or "
"engineering unit is ill-defined or observer-dependent"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.7,
justification=(
"referent is stable within the specified need-and-"
"context pair. Shifts across needs are a feature: "
"a coat in winter and a coat in summer have "
"different use-values, which is correct."
),
provenance=stipulative(
rationale=(
"referent stability within (need, context) is part of the "
"V_A definition. Across-need variation is a feature, not "
"a failure: different (need, context) = different V_A by "
"construction."
),
definition_ref=(
"the (thing, need, context) triple fixes the referent; "
"see module docstring"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.65,
justification=(
"calibration exists within technical domains "
"(pharmacology, nutrition, engineering performance). "
"Across domains, calibration is qualitative."
),
provenance=empirical(
source_refs=[
"FDA/EMA pharmacokinetic calibration protocols",
"AOAC International analytical methods (nutrition)",
"ISO engineering performance standards",
],
rationale=(
"credentialed technical domains maintain reproducible "
"calibration procedures directly testable against need-"
"meeting outcomes"
),
scope_caveat=(
"calibration coverage is domain-dependent; V_A for "
"informational or relational needs is weaker than for "
"material needs"
),
falsification_test=(
"identify a domain with routine V_A claims and no "
"reproducible calibration procedure"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.6,
justification=(
"two observers assessing need-meeting for the same "
"person in the same context will largely agree on "
"whether the thing met the need"
),
provenance=design_choice(
rationale=(
"0.6 reflects that observer agreement is high for "
"material-need cases (food, medication, shelter) but "
"declines for contested-need cases (status, meaning, "
"appropriate-care decisions)"
),
alternatives_considered=[
"0.8 (favoring technical-domain cases)",
"0.4 (favoring contested-need cases)",
"a vector of subscores by need-type",
],
falsification_test=(
"assemble matched observer pairs across a representative "
"need-type spectrum; show inter-rater agreement outside "
"the 0.5-0.7 band"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.4,
justification=(
"no universal conservation, but use-value is "
"constrained by the physical properties of the thing "
"and the physiological or contextual requirements of "
"the need"
),
provenance=theoretical(
rationale=(
"use-value is bounded above by physical properties of the "
"thing (a 500kcal food can meet at most a 500kcal need) "
"and bounded below by zero. These are constraints, not "
"a conservation law, hence the intermediate score."
),
falsification_test=(
"exhibit a V_A measurement that exceeds the physical "
"upper bound derived from the thing's properties"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.85,
justification=(
"strongly falsifiable: apply the thing to the need in "
"the context and observe whether the need is met"
),
provenance=stipulative(
rationale=(
"V_A is defined operationally as need-meeting outcome in "
"context; applying the thing and observing is the "
"definition, not a separate empirical study"
),
definition_ref=(
"V_A operational definition: outcome of (thing applied "
"to need in context)"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"determine whether a thing will meet a specified need in "
"a specified context"
),
physical_referent=(
"operational fit between the thing's properties and the "
"need's requirements"
),
informational_referent=(
"conditional probability that the thing meets the need "
"given the context"
),
drift_score=0.3,
drift_justification=(
"drifts when use-value is generalized across contexts "
"without respecifying the need. Less drift than V_B "
"because the need-meeting test is concrete and local."
),
),
correlation_to_real_signal=0.8,
correlation_justification=(
"strong correlation with actual need-meeting outcomes when "
"the need and context are specified. Drops sharply when "
"use-value is reported as a scalar across unspecified contexts."
),
notes=(
"this is the measurement closest to first-person utility. "
"Under the collapsed term, it is routinely overridden by "
"exchange-value: a medication with high use-value during a "
"health crisis can have low exchange-value to someone without "
"purchasing power, and the collapsed measurement records the "
"exchange-value."
),
)

# ===========================================================================

# Part 3. V_B - exchange-value

# ===========================================================================

EXCHANGE_VALUE_AUDIT = TermAudit(
term="value_B_exchange_value",
claimed_signal=(
"ratio at which a thing trades for other things in a specified "
"market under specified legal and liquidity conditions"
),
standard_setters=[
StandardSetter(
name="market makers and exchanges",
authority_basis="infrastructure control",
incentive_structure=(
"exchange-value measurement is their product; incentive "
"to maintain the measurement as primary and suppress "
"use-value and substrate-value alternatives"
),
independence_from_measured=0.1,
),
StandardSetter(
name="central banks and monetary authorities",
authority_basis="statutory monopoly",
incentive_structure=(
"exchange-value is denominated in the monetary unit "
"they issue; their authority depends on the "
"measurement remaining primary"
),
independence_from_measured=0.1,
),
StandardSetter(
name="tax authorities",
authority_basis="statutory",
incentive_structure=(
"tax base is exchange-value; incentive to keep "
"exchange-value as the operative measurement"
),
independence_from_measured=0.2,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.5,
justification=(
"scope defined within a specific market at a specific "
"time with specific liquidity and legal conditions. "
"Generalized across markets or times, scope breaks."
),
provenance=stipulative(
rationale=(
"V_B is defined as an equilibrium ratio in a specific "
"market; the scope is the market itself. Within-market "
"scope is stipulative; across-market scope is where the "
"failure lives."
),
definition_ref=(
"V_B = ratio at which a thing trades in a specified "
"market under specified legal and liquidity conditions"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.3,
justification=(
"denomination unit (usually money) is itself not a "
"signal; exchange-value inherits that failure. Same "
"thing trades at different exchange-values in "
"different jurisdictions and at different times."
),
provenance=theoretical(
rationale=(
"V_B's denomination inherits money's unit_invariant score "
"(0.05) by the inheritance argument — see money audit. "
"0.3 is higher than money's 0.05 because V_B also admits "
"ratio-forms (commodity-to-commodity) that do not inherit "
"the money failure."
),
source_refs=[
"money audit, unit_invariant criterion",
"Balassa 1964; Samuelson 1964 (PPP non-invariance)",
],
falsification_test=(
"demonstrate a cross-jurisdiction V_B measurement whose "
"invariance exceeds the invariance of its denominator "
"(money)"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.3,
justification=(
"referent shifts with reflexivity: the act of pricing "
"can move the price. Markets are measurement systems "
"that interact with the measured quantity."
),
provenance=theoretical(
rationale=(
"reflexivity is a structural property of markets as "
"measurement systems that participate in what they measure "
"(Soros, later formalized in econophysics). The referent "
"is not stable because the act of measurement perturbs it."
),
source_refs=[
"Soros 1987, 'The Alchemy of Finance'",
"Bouchaud & Potters 2003, 'Theory of Financial Risks and "
"Derivative Pricing'",
],
falsification_test=(
"identify a market whose prices are measurably independent "
"of the pricing process itself"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.6,
justification=(
"market-clearing procedures calibrate exchange-value "
"to itself; they do not calibrate it to use-value or "
"substrate-value"
),
provenance=design_choice(
rationale=(
"0.6 scores 'tautological self-calibration' as a partial "
"signal: within-V_B calibration is real, but calibration "
"to a non-V_B referent is absent. Splitting the concept "
"(self-calibration vs cross-calibration) would change the "
"score."
),
alternatives_considered=[
"0.9 counting market-clearing as full calibration",
"0.2 counting only cross-referent calibration",
"a two-vector split: within/cross",
],
falsification_test=(
"exhibit a market-clearing procedure that calibrates V_B "
"to V_A or V_C without passing through monetary units"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.6,
justification=(
"two observers looking at the same liquid market at "
"the same time will agree on the exchange-value"
),
provenance=empirical(
source_refs=[
"SEC Rule 605 order-execution disclosure data",
"FINRA TRACE corporate bond pricing inter-dealer quote "
"variance studies",
],
rationale=(
"exchange-pricing data directly shows inter-observer "
"agreement in liquid markets (Rule 605); agreement "
"collapses for illiquid instruments (TRACE variance)"
),
scope_caveat=(
"0.6 reflects only liquid-market cases; observer agreement "
"for Level-3 instruments under FASB ASC 820 is much weaker. "
"A subscore by liquidity tier would be more honest."
),
falsification_test=(
"measure inter-dealer quote variance for matched instruments "
"across liquidity strata; show >10% variance for liquid "
"instruments in functioning markets"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.2,
justification=(
"exchange-value is not conserved; it can be created "
"by credit expansion, destroyed by default, and "
"reflected into and out of existence by speculation"
),
provenance=theoretical(
rationale=(
"V_B inherits money's non-conservation (see money audit, "
"conservation_or_law). Score of 0.2 matches money's own "
"score on this criterion."
),
source_refs=[
"money audit, conservation_or_law criterion",
"McLeay, Radia & Thomas 2014, BoE Q1 Bulletin",
],
falsification_test=(
"derive a conservation law for aggregate V_B that holds "
"across credit cycles"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.7,
justification=(
"falsifiable within a specific market: attempt the "
"trade at the stated ratio and observe whether it "
"clears"
),
provenance=stipulative(
rationale=(
"V_B falsifiability is operationally bound to the market-"
"clearance test, which is part of the V_B definition. "
"0.7 acknowledges the test is clean within-market but "
"silent about cross-market claims."
),
definition_ref=(
"V_B operational definition: equilibrium-ratio test via "
"market clearing"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"reduce transaction costs in multilateral exchange by "
"providing a ratio at which things trade"
),
physical_referent=(
"equilibrium ratio in a specific market under specific "
"conditions"
),
informational_referent=(
"aggregated signal of current supply, demand, liquidity, "
"and counterparty confidence in a specific market"
),
drift_score=0.75,
drift_justification=(
"drifts from 'ratio within a specific market' to "
"'universal measurement of worth across all contexts'. "
"The drift is what lets exchange-value override "
"use-value and substrate-value in decisions."
),
),
correlation_to_real_signal=0.55,
correlation_justification=(
"correlation to market equilibrium is high within a specific "
"liquid market. Correlation to use-value or substrate-value "
"is weak and context-dependent."
),
notes=(
"exchange-value is the measurement that market infrastructure "
"is optimized to produce. It is a valid signal for its "
"narrow referent (market-clearing ratio) and a failed signal "
"for the broader referent it is usually invoked for "
"(worth of a thing)."
),
)

# ===========================================================================

# Part 4. V_C - substrate-value

# ===========================================================================

SUBSTRATE_VALUE_AUDIT = TermAudit(
term="value_C_substrate_value",
claimed_signal=(
"thermodynamic contribution to carrying capacity of the system "
"the thing participates in"
),
standard_setters=[
StandardSetter(
name="ecosystem ecology and biogeochemistry",
authority_basis="scientific discipline",
incentive_structure=(
"aligned with accurate measurement of substrate flows; "
"funding and institutional position relatively "
"independent of outcome"
),
independence_from_measured=0.7,
),
StandardSetter(
name="thermodynamics and physical chemistry",
authority_basis="scientific discipline",
incentive_structure=(
"aligned with accurate measurement; physical "
"conservation laws provide external discipline"
),
independence_from_measured=0.85,
),
StandardSetter(
name="industrial ecology / material flow analysis",
authority_basis="methodological credentialing",
incentive_structure=(
"aligned; the discipline exists to measure substrate "
"flows that conventional accounting excludes"
),
independence_from_measured=0.75,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.75,
justification=(
"scope defined once the system boundary is declared "
"and the carrying-capacity metric is specified"
),
provenance=stipulative(
rationale=(
"V_C is defined as a carrying-capacity contribution over "
"a declared system boundary; scope-definedness is part of "
"the definition. 0.75 rather than 1.0 reflects that "
"boundary selection has real effects (watershed vs basin) "
"that the score should acknowledge."
),
definition_ref=(
"V_C = thermodynamic contribution to carrying capacity "
"of the system the thing participates in"
),
),
),
SignalScore(
criterion="unit_invariant",
score=0.7,
justification=(
"units are physical (energy, mass, information, "
"biological capacity) and invariant across contexts "
"when the same system and metric are used"
),
provenance=theoretical(
rationale=(
"physical units are invariant by their metrological "
"definition. 0.7 (not 1.0) because cross-substrate "
"aggregation requires a superordinate unit (exergy is "
"one candidate per thermodynamics/exergy.py) and that "
"aggregation introduces its own invariance gaps."
),
source_refs=[
"BIPM SI unit definitions",
"Szargut 2005, 'Exergy Method: Technical and Ecological "
"Applications'",
],
falsification_test=(
"show that the physical unit system's invariance fails "
"within the same declared system boundary"
),
),
),
SignalScore(
criterion="referent_stable",
score=0.8,
justification=(
"referent is stable: carrying capacity is a property "
"of the system that exists independent of the "
"measurement"
),
provenance=theoretical(
rationale=(
"carrying capacity is a property of the physical system "
"independent of observation — measurement does not "
"perturb it in the way market pricing perturbs V_B. "
"Referent stability follows from physical realism."
),
source_refs=[
"Odum 1971, 'Fundamentals of Ecology'",
"Daly 1977, 'Steady-State Economics'",
],
falsification_test=(
"exhibit a carrying-capacity measurement procedure that "
"measurably alters the capacity of the system being "
"measured"
),
),
),
SignalScore(
criterion="calibration_exists",
score=0.7,
justification=(
"calibration exists in ecology (net primary productivity, "
"soil carbon, species richness), thermodynamics "
"(exergy), and biogeochemistry (nutrient cycling rates)"
),
provenance=empirical(
source_refs=[
"FAO Global Soil Organic Carbon Map methodology",
"ISO 14040 LCA standard; IPCC AR6 methodology chapters",
"Odum 1996, 'Environmental Accounting: Emergy and "
"Environmental Decision Making'",
],
rationale=(
"calibration procedures are published in peer-reviewed "
"ecology, thermodynamics, and biogeochemistry literature "
"with documented uncertainty bounds"
),
scope_caveat=(
"calibration quality varies across substrate types; soil "
"carbon measurement is mature, while coupling-strength "
"measurement in community basins is less developed"
),
falsification_test=(
"identify a substrate type where V_C is routinely claimed "
"and no reproducible measurement protocol exists"
),
),
),
SignalScore(
criterion="observer_invariant",
score=0.7,
justification=(
"two observers measuring the same substrate quantity "
"with the same protocol will agree within documented "
"tolerance"
),
provenance=empirical(
source_refs=[
"ISO/IEC 17025 (inter-laboratory calibration protocols)",
"IPCC uncertainty reporting guidelines",
],
rationale=(
"physical measurements conducted under standardized "
"protocols have documented inter-laboratory variance; "
"V_C inherits this when protocols are followed"
),
scope_caveat=(
"applies when protocols are followed; observer variance "
"rises sharply in field conditions, indigenous-knowledge "
"calibrations, and cross-method comparisons"
),
falsification_test=(
"assemble inter-laboratory round-robin samples on a V_C "
"quantity and show >50% inter-lab variance under "
"standardized protocol"
),
),
),
SignalScore(
criterion="conservation_or_law",
score=0.85,
justification=(
"substrate-value is constrained by thermodynamic "
"conservation laws and biogeochemical cycles; the "
"quantity obeys physical laws that markets do not"
),
provenance=theoretical(
rationale=(
"V_C is directly anchored in thermodynamic first and "
"second laws (energy conservation, entropy non-decrease) "
"and biogeochemical cycle conservation. The framework's "
"own thermodynamics/exergy.py enforces this."
),
source_refs=[
"First and second laws of thermodynamics",
"Gouy-Stodola theorem (exergy destruction ≥ 0)",
"Sciubba 2011, 'What did Lotka really say?'",
"thermodynamics/exergy.py (framework enforcement)",
],
falsification_test=(
"identify a V_C measurement that systematically violates "
"first-law or second-law bounds under the framework's "
"closure checks"
),
),
),
SignalScore(
criterion="falsifiability",
score=0.8,
justification=(
"strongly falsifiable: measure the system's carrying "
"capacity before and after the thing is added or "
"removed"
),
provenance=stipulative(
rationale=(
"V_C is defined operationally as the before/after "
"difference in system carrying capacity; the falsification "
"test is built into the definition"
),
definition_ref=(
"V_C operational definition: delta-carrying-capacity under "
"addition/removal of the thing"
),
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"account for a thing's contribution to the physical and "
"biological substrate on which all operations depend"
),
physical_referent=(
"change in system carrying capacity attributable to the "
"thing"
),
informational_referent=(
"change in system resilience, redundancy, and coupling "
"attributable to the thing"
),
drift_score=0.2,
drift_justification=(
"limited drift because the measurement is anchored in "
"physical law. Drift occurs when substrate-value is "
"reported in monetary units via 'ecosystem services' "
"pricing, which translates back to exchange-value."
),
),
correlation_to_real_signal=0.85,
correlation_justification=(
"high correlation with actual system persistence and "
"resilience when measured in physical units. Correlation "
"drops when substrate-value is translated into monetary "
"units for comparability with exchange-value."
),
notes=(
"substrate-value is the measurement most aligned with "
"thermodynamic reality and least captured by distinction-"
"seeking incentives. It is routinely excluded from the "
"collapsed term because its inclusion would reveal how much "
"reported 'value' is actually substrate drawdown."
),
)

# ===========================================================================

# Part 5. Linkage analysis - where V_A, V_B, V_C correlate or anti-correlate

# ===========================================================================

@dataclass
class ValueLinkage:
    """A documented relationship between two value measurements.

    `strength_estimate` is a numeric claim and carries a Provenance.
    Per AUDIT_07, linkage strengths without a Provenance are treated
    as incomplete by the framework's own coverage surface.
    """
    source: str                         # 'V_A', 'V_B', 'V_C'
    target: str                         # 'V_A', 'V_B', 'V_C'
    relation: str                       # 'positive', 'negative',
    # 'conditional', 'none'
    mechanism: str
    conditions: str
    falsification_test: str
    strength_estimate: float            # -1.0 fully anti, 0 none,
    # +1.0 fully positive
    strength_justification: str
    provenance: Optional["Provenance"] = None

VALUE_LINKAGES = [
ValueLinkage(
source="V_A", target="V_B",
relation="conditional",
mechanism=(
"use-value can drive exchange-value when the market "
"recognizes the need and the person with the need has "
"purchasing power. Either condition failing breaks the "
"linkage."
),
conditions=(
"need is market-legible; need-holder has purchasing power"
),
falsification_test=(
"find cases where use-value is high, conditions hold, and "
"exchange-value is zero or negative"
),
strength_estimate=0.4,
strength_justification=(
"weak positive when both conditions hold; zero or "
"negative otherwise. Insulin during a diabetic episode "
"has enormous use-value to a person without purchasing "
"power; its exchange-value to them is inaccessible."
),
provenance=placeholder(
rationale=(
"0.4 is the auditor's best guess at the average linkage "
"strength absent a meta-analysis. Sign is confident; "
"magnitude is not."
),
retirement_path=(
"meta-analysis of purchasing-power-stratified studies on "
"need-meeting goods (Case & Deaton 'Deaths of Despair' "
"dataset is one candidate starting point)"
),
),
),
ValueLinkage(
source="V_C", target="V_B",
relation="conditional",
mechanism=(
"substrate-value drives exchange-value only when "
"substrate depletion has become visible in market-legible "
"scarcity. Before the scarcity threshold, substrate-value "
"is free-ridden."
),
conditions=(
"substrate scarcity is acute enough to constrain "
"production; institutions exist to price the substrate"
),
falsification_test=(
"measure exchange-value of intact topsoil, aquifer water, "
"or pollinator populations across regions with different "
"scarcity levels"
),
strength_estimate=0.2,
strength_justification=(
"usually near zero; rises only when scarcity forces "
"market recognition"
),
provenance=placeholder(
rationale=(
"0.2 is the auditor's estimate based on the qualitative "
"pattern that substrate-value externalities are rarely "
"priced until scarcity forces recognition. No meta-"
"analysis of substrate price elasticity is cited."
),
retirement_path=(
"systematic review of ecosystem-services pricing studies "
"across substrate-scarcity gradients; MA/IPBES assessments "
"are candidate anchors"
),
),
),
ValueLinkage(
source="V_B", target="V_C",
relation="negative",
mechanism=(
"activities with high exchange-value frequently involve "
"substrate extraction; the exchange-value is partly a "
"rent on depleting the substrate faster than it "
"regenerates"
),
conditions=(
"extraction cost is externalized to the commons or to "
"future periods"
),
falsification_test=(
"sample high-exchange-value activities across sectors; "
"measure substrate trajectory; show positive trajectory "
"for the majority"
),
strength_estimate=-0.5,
strength_justification=(
"moderate negative in extractive sectors; near zero in "
"service or information sectors; occasionally positive "
"in explicitly regenerative sectors"
),
provenance=design_choice(
rationale=(
"LOAD-BEARING negative linkage: the sign (not the "
"magnitude) is the argument's punchline — exchange-value "
"growth draws down substrate. Changing sign to positive "
"would break the Tier-1-inheritance argument. -0.5 is a "
"design choice reflecting sectoral averaging."
),
alternatives_considered=[
"-0.8 (treating extractive sectors as the default)",
"-0.2 (treating information-sector prevalence as the "
"default)",
"a sector-indexed vector instead of a scalar",
],
falsification_test=(
"sample high-V_B activities across sectors; measure V_C "
"trajectory over 30 years; show positive trajectory in "
">50% of cases"
),
),
),
ValueLinkage(
source="V_A", target="V_C",
relation="positive",
mechanism=(
"things with high use-value for survival, health, and "
"function are usually things that also contribute to "
"substrate: food from healthy soil, water from intact "
"watersheds, knowledge that transmits across generations"
),
conditions=(
"use-value is measured against fundamental needs rather "
"than status-display needs"
),
falsification_test=(
"assess use-value and substrate-value of a representative "
"sample of fundamental-need goods and show low "
"correlation"
),
strength_estimate=0.5,
strength_justification=(
"moderate positive for fundamental-need goods; weaker "
"for luxury or status goods where use-value is defined "
"against distinction rather than need"
),
provenance=placeholder(
rationale=(
"0.5 is the auditor's estimate for a fundamental-needs "
"basket; strength varies sharply by need-type and the "
"fundamental-vs-status distinction is itself contested"
),
retirement_path=(
"domain-specific studies correlating fundamental-need "
"satisfaction with substrate flows (IPCC AR6 Impacts; "
"FAO nutrition/soil linkages)"
),
),
),
ValueLinkage(
source="V_C", target="V_A",
relation="positive",
mechanism=(
"substrate supports the contexts in which use-value is "
"realized. A damaged substrate reduces the set of needs "
"that can be met."
),
conditions="always, through long causal chains",
falsification_test=(
"document a case where substrate damage did not "
"eventually reduce use-value availability"
),
strength_estimate=0.7,
strength_justification=(
"strong positive over long timescales; weaker in the "
"short term because substrate drawdown can be invisible "
"until a threshold is crossed"
),
provenance=theoretical(
rationale=(
"V_A ⊂ what V_C makes possible: the set of needs that "
"can be met is bounded by the substrate's carrying "
"capacity. This is a set-theoretic constraint, not a "
"measurement; 0.7 rather than 1.0 reflects lag and "
"threshold nonlinearity in the coupling."
),
source_refs=[
"Rockström et al. 2009, 'A safe operating space for "
"humanity', Nature 461",
"Steffen et al. 2015, 'Planetary boundaries: Guiding "
"human development on a changing planet', Science 347",
],
falsification_test=(
"exhibit a case of documented substrate collapse with no "
"subsequent reduction in the need-meeting set over any "
"timescale"
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
"V_B (exchange-value) and V_C (substrate-value) are "
"negatively correlated in extractive sectors"
),
"falsification": (
"measure both across a sector sample; show positive "
"correlation"
),
},
{
"id": 2,
"claim": (
"most decisions reported as 'value-maximizing' under the "
"collapsed term maximize V_B while depleting V_C"
),
"falsification": (
"sample value-maximizing decisions; show V_C non-"
"decreasing in the majority"
),
},
{
"id": 3,
"claim": (
"things with high V_A for fundamental needs are "
"systematically under-measured by V_B when the need-"
"holder lacks purchasing power"
),
"falsification": (
"document cases where V_B correctly reflects V_A across "
"purchasing-power strata"
),
},
{
"id": 4,
"claim": (
"translating V_C into monetary units for comparability "
"with V_B systematically undervalues V_C because the "
"translation assumes marginal substitutability that does "
"not hold near carrying-capacity thresholds"
),
"falsification": (
"show that ecosystem-services monetary valuations track "
"threshold nonlinearity in substrate carrying capacity"
),
},
{
"id": 5,
"claim": (
"separating V_A, V_B, V_C in accounting produces "
"measurably different allocation decisions than the "
"collapsed measurement"
),
"falsification": (
"run parallel accounting on a matched operation; show "
"allocation decisions do not differ"
),
},
{
"id": 6,
"claim": (
"V_C is more observer-invariant than V_B under the "
"signal-criteria audit"
),
"falsification": (
"show that the signal-criteria audit rates V_B higher "
"than V_C on observer invariance when applied to matched "
"cases"
),
},
]

# ===========================================================================

# Part 7. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
"attack": (
"value is inherently subjective; trying to measure it "
"objectively is a category error"
),
"response": (
"subjective assessment applies cleanly to V_A (use-value "
"is first-person by construction). V_B is inter-subjective "
"(market-clearing). V_C is objective (thermodynamic). "
"Collapsing them into one token and then calling all of "
"them subjective is the actual category error. Separate "
"them and the subjectivity question resolves per "
"measurement."
),
},
{
"attack": (
"exchange-value aggregates use-value across all market "
"participants, so it is the best available measurement"
),
"response": (
"this claim requires purchasing-power symmetry to hold, "
"which empirically does not. Exchange-value weighted by "
"purchasing power aggregates wealth-holders' preferences, "
"not use-value. The claim is a statement about whose "
"use-value counts, not about aggregation validity."
),
},
{
"attack": (
"substrate-value is a pretense of objectivity that hides "
"normative choices about what substrates to count"
),
"response": (
"the choice of which substrates to count is normative, "
"granted. That is why substrate-value is reported as a "
"vector across multiple substrate types (soil, water, "
"carbon, biological capacity, knowledge), not as a "
"scalar. Each component is objective within its scope. "
"The attack applies equally to V_B, whose denomination "
"choice is also normative but rarely acknowledged."
),
},
{
"attack": (
"three-way separation is impractical because decisions "
"require a single number"
),
"response": (
"decisions do not require a single number; they require "
"a decision procedure. A decision procedure can take "
"three numbers and apply explicit weights. Collapsing "
"to one number applies hidden weights. The hidden "
"weights are where the substrate drawdown is encoded."
),
},
{
"attack": (
"V_A, V_B, V_C are not really separate because they "
"influence each other"
),
"response": (
"they influence each other through documented linkages; "
"that is what the linkage analysis is for. Influence is "
"not identity. Water and air are influenced by each "
"other through weather and still have separate "
"measurements."
),
},
{
"attack": (
"markets discover value more efficiently than explicit "
"measurement can"
),
"response": (
"markets discover V_B efficiently within liquid market "
"conditions. They do not discover V_A (because "
"purchasing power is not symmetric) and do not discover "
"V_C (because substrate is externalized from the market "
"by design). Efficiency-at-V_B is not a general claim "
"about value discovery."
),
},
{
"attack": (
"this is just relabeling old concepts (use-value, "
"exchange-value) that economics already rejected"
),
"response": (
"the labels are deliberately old because the distinctions "
"are old. Economics did not reject them on empirical "
"grounds; the profession consolidated around exchange-"
"value because it was measurable with available "
"infrastructure. The addition of V_C and the formal "
"signal-criteria audit is new; the inherited distinctions "
"are reused because they still work."
),
},
]

# ===========================================================================

# Part 8. Summary and collapsed-usage diagnosis

# ===========================================================================

def collapsed_usage_diagnosis() -> Dict:
    return {
    "term": "value_collapsed_current_usage",
    "claim": (
    "one word denoting use-value, exchange-value, and "
    "substrate-value as if they were one measurement"
    ),
    "failure": (
    "three referents with different signal properties fused "
    "into one token. Exchange-value dominates the fusion "
    "because market infrastructure produces it continuously "
    "and cheaply. Use-value and substrate-value are reported "
    "only when translated into exchange-value units, which "
    "systematically distorts them."
    ),
    "consequence": (
    "decisions made on the collapsed measurement trade "
    "substrate-value for exchange-value because the trade is "
    "invisible in the measurement. This is the mechanism by "
    "which Tier 1 economic terms (money, capital, investment, "
    "wealth, GDP, growth) inherit their failure: they all "
    "claim to measure value and all operate on the "
    "exchange-value-dominated collapsed token."
    ),
    "remediation": (
    "report V_A, V_B, V_C independently with their own units "
    "and calibration procedures. Use the linkage matrix to "
    "expose where they correlate and anti-correlate. Make "
    "substrate trade-offs explicit in decision procedures."
    ),
    }

ALL_VALUE_AUDITS = {
"collapsed": COLLAPSED_VALUE_AUDIT,
"V_A_use_value": USE_VALUE_AUDIT,
"V_B_exchange_value": EXCHANGE_VALUE_AUDIT,
"V_C_substrate_value": SUBSTRATE_VALUE_AUDIT,
}

if __name__ == "__main__":
    import json
    print("=== collapsed value audit ===")
    print(json.dumps(COLLAPSED_VALUE_AUDIT.summary(), indent=2))
    print()
    print("=== separated audits ===")
    for key, audit in ALL_VALUE_AUDITS.items():
        if key == "collapsed":
            continue
        print(f"- {key} -")
        print(json.dumps(audit.summary(), indent=2))
        print()
    print("=== linkages ===")
    for link in VALUE_LINKAGES:
        print(f"  {link.source} -> {link.target}  "
              f"({link.relation}, strength={link.strength_estimate:+.2f})")
    print()
    print("=== collapsed-usage diagnosis ===")
    print(json.dumps(collapsed_usage_diagnosis(), indent=2))
    print()
    print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
    print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
