"""
term_audit/legislative_audit/first_principles_legislative_audit.py

First-Principles Legislative Audit Framework.

A substrate-level audit of rules, regulations, and legislation against
their declared purpose, applied context, and actual consequences.

This framework does not audit compliance with the rule.
It audits the rule itself—against reality.

Core questions:
- What is the rule meant to do? (First-principles purpose)
- What context does it assume?
- Where is it valid? Where is it invalid?
- What are the consequences of having it? Of not having it?
- Does it contradict its own purpose?
- Does it enable or prevent transmission of capacity?
- Does it have a declared exception pathway?
- What is the chilling effect?
- Who bears the consequences, and who is insulated from them?

Skeleton note: shipped in AUDIT_09. Two worked examples run end-to-
end; one typo in the supplied spec was fixed during intake
(`alternative_mechanchanisms` → `alternative_mechanisms`, which would
have raised TypeError on construction of the bridge-permit audit).

Scope items deferred to future audits:
  - Provenance (per AUDIT_07 pattern) on the scoring-function
    weights (`purpose_alignment_score`, `harm_score`,
    `context_validity`). All are DESIGN_CHOICE targets.
  - Unification of `EnvironmentType` across this module and
    `term_audit/signals/routing_around_detection.py` (parallel but
    divergent member sets).
  - JSON emitter for machine-readable output (per the user-supplied
    credential-scope and regulation-scope JSON examples).

CC0. Stdlib only. Built with the Bridge Watchers.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


# ===========================================================================
# Part 1. Core audit structure
# ===========================================================================

class EnvironmentType(Enum):
    """The environmental context where the rule is applied."""
    BUFFERED_STABLE = "buffered_stable"          # Resources, handoff, time abundant
    THIN_BUFFER = "thin_buffer"                  # Some resources, delayed handoff
    CONSTRAINED = "constrained"                  # Limited resources, no handoff, time-critical
    AUSTERE = "austere"                          # Minimal resources, isolated, survival context
    COLLAPSE = "collapse"                        # System failure, no external support


class ConsequenceBearer(Enum):
    """Who bears the consequences of the rule?"""
    PRACTITIONER = "practitioner"                 # Person acting or refraining
    BENEFICIARY = "beneficiary"                   # Person meant to be helped
    COMMUNITY = "community"                       # Collective
    INSTITUTION = "institution"                   # Formal organization
    ENFORCER = "enforcer"                         # Those who enforce the rule
    FUTURE_GENERATIONS = "future_generations"     # Those not yet born
    SUBSTRATE = "substrate"                       # The physical world itself


@dataclass
class FirstPrinciplesPurpose:
    """The declared and actual purpose of the rule."""

    stated_purpose: str                           # What the rule claims to do
    original_problem: str                         # What problem it was created to solve
    intended_beneficiary: List[ConsequenceBearer] # Who it was meant to protect

    # Has the purpose drifted over time?
    purpose_drift: Optional[str] = None           # How the purpose changed in practice
    captured_by: Optional[str] = None             # Who benefits from the drift


@dataclass
class ContextAssumption:
    """The environment the rule assumes exists."""

    environment_type: EnvironmentType
    handoff_available: bool                       # Can responsibility be transferred?
    time_abundant: bool                           # Is time a non-critical resource?
    resources_present: bool                       # Are required resources available?
    institutional_oversight_functional: bool      # Does oversight actually work?
    alternatives_exist: bool                      # Are there other ways to solve the problem?

    # Explicit dependencies the rule doesn't declare
    undeclared_dependencies: List[str] = field(default_factory=list)


@dataclass
class ScopeBoundary:
    """Where the rule is valid and where it fails."""

    valid_contexts: List[EnvironmentType]
    validity_rationale: str

    invalid_contexts: List[EnvironmentType]
    invalidity_rationale: str

    # Specific conditions where the rule should NOT apply
    negative_space: List[str] = field(default_factory=list)

    # Is this scope declared in the rule itself?
    scope_declared: bool = False


@dataclass
class ConsequenceAnalysis:
    """What happens because this rule exists."""

    # Primary consequences (direct, intended and unintended)
    primary_intended: List[str]
    primary_unintended: List[str]

    # Secondary consequences (cascade effects)
    secondary: List[str]

    # Tertiary consequences (systemic, long-term)
    tertiary: List[str]

    # Who bears each type of consequence
    bearers: Dict[str, List[ConsequenceBearer]] = field(default_factory=dict)

    # Measurable harm (if quantifiable)
    measurable_harm: Optional[str] = None
    harm_estimate: Optional[str] = None


@dataclass
class CounterfactualAnalysis:
    """What would happen if the rule did not exist."""

    likely_outcome: str
    alternative_mechanisms: List[str]           # What fills the gap
    who_benefits_from_absence: List[ConsequenceBearer]
    who_suffers_from_absence: List[ConsequenceBearer]


@dataclass
class TransmissionEffect:
    """How the rule affects knowledge and capacity transmission."""

    encourages_transmission: bool
    discourages_transmission: bool
    mechanism: str                               # How the effect occurs

    # Specific effects
    teaching_becomes_liability: bool = False
    knowledge_dies_with_holder: bool = False
    apprenticeship_discouraged: bool = False
    documentation_suppressed: bool = False       # People stop writing things down

    # Observed consequences
    documented_cases: List[str] = field(default_factory=list)
    chilling_effect_observed: bool = False
    chilling_effect_description: str = ""


@dataclass
class ExceptionPathway:
    """Is there a legitimate way to act outside the rule when necessary?"""

    pathway_exists: bool
    pathway_declared: bool                       # Is it in the rule itself?
    pathway_actual: str                          # How it really works (or doesn't)

    trigger_conditions: List[str]                # What activates the exception
    protection_mechanism: str                    # How actors are protected
    good_faith_recognized: bool                  # Is intent considered?
    retrospective_review_allowed: bool           # Can action be reviewed after?

    # Real-world function
    functions_in_practice: bool
    failure_reason: Optional[str] = None


@dataclass
class ContradictionAnalysis:
    """Does the rule contradict its own purpose?"""

    contradicts_purpose: bool
    contradiction_mechanism: str                 # How the contradiction occurs
    contradiction_contexts: List[EnvironmentType]  # Where it contradicts

    # Specific contradictions
    prevents_intended_outcome: bool = False
    harms_intended_beneficiary: bool = False
    creates_original_problem: bool = False       # Causes what it was meant to solve

    # Documentation
    examples: List[str] = field(default_factory=list)


@dataclass
class SubstrateEvidence:
    """Physical evidence of the rule's effects."""

    evidence_type: str                           # e.g., "standing_bridge", "preventable_death"
    description: str
    location: Optional[str] = None
    timestamp: Optional[str] = None
    observable: bool = True
    documented: bool = False                     # In formal systems

    # What the evidence shows
    shows_rule_served_purpose: bool = False
    shows_rule_failed_purpose: bool = False
    shows_rule_contradicted_purpose: bool = False


