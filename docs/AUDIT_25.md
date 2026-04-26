# AUDIT 25

Twenty-fifth audit pass. Scope: align the cross-repo topology with
the existing one-way `Mathematic-economics → metabolic-accounting`
import direction by (a) acknowledging math-econ as a fifth companion
repo, (b) mapping the abstract Tier 1 / Tier 2 term audits to the
falsifiable measurement equations math-econ ships under
`equations-v1`, (c) declaring a reciprocal stable-surface tag
(`money_signal-v1`) that downstream consumers can pin against, and
(d) shipping a `ComplianceScorecard` data structure that mirrors
math-econ's worked Smith-compliance pattern for use as a
falsification artifact in this repo.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[INFORMATIONAL]` — pointer / contract
addition without runtime semantics.


## Part A — Motivation

`audit/money_signal_bridge.py` in `JinnZ2/Mathematic-economics`
already imports `money_signal.dimensions` and
`money_signal.coupling` from this repo. The bridge constructs a
neutral `DimensionalContext` and exposes the three primitives
(minsky coefficient, coupling magnitude, sign-flip) that this
repo's `accounting_bridge.signal_quality()` collapses into a
`[0, 1]` score. The dependency is one-way: math-econ depends on
this repo; this repo does not depend on math-econ.

Two consequences of that existing relationship were unaddressed
before this audit:

1. **Documentation drift.** `docs/RELATED.md` listed four repos
   (TAF, this, PhysicsGuard, Logic-Ferret) and had no entry for
   math-econ. A new reader could not see that math-econ already
   imports from this repo, what surface it pins against, or what
   the dependency direction is.
2. **Operationalization gap.** The Tier 1 audits in
   `term_audit/audits/` (`money`, `capital`, `value`) and the
   Tier 2 audits (`productivity`, `efficiency`) state failure
   modes precisely but stop short of citing falsifiable measurement
   equations for the failures. Math-econ already ships those
   equations under a versioned tag (`equations-v1`). The mapping
   was not written down.

A separate gap, partly orthogonal: this repo had no documented
stable-surface tag of its own. Math-econ's bridge had nothing to
pin against, so it tracked `main`. AUDIT_25 declares
`money_signal-v1` and locks the relevant surface in
`docs/SCHEMAS.md`.

A fourth gap, conceptual: math-econ's worked Smith-compliance
scorecard (current US system: 0/8 criteria met against
Adam-Smith-style capitalism) is a clean instance of this repo's
own Preempt-#1 / Preempt-#6 pattern from
`docs/PREEMPTING_ATTACKS.md`. The data structure was missing
locally.


## Part B — Concrete fixes shipped

### Part B.1 — `docs/RELATED.md` adds math-econ as fifth repo

Status: `[CLOSED]` `[INFORMATIONAL]`.

The four-repo table is now a five-repo table. A new "Relationship
to Mathematic-economics (downstream consumer)" section spells out:

- the existing one-way import direction (math-econ →
  metabolic-accounting; never the reverse),
- the three primitives the bridge reads,
- the two practical consequences (citation contract for
  operationalizations; obligation to maintain a stable surface),
- the topology note that math-econ ships its own thermodynamic
  essays and a vendored `physics_guard/` subtree, so it does not
  require runtime access to the other companions either.

The pointer-map table at the bottom of `docs/RELATED.md` adds a
row for "falsifiable measurement equations for Tier 1/2 economic
terms".

### Part B.2 — `docs/EXTERNAL_OPERATIONALIZATIONS.md` ships the term-to-equation map

Status: `[CLOSED]` `[INFORMATIONAL]`.

A new top-level doc maps each currently-committed Tier 1 / Tier 2
audit to its candidate operational measurement equation(s) from
math-econ:

| Audit | Equation(s) |
| --- | --- |
| `money` | MSI, MM, BSC |
| `capital` (K_A / K_B / K_C split) | VE/VL, HHI, SID |
| `value` (V_A / V_B / V_C split) | ER, LWR |
| `productivity` | VE/VL + LWR + ER in combination |
| `efficiency` | HHI, ISR (scalar projections of the vector metric) |

The doc opens with the **signal-quality discount** caveat:
money-denominated math-econ equations cannot be read straight as
measurements without re-introducing the currency bias this repo's
`money_signal/` was built to surface. The canonical workflow is to
construct a `DimensionalContext`, compute the three primitives,
and carry the raw equation output and the `[0, 1]` discount factor
side-by-side rather than collapsing them.

The doc also declares which math-econ equations do **not** map
cleanly into this repo's audits as of this date (RI, DI, ISR for
externality), preventing a future session from over-claiming the
mapping.

Per-module pointers were added as docstring entries to:

- `term_audit/audits/money.py`
- `term_audit/audits/capital.py`
- `term_audit/audits/value.py`
- `term_audit/audits/productivity.py`
- `term_audit/audits/efficiency.py`

Reading-order step 7 was added to `docs/TERMS_TO_AUDIT.md` so an
AI assistant working an audit lands on
`docs/EXTERNAL_OPERATIONALIZATIONS.md` after the local audit
modules.

### Part B.3 — `money_signal-v1` stable-surface tag

Status: `[CLOSED]` `[INFORMATIONAL]`.

`docs/SCHEMAS.md` gains a new "Stable surface tags" section
declaring `money_signal-v1` and what it locks: every enum in
`money_signal/dimensions.py`, the signature and return shape of
`compose_coupling_matrix`, and the **identity** (not the values) of
the three primitives a downstream bridge can read raw.

Calibration knobs (`K_BASE` numeric values, per-factor matrix
contents, exact `historical_cases.py` ordering) are explicitly
**not** locked under `money_signal-v1`. They may shift in a minor
version bump; consumers wanting frozen numerics record the commit
SHA alongside the tag.

The discipline rule mirrors math-econ's: do not delete or
force-move `money_signal-v1`. Add `money_signal-v2` when a
breaking change is needed; consumers migrate at their own pace.

### Part B.4 — `ComplianceScorecard` lands in `term_audit/falsification.py`

Status: `[CLOSED]`.

Two new dataclasses:

- `ComplianceCriterion(name, expected_indicator, observed_indicator,
  threshold_description, source_refs, result, notes)` — one row of
  a compliance scorecard. `result` is one of `met / not_met /
  ambiguous / untested`.
- `ComplianceScorecard(claim, theory_name, theory_source_refs,
  criteria, notes)` — the scorecard itself. Methods:
  - `n_total()`, `n_met()`, `n_not_met()`, `n_ambiguous()`,
    `n_untested()`,
  - `fraction_met()` (None when no criteria are decided),
  - `is_falsified()` (True iff `n_not_met() > 0` and `n_met() ==
    0`; intentionally strict),
  - `summary()`.

The structure is deliberately minimal so concrete scorecards can
be co-located with the term audit that motivates them (e.g. a
future GDP-as-economic-growth audit would carry a Smith-compliance
scorecard alongside its `TermAudit`). The shipped Smith-compliance
worked example lives in math-econ; this module ships the data
structure only.

Tests: `tests/test_compliance_scorecard.py` — covers the empty
scorecard, the all-untested scorecard, the all-met scorecard, the
all-not-met scorecard (which is the load-bearing falsification
case), the mixed-decided scorecard, and the strict-falsification
boundary (a single `met` blocks `is_falsified()`).

### Part B.5 — OSDI cross-reference in `money_signal/coupling_state.py`

Status: `[CLOSED]` `[INFORMATIONAL]`.

The module docstring gains an "External calibration anchor"
paragraph noting that math-econ's OSDI (composite of SID, MSI,
ISR, BSC, MM into a `[0, 1]` structural-context scalar)
constrains which `StateRegime` is reachable, even though OSDI is
not itself a regime. The note flags a future calibration path —
consume an external OSDI score per regime — without committing to
implementation. Today's enum input is unchanged.


## Part C — Why the four candidate strengthenings landed in this order

1. `docs/RELATED.md` first because every other change cites it.
2. `docs/EXTERNAL_OPERATIONALIZATIONS.md` next because it's the
   document the docstring pointers (B.2) depend on.
3. `docs/SCHEMAS.md` `money_signal-v1` next because the
   external-operationalizations doc cites the tag.
4. `ComplianceScorecard` ships standalone (no dependencies on the
   above), but conceptually belongs in this group because its
   primary use case is auditing claims like "the system is X" with
   the same rigor math-econ applied to "the system is capitalist".
5. The OSDI cross-reference is a one-paragraph hook for future
   work. Filed last because it carries no runtime semantics today.


## Part D — Things AUDIT_25 explicitly did NOT do

- **Did not adopt math-econ's pytest layout.** This repo remains
  stdlib-only test scripts.
- **Did not import math-econ at runtime.** The relationship is
  citation-only; consumers wanting the actual measurements depend
  on math-econ themselves.
- **Did not adopt math-econ's PyTorch `AI/` directory or any
  third-party dependency.** CC0 + stdlib-only is non-negotiable.
- **Did not naively wire money-denominated equations into the
  accounting pipeline.** Doing so without the
  `money_signal/accounting_bridge.signal_quality()` discount would
  re-introduce the currency bias the framework is built to defend
  against. The `EXTERNAL_OPERATIONALIZATIONS.md` doc explicitly
  flags this as the canonical caveat.
- **Did not ship a concrete Smith-compliance scorecard.** That
  worked example lives in math-econ; replicating it here would
  duplicate the artifact without strengthening the framework. The
  data structure is what this repo needed; the data is what
  math-econ ships.


## Part E — Counts that should now hold

These are the post-AUDIT_25 invariants that
`scripts/counts_consistency.py` and `scripts/name_set_consistency.py`
do **not** automatically check (because they live in markdown), but
that a future audit should re-verify if any of these files change:

- `docs/RELATED.md` lists exactly five repos.
- `docs/EXTERNAL_OPERATIONALIZATIONS.md` cites exactly the five
  audit modules currently committed under `term_audit/audits/`
  whose terms appear in Tier 1 or Tier 2 (`money`, `capital`,
  `value`, `productivity`, `efficiency`). When new Tier 1/2 audits
  land, this doc must be updated.
- `docs/SCHEMAS.md` declares exactly one stable-surface tag
  (`money_signal-v1`). New tags are additive; do not move existing
  tags.
- `tests/test_compliance_scorecard.py` exercises the strict
  falsification boundary explicitly (`is_falsified()` is False
  when any criterion is `met`, even if every other criterion is
  `not_met`).


## Part F — Forward hooks left open

`[OPEN]`. Filed for a future audit, not blocking this one.

1. **Semantic Drift Rate (SD) consumer.** Math-econ ships an SD
   equation using embedding distance. This repo's
   `term_audit/scoping.py` and `term_audit/contradictions.py`
   could consume an externally-computed SD score per term as
   another axis of narrative-strip detection. Hook noted in
   `docs/EXTERNAL_OPERATIONALIZATIONS.md`; no implementation.
2. **OSDI as `DimensionalContext` field.** The note added to
   `coupling_state.py` is a docstring entry only. A real
   integration would add an `osdi: float` or
   `institutional_collectivity: float` field to
   `DimensionalContext` and propagate it through the factor
   modules. That is a `money_signal-v2` change.
3. **Concrete compliance scorecards.** The `ComplianceScorecard`
   data structure is shipped; a worked Smith-compliance scorecard
   for a future GDP-as-economic-growth audit would be the obvious
   first instance. Filed against the not-yet-committed
   `term_audit/audits/economic_growth.py`.
4. **Reciprocal pin in math-econ.** Once `money_signal-v1` is
   tagged in this repo, math-econ's `audit/money_signal_bridge.py`
   could pin to it explicitly rather than tracking `main`. That
   change lives in math-econ.


## Part G — Test status

Pre-existing tests: every test that passed before AUDIT_25 still
passes (no semantic changes to existing modules; only docstring
additions and a new dataclass in `term_audit/falsification.py`).

New tests: `tests/test_compliance_scorecard.py`, six cases.

Re-run command from repo root:

```
for t in tests/test_*.py; do python "$t" >/dev/null 2>&1 && \
  echo "PASS $t" || echo "FAIL $t"; done
```

Per `CLAUDE.md`'s test discipline: do not report a numerical
result without re-running the test now. The PASS list in
`STATUS.md` is updated only after a fresh pass-through.
