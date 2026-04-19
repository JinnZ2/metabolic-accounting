"""
distributional/institutional.py

Institutional constraint and waste accounting.

CORE CLAIM: A person's THERMODYNAMIC CAPACITY is not what gets measured
by institutions. Institutions measure OUTPUT UNDER THEIR CONSTRAINT.
The gap between available capacity and realized output is WASTE —
energy/capability that could do work but is being dissipated by
institutional mismatch.

This is not a metaphor. It is a first-law violation detection:

  Available capacity            - thermodynamic potential the person
                                  actually has (can be > 1.0 baseline
                                  for neurodivergent people with
                                  environmental fit, strong intrinsic
                                  motivation, task affinity)
  Institutional fit multiplier  - how much of that capacity the
                                  governance/work structure permits
                                  (0.0 = institution fights the person's
                                  neurology; 1.0 = neutral; >1.0 =
                                  institution amplifies capacity)
  Realized output               - what the institution measures
                                  = available_capacity × fit_multiplier
  Wasted capacity               - available - realized
                                  = available_capacity × (1 - fit_multiplier)
                                  (negative values indicate amplification,
                                  not waste — institution is drawing
                                  more capacity than baseline allows)
  Trauma tax                    - energy the person must spend fighting
                                  the structure, masking, managing shame
                                  from being classified as defective.
                                  This DOES NOT return to work.

The TRAUMA TAX matters because it is NOT just capacity lost — it is
capacity REDIRECTED to defense. A person with trauma tax of 0.2 is
burning 0.2 units of energy per period just to survive the institution.
That energy does not come back. It is dissipated.

Key insight: conventional models count only realized output and call
the gap "individual difference" or "productivity variance." This
framework counts the gap as INSTITUTIONAL FAILURE — the design of the
governance/work structure is destroying available capacity.

Flint illustration: a rust-belt manufacturing economy measured all its
workers through a "show up, do linear repetitive work, tolerate
interruption, accept compliance structure" lens. Workers with actual
capacity of 1.5-2.0x baseline (neurodivergent with right task fit)
measured as 0.3-0.5x because the fit was 0.1-0.2. The institution then
called them "low-skill" and "unproductive" and paid them as such. Years
later when the jobs disappeared, nobody knew what the real capacity
was — because the institution had never tested anyone under any other
fit. The waste was invisible because it was never measured.

This module makes it visible.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .access import PopulationCohort


# ===========================================================================
# INSTITUTIONAL FIT PROFILE
# ===========================================================================
#
# Each cohort can have an InstitutionalFitProfile that describes HOW
# THE CURRENT INSTITUTION CONSTRAINS OR AMPLIFIES the capacity of
# members in that cohort. The profile is measured per-member so the
# framework can represent that the SAME institution treats different
# members differently (e.g. neurotypical workers fit, neurodivergent
# workers don't).

@dataclass
class InstitutionalFitProfile:
    """Per-cohort description of how an institution constrains capacity.

    member_fit_multipliers: per-member fit, aligned 1:1 with the
        cohort's members_buffers list. Values:
          0.0   institution destroys this person's capacity entirely
          0.3   severe mismatch; most capacity dissipated as waste
          1.0   neutral fit; output = capacity
          1.5+  institution amplifies capacity (rare — requires
                self-designed work, strong intrinsic motivation,
                environmental match)

    member_trauma_tax: per-member trauma tax. Values 0.0 to 1.0.
        Energy the member burns on fighting the structure, masking,
        absorbing shame, managing executive-function mismatch. This
        capacity DOES NOT return. It is dissipated.

    member_available_capacity: per-member TRUE thermodynamic capacity
        (not baseline output — this is what the person could produce
        under optimal conditions). Can exceed 1.0 for neurodivergent
        members whose hyperfocus + intrinsic motivation produces
        multi-x baseline output when conditions fit.
    """
    cohort_name: str
    member_available_capacity: List[float]
    member_fit_multipliers: List[float]
    member_trauma_tax: List[float]

    def __post_init__(self):
        n_capacity = len(self.member_available_capacity)
        n_fit = len(self.member_fit_multipliers)
        n_trauma = len(self.member_trauma_tax)
        if not (n_capacity == n_fit == n_trauma):
            raise ValueError(
                f"InstitutionalFitProfile for {self.cohort_name}: "
                f"length mismatch ({n_capacity}, {n_fit}, {n_trauma})"
            )

    def population_size(self) -> int:
        return len(self.member_available_capacity)

    def total_available_capacity(self) -> float:
        """Sum of true thermodynamic capacity across members."""
        return sum(self.member_available_capacity)

    def total_realized_output(self, functional_only: bool = True,
                               collapsed_indices: Optional[List[int]] = None
                               ) -> float:
        """Capacity × fit, summed over members. Collapsed members
        produce zero regardless of fit."""
        collapsed = set(collapsed_indices or [])
        total = 0.0
        for i, (cap, fit) in enumerate(zip(
            self.member_available_capacity,
            self.member_fit_multipliers,
        )):
            if functional_only and i in collapsed:
                continue
            total += cap * fit
        return total

    def total_wasted_capacity(self, functional_only: bool = True,
                               collapsed_indices: Optional[List[int]] = None
                               ) -> float:
        """Capacity × (1 - fit), summed over members. Can be negative
        (amplification) but usually positive (waste)."""
        collapsed = set(collapsed_indices or [])
        total = 0.0
        for i, (cap, fit) in enumerate(zip(
            self.member_available_capacity,
            self.member_fit_multipliers,
        )):
            if functional_only and i in collapsed:
                continue
            total += cap * (1.0 - fit)
        return total

    def total_trauma_tax(self, functional_only: bool = True,
                         collapsed_indices: Optional[List[int]] = None
                         ) -> float:
        """Sum of trauma tax across members. Does not return — it is
        dissipated energy."""
        collapsed = set(collapsed_indices or [])
        total = 0.0
        for i, tax in enumerate(self.member_trauma_tax):
            if functional_only and i in collapsed:
                continue
            total += tax
        return total


# ===========================================================================
# WASTE REPORT
# ===========================================================================

@dataclass
class WasteReport:
    """Report on institutional waste for a population of cohorts.

    total_available_capacity: sum of what members COULD produce under
        optimal conditions (their true thermodynamic potential).
    total_realized_output: what institutions actually extract.
    total_wasted_capacity: capacity lost to institutional mismatch.
    total_trauma_tax: energy burned defending against institutional harm.
    waste_ratio: wasted / available — primary failure metric.
    amplification_ratio: fraction of members where institution
        amplifies rather than constrains (fit > 1.0). High values
        signal well-designed institutions.
    """
    total_available_capacity: float
    total_realized_output: float
    total_wasted_capacity: float
    total_trauma_tax: float
    waste_ratio: float
    amplification_ratio: float
    per_cohort: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def total_institutional_loss(self) -> float:
        """Waste + trauma tax = total capacity dissipated by
        institutional failure (as opposed to physiological / basin
        damage, which is tracked separately in the distributional
        invariant)."""
        return self.total_wasted_capacity + self.total_trauma_tax

    def summary_text(self) -> str:
        lines = [
            f"Waste report (institutional failure accounting):",
            f"  total available capacity:   {self.total_available_capacity:.2f}",
            f"  total realized output:      {self.total_realized_output:.2f}",
            f"  total wasted capacity:      {self.total_wasted_capacity:.2f}",
            f"  total trauma tax:           {self.total_trauma_tax:.2f}",
            f"  total institutional loss:   {self.total_institutional_loss():.2f}",
            "",
            f"  waste ratio:                {self.waste_ratio:.2%}",
            f"  amplification ratio:        {self.amplification_ratio:.2%}",
        ]
        if self.per_cohort:
            lines.append("")
            lines.append("  Per-cohort breakdown:")
            for name, stats in self.per_cohort.items():
                lines.append(
                    f"    {name}: available {stats['available']:.2f}, "
                    f"realized {stats['realized']:.2f}, "
                    f"wasted {stats['wasted']:.2f}, "
                    f"trauma {stats['trauma']:.2f}, "
                    f"waste_ratio {stats['waste_ratio']:.2%}"
                )
        return "\n".join(lines)


def compute_waste_report(
    cohorts: Dict[str, PopulationCohort],
    fit_profiles: Dict[str, InstitutionalFitProfile],
) -> WasteReport:
    """Compute institutional waste across cohorts.

    cohorts: dict keyed by cohort name. Uses collapsed_member_indices
             to determine which members are functional this period.
    fit_profiles: dict keyed by cohort name. Each profile describes
                  the institutional constraint on that cohort.

    Collapsed members (cognitive cliff crossed) produce zero regardless
    of fit — they are lost capacity tracked in the distributional
    invariant, not waste. This module only reports waste among STILL-
    FUNCTIONAL members.
    """
    total_available = 0.0
    total_realized = 0.0
    total_wasted = 0.0
    total_trauma = 0.0
    amplified_count = 0
    total_functional_count = 0

    per_cohort: Dict[str, Dict[str, float]] = {}

    for name, cohort in cohorts.items():
        profile = fit_profiles.get(name)
        if profile is None:
            continue
        if profile.population_size() != cohort.population_size():
            raise ValueError(
                f"cohort {name}: profile size {profile.population_size()} "
                f"does not match cohort size {cohort.population_size()}"
            )

        collapsed = cohort.collapsed_member_indices
        c_available = profile.total_available_capacity()
        # for functional members only:
        c_realized = profile.total_realized_output(
            functional_only=True, collapsed_indices=collapsed,
        )
        c_wasted = profile.total_wasted_capacity(
            functional_only=True, collapsed_indices=collapsed,
        )
        c_trauma = profile.total_trauma_tax(
            functional_only=True, collapsed_indices=collapsed,
        )

        # count amplified members (fit > 1.0) among functional
        collapsed_set = set(collapsed)
        for i, fit in enumerate(profile.member_fit_multipliers):
            if i in collapsed_set:
                continue
            total_functional_count += 1
            if fit > 1.0:
                amplified_count += 1

        total_available += c_available
        total_realized += c_realized
        total_wasted += c_wasted
        total_trauma += c_trauma

        c_waste_ratio = (c_wasted / c_available) if c_available > 0 else 0.0
        per_cohort[name] = {
            "available": c_available,
            "realized": c_realized,
            "wasted": c_wasted,
            "trauma": c_trauma,
            "waste_ratio": c_waste_ratio,
        }

    # global waste ratio: wasted / (wasted + realized) for still-
    # functional members. Using denominator of realized+wasted avoids
    # distortion from collapsed members' available capacity (which is
    # zero output regardless of institution).
    denom = total_wasted + total_realized
    waste_ratio = (total_wasted / denom) if denom != 0 else 0.0

    amplification_ratio = (
        amplified_count / total_functional_count
        if total_functional_count > 0 else 0.0
    )

    return WasteReport(
        total_available_capacity=total_available,
        total_realized_output=total_realized,
        total_wasted_capacity=total_wasted,
        total_trauma_tax=total_trauma,
        waste_ratio=waste_ratio,
        amplification_ratio=amplification_ratio,
        per_cohort=per_cohort,
    )


# ===========================================================================
# CONVENIENCE CONSTRUCTORS
# ===========================================================================

def make_profile_neurotypical_standard_job(
    cohort_name: str,
    population_size: int,
    baseline_capacity: float = 0.7,
    baseline_fit: float = 1.0,
) -> InstitutionalFitProfile:
    """Profile for neurotypical workers in standard jobs.

    Defaults: each member has capacity 0.7 (neurotypical baseline),
    fit 1.0 (standard job matches neurotypical work patterns), trauma
    tax 0.0 (no structural mismatch).
    """
    return InstitutionalFitProfile(
        cohort_name=cohort_name,
        member_available_capacity=[baseline_capacity] * population_size,
        member_fit_multipliers=[baseline_fit] * population_size,
        member_trauma_tax=[0.0] * population_size,
    )


def make_profile_neurodivergent_mismatched(
    cohort_name: str,
    population_size: int,
    actual_capacity: float = 1.5,
    institutional_fit: float = 0.2,
    trauma_tax: float = 0.2,
) -> InstitutionalFitProfile:
    """Profile for neurodivergent members in a mismatched institution.

    Defaults reflect: higher actual capacity than neurotypical baseline
    (hyperfocus potential), very low institutional fit (rust-belt /
    compliance-driven work), significant trauma tax from masking,
    shame absorption, fighting executive-function mismatch.
    """
    return InstitutionalFitProfile(
        cohort_name=cohort_name,
        member_available_capacity=[actual_capacity] * population_size,
        member_fit_multipliers=[institutional_fit] * population_size,
        member_trauma_tax=[trauma_tax] * population_size,
    )


def make_profile_self_designed_work(
    cohort_name: str,
    population_size: int,
    actual_capacity: float = 2.5,
    institutional_fit: float = 1.5,
    trauma_tax: float = 0.0,
) -> InstitutionalFitProfile:
    """Profile for members in self-designed work matching their neurology.

    Defaults: high actual capacity (neurodivergent with hyperfocus
    access), fit > 1.0 (institution amplifies rather than constrains),
    zero trauma tax (no structural fight). This is what gets measured
    when governance stops constraining.
    """
    return InstitutionalFitProfile(
        cohort_name=cohort_name,
        member_available_capacity=[actual_capacity] * population_size,
        member_fit_multipliers=[institutional_fit] * population_size,
        member_trauma_tax=[trauma_tax] * population_size,
    )