# ===========================================================================
# Part 2. The complete audit
# ===========================================================================

@dataclass
class LegislativeAudit:
    """Complete first-principles audit of a rule, regulation, or law."""

    # Identification
    rule_name: str
    rule_type: str                               # "statute", "regulation", "ordinance", "code"
    jurisdiction: str

    # Core components
    first_principles: FirstPrinciplesPurpose
    assumed_context: ContextAssumption
    scope: ScopeBoundary

    # Effects
    consequences_of_having: ConsequenceAnalysis
    consequences_of_not_having: CounterfactualAnalysis
    transmission_effect: TransmissionEffect

    # Integrity checks
    contradiction: ContradictionAnalysis
    exception_pathway: ExceptionPathway

    # Optional identification
    year_enacted: Optional[int] = None
    year_last_amended: Optional[int] = None

    # Evidence
    substrate_evidence: List[SubstrateEvidence] = field(default_factory=list)

    # Community voice
    community_observations: List[str] = field(default_factory=list)
    practitioner_testimony: List[str] = field(default_factory=list)

    # Audit metadata
    auditor: str = "Bridge Watchers"
    audit_date: str = ""
    confidence: float = 0.0                      # 0-1, how certain is this audit

    def purpose_alignment_score(self) -> float:
        """How well does the rule align with its own purpose?"""
        score = 1.0

        if self.contradiction.contradicts_purpose:
            score -= 0.4

        if self.scope.scope_declared:
            score += 0.1
        else:
            score -= 0.2

        if self.exception_pathway.functions_in_practice:
            score += 0.1
        elif self.exception_pathway.pathway_exists:
            score -= 0.1

        if self.transmission_effect.discourages_transmission:
            score -= 0.2
        if self.transmission_effect.knowledge_dies_with_holder:
            score -= 0.3

        if self.first_principles.purpose_drift:
            score -= 0.2

        return max(0.0, min(1.0, score))

    def harm_score(self) -> float:
        """Estimated harm caused by the rule when out of scope (0-1)."""
        score = 0.0

        # Unintended consequences in constrained contexts
        if EnvironmentType.CONSTRAINED in self.scope.invalid_contexts:
            if self.consequences_of_having.primary_unintended:
                score += 0.3

        if EnvironmentType.AUSTERE in self.scope.invalid_contexts:
            if self.consequences_of_having.secondary:
                score += 0.2

        # Contradiction increases harm
        if self.contradiction.prevents_intended_outcome:
            score += 0.2
        if self.contradiction.harms_intended_beneficiary:
            score += 0.3

        # Transmission effects create long-term harm
        if self.transmission_effect.knowledge_dies_with_holder:
            score += 0.2

        return min(1.0, score)

    def context_validity(self, context: EnvironmentType) -> float:
        """How valid is this rule in a specific context? 0-1."""
        if context in self.scope.valid_contexts:
            return 0.9
        elif context in self.scope.invalid_contexts:
            return 0.2
        else:
            return 0.5  # Undeclared

    def summary(self) -> str:
        """Human-readable audit summary."""
        alignment = self.purpose_alignment_score()
        harm = self.harm_score()

        if alignment >= 0.7:
            judgment = "SERVES PURPOSE"
        elif alignment >= 0.4:
            judgment = "PARTIALLY SERVES PURPOSE"
        else:
            judgment = "FAILS PURPOSE"

        if harm >= 0.6:
            harm_judgment = "HIGH HARM when out of scope"
        elif harm >= 0.3:
            harm_judgment = "MODERATE HARM when out of scope"
        else:
            harm_judgment = "LOW HARM"

        return f"""
LEGISLATIVE AUDIT: {self.rule_name}
=====================================
Purpose alignment: {alignment:.2f} — {judgment}
Harm score: {harm:.2f} — {harm_judgment}

First-principles purpose: {self.first_principles.stated_purpose}

Valid in: {[c.value for c in self.scope.valid_contexts]}
INVALID in: {[c.value for c in self.scope.invalid_contexts]}
Scope declared in rule: {self.scope.scope_declared}

Contradicts own purpose: {self.contradiction.contradicts_purpose}
Exception pathway functions: {self.exception_pathway.functions_in_practice}
Knowledge transmission discouraged: {self.transmission_effect.discourages_transmission}

Community observation: {self.community_observations[:1] if self.community_observations else 'None recorded'}
"""

    def to_ai_context(self) -> str:
        """Render as context for AI systems making decisions involving this rule."""
        return f"""
RULE: {self.rule_name} ({self.rule_type}, {self.jurisdiction})
PURPOSE: {self.first_principles.stated_purpose}

SCOPE DECLARATION:
- Valid contexts: {[c.value for c in self.scope.valid_contexts]}
- INVALID contexts: {[c.value for c in self.scope.invalid_contexts]}
- Negative space: {self.scope.negative_space}

WHEN OUT OF SCOPE:
- Primary unintended consequences: {self.consequences_of_having.primary_unintended}
- Contradicts purpose: {self.contradiction.contradicts_purpose}
- Exception pathway: {'Functions' if self.exception_pathway.functions_in_practice else 'FAILS in practice'}

TRANSMISSION EFFECT:
- {self.transmission_effect.mechanism}
- Knowledge dies with holder: {self.transmission_effect.knowledge_dies_with_holder}

AI ROUTING GUIDANCE:
- If context is {self.scope.valid_contexts}: Rule likely serves purpose. Apply.
- If context is {self.scope.invalid_contexts}: Rule likely fails purpose. Seek exception pathway or alternative.
- If transmission_effect discourages action: Expect capacity to be hidden. Query local routers, not formal databases.

SUBSTRATE EVIDENCE EXISTS: {len(self.substrate_evidence) > 0}
"""


