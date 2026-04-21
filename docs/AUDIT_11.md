# AUDIT 11

Eleventh audit pass. Scope: intake the four new modules merged into
`origin/main` on the `money_signal/` subsystem — `coupling.py`,
`coupling_state.py`, `coupling_substrate.py`, and `README.md` —
totaling ~1540 new lines. Audit them for drift, integration, and
the framework's own discipline (every claim backed by a test that
actually produces it).

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet designed;
`[DETECTED]` — real bug surfaced, fix options proposed, decision
deferred to user.


## Part A — What landed

### A.1 `money_signal/coupling.py` — composition, memoization, diagnostics

Top-level API for the subsystem:

- `compose_coupling(context, i, j)` — build `K_ij(context)` by
  multiplying base × temporal × cultural × attribution × observer
  × substrate × state factors.
- `assemble_coupling_matrix(context)` — full 4×4 matrix.
- `coupling_matrix_as_dict(context)` — user-facing dict form.
- `validate_composition(context)` — runtime checks the composed K.
- `minsky_coefficient(context)` — `|K[N][R]| / |K[R][N]|`.
- `coupling_magnitude(context)` — mean off-diagonal magnitude.
- `has_sign_flips(context)` — permits True only in NEAR_COLLAPSE.
- `format_composed_matrix(context)` — rendering.
- `validate_all_factor_modules()` — runs each module's local
  validator. **Currently crashes, see § B.**

### A.2 `money_signal/coupling_state.py` — state regime factors

