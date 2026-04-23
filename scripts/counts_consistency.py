"""
scripts/counts_consistency.py

Compute every load-bearing count from code and compare against the
declared baseline. Tripwires drift between what STATUS.md / audit
docs claim and what the codebase actually contains.

Pattern borrowed from physics-playground's counts-consistency table:
the repo makes many numeric claims (test count, Tier 1 audit count,
provenance count, morphism graph shape, historical-case counts,
match rates). Every one of these is computable from code. If the
baseline drifts below/above the actual count, that is either:
  (a) a real change the maintainer must acknowledge (bump the
      baseline, explain why in a new AUDIT_XX.md), or
  (b) silent drift that this script + its test catch early.

CC0. Stdlib-only. AUDIT_23 § B.

Usage:
    python scripts/counts_consistency.py

Exits non-zero and prints a drift table if any count disagrees with
the declared baseline.
"""

import sys
import os
import glob
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass
from typing import Callable, Dict, List


# ---------------------------------------------------------------------------
# Declared baseline (the "should be" number; load-bearing)
# ---------------------------------------------------------------------------
#
# Each entry is: (key, declared_count, audit_anchor, rationale).
# The audit_anchor names where the count is the load-bearing claim.
# Updating a declared_count here should be rare and paired with a
# new AUDIT_XX.md entry that explains why it changed.

DECLARED = [
    # (key, declared, anchor, rationale)
    ("test_files", 53, "AUDIT_23 § B",
     "53 test_*.py files in tests/ after morphism_graph + "
     "counts_consistency tests added"),

    ("tier1_audits", 9, "AUDIT_07 + AUDIT_21",
     "9 Tier 1 TermAudits: money + 4 value (collapsed/A/B/C) + "
     "4 capital (collapsed/A/B/C)"),

    ("provenance_total", 63, "AUDIT_07 § D",
     "63 SignalScore provenance records across the 9 Tier 1 audits "
     "(9 audits * 7 criteria = 63)"),
    ("provenance_complete", 63, "AUDIT_07 § D",
     "63/63 complete — AUDIT_07's discipline that every provenance "
     "record carries complete evidence"),
    ("scope_audits_attached", 4, "AUDIT_21 § B",
     "4 StudyScopeAudits attached: Boskin CPI, BoE 2014 Money "
     "Creation, Balassa PPP, FASB ASC 820 (all on money.py)"),
    ("soft_gaps_remaining", 12, "AUDIT_21 § A.2",
     "14 soft gaps at AUDIT_19 baseline minus 2 resolved in "
     "AUDIT_21 § B = 12 remaining"),

    ("money_cases", 13, "AUDIT_22 Part A",
     "13 money_signal historical anchor cases: Weimar, Zimbabwe, "
     "GFC, Cyprus, Argentina, Bitcoin, Roman denarius, Yap, Kula, "
     "Haudenosaunee wampum, potlatch suppression, Andean ayni, "
     "Tambu Tolai"),
    ("money_matches", 12, "AUDIT_22 Part C",
     "12/13 match (Cyprus remains the documented observer-asymmetry "
     "outlier)"),

    ("investment_cases", 11, "AUDIT_22 Part B",
     "11 investment_signal anchor cases: Enron, MBS, GIG, CLT, "
     "Colonial, 401k, ZIRP retail/PE/CLO, Congo rubber, Amazon rubber"),
    ("investment_matches", 11, "AUDIT_22 Part C",
     "11/11 match — all investment_signal anchors exhibit their "
     "predicted failure signatures"),

    ("morphism_graph_nodes", 9, "AUDIT_23 § A.4",
     "9 nodes: one per Tier 1 audit"),
    ("morphism_graph_edges", 20, "AUDIT_23 § A.4",
     "20 edges total = 11 linkage + 9 inheritance"),
    ("morphism_graph_linkage_edges", 11, "AUDIT_23 § A.4",
     "11 linkage edges = 5 ValueLinkages + 6 CapitalLinkages"),
    ("morphism_graph_inheritance_edges", 9, "AUDIT_23 § A.2",
     "9 inheritance edges = 3 docstring claims + 3 value "
     "decomposition + 3 capital decomposition"),
    ("morphism_graph_components", 1, "AUDIT_23 § A.4",
     "Graph is weakly connected (1 weakly-connected component)"),
]


# ---------------------------------------------------------------------------
# Live computation
# ---------------------------------------------------------------------------

def _count_test_files() -> int:
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return len(glob.glob(os.path.join(here, "tests", "test_*.py")))


