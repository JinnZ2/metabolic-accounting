"""
term_audit/systemic_necessity.py

Horizontal measurement tool for systemic necessity and alternative
availability. Applies across Tier 3 (institutional legitimacy) and
Tier 7 (environmental) terms, and to any measurement that ranks or
compensates roles.

Core claim: formal authority and compensation in modern organizations
are systematically anti-correlated with systemic necessity. Roles
whose removal would cause rapid irreversible system collapse receive
less authority, less compensation, and less formal status than roles
whose removal would cause disruption but adaptive recovery.

Three sub-measurements kept separate:

function_necessity         what happens if the function itself
disappears? measures the function, not
the current role arrangement
role_arrangement_necessity is the current role arrangement the only
viable way to provide the function, or
are there alternatives?
alternative_availability   do viable alternatives exist, and what
structural forces affect their
availability?

The combination exposes where current arrangements are *captured*:
function is necessary, role-arrangement is not, alternatives exist
but face structural suppression.

This module is consumed by expertise, authority, accountability,
leadership, governance, and environmental term audits.

CC0. Stdlib only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# ===========================================================================

# Part 1. Scoring scales

# ===========================================================================

# 

# function_necessity scale:

# 

# 0.0  removing the function has no effect; the function is fictional

# or purely status-producing

# 0.2  removing the function degrades non-essential services;

# adaptive recovery within weeks

# 0.4  removing the function causes significant disruption;

# recovery within months

# 0.6  removing the function threatens system integrity; recovery

# requires years of reconstruction

# 0.8  removing the function causes rapid system failure;

# recovery uncertain within a generation

# 1.0  removing the function causes catastrophic irreversible

# collapse; recovery requires multi-generational reconstruction

# or is impossible

# 

# role_arrangement_necessity scale:

# 

# 0.0  current role arrangement is one of many viable ways to

# provide the function; alternatives are operational elsewhere

# already

# 0.2  current arrangement has alternatives that require moderate

# restructuring

# 0.4  current arrangement has alternatives that require significant

# restructuring but are feasible

# 0.6  current arrangement has alternatives that require system-

# level change to implement

# 0.8  current arrangement has limited alternatives; some functions

# may be irreducible to a single person-shaped role

# 1.0  current role arrangement is the only known viable way to

# provide the function

# 

# alternative_availability scale:

# 

# 0.0  no viable alternatives exist; current arrangement is

# technically irreducible

# 0.2  alternatives theoretically possible but not demonstrated

# 0.4  alternatives demonstrated at small scale; face significant

# scaling barriers

# 0.6  alternatives operating at scale in some contexts; partial

# adoption possible

# 0.8  alternatives operating at scale; structural forces suppress

# broader adoption

# 1.0  alternatives exist, are viable, and are actively suppressed

# by capture mechanisms

# -------------------------

class CollapseTimescale(Enum):
    """Timescale over which function removal produces visible system
    degradation."""
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    GENERATIONS = "generations"
    NEVER = "never"             # function is not actually necessary

@dataclass
class RemovalAnalysis:
    """Thought-experiment analysis of removing a role or function."""
    role_or_function: str
    collapse_timescale: CollapseTimescale
    primary_failure_modes: List[str]
    cascade_effects: List[str]
    recovery_timescale: str     # free-form, includes 'never', 'decades',
    # 'years', 'months', 'weeks'
    reversibility: float        # 0.0 fully irreversible, 1.0 fully
    # reversible
    population_at_risk: str     # free-form: 'local', 'regional',
    # 'national', 'global', 'generational'

@dataclass
class AlternativeArrangement:
    """A viable alternative way to provide a function."""
    description: str
    current_deployment_scale: str   # 'none', 'small', 'regional',
    # 'national', 'global', 'historical'
    structural_barriers: List[str]
    examples: List[str] = field(default_factory=list)

@dataclass
class NecessityProfile:
    """Systemic-necessity profile for a role or function."""
    role_or_function: str
    function_necessity: float
    role_arrangement_necessity: float
    alternative_availability: float
    removal_analysis: RemovalAnalysis
    alternatives: List[AlternativeArrangement]
    notes: str = ""

    def captured_score(self) -> float:
        """
        Captured score: function_necessity is high, role_arrangement_
        necessity is low, alternative_availability is high.

        A high captured score indicates the current arrangement is
        maintained not because it is the only way but because
        alternatives face structural suppression.
        """
        f = self.function_necessity
        r = 1.0 - self.role_arrangement_necessity
        a = self.alternative_availability
        return (f * r * a) ** (1.0/3.0)  # geometric mean

    def irreducibility_score(self) -> float:
        """
        Irreducibility score: function is necessary AND no viable
        alternatives exist.

        A high irreducibility score indicates the current arrangement
        is genuinely necessary and cannot be replaced without causing
        the function itself to fail.
        """
        f = self.function_necessity
        r = self.role_arrangement_necessity
        a = 1.0 - self.alternative_availability
        return (f * r * a) ** (1.0/3.0)

    def dispensability_score(self) -> float:
        """
        Dispensability score: function is not particularly necessary
        and alternatives exist easily.

        A high dispensability score indicates the role could be
        removed or replaced with minimal system disruption.
        """
        f = 1.0 - self.function_necessity
        a = self.alternative_availability
        return (f * a) ** 0.5

# ===========================================================================

# Part 2. Reference role profiles

# ===========================================================================

REFERENCE_PROFILES = [
NecessityProfile(
role_or_function="hazmat_long_haul_driver",
function_necessity=0.95,
role_arrangement_necessity=0.4,
alternative_availability=0.7,
removal_analysis=RemovalAnalysis(
role_or_function="hazmat long-haul driver",
collapse_timescale=CollapseTimescale.DAYS,
primary_failure_modes=[
"food distribution failure to non-rail-served regions",
"medical supply delivery failure",
"fuel distribution breakdown",
"agricultural input delivery stoppage",
],
cascade_effects=[
"hospital non-operation within 5-7 days",
"grocery supply exhaustion within 3-5 days",
"fuel exhaustion within 10-14 days",
"livestock feed interruption within days",
],
recovery_timescale="weeks-to-months if alternatives "
"deployed; catastrophic otherwise",
reversibility=0.3,
population_at_risk="regional-to-national",
),
alternatives=[
AlternativeArrangement(
description="shorter relay-corridor trucking with "
"more drivers working fewer hours",
current_deployment_scale="historical",
structural_barriers=[
"capital ownership of tractor-trailer equipment",
"deregulation favoring long-haul consolidation",
"just-in-time inventory requirements",
],
examples=["pre-deregulation US trucking"],
),
AlternativeArrangement(
description="expanded rail network with intermodal "
"last-mile delivery",
current_deployment_scale="regional",
structural_barriers=[
"private rail ownership resistance to shared "
"infrastructure",
"terminal capacity limitations",
"last-mile connection investment",
],
),
AlternativeArrangement(
description="regional food and supply systems",
current_deployment_scale="small",
structural_barriers=[
"agricultural consolidation",
"retail consolidation",
"distribution infrastructure built for "
"long-haul",
],
),
],
notes=(
"function is catastrophically necessary. Current role "
"arrangement (70-hour weeks, long corridors, single-driver "
"operation) is not the only viable form; alternatives "
"exist at small scale and historical precedent."
),
),
NecessityProfile(
role_or_function="nurse_icu",
function_necessity=0.95,
role_arrangement_necessity=0.55,
alternative_availability=0.4,
removal_analysis=RemovalAnalysis(
role_or_function="ICU nurse",
collapse_timescale=CollapseTimescale.HOURS,
primary_failure_modes=[
"loss of continuous patient monitoring",
"medication administration interruption",
"deterioration detection failure",
"clinical response to emergencies",
],
cascade_effects=[
"patient mortality within hours",
"hospital closure of acute care within 24 hours",
],
recovery_timescale="immediate crisis; training "
"replacements requires 2-4 years",
reversibility=0.1,
population_at_risk="patients in acute care",
),
alternatives=[
AlternativeArrangement(
description="community health workers plus family "
"caregivers with professional support",
current_deployment_scale="small",
structural_barriers=[
"hospital financial model requires licensed "
"nurse billable hours",
"liability regime",
"professional credentialing monopoly",
],
examples=["rural hospice care models",
"some indigenous community health systems"],
),
AlternativeArrangement(
description="higher staffing ratios with shorter "
"shifts reducing substrate burn",
current_deployment_scale="small",
structural_barriers=[
"hospital administrator budget decisions",
"insurance reimbursement structures",
],
),
],
notes=(
"function critically necessary. Role arrangement can be "
"moderately restructured (staffing ratios, shift length) "
"but the direct-care function itself is hard to "
"eliminate."
),
),
NecessityProfile(
role_or_function="farmer",
function_necessity=1.0,
role_arrangement_necessity=0.3,
alternative_availability=0.8,
removal_analysis=RemovalAnalysis(
role_or_function="farmer",
collapse_timescale=CollapseTimescale.MONTHS,
primary_failure_modes=[
"food production stops at end of current growing "
"season",
"seed stock maintenance ends",
"livestock breeding and care ends",
],
cascade_effects=[
"global food supply collapse within one year",
"mass starvation within 2 years",
"irrecoverable loss of landrace seed stocks and "
"breed lines",
],
recovery_timescale="decades for knowledge reconstruction; "
"centuries for soil and seed recovery",
reversibility=0.05,
population_at_risk="global",
),
alternatives=[
AlternativeArrangement(
description="decentralized smallholder agriculture "
"with regional specialization",
current_deployment_scale="historical, small",
structural_barriers=[
"agricultural consolidation since 1940s",
"commodity crop subsidy structure",
"land tenure concentration",
"machinery capital requirements",
],
),
AlternativeArrangement(
description="urban and peri-urban food production",
current_deployment_scale="small",
structural_barriers=[
"zoning",
"water access",
"soil remediation needs",
],
),
AlternativeArrangement(
description="indigenous food systems with "
"landscape-encoded knowledge transmission",
current_deployment_scale="historical, localized",
structural_barriers=[
"land access",
"knowledge transmission disruption",
"legal recognition",
],
),
],
notes=(
"function is existentially necessary. Industrial-scale "
"farmer role arrangement is one of many possible forms; "
"alternatives demonstrated at smaller scales, widely "
"suppressed by capital and policy structure."
),
),
NecessityProfile(
role_or_function="soil_microbiologist_or_ecological_monitor",
function_necessity=0.9,
role_arrangement_necessity=0.3,
alternative_availability=0.75,
removal_analysis=RemovalAnalysis(
role_or_function="soil microbiologists and ecological "
"monitors",
collapse_timescale=CollapseTimescale.YEARS,
primary_failure_modes=[
"early warning signals of ecological degradation "
"stop being recorded",
"cascade failures become invisible until thresholds "
"cross",
"restoration baselines lost",
],
cascade_effects=[
"substrate depletion proceeds without detection",
"recovery interventions delayed or misdirected",
"Holocene-regime model assumptions fail undetected",
],
recovery_timescale="decades to rebuild monitoring "
"infrastructure",
reversibility=0.4,
population_at_risk="global, multi-generational",
),
alternatives=[
AlternativeArrangement(
description="indigenous knowledge transmission with "
"landscape-encoded observation systems",
current_deployment_scale="historical, localized",
structural_barriers=[
"legal recognition",
"knowledge transmission disruption",
"academic non-recognition",
],
),
AlternativeArrangement(
description="farmer and land-operator observation "
"networks",
current_deployment_scale="small",
structural_barriers=[
"non-credentialed observations not accepted in "
"regulatory or academic contexts",
"no institutional infrastructure to aggregate",
],
),
AlternativeArrangement(
description="distributed citizen-science networks "
"with standardized protocols",
current_deployment_scale="small to regional",
structural_barriers=[
"funding favors credentialed research",
"data validation skepticism",
],
),
],
notes=(
"function is critical for long-horizon survival. "
"Current academic-credentialed role arrangement is one "
"form; alternatives with lower substrate cost exist."
),
),
NecessityProfile(
role_or_function="nuclear_plant_operator",
function_necessity=0.85,
role_arrangement_necessity=0.9,
alternative_availability=0.2,
removal_analysis=RemovalAnalysis(
role_or_function="nuclear plant operator",
collapse_timescale=CollapseTimescale.DAYS,
primary_failure_modes=[
"reactor management without qualified operators",
"fuel cycle management breakdown",
"decommissioning management",
"waste handling",
],
cascade_effects=[
"plant shutdown with unmanaged fuel cycle",
"long-term containment risks",
"decommissioning delayed indefinitely",
],
recovery_timescale="training pipeline is 5-10 years "
"minimum",
reversibility=0.4,
population_at_risk="regional-to-continental, "
"multi-generational",
),
alternatives=[
AlternativeArrangement(
description="phasing out nuclear with replacement "
"generation",
current_deployment_scale="regional",
structural_barriers=[
"replacement capacity timeline",
"decommissioning still requires operators",
],
),
],
notes=(
"function irreducibly necessary while reactors operate. "
"Role arrangement genuinely difficult to substitute. "
"This is one of the few roles with high irreducibility."
),
),
NecessityProfile(
role_or_function="hazmat_firefighter",
function_necessity=0.9,
role_arrangement_necessity=0.55,
alternative_availability=0.5,
removal_analysis=RemovalAnalysis(
role_or_function="hazmat firefighter",
collapse_timescale=CollapseTimescale.HOURS,
primary_failure_modes=[
"no response to chemical incidents",
"cascading industrial accidents uncontained",
],
cascade_effects=[
"population exposure to released materials",
"infrastructure damage spreads",
"subsequent incidents lack containment model",
],
recovery_timescale="training is 2-5 years; team "
"formation longer",
reversibility=0.3,
population_at_risk="incident-local to regional",
),
alternatives=[
AlternativeArrangement(
description="industrial self-response teams with "
"mutual aid agreements",
current_deployment_scale="small, historical",
structural_barriers=[
"liability regime favors outsourcing",
"public-service model captures funding",
],
),
],
notes=(
"function necessary where hazmat transport and storage "
"occur. Alternatives possible but current arrangement "
"is difficult to replace quickly."
),
),
NecessityProfile(
role_or_function="structural_engineer_in_field",
function_necessity=0.85,
role_arrangement_necessity=0.4,
alternative_availability=0.65,
removal_analysis=RemovalAnalysis(
role_or_function="structural engineer",
collapse_timescale=CollapseTimescale.YEARS,
primary_failure_modes=[
"new construction design fails safety standards",
"existing infrastructure inspection ends",
"bridge and building maintenance uncontrolled",
],
cascade_effects=[
"infrastructure failures accumulate",
"new construction stops",
"retrofit decisions made without analysis",
],
recovery_timescale="5-10 years for credentialing pipeline",
reversibility=0.5,
population_at_risk="users of built environment",
),
alternatives=[
AlternativeArrangement(
description="master-builder traditions with "
"apprenticeship-based engineering "
"knowledge",
current_deployment_scale="historical",
structural_barriers=[
"credentialing monopoly",
"liability regime",
"building codes require licensed sign-off",
],
),
],
notes=(
"function necessary. Current credentialing pipeline is "
"one form; historical master-builder traditions "
"performed the same function with lower cost-gating."
),
),
NecessityProfile(
role_or_function="corporate_executive",
function_necessity=0.2,
role_arrangement_necessity=0.1,
alternative_availability=0.9,
removal_analysis=RemovalAnalysis(
role_or_function="corporate executive",
collapse_timescale=CollapseTimescale.MONTHS,
primary_failure_modes=[
"strategic decisions delayed",
"capital allocation frozen temporarily",
"some firms fail, others adapt",
],
cascade_effects=[
"employees self-organize around immediate work",
"customer service continues",
"production continues",
"new strategic initiatives paused",
],
recovery_timescale="months for firms that adapt; "
"immediate for operational staff",
reversibility=0.9,
population_at_risk="limited; mostly firm-internal",
),
alternatives=[
AlternativeArrangement(
description="cooperative and employee-owned "
"structures with elected or rotating "
"leadership",
current_deployment_scale="regional",
structural_barriers=[
"securities law favors executive-led corporations",
"credit availability favors traditional "
"structures",
"investor expectations",
],
examples=["Mondragon Corporation", "many European "
"cooperatives", "John Lewis Partnership"],
),
AlternativeArrangement(
description="flat hierarchies with professional "
"self-management",
current_deployment_scale="small",
structural_barriers=[
"scaling past Dunbar-number limits",
"capital provider expectations",
],
examples=["Valve Corporation", "some engineering "
"firms"],
),
AlternativeArrangement(
description="public ownership with elected "
"management boards",
current_deployment_scale="historical, regional",
structural_barriers=[
"privatization policy trajectory",
"public-service disinvestment",
],
),
],
notes=(
"function largely coordination and symbolic; many "
"viable alternative arrangements exist at various "
"scales. Current arrangement maintained by capital "
"ownership structure and legal form, not by "
"functional necessity."
),
),
NecessityProfile(
role_or_function="hospital_administrator",
function_necessity=0.3,
role_arrangement_necessity=0.2,
alternative_availability=0.85,
removal_analysis=RemovalAnalysis(
role_or_function="hospital administrator",
collapse_timescale=CollapseTimescale.WEEKS,
primary_failure_modes=[
"scheduling becomes self-organized",
"budget decisions delayed",
"compliance paperwork accumulates",
"strategic planning pauses",
],
cascade_effects=[
"clinical work continues",
"patient care continues",
"nursing self-organizes shift coverage",
],
recovery_timescale="weeks to months for administrative "
"restructuring",
reversibility=0.95,
population_at_risk="minimal during transition",
),
alternatives=[
AlternativeArrangement(
description="clinician-led governance with rotating "
"administrative duties",
current_deployment_scale="historical",
structural_barriers=[
"hospital financial model",
"insurance billing complexity favors "
"specialized administrators",
"regulatory compliance burden",
],
examples=["pre-1970s teaching hospitals",
"some rural hospitals"],
),
AlternativeArrangement(
description="patient-council and staff-council "
"co-governance",
current_deployment_scale="small",
structural_barriers=[
"ownership structures",
"liability",
],
),
],
notes=(
"coordination function has alternatives. Current "
"administrator role is largely a response to "
"billing complexity and regulatory burden, both of "
"which could be restructured."
),
),
NecessityProfile(
role_or_function="logistics_vp",
function_necessity=0.25,
role_arrangement_necessity=0.15,
alternative_availability=0.9,
removal_analysis=RemovalAnalysis(
role_or_function="logistics VP",
collapse_timescale=CollapseTimescale.WEEKS,
primary_failure_modes=[
"strategic logistics decisions delayed",
"some route optimization paused",
],
cascade_effects=[
"drivers and dispatchers continue routing",
"customers continue ordering",
"deliveries continue",
],
recovery_timescale="immediate for operational work; "
"months for strategic decisions",
reversibility=0.95,
population_at_risk="minimal",
),
alternatives=[
AlternativeArrangement(
description="driver-cooperative ownership with "
"elected dispatch coordinators",
current_deployment_scale="small, historical",
structural_barriers=[
"capital requirements for fleet ownership",
"customer contracts favor consolidated carriers",
],
examples=["independent owner-operator networks"],
),
AlternativeArrangement(
description="algorithmic dispatch with "
"practitioner oversight",
current_deployment_scale="growing",
structural_barriers=[
"who controls the algorithm",
"who defines the objective function",
],
),
],
notes=(
"function has many alternatives. Current role "
"arrangement exists because capital structure "
"concentrates ownership and routing authority."
),
),
NecessityProfile(
role_or_function="policy_architect",
function_necessity=0.35,
role_arrangement_necessity=0.2,
alternative_availability=0.85,
removal_analysis=RemovalAnalysis(
role_or_function="policy architect",
collapse_timescale=CollapseTimescale.YEARS,
primary_failure_modes=[
"new policy innovation slows",
"existing policies continue through institutional "
"inertia",
],
cascade_effects=[
"regulatory updates delayed",
"some coordination problems accumulate",
],
recovery_timescale="months to years",
reversibility=0.85,
population_at_risk="diffuse, slow",
),
alternatives=[
AlternativeArrangement(
description="practitioner-written regulation with "
"expert legal drafting support",
current_deployment_scale="small, historical",
structural_barriers=[
"lobbying infrastructure favors captured "
"policy architects",
"academic-policy revolving door",
],
examples=["many trade guild traditions",
"some indigenous governance systems"],
),
AlternativeArrangement(
description="direct democracy with technical "
"drafting assistance",
current_deployment_scale="regional",
structural_barriers=[
"representative-government constitutional "
"structure",
"voter information infrastructure",
],
examples=["Swiss canton-level governance"],
),
AlternativeArrangement(
description="consensus and customary law with "
"dispute-resolution panels",
current_deployment_scale="historical",
structural_barriers=[
"statutory preemption",
"legal profession capture",
],
),
],
notes=(
"function has many alternatives in historical record "
"and in current small-scale deployment. Current role "
"arrangement maintained by legislative-lobbying "
"capture."
),
),
NecessityProfile(
role_or_function="central_bank_governor",
function_necessity=0.4,
role_arrangement_necessity=0.15,
alternative_availability=0.85,
removal_analysis=RemovalAnalysis(
role_or_function="central bank governor",
collapse_timescale=CollapseTimescale.MONTHS,
primary_failure_modes=[
"monetary policy discretion paused",
"rate decisions delayed",
],
cascade_effects=[
"commercial banks continue lending",
"payment systems continue",
"fiscal policy steps in or not",
],
recovery_timescale="months",
reversibility=0.9,
population_at_risk="limited short-term",
),
alternatives=[
AlternativeArrangement(
description="rule-based monetary policy (Taylor "
"rule, NGDP targeting) with minimal "
"discretion",
current_deployment_scale="proposed",
structural_barriers=[
"central bank institutional interests",
],
),
AlternativeArrangement(
description="commodity-based or distributed-issuance "
"monetary systems",
current_deployment_scale="historical, small",
structural_barriers=[
"legal tender laws",
"tax denomination",
"international reserve conventions",
],
),
AlternativeArrangement(
description="public-banking networks with "
"democratic oversight",
current_deployment_scale="small",
structural_barriers=[
"financial-sector capture of policy",
],
),
],
notes=(
"current role arrangement serves incumbent financial "
"structure. Many alternatives for providing payment "
"coordination and credit allocation exist."
),
),
NecessityProfile(
role_or_function="academic_researcher",
function_necessity=0.4,
role_arrangement_necessity=0.2,
alternative_availability=0.8,
removal_analysis=RemovalAnalysis(
role_or_function="academic researcher (in current form)",
collapse_timescale=CollapseTimescale.GENERATIONS,
primary_failure_modes=[
"formal peer-reviewed knowledge production slows",
"graduate student training pipeline interrupts",
],
cascade_effects=[
"applied-field research continues through "
"practitioner communities",
"independent scholars and open-source research "
"networks continue",
"knowledge transmission shifts to non-academic "
"channels",
],
recovery_timescale="slow decades",
reversibility=0.8,
population_at_risk="diffuse, slow",
),
alternatives=[
AlternativeArrangement(
description="practitioner-scholar communities "
"with open publication",
current_deployment_scale="small to regional",
structural_barriers=[
"funding structure favors academic institutions",
"credentialing requirements for certain fields",
],
examples=["many programming communities",
"traditional ecological knowledge "
"networks", "open-source research"],
),
AlternativeArrangement(
description="guild-style knowledge production with "
"apprenticeship",
current_deployment_scale="historical",
structural_barriers=[
"professionalization of research",
"journal-based credentialing",
],
),
AlternativeArrangement(
description="citizen-science networks",
current_deployment_scale="growing",
structural_barriers=[
"data validation skepticism",
"publication gatekeeping",
],
),
],
notes=(
"knowledge production function is moderately "
"necessary. Current academic role arrangement is one "
"of many possible forms; alternatives exist in "
"practitioner communities and historical guild "
"traditions."
),
),
NecessityProfile(
role_or_function="financial_services_worker",
function_necessity=0.3,
role_arrangement_necessity=0.1,
alternative_availability=0.95,
removal_analysis=RemovalAnalysis(
role_or_function="derivatives and secondary-market "
"financial services worker",
collapse_timescale=CollapseTimescale.MONTHS,
primary_failure_modes=[
"derivatives markets pause",
"secondary-market liquidity contracts",
"some clearing functions disrupted",
],
cascade_effects=[
"direct bank transfers and payment systems continue",
"primary credit markets (loans, mortgages) continue "
"with simpler instruments",
"commodity markets continue with simpler contracts",
"some price discovery slowed",
],
recovery_timescale="months for essential functions; "
"years for complex instruments",
reversibility=0.95,
population_at_risk="limited; financial-sector internal",
),
alternatives=[
AlternativeArrangement(
description="mutual banks, credit unions, and "
"cooperative finance with direct "
"lender-borrower relationships",
current_deployment_scale="regional",
structural_barriers=[
"regulatory capture by large banks",
"scale disadvantages in capital formation",
],
examples=["Raiffeisen networks", "many US credit "
"unions"],
),
AlternativeArrangement(
description="community currencies and mutual credit "
"networks",
current_deployment_scale="small",
structural_barriers=[
"legal tender laws",
"tax accounting",
],
examples=["WIR Bank in Switzerland"],
),
AlternativeArrangement(
description="public banking for payment and credit",
current_deployment_scale="regional, historical",
structural_barriers=[
"privatization trajectory",
"financial-sector lobbying",
],
examples=["Bank of North Dakota", "postal banking "
"systems"],
),
],
notes=(
"most derivatives and secondary-market functions are "
"not systemically necessary. Primary banking (deposit, "
"payment, credit) has extensive alternatives. Current "
"arrangement maintained by capture of policy and "
"regulation."
),
),
]

# ===========================================================================

# Part 3. Cross-role analysis

# ===========================================================================

@dataclass
class NecessityInversionPair:
    """Two roles where authority/compensation is inverted relative to
    systemic necessity."""
    high_necessity_role: str
    low_necessity_role: str
    necessity_gap: float
    description: str

def detect_necessity_inversions(
    profiles: List[NecessityProfile],
    structural_pairs: List[Tuple[str, str]],
    ) -> List[NecessityInversionPair]:
    """
    For each structural pair (exposed_or_necessary, insulated_or_
    dispensable), check whether the organizational authority is
    inverted relative to function necessity.

    structural_pairs entries are (high_necessity_role,
    low_necessity_role) expected from organizational hierarchy.
    """
    profile_map = {p.role_or_function: p for p in profiles}
    pairs: List[NecessityInversionPair] = []

    for high_name, low_name in structural_pairs:
        if high_name not in profile_map or low_name not in profile_map:
            continue
        high = profile_map[high_name]
        low = profile_map[low_name]

        gap = high.function_necessity - low.function_necessity
        if gap > 0:
            pairs.append(NecessityInversionPair(
                high_necessity_role=high_name,
                low_necessity_role=low_name,
                necessity_gap=gap,
                description=(
                    f"{high_name} has function_necessity "
                    f"{high.function_necessity:.2f}; "
                    f"{low_name} has {low.function_necessity:.2f}. "
                    f"Typical organizational hierarchy places "
                    f"{low_name} in authority over {high_name}."
                ),
            ))
    return pairs

KNOWN_NECESSITY_INVERSION_PAIRS = [
("hazmat_long_haul_driver", "logistics_vp"),
("hazmat_long_haul_driver", "corporate_executive"),
("nurse_icu", "hospital_administrator"),
("nurse_icu", "corporate_executive"),
("farmer", "corporate_executive"),
("farmer", "policy_architect"),
("hazmat_firefighter", "policy_architect"),
("structural_engineer_in_field", "corporate_executive"),
("soil_microbiologist_or_ecological_monitor", "corporate_executive"),
("soil_microbiologist_or_ecological_monitor", "policy_architect"),
]

# ===========================================================================

# Part 4. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
"id": 1,
"claim": (
"roles with highest function_necessity scores receive "
"lower formal authority and compensation-per-substrate-"
"cost than roles with lowest function_necessity scores"
),
"falsification": (
"rank roles by function_necessity; measure authority "
"and compensation-per-substrate-cost; show positive "
"correlation"
),
},
{
"id": 2,
"claim": (
"high captured_score roles (high necessity, high "
"alternative availability, low role-arrangement "
"necessity) are maintained through structural "
"suppression of alternatives, not through functional "
"irreplaceability"
),
"falsification": (
"document that alternatives to high captured_score "
"roles do not face structural suppression"
),
},
{
"id": 3,
"claim": (
"roles with highest irreducibility scores (genuinely "
"cannot be replaced) are a small subset of roles "
"currently commanding high status"
),
"falsification": (
"show that high-status roles are disproportionately "
"irreducible"
),
},
{
"id": 4,
"claim": (
"removal thought experiments on high-status roles "
"(executive, administrator, financial services, policy "
"architect) produce substantially smaller cascade "
"effects than removal of low-status operational roles"
),
"falsification": (
"find high-status roles whose removal produces cascade "
"effects comparable to removal of farmers, drivers, "
"nurses, or operators"
),
},
{
"id": 5,
"claim": (
"alternative arrangements for coordination-layer roles "
"(executive, administrator, policy architect) are more "
"available than alternatives for substrate-layer roles "
"(farmer, driver, nurse, operator)"
),
"falsification": (
"document equal alternative availability across layers"
),
},
{
"id": 6,
"claim": (
"the combination of high consequence_exposure (from "
"consequence_accounting) and high function_necessity "
"(from this module) identifies the roles most "
"inverted by current measurement systems, and those "
"roles cluster in substrate layers"
),
"falsification": (
"show that high-exposure high-necessity roles are "
"distributed across all organizational layers"
),
},
{
"id": 7,
"claim": (
"roles with high alternative_availability have this "
"score precisely because alternatives exist and are "
"demonstrated, not because the role is easily "
"discontinued"
),
"falsification": (
"show roles with high alternative_availability lack "
"demonstrated alternatives"
),
},
]

# ===========================================================================

# Part 5. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
"attack": (
"removal thought experiments are speculative; we cannot "
"actually know what would happen if a role disappeared"
),
"response": (
"natural experiments exist for most roles: strikes, "
"pandemic absences, historical transitions, regional "
"variations. The 2020-2022 period produced removal "
"experiments on most operational roles. The experiments "
"are not speculative; they are poorly documented."
),
},
{
"attack": (
"the claim that executive function is replaceable "
"ignores the value of strategic vision"
),
"response": (
"strategic vision is a distinct claim from coordinating "
"function. The function_necessity score separates them. "
"Coordination is replaceable by various arrangements. "
"Strategic vision is rarely tested in a way that "
"distinguishes executive input from organizational "
"momentum; many firms survive long executive transitions "
"without visible strategic failure."
),
},
{
"attack": (
"alternatives that 'exist at small scale' do not prove "
"they would work at scale"
),
"response": (
"alternative_availability is scored across current "
"deployment scale. Historical precedents at national "
"scale are noted separately. The argument that "
"alternatives cannot scale is empirical, not logical, "
"and usually made by observers with stakes in the "
"current arrangement. Mondragon operates at substantial "
"scale; Swiss canton governance operates at national "
"scale; public banking has operated at state scale."
),
},
{
"attack": (
"measuring systemic necessity by removal thought "
"experiments is anti-progress; all roles build on each "
"other"
),
"response": (
"the module measures necessity of specific roles in "
"specific current arrangements. It does not deny "
"interdependence. It isolates which components of the "
"arrangement are functionally necessary from which "
"components are structurally maintained. Both can be "
"true: interdependence is real, and current arrangements "
"are captured."
),
},
{
"attack": (
"this framework would justify eliminating high-status "
"roles, which would produce chaos"
),
"response": (
"the module does not recommend elimination; it measures "
"necessity. Discovering that a role is dispensable is "
"not a policy recommendation. It is information about "
"the current arrangement. Policy decisions require "
"additional inputs including transition planning, "
"sequence, and replacement-system development. The "
"measurement and the action are different."
),
},
{
"attack": (
"some roles with low function_necessity perform "
"important cultural or symbolic work"
),
"response": (
"cultural and symbolic functions are real. The module "
"can add a symbolic_or_cultural_necessity axis. The "
"current scoring focuses on material system function "
"because that is where measurement inversion causes "
"the most damage. Symbolic necessity does not make "
"material necessity false."
),
},
{
"attack": (
"the alternatives listed are idealized; in practice they "
"have failure modes the current arrangement avoids"
),
"response": (
"alternatives have failure modes. The current "
"arrangement has failure modes. The question is which "
"set of failure modes is preferable in which context. "
"The module documents alternatives as existing, not as "
"perfect. Comparative failure analysis is appropriate "
"and welcomed; the claim that current arrangements are "
"failure-free is the claim requiring evidence."
),
},
]

# ===========================================================================

# Part 6. Combined analysis with consequence_accounting

# ===========================================================================

def combined_ranking(
    profiles: List[NecessityProfile],
    ) -> List[Tuple[str, float]]:
    """
    Rank roles by combined necessity-and-inversion signal:
    function_necessity * captured_score.

    High values indicate roles that are functionally necessary AND
    whose current arrangement is captured. These are the roles where
    both measurement failure and systemic importance concentrate.
    """
    scored = []
    for p in profiles:
        combined = p.function_necessity * p.captured_score()
        scored.append((p.role_or_function, combined))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

# ===========================================================================

# Part 7. Rendering

# ===========================================================================

def render_profile_table(profiles: List[NecessityProfile]) -> str:
    lines: List[str] = []
    header = (
    f"{'role':42s}  "
    f"{'func':>5s}  "
    f"{'role':>5s}  "
    f"{'alt':>5s}  "
    f"{'capt':>5s}  "
    f"{'irred':>5s}  "
    f"{'disp':>5s}"
    )
    lines.append(header)
    lines.append(
    f"{'':42s}  "
    f"{'nec':>5s}  "
    f"{'nec':>5s}  "
    f"{'avail':>5s}  "
    f"{'ured':>5s}  "
    f"{'':>5s}  "
    f"{'':>5s}"
    )
    lines.append("-" * len(header))

    sorted_profiles = sorted(
    profiles,
    key=lambda p: p.function_necessity,
    reverse=True,
    )
    for p in sorted_profiles:
        lines.append(
            f"{p.role_or_function[:42]:42s}  "
            f"{p.function_necessity:5.2f}  "
            f"{p.role_arrangement_necessity:5.2f}  "
            f"{p.alternative_availability:5.2f}  "
            f"{p.captured_score():5.2f}  "
            f"{p.irreducibility_score():5.2f}  "
            f"{p.dispensability_score():5.2f}"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    print("=" * 80)
    print("SYSTEMIC NECESSITY: ROLE PROFILES")
    print("=" * 80)
    print()
    print(render_profile_table(REFERENCE_PROFILES))
    print()

    print("=" * 80)
    print("NECESSITY-INVERSION PAIRS")
    print("=" * 80)
    inversions = detect_necessity_inversions(
    REFERENCE_PROFILES,
    KNOWN_NECESSITY_INVERSION_PAIRS,
    )
    for inv in sorted(inversions, key=lambda i: i.necessity_gap,
                      reverse=True):
        print(
            f"  {inv.high_necessity_role[:34]:34s} "
            f"vs {inv.low_necessity_role[:22]:22s}  "
            f"gap={inv.necessity_gap:+.2f}"
        )
    print()

    print("=" * 80)
    print("COMBINED RANKING: function_necessity * captured_score")
    print("=" * 80)
    for role_name, score in combined_ranking(REFERENCE_PROFILES):
        print(f"  {role_name[:42]:42s}  {score:.3f}")
    print()

    print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
    for p in FALSIFIABLE_PREDICTIONS[:3]:
        print(f"  [{p['id']}] {p['claim'][:70]}")
    print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
