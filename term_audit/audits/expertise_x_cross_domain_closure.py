"""
term_audit/audits/expertise_x_cross_domain_closure.py

E_X: Cross-domain closure capacity.

The probability that an individual can take a multi-domain, partially
undefined problem to completed state without failure or external handoff.

This measurement emerges from:
- Rural and remote community practice (no specialists available)
- High-reliability operations (offshore, polar, space, wilderness)
- Pre-industrial craft traditions (one person resolves the system)
- Collapse-recovery scenarios (infrastructure for handoff doesn't exist)

E_X is orthogonal to E_A, E_B, and E_C. High E_A in multiple domains
does not imply high E_X. E_X is the capacity to close the dependency
graph when domains couple and handoff is unavailable.

Path note: this module originally shipped at
`term_audit/cross_domain_closure.py` (outside the audits/ subdir).
AUDIT_08 moved it to match its own docstring and the `audits/`
convention shared with money/value/capital/productivity/efficiency/
disability, and added the sys.path bootstrap that the other audit
modules use so direct invocation works.

CC0. Stdlib only.
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

from term_audit.schema import (
    TermAudit, SignalScore, StandardSetter, FirstPrinciplesPurpose,
)
from term_audit.provenance import (
    empirical, theoretical, design_choice, placeholder, stipulative,
)


# ===========================================================================
# Part 1. E_X definition and scoring
# ===========================================================================

@dataclass
class CrossDomainClosureProfile:
    """Assessment of an individual's E_X capacity."""
    
    # Core metric: probability of closure without failure or handoff
    closure_probability: float  # 0.0 to 1.0
    
    # Contributing factors (not additive; closure is multiplicative)
    domain_breadth: int  # number of distinct domains they can operate in
    improvisation_capacity: float  # 0-1, solve undefined problems
    diagnostic_depth: float  # 0-1, identify true failure source
    handoff_avoidance: float  # 0-1, preference to resolve vs delegate
    failure_recovery_rate: float  # 0-1, recover from own errors
    
    # The key multiplicative factor: dependency coupling
    cross_domain_coupling: float  # how strongly domains interact in their work
    
    # Selection signal from constrained environments
    selection_priority_under_constraint: float  # 0-1, observed selection rate
    
    # Evidence base
    completed_closure_events: int  # number of observed full closures
    attempted_closure_events: int  # total attempts observed
    
    def closure_score(self) -> float:
        """
        Composite E_X score.
        
        The weighting emphasizes cross-domain coupling and handoff
        dependency because those are the failure modes credentials
        don't measure.
        """
        return (
            self.closure_probability * 0.35 +
            (1.0 - self.handoff_avoidance) * 0.25 +  # handoff avoidance is positive
            self.cross_domain_coupling * 0.20 +
            self.improvisation_capacity * 0.10 +
            self.diagnostic_depth * 0.05 +
            self.failure_recovery_rate * 0.05
        )


# ===========================================================================
# Part 2. Standard-setters for E_X
# ===========================================================================

E_X_STANDARD_SETTERS = [
    StandardSetter(
        name="constrained_environment_operators",
        authority_basis=(
            "practitioners in environments where handoff is unavailable "
            "or failure is catastrophic: rural communities, offshore "
            "operations, remote field stations, wilderness responders"
        ),
        incentive_structure=(
            "survival depends on correct selection; selecting wrong "
            "person produces immediate operational failure with no "
            "backup. This is the strongest possible incentive alignment."
        ),
        independence_from_measured=0.95,
    ),
    StandardSetter(
        name="high_reliability_organization_peers",
        authority_basis=(
            "peer assessment in contexts where failure cascades: "
            "nuclear operations, air traffic control, surgical teams, "
            "wildland firefighting"
        ),
        incentive_structure=(
            "team survival depends on accurate assessment of who can "
            "close when systems couple unexpectedly"
        ),
        independence_from_measured=0.85,
    ),
    StandardSetter(
        name="historical_craft_and_trade_traditions",
        authority_basis=(
            "multi-generational observation of who actually resolves "
            "system failures in constrained environments"
        ),
        incentive_structure=(
            "traditions that select wrong practitioners don't persist; "
            "selection pressure operates on generational timescale"
        ),
        independence_from_measured=0.75,
    ),
    StandardSetter(
        name="outcome_tracking_in_constrained_operations",
        authority_basis="operational records of closure events",
        incentive_structure=(
            "records don't have incentives; they provide feedback"
        ),
        independence_from_measured=0.90,
    ),
]


