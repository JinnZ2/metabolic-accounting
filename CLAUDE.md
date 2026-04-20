# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project constraints (non-negotiable)

- **CC0 licensed. Python stdlib only.** Do not introduce third-party dependencies (no numpy, pandas, pydantic, pytest, etc.). Math uses `math` from stdlib; data containers are `@dataclass`.
- **Falsifiable, machine-readable, test-first.** Every claim about framework behavior must be backed by a test that actually produces the output. See `STATUS.md` for the discipline rationale — Claude has fabricated tool output in this repo before, so do not report numerical results you have not just generated via `python tests/test_*.py`.
- **No currency in the physics.** Reserve quantities are `xdu` (exergy-destruction-equivalent units); see `thermodynamics/exergy.py`. Currency conversion is a downstream policy layer, not baked in.
- **`math.inf` is a valid return value**, not an error. Irreversibility (past-cliff metrics, extinct apex species, collapsed aquifers) propagates as `inf` through `required_regeneration_cost → GlucoseFlow.regeneration_required → metabolic_profit → Verdict`. Do not silently clamp; the whole point is honest reporting of unrecoverable states.

## Running tests

There is no test runner, no `pytest`, no `pyproject.toml`, no `requirements.txt`. Every test file is a standalone script that inserts the repo root into `sys.path` and calls its test functions from `__main__`.

```bash
# Run one test (from repo root):
python tests/test_integration.py
# or equivalently:
python -m tests.test_integration

# Run all tests:
for t in tests/test_*.py; do python "$t" && echo "PASS" || echo "FAIL"; done
```

Assertions use plain `assert`; failures abort the script and print the assertion line. There is no `-k`/`-x`/fixture machinery — to run a single case, edit the `if __name__ == "__main__":` block at the bottom of the test file.

The Bug 1 and Bug 4 fixes described in `STATUS.md` are covered by `tests/test_tier_vector.py`. See `docs/AUDIT_04.md` for the audit trail that landed those fixes and for the candidate plan on the still-open Bugs 2 (no social/labor regulatory frameworks) and 3 (no community-specific mitigation patterns).

## Architecture — five-layer stack

Data flows upward; each layer consumes the one(s) below:

```
VERDICT         verdict/            GREEN/AMBER/RED/BLACK + warnings + profit lines
ACCOUNTING      accounting/         GlucoseFlow: revenue, regen required, cascade burn, debt
CASCADE         cascade/            basin state -> effective failure rate -> cascade cost
INFRASTRUCTURE  infrastructure/     systems with basin dependencies + sensitivities
BASIN STATE     basin_states/       soil, air, water, biology, community (primary metrics)
```

Load-bearing in parallel with the main stack (read alongside, not after):

- `reserves/` — **where the forced drawdown actually executes.** `Site` binds basins to **secondary** (per-metric buffer) and **tertiary** (site-shared landscape) reserves. `Site.step(stress)` partitions stress through primary → secondary → tertiary → environment and enforces first-law closure via `thermodynamics/exergy.py`. The `reserve_drawdown_cost` and `environment_loss` that `compute_flow(...)` surfaces on the PnL are computed here, not in `accounting/`. The "invisible hidden cost" you see in `tests/test_integration.py` output (report $399.33, metabolic $370.73, $28.60 delta) is a reserves-layer quantity the accounting layer merely routes through.
- `thermodynamics/exergy.py` — enforces Gouy-Stodola: exergy destruction ≥ 0. `check_closure` and `check_nonnegative_destruction` are called after every reserve partition.
- `distributional/` — maps verdict tiers onto population cohorts with per-basin-type sensitivities. `apply_tier_to_cohorts` supports a vector path (`cohort_basin_sensitivities`) so a firm GREEN on soil and BLACK on community hits cohorts differently. Also houses institutional fit accounting (`available_capacity`, `fit_multiplier`, `trauma_tax`, `waste_ratio`) and civilization-scale comparisons.
- `mitigation/`, `regulatory/`, `social_cascade/` — downstream reporting on top of the verdict.

### Core data flow worth internalizing

`tests/test_integration.py` is the canonical end-to-end wiring:

