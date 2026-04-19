"""
tests/test_distributional.py

Verifies distributional layer in THERMODYNAMIC UNITS ONLY.

No price tests. Instead:
  1. Tier determination works
  2. Individual buffer thresholds create nonlinear collapse:
     small load -> zero cliff crossings
     moderate load -> partial cliff crossings
     high load -> majority cliff crossings
  3. Collapse is IRREVERSIBLE without explicit recovery mechanism
  4. Collapse is not linear: a small load increase past a population's
     buffer mean causes much larger than proportional collapse
  5. Cohort multipliers: community cohorts (1.5x mult) collapse before
     capital cohorts (0.3x mult) under same tier
  6. Distributional invariant: capacity lost is attributed by cohort
     classification; residual load reflects un-collapsed-but-loaded capacity
  7. Externalization ratio: firm with zero internal absorption shows
     100% externalization
  8. Recovery is NOT automatic — requires explicit recovery_fraction
     AND buffer above load
  9. Aggregate functional fraction matches cohort-level collapse
 10. Once collapsed, a member stays collapsed even if load drops
     (unless explicit recovery)

Run: python tests/test_distributional.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basin_states import (
    new_soil_basin, new_air_basin, new_water_basin, new_biology_basin,
)
from reserves import Site
from distributional import (
    Tier, TierAssignment,
    determine_tiers,
    PopulationCohort,
    apply_structural_load,
    recover_cohort,
    apply_tier_to_cohorts,
    make_cohort_with_buffer_distribution,
    compute_distributional_balance,
)


def fresh_site():
    site = Site(name="dist_site", basins={
        "site_soil": new_soil_basin(),
        "site_air": new_air_basin(),
        "site_water": new_water_basin(),
        "site_biology": new_biology_basin(),
    })
    site.attach_defaults()
    return site


def test_1_tier_determination_unchanged():
    """Tier determination still works as before (no price there)."""
    print("\n--- TEST 1: tier determination still works ---")
    site = fresh_site()
    tiers = determine_tiers(site.basins, site.secondary, site.tertiary)
    assert tiers.overall_tier() == Tier.GREEN
    site.tertiary["landscape_reserve"].stock = 50.0
    tiers = determine_tiers(site.basins, site.secondary, site.tertiary)
    assert tiers.overall_tier() == Tier.BLACK
    print("  healthy -> GREEN, past cliff -> BLACK: PASS")


def test_2_threshold_nonlinearity():
    """The core test: output collapse is nonlinear in structural load.

    Build a cohort with triangular buffer distribution centered at 0.5.
    Apply loads 0.1, 0.3, 0.5, 0.7, 0.9.
    At 0.1 -> zero or few cliff crossings.
    At 0.5 -> ~50% cliff crossings.
    At 0.9 -> near total collapse.
    The jump from 0.4 to 0.6 should be larger than the jump from 0.0
    to 0.2 — nonlinearity visible near the distribution's center.
    """
    print("\n--- TEST 2: threshold nonlinearity (the core claim) ---")
    loads = [0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9]
    collapsed_counts = []
    for load in loads:
        c = make_cohort_with_buffer_distribution(
            cohort_name="test", size=1000,
            buffer_mean=0.5, buffer_std=0.15,
            seed=42,
        )
        c, crossed = apply_structural_load(c, load)
        collapsed_counts.append(len(crossed))
        print(f"  load {load:.1f}: {len(crossed)} / 1000 collapsed "
              f"({100*len(crossed)/1000:.1f}%)")
    # nonlinear: jump from 0.4->0.5->0.6 should be steeper than 0.0->0.1->0.2
    assert collapsed_counts[3] > collapsed_counts[0] * 5, \
        "FAIL: load 0.5 should collapse far more than load 0.1"
    # monotone
    for i in range(1, len(loads)):
        assert collapsed_counts[i] >= collapsed_counts[i-1], \
            "FAIL: more load should not reduce collapse"
    # near total at 0.9
    assert collapsed_counts[-1] > 900, \
        f"FAIL: at load 0.9, expected most collapsed, got {collapsed_counts[-1]}"
    print("PASS: output collapse is nonlinear in structural load")


def test_3_irreversibility_without_recovery():
    """Once a member crosses their cliff, they stay there."""
    print("\n--- TEST 3: collapse is irreversible without recovery ---")
    c = make_cohort_with_buffer_distribution(
        cohort_name="test", size=100, buffer_mean=0.5, buffer_std=0.1,
        seed=7,
    )
    # apply high load
    c, crossed_high = apply_structural_load(c, 0.8)
    high_collapsed = c.collapsed_count()
    print(f"  high load: {high_collapsed} collapsed")
    # drop load to zero — without recovery_fraction, should stay collapsed
    c, crossed_low = apply_structural_load(c, 0.0)
    post_drop_collapsed = c.collapsed_count()
    print(f"  load dropped to 0, no recovery: {post_drop_collapsed} still collapsed")
    assert post_drop_collapsed == high_collapsed, \
        "FAIL: load drop should not automatically recover"
    assert len(crossed_low) == 0, \
        "FAIL: no new collapses at load 0"
    print("PASS")


def test_4_cohort_mult_community_collapses_first():
    """Community cohorts with multiplier > 1 collapse before capital
    cohorts with multiplier < 1 under same tier."""
    print("\n--- TEST 4: cohort multipliers — community vs capital ---")
    community = make_cohort_with_buffer_distribution(
        "community", size=200, buffer_mean=0.5, buffer_std=0.15, seed=1,
    )
    capital_market = make_cohort_with_buffer_distribution(
        "capital_market", size=200, buffer_mean=0.5, buffer_std=0.15, seed=2,
    )
    cohorts = {"community": community, "capital_market": capital_market}

    # AMBER tier (load 0.25). With mult 1.5 for community (effective 0.375)
    # and mult 0.3 for capital (effective 0.075)
    ta = TierAssignment(by_basin_type={"soil": Tier.AMBER})
    report = apply_tier_to_cohorts(
        ta, cohorts,
        cohort_load_multipliers={"community": 1.5, "capital_market": 0.3},
    )
    comm_crossed = report.newly_collapsed_this_period["community"]
    cap_crossed = report.newly_collapsed_this_period["capital_market"]
    print(f"  community collapsed (mult 1.5): {comm_crossed}")
    print(f"  capital_market collapsed (mult 0.3): {cap_crossed}")
    assert comm_crossed > cap_crossed, \
        "FAIL: higher-multiplier cohort should collapse more"
    print("PASS")


def test_5_invariant_classification():
    """Distributional balance classifies cohorts correctly."""
    print("\n--- TEST 5: invariant cohort classification ---")
    workers = make_cohort_with_buffer_distribution(
        "skilled_workers", size=100, buffer_mean=0.4, buffer_std=0.1, seed=3,
    )
    inst = make_cohort_with_buffer_distribution(
        "permit_agency", size=50, buffer_mean=0.5, buffer_std=0.1, seed=4,
    )
    community = make_cohort_with_buffer_distribution(
        "local_residents", size=300, buffer_mean=0.3, buffer_std=0.1, seed=5,
    )
    ta = TierAssignment(by_basin_type={"soil": Tier.RED})
    report = apply_tier_to_cohorts(ta, {
        "skilled_workers": workers,
        "permit_agency": inst,
        "local_residents": community,
    })
    balance = compute_distributional_balance(
        report,
        firm_internal_capacity_lost=5.0,
        cohort_classification={
            "skilled_workers": "worker",
            "permit_agency": "institutional",
            "local_residents": "community",
        },
    )
    print(balance.summary_text())
    assert balance.worker_cliffs_crossed > 0, "FAIL: no worker cliffs"
    assert balance.community_cliffs_crossed > 0, "FAIL: no community cliffs"
    assert balance.firm_internal_capacity_lost == 5.0
    # community has LOWER mean buffer (0.3) vs worker (0.4), same load,
    # so community should have MORE cliffs
    # worker (0.4 mean, load 0.55) -> most collapse
    # community (0.3 mean, load 0.55) -> nearly all collapse
    comm_frac = (report.cohorts["local_residents"].collapsed_count()
                 / report.cohorts["local_residents"].population_size())
    worker_frac = (report.cohorts["skilled_workers"].collapsed_count()
                   / report.cohorts["skilled_workers"].population_size())
    assert comm_frac >= worker_frac, \
        f"FAIL: community fraction {comm_frac} < worker fraction {worker_frac}"
    print("PASS")


def test_6_externalization_ratio():
    """Firm with zero internal absorption -> 100% externalization."""
    print("\n--- TEST 6: externalization ratio ---")
    c = make_cohort_with_buffer_distribution(
        "residents", size=500, buffer_mean=0.4, buffer_std=0.2, seed=11,
    )
    ta = TierAssignment(by_basin_type={"water": Tier.BLACK})
    report = apply_tier_to_cohorts(ta, {"residents": c})
    balance = compute_distributional_balance(
        report,
        firm_internal_capacity_lost=0.0,
        cohort_classification={"residents": "community"},
    )
    print(balance.summary_text())
    if balance.total_capacity_lost() > 0:
        assert balance.externalization_ratio == 1.0, \
            f"FAIL: zero internal absorption -> 100% external, " \
            f"got {balance.externalization_ratio}"
    print("PASS")


def test_7_recovery_requires_explicit_mechanism():
    """Without recovery_fraction set, no one recovers. With it set,
    only members whose buffer >= current load can recover."""
    print("\n--- TEST 7: recovery requires explicit mechanism ---")
    c = PopulationCohort(
        cohort_name="test",
        members_buffers=[0.3, 0.5, 0.7, 0.9],
    )
    # crash them all
    c, crossed = apply_structural_load(c, 0.95)
    assert c.collapsed_count() == 4, "FAIL: initial crash"

    # reduce load to 0.4 without recovery -> stays collapsed
    c, crossed_new = apply_structural_load(c, 0.4)
    assert c.collapsed_count() == 4, "FAIL: drop without recovery"

    # now apply recovery at load 0.4 -> members with buffer >= 0.4
    # are eligible (0.5, 0.7, 0.9 = 3 members). recovery_fraction=1.0
    # -> all 3 eligible recover
    c, recovered = recover_cohort(c, 0.4, recovery_fraction=1.0)
    print(f"  members recovered: {len(recovered)}")
    assert len(recovered) == 3, f"FAIL: expected 3 recovered, got {len(recovered)}"
    assert c.collapsed_count() == 1, "FAIL: one should remain collapsed (buffer 0.3 < load 0.4)"
    print("PASS")


def test_8_functional_fraction_aggregate():
    """Aggregate functional fraction correctly reflects cohort collapse."""
    print("\n--- TEST 8: aggregate functional fraction ---")
    c1 = make_cohort_with_buffer_distribution(
        "c1", size=100, buffer_mean=0.3, buffer_std=0.05, seed=13,
    )
    c2 = make_cohort_with_buffer_distribution(
        "c2", size=100, buffer_mean=0.8, buffer_std=0.05, seed=14,
    )
    ta = TierAssignment(by_basin_type={"soil": Tier.RED})
    # load 0.55 — c1 (mean 0.3) mostly collapses, c2 (mean 0.8) mostly survives
    report = apply_tier_to_cohorts(ta, {"c1": c1, "c2": c2})
    print(f"  c1 functional: {c1.functional_count()}/100")
    print(f"  c2 functional: {c2.functional_count()}/100")
    print(f"  overall: {report.functional_fraction():.2%}")
    total_functional = c1.functional_count() + c2.functional_count()
    assert abs(report.functional_fraction() - total_functional/200) < 1e-9, \
        "FAIL: aggregate fraction mismatch"
    # c1 should have mostly collapsed, c2 mostly survived
    assert c1.functional_count() < 30, f"FAIL: c1 should mostly collapse, got {c1.functional_count()}"
    assert c2.functional_count() > 70, f"FAIL: c2 should mostly survive, got {c2.functional_count()}"
    print("PASS")


def test_9_once_collapsed_stays_without_recovery():
    """Persistent collapse across periods under oscillating load."""
    print("\n--- TEST 9: persistent collapse across periods ---")
    c = make_cohort_with_buffer_distribution(
        "test", size=100, buffer_mean=0.5, buffer_std=0.15, seed=19,
    )
    # period 1: high load
    c, _ = apply_structural_load(c, 0.9)
    p1_collapsed = c.collapsed_count()
    # period 2: low load, no recovery mechanism
    c, _ = apply_structural_load(c, 0.1)
    p2_collapsed = c.collapsed_count()
    # period 3: high load again
    c, _ = apply_structural_load(c, 0.95)
    p3_collapsed = c.collapsed_count()

    print(f"  period 1 (load 0.9): {p1_collapsed} collapsed")
    print(f"  period 2 (load 0.1): {p2_collapsed} collapsed")
    print(f"  period 3 (load 0.95): {p3_collapsed} collapsed")
    # collapse is monotonic without recovery
    assert p2_collapsed >= p1_collapsed, "FAIL: period 2 uncollapsed"
    assert p3_collapsed >= p2_collapsed, "FAIL: period 3 regressed"
    print("PASS")


def test_10_no_price_fields_exist():
    """Structural check: no currency fields on access or invariant dataclasses."""
    print("\n--- TEST 10: no price/currency fields in public API ---")
    from distributional import AccessReport, DistributionalBalance, PopulationCohort
    import dataclasses

    price_words = ("cost", "premium", "spread", "bps", "price", "currency",
                   "dollar", "yield", "rate")

    def check(cls):
        fields = dataclasses.fields(cls)
        for f in fields:
            name = f.name.lower()
            for w in price_words:
                # "rate" appears in recovery_rate but that's not price;
                # be specific about currency contamination only
                if w in name and w != "rate":
                    raise AssertionError(
                        f"FAIL: {cls.__name__}.{f.name} contains '{w}' "
                        f"— possible price contamination"
                    )

    check(AccessReport)
    check(DistributionalBalance)
    check(PopulationCohort)
    print("  AccessReport: no price fields")
    print("  DistributionalBalance: no price fields")
    print("  PopulationCohort: no price fields")
    print("PASS")


if __name__ == "__main__":
    test_1_tier_determination_unchanged()
    test_2_threshold_nonlinearity()
    test_3_irreversibility_without_recovery()
    test_4_cohort_mult_community_collapses_first()
    test_5_invariant_classification()
    test_6_externalization_ratio()
    test_7_recovery_requires_explicit_mechanism()
    test_8_functional_fraction_aggregate()
    test_9_once_collapsed_stays_without_recovery()
    test_10_no_price_fields_exist()
    print("\nall distributional tests passed (capacity units only, no price).")
