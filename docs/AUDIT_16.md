# AUDIT 16

Sixteenth audit pass. Scope: intake a new user-supplied module —
`term_audit/informational_cost_audit.py` — that pairs with the
AUDIT_15 study-scope audit.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet designed.


## Part A — The pair

`term_audit/study_scope_audit.py` (AUDIT_15) answers: **where does
a claim hold?** It scores instrument / protocol / regime / causal-
frame / scope boundaries.

`term_audit/informational_cost_audit.py` (AUDIT_16) answers: **what
is the cost of ignoring the scope bound?** It documents the
information-theoretic accumulation that false certainty forces when
anomalies appear outside the scope the study actually measured.

The two modules are designed to be read together. AUDIT_16's CLI
explicitly cross-references AUDIT_15 so that downstream readers
see the pairing (tripwired in test 7).


## Part B — What landed

### B.1 Knowledge structures

Nine documented dicts that encode the module's argument as
structured prose an AI can read:

- `GEOCENTRIC_COMFORT_STATE` — what people believed, why it was
  comfortable, and the informational cost of the commitment.
- `ANOMALIES_UNDER_GEOCENTRISM` — four canonical anomalies
  (retrograde motion, Venus phases, stellar parallax, Jupiter
  moons) each with (observation, geocentric_problem,
  geocentric_solution, cost).
- `INFORMATION_COST_ACCUMULATION` — the four-stage spiral:
  comfort → first anomaly → more anomalies → collapse.
- `HELIOCENTRIC_UNCERTAINTY_STATE` — the alternative path.
- `INFORMATION_COST_AUDIT` — head-to-head comparison of the two
  commitment strategies across initial cost, per-anomaly cost,
  total accumulated cost, regime-shift cost, and final verdict.
- `INFORMATION_THEORY_INSIGHT` — Shannon-entropy framing:
  false certainty feels low-entropy but is actually high-entropy.
- `AI_IMPLICATIONS` — direct application to AI reasoning behavior.
- `HISTORICAL_PATTERN` — what always happens (and what rarely does).
- `VERDICT` — load-bearing booleans (`comfort_is_expensive=True`,
  `uncertainty_is_cheap=True`) and the compressed one-liner.

### B.2 Small machinery

- `CostGrowth` symbolic tags: FLAT / LINEAR / EXPONENTIAL /
  CATASTROPHIC_AT_REGIME_SHIFT. Deliberately qualitative — the
  point is to warn against false-precision scalars.
- `CostLedger` frozen dataclass: strategy + initial cost + per-
  anomaly cost + regime-shift cost + short-horizon apparent cost
  + long-horizon actual cost.
- `GEOCENTRIC_LEDGER` and `HELIOCENTRIC_LEDGER` canonical
  strategies.
- `compare(ledger_a, ledger_b) -> Dict[str, str]` returns a
  per-dimension comparison dict. **Deliberately refuses to collapse
  to a scalar verdict** — doing so would reintroduce the same
  false-certainty compression the module is designed to warn
  against. Tripwired in test 6.


## Part C — Tests

`tests/test_informational_cost_audit.py` (7 cases):

1. all nine knowledge structures present and non-empty
2. four canonical anomalies with full field coverage
3. **load-bearing**: four-stage accumulation in documented order
   (comfort → first anomaly → more anomalies → collapse) — the
   narrative sequence IS the argument structure
4. **load-bearing**: VERDICT invariants stay
   (`comfort_is_expensive=True`, `uncertainty_is_cheap=True`,
   time-horizon caveat present, one_liner contains "false
   certainty") — flipping any of these inverts the module's
   thesis
5. canonical ledgers: geocentric = EXPONENTIAL per anomaly,
   CATASTROPHIC at regime shift; scope-bounded = LINEAR and FLAT
6. **load-bearing**: `compare()` returns per-dimension strings,
   not a scalar. A `total_score` key sneaking in would be caught
7. **pair invariant**: CLI output references `study_scope_audit`
   so the reader sees both halves of the argument

Full regression: **48/48 PASS**.


## Part D — What's NOT done

### D.1 Not wired into the rest of the framework   `[NAMED]`

`informational_cost_audit` is a standalone epistemology module.
Nothing in the existing framework currently calls it. Natural
integration candidates:

- A `StudyScopeAudit` that comes back `OUT_OF_SCOPE` could emit a
  qualitative "commitment cost" tag derived from this module's
  `CostLedger` vocabulary.
- `TermAudit`s that fail multiple signal criteria could reference
  the `INFORMATION_THEORY_INSIGHT` dict as the structural reason
  for the failure (false-certainty compression).

Neither is implemented in AUDIT_16. Listed for a future pass.

### D.2 Not tied into `term_audit/provenance.py`   `[NAMED]`

A `PLACEHOLDER` provenance could optionally carry a
`deferred_cost` field grounded in this module's `CostLedger`
vocabulary — making the "retirement_path" discipline explicit
about the cost of NOT retiring the placeholder promptly. Not
implemented. Listed.


## Close-out

- Module shipped with 9 structured knowledge dicts + small
  machinery (`CostGrowth`, `CostLedger`, `compare`).
- Seven tripwires, four of them load-bearing (the narrative-order
  invariant, the VERDICT booleans, the canonical ledger growth
  tags, and the scalar-collapse refusal).
- Paired with `study_scope_audit` by design; CLI cross-reference
  tripwired.
- Regression: **48/48 PASS** (was 47/47).
- Two integration items named for future passes.