```
Site(basins).attach_defaults()
    → step_result = site.step(stress)
    → flow = compute_flow(revenue, cost, regen_paid, basins, systems,
                           site=site, step_result=step_result)
    → verdict = assess(basins, flow)
```

Without `site`/`step_result`, `compute_flow` still works (backward-compatible path) but `reserve_drawdown_cost` and `environment_loss` are zero — this is not a bug, it is the pre-reserve pipeline.

## Conventions that bite if you miss them

- **The regeneration registry is keyed by `(basin_type, metric_key)`, NOT by basin name.** A basin named `farm_north_soil` with `basin_type="soil"` looks up the same functions as `site_soil`. Renaming a basin must never change its cost lookup; if you add a new basin, set `basin_type` to one of the known values (`soil`, `air`, `water`, `biology`, `community`) or pass a custom registry. `KNOWN_METRICS` + `strict=True` is how the framework refuses to silently under-report cost — see `accounting/regeneration.py` and `tests/test_registry_safety.py`.
- **`high_is_bad` is declarative per-basin** (`BasinState.high_is_bad: set`). The legacy global `HIGH_IS_BAD` in `cascade/detector.py` is a fallback only; prefer the per-basin field for new metrics.
- **Two profit lines, intentionally.** `metabolic_profit()` excludes `environment_loss` (treated as extraordinary, per GAAP ASC 360-10-35 / GASB 42 / SEEA). `metabolic_profit_with_loss()` includes it. `is_extraordinary_loss_material()` applies a 5%-of-revenue materiality heuristic. Do not collapse these into one number.
- **BLACK = irreversibility, not just "very bad."** Reserved for primary irreversibility OR any tertiary pool past its cliff. Do not lower BLACK to mean RED-plus.
- **Tier assignment is a vector.** `TierAssignment.by_basin_type` per basin type; `overall_tier()` is the worst-case aggregate. Code that calls `overall_tier()` and discards the vector is the pattern that caused Bug 4 in `STATUS.md` — prefer basin-type-aware consumers.
- **Basin naming convention** (`distributional/tiers.py::_basin_type_from_name`): names follow `{prefix}_{type}` (e.g. `site_soil`, `plant_water`) so type can be derived by `rsplit("_", 1)`. Keep this when adding new basins.

## Documentation layout

- `README.md` — thesis and layer diagram (public-facing).
- `STATUS.md` — current session state: tests passing, bugs fixed, hidden variables still open, what the framework does NOT do. **Update this** when you change verified behavior.
- `docs/EQUATIONS.md` — every equation in the scaffold, tagged `[CORE] / [PLACEHOLDER] / [HEURISTIC] / [FRAGILE]`. Read before changing any formula; `[PLACEHOLDER]` and `[FRAGILE]` are explicitly waiting to be replaced.
- `docs/AUDIT_01..04.md` — audit reports. `AUDIT_04.md` covers the tier-vector Bug 1/4 fixes and scopes the still-open Bugs 2 (regulatory crosswalk has no social/labor frameworks) and 3 (mitigation has no community-specific leverage patterns). New audits append (`AUDIT_05.md`, etc.); do not overwrite prior ones.
- `docs/RELATED.md` — relationship to the three companion repos (TAF as organism-agnostic parent, PhysicsGuard as claim verifier, Logic-Ferret as narrative auditor). No runtime dependencies between repos; links are structural (shared invariants) not code-level.
- `docs/SCHEMAS.md` — data types this repo exposes for cross-framework consumption (`ExergyFlow`, `GlucoseFlow`, `BasinState`, `Tier`/`TierAssignment`, `Verdict`) with units and invariants. Companion tools read this to construct matching local types without importing from this repo.
- `docs/LITERATURE.md` — citations backing the thermodynamic framing.

## Navigation — where to start by intent

Land on the right file without grepping blind. Each row lists the primary file and the first place to look next.

