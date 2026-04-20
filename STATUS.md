# STATUS.md

Status of the metabolic-accounting framework at end of session.

## Verified (all tests run, all passing)

Thirty-four test suites, every one runs and passes:

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
```

See `docs/AUDIT_06.md` for the cross-check that landed the last three.

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
