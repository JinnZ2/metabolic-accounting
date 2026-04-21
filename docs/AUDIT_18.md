# AUDIT 18

Eighteenth audit pass. Scope: extend the historical-case anchor
sets for both `money_signal/` and `investment_signal/` per the
Todo.md priority-1 case list.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet
designed.


## Part A — money_signal extensions

Four new anchor cases land in `money_signal/historical_cases.py`:

| Case | Period | Role |
| --- | --- | --- |
| **Bitcoin flash crashes** | 2013 / 2017 / 2021-22 | DIGITAL + SPECULATIVE_CLAIM; tests claim #4 and #9 |
| **Roman denarius debasement** | ~200 BCE - 270 CE | METAL substrate, century-scale slow stress |
| **Yap rai stones** | ~1400 CE - present | TRUST_LEDGER counter-example |
| **Kula ring exchange** | 1915 onward | RECIPROCITY_TOKEN counter-example (Melanesia) |

Each case carries `observed_dynamics` entries using the
qualitative `DynamicShift` enum (no fabricated floats) and
typed `Provenance` (`EMPIRICAL` with canonical literature refs
or `PLACEHOLDER` with named retirement paths). Literature anchors
include Gandal et al. 2018 + Liu-Tsyvinski-Wu 2022 (Bitcoin),
Harl 1996 + Butcher & Ponting 2014 (Roman), Friedman 1991 FRBSF
(Yap), and Malinowski 1922 (Kula).

### A.1 Tightened match criterion to honor counter-examples

Adding Yap and Kula (HEALTHY regime, high-Minsky-ratio by
form but low coupling-magnitude by damping) exposed that the
original `compare_case` match criterion was too loose:

```python
# before AUDIT_18:
predicted_n_r_high = (pred.minsky >= 1.5
                     or case.context_during.state == NEAR_COLLAPSE)
```

This flagged Yap/Kula as "predicted amplified" because their
Minsky ratio is 1.68. But their coupling magnitude is 0.13 —
the ratio is preserved but the amplitude is damped. That's the
README claim #3 signature (reciprocity damping), NOT claim #4
(speculative amplification).

After AUDIT_18:

```python
predicted_n_r_high = (
    case.context_during.state == NEAR_COLLAPSE
    or (pred.minsky >= 1.5 and pred.coupling_magnitude >= 0.3)
)
```

The magnitude filter correctly classifies:

| Case | State | Minsky | Magnitude | predicted_high? |
| --- | --- | --- | --- | --- |
| Weimar/Zimbabwe/GFC/Cyprus/Argentina/Bitcoin | NEAR_COLLAPSE | 1.73-2.42 | 0.59-0.98 | True (NEAR_COLLAPSE) |
| Roman | STRESSED | 1.74 | 0.86 | True (ratio AND magnitude) |
| **Yap / Kula** | **HEALTHY** | **1.68** | **0.13** | **False (magnitude < 0.3)** |

### A.2 Test partitioning

`tests/test_historical_cases.py` was restructured to partition
the anchor set by role:

- `NEAR_COLLAPSE_CASES` (6): Weimar, Zimbabwe, GFC, Cyprus,
  Argentina, Bitcoin
- `STRESSED_CASES` (1): Roman denarius
- `COUNTER_EXAMPLES` (2): Yap, Kula

Tests 1, 3, and 6 updated. Match count moved from 4/5 (pre-
AUDIT_18) to **8/9 with Cyprus as the documented outlier**.


## Part B — investment_signal extensions

Two new anchor cases land in `investment_signal/historical_cases.py`:

| Case | Period | Role |
| --- | --- | --- |
| **Colonial resource extraction (VOC/EIC era)** | 1602-1799 | DERIVATIVE distance + EXTRACTIVE_CLAIM; classic substrate-invisibility + reverse-causation anchor |
| **US 401(k) generational realization** | 1978-present | SHORT_CYCLE binding × GENERATIONAL money scope → liquidity illusion at scale |

### B.1 401(k) classification honesty

Initial draft included `infrastructure_depreciation_trap` among
observed failures for 401(k), but that tag describes long-binding-
in-short-scope context, the opposite of what 401(k) actually does.
The 401(k) failure is SHORT-binding (quarterly fund rhythm) in
LONG scope (40-year retirement horizon) — pure liquidity illusion.
The infrastructure-depreciation story about DB → DC pension shift
is a real adjacent phenomenon but doesn't fit the specific
framework tag. Removed; documented in the audit.

### B.2 Match count

Post-extension: framework predicted-covers-observed on **6/7
cases**. ZIRP remains the single documented outlier (same
single-case-encoding limitation documented in AUDIT_14 Part B).


## Part C — Discipline preserved

All new cases follow the honest-placeholder pattern established
in AUDIT_12 / AUDIT_14 Part B:

- No fabricated numeric C[i][j] or R[i][j] values
- Every ObservedDynamic / ObservedInvestmentFailure carries typed
  Provenance
- Every PLACEHOLDER carries a named retirement_path identifying
  the datasets/studies that would retire it
- Every case has a canonical literature reference list
- Counter-examples (Yap, Kula, Community Land Trusts) stay zero-
  or minimum-failure by design — the framework's positive cases

Full regression: **49/49 PASS**.


## Part D — What's NOT done

### D.1 Remaining Todo.md extended-case candidates   `[OPEN]`

Todo.md priority 1 listed these candidates that are NOT yet in
the anchor sets:

- "colonial resource-extraction investments" — partially addressed
  by the new COLONIAL_RESOURCE_EXTRACTION case, but the broader
  pattern (e.g., rubber/cotton/sugar plantations, King Leopold's
  Congo, post-colonial extractive concessions) could support
  multiple distinct anchors.
- Indigenous reciprocity systems beyond the Kula ring (e.g.,
  Haudenosaunee wampum, Andean ayni, potlatch) would benefit from
  their own anchors — each is a distinct TRUST_LEDGER /
  RECIPROCITY_TOKEN system with its own structural invariants.
- Pacific shell networks beyond Yap (e.g., tambu in New Britain,
  kina in New Guinea) — same framing.

Future passes can extend case-by-case following the same
discipline.

### D.2 ZIRP single-case-encoding limitation persists   `[OPEN]`

Same note as AUDIT_14 Part B. ZIRP's retail TWO_LAYER encoding
cannot simultaneously fire `liquidity_illusion` (which it does)
AND `financialized_reverse_causation` (which the Lazonick/Borio
literature documents at firm level). Decomposing ZIRP into
multiple investor-type sub-cases (retail / PE / CLO / sovereign)
is future work.


## Close-out

- Todo.md priority 1 extended-case work progressed: 4 new
  money_signal anchors + 2 new investment_signal anchors.
- Match criterion tightened (magnitude filter) to correctly
  classify TRUST_LEDGER counter-examples.
- Test partitioning (near-collapse / stressed / counter-example)
  replaces the "every case is NEAR_COLLAPSE" simplification that
  no longer holds across the extended set.
- No fabricated numerics introduced; typed Provenance on every
  observation.
- Two named follow-up items (remaining Todo.md candidates, ZIRP
  sub-case decomposition).
- Regression: **49/49 PASS**.
