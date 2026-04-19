"""
infrastructure/systems.py

Infrastructure systems whose function is coupled to basin states.

Each system has:
  - a nominal failure rate (baseline, all basins healthy)
  - a set of basin dependencies (which basin keys drive the rate)
  - a cost profile (maintenance, repair, replacement)
  - a current condition (accumulates damage as basins degrade)

Failure rate is NOT a function of age alone. It is a function of
basin trajectory integrated over time.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class InfrastructureSystem:
    name: str
    nominal_failure_rate: float = 0.01     # events per unit time, baseline
    current_condition: float = 1.0          # 1.0 fresh, 0.0 failed
    baseline_repair_cost: float = 1.0
    replacement_cost: float = 10.0
    # dependencies: list of (basin_name, key, sensitivity)
    # sensitivity = how much this system's failure rate multiplies
    # when the corresponding basin metric crosses its cliff
    dependencies: List[Tuple[str, str, float]] = field(default_factory=list)
    notes: str = ""


def new_foundation_system(name: str = "foundation") -> InfrastructureSystem:
    return InfrastructureSystem(
        name=name,
        nominal_failure_rate=0.002,
        baseline_repair_cost=50.0,
        replacement_cost=500.0,
        dependencies=[
            ("soil", "bearing_capacity", 10.0),
            ("soil", "aggregation_index", 4.0),
            ("water", "aquifer_level", 3.0),   # subsidence coupling
        ],
        notes="Foundation integrity. Primary coupling: soil bearing.",
    )


def new_buried_utility_system(name: str = "buried_utilities") -> InfrastructureSystem:
    return InfrastructureSystem(
        name=name,
        nominal_failure_rate=0.01,
        baseline_repair_cost=10.0,
        replacement_cost=100.0,
        dependencies=[
            ("soil", "aggregation_index", 5.0),
            ("soil", "permeability", 3.0),
            ("water", "contamination_load", 2.0),
        ],
        notes="Buried plumbing and electrical. Soil shear and chemistry.",
    )


def new_hvac_system(name: str = "hvac") -> InfrastructureSystem:
    return InfrastructureSystem(
        name=name,
        nominal_failure_rate=0.02,
        baseline_repair_cost=5.0,
        replacement_cost=50.0,
        dependencies=[
            ("air", "particulate_load", 6.0),
            ("air", "chemical_load", 4.0),
            ("air", "filter_burden", 3.0),
        ],
        notes="HVAC and filter systems. Primary coupling: air.",
    )


def new_thermal_envelope_system(name: str = "thermal_envelope") -> InfrastructureSystem:
    return InfrastructureSystem(
        name=name,
        nominal_failure_rate=0.005,
        baseline_repair_cost=20.0,
        replacement_cost=200.0,
        dependencies=[
            ("soil", "bearing_capacity", 3.0),   # settlement cracks envelope
            ("water", "temperature_anomaly", 2.0),
        ],
        notes="Envelope integrity. Couples to foundation settlement.",
    )


def new_cooling_system(name: str = "process_cooling") -> InfrastructureSystem:
    return InfrastructureSystem(
        name=name,
        nominal_failure_rate=0.015,
        baseline_repair_cost=8.0,
        replacement_cost=80.0,
        dependencies=[
            ("water", "aquifer_level", 5.0),
            ("water", "temperature_anomaly", 6.0),
            ("water", "contamination_load", 3.0),
        ],
        notes="Process cooling. Primary coupling: water availability and temperature.",
    )


def new_biological_service_system(name: str = "biological_services") -> InfrastructureSystem:
    """Pollination, pest control, soil regeneration — ecosystem services as
    infrastructure. Failure means paid replacement (imported pollinators,
    pesticide, fertilizer) or yield collapse."""
    return InfrastructureSystem(
        name=name,
        nominal_failure_rate=0.005,
        baseline_repair_cost=30.0,
        replacement_cost=300.0,
        dependencies=[
            ("biology", "pollinator_index", 8.0),
            ("biology", "microbial_diversity", 5.0),
            ("biology", "vegetation_cover", 3.0),
        ],
        notes="Ecosystem services treated as infrastructure. Replacement is costly.",
    )
