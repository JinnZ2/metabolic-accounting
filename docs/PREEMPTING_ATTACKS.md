## PREEMPTING_ATTACKS.md

The framework is going to face attacks. Most defenses of the current
measurement system are defenses of incentive structures dressed as
defenses of measurement validity. This document encodes seven
preempts that force the attacker to either run a falsification test
and show the math is wrong, OR admit they are defending the incentive
structure and not the measurement.

Each preempt is paired with the code or doc that operationalizes it.
"In the documentation only" is not enough — every preempt must be
something a future contributor can run against, otherwise it is
rhetoric.

## 1. Demand falsifiability at every step

Every claim about framework behavior is expressible as: under
conditions C, the framework predicts observation O. If O is not
observed, the claim is falsified. Claims that cannot be cast in this
form are rhetoric, not arguments — the framework refuses to engage
with them as if they were arguments.

**Encoded in:**
- `term_audit/falsification.py` — `FalsifiablePrediction`,
  `PredictionRegistry`. A prediction is `is_falsifiable()` only when
  it has a stated condition, a predicted observation, and a
  falsification test. Predictions without these surface in
  `PredictionRegistry.unfalsifiable()` — the framework auditing
  itself.
- `term_audit/status_extraction.py::FALSIFIABLE_PREDICTIONS` — five
  numbered predictions, each with `claim` and `falsification`.
- `term_audit/audits/disability.py::Linkage.falsification_test` —
  every linkage between A, B, C measurements has a test procedure.
- The repo discipline (CLAUDE.md, STATUS.md): no claim about
  framework behavior without a test that produces it.

## 2. Separate the measurement layer from the incentive layer

Attacks come in two forms: "your math is wrong" and "your incentive
analysis is unfair." Keep these separate. The math either holds or
it doesn't. The incentive analysis either identifies real incentives
or it doesn't. An attack on one is not an attack on both.

**Encoded in:**
- `term_audit/schema.py::TermAudit.measurement_layer()` and
  `incentive_layer()` — explicit methods that return the math half
  and the incentive half of the audit independently. A critic must
  declare which they are attacking.
- `term_audit/counter_hypotheses.py::CAPTURE_REVERSIBLE_BY_DESIGN` —
  worked example: a hypothesis that holds at the math layer but routes
  the live question to the incentive layer. The framework's response
  is to mark the math claim supported AND name the incentive question
  explicitly.

## 3. Build redundant derivations

Get to the same conclusion from three different angles. If
`status_extraction.py` shows distinction-seeking contracts support,
show it also from (a) direct energy accounting, (b) historical
capture-rate data on specific measurement systems, (c)
game-theoretic modeling of why labelers prefer captured measurements.
If all three converge, the attack vector shrinks — a critic would
have to crack all three independently.

**Encoded in:**
- `term_audit/status_extraction.py` — derivation (a): direct energy
  accounting with first-law conservation enforced (see
  `tests/test_status_extraction.py::test_1_energy_conservation`).
- (b) and (c) are scoped as future work. The structure for adding
  them is the same `CounterHypothesis` shape from
  `counter_hypotheses.py`: register the derivation with its
  `predicted_observations` and `test_function`, run it, compare the
  conclusion against the energy-accounting derivation.

This is the preempt with the longest implementation runway. The
framework currently has one derivation; the goal is three.

## 4. Encode the attack vectors themselves as test cases

Don't wait for attacks. Build the modules that ARE the strongest
attacks on the framework's own work, then show why they fail.

**Encoded in:**
- `term_audit/counter_hypotheses.py` — `CounterHypothesis` dataclass
  with `hypothesis_claim`, `predicted_observations`, `test_procedure`,
  and a runnable `test_function`. Two worked examples:
  - `DISTINCTION_AS_COORDINATION` — the steel-manned defense that
    distinction-seeking is functional adaptation. Falsified within
    the model regime: distinction grows monotonically toward energy
    exhaustion rather than plateauing.
  - `CAPTURE_REVERSIBLE_BY_DESIGN` — supported at the math layer,
    routes the question to the incentive layer (preempt #2).
- `tests/test_preemption.py` runs both and asserts the documented
  results.

Adding a new counter-hypothesis is one new entry in
`ALL_COUNTER_HYPOTHESES`.

## 5. Make the standard-setter incentive explicit and local

Every term audit includes who sets the standard, what they gain by
its current form, AND what they lose if it gets audited and replaced.
The pair makes incentive defenses visible — when a defender of the
current system speaks, their incentive is already documented.

**Encoded in:**
- `term_audit/schema.py::StandardSetter.loss_if_audited` — the
  symmetric counterpart to `incentive_structure`. Optional default
  empty for backward compatibility, but `is_loss_documented()`
  surfaces unfilled fields, and
  `TermAudit.incomplete_loss_documentation()` reports them across
  the audit's standard-setters.

Existing audits (money, disability) were committed before this field
existed; they will be backfilled in a separate commit so the
backfill is reviewable independently.

## 6. Document every assumption as a boundary condition

Not as "this might be wrong" but as "this model is valid in regime X
and breaks down at boundary Y." When the current measurement system
silently assumes the boundary doesn't exist, that is the attack
vector to surface.

**Encoded in:**
- `term_audit/falsification.py::BoundaryCondition` — `regime_description`,
  `valid_when`, `breaks_when`, `breakdown_signal`, `source_refs`.
  `is_documented()` is True only when all four load-bearing fields
  are non-empty.
- `term_audit/schema.py::TermAudit.boundary_conditions` — list of
  BoundaryCondition attached to each audit.

## 7. Build a contradiction-checker

If someone claims the current system is coherent, run their claims
through the checker. Does "money is a stable signal" coexist with
"monetary value varies by jurisdiction, time, and legal regime"? No.
Encode that. Make it automated.

**Encoded in:**
- `term_audit/contradictions.py`:
  - `Claim` dataclass — referent, asserted_property, text, source,
    optional declared_scope.
  - `MUTUALLY_EXCLUSIVE` registry of property pairs that cannot both
    hold for the same referent (stable/varying, conserved/created,
    observer-invariant/observer-dependent, etc.).
  - `check_contradictions(claims)` — pairwise structural detector.
  - `KNOWN_CONTRADICTIONS` — pre-registered historical contradictions
    that defenders of the current system commonly assert
    simultaneously. Acts as both a documentation surface and a smoke
    test of the detector itself.
- `tests/test_preemption.py` exercises the detector against the
  known-contradictions set; every registered pair must surface.

## The core move

Once these seven preempts are in place, every attack on the
framework must take one of two shapes:

1. **A falsification test**, run under the documented conditions,
   that shows a specific prediction does not hold. The framework
   responds by examining the test and either accepting the
   falsification (fixing the model) or pointing to the boundary
   condition the test crossed.

2. **An admission of incentive defense**, in which case the
   discussion moves out of the math layer into the standard-setter
   layer, where the defender's incentive is already documented and
   visible.

Attacks that take any other shape are rhetoric. The framework refuses
to engage with rhetoric on math terms.
