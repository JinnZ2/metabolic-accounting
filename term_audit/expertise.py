“””
term_audit/audits/expertise.py

Audit of the term ‘expertise’ against signal-definition criteria,
separation into three distinct measurements, and four additional
scoring axes specific to institutional legitimacy terms:

cost_gating                does the credential gate by capacity or by
willingness-to-pay?
feedback_timescale         how fast does reality test the claim?
standard_setter_recursion  how many removes is the credentialing body
from the practice?
practitioner_representation are the people who do the work represented
in the body that credentials them?

These four axes extend the standard 7-criteria signal audit for use on
Tier 3 (organizational legitimacy) terms. They are reusable for
authority, accountability, governance, compliance, professionalism.

Core finding: ‘expertise’ as currently used collapses three distinct
measurements (E_A operational capacity, E_B credentialed status, E_C
transmission capacity) and the collapsed token is dominated by E_B,
which fails all four institutional-legitimacy axes in addition to
failing most signal criteria.

CC0. Stdlib only.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from term_audit.schema import (
TermAudit, SignalScore, StandardSetter, FirstPrinciplesPurpose,
)

# ===========================================================================

# Part 1. Institutional-legitimacy axes

# ===========================================================================

# 

# Standard signal criteria do not fully capture failure modes specific

# to institutional legitimacy terms. These four additional axes are

# scored alongside the seven standard criteria.

# —————————————————————————

INSTITUTIONAL_AXES = [
“cost_gating”,
“feedback_timescale”,
“standard_setter_recursion”,
“practitioner_representation”,
]

# Feedback timescale brackets

# 

# hourly     minutes to hours; immediate physical consequence

# daily      up to 24 hours; operational consequence within one cycle

# weekly     up to a week; team or cohort consequence

# monthly    quarterly earnings, policy administration

# annual     academic, legislative, bond-rating, credential-body

# generational  consequence of current practice becomes visible only

# after current staff has retired

FEEDBACK_TIMESCALES = [
(“hourly”, 0.95),                   # score: higher is better
(“daily”, 0.85),
(“weekly”, 0.65),
(“monthly”, 0.40),
(“annual”, 0.20),
(“generational”, 0.05),
]

@dataclass
class InstitutionalScore:
“”“Score on one institutional-legitimacy axis.”””
axis: str                           # one of INSTITUTIONAL_AXES
score: float                        # 0.0 failure, 1.0 full pass
justification: str
source_refs: List[str] = field(default_factory=list)

```
def __post_init__(self):
    if self.axis not in INSTITUTIONAL_AXES:
        raise ValueError(f"unknown axis: {self.axis}")
    if not 0.0 <= self.score <= 1.0:
        raise ValueError(f"score out of bounds: {self.score}")
```

# ===========================================================================

# Part 2. Audit of collapsed ‘expertise’

# ===========================================================================