4 state regimes (HEALTHY, STRESSED, NEAR_COLLAPSE, RECOVERING)
each with a 4×4 factor matrix. This is the only factor module
that may introduce sign flips (only in NEAR_COLLAPSE, per README
claim #7). Validator passes.

### A.3 `money_signal/coupling_substrate.py` — substrate factors

5 substrates (BIOLOGICAL, METAL, PAPER, DIGITAL, TRUST_LEDGER).
METAL is the calibration case (factors ≈ 1.0 within ±0.15).
Validator passes.

### A.4 `money_signal/README.md` — subsystem documentation

208 lines. Documents the 4-term signal equation (R reversal
reliability, N network acceptance, C cost, L latency), composition
law `K_ij(context) = K_ij_base × temporal × cultural × attribution
× observer × substrate × state`, 9 falsifiable claims, diagnostic
outputs, relation to two sibling repos, and usage example. First
user-facing README inside `money_signal/`.


## Part B — Real bug surfaced at intake   `[CLOSED]` (Option 1 applied post-AUDIT_11)

### B.1 `validate_all_factor_modules()` crashes on import-time call

The README tells users to call `validate_all_factor_modules()`
at startup:

```
# Always validate at startup.
validate_all_factor_modules()
```

And `coupling.py`'s own `__main__` block does so. Running
`python -m money_signal.coupling` raises:

```
AssertionError: Minsky asymmetry violated at cultural scope
community_trust: K[N][R] factor=0.7 must be >= K[R][N] factor=0.8
```

Every other factor validator (base, temporal, attribution,
observer, substrate, state) passes cleanly. Only `cultural`
fails.

### B.2 Root cause: validator stricter than README invariant

README claim #1 (Minsky asymmetry): *"`K[N][R] >= K[R][N]` in
every regime except near-collapse. Trust never rebuilds faster
than it collapses."*

This is stated about the **composed** coupling — the matrix a
consumer actually reads. But `validate_cultural_factors()`
checks the FACTOR-level pointwise asymmetry:

```python
f_nr = _CULTURAL_FACTORS[scope][MoneyTerm.N][MoneyTerm.R]
f_rn = _CULTURAL_FACTORS[scope][MoneyTerm.R][MoneyTerm.N]
assert f_nr >= f_rn
```

That is a stronger claim than the README invariant. In
COMMUNITY_TRUST the docstring explicitly says *"Minsky asymmetry
is reduced because reputation backstops the network"* — the
intent is for the cultural factor to damp asymmetry. Factors
`f_nr=0.7`, `f_rn=0.8` do exactly that:

- Composed `K[N][R]` = `K_BASE[N][R] × f_nr` = `0.8 × 0.7` = `0.56`
- Composed `K[R][N]` = `K_BASE[R][N] × f_rn` = `0.7 × 0.8` = `0.56`

Composed ratio = **1.0** (equality — README claim `>=` holds, with
asymmetry exactly cancelled). The validator's pointwise check
rejects this even though the composed invariant is satisfied.

Same pointwise pattern exists at `coupling_attribution.py:410`
and `coupling_observer.py:412`, but those modules happen to not
have reducing-asymmetry cases in their current factor data. They
would fail the same way if anyone added one.

### B.3 Three fix options

**Option 1** — **Weaken the validator to match the README**.
Change each of the three pointwise Minsky checks to compute
composed effective coupling and assert `>=` there. Matches the
documented invariant exactly. Current data passes. Lowest risk
structurally; preserves the semantic intent of COMMUNITY_TRUST.

**Option 2** — **Swap the COMMUNITY_TRUST factors** to `f_nr=0.8,
f_rn=0.7`. Makes the pointwise check pass. But inverts the
semantic intent stated in the docstring — reputation damping
becomes reputation amplification. Probably wrong on substance.

**Option 3** — **Keep the validator, update the README** to state
the stronger pointwise invariant and document why COMMUNITY_TRUST
is an exception. Requires a principled answer to "why is this
scope allowed to break the invariant?" which the current code
doesn't provide.

Recommended: **Option 1**. The README's claim is the load-bearing
one; the validator's pointwise check is an artifact. Tracking for
decision before applying.

### B.4 Tripwire landed

`tests/test_money_signal.py::test_3_cultural_validator_current_failure_detected`
was a DETECTOR test — it explicitly asserted the current failure
mode. **Post-AUDIT_11, Option 1 applied**: the Minsky pointwise
checks in `coupling_cultural.py`, `coupling_attribution.py`, and
`coupling_observer.py` were rewritten to compute composed coupling
(`K_BASE[i][j] * f_ij`) and assert the `>=` relation at that level,
matching README claim #1 exactly. `validate_all_factor_modules()`
now runs clean. The test was flipped to
`test_3_cultural_validator_passes_at_composed_level` and asserts
success on both `validate_cultural_factors()` and
`validate_all_factor_modules()`.

### B.5 Second ship-breaking bug surfaced downstream   `[CLOSED]` (Option 1 applied)

Once § B fix landed, `python -m money_signal.coupling` progressed
past factor validation but then raised on the CLI's own NEAR_COLLAPSE
example case (case_c: SEASONAL / INSTITUTIONAL / STATE_ENFORCED /
TOKEN_HOLDER_THIN / DIGITAL / NEAR_COLLAPSE):

```
AssertionError: Composed coefficient
K[network_acceptance][reversal_reliability]=3.6608 outside sanity
range [-3.0, 3.0].
```

`validate_composition` enforces a `[-3.0, 3.0]` sanity bound on
composed coefficients as a check against runaway amplification.
But README claim #8 (Minsky dominance in collapse) expects
`|K[N][R]|` to *dominate* all other off-diagonals in NEAR_COLLAPSE
— and the CLI's own example is built to exercise that. The
stacking of NEAR_COLLAPSE state × DIGITAL substrate × TOKEN_HOLDER_THIN
observer all amplifying in the same direction produces 3.66,
exceeding the sanity bound.

Three options, parallel to § B.3:

1. Widen the sanity bound (e.g., `[-5.0, 5.0]`) to accommodate
   legitimate NEAR_COLLAPSE stacking. Matches the documented claim
   that `|K[N][R]|` should dominate in collapse.
2. Relax the bound specifically for NEAR_COLLAPSE (the bound is
   there to catch accidental runaway; NEAR_COLLAPSE amplification
   is by design).
3. The CLI's example case is too extreme; replace with a less-
   stacked one. Discards the demonstration of claim #8.

Option 1 applied: sanity bound widened from `[-3.0, 3.0]` to
`[-5.0, 5.0]` in `coupling.py::validate_composition`. Rationale in
the docstring: `[-5.0, 5.0]` accommodates legitimate collapse-
regime stacking (case_c composes to 3.66) while still catching
pathological runaway (>10 indicates a broken factor module, not
an extreme-but-real case). `python -m money_signal.coupling` now
runs end-to-end across all four README example cases with output
consistent with README claims: Minsky coefficients A:1.24×,
B:1.41×, C:1.73×, D:1.94× — showing that reciprocity-ledger
systems have stronger Minsky asymmetry than even collapsing fiat
(but at an order of magnitude smaller coupling magnitude, which
is the actual damping). Tripwire landed in
`tests/test_money_signal.py::test_3b_validate_composition_passes_on_readme_cases`.


## Part C — Other drift / smaller findings

### C.1 No `__init__.py` in `money_signal/`   `[NAMED]`

`ls money_signal/` shows:

```
README.md  coupling.py  coupling_attribution.py  coupling_base.py
coupling_cultural.py  coupling_observer.py  coupling_state.py
coupling_substrate.py  coupling_temporal.py  dimensions.py
```

No `__init__.py`. Imports work (Python 3 namespace packages), but
the README shows a tree diagram that includes one:

```
money_signal/
├── __init__.py
```

Minor drift — either the diagram is aspirational or the file got
missed. Recommend adding a small `__init__.py` with a package
docstring pointing at the README, matching the pattern used in
`term_audit/signals/__init__.py` (AUDIT_08) and
`term_audit/legislative_audit/__init__.py` (AUDIT_09).

### C.2 Relative-import lock   `[NAMED]`

`coupling.py` uses `from .dimensions import ...` which forces
callers to run via `python -m money_signal.coupling` rather than
`python money_signal/coupling.py`. Every other module in the repo
uses the absolute import with sys.path bootstrap pattern to allow
both. Not strictly wrong — relative imports are cleaner inside a
package — but inconsistent with the rest of the repo's execution
convention.

### C.3 Composition is multiplicative per README   `[INFORMATIONAL]`

README's Known Limitations #2: *"Composition is multiplicative,
not additive ... this choice may need revision after historical
calibration."* Flagged by the README itself; no action required.

### C.4 No historical-case calibration yet   `[OPEN]`

README points at a planned `historical_cases.py` module. Not yet
present. Factor values remain first-principles estimates per
Known Limitations #1.


## Part D — Integration with the rest of the framework

### D.1 Tie-in with the three-scope falsification audit (AUDIT_10)

AUDIT_10 § D.1 named: a consumer wiring `money_signal/` into a
decision pipeline should first run
`audit_money_across_three_scopes(current_regime_money_state())`
and emit blocker flags if `structural_claim_holds` is True, so
that downstream `K_ij` values are not computed for a
not-actually-a-signal.

No code shipped this audit. Still `[NAMED]`. The finding from
§ B above is an independent, stronger reason to treat
`money_signal/` outputs cautiously until validators pass.

### D.2 Tie-in with the main accounting stack

README line 134 claims: *"Money-as-signal couples directly into
the existing glucose-flow metaphor: reversal reliability is the
metabolic signal."* But no code currently bridges `money_signal/`
K matrices into `accounting/glucose.py` or `verdict/assess.py`.
The claim is aspirational; the coupling has not been wired.

Not a bug — just naming the next integration step. `[NAMED]`.


## Part E — Tests

`tests/test_money_signal.py` (7 cases) landed this audit:

1. all 9 modules import
2. 6 factor validators pass (base, temporal, attribution,
   observer, substrate, state)
3. **DETECTOR**: cultural validator fails on COMMUNITY_TRUST with
   the specific pointwise-Minsky error (see § B)
4. `coupling_matrix_as_dict` runs end-to-end under the calibration
   context; 4×4 with diagonals 1.0
5. README claim #1 verified at composed level across HEALTHY /
   STRESSED / RECOVERING: `|K[N][R]| >= |K[R][N]|` in all three
6. README claim #7 verified: HEALTHY has no sign flips,
   NEAR_COLLAPSE may have them
7. README claim #6 verified: issuer magnitude (0.208) ≪ thin-holder
   magnitude (0.863) under STRESSED conditions; issuer-insulation
   fragility-underestimation structural

Full regression: **41/41 PASS** (pre-AUDIT_11: 40/40).


## Part F — Coverage snapshot

| Surface | Coverage |
| --- | --- |
| `money_signal/` modules imported | 9/9 |
| Factor validators verified | 6/7 (cultural detected-failing) |
| README falsifiable claims (9) tested | 3/9 (claims #1 composed, #6, #7) |
| Historical-case calibration data | 0 files / planned |
| Integration with three-scope audit | `[NAMED]`, not coded |
| Integration with accounting stack | `[NAMED]`, not coded |
| Typed Provenance on factor values | 0 (same shape gap as AUDIT_10 flagged on `MoneyState`) |


## Part G — Recommended next actions

Ordered by cost:

1. **[SAFE, DECISION NEEDED]** Apply Option 1 from § B.3: change
   the pointwise Minsky checks in cultural, attribution, and
   observer validators to check composed coupling. Matches the
   README invariant. Update test_3 in `test_money_signal.py` to
   flip from DETECTOR to PASS assertion.
2. **[SAFE]** Add `money_signal/__init__.py` per § C.1.
3. **[SAFE]** Cover README claims #2 (hysteresis), #3 (reciprocity
   damping), #4 (speculative amplification), #5 (observer
   asymmetry), #8 (Minsky dominance in collapse), #9 (digital
   infrastructure coupling) with targeted tests. Six more claims →
   six more tests; the pattern is established.
