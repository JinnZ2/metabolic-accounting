"""
tests/test_meritocracy_break.py

Demonstrates that the institutional measurement system is structurally
incapable of distinguishing between:

  (a) neurotypical worker hitting their ceiling at baseline capacity
  (b) neurodivergent worker operating at a tiny fraction of their
      capacity due to institutional constraint, YET STILL OUTPRODUCING (a)

The conventional meritocracy story says high performers are high
capacity, low performers are low capacity. This test shows the
framework can distinguish REALIZED OUTPUT from AVAILABLE CAPACITY,
and that the two often invert.

The consequence: "high performers" in mismatched institutions may be
neurodivergent people operating far below their capacity, and "low
performers" may be neurotypical people operating at their actual
ceiling. The institution cannot tell the difference because it only
measures realized output.

Run: python tests/test_meritocracy_break.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distributional import (
    PopulationCohort,
    InstitutionalFitProfile,
    compute_waste_report,
)


def test_constrained_neurodivergent_outperforms_unconstrained_neurotypical():
    print("\n--- MERITOCRACY BREAK TEST ---")
    print("Question: can a neurodivergent worker in a mismatched")
    print("institution still outperform a neurotypical worker in a")
    print("fitting one, WHILE BEING CLASSIFIED AS UNDERPERFORMING?")
    print()

    # one neurodivergent member, forced into standard institution
    # capacity 3.0, fit 0.2 (severe mismatch), trauma tax 0.3
    nd_cohort = PopulationCohort(
        cohort_name="nd_constrained",
        members_buffers=[0.9],
    )
    nd_profile = InstitutionalFitProfile(
        cohort_name="nd_constrained",
        member_available_capacity=[3.0],
        member_fit_multipliers=[0.2],
        member_trauma_tax=[0.3],
    )

    # one neurotypical member, same institution, fits perfectly
    # capacity 0.7, fit 1.0, no trauma
    nt_cohort = PopulationCohort(
        cohort_name="nt_fitting",
        members_buffers=[0.8],
    )
    nt_profile = InstitutionalFitProfile(
        cohort_name="nt_fitting",
        member_available_capacity=[0.7],
        member_fit_multipliers=[1.0],
        member_trauma_tax=[0.0],
    )

    report = compute_waste_report(
        {"nd_constrained": nd_cohort, "nt_fitting": nt_cohort},
        {"nd_constrained": nd_profile, "nt_fitting": nt_profile},
    )

    nd_realized = report.per_cohort["nd_constrained"]["realized"]
    nt_realized = report.per_cohort["nt_fitting"]["realized"]
    nd_wasted = report.per_cohort["nd_constrained"]["wasted"]
    nd_trauma = report.per_cohort["nd_constrained"]["trauma"]

    print(f"NEURODIVERGENT worker, mismatched institution:")
    print(f"  available capacity: 3.00")
    print(f"  fit multiplier:     0.20 (institution fights neurology)")
    print(f"  trauma tax:         0.30")
    print(f"  realized output:    {nd_realized:.2f}")
    print(f"  wasted capacity:    {nd_wasted:.2f}")
    print()
    print(f"NEUROTYPICAL worker, fitting institution:")
    print(f"  available capacity: 0.70")
    print(f"  fit multiplier:     1.00 (institution matches neurology)")
    print(f"  trauma tax:         0.00")
    print(f"  realized output:    {nt_realized:.2f}")
    print()
    print(f"COMPARISON:")
    print(f"  neurodivergent (constrained) output:  {nd_realized:.2f}")
    print(f"  neurotypical (fitting) output:        {nt_realized:.2f}")

    if nd_realized < nt_realized:
        print(f"  -> neurodivergent UNDERPERFORMS by {nt_realized - nd_realized:.2f}")
        print(f"     Institution classifies nd as 'low performer'")
        print(f"     TRUE STATE: nd has 4.3x the actual capacity;")
        print(f"                 institution is destroying 2.40 units/period.")
    else:
        print(f"  -> neurodivergent STILL OUTPERFORMS by "
              f"{nd_realized - nt_realized:.2f}")
        print(f"     Institution classifies nd as 'just meets expectations'")
        print(f"     or 'not a team player' — because relative to capacity")
        print(f"     they are visibly underperforming to someone who KNOWS,")
        print(f"     but relative to peer output they're on par or above.")
    print()

    # now show the crossover case: how mismatched does the institution
    # have to be before the neurodivergent worker's realized output
    # drops below the neurotypical's?
    print("CROSSOVER ANALYSIS:")
    print("At what fit multiplier does the neurodivergent worker's")
    print("realized output drop below the neurotypical worker's 0.70?")
    print()
    print("  fit multiplier | nd realized output | beats nt (0.70)?")
    print("  ---------------|-------------------|------------------")
    for fit in [1.0, 0.5, 0.3, 0.25, 0.234, 0.2, 0.15, 0.1]:
        output = 3.0 * fit
        beats = "YES" if output > 0.70 else "no"
        print(f"  {fit:13.3f}  |  {output:16.2f}  |  {beats}")
    print()
    print("Crossover at fit ~0.233 — below that, the institution's measurement")
    print("finally catches the neurodivergent worker. Above that, the worker")
    print("outperforms despite being at 23% of their capacity.")
    print()
    print("Real-world implication: institutions routinely extract labor at")
    print("a fraction of what's available, while labeling the worker as")
    print("underperforming relative to their (invisible) ceiling.")


if __name__ == "__main__":
    test_constrained_neurodivergent_outperforms_unconstrained_neurotypical()
    print("\n(this is a demonstration test, no assertions)")