COLLAPSED_EXPERTISE_AUDIT = TermAudit(
term=“expertise_collapsed_current_usage”,
claimed_signal=(
“high capacity in a domain, indicated by credentials, “
“experience, or recognition, treated as a single quantity”
),
standard_setters=[
StandardSetter(
name=“professional credentialing bodies “
“(medical boards, bar associations, engineering “
“societies, accreditation agencies)”,
authority_basis=(
“statutory monopoly over access to practice; self-”
“regulation”
),
incentive_structure=(
“maintain credential scarcity (higher prices, higher “
“prestige) and expand credential scope (more things “
“requiring the credential); neither incentive tracks “
“capacity”
),
independence_from_measured=0.1,
),
StandardSetter(
name=“credentialing universities and schools”,
authority_basis=“accreditation from bodies above”,
incentive_structure=(
“tuition-based revenue; incentive to expand enrollment “
“and increase credential cost; no direct feedback from “
“practice outcomes”
),
independence_from_measured=0.1,
),
StandardSetter(
name=“legislative bodies granting scope of practice”,
authority_basis=“statutory”,
incentive_structure=(
“typically captured by the credentialed profession “
“through lobbying; legislators rarely have capacity to “
“evaluate credential validity”
),
independence_from_measured=0.15,
),
StandardSetter(
name=“employers and managers”,
authority_basis=“hiring authority”,
incentive_structure=(
“credentials reduce hiring liability regardless of “
“whether they correlate with capacity; incentive to “
“use the credential as a filter even when it fails “
“to track capacity”
),
independence_from_measured=0.25,
),
StandardSetter(
name=“practicing practitioners (in the work daily)”,
authority_basis=“direct operational knowledge”,
incentive_structure=(
“incentive to correctly assess peer capacity because “
“lives, equipment, and operations depend on it; this “
“setter is routinely excluded from formal credentialing”
),
independence_from_measured=0.85,
),
],
signal_scores=[
SignalScore(
criterion=“scope_defined”,
score=0.15,
justification=(
“no bounded domain declared. ‘Expert’ is applied to a “
“surgeon, a statistician, a pundit, and a management “
“consultant without scope separation. These do not “
“share a referent.”
),
),
SignalScore(
criterion=“unit_invariant”,
score=0.1,
justification=(
“no units exist. ‘Expertise’ is a categorical assertion “
“with no measurable unit; two people called ‘expert’ “
“have no comparable quantity attached.”
),
),
SignalScore(
criterion=“referent_stable”,
score=0.2,
justification=(
“referent shifts silently between demonstrated capacity, “
“credentialed status, and public recognition. Same “
“token, different measurements.”
),
),
SignalScore(
criterion=“calibration_exists”,
score=0.2,
justification=(
“no calibration procedure maps the term to operational “
“outcomes. Credentialing procedures calibrate to other “
“credentialing procedures (recursion), not to practice.”
),
),
SignalScore(
criterion=“observer_invariant”,
score=0.3,
justification=(
“within a credentialing pipeline, observers agree. “
“Across pipelines and against operational outcomes, “
“observers routinely disagree.”
),
),
SignalScore(
criterion=“conservation_or_law”,
score=0.1,
justification=(
“no conservation structure. Credentials can be granted, “
“revoked, expanded, contracted by regulatory fiat “
“without reference to operational capacity.”
),
),
SignalScore(
criterion=“falsifiability”,
score=0.2,
justification=(
“the collapsed term is not falsifiable because the “
“referent can be silently relocated. A credentialed “
“expert who fails operationally is still credentialed; “
“an uncredentialed practitioner who succeeds “
“operationally is still not an expert by the term’s “
“usage.”
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
“identify who can reliably perform a task in a domain, so “
“that task allocation and advice-seeking can be directed “
“to people with capacity”
),
physical_referent=(
“demonstrated operational capacity to perform the work “
“under realistic conditions with reproducible outcomes”
),
informational_referent=(
“conditional probability of task success given the person, “
“task, and conditions”
),
drift_score=0.85,
drift_justification=(
“drifts from ‘demonstrated capacity’ to ‘credentialed “
“status’, which is an indirect proxy whose correlation “
“with capacity is mediated by cost-gating, recursion, and “
“capture. The drift reverses the direction of the “
“measurement in cases where credential pipelines select “
“for willingness-to-pay rather than capacity.”
),
),
correlation_to_real_signal=0.35,
correlation_justification=(
“weakly correlated with operational capacity across most “
“domains; correlation strongest in hourly-feedback technical “
“domains (surgery, aviation) where credentialing is continuously “
“re-tested against practice, weakest in annual-feedback domains “
“(policy, finance, management) where credentialing is never “
“re-tested”
),
notes=(
“collapsed expertise fails 7 of 7 signal criteria. It is the “
“keystone failure of Tier 3 (organizational legitimacy). “
“Authority, leadership, accountability, governance, compliance, “
“professionalism, and best practices all inherit from it.”
),
)

# ===========================================================================

# Part 3. E_A — demonstrated operational capacity

# ===========================================================================

E_A_AUDIT = TermAudit(
term=“expertise_A_operational_capacity”,
claimed_signal=(
“demonstrated ability to perform a specified task under “
“realistic conditions, reproducibly, across representative “
“cases”
),
standard_setters=[
StandardSetter(
name=“practicing practitioners in the same domain”,
authority_basis=“direct operational knowledge”,
incentive_structure=(
“must correctly assess peer capacity because lives, “
“equipment, and operations depend on it”
),
independence_from_measured=0.9,
),
StandardSetter(
name=“operational outcomes (the work itself)”,
authority_basis=“physical reality”,
incentive_structure=(
“reality does not have incentives; it provides “
“feedback”
),
independence_from_measured=0.95,
),
StandardSetter(
name=“direct beneficiaries of the work (patients, “
“clients, co-workers downstream)”,
authority_basis=“first-person experience of work outcome”,
incentive_structure=(
“aligned with accurate assessment; incentive weakened “
“when outcomes are delayed or displaced”
),
independence_from_measured=0.75,
),
],
signal_scores=[
SignalScore(
criterion=“scope_defined”,
score=0.85,
justification=(
“scope bounded by task, conditions, and case set”
),
),
SignalScore(
criterion=“unit_invariant”,
score=0.7,
justification=(
“within a task, units are well-defined (success rate, “
“error rate, completion time, durability of output)”
),
),
SignalScore(
criterion=“referent_stable”,
score=0.8,
justification=(
“the referent (task success under conditions) is “
“stable; shifts across tasks as expected for a “
“task-specific measurement”
),
),
SignalScore(
criterion=“calibration_exists”,
score=0.75,
justification=(
“calibration procedures exist in most domains: “
“apprenticeship review, operational testing, “
“outcome-audited peer review”
),
),
SignalScore(
criterion=“observer_invariant”,
score=0.75,
justification=(
“two practicing practitioners reviewing the same work “
“agree within documented tolerance”
),
),
SignalScore(
criterion=“conservation_or_law”,
score=0.5,
justification=(
“capacity is constrained by physical substrate (body, “
“equipment, environment); decays without practice; “
“this is not a conservation law but a substrate “
“dynamic”
),
),
SignalScore(
criterion=“falsifiability”,
score=0.9,
justification=(
“strongly falsifiable: give the person the task under “
“the conditions and observe whether they can do it”
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
“identify people who can actually perform the work”
),
physical_referent=(
“observable task performance”
),
informational_referent=(
“conditional probability of task success”
),
drift_score=0.2,
drift_justification=(
“minimal drift when measured directly. Drift occurs when “
“E_A is inferred from E_B rather than observed directly.”
),
),
correlation_to_real_signal=0.9,
correlation_justification=(
“high correlation when measured directly through operational “
“testing; this is what the measurement is supposed to be”
),
notes=(
“E_A is the measurement that actually answers the first-”
“principles question. It is systematically underweighted in “
“the collapsed token because practitioner-domain assessors are “
“rarely the formal standard-setters.”
),
)

# ===========================================================================

# Part 4. E_B — credentialed status

# ===========================================================================

E_B_AUDIT = TermAudit(
term=“expertise_B_credentialed_status”,
claimed_signal=(
“passage through a recognized certification pipeline indicating “
“completion of specified training and examinations”
),
standard_setters=[
StandardSetter(
name=“professional credentialing bodies”,
authority_basis=“statutory monopoly”,
incentive_structure=(
“maintain credential scarcity and expand credential “
“scope”
),
independence_from_measured=0.1,
),
StandardSetter(
name=“accredited universities and schools”,
authority_basis=“accreditation from credentialing bodies”,
incentive_structure=(
“tuition-based revenue; recursive accreditation”
),
independence_from_measured=0.1,
),
StandardSetter(
name=“examination boards”,
authority_basis=“delegated authority from credentialing “
“bodies”,
incentive_structure=(
“exam design drifts toward what is cheap to test, not “
“what correlates with practice capacity”
),
independence_from_measured=0.15,
),
],
signal_scores=[
SignalScore(
criterion=“scope_defined”,
score=0.7,
justification=(
“scope defined within a specific credential; “
“credential X from body Y issued in year Z”
),
),
SignalScore(
criterion=“unit_invariant”,
score=0.5,
justification=(
“credentials are categorical, not continuous; ‘has “
“credential X’ is binary”
),
),
SignalScore(
criterion=“referent_stable”,
score=0.5,
justification=(
“referent is stable only if the credentialing body’s “
“standards are stable; standards drift over decades “
“without notice”
),
),
SignalScore(
criterion=“calibration_exists”,
score=0.35,
justification=(
“calibration is recursive (credential bodies calibrate “
“to other credential bodies); not calibrated against “
“operational outcomes”
),
),
SignalScore(
criterion=“observer_invariant”,
score=0.85,
justification=(
“two observers can easily verify whether a person “
“holds a given credential; agreement is high on “
“credential possession itself”
),
),
SignalScore(
criterion=“conservation_or_law”,
score=0.2,
justification=(
“no conservation; credentials can be granted and “
“revoked by regulatory action without reference to “
“capacity”
),
),
SignalScore(
criterion=“falsifiability”,
score=0.6,
justification=(
“falsifiable as a claim about credential possession “
“(easily verified); not falsifiable as a claim about “
“operational capacity”
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
“originally: provide a low-cost proxy for operational “
“capacity in cases where direct assessment is expensive”
),
physical_referent=(
“none directly; credentials are informational claims”
),
informational_referent=(
“claim of passage through a specified pipeline”
),
drift_score=0.8,
drift_justification=(
“drifts from ‘low-cost proxy for capacity’ to ‘primary “
“measure of capacity’, which reverses the logical “
“structure. A proxy is only valid if its correlation with “
“the underlying measurement is maintained. Credentialing “
“systems do not audit this correlation; they assume it.”
),
),
correlation_to_real_signal=0.4,
correlation_justification=(
“correlation with E_A varies by domain. High in domains with “
“hourly operational feedback (aviation). Moderate in domains “
“with daily feedback (surgery). Low in domains with annual or “
“longer feedback (policy, management, finance, academic “
“research).”
),
notes=(
“E_B is a valid signal for one narrow question (did this “
“person complete this pipeline) and an invalid signal for the “
“broader question (does this person have capacity) that it is “
“usually invoked to answer.”
),
)

# ===========================================================================

# Part 5. E_C — transmission capacity

# ===========================================================================

E_C_AUDIT = TermAudit(
term=“expertise_C_transmission_capacity”,
claimed_signal=(
“ability to teach the skill to others such that the learner “
“acquires demonstrable operational capacity”
),
standard_setters=[
StandardSetter(
name=“successful learners and their subsequent “
“practice outcomes”,
authority_basis=“first-person demonstration of acquired “
“capacity”,
incentive_structure=(
“aligned with accurate assessment of teacher quality”
),
independence_from_measured=0.8,
),
StandardSetter(
name=“apprenticeship and craft traditions”,
authority_basis=“long-standing domain practice”,
incentive_structure=(
“aligned when the craft’s survival depends on “
“transmission; captured when transmission becomes “
“incidental to revenue”
),
independence_from_measured=0.65,
),
StandardSetter(
name=“universities and schools”,
authority_basis=“accreditation”,
incentive_structure=(
“revenue is decoupled from transmission outcomes; “
“payment happens regardless of whether the student “
“acquires operational capacity”
),
independence_from_measured=0.2,
),
],
signal_scores=[
SignalScore(
criterion=“scope_defined”,
score=0.75,
justification=(
“scope bounded by the skill, the learner population, “
“and the transmission conditions”
),
),
SignalScore(
criterion=“unit_invariant”,
score=0.6,
justification=(
“units are learner-outcome measures (acquisition rate, “
“retention rate, downstream practice success)”
),
),
SignalScore(
criterion=“referent_stable”,
score=0.75,
justification=(
“referent is stable when transmission outcomes are “
“measured longitudinally on learners”
),
),
SignalScore(
criterion=“calibration_exists”,
score=0.6,
justification=(
“calibration is possible through learner-outcome “
“tracking; rarely done systematically”
),
),
SignalScore(
criterion=“observer_invariant”,
score=0.6,
justification=(
“moderate agreement when learner outcomes are measured “
“on the same protocol”
),
),
SignalScore(
criterion=“conservation_or_law”,
score=0.4,
justification=(
“transmission capacity decays without practice; “
“substrate dynamic rather than conservation law”
),
),
SignalScore(
criterion=“falsifiability”,
score=0.85,
justification=(
“strongly falsifiable: measure learner capacity after “
“transmission, compare to capacity before”
),
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
“ensure that domain capacity persists across generations “
“by transmitting skill from practitioners to new learners”
),
physical_referent=(
“observable acquisition of capacity by learners”
),
informational_referent=(
“rate of capacity transmission per teacher-learner pairing”
),
drift_score=0.35,
drift_justification=(
“drifts when transmission capacity is inferred from “
“credentialing rather than measured by learner outcomes. “
“A credentialed ‘instructor’ whose learners do not acquire “
“capacity still scores as an expert transmitter under the “
“collapsed usage.”
),
),
correlation_to_real_signal=0.7,
correlation_justification=(
“correlation with actual transmission outcomes is high when “
“measured directly through learner tracking; drops when “
“inferred from credential possession or course delivery “
“rather than acquisition”
),
notes=(
“E_C is orthogonal to E_A and E_B. High E_A does not imply “
“high E_C; many capable practitioners cannot teach. High E_B “
“does not imply high E_C; credentials do not track “
“transmission outcomes. E_C must be measured directly.”
),
)

# ===========================================================================

# Part 6. Institutional-legitimacy scoring for each variant

# ===========================================================================

COLLAPSED_INSTITUTIONAL_SCORES = [
InstitutionalScore(
axis=“cost_gating”,
score=0.15,
justification=(
“credentials routinely require tens to hundreds of “
“thousands of dollars in tuition, opportunity cost, and “
“time. Cost selects for willingness-to-pay, which “
“correlates with class background, which has near-zero “
“correlation with operational capacity. Cost-gating is “
“therefore a negative-quality filter, not a positive one.”
),
),
InstitutionalScore(
axis=“feedback_timescale”,
score=0.25,
justification=(
“credentialing feedback loops operate on generational “
“timescales. A credential’s failure to track capacity “
“becomes visible after decades of practice, by which time “
“the institutional structure that produced the credential “
“has changed staff and no longer feels the feedback.”
),
),
InstitutionalScore(
axis=“standard_setter_recursion”,
score=0.15,
justification=(
“credentialing bodies are typically accredited by other “
“credentialing bodies, accredited by still other bodies, “
“with the bottom of the recursion usually a legislative “
“body or industry coalition that does not practice. “
“Recursion depth is commonly 3-5 levels removed from “
“practice.”
),
),
InstitutionalScore(
axis=“practitioner_representation”,
score=0.2,
justification=(
“credentialing bodies are staffed primarily by former “
“practitioners who no longer practice, by academics who “
“study the domain without doing the work, or by “
“administrators. Currently-practicing practitioners are “
“rarely in decision-making positions.”
),
),
]

E_A_INSTITUTIONAL_SCORES = [
InstitutionalScore(
axis=“cost_gating”,
score=0.8,
justification=(
“operational capacity is acquired through practice; cost “
“gating is minimal. Practice time is the resource, not “
“tuition. Some equipment costs apply in some domains but “
“do not dominate.”
),
),
InstitutionalScore(
axis=“feedback_timescale”,
score=0.85,
justification=(
“E_A is measured on the timescale of the task itself: “
“hourly to daily for most operational work. Feedback is “
“immediate and constraining.”
),
),
InstitutionalScore(
axis=“standard_setter_recursion”,
score=0.85,
justification=(
“E_A’s standard-setters are practicing practitioners and “
“operational outcomes. Recursion depth is zero: the “
“measurement is made directly against practice.”
),
),
InstitutionalScore(
axis=“practitioner_representation”,
score=0.9,
justification=(
“E_A is assessed by practicing practitioners assessing “
“peer capacity; representation is near-total.”
),
),
]

E_B_INSTITUTIONAL_SCORES = [
InstitutionalScore(
axis=“cost_gating”,
score=0.1,
justification=(
“cost gating is the primary filter; medical school, law “
“school, engineering accreditation, graduate school all “
“cost sums that eliminate candidates based on class “
“background rather than capacity”
),
),
InstitutionalScore(
axis=“feedback_timescale”,
score=0.2,
justification=(
“credentialing feedback is generational; individual “
“credentials are rarely re-evaluated against practice “
“outcomes”
),
),
InstitutionalScore(
axis=“standard_setter_recursion”,
score=0.1,
justification=(
“deep recursion; credentialing bodies accredit universities “
“which grant credentials which are recognized by employers “
“who require the credential because the credentialing “
“body says so”
),
),
InstitutionalScore(
axis=“practitioner_representation”,
score=0.2,
justification=(
“practitioners with strong E_A but no E_B are structurally “
“excluded from credentialing body governance”
),
),
]

E_C_INSTITUTIONAL_SCORES = [
InstitutionalScore(
axis=“cost_gating”,
score=0.55,
justification=(
“transmission capacity is acquired through teaching “
“practice; cost gating is moderate when transmission “
“happens inside credentialed institutions (tuition-paid “
“teaching positions) and low when it happens in “
“apprenticeship or craft traditions”
),
),
InstitutionalScore(
axis=“feedback_timescale”,
score=0.6,
justification=(
“feedback timescale depends on when learner outcomes are “
“measured; weekly to monthly during training, annual “
“through practice outcomes”
),
),
InstitutionalScore(
axis=“standard_setter_recursion”,
score=0.6,
justification=(
“moderate recursion in formal education systems; zero “
“recursion in apprenticeship where the teacher’s “
“transmission is measured directly against learner “
“capacity”
),
),
InstitutionalScore(
axis=“practitioner_representation”,
score=0.55,
justification=(
“mixed: apprenticeship traditions have high practitioner “
“representation; formal education has low representation “
“in curriculum design”
),
),
]

# ===========================================================================

# Part 7. Linkage analysis

# ===========================================================================

@dataclass
class ExpertiseLinkage:
source: str
target: str
relation: str
mechanism: str
conditions: str
falsification_test: str
strength_estimate: float
strength_justification: str

EXPERTISE_LINKAGES = [
ExpertiseLinkage(
source=“E_A”, target=“E_B”,
relation=“conditional”,
mechanism=(
“operational capacity can lead to credentialing when the “
“credentialing pipeline is accessible to the practitioner “
“(time, cost, prior access). Many practitioners with high “
“E_A never acquire E_B because the pipeline filters them “
“out at cost or access barriers.”
),
conditions=(
“practitioner has time, cost, and prior access to enter “
“the credentialing pipeline”
),
falsification_test=(
“sample practitioners by E_A score; measure E_B acquisition “
“rate across economic strata; show no correlation with “
“economic access”
),
strength_estimate=0.3,
strength_justification=(
“weak positive; high E_A does not reliably produce E_B “
“because pipeline access is the dominant filter”
),
),
ExpertiseLinkage(
source=“E_B”, target=“E_A”,
relation=“conditional”,
mechanism=(
“credentialing pipelines include some practice, but “
“capacity acquisition is a function of practice hours “
“and feedback quality more than pipeline completion”
),
conditions=(
“credentialing pipeline includes substantial supervised “
“practice with outcome feedback”
),
falsification_test=(
“measure E_A before and after credentialing in matched “
“candidates; decompose E_A gain into pipeline-practice “
“and non-pipeline-practice components”
),
strength_estimate=0.35,
strength_justification=(
“weak positive; credentials produce some E_A but are a “
“poor substitute for practice hours”
),
),
ExpertiseLinkage(
source=“credential_cost”, target=“E_A”,
relation=“negative”,
mechanism=(
“high credential cost filters candidates by willingness-”
“to-pay, which correlates with class background, which “
“has near-zero correlation with operational capacity. “
“The filter actively removes high-E_A candidates who “
“lack cost access.”
),
conditions=(
“credential cost is high relative to candidate resources”
),
falsification_test=(
“measure E_A distribution in candidates excluded by cost; “
“show it is not systematically higher than in candidates “
“who paid the cost”
),
strength_estimate=-0.4,
strength_justification=(
“moderate negative; the measurement system selects “
“against exactly the candidates who would score highest “
“on the thing the measurement claims to track”
),
),
ExpertiseLinkage(
source=“E_A”, target=“E_C”,
relation=“none”,
mechanism=(
“operational capacity does not imply transmission capacity; “
“many highly capable practitioners cannot teach”
),
conditions=“always”,
falsification_test=(
“measure E_A and E_C in the same population; show strong “
“positive correlation”
),
strength_estimate=0.15,
strength_justification=(
“near-zero; E_A and E_C are largely orthogonal”
),
),
ExpertiseLinkage(
source=“E_B”, target=“E_C”,
relation=“none”,
mechanism=(
“credential possession does not imply transmission “
“capacity; credentialed ‘instructors’ are not selected “
“on learner-outcome data”
),
conditions=“always”,
falsification_test=(
“correlate credential status with learner-outcome metrics”
),
strength_estimate=0.1,
strength_justification=“near-zero”,
),
ExpertiseLinkage(
source=“feedback_timescale”, target=“capture_risk”,
relation=“negative”,
mechanism=(
“shorter feedback loops constrain claimed capacity to “
“track actual capacity; longer feedback loops allow “
“claimed capacity to drift from actual capacity without “
“correction”
),
conditions=“always, across all institutional legitimacy terms”,
falsification_test=(
“rank domains by feedback timescale; measure capture “
“severity; show no negative correlation”
),
strength_estimate=-0.75,
strength_justification=(
“strong negative; this is the primary mechanism by which “
“institutional legitimacy terms become captured”
),
),
]

# ===========================================================================

# Part 8. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
“id”: 1,
“claim”: (
“E_B and E_A are weakly correlated; correlation strength “
“depends on domain feedback timescale, with hourly-feedback “
“domains showing the highest correlation and annual-”
“feedback domains the lowest”
),
“falsification”: (
“measure E_A and E_B across domains of varying feedback “
“timescales; show no dependence on timescale”
),
},
{
“id”: 2,
“claim”: (
“credential cost negatively correlates with the E_A “
“distribution of people who obtain the credential”
),
“falsification”: (
“measure E_A in cost-gated and non-cost-gated pathways; “
“show cost-gated pathways produce higher E_A”
),
},
{
“id”: 3,
“claim”: (
“institutional-legitimacy capture severity correlates “
“positively with feedback timescale and standard-setter “
“recursion depth”
),
“falsification”: (
“rank Tier 3 terms by both variables; measure capture “
“severity; show weak or no correlation”
),
},
{
“id”: 4,
“claim”: (
“practitioner-representation scores are systematically “
“lower in credentialing bodies than in operational teams “
“performing the same domain work”
),
“falsification”: (
“measure representation in both; show parity or reverse”
),
},
{
“id”: 5,
“claim”: (
“decisions made by high-E_B low-E_A actors about operations “
“performed by low-E_B high-E_A actors produce systematic “
“operational degradation relative to decisions made by “
“practicing peers”
),
“falsification”: (
“compare operational outcomes across decision authorities; “
“show no systematic difference”
),
},
{
“id”: 6,
“claim”: (
“apprenticeship and craft-tradition transmission produces “
“higher E_C and E_A per unit time and cost than formal “
“credentialing pipelines”
),
“falsification”: (
“measure E_A and E_C acquisition rates in matched “
“apprenticeship and formal-education cohorts; show formal “
“education produces higher rates”
),
},
{
“id”: 7,
“claim”: (
“across Tier 3 terms, those with higher cost-gating scores “
“show lower correlation to operational outcomes”
),
“falsification”: (
“apply the institutional-legitimacy scoring to all Tier 3 “
“terms; measure outcome correlation; show no pattern”
),
},
]

# ===========================================================================

# Part 9. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
“attack”: (
“credentials exist because direct assessment of capacity “
“is expensive; without credentials we have no efficient “
“way to identify experts”
),
“response”: (
“credentials were originally proxies for capacity. A “
“proxy is valid only if its correlation with the “
“underlying quantity is audited and maintained. “
“Credentialing bodies do not audit this correlation; they “
“assume it. The efficiency argument collapses if the “
“proxy has drifted from the referent, which this audit “
“documents. Efficient identification of the wrong thing “
“is not efficient.”
),
},
{
“attack”: (
“practitioners with high E_A but no E_B exist but are “
“rare; the credentialing system captures most capable “
“practitioners”
),
“response”: (
“this is an empirical claim that requires data. The claim “
“that non-credentialed high-E_A practitioners are rare is “
“usually made by observers who have never looked for them “
“because the credentialing pipeline is their exclusive “
“search space. Practitioner-domain populations (skilled “
“trades, nomadic knowledge holders, veteran operators, “
“self-taught craftspeople) are substantial and “
“systematically underrepresented in credentialing data.”
),
},
{
“attack”: (
“operational outcomes are the ultimate test, but they are “
“slow and noisy; credentialing is the available shortcut”
),
“response”: (
“operational outcomes are slow only in annual-feedback “
“domains. In hourly-feedback domains they are near-”
“instantaneous. The argument works in the narrow case “
“(academia, policy, finance) and fails in the broad case “
“(trades, medicine, aviation, operations). The response “
“is domain-specific: use the feedback loop the domain “
“provides, not a universal credentialing shortcut.”
),
},
{
“attack”: (
“cost-gating exists because quality education costs money; “
“removing it would lower capacity”
),
“response”: (
“this conflates capacity acquisition (which costs “
“practice time and sometimes equipment) with credential “
“acquisition (which costs tuition, exam fees, and lost “
“income during full-time study). Apprenticeship and “
“on-the-job practice produce capacity at much lower cost. “
“The argument defends tuition economics, not capacity “
“development.”
),
},
{
“attack”: (
“the practitioner-domain assessors you cite are subjective “
“and inconsistent”
),
“response”: (
“practitioner-domain assessors evaluate against “
“operational reality. Their assessments are as consistent “
“as the reality they assess. Credentialing assessors “
“evaluate against other credentialing standards; their “
“consistency is internal to the pipeline and unanchored “
“to operational reality. The ‘subjectivity’ attack misses “
“which assessor is anchored to external fact.”
),
},
{
“attack”: (
“some domains (medicine, aviation) genuinely require “
“credentialing to protect the public”
),
“response”: (
“public-protection credentialing is defensible in exactly “
“those domains and only to the extent that the credential “
“tracks E_A. The audit does not argue against credentials; “
“it argues against treating credentials as a substitute “
“for capacity assessment. In medicine and aviation, “
“credentials are continuously re-tested against “
“operational outcomes, which is why their E_B-to-E_A “
“correlation is higher than in unchecked domains.”
),
},
{
“attack”: (
“separating E_A, E_B, E_C is impractical for hiring, “
“promotion, and regulatory decisions”
),
“response”: (
“the current practice collapses them by default and “
“applies hidden weights. The separation exposes the “
“weights and allows them to be chosen explicitly. “
“Impracticality here means ‘requires explicit choice where “
“hidden choice was previously made’, which is a feature.”
),
},
{
“attack”: (
“this argument is made by non-credentialed people seeking “
“to elevate themselves”
),
“response”: (
“the argument is made by anyone measuring institutional “
“legitimacy against operational outcomes. Whether the “
“person making the argument is credentialed does not “
“change whether the measurement framework is valid. This “
“attack relocates the debate from measurement validity “
“to speaker identity, which is the ad hominem form of “
“the capture defense.”
),
},
]

