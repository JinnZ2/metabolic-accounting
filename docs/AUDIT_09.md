# AUDIT 09

Ninth audit pass. Scope: intake a user-supplied skeleton for a
first-principles legislative audit framework, fix the one construction-
time bug in the spec, install it at the declared path with the
repo's sys.path bootstrap convention, and tripwire it.

The module audits rules, regulations, and legislation against their
declared purpose, assumed context, and actual consequences. It does
not audit compliance with the rule — it audits the rule itself,
against reality.

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented; `[NAMED]` — real gap, not yet designed.


## Part A — What landed

### A.1 `term_audit/legislative_audit/` package   `[CLOSED]`

New package with two members:

- `__init__.py` — package header pointing at `docs/AUDIT_09.md` for
  origin and scope.
- `first_principles_legislative_audit.py` — core schema + two
  worked audits.

### A.2 Schema

Nine dataclasses capturing the audit surface:

- `FirstPrinciplesPurpose` — stated purpose, original problem,
  intended beneficiaries, purpose drift, capture.
- `ContextAssumption` — the environment the rule assumes.
- `ScopeBoundary` — where valid, where invalid, negative space,
  whether scope is declared in the rule text.
- `ConsequenceAnalysis` — primary/secondary/tertiary consequences,
  who bears them, measurable harm.
- `CounterfactualAnalysis` — what happens if the rule does not
  exist, who benefits from its absence, who suffers.
- `TransmissionEffect` — does knowledge transmission die because of
  the rule? (teaching_becomes_liability, knowledge_dies_with_holder,
  apprenticeship_discouraged, documentation_suppressed,
  chilling_effect).
- `ExceptionPathway` — is there a legitimate way out when the rule
  fails? Does the declared pathway function in practice?
- `ContradictionAnalysis` — does the rule contradict its own
  purpose? Where?
- `SubstrateEvidence` — physical evidence of the rule's effects
  (standing bridge, preventable death, knowledge that stopped).

Plus two enums:

- `EnvironmentType`: BUFFERED_STABLE / THIN_BUFFER / CONSTRAINED /
  AUSTERE / COLLAPSE.
- `ConsequenceBearer`: PRACTITIONER / BENEFICIARY / COMMUNITY /
  INSTITUTION / ENFORCER / FUTURE_GENERATIONS / SUBSTRATE.

### A.3 The composite: `LegislativeAudit`

Three behavioral methods alongside the data:

- `purpose_alignment_score()` — how well does the rule align with
  its own purpose? (0–1, seven weighted penalties/bonuses).
- `harm_score()` — estimated harm when out of scope (0–1).
- `context_validity(context)` — how valid in a specific environment?
  (0.9 / 0.2 / 0.5 for valid / invalid / undeclared).

Plus `summary()` (human-readable) and `to_ai_context()` (for AI
systems making routing decisions involving the rule).

### A.4 Two worked audits

- **Bridge Construction Permit Requirement in a Constrained Context.**
  Grandmaloon's bridge. Alignment 0.00, harm 1.00. Rule FAILS
  PURPOSE when enforced where delay causes preventable death.
  `contradicts_purpose=True`; exception pathway `functions_in_practice=False`.

- **Good Samaritan Protection (as applied).** Alignment 0.00, harm
  1.00. Rule intended to encourage help chills those most capable
  of helping. `discourages_transmission=True`,
  `knowledge_dies_with_holder=True`, `teaching_becomes_liability=True`.


## Part B — Drift caught at intake

### B.1 Typo in the bridge example   `[CLOSED]`

The supplied spec for `audit_bridge_permit_constrained()` passed
`alternative_mechanchanisms=[...]` (extra `ch`) to
`CounterfactualAnalysis`. The dataclass field is
`alternative_mechanisms`. This would have raised
`TypeError: CounterfactualAnalysis.__init__() got an unexpected
keyword argument 'alternative_mechanchanisms'` at module load time
on the first call to the example.

Fixed during intake; the module now imports and runs.


## Part C — Tests added

`tests/test_legislative_audit.py` (7 cases):

1. module imports cleanly
2. both example audits construct (regression for § B.1)
3. scores in [0, 1]; `summary()` and `to_ai_context()` render
   non-empty and include the rule name
4. `context_validity` returns 0.9 / 0.2 for the bridge audit's
   declared valid / invalid contexts
5. **bridge audit surfaces the contradiction** — load-bearing:
   `contradicts_purpose=True`, `prevents_intended_outcome=True`,
   `harms_intended_beneficiary=True`, exception pathway fails in
   practice. Alignment ≤ 0.4, harm ≥ 0.6. If this regresses the
   skeleton has stopped doing what it was built for.
6. **Good Samaritan surfaces the chilling effect** —
   `discourages_transmission=True`, `knowledge_dies_with_holder=True`,
   `teaching_becomes_liability=True`, `chilling_effect_observed=True`.
   Same load-bearing status.
