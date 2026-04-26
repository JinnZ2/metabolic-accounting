# AUDIT 24

Twenty-fourth audit pass. Scope: add bidirectional name-set
consistency as a structural tripwire complementing AUDIT_23's
scalar counts-consistency. Pattern borrowed from the Geometric-
to-Binary-Computational-Bridge repo's `validate_bridge_contract.py`.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented.


## Part A — Motivation

AUDIT_23 § E shipped `scripts/counts_consistency.py`: for each
declared key, assert `declared_count == live_count`. Scalar
check, catches count drift.

The gap: two sets with the same cardinality but different
elements pass the scalar check. Concretely, our pre-AUDIT_24
state had:

- `test_counts_consistency::test_4` checked "every DECLARED key
  is in `compute_live_counts()`" but NOT the reverse. A new key
  added to `compute_live_counts()` without a matching `DECLARED`
  entry slipped through.
- `tests/test_morphism_graph.py::test_1` hardcoded
  `EXPECTED_NODES`. If both the morphism graph and the hardcoded
  set changed (e.g. via simultaneous edits), the test passed
  even when drift existed against the authoritative Tier 1 audit
  module list.
- No tripwire existed for "morphism graph has a node whose
  `audit` field is None" — a construction bug that would
  propagate silently.

`validate_bridge_contract.py` in the Bridge repo solves the
analogous problem by computing `set(manifest) - set(registry)`
and `set(registry) - set(manifest)` — reporting missing and
extra in both directions. AUDIT_24 adopts that pattern.


## Part B — `scripts/name_set_consistency.py`   `[CLOSED]`

### B.1 Declared pairs

Three surface pairs, each tested bidirectionally:

| Pair | Surface A | Surface B | What it catches |
| --- | --- | --- | --- |
| `tier1_audits_↔_morphism_graph_nodes` | Tier 1 audit `.term` strings | Morphism graph node names | A new Tier 1 audit added without a graph node (or vice versa) |
| `counts_declared_↔_counts_live` | `DECLARED` keys in counts_consistency | `compute_live_counts()` return keys | A live key added without a DECLARED entry; reverse was already checked |
| `morphism_graph_nodes_↔_audit_backed_nodes` | All graph node names | Nodes whose `.audit` field is populated | Orphan/un-audited nodes introduced by graph-construction drift |

### B.2 How drift is reported

For each pair, compute:

- `missing_from_a = set(b) - set(a)` — names in B that aren't in A
- `missing_from_b = set(a) - set(b)` — names in A that aren't in B

If either is non-empty, the pair is in DRIFT. The CLI prints
per-pair sections with exact missing-name lists and exits
non-zero.

### B.3 Relationship to counts_consistency

- `counts_consistency.py` — SCALAR. For each declared key, the
  declared count equals the live count. Catches count drift.
- `name_set_consistency.py` — STRUCTURAL. For each declared pair,
  the two sets have the same elements (bidirectionally). Catches
  set-membership drift where counts happen to match.

Both tripwires are load-bearing. Neither subsumes the other.


## Part C — `tests/test_name_set_consistency.py`   `[CLOSED]`

5 cases:

1. All declared pairs agree bidirectionally (the central
   invariant — zero missing in either direction).
2. Each pair's `missing_from_a` and `missing_from_b` are empty
   tuples independently (catches "same cardinality, different
   content" with a direction-specific error message).
3. Pair labels are unique (copy-paste guard).
4. `main()` returns exit 0 at baseline.
5. At least one pair has cardinality ≥ 1 on both sides (guards
   against the degenerate case where `set_a == set_b` holds
   trivially because both are empty — such a "tripwire" would
   catch nothing).


## Part D — Concretely, what regressions does this catch?

### D.1 Tier 1 audit ↔ morphism graph drift

If someone adds a 10th Tier 1 audit (e.g., a new `value_D_*`
component) without updating `build_tier1_morphism_graph()`:

- `tier1_audit_terms()` returns 10 names.
- `morphism_graph_nodes()` returns 9 names.
- `missing_from_morphism_graph_nodes = {'value_D_*'}` — DRIFT
  caught with the exact offending name in the error.

The prior test (`test_morphism_graph::test_1`) would also fail,
but only because of the hardcoded `EXPECTED_NODES` count — it
wouldn't necessarily point at the right root cause.

### D.2 counts_consistency live-side drift

If someone adds a new key to `compute_live_counts()` return dict
without adding a matching `DECLARED` entry:

- `counts_live_keys()` returns the new key.
- `counts_declared_keys()` does not.
- `missing_from_counts_declared_keys = {'<new_key>'}` — DRIFT.

Prior to AUDIT_24, `test_counts_consistency::test_4` only
verified the opposite direction. This closes the reverse gap.

### D.3 Orphan morphism graph nodes

If someone adds a node via `MorphismGraph.add_node(GraphNode(
name='x'))` (no audit), it would be a silent orphan. The new
pair catches it:

- `morphism_graph_nodes` returns `{..., 'x'}`.
- `audit_backed_nodes` does not include `'x'`.
- `missing_from_audit_backed_nodes = {'x'}` — DRIFT.


## Part E — Regression

- Full suite: **54/54 PASS** (53 after AUDIT_23 + new
  `test_name_set_consistency.py`).
- `counts_consistency.py` test_files declared count bumped from
  53 to 54 to track the new test file.
- 15/15 rows still match the counts_consistency baseline.
- 3/3 pairs agree on the name_set_consistency check.
- No existing test weakened.


## Part F — What's NOT in AUDIT_24

### F.1 Historical-case name sets   `[OPEN]`

`tests/test_historical_cases.py::test_1` and
`tests/test_investment_historical_cases.py::test_1` still
hardcode expected name sets (13 money anchors, 11 investment
anchors). Those tests catch drift but carry the same
"hardcoded-expected" smell as the prior morphism graph test.

Migrating them to the `PAIRS` pattern is straightforward but
pulls several test assertions into the name_set_consistency
surface. Left `[OPEN]` — the current hardcoded tests already
catch drift explicitly; porting them is a refactor, not a gap
close.

### F.2 Other repo surfaces   `[OPEN]`

Tier 2+ audits, regulatory frameworks, recovery_pathways stages,
etc. also have implicit "should match" sets (audit registry ↔
test registry ↔ doc registry). Not covered by AUDIT_24; scoped
for later passes when the Tier 2+ audit set stabilizes.


## Close-out

- AUDIT_24 closes the "same cardinality, different content"
  class of drift with bidirectional name-set checks across 3
  declared pairs.
- Counts-consistency (AUDIT_23 § E, scalar) and
  name-set-consistency (AUDIT_24, structural) are complementary
  tripwires on the codebase's numeric and structural claims.
- Pattern borrowed from Geometric-to-Binary-Computational-Bridge
  `validate_bridge_contract.py`; credited in the module
  docstring.
- 54/54 regression pass.