# ===========================================================================

# Part 10. Summary

# ===========================================================================

def institutional_summary(
audit_name: str,
scores: List[InstitutionalScore],
) -> Dict:
total = sum(s.score for s in scores) / len(scores) if scores else 0.0
return {
“audit”: audit_name,
“mean_institutional_score”: total,
“per_axis”: {s.axis: s.score for s in scores},
}

def collapsed_usage_diagnosis() -> Dict:
return {
“term”: “expertise_collapsed_current_usage”,
“claim”: (
“one word denoting operational capacity, credentialed “
“status, and transmission capacity as if they were one “
“measurement”
),
“failure”: (
“three referents with different signal properties fused “
“into one token. E_B dominates the fusion because “
“credentialing infrastructure produces E_B measurements “
“continuously, at low marginal cost once the infrastructure “
“exists. E_A is assumed to follow from E_B. E_C is rarely “
“measured at all.”
),
“consequence”: (
“decisions about who can do work, who can make decisions, “
“and who can be trusted are routed through a measurement “
“that fails all seven signal criteria and all four “
“institutional-legitimacy axes. High-E_A practitioners “
“without E_B are structurally excluded. Decisions get “
“made by high-E_B low-E_A actors about operations they “
“cannot perform.”
),
“remediation”: (
“report E_A (operational capacity, directly measured), “
“E_B (credential status, acknowledged as narrow), and “
“E_C (transmission capacity, measured on learner “
“outcomes) independently. Anchor authority in E_A, not “
“E_B. Audit credential bodies against their correlation “
“with E_A, not against other credential bodies.”
),
}

