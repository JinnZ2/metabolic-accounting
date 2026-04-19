# AUDIT_01.md — State of the framework after equations 4 and 8

Date of audit: after replacement of aggregation rule (eq 4) and regeneration
cost (eq 8).

Purpose: honest assessment of what is now load-bearing, what is still
placeholder, and what new fragilities were introduced by the replacements.


## 1. What changed

### Equation 4 — aggregation rule
  - was: hardcoded multiplicative `rate *= (1 + s_i * d_i)` for each dependency
  - now: pluggable rule (multiplicative, dominant, additive, saturating),
    default additive, audit helper that scores all four on the same inputs
  - side-by-side comparison test published in tests/test_aggregation_comparison.py

### Equation 8 — regeneration cost
  - was: single scalar `rate_per_unit_degradation` applied to every metric
  - now: per-metric registry with 17 cost functions covering soil, air,
    water, biology; nonlinearities (linear, convex, exponential) keyed to
    the physics of each metric; infinity propagation for irreversible
    thresholds; detailed breakdown returned with every computation
  - verdict layer gained a BLACK signal for irreversibility


## 2. What is load-bearing now

After these two replacements, the framework can produce honest first-order
signals:

  - healthy basins with small maintenance gap  -> AMBER with tiny forced drawdown
  - moderate degradation                       -> AMBER with substantial
                                                  forced drawdown; profit gap
                                                  of order hundreds
  - crossing irreversible thresholds           -> BLACK, -inf metabolic
                                                  profit, named metrics

The failure-order ranking across infrastructure is robust to the aggregation
rule choice — hvac and cooling fail first in every scenario, foundation
late. This means the cascade detector is reporting something real about
the coupling, not an artifact of rule choice.


## 3. What is still placeholder, in order of fragility

### a. Equation 3 — degradation fraction ramp  [STILL PLACEHOLDER]
Linear ramp from capacity to cliff. Real failure curves are convex.
Priority to replace: HIGH. This equation feeds both cascade detection
and regeneration cost, so its underestimate of near-cliff risk propagates
everywhere.

### b. Equation 12 — yield signal thresholds  [STILL FRAGILE]
Thresholds are hardcoded. Needs config and declared risk regime
(conservative / moderate / aggressive).
Priority: MEDIUM. Thresholds work for smoke tests but are arbitrary.

### c. Equation 13 — trajectory verdict weighting  [STILL PLACEHOLDER]
Equal-weighted count of degrading vs regenerating metrics. Should be
weighted by cascade coupling and cliff proximity.
Priority: MEDIUM. Low cost, high interpretability gain.

### d. Equations 5 and 7 — Poisson and linear cascade cost  [HEURISTIC]
Closed-form expected value. Defensible for one-period snapshots; wrong
for multi-period forecasts. Needs Monte Carlo cascade.
Priority: LOW for near term, HIGH before anyone uses this for forecasting.

### e. Equation 2 — linear time-to-cliff  [HEURISTIC]
Linear extrapolation of current trajectory. Real trajectories accelerate.
Priority: LOW. Replacement requires trajectory history data we don't yet have.


## 4. New fragilities introduced by the replacements

### Eq 4 replacement

  i.  The choice of DEFAULT_RULE (currently additive) is itself a
      modeling decision that affects every output. This is a policy
      choice that needs explicit documentation. A user running
      `compute_flow` with no rule argument gets additive — we need a
      CLAIMS.md entry making this visible.
  ii. Sensitivity values in infrastructure systems.py were calibrated
      for multiplicative. They may be miscalibrated for additive — a
      sensitivity of 10 under multiplicative contributes a factor of
      11 at full degradation, under additive it contributes +10 to a
      multiplier of 1. The numerical meanings are different.
      ACTION ITEM: review each sensitivity value in the context of the
      new default rule, or declare the values as rule-specific.

### Eq 8 replacement

  iii. Base costs for each metric (30, 60, 100, 200, 400, 500, 800) are
       first-pass round numbers. They need documented rationale or a
       clear disclaimer that they are placeholders. The RATIOS between
       them carry the economic logic (aquifer 17x soil carbon, apex
       indicator 27x soil carbon) and those ratios are defensible;
       the absolute magnitudes are not calibrated to any monetary unit.
  iv.  Nonlinearity parameters (power=1.5, 1.8, 2.0; steepness=2.5, 3.0, 4.0)
       are also first-pass. They change the shape of near-cliff cost
       dramatically. Needs documentation.
  v.   Irreversibility conditions are hand-coded (vegetation->pollinator,
       aquifer+temp -> aquifer, apex<cliff -> apex). These are specific
       couplings chosen to illustrate the mechanism. The full set of
       real-world irreversibility thresholds is much larger and needs
       its own research pass.
  vi.  The DEFAULT_REGISTRY keys use the default basin names
       (site_soil, site_air, etc). If a user creates basins with other
       names, registry lookups miss silently and cost is under-reported.
       ACTION ITEM: either normalize by basin TYPE rather than name,
       or raise when a known metric has no registered function.


## 5. What the scaffold does NOT yet do

  - No coupling between basins. Soil degrading does not drive water
    degradation even though physically it should. This is the
    "connective tissue" stage — next major milestone.
  - No time integration. Everything is a one-period snapshot. A
    simulate() function that steps the state forward under trajectory
    and regeneration action does not yet exist.
  - No converter modules for real-world accounting systems. The
    README promised "low friction adoption"; this is not yet delivered.
  - No real data adapters. The whole framework runs on abstract
    normalized 0..1 values.


## 6. Recommended next moves, in order

  1. Fix new fragility (vi) — registry keys by basin type, not name.
     Low cost, prevents silent miss.
  2. Address new fragility (ii) — review infrastructure sensitivities
     under the new default rule.
  3. Replace Equation 3 (linear ramp -> convex).
  4. Expose Equation 12 thresholds as config.
  5. Weight Equation 13 trajectory verdict.
  6. Begin connective tissue — basin-to-basin coupling.
  7. Only then: Monte Carlo cascade, real data adapters, converter modules.


## 7. Falsifiability status

The framework now produces claims that are explicitly falsifiable:

  - "A firm with moderate-to-severe basin degradation has positive
    reported profit and negative metabolic profit." Tested: YES.
  - "Infrastructure failure ranking is robust to aggregation rule choice
    under moderate degradation." Tested: YES, hvac/cooling first under
    all four rules.
  - "Crossing vegetation cliff makes pollinator regeneration cost
    infinite." Tested: YES.
  - "Aquifer collapse with thermal stress triggers structural
    irreversibility." Tested: YES.

These are first-order claims. They hold inside the model. Whether they
hold in the world is a different question and requires field data.
