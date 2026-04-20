“””
term_audit/civilization_substrate_scaling.py

Horizontal measurement tool for scale-appropriate function and
measurement requirements across civilization scales.

Core claim: functions and measurement systems emerge at specific
scales in response to specific coordination problems. Applying a
measurement system at scales where its coordination problem does not
exist produces capture rather than service. Applying it at scales
where it does serve a real coordination problem produces legitimate
structure.

The repo’s existing audits (money, expertise, productivity, capital,
etc.) become applications of this underlying scale analysis. Each
audited measurement system emerged at a specific scale to solve a
specific problem. Its validity is bounded by that scale.

This module establishes:

scale tiers                band, clan, village, town, city,
region, nation, continental, global
scale-transition problems  what coordination problems emerge at
each transition, forcing new structure
substrate functions        what functions must exist at each scale
for the scale to be thermodynamically
viable
measurement emergence      when each measurement system first
became necessary, and at what scale
scale-appropriateness      for any (measurement, scale) pair,
whether the measurement serves the
scale or captures it

The module is normative-with-descriptive-reference: it scores from
first-principles thermodynamic necessity, and cites historical
precedent as evidence that the first-principles analysis matches
observed human arrangements.

CC0. Stdlib only.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# ===========================================================================

# Part 1. Scale tiers

# ===========================================================================

class ScaleTier(Enum):
“”“Population scale tiers with approximate thresholds.

```
Boundaries are not sharp; they mark transitions where coordination
problems qualitatively change. Numbers are orders of magnitude, not
precise cutoffs.
"""
BAND = "band"              # 3-30: immediate family group
CLAN = "clan"              # 30-150: extended kin, Dunbar limit
VILLAGE = "village"        # 150-1500: stranger cooperation begins
TOWN = "town"              # 1500-15000: specialization deepens
CITY = "city"              # 15000-500000: abstraction layers required
METROPOLIS = "metropolis"  # 500000-10M: infrastructure complexity
REGION = "region"          # 10M-100M: inter-city coordination
NATION = "nation"          # 100M-1B: formal state apparatus
CONTINENTAL = "continental"  # 1B+: transnational coordination
GLOBAL = "global"          # all humans: planetary scale
```

SCALE_ORDER = [
ScaleTier.BAND,
ScaleTier.CLAN,
ScaleTier.VILLAGE,
ScaleTier.TOWN,
ScaleTier.CITY,
ScaleTier.METROPOLIS,
ScaleTier.REGION,
ScaleTier.NATION,
ScaleTier.CONTINENTAL,
ScaleTier.GLOBAL,
]

SCALE_THRESHOLDS = {
ScaleTier.BAND: (3, 30),
ScaleTier.CLAN: (30, 150),
ScaleTier.VILLAGE: (150, 1500),
ScaleTier.TOWN: (1500, 15000),
ScaleTier.CITY: (15000, 500000),
ScaleTier.METROPOLIS: (500000, 10_000_000),
ScaleTier.REGION: (10_000_000, 100_000_000),
ScaleTier.NATION: (100_000_000, 1_000_000_000),
ScaleTier.CONTINENTAL: (1_000_000_000, 5_000_000_000),
ScaleTier.GLOBAL: (5_000_000_000, 10_000_000_000),
}

def scale_for_population(n: int) -> ScaleTier:
“”“Classify a population size into its scale tier.”””
for tier, (low, high) in SCALE_THRESHOLDS.items():
if low <= n < high:
return tier
return ScaleTier.GLOBAL

# ===========================================================================

# Part 2. Coordination problems and scale transitions

# ===========================================================================

# 

# At each transition, specific coordination problems emerge because

# the prior mechanisms no longer work. A village cannot be run like a

# clan because reciprocity networks cannot scale past Dunbar. A city

# cannot be run like a village because most residents are strangers

# to each other. Each transition forces new coordination structure,

# which creates both solutions and new capture vectors.

# —————————————————————————

@dataclass
class CoordinationProblem:
“”“A coordination problem that emerges at a specific scale
transition.”””
problem: str
emerges_at: ScaleTier
prior_mechanism: str                # how it was handled at smaller
# scale
why_prior_fails: str                # why the smaller-scale
# mechanism stops working
solutions_available: List[str]      # what structures can address it
capture_vectors: List[str]          # how each solution can be
# captured
historical_precedents: List[str]

