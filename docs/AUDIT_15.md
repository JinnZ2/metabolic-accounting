# AUDIT 15

Fifteenth audit pass. Scope: intake a new user-supplied module —
`term_audit/study_scope_audit.py` (STUDY_SCOPE_AUDIT) — a
methodology framework for AI systems to treat scientific studies
as scope-bounded measurements rather than timeless laws.

This is new material, not part of the AUDIT_14 E.1-E.4 plan. It
ships between AUDIT_14 Part B and Part C to keep the chunking
clean.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet
designed.


## Part A — What landed

### A.1 `term_audit/study_scope_audit.py`

~540 lines. Six layered audit dataclasses composed into a top-
level `StudyScopeAudit`:

- `InstrumentAudit` — what the instrument could physically measure
  (range, resolution, noise floor, sampling rate, calibration
  traceability). `.blind_spots()` returns the structured list of
  phenomena the instrument structurally cannot see.
- `ProtocolAudit` — what the protocol defined as valid data
  (sample prep, environmental controls, excluded conditions,
  replication, blinding, pre-registration). `.protocol_filters()`
  returns the systematically excluded phenomena.
- `DomainCouplingAudit` — four `Coupling` scores (instrument,
  protocol, substrate, regime) describing how tightly the claim
  is bound to its measurement setup. `.coupling_summary()`
  surfaces all four.
- `RegimeAudit` — baseline stability check. `.regime_risk()` maps
  `STATIONARY` / `DRIFTING` / `NON_STATIONARY` / `UNKNOWN` to
  severity strings.
- `CausalModelAudit` — interpretive-frame inspection.
  `.frame_fragility()` responds monotonically to the two fields
  it reads (unmeasured-confounder count + unknown-unknowns
  acknowledgement).
- `ScopeBoundary` — where the claim holds vs breaks.
  `.scope_status_for(deployment_context)` returns one of
  `IN_SCOPE` / `EDGE_OF_SCOPE` / `OUT_OF_SCOPE` /
  `SCOPE_UNDECLARED`.

Plus three enums (`Coupling`, `Regime`, `ScopeStatus`) and three
prose surfaces (`PREMISE`, `AI_REASONING_RULE`, `META_INSIGHT`)
that encode the epistemology the module implements.

### A.2 Historical anchors

`HISTORICAL_CASES` dict with five documented calibration examples
showing scope-boundary expansion events in the history of science:

- **geocentrism** — naked-eye scope, expanded by the telescope
- **miasma theory** — smell/vision scope, expanded by microscopy
- **caloric theory** — macroscale calorimetry, expanded by kinetic theory
- **steady-state cosmology** — optical telescopes, expanded by radio astronomy
- **low-fat diet consensus** — dietary recall surveys in 20th-century food supply, expanded by metabolic individuality + ultra-processed food category

Each anchor carries a `lesson` documenting the structural mistake
the anchor case teaches — the earlier model was NOT wrong, it was
scope-complete for the instruments of its era.

### A.3 CLI worked example

The module's `_demo()` applies every layer to a toy polymer-X claim
with a Lab-Study-Journal 2018 citation. A clean-lab-coupon 1000-hour
accelerated-weathering study is deployed into a `dirty_urban +
50_year_outdoor_service` context. The audit correctly returns
`scope_status = out_of_scope` and the verdict:

> "claim does NOT apply; using it as reasoning material is a category
>  error (e.g., applying clean-lab data to dirty-field conditions)"

Intake-time fix: the initial naive substring matcher in
`ScopeBoundary._context_matches` was too strict (demo deployment
context used `dirty_urban` with underscore; condition string used
`dirty urban` with space). Added minimal normalization
(`_` and `-` → space in deployment-context keys) so the matcher
is usable without requiring every caller to agree on a separator
convention. Documented in-line that anything more sophisticated is
the caller's responsibility.


## Part B — Tests

`tests/test_study_scope_audit.py` (9 cases):

1. module imports; three enums with ≥3 members each; five historical
   anchors; three prose surfaces present
2. `InstrumentAudit.blind_spots()` returns ≥6 structured lines
   including noise floor + range
