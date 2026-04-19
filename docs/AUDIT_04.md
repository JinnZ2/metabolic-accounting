# AUDIT 04

Fourth audit pass, following the community-basin probe that surfaced
Bugs 1–4 in the prior session. This pass had two goals:

1. Verify STATUS.md's claim that Bugs 1 and 4 were fixed.
2. Scope Bugs 2 and 3, which STATUS.md acknowledged as open.

Status key used throughout: `[CLOSED]` — fix present and covered by a
test that produces the stated behavior; `[OPEN]` — gap documented but
not yet implemented.


## Part A — Verification of prior-session claims

STATUS.md asserted that Bugs 1 and 4 were fixed in-session, and that
the fixes were covered by `tests/test_tier_vector.py`. Running the
suite against the committed tree showed that neither was true at the
start of this audit:

- `tests/test_tier_vector.py` did not exist on disk (STATUS.md listed
  it among 18 passing suites; the tree held 17).
- `distributional/tiers.py::determine_tier_for_basin` still used the
  broken `fraction_remaining < 0` check. No `_metric_past_cliff` or
  `_metric_near_cliff` symbols existed anywhere in the source.
- `distributional/access.py::apply_tier_to_cohorts` accepted only
  `cohort_load_multipliers` and called `tier_assignment.overall_tier()`
  unconditionally — the scalar collapse Bug 4 describes.
- `DEFAULT_TERTIARY_MAPPING` contained only `soil / water / air /
  biology`; no `community` entry.
- `AccessReport` had no `per_cohort_structural_load` field.

Interpretation: STATUS.md was written as if the fixes had landed, but
only the prose did. This matches the discipline warning STATUS.md itself
states ("No claim about framework behavior without a test that produces
it") — and is exactly the failure mode that warning was written to
catch.

### Bug 1 — `[CLOSED]` this session

`distributional/tiers.py` now has `_metric_past_cliff` and
`_metric_near_cliff`. `_metric_past_cliff` compares state against
`basin.cliff_thresholds[key]` and honors `basin.high_is_bad` (state
`>= cliff` for contamination-style metrics, `<= cliff` for
capacity-style). `_metric_near_cliff` uses a 0.25 band of the
cliff-to-healthy range.

`DEFAULT_TERTIARY_MAPPING["community"]` routes the community basin type
to `social_fabric_reserve`, `generational_transmission`,
`institutional_stock`, `civic_trust_reserve` — the four social tertiary
pools already registered in `reserves/defaults.py`. Any of these past
cliff now promotes the community basin to BLACK.

Reproduces STATUS.md's canonical case: `civic_engagement=0.20` with
cliff `0.35` and capacity `1.2` now registers BLACK (prior: slipped
through to GREEN because `0.20/1.2 ≈ 0.167` is non-negative).

Covered by `tests/test_tier_vector.py::test_1..test_5, test_8`.

### Bug 4 — `[CLOSED]` this session

`apply_tier_to_cohorts` now takes an optional
`cohort_basin_sensitivities: Dict[str, Dict[str, float]]`. When
supplied for a cohort, the cohort's load is the weighted sum of
per-basin-type tier loads (weights are absolute, not normalized),
clipped to `[0, 1]`. When omitted, the legacy scalar path
(`overall_tier() * cohort_load_multiplier`) applies — this keeps every
existing call site working.

`AccessReport.per_cohort_structural_load: Dict[str, float]` is now
populated for every cohort regardless of path, so cohort-level exposure
is visible in the report output.

Reproduces STATUS.md's numeric case (DEFAULT_STRUCTURAL_LOAD_BY_TIER:
GREEN=0, BLACK=0.85):

```
community_members, sens={community: 1.5, soil: 0.4}
  load = 1.5 * 0.85 + 0.4 * 0.0 = 1.275  -> clip 1.0  -> 200/200 collapsed
capital_market,    sens={community: 0.1, soil: 0.1}
  load = 0.1 * 0.85 + 0.1 * 0.0 = 0.085              -> 0/500 collapsed
```

Covered by `tests/test_tier_vector.py::test_6, test_7`.

### Impact on the regression baseline

All seventeen pre-existing suites continued to pass after the fixes.
The new suite brings the count to eighteen — matching STATUS.md's
original claim, now truthfully.


## Part B — Bug 2 (open): no social / labor regulatory frameworks

`regulatory/frameworks.py` currently ships five jurisdictions, all
environmental:

- US CERCLA / Superfund
- EU Environmental Liability Directive
- UK Part 2A Contaminated Land regime
- Germany BBodSchG (Federal Soil Protection Act)
- Japan SCCA (Soil Contamination Countermeasures Act)

A firm that destroys community vitality — driving `civic_engagement`,
`generational_knowledge`, `youth_retention`, `economic_security`
through their cliffs — presently gets **zero** regulatory toe-in points
in the crosswalk, even when primary metrics past cliff justify BLACK.
This is a silent gap: the crosswalk output looks clean while the
community basin is collapsing.

### Candidate frameworks to add

Ordered by how cleanly they map onto the existing community basin
metrics. Each entry lists the metrics it would bind to so the crosswalk
can light up when those states degrade.

1. **US Title VI of the Civil Rights Act of 1964 (42 U.S.C. §2000d)**
   — federal funding conditioned on non-discrimination. Binds to
   `economic_security`, `social_capital` when differential basin
   damage falls on protected classes.

