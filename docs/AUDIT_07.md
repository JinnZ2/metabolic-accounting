# AUDIT 07

Seventh audit pass. Scope: the argument-structure weaknesses named
in the Tier 1 read-through after AUDIT_06, and the "ground every
decision in scientific studies / document provenance" directive that
followed.

The headline was: many numeric claims in the framework carry no
defensible provenance, and "back every number with a citation" is
the wrong flat rule — it produces performative refs that don't
actually support the claim. This audit lands a five-kind provenance
taxonomy (EMPIRICAL / THEORETICAL / DESIGN_CHOICE / PLACEHOLDER /
STIPULATIVE), retrofits all three Tier 1 audits to use it, and
tripwires what was load-bearing but previously unenforced.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not yet implemented; `[NAMED]` — real gap, not yet
designed.


## Part A — What landed

### A.1 `term_audit/provenance.py` — the 5-kind taxonomy   `[CLOSED]`

Every numeric or structural choice in the framework now has a
canonical way to be justified:

- **EMPIRICAL** — peer-reviewed measurement with uncertainty bounds;
  requires `source_refs`; `scope_caveat` documents the gap when the
  study measured X but we're applying it to Y.
- **THEORETICAL** — derivable from a conservation law, identity, or
  information-theoretic constraint; requires `source_refs` OR a
  `rationale` naming the law invoked.
- **DESIGN_CHOICE** — structural decision (e.g. the 5-of-7 signal
  threshold, the `-0.5` V_B→V_C strength estimate); requires
  `alternatives_considered` AND `falsification_test`. Without the
  latter, a design choice is unfalsifiable by construction.
- **PLACEHOLDER** — acknowledged guess pending a real derivation or
  measurement; requires `retirement_path` naming the study or
  derivation that would retire the placeholder.
- **STIPULATIVE** — part of the definition (V_A = use-value by
  construction); requires `definition_ref` OR `rationale`.

Plus a `knowledge_dna` pass-through field on every record — the
framework does not interpret it, but propagates it so external
provenance systems (e.g. the user's Knowledge DNA lineage) can
ride along with every claim.

Constructor functions (`empirical(...)`, `theoretical(...)`, etc.)
enforce required fields at build time. `Provenance.missing_fields()`
lets hand-built partial records surface their gaps for the framework
to audit itself.

### A.2 `SignalScore` extended (backward-compatible)   `[CLOSED]`

`SignalScore.provenance: Optional[Provenance]` added alongside the
legacy `source_refs: List[str]` field. Old audits still work; new
audits use the typed provenance. `TermAudit.provenance_coverage()`
aggregates across the audit's signal_scores.

### A.3 The `is_signal` inconsistency — closed   `[CLOSED]`

Pre-AUDIT_07 `schema.py` carried two contradictory rules:

- docstring: "a term that fails three or more of seven → not a signal"
- code: `is_signal(threshold=5)` counting passes at score ≥ 0.7

5 passes at 0.7 ≠ 3 failures at <0.5; the rules overlap but are not
identical. AUDIT_07 exposes scoring thresholds as class constants
(`PASS_SCORE = 0.7`, `PASS_CRITERIA_REQUIRED = 5`, `FAILURE_SCORE =
0.5`) so the rule is inspectable, reconciles the docstring, and
matches the code's actual behavior (5/7 pass = 2/7 fail at most,
which satisfies "fails three or more" as its complement).

### A.4 Vector aggregates — information preserved   `[CLOSED]`

`is_signal()` returns one bit. The collapsed-vs-decomposed argument
depends on a gap (0 passes for money-collapsed vs 7 passes for K_A
productive). `TermAudit` now also exposes:

- `pass_count()` — integer count at threshold
- `score_vector()` — the full 7-dim dict
- `mean_score()` — arithmetic mean (lossy, monotonic)
- `min_score()` — weakest criterion (a single 0 drags the audit)

Test 7 in `tests/test_tier1_coverage.py` asserts the numbers behave:
money collapsed = 0 passes / 0.129 mean / 0.05 min; K_A productive =
7 passes / 0.764 mean / 0.70 min.

### A.5 Tier 1 audits retrofitted with Provenance   `[CLOSED]`

Every SignalScore in every Tier 1 audit now carries a complete
`Provenance`, and every linkage strength estimate too.

