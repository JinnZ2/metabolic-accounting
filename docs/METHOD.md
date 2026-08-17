# METHOD.md — the loop this repo actually runs

This repo is not organized around "features that got built." It is
organized around **claims that survived being run.** Everything else —
the audit trail, the tripwire scripts, `STATUS.md`, `legacy/` — is
machinery for one loop:

```
   hypothesize  →  run  →  result  →  falsified?  →  edit the claim
        ↑                                                    │
        └──────────  rerun  ←  search for unknowns  ←────────┘
```

The loop is the product. A claim that has been around the loop and
come out narrower is worth more than a claim that was never run. This
document exists so a future session does not have to re-derive the
discipline from scattered audit prose.

---

## Why write this down at all

Two failure modes have actually happened in this repo, both recorded:

1. **Fabricated output.** Numerical results were reported that had not
   been produced by running anything. This is why the standing rule is
   *no claim about framework behavior without a test that just produced
   it* (`STATUS.md § Test-first discipline`).
2. **Drift.** `STATUS.md` described a tree that no longer matched the
   code — `AUDIT_04` had to unwind it, and `AUDIT_05 § C` caught the
   same mode a second time. Drift is not sloppiness; it is what happens
   by default when claims and code age at different rates.

Both are loop failures. Fabrication skips **run**. Drift skips
**rerun**.

---

## The six steps, mapped onto repo machinery

### 1. Hypothesize — state the claim and tag where it came from

Write the claim so it can fail. "The coupling matrix is well-behaved"
cannot fail; "the Minsky ratio is ≥ 1 under STRESSED for every factor
module" can.

Tag its provenance immediately. `term_audit/provenance.py` carries a
five-kind taxonomy — `EMPIRICAL` / `THEORETICAL` / `DESIGN_CHOICE` /
`PLACEHOLDER` / `STIPULATIVE`. The tag is not decoration: it tells the
next reader what kind of evidence would falsify the claim. A
`PLACEHOLDER` falls to *any* real measurement; an `EMPIRICAL` claim
needs a contradicting measurement.

Equations carry the same idea in `docs/EQUATIONS.md` via
`[CORE] / [PLACEHOLDER] / [HEURISTIC] / [FRAGILE]`. Changing a formula
without updating its tag hides the scaffold→production transition — the
tag *is* the claim about maturity.

**Until it has been run, it is a hypothesis.** Say so in that language.

### 2. Run — produce the number, don't recall it

```bash
python tests/test_integration.py          # one file
for t in tests/test_*.py; do python "$t" && echo "PASS" || echo "FAIL"; done
```

Every test is a standalone stdlib script. There is no runner, no
fixtures, no `-k`. To run one case, edit the `__main__` block at the
bottom of the file.

Paste **actual stdout**. If you did not just run it, you do not have
the result — and reporting it anyway is the first failure mode above.

### 3. Result — read what actually came back

`math.inf` is a result, not an error. Irreversibility propagates as
`inf` through `required_regeneration_cost → GlucoseFlow.regeneration_required
→ metabolic_profit → Verdict`. Clamping it to a large float would be
falsifying the run to protect the claim.

An anchor that does *not* match is also a result. `money_signal`
matches 12 of 13 historical anchors; Cyprus is flagged as an outlier
rather than tuned into agreement (`tests/test_historical_cases.py`
TEST 6). The outlier is information about scope. Kept, not fixed.

### 4. Falsified? — then edit the claim, never the test

This is the step where discipline is actually spent.

**Do not weaken an assertion to make a failing test pass.** Either fix
the code, or write a *new* test expressing the new intended behavior
and leave the old test's falsification signal intact. A weakened
assertion silently converts a falsified claim into an unexamined one.

The legitimate edits are:

- **Narrow the scope.** The claim held in a smaller regime than
  asserted. This is the most common honest outcome — see
  `term_audit/study_scope_audit.py` for scope as a first-class object,
  and `term_audit/informational_cost_audit.py` for the cost of
  pretending a claim holds past its measured scope.
- **Fix the code.** The claim was right, the implementation wasn't.
- **Retire the claim.** It was wrong. Record it (step 6) — do not
  quietly delete it.

Some falsifications are *load-bearing and must stay falsified*. The
`distinction_as_coordination` counter-hypothesis is asserted-false by
`tests/test_preemption.py` test 10. If it ever flips, that is a real
finding requiring a model change plus updated audit notes — not a test
to relax.

### 5. Search for unknowns — assume drift you haven't looked for

Falsifying the claim you were thinking about is the easy half. The
repo ships three scanners for the claims you weren't:

| Scanner | Catches |
| --- | --- |
| `scripts/counts_consistency.py` | 15 load-bearing counts drifting from declared baseline |
| `scripts/name_set_consistency.py` | 3 registry name-set pairs disagreeing (bidirectional) |
| `scripts/scan_soft_gaps.py` | soft/hedged claims that never got a tripwire |

Run them. They exist because scalar counts in prose (`14 principles`,
`13 anchors`) drift silently against code, and a count in `STATUS.md`
that no longer matches the tree is a false claim regardless of intent.

Structural unknowns to probe by hand: does a module still satisfy the
invariant in **its own docstring**? (`recovery_pathways.py` did not —
its stage-ordering data violated its stated ordering rule.) Does the
file on disk have the name the tests import? (`governance_design_systems.py`
vs `_principles` — it did not.)

### 6. Rerun — the whole suite, then reconcile the record

Full suite, not the file you touched. Then update `STATUS.md` — every
numerical claim there must be reproducible by running a test *right
now*.

Then close the loop on the record itself:

- **Superseded or falsified claim** → append to `legacy/FALSIFIED.md`
  with what falsified it and what replaced it. Precedent carries: a
  future session needs to know what was already tried and why it fell,
  or it will retry it.
- **New audit** → new numbered file (`docs/AUDIT_26.md`, …). Never
  overwrite a past audit. The trail is append-only because superseded
  reasoning is evidence, not clutter.

---

## What "precedence still carries" means operationally

A falsified claim is not deleted, because the falsification is the
finding. Three things stay citable after a claim falls:

1. **The original claim** — so nobody re-proposes it as novel.
2. **What falsified it** — the test, run, or contradiction, by name.
3. **What replaced it, and how much narrower it is** — the scope
   delta is the actual knowledge gained.

`legacy/FALSIFIED.md` is that ledger. `docs/AUDIT_*.md` is the
long-form reasoning behind each entry.

**Files are not moved into `legacy/` merely for being old.** Audit
documents are cited by live code and tests — 23 of the 25 audit files
are referenced from modules or test files by path — so relocating them
would convert a working citation into a dangling one, which is the
drift mode this whole apparatus exists to prevent. `legacy/` carries
*superseded claims*, not aged files. See `legacy/README.md`.

---

## The shortest version

- Untested claim = hypothesis. Say "hypothesis."
- Don't report a number you didn't just produce.
- When it fails, edit the claim — not the assertion.
- `inf` and non-matching anchors are results.
- Look for the drift you weren't asking about; three scanners do this.
- Rerun everything, then write down what fell and what replaced it.
