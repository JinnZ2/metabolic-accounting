# FALSIFIED.md — the precedent ledger

Claims this repo made, ran, and had to edit or retract. Append-only.

Every row was reconstructed from the audit trail and `STATUS.md` and
cross-checked against the code as it stands on 2026-08-14, with the
full suite (55/55) passing at the time of writing.

**Status vocabulary**

| Status | Meaning |
| --- | --- |
| `FIXED` | claim was right, implementation was wrong; code changed |
| `SUPERSEDED` | claim was wrong or too broad; claim changed |
| `OPEN` | falsified, replacement not yet built |
| `STANDING` | asserted false on purpose, tripwired to stay false |

---

## L-01 — Tier determination handled cliff-threshold basins correctly

- **Claimed:** `determine_tier_for_basin` assigned tiers correctly
  across all basin metrics.
- **Falsified by:** `AUDIT_04`, Bug 1. Cliff-threshold basins were
  mis-tiered.
- **Edit:** logic corrected in `distributional/tiers.py`; falsification
  signal preserved as `tests/test_tier_vector.py`.
- **Status:** `FIXED`
- **Precedent:** the audit found this by *reading the code against its
  own docstring*, not by a failing test — no test existed to fail.

## L-02 — A single overall tier was sufficient to describe a firm

- **Claimed:** collapsing the tier vector to `overall_tier()` lost
  nothing that mattered.
- **Falsified by:** `AUDIT_04`, Bug 4. A firm GREEN on soil and BLACK
  on community hits cohorts differently; the scalar erased the
  difference.
- **Edit:** `TierAssignment.by_basin_type` became the primary surface;
  `overall_tier()` demoted to a worst-case aggregate.
  `apply_tier_to_cohorts` grew the `cohort_basin_sensitivities` vector
  path, with the scalar retained as the backward-compatible route.
- **Status:** `FIXED`
- **Precedent:** *calling `overall_tier()` and discarding the vector is
  still the shape of this bug.* Prefer basin-type-aware consumers.

## L-03 — Bugs 2 and 3 would be closed in the same pass as 1 and 4

- **Claimed:** `AUDIT_04` surfaced four bugs; the tier-vector fixes
  implied the rest were near.
- **Falsified by:** elapsed audits. Bug 2 (no social/labor regulatory
  frameworks in `regulatory/frameworks.py`) and Bug 3 (no
  community-specific mitigation patterns in `mitigation/actions.py`)
  remain unbuilt through `AUDIT_25`.
- **Edit:** rescoped from "pending" to named open work;
  `docs/AUDIT_04.md` Parts B and C carry the candidate plans.
- **Status:** `OPEN`

## L-04 — STATUS.md described the tree

- **Claimed:** at the start of the `AUDIT_05` sprint, `STATUS.md`
  reported 18 passing suites and had no knowledge of `term_audit/`.
- **Falsified by:** `AUDIT_05 § C`. The tree had 33 test files and a
  whole undocumented layer.
- **Edit:** `STATUS.md` rewritten (commit `4ea0476`).
- **Status:** `SUPERSEDED`
- **Precedent:** **this is the repo's signature failure mode, and it has
  now recurred three times** — `AUDIT_04` unwound it, `AUDIT_05 § C`
  caught it again, and the AUDIT_23/24 count-and-name scanners were
  built specifically to automate catching it. It is not carelessness;
  prose and code age at different rates by default. Assume it is
  happening and go look.

## L-05 — `cascade_from_negative_linkage` returned a coupling input

- **Claimed:** the adapter converted negative linkages into
  `CascadeCouplingInput`.
- **Falsified by:** `tests/test_metabolic_accounting_adapter.py::test_7`.
  It returned `None` unconditionally — paste damage had left the
  `return` unreachable inside the `if strength >= 0` branch.
- **Edit:** fixed in commit `8145548`.
- **Status:** `FIXED`
- **Precedent:** chat-pasted code arrives with flattened bodies and
  unreachable returns. `scripts/fix_pasted_file.py` exists for this;
  `ast.parse` the result and *run the module* before trusting it.

## L-06 — The governance module was named what its tests imported

- **Claimed:** `term_audit.governance_design_principles` existed and
  declared 13 principles.
- **Falsified by:** `AUDIT_06 § A.1`. The file on disk was
  `governance_design_systems.py` — despite its own docstring naming it
  `_principles` — so the test failed at import. And 14 principles had
  actually landed, not 13.
- **Edit:** file renamed to match the intended name; count tripwire
  corrected 13 → 14 to match what shipped.
- **Status:** `FIXED`
- **Precedent:** a count in prose is a claim. Drift between "the plan"
  and "what landed" is why `scripts/counts_consistency.py` now declares
  15 counts and tripwires them.

## L-07 — `recovery_pathways.py` satisfied its own stage ordering

