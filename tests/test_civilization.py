"""
tests/test_civilization.py

Verifies the civilization-scale waste audit module.

Core tests:
  1. WasteBreakdown totals correctly across four categories
  2. CivilizationAudit per-capita and aggregate math
  3. Era comparisons: modern shows higher waste ratio than Renaissance
     despite higher absolute population
  4. Modern per-capita realized capacity is LOWER than Bronze Age,
     matching the innovation-crisis observation
  5. Counterfactual: if modern had Renaissance waste ratio, realized
     capacity per capita would be substantially higher
  6. Capacity-fit economy hypothetical: amplification + lower waste
     produces several-x more realized capacity per capita than modern
  7. Per-capita waste ratio is within [0,1]

Run: python tests/test_civilization.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distributional import (
    WasteBreakdown,
    CivilizationAudit,
    compare_eras,
    bronze_age_audit,
    renaissance_audit,
    modern_audit,
    capacity_fit_economy_audit,
)


def test_1_waste_breakdown_totals():
    print("\n--- TEST 1: WasteBreakdown totals ---")
    wb = WasteBreakdown(
        institutional_waste=0.1,
        forced_dependency_waste=0.2,
        labor_waste=0.15,
        potential_waste=0.05,
    )
    assert abs(wb.total_waste() - 0.5) < 1e-9
    print(f"  total: {wb.total_waste():.2f}")
    print("PASS")


def test_2_civilization_audit_math():
    print("\n--- TEST 2: per-capita and aggregate math ---")
    audit = CivilizationAudit(
        era_name="Test",
        population_size=1000,
        available_capacity_per_capita=1.0,
        realized_productive_capacity_per_capita=0.5,
        waste_per_capita=WasteBreakdown(0.1, 0.1, 0.1, 0.1),
    )
    assert audit.total_available_capacity() == 1000.0
    assert audit.total_realized_productive() == 500.0
    assert audit.total_waste() == 400.0  # 0.4 × 1000
    assert abs(audit.per_capita_waste_ratio() - 0.4) < 1e-9
    print(f"  available:  {audit.total_available_capacity():.0f}")
    print(f"  realized:   {audit.total_realized_productive():.0f}")
    print(f"  waste:      {audit.total_waste():.0f}")
    print(f"  waste ratio: {audit.per_capita_waste_ratio():.1%}")
    print("PASS")


def test_3_era_waste_ratios():
    print("\n--- TEST 3: era waste ratios ---")
    bronze = bronze_age_audit()
    renaissance = renaissance_audit()
    modern = modern_audit()
    fit = capacity_fit_economy_audit()
    print(f"  Bronze Age waste ratio:     "
          f"{bronze.per_capita_waste_ratio():.1%}")
    print(f"  Renaissance waste ratio:    "
          f"{renaissance.per_capita_waste_ratio():.1%}")
    print(f"  Modern waste ratio:         "
          f"{modern.per_capita_waste_ratio():.1%}")
    print(f"  Capacity-Fit waste ratio:   "
          f"{fit.per_capita_waste_ratio():.1%}")
    # modern should waste more than bronze age or renaissance
    assert modern.per_capita_waste_ratio() > bronze.per_capita_waste_ratio()
    assert modern.per_capita_waste_ratio() > renaissance.per_capita_waste_ratio()
    # fit should have lowest waste ratio per unit capacity
    assert fit.per_capita_waste_ratio() < modern.per_capita_waste_ratio()
    print("PASS")


def test_4_modern_realized_lower_than_bronze():
    """Per-capita realized capacity is lower in modern despite
    more tools, better tech, larger population."""
    print("\n--- TEST 4: modern realized < bronze age realized ---")
    bronze = bronze_age_audit()
    modern = modern_audit()
    print(f"  Bronze Age realized per capita:  "
          f"{bronze.realized_productive_capacity_per_capita:.2f}")
    print(f"  Modern realized per capita:      "
          f"{modern.realized_productive_capacity_per_capita:.2f}")
    ratio = (bronze.realized_productive_capacity_per_capita
             / modern.realized_productive_capacity_per_capita)
    print(f"  Bronze / Modern ratio:            {ratio:.2f}x")
    assert (modern.realized_productive_capacity_per_capita
            < bronze.realized_productive_capacity_per_capita)
    print("PASS — the innovation crisis is visible in the math")


def test_5_counterfactual_modern_with_renaissance_waste():
    print("\n--- TEST 5: counterfactual — modern at Renaissance waste ratio ---")
    renaissance = renaissance_audit()
    modern = modern_audit()
    counterfactual = modern.available_capacity_per_capita * (
        1.0 - renaissance.per_capita_waste_ratio()
    )
    delta = counterfactual - modern.realized_productive_capacity_per_capita
    print(f"  actual modern realized per capita: "
          f"{modern.realized_productive_capacity_per_capita:.2f}")
    print(f"  if modern had Renaissance waste:   {counterfactual:.2f}")
    print(f"  delta (capacity recoverable):      +{delta:.2f} per person")
    print(f"  across 8B people:                  +{delta * 8_000_000_000:,.0f} units")
    assert counterfactual > modern.realized_productive_capacity_per_capita
    print("PASS")


def test_6_capacity_fit_hypothetical():
    print("\n--- TEST 6: capacity-fit economy hypothetical ---")
    modern = modern_audit()
    fit = capacity_fit_economy_audit()
    print(f"  modern realized per capita:    "
          f"{modern.realized_productive_capacity_per_capita:.2f}")
    print(f"  capacity-fit realized per cap: "
          f"{fit.realized_productive_capacity_per_capita:.2f}")
    ratio = (fit.realized_productive_capacity_per_capita
             / modern.realized_productive_capacity_per_capita)
    print(f"  ratio:                         {ratio:.2f}x")
    delta_total = (fit.total_realized_productive()
                   - modern.total_realized_productive())
    print(f"  aggregate delta:               +{delta_total:,.0f} units/period")
    assert ratio > 3.0, "FAIL: capacity-fit should produce several-x modern"
    print("PASS")


def test_7_waste_ratio_bounded():
    print("\n--- TEST 7: waste ratio within [0, 1] ---")
    for audit in [bronze_age_audit(), renaissance_audit(),
                   modern_audit(), capacity_fit_economy_audit()]:
        wr = audit.per_capita_waste_ratio()
        print(f"  {audit.era_name:15s}: {wr:.2%}")
        assert 0.0 <= wr <= 1.0
    print("PASS")


def test_8_era_comparison_output():
    print("\n--- TEST 8: compare_eras output ---")
    bronze = bronze_age_audit()
    modern = modern_audit()
    text = compare_eras(bronze, modern)
    assert "Bronze Age" in text
    assert "Modern" in text
    assert "delta" in text.lower()
    print(text)
    print("PASS")


def test_9_four_era_summary():
    """Display the full picture: four eras side by side."""
    print("\n--- TEST 9: four-era summary ---")
    eras = [
        bronze_age_audit(),
        renaissance_audit(),
        modern_audit(),
        capacity_fit_economy_audit(),
    ]
    for audit in eras:
        print(f"\n{audit.summary_text()}")
    print("\n(no assertions — display only)")
    print("PASS")


if __name__ == "__main__":
    test_1_waste_breakdown_totals()
    test_2_civilization_audit_math()
    test_3_era_waste_ratios()
    test_4_modern_realized_lower_than_bronze()
    test_5_counterfactual_modern_with_renaissance_waste()
    test_6_capacity_fit_hypothetical()
    test_7_waste_ratio_bounded()
    test_8_era_comparison_output()
    test_9_four_era_summary()
    print("\nall civilization-scale audit tests passed.")