COORDINATION_PROBLEMS = [
CoordinationProblem(
problem=“stranger_cooperation”,
emerges_at=ScaleTier.VILLAGE,
prior_mechanism=(
“direct kinship and reputation; you know everyone and “
“their history”
),
why_prior_fails=(
“population exceeds Dunbar number (~150); most people are “
“no longer directly known; reputation networks sparse”
),
solutions_available=[
“customary law with elder councils”,
“reciprocity networks with introducers”,
“ritualized stranger-hosting obligations”,
“public reputation (gossip networks)”,
],
capture_vectors=[
“elder councils ossifying into hereditary authority”,
“reputation networks capturable by status-maintainers”,
“hosting obligations becoming one-way extraction”,
],
historical_precedents=[
“iroquois confederacy councils”,
“germanic thing assemblies”,
“ojibwe council structures”,
],
),
CoordinationProblem(
problem=“water_and_waste_separation”,
emerges_at=ScaleTier.VILLAGE,
prior_mechanism=(
“mobile band moves when local area becomes contaminated; “
“no persistent waste accumulation”
),
why_prior_fails=(
“settled residence means waste accumulates near water; “
“disease vectors concentrate”
),
solutions_available=[
“spatial separation of water source from dwelling and “
“waste disposal”,
“rotating field use with fallow periods”,
“composting and soil incorporation of waste”,
“collective norms enforcing separation”,
],
capture_vectors=[
“water access privatized by powerful families”,
“waste management becoming low-status caste work”,
],
historical_precedents=[
“mesopotamian qanat systems”,
“roman aqueducts initially, then captured”,
“indigenous agricultural waste cycling”,
],
),
CoordinationProblem(
problem=“food_storage_and_seasonality”,
emerges_at=ScaleTier.CLAN,
prior_mechanism=(
“small-group seasonal migration following food sources; “
“minimal storage”
),
why_prior_fails=(
“larger groups cannot move together efficiently; “
“settlement becomes advantageous; storage bridges lean “
“seasons”
),
solutions_available=[
“collective granary with shared-access rules”,
“household storage with reciprocal sharing obligations”,
“preservation techniques (drying, smoking, fermentation, “
“root cellars)”,
“seed stock management across seasons”,
],
capture_vectors=[
“granary control becoming political power”,
“storage-holder authority becoming hereditary”,
“seed stock privatized”,
],
historical_precedents=[
“neolithic collective granaries”,
“hopi and pueblo storage traditions”,
“anglo-saxon thegn food rent”,
],
),
CoordinationProblem(
problem=“knowledge_transmission_beyond_memory”,
emerges_at=ScaleTier.VILLAGE,
prior_mechanism=(
“apprenticeship, storytelling, direct observation; “
“knowledge lives in the person”
),
why_prior_fails=(
“specialization increases; more distinct knowledge bases “
“exist than any single person can master; death of “
“specialist loses specialty unless transmitted”
),
solutions_available=[
“apprenticeship networks with multiple masters”,
“song and story traditions with mnemonic structure”,
“landscape-encoded knowledge (place-names as memory “
“aids)”,
“collective teaching by elder circles”,
“eventually: writing”,
],
capture_vectors=[
“knowledge-holder class becoming hereditary”,
“literacy becoming class marker”,
“credentialing emerging (very late)”,
],
historical_precedents=[
“aboriginal songlines”,
“vedic oral traditions”,
“guild apprenticeship systems”,
“mesopotamian scribal schools”,
],
),
CoordinationProblem(
problem=“cross_village_conflict_resolution”,
emerges_at=ScaleTier.TOWN,
prior_mechanism=(
“within-village customary law; inter-village disputes “
“resolved by feud or kin-arbitration”
),
why_prior_fails=(
“feud is costly; arbitration requires shared customs which “
“erode at larger scale”
),
solutions_available=[
“confederacy councils with rotating leadership”,
“shared ritual centers with neutral authority”,
“formal law codes applying across villages”,
“inter-village marriage alliances”,
],
capture_vectors=[
“law codes becoming elite tools”,
“confederacy leadership consolidating power”,
“ritual centers becoming temple hierarchies”,
],
historical_precedents=[
“iroquois great law of peace”,
“code of hammurabi”,
“anglo-saxon witenagemot”,
“swiss canton confederacies”,
],
),
CoordinationProblem(
problem=“exchange_with_strangers_at_distance”,
emerges_at=ScaleTier.TOWN,
prior_mechanism=(
“gift exchange, reciprocity, barter between known parties”
),
why_prior_fails=(
“trading partners are strangers; reciprocity cannot be “
“verified over time and distance; direct barter requires “
“coincidence of wants”
),
solutions_available=[
“standardized trade goods (obsidian, shells, cattle)”,
“weight-and-measure commodity money (grain, silver)”,
“credit networks with merchant reputation”,
“caravan companies with shared risk”,
],
capture_vectors=[
“commodity money supply controlled by issuers”,
“credit networks becoming rentier class”,
“caravan protection becoming extortion”,
],
historical_precedents=[
“mesopotamian silver-by-weight trade”,
“medieval bills of exchange”,
“silk road caravan systems”,
],
),
CoordinationProblem(
problem=“large_capital_coordination”,
emerges_at=ScaleTier.CITY,
prior_mechanism=(
“household and guild-scale production; capital is “
“tools and workshop, directly held”
),
why_prior_fails=(
“certain productions (mines, irrigation systems, “
“shipbuilding, later factories) require capital “
“assemblies exceeding any individual household”
),
solutions_available=[
“guild cooperatives pooling member capital”,
“state enterprise (royal mines, public works)”,
“commenda and early partnership forms”,
“joint-stock companies (very late, industrial era)”,
],
capture_vectors=[
“guild monopolies restricting entry”,
“state enterprise extracting for ruler”,
“joint-stock concentrating ownership away from workers”,
“financialization decoupling claims from production”,
],
historical_precedents=[
“roman collegia”,
“medieval guilds”,
“dutch east india company”,
“hanseatic league”,
],
),
CoordinationProblem(
problem=“task_allocation_without_direct_observation”,
emerges_at=ScaleTier.CITY,
prior_mechanism=(
“apprenticeship and reputation; capacity directly “
“observable because you see the person work”
),
why_prior_fails=(
“population exceeds ability to personally know all “
“practitioners; task matching requires proxy for capacity”
),
solutions_available=[
“guild certifications (master, journeyman)”,
“university credentialing”,
“reputation networks within sub-communities”,
“probationary work with retention review”,
“rotational apprenticeship”,
],
capture_vectors=[
“guild cost-gating excluding capable practitioners”,
“university credentialing serving class reproduction”,
“credentialing bodies drifting from capacity to status”,
],
historical_precedents=[
“medieval craft guilds with masterpieces”,
“chinese imperial examinations”,
“modern professional licensing”,
],
),
CoordinationProblem(
problem=“infrastructure_beyond_community_scale”,
emerges_at=ScaleTier.CITY,
prior_mechanism=(
“village-scale shared maintenance of wells, paths, “
“common fields”
),
why_prior_fails=(
“roads, aqueducts, sewers, harbors, bridges require “
“labor and materials beyond any community’s capacity; “
“benefits distributed across users who do not “
“personally know each other”
),
solutions_available=[
“corvée labor obligation”,
“tax-funded public works”,
“confraternities and civic societies”,
“state infrastructure ministries”,
],
capture_vectors=[
“corvée becoming serfdom”,
“tax allocation captured by elite projects”,
“infrastructure budgets diverted”,
],
historical_precedents=[
“roman road and aqueduct systems”,
“medieval bridge-guilds”,
“edo period Japanese road maintenance”,
],
),
CoordinationProblem(
problem=“cross_regional_governance”,
emerges_at=ScaleTier.REGION,
prior_mechanism=(
“city-state and confederacy-of-cities governance”
),
why_prior_fails=(
“populations spanning thousands of kilometers with “
“different customary laws, languages, and interests “
“cannot be governed by city-scale mechanisms”
),
solutions_available=[
“federation with enumerated shared powers”,
“empire with local governors”,
“treaty network among autonomous regions”,
“ecclesiastical governance parallel to political”,
],
capture_vectors=[
“federation consolidating into unitary state”,
“empire extracting from periphery for center”,
“treaty enforcement favoring powerful signatories”,
],
historical_precedents=[
“holy roman empire”,
“iroquois confederacy extended”,
“han china regional administration”,
],
),
CoordinationProblem(
problem=“planetary_commons_management”,
emerges_at=ScaleTier.GLOBAL,
prior_mechanism=(
“regional or national resource management within “
“political boundaries”
),
why_prior_fails=(
“atmosphere, oceans, climate, migratory species, “
“pandemic disease, radiation all cross political “
“boundaries; no existing institution has authority “
“or scope”
),
solutions_available=[
“international treaty frameworks”,
“global scientific monitoring with distributed “
“authority”,
“commons-pool institutions at planetary scale “
“(proposed, not implemented)”,
“polycentric governance (Ostrom-style)”,
],
capture_vectors=[
“treaty frameworks captured by powerful states”,
“scientific authority captured by funding sources”,
“international bodies becoming extensions of hegemonic “
“interests”,
],
historical_precedents=[
“montreal protocol (partial success)”,
“international whaling commission (captured)”,
“IPCC (partial, contested)”,
],
),
]

