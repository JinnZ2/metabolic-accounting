# AUDIT_03.md — State after extraordinary-item accounting and overflow-spread physics

Date: after implementing SEEA/GAAP-aligned extraordinary-item treatment,
cumulative environment loss tracking, and the overflow-spread physics fix.

Purpose: honest assessment of what changed, what is now load-bearing,
and what remains.


## 1. What changed since AUDIT_02

### Two profit lines [NEW]
  - `metabolic_profit()` — operating only; charges regen, cascade burn,
    reserve drawdown. Excludes env loss (treated as extraordinary).
  - `metabolic_profit_with_loss()` — full picture; adds env loss as an
    extraordinary item.
  - Distinction follows SEEA and GAAP practice where impairments and
    irreversible losses report separately from operating results.

### Materiality flagging [NEW]
  - `is_extraordinary_loss_material()` — 5% of revenue default threshold,
    configurable via `assess(extraordinary_revenue_threshold=...)`.
  - Verdict carries `extraordinary_item_flagged` and
    `extraordinary_item_amount` fields.
  - Warning line "EXTRAORDINARY ITEM: ..." with revenue-percentage
    context when material.

### Cumulative environment loss tracking [NEW]
  - Site now carries `cumulative_environment_loss`,
    `cumulative_tertiary_drawdown`, and `periods_elapsed` counters.
  - GlucoseFlow exposes `cumulative_environment_loss`.
  - Verdict surfaces cumulative as a separate warning line.

### Overflow-spread physics fix [PHYSICS]
  - When secondary reserve is exhausted, a default 30% of the overflow
    now propagates to tertiary pools instead of routing entirely to
    primary.
  - Rationale from literature: unbuffered damage does not stay local;
    collapsed buffers transmit stress outward (Scheffer 2009;
    Dakos 2019 on hysteresis asymmetry, 25-35% range).
  - Closure invariant still holds at numerical precision of 1.42e-14.
  - Exposed as `overflow_spread_fraction` parameter on partition_stress.


## 2. What is now load-bearing and tested

  - Closure holds under all new pathways including overflow spread.
  - Severe-damage scenarios produce materially non-zero env loss
    (test 3 now triggers at 15% of revenue on a fully collapsed site).
  - Cumulative env loss tracks correctly across periods.
  - Materiality threshold is configurable — the default is documented
    but not imposed.
  - Two-profit-line reporting survives backward compatibility:
    callers without a site still get operating metabolic_profit
    identical to pre-extraordinary behavior.


## 3. What remains placeholder or fragile

### Priority order:

#### a. Equation 12 — yield signal thresholds [STILL FRAGILE]
Still hardcoded. No risk-regime declaration. Priority MEDIUM. Not
blocking but arbitrary.

#### b. Equation 13 — trajectory verdict weighting [STILL PLACEHOLDER]
Equal-weighted metric count. Should weight by coupling and cliff
proximity. Priority LOW-MEDIUM.

#### c. overflow_spread_fraction default (0.30)
Literature-anchored to 25-35% range but first-order. No field
calibration. A site with different buffering structure could have a
different spread coefficient. Exposed as parameter so users can
override.

#### d. Reserve regen rates and capacities still from AUDIT_02
First-pass from Lal 2013 time-bands. Ratios defensible; absolutes
uncalibrated.

#### e. Tertiary pools still don't leak to each other
Landscape/watershed/airshed/organizational remain independent.
Watershed collapse should cascade into landscape; currently doesn't.
Deferred as "connective tissue" work.

#### f. Infrastructure sensitivities still legacy values
Never rebalanced for additive aggregation rule. Flagged since
AUDIT_01. Ranking is invariant across rules; magnitudes may be off.


## 4. New fragilities introduced this round

### i. Two profit lines may confuse users
`metabolic_profit` and `metabolic_profit_with_loss` differ by env loss.
Users who grab "profit" without reading may take the wrong one.

**Action:** documentation and maybe renaming. Consider
`metabolic_profit_operating` and `metabolic_profit_total` as clearer
names. Not urgent but worth thinking about.

### ii. Cumulative env loss has no forgetting
Under current implementation, cumulative loss grows monotonically over
all periods. Over decades of operation even small per-period losses
accumulate into a very large number that may not reflect current
operational character.

**Policy question:** Should cumulative loss decay with time (old damage
"matures" into landscape baseline)? Second-law says no — exergy
destruction is permanent. But for accounting utility, maybe a rolling
window (cumulative over last N periods) for trend signals, while the
all-time total stays for historical record.

