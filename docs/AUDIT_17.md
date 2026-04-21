# AUDIT 17

Seventeenth audit pass. Scope: close the `[NAMED]` integration
item from AUDIT_15 § D.2 — let `term_audit/provenance.py`
`EMPIRICAL` records optionally carry a `StudyScopeAudit`
attachment.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet
designed.


## Part A — What the integration gives us

Before AUDIT_17:

- An `EMPIRICAL` provenance could declare `scope_caveat` as prose
  ("measured in lab; applied in field"). That's a human-readable
  acknowledgement that the study's scope is being stretched.
- There was no machine-readable record of *where* the stretch
  held or failed.

After AUDIT_17:

- `Provenance.scope_audit: Optional[Any]` — a hook for a
  `StudyScopeAudit` (or any equivalent structured record) to
  ride along with an empirical citation.
- `empirical()` constructor accepts `scope_audit=None` as a
  keyword arg; type is `Any` to avoid a circular import between
  `provenance` and `study_scope_audit`.
- `Provenance.has_scope_audit() -> bool` for easy detection.
- `Provenance.soft_gap() -> Optional[str]` surfaces the specific
  gap the integration is designed to catch: an `EMPIRICAL` record
  whose author acknowledged a scope stretch in `scope_caveat` but
  did not attach the machine-readable `scope_audit`.
- `coverage_report()` gains three new fields:
  `scope_audit_count`, `soft_gap_count`, `soft_gap_details`.

The attachment is **optional**. Absence does NOT break
`is_complete()` or `missing_fields()`. This is deliberate — the
AUDIT_07 Tier 1 retrofit landed 74/74 complete coverage on
existing audits; suddenly requiring a `scope_audit` on every
`EMPIRICAL` record would regress that. The soft-gap signal is
the coverage-improvement signal, not a completeness violation.


## Part B — What's load-bearing

### B.1 `soft_gap()` fires on caveat-without-audit   `[LOAD-BEARING]`

The whole point of the integration is to surface one specific
pattern: an `EMPIRICAL` citation whose author knew the scope was
being stretched (declared `scope_caveat`) but did not give the
framework a structured record of the stretch boundaries
(no `scope_audit`). `soft_gap()` catches exactly this. Tripwired.

### B.2 Attaching a scope_audit clears the gap   `[LOAD-BEARING]`

The repair pathway the soft gap points at: attach a
`StudyScopeAudit` to the provenance record. The gap then returns
None. Tripwired — a caveat-bearing record with a scope_audit
attachment is the "fixed" state.

### B.3 No regression on AUDIT_07's Tier 1 coverage   `[LOAD-BEARING]`

`tests/test_provenance_study_scope_integration.py::test_7`
explicitly runs the Tier 1 audit coverage assertions from
AUDIT_07 and confirms 0 none / 0 incomplete across money / value
/ capital. The `scope_audit` field stays `None` on all 74
existing records and none of them becomes incomplete because of
it.


## Part C — Tests

`tests/test_provenance_study_scope_integration.py` (7 cases):

1. default `scope_audit=None`; existing records stay complete
2. `empirical()` accepts and stores `scope_audit` by identity
3. `soft_gap()` returns `None` when `scope_caveat` is empty
4. **load-bearing**: `soft_gap()` fires on caveat-without-audit
5. **load-bearing**: attaching `scope_audit` clears the gap
6. `coverage_report()` surfaces `scope_audit_count` and
   `soft_gap_details` correctly
7. **load-bearing regression guard**: AUDIT_07's Tier 1 74/74
   coverage preserved

Full regression: **49/49 PASS**.


## Part D — What's NOT done

### D.1 No existing Tier 1 provenance has a scope_audit attached   `[OPEN]`

Having the attachment mechanism is not the same as using it. All
74 Tier 1 EMPIRICAL records currently leave `scope_audit=None`.
Retrofitting real `StudyScopeAudit` objects onto them (e.g.,
attaching a scope record to the Boskin Commission citation in
`money.py::calibration_exists`, or to the Fama-French citation
in `capital.py::observer_invariant`) is mechanical
per-citation work. Not done in AUDIT_17 to keep the integration
minimal; flagged as `[OPEN]`.

### D.2 No soft-gap-driven repair workflow shipped   `[NAMED]`

A natural follow-up: a script that walks every Provenance in the
tree, flags the soft gaps, and offers repair stubs
(scope_audit templates the author can fill in). Not implemented.


## Close-out

- AUDIT_15 § D.2 closed.
- Three load-bearing invariants tripwired: soft-gap firing,
  soft-gap clearing, Tier 1 no-regression.
- `coverage_report()` extended with three new reporting fields.
- One follow-up named (populate real `scope_audit` attachments on
  the existing 74 Tier 1 EMPIRICAL records).
- Regression: **49/49 PASS** (was 48/48).
