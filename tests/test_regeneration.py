"""
tests/test_regeneration.py

Test the per-metric regeneration cost functions on three scenarios:
  1. healthy basins
  2. moderate degradation
  3. irreversibility triggered (vegetation collapsed -> pollinator irreversible)

Run:  python -m tests.test_regeneration
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math import isinf

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from infrastructure import (
    new_foundation_system, new_buried_utility_system, new_hvac_system,
    new_thermal_envelope_system, new_cooling_system,
    new_biological_service_system,
)
from accounting import compute_flow, required_regeneration_cost_detailed
from verdict import assess


def healthy_basins():
    return {
        "soil": new_soil_basin(),
        "air": new_air_basin(),
        "water": new_water_basin(),
        "biology": new_biology_basin(),
    }


def moderate_degradation():
    b = healthy_basins()
    b["soil"].state["bearing_capacity"] = 0.75
    b["soil"].state["carbon_fraction"] = 0.03
    b["soil"].trajectory["carbon_fraction"] = -0.002
    b["air"].state["particulate_load"] = 0.3
    b["air"].state["chemical_load"] = 0.3
    b["air"].trajectory["particulate_load"] = 0.01
    b["water"].state["aquifer_level"] = 0.7
    b["water"].trajectory["aquifer_level"] = -0.02
    b["biology"].state["pollinator_index"] = 0.65
    return b


def irreversible_state():
    """Vegetation below cliff triggers pollinator irreversibility.
    Aquifer collapsed with thermal stress triggers aquifer irreversibility."""
    b = moderate_degradation()
    b["biology"].state["vegetation_cover"] = 0.45     # cliff 0.5
    b["biology"].state["pollinator_index"] = 0.3
    b["water"].state["aquifer_level"] = 0.35          # past cliff 0.5, below 0.4 (0.8*cliff)
    b["water"].state["temperature_anomaly"] = 3.5     # past cliff 3.0
    b["biology"].state["apex_indicator"] = 0.2        # past cliff 0.3
    return b


def systems():
    return [
        new_foundation_system(),
        new_buried_utility_system(),
        new_hvac_system(),
        new_thermal_envelope_system(),
        new_cooling_system(),
        new_biological_service_system(),
    ]


def run(label, basins, revenue=1000.0, opex=600.0, regen_paid=0.0):
    syss = systems()
    flow = compute_flow(
        revenue=revenue,
        direct_operating_cost=opex,
        regeneration_paid=regen_paid,
        basins=basins,
        systems=syss,
    )
    v = assess(basins, flow)

    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    print(f"signal:            {v.sustainable_yield_signal}")
    print(f"trajectory:        {v.basin_trajectory}")
    print(f"time_to_red:       {v.time_to_red}")
    req = "infinite" if isinf(flow.regeneration_required) else f"{flow.regeneration_required:.2f}"
    print(f"regen required:    {req}")
    print(f"cascade burn:      {flow.cascade_burn:.2f}")
    print(f"reported profit:   {v.reported_profit:.2f}")
    mp = "-infinite" if isinf(v.metabolic_profit) else f"{v.metabolic_profit:.2f}"
    print(f"metabolic profit:  {mp}")
    if v.irreversible_metrics:
        print(f"irreversible:      {', '.join(v.irreversible_metrics)}")
    if v.warnings:
        print("warnings:")
        for w in v.warnings:
            print(f"  - {w}")

    if flow.regen_breakdown:
        print("\nregen breakdown (non-zero entries):")
        print(f"  {'basin.key':35s} {'deg':>6s} {'base':>8s} {'nl':>8s} {'cost':>10s}")
        for rc in flow.regen_breakdown:
            if rc.total_cost == 0 and rc.degradation == 0:
                continue
            key = f"{rc.basin_name}.{rc.metric_key}"
            cost = "inf" if isinf(rc.total_cost) else f"{rc.total_cost:>10.2f}"
            base = "inf" if isinf(rc.base_cost) else f"{rc.base_cost:>8.1f}"
            flag = " IRR" if rc.irreversible else ""
            print(f"  {key:35s} {rc.degradation:>6.3f} {base:>8} "
                  f"{rc.nonlinearity_factor:>8.3f} {cost:>10}{flag}")


if __name__ == "__main__":
    run("1. HEALTHY", healthy_basins())
    run("2. MODERATE DEGRADATION", moderate_degradation())
    run("3. IRREVERSIBILITY TRIGGERED", irreversible_state())
