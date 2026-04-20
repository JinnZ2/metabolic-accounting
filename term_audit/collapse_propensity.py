"""
term_audit/collapse_propensity.py

Quantitative measurement of multi-tier collapse vulnerability.

Core claim: civilizations (and firms, and any nested system) can lose
multiple scale tiers in a single collapse event when smaller-scale
substrate functions have been allowed to atrophy. The depth of
collapse is predictable from measurable atrophy indicators.

This module extends civilization_substrate_scaling.py with:

collapse_depth_estimate        how many scale tiers would be lost
                               if coordination at a given scale fails
atrophy_vector                 per-function measure of institutional
                               decay at each scale tier
cascade_amplification          how failure at one tier propagates
                               downward through atrophied tiers
recovery_time_estimate         multi-generational recovery horizons
                               when multiple tiers are lost
firm_collapse_analog           applying the same logic to firms:
                               why a firm that has outsourced or
                               financialized its substrate functions
                               collapses further and faster

The module is falsifiable: it makes specific predictions about which
civilizations and which firms are vulnerable to multi-tier collapse,
and what the depth of collapse would be given current atrophy.

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
    substrate_functions_at_scale,
)

# ===========================================================================
# Part 1. Atrophy scoring
# ===========================================================================

class AtrophyLevel(Enum):
    """How intact is the institutional capacity to perform a substrate
    function at a given scale?"""
    ROBUST = "robust"           # widely practiced, multiple
                                # redundant providers, knowledge
                                # widely distributed
    MAINTAINED = "maintained"   # practiced, sufficient providers,
                                # knowledge transmitted
    THIN = "thin"               # practiced but fragile, few
                                # providers, knowledge concentrated
    VESTIGIAL = "vestigial"     # barely practiced, institutional
                                # memory fading, dependent on
                                # larger-scale systems
    ATROPHIED = "atrophied"     # not practiced at this scale;
                                # completely dependent on larger
                                # scale for function


ATROPHY_NUMERIC = {
    AtrophyLevel.ROBUST: 0.0,
    AtrophyLevel.MAINTAINED: 0.25,
    AtrophyLevel.THIN: 0.5,
    AtrophyLevel.VESTIGIAL: 0.75,
    AtrophyLevel.ATROPHIED: 1.0,
}


@dataclass
class FunctionAtrophyProfile:
    """Atrophy assessment for one substrate function across all
    scale tiers where it could be performed."""
    function: str
    atrophy_by_scale: Dict[ScaleTier, AtrophyLevel]
    notes: str = ""

    def atrophy_numeric(self, scale: ScaleTier) -> float:
        """Return numeric atrophy at given scale, or 1.0 if not
        assessed (assume worst)."""
        level = self.atrophy_by_scale.get(scale, AtrophyLevel.ATROPHIED)
        return ATROPHY_NUMERIC[level]

    def lowest_viable_scale(self) -> Optional[ScaleTier]:
        """Return the smallest scale where this function is at least
        MAINTAINED. If none, return None (function is atrophied at
        all scales)."""
        for scale in SCALE_ORDER:
            level = self.atrophy_by_scale.get(scale)
            if level in (AtrophyLevel.ROBUST, AtrophyLevel.MAINTAINED):
                return scale
        return None


# ===========================================================================
# Part 2. Collapse depth calculation
# ===========================================================================

@dataclass
class CollapseDepthEstimate:
    """How many scale tiers would be lost if coordination at a given
    scale fails, given current atrophy patterns."""
    trigger_scale: ScaleTier           # scale where coordination
                                       # fails (e.g., nation,
                                       # continental, global)
    surviving_scale: ScaleTier         # largest scale that can
                                       # still support life
    tiers_lost: int                    # number of tiers dropped
    critical_atrophied_functions: List[str]  # functions whose
                                       # atrophy caused multi-tier
                                       # loss
    recovery_generations: int          # estimated generations to
                                       # rebuild lost tiers
    rationale: str


def estimate_collapse_depth(
    trigger_scale: ScaleTier,
    atrophy_profiles: List[FunctionAtrophyProfile],
) -> CollapseDepthEstimate:
    """
    Given a failure of coordination at trigger_scale, how far down
    does the collapse propagate?

    The logic:
    1. Identify all substrate functions required at or below the
       trigger scale.
    2. For each function, find the smallest scale where it is at
       least MAINTAINED.
    3. The surviving scale is the maximum of those smallest
       maintained scales across all required functions.
    4. If any function has no maintained scale, collapse goes to
       BAND (theoretical minimum for human survival).

    This is conservative: it assumes that if a function is not
    maintained at a scale, that scale cannot support life when
    larger-scale coordination fails.
    """
    trigger_idx = SCALE_ORDER.index(trigger_scale)

    # All functions required at or below trigger scale
    required_functions = [
        f for f in SUBSTRATE_FUNCTIONS
        if SCALE_ORDER.index(f.first_required_at) <= trigger_idx
    ]

    # Build map from function name to profile
    profile_map = {p.function: p for p in atrophy_profiles}

    # Find the smallest maintained scale for each required function
    smallest_maintained: Dict[str, Optional[ScaleTier]] = {}
    atrophied_functions: List[str] = []

    for f in required_functions:
        if f.function not in profile_map:
            # Unassessed: assume worst (atrophied at all scales)
            smallest_maintained[f.function] = None
            atrophied_functions.append(f.function)
            continue

        profile = profile_map[f.function]
        maintained = profile.lowest_viable_scale()
        smallest_maintained[f.function] = maintained

        if maintained is None:
            atrophied_functions.append(f.function)

    # The surviving scale is the maximum of the smallest maintained
    # scales (i.e., we can only go down as far as the most fragile
    # function allows)
    surviving_idx = 0  # BAND is index 0
    critical_functions: List[str] = []

    for func_name, maintained_scale in smallest_maintained.items():
        if maintained_scale is None:
            # Function is not maintained at any scale.
            # Collapse goes to BAND.
            surviving_idx = 0
            critical_functions.append(func_name)
        else:
            maintained_idx = SCALE_ORDER.index(maintained_scale)
            if maintained_idx > surviving_idx:
                surviving_idx = maintained_idx
                critical_functions = [func_name]
            elif maintained_idx == surviving_idx and surviving_idx > 0:
                critical_functions.append(func_name)

    surviving_scale = SCALE_ORDER[surviving_idx]
    tiers_lost = trigger_idx - surviving_idx

    # Recovery time estimate: each lost tier requires roughly one
    # generation to rebuild institutional knowledge and practice.
    # Multiple tiers compound because you must rebuild sequentially.
    # Base: 1 generation per tier. Add 1 generation per critical
    # atrophied function beyond the first.
    recovery_generations = tiers_lost + max(0, len(critical_functions) - 1)

    # Generate rationale
    if tiers_lost == 0:
        rationale = (
            f"All required functions are maintained at or below "
            f"{trigger_scale.value} scale. Collapse would not "
            f"propagate below {surviving_scale.value}."
        )
    elif tiers_lost == 1:
        rationale = (
            f"Single-tier loss from {trigger_scale.value} to "
            f"{surviving_scale.value}. Critical function(s): "
            f"{', '.join(critical_functions)}."
        )
    else:
        rationale = (
            f"Multi-tier collapse from {trigger_scale.value} to "
            f"{surviving_scale.value} ({tiers_lost} tiers lost). "
            f"Critical atrophied functions: "
            f"{', '.join(critical_functions)}. "
            f"These functions are not maintained at intermediate "
            f"scales, forcing collapse to propagate through "
            f"multiple tiers."
        )

    return CollapseDepthEstimate(
        trigger_scale=trigger_scale,
        surviving_scale=surviving_scale,
        tiers_lost=tiers_lost,
        critical_atrophied_functions=critical_functions,
        recovery_generations=recovery_generations,
        rationale=rationale,
    )


# ===========================================================================
# Part 3. Current civilization atrophy assessment
# ===========================================================================

# This is a falsifiable empirical claim about current conditions.
# It is parameterized so it can be updated as evidence accumulates.

CURRENT_ATROPHY_PROFILES = [
    FunctionAtrophyProfile(
        function="subsistence_food_production",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.VESTIGIAL,
            ScaleTier.CLAN: AtrophyLevel.VESTIGIAL,
            ScaleTier.VILLAGE: AtrophyLevel.THIN,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
            ScaleTier.METROPOLIS: AtrophyLevel.ATROPHIED,
            ScaleTier.REGION: AtrophyLevel.ATROPHIED,
            ScaleTier.NATION: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "most populations dependent on industrial agriculture "
            "and long supply chains; subsistence skills largely "
            "lost below village scale"
        ),
    ),
    FunctionAtrophyProfile(
        function="water_access_and_quality",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.THIN,
            ScaleTier.CLAN: AtrophyLevel.THIN,
            ScaleTier.VILLAGE: AtrophyLevel.MAINTAINED,
            ScaleTier.TOWN: AtrophyLevel.MAINTAINED,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
            ScaleTier.METROPOLIS: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "municipal water systems handle urban scales; rural "
            "well knowledge persists; wilderness water knowledge "
            "thinning"
        ),
    ),
    FunctionAtrophyProfile(
        function="shelter_and_thermal_regulation",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.THIN,
            ScaleTier.CLAN: AtrophyLevel.THIN,
            ScaleTier.VILLAGE: AtrophyLevel.MAINTAINED,
            ScaleTier.TOWN: AtrophyLevel.MAINTAINED,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "construction skills exist at village/town scale; "
            "wilderness shelter knowledge thinning; urban "
            "populations fully dependent on infrastructure"
        ),
    ),
    FunctionAtrophyProfile(
        function="waste_separation_from_life_substrate",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ATROPHIED,
            ScaleTier.CLAN: AtrophyLevel.ATROPHIED,
            ScaleTier.VILLAGE: AtrophyLevel.VESTIGIAL,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
            ScaleTier.METROPOLIS: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "composting knowledge exists but not widely practiced; "
            "sewerage is centralized infrastructure; without it, "
            "disease spreads rapidly"
        ),
    ),
    FunctionAtrophyProfile(
        function="knowledge_transmission_across_generations",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ATROPHIED,
            ScaleTier.CLAN: AtrophyLevel.VESTIGIAL,
            ScaleTier.VILLAGE: AtrophyLevel.THIN,
            ScaleTier.TOWN: AtrophyLevel.MAINTAINED,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "formal schooling replaces apprenticeship; practical "
            "skills transmission atrophied; depends on state "
            "education infrastructure"
        ),
    ),
    FunctionAtrophyProfile(
        function="conflict_resolution_within_group",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ROBUST,
            ScaleTier.CLAN: AtrophyLevel.ROBUST,
            ScaleTier.VILLAGE: AtrophyLevel.MAINTAINED,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "small-scale conflict resolution skills persist in "
            "families and small communities; larger scales depend "
            "on formal legal systems"
        ),
    ),
    FunctionAtrophyProfile(
        function="defense_and_boundary_maintenance",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.VESTIGIAL,
            ScaleTier.CLAN: AtrophyLevel.VESTIGIAL,
            ScaleTier.VILLAGE: AtrophyLevel.THIN,
            ScaleTier.TOWN: AtrophyLevel.ATROPHIED,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "most populations have no capacity for local defense; "
            "fully dependent on state monopoly on violence"
        ),
    ),
    FunctionAtrophyProfile(
        function="kinship_and_reproductive_coordination",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ROBUST,
            ScaleTier.CLAN: AtrophyLevel.ROBUST,
            ScaleTier.VILLAGE: AtrophyLevel.MAINTAINED,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "kinship networks persist but weakened; larger scales "
            "depend on formal marriage and reproductive "
            "infrastructure"
        ),
    ),
    FunctionAtrophyProfile(
        function="ecological_and_seasonal_observation",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ATROPHIED,
            ScaleTier.CLAN: AtrophyLevel.ATROPHIED,
            ScaleTier.VILLAGE: AtrophyLevel.VESTIGIAL,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "most populations cannot read ecological signals; "
            "dependent on scientific monitoring and weather apps"
        ),
    ),
    FunctionAtrophyProfile(
        function="infrastructure_maintenance",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ROBUST,  # tools and shelter
            ScaleTier.CLAN: AtrophyLevel.ROBUST,
            ScaleTier.VILLAGE: AtrophyLevel.MAINTAINED,
            ScaleTier.TOWN: AtrophyLevel.MAINTAINED,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "small-scale maintenance skills persist; urban "
            "infrastructure requires specialized centralized "
            "workforces"
        ),
    ),
    FunctionAtrophyProfile(
        function="exchange_beyond_direct_reciprocity",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ROBUST,  # gift exchange
            ScaleTier.CLAN: AtrophyLevel.ROBUST,
            ScaleTier.VILLAGE: AtrophyLevel.MAINTAINED,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "local exchange and barter skills exist but are "
            "marginal; most exchange is monetized and depends on "
            "financial infrastructure"
        ),
    ),
    FunctionAtrophyProfile(
        function="long_horizon_substrate_stewardship",
        atrophy_by_scale={
            ScaleTier.BAND: AtrophyLevel.ATROPHIED,
            ScaleTier.CLAN: AtrophyLevel.ATROPHIED,
            ScaleTier.VILLAGE: AtrophyLevel.VESTIGIAL,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "few populations practice multi-generational "
            "stewardship; dependent on state conservation and "
            "regulation"
        ),
    ),
    FunctionAtrophyProfile(
        function="cross_boundary_commons_management",
        atrophy_by_scale={
            ScaleTier.VILLAGE: AtrophyLevel.THIN,
            ScaleTier.TOWN: AtrophyLevel.THIN,
            ScaleTier.CITY: AtrophyLevel.ATROPHIED,
            ScaleTier.METROPOLIS: AtrophyLevel.ATROPHIED,
            ScaleTier.REGION: AtrophyLevel.ATROPHIED,
        },
        notes=(
            "watershed councils and similar institutions exist "
            "but are thin; most cross-boundary management depends "
            "on state and international bodies"
        ),
    ),
]


def current_civilization_collapse_depth(
    trigger_scale: ScaleTier,
) -> CollapseDepthEstimate:
    """Estimate collapse depth for current civilization given
    observed atrophy patterns."""
    return estimate_collapse_depth(trigger_scale, CURRENT_ATROPHY_PROFILES)


# ===========================================================================
# Part 4. Firm collapse analog
# ===========================================================================

# The same multi-tier collapse logic applies to firms. A firm that
# has outsourced, financialized, or atrophied its substrate functions
# will collapse through multiple organizational layers when its
# coordination layer fails.

class FirmLayer(Enum):
    """Organizational layers in a firm, analogous to civilization
    scale tiers."""
    OPERATOR = "operator"               # individual doing the work
    TEAM = "team"                       # 3-15 people, direct coordination
    DEPARTMENT = "department"           # 15-150, manager coordination
    DIVISION = "division"               # 150-1500, director coordination
    BUSINESS_UNIT = "business_unit"     # 1500-15000, VP coordination
    FIRM = "firm"                       # 15000+, executive coordination
    CONGLOMERATE = "conglomerate"       # multi-firm holding structure


FIRM_LAYER_ORDER = [
    FirmLayer.OPERATOR,
    FirmLayer.TEAM,
    FirmLayer.DEPARTMENT,
    FirmLayer.DIVISION,
    FirmLayer.BUSINESS_UNIT,
    FirmLayer.FIRM,
    FirmLayer.CONGLOMERATE,
]


@dataclass
class FirmSubstrateFunction:
    """A function that must exist at some layer for the firm to
    operate. Analogous to SubstrateFunction."""
    function: str
    first_required_at: FirmLayer
    rationale: str
    atrophy_consequence: str


FIRM_SUBSTRATE_FUNCTIONS = [
    FirmSubstrateFunction(
        function="direct_work_execution",
        first_required_at=FirmLayer.OPERATOR,
        rationale=(
            "someone must actually perform the work the firm claims "
            "to do"
        ),
        atrophy_consequence=(
            "work doesn't get done; firm is a shell"
        ),
    ),
    FirmSubstrateFunction(
        function="peer_coordination",
        first_required_at=FirmLayer.TEAM,
        rationale=(
            "work beyond individual capacity requires coordination "
            "among those doing the work"
        ),
        atrophy_consequence=(
            "work fragments; duplication and gaps emerge"
        ),
    ),
    FirmSubstrateFunction(
        function="capacity_assessment",
        first_required_at=FirmLayer.TEAM,
        rationale=(
            "teams must know who can do what; this is E_A "
            "operational capacity, not credentialing"
        ),
        atrophy_consequence=(
            "wrong people assigned to wrong tasks; failures "
            "propagate"
        ),
    ),
    FirmSubstrateFunction(
        function="substrate_awareness",
        first_required_at=FirmLayer.OPERATOR,
        rationale=(
            "operators must perceive the physical substrate they "
            "work on (soil, machines, code, patients)"
        ),
        atrophy_consequence=(
            "substrate degradation proceeds undetected; cascade "
            "failures surprise the firm"
        ),
    ),
    FirmSubstrateFunction(
        function="local_adaptation",
        first_required_at=FirmLayer.TEAM,
        rationale=(
            "teams must adapt processes to local conditions; "
            "central planning cannot see local variance"
        ),
        atrophy_consequence=(
            "processes become brittle; local failures cascade"
        ),
    ),
    FirmSubstrateFunction(
        function="knowledge_transmission",
        first_required_at=FirmLayer.TEAM,
        rationale=(
            "operational knowledge must transmit from experienced "
            "operators to new ones"
        ),
        atrophy_consequence=(
            "knowledge loss; each departure degrades capacity"
        ),
    ),
    FirmSubstrateFunction(
        function="failure_detection",
        first_required_at=FirmLayer.OPERATOR,
        rationale=(
            "operators are first to detect when things are going "
            "wrong"
        ),
        atrophy_consequence=(
            "failures detected late or not at all; cascade "
            "amplifies"
        ),
    ),
    FirmSubstrateFunction(
        function="resource_allocation",
        first_required_at=FirmLayer.DEPARTMENT,
        rationale=(
            "teams need resources; someone must allocate across "
            "teams"
        ),
        atrophy_consequence=(
            "resource starvation; teams cannot execute"
        ),
    ),
    FirmSubstrateFunction(
        function="cross_team_coordination",
        first_required_at=FirmLayer.DEPARTMENT,
        rationale=(
            "multiple teams working on related things must "
            "coordinate"
        ),
        atrophy_consequence=(
            "teams work at cross-purposes; waste accumulates"
        ),
    ),
]


@dataclass
class FirmAtrophyProfile:
    """Atrophy assessment for a firm's substrate functions."""
    firm_name: str
    atrophy_by_function: Dict[str, FirmLayer]  # lowest layer where
                                                # function is maintained
    outsourced_functions: List[str]            # functions performed
                                                # outside the firm
    financialized_functions: List[str]         # functions replaced
                                                # by financial claims


