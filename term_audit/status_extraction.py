"""
term_audit/status_extraction.py

Distinction-seeking as a thermodynamic sink on environmental support
capacity.

Core claim: human status-distinction activity captures measurement
systems, and captured measurement systems divert environmental support
capacity away from the organisms the environment would otherwise
sustain. This produces a self-reinforcing loop that defunds recovery,
maintenance, and basin regeneration while expanding the labeled
population that requires support that is no longer available.

Companion to the static term audits in term_audit/audits/. Where
audits/disability.py shows what one captured term looks like at rest,
status_extraction.py shows the dynamics by which capture proceeds.
The two together explain both the snapshot and the trajectory.

This module is a skeleton model. It is not calibrated to any specific
dataset. It is structured to be calibratable against any population
where the relevant flows can be measured.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math


# ---------------------------------------------------------------------------
# Energy accounting
# ---------------------------------------------------------------------------
#
# A population's available energy for environmental support is finite at
# any given time. That energy flows into one of three sinks:
#
#   SUPPORT_FLOW      energy spent maintaining the environment that
#                     sustains organisms (food systems, medical care,
#                     housing, knowledge transmission, maintenance of
#                     physical infrastructure, ecological regeneration)
#
#   PRODUCTION_FLOW   energy spent producing new output (goods, services,
#                     knowledge, art)
#
#   DISTINCTION_FLOW  energy spent creating, maintaining, and enforcing
#                     distinction between persons (credentialing systems,
#                     diagnostic systems, ranking systems, measurement
#                     bureaucracies, status displays, enforcement of
#                     labeling outcomes)
#
# Total energy is conserved at the system level:
#
#   SUPPORT_FLOW + PRODUCTION_FLOW + DISTINCTION_FLOW = TOTAL_ENERGY
#
# Distinction flow is energetically cheap per unit of status generated,
# which makes it a low-resistance sink. Without active structural
# constraint, it grows at the expense of the other two.
# ---------------------------------------------------------------------------

@dataclass
class EnergyFlows:
    """Energy budget of a population or subsystem, in arbitrary but
    consistent units."""
    support: float
    production: float
    distinction: float

    @property
    def total(self) -> float:
        return self.support + self.production + self.distinction

    def fractions(self) -> Dict[str, float]:
        t = self.total
        if t == 0:
            return {"support": 0.0, "production": 0.0, "distinction": 0.0}
        return {
            "support": self.support / t,
            "production": self.production / t,
            "distinction": self.distinction / t,
        }


# ---------------------------------------------------------------------------
# Environmental support capacity and tolerance band
# ---------------------------------------------------------------------------
#
# An environment has a tolerance band: the range of operational profiles
# it can sustain without the organism falling into a labeled / excluded
# state. The width of this band is a function of support flow.
#
#   tolerance_width = f(support_flow)
#
# As support flow drops, tolerance width contracts. More organisms fall
# outside the band. Those organisms become candidates for labeling.
# ---------------------------------------------------------------------------

@dataclass
class ToleranceBand:
    """Width of the environment's tolerance band for operational profiles."""
    baseline_support: float             # support flow at which band has
                                        # reference width
    baseline_width: float               # reference width of tolerance band
    contraction_exponent: float = 1.0   # how sharply width contracts as
                                        # support falls. 1.0 = linear;
                                        # > 1.0 = accelerating contraction

    def width(self, support_flow: float) -> float:
        if support_flow <= 0:
            return 0.0
        ratio = support_flow / self.baseline_support
        return self.baseline_width * (ratio ** self.contraction_exponent)

    def fraction_inside(
        self,
        support_flow: float,
        profile_distribution_std: float,
    ) -> float:
        """
        Fraction of a population whose operational profile falls inside
        the tolerance band, assuming profiles are normally distributed
        around the band center with the given standard deviation.

        Uses the error function. Approximation only; real distributions
        are not normal.
        """
        w = self.width(support_flow)
        if profile_distribution_std <= 0:
            return 1.0 if w > 0 else 0.0
        z = (w / 2.0) / profile_distribution_std
        return math.erf(z / math.sqrt(2))


