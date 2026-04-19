# metabolic-accounting

**CC0. Stdlib-only. Falsifiable. Machine-readable.**

A thermodynamic accounting framework that treats money as a flow signal (glucose)
rather than a stock, and treats the basins a firm depends on (soil, air, water,
biology, community, infrastructure) as first-class state variables on the
balance sheet.

## Core thesis

Current accounting hides cascade coupling. A cracked foundation is booked as a
repair; it is actually a symptom of soil substrate degradation that will also
fail the plumbing, the electrical, and the thermal envelope on staggered
timelines. Each of those failures is an unplanned glucose burn.

A firm that extracts without regenerating is an organism consuming its own
basin. Short-term the glucose signal looks strong. Mid-term the forced drawdown
from cascade failures exceeds extraction. Long-term the basin collapses and the
firm with it.

Metabolic accounting makes basin regeneration a **non-optional forced drawdown**
against the profit signal itself.

## Framework layers

```
    VERDICT LAYER         sustainable yield, trajectory, time-to-red
          ^
    ACCOUNTING LAYER      glucose flow, forced drawdown, regeneration debt
          ^
    CASCADE LAYER         basin-state to infrastructure failure coupling
          ^
    INFRASTRUCTURE LAYER  foundations, plumbing, electrical, thermal, filters
          ^
    BASIN STATE LAYER     soil, air, water, biology, community
```

Orthogonal to the stack: `reserves/` holds secondary (per-metric) and tertiary
(site-shared) buffers; `thermodynamics/` enforces first-law closure on every
reserve partition; `distributional/` maps verdicts onto population cohorts
with per-basin-type sensitivities.

## Run it in 60 seconds

No installation. No dependencies. Python 3 stdlib only.

```bash
# run the end-to-end integration test:
python tests/test_integration.py

# run the whole suite (18 test files):
for t in tests/test_*.py; do python "$t" && echo "PASS" || echo "FAIL"; done
```

Sample output from `tests/test_integration.py` (first case — a firm stressing
its site-level basins for one period):

```
--- TEST 1: reserve drawdown on PnL ---
  reserve_drawdown_cost: 15.3093
  environment_loss:      0.0307
  reported_profit:       399.33
  metabolic_profit:      370.73
  visible hidden cost:   28.60
PASS
```

The firm reports 399.33 of profit. Metabolic profit — after the mandatory
forced drawdown for reserve consumption — is 370.73. The 28.60 delta is the
hidden cost the firm would otherwise capitalize as "profit" while consuming
its basin. `environment_loss` (0.03 xdu) is the irreversible slice, reported
as an extraordinary item rather than as operating cost.

## Modules

Layer stack (bottom up):

- `basin_states/` — soil, air, water, biology, community. State, capacity,
  trajectory, cliff thresholds. See `basin_states/base.py` for the shape and
  the type-specific files for literature-anchored defaults.
- `infrastructure/` — systems whose function depends on basin state
  (foundations, buried utilities, HVAC, thermal envelope, cooling, biological
  services).
- `cascade/` — coupling matrix, effective failure rate, pluggable aggregation
  (`multiplicative` / `dominant` / `additive` / `saturating`) and ramp
  functions (`linear` / `power` / `exponential` / `logistic`).
- `accounting/` — glucose flow, per-metric regeneration cost registry,
  `metabolic_profit` vs `metabolic_profit_with_loss`, extraordinary-item
  materiality.
- `verdict/` — GREEN / AMBER / RED / BLACK signal, basin trajectory,
  time-to-red, warnings.

Orthogonal / downstream:

- `reserves/` — `Site` object binds basins to secondary (per-metric) and
  tertiary (site-shared, landscape-scale) reserves. `Site.step(stress)`
  partitions stress through primary → secondary → tertiary → environment.
- `thermodynamics/` — exergy units (xdu, not currency), Gouy-Stodola
  invariant (destruction ≥ 0) enforced on every partition.
- `distributional/` — population cohorts, per-cohort structural load,
  institutional fit (`available_capacity`, `fit_multiplier`, `trauma_tax`),
  strategy comparison (compliance vs capacity-fit), civilization-scale audit.
- `regulatory/` — crosswalk across five jurisdictions (US CERCLA, EU ELD,
  UK Part 2A, Germany BBodSchG, Japan SCCA).
- `mitigation/` — actions ranked by leverage and urgency.
- `social_cascade/` — compound-decay signatures across social substrates.
- `tests/` — 18 falsifiable test suites. Every numerical claim in the
  docs is reproducible from here.
- `docs/` — equations, audit reports, literature anchors.

## Status

Eighteen test suites pass end-to-end. The framework exercises reserve
partitioning with first-law closure, two profit lines (with and without
extraordinary items), cumulative environment loss across periods, vector
tier assignment per basin type, regulatory crosswalk across five
jurisdictions, mitigation-action ranking, distributional nonlinearity,
institutional-fit accounting, and civilization-scale comparisons.

What the framework does NOT do yet: price anything, integrate with external
data sources (USDA/EPA/USGS are a future adapter layer), add social/labor
regulatory frameworks (Bug 2, scoped in `docs/AUDIT_04.md` Part B), add
community-specific mitigation patterns (Bug 3, scoped in `docs/AUDIT_04.md`
Part C), model directional inter-basin coupling over time, model geographic
proximity in cohort exposure, or model trust hysteresis. See `STATUS.md` for
the full, authoritative list.

## Falsifiable claims

1. Basin states are coupled, not independent.
2. Infrastructure failure rates are a function of basin trajectory, not age alone.
3. A firm with negative basin trajectory has non-zero regeneration debt regardless
   of reported profit.
4. Cascade failures arrive in predictable sequence when coupling is modeled.
5. Sustainable yield is bounded above by regeneration rate, not by extraction
   capacity.

Each claim is exercised by at least one test in `tests/`. The discipline is
explicit: no claim about framework behavior without a test that produces the
output.

## Further reading

- [`STATUS.md`](./STATUS.md) — current session state, passing suites, open
  bugs, hidden variables yet to model.
- [`CLAUDE.md`](./CLAUDE.md) — navigation map and conventions for AI
  assistants working on the codebase.
- [`docs/EQUATIONS.md`](./docs/EQUATIONS.md) — every equation in the scaffold
  tagged `[CORE] / [PLACEHOLDER] / [HEURISTIC] / [FRAGILE]`.
- [`docs/AUDIT_01.md`](./docs/AUDIT_01.md)–[`AUDIT_04.md`](./docs/AUDIT_04.md)
  — audit reports. `AUDIT_04` covers the tier-vector fixes and scopes the
  remaining open bugs.
- [`docs/LITERATURE.md`](./docs/LITERATURE.md) — citations backing the
  thermodynamic and social-substrate framing (Sciubba, Joergensen, Case &
  Deaton, Kim 2024, and others).