@dataclass
class FirmCollapseDepth:
    """How many layers a firm would lose if its top coordination
    fails."""
    trigger_layer: FirmLayer
    surviving_layer: FirmLayer
    layers_lost: int
    critical_atrophied_functions: List[str]
    outsourced_vulnerabilities: List[str]
    financialized_vulnerabilities: List[str]
    recovery_months: int
    rationale: str


def estimate_firm_collapse_depth(
    profile: FirmAtrophyProfile,
    trigger_layer: FirmLayer = FirmLayer.FIRM,
) -> FirmCollapseDepth:
    """
    Given a firm's atrophy profile, how many layers collapse if
    executive coordination fails?

    The mechanism is identical to civilization collapse depth:
    - If a function is not maintained at a layer, that layer cannot
      operate when higher layers fail.
    - Outsourced functions are maintained at NO layer within the
      firm; they are external dependencies.
    - Financialized functions are replaced by claims that do not
      perform the function; they are atrophied.
    """
    trigger_idx = FIRM_LAYER_ORDER.index(trigger_layer)

    # All functions required at or below trigger layer
    required = [
        f for f in FIRM_SUBSTRATE_FUNCTIONS
        if FIRM_LAYER_ORDER.index(f.first_required_at) <= trigger_idx
    ]

    surviving_idx = 0  # OPERATOR
    critical: List[str] = []
    outsourced_vuln: List[str] = []
    financialized_vuln: List[str] = []

    for f in required:
        if f.function in profile.outsourced_functions:
            # Function is performed outside the firm.
            # If the external provider fails, the firm has no
            # internal capacity. This is a collapse amplifier.
            outsourced_vuln.append(f.function)
            # The function is effectively atrophied at all internal
            # layers. Surviving layer cannot be above OPERATOR
            # (individuals might still have personal capacity).
            surviving_idx = max(surviving_idx, 0)

        elif f.function in profile.financialized_functions:
            # Function has been replaced by a financial claim
            # (e.g., insurance instead of maintenance, hedging
            # instead of substrate stewardship). When the claim
            # fails to produce the function, there is no
            # operational capacity.
            financialized_vuln.append(f.function)
            surviving_idx = max(surviving_idx, 0)

        elif f.function in profile.atrophy_by_function:
            maintained_layer = profile.atrophy_by_function[f.function]
            maintained_idx = FIRM_LAYER_ORDER.index(maintained_layer)
            if maintained_idx > surviving_idx:
                surviving_idx = maintained_idx
                critical = [f.function]
            elif maintained_idx == surviving_idx and surviving_idx > 0:
                critical.append(f.function)
        else:
            # Unassessed: assume atrophied at all layers
            critical.append(f.function)

    surviving_layer = FIRM_LAYER_ORDER[surviving_idx]
    layers_lost = trigger_idx - surviving_idx

    # Recovery time in months: each lost layer requires rebuilding
    # institutional knowledge. Base: 3 months per layer. Add 6
    # months per outsourced function, 3 months per financialized
    # function.
    recovery_months = (
        layers_lost * 3 +
        len(outsourced_vuln) * 6 +
        len(financialized_vuln) * 3
    )

    if layers_lost == 0:
        rationale = (
            f"Firm maintains all required functions internally. "
            f"Executive failure would not cascade below "
            f"{surviving_layer.value}."
        )
    else:
        rationale = (
            f"Multi-layer collapse from {trigger_layer.value} to "
            f"{surviving_layer.value} ({layers_lost} layers lost). "
            f"Critical atrophied internal functions: {critical}. "
            f"Outsourced vulnerabilities: {outsourced_vuln}. "
            f"Financialized vulnerabilities: {financialized_vuln}."
        )

    return FirmCollapseDepth(
        trigger_layer=trigger_layer,
        surviving_layer=surviving_layer,
        layers_lost=layers_lost,
        critical_atrophied_functions=critical,
        outsourced_vulnerabilities=outsourced_vuln,
        financialized_vulnerabilities=financialized_vuln,
        recovery_months=recovery_months,
        rationale=rationale,
    )