ALL_EXPERTISE_AUDITS = {
“collapsed”: COLLAPSED_EXPERTISE_AUDIT,
“E_A_operational”: E_A_AUDIT,
“E_B_credentialed”: E_B_AUDIT,
“E_C_transmission”: E_C_AUDIT,
}

EXPERTISE_INSTITUTIONAL_SCORES = {
“collapsed”: COLLAPSED_INSTITUTIONAL_SCORES,
“E_A_operational”: E_A_INSTITUTIONAL_SCORES,
“E_B_credentialed”: E_B_INSTITUTIONAL_SCORES,
“E_C_transmission”: E_C_INSTITUTIONAL_SCORES,
}

if **name** == “**main**”:
import json

```
print("=== collapsed expertise audit ===")
print(json.dumps(COLLAPSED_EXPERTISE_AUDIT.summary(), indent=2))
print()

print("=== separated audits ===")
for key, audit in ALL_EXPERTISE_AUDITS.items():
    if key == "collapsed":
        continue
    print(f"--- {key} ---")
    print(json.dumps(audit.summary(), indent=2))
    print()

print("=== institutional-legitimacy scores ===")
for key, scores in EXPERTISE_INSTITUTIONAL_SCORES.items():
    print(
        json.dumps(institutional_summary(key, scores), indent=2)
    )
    print()

print("=== linkages ===")
for link in EXPERTISE_LINKAGES:
    print(f"  {link.source:22s} -> {link.target:18s}  "
          f"({link.relation:11s}, "
          f"strength={link.strength_estimate:+.2f})")
print()

print("=== collapsed-usage diagnosis ===")
print(json.dumps(collapsed_usage_diagnosis(), indent=2))
print()

print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
```
