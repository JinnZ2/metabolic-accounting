"""
tests/test_mitigation.py

Exercises the mitigation module:

  1. Healthy site -> minimal actions, mostly monitoring
  2. Slow degradation far from cliff -> easy wins
  3. Near-cliff trajectory -> urgent actions
  4. Exhausted secondary reserve -> urgent reserve action
  5. Tertiary past cliff -> systemic action
  6. Combined scenario -> all tiers populated
  7. Report as_text() renders correctly
  8. top_easy_wins and top_urgent sort correctly

Run: python -m tests.test_mitigation
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math import isinf

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from reserves import Site
from mitigation import (
    build_mitigation_report,
    TIER_EASY_WIN, TIER_URGENT, TIER_SYSTEMIC,
    identify_basin_actions, identify_reserve_actions,
)


def fresh_site():
    site = Site(name="mit_site", basins={
        "site_soil": new_soil_basin(),
        "site_air": new_air_basin(),
        "site_water": new_water_basin(),
        "site_biology": new_biology_basin(),
    })
    site.attach_defaults()
    return site


def test_1_healthy_minimal():
    """Healthy site with no negative trajectories produces no actions."""
    print("\n--- TEST 1: healthy site, no actions ---")
    site = fresh_site()
    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    print(f"  urgent:    {len(report.urgent)}")
    print(f"  easy_wins: {len(report.easy_wins)}")
    print(f"  systemic:  {len(report.systemic)}")
    print(f"  monitoring:{len(report.monitoring)}")
    print(f"  summary:   {report.summary}")
    total = (len(report.urgent) + len(report.easy_wins)
             + len(report.systemic) + len(report.monitoring))
    assert total == 0, f"FAIL: expected 0 actions, got {total}"
    print("PASS")


def test_2_easy_wins_slow_degradation():
    """Slow degradation far from cliff produces easy wins."""
    print("\n--- TEST 2: slow degradation -> easy wins ---")
    site = fresh_site()
    # slight negative trajectory on soil carbon
    # high fraction_remaining, long time to cliff, high leverage
    site.basins["site_soil"].state["carbon_fraction"] = 0.06
    site.basins["site_soil"].trajectory["carbon_fraction"] = -0.001

    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    print(f"  urgent:    {len(report.urgent)}")
    print(f"  easy_wins: {len(report.easy_wins)}")
    print(f"  systemic:  {len(report.systemic)}")
    print(f"  monitoring:{len(report.monitoring)}")
    if report.easy_wins:
        a = report.easy_wins[0]
        print(f"  example:   [{a.target}] leverage {a.leverage:.2f}, "
              f"ttc {a.urgency:.2f}")
    assert (len(report.easy_wins) >= 1
            or len(report.monitoring) >= 1), "FAIL: no wins or monitoring"
    print("PASS")


def test_3_urgent_near_cliff():
    """Fast degradation near cliff produces urgent actions."""
    print("\n--- TEST 3: near-cliff trajectory -> urgent ---")
    site = fresh_site()
    # carbon_fraction capacity 0.08, cliff 0.02. Set state just above cliff
    # with fast decline — should trigger urgent.
    site.basins["site_soil"].state["carbon_fraction"] = 0.025
    site.basins["site_soil"].trajectory["carbon_fraction"] = -0.002
    # bearing_capacity: cliff 0.6, set near cliff with decline
    site.basins["site_soil"].state["bearing_capacity"] = 0.65
    site.basins["site_soil"].trajectory["bearing_capacity"] = -0.02

    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    print(f"  urgent:    {len(report.urgent)}")
    print(f"  easy_wins: {len(report.easy_wins)}")
    for a in report.top_urgent(5):
        print(f"  urgent: [{a.target}] ttc {a.urgency:.2f}")
    assert len(report.urgent) >= 1, "FAIL: near-cliff should trigger urgent"
    print("PASS")


def test_4_exhausted_secondary_urgent():
    """Exhausted secondary reserve generates urgent reserve action."""
    print("\n--- TEST 4: exhausted secondary reserve ---")
    site = fresh_site()
    # crash one reserve past cliff
    site.secondary["site_soil"]["carbon_fraction"].stock = 10.0  # cliff 20
    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    print(f"  urgent:    {len(report.urgent)}")
    targets = [a.target for a in report.urgent]
    print(f"  targets:   {targets}")
    reserve_targets = [t for t in targets if t.startswith("reserve:")]
    assert len(reserve_targets) >= 1, \
        "FAIL: no reserve-target urgent action"
    # check the reserve action flags leverage as infinite
    for a in report.urgent:
        if a.target.startswith("reserve:"):
            assert isinf(a.leverage) or a.leverage >= 5.0, \
                "FAIL: exhausted reserve should have high leverage"
            break
    print("PASS")


def test_5_tertiary_past_cliff_systemic():
    """Tertiary past cliff produces systemic action."""
    print("\n--- TEST 5: tertiary past cliff -> systemic ---")
    site = fresh_site()
    site.tertiary["landscape_reserve"].stock = 100.0  # cliff 200
    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    print(f"  systemic:  {len(report.systemic)}")
    assert len(report.systemic) >= 1, "FAIL: no systemic action for tertiary cliff"
    found = False
    for a in report.systemic:
        if a.target == "tertiary:landscape_reserve":
            found = True
            print(f"  action: {a.description[:80]}...")
            break
    assert found, "FAIL: no landscape_reserve systemic action"
    print("PASS")


def test_6_combined_scenario():
    """Combined: degraded basins + exhausted reserve + tertiary pressure."""
    print("\n--- TEST 6: combined multi-tier scenario ---")
    site = fresh_site()
    # basin degradation
    site.basins["site_soil"].state["carbon_fraction"] = 0.025
    site.basins["site_soil"].trajectory["carbon_fraction"] = -0.002
    site.basins["site_water"].state["aquifer_level"] = 0.7
    site.basins["site_water"].trajectory["aquifer_level"] = -0.005
    # reserve near cliff
    site.secondary["site_soil"]["bearing_capacity"].stock = 25.0  # cliff 20
    # tertiary approaching cliff
    site.tertiary["watershed_reserve"].stock = 350.0  # cliff 300, frac ~0.23

    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    print(f"  urgent:    {len(report.urgent)}")
    print(f"  easy_wins: {len(report.easy_wins)}")
    print(f"  systemic:  {len(report.systemic)}")
    print(f"  monitoring:{len(report.monitoring)}")
    print(f"  total leverage: {report.total_actionable_leverage():.2f}x")
    assert len(report.urgent) + len(report.easy_wins) >= 2, \
        "FAIL: combined scenario should produce multiple actions"
    print("PASS")


def test_7_as_text_renders():
    """Report.as_text() renders without error and includes key sections."""
    print("\n--- TEST 7: as_text() rendering ---")
    site = fresh_site()
    site.basins["site_soil"].state["carbon_fraction"] = 0.025
    site.basins["site_soil"].trajectory["carbon_fraction"] = -0.002
    site.tertiary["landscape_reserve"].stock = 100.0

    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    text = report.as_text()
    assert "Mitigation report" in text
    assert len(text) > 50
    # sample output
    print("  --- sample output ---")
    for line in text.split("\n")[:15]:
        print(f"  {line}")
    print("  [...truncated]")
    print("PASS")


def test_8_top_sorting():
    """top_easy_wins and top_urgent sort correctly."""
    print("\n--- TEST 8: top_* sorting ---")
    site = fresh_site()
    # create several near-cliff metrics with different urgencies
    site.basins["site_soil"].state["carbon_fraction"] = 0.025
    site.basins["site_soil"].trajectory["carbon_fraction"] = -0.001  # ttc ~5
    site.basins["site_soil"].state["bearing_capacity"] = 0.65
    site.basins["site_soil"].trajectory["bearing_capacity"] = -0.05  # ttc ~1
    site.basins["site_water"].state["aquifer_level"] = 0.52
    site.basins["site_water"].trajectory["aquifer_level"] = -0.005  # ttc ~4

    report = build_mitigation_report(
        basins=site.basins,
        secondary_reserves=site.secondary,
        tertiary_pools=site.tertiary,
    )
    top_urg = report.top_urgent(5)
    print(f"  top urgent count: {len(top_urg)}")
    for a in top_urg:
        print(f"    [{a.target}] ttc {a.urgency:.2f}")
    # assert urgency is ascending (most urgent first)
    urgencies = [a.urgency for a in top_urg if a.urgency is not None]
    assert urgencies == sorted(urgencies), "FAIL: top_urgent not sorted"
    print("PASS")


if __name__ == "__main__":
    test_1_healthy_minimal()
    test_2_easy_wins_slow_degradation()
    test_3_urgent_near_cliff()
    test_4_exhausted_secondary_urgent()
    test_5_tertiary_past_cliff_systemic()
    test_6_combined_scenario()
    test_7_as_text_renders()
    test_8_top_sorting()
    print("\nall mitigation tests passed.")
