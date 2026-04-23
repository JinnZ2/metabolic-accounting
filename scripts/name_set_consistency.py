"""
scripts/name_set_consistency.py

Bidirectional name-set consistency checks across multiple surfaces
in the codebase. For each declared pair (surface_a, surface_b),
compute both sets live from code and report both directions of
drift (missing_from_a, missing_from_b). If either direction is
non-empty, the surfaces have drifted and a maintainer must act.

Pattern borrowed from the Geometric-to-Binary-Computational-Bridge
repo's `validate_bridge_contract.py`, which uses the same structure
to assert that the same bridge-domain names appear in every
registry (manifest, solver registry, adapter catalog, domain
catalog) that claims to know about them.

Complement to `counts_consistency.py`:
  - counts_consistency is SCALAR — for each declared key, live ==
    declared count.
  - name_set_consistency is STRUCTURAL — for each declared pair,
    the two sets have the same elements (bidirectional).

A counts check would miss the case "set A and set B both have 9
elements but one element differs"; the name-set check catches that.

CC0. Stdlib-only. AUDIT_24.

Usage:
    python scripts/name_set_consistency.py

Exits non-zero with a drift table if any pair disagrees.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass
from typing import Callable, List, Set, Tuple


# ---------------------------------------------------------------------------
# Live set producers
# ---------------------------------------------------------------------------

def tier1_audit_terms() -> Set[str]:
    """Canonical set of Tier 1 audit terms (one per audited claim)."""
    from term_audit.audits.money import MONEY_AUDIT
    from term_audit.audits.value import ALL_VALUE_AUDITS
    from term_audit.audits.capital import ALL_CAPITAL_AUDITS
    names: Set[str] = {MONEY_AUDIT.term}
    for a in ALL_VALUE_AUDITS.values():
        names.add(a.term)
    for a in ALL_CAPITAL_AUDITS.values():
        names.add(a.term)
    return names


def morphism_graph_nodes() -> Set[str]:
    """Nodes in the Tier 1 morphism graph."""
    from term_audit.morphism_graph import build_tier1_morphism_graph
    return set(build_tier1_morphism_graph().node_names())


def counts_declared_keys() -> Set[str]:
    """Keys declared in scripts/counts_consistency.py DECLARED."""
    from scripts.counts_consistency import DECLARED
    return {k for (k, _, _, _) in DECLARED}


def counts_live_keys() -> Set[str]:
    """Keys returned by compute_live_counts()."""
    from scripts.counts_consistency import compute_live_counts
    return set(compute_live_counts().keys())


def money_case_names() -> Set[str]:
    """Names of money_signal historical anchor cases."""
    from money_signal.historical_cases import ALL_CASES
    return {c.name for c in ALL_CASES}


def investment_case_names() -> Set[str]:
    """Names of investment_signal historical anchor cases."""
    from investment_signal.historical_cases import ALL_CASES
    return {c.name for c in ALL_CASES}


def morphism_graph_audit_backed_nodes() -> Set[str]:
    """Morphism graph nodes whose `audit` field is populated. In the
    Tier 1 graph, every node should be audit-backed — collapsed-
    composite nodes still point at their collapsed TermAudit."""
    from term_audit.morphism_graph import build_tier1_morphism_graph
    g = build_tier1_morphism_graph()
    return {n.name for n in g.nodes() if n.audit is not None}


# ---------------------------------------------------------------------------
# Declared surface pairs
# ---------------------------------------------------------------------------
#
# Each entry is: (pair_label, surface_a_label, surface_a_producer,
#                 surface_b_label, surface_b_producer, anchor, rationale)

PAIRS = [
    (
        "tier1_audits_↔_morphism_graph_nodes",
        "tier1_audit_terms", tier1_audit_terms,
        "morphism_graph_nodes", morphism_graph_nodes,
        "AUDIT_24",
        "Every Tier 1 TermAudit.term must appear as a node in the "
        "Tier 1 morphism graph, and vice versa. Removes the "
        "hardcoded-expected-set drift risk in test_morphism_graph.",
    ),
    (
        "counts_declared_↔_counts_live",
        "counts_declared_keys", counts_declared_keys,
        "counts_live_keys", counts_live_keys,
        "AUDIT_24",
        "Every key declared in counts_consistency DECLARED must be "
        "computed by compute_live_counts, and every live key must "
        "be declared. Prior test_counts_consistency only checked "
        "one direction.",
    ),
    (
        "morphism_graph_nodes_↔_audit_backed_nodes",
        "morphism_graph_nodes", morphism_graph_nodes,
        "audit_backed_nodes", morphism_graph_audit_backed_nodes,
        "AUDIT_24",
        "Every node in the Tier 1 morphism graph should have a "
        "non-None audit field (including collapsed-composite nodes "
        "that point at their collapsed TermAudit). Orphan nodes "
        "would indicate graph-construction drift.",
    ),
]


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NameSetConsistencyRow:
    pair_label: str
    a_label: str
    b_label: str
    missing_from_a: Tuple[str, ...]   # in b but not in a
    missing_from_b: Tuple[str, ...]   # in a but not in b
    size_a: int
    size_b: int
    anchor: str
    rationale: str

    @property
    def ok(self) -> bool:
        return not self.missing_from_a and not self.missing_from_b


def build_rows() -> List[NameSetConsistencyRow]:
    rows: List[NameSetConsistencyRow] = []
    for (pair_label, a_label, a_fn, b_label, b_fn,
         anchor, rationale) in PAIRS:
        set_a = a_fn()
        set_b = b_fn()
        rows.append(NameSetConsistencyRow(
            pair_label=pair_label,
            a_label=a_label, b_label=b_label,
            missing_from_a=tuple(sorted(set_b - set_a)),
            missing_from_b=tuple(sorted(set_a - set_b)),
            size_a=len(set_a), size_b=len(set_b),
            anchor=anchor, rationale=rationale,
        ))
    return rows


def report(rows: List[NameSetConsistencyRow]) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append("Name-set consistency — bidirectional check across declared pairs")
    lines.append("=" * 78)
    for r in rows:
        status = "PASS" if r.ok else "DRIFT"
        lines.append("")
        lines.append(f"[{status}] {r.pair_label}")
        lines.append(f"    {r.a_label:<30s}  |{r.size_a}|")
        lines.append(f"    {r.b_label:<30s}  |{r.size_b}|")
        if not r.ok:
            if r.missing_from_a:
                lines.append(
                    f"    missing_from_{r.a_label}: "
                    f"{list(r.missing_from_a)}"
                )
            if r.missing_from_b:
                lines.append(
                    f"    missing_from_{r.b_label}: "
                    f"{list(r.missing_from_b)}"
                )
        lines.append(f"    anchor: {r.anchor}")
    lines.append("")
    lines.append("-" * 78)
    n_drift = sum(1 for r in rows if not r.ok)
    if n_drift == 0:
        lines.append(
            f"name-set consistency: {len(rows)}/{len(rows)} pairs agree"
        )
    else:
        lines.append(
            f"name-set consistency: {n_drift}/{len(rows)} pairs drifted"
        )
        lines.append("")
        lines.append(
            "Drift options: (a) legitimate change — update whichever "
            "surface is stale, commit, cite the AUDIT;"
        )
        lines.append(
            "               (b) regression — the side that lost the "
            "name is broken; find and fix."
        )
    return "\n".join(lines)


def main() -> int:
    rows = build_rows()
    print(report(rows))
    return 0 if all(r.ok for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
