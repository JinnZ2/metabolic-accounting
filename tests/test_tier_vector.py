"""
tests/test_tier_vector.py

Locks in Bug 1 and Bug 4 fixes (see STATUS.md).

Bug 1: tier determination was broken for cliff-threshold basins because
the check `fraction_remaining < 0` never fired (state/capacity is
non-negative for any reasonable state). Community basin with
civic_engagement=0.20 and cliff=0.35 should register BLACK but did not.

Bug 4: tier vector was collapsed to a scalar in apply_tier_to_cohorts,
so a firm GREEN on soil and BLACK on community imposed the same
structural load on every cohort. The vector path preserves per-basin-type
tiers and weights them through cohort_basin_sensitivities.

Run: python -m tests.test_tier_vector
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_soil_basin, new_community_basin,
)
from distributional.tiers import (
    Tier, determine_tier_for_basin, determine_tiers,
    DEFAULT_TERTIARY_MAPPING,
    _metric_past_cliff, _metric_near_cliff,
)
from distributional.access import (
    PopulationCohort, apply_tier_to_cohorts,
)
from reserves.defaults import new_standard_tertiary_pools


def test_1_past_cliff_detection():
    """_metric_past_cliff fires for community.civic_engagement=0.20
    when cliff is 0.35 (the scenario that fell through Bug 1)."""
    print("\n--- TEST 1: _metric_past_cliff honors cliff semantics ---")
    basin = new_community_basin()
    basin.state["civic_engagement"] = 0.20   # below cliff 0.35
    assert _metric_past_cliff(basin, "civic_engagement"), \
        "FAIL: civic_engagement=0.20 with cliff=0.35 should be past cliff"

    basin.state["civic_engagement"] = 0.9    # above cliff
    assert not _metric_past_cliff(basin, "civic_engagement"), \
        "FAIL: civic_engagement=0.9 should not be past cliff"

    # high_is_bad semantics: state >= cliff triggers
    from basin_states.base import BasinState
    contam = BasinState(
        name="air", basin_type="air",
        state={"particulate_load": 80.0},
        capacity={"particulate_load": 100.0},
        cliff_thresholds={"particulate_load": 60.0},
        high_is_bad={"particulate_load"},
    )
    assert _metric_past_cliff(contam, "particulate_load"), \
        "FAIL: particulate_load=80 with cliff=60 (high_is_bad) should be past"
    contam.state["particulate_load"] = 30.0
    assert not _metric_past_cliff(contam, "particulate_load"), \
        "FAIL: particulate_load=30 with cliff=60 (high_is_bad) should not be past"
    print("PASS")


def test_2_community_basin_black_when_past_cliff():
    """A community basin with civic_engagement below cliff registers
    BLACK — the exact scenario that silently passed before Bug 1 fix."""
    print("\n--- TEST 2: community basin past cliff → BLACK ---")
    basin = new_community_basin()
    basin.state["civic_engagement"] = 0.20   # cliff is 0.35

    tier = determine_tier_for_basin("site_community", basin)
    assert tier == Tier.BLACK, \
        f"FAIL: expected BLACK, got {tier}"
    print(f"  civic_engagement: {basin.state['civic_engagement']}")
    print(f"  cliff:            {basin.cliff_thresholds['civic_engagement']}")
    print(f"  tier:             {tier.name}")
    print("PASS")


def test_3_community_in_default_tertiary_mapping():
    """The community basin type routes to the four social tertiary pools."""
    print("\n--- TEST 3: community in DEFAULT_TERTIARY_MAPPING ---")
    assert "community" in DEFAULT_TERTIARY_MAPPING, \
        "FAIL: community missing from DEFAULT_TERTIARY_MAPPING"
    expected = {
        "social_fabric_reserve", "generational_transmission",
        "institutional_stock", "civic_trust_reserve",
    }
    assert set(DEFAULT_TERTIARY_MAPPING["community"]) == expected, \
        f"FAIL: community mapping mismatch: " \
        f"{DEFAULT_TERTIARY_MAPPING['community']}"
    print(f"  community → {DEFAULT_TERTIARY_MAPPING['community']}")
    print("PASS")


def test_4_community_tertiary_past_cliff_triggers_black():
    """A social tertiary pool past cliff makes the community basin BLACK
    even when every primary community metric is healthy."""
    print("\n--- TEST 4: social tertiary past cliff → community BLACK ---")
    basin = new_community_basin()   # all primaries healthy
    pools = new_standard_tertiary_pools()
    pools["civic_trust_reserve"].stock = 200.0   # cliff 300 → past

    tier = determine_tier_for_basin(
        "site_community", basin,
        tertiary_pools=pools,
        tertiary_mapping=DEFAULT_TERTIARY_MAPPING,
    )
    assert tier == Tier.BLACK, \
        f"FAIL: expected BLACK via tertiary, got {tier}"
    print(f"  civic_trust_reserve: 200/1000 (cliff 300) past cliff")
    print(f"  tier:                {tier.name}")
    print("PASS")


def test_5_vector_tier_assignment():
    """determine_tiers produces a per-basin-type vector — community
    can be BLACK while soil is GREEN."""
    print("\n--- TEST 5: vector TierAssignment ---")
    basins = {
        "site_soil": new_soil_basin(),
        "site_community": new_community_basin(),
    }
    basins["site_community"].state["civic_engagement"] = 0.20
    ta = determine_tiers(basins)
    assert ta.by_basin_type.get("community") == Tier.BLACK, \
        f"FAIL: community should be BLACK, got " \
        f"{ta.by_basin_type.get('community')}"
    assert ta.by_basin_type.get("soil") == Tier.GREEN, \
        f"FAIL: soil should be GREEN, got {ta.by_basin_type.get('soil')}"
    assert ta.overall_tier() == Tier.BLACK, \
        f"FAIL: overall should be BLACK (worst-basin)"
    print(f"  soil:      {ta.by_basin_type['soil'].name}")
    print(f"  community: {ta.by_basin_type['community'].name}")
    print(f"  overall:   {ta.overall_tier().name}")
    print("PASS")


def test_6_cohort_basin_sensitivities_vector_path():
    """Per-cohort load is the weighted sum of per-basin-type loads.

    With the standard GREEN=0 / BLACK=0.85 table:
      community cohort (weight 1.5 on community BLACK):
        1.5 * 0.85 = 1.275 → clipped to 1.0 → all members collapse
      capital cohort (weight 0.1 on community + 0.1 on soil GREEN):
        0.1 * 0.85 + 0.1 * 0.0 = 0.085 → buffers >= 0.1 survive
    """
    print("\n--- TEST 6: cohort_basin_sensitivities (Bug 4 fix) ---")
    basins = {
        "site_soil": new_soil_basin(),
        "site_community": new_community_basin(),
    }
    basins["site_community"].state["civic_engagement"] = 0.20
    ta = determine_tiers(basins)

    # community cohort: 200 members, every buffer in [0.2, 0.9] — well below 1.0
    community = PopulationCohort(
        cohort_name="community_members",
        members_buffers=[0.2 + 0.003 * i for i in range(200)],
    )
    # capital cohort: 500 members, every buffer >= 0.15 (safely above 0.085)
    capital = PopulationCohort(
        cohort_name="capital_market",
        members_buffers=[0.15 + 0.001 * i for i in range(500)],
    )

    sensitivities = {
        "community_members": {"community": 1.5, "soil": 0.4},
        "capital_market":    {"community": 0.1, "soil": 0.1},
    }

    report = apply_tier_to_cohorts(
        tier_assignment=ta,
        cohorts={"community_members": community, "capital_market": capital},
        cohort_basin_sensitivities=sensitivities,
    )

    comm_load = report.per_cohort_structural_load["community_members"]
    cap_load = report.per_cohort_structural_load["capital_market"]
    comm_collapsed = report.newly_collapsed_this_period["community_members"]
    cap_collapsed = report.newly_collapsed_this_period["capital_market"]

    print(f"  community load:    {comm_load:.3f} (clipped from 1.5*0.85=1.275)")
    print(f"  community coll'd:  {comm_collapsed}/200")
    print(f"  capital load:      {cap_load:.3f} (0.1*0.85 + 0.1*0)")
    print(f"  capital coll'd:    {cap_collapsed}/500")

    assert abs(comm_load - 1.0) < 1e-9, \
        f"FAIL: community load should clip to 1.0, got {comm_load}"
    assert comm_collapsed == 200, \
        f"FAIL: community cohort should fully collapse, got {comm_collapsed}"
    assert abs(cap_load - 0.085) < 1e-9, \
        f"FAIL: capital load should be 0.085, got {cap_load}"
    assert cap_collapsed == 0, \
        f"FAIL: capital cohort should not collapse, got {cap_collapsed}"
    print("PASS")


def test_7_scalar_path_backward_compatible():
    """Without cohort_basin_sensitivities, the legacy scalar path
    (worst-basin load * multiplier) still applies."""
    print("\n--- TEST 7: scalar path backward compatibility ---")
    basins = {
        "site_soil": new_soil_basin(),
        "site_community": new_community_basin(),
    }
    basins["site_community"].state["civic_engagement"] = 0.20
    ta = determine_tiers(basins)   # overall BLACK

    cohort = PopulationCohort(
        cohort_name="workers",
        members_buffers=[0.5] * 100,
    )
    # no sensitivities; legacy scalar path
    report = apply_tier_to_cohorts(
        tier_assignment=ta,
        cohorts={"workers": cohort},
        cohort_load_multipliers={"workers": 1.0},
    )
    assert abs(report.per_cohort_structural_load["workers"] - 0.85) < 1e-9, \
        f"FAIL: scalar path should give 0.85, got " \
        f"{report.per_cohort_structural_load['workers']}"
    assert report.newly_collapsed_this_period["workers"] == 100, \
        "FAIL: all buffers 0.5 < 0.85 should collapse"
    print(f"  load:       {report.per_cohort_structural_load['workers']:.3f}")
    print(f"  collapsed:  {report.newly_collapsed_this_period['workers']}/100")
    print("PASS")


def test_8_near_cliff_band():
    """_metric_near_cliff flags metrics close to but not past cliff,
    without false-flagging healthy baselines."""
    print("\n--- TEST 8: near-cliff band ---")
    basin = new_community_basin()
    # cliff 0.35, cap 1.2 → danger zone up to 0.35 + 0.25*(1.2-0.35) = 0.5625
    basin.state["civic_engagement"] = 0.50
    assert _metric_near_cliff(basin, "civic_engagement"), \
        "FAIL: civic_engagement=0.50 should be near cliff"
    basin.state["civic_engagement"] = 0.9
    assert not _metric_near_cliff(basin, "civic_engagement"), \
        "FAIL: civic_engagement=0.9 should not be near cliff"
    # past-cliff also returns True
    basin.state["civic_engagement"] = 0.20
    assert _metric_near_cliff(basin, "civic_engagement"), \
        "FAIL: past-cliff metric should also register near-cliff"
    print("PASS")


if __name__ == "__main__":
    test_1_past_cliff_detection()
    test_2_community_basin_black_when_past_cliff()
    test_3_community_in_default_tertiary_mapping()
    test_4_community_tertiary_past_cliff_triggers_black()
    test_5_vector_tier_assignment()
    test_6_cohort_basin_sensitivities_vector_path()
    test_7_scalar_path_backward_compatible()
    test_8_near_cliff_band()
    print("\nall tier-vector tests passed.")
