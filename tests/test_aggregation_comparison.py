"""
tests/test_aggregation_comparison.py

Side-by-side comparison of the four aggregation rules on identical inputs.

The goal is to SEE the difference in behavior, not just believe it.
The same degrading-basin scenario is run through:

    multiplicative   (original, compounding)
    dominant         (worst-single-metric)
    additive         (linear superposition)
    saturating       (additive then bounded)

For each rule we report:
    - rate multiplier on foundation (3 soil dependencies)
    - rate multiplier on HVAC (3 air dependencies)
    - predicted order of failure
    - cascade cost over one period

Run:  python -m tests.test_aggregation_comparison
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
    predict_failures, cascade_cost, audit_system,
    multiplicative, dominant, additive, saturating,
)


def degrading_basins():
    basins = {
        "soil": new_soil_basin(),
        "air": new_air_basin(),
        "water": new_water_basin(),
        "biology": new_biology_basin(),
    }
    # all three soil metrics near cliff simultaneously
    basins["soil"].state["bearing_capacity"] = 0.7   # cliff 0.6
    basins["soil"].state["aggregation_index"] = 0.6  # cliff 0.5
    basins["soil"].state["permeability"] = 0.5       # cliff 0.4
    # air also degrading across the board
    basins["air"].state["particulate_load"] = 0.45   # cliff 0.5 (HIGH bad)
    basins["air"].state["chemical_load"] = 0.45
    basins["air"].state["filter_burden"] = 2.5       # cliff 3.0
    # water pulling down
    basins["water"].state["aquifer_level"] = 0.6
    basins["water"].state["contamination_load"] = 0.25
    basins["water"].state["temperature_anomaly"] = 2.5
    # biology stressed
    basins["biology"].state["pollinator_index"] = 0.5
    basins["biology"].state["microbial_diversity"] = 0.6
    basins["biology"].state["vegetation_cover"] = 0.6
    return basins


def all_systems():
    return [
        new_foundation_system(),
        new_buried_utility_system(),
        new_hvac_system(),
        new_thermal_envelope_system(),
        new_cooling_system(),
        new_biological_service_system(),
    ]


def print_rule(label, rule, basins, systems):
    print(f"\n--- rule: {label} ---")
    total_cost = cascade_cost(systems, basins, horizon=1.0, rule=rule)
    print(f"cascade_cost (horizon=1): {total_cost:.2f}")
    preds = predict_failures(systems, basins, rule=rule)
    print(f"{'system':25s} {'mult':>8s} {'rate':>10s} {'ttf':>10s}")
    for p in preds:
        # effective_rate already includes nominal; to get multiplier:
        from cascade.detector import _contributions_for
        nominal = next(
            s.nominal_failure_rate for s in systems if s.name == p.system_name
        )
        mult = p.effective_rate / nominal if nominal > 0 else float("inf")
        print(
            f"{p.system_name:25s} {mult:>8.2f} {p.effective_rate:>10.4f} "
            f"{p.time_to_failure:>10.2f}"
        )


def main():
    basins = degrading_basins()
    systems = all_systems()

    # per-system audit (all four rules on each system's contribution set)
    print("=" * 70)
    print("PER-SYSTEM AUDIT — multiplier under each rule, same inputs")
    print("=" * 70)
    print(f"{'system':25s} {'mult':>10s} {'domin':>10s} {'addit':>10s} {'sat':>10s}")
    for s in systems:
        a = audit_system(s, basins)
        print(
            f"{s.name:25s} {a.multiplicative:>10.2f} {a.dominant:>10.2f} "
            f"{a.additive:>10.2f} {a.saturating_default:>10.2f}"
        )

    # full pipeline under each rule
    print("\n" + "=" * 70)
    print("FULL CASCADE — rate, ttf, cost per rule")
    print("=" * 70)
    print_rule("multiplicative", multiplicative, basins, systems)
    print_rule("dominant", dominant, basins, systems)
    print_rule("additive", additive, basins, systems)
    print_rule("saturating (s_max=10)", saturating(10.0), basins, systems)


if __name__ == "__main__":
    main()
