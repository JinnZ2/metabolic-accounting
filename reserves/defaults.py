"""
reserves/defaults.py

Default reserve configurations for the standard basin types.

Literature-anchored choices:
  - capacity 100 xdu, cliff 20 xdu (normalized scale; 20% of capacity
    is the exhaustion point, matching typical ecological buffer cliffs
    observed in lake / soil / forest studies)
  - regen rate ranges calibrated from soil recovery literature:
      slight degradation: 12-15 years to equilibrium
      moderate: 30-35 years
      severe: 60-65 years
    Scaling those into per-period recovery fractions gives the
    per_period rates below for the soil class; other basins scaled
    by type.

Community (social) reserves — the critical addition.
  Communities are the original load-bearing substrate — they have
  been absorbing invisible labor for generations (child-raising,
  elder care, civic participation, institutional maintenance,
  generational knowledge transfer) without being priced or measured.
  This matches the "soil was free" assumption that the environmental
  layer already corrects. The social layer applies the same correction.

  Calibration:
    - LARGER capacity than environmental reserves (150 xdu default)
      reflecting the deep stock built up by generations of unwaged
      community maintenance
    - HIGHER cliff fraction (0.3 vs 0.2) because social systems collapse
      earlier in their depletion curve — at 30% remaining, not 20%,
      the protective effect of social infrastructure already fails
      (Kim 2024 social-infrastructure threshold)
    - SLOWER regen rates (~0.3x environmental) reflecting Case & Deaton
      observation that social institutions take ~3x as long to rebuild
      as comparable environmental stocks once hollowed out

See docs/LITERATURE.md for the full anchor list.
"""

from typing import Dict, List, Tuple

from .pools import SecondaryReserve, TertiaryPool


# ---------- standard tertiary pools at a site ----------

TERTIARY_POOL_NAMES = [
    "landscape_reserve",
    "watershed_reserve",
    "airshed_reserve",
    "organizational_reserve",
    # social tertiary pools — the community-level shared substrates
    "social_fabric_reserve",           # overall local social cohesion
    "generational_transmission",       # capacity to pass skills/knowledge
                                        # between generations
    "institutional_stock",             # local institutions (schools,
                                        # unions, religious orgs, civic groups)
    "civic_trust_reserve",             # trust in institutions and
                                        # willingness to cooperate
]


def new_standard_tertiary_pools() -> Dict[str, TertiaryPool]:
    return {
        "landscape_reserve": TertiaryPool(
            name="landscape_reserve",
            capacity=1000.0,
            stock=1000.0,
            cliff=200.0,
        ),
        "watershed_reserve": TertiaryPool(
            name="watershed_reserve",
            capacity=1500.0,         # larger — aquifer-scale
            stock=1500.0,
            cliff=300.0,
        ),
        "airshed_reserve": TertiaryPool(
            name="airshed_reserve",
            capacity=800.0,
            stock=800.0,
            cliff=160.0,
        ),
        "organizational_reserve": TertiaryPool(
            name="organizational_reserve",
            capacity=500.0,           # smallest — labor/attention constrained
            stock=500.0,
            cliff=100.0,
        ),
        # social tertiary pools — calibrated larger than environmental
        # because generations of invisible community labor built up deep
        # stocks; but higher cliff fraction (0.3 not 0.2) because
        # social-infrastructure protective effects fail earlier
        # (Kim 2024)
        "social_fabric_reserve": TertiaryPool(
            name="social_fabric_reserve",
            capacity=2000.0,          # deep generational stock
            stock=2000.0,
            cliff=600.0,              # 30% cliff, not 20%
        ),
        "generational_transmission": TertiaryPool(
            name="generational_transmission",
            capacity=1200.0,
            stock=1200.0,
            cliff=360.0,              # 30% cliff
        ),
        "institutional_stock": TertiaryPool(
            name="institutional_stock",
            capacity=1500.0,
            stock=1500.0,
            cliff=450.0,              # 30% cliff
        ),
        "civic_trust_reserve": TertiaryPool(
            name="civic_trust_reserve",
            capacity=1000.0,
            stock=1000.0,
            cliff=300.0,              # 30% cliff
        ),
    }


# ---------- per-basin-type secondary reserve specs ----------

# Mapping from (basin_type, metric_key) to (capacity, cliff, regen_per_period,
# tertiary_targets). Values are first-pass estimates anchored to the
# literature recovery-time bands; see docs/LITERATURE.md.