2. **US OSH Act / OSHA General Duty Clause (29 U.S.C. §654(a)(1))**
   — employer duty to provide a workplace "free from recognized hazards."
   Binds to `economic_security` and environmental basins where
   workplace exposure couples to basin state.

3. **US NLRA (29 U.S.C. §§151–169)** — right to organize. Binds to
   `social_capital` and `civic_engagement` via union density /
   voluntary association metrics in the literature anchor list.

4. **US ADA Title I (42 U.S.C. §12112)** — employment
   non-discrimination for disability. Couples to the institutional-fit
   layer (`distributional/institutional.py`) where `available_capacity`
   and `fit_multiplier` already track discrimination-adjacent signals.

5. **EU Social Climate Fund (Regulation (EU) 2023/955)** — funds to
   address social impacts of climate policy on vulnerable households.
   Binds to `economic_security`, `family_formation`, and to the
   `organizational_reserve` pool.

6. **ILO Core Conventions** (Nos. 29, 87, 98, 100, 105, 111, 138, 182)
   — the eight fundamental labor conventions. Binds to
   `economic_security`, `social_capital`, and cross-jurisdictionally
   to every community-substrate metric.

### Expected shape of the fix

Follow the existing `RegulatoryFramework` dataclass shape in
`regulatory/frameworks.py:42`. Each new framework needs:

- `short_name`, `jurisdiction`, `statutory_anchor`
- basin metrics it couples to (new field, or a typed tag on
  `triggering_conditions`)
- crosswalk triggers mapped onto tier / primary-metric-past-cliff /
  tertiary-past-cliff predicates

The crosswalk in `regulatory/crosswalk.py:173` already accepts short
names for lookup — extending it to route community-tier BLACK through
the social frameworks is a one-line dispatch change plus the framework
entries themselves.

No test exists yet that asserts social-framework triggering; the obvious
shape is a companion to `test_regulatory.py` that builds a community
basin past cliff and asserts the crosswalk returns at least one social
framework.


## Part C — Bug 3 (open): no community-specific mitigation patterns

`mitigation/actions.py` produces a ranked list of mitigation actions
from `identify_basin_actions` (basin-metric-driven) and
`identify_reserve_actions` (reserve-depletion-driven). Both paths are
generic: they operate on `BasinState.trajectory`, cliff distance, and
reserve fraction. This means the community basin's secondary and
tertiary pools DO surface when near cliff (the generic logic catches
them), but no action template recognizes the specific leverage patterns
that apply to community vitality.

Grepped `mitigation/actions.py` for `community | economic_security |
social_capital | civic_engagement | generational` — zero matches. The
module has no awareness that `economic_security` near cliff means
"invest in local employment diversity" rather than, say, "reduce
chemical load."

### Candidate action templates

Each should be a labelled entry similar to the existing
`MitigationAction` constructions around lines 274 / 312 / 334 / 358 /
381 in `mitigation/actions.py`. Minimum set to cover the six community
metrics:

| Trigger                                   | Action pattern                                                |
| ----------------------------------------- | ------------------------------------------------------------- |
| `economic_security` near cliff            | Diversify local employment; stabilize wage floor; purchase local |
| `social_capital` near cliff               | Fund libraries / unions / religious-civic-cultural institutions |
| `family_formation` near cliff             | Family-supportive scheduling; childcare; housing affordability |
| `youth_retention` near cliff              | Apprenticeships; pathways home for outmigrated youth         |
| `generational_knowledge` near cliff       | Trade-skill transmission programs; elder mentorship structures |
| `civic_engagement` near cliff             | Public-meeting access; civic time-off; participatory budgeting |
| `civic_trust_reserve` tertiary past cliff | External audit + institutional-reform commitment              |
| `institutional_stock` tertiary past cliff | Direct capital injection to community institutions            |
| `generational_transmission` tertiary past cliff | Re-establish apprenticeship / knowledge-holder structures     |
| `social_fabric_reserve` tertiary past cliff | Multi-year community-led regeneration plan                     |

### Expected shape of the fix

A new `_community_action_templates` registry mapping
`(basin_type="community", metric_key)` to a list of `MitigationAction`
factories. Called from `identify_basin_actions` when `basin.basin_type
== "community"`. Tertiary-pool-specific actions slot into
`identify_reserve_actions` keyed by pool name.

Suggested test: a companion to `test_mitigation.py` that builds a
community basin with `economic_security` near cliff and asserts the
report contains at least one action whose description references local
employment or wage stabilization.


## Part D — Hidden variables still missing

STATUS.md enumerates five hidden variables surfaced during the community
audit — none of them addressed by the Bug 1/4 fixes:

1. Directional coupling over time (community degradation causes
   environmental degradation)
2. Geographic proximity in cohort exposure
3. Generational lag in `potential_waste`
4. Trust hysteresis (sensitivity drop after `civic_trust_reserve` past
   cliff)
5. Temporal asymmetry between cohorts (capital forward-priced, community
   backward-realized)

Documented here for traceability; each deserves its own audit when it
moves toward implementation. None is a correctness bug in the current
scope — they are scope expansions that require new state variables,
not fixes to existing math.


## Close-out

- Bugs 1 and 4: CLOSED this session, covered by
  `tests/test_tier_vector.py` (8 new tests, all pass alongside the
  17 pre-existing suites).
- Bugs 2 and 3: documented above with candidate frameworks, action
  templates, and expected fix shapes. No code written.
- STATUS.md should be updated to reflect: (a) fixes actually landed
  this audit, (b) `test_tier_vector.py` now exists, (c) total suite
  count is 18, matching the original prose.