def _tier1_audits():
    from term_audit.audits.money import MONEY_AUDIT
    from term_audit.audits.value import ALL_VALUE_AUDITS
    from term_audit.audits.capital import ALL_CAPITAL_AUDITS
    return ([MONEY_AUDIT]
            + list(ALL_VALUE_AUDITS.values())
            + list(ALL_CAPITAL_AUDITS.values()))


def _provenance_stats() -> Dict[str, int]:
    total = 0
    complete = 0
    scope_audits = 0
    soft_gaps = 0
    for a in _tier1_audits():
        for s in a.signal_scores:
            p = s.provenance
            if p is None:
                continue
            total += 1
            if p.is_complete():
                complete += 1
            if p.has_scope_audit():
                scope_audits += 1
            if p.soft_gap():
                soft_gaps += 1
    return {
        "provenance_total": total,
        "provenance_complete": complete,
        "scope_audits_attached": scope_audits,
        "soft_gaps_remaining": soft_gaps,
    }


def _money_stats() -> Dict[str, int]:
    from money_signal.historical_cases import ALL_CASES, compare_case
    match = sum(1 for c in ALL_CASES if compare_case(c).qualitative_match)
    return {"money_cases": len(ALL_CASES), "money_matches": match}


def _investment_stats() -> Dict[str, int]:
    from investment_signal.historical_cases import ALL_CASES, compare_case
    match = sum(1 for c in ALL_CASES if compare_case(c).predicted_contains_observed)
    return {"investment_cases": len(ALL_CASES), "investment_matches": match}


def _graph_stats() -> Dict[str, int]:
    from term_audit.morphism_graph import (
        build_tier1_morphism_graph, EdgeRelation,
    )
    g = build_tier1_morphism_graph()
    return {
        "morphism_graph_nodes": g.n_nodes(),
        "morphism_graph_edges": g.n_edges(),
        "morphism_graph_linkage_edges": len(
            g.edges_by_relation(EdgeRelation.LINKAGE)
        ),
        "morphism_graph_inheritance_edges": len(
            g.edges_by_relation(EdgeRelation.INHERITANCE)
        ),
        "morphism_graph_components": len(g.weakly_connected_components()),
    }


def compute_live_counts() -> Dict[str, int]:
    """Compute every key live from code. No cached state; each call
    walks the audit tree."""
    out: Dict[str, int] = {}
    out["test_files"] = _count_test_files()
    out["tier1_audits"] = len(_tier1_audits())
    out.update(_provenance_stats())
    out.update(_money_stats())
    out.update(_investment_stats())
    out.update(_graph_stats())
    return out


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CountsConsistencyRow:
    """One row of the consistency table."""
    key: str
    declared: int
    live: int
    anchor: str
    rationale: str

    @property
    def ok(self) -> bool:
        return self.declared == self.live

    @property
    def drift(self) -> int:
        return self.live - self.declared


def build_rows() -> List[CountsConsistencyRow]:
    live = compute_live_counts()
    rows: List[CountsConsistencyRow] = []
    for key, declared, anchor, rationale in DECLARED:
        rows.append(CountsConsistencyRow(
            key=key, declared=declared,
            live=live.get(key, -1),
            anchor=anchor, rationale=rationale,
        ))
    return rows


def report(rows: List[CountsConsistencyRow]) -> str:
    lines = []
    lines.append("=" * 90)
    lines.append(
        f"{'key':<36s}  {'declared':>8s}  {'live':>6s}  "
        f"{'drift':>6s}  ok   anchor"
    )
    lines.append("-" * 90)
    for r in rows:
        ok_marker = "PASS" if r.ok else "DRIFT"
        drift = f"{r.drift:+d}" if not r.ok else "0"
        lines.append(
            f"{r.key:<36s}  {r.declared:>8d}  {r.live:>6d}  "
            f"{drift:>6s}  {ok_marker:<5s} {r.anchor}"
        )
    lines.append("-" * 90)
    n_drift = sum(1 for r in rows if not r.ok)
    if n_drift == 0:
        lines.append(
            f"counts consistency: {len(rows)}/{len(rows)} rows match declared baseline"
        )
    else:
        lines.append(
            f"counts consistency: {n_drift}/{len(rows)} rows drifted from baseline"
        )
        lines.append("")
        lines.append(
            "Drift options: (a) legitimate change — bump the DECLARED "
            "entry AND cite a new AUDIT_XX.md;"
        )
        lines.append(
            "               (b) regression — find what broke the count "
            "and fix it."
        )
    return "\n".join(lines)


def main() -> int:
    rows = build_rows()
    print(report(rows))
    return 0 if all(r.ok for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