SECONDARY_SPECS: Dict[Tuple[str, str], Tuple[float, float, float, List[str]]] = {
    # soil
    ("soil", "bearing_capacity"):   (100.0, 20.0, 0.5, ["landscape_reserve"]),
    ("soil", "carbon_fraction"):    (100.0, 20.0, 2.0, ["landscape_reserve"]),    # soil C regens fastest
    ("soil", "aggregation_index"):  (100.0, 20.0, 1.0, ["landscape_reserve"]),
    ("soil", "permeability"):       (100.0, 20.0, 0.8, ["landscape_reserve", "watershed_reserve"]),
    ("soil", "microbial_load"):     (100.0, 20.0, 3.0, ["landscape_reserve"]),    # fast turnover

    # air
    ("air", "particulate_load"):    (100.0, 20.0, 2.0, ["airshed_reserve"]),
    ("air", "chemical_load"):       (100.0, 20.0, 1.5, ["airshed_reserve"]),
    ("air", "oxygen_availability"): (100.0, 20.0, 1.5, ["airshed_reserve", "landscape_reserve"]),
    ("air", "filter_burden"):       (100.0, 20.0, 3.0, ["organizational_reserve"]),  # ops-managed

    # water
    ("water", "aquifer_level"):        (100.0, 20.0, 0.3, ["watershed_reserve"]),    # slow recharge
    ("water", "surface_flow"):         (100.0, 20.0, 1.0, ["watershed_reserve", "landscape_reserve"]),
    ("water", "contamination_load"):   (100.0, 20.0, 0.5, ["watershed_reserve"]),
    ("water", "temperature_anomaly"):  (100.0, 20.0, 0.8, ["watershed_reserve", "airshed_reserve"]),

    # biology
    ("biology", "pollinator_index"):      (100.0, 20.0, 0.8, ["landscape_reserve"]),
    ("biology", "microbial_diversity"):   (100.0, 20.0, 1.5, ["landscape_reserve", "watershed_reserve"]),
    ("biology", "apex_indicator"):        (100.0, 20.0, 0.2, ["landscape_reserve"]),  # slowest recovery
    ("biology", "vegetation_cover"):      (100.0, 20.0, 1.0, ["landscape_reserve", "watershed_reserve"]),

    # community — the social substrate
    # Calibration:
    #   - LARGER capacity (150) reflecting generational accumulation of
    #     invisible community labor
    #   - HIGHER cliff (45 = 30%) because social systems fail earlier
    #     (Kim 2024 social-infrastructure protective threshold)
    #   - SLOWER regen (~0.3x environmental) because social institutions
    #     take ~3x longer to rebuild than comparable environmental stocks
    #     (Case & Deaton 2020 decadal-lag finding)
    #   - tertiary targets routed to social-substrate pools; only
    #     economic_security also connects to organizational_reserve
    #     (firms can cushion their own workforce economically)
    ("community", "economic_security"):       (150.0, 45.0, 0.6, ["social_fabric_reserve", "organizational_reserve"]),
    ("community", "social_capital"):          (150.0, 45.0, 0.3, ["social_fabric_reserve", "institutional_stock"]),
    ("community", "family_formation"):        (150.0, 45.0, 0.2, ["social_fabric_reserve"]),
    ("community", "youth_retention"):         (150.0, 45.0, 0.1, ["generational_transmission", "social_fabric_reserve"]),
    ("community", "generational_knowledge"):  (150.0, 45.0, 0.1, ["generational_transmission", "institutional_stock"]),
    ("community", "civic_engagement"):        (150.0, 45.0, 0.4, ["civic_trust_reserve", "institutional_stock"]),
}


def new_secondary_reserves_for_basin(
    basin_type: str,
    basin_name: str,
    metric_keys,
) -> Dict[str, SecondaryReserve]:
    """Build a set of secondary reserves for one basin, keyed by metric."""
    reserves: Dict[str, SecondaryReserve] = {}
    for key in metric_keys:
        spec = SECONDARY_SPECS.get((basin_type, key))
        if spec is None:
            # sensible default for unknown metric: smallest, slowest regen
            spec = (100.0, 20.0, 0.5, ["landscape_reserve"])
        cap, cliff, regen, targets = spec
        reserves[key] = SecondaryReserve(
            metric_key=key,
            basin_name=basin_name,
            capacity=cap,
            stock=cap,
            cliff=cliff,
            regen_rate_per_period=regen,
            tertiary_targets=list(targets),
        )
    return reserves
