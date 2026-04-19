"""
tests/test_scaffold.py

Smoke test. Wires basins -> infrastructure -> cascade -> accounting -> verdict
and confirms the pipeline runs and produces coherent output.

Run:  python -m tests.test_scaffold
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin
)
from infrastructure import (
    new_foundation_system, new_buried_utility_system, new_hvac_system,
    new_thermal_envelope_system, new_cooling_system,
    new_biological_service_system,
)
from cascade import predict_failures, cascade_cost
from accounting import compute_flow
from verdict import assess


def scenario_healthy():
    basins = {
        "soil": new_soil_basin(),
        "air": new_air_basin(),
        "water": new_water_basin(),
        "biology": new_biology_basin(),
    }
    return basins


def scenario_degrading():
    """Moderately degraded basins, some trajectories negative."""
    basins = scenario_healthy()
    # soil losing carbon and bearing
    basins["soil"].state["carbon_fraction"] = 0.025
    basins["soil"].state["bearing_capacity"] = 0.7
    basins["soil"].trajectory["carbon_fraction"] = -0.002
    basins["soil"].trajectory["bearing_capacity"] = -0.02
    # air degrading
    basins["air"].state["particulate_load"] = 0.45
    basins["air"].state["filter_burden"] = 2.5
    basins["air"].trajectory["particulate_load"] = 0.01
    basins["air"].trajectory["filter_burden"] = 0.05
    # water pulling down
    basins["water"].state["aquifer_level"] = 0.6
    basins["water"].trajectory["aquifer_level"] = -0.03
    # pollinators dropping
    basins["biology"].state["pollinator_index"] = 0.5
    basins["biology"].trajectory["pollinator_index"] = -0.02
    return basins


def systems():
    return [
        new_foundation_system(),
        new_buried_utility_system(),
        new_hvac_system(),
        new_thermal_envelope_system(),
        new_cooling_system(),
        new_biological_service_system(),
    ]


def run(label, basins, revenue=1000.0, opex=700.0, regen_paid=0.0):
    syss = systems()
    flow = compute_flow(
        revenue=revenue,
        direct_operating_cost=opex,
        regeneration_paid=regen_paid,
        basins=basins,
        systems=syss,
    )
    v = assess(basins, flow)
    preds = predict_failures(syss, basins)

    print(f"\n=== {label} ===")
    print(f"signal:            {v.sustainable_yield_signal}")
    print(f"trajectory:        {v.basin_trajectory}")
    print(f"time_to_red:       {v.time_to_red}")
    print(f"reported profit:   {v.reported_profit:.2f}")
    print(f"metabolic profit:  {v.metabolic_profit:.2f}")
    print(f"profit gap:        {v.profit_gap:.2f}")
    print(f"forced drawdown:   {v.forced_drawdown:.2f}")
    print(f"regen debt:        {v.regeneration_debt:.2f}")
    if v.warnings:
        print("warnings:")
        for w in v.warnings:
            print(f"  - {w}")
    print("failure order (first -> last):")
    for p in preds[:3]:
        print(f"  {p.system_name:25s}  rate={p.effective_rate:.4f}  "
              f"ttf={p.time_to_failure:8.2f}  "
              f"dominant={p.dominant_basin[0]}.{p.dominant_basin[1]}")


if __name__ == "__main__":
    run("HEALTHY basins, no regen paid", scenario_healthy())
    run("DEGRADING basins, no regen paid", scenario_degrading())
    run("DEGRADING basins, regen paid", scenario_degrading(), regen_paid=500.0)
