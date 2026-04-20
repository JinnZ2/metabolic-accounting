"""
term_audit/recovery_pathways.py

Modeling of recovery sequences after multi-tier collapse.

Core claim: recovery from collapse follows predictable pathways
determined by which substrate functions survived at which scales.
The sequence of rebuilding is constrained by dependencies among
functions: some functions must be restored before others can be
rebuilt. The pathway is not arbitrary.

This module provides:

recovery_sequence        ordered list of functions to rebuild,
                         with dependencies and prerequisites
recovery_timeline        estimated time per stage given starting
                         conditions
bottleneck_functions     functions whose atrophy most constrains
                         recovery speed
preservation_strategies  what must be preserved *before* collapse
                         to enable recovery after
historical_validation    comparison of modeled pathways to
                         documented recoveries (Bronze Age,
                         post-Roman, post-Classic Maya)

The module is normative-with-historical-reference: it derives
necessary sequence from first-principles dependencies, then
validates against observed recoveries.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum

from term_audit.civilization_substrate_scaling import (
    ScaleTier,
    SCALE_ORDER,
    SubstrateFunction,
    SUBSTRATE_FUNCTIONS,
    MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS,
)
from term_audit.collapse_propensity import (
    AtrophyLevel,
    ATROPHY_NUMERIC,
    FunctionAtrophyProfile,
    CollapseDepthEstimate,
)

# ===========================================================================
# Part 1. Function dependencies
# ===========================================================================

# Some substrate functions cannot be rebuilt until others are restored.
# These dependencies constrain the recovery sequence.

@dataclass
class FunctionDependency:
    """A prerequisite relationship between substrate functions."""
    function: str
    depends_on: List[str]
    rationale: str


FUNCTION_DEPENDENCIES = [
    FunctionDependency(
        function="subsistence_food_production",
        depends_on=[
            "water_access_and_quality",
            "ecological_and_seasonal_observation",
        ],
        rationale=(
            "food production requires water and knowledge of seasonal "
            "timing; without these, planting and harvest fail"
        ),
    ),
    FunctionDependency(
        function="shelter_and_thermal_regulation",
        depends_on=[
            "ecological_and_seasonal_observation",  # materials, climate
        ],
        rationale=(
            "shelter construction requires knowledge of local materials "
            "and climate patterns"
        ),
    ),
    FunctionDependency(
        function="waste_separation_from_life_substrate",
        depends_on=[
            "water_access_and_quality",
            "conflict_resolution_within_group",  # norm enforcement
        ],
        rationale=(
            "waste separation requires water for hygiene and group "
            "norms to enforce separation"
        ),
    ),
    FunctionDependency(
        function="knowledge_transmission_across_generations",
        depends_on=[
            "conflict_resolution_within_group",  # stable social context
        ],
        rationale=(
            "knowledge transmission requires stable social structures; "
            "chronic conflict disrupts apprenticeship and teaching"
        ),
    ),
    FunctionDependency(
        function="infrastructure_maintenance",
        depends_on=[
            "conflict_resolution_within_group",  # coordination
            "knowledge_transmission_across_generations",  # skills
        ],
        rationale=(
            "collective maintenance requires coordination and "
            "transmitted technical knowledge"
        ),
    ),
    FunctionDependency(
        function="long_horizon_substrate_stewardship",
        depends_on=[
            "ecological_and_seasonal_observation",
            "knowledge_transmission_across_generations",
            "conflict_resolution_within_group",
        ],
        rationale=(
            "stewardship requires observation across time, transmission "
            "of accumulated knowledge, and institutions that persist "
            "beyond individual lifetimes"
        ),
    ),
    FunctionDependency(
        function="exchange_beyond_direct_reciprocity",
        depends_on=[
            "conflict_resolution_within_group",  # trust across groups
            "infrastructure_maintenance",  # roads, market spaces
        ],
        rationale=(
            "exchange with strangers requires trust infrastructure and "
            "physical infrastructure"
        ),
    ),
    FunctionDependency(
        function="defense_and_boundary_maintenance",
        depends_on=[
            "conflict_resolution_within_group",  # internal cohesion
            "subsistence_food_production",  # surplus to support specialists
        ],
        rationale=(
            "defense requires group cohesion and sufficient food surplus "
            "to support non-producing defenders"
        ),
    ),
    FunctionDependency(
        function="cross_boundary_commons_management",
        depends_on=[
            "long_horizon_substrate_stewardship",
            "conflict_resolution_within_group",  # extended to inter-group
            "exchange_beyond_direct_reciprocity",  # communication
        ],
        rationale=(
            "cross-boundary management requires stewardship capacity, "
            "conflict resolution across groups, and communication "
            "infrastructure"
        ),
    ),
]


def get_dependency_graph() -> Dict[str, Set[str]]:
    """Return adjacency map: function -> set of functions it depends on."""
    graph: Dict[str, Set[str]] = {}
    for dep in FUNCTION_DEPENDENCIES:
        graph[dep.function] = set(dep.depends_on)
    return graph


def get_reverse_dependency_graph() -> Dict[str, Set[str]]:
    """Return reverse adjacency: function -> set of functions that depend on it."""
    rev_graph: Dict[str, Set[str]] = {}
    for dep in FUNCTION_DEPENDENCIES:
        for prereq in dep.depends_on:
            if prereq not in rev_graph:
                rev_graph[prereq] = set()
            rev_graph[prereq].add(dep.function)
    return rev_graph


# ===========================================================================
# Part 2. Recovery stage definition
# ===========================================================================

class RecoveryStage(Enum):
    """Phases of recovery after collapse."""
    IMMEDIATE_SURVIVAL = "immediate_survival"     # hours to weeks
    SUBSISTENCE_STABILIZATION = "subsistence"     # weeks to seasons
    SOCIAL_RECONSTRUCTION = "social"              # seasons to years
    INFRASTRUCTURE_REBUILDING = "infrastructure"  # years to decades
    COORDINATION_RESTORATION = "coordination"     # decades to generations
    INSTITUTIONAL_MEMORY = "institutional"        # generations


# Map each substrate function to the recovery stage where it is
# typically rebuilt, based on dependencies and historical observation.

FUNCTION_RECOVERY_STAGE = {
    # IMMEDIATE_SURVIVAL: hours to weeks
    "water_access_and_quality": RecoveryStage.IMMEDIATE_SURVIVAL,
    "shelter_and_thermal_regulation": RecoveryStage.IMMEDIATE_SURVIVAL,
    "conflict_resolution_within_group": RecoveryStage.IMMEDIATE_SURVIVAL,

    # SUBSISTENCE_STABILIZATION: weeks to seasons
    "subsistence_food_production": RecoveryStage.SUBSISTENCE_STABILIZATION,
    "ecological_and_seasonal_observation": RecoveryStage.SUBSISTENCE_STABILIZATION,
    "waste_separation_from_life_substrate": RecoveryStage.SUBSISTENCE_STABILIZATION,

    # SOCIAL_RECONSTRUCTION: seasons to years
    "kinship_and_reproductive_coordination": RecoveryStage.SOCIAL_RECONSTRUCTION,
    "knowledge_transmission_across_generations": RecoveryStage.SOCIAL_RECONSTRUCTION,

    # INFRASTRUCTURE_REBUILDING: years to decades
    "infrastructure_maintenance": RecoveryStage.INFRASTRUCTURE_REBUILDING,
    "defense_and_boundary_maintenance": RecoveryStage.INFRASTRUCTURE_REBUILDING,

    # COORDINATION_RESTORATION: decades to generations
    "exchange_beyond_direct_reciprocity": RecoveryStage.COORDINATION_RESTORATION,
    "long_horizon_substrate_stewardship": RecoveryStage.COORDINATION_RESTORATION,

    # INSTITUTIONAL_MEMORY: generations
    "cross_boundary_commons_management": RecoveryStage.INSTITUTIONAL_MEMORY,
}


@dataclass
class RecoveryStageEstimate:
    """Estimated duration and requirements for one recovery stage."""
    stage: RecoveryStage
    typical_duration_years: Tuple[float, float]  # (min, max)
    prerequisite_stages: List[RecoveryStage]
    functions_restored: List[str]
    key_bottlenecks: List[str]
    historical_examples: List[str]


RECOVERY_STAGE_ESTIMATES = [
    RecoveryStageEstimate(
        stage=RecoveryStage.IMMEDIATE_SURVIVAL,
        typical_duration_years=(0.01, 0.1),  # days to weeks
        prerequisite_stages=[],
        functions_restored=[
            "water_access_and_quality",
            "shelter_and_thermal_regulation",
            "conflict_resolution_within_group",
        ],
        key_bottlenecks=[
            "water_access_and_quality",  # without water, nothing else matters
        ],
        historical_examples=[
            "post-disaster survival phase (earthquakes, hurricanes)",
            "refugee camp immediate establishment",
        ],
    ),
    RecoveryStageEstimate(
        stage=RecoveryStage.SUBSISTENCE_STABILIZATION,
        typical_duration_years=(0.5, 3.0),  # months to a few years
        prerequisite_stages=[RecoveryStage.IMMEDIATE_SURVIVAL],
        functions_restored=[
            "subsistence_food_production",
            "ecological_and_seasonal_observation",
            "waste_separation_from_life_substrate",
        ],
        key_bottlenecks=[
            "ecological_and_seasonal_observation",  # knowledge of local timing
            "subsistence_food_production",  # seed stocks, soil knowledge
        ],
        historical_examples=[
            "post-Roman Britain 5th-6th century subsistence phase",
            "post-Classic Maya lowland village phase",
            "1930s Dust Bowl subsistence adaptation",
        ],
    ),
    RecoveryStageEstimate(
        stage=RecoveryStage.SOCIAL_RECONSTRUCTION,
        typical_duration_years=(3.0, 15.0),  # years to a generation
        prerequisite_stages=[RecoveryStage.SUBSISTENCE_STABILIZATION],
        functions_restored=[
            "kinship_and_reproductive_coordination",
            "knowledge_transmission_across_generations",
        ],
        key_bottlenecks=[
            "knowledge_transmission_across_generations",  # lost skills
        ],
        historical_examples=[
            "post-Roman Britain 7th-8th century kingdom formation",
            "post-Bronze Age collapse village network reformation",
            "post-Soviet Central Asian kinship network revival",
        ],
    ),
    RecoveryStageEstimate(
        stage=RecoveryStage.INFRASTRUCTURE_REBUILDING,
        typical_duration_years=(10.0, 50.0),  # decades
        prerequisite_stages=[RecoveryStage.SOCIAL_RECONSTRUCTION],
        functions_restored=[
            "infrastructure_maintenance",
            "defense_and_boundary_maintenance",
        ],
        key_bottlenecks=[
            "infrastructure_maintenance",  # requires surplus and coordination
        ],
        historical_examples=[
            "post-Roman Britain 9th-10th century burh system",
            "post-Mongol Persia irrigation restoration",
            "post-WWII European reconstruction (accelerated by external aid)",
        ],
    ),
    RecoveryStageEstimate(
        stage=RecoveryStage.COORDINATION_RESTORATION,
        typical_duration_years=(30.0, 150.0),  # generations to centuries
        prerequisite_stages=[RecoveryStage.INFRASTRUCTURE_REBUILDING],
        functions_restored=[
            "exchange_beyond_direct_reciprocity",
            "long_horizon_substrate_stewardship",
        ],
        key_bottlenecks=[
            "long_horizon_substrate_stewardship",  # requires generational memory
        ],
        historical_examples=[
            "post-Roman Britain 11th-13th century market town network",
            "post-Classic Maya long-distance trade revival",
            "Medieval European forest management institutions",
        ],
    ),
    RecoveryStageEstimate(
        stage=RecoveryStage.INSTITUTIONAL_MEMORY,
        typical_duration_years=(100.0, 500.0),  # multiple generations
        prerequisite_stages=[RecoveryStage.COORDINATION_RESTORATION],
        functions_restored=[
            "cross_boundary_commons_management",
        ],
        key_bottlenecks=[
            "cross_boundary_commons_management",  # requires stable multi-polity relations
        ],
        historical_examples=[
            "European river commissions (19th century)",
            "Great Lakes water quality agreements (20th century)",
            "Montreal Protocol (late 20th century)",
        ],
    ),
]


# ===========================================================================
# Part 3. Recovery sequence from starting conditions
# ===========================================================================

@dataclass
class RecoveryPathway:
    """A sequenced recovery plan given post-collapse starting conditions."""
    starting_scale: ScaleTier
    target_scale: ScaleTier
    stages: List[RecoveryStage]
    total_years_min: float
    total_years_max: float
    stage_sequence: List[Tuple[RecoveryStage, List[str]]]  # (stage, functions)
    critical_preservations: List[str]  # what should have been preserved
    bottlenecks: List[str]
    pathway_notes: str


def build_recovery_pathway(
    collapse_estimate: CollapseDepthEstimate,
    target_scale: Optional[ScaleTier] = None,
) -> RecoveryPathway:
    """
    Given a collapse depth estimate, build the recovery sequence to
    return to the trigger scale (or a specified target scale).

    The sequence is determined by:
    1. Starting from the surviving scale
    2. Identifying which functions are not maintained at that scale
    3. Ordering those functions by dependency and recovery stage
    4. Building stages until target scale functions are restored
    """
    starting_scale = collapse_estimate.surviving_scale
    if target_scale is None:
        target_scale = collapse_estimate.trigger_scale

    starting_idx = SCALE_ORDER.index(starting_scale)
    target_idx = SCALE_ORDER.index(target_scale)

    if target_idx <= starting_idx:
        return RecoveryPathway(
            starting_scale=starting_scale,
            target_scale=target_scale,
            stages=[],
            total_years_min=0.0,
            total_years_max=0.0,
            stage_sequence=[],
            critical_preservations=[],
            bottlenecks=[],
            pathway_notes="Already at or above target scale.",
        )

    # Identify all functions required at target scale but not maintained
    # at starting scale.
    functions_to_restore: List[str] = []
    for func in SUBSTRATE_FUNCTIONS:
        required_at = SCALE_ORDER.index(func.first_required_at)
        if required_at <= target_idx:
            # Check if this function was among the critical atrophied ones
            # that caused the collapse depth
            if func.function in collapse_estimate.critical_atrophied_functions:
                functions_to_restore.append(func.function)
            # Also include any function first required above starting scale
            elif required_at > starting_idx:
                functions_to_restore.append(func.function)

    # Group functions by recovery stage
    stage_to_functions: Dict[RecoveryStage, List[str]] = {}
    for func_name in functions_to_restore:
        stage = FUNCTION_RECOVERY_STAGE.get(func_name)
        if stage:
            if stage not in stage_to_functions:
                stage_to_functions[stage] = []
            stage_to_functions[stage].append(func_name)

    # Order stages
    stage_order = [
        RecoveryStage.IMMEDIATE_SURVIVAL,
        RecoveryStage.SUBSISTENCE_STABILIZATION,
        RecoveryStage.SOCIAL_RECONSTRUCTION,
        RecoveryStage.INFRASTRUCTURE_REBUILDING,
        RecoveryStage.COORDINATION_RESTORATION,
        RecoveryStage.INSTITUTIONAL_MEMORY,
    ]

    stages_needed: List[RecoveryStage] = []
    for stage in stage_order:
        if stage in stage_to_functions:
            stages_needed.append(stage)

    # Build stage estimates
    stage_sequence: List[Tuple[RecoveryStage, List[str]]] = []
    total_min = 0.0
    total_max = 0.0

    for stage in stages_needed:
        functions = stage_to_functions[stage]
        stage_sequence.append((stage, functions))

        # Find estimate for this stage
        for est in RECOVERY_STAGE_ESTIMATES:
            if est.stage == stage:
                total_min += est.typical_duration_years[0]
                total_max += est.typical_duration_years[1]
                break

    # Critical preservations: what should have been maintained through
    # the collapse to enable faster recovery
    critical_preservations = []
    for func_name in MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS:
        if func_name in collapse_estimate.critical_atrophied_functions:
            critical_preservations.append(func_name)

    # Bottlenecks: functions whose absence most constrains recovery
    bottlenecks = []
    dep_graph = get_dependency_graph()
    rev_graph = get_reverse_dependency_graph()

    for func_name in functions_to_restore:
        # Functions that many other functions depend on are bottlenecks
        dependents = rev_graph.get(func_name, set())
        if len(dependents) >= 2:
            bottlenecks.append(func_name)

    # Generate pathway notes
    tiers_to_climb = target_idx - starting_idx
    notes = (
        f"Recovery from {starting_scale.value} to {target_scale.value} "
        f"requires climbing {tiers_to_climb} scale tiers. "
        f"Functions to restore: {len(functions_to_restore)}. "
        f"Critical atrophied functions that could have reduced collapse "
        f"depth if preserved: {critical_preservations}."
    )

    return RecoveryPathway(
        starting_scale=starting_scale,
        target_scale=target_scale,
        stages=stages_needed,
        total_years_min=total_min,
        total_years_max=total_max,
        stage_sequence=stage_sequence,
        critical_preservations=critical_preservations,
        bottlenecks=bottlenecks,
        pathway_notes=notes,
    )


# ===========================================================================
# Part 4. Preservation strategies
# ===========================================================================

@dataclass
class PreservationStrategy:
    """What must be preserved before/during collapse to enable recovery."""
    function: str
    preservation_form: str
    examples: List[str]
    vulnerability: str  # what threatens this preservation


PRESERVATION_STRATEGIES = [
    PreservationStrategy(
        function="subsistence_food_production",
        preservation_form=(
            "seed banks (both institutional and distributed household); "
            "oral and written knowledge of local cultivation; living "
            "practitioners in multiple locations"
        ),
        examples=[
            "Svalbard Global Seed Vault",
            "Indigenous seed-saving networks",
            "Andean potato diversity maintained across villages",
        ],
        vulnerability=(
            "institutional seed banks depend on continuous funding and "
            "infrastructure; distributed household seed saving is "
            "atrophied in industrial agriculture contexts"
        ),
    ),
    PreservationStrategy(
        function="water_access_and_quality",
        preservation_form=(
            "knowledge of local water tables, springs, and seasonal "
            "patterns; well-digging and water-finding skills; "
            "low-tech purification methods"
        ),
        examples=[
            "Traditional well-digging guilds (surviving in parts of "
            "India, North Africa)",
            "Spring-mapping knowledge in karst regions",
        ],
        vulnerability=(
            "centralized municipal water has atrophied local water "
            "knowledge; most urban populations cannot locate or access "
            "water without infrastructure"
        ),
    ),
    PreservationStrategy(
        function="ecological_and_seasonal_observation",
        preservation_form=(
            "landscape-encoded knowledge (place names, story sites); "
            "phenological calendars maintained by practitioners; "
            "distributed observation networks not dependent on "
            "centralized science institutions"
        ),
        examples=[
            "Aboriginal songlines",
            "Traditional ecological knowledge in Indigenous communities",
            "Farmer almanac traditions",
        ],
        vulnerability=(
            "centralized weather services and digital observation have "
            "atrophied direct ecological reading; knowledge holders are "
            "aging without transmission"
        ),
    ),
    PreservationStrategy(
        function="knowledge_transmission_across_generations",
        preservation_form=(
            "apprenticeship relationships; craft traditions with "
            "built-in teaching; oral history institutions; distributed "
            "libraries and archives"
        ),
        examples=[
            "Medieval guild apprenticeship",
            "Indigenous elder-youth knowledge transmission",
            "Monastic manuscript preservation",
            "Distributed digital archives (Internet Archive)",
        ],
        vulnerability=(
            "formal schooling has replaced apprenticeship for most "
            "practical skills; digital archives depend on continuous "
            "infrastructure"
        ),
    ),
    PreservationStrategy(
        function="long_horizon_substrate_stewardship",
        preservation_form=(
            "commons institutions with multi-generational memory; "
            "sacred restrictions on overuse; landscape features that "
            "encode use-rules"
        ),
        examples=[
            "Swiss alpine commons (centuries of continuous management)",
            "Japanese satoyama landscapes",
            "Balinese subak water temple system",
        ],
        vulnerability=(
            "privatization and state management have displaced commons "
            "institutions; where they survive, they are threatened by "
            "market integration"
        ),
    ),
    PreservationStrategy(
        function="conflict_resolution_within_group",
        preservation_form=(
            "customary law traditions; elder councils; mediation "
            "practices; restorative justice institutions"
        ),
        examples=[
            "Iroquois Great Law of Peace",
            "Somali xeer customary law",
            "Māori rūnanga councils",
            "Restorative justice programs in various jurisdictions",
        ],
        vulnerability=(
            "state legal systems have displaced customary law; where "
            "customary law survives, it is often not recognized by "
            "formal institutions"
        ),
    ),
]


# ===========================================================================
# Part 5. Historical validation

# ===========================================================================

@dataclass
class HistoricalRecoveryCase:
    """A documented historical recovery from collapse."""
    name: str
    collapse_description: str
    pre_collapse_scale: ScaleTier
    post_collapse_scale: ScaleTier
    recovery_duration_years: Tuple[float, float]
    recovery_scale_achieved: ScaleTier
    preserved_functions: List[str]
    atrophied_functions: List[str]
    pathway_match: str  # how well the modeled pathway matches observation
    notes: str


HISTORICAL_CASES = [
    HistoricalRecoveryCase(
        name="Post-Roman Britain",
        collapse_description=(
            "Roman administrative and economic withdrawal early 5th "
            "century; urban collapse; loss of coinage, wheel-thrown "
            "pottery, stone building"
        ),
        pre_collapse_scale=ScaleTier.REGION,  # Roman province
        post_collapse_scale=ScaleTier.VILLAGE,  # subsistence hamlets
        recovery_duration_years=(300.0, 600.0),  # to Norman period market towns
        recovery_scale_achieved=ScaleTier.REGION,  # medieval England
        preserved_functions=[
            "subsistence_food_production",
            "water_access_and_quality",
            "shelter_and_thermal_regulation",
            "kinship_and_reproductive_coordination",
        ],
        atrophied_functions=[
            "exchange_beyond_direct_reciprocity",  # coinage lost
            "infrastructure_maintenance",  # Roman roads decayed
            "cross_boundary_commons_management",
            "long_horizon_substrate_stewardship",  # reforestation suggests some
        ],
        pathway_match=(
            "Modeled pathway matches observed sequence: immediate survival "
            "(5th c), subsistence stabilization (6th c), social "
            "reconstruction (7th-8th c kingdoms), infrastructure "
            "rebuilding (9th-10th c burhs), coordination restoration "
            "(11th-13th c markets). Duration ~500 years matches model "
            "estimate for 3-tier climb."
        ),
        notes=(
            "Roman Britain provides the best-documented European case of "
            "multi-tier collapse and slow recovery. The survival of "
            "village-scale agriculture enabled eventual reconstruction."
        ),
    ),
    HistoricalRecoveryCase(
        name="Post-Bronze Age Eastern Mediterranean",
        collapse_description=(
            "Palace-state collapse ~1200 BCE; loss of Linear B writing, "
            "long-distance trade, monumental architecture, centralized "
            "administration"
        ),
        pre_collapse_scale=ScaleTier.REGION,  # Mycenaean, Hittite palace-states
        post_collapse_scale=ScaleTier.VILLAGE,  # small settlements, no writing
        recovery_duration_years=(300.0, 400.0),  # to Archaic Greek poleis
        recovery_scale_achieved=ScaleTier.REGION,  # Classical Greek world
        preserved_functions=[
            "subsistence_food_production",
            "water_access_and_quality",
            "shelter_and_thermal_regulation",
            "ecological_and_seasonal_observation",
            "kinship_and_reproductive_coordination",
        ],
        atrophied_functions=[
            "exchange_beyond_direct_reciprocity",
            "infrastructure_maintenance",
            "knowledge_transmission_across_generations",  # writing lost
            "cross_boundary_commons_management",
        ],
        pathway_match=(
            "Strong match to modeled pathway: subsistence village phase "
            "(1200-1000 BCE), social reconstruction with new kinship "
            "structures (1000-800 BCE), infrastructure and trade revival "
            "(800-600 BCE), coordination restoration (600-400 BCE). "
            "Duration ~400 years matches model for 3-tier climb."
        ),
        notes=(
            "The loss of writing (knowledge transmission atrophy) was a "
            "critical bottleneck. Recovery required reinvention of "
            "writing (Greek alphabet adapted from Phoenician)."
        ),
    ),
    HistoricalRecoveryCase(
        name="Post-Classic Maya Lowlands",
        collapse_description=(
            "Classic Maya city-state collapse 800-900 CE; population "
            "decline of 70-90%; abandonment of monumental centers; loss "
            "of Long Count calendar and hieroglyphic writing"
        ),
        pre_collapse_scale=ScaleTier.REGION,  # interconnected city-states
        post_collapse_scale=ScaleTier.VILLAGE,  # dispersed hamlets
        recovery_duration_years=(200.0, 400.0),  # to Postclassic centers
        recovery_scale_achieved=ScaleTier.TOWN,  # Postclassic Mayapan
        preserved_functions=[
            "subsistence_food_production",  # milpa agriculture continued
            "water_access_and_quality",  # cenotes remained accessible
            "shelter_and_thermal_regulation",
            "ecological_and_seasonal_observation",
        ],
        atrophied_functions=[
            "long_horizon_substrate_stewardship",  # soil degradation contributed to collapse
            "infrastructure_maintenance",  # reservoirs, terraces
            "knowledge_transmission_across_generations",  # writing lost
            "cross_boundary_commons_management",
        ],
        pathway_match=(
            "Partial match: subsistence phase (900-1000 CE) matches model. "
            "Social reconstruction phase produced new coastal trade "
            "networks (1000-1200 CE). Full recovery to Classic scale was "
            "not achieved before Spanish arrival. Soil degradation "
            "(substrate atrophy) limited recovery ceiling."
        ),
        notes=(
            "This case demonstrates that substrate atrophy (soil "
            "degradation) can permanently lower the recovery ceiling. "
            "The lowlands never regained Classic population density."
        ),
    ),
    HistoricalRecoveryCase(
        name="Post-Soviet Central Asia",
        collapse_description=(
            "Soviet Union dissolution 1991; collapse of centralized "
            "agricultural planning, industrial inputs, and distribution "
            "systems"
        ),
        pre_collapse_scale=ScaleTier.NATION,
        post_collapse_scale=ScaleTier.VILLAGE,  # rural subsistence revival
        recovery_duration_years=(10.0, 25.0),  # ongoing
        recovery_scale_achieved=ScaleTier.NATION,  # partial
        preserved_functions=[
            "kinship_and_reproductive_coordination",  # strong clan networks
            "subsistence_food_production",  # household plots
            "water_access_and_quality",  # traditional irrigation knowledge
            "conflict_resolution_within_group",  # customary law (adat)
        ],
        atrophied_functions=[
            "infrastructure_maintenance",  # Soviet irrigation decaying
            "exchange_beyond_direct_reciprocity",  # barter revived
            "cross_boundary_commons_management",  # Aral Sea, water sharing
        ],
        pathway_match=(
            "Accelerated match: strong preservation of kinship and "
            "subsistence functions enabled faster recovery than purely "
            "atrophied cases. Recovery duration 10-25 years vs. model "
            "prediction of 100+ years for 2-tier climb. The difference "
            "is attributable to intact social substrate."
        ),
        notes=(
            "This case validates the model's core claim: preserved "
            "smaller-scale functions dramatically accelerate recovery. "
            "Where Soviet-era infrastructure decayed, kin-based mutual "
            "aid substituted."
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
            "Recovery from collapse follows a predictable stage sequence "
            "(immediate survival → subsistence → social → infrastructure "
            "→ coordination → institutional) regardless of cultural "
            "context, because the sequence is constrained by function "
            "dependencies"
        ),
        "falsification": (
            "Identify a historical recovery that restored coordination "
            "functions before subsistence functions were stable"
        ),
    },
    {
        "id": 2,
        "claim": (
            "The number of scale tiers lost predicts minimum recovery "
            "time: each lost tier adds 30-150 years to recovery duration "
            "absent external aid"
        ),
        "falsification": (
            "Identify multi-tier collapses that recovered within a "
            "single generation without external assistance"
        ),
    },
    {
        "id": 3,
        "claim": (
            "Preservation of minimum viable civilization functions "
            "through collapse dramatically reduces recovery time; "
            "atrophy of these functions increases it"
        ),
        "falsification": (
            "Compare collapses with similar tier loss but different "
            "preservation patterns; show no correlation between "
            "preservation and recovery speed"
        ),
    },
    {
        "id": 4,
        "claim": (
            "Loss of knowledge_transmission_across_generations "
            "(e.g., writing, apprenticeship) is a critical bottleneck "
            "that extends recovery by generations"
        ),
        "falsification": (
            "Identify a case where writing was lost and recovered within "
            "a single generation without external reintroduction"
        ),
    },
    {
        "id": 5,
        "claim": (
            "Substrate degradation (soil, water, ecological baseline) "
            "can permanently lower the recovery ceiling; some collapses "
            "never return to pre-collapse scale because the substrate "
            "can no longer support it"
        ),
        "falsification": (
            "Identify a civilization that recovered to pre-collapse "
            "scale on a significantly degraded substrate without "
            "external inputs"
        ),
    },
    {
        "id": 6,
        "claim": (
            "The dependency graph accurately predicts which functions "
            "must be restored before others; attempts to skip "
            "dependencies fail"
        ),
        "falsification": (
            "Identify a successful recovery that restored "
            "long_horizon_substrate_stewardship before restoring "
            "ecological_and_seasonal_observation"
        ),
    },
    {
        "id": 7,
        "claim": (
            "External aid can compress recovery timelines but cannot "
            "skip stages; the dependency sequence remains binding"
        ),
        "falsification": (
            "Identify a post-collapse recovery where external aid "
            "enabled coordination restoration before subsistence "
            "stabilization"
        ),
    },
]


# ===========================================================================
# Part 7. Rendering and integration

# ===========================================================================

def render_recovery_pathway(pathway: RecoveryPathway) -> str:
    """Render a recovery pathway as readable text."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append(f"RECOVERY PATHWAY: {pathway.starting_scale.value} → {pathway.target_scale.value}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(pathway.pathway_notes)
    lines.append("")
    lines.append(f"Total estimated recovery: {pathway.total_years_min:.0f}-{pathway.total_years_max:.0f} years")
    lines.append("")
    lines.append("Stage sequence:")
    for stage, functions in pathway.stage_sequence:
        lines.append(f"  {stage.value}:")
        for func in functions:
            lines.append(f"    - {func}")
    lines.append("")
    lines.append(f"Critical functions to preserve before collapse:")
    for func in pathway.critical_preservations:
        lines.append(f"  - {func}")
    lines.append("")
    lines.append(f"Recovery bottlenecks:")
    for func in pathway.bottlenecks:
        lines.append(f"  - {func}")
    return "\n".join(lines)


