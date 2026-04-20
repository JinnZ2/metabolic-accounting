“””
term_audit/alternative_viability.py

Horizontal measurement tool for scoring proposed alternatives against
the arrangements they claim to replace.

Core claim: most proposed ‘alternatives’ to captured arrangements
reproduce the same capture structure in a different implementation.
Scoring alternatives only on ‘does it exist’ or ‘does it provide the
function’ hides this recapitulation. A useful alternative viability
score must measure whether the alternative changes the underlying
exposure-capture-substrate structure, or merely relocates it.

Eight scoring axes, kept separate:

capture_structure_change       does the alternative reproduce the
same credentialing, authority, and
exposure inversion pattern?
failure_topology_shift         does the alternative change the
consequence geometry (blast radius,
failure mode, cascade structure)?
substrate_burn_redistribution  does the alternative reduce per-
actor substrate cost or concentrate
it further?
upstream_demand_coupling       does the alternative require the
same upstream demand scale, or does
its viability depend on demand
reduction?
infrastructure_transition_cost how expensive is building the
alternative relative to maintaining
the current arrangement?
transition_reversibility       if the alternative fails, can the
original arrangement be restored?
knowledge_preservation         does the alternative maintain or
discard the knowledge base of
current practitioners?
scale_honesty                  does the alternative work at current
demand scale, or is its viability
contingent on demand reduction that
it does not itself produce?

The combination produces a total viability score and classifies the
alternative as:
STRUCTURAL       changes the underlying problem
IMPLEMENTATION   provides the function differently, same problem
RELOCATION       moves the problem to different actors
CAPTURE          worse than the original; captures alternative
movements to delay real change

This module is consumed by systemic_necessity and by any audit
comparing proposed alternatives to current arrangements.

CC0. Stdlib only.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

# ===========================================================================

# Part 1. Scoring scales

# ===========================================================================

# 

# All axes scored in [0.0, 1.0] where 1.0 is the viability-positive

# direction.

# 

# capture_structure_change

# 0.0  perfect recapitulation: same credentialing gates, same

# authority inversion, same exposure-insulation asymmetry

# 0.5  partial recapitulation: some capture mechanisms replaced

# but structural pattern persists

# 1.0  structural change: different relationship between exposure,

# authority, and compensation

# 

# failure_topology_shift

# 0.0  worse failure topology: larger blast radius, more cascading,

# more correlated failures

# 0.5  equivalent failure topology in different geometric form

# 1.0  smaller blast radius, more contained failures, less

# cascading across systems

# 

# substrate_burn_redistribution

# 0.0  more concentrated substrate burn (fewer actors carrying

# more cost each)

# 0.5  equivalent substrate burn (same total, similar distribution)

# 1.0  distributed substrate burn (more actors each carrying less)

# 

# upstream_demand_coupling

# 0.0  alternative requires same or greater upstream demand scale

# 0.5  alternative works at current demand but does not itself

# drive demand reduction

# 1.0  alternative explicitly depends on and enables demand

# reduction upstream

# 

# infrastructure_transition_cost

# 0.0  transition cost exceeds decades of current-arrangement

# operating cost; effectively captures resources in the

# transition itself

# 0.5  transition cost comparable to current operating cost over

# 1-2 decades

# 1.0  transition cost low; alternative deploys incrementally

# from existing substrate

# 

# transition_reversibility

# 0.0  fully irreversible; original arrangement cannot be restored

# if alternative fails

# 0.5  partially reversible; significant cost to revert

# 1.0  fully reversible; alternative can be withdrawn with low

# cost if needed

# 

# knowledge_preservation

# 0.0  knowledge base of current practitioners is discarded;

# rebuilding requires generations

# 0.5  knowledge partially preserved but not centered in new

# arrangement

# 1.0  knowledge preserved, transmitted, and central to the

# alternative

# 

# scale_honesty

# 0.0  alternative presented as scale-equivalent to current

# arrangement but is not; hidden dependency on demand

# reduction that the alternative does not provide

# 0.5  alternative explicitly acknowledges scale mismatch but

# does not address it structurally

