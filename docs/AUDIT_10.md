# AUDIT 10

Tenth audit pass. Scope: intake a user-supplied module specifying a
three-scope falsification audit for money (flow-system / community-
organism / civilization-lube), clean the chat-paste damage, install
at the declared path, audit it against the rest of the framework,
and cross-reference to the `money_signal/` subsystem merged in from
`origin/main` in the same intake cycle.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet designed;
`[PARTIALLY ADDRESSED]` — a named gap has a related but non-
identical module landing against it.


## Part A — Merge from main

`origin/main` shipped a new top-level folder `money_signal/` (6
files, ~2100 lines) between AUDIT_09 and AUDIT_10:

- `money_signal/dimensions.py` — `MoneyTerm`, `TemporalScope`,
  `CulturalScope`, `AttributedValue`, `ObserverPosition`,
  `Substrate`, `StateRegime`, `DimensionalContext`.
- `money_signal/coupling_base.py` — base coupling matrix `K_ij`
  between the four money-equation terms. Asymmetric (Minsky-style:
  trust collapses faster than it rebuilds).
- `money_signal/coupling_temporal.py`
- `money_signal/coupling_cultural.py`
- `money_signal/coupling_attribution.py`
- `money_signal/coupling_observer.py`

This is a *model* of how money-as-signal couples across dimensions
when assumed to be a signal. It is distinct from the three-scope
audit, which asks whether money qualifies as a signal in the first
place. The two are complementary:

- `money_signal/` — **given** you're using money as a signal, here's
  how it couples across temporal / cultural / attributional /
  observer axes.
- `three_scope_falsification` — **first**, does money qualify as a
  signal at all in the marketed scopes (flow-system, community-
  organism, civilization-lube)?

Audit-ordering implication: a consumer wiring `money_signal/` into a
decision pipeline should first check the three-scope verdict; if
every scope is falsified, the coupling matrix is computing couplings
for a signal that isn't one. See § D.1 below for the structural-
integration path.


## Part B — Three-scope module intake

### B.1 Path and structure   `[CLOSED]`

Installed at the declared path:

- `term_audit/audits/money_three_scope_falsification.py` (~490
  lines) — schema + audit logic + CLI.