| If you want to... | Start here | Then |
| --- | --- | --- |
| See the pipeline end-to-end | `tests/test_integration.py` | `tests/test_scaffold.py` |
| Change regeneration cost math | `accounting/regeneration.py` | `tests/test_regeneration.py`, `tests/test_registry_safety.py` |
| Add a new basin type | `basin_states/base.py` + one of the type files | `reserves/defaults.py` (`SECONDARY_SPECS`) + register regen fn in `accounting/regeneration.py` |
| Change cascade / failure-rate math | `cascade/detector.py`, `cascade/aggregation.py` | `docs/EQUATIONS.md` §4, `cascade/ramp.py` |
| Understand the glucose / PnL lines | `accounting/glucose.py` | `verdict/assess.py` |
| Change what BLACK / RED / AMBER mean | `verdict/assess.py::yield_signal` | `distributional/tiers.py::determine_tier_for_basin` |
| Add a regulatory framework (Bug 2) | `regulatory/frameworks.py` | `regulatory/crosswalk.py`, `docs/AUDIT_04.md` Part B |
| Add a mitigation action (Bug 3) | `mitigation/actions.py` | `tests/test_mitigation.py`, `docs/AUDIT_04.md` Part C |
| Work with cohorts / distributional load | `distributional/access.py` | `distributional/institutional.py`, `tests/test_distributional.py`, `tests/test_tier_vector.py` |
| Understand reserves + first-law closure | `reserves/site.py` (`step()`) | `reserves/pools.py`, `thermodynamics/exergy.py` |
| Check literature anchors for a metric | `docs/LITERATURE.md` | the relevant basin file in `basin_states/` |
| Audit whether an economic term is a signal | `term_audit/schema.py` | `tests/test_term_audit.py` |
| Attach provenance (empirical / theoretical / design_choice / placeholder / stipulative) to any numeric or structural choice | `term_audit/provenance.py` | `tests/test_provenance.py`, `tests/test_tier1_coverage.py`, `docs/AUDIT_07.md` |
| Write a new concrete term audit | `term_audit/audits/money.py` as template | `term_audit/audits/` (capital, value, productivity, efficiency, disability) |
| Analyze capture risk across every committed audit | `term_audit/incentive_analysis.py` | `tests/test_incentive_analysis.py` |
| Feed term_audit output into the accounting pipeline | `term_audit/integration/metabolic_accounting_adapter.py` | `tests/test_metabolic_accounting_adapter.py` |
| Run term_audit outputs over a time series | `term_audit/integration/temporal_adapter.py` | `tests/test_temporal_adapter.py` |
| Audit a Tier 3 institutional-legitimacy term | `term_audit/expertise.py` (template + 4 axes) | `term_audit/systemic_necessity.py`, `term_audit/consequence_accounting.py` |
| Work with E_X (cross-domain closure) — the fourth expertise dimension | `term_audit/audits/expertise_x_cross_domain_closure.py` | `tests/test_expertise_x_audit.py`, `docs/AUDIT_08.md` |
| Detect populations that routed around formal systems (canary principle + substrate evidence) | `term_audit/signals/routing_around_detection.py` | `tests/test_routing_around_detection.py`, `docs/AUDIT_08.md` |
| Emit AI-readable expertise profiles (JSON-LD) | `term_audit/machine_readable_expertise.py` | `term_audit/audits/expertise_x_cross_domain_closure.py` |
| Audit a law, regulation, or ordinance against its own first-principles purpose | `term_audit/legislative_audit/first_principles_legislative_audit.py` | `tests/test_legislative_audit.py`, `docs/AUDIT_09.md` |
| Audit money across three marketed scopes (flow / community / lube) via 12 invariants | `term_audit/audits/money_three_scope_falsification.py` | `tests/test_money_three_scope_falsification.py`, `docs/AUDIT_10.md` |
| Model money-as-signal coupling matrix (K_ij with temporal/cultural/attribution/observer modifiers) | `money_signal/dimensions.py`, `money_signal/coupling_base.py` | `money_signal/coupling_temporal.py` etc. |
| Score a proposed alternative to a captured measurement | `term_audit/alternative_viability.py` | CAPTURE / RELOCATION / IMPLEMENTATION / STRUCTURAL classifications |
| Reason about measurement appropriateness by civilization scale | `term_audit/civilization_substrate_scaling.py` | `term_audit/collapse_propensity.py` |
| Think about what must be preserved through collapse / how recovery proceeds | `term_audit/recovery_pathways.py` | `tests/test_recovery_pathways.py` |
| Design measurement systems that resist capture | `term_audit/governance_design_principles.py` (14 principles, 6 categories) | `tests/test_governance_design_principles.py` |
| Repair a chat-paste of code (smart quotes, flat bodies) | `scripts/fix_pasted_file.py` | run `python scripts/fix_pasted_file.py IN OUT`, review the diff, `ast.parse` result |
| **Reason about money / capital / investment / any economic term** | `docs/SCOPING_ECONOMIC_TERMS.md` (**read first**) | `term_audit/scoping.py`, `term_audit/audits/money.py` |
| **See the tiered list of terms we are auditing** | `docs/TERMS_TO_AUDIT.md` | `term_audit/tiers.py::find_tier(term)` |
| Understand the dynamics that capture measurement systems | `term_audit/status_extraction.py` | `tests/test_status_extraction.py`, `term_audit/audits/disability.py` |
| **Defend the framework against attacks** | `docs/PREEMPTING_ATTACKS.md` | `term_audit/falsification.py`, `term_audit/contradictions.py`, `term_audit/counter_hypotheses.py` |
| Understand how this repo relates to TAF / PhysicsGuard / Logic-Ferret | `docs/RELATED.md` | `docs/SCHEMAS.md` for the cross-framework data contract |

