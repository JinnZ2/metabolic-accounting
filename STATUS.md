# STATUS.md

Status of the metabolic-accounting framework at end of session.

## Verified (all tests run, all passing)

Eighteen test suites, every one runs and passes:

```
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
test_tier_vector:            PASS   <-- NEW: Bug 1 + Bug 4 fixes
```

To verify:

```
cd metabolic-accounting
for t in tests/test_*.py; do python "$t" && echo "PASS" || echo "FAIL"; done
```

## Audit findings and fixes (this session)

An audit probe was run against the framework asking: does it handle
a community basin with metrics past their cliffs? Real bugs surfaced.

### Bug 1: tier determination was broken for cliff-threshold basins — FIXED

The `determine_tier_for_basin` function checked `fraction_remaining < 0`
to detect past-cliff state. But `fraction_remaining` = state / capacity,
which is always >= 0 for reasonable states. So metrics at 0.2 with
cliff threshold 0.35 never triggered BLACK.

Fix: replaced the check with `_metric_past_cliff` that compares state
against the basin’s `cliff_thresholds[key]`, honoring `high_is_bad`
semantics (contamination metrics are past-cliff when ABOVE threshold).

Also added `_metric_near_cliff` with a 0.25 band that catches metrics
within a quarter of the capacity-to-cliff range without false-flagging
healthy baselines.

Also added the “community” basin type to DEFAULT_TERTIARY_MAPPING so
the four social tertiary pools (social_fabric_reserve,
generational_transmission, institutional_stock, civic_trust_reserve)
correctly drive community-basin tier determination.

Result: a community basin with `civic_engagement=0.20` (cliff 0.35)
now correctly registers as BLACK. Probe verified. Test coverage
in test_tier_vector.py.

### Bug 4: tier vector was collapsed to a scalar in distributional layer — FIXED

`apply_tier_to_cohorts` only ever consulted `tier_assignment.overall_tier()`.
A firm GREEN on environmental basins but BLACK on community basin
assigned the same structural load to every cohort, ignoring which
basins each cohort was actually sensitive to.

Fix: added `cohort_basin_sensitivities` parameter. Each cohort can now
specify which basin types it’s sensitive to with absolute weights:

```python
sensitivities = {
    "community_members": {"community": 1.5, "soil": 0.4},
    "capital_market":    {"community": 0.1, "soil": 0.1},
}
```

Load is a weighted sum of per-basin-type tier loads, clipped to [0, 1].
Backward compatible: callers without sensitivities get the legacy
scalar path.

Also added `per_cohort_structural_load: Dict[str, float]` to AccessReport
so cohort-level load is visible in the report output.

Result (from test 4): community cohort weighted 1.5 × BLACK load gets
full 1.0 load → 200/200 collapsed. Capital cohort weighted 0.1 gets
load 0.085 → 0/500 collapsed. Same BLACK tier, different exposure.

### Bug 2 and Bug 3: surfaced but not yet fixed

- **Bug 2**: regulatory crosswalk has only environmental frameworks
  (CERCLA, EU ELD, UK Part 2A, Germany BBodSchG, Japan SCCA). No
  social/labor frameworks (Title VI, OSHA, NLRA, ADA, EU Social
  Climate Fund, ILO conventions). A firm destroying community
  vitality gets no regulatory toe-in points.
- **Bug 3**: mitigation module has no community-specific leverage
  patterns. It does surface social tertiary pools when they’re near
  cliff (because that logic is generic), but nothing that recognizes
  “economic_security near cliff → invest in local employment” or
  similar community-basin-specific actions.

These remain as documented open issues. See `docs/AUDIT_04.md` when
next written.

## Hidden variables found in the audit (for future work)

Things the framework doesn’t yet capture that matter for vector
consequences:

1. **Directional coupling over time.** Community basin degradation
   CAUSES environmental basin degradation (a collapsed community
   can’t maintain infrastructure). The vector is not static — basins
   feed each other.
1. **Geographic proximity.** Cohort sensitivity to basin damage is
   proximity-based, not just categorical. Workers who commute into
   the damage zone bear less load than residents. The framework
   currently models cohorts as undifferentiated by location.