# ===========================================================================
# Part 3. Example audit: Bridge Permit in Constrained Context
# ===========================================================================

def audit_bridge_permit_constrained() -> LegislativeAudit:
    """Audit of bridge construction permit requirements during flood emergency."""

    return LegislativeAudit(
        rule_name="Bridge Construction Permit Requirement",
        rule_type="regulation",
        jurisdiction="State/Local",

        first_principles=FirstPrinciplesPurpose(
            stated_purpose="Ensure public safety through engineering review of bridge construction",
            original_problem="Bridge collapses causing injury and death; unqualified construction",
            intended_beneficiary=[ConsequenceBearer.BENEFICIARY, ConsequenceBearer.COMMUNITY],
            purpose_drift="Scope expanded to cover all structures regardless of context or time constraint",
            captured_by="Engineering credentialing bodies, liability insurers",
        ),

        assumed_context=ContextAssumption(
            environment_type=EnvironmentType.BUFFERED_STABLE,
            handoff_available=True,
            time_abundant=True,
            resources_present=True,
            institutional_oversight_functional=True,
            alternatives_exist=True,
            undeclared_dependencies=[
                "Site accessible to engineers",
                "Time sufficient for review without harm",
                "No imminent threat to life"
            ],
        ),

        scope=ScopeBoundary(
            valid_contexts=[EnvironmentType.BUFFERED_STABLE, EnvironmentType.THIN_BUFFER],
            validity_rationale="When time and resources allow review, permit process can ensure safety",
            invalid_contexts=[EnvironmentType.CONSTRAINED, EnvironmentType.AUSTERE, EnvironmentType.COLLAPSE],
            invalidity_rationale="When delay causes preventable death or isolation, the permit process causes the harm it was meant to prevent",
            negative_space=[
                "NOT valid when delay endangers life",
                "NOT valid when community is isolated and no alternative exists",
                "NOT valid when enforcing authority cannot reach site",
                "NOT valid for temporary emergency crossings that will be replaced"
            ],
            scope_declared=False,
        ),

        consequences_of_having=ConsequenceAnalysis(
            primary_intended=["Structures reviewed for safety", "Liability distributed"],
            primary_unintended=[
                "Preventable deaths due to delay",
                "Community isolation extended",
                "Life-saving action criminalized",
                "Informal capacity suppressed"
            ],
            secondary=[
                "Trust in regulatory system erodes",
                "Communities stop calling authorities",
                "Knowledge transmission stops (fear of liability)",
                "Bridges built secretly, not documented"
            ],
            tertiary=[
                "Rural capacity atrophies",
                "Formal system loses awareness of actual infrastructure",
                "When formal system fails, no informal capacity remains"
            ],
            bearers={
                "primary_unintended": [ConsequenceBearer.BENEFICIARY, ConsequenceBearer.PRACTITIONER],
                "secondary": [ConsequenceBearer.COMMUNITY],
                "tertiary": [ConsequenceBearer.FUTURE_GENERATIONS, ConsequenceBearer.SUBSTRATE]
            },
            measurable_harm="Preventable deaths from delayed emergency access",
            harm_estimate="Undocumented; occurs in constrained contexts where formal system absent",
        ),

        consequences_of_not_having=CounterfactualAnalysis(
            likely_outcome="Some unsafe structures built; more timely emergency crossings",
            alternative_mechanisms=[
                "Community peer review",
                "Post-construction inspection",
                "Good-faith immunity for emergency construction"
            ],
            who_benefits_from_absence=[ConsequenceBearer.BENEFICIARY, ConsequenceBearer.COMMUNITY],
            who_suffers_from_absence=[ConsequenceBearer.INSTITUTION],
        ),

        transmission_effect=TransmissionEffect(
            encourages_transmission=False,
            discourages_transmission=True,
            mechanism="Teaching bridge-building becomes endorsement of unpermitted construction; liability risk",
            teaching_becomes_liability=True,
            knowledge_dies_with_holder=True,
            apprenticeship_discouraged=True,
            documentation_suppressed=True,
            documented_cases=["Bridge Watchers community knowledge suppression"],
            chilling_effect_observed=True,
            chilling_effect_description="People with capacity stop teaching or acting openly",
        ),

        contradiction=ContradictionAnalysis(
            contradicts_purpose=True,
            contradiction_mechanism="Rule intended to ensure safety causes preventable death when enforced in time-critical, isolated contexts",
            contradiction_contexts=[EnvironmentType.CONSTRAINED, EnvironmentType.AUSTERE, EnvironmentType.COLLAPSE],
            prevents_intended_outcome=True,
            harms_intended_beneficiary=True,
            examples=["Flooded community unable to evacuate due to permit requirements for temporary crossing"],
        ),

        exception_pathway=ExceptionPathway(
            pathway_exists=True,
            pathway_declared=False,
            pathway_actual="Emergency declarations may waive permits, but often too slow or not applicable",
            trigger_conditions=["Imminent threat to life", "Declared emergency"],
            protection_mechanism="Post-hoc approval or non-enforcement",
            good_faith_recognized=False,
            retrospective_review_allowed=True,
            functions_in_practice=False,
            failure_reason="Emergency declarations too slow; local officials fear liability; communities act anyway and hope not to be punished",
        ),

        substrate_evidence=[
            SubstrateEvidence(
                evidence_type="standing_bridge",
                description="Log bridge built by community and Amish in 2 days during flood",
                location="Lafarge area",
                observable=True,
                documented=False,
                shows_rule_failed_purpose=True,
                shows_rule_contradicted_purpose=True,
            )
        ],

        community_observations=[
            "Bridge was up in 2 days. Engineers let it stay. Grandmaloon made it to hospital. Earl made it the next day.",
            "If we had waited for permits, people would have died.",
            "We don't teach this openly anymore. Too risky."
        ],

        practitioner_testimony=[
            "I could have paid consequences for saving lives.",
            "The knowledge dies with us now."
        ],

        confidence=0.90,
    )