# ===========================================================================

# Part 3. Substrate functions by scale

# ===========================================================================

# 

# What functions must exist at each scale for the scale to be

# thermodynamically viable? These are first-principles necessary

# functions, not specific organizational forms that provide them.

# —————————————————————————

@dataclass
class SubstrateFunction:
“”“A function that must exist at or above a given scale.”””
function: str
first_required_at: ScaleTier
rationale: str
forms: List[str]                    # possible organizational forms
# that provide the function
failure_consequence: str
measurement_systems_that_emerge_to_manage: List[str]

SUBSTRATE_FUNCTIONS = [
SubstrateFunction(
function=“subsistence_food_production”,
first_required_at=ScaleTier.BAND,
rationale=(
“organisms require caloric input; without food “
“production or collection, population collapses within “
“weeks”
),
forms=[
“foraging and hunting”,
“horticulture”,
“pastoralism”,
“agriculture”,
“mixed subsistence strategies”,
],
failure_consequence=“starvation within weeks”,
measurement_systems_that_emerge_to_manage=[
“seasonal observation and knowledge”,
“grain and herd accounting (village+)”,
“agricultural statistics (city+)”,
“commodity markets (city+)”,
],
),
SubstrateFunction(
function=“water_access_and_quality”,
first_required_at=ScaleTier.BAND,
rationale=(
“organisms require potable water; contaminated water “
“produces rapid population-level illness”
),
forms=[
“surface water from running streams”,
“wells and springs”,
“cisterns and rain capture”,
“aqueducts and distribution systems”,
],
failure_consequence=“dehydration in days; disease spread”,
measurement_systems_that_emerge_to_manage=[
“local knowledge of seasonal water sources”,
“well ownership and use rules (village+)”,
“water rights law (town+)”,
“water quality testing (city+)”,
],
),
SubstrateFunction(
function=“shelter_and_thermal_regulation”,
first_required_at=ScaleTier.BAND,
rationale=(
“organisms require thermal envelope for survival in “
“most climates; exposure produces rapid mortality”
),
forms=[
“natural shelter (caves, windbreaks)”,
“portable shelter (tents, yurts)”,
“permanent dwellings”,
“urban housing systems”,
],
failure_consequence=(
“exposure mortality in hours to days depending on “
“climate”
),
measurement_systems_that_emerge_to_manage=[
“construction knowledge and apprenticeship”,
“building codes (city+)”,
“housing markets (city+)”,
],
),
SubstrateFunction(
function=“waste_separation_from_life_substrate”,
first_required_at=ScaleTier.VILLAGE,
rationale=(
“settled populations accumulate waste; proximity to “
“water or food produces disease; band-scale groups “
“avoided this through mobility”
),
forms=[
“spatial separation norms”,
“composting and soil incorporation”,
“sewerage and treatment”,
“waste removal services”,
],
failure_consequence=(
“cholera, dysentery, typhoid; population collapse in “
“weeks to months”
),
measurement_systems_that_emerge_to_manage=[
“customary use-rules (village)”,
“sanitation codes (city+)”,
“public health statistics (city+)”,
],
),
SubstrateFunction(
function=“knowledge_transmission_across_generations”,
first_required_at=ScaleTier.BAND,
rationale=(
“humans are obligate cultural animals; essential “
“knowledge (food, water, medicine, danger) dies with “
“the knowledge-holder unless transmitted”
),
forms=[
“apprenticeship”,
“storytelling and oral tradition”,
“landscape-encoded knowledge”,
“writing”,
“formal schooling”,
“apprentice-guild hybrid”,
],
failure_consequence=(
“loss of essential knowledge over one generation; “
“accumulated failure over multiple generations”
),
measurement_systems_that_emerge_to_manage=[
“apprenticeship completion recognition”,
“guild masterpieces (town+)”,
“university credentialing (city+)”,
“professional licensing (nation+)”,
],
),
SubstrateFunction(
function=“conflict_resolution_within_group”,
first_required_at=ScaleTier.BAND,
rationale=(
“social animals produce disputes; unresolved disputes “
“fracture group; group fracture reduces survival in “
“cooperative-dependent species”
),
forms=[
“direct negotiation”,
“elder mediation”,
“customary arbitration”,
“formal courts and law”,
],
failure_consequence=(
“group fracture, feud, reduced cooperation capacity”
),
measurement_systems_that_emerge_to_manage=[
“customary law (village)”,
“written law codes (town+)”,
“court systems (city+)”,
],
),
SubstrateFunction(
function=“defense_and_boundary_maintenance”,
first_required_at=ScaleTier.CLAN,
rationale=(
“bands can flee or merge; clan-scale groups with “
“territory must defend access to resources against “
“other groups”
),
forms=[
“general adult defense capacity (most pre-industrial)”,
“specialized warrior classes”,
“standing armies”,
“police and border enforcement”,
],
failure_consequence=(
“resource loss to competing groups; territorial “
“displacement; population collapse”
),
measurement_systems_that_emerge_to_manage=[
“warrior reputation and lineage”,
“military rank systems (town+)”,
“citizenship and conscription (nation+)”,
],
),
SubstrateFunction(
function=“kinship_and_reproductive_coordination”,
first_required_at=ScaleTier.CLAN,
rationale=(
“genetic diversity requires exogamy; without formal “
“kinship structure at clan scale, inbreeding occurs”
),
forms=[
“kinship reckoning systems (matrilineal, patrilineal, “
“bilateral)”,
“marriage rules and alliance networks”,
“clan exogamy with other-clan marriage”,
],
failure_consequence=(
“genetic collapse over generations; social conflict “
“from reproductive competition”
),
measurement_systems_that_emerge_to_manage=[
“kinship terminology and genealogy”,
“marriage registries (town+)”,
“genetic counseling (nation+, very late)”,
],
),
SubstrateFunction(
function=“ecological_and_seasonal_observation”,
first_required_at=ScaleTier.BAND,
rationale=(
“food timing, hazard anticipation, and substrate health “
“require continuous observation and transmitted knowledge”
),
forms=[
“individual and shared observation”,
“landscape-encoded knowledge systems”,
“phenological calendars”,
“formal scientific monitoring”,
],
failure_consequence=(
“crop and harvest failures, missed hazards, substrate “
“drawdown without detection”
),
measurement_systems_that_emerge_to_manage=[
“seasonal knowledge and ritual calendar”,
“agricultural almanacs (town+)”,
“scientific monitoring networks (city+)”,
“remote sensing (nation+)”,
],
),
SubstrateFunction(
function=“infrastructure_maintenance”,
first_required_at=ScaleTier.VILLAGE,
rationale=(
“wells, paths, granaries, shared buildings degrade “
“without maintenance; collective goods require “
“collective maintenance”
),
forms=[
“rotational community labor”,
“specialized maintenance roles”,
“dedicated infrastructure workforce”,
“public works departments”,
],
failure_consequence=(
“progressive failure of shared infrastructure; “
“cascading failures at larger scale”
),
measurement_systems_that_emerge_to_manage=[
“work-day rotation records (village)”,
“corvée obligations (town+)”,
“tax-funded maintenance (city+)”,
“infrastructure budgets (nation+)”,
],
),
SubstrateFunction(
function=“exchange_beyond_direct_reciprocity”,
first_required_at=ScaleTier.TOWN,
rationale=(
“division of labor produces goods needed by people “
“outside the producer’s reciprocity network; some “
“coordination mechanism required”
),
forms=[
“gift exchange with extended reciprocity”,
“standardized trade commodities”,
“weight-based commodity money”,
“token money with legal backing”,
“credit and banking”,
],
failure_consequence=(
“specialization collapses; productivity falls; cannot “
“support larger populations”
),
measurement_systems_that_emerge_to_manage=[
“trade goods standards”,
“weights and measures (town+)”,
“money and prices (town+)”,
“banking (city+)”,
“financial markets (metropolis+)”,
],
),
SubstrateFunction(
function=“long_horizon_substrate_stewardship”,
first_required_at=ScaleTier.CLAN,
rationale=(
“soil, forest, fisheries, water all require management “
“at timescales exceeding individual lifetime; without “
“stewardship institutions, tragedy-of-commons dynamics “
“deplete substrate”
),
forms=[
“sacred restrictions on overuse”,
“commons management institutions (Ostrom)”,
“rotation and fallow systems”,
“conservation law and enforcement”,
],
failure_consequence=(
“substrate depletion over generations; civilization-”
“level collapse (many historical examples)”
),
measurement_systems_that_emerge_to_manage=[
“sacred and customary restrictions”,
“commons use-records (village)”,
“property and use rights (town+)”,
“conservation statistics (nation+)”,
],
),
SubstrateFunction(
function=“cross_boundary_commons_management”,
first_required_at=ScaleTier.REGION,
rationale=(
“watersheds, migratory species, weather patterns, and “
“atmospheric conditions cross political boundaries; “
“local management insufficient”
),
forms=[
“inter-community agreements”,
“confederation authorities”,
“international treaties”,
“polycentric governance”,
],
failure_consequence=(
“commons degradation at regional or planetary scale; “
“cascade failures across connected systems”
),
measurement_systems_that_emerge_to_manage=[
“boundary commission records (region+)”,
“treaty enforcement mechanisms (nation+)”,
“international environmental monitoring (global)”,
],
),
]

