"""
basin_states/soil.py

Soil substrate as a load-bearing state variable.

Key state properties:
  - bearing_capacity    (kPa or relative) — what foundations rest on
  - carbon_fraction     — soil organic carbon, drives aggregation and strength
  - microbial_load      — biological activity, drives nutrient cycling
  - permeability        — water infiltration and drainage
  - aggregation_index   — structural stability against compaction and erosion

Soil is not a line item. It is the upstream state that governs:
  foundation integrity, buried utility integrity, thermal conductivity,
  water table stability, vegetation support.
"""

from .base import BasinState


def new_soil_basin(name: str = "site_soil") -> BasinState:
    return BasinState(
        name=name,
        basin_type="soil",
        state={
            "bearing_capacity": 1.0,      # normalized 0..1
            "carbon_fraction": 0.05,       # 5% SOC, healthy baseline
            "microbial_load": 1.0,         # normalized 0..1
            "permeability": 1.0,           # normalized 0..1
            "aggregation_index": 1.0,      # normalized 0..1
        },
        capacity={
            "bearing_capacity": 1.0,
            "carbon_fraction": 0.08,       # maximum sustainable SOC for region
            "microbial_load": 1.0,
            "permeability": 1.0,
            "aggregation_index": 1.0,
        },
        trajectory={
            "bearing_capacity": 0.0,
            "carbon_fraction": 0.0,
            "microbial_load": 0.0,
            "permeability": 0.0,
            "aggregation_index": 0.0,
        },
        cliff_thresholds={
            # below these, cascade failures trigger
            "bearing_capacity": 0.6,
            "carbon_fraction": 0.02,
            "microbial_load": 0.3,
            "permeability": 0.4,
            "aggregation_index": 0.5,
        },
        high_is_bad=set(),   # all soil metrics: higher is healthier
        notes="Soil substrate. Upstream of foundation, utilities, thermal, water.",
    )