# 1.0  alternative is scale-honest; either works at current

# scale or openly couples to upstream demand reduction

# —————————————————————————

VIABILITY_AXES = [
“capture_structure_change”,
“failure_topology_shift”,
“substrate_burn_redistribution”,
“upstream_demand_coupling”,
“infrastructure_transition_cost”,
“transition_reversibility”,
“knowledge_preservation”,
“scale_honesty”,
]

class AlternativeClassification(Enum):
STRUCTURAL = “structural”            # changes the underlying
# problem
IMPLEMENTATION = “implementation”    # provides function
# differently, same problem
RELOCATION = “relocation”            # moves problem to different
# actors
CAPTURE = “capture”                  # worse than original;
# captures alternative
# movements

@dataclass
class ViabilityScore:
“”“Score on one viability axis.”””
axis: str
score: float
justification: str
source_refs: List[str] = field(default_factory=list)

```
def __post_init__(self):
    if self.axis not in VIABILITY_AXES:
        raise ValueError(f"unknown axis: {self.axis}")
    if not 0.0 <= self.score <= 1.0:
        raise ValueError(f"score out of bounds: {self.score}")
```

# ===========================================================================

# Part 2. Alternative profile

# ===========================================================================

@dataclass
class AlternativeProfile:
“”“Full scoring of a proposed alternative against a current
arrangement.”””
alternative_name: str
current_arrangement: str
function_provided: str
scores: List[ViabilityScore]
notes: str = “”

```
def score_dict(self) -> Dict[str, float]:
    return {s.axis: s.score for s in self.scores}

def mean_score(self) -> float:
    if not self.scores:
        return 0.0
    return sum(s.score for s in self.scores) / len(self.scores)

def weakest_axes(self, threshold: float = 0.4) -> List[str]:
    return [s.axis for s in self.scores if s.score < threshold]

def classify(self) -> AlternativeClassification:
    """
    Classification rules:
      CAPTURE         mean < 0.3 OR any axis at 0.0 with capture
                      structure unchanged
      RELOCATION      mean 0.3-0.5 with capture_structure_change
                      below 0.3
      IMPLEMENTATION  mean 0.4-0.6 with capture_structure_change
                      below 0.5
      STRUCTURAL      mean >= 0.6 AND capture_structure_change
                      >= 0.5
    """
    mean = self.mean_score()
    scores = self.score_dict()
    capture_change = scores.get("capture_structure_change", 0.0)

    if mean < 0.3:
        return AlternativeClassification.CAPTURE
    if mean >= 0.6 and capture_change >= 0.5:
        return AlternativeClassification.STRUCTURAL
    if capture_change < 0.3:
        return AlternativeClassification.RELOCATION
    if capture_change < 0.5:
        return AlternativeClassification.IMPLEMENTATION
    return AlternativeClassification.IMPLEMENTATION
```

# ===========================================================================

# Part 3. Worked examples

# ===========================================================================

# Example 1: rail replacing hazmat long-haul trucking