# ===========================================================================
# Part 5. Example firm profiles
# ===========================================================================

# These are archetypal profiles for different firm strategies.

FIRM_ARCHEYPES = {
    "craft_guild_firm": FirmAtrophyProfile(
        firm_name="craft_guild_firm",
        atrophy_by_function={
            "direct_work_execution": FirmLayer.OPERATOR,
            "peer_coordination": FirmLayer.TEAM,
            "capacity_assessment": FirmLayer.TEAM,
            "substrate_awareness": FirmLayer.OPERATOR,
            "local_adaptation": FirmLayer.TEAM,
            "knowledge_transmission": FirmLayer.TEAM,
            "failure_detection": FirmLayer.OPERATOR,
            "resource_allocation": FirmLayer.DEPARTMENT,
            "cross_team_coordination": FirmLayer.DEPARTMENT,
        },
        outsourced_functions=[],
        financialized_functions=[],
    ),
    "modern_corporation": FirmAtrophyProfile(
        firm_name="modern_corporation",
        atrophy_by_function={
            "direct_work_execution": FirmLayer.OPERATOR,
            "peer_coordination": FirmLayer.TEAM,
            "capacity_assessment": FirmLayer.BUSINESS_UNIT,  # HR credentialing
            "substrate_awareness": FirmLayer.FIRM,  # only executives see reports
            "local_adaptation": FirmLayer.BUSINESS_UNIT,  # centralized process
            "knowledge_transmission": FirmLayer.FIRM,  # corporate training
            "failure_detection": FirmLayer.DIVISION,  # metrics, not operators
            "resource_allocation": FirmLayer.FIRM,  # central budget
            "cross_team_coordination": FirmLayer.BUSINESS_UNIT,
        },
        outsourced_functions=[
            "substrate_awareness",  # consultants do the observing
        ],
        financialized_functions=[
            "failure_detection",  # insurance, not prevention
        ],
    ),
    "financialized_firm": FirmAtrophyProfile(
        firm_name="financialized_firm",
        atrophy_by_function={
            "direct_work_execution": FirmLayer.OPERATOR,  # still need workers
            "peer_coordination": FirmLayer.TEAM,
            "capacity_assessment": FirmLayer.FIRM,
            "substrate_awareness": FirmLayer.FIRM,
            "local_adaptation": FirmLayer.FIRM,
            "knowledge_transmission": FirmLayer.FIRM,
            "failure_detection": FirmLayer.FIRM,
            "resource_allocation": FirmLayer.FIRM,
            "cross_team_coordination": FirmLayer.FIRM,
        },
        outsourced_functions=[
            "direct_work_execution",  # contractors
            "substrate_awareness",
            "knowledge_transmission",
        ],
        financialized_functions=[
            "failure_detection",
            "local_adaptation",
        ],
    ),
    "extractive_firm": FirmAtrophyProfile(
        firm_name="extractive_firm",  # e.g., mining, ag, fossil
        atrophy_by_function={
            "direct_work_execution": FirmLayer.OPERATOR,
            "peer_coordination": FirmLayer.TEAM,
            "capacity_assessment": FirmLayer.DIVISION,
            "substrate_awareness": FirmLayer.FIRM,  # executives ignore reports
            "local_adaptation": FirmLayer.DIVISION,
            "knowledge_transmission": FirmLayer.FIRM,
            "failure_detection": FirmLayer.FIRM,  # financial reports only
            "resource_allocation": FirmLayer.FIRM,
            "cross_team_coordination": FirmLayer.BUSINESS_UNIT,
        },
        outsourced_functions=[
            "substrate_awareness",  # environmental consultants ignored
        ],
        financialized_functions=[
            "failure_detection",  # legal liability, not prevention
        ],
    ),
}


