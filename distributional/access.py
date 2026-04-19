"""
distributional/access.py

Distributional consequences in thermodynamic and capacity units ONLY.
No currency, no prices, no spreads, no premiums. Price is contextual
and gameable — fractional reserve banking, margin, money creation all
exist outside physics. A framework that embeds price creates a knob
for hiding distress.

Core insight: workers, institutions, and communities do NOT degrade
linearly. Each has an individual threshold (cognitive buffer,
institutional slack, community redundancy) and collapses non-linearly
when structural load crosses that threshold.

A healthy worker: baseline output 0.7, cognitive buffer ~0.3.
Add one IQ point of load + executive dysfunction, buffer exhausted,
output drops from 0.7 to 0.0. Not 0.6. Zero. Until the community's
structural load decreases, that worker produces nothing regardless of
wages offered.

This means the distributional layer must track:
  1. The POPULATION DISTRIBUTION of workers/institutions/community
     members — not a single average capacity
  2. INDIVIDUAL THRESHOLDS — each member of the population has their
     own buffer size
  3. STRUCTURAL LOAD — the cumulative stress the community is imposing
     on each member (through basin degradation, tertiary depletion,
     firm extraction)
  4. CLIFF CROSSINGS PER PERIOD — the actual signal: how many members
     crossed from "functional with buffer" into "zero output" this period?

Price cannot paper over cliff crossings. A worker who crossed into
cognitive collapse is lost to productive capacity until their load
decreases. No wage raises them back. No credit expansion re-creates
the institutional knowledge. The only path back is structural: reduce
the load.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .tiers import Tier, TierAssignment


# ===========================================================================
# POPULATION COHORT MODEL
# ===========================================================================

@dataclass
class PopulationCohort:
    """A cohort of members with individual cognitive/operational buffers.

    A cohort represents a skill category, institutional role, or
    community function. Members within a cohort share a skill set but
    differ in their personal buffer size.

    The BUFFER DISTRIBUTION is represented by a list of floats, each
    representing one member's buffer (0.0 to 1.0). 0.0 means "already
    at cliff", 1.0 means "large buffer, high slack".

    baseline_output_per_member: thermodynamic output potential per
        functional member per period, in normalized units. A functional
        member produces this; a collapsed member produces 0.0.

    Using normalized units (0.0-1.0 for buffers, dimensionless output)
    avoids price contamination. Downstream consumers can translate to
    person-hours, outputs, permits processed, etc. depending on context.
    """
    cohort_name: str
    members_buffers: List[float]
    baseline_output_per_member: float = 1.0
    collapsed_member_indices: List[int] = field(default_factory=list)

    def population_size(self) -> int:
        return len(self.members_buffers)

    def functional_count(self) -> int:
        return self.population_size() - len(self.collapsed_member_indices)

    def collapsed_count(self) -> int:
        return len(self.collapsed_member_indices)

    def functional_fraction(self) -> float:
        if self.population_size() == 0:
            return 0.0
        return self.functional_count() / self.population_size()

    def total_output_capacity(self) -> float:
        """Sum of baseline output across all FUNCTIONAL members.
        Collapsed members contribute zero."""
        return self.functional_count() * self.baseline_output_per_member

    def mean_remaining_buffer(self) -> float:
        """Mean buffer of still-functional members."""
        collapsed_set = set(self.collapsed_member_indices)
        remaining = [b for i, b in enumerate(self.members_buffers)
                     if i not in collapsed_set]
        if not remaining:
            return 0.0
        return sum(remaining) / len(remaining)


def apply_structural_load(
    cohort: PopulationCohort,
    structural_load: float,
) -> Tuple[PopulationCohort, List[int]]:
    """Apply structural load to a cohort and record cliff crossings.

    Any member whose buffer is smaller than the load crosses their
    cliff THIS PERIOD. They are added to collapsed_member_indices
    and produce zero output for all subsequent periods until load
    decreases below their buffer AND a recovery mechanism exists.

    structural_load: normalized load (0.0-1.0).

    Returns (mutated_cohort, indices_that_crossed_this_period).
    """
    collapsed_set = set(cohort.collapsed_member_indices)
    newly_crossed = []
    for i, buffer in enumerate(cohort.members_buffers):
        if i in collapsed_set:
            continue
        if buffer < structural_load:
            newly_crossed.append(i)
    cohort.collapsed_member_indices = sorted(
        collapsed_set | set(newly_crossed)
    )
    return cohort, newly_crossed


def recover_cohort(
    cohort: PopulationCohort,
    structural_load: float,
    recovery_fraction: float = 0.0,
) -> Tuple[PopulationCohort, List[int]]:
    """Model recovery of previously-collapsed members.

    Recovery is NOT automatic. It requires:
      1. Structural load has decreased below the member's buffer
      2. A recovery mechanism (recovery_fraction > 0.0) — typically
         through community support, medical treatment, restored basin
         conditions, or the passage of time with reduced load.

    recovery_fraction: fraction of eligible collapsed members who
        recover this period. Default 0.0 — no automatic recovery.

    Returns (mutated_cohort, indices_that_recovered_this_period).
    """
    if recovery_fraction <= 0.0:
        return cohort, []

    eligible = []
    for i in cohort.collapsed_member_indices:
        if cohort.members_buffers[i] >= structural_load:
            eligible.append(i)

    num_recovered = int(len(eligible) * recovery_fraction)
    recovered = eligible[:num_recovered]

    cohort.collapsed_member_indices = sorted(
        set(cohort.collapsed_member_indices) - set(recovered)
    )
    return cohort, recovered


# ===========================================================================
# TIER-TO-LOAD MAPPING
# ===========================================================================

DEFAULT_STRUCTURAL_LOAD_BY_TIER: Dict[Tier, float] = {
    Tier.GREEN: 0.0,
    Tier.AMBER: 0.25,
    Tier.RED:   0.55,
    Tier.BLACK: 0.85,
}


def structural_load_from_tier(
    tier: Tier,
    table: Optional[Dict[Tier, float]] = None,
) -> float:
    """Map tier to normalized structural load (0.0-1.0).
    NOT a price. A thermodynamic stress intensity."""
    t = table or DEFAULT_STRUCTURAL_LOAD_BY_TIER
    return t[tier]


# ===========================================================================
# ACCESS REPORT IN CAPACITY UNITS ONLY
# ===========================================================================

@dataclass
class AccessReport:
    """Distributional access report in thermodynamic capacity units.

    NO PRICE FIELDS. All measurements are in:
      - fractions (functional_fraction)
      - counts (newly_collapsed_count)
      - normalized capacity units (total_output_capacity)
      - thermodynamic load (structural_load)
    """
    tier_assignment: TierAssignment
    structural_load: float
    cohorts: Dict[str, PopulationCohort]

    newly_collapsed_this_period: Dict[str, int] = field(default_factory=dict)
    newly_recovered_this_period: Dict[str, int] = field(default_factory=dict)

    def total_functional_capacity(self) -> float:
        return sum(c.total_output_capacity() for c in self.cohorts.values())

    def total_baseline_capacity(self) -> float:
        return sum(c.population_size() * c.baseline_output_per_member
                   for c in self.cohorts.values())

    def functional_fraction(self) -> float:
        baseline = self.total_baseline_capacity()
        if baseline == 0:
            return 0.0
        return self.total_functional_capacity() / baseline

    def total_newly_collapsed(self) -> int:
        return sum(self.newly_collapsed_this_period.values())

    def total_newly_recovered(self) -> int:
        return sum(self.newly_recovered_this_period.values())

    def summary_text(self) -> str:
        lines = [
            f"Access report (capacity units, no price):",
            f"  overall tier:       {self.tier_assignment.overall_tier().name}",
            f"  structural_load:    {self.structural_load:.3f}",
            f"  functional fraction:{self.functional_fraction():.3f}",
            f"  total newly collapsed this period: {self.total_newly_collapsed()}",
            f"  total newly recovered this period: {self.total_newly_recovered()}",
            "",
            "Cohort detail:",
        ]
        for name, cohort in self.cohorts.items():
            lines.append(
                f"  {name}: {cohort.functional_count()}/{cohort.population_size()} "
                f"functional ({cohort.functional_fraction():.2%}), "
                f"{self.newly_collapsed_this_period.get(name, 0)} new cliff "
                f"crossings, mean remaining buffer "
                f"{cohort.mean_remaining_buffer():.2f}"
            )
        return "\n".join(lines)


def apply_tier_to_cohorts(
    tier_assignment: TierAssignment,
    cohorts: Dict[str, PopulationCohort],
    load_table: Optional[Dict[Tier, float]] = None,
    cohort_load_multipliers: Optional[Dict[str, float]] = None,
    recovery_fractions: Optional[Dict[str, float]] = None,
) -> AccessReport:
    """Apply the firm's tier to a population of cohorts.

    cohort_load_multipliers: cohort_name -> multiplier. Multipliers
        above 1.0 mean the cohort bears more of the structural load
        (less exit mobility, closer to the basin damage, more
        dependent on local conditions). Community members typically
        1.5x; capital market participants typically 0.2-0.4x
        because they can diversify.

    recovery_fractions: cohort_name -> recovery fraction per period
        for collapsed members whose buffer has risen above current
        load. Defaults to 0.0 (no automatic recovery).
    """
    overall = tier_assignment.overall_tier()
    base_load = structural_load_from_tier(overall, table=load_table)

    multipliers = cohort_load_multipliers or {}
    recoveries = recovery_fractions or {}

    newly_collapsed: Dict[str, int] = {}
    newly_recovered: Dict[str, int] = {}

    for name, cohort in cohorts.items():
        mult = multipliers.get(name, 1.0)
        load = min(1.0, base_load * mult)

        cohort, crossed = apply_structural_load(cohort, load)
        newly_collapsed[name] = len(crossed)

        rec_frac = recoveries.get(name, 0.0)
        cohort, recovered = recover_cohort(cohort, load, rec_frac)
        newly_recovered[name] = len(recovered)

    return AccessReport(
        tier_assignment=tier_assignment,
        structural_load=base_load,
        cohorts=cohorts,
        newly_collapsed_this_period=newly_collapsed,
        newly_recovered_this_period=newly_recovered,
    )


# ===========================================================================
# CONVENIENCE: COHORT BUILDERS
# ===========================================================================

def make_cohort_with_buffer_distribution(
    cohort_name: str,
    size: int,
    buffer_mean: float = 0.5,
    buffer_std: float = 0.2,
    baseline_output_per_member: float = 1.0,
    seed: Optional[int] = None,
) -> PopulationCohort:
    """Construct a cohort with approximately triangular buffer distribution.

    Uses triangular distribution (stdlib-only) as a first-order model.
    For production use substitute a proper distribution.
    """
    import random
    rng = random.Random(seed)
    buffers = []
    for _ in range(size):
        lo = max(0.0, buffer_mean - 2 * buffer_std)
        hi = min(1.0, buffer_mean + 2 * buffer_std)
        b = rng.triangular(lo, hi, buffer_mean)
        buffers.append(b)
    return PopulationCohort(
        cohort_name=cohort_name,
        members_buffers=buffers,
        baseline_output_per_member=baseline_output_per_member,
    )
