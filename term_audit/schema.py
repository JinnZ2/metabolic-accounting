"""
term_audit/schema.py

Auditing economic terms against signal-definition criteria from information
science, and against their own first-principles purpose.

Every term is scored on seven axes. All scores are bounded [0.0, 1.0].
Scores are asserted with justification strings and source references.
No numeric claim may be made without a source_refs entry.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional

from term_audit.provenance import Provenance, coverage_report


# ---------------------------------------------------------------------------
# Signal-definition criteria (from information theory / measurement science)
# ---------------------------------------------------------------------------
#
# For a quantity X to qualify as a signal measuring Y, it must satisfy:
#
# 1. SCOPE_DEFINED       X has a declared, bounded domain of what it measures
# 2. UNIT_INVARIANT      one unit of X means the same thing across contexts
#                        relevant to the claimed measurement
# 3. REFERENT_STABLE     the thing Y being measured is itself well-defined
#                        and does not shift with the act of measurement
# 4. CALIBRATION_EXISTS  there is a reproducible procedure mapping X to Y
# 5. OBSERVER_INVARIANT  two independent observers measuring the same
#                        instance of Y via X get the same X value
#                        (within stated tolerance)
# 6. CONSERVATION_OR_LAW X obeys a known conservation rule or transfer law
#                        that constrains how it can change
# 7. FALSIFIABILITY      there exists a test that could show X fails to
#                        measure Y
#
# A term that fails three or more of these is not a signal. It is a token
# that has learned to occupy a signal-shaped position in discourse.
# ---------------------------------------------------------------------------

SIGNAL_CRITERIA = [
    "scope_defined",
    "unit_invariant",
    "referent_stable",
    "calibration_exists",
    "observer_invariant",
    "conservation_or_law",
    "falsifiability",
]


@dataclass
class SignalScore:
    """Score for one signal-definition criterion.

    `source_refs` is retained for backward compatibility with audits
    that predate the Provenance taxonomy. New audits should use
    `provenance` (see term_audit/provenance.py) which distinguishes
    EMPIRICAL / THEORETICAL / DESIGN_CHOICE / PLACEHOLDER /
    STIPULATIVE — forcing a citation on a design choice produces
    performative references that do not actually support the claim.
    """
    criterion: str                      # one of SIGNAL_CRITERIA
    score: float                        # 0.0 = fails, 1.0 = fully satisfies
    justification: str                  # why this score
    source_refs: List[str] = field(default_factory=list)
    provenance: Optional[Provenance] = None

    def __post_init__(self):
        if self.criterion not in SIGNAL_CRITERIA:
            raise ValueError(f"unknown criterion: {self.criterion}")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score out of bounds: {self.score}")


@dataclass
class StandardSetter:
    """Who defines the standard for this term, and what incentives shape it.

    The pair (incentive_structure, loss_if_audited) makes the
    standard-setter's stake explicit on both sides: what they gain
    from the current definition, what they would lose if it were
    audited and replaced. Per docs/PREEMPTING_ATTACKS.md preempt #5,
    this makes incentive defenses visible — when a defender of the
    current system speaks, their incentive is already documented.
    """
    name: str                           # entity name
    authority_basis: str                # statute, convention, market power, etc.
    incentive_structure: str            # what they gain by the definition
    independence_from_measured: float   # 0.0 = fully captured by measured
                                        # 1.0 = fully independent
    loss_if_audited: str = ""           # what they lose if the standard is
                                        # replaced by a clean signal. Empty
                                        # is allowed for backward compat but
                                        # signals an incomplete audit.

    def is_loss_documented(self) -> bool:
        """True iff loss_if_audited has been filled in. The framework's
        own audit-of-itself surfaces these gaps."""
        return bool(self.loss_if_audited.strip())


@dataclass
class FirstPrinciplesPurpose:
    """What the term was originally for, stated in physical or informational terms."""
    stated_purpose: str                 # the claimed function
    physical_referent: Optional[str]    # what in the physical world it maps to
    informational_referent: Optional[str]  # what information-theoretic quantity
    drift_score: float                  # 0.0 = current use matches purpose
                                        # 1.0 = current use is unrelated to purpose
    drift_justification: str


@dataclass
class TermAudit:
    """Full audit of one economic term."""
    term: str
    claimed_signal: str                 # what is it supposedly measuring
    standard_setters: List[StandardSetter]
    signal_scores: List[SignalScore]
    first_principles: FirstPrinciplesPurpose
    correlation_to_real_signal: float   # 0.0 = uncorrelated, 1.0 = perfect
    correlation_justification: str
    notes: str = ""
    # Preempt extensions (backward-compatible, default empty).
    # See docs/PREEMPTING_ATTACKS.md.
    boundary_conditions: List = field(default_factory=list)   # BoundaryCondition
    predictions: List = field(default_factory=list)           # FalsifiablePrediction

    # Scoring thresholds, exposed as class-level constants so the rule
    # is inspectable and tests can pin it. Changing these is a
    # load-bearing edit — see docs/AUDIT_07.md for the rationale on
    # the pass threshold (5/7 = "fails ≤ 2"), which matches the module
    # docstring's "fails three or more → not a signal" rule.
    PASS_SCORE: float = 0.7
    PASS_CRITERIA_REQUIRED: int = 5
    FAILURE_SCORE: float = 0.5

    def is_signal(self, threshold: Optional[int] = None) -> bool:
        """Term qualifies as a signal only if it passes >= threshold criteria
        at score >= PASS_SCORE.

        Default threshold is PASS_CRITERIA_REQUIRED (5 of 7), matching
        the module docstring: a term that fails three or more of seven
        criteria is not a signal. 5 passing = 2 failing at most.
        """
        if threshold is None:
            threshold = self.PASS_CRITERIA_REQUIRED
        passing = sum(1 for s in self.signal_scores if s.score >= self.PASS_SCORE)
        return passing >= threshold

    def pass_count(self) -> int:
        """Number of criteria passing at score >= PASS_SCORE."""
        return sum(1 for s in self.signal_scores if s.score >= self.PASS_SCORE)

    def score_vector(self) -> Dict[str, float]:
        """Return the full score vector, preserving information that
        is_signal()'s bool return necessarily loses. The collapsed-vs-
        decomposed argument's punchline is the gap between vectors; a
        bool cannot express it."""
        return {s.criterion: s.score for s in self.signal_scores}

    def mean_score(self) -> float:
        """Arithmetic mean of signal scores; lossy but monotonic in
        pass count."""
        if not self.signal_scores:
            return 0.0
        return sum(s.score for s in self.signal_scores) / len(self.signal_scores)

    def min_score(self) -> float:
        """Weakest criterion. A single 0 drags the audit; surfacing min
        separately is how we keep that visible."""
        if not self.signal_scores:
            return 0.0
        return min(s.score for s in self.signal_scores)

    def failure_modes(self) -> List[str]:
        """Return criteria where score < FAILURE_SCORE."""
        return [s.criterion for s in self.signal_scores
                if s.score < self.FAILURE_SCORE]

    def provenance_coverage(self) -> Dict:
        """Aggregate provenance coverage across signal_scores.

        Returns the same shape as provenance.coverage_report, computed
        over the provenance attached to each signal_score. Entries
        without a provenance field count as `none`.

        This is the framework auditing itself for where numeric claims
        are backed vs unbacked.
        """
        return coverage_report([s.provenance for s in self.signal_scores])

    def measurement_layer(self) -> Dict:
        """The math half of the audit, isolated from the incentive half.
        Per docs/PREEMPTING_ATTACKS.md preempt #2: a critic must declare
        which layer they are attacking."""
        return {
            "claimed_signal": self.claimed_signal,
            "signal_scores": self.signal_scores,
            "is_signal": self.is_signal(),
            "failure_modes": self.failure_modes(),
            "correlation_to_real_signal": self.correlation_to_real_signal,
            "boundary_conditions": self.boundary_conditions,
            "predictions": self.predictions,
        }

    def incentive_layer(self) -> Dict:
        """The incentive half of the audit, isolated from the math half.
        An attack on this layer is a defense of an incentive structure,
        not a defense of the measurement's validity."""
        return {
            "term": self.term,
            "standard_setters": self.standard_setters,
            "first_principles": self.first_principles,
        }

    def incomplete_loss_documentation(self) -> List[str]:
        """Standard-setter names whose loss_if_audited field is empty.
        The framework auditing itself."""
        return [
            s.name for s in self.standard_setters
            if not getattr(s, "is_loss_documented", lambda: True)()
        ]

    def summary(self) -> Dict:
        return {
            "term": self.term,
            "claimed_signal": self.claimed_signal,
            "is_signal": self.is_signal(),
            "failure_modes": self.failure_modes(),
            "drift_score": self.first_principles.drift_score,
            "correlation_to_real_signal": self.correlation_to_real_signal,
        }