# ===========================================================================

# Part 4. Measurement emergence and scale-appropriateness

# ===========================================================================

@dataclass
class MeasurementSystem:
“”“A measurement system and its scale-appropriateness profile.”””
name: str
emerged_at: ScaleTier
problem_served: str
appropriate_range: List[ScaleTier]  # scales where it serves
capture_range: List[ScaleTier]      # scales where applying it
# produces capture
descriptive_notes: str

MEASUREMENT_SYSTEMS = [
MeasurementSystem(
name=“direct_reputation”,
emerged_at=ScaleTier.BAND,
problem_served=“capacity assessment within known network”,
appropriate_range=[ScaleTier.BAND, ScaleTier.CLAN,
ScaleTier.VILLAGE],
capture_range=[ScaleTier.CITY, ScaleTier.METROPOLIS,
ScaleTier.REGION, ScaleTier.NATION],
descriptive_notes=(
“most effective at scales where individuals personally “
“know the measured person’s work history; becomes “
“susceptible to gossip capture and clique dynamics at “
“village+ scale; at city+ scale degrades to brand or “
“celebrity rather than reputation”
),
),
MeasurementSystem(
name=“customary_law”,
emerged_at=ScaleTier.VILLAGE,
problem_served=“conflict resolution with shared tradition”,
appropriate_range=[ScaleTier.VILLAGE, ScaleTier.TOWN],
capture_range=[ScaleTier.CITY, ScaleTier.METROPOLIS,
ScaleTier.REGION],
descriptive_notes=(
“requires shared cultural context to function; at town+ “
“scale with multiple subcultures, customary law fractures “
“or privileges one subculture over others”
),
),
MeasurementSystem(
name=“written_law_codes”,
emerged_at=ScaleTier.TOWN,
problem_served=(
“conflict resolution across multiple villages with “
“different customs”
),
appropriate_range=[ScaleTier.TOWN, ScaleTier.CITY,
ScaleTier.METROPOLIS, ScaleTier.REGION,
ScaleTier.NATION],
capture_range=[ScaleTier.BAND, ScaleTier.CLAN,
ScaleTier.VILLAGE],
descriptive_notes=(
“applied at village or smaller scale, written law “
“crowds out customary law and substitutes formal “
“procedure for direct resolution; often inefficient “
“and alienating at those scales”
),
),
MeasurementSystem(
name=“commodity_money”,
emerged_at=ScaleTier.TOWN,
problem_served=“exchange among non-reciprocity strangers”,
appropriate_range=[ScaleTier.TOWN, ScaleTier.CITY,
ScaleTier.METROPOLIS],
capture_range=[ScaleTier.BAND, ScaleTier.CLAN,
ScaleTier.VILLAGE, ScaleTier.REGION,
ScaleTier.NATION, ScaleTier.CONTINENTAL,
ScaleTier.GLOBAL],
descriptive_notes=(
“applied at clan/village scale, money crowds out “
“reciprocity networks; applied at nation/global scale, “
“decouples from any real commodity backing and becomes “
“substrate for financial extraction (see money audit)”
),
),
MeasurementSystem(
name=“guild_certification”,
emerged_at=ScaleTier.TOWN,
problem_served=(
“capacity verification for strangers in skilled trades”
),
appropriate_range=[ScaleTier.TOWN, ScaleTier.CITY],
capture_range=[ScaleTier.METROPOLIS, ScaleTier.REGION,
ScaleTier.NATION],
descriptive_notes=(
“functions when guild members still know each other and “
“can audit credentials against practice; at larger scale “
“credentialing becomes recursive and cost-gates “
“(see expertise audit)”
),
),
MeasurementSystem(
name=“university_credentialing”,
emerged_at=ScaleTier.CITY,
problem_served=“knowledge transmission at urban scale”,
appropriate_range=[ScaleTier.CITY, ScaleTier.METROPOLIS],
capture_range=[ScaleTier.REGION, ScaleTier.NATION,
ScaleTier.CONTINENTAL],
descriptive_notes=(
“at nation+ scale, credentialing decouples from capacity “
“entirely; credentials become class markers and access “
“filters rather than capacity signals”
),
),
MeasurementSystem(
name=“financial_capital_markets”,
emerged_at=ScaleTier.METROPOLIS,
problem_served=“large capital coordination for industry”,
appropriate_range=[ScaleTier.METROPOLIS],
capture_range=[ScaleTier.REGION, ScaleTier.NATION,
ScaleTier.CONTINENTAL, ScaleTier.GLOBAL],
descriptive_notes=(
“at region+ scale, capital markets decouple from “
“productive operations; financialization dominates “
“and extracts from substrate (see capital audit)”
),
),
MeasurementSystem(
name=“productivity_aggregates”,
emerged_at=ScaleTier.NATION,
problem_served=(
“national economic planning and comparison”
),
appropriate_range=[],  # never truly appropriate under
# current definition
capture_range=[ScaleTier.VILLAGE, ScaleTier.TOWN,
ScaleTier.CITY, ScaleTier.METROPOLIS,
ScaleTier.REGION, ScaleTier.NATION,
ScaleTier.CONTINENTAL, ScaleTier.GLOBAL],
descriptive_notes=(
“productivity as currently defined fails signal criteria “
“at every scale (see productivity audit). The “
“measurement problem it claims to solve (output per “
“input) is real but the current measurement produces “
“capture rather than service at every scale”
),
),
MeasurementSystem(
name=“international_monitoring”,
emerged_at=ScaleTier.GLOBAL,
problem_served=(
“planetary commons management (climate, disease, “
“migration, oceans)”
),
appropriate_range=[ScaleTier.CONTINENTAL, ScaleTier.GLOBAL],
capture_range=[],  # still too early in deployment for
# capture to have dominated
descriptive_notes=(
“legitimately needed at continental and global scale “
“because the commons problems are transnational; “
“currently in early development; capture mechanisms “
“already visible (funding capture, political capture “
“of scientific bodies) but not yet dominant”
),
),
]