3. `ProtocolAudit.protocol_filters()` includes explicit
   `excluded_conditions` entries — tripwire against those being
   silently lost
4. `DomainCouplingAudit.coupling_summary()` returns all four
   dimensions with valid `Coupling` enum values
5. `RegimeAudit.regime_risk()` maps each Regime state to a
   distinct severity string (catch collapse-to-identical on regression)
6. `CausalModelAudit.frame_fragility()` responds monotonically to
   unmeasured-confounder count + unknown-unknowns flag — LOW /
   MEDIUM / HIGH all reachable
7. **LOAD-BEARING**: `ScopeBoundary.scope_status_for` returns
   `OUT_OF_SCOPE` when deployment matches out-of-scope conditions,
   dominating in-scope and edge matches. Reversing this would
   silently bless deployments that violate declared exclusions.
8. `StudyScopeAudit.audit_report` distinguishes verdicts across
   undeclared / out-of-scope / in-scope deployment contexts
9. every historical anchor carries a populated `lesson` field


## Part C — Relationship to existing framework

### C.1 Overlap and differentiation

| Module | Scope |
| --- | --- |
| `term_audit/schema.py` + `audits/*.py` | audits a **term** against 7 signal-definition criteria |
| `term_audit/legislative_audit/` | audits a **rule** against declared purpose + consequence |
| `term_audit/provenance.py` | taxonomy for **numeric/structural claims** (5 kinds) |
| **`term_audit/study_scope_audit.py`** | audits a **study** against instrument/protocol/regime bounds |

These four axes are complementary. A single claim might pass a
term-signal audit (the claim uses a clean signal like `V_C`
substrate-value) while failing a study-scope audit (the study
generating the claim measured at instrument scope too narrow for
the deployment context).

### C.2 Not replacing peer review

The module docstring is explicit: this is NOT a framework for
invalidating peer review, the scientific method, or empirical
evidence. It restricts how those results TRAVEL outside the scope
where they were measured. A study is true within its scope,
silent outside, and becomes false only when applied outside its
scope as if it held there.

### C.3 Not applied as a gate anywhere in the framework

AUDIT_15 ships the methodology module as a standalone resource.
Nothing in the existing framework currently *calls* `StudyScopeAudit`
to gate a claim. That integration is a future design — the natural
candidates are:

- The `source_refs` field on `SignalScore` could be extended to
  carry a `StudyScopeAudit` per ref, surfacing whether the study
  is being cited within its scope.
- The `EMPIRICAL` provenance kind in `term_audit/provenance.py`
  could require a `StudyScopeAudit` attachment for high-confidence
  claims.

Neither is implemented in AUDIT_15. Naming as `[OPEN]` integration
targets.


## Part D — What's NOT done

### D.1 Domain-specific matchers not shipped   `[OPEN]`

`ScopeBoundary._context_matches` is a deliberate placeholder for
substring-level fuzzy matching. Domain-specific deployments
(clinical-trial populations, polymer weathering regimes,
climate-model horizons) need domain-specific matchers.

The framework's discipline for this pattern is to ship the
placeholder with a clear "override me" docstring (same shape as
`accounting/regeneration.py::regen_fn` uses custom registries per
basin type). Documented; subclass hook left open.

### D.2 Integration with `term_audit/provenance.py`   `[NAMED]`

As noted in § C.3, the natural next step is for `EMPIRICAL`
provenance records to optionally carry a `StudyScopeAudit`. This
would let the framework surface scope violations at the same
coverage-report surface that already tracks provenance kinds.
Not implemented; natural follow-up.


## Close-out

- `term_audit/study_scope_audit.py` shipped.
- 9-test tripwire locks the structural surface + historical
  anchors + the load-bearing OUT_OF_SCOPE dominance.
- One intake-time fix (context matcher normalization) so the CLI
  demo produces the documented `out_of_scope` verdict.
- Relationship to existing framework documented; no gating
  integration shipped in this audit.
- Regression: **46/46 PASS** (was 45/45).
- Two items named for future passes: domain-specific matchers,
  integration with Provenance.