RAIL_REPLACES_HAZMAT_TRUCKING = AlternativeProfile(
alternative_name=“expanded_rail_replacing_hazmat_trucking”,
current_arrangement=“hazmat_long_haul_trucking”,
function_provided=(
“long-distance transport of hazardous materials (anhydrous “
“ammonia, chlorine, petroleum, LNG, etc.) from production “
“sites to distribution and use points”
),
scores=[
ViabilityScore(
axis=“capture_structure_change”,
score=0.15,
justification=(
“rail reproduces the same credentialing capture: “
“conductor licensing, dispatcher credentials, signal “
“operator certification, safety inspector “
“credentialing. Rail companies are capital-owned “
“corporations with the same executive-vs-operator “
“authority inversion as trucking. Practitioner “
“representation in rail safety decisions is as “
“constrained as in trucking.”
),
source_refs=[
“East Palestine derailment 2023: NTSB findings on “
“carrier-pressure against crew judgment”,
“Lac-Megantic disaster 2013: crew reductions “
“implemented by rail management over operator “
“objections”,
],
),
ViabilityScore(
axis=“failure_topology_shift”,
score=0.2,
justification=(
“rail concentrates cargo mass: a single train can “
“carry 100+ tank cars at 30,000 gallons each. A “
“derailment blast radius exceeds a single-truck “
“incident by 1-2 orders of magnitude. Correlated “
“failures across tank cars in a single event “
“(East Palestine, Graniteville). Trains cannot “
“stop, swerve, or route around obstacles; truck “
“drivers can make defensive maneuvers.”
),
source_refs=[
“East Palestine 2023 (38 cars, 11 hazmat, vinyl “
“chloride release)”,
“Graniteville 2005 (chlorine release, 9 dead)”,
“Lac-Megantic 2013 (47 dead, town center destroyed)”,
],
),
ViabilityScore(
axis=“substrate_burn_redistribution”,
score=0.4,
justification=(
“rail crews run shorter shifts but under more rigid “
“time constraints; fatigue and stress profiles are “
“comparable. Fewer operators per unit cargo, so “
“substrate burn concentrates in remaining operators “
“rather than distributing”
),
),
ViabilityScore(
axis=“upstream_demand_coupling”,
score=0.1,
justification=(
“rail replacement assumes the same upstream demand “
“for hazmat movement. Most hazmat demand is driven “
“by industrial agriculture (anhydrous ammonia), “
“petrochemical processing, and JIT manufacturing. “
“Rail does not reduce these; it just moves the same “
“volume differently”
),
),
ViabilityScore(
axis=“infrastructure_transition_cost”,
score=0.05,
justification=(
“building rail to reach all current trucking delivery “
“points requires trillions of dollars and decades of “
“construction. Rail cannot serve most last-mile “
“destinations without truck transfer anyway. The “
“transition cost itself captures resources that “
“could fund structural alternatives”
),
source_refs=[
“Association of American Railroads infrastructure “
“investment data”,
“Federal Railroad Administration corridor studies”,
],
),
ViabilityScore(
axis=“transition_reversibility”,
score=0.3,
justification=(
“rail infrastructure, once built, imposes land-use “
“commitments that are difficult to reverse. Abandoned “
“rail corridors can be reclaimed but at significant “
“cost. The trucking workforce displaced during “
“transition loses specialized knowledge”
),
),
ViabilityScore(
axis=“knowledge_preservation”,
score=0.25,
justification=(
“truck driver knowledge (route conditions, weather “
“response, equipment feel, load dynamics) does not “
“transfer to rail operation. Transition discards “
“decades of accumulated practitioner knowledge and “
“rebuilds a different knowledge base from scratch”
),
),
ViabilityScore(
axis=“scale_honesty”,
score=0.2,
justification=(
“rail advocates typically present rail as a “
“direct-replacement solution for trucking without “
“acknowledging that full replacement is “
“geometrically impossible (road network is ~100x “
“denser than rail network) and that the scale of “
“hazmat movement is itself inflated by “
“extractive industrial structure that rail does “
“not address”
),
),
],
notes=(
“rail is frequently proposed as an alternative to long-haul “
“trucking, including specifically for hazmat. This analysis “
“shows rail is an IMPLEMENTATION alternative at best and a “
“RELOCATION alternative in practice: same capture structure, “
“different and typically worse failure topology, “
“infrastructure cost that itself captures transition “
“resources, discarded knowledge base. The core problem “
“(scale of hazmat movement driven by extractive industrial “
“structure) is not addressed by mode switching.”
),
)

# Example 2: regional food systems replacing long-haul industrial

# food distribution

