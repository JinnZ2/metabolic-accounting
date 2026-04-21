# AUDIT 12

Twelfth audit pass. Scope: close the two `[OPEN]` items surfaced by
AUDIT_11's close-out —

1. `money_signal/historical_cases.py` — empirical calibration
   anchor module (README Known Limitations #1).
2. `money_signal/accounting_bridge.py` — glucose-flow integration
   per README line 134 ("reversal reliability is the metabolic
   signal").

Both shipped. Both tripwired. AUDIT_11 Close-out updated.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet designed.


## Part A — Historical cases module   `[CLOSED]` (as skeleton)

### A.1 What landed

`money_signal/historical_cases.py` (~620 lines):

- `DynamicShift` enum: 6 qualitative shift categories
  (AMPLIFIED_STRONG / AMPLIFIED / UNCHANGED / DAMPED / DAMPED_STRONG
  / SIGN_FLIPPED). Deliberately qualitative; no numeric K_ij values.
- `ObservedDynamic` dataclass: one qualitative K_ij shift with
  evidence text and typed `Provenance` (per AUDIT_07 taxonomy).
- `HistoricalCase` composite: pre/during/post DimensionalContext +
  list of ObservedDynamics + primary_refs + historical_confidence.
- `FrameworkPrediction` + `CaseComparison` + `predict()` +
  `compare_case()`: run the framework against a case's DURING
  context and report qualitative agreement.

Five anchor cases shipped:

| Case | Period | Role |
| --- | --- | --- |
| Weimar hyperinflation | 1921-1923 | canonical near-collapse + recovery |
| Zimbabwe hyperinflation | 2007-2009 | substrate transition (PAPER → DIGITAL) |
| Global Financial Crisis | 2007-2009 | README claim #4 (speculative amp) + #7 (sign flips) anchor |
| Cyprus bank haircut | 2013 | README claim #5 (observer asymmetry) anchor |
| Argentina peso collapse | 2001-2002 | repeated-pattern hysteresis anchor |

### A.2 The discipline: honest placeholders, not fabricated calibration

The README explicitly says historical calibration is needed before
factor values should be read quantitatively. AUDIT_12's intake of
this module preserves that discipline:

- Every `ObservedDynamic.shift` uses a qualitative `DynamicShift`
  enum. No floats. A test (`test_historical_cases.py::test_7`)
  tripwires this — if anyone adds a float-valued shift, the test
  catches it.
- Every `ObservedDynamic.provenance` is either `EMPIRICAL` with
  `source_refs` to canonical literature (Feldman 1993, Holtfrerich
  1986, Hanke & Kwok 2009, Gorton 2010, etc.) or `PLACEHOLDER` with
  a `retirement_path` naming the dataset that would retire it.
- `historical_confidence` is a float about the case's documentation
  density, not a fit quality.

Fabricating numeric K_ij values against the cases would be the
"performative citation" failure mode the AUDIT_07 Provenance
taxonomy was built to prevent.

### A.3 Qualitative match finding   `[NAMED]`

Running `compare_case()` across the 5 anchors produces 4/5
qualitative matches:

- Weimar ✓
- Zimbabwe ✓
- GFC ✓
- Cyprus ✗ (expected; this is the observer-asymmetry case, not a
  K[N][R] amplification case)
- Argentina ✓

The 4-of-5 outcome is tripwired (`test_historical_cases.py::test_6`).
A change in the count is load-bearing: either the factor values
moved, the case curation changed, or the match criteria drifted.
The initial sign-flip check was too strict (rejected absence-of-
evidence as disconfirming); AUDIT_12 fixed the match semantics to
treat recorded silence on sign flips as uninformative (the
framework predicts flips *can* occur, observation confirms or is
silent).


## Part B — Accounting bridge module   `[CLOSED]`

### B.1 What landed

`money_signal/accounting_bridge.py` (~220 lines):

- `signal_quality(ctx) -> float` in [0, 1]. Scalar reliability of
  monetary denomination under this coupling context. Baseline
  quality 0.92 (never 1.0 — no monetary regime is perfectly
  reliable). Penalties for elevated Minsky, elevated coupling
  magnitude, and sign flips.
- `coupling_assumption_flags(ctx) -> List[AssumptionValidatorFlag]`.
  Emits the real adapter type (not the lite type used by
  `money_three_scope_falsification.py` — that module's standalone-
  decoupling rationale does not apply here because this module
  already sits inside the integrated tree). One flag per active
  stressor plus a dedicated high-severity
  `near_collapse_regime` flag.
- `SignalAdjustedFlow` + `adjust_glucose_flow(flow, ctx)`:
  non-mutating adjunct view on a `GlucoseFlow` that reports raw
  and quality-discounted profit. Lazy-imports accounting/ inside
  the function so the bridge module remains standalone-testable.
- CLI demo across four scenarios (healthy-deep → healthy-thin →
  stressed-thin → near-collapse-thin).

### B.2 The bridge direction matters

One-way, downhill:

```
    money_signal/  ---reads---> term_audit/provenance.py
                                term_audit/integration/metabolic_accounting_adapter.py (AssumptionValidatorFlag)

    money_signal/accounting_bridge  ---reads (lazily)---> accounting/glucose.py
```

**`money_signal/` does not import `accounting/` at module top level
anywhere.** Tripwired by
`test_money_signal_accounting_bridge.py::test_8`, which scans every
file in `money_signal/` for top-level `from accounting.` or
`import accounting` and fails if any is found. The only
accounting reference is inside `adjust_glucose_flow()` as a
function-local lazy import. Reversing this direction would
entangle the physical (xdu) and relational (coupling) layers.

### B.3 Sample output

| State regime | quality | flag count |
| --- | --- | --- |
| HEALTHY (deep holder) | 0.920 | 0 |
| HEALTHY (thin holder) | 0.919 | 1 (minsky 0.001) |
| STRESSED (thin holder) | 0.869 | 2 |
| NEAR_COLLAPSE (thin holder, digital) | 0.449 | 4 (incl. near_collapse_regime @ 0.90) |

Gap healthy → near-collapse: 0.47. A firm reporting \$350 reported
profit under a near-collapse monetary regime carries a
signal-adjusted value of \$157 — the bridge makes that
under-represented-in-the-books reality visible.

### B.4 Weights are DESIGN_CHOICE

The thresholds and penalty coefficients inside `signal_quality`
(baseline 0.92, Minsky threshold 1.3 / penalty 0.18 per step,
magnitude threshold 0.8 / penalty 0.22, sign-flip penalty 0.35)
are `DESIGN_CHOICE` under the AUDIT_07 Provenance taxonomy.
Inline comments reference the taxonomy and flag calibration as
the retirement path (historical_cases.py anchors are where these
weights can eventually be tuned).

Not retrofitted to typed `Provenance` records in this pass —
deferred as a follow-up per AUDIT_10 § D.2 (same pattern as
MoneyState.provenance retrofit: known gap, mechanical fix, scoped
out of intake).


## Part C — Tests added

- `tests/test_historical_cases.py` (7 cases)
- `tests/test_money_signal_accounting_bridge.py` (8 cases)

Full regression post-AUDIT_12: **43/43 PASS**.


## Part D — What's NOT done (scoped for future passes)

### D.1 Empirical K_ij extraction   `[OPEN]`

Each `ObservedDynamic` ships with a qualitative shift. The quantitative
K_ij ratio extraction is deferred — the `PLACEHOLDER` entries name
the specific datasets (Bresciani-Turroni's wage-price series, BCRA
dollar-savings ratios, FRED LIBOR-OIS window, etc.) that would
retire them. This is genuine research work, not a code task.

### D.2 Typed Provenance on bridge weights   `[OPEN]`

`_BASELINE_QUALITY`, `_MINSKY_THRESHOLD`, etc. are named constants
with inline comments. Same shape as AUDIT_10 § D.2 flagged for
`MoneyState.provenance`. Retrofit pattern:

```python
SIGNAL_QUALITY_WEIGHTS = {
    "baseline": (0.92, design_choice(
        rationale="...",
        alternatives_considered=["1.00", "0.85"],
        falsification_test="calibrate against historical_cases",
    )),
    ...
}
```

Mechanical; deferred.

### D.3 Integration with `compute_flow()`   `[NAMED]`

`accounting/glucose.py::compute_flow` is the canonical entry point
for building a `GlucoseFlow`. `adjust_glucose_flow` sits alongside,
not inside, that pipeline. A caller running the full stack could:

1. Build a `GlucoseFlow` via `compute_flow(...)`.
2. Build a `DimensionalContext` from their operational environment.
3. Call `adjust_glucose_flow(flow, ctx)` to get the signal-adjusted
   view.

Wiring step 2 automatically — inferring the context from the site /
basin state / environmental regime — is the natural next
integration step but requires design direction. The dimensional
enums are not trivially derivable from the existing `Site` /
`BasinState` schema.

### D.4 Add the observer-asymmetry reporter   `[NAMED]`

README line 125 claims: *"The distributional module reads them to
produce observer-asymmetry reports."* `distributional/` currently
has `access.py`, `institutional.py`, `tiers.py` — no observer-
asymmetry reporter that consumes `money_signal/` K matrices.
Natural next module; out of scope here.


## Part E — AUDIT_11 Close-out update

Two items previously `[OPEN]` now `[CLOSED]`:

- ~~historical_cases.py~~ → Part A
- ~~glucose-flow bridge~~ → Part B

Remaining from AUDIT_11 close-out:

- Integration with three-scope audit (AUDIT_10 § D.1) — still
  `[NAMED]`; this audit's accounting_bridge is a different
  integration (signal-quality-on-flows, not precondition-on-
  coupling-pipelines).


## Part F — Coverage snapshot

| Surface | Coverage |
| --- | --- |
| money_signal/ modules | 11/11 (9 core + bridge + historical_cases) |
| README falsifiable claims tripwired | 9/9 (all) |
| Factor validators tripwired | 7/7 |
| Historical anchor cases | 5 with honest Provenance |
| Quantitative historical calibration | 0 (deferred, honest placeholder) |
| Signal-quality bridge | 1 module + 8-case tripwire |
| Typed Provenance on bridge weights | 0 (deferred per § D.2) |


## Close-out

- Two `[OPEN]` items from AUDIT_11 closed as skeletons with
  honest provenance discipline. Neither fabricates data the
  framework hasn't earned.
- `money_signal/` is now externally-consumable: a downstream tool
  can read the README, call `coupling_matrix_as_dict`,
  `signal_quality`, or `compare_case` and get structurally-sound
  answers.
- 2 new test files (15 new tests), 2 new modules.
- Regression 43/43 PASS. Main stack untouched; first-law closure
  unchanged.
- Three items named for follow-up: empirical K_ij extraction,
  typed Provenance on bridge weights, automatic DimensionalContext
  inference for `compute_flow` integration.