# ===========================================================================
# Part 3. E_X signal criteria audit
# ===========================================================================

E_X_AUDIT = TermAudit(
    term="expertise_X_cross_domain_closure",
    claimed_signal=(
        "capacity to take a multi-domain, partially undefined problem "
        "to completed state without failure or external handoff"
    ),
    standard_setters=E_X_STANDARD_SETTERS,
    signal_scores=[
        SignalScore(
            criterion="scope_defined",
            score=0.80,
            justification=(
                "scope is bounded by the observed closure events; "
                "defined as 'problems presented and resolved without "
                "handoff'. Scope shifts as practitioner demonstrates "
                "closure across new domains."
            ),
            provenance=stipulative(
                rationale=(
                    "E_X is defined by the closure-without-handoff test; "
                    "scope-definedness is built into the definition via the "
                    "(practitioner, problem-set, handoff-unavailable context) "
                    "triple. 0.80 rather than 1.0 allows for contested cases "
                    "where 'without handoff' is ambiguous at the margin."
                ),
                definition_ref=(
                    "module docstring: E_X = probability of closure without "
                    "failure or external handoff across multi-domain problems"
                ),
            ),
        ),
        SignalScore(
            criterion="unit_invariant",
            score=0.70,
            justification=(
                "unit is closure probability estimated from observed "
                "events; comparable across practitioners with similar "
                "observation density"
            ),
            provenance=theoretical(
                rationale=(
                    "probability as unit is invariant by construction. "
                    "0.70 rather than 1.0 reflects that observation density "
                    "varies across practitioners and naive ratio estimation "
                    "loses invariance at low event counts."
                ),
                falsification_test=(
                    "compute closure probabilities for practitioners at "
                    "matched observation densities and show >20% invariance "
                    "failure under the same protocol"
                ),
            ),
        ),
        SignalScore(
            criterion="referent_stable",
            score=0.75,
            justification=(
                "referent (completed resolution without handoff) is "
                "stable and observable. A problem either was resolved "
                "without handoff or it wasn't."
            ),
            provenance=stipulative(
                rationale=(
                    "the closure-vs-handoff distinction is binary by "
                    "definition; 0.75 rather than 1.0 reflects that "
                    "partial-handoff edge cases (consultation, informal "
                    "support) are contested in practice"
                ),
                definition_ref=(
                    "E_X referent: outcome of (problem resolved | no external "
                    "handoff) over repeated presentations"
                ),
            ),
        ),
        SignalScore(
            criterion="calibration_exists",
            score=0.65,
            justification=(
                "calibration occurs naturally in constrained environments: "
                "practitioners are tested on real closures and selection "
                "priority updates based on outcomes"
            ),
            provenance=empirical(
                source_refs=[
                    "Weick & Sutcliffe 2007, 'Managing the Unexpected: "
                    "Resilient Performance in an Age of Uncertainty' "
                    "(high-reliability organizations, HROs)",
                    "Ostrom 1990, 'Governing the Commons' (communities "
                    "selecting practitioners under constraint)",
                    "Perrow 1984, 'Normal Accidents' (coupled-system "
                    "failure under credential-based selection)",
                ],
                rationale=(
                    "literature on HROs and common-pool resource governance "
                    "documents outcome-based practitioner selection in "
                    "constrained environments; that selection process is "
                    "the natural calibration"
                ),
                scope_caveat=(
                    "cited literature is qualitative/case-study; a formal "
                    "calibration protocol (pre-registered closure events, "
                    "standardized difficulty) has not been built"
                ),
                falsification_test=(
                    "pre-register closure-event difficulty across matched "
                    "environments; show practitioner selection does not "
                    "track closure success"
                ),
            ),
        ),
        SignalScore(
            criterion="observer_invariant",
            score=0.70,
            justification=(
                "multiple constrained-environment observers agree on "
                "who can close; agreement strongest in high-stakes "
                "contexts where selection errors are visible"
            ),
            provenance=design_choice(
                rationale=(
                    "0.70 reflects that inter-observer agreement is high "
                    "in constrained/high-stakes environments (HRO selection "
                    "literature) but lower in settings where selection "
                    "errors are masked by buffer; the score averages across "
                    "contexts"
                ),
                alternatives_considered=[
                    "0.85 (weighting constrained-environment cases)",
                    "0.50 (weighting buffered-environment cases where "
                    "credentials substitute for observation)",
                    "a vector indexed by environment-type",
                ],
                falsification_test=(
                    "assemble matched observer pairs in constrained "
                    "environments; measure inter-rater agreement on E_X "
                    "rankings and show agreement below 0.6"
                ),
            ),
        ),
        SignalScore(
            criterion="conservation_or_law",
            score=0.40,
            justification=(
                "closure capacity is not conserved; it can be acquired "
                "through cross-domain experience and atrophies without "
                "practice. Substrate dynamic rather than conservation law."
            ),
            provenance=theoretical(
                rationale=(
                    "E_X follows a maintenance-and-accumulation dynamic "
                    "parallel to K_C (institutional capital): grows through "
                    "iterated cross-domain closure, decays without practice. "
                    "This is a dynamic constraint, not a conservation law; "
                    "0.40 reflects the intermediate status."
                ),
                source_refs=[
                    "Anders Ericsson 1993, 'The Role of Deliberate Practice "
                    "in the Acquisition of Expert Performance'",
                    "capital audit, K_C conservation_or_law provenance "
                    "(parallel dynamic structure)",
                ],
                falsification_test=(
                    "find a population where E_X persists across extended "
                    "(>5 year) practice absence without refresher cycles"
                ),
            ),
        ),
        SignalScore(
            criterion="falsifiability",
            score=0.90,
            justification=(
                "strongly falsifiable: present a multi-domain problem "
                "under constraint, observe whether closure occurs "
                "without handoff"
            ),
            provenance=stipulative(
                rationale=(
                    "E_X falsifiability is built into the operational "
                    "definition: the closure test is both the measurement "
                    "and the falsification procedure. 0.90 allows for the "
                    "observational overhead of running the test under "
                    "genuinely constrained conditions."
                ),
                definition_ref=(
                    "E_X operational definition: closure-without-handoff "
                    "test on a multi-domain problem under constraint"
                ),
            ),
        ),
    ],
    first_principles=FirstPrinciplesPurpose(
        stated_purpose=(
            "identify practitioners who can take multi-domain, partially "
            "undefined problems to completed state in environments where "
            "specialists and handoff infrastructure are unavailable"
        ),
        physical_referent=(
            "observed closure events: problems presented, resolved "
            "without external handoff, outcome observable"
        ),
        informational_referent=(
            "conditional probability of closure given (practitioner, "
            "problem-class, environmental constraint level)"
        ),
        drift_score=0.15,
        drift_justification=(
            "minimal drift: E_X is a proposed measurement, not yet "
            "widely adopted, so it has not accumulated the collapse-"
            "into-credentials pattern that E_A and E_B have. The "
            "drift risk is future, not historical — if E_X becomes "
            "institutionally recognized, it will be subject to the "
            "same capture pressures that corrupted E_B."
        ),
    ),
    correlation_to_real_signal=0.85,
    correlation_justification=(
        "E_X correlates strongly with operational outcomes in constrained "
        "environments because it is the measurement those environments "
        "actually use for selection. The correlation is highest where "
        "handoff is unavailable and domains couple."
    ),
    notes=(
        "E_X is the measurement that credentials cannot capture because "
        "credentials are defined by scope boundaries. E_X is measured by "
        "closure across boundaries. Rural communities, remote operations, "
        "and high-reliability teams already use this measurement. The "
        "audit makes it explicit and portable."
    ),
)


