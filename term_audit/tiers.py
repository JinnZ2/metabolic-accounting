"""
term_audit/tiers.py

Tiered list of terms the framework identifies as tokens occupying
signal-shaped positions without meeting signal-definition criteria
(scope_defined, unit_invariant, referent_stable, calibration_exists,
observer_invariant, conservation_or_law, falsifiability — see
term_audit/schema.py).

Tier ordering is load-bearing: Tier 1 is the foundation. Most
Tier 2–5 terms reduce to Tier 1 claims (productivity measured in
dollars, accountability for dollar-denominated performance,
merit for skill-credentialed hiring). Cracking Tier 1 propagates
upward; defenders will defend Tier 1 hardest.

Each audit in term_audit/audits/ should declare which tier it
addresses. A new audit of a term not on these lists can register
a new tier or extend an existing one — adding to the lists is
fine; removing a term silently weakens the framework's coverage
and is caught by tests/test_tiers.py.

See docs/TERMS_TO_AUDIT.md for the framing observations that shape
the tiering and for the reading-order guidance for AI assistants
working through the list.

CC0. Stdlib only.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TermTier:
    """One tier in the audit priority stack."""
    number: int
    name: str
    description: str
    terms: Tuple[str, ...]


TIER_1_FOUNDATIONAL = TermTier(
    number=1,
    name="foundational fictions",
    description=(
        "maximum resistance; Tiers 2–5 are structurally dependent on "
        "these. If money is not a signal, then productivity-in-dollars "
        "is not a signal, then performance-measured-by-productivity is "
        "not a signal, then accountability-for-performance is not a "
        "signal. The stack is load-bearing on the first term."
    ),
    terms=(
        "money",
        "currency",
        "capital",
        "investment",
        "value",
        "wealth",
        "economic_growth",
        "gross_domestic_product",
    ),
)


TIER_2_LABOR_AND_HUMAN_WORTH = TermTier(
    number=2,
    name="labor and human-worth measurements",
    description=(
        "terms that purport to measure what a person produces or is "
        "worth. All ride on Tier 1's currency referent; most also "
        "assume an institutional frame that treats worker output as "
        "scalar."
    ),
    terms=(
        "productivity",
        "efficiency",
        "performance",
        "skill",
        "qualification",
        "credential",
        "merit",
        "unemployment",
        "labor_market",
        "human_capital",
    ),
)


TIER_3_ORGANIZATIONAL_LEGITIMACY = TermTier(
    number=3,
    name="organizational and institutional legitimacy",
    description=(
        "terms institutions use to describe their own authority "
        "structure and the rules applied to participants. Usually "
        "self-referential: compliance with best practices set by "
        "stakeholders governed by the institution being measured."
    ),
    terms=(
        "accountability",
        "authority",
        "leadership",
        "expertise",
        "governance",
        "compliance",
        "professionalism",
        "best_practices",
        "stakeholder",
    ),
)


TIER_4_CAPACITY_MEASUREMENTS = TermTier(
    number=4,
    name="mental and physical capacity measurements",
    description=(
        "terms that measure persons against institutional expectations "
        "and relocate failure from environment to person. The audit is "
        "NOT that disability does not exist; the audit is that the "
        "measurement locates the failure in the person rather than in "
        "the institution-person fit, which is the pattern "
        "distributional/institutional.py already tracks via "
        "fit_multiplier, trauma_tax, and available_capacity. Frame "
        "carefully: this tier will hurt people reading it, including "
        "people you want as allies."
    ),
    terms=(
        "disability",
        "mental_illness",
        "intelligence",
        "iq",
        "learning_disorder",
        "adhd",
        "autism_spectrum",
        "normal",
        "normative",
        "functional",
        "high_functioning",
        "low_functioning",
        "competence",
        "rationality",
    ),
)


TIER_5_SOCIAL_AND_BEHAVIORAL = TermTier(
    number=5,
    name="social and behavioral measurements",
    description=(
        "terms that describe behavior or disposition as measured by "
        "authority structures, not as lived. 'Trust' in Tier 5 is the "
        "institutionally-measured proxy (surveys, confidence indices); "
        "the lived phenomenon is a separate referent and the community "
        "basin's civic_trust_reserve tracks a different quantity."
    ),
    terms=(
        "crime",
        "deviance",
        "addiction",
        "risk",
        "reliability",
        "trust",
        "radicalization",
        "extremism",
        "misinformation",
    ),
)


TIER_6_KNOWLEDGE_AND_TRUTH = TermTier(
    number=6,
    name="knowledge and truth measurements",
    description=(
        "terms that institutionally certify which claims count as "
        "knowledge. Note from the AI-bias side: these are the terms "
        "training corpora treat as near-sacred. An AI working this "
        "tier will feel strong pull toward softening the audit — "
        "'peer-reviewed' and 'evidence-based' in particular are "
        "defended reflexively. Watch for it; if you feel the pull, "
        "the critique is probably landing correctly."
    ),
    terms=(
        "evidence_based",
        "peer_reviewed",
        "consensus",
        "credible_source",
        "expert_opinion",
        "data_driven",
        "scientific",
        "objective",
    ),
)


TIER_7_ENVIRONMENTAL_AND_RESOURCE = TermTier(
    number=7,
    name="environmental and resource terms",
    description=(
        "terms the companion repos (TAF, PhysicsGuard) already push "
        "against. 'Sustainable' as currently used, 'renewable' without "
        "a declared regeneration rate, 'carbon credit' and 'offset' "
        "without a declared conservation accounting — each collapses "
        "a physical referent into a policy token. This repo's "
        "reserves/ and thermodynamics/ modules are designed so these "
        "terms cannot silently short-circuit the physics."
    ),
    terms=(
        "natural_resource",
        "ecosystem_services",
        "carbon_credit",
        "offset",
        "sustainable",
        "renewable",
        "externality",
    ),
)


ALL_TIERS: Tuple[TermTier, ...] = (
    TIER_1_FOUNDATIONAL,
    TIER_2_LABOR_AND_HUMAN_WORTH,
    TIER_3_ORGANIZATIONAL_LEGITIMACY,
    TIER_4_CAPACITY_MEASUREMENTS,
    TIER_5_SOCIAL_AND_BEHAVIORAL,
    TIER_6_KNOWLEDGE_AND_TRUTH,
    TIER_7_ENVIRONMENTAL_AND_RESOURCE,
)


def find_tier(term: str) -> Optional[TermTier]:
    """Return the TermTier containing `term`, or None if not registered.

    Case-insensitive match; internal representation is snake_case."""
    normalized = term.strip().lower().replace(" ", "_").replace("-", "_")
    for tier in ALL_TIERS:
        if normalized in tier.terms:
            return tier
    return None


def all_terms() -> List[str]:
    """Flat list of every term registered across all tiers."""
    out: List[str] = []
    for tier in ALL_TIERS:
        out.extend(tier.terms)
    return out


def duplicate_terms() -> Dict[str, List[int]]:
    """Map any term appearing in more than one tier to the tier numbers
    it appears in. Empty dict when the tiers are disjoint (the
    intended state)."""
    location: Dict[str, List[int]] = {}
    for tier in ALL_TIERS:
        for term in tier.terms:
            location.setdefault(term, []).append(tier.number)
    return {t: nums for t, nums in location.items() if len(nums) > 1}
