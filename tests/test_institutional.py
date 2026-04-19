"""
tests/test_institutional.py

Verifies the institutional constraint and waste accounting layer.

Core tests:
  1. Neurotypical in standard job: fit 1.0, waste near zero, no trauma
  2. Neurodivergent in mismatched job: high waste ratio, trauma tax > 0
  3. Self-designed work: amplification > 1, waste = 0 (or negative),
     trauma 0
  4. Collapsed members excluded from waste accounting (they're in
     the distributional invariant, not waste)
  5. Waste ratio computed correctly
  6. Amplification ratio computed correctly
  7. Kavik scenario: one person doing 3 full-time jobs (70 hr driving
     + 35 hr coding) vs a neurotypical operating at standard fit —
     the neurodivergent person shows UP to 3x available capacity
     while the neurotypical shows 0.7 baseline

Run: python tests/test_institutional.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distributional import (
    PopulationCohort,
    InstitutionalFitProfile,
    WasteReport,
    compute_waste_report,
    make_profile_neurotypical_standard_job,
    make_profile_neurodivergent_mismatched,
    make_profile_self_designed_work,
)


def make_cohort(name, size):
    """Simple cohort with uniform healthy buffers for waste testing."""
    return PopulationCohort(
        cohort_name=name,
        members_buffers=[0.8] * size,  # healthy, none collapsed
    )


def test_1_neurotypical_standard_job():
    """Neurotypical in standard job: fit 1.0, zero waste, zero trauma."""
    print("\n--- TEST 1: neurotypical in standard job ---")
    cohort = make_cohort("workers", 100)
    profile = make_profile_neurotypical_standard_job(
        "workers", 100, baseline_capacity=0.7, baseline_fit=1.0,
    )
    report = compute_waste_report({"workers": cohort}, {"workers": profile})
    print(f"  available:  {report.total_available_capacity:.2f}")
    print(f"  realized:   {report.total_realized_output:.2f}")
    print(f"  wasted:     {report.total_wasted_capacity:.2f}")
    print(f"  trauma tax: {report.total_trauma_tax:.2f}")
    print(f"  waste ratio:{report.waste_ratio:.2%}")
    # 100 members × 0.7 capacity × 1.0 fit = 70 realized
    assert abs(report.total_available_capacity - 70.0) < 1e-9
    assert abs(report.total_realized_output - 70.0) < 1e-9
    assert abs(report.total_wasted_capacity) < 1e-9
    assert report.total_trauma_tax == 0.0
    assert report.waste_ratio == 0.0
    print("PASS")


def test_2_neurodivergent_mismatched():
    """Mismatched institution: high waste ratio + trauma tax."""
    print("\n--- TEST 2: neurodivergent in mismatched job ---")
    cohort = make_cohort("workers", 100)
    profile = make_profile_neurodivergent_mismatched(
        "workers", 100,
        actual_capacity=1.5, institutional_fit=0.2, trauma_tax=0.2,
    )
    report = compute_waste_report({"workers": cohort}, {"workers": profile})
    print(f"  available:  {report.total_available_capacity:.2f}")
    print(f"  realized:   {report.total_realized_output:.2f}")
    print(f"  wasted:     {report.total_wasted_capacity:.2f}")
    print(f"  trauma tax: {report.total_trauma_tax:.2f}")
    print(f"  waste ratio:{report.waste_ratio:.2%}")
    # 100 × 1.5 × 0.2 = 30 realized
    # 100 × 1.5 × 0.8 = 120 wasted
    # 100 × 0.2     = 20 trauma
    assert abs(report.total_available_capacity - 150.0) < 1e-9
    assert abs(report.total_realized_output - 30.0) < 1e-9
    assert abs(report.total_wasted_capacity - 120.0) < 1e-9
    assert abs(report.total_trauma_tax - 20.0) < 1e-9
    # waste ratio = 120 / (30 + 120) = 0.8
    assert abs(report.waste_ratio - 0.8) < 1e-9
    print("PASS")


def test_3_self_designed_amplification():
    """Self-designed work: fit > 1.0, realized > available, no trauma."""
    print("\n--- TEST 3: self-designed work amplifies capacity ---")
    cohort = make_cohort("builders", 10)
    profile = make_profile_self_designed_work(
        "builders", 10,
        actual_capacity=2.5, institutional_fit=1.5, trauma_tax=0.0,
    )
    report = compute_waste_report(
        {"builders": cohort}, {"builders": profile}
    )
    print(f"  available:  {report.total_available_capacity:.2f}")
    print(f"  realized:   {report.total_realized_output:.2f}")
    print(f"  wasted:     {report.total_wasted_capacity:.2f}")
    print(f"  amplification_ratio: {report.amplification_ratio:.2%}")
    # 10 × 2.5 = 25 available
    # 10 × 2.5 × 1.5 = 37.5 realized (institution amplifies)
    # 10 × 2.5 × (1 - 1.5) = -12.5 wasted (negative = amplified)
    assert abs(report.total_realized_output - 37.5) < 1e-9
    assert report.total_wasted_capacity < 0, \
        "FAIL: amplification should produce negative waste"
    assert report.total_trauma_tax == 0.0
    assert report.amplification_ratio == 1.0, \
        "FAIL: all members should be amplified"
    print("PASS")


def test_4_collapsed_members_excluded():
    """Members who crossed cognitive cliff are excluded from waste
    (they're in the distributional invariant)."""
    print("\n--- TEST 4: collapsed members excluded from waste ---")
    cohort = make_cohort("workers", 10)
    # mark half as collapsed
    cohort.collapsed_member_indices = [0, 1, 2, 3, 4]
    profile = make_profile_neurodivergent_mismatched(
        "workers", 10, actual_capacity=1.5, institutional_fit=0.2,
        trauma_tax=0.2,
    )
    report = compute_waste_report({"workers": cohort}, {"workers": profile})
    print(f"  functional 5 members; waste over those only")
    print(f"  realized:   {report.total_realized_output:.2f}")
    print(f"  wasted:     {report.total_wasted_capacity:.2f}")
    print(f"  trauma tax: {report.total_trauma_tax:.2f}")
    # 5 × 1.5 × 0.2 = 1.5 realized
    # 5 × 1.5 × 0.8 = 6.0 wasted
    # 5 × 0.2     = 1.0 trauma
    assert abs(report.total_realized_output - 1.5) < 1e-9
    assert abs(report.total_wasted_capacity - 6.0) < 1e-9
    assert abs(report.total_trauma_tax - 1.0) < 1e-9
    print("PASS")


def test_5_waste_ratio():
    """Waste ratio: wasted / (wasted + realized)."""
    print("\n--- TEST 5: waste ratio computation ---")
    # three cohorts: standard, mismatched, self-designed
    cohorts = {
        "neurotyp": make_cohort("neurotyp", 100),
        "mismatched": make_cohort("mismatched", 100),
        "self_designed": make_cohort("self_designed", 100),
    }
    profiles = {
        "neurotyp": make_profile_neurotypical_standard_job(
            "neurotyp", 100, baseline_capacity=0.7, baseline_fit=1.0,
        ),
        "mismatched": make_profile_neurodivergent_mismatched(
            "mismatched", 100, actual_capacity=1.5,
            institutional_fit=0.1, trauma_tax=0.3,
        ),
        "self_designed": make_profile_self_designed_work(
            "self_designed", 100, actual_capacity=2.0,
            institutional_fit=1.2, trauma_tax=0.0,
        ),
    }
    report = compute_waste_report(cohorts, profiles)
    print(report.summary_text())
    # mismatched cohort has highest waste ratio
    assert report.per_cohort["mismatched"]["waste_ratio"] > 0.8
    assert report.per_cohort["neurotyp"]["waste_ratio"] == 0.0
    # self_designed has negative (amplified)
    assert report.per_cohort["self_designed"]["waste_ratio"] < 0
    print("PASS")


def test_6_amplification_ratio():
    """Amplification ratio: fraction of functional members with fit > 1.0."""
    print("\n--- TEST 6: amplification ratio ---")
    # 100 members: 30 amplified, 70 not
    capacities = [1.5] * 100
    fits = [1.5] * 30 + [1.0] * 70
    trauma = [0.0] * 100
    cohort = make_cohort("mixed", 100)
    profile = InstitutionalFitProfile(
        cohort_name="mixed",
        member_available_capacity=capacities,
        member_fit_multipliers=fits,
        member_trauma_tax=trauma,
    )
    report = compute_waste_report({"mixed": cohort}, {"mixed": profile})
    print(f"  amplification ratio: {report.amplification_ratio:.2%}")
    assert abs(report.amplification_ratio - 0.30) < 1e-9
    print("PASS")


def test_7_kavik_scenario():
    """Kavik: one neurodivergent member operating at ~3x baseline
    capacity in self-structured work, doing both driving + coding.

    Compare to hypothetical neurotypical in standard 35-hr job.
    """
    print("\n--- TEST 7: Kavik scenario — self-structured hyperfocus ---")
    kavik_cohort = PopulationCohort(
        cohort_name="kavik",
        members_buffers=[0.9],  # one person, high buffer
    )
    kavik_profile = InstitutionalFitProfile(
        cohort_name="kavik",
        # 70hr driving + 35hr coding ≈ 3x a standard 35hr work week
        # actual_capacity 3.0 reflects hyperfocus + intrinsic motivation
        # + environmental fit (self-designed pacing, self-chosen domain)
        member_available_capacity=[3.0],
        # fit 1.0+ because work is self-structured — institution isn't
        # fighting; it's letting the person operate at their capacity
        member_fit_multipliers=[1.0],
        member_trauma_tax=[0.0],
    )
    neurotyp_cohort = PopulationCohort(
        cohort_name="standard_worker",
        members_buffers=[0.7],
    )
    neurotyp_profile = make_profile_neurotypical_standard_job(
        "standard_worker", 1,
        baseline_capacity=0.7, baseline_fit=1.0,
    )

    report = compute_waste_report(
        {"kavik": kavik_cohort, "standard_worker": neurotyp_cohort},
        {"kavik": kavik_profile, "standard_worker": neurotyp_profile},
    )
    print(report.summary_text())

    # Kavik's realized output is roughly 4.3x the neurotypical's
    kavik_realized = report.per_cohort["kavik"]["realized"]
    neurotyp_realized = report.per_cohort["standard_worker"]["realized"]
    ratio = kavik_realized / neurotyp_realized
    print(f"\n  kavik realized output:   {kavik_realized:.2f}")
    print(f"  neurotyp realized:       {neurotyp_realized:.2f}")
    print(f"  ratio:                   {ratio:.2f}x")

    # Now show what happens if Kavik were in a standard job instead
    # (institutional_fit drops because mismatch; trauma tax appears)
    kavik_mismatched_profile = InstitutionalFitProfile(
        cohort_name="kavik_forced",
        member_available_capacity=[3.0],  # capacity unchanged
        member_fit_multipliers=[0.2],    # institution fights neurology
        member_trauma_tax=[0.3],         # burning energy to survive
    )
    report_mismatched = compute_waste_report(
        {"kavik_forced": kavik_cohort},
        {"kavik_forced": kavik_mismatched_profile},
    )
    forced_realized = report_mismatched.per_cohort["kavik_forced"]["realized"]
    forced_wasted = report_mismatched.per_cohort["kavik_forced"]["wasted"]
    forced_trauma = report_mismatched.per_cohort["kavik_forced"]["trauma"]
    print(f"\n  IF SAME KAVIK WERE FORCED INTO STANDARD INSTITUTION:")
    print(f"    realized:   {forced_realized:.2f} "
          f"(collapse from {kavik_realized:.2f})")
    print(f"    wasted:     {forced_wasted:.2f} "
          f"(capacity institution destroys)")
    print(f"    trauma tax: {forced_trauma:.2f} "
          f"(energy burned defending against structure)")
    print(f"\n  THE INSTITUTIONAL DECISION CHANGES:")
    print(f"    realized output from {kavik_realized:.2f} to {forced_realized:.2f}")
    print(f"    delta {kavik_realized - forced_realized:.2f} "
          f"lost to institutional mismatch.")
    print(f"    (This is the WASTE that conventional accounting treats as")
    print(f"     'person is low-capacity' rather than 'institution is failing')")

    assert forced_realized < kavik_realized, \
        "FAIL: institutional mismatch should reduce realized output"
    assert forced_wasted > 0, \
        "FAIL: mismatch should produce waste"
    print("\nPASS")


if __name__ == "__main__":
    test_1_neurotypical_standard_job()
    test_2_neurodivergent_mismatched()
    test_3_self_designed_amplification()
    test_4_collapsed_members_excluded()
    test_5_waste_ratio()
    test_6_amplification_ratio()
    test_7_kavik_scenario()
    print("\nall institutional waste tests passed.")
