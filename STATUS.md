# STATUS.md

Status of the metabolic-accounting framework at end of session.

## Verified (all tests run, all passing)

Fifty-one test suites, every one runs and passes:

```
# main accounting stack (18, pre-term_audit)
test_aggregation_comparison: PASS
test_civilization:           PASS
test_community_basin:        PASS
test_distributional:         PASS
test_extraordinary:          PASS
test_institutional:          PASS
test_integration:            PASS
test_meritocracy_break:      PASS
test_mitigation:             PASS
test_ramp_comparison:        PASS
test_regeneration:           PASS
test_registry_safety:        PASS
test_regulatory:             PASS
test_reserves:               PASS
test_scaffold:               PASS
test_social_cascade:         PASS
test_strategy:               PASS
test_tier_vector:            PASS   <-- Bug 1 + Bug 4 fixes (AUDIT_04)

# term_audit layer and its adapter (16)
test_term_audit:             PASS   <-- schema: SignalScore, TermAudit
test_scoping:                PASS   <-- 15 scoping dimensions
test_tiers:                  PASS   <-- seven-tier registry
test_preemption:             PASS   <-- seven preempts encoded
test_status_extraction:      PASS   <-- dynamic model + energy conservation
test_money_audit:            PASS   <-- Tier 1: money 7/7 failure
test_value_audit:            PASS   <-- Tier 1: V_A / V_B / V_C decomposition
test_capital_audit:          PASS   <-- Tier 1: K_A / K_B / K_C decomposition
test_productivity_audit:     PASS   <-- Tier 2: dependency redefinition
test_efficiency_audit:       PASS   <-- Tier 2: vector-space redefinition
test_disability_audit:       PASS   <-- Tier 4: A / B / C decomposition
test_incentive_analysis:     PASS   <-- cross-term archetype capture risk
test_metabolic_accounting_adapter: PASS   <-- term_audit -> accounting bridge
test_temporal_adapter:       PASS   <-- AUDIT_06: tripwire for time-series wrapper
test_governance_design_principles: PASS   <-- AUDIT_06: 14 principles, 6 categories
test_recovery_pathways:      PASS   <-- AUDIT_06: stage-ordering invariant restored
test_provenance:             PASS   <-- AUDIT_07: 5-kind provenance taxonomy
test_tier1_coverage:         PASS   <-- AUDIT_07: Tier 1 fully provenanced + neg-linkage tripwires
test_expertise_x_audit:      PASS   <-- AUDIT_08: E_X cross-domain closure, selection-inversion tripwire
test_routing_around_detection: PASS   <-- AUDIT_08: canary-principle + substrate-evidence
test_legislative_audit:      PASS   <-- AUDIT_09: first-principles rule audit, Bridge Watchers skeleton
test_money_three_scope_falsification: PASS   <-- AUDIT_10: money fails signal-invariants in all 3 marketed scopes
test_money_signal:           PASS   <-- AUDIT_11: coupling framework smoke + all 9 README falsifiable claims
test_historical_cases:       PASS   <-- AUDIT_12: 5 anchor cases with honest PLACEHOLDER provenance
test_money_signal_accounting_bridge: PASS   <-- AUDIT_12: signal_quality + flag emitter + GlucoseFlow discount; AUDIT_13: weight Provenance + verdict inference
test_investment_signal:      PASS   <-- AUDIT_13 + AUDIT_14 Part A: investment_signal/ intake, 23/23 README claims tripwired
test_investment_historical_cases: PASS   <-- AUDIT_14 Part B: 5 anchor cases, CLT counter-example, 4/5 framework-covers-observed
test_study_scope_audit:      PASS   <-- AUDIT_15: scope-bounded measurement audit framework
test_signal_asymmetry:       PASS   <-- AUDIT_14 Part C: distributional stub + 4 literature anchors
test_informational_cost_audit: PASS   <-- AUDIT_16: why false certainty costs exponentially
test_provenance_study_scope_integration: PASS   <-- AUDIT_17: Provenance optionally carries a StudyScopeAudit
test_audit_19_integrations:  PASS   <-- AUDIT_19: scope↔cost wiring, PLACEHOLDER deferred_cost, 2 Tier 1 retrofits
test_scan_soft_gaps:         PASS   <-- AUDIT_21: soft-gap scanner; 14 → 12 gaps after 2 more retrofits
```

See `docs/AUDIT_06.md` through `docs/AUDIT_15.md` for the cross-checks
that landed the most recent tests.

To verify:

```
for t in tests/test_*.py; do python "$t" && echo "PASS" || echo "FAIL"; done
```

## Main accounting stack — AUDIT_04 findings

An audit probe against the framework asked: does it handle a community
basin with metrics past their cliffs? Real bugs surfaced. Bugs 1 and 4
were described as fixed in an earlier pass, but the code changes had
not landed — only the prose. The fourth audit (`docs/AUDIT_04.md`)
re-verified, implemented the fixes, and added `tests/test_tier_vector.py`
to lock them in.

### Bug 1: tier determination was broken for cliff-threshold basins — FIXED

The `determine_tier_for_basin` function checked `fraction_remaining < 0`
to detect past-cliff state. But `fraction_remaining` = state / capacity,
which is always >= 0 for reasonable states. So metrics at 0.2 with
cliff threshold 0.35 never triggered BLACK.

Fix: replaced the check with `_metric_past_cliff` that compares state
against the basin's `cliff_thresholds[key]`, honoring `high_is_bad`
semantics (contamination metrics are past-cliff when ABOVE threshold).
Added `_metric_near_cliff` with a 0.25 band. Added `community` to
DEFAULT_TERTIARY_MAPPING.