# ---------------------------------------------------------------------------
# Distinction-seeking as self-reinforcing capture
# ---------------------------------------------------------------------------
#
# Distinction flow produces distinction benefit (felt status differential,
# access to resources, hierarchical position). The marginal cost of
# distinction is low when the measurement infrastructure already exists,
# because each additional act of labeling reuses existing apparatus.
#
# Distinction flow also captures measurement systems over time. A
# measurement system initially built for a non-distinction purpose
# (e.g. identifying actual substrate damage) accretes distinction
# functions because distinction-seekers route their activity through
# whatever measurement infrastructure exists.
#
# The capture rate depends on the share of the measurement system's
# operation that is already driven by distinction flow:
#
#   d(capture_fraction)/dt = k * distinction_share * (1 - capture_fraction)
#
# Logistic capture. Once a system is mostly captured, further capture
# is cheap. Before capture, there is resistance.
# ---------------------------------------------------------------------------

@dataclass
class MeasurementSystem:
    """A measurement system that can be captured by distinction-seeking."""
    name: str
    intended_purpose: str
    capture_fraction: float = 0.0       # 0.0 = not captured; 1.0 = fully
                                        # serving distinction rather than
                                        # its stated purpose
    capture_rate_constant: float = 0.1  # per time step
    resistance: float = 0.0             # structural resistance to capture;
                                        # subtracted from capture rate

    def step(self, distinction_share: float, dt: float = 1.0) -> None:
        pressure = distinction_share - self.resistance
        if pressure < 0:
            pressure = 0.0
        rate = self.capture_rate_constant * pressure * (
            1.0 - self.capture_fraction
        )
        self.capture_fraction = min(
            1.0,
            self.capture_fraction + rate * dt,
        )

    def diverted_support(
        self,
        population_support_potential: float,
    ) -> float:
        """
        Amount of would-be support flow that this measurement system is
        diverting into distinction flow at its current capture level.
        """
        return population_support_potential * self.capture_fraction


# ---------------------------------------------------------------------------
# The full loop
# ---------------------------------------------------------------------------

@dataclass
class StatusExtractionModel:
    """
    Minimal dynamic model of the status-extraction loop.

    State variables:
      flows                current energy allocation
      tolerance            current tolerance band
      systems              list of measurement systems, each with a
                           capture fraction

    Each time step:
      1. Compute distinction share from current flows.
      2. Update capture fractions of all measurement systems.
      3. Diverted support moves from support flow into distinction flow.
      4. Tolerance band contracts per new support flow.
      5. Fraction of population falling outside band becomes the
         labeled_fraction for the next step, which further amplifies
         demand for distinction infrastructure.
    """
    flows: EnergyFlows
    tolerance: ToleranceBand
    systems: List[MeasurementSystem]
    profile_distribution_std: float
    amplification_per_labeled: float = 0.1
    # fraction of labeled population's would-be support budget that
    # instead gets routed into further distinction activity

    history: List[Dict] = field(default_factory=list)

    def step(self, dt: float = 1.0) -> None:
        distinction_share = self.flows.fractions()["distinction"]

        for sys in self.systems:
            sys.step(distinction_share, dt)

        # average capture fraction drives fresh diversion of support
        avg_capture = (
            sum(s.capture_fraction for s in self.systems) / len(self.systems)
            if self.systems else 0.0
        )
        divert = self.flows.support * avg_capture * 0.05 * dt
        # 5% of currently-captured support diverts per unit time; this
        # is a tunable kinetic parameter

        self.flows.support -= divert
        self.flows.distinction += divert

        # labeled fraction amplifies distinction demand
        inside = self.tolerance.fraction_inside(
            self.flows.support,
            self.profile_distribution_std,
        )
        labeled = 1.0 - inside
        amplification = labeled * self.amplification_per_labeled * dt
        amp_flow = self.flows.production * amplification
        self.flows.production -= amp_flow
        self.flows.distinction += amp_flow

        self.history.append({
            "support": self.flows.support,
            "production": self.flows.production,
            "distinction": self.flows.distinction,
            "tolerance_width": self.tolerance.width(self.flows.support),
            "fraction_inside": inside,
            "labeled_fraction": labeled,
            "avg_capture": avg_capture,
        })

    def run(self, steps: int, dt: float = 1.0) -> None:
        for _ in range(steps):
            self.step(dt)


