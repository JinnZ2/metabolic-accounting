"""
term_audit/audits/money_three_scope_falsification.py

CC0. Stdlib-only.

Argument (load-bearing, structural):

    Money is marketed as a signal in at least three incompatible scopes:
        SCOPE_A  flow system        (glucose-type in/out measurement)
        SCOPE_B  community organism (shared-metabolism coordination signal)
        SCOPE_C  civilization lube  (system-wide lubrication / coupling medium)

    Each scope requires a different set of invariants to hold.
    Money simultaneously fails the invariants of all three.
    The failure is NOT coincidental. It is a necessary consequence of
    using a CONTROL MECHANISM (unilaterally movable by an exogenous
    entity) as a MEASUREMENT UNIT (requires stability, observer-
    invariance, conservation).

    A term cannot be both the ruler and the hand moving the ruler.

This module encodes that argument as falsifiable predictions + tests.
Each prediction has a PASS condition. Money fails every PASS condition.
If money EVER passes one, that prediction is falsified and the scope
claim for that framing is rescued. The tests are the tripwires.

Output is a structured verdict object feedable to the
metabolic_accounting_adapter.

Related modules:
  - term_audit/audits/money.py: the 7-criterion signal audit on money.
    This module is orthogonal and complementary — `money.py` audits
    the term against information-theoretic signal criteria; this
    module audits the term across three SCOPE framings. A term can
    fail the signal criteria for different reasons in different scopes.
  - term_audit/integration/metabolic_accounting_adapter.py: the real
    AssumptionValidatorFlag shape. See `emit_assumption_flags`
    below for a compatibility bridge; when the adapter is available
    the lite type is upgraded to the real one.
  - money_signal/: the coupling-matrix model of money-as-signal
    dynamics (base K_ij plus scope/cultural/attribution/observer
    modifiers). The three-scope audit asks whether money qualifies
    as a signal at all; money_signal/ characterizes how it couples
    when assumed to be one.

AUDIT_10 landing: cleaned chat-paste (smart quotes, `__future__`
tokens, indentation), split tests to `tests/test_money_three_scope_\
falsification.py`, added sys.path bootstrap.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Scope definitions
# ---------------------------------------------------------------------------

class Scope(Enum):
    FLOW_SYSTEM        = "flow_system"          # in/out, conserved, measurable
    COMMUNITY_ORGANISM = "community_organism"   # shared metabolism signal
    CIVILIZATION_LUBE  = "civilization_lube"    # system-wide coupling medium


@dataclass(frozen=True)
class ScopeInvariant:
    """A single invariant a term must satisfy to function inside a scope."""
    name: str
    description: str
    # Given the current state of `money`, does the invariant hold?
    # Returns (holds: bool, evidence: str).
    check: Callable[["MoneyState"], Tuple[bool, str]]


@dataclass(frozen=True)
class ScopeClaim:
    """A claim that money functions as a signal inside a given scope."""
    scope: Scope
    invariants: Tuple[ScopeInvariant, ...]
    # Why this scope REQUIRES these invariants (first-principles).
    rationale: str


# ---------------------------------------------------------------------------
# Observable money state (what the world actually looks like)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MoneyState:
    """
    Snapshot of the properties of money that the invariants interrogate.
    Populated from observable reality, not model assumptions.

    Every field is a claim about the current monetary regime. Flipping
    any field flips the corresponding invariant result. That is the
    falsification hook.
    """
    # FLOW_SYSTEM invariants probe these:
    unit_stable_over_time:          bool  # purchasing power preserved
    conserved_across_transactions:  bool  # no net creation/destruction mid-flow
    observer_invariant:             bool  # same unit means same thing for all
    regeneration_rate_endogenous:   bool  # user controls their own inflow rate

    # COMMUNITY_ORGANISM invariants probe these:
    signal_readable_by_all_members: bool  # every member can decode the signal
    signal_carries_substrate_info:  bool  # dollar reflects real substrate state
    no_single_actor_can_rewrite:    bool  # no unilateral redenomination
    failure_modes_symmetric:        bool  # hurts high and low earners equally

    # CIVILIZATION_LUBE invariants probe these:
    couples_without_extraction:     bool  # lubricates without siphoning
    phase_coherent_across_domains:  bool  # same $ same meaning across sectors
    degradation_visible_in_signal:  bool  # wear shows up in the lubricant
    replaceable_without_seizure:    bool  # can be swapped without system halt

    # Provenance: where each claim came from
    provenance: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Invariant checks
# ---------------------------------------------------------------------------

def _flow_invariants() -> Tuple[ScopeInvariant, ...]:
    return (
        ScopeInvariant(
            name="unit_stability",
            description="A flow signal requires a stable unit; otherwise in and out cannot be compared.",
            check=lambda s: (
                s.unit_stable_over_time,
                "inflation/deflation continuously moves the unit; fixed-income holders "
                "observe negative regeneration without any transaction occurring",
            ),
        ),
        ScopeInvariant(
            name="conservation",
            description="A flow signal conserves across transactions; creation events must be bookable.",
            check=lambda s: (
                s.conserved_across_transactions,
                "central bank creation and commercial bank credit expansion "
                "create money without a matching transaction entry at the user level",
            ),
        ),
        ScopeInvariant(
            name="observer_invariance",
            description="A flow signal means the same thing to every observer inside the system.",
            check=lambda s: (
                s.observer_invariant,
                "the same dollar is survival to one observer, optionality to another, "
                "and rounding error to a third; the unit is not observer-invariant",
            ),
        ),
        ScopeInvariant(
            name="endogenous_regeneration",
            description=(
                "For money to behave as glucose flow for an entity, the entity must "
                "have meaningful agency over its own regeneration rate."
            ),
            check=lambda s: (
                s.regeneration_rate_endogenous,
                "the regeneration rate is set exogenously (Fed policy, employer wage, "
                "benefit schedule); the entity whose basin is being audited does not "
                "hold the dial",
            ),
        ),
    )


def _community_invariants() -> Tuple[ScopeInvariant, ...]:
    return (
        ScopeInvariant(
            name="readable_by_all",
            description=(
                "A coordination signal in a community organism must be decodable "
                "by every member participating in the metabolism."
            ),
            check=lambda s: (
                s.signal_readable_by_all_members,
                "financial literacy is non-uniform by design; derivative instruments "
                "are opaque even to holders; the signal is not decodable by all members",
            ),
        ),
        ScopeInvariant(
            name="substrate_linkage",
            description=(
                "A community signal must carry information about the underlying "
                "substrate state, not just about itself."
            ),
            check=lambda s: (
                s.signal_carries_substrate_info,
                "price decouples from substrate during speculation, subsidy, and "
                "monopsony regimes; signal carries information about itself, not "
                "about soil/water/biology",
            ),
        ),
        ScopeInvariant(
            name="no_unilateral_rewrite",
            description=(
                "A shared signal cannot be unilaterally rewritten by a single "
                "actor without breaking coordination."
            ),
            check=lambda s: (
                s.no_single_actor_can_rewrite,
                "interest rate adjustments, quantitative easing, and redenominations "
                "rewrite the signal unilaterally from outside the community",
            ),
        ),
        ScopeInvariant(
            name="symmetric_failure",
            description=(
                "A community-organism signal must fail symmetrically; asymmetric "
                "failure means it is a coordination signal for one subset and a "
                "cage for another."
            ),
            check=lambda s: (
                s.failure_modes_symmetric,
                "inflation compresses fixed-income holders while asset holders gain; "
                "the failure mode is structurally asymmetric",
            ),
        ),
    )


def _civilization_invariants() -> Tuple[ScopeInvariant, ...]:
    return (
        ScopeInvariant(
            name="non_extractive_coupling",
            description="A lubricant couples surfaces without itself being a siphon.",
            check=lambda s: (
                s.couples_without_extraction,
                "interest, rent, and financial-layer fees are extraction built into "
                "the coupling medium; the lubricant is also a pump",
            ),
        ),
        ScopeInvariant(
            name="phase_coherence",
            description=(
                "A system-wide lubricant must carry the same meaning across "
                "coupled domains; otherwise it desynchronizes the system."
            ),
            check=lambda s: (
                s.phase_coherent_across_domains,
                "a dollar in healthcare, education, housing, and food is not the same "
                "dollar; sector-specific price dynamics break phase coherence",
            ),
        ),
        ScopeInvariant(
            name="wear_visibility",
            description=(
                "A real lubricant shows degradation in its own signal (color, "
                "viscosity, particulate load). A healthy civilization lube "
                "must show wear."
            ),
            check=lambda s: (
                s.degradation_visible_in_signal,
                "GDP growth reports can rise while soil, aquifer, social trust, and "
                "infrastructure degrade; wear is invisible in the monetary signal",
            ),
        ),
        ScopeInvariant(
            name="replaceable_without_seizure",
            description=(
                "A true lubricant can be swapped without halting the machine. "
                "If removing it seizes the system, it has become load-bearing "
                "in a way a lubricant must never be."
            ),
            check=lambda s: (
                s.replaceable_without_seizure,
                "removal of monetary medium halts supply chains, employment, and "
                "food distribution within days; the lubricant is load-bearing",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# The three scope claims
# ---------------------------------------------------------------------------

SCOPE_CLAIMS: Dict[Scope, ScopeClaim] = {
    Scope.FLOW_SYSTEM: ScopeClaim(
        scope=Scope.FLOW_SYSTEM,
        invariants=_flow_invariants(),
        rationale=(
            "A flow-system signal requires stable unit, conservation across "
            "transactions, observer invariance, and endogenous regeneration "
            "for the entity being audited. Without all four, in/out accounting "
            "is measuring noise in the unit rather than flow of the thing."
        ),
    ),
    Scope.COMMUNITY_ORGANISM: ScopeClaim(
        scope=Scope.COMMUNITY_ORGANISM,
        invariants=_community_invariants(),
        rationale=(
            "A community-organism coordination signal must be readable by all "
            "members, carry substrate information, not be unilaterally "
            "rewritable, and fail symmetrically. Asymmetric failure under "
            "external rewrite is the definition of a control surface, not a "
            "shared signal."
        ),
    ),
    Scope.CIVILIZATION_LUBE: ScopeClaim(
        scope=Scope.CIVILIZATION_LUBE,
        invariants=_civilization_invariants(),
        rationale=(
            "A civilization-scale lubricant must couple without extracting, "
            "maintain phase coherence across coupled domains, show wear in "
            "its own signal, and be replaceable without system seizure. A "
            "medium that fails all four is not lubricant; it is a load-bearing "
            "control structure misframed as lubricant."
        ),
    ),
}


# ---------------------------------------------------------------------------
# Verdict structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InvariantResult:
    scope: Scope
    invariant: str
    holds: bool
    evidence: str


@dataclass(frozen=True)
class ScopeVerdict:
    scope: Scope
    invariants_total: int
    invariants_passed: int
    invariants_failed: int
    results: Tuple[InvariantResult, ...]
    rationale: str

    @property
    def scope_claim_survives(self) -> bool:
        # The scope claim ("money works as a signal here") survives only if
        # every invariant required by that scope holds.
        return self.invariants_failed == 0


@dataclass(frozen=True)
class ThreeScopeVerdict:
    state: MoneyState
    per_scope: Tuple[ScopeVerdict, ...]

    @property
    def surviving_scopes(self) -> Tuple[Scope, ...]:
        return tuple(v.scope for v in self.per_scope if v.scope_claim_survives)

    @property
    def falsified_scopes(self) -> Tuple[Scope, ...]:
        return tuple(v.scope for v in self.per_scope if not v.scope_claim_survives)

    @property
    def structural_claim_holds(self) -> bool:
        # Load-bearing claim of this module:
        #   money fails as a signal in EVERY scope where it is marketed to work.
        # The claim HOLDS (argument stands) when no scope survives.
        # The claim is FALSIFIED when any scope survives.
        return len(self.surviving_scopes) == 0


# ---------------------------------------------------------------------------
# Audit runner
# ---------------------------------------------------------------------------

def run_scope(claim: ScopeClaim, state: MoneyState) -> ScopeVerdict:
    results: List[InvariantResult] = []
    for inv in claim.invariants:
        holds, evidence = inv.check(state)
        results.append(
            InvariantResult(
                scope=claim.scope,
                invariant=inv.name,
                holds=holds,
                evidence=evidence,
            )
        )
    passed = sum(1 for r in results if r.holds)
    failed = sum(1 for r in results if not r.holds)
    return ScopeVerdict(
        scope=claim.scope,
        invariants_total=len(results),
        invariants_passed=passed,
        invariants_failed=failed,
        results=tuple(results),
        rationale=claim.rationale,
    )


def audit_money_across_three_scopes(state: MoneyState) -> ThreeScopeVerdict:
    verdicts = tuple(
        run_scope(SCOPE_CLAIMS[scope], state)
        for scope in (Scope.FLOW_SYSTEM, Scope.COMMUNITY_ORGANISM, Scope.CIVILIZATION_LUBE)
    )
    return ThreeScopeVerdict(state=state, per_scope=verdicts)


# ---------------------------------------------------------------------------
# Observable state of money under the current regime
# ---------------------------------------------------------------------------

def current_regime_money_state() -> MoneyState:
    """
    Every flag is set to reflect the observable current regime.
    To falsify this module's structural claim, flip any flag to True
    and re-run: the corresponding scope's invariant will then hold,
    and if enough hold, that scope's claim survives.

    That is the tripwire. The argument is only as strong as these flags
    remaining False under honest observation.
    """
    return MoneyState(
        # FLOW_SYSTEM
        unit_stable_over_time          = False,
        conserved_across_transactions  = False,
        observer_invariant             = False,
        regeneration_rate_endogenous   = False,
        # COMMUNITY_ORGANISM
        signal_readable_by_all_members = False,
        signal_carries_substrate_info  = False,
        no_single_actor_can_rewrite    = False,
        failure_modes_symmetric        = False,
        # CIVILIZATION_LUBE
        couples_without_extraction     = False,
        phase_coherent_across_domains  = False,
        degradation_visible_in_signal  = False,
        replaceable_without_seizure    = False,
        provenance={
            "unit_stable_over_time":          "observable: CPI, purchasing power series",
            "conserved_across_transactions":  "observable: M2 expansion, bank credit creation",
            "observer_invariant":             "observable: marginal utility nonlinearity across income strata",
            "regeneration_rate_endogenous":   "observable: fixed-income indexation vs policy rate",
            "signal_readable_by_all_members": "observable: financial literacy distributions, derivative opacity",
            "signal_carries_substrate_info":  "observable: commodity price vs ecological state divergence",
            "no_single_actor_can_rewrite":    "observable: central bank policy announcements",
            "failure_modes_symmetric":        "observable: asset vs wage inflation divergence",
            "couples_without_extraction":     "observable: interest, rent, finance-sector share of GDP",
            "phase_coherent_across_domains":  "observable: sectoral price indices (healthcare, education, housing)",
            "degradation_visible_in_signal":  "observable: GDP growth vs soil/aquifer/trust indicators",
            "replaceable_without_seizure":    "observable: historical monetary seizure events, supply-chain fragility",
        },
    )


# ---------------------------------------------------------------------------
# Adapter hook for metabolic_accounting
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AssumptionValidatorFlagLite:
    """
    Minimal surface matching term_audit/integration/metabolic_accounting_adapter.py
    AssumptionValidatorFlag. Kept local so this module stays importable in
    isolation. `emit_assumption_flags` is the bridge; callers running inside
    the full tree can map these to the real adapter type via
    `to_real_flag(...)` below.

    Audit note (AUDIT_10): the real `AssumptionValidatorFlag` uses
    `source_audit`/`failure_mode`/`severity: float`/`message`. This lite
    type uses `source`/`reason`/`severity: str` per the original spec.
    Field names and severity types differ. `to_real_flag()` resolves
    both.
    """
    source: str
    reason: str
    severity: str   # "info" | "warning" | "blocker"


_SEVERITY_FLOAT = {
    "info":     0.1,
    "warning":  0.5,
    "blocker":  1.0,
}


def to_real_flag(lite: "AssumptionValidatorFlagLite", failure_mode: str):
    """Bridge lite -> real AssumptionValidatorFlag.

    The real adapter type has fields the lite type does not carry
    ('failure_mode' — which signal criterion is violated) and uses a
    float severity. This helper provides the mapping:

        lite.source   -> real.source_audit
        lite.reason   -> real.message
        lite.severity -> real.severity (str -> float via _SEVERITY_FLOAT)
        failure_mode  -> real.failure_mode   (caller-supplied)

    The module does not import the adapter at top level so it remains
    usable without the rest of the tree; this import is lazy.
    """
    from term_audit.integration.metabolic_accounting_adapter import (
        AssumptionValidatorFlag,
    )
    sev = _SEVERITY_FLOAT.get(lite.severity, 1.0)
    return AssumptionValidatorFlag(
        source_audit=lite.source,
        failure_mode=failure_mode,
        severity=sev,
        message=lite.reason,
    )


def emit_assumption_flags(verdict: ThreeScopeVerdict) -> Tuple[AssumptionValidatorFlagLite, ...]:
    """
    For every scope whose claim is falsified, emit a blocker flag so that
    any downstream metabolic-accounting run using money as a signal in that
    scope is forced to justify why.
    """
    flags: List[AssumptionValidatorFlagLite] = []
    for sv in verdict.per_scope:
        if not sv.scope_claim_survives:
            failed_names = ", ".join(
                r.invariant for r in sv.results if not r.holds
            )
            flags.append(
                AssumptionValidatorFlagLite(
                    source=f"money_three_scope_falsification:{sv.scope.value}",
                    reason=(
                        f"money claimed as signal in scope '{sv.scope.value}', "
                        f"but {sv.invariants_failed}/{sv.invariants_total} "
                        f"invariants fail ({failed_names})"
                    ),
                    severity="blocker",
                )
            )
    return tuple(flags)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_verdict(v: ThreeScopeVerdict) -> None:
    print("=" * 72)
    print("money: three-scope falsification audit")
    print("=" * 72)
    for sv in v.per_scope:
        print(f"\nSCOPE: {sv.scope.value}")
        print(f"  rationale: {sv.rationale}")
        print(f"  invariants: {sv.invariants_passed}/{sv.invariants_total} hold")
        for r in sv.results:
            mark = "HOLD" if r.holds else "FAIL"
            print(f"    [{mark}] {r.invariant}")
            print(f"           {r.evidence}")
        print(f"  scope_claim_survives: {sv.scope_claim_survives}")

    print("\n" + "-" * 72)
    print(f"surviving scopes:  {[s.value for s in v.surviving_scopes]}")
    print(f"falsified scopes:  {[s.value for s in v.falsified_scopes]}")
    print(f"structural claim (money fails in all three scopes) holds: "
          f"{v.structural_claim_holds}")
    print("-" * 72)

    flags = emit_assumption_flags(v)
    print(f"\nassumption flags emitted: {len(flags)}")
    for f in flags:
        print(f"  [{f.severity.upper()}] {f.source}")
        print(f"    {f.reason}")


if __name__ == "__main__":
    _print_verdict(audit_money_across_three_scopes(current_regime_money_state()))
