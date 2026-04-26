"""
term_audit/morphism_graph.py

Minimal stdlib-only directed-graph representation over the Tier 1
term-audit claim space.

Pattern borrowed from the physics-playground repo's
`graph.py::EquationGraph` (90 physics equations, 112 weighted
morphism edges, weakly-connected invariant). Adapted for the term-
audit domain: nodes are named claims (money, V_A, V_B, V_C, K_A,
K_B, K_C + two collapsed composites), edges carry sign + strength
+ relation_type. Written stdlib-only so it fits this repo's CC0
discipline.

AUDIT_23 § A. Closes AUDIT_07 § C.2 (inheritance invariant as
code) via `test_morphism_graph.py`.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Set, Tuple


class EdgeRelation(Enum):
    """How two claim nodes relate to each other.

    LINKAGE edges come from the ValueLinkage / CapitalLinkage arrays
    — the framework's explicit directed coupling between decomposed
    claim components.

    INHERITANCE edges encode the prose-level 'X inherits signal-
    failure from Y' claim made in the audit docstrings. AUDIT_07
    § C.2 named this as uncoded; the graph now makes it machine-
    checkable.
    """
    LINKAGE = "linkage"
    INHERITANCE = "inheritance"


class EdgeSign(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CONDITIONAL = "conditional"
    NONE = "none"


@dataclass(frozen=True)
class GraphNode:
    """One claim in the graph. `name` is the lookup key; `audit`
    carries the TermAudit (or None for composite / abstract nodes);
    `metadata` is free-form for per-node tags."""
    name: str
    audit: object = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdge:
    """One directed edge with sign + strength + relation type."""
    source: str
    target: str
    sign: EdgeSign
    strength: float
    relation: EdgeRelation
    # Optional rationale text (human-readable evidence)
    rationale: str = ""


# ---------------------------------------------------------------------------
# MorphismGraph — stdlib-only directed graph
# ---------------------------------------------------------------------------

class MorphismGraph:
    """Minimal directed graph. Not a drop-in NetworkX replacement —
    just what AUDIT_23 needs: add_node, add_edge, neighbors,
    weakly_connected_components, shortest_path (BFS), reachable.

    No external deps. Nodes indexed by name (string). Edges stored
    as (source, target) -> GraphEdge in a dict-of-dict adjacency
    structure.
    """

    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        # Forward and reverse adjacency for efficient weakly-connected
        # traversal without double-bookkeeping in callers.
        self._fwd: Dict[str, Dict[str, GraphEdge]] = {}
        self._rev: Dict[str, Dict[str, GraphEdge]] = {}

    # ----- Construction -----

    def add_node(self, node: GraphNode) -> None:
        if node.name in self._nodes:
            raise ValueError(f"duplicate node name: {node.name}")
        self._nodes[node.name] = node
        self._fwd.setdefault(node.name, {})
        self._rev.setdefault(node.name, {})

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source not in self._nodes:
            raise ValueError(f"edge source not in graph: {edge.source}")
        if edge.target not in self._nodes:
            raise ValueError(f"edge target not in graph: {edge.target}")
        if edge.target in self._fwd[edge.source]:
            raise ValueError(
                f"duplicate edge {edge.source} -> {edge.target}; "
                "multi-edges not supported"
            )
        self._fwd[edge.source][edge.target] = edge
        self._rev[edge.target][edge.source] = edge

    # ----- Queries -----

    def nodes(self) -> List[GraphNode]:
        return list(self._nodes.values())

    def node_names(self) -> List[str]:
        return list(self._nodes.keys())

    def edges(self) -> List[GraphEdge]:
        return [e for nbrs in self._fwd.values() for e in nbrs.values()]

    def successors(self, name: str) -> List[str]:
        return list(self._fwd.get(name, {}).keys())

    def predecessors(self, name: str) -> List[str]:
        return list(self._rev.get(name, {}).keys())

    def edge(self, source: str, target: str) -> Optional[GraphEdge]:
        return self._fwd.get(source, {}).get(target)

    def has_edge(self, source: str, target: str) -> bool:
        return target in self._fwd.get(source, {})

    def in_degree(self, name: str) -> int:
        return len(self._rev.get(name, {}))

    def out_degree(self, name: str) -> int:
        return len(self._fwd.get(name, {}))

    def n_nodes(self) -> int:
        return len(self._nodes)

    def n_edges(self) -> int:
        return sum(len(nbrs) for nbrs in self._fwd.values())

    # ----- Traversal -----

    def reachable_from(self, start: str) -> Set[str]:
        """Forward-reachable set (BFS on directed edges)."""
        if start not in self._nodes:
            raise KeyError(start)
        seen: Set[str] = set()
        frontier = [start]
        while frontier:
            nxt: List[str] = []
            for node in frontier:
                if node in seen:
                    continue
                seen.add(node)
                nxt.extend(self._fwd.get(node, {}).keys())
            frontier = nxt
        return seen

    def undirected_reachable(self, start: str) -> Set[str]:
        """Reachable set ignoring edge direction (for weakly-
        connected-component analysis)."""
        if start not in self._nodes:
            raise KeyError(start)
        seen: Set[str] = set()
        frontier = [start]
        while frontier:
            nxt: List[str] = []
            for node in frontier:
                if node in seen:
                    continue
                seen.add(node)
                nxt.extend(self._fwd.get(node, {}).keys())
                nxt.extend(self._rev.get(node, {}).keys())
            frontier = nxt
        return seen

    def weakly_connected_components(self) -> List[Set[str]]:
        """Partition nodes into weakly-connected components."""
        remaining: Set[str] = set(self._nodes.keys())
        components: List[Set[str]] = []
        while remaining:
            start = next(iter(remaining))
            comp = self.undirected_reachable(start)
            components.append(comp)
            remaining -= comp
        return components

    def is_weakly_connected(self) -> bool:
        """True iff the graph has exactly one weakly-connected
        component. Tripwire: AUDIT_07 § C.2's inheritance-invariant
        work requires every Tier 1 claim node to be at least
        weakly reachable from every other."""
        if not self._nodes:
            return True
        return len(self.weakly_connected_components()) == 1

    def isolated_nodes(self) -> List[str]:
        """Nodes with zero in- and zero out-degree."""
        return [n for n in self._nodes
                if self.in_degree(n) == 0 and self.out_degree(n) == 0]

    # ----- Edge queries by relation / sign -----

    def edges_by_relation(self, relation: EdgeRelation) -> List[GraphEdge]:
        return [e for e in self.edges() if e.relation == relation]

    def edges_by_sign(self, sign: EdgeSign) -> List[GraphEdge]:
        return [e for e in self.edges() if e.sign == sign]

    # ----- Display -----

    def describe(self) -> str:
        lines = [
            f"MorphismGraph: {self.n_nodes()} nodes, {self.n_edges()} edges",
            f"  weakly connected: {self.is_weakly_connected()}",
            f"  components:       {len(self.weakly_connected_components())}",
            f"  isolated nodes:   {self.isolated_nodes() or '-'}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Construct the Tier 1 morphism graph
# ---------------------------------------------------------------------------

# Node naming convention: the audit's `term` field from its TermAudit
# (money / value_collapsed_current_usage / value_A_use_value /
# value_B_exchange_value / value_C_substrate_value /
# capital_collapsed_current_usage / capital_A_productive /
# capital_B_financial / capital_C_institutional). This matches the
# existing TermAudit.term field so tests can reference identifiers
# that are already canonical.

_INHERITANCE_EDGES = [
    # money dominantly inherits from V_B (exchange-value). Prose
    # in money.py: "money's multi-referent structure is established
    # in classical monetary theory ... value_B inherits money's
    # unit_invariant failure." The inheritance direction is
    # money <- V_B: money's signal-failure is a consequence of
    # value-the-collapsed-term's failure, which is dominated by V_B.
    # Edge direction encodes "X INHERITS FROM Y": source=Y, target=X.
    ("value_B_exchange_value", "money",
     EdgeSign.NEGATIVE, 0.9, EdgeRelation.INHERITANCE,
     "money as signal inherits V_B-dominated collapse-failure per "
     "money.py module docstring"),

    # K_B inherits from V_B. capital.py module docstring: "K_B
    # inherits from V_B (exchange-value)."
    ("value_B_exchange_value", "capital_B_financial",
     EdgeSign.NEGATIVE, 0.9, EdgeRelation.INHERITANCE,
     "K_B financial claims inherit V_B exchange-value failure"),

    # K_A anchors to V_C (substrate-value). capital.py module
    # docstring: "K_A inherits from V_C (substrate-value)."
    ("value_C_substrate_value", "capital_A_productive",
     EdgeSign.POSITIVE, 0.9, EdgeRelation.INHERITANCE,
     "K_A productive anchors to V_C substrate-value signal quality"),

    # Decompositions: collapsed audits are consequences of their
    # components. Direction = from component to composite.
    ("value_A_use_value", "value_collapsed_current_usage",
     EdgeSign.POSITIVE, 0.5, EdgeRelation.INHERITANCE,
     "collapsed 'value' as used in discourse fuses V_A into token"),
    ("value_B_exchange_value", "value_collapsed_current_usage",
     EdgeSign.POSITIVE, 0.9, EdgeRelation.INHERITANCE,
     "collapsed 'value' is dominated by V_B in practice"),
    ("value_C_substrate_value", "value_collapsed_current_usage",
     EdgeSign.POSITIVE, 0.2, EdgeRelation.INHERITANCE,
     "collapsed 'value' rarely includes V_C in practice"),

    ("capital_A_productive", "capital_collapsed_current_usage",
     EdgeSign.POSITIVE, 0.3, EdgeRelation.INHERITANCE,
     "collapsed 'capital' sometimes invokes K_A (replacement-cost)"),
    ("capital_B_financial", "capital_collapsed_current_usage",
     EdgeSign.POSITIVE, 0.9, EdgeRelation.INHERITANCE,
     "collapsed 'capital' is dominated by K_B in practice"),
    ("capital_C_institutional", "capital_collapsed_current_usage",
     EdgeSign.POSITIVE, 0.1, EdgeRelation.INHERITANCE,
     "collapsed 'capital' rarely includes K_C in practice"),
]


def _sign_from_linkage_relation(relation_str: str) -> EdgeSign:
    return {
        "positive": EdgeSign.POSITIVE,
        "negative": EdgeSign.NEGATIVE,
        "conditional": EdgeSign.CONDITIONAL,
        "none": EdgeSign.NONE,
    }.get(relation_str, EdgeSign.NONE)


def _normalize_value_node(short: str) -> str:
    """ValueLinkage uses 'V_A', 'V_B', 'V_C' short labels. Convert
    to the TermAudit.term form used as graph node names."""
    return {
        "V_A": "value_A_use_value",
        "V_B": "value_B_exchange_value",
        "V_C": "value_C_substrate_value",
    }[short]


def _normalize_capital_node(short: str) -> str:
    return {
        "K_A": "capital_A_productive",
        "K_B": "capital_B_financial",
        "K_C": "capital_C_institutional",
    }[short]


def build_tier1_morphism_graph() -> MorphismGraph:
    """Assemble the Tier 1 morphism graph from existing artifacts:

    - Nodes: the 9 TermAudits (MONEY_AUDIT + 4 value + 4 capital).
    - Linkage edges: from VALUE_LINKAGES (5) and CAPITAL_LINKAGES (6).
    - Inheritance edges: the 9 prose-level inheritance claims in
      money.py and capital.py, now encoded explicitly.

    Total: 9 nodes, 20 edges (11 linkage + 9 inheritance).
    """
    from term_audit.audits.money import MONEY_AUDIT
    from term_audit.audits.value import ALL_VALUE_AUDITS, VALUE_LINKAGES
    from term_audit.audits.capital import ALL_CAPITAL_AUDITS, CAPITAL_LINKAGES

    g = MorphismGraph()

    # --- Nodes ---
    g.add_node(GraphNode(name=MONEY_AUDIT.term, audit=MONEY_AUDIT))
    for _, audit in ALL_VALUE_AUDITS.items():
        g.add_node(GraphNode(name=audit.term, audit=audit))
    for _, audit in ALL_CAPITAL_AUDITS.items():
        g.add_node(GraphNode(name=audit.term, audit=audit))

    # --- Linkage edges ---
    for link in VALUE_LINKAGES:
        g.add_edge(GraphEdge(
            source=_normalize_value_node(link.source),
            target=_normalize_value_node(link.target),
            sign=_sign_from_linkage_relation(link.relation),
            strength=abs(link.strength_estimate),
            relation=EdgeRelation.LINKAGE,
            rationale=link.mechanism,
        ))
    for link in CAPITAL_LINKAGES:
        g.add_edge(GraphEdge(
            source=_normalize_capital_node(link.source),
            target=_normalize_capital_node(link.target),
            sign=_sign_from_linkage_relation(link.relation),
            strength=abs(link.strength_estimate),
            relation=EdgeRelation.LINKAGE,
            rationale=link.mechanism,
        ))

    # --- Inheritance edges ---
    for src, tgt, sign, strength, relation, rationale in _INHERITANCE_EDGES:
        g.add_edge(GraphEdge(
            source=src, target=tgt, sign=sign,
            strength=strength, relation=relation, rationale=rationale,
        ))

    return g


# ---------------------------------------------------------------------------
# Inheritance invariant — bridges prose claim to testable assertion
# ---------------------------------------------------------------------------

# Per-pair inheritance claims we can check mechanically. The format:
#   (inheritor_name, inherited_name, direction)
# where direction is "fails_at_least_as_much" (inheritor's pass count
# should be <= inherited's + slack) OR "tracks" (pass counts should
# be within slack of each other).
#
# Slack accounts for the scores being auditor judgments that may
# differ by a criterion at the margins; the STRUCTURAL claim is the
# one being enforced, not exact numeric agreement.
INHERITANCE_CLAIMS = [
    # money inherits V_B-dominantly. money.pass_count should be
    # <= V_B.pass_count (money fails at least as much).
    ("money", "value_B_exchange_value", "fails_at_least_as_much"),

    # K_B inherits from V_B. Same direction.
    ("capital_B_financial", "value_B_exchange_value",
     "fails_at_least_as_much"),

    # K_A anchors to V_C — K_A passes at least as much as V_C
    # (the substrate-value quality TRANSFERS UP into K_A).
    ("capital_A_productive", "value_C_substrate_value",
     "passes_at_least_as_much"),

    # Collapsed-term inheritance: the collapsed audits fail at least
    # as much as their V_B / K_B dominant component.
    ("value_collapsed_current_usage", "value_B_exchange_value",
     "fails_at_least_as_much"),
    ("capital_collapsed_current_usage", "capital_B_financial",
     "fails_at_least_as_much"),
]


def check_inheritance_invariant(
    graph: MorphismGraph, slack: int = 1
) -> List[str]:
    """Run every INHERITANCE_CLAIMS check against the supplied graph's
    TermAudit nodes. Returns a list of violation messages; empty list
    means the invariant holds with the specified slack.

    Slack is in units of "pass count" (integer 0-7). The structural
    inheritance claim is not a strict numeric bound; slack of 1 means
    "within one criterion's worth of difference" and matches the
    auditor-judgment tolerance AUDIT_07 established."""
    violations: List[str] = []
    for inheritor, inherited, direction in INHERITANCE_CLAIMS:
        inh_audit = graph._nodes[inheritor].audit
        src_audit = graph._nodes[inherited].audit
        if inh_audit is None or src_audit is None:
            violations.append(
                f"missing audit on node {inheritor} or {inherited}"
            )
            continue
        inh_pass = inh_audit.pass_count()
        src_pass = src_audit.pass_count()
        if direction == "fails_at_least_as_much":
            if inh_pass > src_pass + slack:
                violations.append(
                    f"{inheritor}.pass_count ({inh_pass}) > "
                    f"{inherited}.pass_count ({src_pass}) + slack ({slack}) "
                    f"— inheritor should fail at least as much"
                )
        elif direction == "passes_at_least_as_much":
            if inh_pass < src_pass - slack:
                violations.append(
                    f"{inheritor}.pass_count ({inh_pass}) < "
                    f"{inherited}.pass_count ({src_pass}) - slack ({slack}) "
                    f"— inheritor should pass at least as much"
                )
        else:
            violations.append(f"unknown direction {direction!r}")
    return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _demo() -> None:
    g = build_tier1_morphism_graph()
    print("=" * 72)
    print("Tier 1 morphism graph")
    print("=" * 72)
    print(g.describe())
    print()
    print("edges by relation:")
    for rel in EdgeRelation:
        n = len(g.edges_by_relation(rel))
        print(f"  {rel.value:<12s}  {n} edges")
    print()
    print("edges by sign:")
    for sgn in EdgeSign:
        n = len(g.edges_by_sign(sgn))
        print(f"  {sgn.value:<12s}  {n} edges")
    print()
    violations = check_inheritance_invariant(g)
    print(f"inheritance invariant: {'HOLDS' if not violations else 'VIOLATED'}")
    for v in violations:
        print(f"  - {v}")


if __name__ == "__main__":
    _demo()
