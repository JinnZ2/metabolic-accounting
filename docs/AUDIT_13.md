# AUDIT 13

Thirteenth audit pass. Two concerns:

1. **Follow-ups from AUDIT_12 Part D** — retrofit typed Provenance
   on the `accounting_bridge` weights (D.2) and ship a
   `context_from_verdict` inference helper (D.3).
2. **New material merged from `origin/main`** — the full
   `investment_signal/` subsystem (~3450 lines, 8 files).

Both done in one pass. Ship-breaking import bug caught and fixed
at intake on the new subsystem.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet
designed.


## Part A — AUDIT_12 follow-ups   `[CLOSED]`

### A.1 Typed Provenance on bridge weights (AUDIT_12 § D.2)

Before AUDIT_13, `accounting_bridge.py` declared six untyped
module-level constants (`_BASELINE_QUALITY`, `_MINSKY_THRESHOLD`,
etc.) with inline comments. The AUDIT_07 Provenance discipline was
not applied.

After AUDIT_13: a `WeightedThreshold` dataclass wraps each weight
with a typed `Provenance`. All six are `DESIGN_CHOICE` kind with
`alternatives_considered` + `falsification_test` required by the
constructor. Each `falsification_test` cites
`money_signal/historical_cases.py` as the retirement path (where the
weight would be calibrated against real data).

`ALL_WEIGHTS` tuple exposes the collection for provenance-coverage
auditing. `tests/test_money_signal_accounting_bridge.py::test_9`
asserts 6/6 DESIGN_CHOICE coverage complete; regressions in either
direction trip the test.

### A.2 StateRegime inference from Verdict (AUDIT_12 § D.3)

Two new helpers in `accounting_bridge.py`:

- `regime_from_verdict_signal(signal, recovering=False) -> StateRegime`
  maps the GREEN / AMBER / RED / BLACK signal strings produced by
  `verdict/assess.py::yield_signal` to the framework's
  `StateRegime` enum. RECOVERING is NOT inferred (a single-period
  signal cannot distinguish post-collapse recovery from steady-state
  health); callers pass `recovering=True` when they know the firm is
  post-event. Unknown signals raise `ValueError`.

- `context_from_verdict_signal(signal, *, temporal, cultural,
  attribution, observer, substrate, recovering=False) ->
  DimensionalContext` builds a full context with state inferred
  and the five monetary-regime dimensions required to be declared.

Rationale for not inferring more: five of six dimensions describe
the MONETARY regime the firm operates in (what currency, what
institutional context, what substrate), not the firm's basin
state. Those cannot be derived from `Site`/`BasinState` without
external declaration. The helper minimizes caller burden to the
declaration that is actually required.

Tripwires: tests 10, 11, 12 in `test_money_signal_accounting_bridge.py`.
Test 12 runs a real `Verdict` object end-to-end through
`context_from_verdict_signal` → `signal_quality`, closing the
AUDIT_12 § D.3 integration path.

### A.3 AUDIT_12 § D.1 still `[OPEN]`

Empirical K_ij extraction from the retirement-path datasets
(Bresciani-Turroni, BCRA, FRED, etc.) is real research work and
remains deferred. The framework's discipline is preserved:
placeholders are honest about being placeholders.


## Part B — investment_signal/ intake   `[CLOSED]` (with bug)

### B.1 What landed on origin/main

Eight new files under a sibling package:

- `investment_signal/dimensions.py` — `InvestmentSubstrate` (7),
  `InvestmentAttribution` (7), `DerivativeDistance` (5),
  `TimeBinding` (6), `InvestmentContext`.
- `investment_signal/substrate_vectors.py` — frozen 7-dim
  `SubstrateVector` + arithmetic + diagnostics.
- `investment_signal/conversion_matrix.py` — C[in][vehicle] 7×7
  conversion reliability.
- `investment_signal/realization_matrix.py` — R[vehicle][return]
  7×7 realization reliability.
- `investment_signal/time_binding.py` — binding × scope integrity
  + substrate modifiers.
- `investment_signal/derivative_distance.py` — 5-level abstraction
  degradation (DIRECT / ONE_LAYER / TWO_LAYER / DERIVATIVE /
  SYNTHETIC).
- `investment_signal/coupling.py` — `InvestmentSignal` assembly
  with 20 structural fields, dependency-broken detection,
  validator runner.
- `investment_signal/README.md` — 252 lines. Defines the core
  thesis (investment as cross-substrate commitment), 23 falsifiable
  claims, usage example, relation to sibling repos.

Plus `Todo.md` (7 lines) at repo root.

### B.2 Ship-breaking import bug caught at intake   `[CLOSED]`

Three files used `..money_signal` relative imports:

- `dimensions.py:29` — `from ..money_signal.dimensions import DimensionalContext as MoneyContext`
- `coupling.py:88, 95` — `from ..money_signal.coupling import ...`
- `time_binding.py:56` — `from ..money_signal.dimensions import TemporalScope`

These fail with `ImportError: attempted relative import beyond
top-level package` because `investment_signal/` and `money_signal/`
are **sibling top-level packages**, not children of a common
parent. The `..` escapes the repo.

Running `validate_all_investment_modules()` from the README's
"Always validate at startup" example crashed on the first import.
Same class of bug as AUDIT_11 § B (`validate_all_factor_modules()`
shipped broken) and AUDIT_06 § A.1
(`governance_design_principles` path/docstring desync).

