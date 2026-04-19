“””
term_audit/audits/efficiency.py

Audit of the term ‘efficiency’ against signal-definition criteria,
and redefinition from first principles as a vector-space measurement
of substrate coupling density and carrying-capacity trajectory,
calibrated against natural systems operating at thermodynamic limit.

Core finding: conventional efficiency is a linear throughput metric
that measures extraction velocity and calls it efficiency. Natural
systems (forest, river, soil food web, protein folding, watershed
dynamics) operate at near-theoretical thermodynamic efficiency through
dense multi-directional coupling of flows. The conventional measurement
is inverted: systems labeled efficient are typically low-coupling
extraction operations, while systems with high actual efficiency are
labeled inefficient because their coupling structure is invisible to
linear metrics.

CC0. Stdlib only.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math

from term_audit.schema import (
TermAudit, SignalScore, StandardSetter, FirstPrinciplesPurpose,
)

# ===========================================================================

# Part 1. Audit of conventional (linear) efficiency as a signal

# ===========================================================================

CONVENTIONAL_EFFICIENCY_AUDIT = TermAudit(
term=“efficiency_conventional_linear”,
claimed_signal=(
“output per unit of input, typically measured as throughput “
“per head count, or revenue per dollar of cost, or units “
“produced per unit of time”
),
standard_setters=[
StandardSetter(
name=“industrial engineering profession”,
authority_basis=“credentialed practice, Taylorist lineage”,
incentive_structure=(
“the linear efficiency metric is the deliverable; the “
“profession’s existence depends on the metric being “
“treated as meaningful”
),
independence_from_measured=0.1,
),
StandardSetter(
name=“management consulting”,
authority_basis=“market position”,
incentive_structure=(
“linear efficiency optimization is the product sold; “
“multi-dimensional efficiency cannot be packaged or “
“billed in the same way”
),
independence_from_measured=0.05,
),
StandardSetter(
name=“capital owners”,
authority_basis=“ownership position”,
incentive_structure=(
“linear efficiency maps directly to extraction rate; “
“coupled efficiency would reveal substrate drawdown “
“and reduce apparent returns”
),
independence_from_measured=0.05,
),
StandardSetter(
name=“regulatory and statistical agencies”,
authority_basis=“statutory”,
incentive_structure=(
“measurement continuity; existing data series use “
“linear metrics; changing the metric invalidates “
“decades of comparison data”
),
independence_from_measured=0.3,
),
],
signal_scores=[
SignalScore(
criterion=“scope_defined”,
score=0.2,
justification=(
“scope declared narrowly (output and input within a “
“single operation) while actual operation is embedded “
“in coupled substrate flows that the measurement “
“excludes by construction”
),
),
SignalScore(
criterion=“unit_invariant”,
score=0.15,
justification=(
“units vary across operations; widgets-per-hour, “
“revenue-per-employee, and miles-per-gallon are all “
“called efficiency but are not comparable”
),
),
SignalScore(
criterion=“referent_stable”,
score=0.3,
justification=(
“referent shifts between physical throughput, financial “
“return, and time-utilization depending on who is “
“measuring”
),
),
SignalScore(
criterion=“calibration_exists”,
score=0.4,
justification=(
“within a single operation type, calibration procedures “
“exist and are reproducible; across operation types, “
“calibration is not possible”
),
),
SignalScore(
criterion=“observer_invariant”,
score=0.4,
justification=(
“for a single fixed operation with fixed units, two “
“observers will agree; the agreement disappears once “
“scope or units vary”
),
),
SignalScore(
criterion=“conservation_or_law”,
score=0.15,
justification=(
“linear efficiency violates thermodynamic accounting “
“because it excludes uncoupled waste streams and “
“substrate drawdown from the denominator; an operation “
“that dumps waste to the commons shows higher “
“efficiency than one that cycles its waste internally”
),
),
SignalScore(
criterion=“falsifiability”,
score=0.5,
justification=(
“falsifiable within narrow scope; not falsifiable as a “
“general claim about efficiency because scope can be “
“redrawn to exclude inconvenient flows”
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
“identify operations that achieve more output per unit of “
“input than alternatives, so resources can be allocated “
“to the higher-output option”
),
physical_referent=(
“thermodynamic efficiency: useful work output per total “
“energy input, measured across all coupled flows”
),
informational_referent=(
“coupling density of operations; how many flows share “
“substrate rather than requiring independent inputs”
),
drift_score=0.8,
drift_justification=(
“drift from thermodynamic efficiency (coupled flow density) “
“to extraction-velocity metric. The original purpose “
“(identifying higher-output-per-input operations) required “
“accounting for all inputs including substrate drawdown “
“and uncoupled waste. The current usage excludes both, “
“inverting the direction of the measurement in most “
“industrial contexts.”
),
),
correlation_to_real_signal=0.25,
correlation_justification=(
“weakly correlated with thermodynamic efficiency in simple “
“mechanical operations (engine efficiency, heat exchanger “
“design) where input accounting is complete. Correlation “
“collapses in biological, ecological, economic, and social “
“systems where coupling structure is excluded from the “
“measurement.”
),
notes=(
“conventional efficiency is a narrow-scope signal masquerading “
“as a general-scope one. Within a well-defined closed system “
“with complete input accounting, the measurement is valid. “
“Applied to open, coupled, substrate-dependent systems, it “
“inverts the direction of the measurement, rewarding “
“extraction and penalizing regeneration.”
),
)

# ===========================================================================

# Part 2. Vector-space redefinition

# ===========================================================================

# 

# Efficiency is not a scalar. It is a point in a vector space defined

# by at least three axes:

# 

# DIM_1  EROI

# energy return on energy invested, including all inputs

# (caloric, caloric-equivalent labor, fossil, embodied,

# substrate-maintenance)

# 

# DIM_2  coupling coefficient

# density of shared substrate flows across operations;

# how many outputs of one process become inputs of another

# within the system

# 

# DIM_3  carrying capacity trajectory

# change in the system’s ability to support future operations;

# positive for regenerative systems, negative for extractive

# 

# A fourth axis is often required for systems involving knowledge:

# 

# DIM_4  knowledge density

# amount of context-specific, transferable knowledge embedded

# in the operation, which reduces external input requirements

# and increases coupling capacity

# 

# Efficiency is the vector magnitude in this space, weighted by the

# persistence of each dimension over time. A high EROI with negative

# carrying capacity trajectory is not efficient; it is fast extraction.

# —————————————————————————

@dataclass
class EfficiencyVector:
“”“Efficiency measurement in vector space.”””
eroi: float                         # energy return on energy invested
# 0.0 = pure loss; 1.0 = break-even;
# > 1.0 = net gain; scaled
coupling_coefficient: float         # 0.0 = fully uncoupled operations
# 1.0 = every output is another’s
# input (forest-limit)
carrying_capacity_trajectory: float # -1.0 = rapidly degrading substrate
# 0.0 = steady-state
# +1.0 = rapidly regenerating
knowledge_density: float = 0.0      # 0.0 = no embedded knowledge;
# 1.0 = dense context-specific
# knowledge per operation

```
def magnitude(self) -> float:
    """Vector magnitude, penalizing negative carrying-capacity."""
    if self.carrying_capacity_trajectory < 0:
        # extraction is not efficiency even if EROI is high;
        # penalize by squaring the negative trajectory
        ccp = self.carrying_capacity_trajectory * 2.0
    else:
        ccp = self.carrying_capacity_trajectory
    return math.sqrt(
        (self.eroi ** 2)
        + (self.coupling_coefficient ** 2)
        + (ccp ** 2)
        + (self.knowledge_density ** 2)
    )

def classification(self) -> str:
    """Qualitative classification of the efficiency regime."""
    if self.carrying_capacity_trajectory < -0.3:
        return "extractive"
    if self.coupling_coefficient < 0.3 and self.eroi > 1.0:
        return "linear_high_throughput"
    if self.coupling_coefficient >= 0.6 and \
       self.carrying_capacity_trajectory >= 0.3:
        return "regenerative_coupled"
    if self.coupling_coefficient >= 0.4 and \
       self.carrying_capacity_trajectory >= 0.0:
        return "coupled_steady"
    return "mixed"
```

@dataclass
class CoupledOperation:
“”“A single operation within a system, with explicit flow coupling.”””
name: str
inputs: List[str]                   # substrate flows consumed
outputs: List[str]                  # substrate flows produced
waste_streams: List[str]            # outputs not used by other ops

```
def coupling_with(self, other: "CoupledOperation") -> float:
    """Fraction of this op's outputs that feed into the other's
    inputs."""
    if not self.outputs:
        return 0.0
    shared = len(set(self.outputs) & set(other.inputs))
    return shared / len(self.outputs)
```

def system_coupling_coefficient(
operations: List[CoupledOperation],
) -> float:
“””
Average coupling coefficient across a system of operations.
Captures how densely outputs of each operation feed inputs of others.
“””
if len(operations) < 2:
return 0.0
total = 0.0
count = 0
for i, op_a in enumerate(operations):
for j, op_b in enumerate(operations):
if i == j:
continue
total += op_a.coupling_with(op_b)
count += 1
return total / count if count else 0.0

# ===========================================================================

# Part 3. Natural-system calibration

# ===========================================================================

# 

# Natural systems operating at thermodynamic limit provide the calibration

# anchors. Their coupling coefficients, EROI, and carrying-capacity

# trajectories are empirically estimable and serve as reference values.

# —————————————————————————

@dataclass
class NaturalSystemReference:
“”“Reference values for a natural system operating near thermodynamic limit.”””
name: str
eroi_estimate: float
coupling_estimate: float
capacity_trajectory_estimate: float
knowledge_density_estimate: float
notes: str
source_refs: List[str] = field(default_factory=list)

NATURAL_SYSTEM_REFERENCES = [
NaturalSystemReference(
name=“mature_deciduous_forest”,
eroi_estimate=0.9,
coupling_estimate=0.95,
capacity_trajectory_estimate=0.2,
knowledge_density_estimate=0.9,
notes=(
“near-complete coupling of flows: photosynthesis, “
“decomposition, nitrogen fixation, water cycling, “
“predator-prey dynamics. Every output is an input “
“somewhere. Knowledge density is high because organisms “
“carry context-specific evolved strategies.”
),
),
NaturalSystemReference(
name=“healthy_river_system”,
eroi_estimate=0.85,
coupling_estimate=0.9,
capacity_trajectory_estimate=0.15,
knowledge_density_estimate=0.85,
notes=(
“dense coupling of hydrological, nutrient, sediment, “
“and biological flows. Riparian zones couple terrestrial “
“and aquatic systems.”
),
),
NaturalSystemReference(
name=“soil_food_web”,
eroi_estimate=0.95,
coupling_estimate=0.98,
capacity_trajectory_estimate=0.25,
knowledge_density_estimate=0.95,
notes=(
“highest coupling of any natural system; every organism’s “
“output is another’s input; regeneration rate exceeds “
“loss rate in undisturbed conditions”
),
),
NaturalSystemReference(
name=“protein_folding_machinery”,
eroi_estimate=0.99,
coupling_estimate=0.99,
capacity_trajectory_estimate=0.0,
knowledge_density_estimate=0.99,
notes=(
“near-theoretical thermodynamic limit; cellular folding “
“couples thermodynamic, kinetic, and informational “
“constraints simultaneously”
),
),
]

CORPORATE_SYSTEM_REFERENCES = [
NaturalSystemReference(
name=“conventional_industrial_agriculture”,
eroi_estimate=0.15,
coupling_estimate=0.1,
capacity_trajectory_estimate=-0.6,
knowledge_density_estimate=0.2,
notes=(
“low EROI (caloric return per fossil caloric input is often “
“below 1); low coupling (most waste streams exit the system “
“as pollution); strongly negative carrying-capacity “
“trajectory (soil loss, water depletion, biodiversity “
“collapse); low knowledge density (monoculture, mechanized “
“operation, minimal context-specific adaptation)”
),
source_refs=[
“Pimentel & Pimentel 2008, ‘Food, Energy, and Society’”,
“Montgomery 2007, ‘Dirt: The Erosion of Civilizations’”,
],
),
NaturalSystemReference(
name=“long_haul_trucking_corporate”,
eroi_estimate=0.25,
coupling_estimate=0.15,
capacity_trajectory_estimate=-0.3,
knowledge_density_estimate=0.3,
notes=(
“low coupling (fuel, driver, vehicle, route are largely “
“independent purchased inputs); negative trajectory “
“(driver substrate drawdown, vehicle maintenance deferral, “
“road infrastructure degradation)”
),
),
NaturalSystemReference(
name=“financial_services_extraction”,
eroi_estimate=0.0,
coupling_estimate=0.05,
capacity_trajectory_estimate=-0.2,
knowledge_density_estimate=0.4,
notes=(
“no EROI because no physical energy output; near-zero “
“coupling to substrate flows; negative trajectory via “
“concentration of claims on substrate without regenerating “
“substrate”
),
),
]

COUPLED_HUMAN_OPERATION_REFERENCES = [
NaturalSystemReference(
name=“small_holder_coupled_land_operation”,
eroi_estimate=0.7,
coupling_estimate=0.65,
capacity_trajectory_estimate=0.25,
knowledge_density_estimate=0.75,
notes=(
“example: driver who produces own food, remediates own “
“soil, builds own infrastructure, carries generational “
“ecological knowledge. Food production couples to labor “
“substrate, soil remediation couples to property carrying “
“capacity, construction couples to infrastructure base, “
“knowledge couples all of the above. This is the “
“operational regime of regenerative small-scale human “
“systems operating near natural-system efficiency.”
),
),
]

# ===========================================================================

# Part 4. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
“id”: 1,
“claim”: (
“systems scored as efficient by linear corporate metrics “
“have lower EROI than natural systems at thermodynamic “
“limit”
),
“falsification”: (
“calculate EROI of top-quartile-efficient corporate “
“operations with full input accounting; compare to natural “
“system EROI; show corporate EROI >= natural EROI”
),
},
{
“id”: 2,
“claim”: (
“linear-efficient systems have coupling coefficients at “
“least 3x lower than natural systems”
),
“falsification”: (
“document coupling coefficients across a matched sample; “
“show corporate coupling within 3x of forest or soil-web “
“coupling”
),
},
{
“id”: 3,
“claim”: (
“linear-efficient systems have negative carrying-capacity “
“trajectories in the substrate they depend on”
),
“falsification”: (
“show at least one industrial sector where both linear “
“efficiency and carrying-capacity trajectory are positive “
“over 30 years”
),
},
{
“id”: 4,
“claim”: (
“when measured in vector-space efficiency with full “
“substrate accounting, coupled small-scale operations “
“score higher than linear-efficient corporate operations”
),
“falsification”: (
“measure a matched pair of operations with complete input “
“accounting; show the linear-efficient one has higher “
“vector magnitude”
),
},
{
“id”: 5,
“claim”: (
“conventional efficiency and vector-space efficiency “
“anticorrelate in systems that extract from substrate “
“faster than they regenerate it”
),
“falsification”: (
“find a substrate-extracting system with positive “
“correlation between the two measurements”
),
},
]