- **Claimed:** the module's stage-ordering invariant held over its
  prerequisite graph.
- **Falsified by:** `AUDIT_06`. `shelter_and_thermal_regulation`
  (IMMEDIATE_SURVIVAL) listed `ecological_and_seasonal_observation`
  (SUBSISTENCE) as a prerequisite — the module violated the rule stated
  in its own docstring.
- **Edit:** edge removed with an inline rationale citing the audit
  (immediate shelter is pre-seasonal); the missing
  `shelter_and_thermal_regulation` preservation strategy added.
- **Status:** `FIXED`
- **Precedent:** **check modules against their own docstring
  invariants.** Two separate findings here came from that one move.

## L-08 — `temporal_adapter.py` imported cleanly

- **Claimed:** the module was working.
- **Falsified by:** `AUDIT_06`. It raised `NameError` at import time —
  `TermAudit` annotated without being imported. Nothing had ever
  imported it.
- **Edit:** fixed; `tests/test_temporal_adapter.py` added as the
  module's first tripwire.
- **Status:** `FIXED`
- **Precedent:** an untested module is not "probably fine," it is
  unrun. This one had never been executed at all.

## L-09 — `source_refs: List[str]` captured provenance

- **Claimed:** `SignalScore`'s loose string list was enough to record
  where a number came from.
- **Falsified by:** `AUDIT_07`. The list could not distinguish an
  empirical citation from a design choice from a placeholder — so a
  stipulated constant and a measured value read identically.
- **Edit:** `term_audit/provenance.py` added the five-kind taxonomy
  (`EMPIRICAL` / `THEORETICAL` / `DESIGN_CHOICE` / `PLACEHOLDER` /
  `STIPULATIVE`) with `knowledge_dna` pass-through.
- **Status:** `SUPERSEDED`

## L-10 — `validate_all_factor_modules()` validated the factor modules

- **Claimed:** `money_signal`'s README said "always validate at
  startup," implying the validator ran clean.
- **Falsified by:** `AUDIT_11 § B`. It shipped broken. The **pointwise**
  Minsky check in `coupling_cultural.py`, `coupling_attribution.py`, and
  `coupling_observer.py` rejected `COMMUNITY_TRUST`, whose factors
  deliberately damp Minsky asymmetry — composed ratio 1.0, which
  *satisfies* README claim #1 at the composed level.
- **Edit:** all three validators now compute composed coupling
  (`K_BASE[i][j] * f_ij`) and assert `>=` at that level.
- **Status:** `FIXED`
- **Precedent:** the check was applied at the wrong level of
  composition. The claim was true; the test of it was testing a
  different quantity. Before fixing data to satisfy a validator,
  confirm the validator measures the thing the claim is about.

## L-11 — Every historical anchor would match the framework

- **Claimed:** the `money_signal` anchors would corroborate the
  coupling model.
- **Falsified by:** `tests/test_historical_cases.py` TEST 6, run
  2026-08-14: **12 of 13 qualitative matches; Cyprus flagged as
  outlier.**
- **Edit:** none to the model. The expected distribution was written
  into the test as 12/13 with Cyprus named, rather than tuning
  parameters until Cyprus agreed.
- **Status:** `OPEN` — Cyprus remains unexplained and is *kept*
  unexplained.
- **Precedent:** **the outlier is the asset.** A framework that matched
  13/13 after tuning would carry less information than one that matches
  12/13 and says which one it misses.

## L-12 — `distinction_as_coordination` (counter-hypothesis)

- **Claimed (by the counter-hypothesis, not by us):** status
  distinctions function as coordination mechanisms rather than
  extraction.
- **Falsified by:** `term_audit/counter_hypotheses.py` under default
  dynamics; asserted false by `tests/test_preemption.py` test 10, which
  requires it stay falsified at a ≥2% margin.
- **Edit:** none. Held falsified deliberately.
- **Status:** `STANDING`
- **Precedent:** **if this flips, it is a finding, not a broken test.**
  Supporting it would require changing the model *and* the audit notes
  together. Do not relax the assertion to make a run pass.

## L-13 — `STATUS.md` section structure was clean

- **Claimed:** implicitly, by `STATUS.md` being the maintained record.
- **Falsified by:** direct inspection, 2026-08-14. The heading
  `## AUDIT_14 — Part B (E.2): investment_signal/historical_cases.py`
  appeared **three times**; two occurrences (former lines 516 and 756)
  were empty orphan stubs with no body, one immediately followed by the
  unrelated `AUDIT_25` section wedged mid-sequence.
- **Edit:** the two empty duplicates removed; the single occurrence
  carrying content retained. No content was deleted.
- **Status:** `FIXED`
- **Precedent:** same family as L-04, found the same way — reading the
  record rather than the code. Structural drift in the record is
  invisible to every scanner the repo has, because the scanners check
  counts and name sets, not document structure.