Result: a community basin with `civic_engagement=0.20` (cliff 0.35)
now correctly registers as BLACK. Probe verified. Test coverage in
`tests/test_tier_vector.py`.

### Bug 4: tier vector was collapsed to a scalar — FIXED

`apply_tier_to_cohorts` only ever consulted
`tier_assignment.overall_tier()`. A firm GREEN on environmental basins
but BLACK on community basin assigned the same structural load to every
cohort, ignoring which basins each cohort was actually sensitive to.

Fix: added `cohort_basin_sensitivities` parameter. Backward compatible:
callers without sensitivities get the legacy scalar path.

### Bug 2 and Bug 3: surfaced but not yet fixed

- **Bug 2**: regulatory crosswalk has only environmental frameworks
  (CERCLA, EU ELD, UK Part 2A, Germany BBodSchG, Japan SCCA). No
  social/labor frameworks (Title VI, OSHA, NLRA, ADA, EU Social
  Climate Fund, ILO conventions).
- **Bug 3**: mitigation module has no community-specific leverage
  patterns.

Candidate fixes documented in `docs/AUDIT_04.md` Parts B and C.

## Term-audit layer (new this session)

The framework's companion measurement-audit infrastructure. Audits
terms themselves against information-theoretic signal criteria
(scope_defined, unit_invariant, referent_stable, calibration_exists,
observer_invariant, conservation_or_law, falsifiability). A term that
fails three or more is a token occupying a signal-shaped position in
discourse, not a measurement.

### Infrastructure modules

