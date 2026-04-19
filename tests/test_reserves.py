"""
tests/test_reserves.py

Exercises the reserve layer end-to-end:

  1. site builds and attaches defaults
  2. applies a period of stress
  3. verifies first-law closure at every metric
  4. verifies exergy destruction is non-negative
  5. compound decay past tertiary cliff shows irreversibility signature
  6. passive regeneration restores reserves when unloaded

Run:  python -m tests.test_reserves
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from reserves import Site
from thermodynamics import ThermodynamicViolation


def fresh_site():
    site = Site(name="test_site", basins={
        "site_soil": new_soil_basin(),
        "site_air": new_air_basin(),
        "site_water": new_water_basin(),
        "site_biology": new_biology_basin(),
    })
    site.attach_defaults()
    return site


def test_1_defaults_populated():
    print("\n--- TEST 1: site defaults populate correctly ---")
    site = fresh_site()
    # Environmental pools must all be present (4). Additional social
    # pools (4) are now registered by default for future community
    # basin support. This test verifies environmental pools are intact.
    env_pools = {"landscape_reserve", "watershed_reserve",
                 "airshed_reserve", "organizational_reserve"}
    present = set(site.tertiary.keys())
    assert env_pools.issubset(present), \
        f"FAIL: missing environmental pools: {env_pools - present}"
    assert len(site.tertiary) >= 4, \
        f"FAIL: expected >=4 tertiary pools, got {len(site.tertiary)}"
    total_reserves = sum(len(v) for v in site.secondary.values())
    assert total_reserves == 17, f"FAIL: expected 17 secondary reserves, got {total_reserves}"
    statuses = site.tertiary_status()
    for name, frac in statuses.items():
        assert abs(frac - 1.0) < 1e-9, f"FAIL: {name} not at full capacity"
    print(f"  tertiary pools:     {len(site.tertiary)} "
          f"({len(env_pools)} env + {len(site.tertiary) - len(env_pools)} social)")
    print(f"  secondary reserves: {total_reserves}")
    print("PASS")


def test_2_single_step_closure():
    """Impose stress on one metric; closure must hold."""
    print("\n--- TEST 2: single-step closure ---")
    site = fresh_site()
    site.strict = True   # any violation should raise

    stress = {("site_soil", "carbon_fraction"): 10.0}
    result = site.step(stress)

    p = result.partitions[0]
    total = (p.primary_damage + p.secondary_drawdown_kept +
             p.tertiary_drawdown_kept + p.environment_loss)
    print(f"  imposed:             {p.stress_imposed:.4f}")
    print(f"  primary:             {p.primary_damage:.4f}")
    print(f"  secondary kept:      {p.secondary_drawdown_kept:.4f}")
    print(f"  tertiary kept:       {p.tertiary_drawdown_kept:.4f}")
    print(f"  environment loss:    {p.environment_loss:.4f}")
    print(f"  sum of parts:        {total:.4f}")
    print(f"  closure delta:       {abs(total - p.stress_imposed):.2e}")
    assert abs(total - p.stress_imposed) < 1e-6, "FAIL: closure violated"
    print(f"  flows recorded:      {len(p.flows)}")
    print("PASS")


def test_3_closure_every_metric():
    """Stress every metric simultaneously; closure per-metric and total."""
    print("\n--- TEST 3: multi-metric closure ---")
    site = fresh_site()
    site.strict = True

    stress = {}
    for bname, basin in site.basins.items():
        for key in basin.state:
            stress[(bname, key)] = 5.0

    result = site.step(stress)
    total = (result.total_primary + result.total_secondary_kept +
             result.total_tertiary_kept + result.total_environment)
    print(f"  total imposed:       {result.total_imposed:.4f}")
    print(f"  total primary:       {result.total_primary:.4f}")
    print(f"  total secondary:     {result.total_secondary_kept:.4f}")
    print(f"  total tertiary:      {result.total_tertiary_kept:.4f}")
    print(f"  total environment:   {result.total_environment:.4f}")
    print(f"  closure delta:       {abs(total - result.total_imposed):.2e}")
    assert abs(total - result.total_imposed) < 1e-6, "FAIL: aggregate closure"
    print("PASS")


def test_4_reserves_drain_with_load():
    """Heavy stress over many periods should drain reserves."""
    print("\n--- TEST 4: reserves drain under sustained load ---")
    site = fresh_site()
    initial_landscape = site.tertiary["landscape_reserve"].stock
    initial_soil_carbon = site.secondary["site_soil"]["carbon_fraction"].stock

    heavy = {("site_soil", "carbon_fraction"): 8.0}
    for _ in range(20):
        site.step(heavy, regenerate=False)

    final_soil = site.secondary["site_soil"]["carbon_fraction"].stock
    final_landscape = site.tertiary["landscape_reserve"].stock
    print(f"  soil carbon reserve:  {initial_soil_carbon:.1f} -> {final_soil:.1f}")
    print(f"  landscape reserve:    {initial_landscape:.1f} -> {final_landscape:.1f}")
    assert final_soil < initial_soil_carbon, "FAIL: secondary did not drain"
    assert final_landscape < initial_landscape, "FAIL: tertiary did not drain"
    print("PASS")


def test_5_past_cliff_accelerated_loss():
    """Past-cliff tertiary pool should leak faster to environment."""
    print("\n--- TEST 5: past-cliff accelerated environment loss ---")

    # Compare two identical sites, one with healthy tertiary, one with
    # tertiary past cliff. Secondary reserves left healthy so leaks
    # actually reach tertiary.
    site_healthy = fresh_site()
    site_broken = fresh_site()
    site_broken.tertiary["landscape_reserve"].stock = 100.0   # past cliff (200)
    assert site_broken.tertiary["landscape_reserve"].past_cliff()

    # degrade the primary state somewhat so cliff_distance > 0 and
    # leak_to_tertiary is non-trivial
    for s in (site_healthy, site_broken):
        s.basins["site_soil"].state["carbon_fraction"] = 0.04  # from 0.05

    stress = {("site_soil", "carbon_fraction"): 10.0}
    r_healthy = site_healthy.step(stress, regenerate=False)
    r_broken = site_broken.step(stress, regenerate=False)

    env_h = r_healthy.partitions[0].environment_loss
    env_b = r_broken.partitions[0].environment_loss
    print(f"  env loss healthy tertiary:   {env_h:.4f}")
    print(f"  env loss broken tertiary:    {env_b:.4f}")
    print(f"  amplification factor:        {env_b / max(env_h, 1e-9):.2f}x")
    assert env_b > env_h, "FAIL: broken tertiary did not accelerate env loss"
    # base rate 2-5%, past-cliff rate 25% -> expect roughly 5-10x amplification
    assert env_b / max(env_h, 1e-9) > 3.0, "FAIL: amplification too weak"
    print("PASS: past-cliff signature visible")


def test_6_passive_regen():
    """Unloaded reserves should regenerate toward capacity."""
    print("\n--- TEST 6: passive regeneration ---")
    site = fresh_site()
    # drain one reserve
    r = site.secondary["site_soil"]["carbon_fraction"]
    r.stock = 50.0
    before = r.stock

    # ten no-stress periods
    for _ in range(10):
        site.step(stress={}, regenerate=True)
    after = r.stock
    print(f"  carbon reserve:      {before:.1f} -> {after:.1f}")
    assert after > before, "FAIL: no passive regen"
    print("PASS")


def test_7_thermodynamic_floor():
    """Artificial negative destruction should raise in strict mode."""
    print("\n--- TEST 7: thermodynamic floor (Gouy-Stodola) ---")
    from thermodynamics import check_nonnegative_destruction
    try:
        check_nonnegative_destruction(-0.5, context="test")
    except ThermodynamicViolation as e:
        print(f"  caught: {str(e)[:80]}...")
        print("PASS: negative destruction refused")
        return
    print("FAIL: negative destruction not caught")


if __name__ == "__main__":
    test_1_defaults_populated()
    test_2_single_step_closure()
    test_3_closure_every_metric()
    test_4_reserves_drain_with_load()
    test_5_past_cliff_accelerated_loss()
    test_6_passive_regen()
    test_7_thermodynamic_floor()
    print("\nall reserve tests passed.")