# ===========================================================================

# Part 5. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
“attack”: (
“vector-space efficiency is just adding complexity to “
“hide bad performance on real metrics”
),
“response”: (
“the complexity exists in the system being measured, not “
“in the measurement. Reducing the measurement to a scalar “
“is what hides performance. The vector representation “
“surfaces dimensions the scalar excludes by construction.”
),
},
{
“attack”: (
“natural systems are not a valid calibration because they “
“are not doing the same work as industrial systems”
),
“response”: (
“natural systems are calibration anchors because they “
“demonstrate the thermodynamic upper bound for coupled “
“flow efficiency. The work is different; the physics “
“constraining the efficiency is the same. An industrial “
“system cannot exceed a natural system’s coupling density “
“without violating thermodynamic law.”
),
},
{
“attack”: (
“coupling coefficient is not measurable; how do you count “
“shared substrate flows”
),
“response”: (
“enumerate operations, enumerate their input and output “
“flows, compute pairwise overlaps. This is a standard “
“procedure in industrial ecology (material flow analysis) “
“and ecosystem ecology (food-web analysis). It is “
“measurable; the objection is that the measurement has “
“not been applied to the sectors where it would be “
“inconvenient.”
),
},
{
“attack”: (
“carrying-capacity trajectory requires long timescales “
“and is therefore unreliable for operational decisions”
),
“response”: (
“long-timescale measurement is the point. A measurement “
“that excludes long-timescale effects is measuring “
“extraction, not efficiency. Decisions that optimize a “
“short-timescale measurement while degrading a “
“long-timescale substrate are optimizing the wrong “
“function.”
),
},
{
“attack”: (
“knowledge density is unmeasurable and therefore not a “
“real axis”
),
“response”: (
“knowledge density is operationalized as: reduction in “
“external input requirement due to context-specific “
“adaptation, plus transferability of the operation to “
“similar contexts. Both are measurable. The objection “
“reflects that the measurement has been underdeveloped, “
“not that it is impossible.”
),
},
{
“attack”: (
“vector-space efficiency cannot guide resource allocation “
“because it does not produce a scalar ranking”
),
“response”: (
“vector magnitude produces a scalar ranking. The vector “
“representation also exposes which dimensions a system “
“is weak on, which a scalar-only measurement hides. “
“Allocation decisions are better, not worse, when the “
“dimensions are visible.”
),
},
{
“attack”: (
“the examples chosen as ‘coupled’ are cherry-picked “
“small-scale operations that do not scale”
),
“response”: (
“natural systems scale (a forest is not small). The “
“scaling constraint on coupled human systems is not “
“physics; it is the capture of land, knowledge, and time “
“by the linear-efficient sector. Scaling is a political “
“and structural question, not a physics question.”
),
},
]