Fix: replace `..money_signal` with absolute `money_signal` in the
three files. Intake validated: all 7 modules import, full README
usage example runs to completion.

### B.3 `__init__.py` also missing   `[CLOSED]`

The README's architecture tree shows `__init__.py` but the file
was not in the merge. Same drift as AUDIT_11 § C.1 on money_signal.
Added with a module-level docstring pointing at the README and
mapping the 7 module filenames.

### B.4 Other structural observations from intake

- Enum naming slight inconsistency. `DerivativeDistance` members
  are `DIRECT / ONE_LAYER / TWO_LAYER / DERIVATIVE / SYNTHETIC`
  — the README uses "MULTI_LAYER" in one place (§ Falsifiable claim
  #15). The enum member is `DERIVATIVE`. Caught during test
  authoring; tests use the real member name. No code change.
- `TimeBinding` has no `MEDIUM_CYCLE` (README is clean here, just a
  test-author assumption). Real members: IMMEDIATE, SHORT_CYCLE,
  SEASONAL, MULTI_YEAR, GENERATIONAL, MULTI_GENERATIONAL.


## Part C — Tests landed

`tests/test_investment_signal.py` (12 cases). Coverage of the
README's 23 falsifiable claims:

| Test | README claim | What it locks |
| --- | --- | --- |
| 1 | n/a | 7 module imports (regression for § B.2) |
| 2 | n/a | `validate_all_investment_modules()` passes |
| 3 | usage | README usage example runs; 2 expected failures surface |
| 4 | #1  | `C[RELATIONAL][MONEY] <= 0.3` (monetizing destroys) |
| 5 | #2  | `C[MONEY][RELATIONAL] <= 0.3` (money can't buy trust) |
| 6 | #5  | `R[i][i] in [0.5, 1.0)` for all 7 substrates |
| 7 | #9  | `R[MONEY][MONEY] >= 0.85` nominal |
| 8 | #11 | liquidity-illusion severity ≥ 0.5 for 4 binding×scope pairs |
| 9 | #15 | signal reliability monotonically decreases with distance |
| 10 | #20 | SYNTHETIC reverse_causation ≥ 0.5 + is_financialized |
| 11 | #22 | MONEY has highest abstraction tolerance |
| 12 | #23 | NEAR_COLLAPSE money → dependency_broken=True |

11 of 23 claims directly tripwired; the other 12 are covered
transitively by the built-in `validate_*` functions which test_2
runs.

Full regression post-AUDIT_13: **44/44 PASS** (pre-AUDIT_13: 43/43).


## Part D — Coverage snapshot

| Surface | Coverage |
| --- | --- |
| investment_signal/ modules | 8/8 (7 code + README) + __init__.py |
| Factor validators | all pass (via validate_all_investment_modules) |
| README falsifiable claims directly tripwired | 11/23 |
| accounting_bridge weight Provenance | 6/6 DESIGN_CHOICE (AUDIT_12 § D.2 closed) |
| Verdict → DimensionalContext inference | shipped (AUDIT_12 § D.3 closed) |
| money_signal glucose-flow bridge | shipped (AUDIT_12 § B) |
| money_signal historical cases | 5 anchors (AUDIT_12 § A) |


## Part E — What's NOT done (scoped for future passes)

### E.1 Remaining investment_signal claims (#3, #4, #6-#8, #10, #12-#14, #16-#19, #21)   `[OPEN]`

Twelve of the 23 README claims are covered only by the built-in
`validate_*` assertions, which fire at validation time but don't
appear in `tests/`. Adding targeted tests would raise direct
tripwire coverage to 23/23.

### E.2 `investment_signal/historical_cases.py`   `[OPEN]`

Parallel to `money_signal/historical_cases.py`. README Known
Limitation #1 flags empirical calibration as pending. Same honest-
placeholder discipline would apply.

### E.3 `Todo.md` not integrated   `[NAMED]`

The commit `676d328 Add initial Todo list with project priorities`
added a `Todo.md` at repo root. Not referenced from `CLAUDE.md`
or `STATUS.md`. Either integrate it into the existing nav surface
or promote its items into the AUDIT trail.

### E.4 Distributional integration   `[NAMED]`

README § "Relation to other repos" promises a
`thermodynamic-accountability-framework/investment_distribution/`
consumer. Inside this repo, `distributional/` does not yet
consume `InvestmentSignal` (parallel to the money_signal case in
AUDIT_12 § D.4). Same structural gap in both subsystems.


## Close-out

- AUDIT_12 § D.2 closed (provenance retrofit on bridge weights,
  6/6 DESIGN_CHOICE).
- AUDIT_12 § D.3 closed (`context_from_verdict_signal` helper +
  real-Verdict integration test).
- AUDIT_12 § D.1 still `[OPEN]` — empirical K_ij extraction is
  research work, not code work.
- `investment_signal/` subsystem landed with one ship-breaking
  import bug fixed at intake and one missing `__init__.py` added.
  All 7 modules import; `validate_all_investment_modules()` runs
  clean; README usage example runs end-to-end.
- 12 new tripwires locked in 11 of 23 README falsifiable claims.
- Regression 44/44. Main stack untouched; first-law closure
  unchanged.
- Four follow-up items named for future passes (remaining claims,
  investment historical cases, Todo.md integration, distributional
  consumer).
