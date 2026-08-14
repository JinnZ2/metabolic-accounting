# AUDIT_26.md — method documentation + legacy precedent shelf

Date: 2026-08-14.

Purpose: write down the falsification loop the repo has been running
implicitly, build the shelf where superseded claims live, and check the
"move legacy files into a legacy folder" hypothesis before acting on it.

Baseline at start: **55/55 test files passing** (`for t in tests/test_*.py;
do python "$t"; done`). Baseline unchanged at end.


## Part A — the hypothesis that got falsified

**Hypothesis.** There is an accumulation of aged files in this repo that
can be relocated into `legacy/` to tidy the tree, with precedent
preserved by the move rather than by deletion.

**Run.** Three checks:

1. **Citation sweep.** For each `AUDIT_NN`, count references from
   non-audit files:
   ```
   grep -rln "AUDIT_$n" --include=*.py --include=*.md . | grep -v '^./docs/AUDIT_'
   ```
2. **Dead-module sweep.** Every `.py` outside `tests/` listed and
   checked for importers; every `legacy`/`deprecated`/`obsolete` marker
   in source read in context.
3. **Build-artifact sweep.** `git ls-files | grep -c pycache`.

**Result — falsified.**

| Check | Finding |
| --- | --- |
| Citations | **23 of 25** audit files are cited *by path* from live modules and tests. `AUDIT_07` alone is referenced by 20 files, including `term_audit/morphism_graph.py`, `term_audit/schema.py`, `money_signal/accounting_bridge.py`, `scripts/counts_consistency.py`, and 9 test files. |
| Dead modules | **None.** Every `legacy` marker in source marks a live backward-compatibility path with callers and tests — `accounting/glucose.py` (regen registry wrapper), `distributional/access.py` (scalar cohort path), `cascade/detector.py` (global `HIGH_IS_BAD` fallback). |
| Artifacts | **0** committed `__pycache__` entries; `.gitignore` already covers them. |

Moving audit files would convert ~100 working citations into dangling
pointers — the precise drift mode `AUDIT_04` had to unwind and
`AUDIT_05 § C` caught a second time. The only two uncited audits
(`AUDIT_02`, `AUDIT_03`) sit inside a contiguous `01..25` sequence that
`README.md` and `CLAUDE.md` route readers into; extracting them leaves
gaps in a browsed sequence and buys nothing, since the audit trail is
already an append-only archive.

**Edited claim.** `legacy/` carries *superseded claims*, not aged files.
The tidying value was never in moving documents — it was in the fact
that no single place answered *"what did we already try, and why did it
fall?"* That question previously required reading 238 KB across 25
audits plus a 45 KB `STATUS.md`.


## Part B — `legacy/FALSIFIED.md`   `[NEW]`

The precedent ledger. **13 entries** (`L-01` … `L-13`), each recording
the claim as made, what falsified it, the edit that followed, and
current status under a four-term vocabulary:

- `FIXED` — claim right, implementation wrong; code changed
- `SUPERSEDED` — claim wrong or too broad; claim changed
- `OPEN` — falsified, replacement not built
- `STANDING` — asserted false on purpose, tripwired to stay false

Reconstructed from `AUDIT_04`, `05 § C`, `06 § A.1`, `07`, `11 § B`, the
`STATUS.md` bug sections, and direct runs. Cited commit hashes
(`8145548`, `4ea0476`) were verified to exist and to carry corroborating
messages.

Entries worth carrying forward regardless of what you are working on:

- **`L-04` — the drift mode has now recurred three times.** `AUDIT_04`
  unwound it, `AUDIT_05 § C` caught it again, and the AUDIT_23/24
  scanners were built to automate catching it. Assume it is happening.
- **`L-11` — Cyprus stays an outlier.** 12/13 anchors match; the
  expected distribution was written into the test *with Cyprus named*
  rather than tuning until it agreed. The outlier is the asset.
- **`L-12` — `distinction_as_coordination` must stay falsified.** If it
  flips, that is a finding requiring a model change plus updated audit
  notes; it is not an assertion to relax.
- **`L-07` — check modules against their own docstring invariants.**
  Two separate `recovery_pathways.py` findings came from that one move.


## Part C — `docs/METHOD.md`   `[NEW]`

The loop, written down: hypothesize → run → result → falsified? → edit
the claim → search for unknowns → rerun.

Each step is mapped onto machinery that already exists rather than
described abstractly — provenance kinds and equation tags at
*hypothesize*; standalone stdlib test scripts at *run*; `math.inf` and
non-matching anchors as legitimate *results*; the never-weaken-an-
assertion rule at *edit*; the three scanners (`counts_consistency`,
`name_set_consistency`, `scan_soft_gaps`) at *search for unknowns*; full
suite plus record reconciliation at *rerun*.

It opens with why it exists: the two failure modes that have actually
occurred here. Fabricated output skips **run**. Drift skips **rerun**.


## Part D — drift caught this pass

**`STATUS.md` structural drift.** The heading
`## AUDIT_14 — Part B (E.2): investment_signal/historical_cases.py`
appeared **three times**. Two occurrences (then at lines 516 and 756)
were empty orphan stubs carrying no body — one of them wedging the
unrelated `AUDIT_25` section into the middle of the AUDIT_14 sequence.

Fix: the two empty duplicates removed, the single content-carrying
occurrence retained. Diff is **4 deletions, 0 insertions, no content
lost**. Logged as `L-13`.

Note the gap this exposes: **no scanner in the repo could have caught
it.** `counts_consistency.py` checks scalars, `name_set_consistency.py`
checks set equality, `scan_soft_gaps.py` checks hedged claims — none
inspects document structure. Found by reading the record rather than
the code, same as `L-04`.


## Part E — verification

- Full suite re-run after all edits: **55/55 passing**.
- `scripts/counts_consistency.py`, `scripts/name_set_consistency.py`,
  `scripts/scan_soft_gaps.py` re-run; unchanged from baseline.
- No code touched this pass. Changes are `docs/METHOD.md` `[NEW]`,
  `legacy/README.md` `[NEW]`, `legacy/FALSIFIED.md` `[NEW]`,
  `docs/AUDIT_26.md` `[NEW]`, plus the `STATUS.md` deletion and
  navigation entries in `CLAUDE.md`.


## Part F — named, not done

- **`D.1`** A document-structure tripwire (duplicate headings, orphan
  sections in `STATUS.md` / `docs/*.md`) would close the Part D gap.
  Cheap: parse headings, assert uniqueness, assert each has a body.
- **`D.2`** `legacy/FALSIFIED.md` is currently hand-maintained. Nothing
  enforces that a falsified claim gets an entry. A tripwire asserting
  every `Bug N` in `STATUS.md` has a corresponding `L-NN` row would make
  the ledger self-checking.
- **`D.3`** `AUDIT_04` Bugs 2 and 3 remain open through this audit
  (`L-03`). Unchanged scope; noted so the count does not drift.