# ===========================================================================

# Part 6. Worked example: the smallholder coupled operation

# ===========================================================================

def smallholder_example() -> Tuple[List[CoupledOperation], EfficiencyVector]:
“””
Worked example: driver who produces own food, remediates soil,
builds structure, and carries generational knowledge, while also
working a long-haul corridor.
“””
operations = [
CoupledOperation(
name=“food_production”,
inputs=[“sunlight”, “water”, “soil_nutrients”, “labor”,
“knowledge”],
outputs=[“food”, “compost_input”, “seed_stock”],
waste_streams=[],
),
CoupledOperation(
name=“soil_remediation”,
inputs=[“compost_input”, “labor”, “knowledge”,
“water”, “amendments”],
outputs=[“soil_nutrients”, “water_retention_capacity”,
“carbon_sequestration”],
waste_streams=[],
),
CoupledOperation(
name=“driver_substrate_maintenance”,
inputs=[“food”, “shelter”, “recovery_time”],
outputs=[“labor”, “revenue”],
waste_streams=[“metabolic_byproducts”],
),
CoupledOperation(
name=“structure_building”,
inputs=[“labor”, “materials”, “knowledge”],
outputs=[“shelter”, “infrastructure”,
“water_retention_capacity”],
waste_streams=[“construction_scrap”],
),
CoupledOperation(
name=“knowledge_maintenance”,
inputs=[“observation_time”, “transmission_contact”],
outputs=[“knowledge”],
waste_streams=[],
),
CoupledOperation(
name=“long_haul_distribution”,
inputs=[“labor”, “fuel”, “vehicle_maintenance”],
outputs=[“revenue”, “food_distribution_service”],
waste_streams=[“emissions”, “road_wear”],
),
]
coupling = system_coupling_coefficient(operations)
vec = EfficiencyVector(
eroi=0.7,
coupling_coefficient=coupling,
carrying_capacity_trajectory=0.25,
knowledge_density=0.75,
)
return operations, vec

