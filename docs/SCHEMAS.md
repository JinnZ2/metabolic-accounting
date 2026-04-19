# SCHEMAS.md

Data types that `metabolic-accounting` exposes for cross-framework
consumption. The purpose of this document is to make the structural
interface with companion frameworks (TAF, PhysicsGuard, Logic-Ferret —
see `docs/RELATED.md`) explicit **without requiring a Python import
between repos**.

Everything below is a shape-level contract describing what the field
means, its unit, and the invariants it satisfies. A companion framework
that wants to ingest `metabolic-accounting` output reads the relevant
section here and constructs a matching local type.

All types are plain `@dataclass`. Definitions live in the modules noted.

---

## ExergyFlow

**Defined in:** `thermodynamics/exergy.py`

**Purpose:** A single exergy transfer event in the ledger — the
atomic unit of thermodynamic accounting in this framework.

| Field       | Type  | Unit | Invariant                                               |
| ----------- | ----- | ---- | ------------------------------------------------------- |
| `source`    | str   | —    | Free-form identifier (e.g. `"air.particulate_load"`)    |
| `sink`      | str   | —    | Free-form identifier (e.g. `"landscape_reserve"`)       |
| `amount`    | float | xdu  | Positive → source loses, sink gains                     |
| `destroyed` | float | xdu  | **≥ 0 always** (Gouy-Stodola; negative is refused)      |
| `note`      | str   | —    | Human-readable context                                  |

**Cross-framework note:** `destroyed` is exactly the quantity PhysicsGuard
would verify against the second law. If `destroyed < 0` ever appears in
output, the framework is misconfigured — `check_nonnegative_destruction`
in `thermodynamics/exergy.py` refuses it locally.

**Unit (`xdu`):** exergy-destruction-equivalent. Not currency. Currency
conversion is a downstream policy choice handled by `XduConverter` in
the same module; `xdu_per_currency_unit` is a **declared parameter**,
not a physical constant.

---

## GlucoseFlow

**Defined in:** `accounting/glucose.py`

**Purpose:** One period's PnL in metabolic-accounting terms. The firm is
an organism; this is the organism's energy budget for the period.

| Field                          | Type            | Unit      | Notes                                                 |
| ------------------------------ | --------------- | --------- | ----------------------------------------------------- |
| `revenue`                      | float           | currency  | Input flow                                            |
| `direct_operating_cost`        | float           | currency  | Conventional operating cost                           |
| `regeneration_paid`            | float           | currency  | What the firm chose to spend on regeneration          |
| `regeneration_required`        | float           | currency  | What the basins actually demand; may be `math.inf`    |
| `cascade_burn`                 | float           | currency  | Expected unplanned infrastructure-failure cost        |
| `regeneration_debt`            | float           | currency  | Accumulated underpayment; may be `math.inf`           |
| `reserve_drawdown_cost`        | float           | xdu       | Secondary + tertiary stock consumed this period       |
| `environment_loss`             | float           | xdu       | Irreversible dissipation this period                  |
| `cumulative_environment_loss`  | float           | xdu       | Sum of `environment_loss` across all periods to date  |
| `exhausted_reserves`           | List[Tuple[str,str]] | —    | (basin_name, metric_key) pairs whose secondary pool is below cliff |
| `tertiary_past_cliff`          | List[str]       | —         | Tertiary pool names past cliff                        |
| `irreversible_metrics`         | List[str]       | —         | `"{basin}.{metric}"` strings crossed an irreversible threshold |
| `regen_breakdown`              | List[RegenCost] | —         | Per-metric regeneration cost detail                   |
| `registry_warnings`            | List[str]       | —         | Configuration warnings surfaced during cost lookup    |

**Methods** (derived, not stored):

- `reported_profit()` → revenue − direct_operating_cost − cascade_burn
- `metabolic_profit()` → also subtracts regeneration_required and
  reserve_drawdown_cost. Returns `-inf` when regeneration is infinite.
- `metabolic_profit_with_loss()` → additionally subtracts
  `environment_loss`. Returns `-inf` when either is infinite.
- `has_irreversibility()` → True iff any metric is past an irreversible
  threshold, any tertiary pool is past cliff, or
  `regeneration_required` is infinite.
- `is_extraordinary_loss_material(revenue_threshold=0.05,
  min_absolute=0.0)` → GAAP-style materiality check on
  `environment_loss`.

**Cross-framework note:** the two profit lines are deliberate. A
companion tool should never collapse them into one number;
`metabolic_profit` excludes extraordinary items per GAAP ASC 360-10-35
/ GASB 42 / SEEA treatment, while `metabolic_profit_with_loss`
includes them. PhysicsGuard ingesting these would model
`environment_loss > 0` as an irreversibility claim requiring second-law
consistency.

---

## BasinState

**Defined in:** `basin_states/base.py`

**Purpose:** The primary state variables of one basin the firm depends on.

| Field              | Type               | Unit          | Notes                                               |
| ------------------ | ------------------ | ------------- | --------------------------------------------------- |
| `name`             | str                | —             | Instance name (`site_soil`, `farm_north_water`, …)  |
| `basin_type`       | str                | —             | Normalized type (`soil`, `air`, `water`, `biology`, `community`) |
| `state`            | Dict[str, float]   | per-metric    | Current value of each metric                        |
| `capacity`         | Dict[str, float]   | per-metric    | Sustainable-yield upper bound                       |
| `trajectory`       | Dict[str, float]   | per-metric/period | Rate of change; negative = depleting            |
| `cliff_thresholds` | Dict[str, float]   | per-metric    | Value at which cascade failure triggers             |
| `high_is_bad`      | Set[str]           | —             | Metrics where ABOVE cliff = past cliff (contamination); default is BELOW |
| `last_updated`     | Optional[str]      | —             | Free-form timestamp                                 |
| `notes`            | str                | —             | Human-readable context                              |

