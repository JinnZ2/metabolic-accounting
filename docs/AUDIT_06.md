# AUDIT 06

Sixth audit pass. Scope: a full-repo cross-check of STATUS.md /
AUDIT_05.md claims against a fresh run of `tests/test_*.py` and a
module-import sweep. Goal: identify drift landed since AUDIT_05 and
name the specific failures rather than leave them as aggregate counts.

Status key: `[CLOSED]` — fix present and covered by tests; `[OPEN]` —
scoped but not implemented; `[NAMED]` — identified as real gap, not
yet designed; `[DRIFT]` — STATUS.md or CLAUDE.md asserts a fact that
the code does not.


## Part A — Test-suite reality

Tree has **33** test files. A fresh regression run
(`for t in tests/test_*.py; do python "$t" && echo PASS || echo FAIL; done`)
produces:

- **31 PASS**
- **2 FAIL**: `test_governance_design_principles.py`,
  `test_recovery_pathways.py`

STATUS.md § "Verified (all tests run, all passing)" currently lists
31 passing suites and opens with "Thirty-one test suites, every one
runs and passes." This is false as written — the tree has two
additional test files that fail. AUDIT_05 acknowledged "33 test files
(31 verified passing)" but did not name the two failures; STATUS.md
never acknowledged the discrepancy at all.

### A.1 `test_governance_design_principles.py` — `ModuleNotFoundError`   `[OPEN]`

```
from term_audit.governance_design_principles import (
    DESIGN_PRINCIPLES, ...
)
ModuleNotFoundError: No module named 'term_audit.governance_design_principles'
```

