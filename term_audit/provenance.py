"""
term_audit/provenance.py

Provenance taxonomy for numeric and structural choices.

Core claim: "back every number with a citation" is the right instinct
but fails as a flat rule, because not every decision in the framework
is an empirical claim. Some are derivations, some are design choices,
some are placeholders, some are part of the definition. Forcing a
citation on a design choice produces performative references that
do not actually support the claim — worse than nothing.

This module encodes five kinds of provenance and the field required
to make each one honest:

  EMPIRICAL      measurement from a peer-reviewed study
                 -> requires source_refs (+ scope_caveat if applying
                    the study outside what it actually measured)

  THEORETICAL    derivable from a conservation law, identity, or
                 information-theoretic constraint
                 -> requires source_refs to the derivation, OR a
                    rationale naming the law invoked

  DESIGN_CHOICE  structural decision (e.g. 5-of-7 signal threshold,
                 multiplicative vs additive aggregation)
                 -> requires alternatives_considered AND
                    falsification_test (what would show this choice
                    wrong)

  PLACEHOLDER    acknowledged guess, pending a real derivation or
                 measurement
                 -> requires retirement_path naming the study or
                    derivation that would replace it

  STIPULATIVE    part of the definition itself (V_A = use-value by
                 construction; a dollar is a dollar by statute)
                 -> requires definition_ref OR rationale

A sixth field, `knowledge_dna`, is a free-form pass-through for
external provenance systems (e.g. Knowledge DNA lineage hashes).
The framework does not interpret it; it propagates it with the
claim so downstream systems can validate.

Audit-of-itself: `Provenance.missing_fields()` returns the fields
required-but-missing for the stated kind. `provenance_coverage()` on
TermAudit (see schema.py) aggregates this into a report.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional


class ProvenanceKind(Enum):
    """Classification of how a numeric or structural choice is justified."""
    EMPIRICAL = "empirical"
    THEORETICAL = "theoretical"
    DESIGN_CHOICE = "design_choice"
    PLACEHOLDER = "placeholder"
    STIPULATIVE = "stipulative"


@dataclass
class Provenance:
    """Provenance record for a single numeric or structural choice.

    Every SignalScore, linkage strength_estimate, equation coefficient,
    and threshold in the framework should carry one of these. What
    constitutes "complete" depends on kind — see module docstring.
    """
    kind: ProvenanceKind

    # EMPIRICAL / THEORETICAL: citations
    source_refs: List[str] = field(default_factory=list)

    # EMPIRICAL: what the study actually measured vs how we are using it
    # (e.g., "soil-carbon regen measured on Iowa corn belt; applied here
    # to generic soil basin — Mediterranean soils likely differ")
    scope_caveat: str = ""

    # DESIGN_CHOICE: what else was considered and why this one won
    alternatives_considered: List[str] = field(default_factory=list)

    # EMPIRICAL / THEORETICAL / DESIGN_CHOICE: the test that would show
    # the choice is wrong. For EMPIRICAL this is often redundant with
    # the study's own methodology; for DESIGN_CHOICE it is required
    # because design choices are otherwise unfalsifiable.
    falsification_test: str = ""

    # PLACEHOLDER: the study, derivation, or measurement that would
    # retire this placeholder and what it would take to produce it
    retirement_path: str = ""

    # STIPULATIVE: pointer to the definition
    definition_ref: str = ""

    # Always useful: the reason this choice was made, not what it is
    rationale: str = ""

    # Free-form pass-through for external provenance / lineage systems
    # (e.g., Knowledge DNA). Framework does not interpret; propagates.
    knowledge_dna: str = ""

    # AUDIT_17 integration: optional attachment to a StudyScopeAudit
    # from term_audit/study_scope_audit.py. The type is `Any` here
    # to avoid the provenance <-> study_scope_audit circular import;
    # callers typically attach a StudyScopeAudit instance. Absence
    # is NOT a missing_fields() failure — attaching is a coverage
    # improvement surfaced by soft_gap_report(), not a required
    # field that would break the Tier 1 retrofit's 74/74 coverage.
    scope_audit: Optional[Any] = None

    def missing_fields(self) -> List[str]:
        """Return names of fields required-but-missing for this kind.

        Empty list = provenance is complete. Non-empty list = the audit
        is incomplete in a specific, named way. This is the surface the
        framework uses to audit itself.
        """
        missing: List[str] = []
        if self.kind == ProvenanceKind.EMPIRICAL:
            if not self.source_refs:
                missing.append("source_refs")
        elif self.kind == ProvenanceKind.THEORETICAL:
            if not self.source_refs and not self.rationale.strip():
                missing.append("source_refs_or_rationale")
        elif self.kind == ProvenanceKind.DESIGN_CHOICE:
            if not self.alternatives_considered:
                missing.append("alternatives_considered")
            if not self.falsification_test.strip():
                missing.append("falsification_test")
        elif self.kind == ProvenanceKind.PLACEHOLDER:
            if not self.retirement_path.strip():
                missing.append("retirement_path")
        elif self.kind == ProvenanceKind.STIPULATIVE:
            if not self.definition_ref.strip() and not self.rationale.strip():
                missing.append("definition_ref_or_rationale")
        return missing

    def is_complete(self) -> bool:
        """True iff every field required by this kind is filled in."""
        return not self.missing_fields()

    def has_scope_audit(self) -> bool:
        """True iff a StudyScopeAudit (or equivalent attachment) is
        present on this Provenance record. Not required for
        `is_complete()` — this is a soft coverage signal."""
        return self.scope_audit is not None

    def soft_gap(self) -> Optional[str]:
        """Report a soft coverage gap that does NOT invalidate
        completeness but flags a recommended attachment.

        Current soft gap: an EMPIRICAL provenance that declares a
        `scope_caveat` (i.e., the author has explicitly noted that
        the study measured X but the framework is applying it to Y)
        but has no `scope_audit` attached. The caveat says "we know
        the scope is being stretched"; without a scope_audit, the
        framework has no machine-readable record of WHERE it holds
        vs where it fails.

        Returns the soft-gap description string, or None.
        """
        if (self.kind == ProvenanceKind.EMPIRICAL
                and self.scope_caveat.strip()
                and not self.has_scope_audit()):
            return (
                "EMPIRICAL provenance declares a scope_caveat but has "
                "no scope_audit attached — the author acknowledged the "
                "scope stretch in prose but the framework has no "
                "machine-readable scope-boundary record"
            )
        return None


def empirical(
    source_refs: List[str],
    rationale: str = "",
    scope_caveat: str = "",
    falsification_test: str = "",
    knowledge_dna: str = "",
    scope_audit: Optional[Any] = None,
) -> Provenance:
    """Constructor for empirical provenance. Enforces source_refs at build.

    AUDIT_17: optional `scope_audit` attachment (typically a
    StudyScopeAudit from term_audit/study_scope_audit.py). When
    present, it carries a machine-readable boundary record
    complementing the prose `scope_caveat`. When absent AND a
    scope_caveat is declared, `soft_gap()` surfaces the gap.
    """
    if not source_refs:
        raise ValueError("empirical provenance requires source_refs")
    return Provenance(
        kind=ProvenanceKind.EMPIRICAL,
        source_refs=list(source_refs),
        rationale=rationale,
        scope_caveat=scope_caveat,
        falsification_test=falsification_test,
        knowledge_dna=knowledge_dna,
        scope_audit=scope_audit,
    )


def theoretical(
    rationale: str,
    source_refs: Optional[List[str]] = None,
    falsification_test: str = "",
    knowledge_dna: str = "",
) -> Provenance:
    """Constructor for theoretical provenance.

    A derivation from a conservation law or identity. If the derivation
    is published, source_refs points to it; rationale is still required
    because a ref without a stated rationale cannot be verified at the
    call site.
    """
    if not rationale.strip():
        raise ValueError("theoretical provenance requires a rationale")
    return Provenance(
        kind=ProvenanceKind.THEORETICAL,
        rationale=rationale,
        source_refs=list(source_refs) if source_refs else [],
        falsification_test=falsification_test,
        knowledge_dna=knowledge_dna,
    )


def design_choice(
    rationale: str,
    alternatives_considered: List[str],
    falsification_test: str,
    knowledge_dna: str = "",
) -> Provenance:
    """Constructor for a design-choice provenance.

    All three fields are load-bearing: without alternatives, the choice
    is undefended; without a falsification test, it is unfalsifiable.
    """
    if not alternatives_considered:
        raise ValueError("design_choice requires alternatives_considered")
    if not falsification_test.strip():
        raise ValueError("design_choice requires falsification_test")
    return Provenance(
        kind=ProvenanceKind.DESIGN_CHOICE,
        rationale=rationale,
        alternatives_considered=list(alternatives_considered),
        falsification_test=falsification_test,
        knowledge_dna=knowledge_dna,
    )


def placeholder(
    rationale: str,
    retirement_path: str,
    knowledge_dna: str = "",
) -> Provenance:
    """Constructor for placeholder provenance.

    The retirement_path is not optional. A placeholder without a
    retirement path is indistinguishable from a silently-accepted
    guess.
    """
    if not retirement_path.strip():
        raise ValueError("placeholder requires retirement_path")
    return Provenance(
        kind=ProvenanceKind.PLACEHOLDER,
        rationale=rationale,
        retirement_path=retirement_path,
        knowledge_dna=knowledge_dna,
    )


def stipulative(
    rationale: str,
    definition_ref: str = "",
    knowledge_dna: str = "",
) -> Provenance:
    """Constructor for stipulative provenance (part of the definition)."""
    if not rationale.strip() and not definition_ref.strip():
        raise ValueError("stipulative requires definition_ref or rationale")
    return Provenance(
        kind=ProvenanceKind.STIPULATIVE,
        rationale=rationale,
        definition_ref=definition_ref,
        knowledge_dna=knowledge_dna,
    )


def coverage_report(provenances: List[Optional[Provenance]]) -> dict:
    """Aggregate coverage across a list of Provenance records.

    Returns:
      total                total number of slots
      with_provenance      number that have any Provenance attached
      complete             number with Provenance whose missing_fields
                           is empty
      incomplete           number with Provenance but missing required
                           fields
      none                 number with no Provenance at all
      by_kind              count per ProvenanceKind for attached ones
      incomplete_details   list of (index, kind, missing_fields) for
                           each incomplete entry
      knowledge_dna_count  number of entries with a non-empty
                           knowledge_dna field
      scope_audit_count    AUDIT_17: number of entries with a
                           StudyScopeAudit attached
      soft_gap_count       AUDIT_17: number of entries where
                           soft_gap() returns non-None — coverage
                           improvement signal, not a failure
      soft_gap_details     list of (index, kind, gap_description)

    This is the surface used by TermAudit.provenance_coverage() and by
    tests that assert the framework has audited itself for gaps.
    """
    total = len(provenances)
    with_prov = 0
    complete = 0
    incomplete = 0
    none_count = 0
    by_kind = {k.value: 0 for k in ProvenanceKind}
    incomplete_details = []
    dna_count = 0
    scope_audit_count = 0
    soft_gap_count = 0
    soft_gap_details: List = []

    for idx, p in enumerate(provenances):
        if p is None:
            none_count += 1
            continue
        with_prov += 1
        by_kind[p.kind.value] += 1
        if p.knowledge_dna.strip():
            dna_count += 1
        if p.has_scope_audit():
            scope_audit_count += 1
        gap = p.soft_gap()
        if gap is not None:
            soft_gap_count += 1
            soft_gap_details.append((idx, p.kind.value, gap))
        missing = p.missing_fields()
        if missing:
            incomplete += 1
            incomplete_details.append((idx, p.kind.value, missing))
        else:
            complete += 1

    return {
        "total": total,
        "with_provenance": with_prov,
        "complete": complete,
        "incomplete": incomplete,
        "none": none_count,
        "by_kind": by_kind,
        "incomplete_details": incomplete_details,
        "knowledge_dna_count": dna_count,
        "scope_audit_count": scope_audit_count,
        "soft_gap_count": soft_gap_count,
        "soft_gap_details": soft_gap_details,
    }
