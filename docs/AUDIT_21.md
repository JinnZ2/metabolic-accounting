# AUDIT 21

Twenty-first audit pass. Scope: surface the actual retrofit debt
honestly, and attach 2 more real StudyScopeAudits where the cited
methodology is public enough to ground without fabrication.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[DEMONSTRATED]` — pattern shipped on
a small set, remainder left `[OPEN]` for per-item research.


## Part A — `scripts/scan_soft_gaps.py`   `[CLOSED]`

AUDIT_17 § D.2 named a soft-gap-driven repair workflow script.
AUDIT_21 ships it.

### A.1 What it surfaces

Per-audit rows (audit_term, total provenances, complete,
scope_audits attached, soft_gap_count, tripped criteria) plus
aggregate totals. CLI invocation (`python scripts/scan_soft_gaps.py`)
prints a formatted text summary.

### A.2 The honest retrofit debt

Pre-AUDIT_21 Part A: I said "72 EMPIRICAL records without
scope_audit attachment" in AUDIT_17 § D.1. That was a pessimistic
over-count. The scanner reports the actual structural gap:

- **63 SignalScore provenance records** across 9 Tier 1 audits
  (money + 4 value sub-audits + 4 capital sub-audits)
- **63/63 complete** per `is_complete()` — AUDIT_07's discipline
  preserved
- As of the AUDIT_19 baseline: **2 scope_audits attached**
  (Boskin CPI + BoE 2014 Money Creation)
- As of the AUDIT_19 baseline: **14 soft gaps remaining** —
  EMPIRICAL records with `scope_caveat` but no `scope_audit`

14 is the real retrofit debt, not 72. Each is per-citation work.

### A.3 Tripwire

`tests/test_scan_soft_gaps.py` (5 cases) locks the 9-audit walk,
row shape consistency, aggregate correctness, the specific
retrofit-count baseline, and per-row completeness discipline.


## Part B — Two more real scope_audits (money.py → 0 soft gaps)   `[CLOSED]`

### B.1 Retrofits shipped

- **`_BALASSA_PPP_SCOPE_AUDIT`** attached to the `unit_invariant`
  score. Grounded in Balassa 1964 *JPE* + Samuelson 1964 *RES*.
- **`_FASB_ASC_820_SCOPE_AUDIT`** attached to the
  `observer_invariant` score. Grounded in FASB ASC 820 / IFRS 13
  Level 1/2/3 hierarchy.

Each populates all six layers — Instrument, Protocol,
DomainCoupling, Regime, CausalModel, ScopeBoundary — from the
published methodology. Nothing fabricated.

### B.2 Notable findings surfaced by the retrofits

The Balassa-Samuelson scope audit's `extrapolation_claims`
explicitly flags: *"downstream users often invoke
Balassa-Samuelson to argue about real purchasing power within
a country across income strata — that is out of the paper's
declared scope."* The framework's `money.py::unit_invariant`
score (0.05) extends the claim to contract-form /
counterparty / coercion-level invariance — a scope stretch the
attached scope audit now makes machine-readable.

The FASB ASC 820 scope audit's
`confounders_unmeasured` includes: *"inter-observer variance on
Level 3 valuations across independent valuation firms"* — a gap
the accounting literature has long named but the standard does
not close.

### B.3 Post-retrofit coverage

`money.py` is now fully scope-audited: 7/7 complete, 4
scope_audits attached, 0 remaining soft gaps.

Tree-wide aggregate: **4 attached / 12 remaining / 63 total**.


## Part C — What's NOT done

### C.1 12 remaining soft gaps across value.py and capital.py   `[OPEN]`

Per scanner output:

| Audit | Criteria tripped |
| --- | --- |
| value::collapsed | observer_invariant |
| value::V_A_use_value | unit_invariant, calibration_exists |
| value::V_B_exchange_value | observer_invariant |
| value::V_C_substrate_value | calibration_exists, observer_invariant |
| capital::collapsed | observer_invariant |
| capital::K_A_productive | calibration_exists, observer_invariant |
| capital::K_B_financial | calibration_exists, observer_invariant |
| capital::K_C_institutional | calibration_exists |

Each requires per-citation methodology reading. Not shipped in
AUDIT_21 to keep scope tight. The scanner now makes the list
explicit and the progress auditable.

### C.2 Empirical K-value extraction from PLACEHOLDER retirement paths   `[OPEN]`

Not code work. The retirement_path entries name the datasets
(BCRA, FRED, Preqin, ILPA, DOL Form 5500, etc.) honestly; the
extraction is external research.


## Close-out

- AUDIT_17 § D.2 closed: soft-gap scanner shipped.
- 14-gap pre-AUDIT_21 baseline reduced to 12 via 2 new retrofits.
- money.py is now the reference fully-scope-audited Tier 1 audit;
  value and capital follow the same pattern when per-citation
  research is done.
- No regression on AUDIT_07's 63/63 Tier 1 SignalScore
  completeness.
- Regression: **51/51 PASS**.