# ===========================================================================
# Part 6. Falsifiable predictions
# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
    {
        "id": 1,
        "claim": (
            "Civilizations with more atrophied substrate functions at "
            "smaller scales will experience deeper collapse when "
            "larger-scale coordination fails"
        ),
        "falsification": (
            "Identify historical collapses where smaller-scale "
            "functions were atrophied but collapse depth was shallow; "
            "or where functions were robust but collapse was deep"
        ),
    },
    {
        "id": 2,
        "claim": (
            "Current civilization, if nation-scale coordination fails, "
            "would collapse to town scale or below because critical "
            "substrate functions (food, water, waste, ecological "
            "observation) are not maintained at intermediate scales"
        ),
        "falsification": (
            "Demonstrate that these functions are in fact robustly "
            "maintained at regional, metropolitan, and city scales"
        ),
    },
    {
        "id": 3,
        "claim": (
            "Firms that have outsourced or financialized substrate "
            "functions will collapse through more organizational "
            "layers when executive coordination fails than firms that "
            "maintain those functions internally"
        ),
        "falsification": (
            "Compare collapse depths of financialized vs. craft firms "
            "during a market disruption; show no difference"
        ),
    },
    {
        "id": 4,
        "claim": (
            "Recovery time from collapse scales with the number of "
            "atrophied functions and lost tiers; multi-tier collapse "
            "requires multi-generational recovery"
        ),
        "falsification": (
            "Identify a multi-tier collapse that recovered within a "
            "single generation without external assistance"
        ),
    },
    {
        "id": 5,
        "claim": (
            "The functions in MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS "
            "are necessary at all scales; atrophy of any of them at a "
            "given scale makes that scale non-viable when higher "
            "coordination fails"
        ),
        "falsification": (
            "Find a scale tier that persisted without one of these "
            "functions after higher coordination collapsed"
        ),
    },
    {
        "id": 6,
        "claim": (
            "Outsourced firm functions create external dependencies "
            "that amplify collapse; a firm with outsourced "
            "substrate_awareness cannot detect its own degradation"
        ),
        "falsification": (
            "Show that outsourced substrate awareness produces equal "
            "or better detection of degradation than internal "
            "operator awareness"
        ),
    },
    {
        "id": 7,
        "claim": (
            "Financialized functions (insurance, hedging, liability "
            "transfer) do not perform the underlying function; they "
            "transfer claims about the function. When the function "
            "fails, the financial claim does not restore it."
        ),
        "falsification": (
            "Demonstrate a case where an insured-but-unmaintained "
            "system continued to function after the insured event"
        ),
    },
]


