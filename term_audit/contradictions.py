"""
term_audit/contradictions.py

Automated contradiction detection for claims about measurement systems.

Implements preempt #7 from docs/PREEMPTING_ATTACKS.md: build a
contradiction-checker. If someone claims the current system is
coherent, run their claims through this module. Does "money is a
stable signal" coexist with "monetary value varies by jurisdiction,
time, and legal regime"? No. Encode that. Make it automated.

The detector is structural, not natural-language. It looks for two
patterns:

  DIRECT_CONTRADICTION:
    Two claims about the same referent assert mutually-exclusive
    properties from a registered exclusion set.

  SCOPE_CONTRADICTION:
    Two claims about the same referent declare incompatible scopes
    (one says invariant, the other says jurisdiction-dependent).

Adding a new mutually-exclusive property pair is one line in
MUTUALLY_EXCLUSIVE. Adding a known historical contradiction is one
entry in KNOWN_CONTRADICTIONS.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Mutually-exclusive properties
# ---------------------------------------------------------------------------
#
# If a claim asserts property P about a referent and another claim
# asserts property Q about the same referent, and {P, Q} is a registered
# mutually-exclusive pair, the two claims contradict.
#
# The registry is symmetric: declaring (P, Q) implies (Q, P).
# ---------------------------------------------------------------------------

MUTUALLY_EXCLUSIVE: List[Tuple[str, str]] = [
    ("stable", "varying"),
    ("stable", "shifting"),
    ("stable", "context_dependent"),
    ("invariant", "context_dependent"),
    ("invariant", "jurisdiction_dependent"),
    ("invariant", "regime_dependent"),
    ("conserved", "created_or_destroyed"),
    ("conserved", "non_conserved"),
    ("observer_invariant", "observer_dependent"),
    ("calibrated", "uncalibrated"),
    ("calibrated", "no_reproducible_procedure"),
    ("scope_defined", "scope_undeclared"),
    ("falsifiable", "unfalsifiable"),
    ("monotone", "non_monotone"),
    ("deterministic", "stochastic"),
    ("universal", "domain_specific"),
]


def _exclusion_set() -> Dict[str, Set[str]]:
    """Build the symmetric exclusion lookup from MUTUALLY_EXCLUSIVE."""
    out: Dict[str, Set[str]] = {}
    for a, b in MUTUALLY_EXCLUSIVE:
        out.setdefault(a, set()).add(b)
        out.setdefault(b, set()).add(a)
    return out


_EXCLUSION = _exclusion_set()


# ---------------------------------------------------------------------------
# Claim and Contradiction
# ---------------------------------------------------------------------------

@dataclass
class Claim:
    """A claim about a measurement or referent.

    `referent` is the canonical name of the thing being claimed about
    (e.g. 'money', 'GDP', 'productivity'). Two claims contradict only
    if their referents match.

    `asserted_property` is one of the labels in MUTUALLY_EXCLUSIVE
    (or any other label — only registered pairs trigger contradictions).

    `text` and `source` are for human review.
    """
    referent: str
    asserted_property: str
    text: str
    source: str = ""
    declared_scope: Dict[str, str] = field(default_factory=dict)

    def normalized_referent(self) -> str:
        return self.referent.strip().lower().replace(" ", "_").replace("-", "_")


@dataclass
class Contradiction:
    """A detected contradiction between two claims."""
    claim_a: Claim
    claim_b: Claim
    kind: str                   # 'direct' | 'scope'
    explanation: str


def check_contradictions(claims: List[Claim]) -> List[Contradiction]:
    """Return all pairwise contradictions in `claims`.

    Quadratic in len(claims). Acceptable because contradiction
    detection is run on small claim sets (one audit's worth, or one
    paper's worth), not on populations."""
    out: List[Contradiction] = []
    for i, a in enumerate(claims):
        for b in claims[i + 1:]:
            if a.normalized_referent() != b.normalized_referent():
                continue
            # direct property exclusion
            excl = _EXCLUSION.get(a.asserted_property, set())
            if b.asserted_property in excl:
                out.append(Contradiction(
                    claim_a=a, claim_b=b,
                    kind="direct",
                    explanation=(
                        f"properties {a.asserted_property!r} and "
                        f"{b.asserted_property!r} are mutually exclusive "
                        f"for referent {a.referent!r}"
                    ),
                ))
                continue
            # scope contradiction: same referent, same property, but
            # declared scopes disagree on a load-bearing dimension
            for dim in ("jurisdiction", "time_horizon", "referent"):
                va = a.declared_scope.get(dim)
                vb = b.declared_scope.get(dim)
                if va and vb and va != vb and a.asserted_property == "invariant":
                    out.append(Contradiction(
                        claim_a=a, claim_b=b,
                        kind="scope",
                        explanation=(
                            f"claim asserts {a.asserted_property!r} but "
                            f"declared {dim} differs ({va!r} vs {vb!r})"
                        ),
                    ))
                    break
    return out


# ---------------------------------------------------------------------------
# Known contradictions (historical / canonical)
# ---------------------------------------------------------------------------
#
# Pre-registered pairs of claims that are structurally incompatible
# but commonly asserted together by defenders of the current
# measurement system. These are documented so a critic doesn't have
# to re-derive them every time.
# ---------------------------------------------------------------------------

KNOWN_CONTRADICTIONS: List[Tuple[Claim, Claim, str]] = [
    (
        Claim(
            referent="money",
            asserted_property="stable",
            text="money is a stable signal of value across contexts",
            source="standard economics framing",
        ),
        Claim(
            referent="money",
            asserted_property="varying",
            text=(
                "monetary value varies by jurisdiction, time, "
                "purchasing power, and legal regime"
            ),
            source="empirical observation; Balassa-Samuelson, BLS regional CPI",
        ),
        "stable-vs-varying for the same referent",
    ),
    (
        Claim(
            referent="money",
            asserted_property="conserved",
            text="dollars are conserved within the financial system",
            source="folk monetary intuition",
        ),
        Claim(
            referent="money",
            asserted_property="created_or_destroyed",
            text=(
                "credit creation adds units; default destroys units; "
                "central-bank operations add or remove units"
            ),
            source=(
                "McLeay, Radia, Thomas 2014, "
                "'Money Creation in the Modern Economy', "
                "Bank of England Quarterly Bulletin"
            ),
        ),
        "conservation claim contradicted by documented credit dynamics",
    ),
    (
        Claim(
            referent="disability",
            asserted_property="observer_invariant",
            text="disability status is an objective property of a person",
            source="standard clinical / institutional framing",
        ),
        Claim(
            referent="disability",
            asserted_property="observer_dependent",
            text=(
                "the same person is disabled in one environment and not "
                "in another; the measurement is relational"
            ),
            source="term_audit/audits/disability.py (DISABILITY_A)",
        ),
        "observer-invariance claim contradicted by environment-relative outcome",
    ),
]


def known_contradictions_check() -> List[Contradiction]:
    """Run check_contradictions over every registered KNOWN pair.
    Useful as a smoke test of the detector itself: every registered
    pair MUST surface as a contradiction; if any does not, the
    detector has regressed."""
    out: List[Contradiction] = []
    for a, b, _ in KNOWN_CONTRADICTIONS:
        out.extend(check_contradictions([a, b]))
    return out
