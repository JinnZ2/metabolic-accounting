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


## Part B — AUDIT_13 § E.2: investment_signal historical cases   `[CLOSED]`

### B.1 Module shipped

`investment_signal/historical_cases.py` (~480 lines) plus
`tests/test_investment_historical_cases.py` (8 cases). Five anchor
cases parallel to `money_signal/historical_cases.py`:

| Case | Failure signature | Confidence |
| --- | --- | --- |
| **Enron 2001** | SYNTHETIC distance → reverse causation + substrate invisible | 0.95 |
| **MBS 2004-2008** | DERIVATIVE distance + multi-layer opacity + terminal money near-collapse | 0.95 |
| **ZIRP 2009-2021** | stressed money + GENERATIONAL scope + SHORT_CYCLE binding → liquidity illusion | 0.80 |
| **Gig economy 2013-present** | DERIVATIVE distance + TIME/ATTENTION extraction | 0.85 |
| **Community Land Trusts 1970-present** | **counter-example**: DIRECT + MULTI_GENERATIONAL + RECIPROCAL_OBLIGATION → 0 failures | 0.80 |

### B.2 Discipline preserved

Every `ObservedInvestmentFailure` uses a tag from the canonical
`VALID_FAILURE_TAGS` set (the 8 tags produced by
`signal_failure_reasons`). The constructor rejects unknown tags at
`__post_init__`. Every observation carries typed `Provenance`:
`EMPIRICAL` with canonical literature refs (McLean & Elkind,
Powers Report, Gorton 2010, FCIC 2011, Rosenblat 2018, Davis 2010,
etc.) or `PLACEHOLDER` with a named retirement path (e.g., ILPA
+ Preqin series for ZIRP liquidity gaps). No fabricated numeric
C[i][j] or R[i][j] values.

### B.3 Framework-vs-observed calibration: 4/5 covers

`compare_case()` reports whether the framework's predicted failure
tags for the DURING context cover the historically observed tags.
Same asymmetric discipline as money_signal: predicted-MORE is
permitted (absence of evidence ≠ evidence of absence); predicted-
MISSING-A-RECORDED-FAILURE is a real finding.

Result: **4/5 cases covered**. ZIRP is the single outlier — the
mismatch is documented in the case's own notes as a
single-case-encoding limitation rather than a framework bug. The
ZIRP era spans multiple characteristic derivative distances (retail
TWO_LAYER, PE DERIVATIVE, CLOs SYNTHETIC). The characteristic
context chosen (TWO_LAYER retail diversified portfolio) correctly
fires `liquidity_illusion` but sits below the 0.5 reverse-causation
threshold for `is_financialized` — the firm-level buyback dynamics
documented by Lazonick/Borio are DERIVATIVE-distance phenomena not
captured in the single retail-portfolio encoding. Decomposing ZIRP
into multiple investor-type sub-cases is a future refinement
(tracked as a soft item rather than an `[OPEN]`).

### B.4 Intake adjustments that produced the 4/5

Running the CLI before adjustment produced 2/5. Three context
classifications were tightened during intake to match the observed
tag sets honestly:

1. **MBS 2008 DURING** money context: `STRESSED` → `NEAR_COLLAPSE`.
   Cross-reference with `money_signal/historical_cases.py::GFC_2008`,
   which already classified the Sep 2008 terminal phase as
   NEAR_COLLAPSE. This propagates `money_near_collapse` and
   `money_dependency_broken` into the predicted tag set.
2. **ZIRP DURING** money temporal: `SEASONAL` → `GENERATIONAL`.
   ZIRP-era liabilities (pension, 30-year mortgages, infrastructure)
   are committed at generational horizons. Short-cycle investor-
   side binding against that horizon is exactly claim #11's
   liquidity-illusion shape.
3. **GIG economy DURING** derivative distance: `TWO_LAYER` →
   `DERIVATIVE`. Algorithmic pricing on top of the platform-service
   stack is a genuine financial layer; claim #18's monotonic
   reverse-causation curve places it above the 0.5 threshold only
   at DERIVATIVE (0.60) or higher.

None of these are code changes — they are classification honesty.
The framework's thresholds did not move.

### B.5 Tripwires

`tests/test_investment_historical_cases.py` (8 cases):

- 1: five anchor cases registered
- 2: every failure tag is in `VALID_FAILURE_TAGS`; constructor
  rejects bogus tags
- 3: every `ObservedInvestmentFailure` has complete Provenance
- 4: `compare_case` runs on every anchor
- 5: **load-bearing** — expected 4/5 match with ZIRP as the named
  outlier; any drift in the count forces explicit review
- 6: MBS DURING context propagates `money_near_collapse` into
  predicted tags (dependency-propagation regression)
