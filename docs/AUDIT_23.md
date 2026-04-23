# AUDIT 23

Twenty-third audit pass. Scope: close AUDIT_07 § C.2
("inheritance invariant as code") by building a stdlib-only
directed-graph representation over the Tier 1 claim space and
tripwiring the prose-level inheritance claims as mechanical
assertions.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[DEMONSTRATED]` — pattern shipped
on a small set, remainder left `[OPEN]` for per-item research.


## Part A — `term_audit/morphism_graph.py`   `[CLOSED]`

AUDIT_07 § C.2 flagged that inheritance between Tier 1 audits
(money inherits V_B, K_B inherits V_B, K_A anchors to V_C) was
prose-only. The audits wrote the claim in docstrings; nothing
in the codebase asserted that inheritors actually behave the way
inheritance requires. AUDIT_23 § A ships the graph and the
mechanical check.

### A.1 What exists now

`term_audit/morphism_graph.py` (~440 lines, stdlib only — pattern
borrowed from the physics-playground repo's `graph.py`, adapted
for the term-audit domain):

- `MorphismGraph` — directed-graph class with forward + reverse
  adjacency. Operations: `add_node`, `add_edge` (duplicate + miss-
  ing-endpoint refusal), `successors`, `predecessors`,
  `reachable_from`, `undirected_reachable`,
  `weakly_connected_components`, `is_weakly_connected`,
  `edges_by_relation`, `edges_by_sign`, `describe`.
- `GraphNode` / `GraphEdge` dataclasses (frozen). Edge carries
  sign + strength + relation_type + optional rationale.
- `EdgeRelation` enum: LINKAGE (from ValueLinkage /
  CapitalLinkage arrays) vs. INHERITANCE (the prose-level claim
  now encoded explicitly).
- `EdgeSign` enum: POSITIVE / NEGATIVE / CONDITIONAL / NONE.
- `build_tier1_morphism_graph()` — assembles **9 nodes, 20 edges**
  from existing artifacts: MONEY_AUDIT + ALL_VALUE_AUDITS (4) +
  ALL_CAPITAL_AUDITS (4) for nodes; VALUE_LINKAGES (5) +
  CAPITAL_LINKAGES (6) for linkage edges; `_INHERITANCE_EDGES`
  (9) for inheritance edges.
- `INHERITANCE_CLAIMS` + `check_inheritance_invariant(graph,
  slack=1)` — the mechanical check. Returns list of violation
  messages; empty list means invariant holds.

### A.2 The inheritance edges

9 total, derived from the audit module docstrings:

- 3 **docstring inheritance claims**:
  - `value_B_exchange_value` → `money` (NEGATIVE, 0.9) — money
    as signal inherits V_B-dominated collapse-failure.
  - `value_B_exchange_value` → `capital_B_financial` (NEGATIVE,
    0.9) — K_B financial claims inherit V_B exchange-value
    failure.
  - `value_C_substrate_value` → `capital_A_productive`
    (POSITIVE, 0.9) — K_A productive anchors to V_C substrate-
    value signal quality.
- 3 **decomposition edges into `value_collapsed_current_usage`**
  (from V_A / V_B / V_C; dominated by V_B at strength 0.9).
- 3 **decomposition edges into `capital_collapsed_current_usage`**
  (from K_A / K_B / K_C; dominated by K_B at strength 0.9).

Direction convention: `source → target` means "target inherits
from source" — the source is the thing being inherited FROM.

### A.3 The mechanical check

`INHERITANCE_CLAIMS` lists 5 inheritor↔source pairs with a
direction:

- `fails_at_least_as_much` — inheritor's `pass_count` must be
  ≤ source's `pass_count + slack`. Applied to:
  - `money` inherits `value_B_exchange_value`
  - `capital_B_financial` inherits `value_B_exchange_value`
  - `value_collapsed_current_usage` ← dominant `value_B_exchange_value`
  - `capital_collapsed_current_usage` ← dominant `capital_B_financial`
- `passes_at_least_as_much` — inheritor's `pass_count` must be
  ≥ source's `pass_count − slack`. Applied to:
  - `capital_A_productive` anchors to `value_C_substrate_value`

Slack (default 1, in integer pass-count units) matches the
auditor-judgment tolerance AUDIT_07 established — the structural
claim is being enforced, not exact numeric agreement.

**Current state**: invariant HOLDS over all 5 claim pairs
(empty violations list).

### A.4 Graph shape

```
MorphismGraph: 9 nodes, 20 edges
  weakly connected: True
  components:       1
  isolated nodes:   -

edges by relation:
  linkage       11 edges
  inheritance    9 edges

edges by sign:
  positive      11 edges
  negative       5 edges
  conditional    4 edges
  none           0 edges
