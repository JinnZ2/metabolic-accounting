# AUDIT_02.md — State of the framework after reserve-layer integration

Date: after second-law-accounting reserve layer and Site integration.

Purpose: honest assessment of what changed, what is now load-bearing,
what remains placeholder or fragile, and what new risks were introduced.


## 1. What changed since AUDIT_01

### Thermodynamics module [NEW]
  - `thermodynamics/exergy.py`: xdu (exergy-destruction-equivalent) as
    the internal unit. XduConverter as explicit currency bridge.
    ThermodynamicViolation exception. Three checks:
      check_nonnegative_destruction (Gouy-Stodola floor)
      check_regen_floor              (regen >= damage)
      check_closure                  (first-law mass balance)

### Reserve layer [NEW]
  - `reserves/pools.py`: SecondaryReserve (per-metric per-basin),
    TertiaryPool (site-shared), partition_stress() that routes one
    period's stress through primary / secondary / tertiary / environment.
  - `reserves/defaults.py`: SECONDARY_SPECS for all 17 (basin_type,
    metric_key) pairs; standard tertiary pools (landscape, watershed,
    airshed, organizational).
  - `reserves/site.py`: Site coordinator with step(stress), closure
    verification every metric every period, exhausted/past-cliff
    accessors.

### GlucoseFlow extended
  - new fields: reserve_drawdown_cost, environment_loss,
    exhausted_reserves, tertiary_past_cliff
  - metabolic_profit now subtracts reserve_drawdown_cost
  - has_irreversibility now counts tertiary_past_cliff

### Verdict layer extended
  - surfaces EXHAUSTED RESERVES warning
  - surfaces TERTIARY PAST CLIFF warning
  - BLACK signal on tertiary-past-cliff (was previously only on
    primary irreversibility)

### Literature anchoring [NEW]
  - `docs/LITERATURE.md`: every default parameter mapped to a
    peer-reviewed source with quotation.


## 2. What is now load-bearing

After reserve integration, these outputs are trustworthy first-order signals:

  - First-law closure holds at every metric every period
    (verified numerically to delta < 1.5e-14 on 17-metric simultaneous stress)
  - Gouy-Stodola floor refuses negative exergy destruction
  - reserves drain under sustained load and recover passively under idle
  - past-cliff tertiary amplifies environment loss ~12.5x vs healthy
  - BLACK verdict triggers on tertiary-past-cliff without needing
    primary-metric irreversibility
  - backward compatibility: compute_flow() without a site behaves
    identically to pre-integration


## 3. What remains placeholder or fragile

### In priority order:

#### a. Equation 12 — yield signal thresholds [STILL FRAGILE]
Thresholds for RED, AMBER, and the "less than half of reported" check
are hardcoded. Needs config and declared risk regime. Priority:
MEDIUM. Not blocking, but arbitrary.

#### b. Equation 13 — trajectory verdict weighting [STILL PLACEHOLDER]
Equal-weighted count of degrading vs regenerating metrics. Should
weight by cascade coupling and cliff proximity. Priority: LOW-MEDIUM.

#### c. Reserve regen rates in SECONDARY_SPECS [FIRST-PASS]
Per-metric rates were assigned from literature recovery-time bands
(Lal 2013 for soil: 12-15 yr slight, 30-35 yr moderate, 60-65 yr severe)
but the translation from "years to equilibrium" to "xdu per period"
is a normalized mapping, not calibrated to real restoration project data.
Ratios between metrics are defensible; absolute values are not.

#### d. Tertiary pool capacities (1000, 1500, 800, 500) [FIRST-PASS]
Round numbers chosen for size-ordering (watershed largest, organizational
smallest). Relative sizes defensible; absolutes need field calibration.

#### e. Sensitivity values in infrastructure systems [LEGACY]
Never rebalanced for the additive aggregation rule (carried forward from
multiplicative default). Flagged in AUDIT_01, still not addressed.
Low priority because the ranking is invariant across rules, but
magnitudes may be miscalibrated.

#### f. Equation 2 — linear time-to-cliff [HEURISTIC]
Still linear extrapolation. Needs trajectory history data. Low priority.

#### g. Equations 5 and 7 — Poisson failure, linear cascade horizon
Still closed-form expected value. Replace with Monte Carlo before
using the framework for multi-period forecasting.


## 4. New fragilities introduced by the reserve integration

### i. Reserve drawdown vs regeneration_required are additively combined
`metabolic_profit = revenue - opex - regen_required - cascade_burn - reserve_drawdown`

There is a conceptual question: is reserve drawdown already implicitly
inside regen_required, or is it a separate cost? Current code treats
them as separate (regen pays to FIX primary degradation; drawdown is
the cost of stress ABSORBED this period). This distinction matters and
needs explicit documentation.

**Action:** add a clarifying note to LITERATURE.md: regen_required
addresses the stock of accumulated primary damage; reserve_drawdown_cost
addresses the flow of this-period absorbed stress. Both are real
costs. Double-counting is possible if the same mechanism is modeled in
both places.

### ii. Integration of step_result is single-period
compute_flow accepts exactly one step_result. If a user runs step()
multiple times between compute_flow calls, only the last result is
visible. Needs documentation or a multi-step accumulator.

**Action:** document usage pattern explicitly. Add a cumulative
SiteStepResult helper in a future change if needed.