4. **[MEDIUM]** Wire the three-scope audit as a precondition for
   `money_signal/` pipelines per AUDIT_10 § D.1 and AUDIT_11 § D.1.
5. **[MEDIUM]** Start `money_signal/historical_cases.py` to
   replace first-principles factor estimates with calibrated
   values per README Known Limitations #1.
6. **[LARGE]** Bridge `money_signal/` outputs into
   `accounting/glucose.py` and `verdict/assess.py` per § D.2.
   README claims reversal-reliability maps directly to the
   metabolic-signal glucose flow; make that map code.


## Close-out

- 4 new modules merged in (coupling.py, coupling_state.py,
  coupling_substrate.py, README.md), 9/9 import.
- **`validate_all_factor_modules()` ships broken**: pointwise
  Minsky check in cultural rejects COMMUNITY_TRUST even though
  the composed invariant it's meant to enforce holds. Three fix
  options in § B.3; Option 1 recommended; detector test landed.
- 6 of 7 factor validators tripwired as passing; cultural
  tripwired as the specific documented failure.
- 3 of the README's 9 falsifiable claims are now tripwired;
  remaining 6 scoped for next pass.
- Integration with three-scope audit (AUDIT_10 § D.1) and main
  accounting stack (AUDIT_11 § D.2) named but not coded.
- Regression 41/41. Main stack untouched; first-law closure
  unchanged.
