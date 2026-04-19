"""
term_audit/

Auditing economic terms against information-theoretic signal criteria and
against their own first-principles purpose. A term that fails three or more
of the seven signal criteria is not a signal — it is a token that has
learned to occupy a signal-shaped position in discourse.

Sits alongside the main accounting stack rather than inside it: the main
pipeline computes verdicts for firms; term_audit computes verdicts for the
terms firms (and economists, regulators, analysts) use to describe
themselves. Aligned with the narrative-stripper concept in the parent
thermodynamic-accountability-framework (see docs/RELATED.md).

Two modules:
  - schema.py:   score an economic term against the seven signal criteria
                 after the fact.
  - scoping.py:  codify the dimensions that WOULD need to be declared in
                 advance for the term to function as a measurement in a
                 given use. See docs/SCOPING_ECONOMIC_TERMS.md for the
                 full argument and worked expansions.
"""

from .schema import (
    SIGNAL_CRITERIA,
    SignalScore,
    StandardSetter,
    FirstPrinciplesPurpose,
    TermAudit,
)
from .scoping import (
    SCOPING_DIMENSIONS,
    SCOPING_DIMENSION_NAMES,
    DeclaredScope,
)
from .tiers import (
    TermTier,
    ALL_TIERS,
    TIER_1_FOUNDATIONAL,
    TIER_2_LABOR_AND_HUMAN_WORTH,
    TIER_3_ORGANIZATIONAL_LEGITIMACY,
    TIER_4_CAPACITY_MEASUREMENTS,
    TIER_5_SOCIAL_AND_BEHAVIORAL,
    TIER_6_KNOWLEDGE_AND_TRUTH,
    TIER_7_ENVIRONMENTAL_AND_RESOURCE,
    find_tier,
    all_terms,
    duplicate_terms,
)
from .status_extraction import (
    EnergyFlows,
    ToleranceBand,
    MeasurementSystem,
    StatusExtractionModel,
    FALSIFIABLE_PREDICTIONS,
    example_run,
)

__all__ = [
    "SIGNAL_CRITERIA",
    "SignalScore",
    "StandardSetter",
    "FirstPrinciplesPurpose",
    "TermAudit",
    "SCOPING_DIMENSIONS",
    "SCOPING_DIMENSION_NAMES",
    "DeclaredScope",
    "TermTier",
    "ALL_TIERS",
    "TIER_1_FOUNDATIONAL",
    "TIER_2_LABOR_AND_HUMAN_WORTH",
    "TIER_3_ORGANIZATIONAL_LEGITIMACY",
    "TIER_4_CAPACITY_MEASUREMENTS",
    "TIER_5_SOCIAL_AND_BEHAVIORAL",
    "TIER_6_KNOWLEDGE_AND_TRUTH",
    "TIER_7_ENVIRONMENTAL_AND_RESOURCE",
    "find_tier",
    "all_terms",
    "duplicate_terms",
    "EnergyFlows",
    "ToleranceBand",
    "MeasurementSystem",
    "StatusExtractionModel",
    "FALSIFIABLE_PREDICTIONS",
    "example_run",
]

