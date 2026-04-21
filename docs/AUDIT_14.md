# AUDIT 14

Fourteenth audit pass. Scope: the four items named in AUDIT_13 § E
— remaining investment_signal claims (E.1), Todo.md integration
(E.3), investment_signal historical cases (E.2), and a distributional
consumer stub (E.4).

**Chunked delivery.** Each item lands in its own commit on this
branch; this document grows across them. Part A (E.1 + E.3) lands
first; Parts B (E.2) and C (E.4) follow. Regression green at every
commit.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet designed.


## Part A — AUDIT_13 § E.1 + § E.3   `[CLOSED]`

### A.1 investment_signal coverage: 11/23 → 23/23 claims tripwired

Before this audit: 11 of the 23 README falsifiable claims in
`investment_signal/` had direct tripwire tests in
`test_investment_signal.py`. The remaining 12 (actually 14 on
recount) were covered only transitively by the `validate_*`
functions.

After AUDIT_14 § A: **all 23 claims directly tripwired**. 14 new
tests added:

| Test | Claim | Locked value |
| --- | --- | --- |
| 13 | #3 | `C[ATTENTION][MONEY] = 0.30 ≤ 0.4` (attention extracted before money) |
| 14 | #4 | `C[RESOURCE][ENERGY] = 0.80 ≥ 0.6` (physics floor) |
| 15 | #6 | `R[MONEY][RELATIONAL] = 0.10 ≤ 0.2` (money can't produce trust) |
| 16 | #7 | `R[RELATIONAL][MONEY] = 0.30 ≤ 0.4` (monetizing destroys the vehicle) |
| 17 | #8 | `R[RELATIONAL][RELATIONAL] = 0.95 ≥ 0.9` (compounds in own substrate) |
| 18 | #10 | `R[LABOR][TIME] = 0.10 ≤ 0.3` (labor consumes time) |
| 19 | #12 | `MULTI_GENERATIONAL(EPOCHAL) = 0.60` dominates all 5 other bindings |
| 20 | #13 | TIME modifier 0.70, ATTENTION 0.50 — both < 1.0 |
| 21 | #14 | RELATIONAL binding modifier 1.15 is the max across 7 substrates |
| 22 | #16 | visibility: 1.00 → 0.70 → 0.40 → 0.15 → 0.02 monotonically down |
| 23 | #17 | cascade:    0.05 → 0.15 → 0.35 → 0.65 → 0.90 monotonically up |
| 24 | #18 | reverse:    0.00 → 0.10 → 0.30 → 0.60 → 0.85 monotonically up |
| 25 | #19 | DIRECT: reverse = 0.00, visibility = 1.00 (baseline clean) |
| 26 | #21 | TIME 0.30, ATTENTION 0.20, RELATIONAL 0.05 — all < 0.35 (can't be derivatized) |

Any edit that silently changes one of these values breaks the
corresponding test. The 23 README claims are now load-bearing in
the code, not just prose.

### A.2 Todo.md integration

Before: `Todo.md` (7 lines, from commit `676d328` on main) sat at
repo root with no cross-reference from the audit trail or CLAUDE.md
nav.

After:

- `CLAUDE.md` nav table gets a new row pointing at `Todo.md` as the
  "forward-priority list."
- `Todo.md` gets an "Audit cross-reference" section mapping each
  of the three priorities to audit entries:
  - **Priority 1 (historical_cases)**: money_signal shipped in
    AUDIT_12; investment_signal shipped in AUDIT_14 Part B
    (pending); extended case list (Bitcoin, Roman denarius, Pacific
    shell networks, etc.) remains `[OPEN]`.
  - **Priority 2 (distributional)**: explicitly routed to
    `thermodynamic-accountability-framework/money_distribution/` and
    `investment_distribution/` per the document itself. In THIS
    repo, AUDIT_14 Part C ships an interface stub + literature
    anchors.
  - **Priority 3 (earth-systems-physics)**: not yet started; blocked
    on priorities 1 and 2 per Todo.md's own sequencing.

### A.3 E.4 scope change (informed by Todo.md)

Todo.md unambiguously places distributional analysis in the sister
repo. This resolves the Option (X) vs (Y) question AUDIT_13 § E.4
left open:

- **Option (Y) confirmed**: the distributional implementation lives
  in the sister repo, not here.
- AUDIT_14 Part C will ship a **lean interface stub** in
  `distributional/signal_asymmetry.py`: the data shape
  (`ObserverAsymmetryReport`), a literature-anchor registry
  (DINA / HANK / stratification / incidence), and a clear
  "see the sister repo for the analytic consumer" pointer.
- Saves ~3 hours of work, preserves scope discipline, matches the
  user's documented routing intent.


## Part B — AUDIT_13 § E.2: investment_signal historical cases   `[PENDING, chunk 2]`

To land in the next commit on this branch. Five anchor cases
following the money_signal/historical_cases.py pattern:

- Enron 2001 (SYNTHETIC reverse causation)
- 2008 MBS (high-derivative-distance opacity)
- ZIRP era 2009-2021 (investment under stressed money)
- Gig economy (C[TIME][MONEY] extraction)
- Community land trusts (counter-example: preserving relational
  capital under monetary pressure)

Same honest-placeholder discipline: qualitative `DynamicShift`
enum, typed `PLACEHOLDER` provenance with retirement paths, no
fabricated numeric values. `compare_case()` + tripwire test.


## Part C — AUDIT_13 § E.4: distributional stub   `[PENDING, chunk 3]`

To land in the final commit on this branch. Per § A.3 above:
lean interface stub with literature-anchor registry, not a full
implementation.

Planned shape:

```python
# distributional/signal_asymmetry.py

@dataclass(frozen=True)
class ObserverAsymmetryReport:
    """Cross-observer comparison of signal quality / coupling under
    the same system state. See docs/AUDIT_14.md § C."""
    ...

LITERATURE_ANCHORS: Dict[str, Provenance] = {
    "distributional_national_accounts": empirical(...),  # Piketty-Saez-Zucman / WID.world
    "heterogeneous_agent_macro":        empirical(...),  # Kaplan-Moll-Violante HANK
    "stratification_economics":         theoretical(...), # Darity-Hamilton
    "fiscal_incidence":                 empirical(...),   # Harberger / CBO / JCT
}

# Concrete implementation: see
# thermodynamic-accountability-framework/money_distribution/ and
# investment_distribution/
```

No K-matrix consumption or numeric reporting here. The point is
to leave an anchor in the repo that the sister-repo implementation
can reference, with the literature framework pre-identified.


## Part D — AUDIT_13 Part E status at end of audit

| Item | Status |
| --- | --- |
| § E.1 remaining README claims | `[CLOSED]` — 14 new tests, 23/23 tripwired |
| § E.2 investment historical_cases | `[PENDING, chunk 2]` |
| § E.3 Todo.md integration | `[CLOSED]` — nav row + cross-reference section |
| § E.4 distributional consumer | `[PENDING, chunk 3]` — confirmed Option (Y), lean stub |


## Close-out (Part A commit)

- 14 new tripwires bring investment_signal coverage to 23/23
  README falsifiable claims.
- Todo.md integrated into the nav surface + audit trail.
- Scope decision on E.4 closed via Todo.md's own routing.
- Parts B and C follow in subsequent commits on this branch.
- Regression: **44/44 PASS** post-Part A (same file count; all 14
  new tests are inside the existing `test_investment_signal.py`,
  growing it from 12 cases to 26).