# ===========================================================================
# Part 7. Attack-response matrix
# ===========================================================================

ATTACK_RESPONSES = [
    {
        "attack": (
            "This is collapse-porn; civilizations don't actually "
            "collapse through multiple tiers"
        ),
        "response": (
            "The Bronze Age collapse took the Eastern Mediterranean "
            "from palace-states with writing and long-distance trade "
            "to village-scale illiterate communities in a single "
            "generation. The Western Roman collapse took Britain from "
            "provincial urban civilization to village-scale within a "
            "century. Multi-tier collapse is historically documented. "
            "The question is whether current civilization is more or "
            "less vulnerable."
        ),
    },
    {
        "attack": (
            "Modern technology substitutes for atrophied functions; "
            "we don't need village-scale food production because we "
            "have industrial agriculture"
        ),
        "response": (
            "Industrial agriculture is a nation-scale coordination "
            "system. The claim is about what happens when nation-scale "
            "coordination fails. If village-scale food production is "
            "atrophied, there is no fallback. Technology that depends "
            "on the coordination layer does not substitute for the "
            "coordination layer."
        ),
    },
    {
        "attack": (
            "Firms outsource functions because it's efficient; this "
            "analysis is anti-efficiency"
        ),
        "response": (
            "Efficiency is a measurement that fails signal criteria "
            "(see efficiency audit). Outsourcing may reduce measured "
            "cost while increasing collapse vulnerability. The "
            "analysis does not prescribe against outsourcing; it "
            "measures the collapse consequence. A firm can choose to "
            "accept that vulnerability. The measurement makes the "
            "choice explicit rather than hidden."
        ),
    },
    {
        "attack": (
            "The atrophy scores for current civilization are "
            "subjective and pessimistic"
        ),
        "response": (
            "The scores are parameterized and falsifiable. If they are "
            "wrong, the module provides the structure for correcting "
            "them: assess each function at each scale with evidence. "
            "The claim that they are pessimistic is itself a "
            "falsifiable claim about the state of the world."
        ),
    },
    {
        "attack": (
            "This is just prepper ideology in academic language"
        ),
        "response": (
            "The module makes no prescriptions about what individuals "
            "or firms should do. It measures collapse propensity given "
            "observed atrophy. The measurement is independent of any "
            "particular response. Prepper ideology prescribes a "
            "specific response (individual stockpiling). This module "
            "prescribes nothing."
        ),
    },
    {
        "attack": (
            "Recovery time estimates are arbitrary; we don't know how "
            "long rebuilding takes"
        ),
        "response": (
            "The estimates are order-of-magnitude heuristics, labeled "
            "as such. The core claim is that multi-tier collapse "
            "requires longer recovery than single-tier collapse. The "
            "exact multiplier is less important than the direction "
            "and the mechanism. If better data exists, the parameter "
            "can be updated."
        ),
    },
]