7. `purpose_alignment_score` and `harm_score` respond monotonically
   to the fields they read. The two example audits both saturate at
   the [0,1] clamp, so the test builds a clean baseline via
   `dataclasses.replace()` where the raw score sits at 1.00, then
   flips inputs one at a time: `+contradiction` → 0.80, `+chill` →
   0.70. Confirms the weights are not collapsing signal through
   sign cancellation.

Full regression: **39/39 PASS** (pre-AUDIT_09: 38/38).


## Part D — What's NOT yet done (scoped for future passes)

### D.1 Provenance on scoring weights   `[OPEN]`

`purpose_alignment_score()` has 7 hard-coded weights (0.4, 0.1, 0.2,
0.1, 0.1, 0.2, 0.3, 0.2). `harm_score()` has 5 (0.3, 0.2, 0.2, 0.3,
0.2). `context_validity()` has 3 values (0.9, 0.2, 0.5). None carry
`Provenance` per the AUDIT_07 pattern.

All of these are `DESIGN_CHOICE` provenance targets. They need
`alternatives_considered` and `falsification_test` fields. The
Tier-1 retrofit pattern retrofitted data; retrofitting a function's
weights requires a different shape — either extract weights to
module-level named constants with companion `Provenance` records,
or introduce a `ScoringModel` dataclass carrying the weights plus
a `Provenance` each.

### D.2 `EnvironmentType` divergence   `[NAMED]`

The `EnvironmentType` in this module has members:
`BUFFERED_STABLE`, `THIN_BUFFER`, `CONSTRAINED`, `AUSTERE`,
`COLLAPSE`.

The `EnvironmentType` in `term_audit/signals/routing_around_detection.py`
(AUDIT_08) has members: `BUFFERED`, `THIN_BUFFER`, `CONSTRAINED`,
`COLLAPSE_RECOVERY`.

Parallel but divergent. A shared `term_audit/environment.py` with a
unified enum and both old names as aliases (for backward compat)
would close this. Not done in this pass to keep the intake minimal.

### D.3 JSON emitter for machine-readable output   `[OPEN]`

The user-supplied context included JSON examples showing credential-
scope (ASE mechanic, EMT, WFA) and regulation-scope (bridge permit,
Good Samaritan) documents. `LegislativeAudit.to_ai_context()` emits
a text-prose context, not JSON. A structured JSON emitter would
bridge to the credential-scope schema already anticipated in
`machine_readable_expertise.py`.

### D.4 Credential-scope audit   `[NAMED]`

The JSON examples also describe a `CredentialScope` shape
(environment_dependencies, validity_without_dependencies,
domain_boundaries per vehicle/context, handoff_assumed,
time_constraint_tolerance, buffer_requirements, negative_space).
This is a distinct audit target from `LegislativeAudit` — it audits
what a credential declares itself to be, not what a law does. Best
shipped as a sibling module: `term_audit/legislative_audit/
credential_scope.py` or `term_audit/audits/credential_scope.py`.

### D.5 More audits   `[OPEN]`

The user flagged: *"Every rule that touches constrained environments.
Every regulation that assumes buffer where buffer doesn't exist.
Every law that contradicts its own purpose when applied outside its
undeclared scope."* The skeleton is ready for that expansion; the
two examples establish the shape.


## Part E — Coverage snapshot

New surface added this audit:

| Surface | Total | Complete | Notes |
| --- | --- | --- | --- |
| Legislative audit schema | 9 dataclasses + 2 enums | 9/9 + 2/2 | — |
| Example audits | 2 | 2/2 | bridge permit, Good Samaritan |
| Scoring functions | 3 | 3/3 | tripwired for monotonicity |
| Provenance on scoring weights | ~15 magic numbers | 0/~15 | deferred to AUDIT_10+ |


## Part F — Recommended next actions

Ordered by cost:

1. **[SAFE]** Credential-scope audit module per § D.4. Same pattern
   as the legislative skeleton; structurally parallel.
2. **[SAFE]** Unify `EnvironmentType` per § D.2. Mechanical alias.
3. **[MEDIUM]** Apply the AUDIT_07 provenance pattern to the
   scoring-function weights per § D.1. This requires a small
   `ScoringWeights` dataclass carrying each weight + its
   `Provenance`. Design decision: do it per-function or in a single
   registry.
4. **[MEDIUM]** JSON emitter per § D.3. Bridges to the
   `machine_readable_expertise` JSON-LD pattern already in the tree.
5. **[LARGE]** Populate more audits per § D.5.


## Close-out

- Skeleton landed at the path the module's own docstring declared.
- sys.path bootstrap added for consistency with the rest of the tree.
- One construction-time typo fixed at intake (`alternative_mechan-
  chanisms` → `alternative_mechanisms`).
- 7-case tripwire locks in: constructibility, score bounds,
  context_validity discrimination, bridge contradiction,
  Good Samaritan chilling effect, and scoring-function monotonicity.
- Regression 39/39 green. Main stack untouched; first-law closure
  unchanged.
- Five items scoped for future passes (provenance on weights, enum
  unification, JSON emitter, credential-scope audit, more audits).
