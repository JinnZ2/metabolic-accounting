"""
distributional/strategy.py

Institutional strategy comparison.

An institution makes a fundamental design choice — usually implicit,
usually unexamined — between two strategies:

  COMPLIANCE strategy:
    Design a standard job structure. Hire people who fit. Measure
    output against a fixed standard. Pay for measured output.
    Assumes: capacity is roughly uniform across workers.
    Optimizes: management overhead, predictability, legibility.
    Waste: whatever capacity doesn't fit the standard is dissipated.

  CAPACITY_FIT strategy:
    Observe each worker's actual capacity and passions. Design the
    work around their fit. Measure output against what their capacity
    makes possible. Pay for fit discovery plus output.
    Assumes: capacity varies widely; institution must adapt to worker.
    Optimizes: actual output, worker regeneration (no trauma tax).
    Waste: low, because capacity is discovered and structured for.

This module makes the tradeoff explicit and computable. Given a
population of workers with known available_capacity distribution,
it computes expected outcomes under each strategy:

  - total realized output
  - wasted capacity
  - trauma tax (structural)
  - management overhead
  - churn risk (workers leaving due to mismatch)
  - output per management unit

Empirical framing: when Kavik ran multiple companies, he found that
hiring for neurodivergent fit consistently outperformed standard
hiring. This is not anecdote — it reflects the thermodynamic reality
that capacity is heterogeneous and compliance-based measurement
systematically dissipates the upper tail.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .access import PopulationCohort
from .institutional import (
    InstitutionalFitProfile,
    WasteReport,
    compute_waste_report,
)


# ===========================================================================
# STRATEGY MODELS
# ===========================================================================

@dataclass
class StrategyCost:
    """Overhead costs associated with a strategy.

    management_overhead: capacity units/period spent on management.
        Compliance is lower (standardized processes, less supervision
        per worker). Capacity_fit is higher (per-worker design cost,
        ongoing adaptation).

    discovery_cost: upfront capacity units spent discovering each
        worker's fit. Zero for compliance (job is fixed); substantial
        for capacity_fit (interviews, trial periods, iteration).

    churn_risk: fraction of workforce expected to leave per period.
        Compliance: higher (mismatched workers burn out or quit).
        Capacity_fit: lower (bulldogs stay — the fit regenerates them).
    """
    management_overhead_per_worker: float
    discovery_cost_per_worker: float
    churn_rate_per_period: float


@dataclass
class StrategyOutcome:
    """Result of applying a strategy to a workforce."""
    strategy_name: str
    total_realized_output: float
    total_wasted_capacity: float
    total_trauma_tax: float
    total_management_overhead: float
    total_discovery_cost: float
    expected_churn: int

    def net_output(self) -> float:
        """Realized output minus management overhead and amortized
        discovery cost. This is what the institution actually captures."""
        return (self.total_realized_output
                - self.total_management_overhead
                - self.total_discovery_cost)

    def output_per_management_unit(self) -> float:
        if self.total_management_overhead == 0:
            return float("inf")
        return self.total_realized_output / self.total_management_overhead


@dataclass
class StrategyComparison:
    """Side-by-side comparison of strategies over the same workforce."""
    compliance: StrategyOutcome
    capacity_fit: StrategyOutcome

    def output_delta(self) -> float:
        """How much more (or less) net output does capacity_fit produce?"""
        return self.capacity_fit.net_output() - self.compliance.net_output()

    def waste_delta(self) -> float:
        """How much capacity does compliance dissipate that
        capacity_fit would capture?"""
        return (self.compliance.total_wasted_capacity
                - self.capacity_fit.total_wasted_capacity)

    def trauma_delta(self) -> float:
        """How much trauma tax does compliance impose that
        capacity_fit avoids?"""
        return (self.compliance.total_trauma_tax
                - self.capacity_fit.total_trauma_tax)

    def churn_delta(self) -> int:
        """How many more workers quit per period under compliance?"""
        return self.compliance.expected_churn - self.capacity_fit.expected_churn

    def summary_text(self) -> str:
        lines = [
            "Strategy comparison (capacity units, no price):",
            "",
            f"  COMPLIANCE strategy:",
            f"    realized output:     "
            f"{self.compliance.total_realized_output:.2f}",
            f"    wasted capacity:     "
            f"{self.compliance.total_wasted_capacity:.2f}",
            f"    trauma tax:          "
            f"{self.compliance.total_trauma_tax:.2f}",
            f"    management overhead: "
            f"{self.compliance.total_management_overhead:.2f}",
            f"    discovery cost:      "
            f"{self.compliance.total_discovery_cost:.2f}",
            f"    expected churn:      "
            f"{self.compliance.expected_churn} workers/period",
            f"    net output:          "
            f"{self.compliance.net_output():.2f}",
            "",
            f"  CAPACITY_FIT strategy:",
            f"    realized output:     "
            f"{self.capacity_fit.total_realized_output:.2f}",
            f"    wasted capacity:     "
            f"{self.capacity_fit.total_wasted_capacity:.2f}",
            f"    trauma tax:          "
            f"{self.capacity_fit.total_trauma_tax:.2f}",
            f"    management overhead: "
            f"{self.capacity_fit.total_management_overhead:.2f}",
            f"    discovery cost:      "
            f"{self.capacity_fit.total_discovery_cost:.2f}",
            f"    expected churn:      "
            f"{self.capacity_fit.expected_churn} workers/period",
            f"    net output:          "
            f"{self.capacity_fit.net_output():.2f}",
            "",
            f"  DELTA (capacity_fit - compliance):",
            f"    output delta:        {self.output_delta():+.2f}",
            f"    waste captured:      {self.waste_delta():+.2f}",
            f"    trauma avoided:      {self.trauma_delta():+.2f}",
            f"    churn avoided:       {self.churn_delta()} workers/period",
        ]
        return "\n".join(lines)


# ===========================================================================
# DEFAULT STRATEGY COSTS
# ===========================================================================
#
# Defaults based on observation that capacity_fit institutions invest
# more in discovery/management but capture dramatically more output.
# These are first-order estimates in normalized capacity units.

DEFAULT_COMPLIANCE_COSTS = StrategyCost(
    management_overhead_per_worker=0.05,
    discovery_cost_per_worker=0.00,
    churn_rate_per_period=0.08,  # ~8% per period for mismatched workforce
)

DEFAULT_CAPACITY_FIT_COSTS = StrategyCost(
    management_overhead_per_worker=0.12,
    discovery_cost_per_worker=0.15,  # upfront investment in finding fit
    churn_rate_per_period=0.02,  # bulldogs stay
)


# ===========================================================================
# STRATEGY SIMULATION
# ===========================================================================

def _apply_compliance_strategy(
    available_capacity: List[float],
    costs: StrategyCost,
) -> StrategyOutcome:
    """Compliance strategy: fixed job structure.

    Each worker's fit is determined by how well they match the
    standard neurotypical job design. Workers with capacity close to
    the neurotypical baseline (~0.7) fit well (fit ~1.0). Workers
    with higher capacity (neurodivergent, high-potential) have LOWER
    fit because the standard job fights their neurology. Workers with
    lower capacity also have lower fit for similar structural reasons.

    This produces the counterintuitive result that high-capacity
    workers are classified as poor fits under compliance — and the
    empirical observation is that's exactly what happens in practice.
    """
    realized = 0.0
    wasted = 0.0
    trauma = 0.0

    for cap in available_capacity:
        # compliance fit: peaks at capacity ~ 0.7 (neurotypical baseline),
        # drops off above and below. Workers with capacity 3.0 get fit
        # ~0.2 because the job structure fights their neurology.
        if cap <= 0.7:
            fit = cap / 0.7  # low-capacity workers fit to a degree
        else:
            # above baseline, fit drops sharply with distance from baseline
            fit = max(0.1, 0.7 / cap)
        # trauma tax: proportional to mismatch
        tax = max(0.0, (1.0 - fit) * 0.25)

        realized += cap * fit
        wasted += cap * (1.0 - fit)
        trauma += tax

    n = len(available_capacity)
    mgmt = n * costs.management_overhead_per_worker
    discovery = n * costs.discovery_cost_per_worker
    churn = int(n * costs.churn_rate_per_period)

    return StrategyOutcome(
        strategy_name="compliance",
        total_realized_output=realized,
        total_wasted_capacity=wasted,
        total_trauma_tax=trauma,
        total_management_overhead=mgmt,
        total_discovery_cost=discovery,
        expected_churn=churn,
    )


def _apply_capacity_fit_strategy(
    available_capacity: List[float],
    costs: StrategyCost,
    fit_quality: float = 0.85,
) -> StrategyOutcome:
    """Capacity_fit strategy: work designed around each worker.

    fit_quality: how well the institution discovers fit. 1.0 is ideal
        (perfect match — output equals available capacity). 0.85 is
        realistic with good hiring/onboarding. 0.5 is a poor attempt
        at fit-based hiring.
    """
    realized = 0.0
    wasted = 0.0
    trauma = 0.0

    for cap in available_capacity:
        fit = fit_quality
        realized += cap * fit
        wasted += cap * (1.0 - fit)
        # trauma tax near zero when fit is high
        tax = max(0.0, (1.0 - fit) * 0.05)
        trauma += tax

    n = len(available_capacity)
    mgmt = n * costs.management_overhead_per_worker
    discovery = n * costs.discovery_cost_per_worker
    churn = int(n * costs.churn_rate_per_period)

    return StrategyOutcome(
        strategy_name="capacity_fit",
        total_realized_output=realized,
        total_wasted_capacity=wasted,
        total_trauma_tax=trauma,
        total_management_overhead=mgmt,
        total_discovery_cost=discovery,
        expected_churn=churn,
    )


def compare_strategies(
    available_capacity: List[float],
    compliance_costs: Optional[StrategyCost] = None,
    capacity_fit_costs: Optional[StrategyCost] = None,
    fit_quality: float = 0.85,
) -> StrategyComparison:
    """Compare outcomes under each strategy for the same workforce."""
    cc = compliance_costs or DEFAULT_COMPLIANCE_COSTS
    fc = capacity_fit_costs or DEFAULT_CAPACITY_FIT_COSTS

    compliance_outcome = _apply_compliance_strategy(available_capacity, cc)
    fit_outcome = _apply_capacity_fit_strategy(
        available_capacity, fc, fit_quality=fit_quality,
    )

    return StrategyComparison(
        compliance=compliance_outcome,
        capacity_fit=fit_outcome,
    )