# ===========================================================================
# Part 4. Relationship to E_A, E_B, E_C
# ===========================================================================

@dataclass
class ExpertiseFullProfile:
    """Complete decomposition of expertise into four orthogonal measurements."""
    
    # E_A: operational capacity in defined domain
    e_a_scores: Dict[str, float]  # domain -> capacity (0-1)
    
    # E_B: credentialed status
    e_b_credentials: List[str]  # credentials held
    
    # E_C: transmission capacity
    e_c_transmission: float  # 0-1
    
    # E_X: cross-domain closure
    e_x_profile: CrossDomainClosureProfile
    
    def domain_average(self) -> float:
        """Average E_A across domains. NOT a substitute for E_X."""
        if not self.e_a_scores:
            return 0.0
        return sum(self.e_a_scores.values()) / len(self.e_a_scores)
    
    def selection_fitness_constrained(self) -> float:
        """
        Selection fitness in constrained environments.
        
        E_X dominates because handoff unavailable.
        """
        return (
            self.e_x_profile.closure_score() * 0.60 +
            self.domain_average() * 0.25 +
            self.e_c_transmission * 0.15
            # E_B intentionally zero weight in constrained selection
        )
    
    def selection_fitness_credentialed(self) -> float:
        """
        Selection fitness in credential-gated environments.
        
        E_B dominates because that's what the system measures.
        This is the inversion the audit documents.
        """
        return (
            (1.0 if self.e_b_credentials else 0.0) * 0.70 +
            self.domain_average() * 0.20 +
            self.e_c_transmission * 0.10
        )


