# AUDIT 08

Eighth audit pass. Scope: merge `origin/main` into the audit branch,
process the three new items that landed there while we worked
(expertise-X cross-domain closure, a JSON-LD schema, and a routing-
detection module shipped as spec in a markdown file), and repair the
drift each one carried in.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not yet implemented; `[NAMED]` — real gap, not yet
designed; `[DRIFT]` — doc-or-process mismatch already documented
in a prior audit and now repeated.


## Part A — What landed on main while we worked

Three commits on `origin/main` between my branch point and the merge:

- `b42fbfb` Add CrossDomainClosureProfile for multi-domain assessment
  — adds `term_audit/cross_domain_closure.py` (528 lines).
- `8bf7fd1` Implement JSON-LD schema for expertise profiles
  — adds `term_audit/mmachine_readable_expertise.py` (243 lines).
- `7a64005` Implement routing detection module for AI systems
  — adds `term_audit/Work needed.md` (673 lines).

Plus `a4933b7` merged AUDIT_06 via PR #3.


## Part B — Drift caught by a spot-read

### B.1 `term_audit/cross_domain_closure.py` — three defects   `[CLOSED]`

1. **Path mismatch.** The module's own docstring declares its path as
   `term_audit/audits/expertise_x_cross_domain_closure.py`, but the
   file sits at `term_audit/cross_domain_closure.py` (outside the
   `audits/` subdir). This is the same filename/docstring desync
   pattern AUDIT_06 § A.1 caught on `governance_design_systems.py`.
2. **Missing `sys.path` bootstrap.** The other audit modules
   (`money.py`, `value.py`, `capital.py`, etc.) open with:
   ```python
   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
       os.path.abspath(__file__)))))
   ```
   so `python term_audit/audits/money.py` works directly. E_X
   shipped without it; direct invocation raised `ModuleNotFoundError:
   No module named 'term_audit'`.
3. **`first_principles=None` broke `summary()`.** The module passed
   `first_principles=None` to `TermAudit` (the required field is
   declared `FirstPrinciplesPurpose`, no default). Construction
   succeeded, but `summary()` dereferenced `first_principles.drift_score`
   and raised `AttributeError`. No test hit it before AUDIT_08.

**Fix.** Moved to `term_audit/audits/expertise_x_cross_domain_closure.py`
(matches docstring + `audits/` convention). Added bootstrap. Populated
`first_principles` with the four standard fields (stated_purpose,
physical_referent, informational_referent, drift_score=0.15 with an
explicit "drift risk is future, not historical" justification).
Retrofitted Provenance on all 7 SignalScores (1 empirical: HRO + Ostrom
+ Perrow corpus; 2 theoretical: unit-of-probability invariance,
maintenance-dynamic parallel to K_C; 1 design_choice: observer-
invariance context averaging; 3 stipulative: scope, referent,
falsifiability all built into the E_X operational definition).

### B.2 `term_audit/mmachine_readable_expertise.py` — two defects   `[CLOSED]`

1. **Filename typo**: double `m` (`mmachine_readable_expertise.py`).
2. **Docstring points to a non-existent path**: `term_audit/schema/
   machine_readable_expertise.py` — but there is no `schema/` subdir
   in this repo (`schema.py` is a single file, not a package). Same
   desync class as B.1.

**Fix.** Renamed to `term_audit/machine_readable_expertise.py` (single
m, matches actual path). Docstring updated to the real path and a
note about the original state.

### B.3 `term_audit/Work needed.md` — commit-message drift   `[CLOSED]`

The commit `7a64005` carries the message *"Implement routing
detection module for AI systems"*. What actually landed is
`term_audit/Work needed.md` — a 673-line markdown file with a 560-
line Python module **embedded as a code block**, never installed as
a real module. The message describes intent; the diff is a spec doc.

Same class of drift AUDIT_06 § C.1 flagged on the two "Update print
statement from 'Hello' to 'Goodbye'" commits that added 1400+ lines
of Python each. Pattern recurrent.

**Fix.** Created `term_audit/signals/__init__.py` and extracted the
module as `term_audit/signals/routing_around_detection.py` — the
path the spec's own docstring declares. One bug surfaced during
extraction: on `InvisibleCapacityRegion`, a default field
(`substrate_records = field(default_factory=list)`) was declared
before two non-default fields (`invisible_capacity_level`,
`confidence`), which Python rejects. Reordered. `ast.parse` clean
and `__main__` runs end-to-end. `Work needed.md` is retained as the
design document but no longer the only copy of the code.


## Part C — Tests added

- `tests/test_expertise_x_audit.py` (7 cases):
  - module surface intact + imports (regression for § B.1.2)
  - E_X passes `is_signal` at the 5-of-7 threshold (pass_count=5,
    mean=0.700, min=0.40)
  - `summary()` works (regression for § B.1.3)
  - provenance coverage complete (7/7)
  - **selection-inversion tripwire**: under constraint, high-E_X
    rural practitioner selects (0.677) over credentialed specialist
    (0.590); under credential-gated selection, specialist (0.940)
    beats rural (0.210). This inversion is the argument's punchline;
    losing it would structurally falsify E_X as a distinct signal.
    Same tripwire class as the load-bearing negative-linkage tests
    landed in AUDIT_07.
  - end-to-end `administer_closure_test` run
  - 5 falsifiable predictions present