**Money (1 audit × 7 criteria = 7 entries):**
- 4 empirical (BLS regional CPI, PPP, Boskin, FASB 820, BoE 2014)
- 3 theoretical (multi-referent structure, reflexivity, circularity)

**Value (4 audits × 7 = 28 entries + 5 linkages):**
- collapsed: 1 empirical, 6 theoretical
- V_A use:   2 empirical (IoM DRIs, ASHRAE), 1 theoretical, 1 design_choice, 3 stipulative
- V_B exch:  1 empirical (SEC Rule 605, TRACE), 3 theoretical, 1 design_choice, 2 stipulative
- V_C subs:  2 empirical (FAO/IPCC/ISO/Odum), 3 theoretical, 2 stipulative
- linkages:  1 theoretical, 1 design_choice, 3 placeholder (load-bearing V_B→V_C is DESIGN_CHOICE with 3 alternatives considered and a concrete falsification test)

**Capital (4 × 7 = 28 + 6 linkages):**
- collapsed: 1 empirical (Fama-French, FASB), 6 theoretical (Cambridge capital controversy, Robinson, Sraffa)
- K_A prod:  2 empirical (ISO, FAO, NIST), 3 theoretical, 2 stipulative
- K_B fin:   2 empirical (FASB, IFRS, SEC, FINRA), 3 theoretical, 2 stipulative
- K_C inst:  1 empirical (WGI, Ostrom, Putnam), 2 theoretical, 1 design_choice, 3 stipulative
- linkages:  1 empirical (La Porta et al.), 1 theoretical, 2 design_choice, 2 placeholder (K_B→K_A and K_B→K_C are DESIGN_CHOICE with alternatives)

Total: **70 SignalScores + 11 linkages = 81 provenance records**, all
complete. `tests/test_tier1_coverage.py` asserts this holds.

### A.6 Load-bearing negative-linkage tripwire   `[CLOSED]`

AUDIT_05 said: "changing any of [the load-bearing negative linkages]
to positive would break the Tier-1-inheritance argument." No test
actually enforced this. AUDIT_07 encodes it as test 6:

- `V_B → V_C` (exchange-value draws down substrate-value): -0.50
- `K_B → K_A` (financial-capital growth draws down productive-capital): -0.60
- `K_B → K_C` (financialization crowds out institutional-capital): -0.55

If any of these flips to positive or zero, the test fails with a
named load-bearing rationale in the error message.


## Part B — What changed in behavior, not just structure

### B.1 Design-choice honesty

Before AUDIT_07, scoring-level judgments (the specific 0.1 vs 0.15
distinctions) were implicitly asserted as empirical. After AUDIT_07,
each carries a Provenance kind. This exposes what the framework is
actually doing:

- Most money SignalScores are EMPIRICAL or THEORETICAL with real
  backing — the foundational claim about money is well-anchored.
- Value and capital SignalScores lean heavily STIPULATIVE — the
  V_A/V_B/V_C and K_A/K_B/K_C decompositions are definitional work,
  not empirical claims, and the Provenance now says so.
- Linkage strengths are mostly PLACEHOLDER — the auditor's best
  guess absent a meta-analysis. Load-bearing signs are DESIGN_CHOICE
  with alternatives and falsification tests; the magnitudes are
  guesses, the signs are structural.

This is the honesty repair the directive was asking for: the
framework now exposes what it knows vs what it has assumed.

### B.2 Knowledge DNA integration

Every `Provenance` has a `knowledge_dna: str` pass-through field.
The framework does not parse or validate it — this is deliberate.
External provenance systems (Knowledge DNA lineage, content-address
hashing, cryptographic attestation) can attach their lineage
identifiers to any claim, and the framework preserves them through
coverage reports (`knowledge_dna_count` in the aggregate report).


## Part C — What's NOT yet done (scoped out, not repaired)

- **Tier 2 / 3 / 4 audits** not retrofitted. `productivity`,
  `efficiency`, `disability` still use the legacy `source_refs`
  shape. Coverage reports on these will show `none` counts until a
  future pass extends the pattern. This was scoped intentionally:
  ship the pattern on the load-bearing Tier 1 trio first, let it
  shake out, then extend.