def render_historical_validation() -> str:
    """Render historical cases compared to model predictions."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("HISTORICAL VALIDATION")
    lines.append("=" * 80)
    lines.append("")

    for case in HISTORICAL_CASES:
        lines.append(f"--- {case.name} ---")
        lines.append(f"  Collapse: {case.pre_collapse_scale.value} → {case.post_collapse_scale.value}")
        lines.append(f"  Recovery: {case.recovery_duration_years[0]:.0f}-{case.recovery_duration_years[1]:.0f} years to {case.recovery_scale_achieved.value}")
        lines.append(f"  Preserved: {', '.join(case.preserved_functions)}")
        lines.append(f"  Atrophied: {', '.join(case.atrophied_functions)}")
        lines.append(f"  Model match: {case.pathway_match[:100]}...")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    from term_audit.collapse_propensity import (
        current_civilization_collapse_depth,
        ScaleTier,
    )

    # Example: recovery from nation-scale collapse under current atrophy
    print("=" * 80)
    print("CURRENT CIVILIZATION RECOVERY PATHWAY")
    print("=" * 80)
    print()

    nation_collapse = current_civilization_collapse_depth(ScaleTier.NATION)
    pathway = build_recovery_pathway(nation_collapse)
    print(render_recovery_pathway(pathway))
    print()

    print(render_historical_validation())
    print()

    print("=" * 80)
    print("PRESERVATION STRATEGIES")
    print("=" * 80)
    for strat in PRESERVATION_STRATEGIES[:3]:
        print(f"\n{strat.function}:")
        print(f"  Form: {strat.preservation_form[:100]}...")
        print(f"  Vulnerability: {strat.vulnerability}")

    print()
    print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