**Methods** (derived):

- `fraction_remaining(key)` → state/capacity, reporting-only
- `time_to_cliff(key)` → linear extrapolation along trajectory to cliff
- `is_degrading()` → list of keys with negative trajectory

**Cross-framework note:** `basin_type` is the lookup key for regeneration
cost functions and for `distributional/tiers.py::DEFAULT_TERTIARY_MAPPING`.
A companion framework that maps claims to basin types should use the
five canonical values, not the basin `name`.

---

## Tier and TierAssignment

**Defined in:** `distributional/tiers.py`

**Purpose:** Per-basin-type severity signal. Vector by design — a firm
can be GREEN on soil and BLACK on community simultaneously.

`Tier` is an `Enum`: `GREEN (0) / AMBER (1) / RED (2) / BLACK (3)`.
Semantics:

- **GREEN**  all reserves healthy; no primary irreversibility.
- **AMBER**  primary reserves under pressure OR secondary draining OR
  a metric inside the near-cliff band.
- **RED**    secondary exhausted on at least one metric OR tertiary
  < 30% capacity.
- **BLACK**  primary irreversibility (state past cliff) OR any relevant
  tertiary pool past cliff. **Reserved for landscape-scale damage.**

`TierAssignment`:

| Field            | Type              | Invariant                                          |
| ---------------- | ----------------- | -------------------------------------------------- |
| `by_basin_type`  | Dict[str, Tier]   | One entry per basin type present on the site      |

**Methods:** `overall_tier()` (worst-basin aggregate — use only when a
single scalar is genuinely needed), `basins_at_or_worse_than(tier)`,
`basins_at(tier)`.

**Cross-framework note:** collapsing the vector to a scalar via
`overall_tier()` is the pattern that caused Bug 4 (see
`docs/AUDIT_04.md`). Companion frameworks should consume
`by_basin_type` directly.

---

## Verdict

**Defined in:** `verdict/assess.py`

**Purpose:** Machine-readable judgment for one period, combining basin
state, glucose flow, and trajectory.

| Field                         | Type             | Unit          | Notes                                              |
| ----------------------------- | ---------------- | ------------- | -------------------------------------------------- |
| `sustainable_yield_signal`    | str              | —             | One of `GREEN` / `AMBER` / `RED` / `BLACK`         |
| `basin_trajectory`            | str              | —             | One of `IMPROVING` / `STABLE` / `DEGRADING`        |
| `time_to_red`                 | Optional[float]  | periods       | Shortest `time_to_cliff` across all metrics        |
| `forced_drawdown`             | float            | currency      | `regeneration_required + cascade_burn`; may be inf |
| `regeneration_debt`           | float            | currency      | Accumulated underpayment; may be inf               |
| `metabolic_profit`            | float            | currency      | May be `-inf` on irreversibility                   |
| `reported_profit`             | float            | currency      | Conventional profit                                |
| `profit_gap`                  | float            | currency      | `reported - metabolic`; may be inf                 |
| `extraordinary_item_flagged`  | bool             | —             | Per GAAP-style materiality test                    |
| `extraordinary_item_amount`   | float            | xdu           | Equals `GlucoseFlow.environment_loss`              |
| `metabolic_profit_with_loss`  | float            | currency      | Profit after extraordinary item                    |
| `irreversible_metrics`        | List[str]        | —             | `"{basin}.{metric}"` strings                       |
| `warnings`                    | List[str]        | —             | Human-readable warnings, one per issue             |

**Cross-framework note:** `sustainable_yield_signal` is a stringly-typed
enum for portability. A companion tool reading it should match exactly
against the four values; `BLACK` is the only one that means
irreversibility, and treating it as "very RED" is wrong.

---

## Invariants (cross-framework contract)

These are the physical / structural invariants that hold at every step
of the pipeline. A companion verifier (e.g. PhysicsGuard) can assert
them against any output from this framework:

1. **Gouy-Stodola.** `ExergyFlow.destroyed ≥ 0` for every flow
   generated by `Site.step(...)`.
2. **First-law closure.** The sum of `primary` + `secondary_kept` +
   `tertiary_kept` + `environment` partitions equals the imposed
   stress, within a tolerance checked by
   `thermodynamics/exergy.py::check_closure`.
3. **Mass / stock non-negativity.** `SecondaryReserve.stock ≥ 0` and
   `TertiaryPool.stock ≥ 0` at all times.
4. **Irreversibility propagation.** If any
   `RegenCost.irreversible == True` or any `RegenCost.total_cost` is
   `math.inf`, then `GlucoseFlow.regeneration_required` is `math.inf`
   and `Verdict.sustainable_yield_signal == "BLACK"`.
5. **Cumulative monotonicity.** `cumulative_environment_loss` is
   non-decreasing across periods. It is never reset — irreversible
   damage does not "recover" just because a later period looks better.
6. **Tier vector preservation.** `TierAssignment.by_basin_type` is not
   reducible to `overall_tier()` without information loss; any
   consumer that collapses the vector is making a policy choice, not
   reading a fact.
7. **No currency in physics.** Reserve and exergy quantities are `xdu`.
   Currency conversion is declarative (`XduConverter`), not physical.

Companion frameworks asserting any of the above against output from
this repo should return a clean verdict. A failing assertion indicates
either a bug here or a configuration mismatch — not a policy
disagreement.