# ===========================================================================

# Part 5. Scale-appropriateness scoring

# ===========================================================================

def measurement_appropriateness(
measurement_name: str,
scale: ScaleTier,
) -> float:
“””
Score whether a measurement is appropriate at a given scale.

```
Returns:
  1.0   measurement emerged at this scale to serve it;
        near-full appropriateness
  0.75  scale is within the measurement's appropriate range
  0.25  scale is below the measurement's emergence scale;
        measurement crowds out scale-appropriate mechanisms
  0.0   scale is in the measurement's capture range; applying
        it produces capture

Unknown measurements return 0.5 (no data).
"""
for m in MEASUREMENT_SYSTEMS:
    if m.name == measurement_name:
        if scale == m.emerged_at:
            return 1.0
        if scale in m.appropriate_range:
            return 0.75
        if scale in m.capture_range:
            return 0.0
        emerged_idx = SCALE_ORDER.index(m.emerged_at)
        scale_idx = SCALE_ORDER.index(scale)
        if scale_idx < emerged_idx:
            return 0.25
        return 0.5
return 0.5
```

def substrate_functions_at_scale(
scale: ScaleTier,
) -> List[SubstrateFunction]:
“”“Return all substrate functions required at or below the
given scale.”””
target_idx = SCALE_ORDER.index(scale)
return [
f for f in SUBSTRATE_FUNCTIONS
if SCALE_ORDER.index(f.first_required_at) <= target_idx
]