The module exists on disk as `term_audit/governance_design_systems.py`
(commit `cc8f6cc`, "Add governance design principles and compliance
assessment"). The module's own file-level docstring still reads
`term_audit/governance_design_principles.py` — i.e. the author named
the module one thing in docs and another on disk, and the test
(commit `e41d030`, "Implement tests for governance design principles")
imports the doc name. Neither commit run against the other.

This is the same class of drift that AUDIT_04 unwound when STATUS.md
prose claimed fixes that had not landed, and that AUDIT_05 surfaced
as "paste-damage bugs caught by running the module." In this case
the bug was not caught because the test has never run.

**Fix options.** Rename the file to
`term_audit/governance_design_principles.py` (matches docstring +
test + commit message; mismatches commit-tree filename) or rename
the test to `test_governance_design_systems.py` and update the
import (matches on-disk filename). The first is more consistent
with the committed intent; either closes the gap.

### A.2 `test_recovery_pathways.py::test_4_stage_sequence_is_ordered` — modeling contradiction   `[NAMED]`

```
AssertionError: FAIL: stage order violations:
shelter_and_thermal_regulation (stage immediate_survival)
  depends on ecological_and_seasonal_observation (stage subsistence)
```

`term_audit/recovery_pathways.py` declares
`shelter_and_thermal_regulation` at stage `IMMEDIATE_SURVIVAL`
(rank 0) but lists `ecological_and_seasonal_observation` — rank 1,
`SUBSISTENCE_STABILIZATION` — as a prerequisite. Test 4 asserts no
function may depend on a prerequisite drawn from a later stage.
The code violates its own invariant.

This is not a test bug. Either:

- The dependency is over-specified. "Immediate shelter" in a collapse
  scenario is a windbreak or cave, which does not require seasonal
  knowledge; climate-adapted construction does, but that belongs to a
  later stage. Removing the `ecological_and_seasonal_observation`
  edge from `shelter_and_thermal_regulation` closes the violation
  and is defensible.
- Or shelter_and_thermal_regulation should move to
  `SUBSISTENCE_STABILIZATION`. Less defensible — thermal exposure
  kills in hours, not seasons.

Recommend the first. Either path is a model edit with a literature
citation required (per `docs/LITERATURE.md` discipline).

### A.3 `term_audit/integration/temporal_adapter.py` — import-time `NameError`   `[OPEN]`

```python
@dataclass
class AuditSnapshot:
    ...
    v_c_audit: Optional[TermAudit] = None      # substrate value
                        ^^^^^^^^^
NameError: name 'TermAudit' is not defined
```

Module imports from `term_audit.integration.metabolic_accounting_adapter`
but never imports `TermAudit` itself (commit `eb55207`, "Add temporal
adapter for metabolic accounting integration"). No test imports this
module, so the regression suite does not catch the failure — but the
module is unusable as shipped.

**Fix.** Add `from term_audit.schema import TermAudit` to the import
block. Then either wire a tripwire test (recommended, per the
test-first discipline) or explicitly mark the module `[DRAFT]` in
its docstring so the next session knows it is not yet live.


## Part B — Documentation drift

### B.1 STATUS.md claims 31/31; reality is 31/33   `[DRIFT]`

STATUS.md § "Verified" header: "Thirty-one test suites, every one
runs and passes." The two test files missing from the list
(`test_governance_design_principles`, `test_recovery_pathways`) are
exactly the two that currently fail. A reader running the command
STATUS.md prints — `for t in tests/test_*.py; do python "$t" && echo
PASS || echo FAIL; done` — gets 2 FAIL lines with no hint from the
status file that those failures are expected.

This is the exact failure mode AUDIT_04 named: "Bug 1 and Bug 4
were described as fixed in an earlier pass, but the code changes had
not landed — only the prose." Here, two tests exist but are treated
as if they do not. The repo's own discipline
(`CLAUDE.md` "Every claim about framework behavior must be backed by
a test that actually produces the output") is violated by its own
status file.

**Fix.** Update STATUS.md to (a) acknowledge 33 test files exist,
(b) name the two that fail, (c) link to this audit for the cause.

### B.2 CLAUDE.md navigation table omits ~9 modules   `[DRIFT]`

The "Navigation — where to start by intent" table in `CLAUDE.md`
does not list any of:

- `term_audit/recovery_pathways.py`
- `term_audit/governance_design_systems.py` (or `_principles.py`)
- `term_audit/alternative_viability.py`
- `term_audit/consequence_accounting.py`
- `term_audit/collapse_propensity.py`
- `term_audit/civilization_substrate_scaling.py`
- `term_audit/systemic_necessity.py`
- `term_audit/expertise.py`
- `term_audit/integration/temporal_adapter.py`

AUDIT_05.md § "Horizontal-measurement tools (Tier 3 territory)"
describes most of these; none of them made it into the CLAUDE.md
navigation surface. CLAUDE.md is the first document a fresh session
reads to orient itself; omissions here cause re-derivation or
re-invention of modules that already exist. AUDIT_05 landed commit
`4adedcf` ("Extend CLAUDE.md nav table with term_audit-era landings")
but the table still predates the seven modules above.

**Fix.** Append rows for each module to the CLAUDE.md nav table with
the canonical "start here / then here" pattern.


## Part C — Process drift

### C.1 Commit messages that do not describe the diff   `[NAMED]`

Two commits on this branch carry messages that bear no relation to
their diffs:

```
3631856 Update print statement from 'Hello' to 'Goodbye'
        +1464 lines in term_audit/civilization_substrate_scaling.py

64ebab4 Update fmt.Println message from 'Hello' to 'Goodbye'
        +1151 lines in term_audit/collapse_propensity.py
```

Both commits add substantial new modules; neither touches a print
statement of any kind, let alone a Go `fmt.Println`. These look like
machine-generated boilerplate messages unrelated to the actual
change. `git log` is a load-bearing audit surface in this repo
(AUDIT_04 used it to unwind the STATUS.md / code mismatch); messages
disconnected from their diffs degrade that surface.

No action this audit — the commits are historical and amending them
risks rewriting a branch others may have pulled. Named here so future
sessions know the two "Hello/Goodbye" commits are in fact
substantive module adds, not cosmetic string edits.


## Part D — What's verified healthy

A spot-check of load-bearing invariants:

- Main accounting stack: all 18 suites pass. `test_integration`
  reproduces STATUS.md numerics (reported 399.33, metabolic 370.73,
  visible hidden cost 28.60; cumulative drawdown 221.61 xdu at 30
  periods).
- Reserves / first-law closure: multi-metric closure delta 1.42e-14
  across 17 metrics. Matches STATUS.md. Negative-destruction refusal
  still fires (entropy-decrease guard).
- Tier registry: 7 tiers, 65 terms, counts per tier 8/10/9/14/9/8/7.
  Matches STATUS.md and `docs/TERMS_TO_AUDIT.md`.
- `test_preemption`: 12/12 pass. Load-bearing Test 10
  (`distinction_as_coordination` must stay falsified) still falsifies
  at 22.863 / 100 total energy — well above the 2% threshold — which
  is the margin AUDIT_05 relied on.
- Term audits: all numerical claims in STATUS.md § "Term-audit
  layer" reproduce (`efficiency` fails 6/7 — calibration,
  conservation, observer, referent, scope, unit — with falsifiability
  surviving; matches both STATUS.md and AUDIT_05).


## Part E — Open bugs rolled forward

From AUDIT_04 and AUDIT_05, unchanged this audit:

- **Bug 2** (regulatory crosswalk has no social/labor frameworks):
  `[OPEN]`. Candidates in `AUDIT_04.md` Part B.
- **Bug 3** (no community-specific mitigation patterns): `[OPEN]`.
  Candidates in `AUDIT_04.md` Part C.
- **D.1** (endogenous firm-behavior feedback from verdict → next
  period): `[NAMED]`.
- **D.2** (directional inter-basin coupling over time): `[NAMED]`.

Plus the AUDIT_05 § "Part E" hidden-variable list (geographic
proximity, generational lag, trust hysteresis, temporal asymmetry,
redundant status_extraction derivations): `[OPEN]`, unchanged.


## Part F — Coverage snapshot

| Tier | Audited / Total | Added since AUDIT_05 |
| --- | --- | --- |
| 1 — foundational fictions | 3 / 8 | 0 |
| 2 — labor and human-worth | 2 / 10 | 0 |
| 3 — organizational legitimacy | 0 / 9 (machinery landed) | 0 |
| 4 — capacity measurements | 1 / 14 | 0 |
| 5 — social and behavioral | 0 / 9 | 0 |
| 6 — knowledge and truth | 0 / 8 | 0 |
| 7 — environmental and resource | 0 / 7 | 0 |

6 of 65 audited, same as AUDIT_05. This sprint did not add concrete
audits; it added supporting infrastructure
(`recovery_pathways`, `governance_design_systems`, `temporal_adapter`)
and introduced the three defects above.


## Part G — Recommended next actions, ordered by reversibility

1. **[SAFE]** Fix `test_governance_design_principles.py` by renaming
   `term_audit/governance_design_systems.py` →
   `term_audit/governance_design_principles.py` (matches docstring
   and commit intent). One-line test change only if the rename is
   rejected.
2. **[SAFE]** Add `from term_audit.schema import TermAudit` to
   `term_audit/integration/temporal_adapter.py`. Add a smoke-import
   tripwire test.
3. **[MEDIUM]** Resolve `recovery_pathways` stage-dependency
   contradiction. Recommend removing the
   `shelter_and_thermal_regulation →
   ecological_and_seasonal_observation` dependency (reasonable:
   immediate shelter is pre-seasonal). Requires a note in
   `docs/LITERATURE.md` if one exists for this claim; otherwise tag
   as `[HEURISTIC]` per `docs/EQUATIONS.md` discipline.
4. **[SAFE]** Update STATUS.md § "Verified" to reflect 33 test
   files, name the 2 currently failing, link to this audit.
5. **[SAFE]** Extend CLAUDE.md navigation table with the 9 unlisted
   modules from § B.2.

None of these are architectural. All are drift-repair.


## Close-out

- Two concrete test failures surfaced that STATUS.md asserts do not
  exist. Both named and scoped for fix.
- One silent module-import failure (`temporal_adapter.py`) that
  survives because no test touches it.
- STATUS.md / CLAUDE.md drift catalogued; fix path is mechanical.
- Main accounting stack, first-law closure, tier registry, preempt
  #10 all verified healthy against STATUS.md numerics.
- No changes to AUDIT_04 bugs 2/3 or the AUDIT_05 hidden-variable
  list; no new architectural observations.
