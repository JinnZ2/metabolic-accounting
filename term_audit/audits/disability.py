"""
term_audit/audits/disability.py

Audit of the term 'disability' against signal-definition criteria.

Core finding: 'disability' as currently used collapses three distinct
measurements into one token. Each of the three has a different referent,
different calibration procedure, and different observer-invariance
properties. Collapsing them is the measurement failure.

This module separates them, scores each independently, and provides a
linkage layer for evaluating empirical correlation and causation
between them.

Tier 4 framing per docs/TERMS_TO_AUDIT.md: this audit targets the
measurement, not the person the measurement was applied to. The
collapsed usage relocates environmental and structural failures into
individuals — the same pattern distributional/institutional.py
already tracks via fit_multiplier, trauma_tax, and
available_capacity.

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

from term_audit.schema import (
    TermAudit, SignalScore, StandardSetter, FirstPrinciplesPurpose,
)


# ---------------------------------------------------------------------------
# Three candidate measurements, kept separate
# ---------------------------------------------------------------------------
#
# MEASUREMENT_A  environment-person mismatch
#   referent:   the gap between a person's operational profile and the
#               tolerance band of a specific environment
#   property of: the (person, environment) pair
#   symmetry:   remediation can target either side
#
# MEASUREMENT_B  task-and-condition-bounded capacity
#   referent:   functional capacity for a specified task under specified
#               conditions
#   property of: the (person, task, conditions) triple
#   symmetry:   does not generalize across tasks or conditions
#
# MEASUREMENT_C  substrate damage relative to individual baseline
#   referent:   measurable physical or neurological loss relative to the
#               same individual's prior functional baseline
#   property of: the person, longitudinally
#   symmetry:   requires a baseline; cannot be computed cross-sectionally
#
# ---------------------------------------------------------------------------


# ===========================================================================
# MEASUREMENT A  environment-person mismatch
# ===========================================================================

DISABILITY_A = TermAudit(
    term="disability_A_mismatch",
    claimed_signal=(
        "gap between a person's operational profile and the tolerance "
        "band of their current environment"
    ),
    standard_setters=[
        StandardSetter(
            name="architects, HR policy setters, school curriculum designers",
            authority_basis="control of environment design",
            incentive_structure=(
                "narrow tolerance bands reduce design cost and increase "
                "managerial legibility; wider bands increase design cost "
                "but widen the usable population"
            ),
            independence_from_measured=0.4,
        ),
        StandardSetter(
            name="ADA / equivalent legal frameworks",
            authority_basis="statutory",
            incentive_structure=(
                "compliance-driven; measures environment against a legal "
                "minimum, not against the actual distribution of human "
                "operational profiles"
            ),
            independence_from_measured=0.5,
        ),
    ],
    signal_scores=[
        SignalScore(
            criterion="scope_defined",
            score=0.7,
            justification=(
                "mismatch is bounded once you specify the person and the "
                "environment. Scope is declarable."
            ),
        ),
        SignalScore(
            criterion="unit_invariant",
            score=0.4,
            justification=(
                "mismatch units vary by environment dimension (sensory, "
                "cognitive, physical, temporal). No single scalar "
                "captures it; a vector representation is required."
            ),
        ),
        SignalScore(
            criterion="referent_stable",
            score=0.6,
            justification=(
                "the referent (the gap) is stable once the environment "
                "is specified. It shifts when the environment changes, "
                "which is a feature not a bug."
            ),
        ),
        SignalScore(
            criterion="calibration_exists",
            score=0.5,
            justification=(
                "partial. Ergonomics, human factors, and universal "
                "design literature provide calibration for physical "
                "dimensions. Cognitive and sensory dimensions are "
                "less calibrated."
            ),
        ),
        SignalScore(
            criterion="observer_invariant",
            score=0.6,
            justification=(
                "two observers measuring the same person in the same "
                "environment will largely agree on the mismatch vector, "
                "provided the environment's tolerance band is documented."
            ),
        ),
        SignalScore(
            criterion="conservation_or_law",
            score=0.3,
            justification=(
                "no conservation law; this is a geometric relation "
                "between two distributions, not a conserved quantity."
            ),
        ),
        SignalScore(
            criterion="falsifiability",
            score=0.7,
            justification=(
                "falsifiable. Change the environment; measure whether "
                "the person's function changes. If it does, the "
                "mismatch was real. If it does not, it was not."
            ),
        ),
    ],
    first_principles=FirstPrinciplesPurpose(
        stated_purpose=(
            "identify where environments fail to accommodate the actual "
            "distribution of human operational profiles"
        ),
        physical_referent=(
            "geometric gap between two distributions: person's "
            "operational profile and environment's tolerance band"
        ),
        informational_referent=(
            "mutual information between person-state and "
            "environment-compatibility"
        ),
        drift_score=0.7,
        drift_justification=(
            "current usage relocates this mismatch into the person as "
            "a property, erasing the environment from the measurement. "
            "The drift is from 'relational geometry' to 'individual "
            "defect', which reverses the direction of the measurement."
        ),
    ),
    correlation_to_real_signal=0.7,
    correlation_justification=(
        "when measured as a relational quantity it correlates strongly "
        "with observable outcomes (task completion, fatigue, injury, "
        "attrition). Correlation collapses when the relational structure "
        "is erased."
    ),
    notes=(
        "this is the measurement most often smuggled under the current "
        "usage of 'disability'. Separating it lets us audit environments, "
        "not people."
    ),
)


# ===========================================================================
# MEASUREMENT B  task-and-condition-bounded capacity
# ===========================================================================

DISABILITY_B = TermAudit(
    term="disability_B_bounded_capacity",
    claimed_signal=(
        "functional capacity for a specified task under specified "
        "conditions"
    ),
    standard_setters=[
        StandardSetter(
            name="occupational assessors, sports medicine, rehabilitation",
            authority_basis="credentialed practice",
            incentive_structure=(
                "bounded measurement is aligned with their work; they "
                "benefit from accurate task-specific assessment"
            ),
            independence_from_measured=0.6,
        ),
        StandardSetter(
            name="insurance and disability benefit programs",
            authority_basis="statutory and contractual",
            incentive_structure=(
                "incentive to either narrow or widen the task scope "
                "depending on whether the program is paying out or "
                "denying claims"
            ),
            independence_from_measured=0.2,
        ),
    ],
    signal_scores=[
        SignalScore(
            criterion="scope_defined",
            score=0.85,
            justification=(
                "when task and conditions are specified, scope is "
                "tightly defined."
            ),
        ),
        SignalScore(
            criterion="unit_invariant",
            score=0.7,
            justification=(
                "within a specified task, units are typically "
                "well-defined (weight lifted, distance walked, error "
                "rate on a task, sustained attention duration)."
            ),
        ),
        SignalScore(
            criterion="referent_stable",
            score=0.75,
            justification=(
                "capacity for a specific task is a stable referent "
                "that can be measured repeatedly."
            ),
        ),
        SignalScore(
            criterion="calibration_exists",
            score=0.7,
            justification=(
                "task-specific calibration procedures exist in sports "
                "medicine, ergonomics, and occupational therapy."
            ),
        ),
        SignalScore(
            criterion="observer_invariant",
            score=0.75,
            justification=(
                "two assessors using the same protocol generally agree "
                "to within documented tolerance."
            ),
        ),
        SignalScore(
            criterion="conservation_or_law",
            score=0.4,
            justification=(
                "no universal conservation, but within-individual "
                "capacity is constrained by energy availability and "
                "recovery kinetics."
            ),
        ),
        SignalScore(
            criterion="falsifiability",
            score=0.85,
            justification=(
                "strongly falsifiable. Give the person the task under "
                "the conditions and measure."
            ),
        ),
    ],
    first_principles=FirstPrinciplesPurpose(
        stated_purpose=(
            "match people to tasks for which their current capacity "
            "is sufficient"
        ),
        physical_referent=(
            "measurable task performance under specified conditions"
        ),
        informational_referent=(
            "conditional probability of task success given person "
            "and conditions"
        ),
        drift_score=0.5,
        drift_justification=(
            "drifts when a bounded capacity measurement is generalized "
            "to 'cannot work' or 'cannot function'. The generalization "
            "discards the task and condition specification, which is "
            "the part that made the measurement meaningful."
        ),
    ),
    correlation_to_real_signal=0.8,
    correlation_justification=(
        "correlates well with actual task outcomes when task and "
        "conditions are held constant. Does not correlate with "
        "outcomes on different tasks under different conditions."
    ),
    notes=(
        "this is the narrow legitimate operational use. It answers "
        "'can this person do this specific task under these specific "
        "conditions', nothing more."
    ),
)


# ===========================================================================
# MEASUREMENT C  substrate damage relative to individual baseline
# ===========================================================================

DISABILITY_C = TermAudit(
    term="disability_C_substrate_damage",
    claimed_signal=(
        "measurable physical or neurological loss relative to the "
        "same individual's prior functional baseline"
    ),
    standard_setters=[
        StandardSetter(
            name="clinical medicine",
            authority_basis="credentialed diagnostic practice",
            incentive_structure=(
                "diagnosis drives treatment which drives revenue; "
                "incentive to identify substrate damage even where the "
                "issue is mismatch (A) or bounded capacity (B)"
            ),
            independence_from_measured=0.3,
        ),
        StandardSetter(
            name="imaging and laboratory measurement",
            authority_basis="physical instrumentation",
            incentive_structure=(
                "relatively independent when measuring physical "
                "substrate; less independent when interpreting "
                "borderline findings"
            ),
            independence_from_measured=0.7,
        ),
    ],
    signal_scores=[
        SignalScore(
            criterion="scope_defined",
            score=0.8,
            justification=(
                "bounded by the individual's own baseline; scope is "
                "explicitly longitudinal and within-subject."
            ),
        ),
        SignalScore(
            criterion="unit_invariant",
            score=0.75,
            justification=(
                "physical measurements (nerve conduction, range of "
                "motion, tissue integrity) have stable units."
            ),
        ),
        SignalScore(
            criterion="referent_stable",
            score=0.75,
            justification=(
                "referent is stable when a true baseline was "
                "measured. Collapses when no baseline exists and "
                "a population average is substituted."
            ),
        ),
        SignalScore(
            criterion="calibration_exists",
            score=0.7,
            justification=(
                "instrumentation is calibrated; interpretation layer "
                "is less so."
            ),
        ),
        SignalScore(
            criterion="observer_invariant",
            score=0.65,
            justification=(
                "high for instrumented measurement, lower for clinical "
                "interpretation."
            ),
        ),
        SignalScore(
            criterion="conservation_or_law",
            score=0.6,
            justification=(
                "physical tissue obeys physical laws; loss of function "
                "correlates with measurable substrate change."
            ),
        ),
        SignalScore(
            criterion="falsifiability",
            score=0.75,
            justification=(
                "falsifiable by direct physical measurement against "
                "the individual's baseline."
            ),
        ),
    ],
    first_principles=FirstPrinciplesPurpose(
        stated_purpose=(
            "detect actual substrate loss so it can be treated, "
            "compensated for, or protected against further loss"
        ),
        physical_referent=(
            "tissue-level or functional-level change relative to "
            "individual baseline"
        ),
        informational_referent=(
            "within-subject change signal in physiological "
            "measurements"
        ),
        drift_score=0.4,
        drift_justification=(
            "drifts when population averages are used as a baseline "
            "substitute for the individual. A person whose baseline "
            "was always outside the population mean gets labeled "
            "damaged without damage having occurred."
        ),
    ),
    correlation_to_real_signal=0.75,
    correlation_justification=(
        "high correlation with actual substrate state when individual "
        "baseline is known. Drops sharply when population baseline "
        "is substituted."
    ),
    notes=(
        "this is the narrow medical referent. It requires a real "
        "within-subject baseline, not a population average. Most "
        "current diagnostic practice substitutes population averages "
        "because within-subject baselines are expensive to establish."
    ),
)


# ===========================================================================
# Linkage evaluation
# ===========================================================================
#
# The three measurements are distinct but not independent. Some causal
# and correlational linkages are worth separating explicitly.
#
#   A  mismatch         ->  can produce apparent B (bounded capacity failure)
#                           without any C (substrate damage)
#   C  substrate damage ->  typically produces real B (bounded capacity loss)
#   B  bounded capacity ->  does not by itself imply C
#   A  mismatch         ->  if chronic, can produce C via stress pathways
#   C  substrate damage ->  can widen A by narrowing the person's tolerance
#                           for environment variation
#
# ---------------------------------------------------------------------------

@dataclass
class Linkage:
    """A hypothesized causal or correlational link between two measurements."""
    source: str                         # one of 'A', 'B', 'C'
    target: str                         # one of 'A', 'B', 'C'
    relation: str                       # 'causal', 'correlational', 'none'
    mechanism: str                      # physical or informational mechanism
    conditions: str                     # conditions under which it holds
    falsification_test: str             # how to test whether it holds
    strength_estimate: float            # 0.0 = no link, 1.0 = deterministic
    strength_justification: str
    source_refs: List[str] = field(default_factory=list)


DISABILITY_LINKAGES = [
    Linkage(
        source="A", target="B",
        relation="causal",
        mechanism=(
            "environmental mismatch reduces observable task capacity "
            "even when underlying substrate is intact; the environment "
            "is consuming capacity that would otherwise be available "
            "for the task"
        ),
        conditions=(
            "task is performed within the mismatched environment; "
            "person cannot route around the mismatch"
        ),
        falsification_test=(
            "measure task capacity in the mismatched environment, "
            "then remeasure in a matched environment. If capacity "
            "rises, A caused the apparent B."
        ),
        strength_estimate=0.7,
        strength_justification=(
            "strong in cases where the mismatch is on the same "
            "dimension the task taxes (sensory, attentional, motor)"
        ),
    ),
    Linkage(
        source="C", target="B",
        relation="causal",
        mechanism=(
            "substrate damage reduces the physical or neurological "
            "capacity available for task performance"
        ),
        conditions=(
            "the damaged substrate is on a pathway the task requires"
        ),
        falsification_test=(
            "measure task capacity before and after documented "
            "substrate change in the same individual"
        ),
        strength_estimate=0.85,
        strength_justification=(
            "nearly deterministic when the damage is on-pathway"
        ),
    ),
    Linkage(
        source="B", target="C",
        relation="none",
        mechanism=(
            "bounded capacity failure does not imply substrate damage; "
            "it can be produced by A (mismatch), fatigue, skill gap, "
            "or motivational state"
        ),
        conditions="always",
        falsification_test=(
            "show a case where B is low and no A, fatigue, skill gap, "
            "or motivational state is present, yet no C is found"
        ),
        strength_estimate=0.0,
        strength_justification=(
            "asymmetry: C implies B on-pathway, but B does not imply C"
        ),
    ),
    Linkage(
        source="A", target="C",
        relation="causal",
        mechanism=(
            "chronic environmental mismatch produces physiological "
            "stress, which produces measurable substrate damage over "
            "time (cortisol-mediated tissue effects, sleep-deprivation "
            "neural effects, repetitive strain)"
        ),
        conditions=(
            "mismatch is chronic and the person cannot exit the "
            "environment"
        ),
        falsification_test=(
            "longitudinal measurement of substrate markers in matched "
            "versus mismatched cohorts with otherwise similar exposure"
        ),
        strength_estimate=0.5,
        strength_justification=(
            "well-documented for some mismatch types (noise, shift work, "
            "chronic sensory overload); less documented for others"
        ),
    ),
    Linkage(
        source="C", target="A",
        relation="causal",
        mechanism=(
            "substrate damage narrows the person's tolerance band, "
            "widening the gap between their operational profile and "
            "the environment's tolerance band"
        ),
        conditions=(
            "always, if the damage is on a dimension the environment "
            "taxes"
        ),
        falsification_test=(
            "measure A before and after documented C in same "
            "individual in same environment"
        ),
        strength_estimate=0.7,
        strength_justification=(
            "geometric consequence of narrowing one distribution"
        ),
    ),
]


# ===========================================================================
# Combined summary
# ===========================================================================

ALL_DISABILITY_AUDITS = {
    "A_mismatch": DISABILITY_A,
    "B_bounded_capacity": DISABILITY_B,
    "C_substrate_damage": DISABILITY_C,
}


def collapsed_usage_audit() -> Dict:
    """
    Audit the current collapsed usage of 'disability' as a single term
    covering A, B, and C simultaneously.
    """
    return {
        "term": "disability_collapsed_current_usage",
        "claim": (
            "one word denoting environment mismatch, task-bounded "
            "capacity limitation, and substrate damage as if they "
            "were one measurement"
        ),
        "failure": (
            "three distinct referents collapsed into one token. "
            "None of the three can be measured cleanly because any "
            "measurement is contaminated by the other two. A mismatch "
            "gets booked as substrate damage. Substrate damage gets "
            "booked as bounded capacity. Bounded capacity on one task "
            "gets generalized to bounded capacity on all tasks."
        ),
        "consequence": (
            "the collapsed usage relocates environmental and structural "
            "failures into individuals. It makes the environment "
            "unauditable because the measurement exits through the "
            "person."
        ),
        "remediation": (
            "separate the three measurements. Report A, B, and C "
            "independently. Evaluate their linkages empirically per "
            "case. Do not use a single word to refer to any of them."
        ),
    }


if __name__ == "__main__":
    import json
    for key, audit in ALL_DISABILITY_AUDITS.items():
        print(f"=== {key} ===")
        print(json.dumps(audit.summary(), indent=2))
        print()
    print("=== collapsed-usage audit ===")
    print(json.dumps(collapsed_usage_audit(), indent=2))
    print()
    print(f"=== linkages: {len(DISABILITY_LINKAGES)} documented ===")
    for link in DISABILITY_LINKAGES:
        print(f"  {link.source} -> {link.target}  "
              f"({link.relation}, strength={link.strength_estimate})")
