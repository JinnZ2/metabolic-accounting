"""
tests/test_integration.py

Wires Site -> step(stress) -> compute_flow(site, step_result) -> assess().

Verifies:
  1. reserve_drawdown_cost appears on the PnL
  2. metabolic profit is lower than reported profit by the expected margin
  3. verdict warnings surface reserve exhaustion and tertiary past cliff
  4. tertiary past cliff triggers BLACK even without primary irreversibility

Run:  python -m tests.test_integration
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
from reserves import Site
from accounting import compute_flow
from verdict import assess


def fresh_site():
    site = Site(name="integration_site", basins={
        "site_soil": new_soil_basin(),
        "site_air": new_air_basin(),
        "site_water": new_water_basin(),
        "site_biology": new_biology_basin(),
    })
    site.attach_defaults()
    return site


def systems():
    return [
        new_foundation_system(),
        new_buried_utility_system(),
        new_hvac_system(),
        new_thermal_envelope_system(),
        new_cooling_system(),
        new_biological_service_system(),
    ]


def test_1_drawdown_on_pnl():
    """Stress a site; drawdown should appear on the PnL and reduce
    metabolic profit."""
    print("\n--- TEST 1: reserve drawdown on PnL ---")
    site = fresh_site()
    # moderate stress on each basin
    stress = {
        ("site_soil", "carbon_fraction"): 6.0,
        ("site_air", "particulate_load"): 4.0,
        ("site_water", "aquifer_level"): 3.0,
        ("site_biology", "pollinator_index"): 4.0,
    }
    step_result = site.step(stress, regenerate=False)

    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=step_result,
    )
    print(f"  reserve_drawdown_cost: {flow.reserve_drawdown_cost:.4f}")
    print(f"  environment_loss:      {flow.environment_loss:.4f}")
    print(f"  reported_profit:       {flow.reported_profit():.2f}")
    print(f"  metabolic_profit:      {flow.metabolic_profit():.2f}")
    gap = flow.reported_profit() - flow.metabolic_profit()
    print(f"  visible hidden cost:   {gap:.2f}")
    assert flow.reserve_drawdown_cost > 0, "FAIL: drawdown not surfaced"
    assert flow.environment_loss > 0, "FAIL: env loss not surfaced"
    assert flow.metabolic_profit() < flow.reported_profit(), \
        "FAIL: metabolic profit not reduced"
    print("PASS")


def test_2_backward_compat_no_site():
    """compute_flow without site still works exactly as before."""
    print("\n--- TEST 2: backward compatibility (no site) ---")
    site = fresh_site()  # just for basins
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
    )
    assert flow.reserve_drawdown_cost == 0.0, "FAIL: drawdown leaked"
    assert flow.environment_loss == 0.0, "FAIL: env loss leaked"
    assert not flow.exhausted_reserves, "FAIL: ghost exhausted reserves"
    assert not flow.tertiary_past_cliff, "FAIL: ghost tertiary past cliff"
    print(f"  reserve_drawdown_cost: {flow.reserve_drawdown_cost}")
    print(f"  metabolic_profit:      {flow.metabolic_profit():.2f}")
    print("PASS")


def test_3_tertiary_past_cliff_triggers_black():
    """Tertiary past cliff -> BLACK even with no primary irreversibility."""
    print("\n--- TEST 3: tertiary past cliff triggers BLACK ---")
    site = fresh_site()
    # manually crash landscape reserve past cliff
    site.tertiary["landscape_reserve"].stock = 100.0  # cliff is 200

    # do a tiny step so compute_flow sees the site state
    stress = {("site_soil", "carbon_fraction"): 0.1}
    step_result = site.step(stress, regenerate=False)

    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=step_result,
    )
    v = assess(site.basins, flow)
    print(f"  signal:            {v.sustainable_yield_signal}")
    print(f"  tertiary past:     {flow.tertiary_past_cliff}")
    assert v.sustainable_yield_signal == "BLACK", \
        f"FAIL: expected BLACK, got {v.sustainable_yield_signal}"
    assert "landscape_reserve" in flow.tertiary_past_cliff
    assert any("TERTIARY PAST CLIFF" in w for w in v.warnings), \
        "FAIL: no tertiary warning"
    print("PASS")


def test_4_exhausted_secondary_surfaces():
    """Exhausted secondary should show up as a warning."""
    print("\n--- TEST 4: exhausted secondary reserve warning ---")
    site = fresh_site()
    # push one secondary reserve past cliff
    site.secondary["site_soil"]["carbon_fraction"].stock = 15.0  # cliff 20
    step_result = site.step(stress={}, regenerate=False)

    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=step_result,
    )
    v = assess(site.basins, flow)
    print(f"  exhausted:  {flow.exhausted_reserves}")
    assert ("site_soil", "carbon_fraction") in flow.exhausted_reserves
    assert any("EXHAUSTED" in w for w in v.warnings), "FAIL: no exhausted warning"
    print("PASS")


def test_5_compound_decay_over_periods():
    """Sustained stress over 30 periods should drain reserves and raise drawdown."""
    print("\n--- TEST 5: compound decay over 30 periods ---")
    site = fresh_site()
    stress = {
        ("site_soil", "carbon_fraction"): 5.0,
        ("site_water", "aquifer_level"): 4.0,
    }

    cumulative_drawdown = 0.0
    cumulative_env_loss = 0.0
    for period in range(30):
        sr = site.step(stress, regenerate=True)
        cumulative_drawdown += sr.total_secondary_kept + sr.total_tertiary_kept
        cumulative_env_loss += sr.total_environment

    print(f"  cumulative drawdown:   {cumulative_drawdown:.2f} xdu")
    print(f"  cumulative env loss:   {cumulative_env_loss:.2f} xdu")
    print(f"  final landscape stock: "
          f"{site.tertiary['landscape_reserve'].stock:.1f}")
    print(f"  final watershed stock: "
          f"{site.tertiary['watershed_reserve'].stock:.1f}")
    exhausted = site.exhausted_reserves()
    print(f"  exhausted reserves:    {len(exhausted)}")

    assert cumulative_env_loss > 0, "FAIL: no env loss over 30 periods"
    print("PASS")


if __name__ == "__main__":
    test_1_drawdown_on_pnl()
    test_2_backward_compat_no_site()
    test_3_tertiary_past_cliff_triggers_black()
    test_4_exhausted_secondary_surfaces()
    test_5_compound_decay_over_periods()
    print("\nall integration tests passed.")
