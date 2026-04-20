# AUDIT 05

Fifth audit pass. Scope: the sprint that opened the `term_audit/`
layer, committed 6 concrete audits + 7 supporting tools, built the
`term_audit -> metabolic-accounting` adapter, and surfaced 3
structural observations about the main stack that are scoped out
here but named for future sessions.

Status key: `[CLOSED]` — fix present and covered by tests; `[OPEN]` —
scoped but not implemented; `[NAMED]` — identified as real gap, not
yet designed.


## Part A — What landed

### Term-audit schema layer

Nine infrastructure modules, all CC0 / stdlib / tested:

- `term_audit/schema.py` — 7-criterion signal audit with
  `StandardSetter.loss_if_audited` (preempt #5) and explicit
  `measurement_layer()` / `incentive_layer()` views on `TermAudit`
  (preempt #2).
- `term_audit/scoping.py` — 15 required scoping dimensions;
  `DeclaredScope` surfaces missing dimensions explicitly.
- `term_audit/tiers.py` — seven-tier registry of 65 terms the
  framework rubs against.
- `term_audit/falsification.py` — `FalsifiablePrediction`,
  `BoundaryCondition`, `PredictionRegistry` (preempts #1 and #6).
- `term_audit/contradictions.py` — pairwise structural contradiction
  detector with `KNOWN_CONTRADICTIONS` registry (preempt #7).
- `term_audit/counter_hypotheses.py` — `CounterHypothesis` runner
  (preempt #4); `DISTINCTION_AS_COORDINATION` falsifies the
  steel-manned defense within the model regime.
- `term_audit/status_extraction.py` — dynamic model of measurement-
  system capture; enforces energy conservation across every step.
- `term_audit/incentive_analysis.py` — cross-term archetype analysis
  across every committed audit; `classify_setter` into 10 archetypes;
  `analyze_cross_term` returns per-term capture risk and archetype
  aggregates.
- `term_audit/integration/metabolic_accounting_adapter.py` — one-way
  bridge from `term_audit` outputs to `metabolic-accounting` inputs
  (`BasinStateInput`, `InfrastructureInput`, `CascadeCouplingInput`,
  `GlucoseFlowInput`, `VerdictInput`, `AssumptionValidatorFlag`).

### Audits committed

| Term | Tier | Result | Decomposition |
| --- | --- | --- | --- |
| `money` | 1 | 0/7 signal criteria pass | single |
| `value` | 1 | collapsed 0/7; V_A 3/7, V_B 1/7, V_C 7/7 | V_A use / V_B exchange / V_C substrate |
| `capital` | 1 | collapsed 0/7; K_A 7/7, K_B 0/7, K_C 0/7 | K_A productive / K_B financial / K_C institutional |
| `productivity` | 2 | 0/7, with dependency-based redefinition | `JobDependencyProfile` + 10 categories |
| `efficiency` | 2 | 1/7 (falsifiability only), vector-space redefinition | `EfficiencyVector` on EROI / coupling / trajectory / knowledge |
| `disability` | 4 | 3-measurement decomposition | A mismatch / B bounded / C substrate |

All collapsed tokens fail 7/7. All decompositions surface at least
one clean signal when properly scoped. Every audit has tripwire
tests locking in load-bearing findings (especially the NEGATIVE
linkages: V_B → V_C, K_B → K_A, K_B → K_C, and the NONE relation
B → C in disability — changing any of these to positive would
break the Tier-1-inheritance argument).

### Horizontal-measurement tools (Tier 3 territory)

Four additional modules building out the institutional-legitimacy
measurement surface:

- `term_audit/expertise.py` — 3-measurement decomposition (E_A
  operational, E_B credentialed, E_C transmission); introduces
  four institutional-legitimacy axes (cost_gating,
  feedback_timescale, standard_setter_recursion,
  practitioner_representation) reusable across all Tier 3 terms.
- `term_audit/systemic_necessity.py` — 14 role profiles;
  `detect_necessity_inversions` surfaced 10 hierarchy/necessity
  inversions including (farmer vs corporate_executive, gap +0.80)
  and (hazmat_long_haul_driver vs corporate_executive, +0.75).
- `term_audit/alternative_viability.py` — scoring machinery for
  proposed substitutions (CAPTURE / RELOCATION / IMPLEMENTATION /
  STRUCTURAL classifications) across reference alternatives.
- `term_audit/civilization_substrate_scaling.py` — scale-tier
  analysis across band → global; substrate functions required per
  scale, measurement-appropriateness per (measurement, scale)
  pair, collapse analysis with fallback and recovery requirements.
- `term_audit/consequence_accounting.py` — 18 role profiles;
  `detect_inversions` surfaced 12 of 12 expected structural
  authority inversions (exposure ↔ authority mismatch).
- `term_audit/collapse_propensity.py`,
  `term_audit/governance_design_systems.py`,
  `term_audit/recovery_pathways.py` — additional measurement
  infrastructure landed during the sprint.

### Tooling

- `scripts/fix_pasted_file.py` — chat-paste repair: smart quotes,
  markdown fences, `**name**` / `**main**` bolding, class/function
  body indentation, sys.path bootstrap insertion. Evolved through
  the sprint to handle Enum members, class-level constants,
  continuation keywords, inline-comment colon openers, multi-line
  def signatures, and method-vs-top-level `def` disambiguation.
  Tracks its own limitations: deeply-nested control flow still
  needs manual cleanup; `ast.parse` at the end flags when output
  is incomplete.

### Defensive posture

`docs/PREEMPTING_ATTACKS.md` encodes seven preempts, each with a code
anchor. `tests/test_preemption.py` (12 cases) tripwires every preempt,
including a load-bearing assertion that `DISTINCTION_AS_COORDINATION`
must stay falsified under default dynamics — its message explicitly
warns future contributors that changing it is a non-soft change.


## Part B — Bugs caught by tests this sprint

1. **`cascade_from_negative_linkage` always returned None.** Paste
   damage had left the `return CascadeCouplingInput(...)` inside the
   `if strength >= 0: return None` branch, making it unreachable.
   `tests/test_metabolic_accounting_adapter.py::test_7` surfaced it.
   Fixed in commit `8145548`.

2. **Many paste-damage bugs in fresh module files.** Each of
   `expertise`, `systemic_necessity`, `alternative_viability`,
   `civilization_substrate_scaling`, `consequence_accounting`, the
   `money`/`value`/`capital` main blocks, `metabolic_accounting_adapter`,
   and `incentive_analysis` arrived with at least one
   return-inside-loop, progressive indent-cascade, or
   method-nested-in-method issue. All caught by running the module,
   all fixed before commit.


## Part C — STATUS.md drift caught and corrected

At sprint start STATUS.md listed 18 passing suites, no knowledge of
`term_audit`, no audit inventory. By end of sprint the tree has
33 test files (31 verified passing via full regression) and a full
audit inventory. STATUS.md was updated in commit `4ea0476`. This is
the same drift mode AUDIT_04 had to unwind — now caught inside the
repo's own discipline rather than surfacing from a fresh audit.


## Part D — Structural observations (user-raised, scoped this audit)

Three architectural questions surfaced during sprint review. Each is
real but out of scope for this audit; each gets a design sketch here
so the next session does not re-derive.

### D.1 Feedback loop: verdict → firm behavior   `[NAMED]`

**Current state.** `compute_flow(revenue, direct_operating_cost,
regeneration_paid, basins, systems, site, step_result)` takes every
behavior input from the caller. Nothing in the pipeline reads
`Verdict.sustainable_yield_signal` or `Verdict.forced_drawdown` and
adjusts next-period revenue / regen spend / extraction. The firm's
stress vector is fully exogenous.

**Why it matters.** Counterfactual questions like "would responding
to AMBER with +X in regen spend prevent RED?" cannot be answered
without an endogenous policy layer. The framework currently runs one
period at a time with caller-supplied inputs — fine for snapshots,
limited for trajectories.

**Proposed shape.**

- New module: `behavior/` or `simulation/` at top level.
- `FirmPolicy` abstraction mapping `(Verdict, basin state, history)
  → (regen_paid_next, extraction_next, mitigation_actions)`.
- Several reference policies: `StatusQuoPolicy`,
  `ComplianceMinimumPolicy`, `BlackTierEmergencyPolicy`,
  `CapacityFitPolicy`.
- A multi-period `simulate(initial_site, policy, steps)` that loops
  `site.step → compute_flow → assess → policy.decide → apply`.
- Decisions about what stays exogenous (market shocks, external
  demand) vs endogenous (regen, extraction, mitigation).

**Tradeoff.** Substantial scope increase; enters organizational-
behavior territory. Also where the most useful counterfactuals live.
Probably its own audit (AUDIT_06) when prioritized.

### D.2 Inter-basin coupling over time   `[NAMED]`

**Current state.** `cascade/detector.py` computes failure rates from
current basin state. Nothing propagates this period's soil
degradation into next period's water trajectory. The cascade is
static: given state X, predict failure. The dynamic is missing.

**Why it matters.** Soil permeability loss → reduced aquifer recharge
→ higher irrigation stress → higher cascade burn on water-dependent
infrastructure → deferred maintenance → eventual water-basin collapse
feeding back to soil. This is the cascade dynamics the framework's
thesis depends on, but currently only the first step is modeled.

**Proposed shape.**

- New field on `Site` or `BasinState`: `coupling_matrix: Dict[Tuple[
  str, str], CouplingLink]` where key is
  `(source_basin.metric, target_basin.metric)` and `CouplingLink`
  carries `gain`, `lag_periods`, `mechanism`, `source_refs`.
- `Site.step()` would, before the stress partition, propagate
  previous-period degradations through the coupling matrix into
  this period's trajectory adjustments.
- Coupling coefficients must be literature-anchored (soil carbon →
  aquifer recharge, etc.) — see `docs/LITERATURE.md`. Adding them
  without anchors repeats the `[PLACEHOLDER]` tagging issue
  `docs/EQUATIONS.md` already flags.

**Tradeoff.** Medium scope. Natural extension given the framework's
existing basin-type and ramp infrastructure. The main cost is
literature work for coupling coefficients; the code shape is a
straightforward addition to `reserves/site.py::step()`.

### D.3 Reserves/ prominence   `[CLOSED]`

Landed this sprint in commit `798e60b`. `README.md` now says reserves
is "where the forced drawdown actually executes." `CLAUDE.md`
upgraded from "orthogonal to the main stack" to "load-bearing in
parallel with the main stack" and explicitly names which PnL fields
originate in reserves (not accounting).


## Part E — Hidden variables enumerated pre-sprint, status now

From STATUS.md § "Hidden variables found in the audit":

1. Directional coupling over time — see D.2 above. Still `[OPEN]`.
2. Geographic proximity in cohort exposure — `[OPEN]`, unchanged.
3. Generational lag in `potential_waste` — `[OPEN]`, unchanged.
4. Trust hysteresis — `[OPEN]`, unchanged.
5. Temporal asymmetry between cohorts — `[OPEN]`, unchanged.


## Part F — Open bugs from AUDIT_04

Unchanged this sprint.

- **Bug 2** (regulatory crosswalk has no social/labor frameworks):
  `[OPEN]`. Candidate frameworks documented in `AUDIT_04.md` Part B.
- **Bug 3** (no community-specific mitigation patterns): `[OPEN]`.
  Candidates in `AUDIT_04.md` Part C.


## Part G — Coverage by tier (audits committed vs terms in registry)

| Tier | Committed / Total | Remaining priority terms |
| --- | --- | --- |
| 1 — foundational fictions | 3 / 8 | `currency`, `investment`, `wealth`, `economic_growth`, `gross_domestic_product` |
| 2 — labor and human-worth | 2 / 10 | `performance`, `skill`, `qualification`, `credential`, `merit`, `unemployment`, `labor_market`, `human_capital` |
| 3 — organizational legitimacy | 0 / 9 (machinery landed) | `accountability`, `authority`, `leadership`, `expertise` partially via `expertise.py`, `governance`, `compliance`, `professionalism`, `best_practices`, `stakeholder` |
| 4 — capacity measurements | 1 / 14 | `mental_illness`, `intelligence`, `iq`, `learning_disorder`, `adhd`, `autism_spectrum`, `normal`/`normative`, `functional`, `high_functioning`/`low_functioning`, `competence`, `rationality` |
| 5 — social and behavioral | 0 / 9 | all |
| 6 — knowledge and truth | 0 / 8 | all — the AI-drift tier per `docs/TERMS_TO_AUDIT.md` |
| 7 — environmental and resource | 0 / 7 | all — largely covered by companion repos per `docs/RELATED.md` |

6 of 65 audited. The Tier-1 foundational work is most advanced
(3 of 8, with the load-bearing collapse-finding established across
`money`, `value`, and `capital`). Tier 3 is next: machinery is in
place via `expertise.py`'s four institutional-legitimacy axes,
but only one term audited with them.


## Close-out

- Sprint delivered the term_audit layer, 6 concrete audits, 10
  supporting measurement / meta-analysis modules, and an adapter
  to the main accounting stack.
- STATUS.md is synchronized with the code as of commit `4ea0476`.
- Two bugs caught by tests (cascade return, paste-damage class).
- Three structural observations raised by review (D.1, D.2, D.3);
  D.3 closed this sprint, D.1 and D.2 scoped for future audits.
- Two pre-existing AUDIT_04 bugs (2 and 3) unchanged.
- 6 of 65 tiered terms audited. Clear next priority: continue
  Tier 1 (currency / investment / wealth / GDP) or open Tier 3
  with `accountability` / `authority` using the expertise.py
  institutional-legitimacy axes as a template.