- `tests/test_money_three_scope_falsification.py` (7 cases) —
  extracted from the module's own in-file tests per its comment
  (*"move to tests/test_money_three_scope_falsification.py when
  pasting into the repo"*).

sys.path bootstrap added for consistency with the rest of
`term_audit/audits/`.

### B.2 Chat-paste damage caught at intake   `[CLOSED]`

Repo has `scripts/fix_pasted_file.py` exactly for this failure
mode. The supplied paste carried:

- Smart-quote substitutions (`"`, `"`, `'`, `'` → ASCII)
- `from **future** import annotations` → `from __future__ import
  annotations`
- `if **name** == "**main**":` → `if __name__ == "__main__":`
- `t.**name**` → `t.__name__`
- Markdown-style bolding (`**text**`) leaked into identifier
  positions in several places

Cleaned during intake; `ast.parse` verified before commit.

### B.3 Lite / real adapter flag mismatch   `[CLOSED]`

The spec's `AssumptionValidatorFlagLite` claimed "minimal surface
matching ... `AssumptionValidatorFlag`." But the real adapter
surface differs materially:

| Lite | Real |
| --- | --- |
| `source: str` | `source_audit: str` |
| `reason: str` | `message: str` |
| `severity: str` (`"info"`/`"warning"`/`"blocker"`) | `severity: float` (0.0–1.0) |
| — | `failure_mode: str` (which signal criterion) |

Semantic mapping is clean; field names and severity types are not.
A naive `AssumptionValidatorFlag(**asdict(lite))` would
`TypeError`.

Added `to_real_flag(lite, failure_mode=...)` bridge:

- `lite.source` → `real.source_audit`
- `lite.reason` → `real.message`
- `lite.severity` → `real.severity` via `_SEVERITY_FLOAT`
  (`info`=0.1, `warning`=0.5, `blocker`=1.0)
- `failure_mode` supplied by caller.

Test 6 locks the bridge: 3 blocker-severity lite flags map to 3
real flags with `severity == 1.0`.

### B.4 Tripwires landed

`tests/test_money_three_scope_falsification.py`:

1. every scope fails under current regime (4/4 + 4/4 + 4/4 invariant
   failures)
2. **LOAD-BEARING: `structural_claim_holds=True` under the current
   regime.** If this flips under honest observation of
   `current_regime_money_state()`, that is a real finding — update
   the state flags AND the audit notes together.
3. falsification hook works (all 12 flags `True` → 3/3 scopes
   survive → claim falsified — confirms the argument *is* falsifiable,
   not tautological)
4. partial rescue: flow-system flags `True` only → flow survives,
   others falsified
5. assumption flags emit one blocker per failed scope with correct
   source tags
6. lite → real adapter bridge (§ B.3)
7. control-vs-measurement contradiction surfaces in ≥2 scopes
   (`endogenous_regeneration=False` AND `no_unilateral_rewrite=False`
   are simultaneously failing — the spec's "ruler and hand moving
   the ruler" claim visible in the verdict structure)


## Part C — Relationship to existing Tier 1 money work

### C.1 `term_audit/audits/money.py` (the 7-criterion audit)

Orthogonal and complementary:

| | `money.py` | `money_three_scope_falsification.py` |
| --- | --- | --- |
| Axis | 7 information-theoretic signal criteria | 3 context scopes × 4 invariants each |
| Output | Scores 0.0–1.0 per criterion, `is_signal` bool at 5/7 | Boolean `scope_claim_survives` per scope, `structural_claim_holds` overall |
| Provenance (AUDIT_07) | 7/7 complete (4 empirical, 3 theoretical) | 0/12 typed `Provenance`; evidence is free-form strings (§ D.2) |
| Abstraction | what money IS (as a would-be signal) | what money is CLAIMED TO DO (in three marketed contexts) |

Both converge: 0/7 criteria passed → not a signal; 0/12 invariants
held → fails in every marketed scope. The same conclusion reached
from two independent starting points strengthens the Tier-1
inheritance argument AUDIT_07 relies on.

### C.2 AUDIT_07 § C.4 — money four-function decomposition status   `[PARTIALLY ADDRESSED]`

AUDIT_07 Part C.4 named: *"Money four-function decomposition (M_A
medium-of-exchange / M_B store-of-value / M_C unit-of-account / M_D
standard-of-deferred-payment) still not audited; money.py remains
structurally asymmetric with value.py / capital.py."*

This module adds a *different* decomposition — not the classical
four-function one, but a three-scope one (flow / community / lube).
It is structurally parallel to V_A/V_B/V_C and K_A/K_B/K_C in that
it audits money across multiple framings. It does not replace the
classical four-function audit; it audits a different claim.

Updated status:

- **M_A/M_B/M_C/M_D classical decomposition**: still `[OPEN]`.
- **Scope-framing decomposition (flow/community/lube)**: `[CLOSED]`
  via this module.

Both decompositions are valid audits of different claims; neither
closes the other. Shipping both is consistent with the framework's
discipline of separating what are actually different measurements.


## Part D — Architectural observations

### D.1 Integration between `money_signal/` and this audit   `[NAMED]`

`money_signal/` computes coupling coefficients `K_ij` under the
assumption that money functions as a signal. This module determines
whether that assumption holds. A natural integration:

- A `money_signal` pipeline should invoke
  `audit_money_across_three_scopes(current_regime_money_state())`
  at its entry point.
- If `structural_claim_holds` is `True` (i.e. all three scopes
  falsified), the pipeline should emit the three blocker
  `AssumptionValidatorFlag`s upstream before any `K_ij` computation.
- Downstream consumers of `K_ij` values then know the coupling
  matrix is modeling a not-actually-a-signal.

No code shipped for this integration in AUDIT_10; naming the
interface as the natural next step.

### D.2 Provenance on `MoneyState` flags and invariant evidence   `[OPEN]`

The module ships provenance as `Dict[str, str]` mapping each
`MoneyState` field to a free-form string (e.g., `"observable: CPI,
purchasing power series"`). This is not the typed `Provenance`
taxonomy from AUDIT_07 (EMPIRICAL / THEORETICAL / DESIGN_CHOICE /
PLACEHOLDER / STIPULATIVE). The invariant evidence strings
(returned by the `check` lambdas) are also untyped.

Retrofit path parallel to the Tier 1 retrofit AUDIT_07 landed:

- Convert `provenance: Dict[str, str]` to `Dict[str, Provenance]`.
- The `"observable: CPI"` style naturally maps to `empirical(...)`
  with `source_refs` naming the specific series.
- The structural-argument invariant evidence (e.g. *"the same dollar
  is survival to one observer, optionality to another"*) maps to
  `theoretical(...)` with a `falsification_test` — which is already
  implicit in the module's `test_3` (flip the flag and observe).

Scoped for a future audit pass; deferring here to keep the intake
minimal and preserve the module as the user specified it.

### D.3 `Scope` enum unification   `[NAMED]`

The `Scope` enum here (FLOW_SYSTEM / COMMUNITY_ORGANISM /
CIVILIZATION_LUBE) is a third axis alongside:

- `term_audit/legislative_audit/first_principles_legislative_audit.py::EnvironmentType`
  (BUFFERED_STABLE / THIN_BUFFER / CONSTRAINED / AUSTERE / COLLAPSE)
- `term_audit/signals/routing_around_detection.py::EnvironmentType`
  (BUFFERED / THIN_BUFFER / CONSTRAINED / COLLAPSE_RECOVERY)

These are three different axes — they should stay distinct. But
AUDIT_09 § D.2 already flagged the divergence between the two
`EnvironmentType` enums; this audit does not add a new unification
target, just notes that the three axes are coherently orthogonal.


## Part E — Coverage snapshot

New surface added this audit:

| Surface | Total | Complete | Notes |
| --- | --- | --- | --- |
| Three-scope audit schema | 4 enums + 6 dataclasses | all | — |
| Scope invariants | 12 (4 per scope × 3) | 12/12 | each returns (hold, evidence) |
| Falsifiable structural claim | 1 | tripwired | test 2 |
| Lite → real adapter bridge | 1 | 1/1 | `to_real_flag()` |
| Typed provenance on MoneyState | 12 | 0/12 | untyped dict, deferred (§ D.2) |
| Typed provenance on scope rationales | 3 | 0/3 | untyped, deferred |


## Part F — Recommended next actions

Ordered by cost:

1. **[SAFE]** Apply AUDIT_07 provenance pattern to `MoneyState.provenance`
   and scope rationales per § D.2. Mechanical retrofit.
2. **[MEDIUM]** Wire `audit_money_across_three_scopes` as a
   precondition in `money_signal/` pipelines per § D.1. Small
   helper module or a decorator on the pipeline entry function.
3. **[MEDIUM]** Add the classical four-function decomposition
   (M_A / M_B / M_C / M_D) per AUDIT_07 § C.4 now that the
   three-scope decomposition establishes the "money is reaudited
   at multiple framings" pattern.
4. **[LARGE]** Convert the `MoneyState` observable flags to
   evidence-backed values pulled from real empirical series (BLS
   CPI, Fed M2, GDP deflator, FRB credit-creation data). Would
   transform the audit from structural-claim into an automatable
   quarterly check.


## Part G — Load-bearing tripwires summary

This audit added the structural-claim tripwire to the list AUDIT_07
and AUDIT_08 began:

| Tripwire | Module | Load-bearing claim |
| --- | --- | --- |
| V_B → V_C negative | value.py | exchange-value draws down substrate-value |
| K_B → K_A negative | capital.py | financial growth is substrate extraction |
| K_B → K_C negative | capital.py | financialization crowds out institutional capacity |
| preempt #10 falsified | `counter_hypotheses.py` | `distinction_as_coordination` stays falsified at ≥2% margin |
| E_X selection inversion | `expertise_x_cross_domain_closure.py` | rural high-E_X > credentialed specialist under constraint |
| bridge audit contradicts purpose | `legislative_audit/` | rule causes the harm it was meant to prevent |
| Good Samaritan chilling effect | `legislative_audit/` | transmission_effect.discourages_transmission holds |
| **three-scope structural claim** | **this module** | **money fails as a signal in every marketed scope** |

If any of these regresses, the framework has lost a structural
argument — the test failure is a real finding, not a bug. Keep the
error messages verbose so the discovery is visible.


## Close-out

- Skeleton landed at the user-declared path.
- Chat-paste damage cleaned at intake (smart quotes, `__future__`
  tokens, markdown-bold leaks on dunder names).
- Adapter-flag mismatch named and bridged (`to_real_flag`).
- 7-case tripwire locks the structural argument + the falsification
  hook + the adapter bridge.
- AUDIT_07 § C.4 updated to `[PARTIALLY ADDRESSED]` — scope
  decomposition landed; classical four-function still `[OPEN]`.
- `money_signal/` integration path named but not implemented.
- Typed provenance retrofit on `MoneyState` flags deferred to a
  future pass.
- Full regression: **40/40 PASS**. Main stack untouched.