1. **Generational lag in potential_waste.** A child whose parents were
   constrained develops lower available_capacity. The waste category
   doesn’t reset per-person — it compounds across generations.
1. **Trust hysteresis.** Once a community loses trust
   (civic_trust_reserve past cliff), cohort sensitivity to
   institutional signals drops toward zero. Additional damage produces
   no additional load-response because the cohort has already
   disengaged. Missing from current model.
1. **Temporal asymmetry between cohorts.** Capital market absorption
   is forward-priced (spreads move on expectations); community
   absorption is backward-realized (property values crash after
   visible decline). Current framework treats them on the same
   period scale.

## What the framework does end-to-end

- Four environmental basins + one community basin (6 dimensions)
- Per-metric secondary reserves, site-level tertiary pools
- First-law closure at 1.42e-14 across 17 metrics
- Two profit lines: metabolic_profit, metabolic_profit_with_loss
- Extraordinary-item flagging (configurable materiality threshold)
- Cumulative environment loss across periods
- GREEN/AMBER/RED/BLACK verdict with BLACK = primary irreversibility
  or tertiary past cliff
- Vector tier assignment per basin type (community can be BLACK while
  soil is GREEN)
- Regulatory crosswalk across 5 jurisdictions
- Mitigation actions ranked by leverage and urgency
- Distributional layer: threshold-nonlinear cliff crossings,
  no price, no currency
- Institutional fit accounting: available_capacity, fit_multiplier,
  trauma_tax, waste_ratio, amplification_ratio
- Strategy comparison: compliance vs capacity_fit tradeoff
- Civilization-scale audit: four waste categories
  (institutional, forced_dependency, labor, potential) across eras
- Vector-aware cohort sensitivities for per-basin-type load

## Key numerical findings from actual test runs

### Distributional nonlinearity (test_distributional)

```
load 0.1: 0 / 1000 collapsed (0.0%)
load 0.3: 46 / 1000 collapsed (4.6%)
load 0.5: 480 / 1000 collapsed (48.0%)
load 0.9: 1000 / 1000 collapsed (100.0%)
```

Nonlinear threshold dynamics visible in actual output.

### Meritocracy break (test_meritocracy_break)

Constrained neurodivergent worker at fit 0.2 outperforms unconstrained
neurotypical until fit drops below ~0.233. Framework computes this
crossover.

### Strategy comparison (test_strategy, 10-worker team)

```
Compliance:   realized 7.00,  wasted 7.50, trauma 1.12
Capacity-Fit: realized 12.33, wasted 2.18, trauma 0.08
Delta: +76% output captured
```

### Civilization scale (test_civilization)

```
Bronze Age:    waste ratio 30%, realized 0.70 per capita
Renaissance:   waste ratio 45%, realized 0.55 per capita
Modern:        waste ratio 75%, realized 0.25 per capita
Capacity-Fit:  waste ratio 17%, realized 1.25 per capita
```

### Tier-vector (test_tier_vector, this session)

```
Community basin BLACK, soil GREEN
Community cohort (weight 1.5 on community):  load 1.0, 200/200 collapsed
Capital cohort (weight 0.1 on community):    load 0.085, 0/500 collapsed
```

The vector is preserved — cohorts see their actual exposure, not the
scalar worst-basin tier.

## What the framework does NOT do

- Does not price anything (intentional — price is gameable)
- Does not have a wired-up Flint scenario runner
- No social/labor regulatory frameworks (Bug 2)
- No community-specific mitigation patterns (Bug 3)
- Does not audit its own assumptions against external data
- Does not integrate with external data sources (placeholder)
- Does not have multi-period simulate() wrapper
- Does not model directional coupling between basins over time
- Does not model geographic proximity in cohort exposure
- Does not model generational lag in potential_waste
- Does not model trust hysteresis
- Does not model temporal asymmetry between cohorts

## Test-first discipline

Given that Claude fabricated two sets of tool outputs earlier in the
session, the discipline is:

- No claim about framework behavior without a test that produces it
- Every test output shown comes from actual stdout
- If a test doesn’t exist for a claim, the claim is hypothesis
- Users should re-run all tests to verify