"""
distributional/tiers.py

Tier determination from basin state. Vector approach — a firm can be
GREEN on air, AMBER on water, BLACK on biology. Each basin type has
its own tier, and each layer (worker access, capital access,
infrastructure access, community capacity) responds to the relevant
basins.

Tier mapping from our framework:
  GREEN:  all reserves healthy, no primary irreversibility
  AMBER:  primary reserves under pressure, secondary reserves draining
  RED:    secondary reserves exhausted on at least one metric,
          tertiary pools approaching cliff
  BLACK:  primary irreversibility OR tertiary pool past cliff
          (landscape-scale damage signature)

This is a first-pass mapping. Thresholds are exposed as parameters so
users can tune them for their jurisdiction or industry.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class Tier(Enum):
    GREEN = 0
    AMBER = 1
    RED = 2
    BLACK = 3

    def degradation_level(self) -> float:
        """0.0 for GREEN, 1.0 for BLACK, linear between."""
        return self.value / 3.0


@dataclass
class TierAssignment:
    """Per-basin-type tier assignment for a single firm."""
    by_basin_type: Dict[str, Tier] = field(default_factory=dict)
    # basin_type -> Tier, e.g. {"soil": Tier.AMBER, "water": Tier.BLACK}

    def overall_tier(self) -> Tier:
        """Worst tier across all basin types — conservative aggregate."""
        if not self.by_basin_type:
            return Tier.GREEN
        return max(self.by_basin_type.values(), key=lambda t: t.value)

    def basins_at_or_worse_than(self, tier: Tier) -> List[str]:
        """Which basin types are at or worse than the given tier."""
        return [bt for bt, t in self.by_basin_type.items()
                if t.value >= tier.value]

    def basins_at(self, tier: Tier) -> List[str]:
        """Which basin types are exactly at the given tier."""
        return [bt for bt, t in self.by_basin_type.items() if t == tier]


def _basin_type_from_name(basin_name: str) -> str:
    """Extract basin type from a basin name like 'site_soil' -> 'soil'."""
    # convention: basin names follow pattern '{prefix}_{type}'
    # e.g. 'site_soil' -> 'soil', 'plant_water' -> 'water'
    parts = basin_name.rsplit("_", 1)
    if len(parts) == 2:
        return parts[1]
    return basin_name


def determine_tier_for_basin(
    basin_name: str,
    basin,
    secondary_reserves: Optional[Dict] = None,
    tertiary_pools: Optional[Dict] = None,
    tertiary_mapping: Optional[Dict[str, List[str]]] = None,
) -> Tier:
    """Determine tier for a single basin.

    basin: a BasinState object
    secondary_reserves: dict mapping basin_name -> {metric_key: SecondaryReserve}
    tertiary_pools: dict of tertiary pools on the site
    tertiary_mapping: basin_type -> list of tertiary pool names
                      that reflect landscape-scale damage for that basin

    Logic:
      BLACK: any metric past its cliff (irreversibility flag) OR
             any corresponding tertiary pool past cliff
      RED:   any corresponding secondary reserve exhausted OR
             any corresponding tertiary pool < 30% capacity
      AMBER: any metric trending toward cliff (time_to_cliff < infinity) OR
             any corresponding secondary reserve < 50% capacity
      GREEN: else
    """
    basin_type = _basin_type_from_name(basin_name)

    # check primary irreversibility
    for key in basin.state:
        frac = basin.fraction_remaining(key)
        # frac < 0 means past cliff
        if frac < 0:
            return Tier.BLACK

    # check corresponding tertiary pools
    if tertiary_pools and tertiary_mapping:
        relevant_pools = tertiary_mapping.get(basin_type, [])
        for pool_name in relevant_pools:
            pool = tertiary_pools.get(pool_name)
            if pool is None:
                continue
            if pool.past_cliff():
                return Tier.BLACK
            if pool.fraction_remaining() < 0.3:
                return Tier.RED

    # check secondary reserves for exhaustion
    if secondary_reserves:
        basin_secondaries = secondary_reserves.get(basin_name, {})
        for key, reserve in basin_secondaries.items():
            if reserve.is_exhausted():
                return Tier.RED

    # check secondary reserves for pressure
    if secondary_reserves:
        basin_secondaries = secondary_reserves.get(basin_name, {})
        for key, reserve in basin_secondaries.items():
            if reserve.fraction_remaining() < 0.5:
                return Tier.AMBER

    # check metric trajectories
    for key in basin.state:
        ttc = basin.time_to_cliff(key)
        if ttc is not None and ttc != float('inf'):
            return Tier.AMBER

    return Tier.GREEN


# Default mapping of basin type to tertiary pools that reflect
# landscape-scale damage for that basin
DEFAULT_TERTIARY_MAPPING: Dict[str, List[str]] = {
    "soil": ["landscape_reserve"],
    "water": ["watershed_reserve"],
    "air": ["airshed_reserve"],
    "biology": ["landscape_reserve"],   # biodiversity tied to landscape
}


def determine_tiers(
    basins: Dict,
    secondary_reserves: Optional[Dict] = None,
    tertiary_pools: Optional[Dict] = None,
    tertiary_mapping: Optional[Dict[str, List[str]]] = None,
) -> TierAssignment:
    """Determine per-basin-type tiers for a firm.

    Returns a TierAssignment keyed by basin type (soil, water, air,
    biology). If multiple basins share a type, the worst tier wins.
    """
    if tertiary_mapping is None:
        tertiary_mapping = DEFAULT_TERTIARY_MAPPING

    per_basin_tiers: Dict[str, Tier] = {}
    for basin_name, basin in basins.items():
        t = determine_tier_for_basin(
            basin_name=basin_name,
            basin=basin,
            secondary_reserves=secondary_reserves,
            tertiary_pools=tertiary_pools,
            tertiary_mapping=tertiary_mapping,
        )
        btype = _basin_type_from_name(basin_name)
        # if this basin type already has a tier, keep the worst
        if btype in per_basin_tiers:
            if t.value > per_basin_tiers[btype].value:
                per_basin_tiers[btype] = t
        else:
            per_basin_tiers[btype] = t

    return TierAssignment(by_basin_type=per_basin_tiers)
