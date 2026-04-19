"""
tests/test_ramp_comparison.py

Side-by-side comparison of degradation ramp shapes.

Part A: score each ramp shape at fixed cliff distances so the curves
are visible as numbers.

Part B: run the full cascade + accounting pipeline under each ramp on an
identical moderately-degraded basin set so the downstream effect is
visible (failure rates, metabolic profit, time-to-red).

Run:  python -m tests.test_ramp_comparison
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from infrastructure import (
    new_foundation_system, new_buried_utility_system, new_hvac_system,
    new_thermal_envelope_system, new_cooling_system,
    new_biological_service_system,
)
from cascade import (
    predict_failures, cascade_cost, audit_distance,
    linear, power, exponential, logistic,
)
from accounting import compute_flow
from verdict import assess


def moderately_degraded():
    b = {
        "soil": new_soil_basin(),
        "air": new_air_basin(),
        "water": new_water_basin(),
        "biology": new_biology_basin(),
    }
    b["soil"].state["bearing_capacity"] = 0.75
    b["soil"].state["carbon_fraction"] = 0.035
    b["soil"].trajectory["carbon_fraction"] = -0.002
    b["air"].state["particulate_load"] = 0.3
    b["air"].state["chemical_load"] = 0.3
    b["air"].trajectory["particulate_load"] = 0.01
    b["water"].state["aquifer_level"] = 0.7
    b["water"].trajectory["aquifer_level"] = -0.02
    b["biology"].state["pollinator_index"] = 0.65
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


def part_a():
    print("=" * 72)
    print("PART A: ramp output at fixed cliff distances")
    print("=" * 72)
    print(f"{'x':>6s} {'linear':>10s} {'power2':>10s} {'power3':>10s} "
          f"{'exp(k=3)':>10s} {'logistic':>10s}")
    for x in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        a = audit_distance(x)
        print(f"{x:>6.2f} {a.linear:>10.3f} {a.power_2:>10.3f} "
              f"{a.power_3:>10.3f} {a.exponential_3:>10.3f} "
              f"{a.logistic_default:>10.3f}")


def part_b_one(label, ramp):
    basins = moderately_degraded()
    syss = systems()
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=basins, systems=syss, ramp=ramp,
    )
    v = assess(basins, flow)
    preds = predict_failures(syss, basins, ramp=ramp)
    cost = cascade_cost(syss, basins, horizon=1.0, ramp=ramp)
    print(f"\n--- ramp: {label} ---")
    print(f"  signal:             {v.sustainable_yield_signal}")
    print(f"  regen required:     {flow.regeneration_required:>8.2f}")
    print(f"  cascade burn:       {cost:>8.2f}")
    print(f"  reported profit:    {v.reported_profit:>8.2f}")
    print(f"  metabolic profit:   {v.metabolic_profit:>8.2f}")
    print(f"  top 3 failures:")
    for p in preds[:3]:
        print(f"    {p.system_name:22s} rate={p.effective_rate:.4f} "
              f"ttf={p.time_to_failure:7.2f}")


def part_b():
    print("\n" + "=" * 72)
    print("PART B: same degraded basins, different ramps, full pipeline")
    print("=" * 72)
    part_b_one("linear (old default)", linear())
    part_b_one("power p=2 (new default)", power(2.0))
    part_b_one("power p=3", power(3.0))
    part_b_one("exponential k=3", exponential(3.0))
    part_b_one("logistic x0=0.6", logistic(0.6, 10.0))


if __name__ == "__main__":
    part_a()
    part_b()