## Do not silently rewrite these

These files either encode a historical record, a literature anchor, or a safety invariant. Edits are fine *with a reason*; silent rewrites have caused real drift in this repo before (see the STATUS.md / code mismatch that `docs/AUDIT_04.md` had to unwind).

- `STATUS.md` — append-or-explicit-edit only. Every numerical claim here should be reproducible by running a test right now. If you change verified behavior, re-run the suite before updating the PASS list.
- `docs/AUDIT_0*.md` — historical audit trail. Never overwrite a past audit; start a new one (`AUDIT_05.md`, etc.) and link back.
- `docs/EQUATIONS.md` — equation tags (`[CORE] / [PLACEHOLDER] / [HEURISTIC] / [FRAGILE]`) are load-bearing. Changing a formula without updating the tag hides the scaffold→production transition.
- `docs/LITERATURE.md` — citation anchors (Case & Deaton, Kim 2024, Sciubba, etc.). Don't drop a citation without replacing it with an equally specific source.
- `tests/*` — never weaken an assertion to make a failing test pass. Either fix the code or write a *new* test that expresses the new intended behavior, and leave the old test's falsification signal intact.
- `accounting/regeneration.py::KNOWN_METRICS` and `DEFAULT_REGISTRY` — removing an entry silently under-reports cost. The `strict=True` refusal path depends on `KNOWN_METRICS`; see `tests/test_registry_safety.py`.
- `reserves/defaults.py` (`SECONDARY_SPECS`, tertiary pool capacities/cliffs) — numbers here are literature-anchored, not tunable knobs. Don't adjust without citing the new anchor in `docs/LITERATURE.md`.
- `thermodynamics/exergy.py` — the Gouy-Stodola invariant (`Exd ≥ 0`) is enforced here. Don't relax `check_nonnegative_destruction` or `check_closure` to make a test pass; if closure fails, the physics is wrong upstream.
- `docs/SCOPING_ECONOMIC_TERMS.md` and `term_audit/scoping.py::SCOPING_DIMENSIONS` — the scoping discipline that prevents training-bias re-anchoring to currency. Don't quietly drop dimensions or loosen `DeclaredScope` validators. Removing a dimension silently weakens the framework's resistance to narrative strip. Add new dimensions at the end; mark obsolete ones deprecated rather than deleting.
- `docs/TERMS_TO_AUDIT.md` and `term_audit/tiers.py` — the seven-tier list of terms the framework rubs against. The Tier 4 environment-vs-person framing and the Tier 6 AI-drift note are load-bearing handoffs for future sessions; `tests/test_tiers.py` tripwires against silent removal. Add terms to tiers as coverage grows; do not reorganize tiers without a commit message explaining why.
- `docs/PREEMPTING_ATTACKS.md` and the modules it points at (`term_audit/falsification.py`, `term_audit/contradictions.py`, `term_audit/counter_hypotheses.py`, plus the `measurement_layer()` / `incentive_layer()` methods on `TermAudit`) — the framework's defensive posture. Test 10 of `tests/test_preemption.py` asserts the `distinction_as_coordination` counter-hypothesis stays falsified; if you intend to support it, update the model AND the audit notes — that is not a soft change.