REGIONAL_FOOD_REPLACES_LONG_HAUL = AlternativeProfile(
alternative_name=“regional_food_systems”,
current_arrangement=“long_haul_industrial_food_distribution”,
function_provided=(
“food delivery from production to consumption points”
),
scores=[
ViabilityScore(
axis=“capture_structure_change”,
score=0.75,
justification=(
“shorter corridors permit cooperative, owner-operator, “
“and farmer-direct distribution. Capital requirements “
“per operator decrease. Practitioner authority over “
“working conditions increases. Credentialing capture “
“partially broken because the operators and the “
“producers are often the same people or tightly “
“coupled”
),
source_refs=[
“La Via Campesina organizational structure”,
“Farm-to-Consumer Legal Defense Fund”,
“regional food hub case studies”,
],
),
ViabilityScore(
axis=“failure_topology_shift”,
score=0.85,
justification=(
“shorter transport distances reduce per-event “
“consequence exposure. Distributed production means “
“failures are local rather than regional or national. “
“Hazmat demand drops significantly because “
“regenerative agriculture uses far less anhydrous “
“ammonia, chemical fertilizer, and pesticide”
),
),
ViabilityScore(
axis=“substrate_burn_redistribution”,
score=0.8,
justification=(
“more operators running shorter routes means “
“per-operator substrate burn decreases substantially. “
“70-hour weeks become unnecessary. Family and “
“community time recovered. Driver-producer overlap “
“means operators are embedded in regenerative “
“activities during non-driving time”
),
),
ViabilityScore(
axis=“upstream_demand_coupling”,
score=0.9,
justification=(
“regional food systems explicitly depend on and “
“enable upstream demand reduction: less industrial “
“agriculture means less chemical input demand, “
“less hazmat transport, less long-haul refrigeration “
“energy, less packaging, less distribution overhead”
),
),
ViabilityScore(
axis=“infrastructure_transition_cost”,
score=0.7,
justification=(
“transition uses existing road infrastructure and “
“smaller existing trucks. Investment in regional “
“processing (mills, dairies, slaughterhouses, “
“storage) is substantial but orders of magnitude “
“below rail expansion. Can deploy incrementally”
),
),
ViabilityScore(
axis=“transition_reversibility”,
score=0.85,
justification=(
“regional systems can coexist with current “
“distribution during transition. If the alternative “
“proves non-viable in some context, long-haul can “
“continue. No large irreversible infrastructure “
“commitment”
),
),
ViabilityScore(
axis=“knowledge_preservation”,
score=0.8,
justification=(
“current driver knowledge transfers directly to “
“regional routes. Farmer and processor knowledge is “
“preserved and recentered rather than discarded. “
“Generational ecological knowledge becomes central “
“again rather than marginalized”
),
),
ViabilityScore(
axis=“scale_honesty”,
score=0.7,
justification=(
“honest about the requirement that upstream demand “
“for long-haul hazmat and industrial inputs must “
“shrink. Does not pretend to replace current scale “
“1-to-1; couples explicitly to the agricultural and “
“industrial restructuring that makes the scale “
“reduction possible”
),
),
],
notes=(
“regional food systems are a STRUCTURAL alternative: they “
“change the capture structure, improve failure topology, “
“distribute substrate burn, and couple to upstream demand “
“reduction. The main viability constraint is structural “
“suppression (commodity subsidies, retail consolidation, “
“agricultural land concentration) rather than technical or “
“economic infeasibility”
),
)

# Example 3: cooperative trucking with shorter relays

