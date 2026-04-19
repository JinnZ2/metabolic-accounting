"""
tests/test_social_cascade.py

Pass 2 of the social substrate layer: behavioral cascade signatures,
social tertiary pools, and compound BLACK detection.

Exercises:

  1. Healthy community basin produces near-baseline signatures
  2. Depleted community basin produces elevated signatures
  3. Rural community basin starts with noticeable signature elevation
  4. Full collapse produces rural-cohort-multiplier signatures
  5. is_social_black triggers correctly on threshold conditions
  6. Tertiary pool amplification: exhausted pool amplifies signatures
  7. Compound BLACK: env + social both in irreversibility
  8. Env BLACK alone does not trigger compound
  9. Social BLACK alone does not trigger compound
  10. Full pipeline: Site with community basin -> signatures computed

Run: python -m tests.test_social_cascade
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_community_basin, new_rural_community_basin,
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from reserves import Site
from social_cascade import (
    compute_community_signatures, is_social_black,
    build_compound_report,
    BASELINE_DEATHS_OF_DESPAIR, BASELINE_VIOLENT_CRIME,
    BASELINE_PROBLEM_GAMBLING_PCT, BASELINE_YOUTH_DISENGAGEMENT_PCT,
    RURAL_COHORT_MULTIPLIER,
)


def fresh_site_with_community():
    """Build a site with community basin and default social reserves/pools."""
    site = Site(name="social_site", basins={
        "site_soil": new_soil_basin(),
        "site_water": new_water_basin(),
        "site_community": new_community_basin(),
    })
    site.attach_defaults()
    return site


def test_1_healthy_near_baseline():
    """Healthy community basin produces signatures near baseline (no elevation)."""
    print("\n--- TEST 1: healthy community basin ---")
    site = fresh_site_with_community()
    basin = site.basins["site_community"]
    sig = compute_community_signatures(
        basin,
        secondary_reserves=site.secondary.get("site_community"),
        tertiary_pools=site.tertiary,
    )
    print(f"  deaths of despair: {sig.deaths_of_despair_rate:.2f} (baseline {BASELINE_DEATHS_OF_DESPAIR})")
    print(f"  violent crime:     {sig.violent_crime_rate:.1f} (baseline {BASELINE_VIOLENT_CRIME})")
    print(f"  gambling:          {sig.problem_gambling_prevalence:.3f}% (baseline {BASELINE_PROBLEM_GAMBLING_PCT}%)")
    print(f"  aggregate load:    {sig.aggregate_externalized_load:.3f}")
    # should be at baseline — no elevation
    assert sig.aggregate_externalized_load < 0.1, \
        f"FAIL: healthy basin should have ~0 externalized load"
    assert not is_social_black(sig), "FAIL: healthy basin should not be social BLACK"
    print("PASS")


def test_2_depleted_elevated_signatures():
    """Depleted community basin produces measurably elevated signatures."""
    print("\n--- TEST 2: depleted community basin elevates signatures ---")
    site = fresh_site_with_community()
    basin = site.basins["site_community"]
    # push several metrics toward their cliffs
    basin.state["economic_security"] = 0.55      # near cliff 0.5
    basin.state["social_capital"] = 0.45          # near cliff 0.4
    basin.state["family_formation"] = 0.55        # near cliff 0.5

    sig = compute_community_signatures(
        basin,
        tertiary_pools=site.tertiary,
    )
    print(f"  deaths of despair: {sig.deaths_of_despair_rate:.2f} (baseline {BASELINE_DEATHS_OF_DESPAIR})")
    print(f"  violent crime:     {sig.violent_crime_rate:.1f}")
    print(f"  family collapse:   {sig.family_collapse_rate:.3f}/1000")
    print(f"  aggregate load:    {sig.aggregate_externalized_load:.3f}")
    print(f"  driven by:         {sig.driven_by_metrics}")
    assert sig.despair_delta > 0, "FAIL: despair should elevate"
    assert sig.violent_crime_delta > 0, "FAIL: violent crime should elevate"
    assert sig.aggregate_externalized_load > 0.5, \
        "FAIL: aggregate load should be >> baseline when basin near cliffs"
    print("PASS")


def test_3_rural_basin_starts_elevated():
    """Rural basin already shows signature elevation from pre-depletion."""
    print("\n--- TEST 3: rural community basin starts elevated ---")
    site = Site(name="rural_site", basins={
        "site_community": new_rural_community_basin(),
    })
    site.attach_defaults()
    basin = site.basins["site_community"]
    sig = compute_community_signatures(basin, tertiary_pools=site.tertiary)
    print(f"  despair rate:      {sig.deaths_of_despair_rate:.2f}")
    print(f"  despair delta:     {sig.despair_delta:+.2f}")
    print(f"  youth disengagement:{sig.youth_disengagement_pct:.2f}%")
    print(f"  aggregate load:    {sig.aggregate_externalized_load:.3f}")
    assert sig.despair_delta > 0, "FAIL: rural baseline should show despair elevation"
    assert sig.youth_disengagement_delta > 0, \
        "FAIL: rural youth_retention pre-depletion should elevate youth disengagement"
    print("PASS")


def test_4_full_collapse_reaches_multiplier():
    """Severe depletion produces signatures approaching rural cohort multiplier."""
    print("\n--- TEST 4: full collapse reaches rural-cohort multiplier ---")
    site = fresh_site_with_community()
    basin = site.basins["site_community"]
    # crash all metrics past their cliffs
    basin.state.update({
        "economic_security": 0.2,
        "social_capital": 0.15,
        "family_formation": 0.2,
        "youth_retention": 0.1,
        "generational_knowledge": 0.1,
        "civic_engagement": 0.15,
    })
    # also crash social tertiary pools to amplify
    site.tertiary["social_fabric_reserve"].stock = 400.0   # cliff 600
    site.tertiary["generational_transmission"].stock = 200.0  # cliff 360
    site.tertiary["institutional_stock"].stock = 300.0     # cliff 450
    site.tertiary["civic_trust_reserve"].stock = 150.0     # cliff 300

    sig = compute_community_signatures(basin, tertiary_pools=site.tertiary)
    print(f"  despair rate:      {sig.deaths_of_despair_rate:.2f}")
    print(f"  ratio to baseline: {sig.deaths_of_despair_rate / BASELINE_DEATHS_OF_DESPAIR:.2f}x")
    print(f"  rural multiplier:  {RURAL_COHORT_MULTIPLIER}x")
    print(f"  aggregate load:    {sig.aggregate_externalized_load:.3f}")
    assert sig.deaths_of_despair_rate >= BASELINE_DEATHS_OF_DESPAIR * RURAL_COHORT_MULTIPLIER, \
        f"FAIL: full collapse should hit rural multiplier"
    assert is_social_black(sig), "FAIL: full collapse should trigger social BLACK"
    print("PASS")


def test_5_is_social_black_triggers():
    """is_social_black triggers on each of its three pathways."""
    print("\n--- TEST 5: is_social_black triggers correctly ---")
    from social_cascade import CommunitySignatures

    # pathway A: despair rate above rural multiplier
    sig_a = CommunitySignatures()
    sig_a.deaths_of_despair_rate = BASELINE_DEATHS_OF_DESPAIR * RURAL_COHORT_MULTIPLIER
    sig_a.despair_delta = sig_a.deaths_of_despair_rate - BASELINE_DEATHS_OF_DESPAIR
    assert is_social_black(sig_a), "FAIL: pathway A should trigger"
    print(f"  pathway A (despair >= 2x baseline): TRIGGERED")

    # pathway B: aggregate load >= 3.0
    sig_b = CommunitySignatures(aggregate_externalized_load=3.5)
    assert is_social_black(sig_b), "FAIL: pathway B should trigger"
    print(f"  pathway B (aggregate load >= 3.0):  TRIGGERED")

    # pathway C: any single signature >= 2x baseline
    sig_c = CommunitySignatures()
    sig_c.violent_crime_rate = BASELINE_VIOLENT_CRIME * 2.1
    assert is_social_black(sig_c), "FAIL: pathway C should trigger"
    print(f"  pathway C (single sig >= 2x):       TRIGGERED")

    # below all thresholds: no trigger
    sig_none = CommunitySignatures(aggregate_externalized_load=0.5)
    sig_none.deaths_of_despair_rate = BASELINE_DEATHS_OF_DESPAIR * 1.3
    assert not is_social_black(sig_none), "FAIL: below thresholds shouldn't trigger"
    print(f"  baseline-ish conditions:             NOT TRIGGERED")
    print("PASS")


def test_6_tertiary_amplification():
    """Exhausted social tertiary pool amplifies signatures from the same basin state."""
    print("\n--- TEST 6: tertiary pool exhaustion amplifies signatures ---")
    site = fresh_site_with_community()
    basin = site.basins["site_community"]
    # same moderate basin depletion in both cases
    basin.state["economic_security"] = 0.6
    basin.state["social_capital"] = 0.5

    sig_healthy_tertiary = compute_community_signatures(
        basin, tertiary_pools=site.tertiary)

    # now exhaust social tertiary pools
    site.tertiary["social_fabric_reserve"].stock = 300.0   # past cliff 600
    site.tertiary["institutional_stock"].stock = 200.0     # past cliff 450

    sig_exhausted_tertiary = compute_community_signatures(
        basin, tertiary_pools=site.tertiary)

    print(f"  despair, healthy tertiary:   {sig_healthy_tertiary.deaths_of_despair_rate:.2f}")
    print(f"  despair, exhausted tertiary: {sig_exhausted_tertiary.deaths_of_despair_rate:.2f}")
    print(f"  amplification factor:        "
          f"{sig_exhausted_tertiary.deaths_of_despair_rate / sig_healthy_tertiary.deaths_of_despair_rate:.2f}x")

    assert sig_exhausted_tertiary.deaths_of_despair_rate > \
           sig_healthy_tertiary.deaths_of_despair_rate, \
        "FAIL: exhausted tertiary should amplify signatures"
    print("PASS")


def test_7_compound_black():
    """Both environmental and social BLACK triggers compound BLACK."""
    print("\n--- TEST 7: compound BLACK triggers correctly ---")
    # env irreversibility present
    env_irr = ["site_soil.carbon_fraction"]
    env_tertiary_cliff = ["landscape_reserve"]

    # social BLACK present: make signatures hit pathway A
    from social_cascade import CommunitySignatures
    social_sig = CommunitySignatures()
    social_sig.deaths_of_despair_rate = (
        BASELINE_DEATHS_OF_DESPAIR * RURAL_COHORT_MULTIPLIER * 1.1
    )
    social_sig.aggregate_externalized_load = 3.5

    report = build_compound_report(
        environmental_irreversible_metrics=env_irr,
        environmental_tertiary_past_cliff=env_tertiary_cliff,
        social_signatures=social_sig,
    )
    print(f"  env BLACK:      {report.environmental_black}")
    print(f"  social BLACK:   {report.social_black}")
    print(f"  compound BLACK: {report.compound_black}")
    print(f"  notes:          {report.notes[:100]}...")
    assert report.compound_black, "FAIL: env BLACK + social BLACK should trigger compound"
    print("PASS")


def test_8_env_black_alone_no_compound():
    """Env BLACK alone does NOT trigger compound BLACK."""
    print("\n--- TEST 8: env BLACK alone ---")
    from social_cascade import CommunitySignatures
    # env BLACK on, social healthy
    report = build_compound_report(
        environmental_irreversible_metrics=["site_soil.carbon_fraction"],
        environmental_tertiary_past_cliff=[],
        social_signatures=CommunitySignatures(),   # empty/healthy
    )
    print(f"  env BLACK:      {report.environmental_black}")
    print(f"  social BLACK:   {report.social_black}")
    print(f"  compound BLACK: {report.compound_black}")
    assert report.environmental_black, "FAIL: env should be BLACK"
    assert not report.compound_black, "FAIL: compound should not trigger without social BLACK"
    print("PASS")


def test_9_social_black_alone_no_compound():
    """Social BLACK without env BLACK does NOT trigger compound."""
    print("\n--- TEST 9: social BLACK alone (deindustrialization signature) ---")
    from social_cascade import CommunitySignatures
    social_sig = CommunitySignatures(aggregate_externalized_load=3.5)
    social_sig.deaths_of_despair_rate = BASELINE_DEATHS_OF_DESPAIR * 2.5
    report = build_compound_report(
        environmental_irreversible_metrics=[],
        environmental_tertiary_past_cliff=[],
        social_signatures=social_sig,
    )
    print(f"  env BLACK:      {report.environmental_black}")
    print(f"  social BLACK:   {report.social_black}")
    print(f"  compound BLACK: {report.compound_black}")
    print(f"  notes:          {report.notes[:100]}...")
    assert report.social_black, "FAIL: social should be BLACK"
    assert not report.compound_black, "FAIL: compound should not trigger without env BLACK"
    print("PASS")


def test_10_site_pipeline_integration():
    """Full pipeline: Site with stress applied produces signatures via pipeline."""
    print("\n--- TEST 10: full pipeline integration ---")
    site = fresh_site_with_community()
    # apply sustained stress to economic_security
    for _ in range(3):
        site.step(stress={("site_community", "economic_security"): 20.0},
                  regenerate=False)
    basin = site.basins["site_community"]
    sig = compute_community_signatures(
        basin,
        secondary_reserves=site.secondary.get("site_community"),
        tertiary_pools=site.tertiary,
    )
    print(f"  after 3 stress periods:")
    print(f"    basin state:   {basin.state}")
    print(f"    despair rate:  {sig.deaths_of_despair_rate:.2f}")
    print(f"    aggregate:     {sig.aggregate_externalized_load:.3f}")
    # should have some elevation from cumulative damage
    # (even if basin state didn't move much, social tertiary pools should show it)
    tp_fracs = {n: p.fraction_remaining() for n, p in site.tertiary.items()}
    print(f"    social tertiary fractions: "
          f"fabric={tp_fracs['social_fabric_reserve']:.3f}, "
          f"inst={tp_fracs['institutional_stock']:.3f}")
    print("PASS")


if __name__ == "__main__":
    test_1_healthy_near_baseline()
    test_2_depleted_elevated_signatures()
    test_3_rural_basin_starts_elevated()
    test_4_full_collapse_reaches_multiplier()
    test_5_is_social_black_triggers()
    test_6_tertiary_amplification()
    test_7_compound_black()
    test_8_env_black_alone_no_compound()
    test_9_social_black_alone_no_compound()
    test_10_site_pipeline_integration()
    print("\nall social cascade tests passed.")
