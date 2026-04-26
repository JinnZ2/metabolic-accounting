"""
tests/test_morphism_graph.py

Tripwires for term_audit/morphism_graph.py (AUDIT_23 Part A).

Closes AUDIT_07 § C.2 — "inheritance invariant as code" — by making
the prose-level inheritance claims in money.py and capital.py
mechanically checkable.

Locks in:
  1. Graph builds cleanly: 9 nodes, 20 edges (11 linkage + 9
     inheritance), no duplicates, no orphan nodes.
  2. Graph is weakly connected — every Tier 1 claim node is at
     least undirected-reachable from every other.
  3. Load-bearing negative linkages are present with sign=NEGATIVE:
     V_B -> V_C (exchange-value hides substrate-value),
     K_B -> K_A (financial claims displace productive capacity),
     K_B -> K_C (financial claims displace institutional-capital).
  4. Inheritance edges encode the three prose claims:
     money <- V_B, K_B <- V_B, K_A <- V_C.
  5. Inheritance invariant holds (check_inheritance_invariant returns
     []). If pass-counts drift so that inheritors stop tracking their
     sources, the structural claim in the audit prose has been
     broken and this test catches it.
  6. add_edge rejects duplicate edges (multi-edge ban is invariant,
     not preference).
  7. add_edge rejects edges whose endpoints aren't in the graph
     (tripwire against silent typos in future edge additions).
  8. Inheritance edge set is exactly the 9 claims in
     _INHERITANCE_EDGES — if someone adds a 10th inheritance edge,
     AUDIT_23 § A's scope claim needs updating.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from term_audit.morphism_graph import (
    EdgeRelation, EdgeSign, GraphEdge, GraphNode, MorphismGraph,
    build_tier1_morphism_graph, check_inheritance_invariant,
    INHERITANCE_CLAIMS,
)


EXPECTED_NODES = {
    "money",
    "value_collapsed_current_usage",
    "value_A_use_value",
    "value_B_exchange_value",
    "value_C_substrate_value",
    "capital_collapsed_current_usage",
    "capital_A_productive",
    "capital_B_financial",
    "capital_C_institutional",
}


def test_1_graph_builds_with_expected_shape():
    """9 nodes + 20 edges (11 linkage + 9 inheritance). Size is
    load-bearing; changes here indicate either a new Tier 1 audit
    being added or a linkage being added/removed."""
    print("\n--- TEST 1: graph shape (9 nodes, 20 edges) ---")
    g = build_tier1_morphism_graph()
    assert g.n_nodes() == 9, f"FAIL: expected 9 nodes, got {g.n_nodes()}"
    assert g.n_edges() == 20, f"FAIL: expected 20 edges, got {g.n_edges()}"
    names = set(g.node_names())
    assert names == EXPECTED_NODES, (
        f"FAIL: node name set differs; missing={EXPECTED_NODES - names}, "
        f"unexpected={names - EXPECTED_NODES}"
    )
    lk = g.edges_by_relation(EdgeRelation.LINKAGE)
    inh = g.edges_by_relation(EdgeRelation.INHERITANCE)
    assert len(lk) == 11, f"FAIL: expected 11 linkage edges, got {len(lk)}"
    assert len(inh) == 9, f"FAIL: expected 9 inheritance edges, got {len(inh)}"
    assert not g.isolated_nodes(), (
        f"FAIL: isolated nodes present: {g.isolated_nodes()}"
    )
    print(f"  9 nodes / 20 edges (11 linkage + 9 inheritance); no orphans")
    print("PASS")


def test_2_graph_is_weakly_connected():
    """Every Tier 1 claim node is at least undirected-reachable from
    every other. If this fails, some audit has been added as an
    island — the framework is claiming it has nothing to do with the
    rest of the Tier 1 claim space, which should be an explicit
    decision, not silent drift."""
    print("\n--- TEST 2: graph is weakly connected ---")
    g = build_tier1_morphism_graph()
    assert g.is_weakly_connected(), (
        f"FAIL: graph has {len(g.weakly_connected_components())} components; "
        f"expected 1"
    )
    print(f"  1 weakly-connected component spanning all 9 nodes")
    print("PASS")


def test_3_load_bearing_negative_linkages_present():
    """V_B -> V_C, K_B -> K_A, K_B -> K_C are the three structurally
    load-bearing negative linkages in value.py and capital.py. Losing
    any of them silently (e.g. dropping to POSITIVE or CONDITIONAL)
    would unwind the framework's core claim about how exchange-value
    hides substrate-value and how financial claims displace
    productive / institutional capital."""
    print("\n--- TEST 3: V_B->V_C, K_B->K_A, K_B->K_C are NEGATIVE ---")
    g = build_tier1_morphism_graph()
    expected_negatives = [
        ("value_B_exchange_value", "value_C_substrate_value"),
        ("capital_B_financial", "capital_A_productive"),
        ("capital_B_financial", "capital_C_institutional"),
    ]
    for src, tgt in expected_negatives:
        e = g.edge(src, tgt)
        assert e is not None, f"FAIL: edge {src} -> {tgt} missing"
        assert e.relation == EdgeRelation.LINKAGE, (
            f"FAIL: {src}->{tgt} expected LINKAGE, got {e.relation}"
        )
        assert e.sign == EdgeSign.NEGATIVE, (
            f"FAIL: {src}->{tgt} expected NEGATIVE, got {e.sign}"
        )
        print(f"  {src} -> {tgt}: NEGATIVE linkage confirmed")
    print("PASS")


def test_4_inheritance_edges_encode_three_prose_claims():
    """money.py and capital.py docstrings make three inheritance
    claims: money inherits V_B, K_B inherits V_B, K_A anchors to V_C.
    Encoded as INHERITANCE edges; this test locks in their presence
    + direction + sign."""
    print("\n--- TEST 4: three docstring inheritance claims encoded ---")
    g = build_tier1_morphism_graph()
    claims = [
        # (source = inherited-from, target = inheritor, expected sign)
        ("value_B_exchange_value", "money", EdgeSign.NEGATIVE),
        ("value_B_exchange_value", "capital_B_financial", EdgeSign.NEGATIVE),
        ("value_C_substrate_value", "capital_A_productive", EdgeSign.POSITIVE),
    ]
    for src, tgt, sign in claims:
        e = g.edge(src, tgt)
        assert e is not None, f"FAIL: inheritance edge {src} -> {tgt} missing"
        assert e.relation == EdgeRelation.INHERITANCE, (
            f"FAIL: {src}->{tgt} expected INHERITANCE, got {e.relation}"
        )
        assert e.sign == sign, (
            f"FAIL: {src}->{tgt} expected {sign}, got {e.sign}"
        )
        print(f"  {src} -> {tgt}: {sign.value} INHERITANCE confirmed")
    print("PASS")


def test_5_inheritance_invariant_holds():
    """LOAD-BEARING: the inheritance invariant is the whole point of
    AUDIT_23 § A. If inheritor pass-counts drift above their source's
    pass-count (beyond the slack tolerance), the prose inheritance
    claim is broken — the audits are no longer telling a consistent
    story. This test catches that drift."""
    print("\n--- TEST 5: inheritance invariant holds (slack=1) ---")
    g = build_tier1_morphism_graph()
    violations = check_inheritance_invariant(g, slack=1)
    assert not violations, (
        f"FAIL: inheritance invariant violated:\n  "
        + "\n  ".join(violations)
    )
    print(f"  inheritance invariant HOLDS over {len(INHERITANCE_CLAIMS)} "
          f"claim pairs (slack=1)")
    print("PASS")


def test_6_add_edge_rejects_duplicate():
    """Multi-edges are not supported. Adding the same source->target
    twice must raise ValueError."""
    print("\n--- TEST 6: add_edge rejects duplicate edges ---")
    g = MorphismGraph()
    g.add_node(GraphNode(name="a"))
    g.add_node(GraphNode(name="b"))
    g.add_edge(GraphEdge(
        source="a", target="b", sign=EdgeSign.POSITIVE,
        strength=1.0, relation=EdgeRelation.LINKAGE,
    ))
    try:
        g.add_edge(GraphEdge(
            source="a", target="b", sign=EdgeSign.NEGATIVE,
            strength=0.5, relation=EdgeRelation.INHERITANCE,
        ))
    except ValueError as exc:
        print(f"  duplicate rejected: {exc}")
        print("PASS")
        return
    raise AssertionError("FAIL: duplicate edge was silently accepted")


def test_7_add_edge_rejects_missing_endpoint():
    """Silent typos in edge additions would be catastrophic (an edge
    to 'V_B_exchange_vlue' would simply never be traversed). The
    constructor must reject edges whose endpoints aren't yet in the
    graph."""
    print("\n--- TEST 7: add_edge rejects missing endpoint ---")
    g = MorphismGraph()
    g.add_node(GraphNode(name="a"))
    # target not in graph
    try:
        g.add_edge(GraphEdge(
            source="a", target="ghost", sign=EdgeSign.POSITIVE,
            strength=1.0, relation=EdgeRelation.LINKAGE,
        ))
    except ValueError:
        pass
    else:
        raise AssertionError("FAIL: missing target accepted")
    # source not in graph
    try:
        g.add_edge(GraphEdge(
            source="ghost", target="a", sign=EdgeSign.POSITIVE,
            strength=1.0, relation=EdgeRelation.LINKAGE,
        ))
    except ValueError:
        pass
    else:
        raise AssertionError("FAIL: missing source accepted")
    print(f"  missing-endpoint edges correctly rejected")
    print("PASS")


def test_8_inheritance_edge_count_is_exactly_nine():
    """AUDIT_23 § A scopes 9 inheritance edges: 3 docstring claims +
    6 decomposition edges (3 value components -> collapsed_value, 3
    capital components -> collapsed_capital). A 10th inheritance edge
    would extend the scope of AUDIT_23 § A; this test forces that
    extension to be explicit."""
    print("\n--- TEST 8: exactly 9 inheritance edges ---")
    g = build_tier1_morphism_graph()
    inh = g.edges_by_relation(EdgeRelation.INHERITANCE)
    assert len(inh) == 9, (
        f"FAIL: expected 9 inheritance edges, got {len(inh)}. "
        f"If you're extending, update docs/AUDIT_23.md § A first."
    )
    # Spot check: three to collapsed_value, three to collapsed_capital,
    # three "audit-level" (money / K_B / K_A).
    targets = sorted(e.target for e in inh)
    assert targets.count("value_collapsed_current_usage") == 3
    assert targets.count("capital_collapsed_current_usage") == 3
    assert targets.count("money") == 1
    assert targets.count("capital_B_financial") == 1
    assert targets.count("capital_A_productive") == 1
    print(f"  9 inheritance edges: 3 collapsed_value + 3 collapsed_capital "
          f"+ 3 docstring claims")
    print("PASS")


if __name__ == "__main__":
    test_1_graph_builds_with_expected_shape()
    test_2_graph_is_weakly_connected()
    test_3_load_bearing_negative_linkages_present()
    test_4_inheritance_edges_encode_three_prose_claims()
    test_5_inheritance_invariant_holds()
    test_6_add_edge_rejects_duplicate()
    test_7_add_edge_rejects_missing_endpoint()
    test_8_inheritance_edge_count_is_exactly_nine()
    print("\nall morphism_graph tests passed.")