COOPERATIVE_TRUCKING = AlternativeProfile(
alternative_name=“cooperative_trucking_relay_networks”,
current_arrangement=“corporate_long_haul_trucking”,
function_provided=“long-distance freight transport”,
scores=[
ViabilityScore(
axis=“capture_structure_change”,
score=0.75,
justification=(
“driver-owned cooperatives invert the authority “
“structure: drivers own equipment, set schedules, “
“and make dispatch decisions collectively. “
“Logistics-VP role disappears or becomes an “
“elected coordinator accountable to drivers”
),
source_refs=[
“CoopCycle and similar driver-cooperative models”,
“historical trucker cooperative movements pre-”
“deregulation”,
],
),
ViabilityScore(
axis=“failure_topology_shift”,
score=0.55,
justification=(
“shorter relays reduce fatigue-related failure modes “
“substantially. Same per-event consequence when “
“errors occur, but fewer errors due to better “
“operator condition. Does not change hazmat “
“blast-radius geometry”
),
),
ViabilityScore(
axis=“substrate_burn_redistribution”,
score=0.85,
justification=(
“relay networks distribute driving across more “
“operators, each running shorter shifts with longer “
“home periods. 70-hour weeks become 40-50 hours. “
“Substrate burn per operator drops substantially”
),
),
ViabilityScore(
axis=“upstream_demand_coupling”,
score=0.35,
justification=(
“does not directly reduce upstream demand. Same “
“volume of freight, moved differently. Indirect “
“demand effects through reduced industry “
“consolidation pressure”
),
),
ViabilityScore(
axis=“infrastructure_transition_cost”,
score=0.75,
justification=(
“uses existing roads, existing equipment, existing “
“driver workforce. Investment is organizational “
“(cooperative formation, relay coordination systems) “
“rather than physical infrastructure”
),
),
ViabilityScore(
axis=“transition_reversibility”,
score=0.9,
justification=(
“can deploy in parallel with current arrangement; “
“individual drivers can transition; no large “
“irreversible commitments”
),
),
ViabilityScore(
axis=“knowledge_preservation”,
score=0.95,
justification=(
“current driver knowledge is directly applicable and “
“becomes central to the cooperative’s operation. “
“Route knowledge, equipment knowledge, and weather “
“knowledge are preserved and transmitted through “
“peer networks”
),
),
ViabilityScore(
axis=“scale_honesty”,
score=0.7,
justification=(
“scale-honest about handling current freight volume “
“with restructured operator arrangements. Does not “
“pretend to reduce freight demand, which is its “
“main limitation as a structural solution”
),
),
],
notes=(
“cooperative trucking is a STRUCTURAL alternative for the “
“capture-structure and substrate-burn dimensions but only “
“an IMPLEMENTATION alternative for the underlying freight “
“volume. Most useful in combination with regional food “
“systems or demand-reduction strategies, not as a “
“stand-alone solution”
),
)

# Example 4: community health workers replacing ICU nurses (presented

# as worked example of a CAPTURE-class alternative — this is how

# cost-cutting proposals often appear)

COMMUNITY_HEALTH_WORKERS_REPLACING_ICU_NURSES = AlternativeProfile(
alternative_name=(
“community_health_workers_replacing_icu_nurses”
),
current_arrangement=“icu_nursing”,
function_provided=(
“intensive monitoring and intervention for critically ill “
“patients”
),
scores=[
ViabilityScore(
axis=“capture_structure_change”,
score=0.1,
justification=(
“community health worker employment structures “
“typically reproduce hospital administrator authority “
“with lower pay; capture structure unchanged or “
“worsened”
),
),
ViabilityScore(
axis=“failure_topology_shift”,
score=0.05,
justification=(
“reducing training and experience of bedside “
“providers without restructuring ICU demand worsens “
“failure topology: more errors, more patient deaths, “
“more cascade failures from delayed deterioration “
“detection”
),
),
ViabilityScore(
axis=“substrate_burn_redistribution”,
score=0.2,
justification=(
“shifts substrate burn from credentialed nurses to “
“community health workers with less preparation, “
“rather than distributing burden across a larger “
“prepared workforce”
),
),
ViabilityScore(
axis=“upstream_demand_coupling”,
score=0.1,
justification=(
“does not address why so many patients need ICU “
“care; simply provides the function with less “
“qualified labor”
),
),
ViabilityScore(
axis=“infrastructure_transition_cost”,
score=0.6,
justification=(
“low financial transition cost because labor cost “
“drops; high mortality cost during transition”
),
),
ViabilityScore(
axis=“transition_reversibility”,
score=0.4,
justification=(
“nurse training pipelines degrade during transition; “
“rebuilding takes a decade; mortality during “
“transition is irreversible”
),
),
ViabilityScore(
axis=“knowledge_preservation”,
score=0.15,
justification=(
“discards ICU nursing knowledge base; does not “
“transfer to community health worker role because “
“preparation is insufficient for ICU context”
),
),
ViabilityScore(
axis=“scale_honesty”,
score=0.1,
justification=(
“typically presented as cost-saving alternative “
“without acknowledging mortality consequences; not “
“scale-honest because it does not address demand “
“drivers”
),
),
],
notes=(
“this is a CAPTURE-class alternative: presented as an “
“alternative but reproduces the capture structure with “
“worse outcomes for patients and workers. Listed here as “
“a negative example. Structural alternatives to ICU nursing “
“exist (preventive care reducing ICU demand, higher staffing “
“ratios, patient-council oversight of working conditions) “
“but direct labor-replacement is not one of them”
),
)