# ===========================================================================
# Part 5. The dependency graph closure test
# ===========================================================================

@dataclass
class DependencyGraphProblem:
    """A test case for E_X measurement."""
    
    problem_description: str
    domains_involved: List[str]
    coupling_strength: float  # how strongly domains interact
    handoff_available: bool  # can the practitioner delegate?
    time_constraint: Optional[float]  # time available before failure
    resource_constraint: Optional[str]  # what's limited
    
    # The actual dependency graph that must be closed
    required_capacities: List[str]  # what must be done to resolve


def administer_closure_test(
    practitioner: ExpertiseFullProfile,
    problem: DependencyGraphProblem,
) -> Dict:
    """
    Predict closure probability for a given practitioner-problem pair.
    
    This is the operational test that constrained environments run
    implicitly every time they select who to call.
    """
    # Can they cover the required capacities?
    covered = set()
    for capacity in problem.required_capacities:
        # Check direct E_A in relevant domains
        for domain, score in practitioner.e_a_scores.items():
            if domain in capacity and score >= 0.6:
                covered.add(capacity)
                break
    
    coverage_ratio = len(covered) / len(problem.required_capacities) if problem.required_capacities else 1.0
    
    # E_X adjusts coverage by coupling strength and improvisation
    if problem.coupling_strength > 0.5:
        # High coupling: domain coverage is less predictive; closure
        # depends on cross-domain integration capacity
        predicted_closure = (
            coverage_ratio * 0.4 +
            practitioner.e_x_profile.closure_probability * 0.6
        )
    else:
        # Low coupling: domains are separable; coverage predicts well
        predicted_closure = coverage_ratio
    
    # Handoff availability changes the threshold for success
    if problem.handoff_available:
        # With handoff, can succeed by delegating uncovered capacities
        predicted_closure = min(1.0, predicted_closure * 1.2)
    
    return {
        "predicted_closure": predicted_closure,
        "coverage_ratio": coverage_ratio,
        "e_x_contribution": practitioner.e_x_profile.closure_score(),
        "would_select": predicted_closure >= 0.7,  # typical threshold
        "failure_risk": 1.0 - predicted_closure,
    }


# ===========================================================================
# Part 6. Falsifiable predictions
# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
    {
        "id": 1,
        "claim": (
            "E_X (cross-domain closure) is a better predictor of operational "
            "success in constrained environments than E_A domain average, "
            "E_B credential count, or E_C transmission capacity"
        ),
        "falsification": (
            "Measure all four in a constrained-environment sample; show "
            "E_X does not dominate predictive power"
        ),
    },
    {
        "id": 2,
        "claim": (
            "High E_A across multiple domains does not imply high E_X; the "
            "correlation is weak because closure requires integration "
            "capacity that domain competence doesn't measure"
        ),
        "falsification": (
            "Measure E_A and E_X in a multi-domain practitioner sample; "
            "show strong correlation (r > 0.7)"
        ),
    },
    {
        "id": 3,
        "claim": (
            "Credentials (E_B) have near-zero weight in actual selection "
            "decisions in constrained environments where handoff is "
            "unavailable and failure is visible"
        ),
        "falsification": (
            "Observe selection decisions in rural/remote/offshore contexts; "
            "show credentials influence selection independent of "
            "demonstrated closure history"
        ),
    },
    {
        "id": 4,
        "claim": (
            "The dependency graph closure test predicts operational outcomes "
            "better than credential-based assignment when domains couple "
            "(coupling_strength > 0.5)"
        ),
        "falsification": (
            "Run paired assignments (credential vs closure-test) on coupled "
            "problems; show no outcome difference"
        ),
    },
    {
        "id": 5,
        "claim": (
            "Constrained-environment communities already use E_X as their "
            "primary selection signal; they call it 'who you call when it "
            "has to work' and their selection accuracy exceeds formal "
            "credentialing systems for coupled-domain problems"
        ),
        "falsification": (
            "Compare selection accuracy (problem resolution rate) between "
            "rural community referral networks and formal credential-based "
            "assignment; show credential-based outperforms"
        ),
    },
]