# ---------------------------------------------------------------------------
# Falsifiable predictions
# ---------------------------------------------------------------------------
#
# PREDICTION 1  Distinction flow grows monotonically absent structural
#               resistance. Falsified if a society with no structural
#               constraints on distinction-seeking shows stable or
#               shrinking distinction flow over time.
#
# PREDICTION 2  As distinction share rises, the fraction of the
#               population labeled as outside the tolerance band rises
#               non-linearly. Falsified if labeling rate shows no
#               dependence on distinction flow once support flow is
#               held constant.
#
# PREDICTION 3  Measurement systems with low structural resistance are
#               captured first. Credentialing and diagnosis should
#               capture before physical instrumentation. Falsified by
#               showing consistent pattern where instrumentation-based
#               measurement captures before interpretation-based.
#
# PREDICTION 4  Recovery rates from identical substrate damage vary
#               strongly by environmental support flow and weakly by
#               individual characteristics once support is controlled.
#               Falsified by showing individual characteristics
#               dominate recovery variance in matched-support cohorts.
#
# PREDICTION 5  Reducing distinction flow without reducing total energy
#               expands tolerance band and reduces labeled fraction
#               within one generation. Falsified by showing labeled
#               fraction does not respond to redirected flow.
# ---------------------------------------------------------------------------

FALSIFIABLE_PREDICTIONS = [
    {
        "id": 1,
        "claim": (
            "distinction flow grows monotonically without structural "
            "resistance"
        ),
        "falsification": (
            "a society with no constraints shows stable or shrinking "
            "distinction flow"
        ),
    },
    {
        "id": 2,
        "claim": (
            "labeled fraction rises non-linearly with distinction share"
        ),
        "falsification": (
            "labeling rate shows no dependence on distinction flow at "
            "held support flow"
        ),
    },
    {
        "id": 3,
        "claim": (
            "low-resistance measurement systems capture first; "
            "credentialing and diagnosis before instrumentation"
        ),
        "falsification": (
            "instrumentation-based measurement consistently captures "
            "before interpretation-based"
        ),
    },
    {
        "id": 4,
        "claim": (
            "recovery variance is dominated by environmental support, "
            "not individual characteristics, once damage is matched"
        ),
        "falsification": (
            "individual characteristics dominate recovery variance in "
            "matched-support cohorts"
        ),
    },
    {
        "id": 5,
        "claim": (
            "redirecting flow from distinction to support expands "
            "tolerance band and reduces labeled fraction within one "
            "generation"
        ),
        "falsification": (
            "labeled fraction does not respond to redirected flow"
        ),
    },
]


# ---------------------------------------------------------------------------
# Worked example
# ---------------------------------------------------------------------------

def example_run() -> StatusExtractionModel:
    """Worked example with arbitrary but consistent units."""
    flows = EnergyFlows(support=50.0, production=40.0, distinction=10.0)
    tolerance = ToleranceBand(
        baseline_support=50.0,
        baseline_width=4.0,
        contraction_exponent=1.2,
    )
    systems = [
        MeasurementSystem(
            name="credentialing",
            intended_purpose="verify task-specific skills",
            capture_rate_constant=0.15,
            resistance=0.05,
        ),
        MeasurementSystem(
            name="clinical_diagnosis",
            intended_purpose="identify substrate damage",
            capture_rate_constant=0.12,
            resistance=0.1,
        ),
        MeasurementSystem(
            name="performance_review",
            intended_purpose="assess task outcomes",
            capture_rate_constant=0.18,
            resistance=0.03,
        ),
        MeasurementSystem(
            name="physical_instrumentation",
            intended_purpose="measure physical quantities",
            capture_rate_constant=0.08,
            resistance=0.3,
        ),
    ]
    model = StatusExtractionModel(
        flows=flows,
        tolerance=tolerance,
        systems=systems,
        profile_distribution_std=2.0,
        amplification_per_labeled=0.08,
    )
    model.run(steps=40)
    return model


if __name__ == "__main__":
    import json
    m = example_run()
    print("final state:")
    print(json.dumps(m.history[-1], indent=2))
    print()
    print("measurement system capture fractions:")
    for s in m.systems:
        print(f"  {s.name:30s}  {s.capture_fraction:.3f}")
    print()
    print("flow fractions over time (every 5 steps):")
    print(f"  {'step':>4}  {'support':>8}  {'production':>10}  "
          f"{'distinction':>11}  {'labeled':>8}")
    for i in range(0, len(m.history), 5):
        h = m.history[i]
        total = h["support"] + h["production"] + h["distinction"]
        print(
            f"  {i:4d}  "
            f"{h['support']/total:8.3f}  "
            f"{h['production']/total:10.3f}  "
            f"{h['distinction']/total:11.3f}  "
            f"{h['labeled_fraction']:8.3f}"
        )
