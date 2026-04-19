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
from typing import List, Dict, Optional


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
    """Score for one signal-definition criterion."""
    criterion: str                      # one of SIGNAL_CRITERIA
    score: float                        # 0.0 = fails, 1.0 = fully satisfies
    justification: str                  # why this score
    source_refs: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.criterion not in SIGNAL_CRITERIA:
            raise ValueError(f"unknown criterion: {self.criterion}")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score out of bounds: {self.score}")


@dataclass
class StandardSetter:
    """Who defines the standard for this term, and what incentives shape it."""
    name: str                           # entity name
    authority_basis: str                # statute, convention, market power, etc.
    incentive_structure: str            # what they gain/lose by the definition
    independence_from_measured: float   # 0.0 = fully captured by measured
                                        # 1.0 = fully independent


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

    def is_signal(self, threshold: int = 5) -> bool:
        """Term qualifies as a signal only if it passes >= threshold criteria
        at score >= 0.7."""
        passing = sum(1 for s in self.signal_scores if s.score >= 0.7)
        return passing >= threshold

    def failure_modes(self) -> List[str]:
        """Return criteria where score < 0.5."""
        return [s.criterion for s in self.signal_scores if s.score < 0.5]

    def summary(self) -> Dict:
        return {
            "term": self.term,
            "claimed_signal": self.claimed_signal,
            "is_signal": self.is_signal(),
            "failure_modes": self.failure_modes(),
            "drift_score": self.first_principles.drift_score,
            "correlation_to_real_signal": self.correlation_to_real_signal,
        }