**Recommendation:** keep true cumulative as-is (physics), add
`rolling_environment_loss` with configurable window (accounting
utility). Separate concerns.

### iii. overflow_spread_fraction is a global constant
Same 30% for every reserve. Realistically this coefficient varies:
- Soil reserves with strong mycorrhizal networks retain more locally
  (lower spread)
- Water reserves with regional hydrological connectivity spread more
  (higher spread)
- Apex-species reserves spread dramatically (connectivity-dependent)

**Action:** expose as a per-reserve parameter on SecondaryReserve, with
30% as class default.

### iv. Extraordinary-item threshold is by revenue only
Standard materiality uses multiple bases (revenue, net income, total
assets, equity). A firm with negative metabolic profit has an
undefined "percentage of profit." Current revenue-only threshold is
simple but may miss material losses in low-revenue scenarios.

**Action:** add `min_absolute` already supports this case; expand to
multi-basis materiality if needed for real-world adoption.

### v. compute_flow signature grows
Now takes 11+ parameters. Approaching refactor-needed territory.

**Action:** extract a `ComputeFlowConfig` dataclass for optional
parameters. Non-breaking change via kwarg forwarding.


## 5. Falsifiability status

Verified-in-model claims that now have falsifiability gates:

  - First-law closure holds across 17 primary metrics + 4 tertiary
    pools + overflow-spread pathway at delta 1.42e-14.
  - Gouy-Stodola floor refuses negative exergy destruction.
  - Severe-damage scenarios produce env loss ≥ 5% of revenue
    (tested at 15%, well above threshold).
  - Cumulative env loss accumulates correctly: sum of per-period
    values equals site.cumulative_environment_loss at numerical
    precision.
  - Materiality threshold is configurable and produces expected
    binary outcomes at boundary values.
  - Extraordinary item and operating metabolic profit differ by
    exactly the environment loss.


## 6. What the framework NOW does

Complete end-to-end: stress input → multi-tier reserve absorption →
first-law closure verification → second-law floor check → glucose flow
computation with two profit lines → verdict with extraordinary-item
flagging → cumulative cross-period tracking → site-state queries for
exhausted reserves and past-cliff tertiary pools → BLACK on
irreversibility OR tertiary-past-cliff → configurable materiality
thresholds for audit reporting.

All with literature-anchored defaults, CC0, stdlib-only.


## 7. What the framework still does NOT do

  - Multi-period simulate() wrapper (step() exists, simulate doesn't)
  - Tertiary-to-tertiary coupling
  - Real data adapters (USDA / EPA / USGS / GBIF)
  - Converter modules for corporate accounting systems (SAP / Oracle / GL)
  - Multi-site composition
  - Policy intervention simulation (what-if regen spend)


## 8. Recommended next moves

In order of unlock:

  1. Fragility (ii): rolling_environment_loss window (small, high value)
  2. Fragility (iii): per-reserve overflow_spread_fraction override
  3. Equation 12: yield thresholds as configurable risk regime
  4. Multi-period simulate(n_periods, stress_schedule, regen_schedule)
  5. Equation 13: weighted trajectory verdict
  6. Fragility (v): ComputeFlowConfig refactor
  7. Connective tissue: tertiary-to-tertiary coupling
  8. Real data adapters and converter modules


## 9. Verdict on overall framework state

The framework is now **accounting-complete** at first-order. It
produces:
- a reported-profit line matching conventional accounting
- an operating-metabolic line charging recurring ecological costs
- a full-metabolic line adding irreversible extraordinary losses
- a cumulative irreversible-loss counter
- a materiality-threshold-driven extraordinary-item flag
- a BLACK verdict signal for landscape-scale or primary irreversibility

This is sufficient to produce defensible, SEEA/GAAP-aligned, second-law-
respecting metabolic accounting for a controlled site. The defaults
are literature-anchored with explicit citations in LITERATURE.md. The
framework refuses impossible computations (ThermodynamicViolation) and
surfaces configuration errors (UnregisteredMetricError).

It is NOT yet ready for unsupervised production use. Real data adapters,
multi-site aggregation, and policy simulation are unbuilt. Those are
next-quarter concerns, not next-session concerns.

The single most important output of this entire framework is now
correctly surfaced: the distinction between "firm is running
unsustainably but recoverably" (RED) and "firm is destroying something
unrecoverable at landscape or primary scale" (BLACK, with
extraordinary-item flag when material). That distinction, which
conventional accounting erases, is now machine-readable and
literature-defensible.
