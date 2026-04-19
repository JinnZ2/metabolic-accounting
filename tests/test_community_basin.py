"""
tests/test_community_basin.py

Pass 1 of the social substrate layer: community vitality basin.

Exercises:
  1. GREEN community basin starts healthy with expected fields
  2. Rural community basin starts pre-depleted matching literature
  3. Fraction remaining and time to cliff work the same as environmental basins
  4. All six community regen functions are registered and callable
  5. Regen costs honor irreversibility for generational_knowledge past cliff
  6. Regen costs honor the social_capital irreversibility threshold (0.5 * cliff)
  7. Regen costs honor the family_formation coupling to economic_security
  8. Regen costs honor the youth_retention self-reinforcing cliff
  9. Community basin integrates with the existing Site class

Run: python -m tests.test_community_basin
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math import isinf

from basin_states import (
    new_community_basin, new_rural_community_basin,
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from accounting.regeneration import (
    DEFAULT_REGISTRY, KNOWN_METRICS,
    regen_economic_security, regen_social_capital,
    regen_family_formation, regen_youth_retention,
    regen_generational_knowledge, regen_civic_engagement,
)
from reserves import Site


def test_1_green_community_basin():
    """GREEN community basin starts healthy with expected fields."""
    print("\n--- TEST 1: green community basin baseline ---")
    basin = new_community_basin()
    expected_metrics = {
        "economic_security", "social_capital", "family_formation",
        "youth_retention", "generational_knowledge", "civic_engagement",
    }
    assert set(basin.state.keys()) == expected_metrics, \
        f"FAIL: metrics mismatch. got {set(basin.state.keys())}"
    assert basin.basin_type == "community", "FAIL: basin_type wrong"
    # all metrics start at 1.0 (full health)
    for k, v in basin.state.items():
        assert v == 1.0, f"FAIL: {k} baseline should be 1.0, got {v}"
    # all cliff thresholds are below baseline
    for k, cliff in basin.cliff_thresholds.items():
        assert 0 < cliff < 1.0, \
            f"FAIL: cliff for {k} out of range: {cliff}"
    print(f"  metrics:          {len(basin.state)}")
    print(f"  cliff thresholds: {basin.cliff_thresholds}")
    print("PASS")


def test_2_rural_community_pre_depletion():
    """Rural community basin starts pre-depleted matching vulnerability
    literature (~2x despair mortality in rural/low-education cohort)."""
    print("\n--- TEST 2: rural community basin pre-depletion ---")
    basin = new_rural_community_basin()
    # every metric should be below green baseline (partially depleted)
    for k, v in basin.state.items():
        assert v < 1.0, f"FAIL: {k} not pre-depleted, got {v}"
        assert v > basin.cliff_thresholds[k], \
            f"FAIL: {k} shouldn't start past cliff, got {v}"
    # youth_retention is most depleted (brain-drain signature)
    assert basin.state["youth_retention"] <= 0.6, \
        "FAIL: rural basin should show strong brain-drain signature"
    print(f"  state:      {basin.state}")
    print(f"  all above cliff, all below green baseline")
    print("PASS")


def test_3_fraction_and_time_to_cliff():
    """Basin methods work the same as environmental basins."""
    print("\n--- TEST 3: fraction_remaining and time_to_cliff ---")
    basin = new_community_basin()
    # set a metric to known state with trajectory
    basin.state["generational_knowledge"] = 0.6
    basin.trajectory["generational_knowledge"] = -0.05
    frac = basin.fraction_remaining("generational_knowledge")
    ttc = basin.time_to_cliff("generational_knowledge")
    # cap 1.2 so 0.6/1.2 = 0.5
    assert abs(frac - 0.5) < 1e-9, f"FAIL: frac expected 0.5, got {frac}"
    # cliff 0.3, state 0.6, rate -0.05 -> (0.6-0.3)/0.05 = 6 periods
    assert abs(ttc - 6.0) < 1e-9, f"FAIL: ttc expected 6.0, got {ttc}"
    print(f"  fraction_remaining: {frac:.4f}")
    print(f"  time_to_cliff:      {ttc:.4f}")
    print("PASS")


def test_4_all_regen_functions_registered():
    """All six community metrics have regen functions registered."""
    print("\n--- TEST 4: community regen functions registered ---")
    expected = {
        ("community", "economic_security"),
        ("community", "social_capital"),
        ("community", "family_formation"),
        ("community", "youth_retention"),
        ("community", "generational_knowledge"),
        ("community", "civic_engagement"),
    }
    for key in expected:
        assert key in DEFAULT_REGISTRY, f"FAIL: {key} not registered"
        assert key in KNOWN_METRICS, f"FAIL: {key} not in KNOWN_METRICS"
    print(f"  registered: {len(expected)} community metrics")
    for pair in sorted(expected):
        fn = DEFAULT_REGISTRY[pair]
        print(f"    {pair[1]:30s} -> {fn.__name__}")
    print("PASS")


def test_5_generational_knowledge_irreversibility():
    """regen_generational_knowledge returns inf when state past cliff."""
    print("\n--- TEST 5: generational_knowledge irreversibility ---")
    basin = new_community_basin()
    # set state at cliff
    basin.state["generational_knowledge"] = 0.25
    cost = regen_generational_knowledge(basin, "generational_knowledge", 0.5)
    assert isinf(cost.total_cost), \
        f"FAIL: past-cliff cost should be inf, got {cost.total_cost}"
    assert cost.irreversible, "FAIL: irreversible flag not set"
    print(f"  state past cliff: {basin.state['generational_knowledge']}")
    print(f"  cliff:            {basin.cliff_thresholds['generational_knowledge']}")
    print(f"  cost:             {cost.total_cost}")
    print(f"  irreversible:     {cost.irreversible}")
    print(f"  notes:            {cost.notes[:80]}...")
    # and above cliff: finite
    basin.state["generational_knowledge"] = 0.8
    cost_ok = regen_generational_knowledge(basin, "generational_knowledge", 0.2)
    assert not isinf(cost_ok.total_cost), \
        "FAIL: above-cliff cost should be finite"
    print(f"  above cliff cost: {cost_ok.total_cost:.2f} (finite)")
    print("PASS")


def test_6_social_capital_deep_cliff_irreversibility():
    """regen_social_capital returns inf when state past 0.5 * cliff."""
    print("\n--- TEST 6: social_capital deep-cliff irreversibility ---")
    basin = new_community_basin()
    cliff = basin.cliff_thresholds["social_capital"]  # 0.4
    # state at 0.5 * cliff = 0.2 should trigger irreversibility
    basin.state["social_capital"] = 0.5 * cliff
    cost = regen_social_capital(basin, "social_capital", 0.5)
    assert isinf(cost.total_cost), \
        f"FAIL: deep-cliff cost should be inf, got {cost.total_cost}"
    print(f"  state:        {basin.state['social_capital']}")
    print(f"  0.5 * cliff:  {0.5 * cliff}")
    print(f"  cost:         {cost.total_cost}")
    # at cliff but not deep: finite
    basin.state["social_capital"] = cliff
    cost2 = regen_social_capital(basin, "social_capital", 0.5)
    assert not isinf(cost2.total_cost), \
        "FAIL: at-cliff-not-deep cost should be finite"
    print(f"  at cliff (not deep) cost: {cost2.total_cost:.2f} (finite)")
    print("PASS")


def test_7_family_formation_economic_coupling():
    """regen_family_formation returns inf when economic_security past cliff."""
    print("\n--- TEST 7: family_formation / economic_security coupling ---")
    basin = new_community_basin()
    # start with family_formation healthy but economic_security past cliff
    basin.state["economic_security"] = (
        basin.cliff_thresholds["economic_security"] * 0.9
    )
    basin.state["family_formation"] = 0.8  # healthy on its own
    cost = regen_family_formation(basin, "family_formation", 0.2)
    assert isinf(cost.total_cost), \
        f"FAIL: should be inf when econ substrate past cliff, got {cost.total_cost}"
    print(f"  economic_security: {basin.state['economic_security']}")
    print(f"  econ cliff:        {basin.cliff_thresholds['economic_security']}")
    print(f"  family_formation:  {basin.state['family_formation']}")
    print(f"  cost:              {cost.total_cost}")
    # restore economic_security: cost becomes finite
    basin.state["economic_security"] = 0.8
    cost2 = regen_family_formation(basin, "family_formation", 0.2)
    assert not isinf(cost2.total_cost), \
        "FAIL: should be finite when econ substrate healthy"
    print(f"  with econ healthy, cost: {cost2.total_cost:.2f} (finite)")
    print("PASS")


def test_8_youth_retention_cliff():
    """regen_youth_retention returns inf when past cliff (brain-drain)."""
    print("\n--- TEST 8: youth_retention brain-drain cliff ---")
    basin = new_community_basin()
    basin.state["youth_retention"] = basin.cliff_thresholds["youth_retention"]
    cost = regen_youth_retention(basin, "youth_retention", 0.5)
    assert isinf(cost.total_cost), \
        f"FAIL: past-cliff youth_retention should be inf, got {cost.total_cost}"
    print(f"  state:  {basin.state['youth_retention']}")
    print(f"  cliff:  {basin.cliff_thresholds['youth_retention']}")
    print(f"  cost:   {cost.total_cost}")
    print(f"  notes:  {cost.notes[:100]}...")
    print("PASS")


def test_9_community_basin_in_site():
    """Community basin can be added to a Site alongside environmental basins."""
    print("\n--- TEST 9: community basin integrates with Site ---")
    site = Site(name="test_site", basins={
        "site_soil": new_soil_basin(),
        "site_air": new_air_basin(),
        "site_water": new_water_basin(),
        "site_biology": new_biology_basin(),
        "site_community": new_community_basin(),
    })
    site.attach_defaults()
    # step with no stress should work
    sr = site.step(stress={}, regenerate=False)
    assert "site_community" in site.basins, "FAIL: community basin not in Site"
    print(f"  site has {len(site.basins)} basins")
    print(f"  community basin registered with type: "
          f"{site.basins['site_community'].basin_type}")
    # step with stress on a community metric
    stress = {("site_community", "economic_security"): 5.0}
    sr2 = site.step(stress, regenerate=False)
    print(f"  stress applied to community.economic_security; step succeeded")
    print("PASS")


if __name__ == "__main__":
    test_1_green_community_basin()
    test_2_rural_community_pre_depletion()
    test_3_fraction_and_time_to_cliff()
    test_4_all_regen_functions_registered()
    test_5_generational_knowledge_irreversibility()
    test_6_social_capital_deep_cliff_irreversibility()
    test_7_family_formation_economic_coupling()
    test_8_youth_retention_cliff()
    test_9_community_basin_in_site()
    print("\nall community basin tests passed.")