# ===========================================================================

# Part 4. Cross-alternative analysis

# ===========================================================================

REFERENCE_ALTERNATIVES = [
RAIL_REPLACES_HAZMAT_TRUCKING,
REGIONAL_FOOD_REPLACES_LONG_HAUL,
COOPERATIVE_TRUCKING,
COMMUNITY_HEALTH_WORKERS_REPLACING_ICU_NURSES,
]

def rank_alternatives(
alternatives: List[AlternativeProfile],
) -> List[tuple]:
“”“Rank alternatives by mean viability score descending.”””
ranked = [(a, a.mean_score(), a.classify()) for a in alternatives]
ranked.sort(key=lambda x: x[1], reverse=True)
return ranked

# ===========================================================================

# Part 5. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
“id”: 1,
“claim”: (
“most alternatives proposed by institutional actors “
“(think-tanks, consulting firms, policy advisors) score “
“as IMPLEMENTATION or RELOCATION, not STRUCTURAL”
),
“falsification”: (
“sample institutional alternatives; measure “
“classification distribution; show STRUCTURAL dominates”
),
},
{
“id”: 2,
“claim”: (
“alternatives scoring high on capture_structure_change “
“systematically face greater structural suppression than “
“alternatives scoring low”
),
“falsification”: (
“measure capture_structure_change score against adoption “
“and funding trajectories; show positive correlation “
“with adoption”
),
},
{
“id”: 3,
“claim”: (
“upstream_demand_coupling score correlates positively “
“with long-term viability of the alternative”
),
“falsification”: (
“track alternatives over 10+ year periods; show “
“demand-coupled alternatives fail more often than “
“non-coupled”
),
},
{
“id”: 4,
“claim”: (
“large-infrastructure alternatives (rail replacing “
“trucking, nuclear replacing fossil, top-down “
“technocratic solutions) score lower on STRUCTURAL “
“axes than smaller distributed alternatives”
),
“falsification”: (
“compare viability scores across a sample of large-”
“infrastructure and distributed alternatives; show “
“large-infrastructure scores higher on average”
),
},
{
“id”: 5,
“claim”: (
“CAPTURE-class alternatives receive more institutional “
“funding and promotion than STRUCTURAL alternatives for “
“the same function”
),
“falsification”: (
“compare funding trajectories of matched CAPTURE and “
“STRUCTURAL alternatives; show STRUCTURAL receives “
“comparable or greater funding”
),
},
{
“id”: 6,
“claim”: (
“knowledge_preservation score correlates with long-term “
“alternative viability because practitioner knowledge is “
“substrate for continued adaptation”
),
“falsification”: (
“track alternatives with varying knowledge preservation; “
“show no relationship with long-term outcomes”
),
},
]

# ===========================================================================