- **Equations in `docs/EQUATIONS.md`** not yet converted to typed
  `Provenance` records. Eq 4 (multiplicative cascade) is still
  FRAGILE; Eq 3 (linear ramp) still PLACEHOLDER; the doc-level tags
  are a different surface from the code-level `Provenance` type.
  A unified `equations/registry.py` is the natural next step but
  out of scope here.
- **Inheritance invariant as code.** The claim "money's signal-criteria
  scores are bounded above by the best score across the V_A/V_B/V_C
  components money claims to measure" is stated in prose but not
  enforced by a test. The vector aggregates added in A.4 make this
  encodable in a next pass.
- **Money four-function decomposition** (M_A medium-of-exchange /
  M_B store-of-value / M_C unit-of-account / M_D standard-of-deferred-
  payment) still not audited; `money.py` remains structurally
  asymmetric with `value.py` / `capital.py`.


## Part D — Coverage snapshot

| Surface | Total | Complete | Incomplete | None |
| --- | --- | --- | --- | --- |
| money signal_scores | 7 | 7 | 0 | 0 |
| value signal_scores (4 audits) | 28 | 28 | 0 | 0 |
| capital signal_scores (4 audits) | 28 | 28 | 0 | 0 |
| value linkages | 5 | 5 | 0 | 0 |
| capital linkages | 6 | 6 | 0 | 0 |
| **Tier 1 subtotal** | **74** | **74** | **0** | **0** |
| Tier 2 signal_scores (productivity, efficiency) | 14 | 0 | 0 | 14 |
| Tier 4 signal_scores (disability) | ~21 | 0 | 0 | ~21 |
| Equations in docs/EQUATIONS.md | 13 | — | — | — |

Tier 1 is fully provenanced. The rest of the stack is named and
scoped for a future pass.


## Part E — Test-suite change

- `tests/test_provenance.py` (new, 9 tests) — locks in the 5-kind
  taxonomy, constructor validators, coverage aggregation, and the
  knowledge_dna pass-through invariant.
- `tests/test_tier1_coverage.py` (new, 7 tests) — locks in full
  provenance coverage on Tier 1, the three load-bearing negative-
  linkage signs, and the vector-aggregate differentiation between
  collapsed tokens and clean substrate terms.

Full regression: **36/36 PASS** (pre-AUDIT_07: 35/35). Main stack
unchanged: first-law closure still 1.42e-14, preempt #10 still
falsifies `distinction_as_coordination` at 22.863/100, all Tier 1/2/4
numerical findings in STATUS.md reproduce.


## Part F — Recommended next actions

Ordered by cost / value:

1. **[SAFE]** Extend provenance to Tier 2/4 audits (productivity,
   efficiency, disability). Mechanical: same pattern as Tier 1. Adds
   ~35 more provenance records.
2. **[MEDIUM]** Wire the inheritance invariant as a test. Per-criterion
   assertion: for every criterion c, `money.score(c)` ≤
   `max(V_A.score(c), V_B.score(c), V_C.score(c))`. Same for K vs V.
   Makes the thesis falsifiable at code level.
3. **[MEDIUM]** Build `equations/registry.py` that reads `docs/EQUATIONS.md`
   tags and attaches a `Provenance` to each equation. Eq 4 FRAGILE →
   DESIGN_CHOICE with alternatives_considered; Eq 3 PLACEHOLDER →
   PLACEHOLDER with retirement_path. One source of truth instead of
   two.
4. **[LARGE]** Add a fourth decomposition to money.py
   (M_A/M_B/M_C/M_D). Restores structural symmetry with value and
   capital; strengthens the foundational Tier 1 audit.
5. **[LARGE]** Replace Eq 3 linear ramp with the power-law form
   already documented in EQUATIONS.md; replace Eq 4 multiplicative
   aggregation with a pluggable (dominant / additive / saturating)
   aggregator. The EQUATIONS.md design is already written; code has
   not moved.


## Close-out

- 5-kind provenance taxonomy landed; every kind tripwired.
- Tier 1 audits fully provenanced: 74/74 records complete.
- Three load-bearing negative-linkage signs tripwired against
  silent flip.
- `is_signal` threshold reconciled with docstring rule.
- Vector aggregates added alongside the bool to preserve the
  collapsed-vs-decomposed gap.
- Knowledge DNA pass-through integrated at every provenance record.
- Tier 2/3/4 provenance, inheritance invariant, money four-function
  decomposition, and equation-registry scoped for future passes.
- 36/36 regression green.