def coordination_problems_at_scale(
scale: ScaleTier,
) -> List[CoordinationProblem]:
“”“Return all coordination problems that emerge at or below
the given scale.”””
target_idx = SCALE_ORDER.index(scale)
return [
p for p in COORDINATION_PROBLEMS
if SCALE_ORDER.index(p.emerges_at) <= target_idx
]

# ===========================================================================

# Part 6. Collapse analysis and minimum viable civilization

# ===========================================================================

@dataclass
class CollapseProfile:
“”“Analysis of what persists and what fails if a scale tier’s
coordination mechanisms collapse.”””
collapsed_scale: ScaleTier
functions_still_supported: List[str]
functions_that_fail: List[str]
fallback_scale: ScaleTier           # largest scale that can
# still support life
recovery_requirements: List[str]

MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS = [
“subsistence_food_production”,
“water_access_and_quality”,
“shelter_and_thermal_regulation”,
“knowledge_transmission_across_generations”,
“conflict_resolution_within_group”,
“ecological_and_seasonal_observation”,
“long_horizon_substrate_stewardship”,
]

def analyze_collapse(
collapsed_scale: ScaleTier,
) -> CollapseProfile:
“””
Analyze what happens if coordination at a given scale collapses.

```
The logic: functions that were first required at scales larger
than the collapse scale may fail. Functions required at or below
the collapse scale (specifically, at or below the largest
surviving scale) can persist.
"""
collapsed_idx = SCALE_ORDER.index(collapsed_scale)

# Largest surviving scale is one below the collapsed scale
if collapsed_idx == 0:
    fallback = ScaleTier.BAND
else:
    fallback = SCALE_ORDER[collapsed_idx - 1]

fallback_idx = SCALE_ORDER.index(fallback)

supported = [
    f.function for f in SUBSTRATE_FUNCTIONS
    if SCALE_ORDER.index(f.first_required_at) <= fallback_idx
]
failing = [
    f.function for f in SUBSTRATE_FUNCTIONS
    if SCALE_ORDER.index(f.first_required_at) > fallback_idx
]

recovery: List[str] = []
if collapsed_scale in (ScaleTier.NATION, ScaleTier.CONTINENTAL,
                       ScaleTier.GLOBAL):
    recovery.append(
        "rebuild regional coordination before attempting "
        "national reconstruction"
    )
    recovery.append(
        "preserve and transmit knowledge systems at village "
        "and town scale"
    )
if collapsed_scale in (ScaleTier.CITY, ScaleTier.METROPOLIS):
    recovery.append(
        "preserve infrastructure maintenance capacity at "
        "village scale"
    )
    recovery.append(
        "rebuild town-scale exchange networks before city "
        "reconstruction"
    )
if collapsed_scale in (ScaleTier.VILLAGE, ScaleTier.TOWN):
    recovery.append(
        "preserve food, water, shelter, and knowledge "
        "transmission at clan scale"
    )
    recovery.append(
        "rebuild village-scale commons institutions before "
        "larger-scale coordination"
    )

return CollapseProfile(
    collapsed_scale=collapsed_scale,
    functions_still_supported=supported,
    functions_that_fail=failing,
    fallback_scale=fallback,
    recovery_requirements=recovery,
)
```