# ===========================================================================
# Part 8. Rendering and integration

# ===========================================================================

def render_collapse_depth_table() -> str:
    """Render collapse depth estimates for each trigger scale under
    current atrophy assumptions."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("COLLAPSE DEPTH ESTIMATES: CURRENT CIVILIZATION")
    lines.append("=" * 80)
    lines.append("")
    header = (
        f"{'trigger scale':16s}  {'tiers lost':>10s}  "
        f"{'surviving':12s}  {'recovery (gen)':>14s}"
    )
    lines.append(header)
    lines.append("-" * len(header))

    for scale in SCALE_ORDER:
        if scale in (ScaleTier.BAND, ScaleTier.CLAN):
            continue  # can't collapse from smallest scales
        estimate = current_civilization_collapse_depth(scale)
        lines.append(
            f"{scale.value:16s}  {estimate.tiers_lost:10d}  "
            f"{estimate.surviving_scale.value:12s}  "
            f"{estimate.recovery_generations:14d}"
        )

    lines.append("")
    lines.append("Critical atrophied functions by trigger scale:")
    lines.append("")
    for scale in SCALE_ORDER:
        if scale in (ScaleTier.BAND, ScaleTier.CLAN):
            continue
        estimate = current_civilization_collapse_depth(scale)
        if estimate.critical_atrophied_functions:
            lines.append(
                f"  {scale.value}: "
                f"{', '.join(estimate.critical_atrophied_functions)}"
            )

    return "\n".join(lines)


def render_firm_collapse_table() -> str:
    """Render collapse depth for each firm archetype."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("FIRM COLLAPSE DEPTH BY ARCHETYPE")
    lines.append("=" * 80)
    lines.append("")

    for name, profile in FIRM_ARCHEYPES.items():
        estimate = estimate_firm_collapse_depth(profile)
        lines.append(f"--- {name} ---")
        lines.append(f"  trigger:     {estimate.trigger_layer.value}")
        lines.append(f"  surviving:   {estimate.surviving_layer.value}")
        lines.append(f"  layers lost: {estimate.layers_lost}")
        lines.append(f"  recovery:    {estimate.recovery_months} months")
        if estimate.critical_atrophied_functions:
            lines.append(
                f"  critical:    "
                f"{', '.join(estimate.critical_atrophied_functions)}"
            )
        if estimate.outsourced_vulnerabilities:
            lines.append(
                f"  outsourced:  "
                f"{', '.join(estimate.outsourced_vulnerabilities)}"
            )
        if estimate.financialized_vulnerabilities:
            lines.append(
                f"  financialized: "
                f"{', '.join(estimate.financialized_vulnerabilities)}"
            )
        lines.append(f"  rationale:   {estimate.rationale[:60]}...")
        lines.append("")

    return "\n".join(lines)


