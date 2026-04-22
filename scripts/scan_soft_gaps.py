"""
scripts/scan_soft_gaps.py

Walk every Tier 1 TermAudit in the tree and report the soft gaps
each one carries. Produces a structured summary the caller can
use to prioritize follow-up work.

Soft gaps as of AUDIT_17 / AUDIT_19:
  - EMPIRICAL provenance with `scope_caveat` but no `scope_audit`
  - PLACEHOLDER provenance with `deferred_cost == "exponential"`

This script does NOT fix gaps — it surfaces them honestly so a
reader can decide what to attack next. Fixing an EMPIRICAL gap
requires reading the cited paper and populating a StudyScopeAudit;
fixing a PLACEHOLDER gap means retiring the placeholder by doing
the cited dataset extraction.

Named as AUDIT_17 § D.2 follow-up; shipped in AUDIT_21. CC0.
Stdlib-only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass
from typing import Dict, List, Tuple

from term_audit.audits.money import MONEY_AUDIT
from term_audit.audits.value import ALL_VALUE_AUDITS
from term_audit.audits.capital import ALL_CAPITAL_AUDITS
from term_audit.provenance import coverage_report


@dataclass(frozen=True)
class AuditSoftGapRow:
    """One row in the scan output."""
    audit_term: str
    total_provenances: int
    complete: int
    scope_audit_count: int
    soft_gap_count: int
    soft_gap_criteria: Tuple[str, ...]   # which criteria trip gaps


def scan() -> List[AuditSoftGapRow]:
    """Scan every known Tier 1 TermAudit and return per-audit rows."""
    rows: List[AuditSoftGapRow] = []
    for label, audit in _iter_audits():
        cov = audit.provenance_coverage()
        # Figure out which criteria tripped soft gaps
        tripped: List[str] = []
        for (idx, _kind, _msg) in cov["soft_gap_details"]:
            # idx is the index into audit.signal_scores
            if 0 <= idx < len(audit.signal_scores):
                tripped.append(audit.signal_scores[idx].criterion)
        rows.append(AuditSoftGapRow(
            audit_term=label,
            total_provenances=cov["total"],
            complete=cov["complete"],
            scope_audit_count=cov["scope_audit_count"],
            soft_gap_count=cov["soft_gap_count"],
            soft_gap_criteria=tuple(tripped),
        ))
    return rows


def _iter_audits():
    yield ("money", MONEY_AUDIT)
    for k, v in sorted(ALL_VALUE_AUDITS.items()):
        yield (f"value::{k}", v)
    for k, v in sorted(ALL_CAPITAL_AUDITS.items()):
        yield (f"capital::{k}", v)


def aggregate(rows: List[AuditSoftGapRow]) -> Dict[str, int]:
    """Aggregate totals across rows."""
    return {
        "n_audits": len(rows),
        "total_provenances": sum(r.total_provenances for r in rows),
        "total_complete": sum(r.complete for r in rows),
        "total_scope_audits_attached": sum(r.scope_audit_count for r in rows),
        "total_soft_gaps": sum(r.soft_gap_count for r in rows),
    }


def _render(rows: List[AuditSoftGapRow], agg: Dict[str, int]) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append("Tier 1 soft-gap scan")
    lines.append("=" * 78)
    lines.append(
        f"{'audit':<35s}  {'prov':>4s}  {'cmpl':>4s}  "
        f"{'audits':>6s}  {'gaps':>4s}  tripped"
    )
    lines.append("-" * 78)
    for r in rows:
        criteria = ",".join(r.soft_gap_criteria) if r.soft_gap_criteria else "-"
        lines.append(
            f"{r.audit_term:<35s}  {r.total_provenances:>4d}  "
            f"{r.complete:>4d}  {r.scope_audit_count:>6d}  "
            f"{r.soft_gap_count:>4d}  {criteria}"
        )
    lines.append("-" * 78)
    lines.append(f"totals:")
    lines.append(f"  audits scanned:           {agg['n_audits']}")
    lines.append(f"  provenance records:       {agg['total_provenances']}")
    lines.append(f"  complete:                 {agg['total_complete']}")
    lines.append(f"  scope_audits attached:    {agg['total_scope_audits_attached']}")
    lines.append(f"  soft_gaps remaining:      {agg['total_soft_gaps']}")
    lines.append("=" * 78)
    lines.append(
        "Retirement path: each soft gap corresponds to an EMPIRICAL "
        "record whose scope_caveat acknowledges a stretch without "
        "attaching a machine-readable StudyScopeAudit, OR a "
        "PLACEHOLDER record flagged as exponential-cost. Each requires "
        "per-citation work: read the cited paper, populate the "
        "StudyScopeAudit's six layers from the published methodology, "
        "attach. Not a one-shot retrofit."
    )
    return "\n".join(lines)


def main() -> int:
    rows = scan()
    agg = aggregate(rows)
    print(_render(rows, agg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
