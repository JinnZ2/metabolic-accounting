"""
distributional/civilization.py

Civilization-scale waste audit.

Extends the existing institutional-waste layer with three additional
categories of capacity dissipation that only become visible at scale:

  1. INSTITUTIONAL WASTE (already tracked in institutional.py):
     Capacity a person HAS but the institutional structure doesn't
     let them realize. Measured as (available - realized).

  2. FORCED DEPENDENCY WASTE:
     Capacity a person HAS and could contribute, but the institution
     has structured them into dependency. Means-tested disability
     systems that require zero-earnings to maintain support.
     Credentialing barriers that lock trained practitioners out.
     Work restrictions on recipients of public assistance.
     Occupational licensing that monopolizes competence.
     Result: person has 1.5 units of capacity, is legally / structurally
     prevented from contributing any of it without losing support.

  3. LABOR WASTE:
     Capacity that IS being realized as work but the work produces
     NOTHING. Compliance theater. Redundant management layers. Make-work.
     Meetings that could be emails. Surveillance overhead. Justification
     paperwork. Middle management of middle management.
     Result: 8 hours of "work" that could have been 1 hour of actual
     work, with 7 hours of capacity burned on structural friction.

  4. POTENTIAL WASTE:
     Capacity that never manifests because the person was prevented
     from discovering it. Education systems that fail neurodivergent
     learners. Career tracks closed off early by geography, class,
     credentialing. Communities where no one around you does the work
     you would be capable of. Languages of thought not taught.
     Result: the Leonardos born in rust belts who become assembly-line
     workers because no one showed them their own capacity.

The innovation crisis Kavik identifies — per-capita innovation lower
now than Bronze Age or Renaissance despite 100x population — is
explained by the civilization-scale sum of these four waste categories.

Historical comparison: Bronze Age craftspeople had access to
work-shop / apprentice structures where available capacity could be
discovered and realized. Renaissance workshops amplified hyperfocused
polymaths. Modern institutions optimize for compliance and control,
dissipating capacity on surveillance, dependency traps, and
undiscovered potential.

All four categories are expressed in thermodynamic capacity units.
No currency. No price. This is where the compounding civilizational
cost becomes visible.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class WasteBreakdown:
    """The four categories of capacity waste, in thermodynamic units."""
    institutional_waste: float       # capacity HAS, not realized under fit
    forced_dependency_waste: float   # capacity HAS, structurally blocked
    labor_waste: float               # capacity realized into null work
    potential_waste: float           # capacity never discovered / developed

    def total_waste(self) -> float:
        return (self.institutional_waste
                + self.forced_dependency_waste
                + self.labor_waste
                + self.potential_waste)


@dataclass
class CivilizationAudit:
    """Per-capita and aggregate capacity audit for a population.

    population_size: total persons in the audit scope
    available_capacity_per_capita: mean capacity if fully realized
        (under ideal conditions: fit discovered, no dependency trap,
        productive work, potential developed)
    realized_productive_capacity_per_capita: capacity that actually
        produces something — institutional fit applied, no labor waste,
        no dependency block
    waste_per_capita: WasteBreakdown averaged across population

    These numbers are comparative: a framework users can compute for
    different institutional eras (modern, Renaissance, Bronze Age —
    modeled), industries, or populations to see where civilization
    is dissipating capacity.
    """
    era_name: str
    population_size: int
    available_capacity_per_capita: float
    realized_productive_capacity_per_capita: float
    waste_per_capita: WasteBreakdown

    def total_available_capacity(self) -> float:
        return self.available_capacity_per_capita * self.population_size

    def total_realized_productive(self) -> float:
        return self.realized_productive_capacity_per_capita * self.population_size

    def total_waste(self) -> float:
        return self.waste_per_capita.total_waste() * self.population_size

    def per_capita_waste_ratio(self) -> float:
        """Per-capita fraction of available capacity being wasted."""
        if self.available_capacity_per_capita == 0:
            return 0.0
        return (self.waste_per_capita.total_waste()
                / self.available_capacity_per_capita)

    def summary_text(self) -> str:
        lines = [
            f"Civilization audit — {self.era_name}",
            f"  population:                        {self.population_size:,}",
            f"  available capacity per capita:     "
            f"{self.available_capacity_per_capita:.2f}",
            f"  realized productive per capita:    "
            f"{self.realized_productive_capacity_per_capita:.2f}",
            f"",
            f"  waste per capita:",
            f"    institutional (fit mismatch):    "
            f"{self.waste_per_capita.institutional_waste:.2f}",
            f"    forced dependency:               "
            f"{self.waste_per_capita.forced_dependency_waste:.2f}",
            f"    labor (null work):               "
            f"{self.waste_per_capita.labor_waste:.2f}",
            f"    potential (never discovered):    "
            f"{self.waste_per_capita.potential_waste:.2f}",
            f"    TOTAL waste per capita:          "
            f"{self.waste_per_capita.total_waste():.2f}",
            f"",
            f"  per-capita waste ratio:            "
            f"{self.per_capita_waste_ratio():.2%}",
            f"",
            f"  aggregate:",
            f"    total available capacity:        "
            f"{self.total_available_capacity():,.0f}",
            f"    total realized productive:       "
            f"{self.total_realized_productive():,.0f}",
            f"    total waste:                     "
            f"{self.total_waste():,.0f}",
        ]
        return "\n".join(lines)


def compare_eras(
    era_a: CivilizationAudit,
    era_b: CivilizationAudit,
) -> str:
    """Comparative summary across two civilizational eras."""
    lines = [
        f"Era comparison: {era_a.era_name} vs {era_b.era_name}",
        "",
        f"                           {era_a.era_name:>20s} {era_b.era_name:>20s}",
        f"  population              {era_a.population_size:>20,} "
        f"{era_b.population_size:>20,}",
        f"  avail. cap. per capita  {era_a.available_capacity_per_capita:>20.2f} "
        f"{era_b.available_capacity_per_capita:>20.2f}",
        f"  realized per capita     {era_a.realized_productive_capacity_per_capita:>20.2f} "
        f"{era_b.realized_productive_capacity_per_capita:>20.2f}",
        f"  inst. waste per capita  {era_a.waste_per_capita.institutional_waste:>20.2f} "
        f"{era_b.waste_per_capita.institutional_waste:>20.2f}",
        f"  dep. waste per capita   {era_a.waste_per_capita.forced_dependency_waste:>20.2f} "
        f"{era_b.waste_per_capita.forced_dependency_waste:>20.2f}",
        f"  labor waste per capita  {era_a.waste_per_capita.labor_waste:>20.2f} "
        f"{era_b.waste_per_capita.labor_waste:>20.2f}",
        f"  pot. waste per capita   {era_a.waste_per_capita.potential_waste:>20.2f} "
        f"{era_b.waste_per_capita.potential_waste:>20.2f}",
        f"  waste ratio             {era_a.per_capita_waste_ratio():>19.2%} "
        f"{era_b.per_capita_waste_ratio():>19.2%}",
        "",
    ]
    delta_per_capita_realized = (
        era_b.realized_productive_capacity_per_capita
        - era_a.realized_productive_capacity_per_capita
    )
    lines.append(
        f"  delta realized/capita ({era_b.era_name} - {era_a.era_name}): "
        f"{delta_per_capita_realized:+.2f}"
    )
    # what the second era would produce per capita at the first era's waste
    lines.append("")
    lines.append(
        f"  If {era_b.era_name} had {era_a.era_name}'s waste ratio:"
    )
    counterfactual_realized = era_b.available_capacity_per_capita * (
        1.0 - era_a.per_capita_waste_ratio()
    )
    lines.append(
        f"    realized per capita would be: {counterfactual_realized:.2f} "
        f"(actual: {era_b.realized_productive_capacity_per_capita:.2f})"
    )
    return "\n".join(lines)


# ===========================================================================
# HISTORICAL ERA CONSTRUCTORS
# ===========================================================================
#
# These are first-order models, not empirical history. They reflect
# structural features of the institutional systems of each era, not
# specific individuals. Users can tune parameters to test scenarios.
# The goal: make the waste categories visible as comparative numbers,
# not to claim historical precision.


def bronze_age_audit(population_size: int = 10_000_000) -> CivilizationAudit:
    """Bronze Age (~1500 BCE) — craft-workshop economy.

    Model assumptions:
      - most people work in craft / agriculture matched to local skill
      - hierarchy is by competence at the task, not abstract rank
      - dependency structures minimal — elderly supported by family
      - labor waste low because work directly produces food/shelter/tools
      - potential waste exists (geography, class) but fit-discovery
        happens within the community (apprenticeship, family trade)
    """
    return CivilizationAudit(
        era_name="Bronze Age",
        population_size=population_size,
        available_capacity_per_capita=1.0,
        realized_productive_capacity_per_capita=0.70,
        waste_per_capita=WasteBreakdown(
            institutional_waste=0.05,
            forced_dependency_waste=0.05,
            labor_waste=0.05,
            potential_waste=0.15,
        ),
    )


def renaissance_audit(population_size: int = 60_000_000) -> CivilizationAudit:
    """Renaissance (~1500) — workshop + apprentice + patronage economy.

    Model assumptions:
      - workshop/apprenticeship structure amplifies capacity-fit for
        those who find the right master
      - patronage system allows hyperfocused polymaths (Leonardo,
        Michelangelo) to realize extraordinary capacity
      - more institutional structure than Bronze Age but still
        capacity-fit-oriented for skilled workers
      - dependency waste higher than Bronze Age (emerging poor laws,
        guild restrictions) but lower than modern
      - labor waste low — craft still produces directly
      - potential waste high for peasants (majority of population)
    """
    return CivilizationAudit(
        era_name="Renaissance",
        population_size=population_size,
        available_capacity_per_capita=1.0,
        realized_productive_capacity_per_capita=0.55,
        waste_per_capita=WasteBreakdown(
            institutional_waste=0.10,
            forced_dependency_waste=0.08,
            labor_waste=0.07,
            potential_waste=0.20,
        ),
    )


def modern_audit(population_size: int = 8_000_000_000) -> CivilizationAudit:
    """Modern (~2025) — compliance-optimized institutional economy.

    Model assumptions:
      - most work done through large institutions optimized for
        compliance, control, predictability
      - institutional fit is poor for a large fraction of workers
        (neurodivergent, creative, hands-on learners)
      - means-tested dependency systems create structural traps
      - compliance theater, surveillance overhead, redundant
        management layers burn substantial capacity on null work
      - potential waste enormous — most people never discover what
        their capacity is under fit conditions because fit isn't
        offered
      - per-capita innovation lower than earlier eras despite
        100x+ population and better tools, because realized capacity
        per person is LOWER
    """
    return CivilizationAudit(
        era_name="Modern",
        population_size=population_size,
        available_capacity_per_capita=1.0,
        realized_productive_capacity_per_capita=0.25,
        waste_per_capita=WasteBreakdown(
            institutional_waste=0.25,
            forced_dependency_waste=0.15,
            labor_waste=0.15,
            potential_waste=0.20,
        ),
    )


def capacity_fit_economy_audit(
    population_size: int = 8_000_000_000,
) -> CivilizationAudit:
    """Hypothetical modern economy with capacity_fit as default strategy.

    Model assumptions:
      - institutions designed around capacity discovery, not compliance
      - no means-tested dependency traps — contribution valued at
        realized capacity regardless of hours or official employment
      - labor waste minimal — null work is recognized and eliminated
      - potential waste reduced by early capacity-fit assessment,
        flexible learning structures, multiple pathways
      - amplification common (fit > 1.0) because environment matches
        neurology
      - modeled as what the framework's capacity_fit strategy produces
        when run at civilizational scale
    """
    return CivilizationAudit(
        era_name="Capacity-Fit",
        population_size=population_size,
        available_capacity_per_capita=1.5,  # amplification
        realized_productive_capacity_per_capita=1.25,
        waste_per_capita=WasteBreakdown(
            institutional_waste=0.10,
            forced_dependency_waste=0.03,
            labor_waste=0.05,
            potential_waste=0.07,
        ),
    )