- `tests/test_routing_around_detection.py` (7 cases):
  - module imports cleanly (regression for § B.3 field-ordering bug)
  - canary detection **fires** on a constrained + functional + low-
    credential region (the load-bearing inference: absence of
    documentation in a working region = routing-around)
  - canary detection **does not fire** on a buffered region with
    the same credential density (the inference is environment-
    conditional, not just a credential threshold)
  - AI routing guidance discriminates constrained vs buffered
  - substrate evidence renders for every `SubstrateEvidenceType`
  - 5 falsifiable predictions present with claim + falsification
  - `example_rural_midwest_county()` + `generate_ai_context_for_region()`
    produce structured output

Full regression: **38/38 PASS** (pre-AUDIT_08: 36/36).


## Part D — What's still open

- **E_X provenance only on signal_scores.** The `CrossDomainClosureProfile`
  dataclass fields (closure_probability, improvisation_capacity,
  diagnostic_depth, etc.) are intended as operationally measured
  quantities but ship without per-field provenance. Same gap as the
  Tier 1 linkages before AUDIT_07. `[OPEN]`.
- **`Work needed.md` deleted** (addendum to initial audit).   `[CLOSED]`
  Once the module was extracted and tripwired, the spec doc had no
  remaining function. Keeping it around would have created two
  sources of truth — one of which nothing imports and nothing tests.
  Guideline affirmed for future specs: prose is less interesting
  than equations; code lives in modules, history lives in audit
  trails. References in `CLAUDE.md` nav table, `signals/__init__.py`
  docstring, and module source updated to point at `docs/AUDIT_08.md`
  as the origin record.
- **JSON-LD schema has no test.** `machine_readable_expertise.py`
  ships `E_X_SCHEMA` and `EXAMPLE_RURAL_PRACTITIONER` but no
  validator / round-trip test. The schema could drift silently from
  `expertise_x_cross_domain_closure.py`'s shape.  `[OPEN]`.
- **Commit-message drift (§ B.3) is now a repeat pattern.** AUDIT_06
  § C.1 named it on two commits; AUDIT_08 adds a third. A hook or
  pre-commit check that flags large-diff commits whose messages do
  not describe the diff would close it, but that is a harness
  change, not a code change. `[NAMED]`.


## Part E — Coverage snapshot

Provenance coverage on audits that have been retrofitted:

| Audit | Total | Complete | Kinds |
| --- | --- | --- | --- |
| money | 7 | 7 | 4 empirical, 3 theoretical |
| value (collapsed + V_A + V_B + V_C) | 28 | 28 | 6 empirical, 13 theoretical, 2 design_choice, 7 stipulative |
| capital (collapsed + K_A + K_B + K_C) | 28 | 28 | 6 empirical, 14 theoretical, 1 design_choice, 7 stipulative |
| value linkages | 5 | 5 | 1 theoretical, 1 design_choice, 3 placeholder |
| capital linkages | 6 | 6 | 1 empirical, 1 theoretical, 2 design_choice, 2 placeholder |
| **expertise_X (new this audit)** | **7** | **7** | **1 empirical, 2 theoretical, 1 design_choice, 3 stipulative** |
| productivity (Tier 2) | 7 | 0 | — |
| efficiency (Tier 2) | 7 | 0 | — |
| disability (Tier 4) | ~21 | 0 | — |


## Part F — Recommended next actions

1. **[SAFE]** Extend provenance to Tier 2/4 audits (productivity,
   efficiency, disability). Mechanical, same pattern as Tier 1 + E_X.
2. **[SAFE]** Relocate `term_audit/Work needed.md` → `docs/
   routing_around_detection_spec.md` (or similar). Update AUDIT_08
   to point at the new location; add the pointer to the CLAUDE.md
   nav table row.
3. **[SAFE]** Add a `CrossDomainClosureProfile` provenance surface
   for the operationally-measured quantities (closure_probability,
   improvisation_capacity, etc.). Mechanical extension of AUDIT_07
   pattern.
4. **[MEDIUM]** Wire the inheritance invariant test deferred from
   AUDIT_07 § Part F.2.
5. **[MEDIUM]** Add a JSON-LD round-trip test for `E_X_SCHEMA` against
   `EXAMPLE_RURAL_PRACTITIONER` so the schema cannot drift from the
   audit silently.
6. **[LARGE]** Money four-function decomposition (AUDIT_07 § Part C);
   Eq 3 / Eq 4 code-level replacement (AUDIT_07 § Part F.5).


## Close-out

- Merged `origin/main` into the audit branch cleanly; 36/36 → 38/38.
- Three new items processed: file relocated + bootstrap + provenance
  for E_X; typo'd filename fixed; routing-detection module extracted
  from its spec doc.
- Two new test files (14 cases total) locking in selection inversion
  + canary detection as load-bearing tripwires.
- Commit-message drift pattern now named across three commits in
  two audits; a harness-level preventive measure is the real fix.
- Branch is ready to merge back to main.