def metabolic_accounting_collapse_analog() -> str:
    """Explicit mapping from firm collapse to metabolic accounting
    cascade failures."""
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("METABOLIC ACCOUNTING: COLLAPSE MECHANISM ANALOG")
    lines.append("=" * 80)
    lines.append("")

    lines.append("Firm layer atrophy maps to cascade coupling:")
    lines.append("")
    lines.append("  OPERATOR substrate_awareness atrophied")
    lines.append("    -> basin degradation proceeds undetected")
    lines.append("    -> cascade failures surprise the firm")
    lines.append("")
    lines.append("  TEAM capacity_assessment atrophied (replaced by")
    lines.append("    credentialing)")
    lines.append("    -> wrong people assigned to wrong tasks")
    lines.append("    -> failures propagate rather than being caught")
    lines.append("")
    lines.append("  DEPARTMENT cross_team_coordination atrophied")
    lines.append("    -> teams work at cross-purposes")
    lines.append("    -> basin regeneration efforts are siloed and fail")
    lines.append("")
    lines.append("  FIRM failure_detection financialized")
    lines.append("    -> insurance and liability transfer replace")
    lines.append("       prevention")
    lines.append("    -> firm pays claims after collapse rather than")
    lines.append("       avoiding collapse")
    lines.append("")
    lines.append("An extractive firm with this atrophy profile will:")
    lines.append("  1. Extract until basin threshold crossed")
    lines.append("  2. Fail to detect crossing (operator awareness")
    lines.append("     atrophied)")
    lines.append("  3. Assign wrong response (capacity assessment")
    lines.append("     atrophied)")
    lines.append("  4. Coordinate poorly (cross-team atrophied)")
    lines.append("  5. File insurance claims after collapse")
    lines.append("     (failure detection financialized)")
    lines.append("")
    lines.append("The firm's collapse depth is proportional to how many")
    lines.append("of these substrate functions it has atrophied.")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(render_collapse_depth_table())
    print()
    print(render_firm_collapse_table())
    print()
    print(metabolic_accounting_collapse_analog())
    print()
    print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
    for p in FALSIFIABLE_PREDICTIONS[:3]:
        print(f"  [{p['id']}] {p['claim'][:70]}")
    print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
