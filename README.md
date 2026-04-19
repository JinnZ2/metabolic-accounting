# metabolic-accounting

**CC0. Stdlib-only. Falsifiable. Machine-readable.**

A thermodynamic accounting framework that treats money as a flow signal (glucose)
rather than a stock, and treats the basins a firm depends on (soil, air, water,
biology, infrastructure) as first-class state variables on the balance sheet.

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
    BASIN STATE LAYER     soil, air, water, biology
```

## Modules

- `basin_states/`   soil, air, water, biology - state, capacity, trajectory
- `infrastructure/` systems whose function depends on basin states
- `cascade/`        coupling matrix, failure cascade, time lag, cost multiplier
- `accounting/`     glucose flow, extraction rate, regeneration rate, drawdown
- `verdict/`        sustainable yield signal, basin trajectory, time-to-red
- `tests/`          falsifiable test cases for every claim
- `examples/`       worked scenarios
- `docs/`           equations, assumptions, boundary conditions

## Status

Skeleton stage. Abstract first; real data adapters (USDA, EPA, USGS) later.

## Falsifiable claims (to be hardened in docs/CLAIMS.md)

1. Basin states are coupled, not independent.
2. Infrastructure failure rates are a function of basin trajectory, not age alone.
3. A firm with negative basin trajectory has non-zero regeneration debt regardless
   of reported profit.
4. Cascade failures arrive in predictable sequence when coupling is modeled.
5. Sustainable yield is bounded above by regeneration rate, not by extraction
   capacity.