# ===========================================================================

# Part 7. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
“id”: 1,
“claim”: (
“measurement systems applied at scales outside their “
“appropriate_range produce measurable capture effects “
“(drift, cost gating, authority inversion)”
),
“falsification”: (
“apply a measurement across scales; show capture effects “
“emerge only randomly, not correlated with scale “
“mismatch”
),
},
{
“id”: 2,
“claim”: (
“substrate functions required at smaller scales remain “
“required at all larger scales; they do not become “
“optional”
),
“falsification”: (
“find a civilization at any scale that has successfully “
“eliminated one of the substrate functions required at “
“smaller scales”
),
},
{
“id”: 3,
“claim”: (
“collapses of larger-scale coordination preserve smaller-”
“scale function if smaller-scale institutions are intact”
),
“falsification”: (
“document historical cases where large-scale collapse “
“produced smaller-scale collapse despite intact local “
“institutions”
),
},
{
“id”: 4,
“claim”: (
“the bare-essentials minimum viable civilization “
“functions (food, water, shelter, knowledge transmission, “
“conflict resolution, ecological observation, substrate “
“stewardship) are the same across all human cultures “
“that have achieved multi-generational persistence”
),
“falsification”: (
“identify a multi-generational culture that omits one “
“of these functions”
),
},
{
“id”: 5,
“claim”: (
“measurement systems emerge at specific scales in “
“predictable response to specific coordination problems; “
“the emergence order is consistent across civilizations”
),
“falsification”: (
“identify civilizations where measurement systems emerged “
“in different order (e.g., university credentialing “
“before writing, or financial capital before commodity “
“money)”
),
},
{
“id”: 6,
“claim”: (
“large-scale measurement systems (national productivity, “
“global finance) cannot substitute for smaller-scale “
“substrate function; attempts to do so produce substrate “
“drawdown”
),
“falsification”: (
“demonstrate a case where large-scale measurement-system “
“management successfully substituted for village-scale “
“substrate stewardship over 50+ years”
),
},
{
“id”: 7,
“claim”: (
“current civilization has allowed smaller-scale substrate “
“institutions to atrophy while building larger-scale “
“measurement systems; this produces cascade vulnerability “
“because collapse at the top layers removes the “
“measurement infrastructure before smaller-scale “
“replacements can be rebuilt”
),
“falsification”: (
“document that village-scale substrate institutions are “
“stable or strengthening in current civilization”
),
},
]

# ===========================================================================

