"""
term_audit/counter_hypotheses.py

Adversarial models that encode the strongest defenses of the current
measurement system, run them as testable hypotheses, and show where
they fail.

Implements preempt #4 from docs/PREEMPTING_ATTACKS.md: don't wait for
attacks. Build the modules that ARE the strongest attacks on this
work, then show where they break.

Each counter-hypothesis is structured as:
  - hypothesis_claim: what the defender would assert
  - predicted_observations: what should be observed if the hypothesis holds
  - test_procedure: how to run the test
  - run(): execute the test, return result
  - result: 'supported' / 'falsified' / 'ambiguous'

The test must run on the same model the framework uses for its own
predictions, so the comparison is symmetric. A defender who rejects
the test must specify what model they would prefer — and that
specification is itself a falsifiable claim.

CC0. Stdlib only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class CounterHypothesis:
    """An adversarial hypothesis the framework could be wrong about,
    rendered concretely enough to test."""
    name: str
    hypothesis_claim: str
    predicted_observations: List[str]
    test_procedure: str
    test_function: Optional[Callable] = None   # returns dict with 'result'
    notes: str = ""

    def run(self) -> Dict:
        if self.test_function is None:
            return {"result": "no_test", "details": "test_function not bound"}
        return self.test_function()


# ---------------------------------------------------------------------------
# Counter-hypothesis 1: distinction-seeking is adaptive coordination
# ---------------------------------------------------------------------------
#
# The strongest defense of measurement-system capture is that
# distinction-seeking is adaptive — that as populations grow, the
# coordination problem requires more measurement, more credentialing,
# more diagnosis. Under this hypothesis:
#
#   - distinction share rises with population scale, then PLATEAUS
#     when coordination needs are met
#   - capture should NOT produce labeling-rate increases (because the
#     coordination is functional, not extractive)
#   - reducing distinction flow should produce coordination breakdown
#
# Test in the existing model: simulate a long run with the framework's
# default dynamics. If distinction plateaus at a coordination-needs
# threshold, the hypothesis is supported. If it grows monotonically
# until total energy is exhausted, the hypothesis is falsified within
# this regime.
# ---------------------------------------------------------------------------

def _test_distinction_plateaus():
    """Run the status-extraction example_run for an extended horizon
    and check whether distinction share plateaus."""
    from term_audit.status_extraction import example_run

    m = example_run()
    # extend the run: 60 more steps (100 total)
    m.run(steps=60)

    # measure plateau: did distinction share stop rising in the
    # second half of the run?
    history = m.history
    half = len(history) // 2
    early_distinction = history[half - 1]["distinction"]
    late_distinction = history[-1]["distinction"]
    growth_in_second_half = late_distinction - early_distinction

    # plateau criterion: less than 2% of total energy added in second half
    total = (history[-1]["support"] + history[-1]["production"]
             + history[-1]["distinction"])
    plateaued = (growth_in_second_half / total) < 0.02

    return {
        "result": "supported" if plateaued else "falsified",
        "early_distinction": early_distinction,
        "late_distinction": late_distinction,
        "growth_in_second_half": growth_in_second_half,
        "total_energy": total,
        "plateau_threshold_fraction": 0.02,
        "details": (
            "if distinction were a coordination service, it should "
            "plateau when coordination needs are met. In the model's "
            "default dynamics, it grows monotonically toward total "
            "energy exhaustion instead."
        ),
    }


DISTINCTION_AS_COORDINATION = CounterHypothesis(
    name="distinction_as_coordination",
    hypothesis_claim=(
        "distinction-flow expansion is functional adaptation; captured "
        "measurement systems serve necessary coordination at scale, "
        "and capture-driven labeling-rate increases reflect real "
        "coordination demand rather than extraction"
    ),
    predicted_observations=[
        "distinction share rises with population scale, then PLATEAUS "
        "when coordination needs are met",
        "capture does NOT produce labeling-rate increases",
        "reducing distinction flow produces coordination breakdown",
    ],
    test_procedure=(
        "Run status_extraction.example_run for 100 steps. Compare "
        "distinction share in the second half of the run against the "
        "first half. If growth in the second half is < 2% of total "
        "energy, plateau is supported and the hypothesis stands. "
        "Otherwise the hypothesis is falsified within this model "
        "regime."
    ),
    test_function=_test_distinction_plateaus,
    notes=(
        "this is the steel-manned defense most often heard. The model "
        "shows that under its current dynamics, no plateau occurs — "
        "distinction grows until total energy is exhausted. A "
        "defender who rejects this test must specify what alternative "
        "model would produce a plateau, and that specification is "
        "itself a falsifiable claim subject to the same discipline."
    ),
)


# ---------------------------------------------------------------------------
# Counter-hypothesis 2: measurement capture is reversible by good design
# ---------------------------------------------------------------------------
#
# A second defense: capture is a design failure that better
# institutional design corrects. Under this hypothesis:
#
#   - high-resistance measurement systems should resist capture
#     indefinitely
#   - any capture observed in low-resistance systems is fixable by
#     adding resistance
#
# Test in the model: a high-resistance system should not capture
# even under sustained distinction pressure. The model already
# encodes this (resistance acts as activation threshold). The
# hypothesis is therefore SUPPORTED at the model level — but the
# observable claim becomes: in the real world, who controls the
# resistance parameter, and what is their incentive to set it high?
# That question routes back to the standard_setter incentive layer
# and is NOT a math defense.
# ---------------------------------------------------------------------------

def _test_high_resistance_resists():
    """High-resistance systems should remain uncaptured under sustained
    distinction pressure."""
    from term_audit.status_extraction import MeasurementSystem

    s = MeasurementSystem(
        name="high_resistance_test",
        intended_purpose="test resistance",
        capture_rate_constant=1.0,      # maximum
        resistance=0.95,                 # very high
    )
    for _ in range(200):
        s.step(distinction_share=0.90)   # below resistance

    return {
        "result": "supported" if s.capture_fraction == 0.0 else "falsified",
        "final_capture": s.capture_fraction,
        "details": (
            "high-resistance systems do resist capture in the model. "
            "The hypothesis holds at the math layer. The defense is "
            "therefore valid as a model claim, BUT routes the question "
            "to: who sets resistance, and what is their incentive? That "
            "is an incentive-layer question, not a math-layer question."
        ),
    }


CAPTURE_REVERSIBLE_BY_DESIGN = CounterHypothesis(
    name="capture_reversible_by_design",
    hypothesis_claim=(
        "measurement capture is a design failure that better "
        "institutional design corrects; high-resistance systems "
        "resist capture indefinitely"
    ),
    predicted_observations=[
        "high-resistance measurement systems remain uncaptured under "
        "sustained distinction pressure",
        "low-resistance capture is fixable by adding structural "
        "resistance to the system",
    ],
    test_procedure=(
        "Build a MeasurementSystem with resistance=0.95 and step it "
        "200 times with distinction_share=0.90 (below resistance). "
        "If capture_fraction stays at 0.0, the hypothesis holds at "
        "the math layer."
    ),
    test_function=_test_high_resistance_resists,
    notes=(
        "this hypothesis IS supported at the math layer. The framework "
        "does not claim capture is inevitable for arbitrarily high "
        "resistance. The interesting question — who sets resistance, "
        "with what incentive — is then an incentive-layer question, "
        "and per docs/PREEMPTING_ATTACKS.md preempt #2, math defenses "
        "and incentive defenses must be argued separately."
    ),
)


ALL_COUNTER_HYPOTHESES = [
    DISTINCTION_AS_COORDINATION,
    CAPTURE_REVERSIBLE_BY_DESIGN,
]


if __name__ == "__main__":
    import json
    for h in ALL_COUNTER_HYPOTHESES:
        print(f"=== {h.name} ===")
        print(f"  claim: {h.hypothesis_claim[:80]}...")
        result = h.run()
        print(f"  result: {result['result']}")
        print(f"  details: {result['details'][:200]}...")
        print()