# Part 6. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
“attack”: (
“this framework is anti-technology: it penalizes “
“infrastructure investment”
),
“response”: (
“the framework distinguishes infrastructure that enables “
“distributed alternatives (regional processing, local “
“renewable generation, cooperative platforms) from “
“infrastructure that replicates centralized capture “
“patterns (national rail corridors, industrial-scale “
“replacement systems). Technology is not penalized; “
“capture structure is measured.”
),
},
{
“attack”: (
“scale_honesty is subjective; who decides what counts as “
“scale-honest”
),
“response”: (
“scale honesty is measured against the alternative’s own “
“documented claims. If proponents present an alternative “
“as scale-equivalent to the current arrangement, the “
“claim is testable against current demand versus “
“alternative capacity. If the alternative requires demand “
“reduction to be viable, honest presentation acknowledges “
“this. The test is whether the alternative’s own “
“description matches its technical requirements.”
),
},
{
“attack”: (
“this framework would rule out most large projects as “
“non-viable, leaving us unable to address systemic “
“problems”
),
“response”: (
“the framework does not rule out projects; it classifies “
“them. A project classified as IMPLEMENTATION is not “
“thereby forbidden; it is identified as not changing “
“the underlying problem. Addressing systemic problems “
“requires STRUCTURAL alternatives, which by definition “
“are available and documented. The argument that large “
“projects are necessary to address systemic problems is “
“often the argument through which STRUCTURAL “
“alternatives are displaced.”
),
},
{
“attack”: (
“the regional food systems example romanticizes “
“small-scale production”
),
“response”: (
“the example documents scored axes, not romance. “
“Substrate burn reduction, failure topology improvement, “
“and upstream demand coupling are measured. Regional “
“food systems score well on these because the structural “
“properties are real. Small-scale production has failure “
“modes too (weather vulnerability, limited variety in “
“harsh climates); those failure modes are different from “
“industrial agriculture’s failure modes and the scoring “
“accounts for that.”
),
},
{
“attack”: (
“CAPTURE-class alternatives still provide the function “
“at lower cost, so they are not worse”
),
“response”: (
“cost comparison under a captured measurement system “
“(money not accounting for substrate depletion, mortality, “
“knowledge loss) is not a valid comparison. The “
“community health worker example shows how cost-saving “
“alternatives can be far worse when full consequence is “
“measured. The argument assumes the current cost “
“accounting is trustworthy, which earlier audits “
“establish it is not.”
),
},
{
“attack”: (
“this reduces to ‘small is beautiful’ ideology”
),
“response”: (
“the framework does not privilege small. Nuclear plant “
“operation scores as irreducible because no distributed “
“alternative currently exists. Structural engineering “
“for large infrastructure scores as necessary. Some “
“functions require concentration. The framework “
“distinguishes concentration that serves function from “
“concentration that serves capture. This is empirical “
“per function, not ideological.”
),
},
{
“attack”: (
“transition_reversibility is a trivial requirement; “
“almost nothing is fully reversible”
),
“response”: (
“transition_reversibility is scored as a gradient, not “
“a binary. Rail corridor commitments are less reversible “
“than cooperative formation. The axis measures the cost “
“and feasibility of reversal, not perfect reversibility. “
“It matters because alternatives that fail produce “
“different costs depending on reversibility.”
),
},
]

# ===========================================================================

# Part 7. Rendering

# ===========================================================================

def render_alternatives_table(
alternatives: List[AlternativeProfile],
) -> str:
lines: List[str] = []
header = (
f”{‘alternative’:46s}  “
f”{‘mean’:>5s}  “
f”{‘class’:16s}”
)
lines.append(header)
lines.append(”-” * len(header))

```
ranked = rank_alternatives(alternatives)
for alt, mean, cls in ranked:
    lines.append(
        f"{alt.alternative_name[:46]:46s}  "
        f"{mean:5.2f}  "
        f"{cls.value:16s}"
    )
return "\n".join(lines)
```

def render_alternative_detail(alt: AlternativeProfile) -> str:
lines: List[str] = []
lines.append(f”alternative: {alt.alternative_name}”)
lines.append(f”replaces:    {alt.current_arrangement}”)
lines.append(f”function:    {alt.function_provided}”)
lines.append(f”mean score:  {alt.mean_score():.2f}”)
lines.append(f”class:       {alt.classify().value}”)
lines.append(””)
lines.append(“axis scores:”)
for s in alt.scores:
lines.append(f”  {s.axis:35s}  {s.score:.2f}”)
weak = alt.weakest_axes(threshold=0.4)
if weak:
lines.append(f”weakest axes: {’, ’.join(weak)}”)
return “\n”.join(lines)

if **name** == “**main**”:
print(”=” * 80)
print(“ALTERNATIVE VIABILITY SCORING”)
print(”=” * 80)
print()
print(render_alternatives_table(REFERENCE_ALTERNATIVES))
print()

```
for alt in REFERENCE_ALTERNATIVES:
    print("=" * 80)
    print(render_alternative_detail(alt))
    print()

print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
```
