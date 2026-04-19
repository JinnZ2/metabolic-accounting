# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project constraints (non-negotiable)

- **CC0 licensed. Python stdlib only.** Do not introduce third-party dependencies (no numpy, pandas, pydantic, pytest, etc.). Math uses `math` from stdlib; data containers are `@dataclass`.
- **Falsifiable, machine-readable, test-first.** Every claim about framework behavior must be backed by a test that actually produces the output. See `STATUS.md` for the discipline rationale — Claude has fabricated tool output in this repo before, so do not report numerical results you have not just generated via `python tests/test_*.py`.
- **No currency in the physics.** Reserve quantities are `xdu` (exergy-destruction-equivalent units); see `thermodynamics/exergy.py`. Currency conversion is a downstream policy layer, not baked in.
- **`math.inf` is a valid return value**, not an error. Irreversibility (past-cliff metrics, extinct apex species, collapsed aquifers) propagates as `inf` through `required_regeneration_cost → GlucoseFlow.regeneration_required → metabolic_profit → Verdict`. Do not silently clamp; the whole point is honest reporting of unrecoverable states.

## Running tests

There is no test runner, no `pytest`, no `pyproject.toml`, no `requirements.txt`. Every test file is a standalone script that inserts the repo root into `sys.path` and calls its test functions from `__main__`.

```bash
# Run one test (from repo root):
python tests/test_integration.py
# or equivalently:
python -m tests.test_integration

# Run all tests:
for t in tests/test_*.py; do python "$t" && echo "PASS" || echo "FAIL"; done
```

Assertions use plain `assert`; failures abort the script and print the assertion line. There is no `-k`/`-x`/fixture machinery — to run a single case, edit the `if __name__ == "__main__":` block at the bottom of the test file.

The Bug 1 and Bug 4 fixes described in `STATUS.md` are covered by `tests/test_tier_vector.py`. See `docs/AUDIT_04.md` for the audit trail that landed those fixes and for the candidate plan on the still-open Bugs 2 (no social/labor regulatory frameworks) and 3 (no community-specific mitigation patterns).

## Architecture — five-layer stack

Data flows upward; each layer consumes the one(s) below:

```
VERDICT         verdict/            GREEN/AMBER/RED/BLACK + warnings + profit lines
ACCOUNTING      accounting/         GlucoseFlow: revenue, regen required, cascade burn, debt
CASCADE         cascade/            basin state -> effective failure rate -> cascade cost
INFRASTRUCTURE  infrastructure/     systems with basin dependencies + sensitivities
BASIN STATE     basin_states/       soil, air, water, biology, community (primary metrics)
```

Orthogonal to the main stack (read in parallel):

- `reserves/` — `Site` binds basins to **secondary** (per-metric buffer) and **tertiary** (site-shared landscape) reserves. `Site.step(stress)` partitions stress through primary → secondary → tertiary → environment and enforces first-law closure via `thermodynamics/exergy.py`. Feeding the `Site` + `SiteStepResult` into `compute_flow(...)` is what surfaces `reserve_drawdown_cost` and `environment_loss` on the PnL.
- `thermodynamics/exergy.py` — enforces Gouy-Stodola: exergy destruction ≥ 0. `check_closure` and `check_nonnegative_destruction` are called after every reserve partition.
- `distributional/` — maps verdict tiers onto population cohorts with per-basin-type sensitivities. `apply_tier_to_cohorts` supports a vector path (`cohort_basin_sensitivities`) so a firm GREEN on soil and BLACK on community hits cohorts differently. Also houses institutional fit accounting (`available_capacity`, `fit_multiplier`, `trauma_tax`, `waste_ratio`) and civilization-scale comparisons.
- `mitigation/`, `regulatory/`, `social_cascade/` — downstream reporting on top of the verdict.

### Core data flow worth internalizing

`tests/test_integration.py` is the canonical end-to-end wiring:

```
Site(basins).attach_defaults()
    → step_result = site.step(stress)
    → flow = compute_flow(revenue, cost, regen_paid, basins, systems,
                           site=site, step_result=step_result)
    → verdict = assess(basins, flow)
```

Without `site`/`step_result`, `compute_flow` still works (backward-compatible path) but `reserve_drawdown_cost` and `environment_loss` are zero — this is not a bug, it is the pre-reserve pipeline.

## Conventions that bite if you miss them

- **The regeneration registry is keyed by `(basin_type, metric_key)`, NOT by basin name.** A basin named `farm_north_soil` with `basin_type="soil"` looks up the same functions as `site_soil`. Renaming a basin must never change its cost lookup; if you add a new basin, set `basin_type` to one of the known values (`soil`, `air`, `water`, `biology`, `community`) or pass a custom registry. `KNOWN_METRICS` + `strict=True` is how the framework refuses to silently under-report cost — see `accounting/regeneration.py` and `tests/test_registry_safety.py`.
- **`high_is_bad` is declarative per-basin** (`BasinState.high_is_bad: set`). The legacy global `HIGH_IS_BAD` in `cascade/detector.py` is a fallback only; prefer the per-basin field for new metrics.
- **Two profit lines, intentionally.** `metabolic_profit()` excludes `environment_loss` (treated as extraordinary, per GAAP ASC 360-10-35 / GASB 42 / SEEA). `metabolic_profit_with_loss()` includes it. `is_extraordinary_loss_material()` applies a 5%-of-revenue materiality heuristic. Do not collapse these into one number.
- **BLACK = irreversibility, not just "very bad."** Reserved for primary irreversibility OR any tertiary pool past its cliff. Do not lower BLACK to mean RED-plus.
- **Tier assignment is a vector.** `TierAssignment.by_basin_type` per basin type; `overall_tier()` is the worst-case aggregate. Code that calls `overall_tier()` and discards the vector is the pattern that caused Bug 4 in `STATUS.md` — prefer basin-type-aware consumers.
- **Basin naming convention** (`distributional/tiers.py::_basin_type_from_name`): names follow `{prefix}_{type}` (e.g. `site_soil`, `plant_water`) so type can be derived by `rsplit("_", 1)`. Keep this when adding new basins.

## Documentation layout

- `README.md` — thesis and layer diagram (public-facing).
- `STATUS.md` — current session state: tests passing, bugs fixed, hidden variables still open, what the framework does NOT do. **Update this** when you change verified behavior.
- `docs/EQUATIONS.md` — every equation in the scaffold, tagged `[CORE] / [PLACEHOLDER] / [HEURISTIC] / [FRAGILE]`. Read before changing any formula; `[PLACEHOLDER]` and `[FRAGILE]` are explicitly waiting to be replaced.
- `docs/AUDIT_01..03.md` — prior audit reports. `STATUS.md` references a future `docs/AUDIT_04.md` for open Bugs 2 and 3 (regulatory crosswalk has no social/labor frameworks; mitigation has no community-specific leverage patterns).
- `docs/LITERATURE.md` — citations backing the thermodynamic framing.

## Things the framework intentionally does NOT do

Do not "fix" these by adding them unprompted — they are scoped out. In particular: no pricing, no external-data adapters (USDA/EPA/USGS are a future layer), no multi-period `simulate()` wrapper, no directional inter-basin coupling over time, no geographic-proximity model for cohort exposure, no trust hysteresis. See `STATUS.md § "What the framework does NOT do"` for the authoritative list.