When in doubt, read the module docstring first — every module in this repo leads with a docstring that states its invariants. If your change violates one, either update the docstring with a stated reason or stop and ask.

## Known terms we rub against

The framework identifies a tiered list of terms as tokens occupying
signal-shaped positions in discourse without meeting
signal-definition criteria. Codified in `term_audit/tiers.py`; full
list with framing observations in `docs/TERMS_TO_AUDIT.md`.

- **Tier 1 — foundational fictions** (maximum resistance):
  `money`, `currency`, `capital`, `investment`, `value`, `wealth`,
  `economic_growth`, `gross_domestic_product`.
- **Tier 2 — labor and human-worth measurements**: `productivity`,
  `efficiency`, `performance`, `skill`, `qualification`,
  `credential`, `merit`, `unemployment`, `labor_market`,
  `human_capital`.
- **Tier 3 — organizational and institutional legitimacy**:
  `accountability`, `authority`, `leadership`, `expertise`,
  `governance`, `compliance`, `professionalism`, `best_practices`,
  `stakeholder`.
- **Tier 4 — mental and physical capacity measurements**:
  `disability`, `mental_illness`, `intelligence`, `iq`,
  `learning_disorder`, `adhd`, `autism_spectrum`, `normal` /
  `normative`, `functional`, `high_functioning` / `low_functioning`,
  `competence`, `rationality`.
- **Tier 5 — social and behavioral measurements**: `crime`,
  `deviance`, `addiction`, `risk`, `reliability`, `trust` (as
  institutionally measured), `radicalization`, `extremism`,
  `misinformation`.
- **Tier 6 — knowledge and truth measurements**: `evidence_based`,
  `peer_reviewed`, `consensus`, `credible_source`, `expert_opinion`,
  `data_driven`, `scientific`, `objective`.
- **Tier 7 — environmental and resource terms**: `natural_resource`,
  `ecosystem_services`, `carbon_credit`, `offset`, `sustainable`,
  `renewable`, `externality`.

**Three observations shape how to work the list.** They are
operational, not optional.

1. **The tiers are not independent.** Tier 1 is structurally
   load-bearing for Tiers 2–5. Productivity-in-dollars is not a
   signal if money is not a signal, and so on up the stack. Audit
   Tier 1 first and cite those audits rather than re-doing the
   foundational work each time.
2. **Tier 4 will hurt people, including allies.** The audit is NOT
   that the phenomena don't exist; it is that the measurement
   relocates failure from environment to person. Every Tier 4
   audit must make that distinction explicit and link to
   `distributional/institutional.py` (which already tracks the
   environment-fit categories: `fit_multiplier`, `trauma_tax`,
   `available_capacity`).
3. **Tier 6 is where AI drifts hardest.** "Peer-reviewed" and
   "evidence-based" are near-sacred in training corpora. An AI
   working Tier 6 will feel strong pull toward softening — hedges
   like "but peer review does serve an important function"
   appearing before the audit is complete. The hedge itself is
   the signal that the critique is landing. Complete the audit
   first; add contextualizing language only where the scoring
   specifically warrants it, not as a preemptive cushion.

## Things the framework intentionally does NOT do

Do not "fix" these by adding them unprompted — they are scoped out. In particular: no pricing, no external-data adapters (USDA/EPA/USGS are a future layer), no multi-period `simulate()` wrapper, no directional inter-basin coupling over time, no geographic-proximity model for cohort exposure, no trust hysteresis. See `STATUS.md § "What the framework does NOT do"` for the authoritative list.
