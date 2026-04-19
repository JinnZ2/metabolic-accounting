"""
basin_states/air.py

Air quality as a basin state.

Key state properties:
  - particulate_load    (PM2.5 / PM10 index, inverse health)
  - chemical_load       (NOx, SOx, VOC index)
  - oxygen_availability (normalized, drops at altitude or in combustion zones)
  - filter_burden       (cost multiplier on intake systems)

Air quality governs:
  HVAC filter replacement rate, combustion equipment efficiency,
  worker health and cognition, sensitive equipment corrosion,
  biological substrate (plant stomata, pollinator viability).
"""

from .base import BasinState


def new_air_basin(name: str = "site_air") -> BasinState:
    return BasinState(
        name=name,
        basin_type="air",
        state={
            "particulate_load": 0.1,        # 0 = clean, 1 = severe
            "chemical_load": 0.1,
            "oxygen_availability": 1.0,
            "filter_burden": 1.0,           # 1.0 = baseline filter cost
        },
        capacity={
            # capacity here means tolerable ceiling for firm operations
            "particulate_load": 1.0,
            "chemical_load": 1.0,
            "oxygen_availability": 1.0,
            "filter_burden": 5.0,           # ceiling on how bad burden can get
        },
        trajectory={
            "particulate_load": 0.0,
            "chemical_load": 0.0,
            "oxygen_availability": 0.0,
            "filter_burden": 0.0,
        },
        cliff_thresholds={
            # for "bad" metrics (load, burden) cliff is upper
            # for "good" metrics (oxygen) cliff is lower
            # direction is declared via high_is_bad below
            "particulate_load": 0.5,
            "chemical_load": 0.5,
            "oxygen_availability": 0.85,
            "filter_burden": 3.0,
        },
        high_is_bad={"particulate_load", "chemical_load", "filter_burden"},
        notes="Air basin. Governs HVAC, combustion, worker health, biological substrate.",
    )