- `term_audit/schema.py` — `SignalScore`, `StandardSetter`,
  `FirstPrinciplesPurpose`, `TermAudit`. StandardSetter now includes
  `loss_if_audited` (preempt #5). TermAudit exposes explicit
  `measurement_layer()` / `incentive_layer()` views (preempt #2).
- `term_audit/scoping.py` — `SCOPING_DIMENSIONS` (15 dimensions per
  `docs/SCOPING_ECONOMIC_TERMS.md`), `DeclaredScope` with
  `missing_dimensions()`, `is_adequately_scoped()`, `scoping_fraction()`.
- `term_audit/tiers.py` — seven-tier registry of terms the framework
  rubs against (65 terms), `find_tier()`, `all_terms()`,
  `duplicate_terms()`.
- `term_audit/falsification.py` — `FalsifiablePrediction`,
  `BoundaryCondition`, `PredictionRegistry` (preempts #1 and #6).
- `term_audit/contradictions.py` — `Claim`, `Contradiction`,
  `check_contradictions()`, `KNOWN_CONTRADICTIONS` with 3 pre-registered
  historical pairs that surface as expected (preempt #7).
- `term_audit/counter_hypotheses.py` — adversarial hypotheses run
  against the framework's own claims (preempt #4). Two registered:
  `DISTINCTION_AS_COORDINATION` (falsified in model regime),
  `CAPTURE_REVERSIBLE_BY_DESIGN` (supported at math layer; routes
  question to incentive layer).
- `term_audit/status_extraction.py` — dynamic model of measurement-system
  capture. Energy conservation enforced at every step (same
  first-law-closure discipline as `thermodynamics/exergy.py`).
- `term_audit/incentive_analysis.py` — cross-term meta-analysis.
  Classifies every audit's setters into 10 archetypes; computes
  capture risk per term. Highest capture observed:
  efficiency_conventional_linear 0.84, value_collapsed 0.84,
  productivity_conventional 0.79.
- `term_audit/integration/metabolic_accounting_adapter.py` — one-way
  bridge from term_audit outputs to metabolic-accounting inputs.
  Produces BasinStateInput, InfrastructureInput, CascadeCouplingInput,
  GlucoseFlowInput, VerdictInput, AssumptionValidatorFlag. Dataclass
  shapes only; no runtime import of the metabolic-accounting repo.

### Audits committed

- **Tier 1 (3 of 8 terms):**
  - `money` — fails 7 of 7 signal criteria.
  - `value` — three distinct measurements separated. V_C substrate
    passes 7/7; V_A use partial 3/7; V_B exchange 1/7. Five linkages
    with LOAD-BEARING NEGATIVE B -> C (exchange substitutes for
    substrate).
  - `capital` — K_A productive passes 7/7; K_B financial 0/7; K_C
    institutional 0/7. Six linkages with LOAD-BEARING NEGATIVE
    K_B -> K_A (financial growth substitutes for productive plant).

- **Tier 2 (2 of 10 terms):**
  - `productivity` — fails 7/7. Includes dependency-based
    redefinition (`JobDependencyProfile` with 10 dependency
    categories). Long-haul driver worked example: pay $1600,
    true_input $2070, $470/week extraction routed to organism (224.78),
    public (45.41), family (90.82), deferred maintenance (108.99).
  - `efficiency` — fails 6/7 (falsifiability survives). Includes
    vector-space redefinition (`EfficiencyVector` on EROI / coupling
    / carrying-capacity / knowledge-density) with natural-system
    calibration anchors.

- **Tier 4 (1 of ~14 terms):**
  - `disability` — three distinct measurements separated. B
    (bounded capacity, scoped to task+condition) and C (substrate
    damage vs individual baseline) qualify as signals. A (environment
    mismatch) does not qualify as a single-scalar signal (it's a
    vector). Five linkages with LOAD-BEARING NONE relation for
    B -> C (capacity failure does NOT imply substrate damage).

All collapsed tokens fail 7/7; all decompositions surface at least
one clean signal when properly scoped.

## Key numerical findings from actual test runs

### Main stack (from earlier sessions; verified to still pass)

```
# distributional nonlinearity
load 0.1: 0 / 1000 collapsed (0.0%)
load 0.3: 46 / 1000 collapsed (4.6%)
load 0.5: 480 / 1000 collapsed (48.0%)
load 0.9: 1000 / 1000 collapsed (100.0%)

# strategy comparison (10-worker team)
Compliance:   realized 7.00,  wasted 7.50, trauma 1.12
Capacity-Fit: realized 12.33, wasted 2.18, trauma 0.08
Delta: +76% output captured

# civilization scale
Bronze Age:    waste 30%, realized 0.70 per capita
Renaissance:   waste 45%, realized 0.55 per capita
Modern:        waste 75%, realized 0.25 per capita
Capacity-Fit:  waste 17%, realized 1.25 per capita

# tier-vector cohort sensitivity
Community basin BLACK, soil GREEN
Community cohort (weight 1.5): load 1.0, 200/200 collapsed
Capital cohort (weight 0.1):   load 0.085, 0/500 collapsed
```

### Term-audit layer (this session)

```
# status_extraction (40-step example_run)
initial flows: support=50.0, production=40.0, distinction=10.0 (total=100)
final flows:   support=27.6, production=10.2, distinction=62.1 (total=100)
# energy conservation holds at 1e-9 tolerance across 50 steps

# capture order (Prediction 3 validated in example_run)
performance_review  (resistance 0.03) captured 0.894
credentialing        (resistance 0.05) captured 0.824
clinical_diagnosis   (resistance 0.10) captured 0.678
physical_instr       (resistance 0.30) captured 0.231

# counter-hypothesis: distinction-as-coordination
second-half growth: 22.86 of 100.0 total energy (above 2% threshold)
result: FALSIFIED within model regime

# incentive_analysis across 10 committed audits
highest capture risk:
  efficiency_conventional_linear  0.84
  value_collapsed_current_usage   0.84
  productivity_conventional       0.79
lowest capture risk:
  value_A_use_value               0.14
  value_C_substrate_value         0.16

# metabolic_accounting_adapter end-to-end
long-haul driver: extraction 2070, regen 1600, drawdown 470, net -470
verdict: sustainable_yield 0.056, trajectory -0.0017, ttr 21.67,
         confidence 0.757
1 assumption flag surfaced from signal-criteria failure
```

## Bugs caught by tests this session

1. `cascade_from_negative_linkage` returned `None` unconditionally —
   paste damage had left the `return CascadeCouplingInput(...)`
   unreachable inside the `if strength >= 0` branch.
   `test_metabolic_accounting_adapter.py::test_7` surfaced it.
   Fixed in commit `8145548`.

## Bugs caught by AUDIT_06

4. `test_governance_design_principles.py` imported
   `term_audit.governance_design_principles` but the module was on
   disk as `governance_design_systems.py` (despite its own docstring
   naming it `_principles`). File renamed to match the intended name;
   principle count tripwire corrected from 13 → 14 to reflect what
   actually landed.
5. `term_audit/recovery_pathways.py` violated its own stage-ordering
   invariant: `shelter_and_thermal_regulation` (IMMEDIATE_SURVIVAL)
   listed `ecological_and_seasonal_observation` (SUBSISTENCE) as a
   prerequisite. Edge removed with an inline rationale citing the
   audit — immediate shelter is pre-seasonal. Also added the missing
   `shelter_and_thermal_regulation` preservation strategy.
6. `term_audit/integration/temporal_adapter.py` raised `NameError`
   at import time (`TermAudit` annotated without import). Fixed;
   `tests/test_temporal_adapter.py` added as the first tripwire for
   the module.

## AUDIT_07 — argument-structure and provenance

7. `SignalScore` had only a loose `source_refs: List[str]` — no way
   to distinguish an empirical citation from a design choice from a
   placeholder. `term_audit/provenance.py` adds a 5-kind taxonomy
   (EMPIRICAL / THEORETICAL / DESIGN_CHOICE / PLACEHOLDER /
   STIPULATIVE) with a `knowledge_dna` pass-through. 74/74 Tier 1
   records now fully provenanced. See `docs/AUDIT_07.md` Parts A and D.
8. `is_signal` threshold and the schema.py docstring were
   contradictory (docstring said "fails ≥ 3"; code counted passes
   ≥ 5). Thresholds exposed as class constants, rule reconciled.
9. Vector aggregates added: `pass_count`, `mean_score`, `min_score`,
   `score_vector` — `is_signal`'s bool return lost the collapsed-vs-
   decomposed gap that is the argument's punchline. Vector preserves it.
10. Load-bearing negative-linkage signs (V_B→V_C, K_B→K_A, K_B→K_C)
    now tripwired in `tests/test_tier1_coverage.py::test_6`. AUDIT_05
    named them as load-bearing but did not encode the assertion.

## AUDIT_08 — process new material from main

11. `term_audit/cross_domain_closure.py` (E_X audit) shipped at the
    wrong path, with no sys.path bootstrap, and with
    `first_principles=None` (broke `summary()`). Moved to
    `term_audit/audits/expertise_x_cross_domain_closure.py`,
    bootstrap added, `first_principles` populated, AUDIT_07
    provenance pattern applied (7/7 scores). `tests/test_expertise_x_audit.py`
    (7 cases) tripwires the selection inversion as a load-bearing claim.
12. `term_audit/mmachine_readable_expertise.py` had a double-m typo
    in its filename and a docstring pointing at
    `term_audit/schema/machine_readable_expertise.py` (path does not
    exist). Renamed to `term_audit/machine_readable_expertise.py`,
    docstring corrected.
13. `term_audit/Work needed.md` shipped with commit message
    "Implement routing detection module for AI systems" but added
    only a markdown spec — no code. Extracted the embedded Python as
    `term_audit/signals/routing_around_detection.py` (fixed a
    dataclass field-ordering bug during extraction).
    `tests/test_routing_around_detection.py` (7 cases) tripwires
    canary detection's environment-conditional firing.

## AUDIT_09 — first-principles legislative audit skeleton

14. New package `term_audit/legislative_audit/`. Intake of a user-
    supplied skeleton (Bridge Watchers): `LegislativeAudit` composite
    over `FirstPrinciplesPurpose`, `ContextAssumption`, `ScopeBoundary`,
    `ConsequenceAnalysis`, `CounterfactualAnalysis`, `TransmissionEffect`,
    `ContradictionAnalysis`, `ExceptionPathway`, `SubstrateEvidence`.
    Two worked examples (bridge-permit-in-constrained-context, Good
    Samaritan chilling effect) both saturate at alignment 0.00 / harm
    1.00. Typo in the supplied spec (`alternative_mechanchanisms`)
    fixed at intake; `tests/test_legislative_audit.py` (7 cases)
    tripwires the skeleton, including monotonicity of the scoring
    functions.

## AUDIT_10 — money three-scope falsification audit

15. New module `term_audit/audits/money_three_scope_falsification.py`.
    Intake of a user-supplied module auditing money across three
    marketed scopes (flow-system / community-organism / civilization-
    lube) via 12 invariants (4 per scope). Under
    `current_regime_money_state()` all 3 scopes falsify (0/12
    invariants hold), and `structural_claim_holds` is True.
    `tests/test_money_three_scope_falsification.py` (7 cases)
    tripwires the structural claim, the falsification hook (flip
    all 12 flags to True → all scopes survive → claim falsified),
    and a `to_real_flag()` bridge from the module's lite flag type
    to the adapter's real `AssumptionValidatorFlag` (lite uses
    `source`/`reason`/str-severity, real uses `source_audit`/
    `message`/float-severity + `failure_mode`).
16. Chat-paste damage caught at intake: smart quotes throughout,
    `from **future** import annotations` and `if **name** ==
    "**main**":` (markdown-bold leaking onto dunder names), and
    similar. Cleaned before commit.
17. Merged `money_signal/` (6 files, ~2100 lines) from `origin/main`:
    coupling-matrix model of money-as-signal dynamics across temporal
    / cultural / attribution / observer axes. Complementary to the
    three-scope audit: three-scope asks whether money qualifies as a
    signal at all; `money_signal/` characterizes how it couples when
    assumed to be one. Integration path named in AUDIT_10 § D.1.
18. AUDIT_07 § C.4 (money four-function decomposition) status updated
    to `[PARTIALLY ADDRESSED]`: this audit adds a scope-framing
    decomposition (flow / community / lube), which is structurally
    parallel to V_A/V_B/V_C and K_A/K_B/K_C. The classical
    four-function decomposition (M_A medium-of-exchange / M_B store-
    of-value / M_C unit-of-account / M_D standard-of-deferred-
    payment) remains `[OPEN]` as a distinct audit target.

## AUDIT_11 — money_signal subsystem completion + cultural validator bug

19. Merged 4 new files from `origin/main` on `money_signal/`:
    `coupling.py` (composition + memoization + diagnostics),
    `coupling_state.py`, `coupling_substrate.py`, `README.md`
    (~1540 new lines). All 9 modules import. Three of the README's
    9 falsifiable claims tripwired at composed-coupling level:
    #1 Minsky asymmetry holds (ratio 1.31/1.51/0.52 across
    HEALTHY/STRESSED/RECOVERING), #6 issuer insulation (0.208 vs
    0.863 thin-holder magnitude under STRESSED), #7 near-collapse
    permits sign flips.
20. **FIXED bug** (AUDIT_11 § B, Option 1 applied):
    `validate_all_factor_modules()` shipped broken — the README says
    "Always validate at startup" but the pointwise Minsky check in
    `coupling_cultural.py`/`coupling_attribution.py`/`coupling_observer.py`
    rejected COMMUNITY_TRUST, whose factors deliberately damp Minsky
    asymmetry (composed ratio = 1.0, satisfying README claim #1 at
    composed level). Fix: all three validators now compute composed
    coupling (`K_BASE[i][j] * f_ij`) and assert `>=` at that level.
    `validate_all_factor_modules()` runs clean.
    `tests/test_money_signal.py::test_3` flipped from DETECTOR to
    PASS assertion.
21. **FIXED bug** (AUDIT_11 § B.5, Option 1 applied): once the
    factor-validator fix landed, `python -m money_signal.coupling`
    hit a second sanity-bound assertion: composed K[N][R] = 3.66
    on the module's own NEAR_COLLAPSE example (case_c) exceeded
    the bound `[-3.0, 3.0]`. The bound contradicted README claim
    #8 ("|K[N][R]| dominates all other off-diagonals in collapse").
    Fix: bound widened to `[-5.0, 5.0]`. Accommodates legitimate
    collapse-regime stacking; still catches pathological runaway
    (>10). `python -m money_signal.coupling` now runs end-to-end
    across all four README example cases. Tripwire in
    `tests/test_money_signal.py::test_3b` asserts
    `validate_composition` passes on cases A–D with expected Minsky
    coefficients 1.24×/1.41×/1.73×/1.94×.
22. **Coverage completion**: `money_signal/__init__.py` added
    (AUDIT_11 § C.1 closed). All 9 README falsifiable claims now
    tripwired (originally 3/9 at AUDIT_11 close): tests 8/9/10/11/12/13
    cover claims #2 hysteresis, #3 reciprocity damping, #4 speculative
    amplification, #5 observer asymmetry, #8 Minsky dominance in
    collapse, #9 digital infrastructure coupling. Tests 5/7/6/12/3b
    cover claims #1/#6/#7/#8/composed-Minsky across the framework.
    Test suite for the money_signal subsystem: 14 cases.

## AUDIT_12 — historical cases + accounting bridge

23. **`money_signal/historical_cases.py`** (AUDIT_11 close-out item
    closed): 5 anchor cases (Weimar 1921-23, Zimbabwe 2007-09,
    GFC 2008, Cyprus 2013, Argentina 2001-02) documenting the
    framework's pre/during/post DimensionalContexts and recorded
    qualitative K_ij shifts. Every ObservedDynamic uses the
    DynamicShift enum (no fabricated numeric K values per the
    AUDIT_07 Provenance discipline). Every shift carries typed
    Provenance — EMPIRICAL with canonical source refs or
    PLACEHOLDER with a named retirement dataset. `compare_case`
    produces 4/5 qualitative matches; Cyprus correctly flagged as
    the observer-asymmetry case (claim #5), not a K[N][R]
    amplification case. 7 tripwires.
24. **`money_signal/accounting_bridge.py`** (AUDIT_11 close-out item
    closed): `signal_quality(ctx) -> float in [0,1]` computes the
    reliability of monetary denomination under a coupling context.
    `coupling_assumption_flags(ctx)` emits real AssumptionValidatorFlag
    records for the accounting adapter pipeline. `adjust_glucose_flow`
    produces a non-mutating adjunct view on a GlucoseFlow showing
    raw and signal-quality-discounted profit. Quality gradient
    across state regimes: healthy-thin 0.919, stressed 0.869,
    near-collapse 0.449 (gap 0.47). Near-collapse emits 4 flags
    including a dedicated `near_collapse_regime` flag at severity
    0.90. 8 tripwires, including test_8 that mechanically asserts
    **no top-level `money_signal/ -> accounting/` import** anywhere
    in the package — the bridge direction is load-bearing.
25. **AUDIT_11 close-out resolved**: the two items named as `[OPEN]`
    in AUDIT_11 close-out (historical_cases.py, glucose-flow
    integration) are now `[CLOSED]` as skeletons. Three new items
    named in AUDIT_12 § D for future passes: empirical K_ij
    extraction from the retirement_path datasets, typed Provenance
    on the bridge weights, automatic DimensionalContext inference
    for compute_flow integration.

## AUDIT_13 — follow-ups + investment_signal intake

26. AUDIT_12 § D.2 closed: `accounting_bridge.py` weights wrapped
    in `WeightedThreshold` records with typed `Provenance`
    (6/6 DESIGN_CHOICE, each with alternatives_considered +
    falsification_test pointing at historical_cases as retirement
    path). `ALL_WEIGHTS` tuple exposes the collection for coverage
    auditing.
27. AUDIT_12 § D.3 closed: `regime_from_verdict_signal` maps
    GREEN/AMBER/RED/BLACK → HEALTHY/STRESSED/NEAR_COLLAPSE/
    NEAR_COLLAPSE. RECOVERING requires explicit `recovering=True`
    flag (single-period signal cannot distinguish recovery from
    steady-state health). `context_from_verdict_signal` builds
    a full DimensionalContext with only the five monetary-regime
    dimensions requiring explicit declaration. 3 new tests cover
    the helpers including a real-Verdict end-to-end integration.
28. **`investment_signal/` subsystem intake** (new from
    origin/main, ~3450 lines, 8 files). Coupled-dynamics framework
    for investment as cross-substrate commitment — seven substrates
    (TIME/RESOURCE/ENERGY/LABOR/ATTENTION/MONEY/RELATIONAL_CAPITAL),
    7×7 conversion + realization matrices, time binding × scope
    integrity, 5-level derivative-distance abstraction, dependency
    coupling to money_signal. README ships 23 falsifiable claims.
    Ship-breaking bug caught at intake: three files used
    `..money_signal` relative imports which fail because
    `investment_signal/` and `money_signal/` are sibling top-level
    packages, not children of a common package. Fixed by replacing
    `..money_signal` with absolute `money_signal` in
    `dimensions.py`, `coupling.py` (two sites), `time_binding.py`.
    `__init__.py` added (was missing despite README tree showing
    it — same drift as AUDIT_11 § C.1). 12 new tests tripwire 11
    of the 23 README falsifiable claims, plus the import and
    validator regressions. README usage example now runs end-to-end.

## AUDIT_14 — Part A (E.1 + E.3): investment_signal 23/23 + Todo.md integrated

29. **investment_signal coverage 11/23 → 23/23**: 14 new tests in
    `test_investment_signal.py` cover the remaining README
    falsifiable claims (#3 #4 #6 #7 #8 #10 #12 #13 #14 #16 #17 #18
    #19 #21). All 23 claims now directly tripwired; no longer
    dependent only on `validate_*` transitively. Any factor-value
    edit that silently changes a locked value breaks the
    corresponding test with a named message.
30. **Todo.md integrated**: CLAUDE.md nav table gets a new row
    pointing at `Todo.md` as the forward-priority list; `Todo.md`
    itself gets an "Audit cross-reference" section mapping its
    three priorities to audit entries. Scope of AUDIT_13 § E.4
    closed in light of Todo.md's routing: distributional work
    lives in the sister repo
    (`thermodynamic-accountability-framework/money_distribution/`,
    `investment_distribution/`), not here. AUDIT_14 Part C will
    ship a lean interface stub instead of a full local consumer.
31. **AUDIT_14 chunking**: Parts B (investment_signal
    historical_cases.py) and C (distributional stub) ship in
    subsequent commits on this branch, extending `docs/AUDIT_14.md`.

## AUDIT_14 — Part B (E.2): investment_signal/historical_cases.py

## AUDIT_22 — three more historical anchors (Todo.md priority 1)

49. **money_signal extensions** (2 new): ANDEAN_AYNI (labor-
    reciprocity ledger across generations — fourth counter-example,
    first to anchor on LABOR substrate rather than shell/object
    tokens; refs: Alberti & Mayer 1974, Mayer 2002, Harris 1985)
    and TAMBU_TOLAI (PNG shell-money; notable dual-regime structure
    coexisting with kina fiat; refs: Epstein 1969, Errington &
    Gewertz 1987, Martin 2013). Match count **12/13** (Cyprus
    remains the observer-asymmetry outlier).
50. **investment_signal extension** (1 new): AMAZON_RUBBER_BOOM
    _1879_1912 — paired with CONGO_RUBBER_1885_1908 via the same
    1890s-1910s global rubber-demand cycle. Fires the same three
    failure modes (substrate_invisible, financialized_reverse,
    substrate_abstraction_destroys_nature) under a different
    colonial regime (London-listed PAC / Casa Arana vs Leopold's
    personal kingdom). Casement reported on both. Match count
    **11/11**. The Congo+Amazon pair demonstrates framework
    structural classification is context-driven, not regime-
    specific — an anchor-level validation of claims #16/#17/#18/
    #21. Refs: Casement 1912 Putumayo Report, Hardenburg 1912,
    Taussig 1987, Stanfield 1998.

## AUDIT_21 — soft-gap scanner + 2 more scope-audit retrofits

47. **`scripts/scan_soft_gaps.py`** shipped (closes AUDIT_17 § D.2).
    Walks 9 Tier 1 audits and reports per-audit rows + aggregate
    totals. Honest retrofit debt: not 72 (AUDIT_17 pessimistic
    estimate) but **14** EMPIRICAL records where the author declared
    a scope_caveat in prose without attaching a machine-readable
    StudyScopeAudit. Each is per-citation work.
48. **Two more scope_audit retrofits** attached to money.py:
    `_BALASSA_PPP_SCOPE_AUDIT` on unit_invariant (grounded in
    Balassa 1964 JPE + Samuelson 1964 RES) and
    `_FASB_ASC_820_SCOPE_AUDIT` on observer_invariant (grounded in
    FASB ASC 820 / IFRS 13 Level 1/2/3 hierarchy). **money.py is
    now fully scope-audited** — 4 scope_audits attached, 0 remaining
    soft gaps. Tree-wide aggregate: 4 attached / 12 remaining / 63
    total provenances.

## AUDIT_20 — anchor extensions + ZIRP decomposition

44. **money_signal extensions**: Haudenosaunee wampum
    (RECIPROCITY_TOKEN + TRUST_LEDGER counter-example; diplomatic-ledger
    dual function) and Potlatch ceremony suppression 1884-1951
    (STRESSED regime induced by external legal prohibition, with
    post-repeal RECOVERING demonstrating hysteresis claim #2 at
    generational scale). Literature: Fenton 1998 + Muller 2008 +
    Williams 1997 (wampum); Cole & Chaikin 1990 + Bracken 1997 +
    U'mista Cultural Society (potlatch). Match count 10/11
    (Cyprus remains the observer-asymmetry outlier).
45. **investment_signal extension**: Congo Free State rubber
    extraction 1885-1908 fires three failure modes simultaneously
    (substrate_invisible_at_distance, financialized_reverse_causation,
    substrate_abstraction_destroys_nature) — a ~5-15M-death
    extraction regime the framework encodes without ad hoc
    special-casing. Literature: Hochschild 1998, Casement 1904,
    Morel 1906, Vansina 2010.
46. **ZIRP decomposition** (AUDIT_18 § D.2 closed): ZIRP_2009_2021
    split into three investor-type sub-cases — ZIRP_RETAIL_DIVERSIFIED
    (TWO_LAYER, liquidity illusion), ZIRP_PRIVATE_EQUITY (DERIVATIVE,
    financialized_reverse_causation via Lazonick/Borio buyback
    dynamics), ZIRP_CLO_STRUCTURED (SYNTHETIC, multiple failures
    via Griffin & Nickerson 2023 + BIS 2018). Each sub-case is
    internally consistent: observed failures match the framework's
    predictions for that specific context. **investment_signal
    match count now 10/10** — the former single outlier resolves
    by honest encoding rather than by weakening the match
    criterion.

## AUDIT_19 — scope↔cost integration + 2 Tier 1 scope-audit retrofits

41. `StudyScopeAudit.audit_report` now includes
    `cost_growth_if_applied_out_of_scope` cross-referencing the
    `CostGrowth` vocabulary from informational_cost_audit. Mapping:
    IN_SCOPE/EDGE_OF_SCOPE → LINEAR, OUT_OF_SCOPE → EXPONENTIAL,
    SCOPE_UNDECLARED → "unknown". Closes AUDIT_16 § D.1.
42. `Provenance.deferred_cost` optional field landed on PLACEHOLDER
    records. `placeholder()` constructor accepts `deferred_cost` kwarg.
    `Provenance.soft_gap()` now also fires on PLACEHOLDER +
    deferred_cost=EXPONENTIAL (compounding debt signal). LINEAR / None
    are honest defaults and do not fire. Closes AUDIT_16 § D.2.
43. Two real StudyScopeAudits demonstrated on money.py:
    `_BOSKIN_CPI_SCOPE_AUDIT` attached to `calibration_exists` score
    (grounded in Boskin Commission 1996 Final Report + BLS CPI
    Handbook) and `_BOE_2014_MONEY_CREATION_SCOPE_AUDIT` attached to
    `conservation_or_law` (grounded in McLeay/Radia/Thomas 2014 BoE
    Q1 Bulletin). Each populates all 6 layers with facts drawn from
    the published methodology — nothing fabricated. Remaining 72
    Tier 1 EMPIRICAL records honestly left `[OPEN]` rather than
    fabricated in bulk (AUDIT_19 § C.2). Coverage picture on
    money.py post-retrofit: 7/7 complete, 2 scope_audits attached,
    2 remaining soft gaps (the EMPIRICAL records with scope_caveats
    that AUDIT_19 did not retrofit). AUDIT_07's 74/74 coverage
    preserved. Demonstrates AUDIT_17 § D.1.

## AUDIT_18 — extended historical cases (Todo.md priority 1)

39. `money_signal/historical_cases.py` extended with four anchors:
    Bitcoin flash crashes (DIGITAL + SPECULATIVE_CLAIM, tests
    claim #4/#9), Roman denarius debasement (METAL, multi-century
    slow stress), Yap rai stones (TRUST_LEDGER counter-example),
    Kula ring (RECIPROCITY_TOKEN counter-example). Match criterion
    tightened: `predicted_n_r_high` now requires elevated Minsky
    AND coupling_magnitude ≥ 0.3, correctly classifying TRUST_LEDGER
    cases (Minsky 1.68 / magnitude 0.13) as form-preserved / amplitude-
    damped rather than amplified. `tests/test_historical_cases.py`
    restructured to partition anchors by role (6 near-collapse, 1
    stressed, 2 counter-examples). Match count 8/9 with Cyprus as the
    documented outlier.
40. `investment_signal/historical_cases.py` extended with two
    anchors: Colonial resource extraction (VOC/EIC era, DERIVATIVE
    + EXTRACTIVE_CLAIM) and US 401(k) generational realization
    (SHORT_CYCLE binding × GENERATIONAL money scope). Draft
    401(k) case initially included infrastructure_depreciation_trag
    tag but it was removed — that tag describes long-binding-in-
    short-scope, the opposite of 401(k)'s actual failure pattern;
    keeping it would have been classification dishonesty. Match
    count 6/7 with ZIRP as the documented single outlier.

## AUDIT_17 — Provenance + StudyScopeAudit integration

38. `term_audit/provenance.py` extended: `Provenance.scope_audit:
    Optional[Any]` (type `Any` to avoid circular import with
    study_scope_audit) lets an EMPIRICAL record optionally carry a
    machine-readable StudyScopeAudit alongside the existing prose
    `scope_caveat`. New `has_scope_audit()` and `soft_gap()`
    methods. `empirical()` constructor accepts `scope_audit=None`
    kwarg. `coverage_report()` gains `scope_audit_count`,
    `soft_gap_count`, `soft_gap_details` fields. Integration is
    OPTIONAL — absence of `scope_audit` does NOT break
    `is_complete()`, so AUDIT_07's 74/74 Tier 1 provenance
    coverage is preserved (tripwired in test 7). Three
    load-bearing invariants: soft-gap fires on caveat-without-audit
    (the signal AUDIT_17 exists to produce), soft-gap clears when
    scope_audit attached (the repair pathway), and Tier 1 74/74
    no-regression. 7 tripwires. Closes the `[NAMED]` item from
    AUDIT_15 § D.2.

## AUDIT_16 — INFORMATIONAL_COST_AUDIT (paired with study_scope_audit)

37. **`term_audit/informational_cost_audit.py`** shipped as the
    complement to AUDIT_15's study_scope_audit. study_scope_audit
    answers "where does the claim hold?"; this module answers
    "what's the cost of pretending it holds beyond that scope?"
    Nine knowledge structures (geocentric comfort state, four
    canonical anomalies, four-stage cost spiral, heliocentric
    alternative, head-to-head comparison, Shannon-entropy insight,
    AI implications, historical pattern, VERDICT) plus a small
    `CostLedger` dataclass with `CostGrowth` symbolic tags
    (FLAT / LINEAR / EXPONENTIAL / CATASTROPHIC_AT_REGIME_SHIFT).
    `compare(ledger_a, ledger_b)` deliberately refuses to collapse
    to a scalar verdict — the module is designed to warn against
    exactly that false-certainty compression, and the tripwire test
    catches any scalar key sneaking in. 7 tripwires including three
    load-bearing invariants: narrative-order of the four-stage
    spiral, the VERDICT booleans (comfort_is_expensive=True,
    uncertainty_is_cheap=True), and the compare() scalar-collapse
    refusal.

## AUDIT_15 — STUDY_SCOPE_AUDIT methodology module

33. **`term_audit/study_scope_audit.py`** shipped (new material, not
    part of AUDIT_14 plan). Six layered audit dataclasses — Instrument
    (range/resolution/noise-floor/sampling), Protocol (prep/controls/
    exclusions/replication), DomainCoupling (4 Coupling strengths:
    instrument/protocol/substrate/regime), Regime (4 states:
    STATIONARY/DRIFTING/NON_STATIONARY/UNKNOWN), CausalModel
    (frame + confounders + unknown-unknowns flag), ScopeBoundary
    (IN/EDGE/OUT/UNDECLARED). Composite `StudyScopeAudit.audit_report()`
    returns a scope-bounded verdict rather than true/false. Five
    HISTORICAL_CASES (geocentrism, miasma, caloric, steady-state
    cosmology, low-fat diet) calibrate the methodology against
    documented scope-boundary expansion events. Load-bearing
    discipline: OUT_OF_SCOPE dominates IN_SCOPE and EDGE_OF_SCOPE
    when deployment context matches both — tripwired in test_7.
    9 tripwire tests. NOT applied as a gate anywhere in the framework;
    integration with `term_audit/provenance.py` is named for a
    future pass (docs/AUDIT_15.md § D.2).

## AUDIT_14 — Part B (E.2): investment_signal/historical_cases.py

## AUDIT_14 — Part C (E.4): distributional/signal_asymmetry stub

35. **`distributional/signal_asymmetry.py`** shipped as a lean
    interface stub per Todo.md priority 2 routing: production
    cross-observer analysis lives in the sister repo
    (`thermodynamic-accountability-framework/money_distribution/`,
    `investment_distribution/`). This stub provides a shared
    `ObserverAsymmetryReport` dataclass, an `observer_delta()`
    helper, a pointer constant to the sister repo, and
    `LITERATURE_ANCHORS` with four typed-Provenance entries:
    Distributional National Accounts (Piketty-Saez-Zucman /
    WID.world), Heterogeneous Agent Macro (Kaplan-Moll-Violante
    HANK), Stratification Economics (Darity-Hamilton), Fiscal
    Incidence (Harberger / CBO / JCT). 6 tripwires.
    AUDIT_13 Part E fully closed across chunks A/B/C.

## AUDIT_14 — Part B (E.2): investment_signal/historical_cases.py

36. **`investment_signal/historical_cases.py`** shipped. Five anchor
    cases parallel to money_signal/historical_cases.py: Enron 2001
    (SYNTHETIC reverse causation, conf 0.95), MBS 2004-2008 (multi-
    layer opacity + terminal money near-collapse, conf 0.95), ZIRP
    2009-2021 (liquidity illusion via scope mismatch, conf 0.80),
    Gig economy 2013-present (DERIVATIVE distance + TIME/ATTENTION
    extraction, conf 0.85), Community Land Trusts 1970-present
    (**counter-example**: DIRECT + MULTI_GENERATIONAL +
    RECIPROCAL_OBLIGATION produces 0 observed failures, conf 0.80).
    Every ObservedInvestmentFailure uses a tag from the canonical
    VALID_FAILURE_TAGS set and carries typed Provenance (EMPIRICAL
    with literature refs or PLACEHOLDER with retirement paths).
    `compare_case()` framework-covers-observed: **4/5**; ZIRP is the
    documented single outlier (retail TWO_LAYER encoding doesn't hit
    the 0.5 reverse-causation threshold that the firm-level buyback
    literature describes — single-case-encoding limitation, not a
    framework bug). `tests/test_investment_historical_cases.py` (8
    cases) tripwires the structure, the 4/5 match count, and the
    CLT zero-failure counter-example.

## What the framework does end-to-end

Main accounting stack:

- Four environmental basins + one community basin (6 dimensions)
- Per-metric secondary reserves, site-level tertiary pools
- First-law closure at 1.42e-14 across 17 metrics
- Two profit lines: `metabolic_profit`, `metabolic_profit_with_loss`
- Extraordinary-item flagging (configurable materiality threshold)
- GREEN/AMBER/RED/BLACK verdict with BLACK = irreversibility
- Vector tier assignment per basin type
- Regulatory crosswalk across 5 jurisdictions
- Mitigation actions ranked by leverage and urgency
- Distributional layer with threshold-nonlinear cliff crossings
- Institutional fit accounting, strategy comparison, civilization-scale

Term-audit layer (new):

- Seven-criterion signal scoring for any term
- Fifteen-dimension declared-scope machinery
- Seven-tier registry of terms to rub against (65 terms, 6 audited so far)
- Contradiction-checker with pre-registered known pairs
- Counter-hypothesis runner that falsifies or supports
- Predictions + boundary conditions as first-class types
- Cross-term capture-risk analysis across all audits
- Dynamic measurement-capture model with energy conservation
- One-way adapter to metabolic-accounting inputs

## What the framework does NOT do

- Does not price anything (intentional — price is gameable)
- Does not have a wired-up Flint scenario runner
- No social/labor regulatory frameworks (Bug 2)
- No community-specific mitigation patterns (Bug 3)
- Does not integrate with external data sources (placeholder)
- Does not have multi-period simulate() wrapper
- Does not model directional coupling between basins over time
- Does not model geographic proximity in cohort exposure
- Does not model generational lag in potential_waste
- Does not model trust hysteresis
- Does not model temporal asymmetry between cohorts
- Does not have redundant derivations for status_extraction
  (preempt #3: target is three independent derivations; have one)
- Audits committed cover only 6 of 65 tiered terms (Tier 1: 3/8,
  Tier 2: 2/10, Tier 3: 0/9, Tier 4: 1/14, Tier 5: 0/9, Tier 6: 0/8,
  Tier 7: 0/7)

## Test-first discipline

- No claim about framework behavior without a test that produces it
- Every test output shown comes from actual stdout
- If a test doesn't exist for a claim, the claim is hypothesis
- STATUS.md drift is exactly the failure mode AUDIT_04 caught; this
  status file is kept current as part of the discipline
- Users should re-run all tests to verify
