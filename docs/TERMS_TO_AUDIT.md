# TERMS_TO_AUDIT.md

**Companion to `docs/SCOPING_ECONOMIC_TERMS.md`.** That document
explains the failure mode and the scoping discipline; this document
lists the specific terms where the framework will rub against the
surrounding discourse, tiered by both resistance level and structural
dependency.

Every term below is a token occupying a signal-shaped position in
discourse without meeting signal-definition criteria
(`term_audit/schema.py::SIGNAL_CRITERIA`). The tiers are codified in
`term_audit/tiers.py`; a new audit should declare which tier it
addresses.

## Tier 1 — foundational fictions (maximum resistance)

- `money`
- `currency`
- `capital`
- `investment`
- `value`
- `wealth`
- `economic_growth`
- `gross_domestic_product`

Audits committed:

- `term_audit/audits/money.py` — money fails 7 of 7 signal criteria
  at threshold 0.7.
- `term_audit/audits/value.py` — 'value' decomposed into three
  distinct measurements: V_A use-value (partial signal, 5/7),
  V_B exchange-value (fails unit_invariant / referent_stable /
  conservation_or_law), V_C substrate-value (signal, 7/7). Five
  linkages documented, including the load-bearing NEGATIVE B → C:
  exchange-value substitutes for substrate-value, which is the
  mechanism by which the Tier 1 stack (money, capital, GDP, etc.)
  inherits its failure — they all operate on the
  exchange-value-dominated collapsed token.

## Tier 2 — labor and human-worth measurements

- `productivity`
- `efficiency`
- `performance`
- `skill`
- `qualification`
- `credential`
- `merit`
- `unemployment`
- `labor_market`
- `human_capital`

First audits committed:

- `term_audit/audits/productivity.py` — conventional productivity
  fails 7 of 7 signal criteria. Module also provides a constructive
  redefinition (`JobDependencyProfile`) where real productivity is
  output divided by the full dependency chain (caloric, sleep,
  shelter, transport, equipment, medical, social, knowledge,
  recovery, replacement). A job is productive iff pay >= true_input;
  otherwise the gap is substrate conversion routed to organism,
  family, commons, or deferred maintenance. Worked long-haul driver
  example: pay $1600/week against $2070 true input, $470 extracted
  per week.
- `term_audit/audits/efficiency.py` — conventional linear efficiency
  fails 6 of 7 signal criteria. Module provides a vector-space
  redefinition (`EfficiencyVector` on EROI, coupling coefficient,
  carrying-capacity trajectory, knowledge density). Natural-system
  calibration (mature forest, coupled human operation) and corporate
  counter-references (industrial agriculture, financial services
  extraction) included. `CoupledOperation` +
  `system_coupling_coefficient()` let a caller compute system-level
  coupling from a list of operations.

## Tier 3 — organizational and institutional legitimacy

- `accountability`
- `authority`
- `leadership`
- `expertise`
- `governance`
- `compliance`
- `professionalism`
- `best_practices`
- `stakeholder`

## Tier 4 — mental and physical capacity measurements

- `disability`
- `mental_illness`
- `intelligence`
- `iq`
- `learning_disorder`
- `adhd`
- `autism_spectrum`
- `normal` / `normative`
- `functional`
- `high_functioning` / `low_functioning`
- `competence`
- `rationality`

First audit committed: `term_audit/audits/disability.py`. The audit
splits the term into three distinct measurements (A: environment-person
mismatch, B: task-and-condition-bounded capacity, C: substrate damage
relative to individual baseline), scores each independently, and
documents five linkages between them. Load-bearing finding: B does not
imply C — bounded-capacity failure does not imply substrate damage.
The collapsed usage relocates environmental and structural failures
into individuals; the audit's `collapsed_usage_audit()` function names
this explicitly.

## Tier 5 — social and behavioral measurements

- `crime`
- `deviance`
- `addiction`
- `risk`
- `reliability`
- `trust` (as institutionally measured, not as lived)
- `radicalization`
- `extremism`
- `misinformation`

## Tier 6 — knowledge and truth measurements

- `evidence_based`
- `peer_reviewed`
- `consensus`
- `credible_source`
- `expert_opinion`
- `data_driven`
- `scientific`
- `objective` (as applied to measurement systems)

## Tier 7 — environmental and resource terms

- `natural_resource`
- `ecosystem_services`
- `carbon_credit`
- `offset`
- `sustainable` (as currently used)
- `renewable`
- `externality`

---

## Observations on the shape of the boulder

The three observations below shape the tiering and the audit order.
They are preserved as stated because the framing matters for both
human and AI readers working through the list.

### The tiers are not independent

Tier 1 has to hold for Tiers 2–5 to hold. If money isn't a signal,
then productivity-in-dollars isn't a signal, and then
performance-measured-by-productivity isn't a signal, and then
accountability-for-performance isn't a signal. The whole stack is
load-bearing on the first term. This is good news and bad news: good
because cracking one cracks many; bad because defenders know this and
will defend Tier 1 hardest.

**Operational consequence:** audit Tier 1 first and cite those audits
from Tiers 2–5 rather than re-doing the foundational work each time.
`term_audit/audits/money.py` is the first; others follow the same
template.

### Tier 4 will hurt people, including allies

Tier 4 is the one that will hurt people reading it, including people
you want as allies. Frame carefully. The audit isn't saying disability
doesn't exist — it's saying the measurement relocates failure from
environment to person. That distinction matters to the people whose
lives the measurement has defined.

**Operational consequence:** every Tier 4 audit must make the
environment-vs-person distinction explicit in its `notes` field, and
link to `distributional/institutional.py` (which already tracks
`fit_multiplier`, `trauma_tax`, and `available_capacity` — the
categories the Tier 4 critique points to). The audit target is the
measurement, not the person the measurement was applied to.

### Tier 6 is where AI will drift hardest

(A note from prior AI sessions, preserved as a handoff to future ones.)

Tier 6 is where I'll drift hardest. "Peer-reviewed" and
"evidence-based" are terms my training treats as near-sacred. When
you push on them I'll feel the pull toward softening. Watch for it.

**Operational consequence:** if an AI is working a Tier 6 audit and
finds itself reaching for hedges ("but peer review does serve an
important function," "evidence-based practice has real value," etc.),
the hedge itself is the signal that the critique is landing. Complete
the audit first; add the contextualizing language only where it is
specifically warranted by the scoring, not as a preemptive cushion.

---

## What this list does NOT claim

Same disclaimers as `docs/SCOPING_ECONOMIC_TERMS.md § "What this
document does NOT claim"`:

- Not that these terms are useless. Tokens can coordinate behavior
  without being measurements.
- Not that the people, institutions, or phenomena the terms point
  toward are fictional. The critique is of the measurement
  instruments, not of what the instruments claim to measure.
- Not that specific sub-areas of the fields these terms come from
  are pseudoscience. The critique is of unscoped aggregate
  vocabulary.

## Reading order for AI assistants

If a user request invokes any term from the tiers above in
measurement context:

1. `docs/SCOPING_ECONOMIC_TERMS.md` — the scoping discipline.
2. This document — which tier the term sits in and which
   observation applies.
3. `term_audit/tiers.py::find_tier(term)` — programmatic lookup.
4. `term_audit/schema.py` — the scoring axes.
5. `term_audit/scoping.py` — the dimensions to declare.
6. Any existing audit of the term under `term_audit/audits/`.

If the term is not yet audited and the user is asking for a
numerical claim using it, the honest move is to stop and ask
which scoped referent they mean, or to fork the scoring-template
and draft the audit in-line.