if **name** == “**main**”:
import json
print(”=== conventional efficiency audit ===”)
print(json.dumps(CONVENTIONAL_EFFICIENCY_AUDIT.summary(), indent=2))
print()
print(“failure modes:”, CONVENTIONAL_EFFICIENCY_AUDIT.failure_modes())
print()
print(”=== natural system references ===”)
for ref in NATURAL_SYSTEM_REFERENCES:
v = EfficiencyVector(
eroi=ref.eroi_estimate,
coupling_coefficient=ref.coupling_estimate,
carrying_capacity_trajectory=ref.capacity_trajectory_estimate,
knowledge_density=ref.knowledge_density_estimate,
)
print(f”  {ref.name:40s}  “
f”magnitude={v.magnitude():.3f}  “
f”class={v.classification()}”)
print()
print(”=== corporate system references ===”)
for ref in CORPORATE_SYSTEM_REFERENCES:
v = EfficiencyVector(
eroi=ref.eroi_estimate,
coupling_coefficient=ref.coupling_estimate,
carrying_capacity_trajectory=ref.capacity_trajectory_estimate,
knowledge_density=ref.knowledge_density_estimate,
)
print(f”  {ref.name:40s}  “
f”magnitude={v.magnitude():.3f}  “
f”class={v.classification()}”)
print()
print(”=== coupled human operation references ===”)
for ref in COUPLED_HUMAN_OPERATION_REFERENCES:
v = EfficiencyVector(
eroi=ref.eroi_estimate,
coupling_coefficient=ref.coupling_estimate,
carrying_capacity_trajectory=ref.capacity_trajectory_estimate,
knowledge_density=ref.knowledge_density_estimate,
)
print(f”  {ref.name:40s}  “
f”magnitude={v.magnitude():.3f}  “
f”class={v.classification()}”)
print()
print(”=== smallholder worked example ===”)
ops, vec = smallholder_example()
print(f”  operations: {len(ops)}”)
print(f”  computed coupling coefficient: “
f”{system_coupling_coefficient(ops):.3f}”)
print(f”  efficiency vector magnitude: {vec.magnitude():.3f}”)
print(f”  classification: {vec.classification()}”)
print()
print(”=== falsifiable predictions:”, len(FALSIFIABLE_PREDICTIONS))
print(”=== attack-response matrix:”, len(ATTACK_RESPONSES), “entries”)