```

**Weakly connected** is load-bearing: every Tier 1 claim node is
at least undirected-reachable from every other. If a future audit
adds an island, the test catches it and forces explicit justi-
fication (this audit does not belong in the Tier 1 claim space)
rather than silent drift.

### A.5 Tests — `tests/test_morphism_graph.py` (8 cases)

1. Graph shape: 9 nodes / 20 edges (11 linkage + 9 inheritance),
   node-name set matches, no orphans.
2. Graph is weakly connected (single component).
3. Load-bearing negative linkages present: V_B→V_C, K_B→K_A,
   K_B→K_C all present with `sign=NEGATIVE`.
4. Three docstring inheritance edges encoded correctly (direction
   + sign).
5. `check_inheritance_invariant()` returns empty list — the
   invariant HOLDS at slack=1 for all 5 claim pairs.
6. `add_edge` rejects duplicate edges (multi-edge ban).
7. `add_edge` rejects edges with missing endpoints (typo guard).
8. Inheritance-edge count is exactly 9 — a 10th extension would
   scope-creep AUDIT_23 § A and must be explicit.


## Part B — What's NOT in Part A

### B.1 Tier 2+ audits are not in the graph   `[OPEN]`

Tier 2 (labor / human-worth) and Tier 3 (institutional legitimacy)
audits each have their own linkage structures inside their
individual modules, but the cross-tier linkages (e.g. productivity
depends on money-as-signal quality) are not yet edges in a
combined graph. This is scoped `[OPEN]` — adding them is per-tier
work and benefits from the Tier 2 / Tier 3 audit set stabilizing
first.

### B.2 Numeric inheritance strength is auditor-judgment   `[OPEN]`

The strength values on inheritance edges (0.9 for docstring
claims, 0.2–0.9 for decomposition edges) are auditor judgments,
not empirical. PLACEHOLDER-typed; retirement-path is per-pair
empirical work (e.g. "measure how V_B pass-count drift
historically correlated with money pass-count drift across audit
revisions"). Left `[OPEN]`; does not block the structural
invariant.


## Part C — Why this closes AUDIT_07 § C.2

AUDIT_07 § C.2 named the gap precisely: "money.py and capital.py
describe inheritance in prose; nothing in the code asserts the
claim holds." AUDIT_23 § A:

- Encodes the prose claim as `INHERITANCE` edges in a directed
  graph (audit-trail grounded, not inferred).
- Converts "inheritor fails at least as much as source" into a
  mechanical pass-count comparison (`check_inheritance_invariant`).
- Tripwires the check: if pass-counts drift so that inheritors
  stop tracking sources (beyond slack=1), `test_5` fails and the
  drift surfaces immediately.
- Tripwires the graph shape: node count, edge count, inheritance-
  edge count, load-bearing negative linkages, weakly-connected
  invariant.

The prose claim now has a matching machine-check. AUDIT_07 § C.2
item: `[CLOSED]`.


## Part D — Regression (after Part A)

- Full suite: **52/52 PASS** (51 prior + new
  `test_morphism_graph.py`).
- No existing test weakened; new graph module is additive.
- AUDIT_07's 63/63 complete-provenance discipline unchanged.
- AUDIT_21's soft-gap tripwire unchanged (4 attached / 12
  remaining / 63 total).


## Part E — `scripts/counts_consistency.py`   `[CLOSED]`

Pattern borrowed (again) from physics-playground: every load-
bearing numeric claim in the codebase should be both (a)
declared in one place and (b) computable from code. If the two
disagree, either the code changed or the docs did — in either
case, someone needs to act.

### E.1 What it declares

15 counts, each with a declared baseline + audit anchor +
rationale. Grouped:

- **Test / audit shape** (2): `test_files=53`, `tier1_audits=9`.
- **Provenance discipline** (4): `provenance_total=63`,
  `provenance_complete=63`, `scope_audits_attached=4`,
  `soft_gaps_remaining=12`.
- **Historical cases** (4): `money_cases=13`, `money_matches=12`,
  `investment_cases=11`, `investment_matches=11`.
- **Morphism graph** (5): `morphism_graph_nodes=9`,
  `morphism_graph_edges=20`, `morphism_graph_linkage_edges=11`,
  `morphism_graph_inheritance_edges=9`,
  `morphism_graph_components=1`.

### E.2 How it computes

`compute_live_counts()` walks the codebase at call-time — no
cached values. It imports the Tier 1 audits, the historical-case
modules, and the morphism-graph builder, then counts provenance
records, match rates, graph shape. Each count is the single
source of truth.

### E.3 Tripwire — `tests/test_counts_consistency.py` (5 cases)

1. All 15 rows match declared (load-bearing).
2. No drift anywhere (live != -1 sentinel — catches keys missing
   from the live-computation side).
3. Declared keys unique (copy-paste guard).
4. Live count is int and >= 0 for every declared key.
5. `main()` returns exit 0 at baseline (command-line contract).

### E.4 Drift handling

The script + test don't try to pick between "legitimate change"
vs "regression" — both require explicit action. When a drift
lands:

- (a) **Legitimate change** — a new audit added a test / anchor
  / scope_audit. Bump the `DECLARED` entry AND cite the AUDIT_XX
  that made the change so the history is traceable.
- (b) **Silent regression** — some code change accidentally
  broke a count. Find it and fix the code, not the baseline.

The case this catches is (c) silent drift: STATUS.md and audit
docs quietly diverging from reality. Without this tripwire, that
drift accumulates until STATUS.md reads like fiction.

### E.5 Relationship to existing tripwires

Existing tripwires assert individual counts in their own tests
(`test_historical_cases::test_1_all_anchor_cases` asserts 13
money cases, `test_morphism_graph::test_1_graph_shape` asserts
9/20/11/9). The counts-consistency table is the **one place**
all 15 numbers live together — when STATUS.md or a doc makes a
claim, the table is where to check it, and the test guards that
table.


## Part F — Regression (after Part B)

- Full suite: **53/53 PASS** (52 after Part A + new
  `test_counts_consistency.py`).
- `counts_consistency.py` output: 15/15 rows match declared
  baseline.
- No existing test weakened.


## Close-out

- AUDIT_07 § C.2 `[CLOSED]` via `term_audit/morphism_graph.py` +
  `tests/test_morphism_graph.py` (Part A).
- Counts-consistency discipline landed via
  `scripts/counts_consistency.py` +
  `tests/test_counts_consistency.py` (Part B). 15 load-bearing
  counts declared + tripwired.
- stdlib-only discipline preserved throughout.
- 9 nodes / 20 edges / weakly-connected / invariant holds + 15
  counts consistent — all numbers the regression catches on
  drift.