# ===========================================================================
# Part 7. Integration with metabolic accounting
# ===========================================================================

def e_x_to_metabolic_accounting(
    profile: CrossDomainClosureProfile,
    entity_name: str,
) -> Dict:
    """
    Map E_X profile to metabolic accounting inputs.
    
    E_X becomes a basin state: cross_domain_closure_capacity.
    This basin regenerates through practice across coupled domains
    and extracts through credential-gating that prevents cross-domain
    work (scope of practice restrictions).
    """
    return {
        "basin_name": f"{entity_name}_closure_capacity",
        "category": "human_substrate",  # or new category: "integration_capacity"
        "current_level": profile.closure_probability,
        "regeneration_rate": 0.05 * profile.cross_domain_coupling,  # coupling drives learning
        "extraction_rate": 0.02 * (1.0 - profile.handoff_avoidance),  # handoff culture extracts
        "signal_quality": 0.75,  # constrained-environment observation is reliable
        "assumption_boundary": (
            "E_X measurement assumes closure events are observed and "
            "remembered; breaks down when communities fragment and "
            "selection history is lost"
        ),
    }


if __name__ == "__main__":
    # Example: rural practitioner with high E_X, no credentials
    rural_practitioner = ExpertiseFullProfile(
        e_a_scores={
            "electrical": 0.85,
            "mechanical": 0.80,
            "structural": 0.70,
            "hydraulic": 0.65,
        },
        e_b_credentials=[],  # none
        e_c_transmission=0.60,  # can teach but not formally
        e_x_profile=CrossDomainClosureProfile(
            closure_probability=0.90,
            domain_breadth=4,
            improvisation_capacity=0.85,
            diagnostic_depth=0.90,
            handoff_avoidance=0.95,  # resolves, doesn't delegate
            failure_recovery_rate=0.85,
            cross_domain_coupling=0.80,
            selection_priority_under_constraint=0.95,  # first call
            completed_closure_events=230,
            attempted_closure_events=255,
        ),
    )
    
    # Example: credentialed specialist
    credentialed_specialist = ExpertiseFullProfile(
        e_a_scores={"electrical": 0.95},  # deep but narrow
        e_b_credentials=["PE_Electrical", "Master_Electrician"],
        e_c_transmission=0.40,  # doesn't teach much
        e_x_profile=CrossDomainClosureProfile(
            closure_probability=0.60,  # stops at domain boundary
            domain_breadth=1,
            improvisation_capacity=0.30,
            diagnostic_depth=0.80,  # deep in domain, shallow across
            handoff_avoidance=0.20,  # delegates outside scope
            failure_recovery_rate=0.90,
            cross_domain_coupling=0.10,
            selection_priority_under_constraint=0.30,
            completed_closure_events=45,
            attempted_closure_events=50,
        ),
    )
    
    # Test a coupled problem
    coupled_problem = DependencyGraphProblem(
        problem_description="pump house electrical and foundation failure",
        domains_involved=["electrical", "structural", "hydraulic"],
        coupling_strength=0.80,  # high coupling
        handoff_available=False,  # rural: no specialist available
        time_constraint=48.0,
        resource_constraint="on-site materials only",
        required_capacities=[
            "electrical_diagnosis",
            "structural_assessment",
            "hydraulic_repair",
            "improvised_mounting",
        ],
    )
    
    print("=" * 72)
    print("E_X: CROSS-DOMAIN CLOSURE CAPACITY")
    print("=" * 72)
    print()
    
    print("--- rural practitioner (high E_X, no credentials) ---")
    rural_result = administer_closure_test(rural_practitioner, coupled_problem)
    print(f"  closure probability: {rural_result['predicted_closure']:.2f}")
    print(f"  would select: {rural_result['would_select']}")
    print(f"  E_X contribution: {rural_result['e_x_contribution']:.2f}")
    
    print()
    print("--- credentialed specialist (high E_A, narrow scope) ---")
    specialist_result = administer_closure_test(credentialed_specialist, coupled_problem)
    print(f"  closure probability: {specialist_result['predicted_closure']:.2f}")
    print(f"  would select: {specialist_result['would_select']}")
    print(f"  E_X contribution: {specialist_result['e_x_contribution']:.2f}")
    
    print()
    print("--- selection inversion ---")
    print(f"  constrained environment selects: rural practitioner")
    print(f"  credential-gated environment selects: credentialed specialist")
    print(f"  the inversion is measurable")