### iii. Synthetic partition for no-reserve case (site.step)
When a stress target has a basin but no secondary reserve, the code
creates a "synthetic" partition that dumps everything to primary. This
preserves closure mathematically but hides the configuration gap.

**Action:** already surfaces a warning, but in strict mode this should
probably raise.

### iv. Environment loss is not yet charged back anywhere
environment_loss is reported on GlucoseFlow and surfaced as a warning,
but not subtracted from metabolic profit. The reasoning: environment
loss is irreversible and unchargeable — no amount of current-period
spending recovers it. But NOT charging it also means it doesn't
influence the profit signal, which may understate how bad the period
was.

**Policy question:** should environment_loss be added to
reserve_drawdown_cost for PnL purposes? Or should it only contribute
to the BLACK-when-cumulative-exceeds-threshold logic (not yet
implemented)?

### v. No cross-period memory for environment loss
Each period's environment_loss stands alone. Over 100 periods, total
irreversible loss could be substantial but never triggers a
cumulative signal.

**Action:** add cumulative_environment_loss to Site as a
state-over-time counter. Consider a BLACK threshold on cumulative loss.

### vi. Tertiary pools do not leak to each other
Landscape and watershed are modeled as independent pools. In reality
watershed degradation cascades into landscape (riparian collapse,
loss of soil moisture), and landscape degradation cascades into
watershed (loss of infiltration, increased runoff).

**Action:** add optional tertiary-to-tertiary coupling as the
"connective tissue" work promised in AUDIT_01. Defer until equations
12/13 are addressed.

### vii. Reserve capacities are basin-type constants
Every soil basin at every site starts with the same 100 xdu bearing-
capacity reserve regardless of actual site conditions. A heavily
damaged site starting with full reserves is dishonest.

**Action:** factory functions should accept an optional `initial_fraction`
argument, and sites that already have degraded basins should have
initial reserves scaled accordingly. Priority: MEDIUM.


## 5. What the framework now does NOT yet do

  - Multi-period simulation engine. step() exists but there is no
    `simulate(n_periods, stress_schedule)` wrapper.
  - Cross-period accumulation of environment loss and regeneration debt.
  - Converter modules for mapping real accounting (SAP, Oracle, GL codes)
    into stress inputs.
  - Real data adapters (USDA soil survey, EPA air quality, USGS water,
    GBIF biodiversity). Framework runs on abstract xdu.
  - Basin-to-basin coupling via tertiary pools (soil degradation
    driving water degradation through shared watershed reserve).
  - Multi-site composition. Currently one Site at a time.
  - Policy/intervention simulation ("what if we spent X on regen?").


## 6. Falsifiability status

Claims the framework now generates that are internally verified:

  - First-law closure holds across 17 primary metrics and 4 tertiary
    pools under simultaneous stress, with numerical delta < 1e-13.
  - Gouy-Stodola floor: any computation producing negative exergy
    destruction is refused.
  - Past-cliff tertiary amplifies environment loss 12.5x vs healthy,
    matching the Nature Water 2025 asymmetry-of-recovery finding.
  - Passive regeneration restores reserves toward capacity at
    rates calibrated to Lal 2013 recovery-time bands.
  - Backward compatibility: callers without site coupling see
    identical behavior to pre-reserve framework.

Claims that hold in the model but have NOT been tested against field data:

  - Specific cost ratios between soil C, aquifer, and pollinator
    regeneration (literature-anchored but not site-calibrated)
  - Tertiary pool capacities and cliffs (relative ratios defensible,
    absolutes not calibrated)
  - Linear scaling of entropy tax with cliff distance
    (first-order encoding of a finding that may be more complex)


## 7. Recommended next moves, in order

  1. Resolve fragility (i): clarify whether regen_required and
     reserve_drawdown_cost conceptually overlap. Document in
     LITERATURE.md or integrate into a unified cost-accounting
     clarification doc.
  2. Fragility (v): cumulative environment loss tracking.
  3. Fragility (vii): initial_fraction scaling for reserves on
     already-degraded basins.
  4. Equation 12: yield thresholds as config with declared risk regime.
  5. Equation 13: weight trajectory by coupling and cliff proximity.
  6. Fragility (vi): tertiary-to-tertiary coupling (connective tissue).
  7. Multi-period simulate() wrapper.
  8. Only then: Monte Carlo cascade, real data adapters, converter modules.


## 8. Verdict on overall framework state

The framework is now thermodynamically honest at first-order. Every
stress imposed closes against a balanced distribution of damage,
reserve drawdown, and environment loss. Regeneration cost is forced
onto the PnL along with reserve drawdown. Three distinct failure
modes are now visible in the verdict:

  RED    — running unsustainably (negative metabolic profit,
            imminent cliff, unsustainable debt)
  BLACK  — landscape-scale damage (tertiary past cliff, or primary
            irreversibility)
  AMBER  — warning zone
  GREEN  — sustainable

The framework is ready for controlled use by someone who understands
the literature-anchored defaults and their limits. It is NOT ready
for unsupervised use on real corporate balance sheets — that requires
the converter modules, data adapters, and calibration work listed in
section 5.

Closure check numerical accuracy (< 1e-13 on 17-metric stress)
indicates the first-law plumbing is solid. The BLACK-on-tertiary-cliff
mechanism correctly separates "firm is losing money" from "firm is
destroying something unrecoverable." That distinction is the single
most important output of the whole framework, and it is now visible.
