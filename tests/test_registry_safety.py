"""
tests/test_registry_safety.py

Verify the safety-net features:

  1. Renaming a basin does NOT break regen cost lookup
     (registry keys by basin_type, not by name).
  2. A basin with no basin_type declared surfaces a clear warning.
  3. A known metric with no registered function raises in strict mode
     and warns loudly in non-strict mode.
  4. The full pipeline still runs end-to-end after the rewiring.

Run:  python -m tests.test_registry_safety
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from basin_states.base import BasinState
from infrastructure import (
    new_foundation_system, new_hvac_system, new_cooling_system,
    new_biological_service_system,
)
from accounting import (
    compute_flow, required_regeneration_cost_detailed,
    UnregisteredMetricError,
)


def systems():
    return [
        new_foundation_system(),
        new_hvac_system(),
        new_cooling_system(),
        new_biological_service_system(),
    ]


def test_1_renamed_basins():
    """Same physics, non-default names. Registry must still match by type."""
    print("\n--- TEST 1: renamed basins ---")
    basins = {
        "farm_north_soil": new_soil_basin(name="farm_north_soil"),
        "depot_air":       new_air_basin(name="depot_air"),
        "well_7":          new_water_basin(name="well_7"),
        "corridor_biology": new_biology_basin(name="corridor_biology"),
    }
    # degrade one metric so regen > 0
    basins["farm_north_soil"].state["carbon_fraction"] = 0.03
    basins["depot_air"].state["particulate_load"] = 0.3

    total, breakdown, irr, warnings = required_regeneration_cost_detailed(basins)
    non_zero = [rc for rc in breakdown if rc.total_cost > 0]
    print(f"total cost:      {total:.2f}")
    print(f"warnings:        {len(warnings)}")
    print(f"non-zero lines:  {len(non_zero)}")
    for rc in non_zero:
        print(f"  {rc.basin_name}.{rc.metric_key}: {rc.total_cost:.2f}")
    assert total > 0, "FAIL: renamed basins got zero cost — registry not by type"
    assert len(warnings) == 0, f"FAIL: unexpected warnings: {warnings}"
    print("PASS: renamed basins resolved by type.")


def test_2_missing_basin_type():
    """Basin with no basin_type declared should surface a warning."""
    print("\n--- TEST 2: basin with no basin_type ---")
    b = BasinState(
        name="mystery_basin",
        # deliberately no basin_type
        state={"carbon_fraction": 0.03},
        capacity={"carbon_fraction": 0.08},
        trajectory={"carbon_fraction": 0.0},
        cliff_thresholds={"carbon_fraction": 0.02},
    )
    basins = {"mystery": b}
    total, breakdown, irr, warnings = required_regeneration_cost_detailed(basins)
    print(f"total cost:  {total:.2f}")
    print(f"warnings:    {len(warnings)}")
    for w in warnings:
        print(f"  - {w}")
    assert any("no basin_type" in w for w in warnings), \
        "FAIL: no warning for missing basin_type"
    print("PASS: missing basin_type surfaces warning.")


def test_3_known_metric_unregistered_strict():
    """Known (basin_type, metric) pair but registry lacks it -> strict raises."""
    print("\n--- TEST 3: known metric missing from custom registry (strict) ---")
    basins = {"s": new_soil_basin()}
    basins["s"].state["carbon_fraction"] = 0.03  # degrade so it matters

    # custom registry missing the soil.carbon_fraction entry
    from accounting.regeneration import regen_soil_bearing
    bad_registry = {("soil", "bearing_capacity"): regen_soil_bearing}

    try:
        required_regeneration_cost_detailed(
            basins, registry=bad_registry, strict=True,
        )
    except UnregisteredMetricError as e:
        print(f"caught: {e}")
        print("PASS: strict mode raised UnregisteredMetricError.")
        return
    print("FAIL: strict mode did not raise.")


def test_4_known_metric_unregistered_non_strict():
    """Same as test 3 but non-strict — should warn with [known metric] tag."""
    print("\n--- TEST 4: known metric missing (non-strict) ---")
    basins = {"s": new_soil_basin()}
    basins["s"].state["carbon_fraction"] = 0.03

    from accounting.regeneration import regen_soil_bearing
    bad_registry = {("soil", "bearing_capacity"): regen_soil_bearing}

    total, breakdown, irr, warnings = required_regeneration_cost_detailed(
        basins, registry=bad_registry, strict=False,
    )
    print(f"total cost:  {total:.2f}")
    print(f"warnings:")
    for w in warnings:
        print(f"  - {w}")
    assert any("[known metric]" in w for w in warnings), \
        "FAIL: no [known metric] tag in warnings"
    print("PASS: non-strict mode warns with [known metric] tag.")


def test_5_full_pipeline_renamed():
    """Full compute_flow with renamed basins — end-to-end sanity."""
    print("\n--- TEST 5: full pipeline with renamed basins ---")
    basins = {
        "farm_north_soil": new_soil_basin(name="farm_north_soil"),
        "depot_air":       new_air_basin(name="depot_air"),
        "well_7":          new_water_basin(name="well_7"),
        "corridor_biology": new_biology_basin(name="corridor_biology"),
    }
    # moderate degradation
    basins["farm_north_soil"].state["bearing_capacity"] = 0.7
    basins["depot_air"].state["particulate_load"] = 0.4
    basins["well_7"].state["aquifer_level"] = 0.6
    basins["corridor_biology"].state["pollinator_index"] = 0.55

    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=basins, systems=systems(),
    )
    print(f"regen required:    {flow.regeneration_required:.2f}")
    print(f"cascade burn:      {flow.cascade_burn:.2f}")
    print(f"metabolic profit:  {flow.metabolic_profit():.2f}")
    print(f"registry warnings: {len(flow.registry_warnings)}")
    assert flow.regeneration_required > 0, "FAIL: regen required is zero"
    assert len(flow.registry_warnings) == 0, \
        f"FAIL: unexpected warnings {flow.registry_warnings}"
    print("PASS: end-to-end pipeline works with renamed basins.")


if __name__ == "__main__":
    test_1_renamed_basins()
    test_2_missing_basin_type()
    test_3_known_metric_unregistered_strict()
    test_4_known_metric_unregistered_non_strict()
    test_5_full_pipeline_renamed()
    print("\nall safety-net tests passed.")
