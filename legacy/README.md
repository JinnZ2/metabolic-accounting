# legacy/ — the precedent shelf

This directory holds **claims that no longer hold**, kept because the
falsification is itself a finding. It is the storage half of the loop
described in `docs/METHOD.md`.

The ledger is `FALSIFIED.md`.

## What goes here

A claim that was stated, run, and either falsified outright or narrowed
enough that its original form is no longer true. Each entry records
four things:

1. the claim as originally made,
2. what falsified it — the test, run, or contradiction, by name,
3. the edit that followed,
4. its status now (`SUPERSEDED`, `FIXED`, `OPEN`, or `STANDING`).

`STANDING` is the unusual one: a claim asserted *false* on purpose,
with a tripwire keeping it false. If it flips, that is a finding, not a
test to relax.

## What does not go here

**Files are not moved here for being old.** That was the obvious
reading of "put the legacy files in a legacy folder," and it was
checked before being rejected:

- 23 of the 25 `docs/AUDIT_*.md` files are cited **by path** from live
  modules and tests — `term_audit/morphism_graph.py`,
  `money_signal/accounting_bridge.py`, `scripts/counts_consistency.py`,
  and roughly twenty test files among them. Relocating an audit turns
  every one of those citations into a dangling pointer. That is exactly
  the drift mode `AUDIT_04` had to unwind and `AUDIT_05 § C` caught a
  second time.
- The remaining two (`AUDIT_02`, `AUDIT_03`) are uncited but sit inside
  a contiguous `01..25` sequence that `README.md` and `CLAUDE.md` send
  readers into. Pulling two files out leaves gaps in a sequence people
  browse, and buys nothing — the audit trail is *already* an
  append-only archive.
- No dead modules were found. Every `legacy` marker in the Python
  source (`accounting/glucose.py`, `distributional/access.py`,
  `cascade/detector.py`) marks a **live backward-compatibility path**
  with callers and tests, not an abandoned file.

So: superseded *claims* move here. Aged *files* stay where their
citations point. The audit trail is the archive; this is the index of
what it retracted.

## How to add an entry

Append to `FALSIFIED.md` — do not renumber or rewrite existing rows.
Same append-only rule as `docs/AUDIT_*.md`, for the same reason: a
retraction that can itself be silently retracted is not a record.