# Part 8. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
“attack”: (
“this is romanticizing small-scale society; pre-modern “
“life was brutal and short”
),
“response”: (
“the module does not advocate returning to any specific “
“historical scale. It analyzes what functions are “
“required at each scale and how measurement systems “
“apply. Pre-modern life had limitations; those “
“limitations do not invalidate the analysis of which “
“functions must exist. Modern capacities built on top “
“of a failing substrate base also produce brutality “
“and shortened lives (substrate exhaustion, ecological “
“collapse, deaths of despair).”
),
},
{
“attack”: (
“scale tiers are arbitrary; population thresholds don’t “
“produce sharp transitions”
),
“response”: (
“the thresholds mark zones where coordination problems “
“qualitatively change. Dunbar’s number is empirical. “
“The village-to-town transition produces stranger-”
“cooperation problems that clan-scale groups do not “
“face. The city transition produces anonymity problems “
“towns do not face. The transitions are not sharp but “
“they are real. The module does not claim precision at “
“the individual level; it claims regime changes at “
“order-of-magnitude scale.”
),
},
{
“attack”: (
“applying village-scale mechanisms at larger scales is “
“the romanticism this framework warns against; likewise, “
“the framework itself should not prescribe village “
“mechanisms at nation scale”
),
“response”: (
“agreed. The framework prescribes scale-matching, not “
“any particular scale’s mechanisms applied universally. “
“A nation needs nation-scale coordination for nation-”
“scale problems and village-scale function for village-”
“scale problems. The current failure is that we have “
“built nation-scale mechanisms that override village-”
“scale function rather than support it.”
),
},
{
“attack”: (
“the historical precedents are cherry-picked; every “
“civilization has different mechanisms”
),
“response”: (
“the precedents are evidence that the first-principles “
“analysis matches observed human arrangements, not “
“claims that all civilizations are identical. The “
“module is normative-with-descriptive-reference. The “
“normative claim is that certain coordination problems “
“must be solved somehow at certain scales. The “
“descriptive reference shows various cultures solving “
“them. Different mechanisms for the same problem is “
“expected and does not falsify the framework.”
),
},
{
“attack”: (
“this framework would dismantle modern infrastructure, “
“producing mass death”
),
“response”: (
“the framework does not prescribe dismantling anything. “
“It analyzes which functions are thermodynamically “
“necessary and which measurement systems serve their “
“scales. Modern infrastructure that serves real “
“coordination problems scores well. Modern measurement “
“systems that produce capture score poorly. Policy “
“choices follow from the analysis, they are not the “
“analysis.”
),
},
{
“attack”: (
“large-scale problems (climate change, pandemic, “
“nuclear weapons) require large-scale coordination “
“that your framework is hostile to”
),
“response”: (
“the framework explicitly recognizes that cross-boundary “
“commons management is a coordination problem emerging “
“at regional and global scale. Global coordination for “
“genuinely global problems scores as appropriate. The “
“hostility is toward applying large-scale measurement “
“systems at smaller scales where they override local “
“function, not toward large-scale coordination where “
“it is thermodynamically necessary.”
),
},
{
“attack”: (
“this is anarchism or localism in scientific dress”
),
“response”: (
“the framework is neither. Anarchism rejects large-”
“scale coordination; the framework accepts it where “
“necessary. Localism claims local is always best; the “
“framework claims scale-match is best. The framework “
“rules out many anarchist and localist positions (e.g. “
“village-scale cannot solve climate coordination; “
“national-scale infrastructure is necessary for certain “
“functions). The classification as an ideology misses “
“that the framework is a measurement tool.”
),
},
]

# ===========================================================================

# Part 9. Rendering

# ===========================================================================

def render_substrate_functions_table() -> str:
lines: List[str] = []
header = (
f”{‘function’:42s}  “
f”{‘first required at’:18s}  “
f”{‘failure consequence’:30s}”
)
lines.append(header)
lines.append(”-” * len(header))
for f in SUBSTRATE_FUNCTIONS:
lines.append(
f”{f.function[:42]:42s}  “
f”{f.first_required_at.value:18s}  “
f”{f.failure_consequence[:30]:30s}”
)
return “\n”.join(lines)

def render_measurement_appropriateness_table() -> str:
lines: List[str] = []
header = f”{‘measurement’:30s}  “ + “  “.join(
f”{t.value[:6]:>6s}” for t in SCALE_ORDER
)
lines.append(header)
lines.append(”-” * len(header))
for m in MEASUREMENT_SYSTEMS:
row = f”{m.name[:30]:30s}  “
scores = [
measurement_appropriateness(m.name, t) for t in SCALE_ORDER
]
row += “  “.join(f”{s:6.2f}” for s in scores)
lines.append(row)
return “\n”.join(lines)

if **name** == “**main**”:
print(”=” * 80)
print(“SUBSTRATE FUNCTIONS BY SCALE”)
print(”=” * 80)
print()
print(render_substrate_functions_table())
print()

```
print("=" * 80)
print("MEASUREMENT APPROPRIATENESS BY SCALE")
print("=" * 80)
print()
print(render_measurement_appropriateness_table())
print()

print("=" * 80)
print("COORDINATION PROBLEMS EMERGING AT EACH SCALE")
print("=" * 80)
for scale in SCALE_ORDER:
    problems = [
        p for p in COORDINATION_PROBLEMS if p.emerges_at == scale
    ]
    if problems:
        print(f"\n{scale.value} scale:")
        for p in problems:
            print(f"  - {p.problem}")
print()

print("=" * 80)
print("COLLAPSE ANALYSIS: NATION-SCALE COLLAPSE")
print("=" * 80)
collapse = analyze_collapse(ScaleTier.NATION)
print(f"collapsed scale:  {collapse.collapsed_scale.value}")
print(f"fallback scale:   {collapse.fallback_scale.value}")
print(f"\nfunctions still supported at fallback:")
for f in collapse.functions_still_supported:
    print(f"  + {f}")
print(f"\nfunctions that fail:")
for f in collapse.functions_that_fail:
    print(f"  - {f}")
print(f"\nrecovery requirements:")
for r in collapse.recovery_requirements:
    print(f"  * {r}")
print()

print("=" * 80)
print("MINIMUM VIABLE CIVILIZATION FUNCTIONS")
print("=" * 80)
for fname in MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS:
    print(f"  * {fname}")
print()

print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
```
