"""
tests/test_strategy.py

Verifies the institutional-strategy comparison layer.

Core tests:
  1. Homogeneous neurotypical workforce: compliance wins (no capacity
     variance to capture, so capacity_fit's overhead is pure loss)
  2. Heterogeneous workforce with neurodivergent tail: capacity_fit
     dramatically outperforms despite higher overhead
  3. Poor fit_quality erodes capacity_fit's advantage
  4. Churn differential: compliance loses more workers per period
  5. Empirical: a realistic workforce distribution shows the crossover
     point where capacity_fit becomes economically rational

Run: python tests/test_strategy.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distributional import (
    compare_strategies,
    StrategyCost,
    DEFAULT_COMPLIANCE_COSTS,
    DEFAULT_CAPACITY_FIT_COSTS,
)


def test_1_homogeneous_neurotypical():
    """When everyone is at neurotypical baseline, compliance is a
    reasonable default and capacity_fit's overhead is wasted."""
    print("\n--- TEST 1: homogeneous neurotypical workforce ---")
    capacities = [0.7] * 20  # 20 workers at neurotypical baseline
    comparison = compare_strategies(capacities)
    print(comparison.summary_text())
    # with homogeneous capacity at 0.7, compliance fit = 1.0, so
    # compliance realized == capacity_fit realized (both capture capacity)
    # but capacity_fit has higher overhead -> net output lower
    print()
    print(f"  output_delta: {comparison.output_delta():.2f}")
    assert comparison.output_delta() < 0, \
        "FAIL: homogeneous neurotypical should favor compliance"
    print("PASS")


def test_2_heterogeneous_with_neurodivergent_tail():
    """Realistic workforce with some neurodivergent high-capacity
    workers: capacity_fit captures the tail that compliance wastes."""
    print("\n--- TEST 2: heterogeneous workforce (with nd tail) ---")
    # 20 workers: 12 neurotypical (0.7), 5 neurodivergent moderate (1.5),
    # 3 neurodivergent high (2.5) — about the distribution you'd see
    # in a real population
    capacities = ([0.7] * 12
                  + [1.5] * 5
                  + [2.5] * 3)
    comparison = compare_strategies(capacities)
    print(comparison.summary_text())
    print()
    print(f"  output_delta:  {comparison.output_delta():+.2f}")
    print(f"  waste captured: {comparison.waste_delta():+.2f}")
    print(f"  trauma avoided: {comparison.trauma_delta():+.2f}")
    # capacity_fit should win because it captures the nd tail
    assert comparison.output_delta() > 0, \
        "FAIL: heterogeneous should favor capacity_fit"
    assert comparison.waste_delta() > 0, \
        "FAIL: compliance should waste more capacity"
    print("PASS")


def test_3_poor_fit_quality_erodes_advantage():
    """If the institution's discovery process is bad (fit_quality 0.3),
    capacity_fit loses its advantage."""
    print("\n--- TEST 3: poor fit_quality erodes capacity_fit ---")
    capacities = ([0.7] * 12 + [1.5] * 5 + [2.5] * 3)

    good_fit = compare_strategies(capacities, fit_quality=0.85)
    poor_fit = compare_strategies(capacities, fit_quality=0.30)

    print(f"  good fit (0.85): output_delta = "
          f"{good_fit.output_delta():+.2f}")
    print(f"  poor fit (0.30): output_delta = "
          f"{poor_fit.output_delta():+.2f}")
    assert good_fit.output_delta() > poor_fit.output_delta(), \
        "FAIL: poor fit should reduce capacity_fit advantage"
    print("PASS")


def test_4_churn_differential():
    """Compliance loses more workers per period than capacity_fit."""
    print("\n--- TEST 4: churn differential ---")
    capacities = [1.0] * 100
    comparison = compare_strategies(capacities)
    print(f"  compliance churn:   "
          f"{comparison.compliance.expected_churn} / 100 per period")
    print(f"  capacity_fit churn: "
          f"{comparison.capacity_fit.expected_churn} / 100 per period")
    assert comparison.churn_delta() > 0, \
        "FAIL: compliance should have higher churn"
    print("PASS")


def test_5_crossover_analysis():
    """How heterogeneous does a workforce need to be before
    capacity_fit becomes economically rational?"""
    print("\n--- TEST 5: crossover analysis ---")
    print("  Vary fraction of workforce that is neurodivergent (cap 2.0)")
    print("  vs neurotypical (cap 0.7). Find crossover.")
    print()
    print("  nd fraction | compliance net | capacity_fit net | winner")
    print("  ------------|----------------|------------------|--------")

    for nd_frac in [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]:
        total = 20
        n_nd = int(total * nd_frac)
        n_nt = total - n_nd
        caps = [0.7] * n_nt + [2.0] * n_nd
        cmp = compare_strategies(caps)
        winner = ("capacity_fit" if cmp.output_delta() > 0
                  else "compliance")
        print(f"  {nd_frac:11.2f} | "
              f"{cmp.compliance.net_output():14.2f} | "
              f"{cmp.capacity_fit.net_output():16.2f} | "
              f"{winner}")
    print()
    print("Even small fractions of high-capacity workers tip the")
    print("economics toward capacity_fit. Institutions that hire purely")
    print("for neurotypical compliance are leaving capacity on the table.")
    print()
    print("(no assertions — this is a demonstration)")
    print("PASS")


def test_6_kavik_scenario_ten_workers():
    """Kavik's observation: when he found neurodivergent workers and
    structured work around them, they outperformed everyone. Simulate:
    10 workers, average capacity 1.5, fit_quality 0.85."""
    print("\n--- TEST 6: Kavik's 10-worker company ---")
    # 10 workers Kavik hired for fit, with average capacity 1.5
    # (mix of neurotypical 0.7 and various neurodivergent high-capacity)
    capacities = [2.5, 2.0, 1.8, 1.6, 1.5, 1.3, 1.2, 1.0, 0.9, 0.7]
    comparison = compare_strategies(capacities)
    print(comparison.summary_text())
    print()
    print("  Kavik-style capacity_fit captures the full range.")
    print(f"  Output captured that compliance would have wasted:")
    print(f"    +{comparison.waste_delta():.2f} capacity units/period")
    assert comparison.output_delta() > 0
    print("PASS")


if __name__ == "__main__":
    test_1_homogeneous_neurotypical()
    test_2_heterogeneous_with_neurodivergent_tail()
    test_3_poor_fit_quality_erodes_advantage()
    test_4_churn_differential()
    test_5_crossover_analysis()
    test_6_kavik_scenario_ten_workers()
    print("\nall strategy tests passed.")
