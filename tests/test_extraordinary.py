"""
tests/test_extraordinary.py

Tests the SEEA/GAAP-aligned extraordinary-item treatment of
irreversible environment loss, and cumulative loss tracking.

Run: python -m tests.test_extraordinary
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math import isinf

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from infrastructure import (
    new_foundation_system, new_hvac_system, new_cooling_system,
    new_biological_service_system,
)
from reserves import Site
from accounting import compute_flow
from verdict import assess


def fresh_site():
    site = Site(name="x_site", basins={
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
        new_hvac_system(),
        new_cooling_system(),
        new_biological_service_system(),
    ]


def test_1_two_profit_lines():
    """metabolic_profit and metabolic_profit_with_loss differ by env loss."""
    print("\n--- TEST 1: two profit lines exist and differ correctly ---")
    site = fresh_site()
    # force tertiary past cliff so env loss is material
    site.tertiary["landscape_reserve"].stock = 100.0
    stress = {("site_soil", "carbon_fraction"): 20.0}
    sr = site.step(stress, regenerate=False)

    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    mp = flow.metabolic_profit()
    mp_full = flow.metabolic_profit_with_loss()
    delta = mp - mp_full
    print(f"  environment_loss:              {flow.environment_loss:.4f}")
    print(f"  metabolic_profit (ops only):   {mp:.4f}")
    print(f"  metabolic_profit_with_loss:    {mp_full:.4f}")
    print(f"  delta (should equal env_loss): {delta:.4f}")
    assert abs(delta - flow.environment_loss) < 1e-9, \
        "FAIL: delta does not match env loss"
    print("PASS")


def test_2_materiality_flag_below_threshold():
    """Small env loss relative to revenue: not flagged."""
    print("\n--- TEST 2: small env loss not flagged (below 5% threshold) ---")
    site = fresh_site()
    # degrade a basin slightly but keep tertiary healthy -> tiny env loss
    site.basins["site_soil"].state["carbon_fraction"] = 0.045
    stress = {("site_soil", "carbon_fraction"): 3.0}
    sr = site.step(stress, regenerate=False)
    flow = compute_flow(
        revenue=10_000.0, direct_operating_cost=6_000.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    v = assess(site.basins, flow)
    ratio = flow.environment_loss / flow.revenue if flow.revenue > 0 else 0
    print(f"  environment_loss:     {flow.environment_loss:.4f}")
    print(f"  revenue:              {flow.revenue:.2f}")
    print(f"  env/revenue ratio:    {ratio:.6f}")
    print(f"  extraordinary flag:   {v.extraordinary_item_flagged}")
    assert not v.extraordinary_item_flagged, "FAIL: flagged below threshold"
    print("PASS")


def test_3_materiality_flag_above_threshold():
    """Large env loss relative to revenue: flagged.

    Scenario: multiple tertiary pools past cliff, multiple secondary
    reserves exhausted so stress cannot be buffered, high stress rate
    over many periods — this is what a truly failing site looks like.
    """
    print("\n--- TEST 3: severe damage scenario IS flagged ---")
    site = fresh_site()
    # crash all tertiary pools past cliff
    for pool in site.tertiary.values():
        pool.stock = pool.cliff * 0.5
    # exhaust all secondary reserves
    for reserves in site.secondary.values():
        for r in reserves.values():
            r.stock = r.cliff * 0.5
    # primary metrics also degraded
    site.basins["site_soil"].state["carbon_fraction"] = 0.02
    site.basins["site_water"].state["aquifer_level"] = 0.4

    stress = {
        ("site_soil", "carbon_fraction"): 100.0,
        ("site_soil", "bearing_capacity"): 50.0,
        ("site_water", "aquifer_level"): 80.0,
        ("site_biology", "pollinator_index"): 50.0,
    }
    sr = site.step(stress, regenerate=False)

    # very low revenue — a firm with small revenue seeing big damage
    flow = compute_flow(
        revenue=50.0, direct_operating_cost=30.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    v = assess(site.basins, flow)
    ratio = flow.environment_loss / flow.revenue if flow.revenue > 0 else 0
    print(f"  environment_loss:     {flow.environment_loss:.4f}")
    print(f"  revenue:              {flow.revenue:.2f}")
    print(f"  env/revenue ratio:    {ratio:.4f}")
    print(f"  extraordinary flag:   {v.extraordinary_item_flagged}")
    assert v.extraordinary_item_flagged, "FAIL: severe scenario should flag"
    assert any("EXTRAORDINARY ITEM" in w for w in v.warnings), \
        "FAIL: no EXTRAORDINARY ITEM warning"
    print("PASS")


def test_4_cumulative_tracked():
    """Site accumulates env loss across periods."""
    print("\n--- TEST 4: cumulative env loss across periods ---")
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0  # past cliff
    stress = {("site_soil", "carbon_fraction"): 8.0}

    per_period = []
    for i in range(5):
        sr = site.step(stress, regenerate=True)
        per_period.append(sr.total_environment)

    expected_cumulative = sum(per_period)
    print(f"  periods elapsed:          {site.periods_elapsed}")
    print(f"  per-period env losses:    "
          f"{[f'{x:.4f}' for x in per_period]}")
    print(f"  sum of per-period:        {expected_cumulative:.4f}")
    print(f"  site cumulative:          {site.cumulative_environment_loss:.4f}")
    assert abs(site.cumulative_environment_loss - expected_cumulative) < 1e-9, \
        "FAIL: cumulative does not equal sum"
    print("PASS")


def test_5_cumulative_visible_in_verdict():
    """Cumulative shows up as a warning."""
    print("\n--- TEST 5: cumulative surfaces in verdict warnings ---")
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0
    stress = {("site_soil", "carbon_fraction"): 5.0}
    for _ in range(10):
        sr = site.step(stress, regenerate=True)

    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    v = assess(site.basins, flow)
    print(f"  cumulative in flow:   {flow.cumulative_environment_loss:.4f}")
    has_warn = any("cumulative environment loss" in w for w in v.warnings)
    print(f"  cumulative warning:   {has_warn}")
    assert has_warn, "FAIL: no cumulative warning"
    print("PASS")


def test_6_configurable_thresholds():
    """Custom thresholds on assess() change the flag decision."""
    print("\n--- TEST 6: configurable materiality thresholds ---")
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0
    stress = {("site_soil", "carbon_fraction"): 20.0}
    sr = site.step(stress, regenerate=False)
    flow = compute_flow(
        revenue=1000.0, direct_operating_cost=600.0,
        regeneration_paid=0.0,
        basins=site.basins, systems=systems(),
        site=site, step_result=sr,
    )
    env = flow.environment_loss
    rev = flow.revenue
    ratio = env / rev
    # strict threshold below actual ratio -> should flag
    strict_t = ratio * 0.5
    # loose threshold above actual ratio -> should NOT flag
    loose_t = ratio * 2.0
    v_strict = assess(site.basins, flow,
                      extraordinary_revenue_threshold=strict_t)
    v_loose = assess(site.basins, flow,
                     extraordinary_revenue_threshold=loose_t)
    print(f"  env loss:             {env:.4f}")
    print(f"  revenue:              {rev:.2f}")
    print(f"  actual ratio:         {ratio:.6f}")
    print(f"  strict threshold:     {strict_t:.6f}")
    print(f"  loose threshold:      {loose_t:.6f}")
    print(f"  strict flag:          {v_strict.extraordinary_item_flagged}")
    print(f"  loose flag:           {v_loose.extraordinary_item_flagged}")
    assert v_strict.extraordinary_item_flagged, "FAIL: strict should flag"
    assert not v_loose.extraordinary_item_flagged, "FAIL: loose should not"
    print("PASS")


if __name__ == "__main__":
    test_1_two_profit_lines()
    test_2_materiality_flag_below_threshold()
    test_3_materiality_flag_above_threshold()
    test_4_cumulative_tracked()
    test_5_cumulative_visible_in_verdict()
    test_6_configurable_thresholds()
    print("\nall extraordinary-item tests passed.")
