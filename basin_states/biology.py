"""
basin_states/biology.py

Biological systems as a basin state.

Key state properties:
  - pollinator_index       (keystone for agricultural and horticultural coupling)
  - microbial_diversity    (soil and water coupled; drives nutrient and waste cycling)
  - apex_indicator         (presence/health of apex predators or sentinel species)
  - vegetation_cover       (fraction; drives soil stability, air filtration, water retention)

Biology is simultaneously a basin and a cascade amplifier. Loss of pollinators
collapses agricultural yield. Loss of microbial diversity degrades soil and water
simultaneously. Loss of vegetation accelerates soil erosion and air particulate load.
"""

from .base import BasinState


def new_biology_basin(name: str = "site_biology") -> BasinState:
    return BasinState(
        name=name,
        basin_type="biology",
        state={
            "pollinator_index": 1.0,
            "microbial_diversity": 1.0,
            "apex_indicator": 1.0,
            "vegetation_cover": 1.0,
        },
        capacity={
            "pollinator_index": 1.0,
            "microbial_diversity": 1.0,
            "apex_indicator": 1.0,
            "vegetation_cover": 1.0,
        },
        trajectory={
            "pollinator_index": 0.0,
            "microbial_diversity": 0.0,
            "apex_indicator": 0.0,
            "vegetation_cover": 0.0,
        },
        cliff_thresholds={
            "pollinator_index": 0.4,
            "microbial_diversity": 0.5,
            "apex_indicator": 0.3,
            "vegetation_cover": 0.5,
        },
        high_is_bad=set(),   # all biology metrics: higher is healthier
        notes="Biology basin. Amplifies and is amplified by soil, water, and air basins.",
    )