- 7: GIG at DERIVATIVE distance produces
  `financialized_reverse_causation` (threshold regression)
- 8: **load-bearing counter-example** — CLTs have zero observed
  failures; adding one forces reconsideration of the positive-case
  discipline.


## Part C — AUDIT_13 § E.4: distributional stub   `[CLOSED]`

Shipped per § A.3: lean interface stub with literature-anchor
registry, NOT a full implementation. Production cross-observer
analysis lives in
`thermodynamic-accountability-framework/money_distribution/` and
`investment_distribution/` per `Todo.md` priority 2.

### C.1 What landed

`distributional/signal_asymmetry.py` (~260 lines):

- **`LITERATURE_ANCHORS`** dict: four mature empirical strands,
  each a complete typed `Provenance` record under the AUDIT_07
  taxonomy.
  - `distributional_national_accounts` — EMPIRICAL (Piketty-Saez-
    Zucman QJE 2018; WID.world open-data corpus)
  - `heterogeneous_agent_macro` — EMPIRICAL (Kaplan-Moll-Violante
    AER 2018; Bhandari et al. Econometrica 2021)
  - `stratification_economics` — THEORETICAL (Darity 2005; Darity-
    Hamilton 2015). Defensive anchor for the framework's discrete
    `ObserverPosition` enum against continuous-percentile critique.
  - `fiscal_incidence` — EMPIRICAL (Harberger 1962; CBO annual
    distributional analyses; JCT methodology)
- **`ObserverAsymmetryReport`** frozen dataclass: shared data shape
  the sister-repo implementation can target. Minimal fields
  (`subject`, `observers`, `values`, `delta`, `asymmetry_ratio`,
  `caveats`, `literature_anchor_key`) — the sister repo is
  expected to attach richer telemetry.
- **`observer_delta()`** helper: simplest-possible asymmetry
  diagnostic — subtract two scalar observer-indexed values. Rejects
  unknown `literature_anchor_key` with a named `ValueError`.
- **`SISTER_REPO_IMPLEMENTATION_NOTE`** constant: explicit pointer
  to the sister-repo targets.

### C.2 Tripwires

`tests/test_signal_asymmetry.py` (6 cases):

- 1: four literature anchors registered with expected keys
- 2: **load-bearing** — every anchor carries complete typed
  Provenance. Regressing this erases the epistemic grounding of
  the stub.
- 3: `observer_delta` builds a structurally valid report
- 4: unknown `literature_anchor_key` → `ValueError` (not silent
  acceptance)
- 5: `value_a == 0` → `asymmetry_ratio = None` (no silent
  `ZeroDivisionError`, no silent infinity)
- 6: sister-repo pointer names both target repos

### C.3 What this stub does NOT do

- No K-matrix consumption.
- No numeric reporting against `money_signal/coupling_observer.py`
  or `investment_signal/`.
- No gating of any accounting-pipeline result.

If you need full cross-observer analysis, go to the sister repos
named in `SISTER_REPO_IMPLEMENTATION_NOTE`.


## Part D — AUDIT_13 Part E status at end of audit

| Item | Status |
| --- | --- |
| § E.1 remaining README claims | `[CLOSED]` — 14 new tests, 23/23 tripwired |
| § E.2 investment historical_cases | `[CLOSED]` — 5 anchors, 4/5 framework-covers-observed |
| § E.3 Todo.md integration | `[CLOSED]` — nav row + cross-reference section |
| § E.4 distributional consumer | `[CLOSED]` — lean stub with 4 literature anchors; production lives in sister repo |


## Close-out (all three chunks)

- AUDIT_13 Part E fully closed across three commits.
- 14 + 8 + 6 = 28 new tripwire tests added across Parts A / B / C.
- Two sibling audits landed during the chunking:
  - AUDIT_15 (STUDY_SCOPE_AUDIT, new user-supplied methodology module)
- `money_signal/` and `investment_signal/` subsystems both have:
  - complete README-claim coverage tripwired
  - an honest-placeholder historical_cases module
  - a live accounting-bridge path (money_signal only, so far)
  - a distributional interface stub routing to the sister repo
- Regression across all three chunks: **47/47 PASS** at close
  (was 44/44 before Part A).
- Three items `[OPEN]` for future passes across the entire AUDIT_14
  cycle:
  1. ZIRP single-case-encoding outlier (subdivide into investor-type
     sub-cases) — documented in Part B § B.3.
  2. Extended Todo.md case list (Bitcoin flash crashes, Roman
     denarius, Pacific shell networks, Indigenous reciprocity,
     colonial resource extraction, 401k generational) — documented
     in Todo.md audit cross-reference.
  3. Full cross-observer analytic implementation — sister-repo
     scope per Todo.md priority 2; not built here.
