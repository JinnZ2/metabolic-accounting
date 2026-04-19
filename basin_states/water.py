"""
basin_states/water.py

Water as a basin state.

Key state properties:
  - aquifer_level        (normalized vs historical sustainable level)
  - surface_flow         (normalized vs baseline)
  - contamination_load   (0 clean, 1 severe — compound index)
  - temperature_anomaly  (deviation from baseline, matters for cooling and biology)

Water governs:
  cooling systems, process water supply, sanitation, fire suppression
  capacity, biological substrate (riparian and microbial), soil moisture
  feedback into bearing capacity.
"""

from .base import BasinState


def new_water_basin(name: str = "site_water") -> BasinState:
    return BasinState(
        name=name,
        basin_type="water",
        state={
            "aquifer_level": 1.0,
            "surface_flow": 1.0,
            "contamination_load": 0.05,
            "temperature_anomaly": 0.0,
        },
        capacity={
            "aquifer_level": 1.0,
            "surface_flow": 1.0,
            "contamination_load": 1.0,
            "temperature_anomaly": 5.0,     # degrees C tolerance ceiling
        },
        trajectory={
            "aquifer_level": 0.0,
            "surface_flow": 0.0,
            "contamination_load": 0.0,
            "temperature_anomaly": 0.0,
        },
        cliff_thresholds={
            "aquifer_level": 0.5,
            "surface_flow": 0.4,
            "contamination_load": 0.3,
            "temperature_anomaly": 3.0,
        },
        high_is_bad={"contamination_load", "temperature_anomaly"},
        notes="Water basin. Couples to soil bearing, biology, and cooling infrastructure.",
    )
