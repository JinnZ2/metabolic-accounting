# AUDIT 19

Nineteenth audit pass. Scope: three integration follow-ups named
in AUDIT_16 § D and AUDIT_17 § D.1.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet
designed; `[DEMONSTRATED]` — pattern shipped on a small set,
remainder left `[OPEN]` for per-item research.


## Part A — `StudyScopeAudit` × `informational_cost_audit`   `[CLOSED]`

AUDIT_16 § D.1 named a wiring: a `StudyScopeAudit` that comes
back `OUT_OF_SCOPE` should emit a qualitative "commitment cost"
tag drawn from the `CostLedger` vocabulary.

Implementation:

- `StudyScopeAudit.audit_report()` now includes a
  `cost_growth_if_applied_out_of_scope` field.
- `StudyScopeAudit._cost_growth_for_status(status)` maps each
  `ScopeStatus` to a `CostGrowth` tag:

| Scope status | Cost-growth tag |
| --- | --- |
| `IN_SCOPE` | `LINEAR` — each observation integrates cleanly |
| `EDGE_OF_SCOPE` | `LINEAR` — cautious; requires independent verification |
| `OUT_OF_SCOPE` | **`EXPONENTIAL`** — epicycle accumulation |
| `SCOPE_UNDECLARED` | `"unknown"` — declare context first |

The integration is lazy-imported so `study_scope_audit` remains
usable without `informational_cost_audit`. The CostGrowth tag is
a string constant, not an enum, to avoid tight coupling of the
two modules.

### Tripwires (tests 1-2 in `test_audit_19_integrations.py`)

- `audit_report` includes the new field
- **load-bearing**: mapping from each `ScopeStatus` to its
  `CostGrowth` tag is locked; `OUT_OF_SCOPE → EXPONENTIAL` is
  the thesis binding


## Part B — `Provenance.deferred_cost` on PLACEHOLDER   `[CLOSED]`

AUDIT_16 § D.2 named the other side of the pair: a PLACEHOLDER
provenance could optionally carry a cost-growth tag naming the
trajectory of its deferred documentation debt.

Implementation:

- `Provenance.deferred_cost: Optional[str] = None` field.
  String-typed (not enum) for the same reason as Part A.
- `placeholder()` constructor accepts the `deferred_cost` kwarg.
- `Provenance.soft_gap()` extended: a PLACEHOLDER with
  `deferred_cost == "exponential"` now fires a soft-gap signal
  naming the compounding debt.

Honest defaults:
- `LINEAR` (or `None`): steady documentation debt, pays off on
  retirement. No soft gap fires.
- `EXPONENTIAL`: debt compounding faster than linear. Soft gap
  fires. Retirement should be prioritized.

### Tripwires (tests 3-5)

- `placeholder()` accepts and stores `deferred_cost`
- **load-bearing**: EXPONENTIAL deferred_cost fires soft_gap
- LINEAR / None does not fire that specific gap


## Part C — Two Tier 1 scope-audit retrofits   `[DEMONSTRATED]`

AUDIT_17 § D.1 named: retrofit real `StudyScopeAudit` objects
onto the 74 Tier 1 EMPIRICAL records. AUDIT_19 Part C scopes
this down to a **demonstration of the pattern** on two
citations where the cited methodology is public enough to
ground a real scope audit honestly.

### C.1 Retrofits shipped

- `_BOSKIN_CPI_SCOPE_AUDIT` attached to the `calibration_exists`
  score. Grounded in the Boskin Commission 1996 Final Report and
  the BLS CPI Handbook of Methods.
- `_BOE_2014_MONEY_CREATION_SCOPE_AUDIT` attached to the
  `conservation_or_law` score. Grounded in McLeay/Radia/Thomas
  2014 *Money Creation in the Modern Economy* (BoE Quarterly
  Bulletin 2014 Q1).

Each scope audit populates all six layers — Instrument, Protocol,
DomainCoupling, Regime, CausalModel, ScopeBoundary — with facts
drawn from the published methodology. Nothing is fabricated;
each field is either directly extractable from the cited
document (basket weights, reporting perimeter, drift indicators)
or explicitly marked as unmeasured / undeclared.

### C.2 Why only two

The remaining 72 Tier 1 EMPIRICAL records would require
per-citation methodology-extraction work that cannot be
honestly performed without reading each cited paper's full
instrumentation and protocol. Fabricating scope audits without
that grounding would be exactly the performative-citation
failure mode `study_scope_audit` and `informational_cost_audit`
are designed to warn against.

The two retrofits stand as the pattern. Extending to additional
records is future work, honest to do one citation at a time
with real reading.

### C.3 Coverage picture

Post-retrofit on `MONEY_AUDIT`:

- 7/7 `is_complete` (AUDIT_07 preserved)
- 2 `scope_audit_count` (the two retrofits)
- 2 `soft_gap_count` (the two remaining EMPIRICAL records with
  `scope_caveat` but no `scope_audit`: `unit_invariant` / BLS
  Regional CPI + Balassa-Samuelson, and `observer_invariant` /
  FASB ASC 820 Level-3)

The honest shape. The soft-gap surface correctly reports what
was done and what wasn't.

### Tripwires (tests 6-8)

- two named retrofits attached by identity
- **load-bearing**: coverage shape matches expectations (2
  scope_audits, 2 remaining soft gaps, 7/7 complete)
- Boskin scope audit routes a cross-regime-comparison
  deployment to `OUT_OF_SCOPE` or `SCOPE_UNDECLARED` (both
  honest)


## Part D — What's NOT done

### D.1 72 remaining Tier 1 EMPIRICAL records   `[OPEN]`

Per § C.2 above. Each requires real methodology-extraction.
Tracked as a per-citation effort, not a one-shot retrofit.

### D.2 Soft-gap-driven repair workflow script   `[NAMED]`

AUDIT_17 § D.2 named this — a helper that walks every
Provenance in the tree, aggregates soft gaps, and emits repair
stubs. Not shipped in AUDIT_19 to keep the scope tight. The
existing `coverage_report()` surface already carries
`soft_gap_details` which makes such a script easy; it's just
not written yet.


## Close-out

- AUDIT_16 § D.1 closed (scope-status → cost-growth tag).
- AUDIT_16 § D.2 closed (PLACEHOLDER deferred_cost + soft_gap).
- AUDIT_17 § D.1 demonstrated on 2 records; remaining 72
  honestly left `[OPEN]`.
- No regression on AUDIT_07's 74/74 Tier 1 coverage.
- 8 new tripwires; three load-bearing (scope→cost mapping,
  exponential placeholder gap, honest retrofit coverage shape).
- Regression: **50/50 PASS** (was 49/49).
