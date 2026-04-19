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
"""

from .schema import (
    SIGNAL_CRITERIA,
    SignalScore,
    StandardSetter,
    FirstPrinciplesPurpose,
    TermAudit,
)

__all__ = [
    "SIGNAL_CRITERIA",
    "SignalScore",
    "StandardSetter",
    "FirstPrinciplesPurpose",
    "TermAudit",
]