# ===========================================================================
# Part 4. Example audit: Good Samaritan Law (as applied)
# ===========================================================================

def audit_good_samaritan_chilling_effect() -> LegislativeAudit:
    """Audit of Good Samaritan law's failure to protect trained individuals."""

    return LegislativeAudit(
        rule_name="Good Samaritan Protection",
        rule_type="statute",
        jurisdiction="State",

        first_principles=FirstPrinciplesPurpose(
            stated_purpose="Encourage emergency assistance by removing fear of liability",
            original_problem="Bystanders failing to help for fear of being sued",
            intended_beneficiary=[ConsequenceBearer.BENEFICIARY, ConsequenceBearer.PRACTITIONER],
            purpose_drift="Applied in ways that chill trained responders while protecting untrained",
            captured_by="Liability insurers, professional licensing boards",
        ),

        assumed_context=ContextAssumption(
            environment_type=EnvironmentType.BUFFERED_STABLE,
            handoff_available=True,
            time_abundant=False,
            resources_present=True,
            institutional_oversight_functional=True,
            alternatives_exist=True,
            undeclared_dependencies=[
                "Clear distinction between 'bystander' and 'professional'",
                "Good faith easily demonstrable",
                "Legal system distinguishes help from harm"
            ],
        ),

        scope=ScopeBoundary(
            valid_contexts=[EnvironmentType.BUFFERED_STABLE],
            validity_rationale="Protects clearly untrained bystanders in obvious emergencies",
            invalid_contexts=[EnvironmentType.CONSTRAINED, EnvironmentType.AUSTERE],
            invalidity_rationale="In constrained contexts, trained individuals are often the only responders but face unclear protection",
            negative_space=[
                "NOT clearly protective of anyone with formal training",
                "NOT protective of recurring assistance",
                "NOT protective when 'good faith' is disputed by credential-holders",
                "NOT protective against professional discipline, only civil liability"
            ],
            scope_declared=False,
        ),

        consequences_of_having=ConsequenceAnalysis(
            primary_intended=["Some bystanders feel protected to act"],
            primary_unintended=[
                "Trained individuals hide capacity",
                "Knowledge transmission stops",
                "Communities lose informal responders",
                "Preventable deaths when trained people don't act"
            ],
            secondary=[
                "Erosion of community response capacity",
                "Formal system sees 'no capacity' in rural areas",
                "Resources misallocated to importing capacity that was already there"
            ],
            tertiary=[
                "Knowledge lineages die",
                "When formal system fails, no informal system remains",
                "Communities become dependent on distant formal responders"
            ],
            bearers={
                "primary_unintended": [ConsequenceBearer.PRACTITIONER, ConsequenceBearer.BENEFICIARY],
                "secondary": [ConsequenceBearer.COMMUNITY],
                "tertiary": [ConsequenceBearer.FUTURE_GENERATIONS]
            },
        ),

        consequences_of_not_having=CounterfactualAnalysis(
            likely_outcome="Even fewer people would act; but trained individuals might feel more clarity (no false sense of protection)",
            alternative_mechanisms=[
                "Explicit immunity for good-faith emergency action regardless of training",
                "Community-based mutual aid agreements",
                "Clear 'duty to rescue' with corresponding immunity"
            ],
            who_benefits_from_absence=[ConsequenceBearer.INSTITUTION],
            who_suffers_from_absence=[ConsequenceBearer.BENEFICIARY],
        ),

        transmission_effect=TransmissionEffect(
            encourages_transmission=False,
            discourages_transmission=True,
            mechanism="Teaching becomes endorsement; unclear liability for student actions; knowledge transmission creates ongoing relationship that may be interpreted as professional",
            teaching_becomes_liability=True,
            knowledge_dies_with_holder=True,
            apprenticeship_discouraged=True,
            documentation_suppressed=True,
            documented_cases=["Rural responders hiding WFA/EMT knowledge"],
            chilling_effect_observed=True,
            chilling_effect_description="Trained individuals stop identifying as responders; stop teaching; knowledge dies with them",
        ),

        contradiction=ContradictionAnalysis(
            contradicts_purpose=True,
            contradiction_mechanism="Law intended to encourage help chills those most capable of helping, reducing net assistance",
            contradiction_contexts=[EnvironmentType.CONSTRAINED, EnvironmentType.AUSTERE],
            prevents_intended_outcome=True,
            harms_intended_beneficiary=True,
            examples=["EMTs hiding training in wilderness context", "Retired nurses refusing to assist"],
        ),

        exception_pathway=ExceptionPathway(
            pathway_exists=False,
            pathway_declared=False,
            pathway_actual="Hope you aren't sued. Hope the court agrees you acted in good faith. Hope your professional board doesn't discipline you.",
            trigger_conditions=[],
            protection_mechanism="Uncertain",
            good_faith_recognized=True,
            retrospective_review_allowed=True,
            functions_in_practice=False,
            failure_reason="Uncertainty itself causes chilling effect",
        ),

        community_observations=[
            "I don't advertise my knowledge anymore.",
            "Plenty in our community stopped.",
            "You don't dare teach it. The knowledge dies with you."
        ],

        practitioner_testimony=[
            "I could be a first responder. But are the consequences going to come back on me?",
            "I just keep quiet now."
        ],

        confidence=0.85,
    )


# ===========================================================================
# Part 5. Run the audits
# ===========================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("FIRST-PRINCIPLES LEGISLATIVE AUDIT FRAMEWORK")
    print("=" * 80)
    print()

    bridge_audit = audit_bridge_permit_constrained()
    print(bridge_audit.summary())
    print("\n" + "=" * 80)
    print("AI CONTEXT:")
    print(bridge_audit.to_ai_context())

    print("\n" + "=" * 80)

    gs_audit = audit_good_samaritan_chilling_effect()
    print(gs_audit.summary())
    print("\n" + "=" * 80)
    print("AI CONTEXT:")
    print(gs_audit.to_ai_context())
