"""
investment_signal/dimensions.py

Core dimensional types for the investment-as-signal framework.

Investment is modeled as substrate-of-self committed against
substrate-of-future. The seven substrates are the fungible-but-not-
equivalent carriers that can be invested and received as return.

Every investment is a vector across all seven substrates for input
and another vector across all seven substrates for output. Most
investments are sparse -- only a few substrates are nonzero.

Investment depends on money-signal. If money is in near-collapse or
recovering with heavy hysteresis, investment cannot function as
investment -- the time binding fails because the unit of account is
itself unstable. This module imports DimensionalContext from
money_signal to enforce that dependency.

CC0. Stdlib-only.
"""

from dataclasses import dataclass
from enum import Enum

# Investment inherits the full money-signal context because investment
# is money-plus-time. All money-signal dimensions apply to the money
# component of any investment analysis.
from ..money_signal.dimensions import DimensionalContext as MoneyContext


# ============================================================================
# INVESTMENT SUBSTRATES
# ============================================================================

class InvestmentSubstrate(Enum):
    """
    The seven substrates that can be invested or received as return.

    Each substrate has distinct thermodynamic and relational
    properties. They are fungible through conversion but not
    equivalent -- conversion is lossy and context-dependent.

    Conventional finance collapses all seven to MONEY, which is the
    primary measurement failure this framework exists to expose.
    """
    TIME = "time"                            # hours of life allocated
    RESOURCE = "resource"                    # physical material committed
    ENERGY = "energy"                        # work capacity (biological, thermal, electrical)
    LABOR = "labor"                          # applied skill and effort
    ATTENTION = "attention"                  # cognitive bandwidth
    MONEY = "money"                          # the multiplexed carrier from money_signal
    RELATIONAL_CAPITAL = "relational_capital"  # trust built up in a network


# ============================================================================
# INVESTMENT ATTRIBUTION
# ============================================================================

class InvestmentAttribution(Enum):
    """
    What the investor believes the investment represents.

    Analogous to AttributedValue in money_signal but with investment-
    specific categories. The same physical flow of substrates can be
    attributed differently by different investors, and the attribution
    changes the coupling dynamics.
    """
    PRODUCTIVE_CAPACITY = "productive_capacity"      # building something that produces in the future
    EXTRACTIVE_CLAIM = "extractive_claim"            # claim on future extraction from a substrate
    SPECULATIVE_BET = "speculative_bet"              # wagering on future price shifts
    RECIPROCAL_OBLIGATION = "reciprocal_obligation"  # gift/obligation cycles, indigenous reciprocity
    RENT_SEEKING = "rent_seeking"                    # positioning for toll extraction
    INSURANCE = "insurance"                          # paying now to hedge future substrate loss
    SPECULATION_ON_SPECULATION = "speculation_on_speculation"  # derivative of derivative, no underlying


# ============================================================================
# DERIVATIVE DISTANCE
# ============================================================================

class DerivativeDistance(Enum):
    """
    How many layers of abstraction sit between the investment and
    real substrate.

    Zero distance: direct ownership of productive substrate
    (farmland, tools, skills embodied in self).

    High distance: derivative of derivative of derivative, where the
    original substrate connection is so remote that the investment
    behaves independently of any physical reality.

    High derivative distance is where investment decouples from
    substrate coupling and becomes a different category of thing
    entirely.
    """
    DIRECT = "direct"                          # own the physical productive substrate
    ONE_LAYER = "one_layer"                    # equity, bond, direct claim on producer
    TWO_LAYER = "two_layer"                    # fund, index, claim on claims
    DERIVATIVE = "derivative"                  # option, future, claim on claim behavior
    SYNTHETIC = "synthetic"                    # claim with no underlying substrate link


# ============================================================================
# TIME BINDING
# ============================================================================

class TimeBinding(Enum):
    """
    The temporal commitment structure of the investment.

    Analogous to TemporalScope in money_signal but specifically for
    how the investment is bound to time, not for evaluation horizon.

    Short time binding with long realization horizon is a common
    failure pattern -- the investor can exit quickly but the
    substrate takes time to produce. This mismatch creates the
    liquidity-illusion dynamic of modern financial markets.
    """
    IMMEDIATE = "immediate"                  # return expected within days
    SHORT_CYCLE = "short_cycle"              # weeks to a quarter
    SEASONAL = "seasonal"                    # one growing/production cycle
    MULTI_YEAR = "multi_year"                # 2-10 years
    GENERATIONAL = "generational"            # 20+ years, inherited
    MULTI_GENERATIONAL = "multi_generational"  # knowledge/land across generations


# ============================================================================
# INVESTMENT CONTEXT
# ============================================================================

@dataclass(frozen=True)
class InvestmentContext:
    """
    The full dimensional context for an investment signal evaluation.

    Contains a complete MoneyContext plus investment-specific
    dimensions. Frozen so it can be used as a memoization key.

    The money_context is mandatory, not optional. Investment cannot
    be analyzed independently of the money state because time
    binding integrity depends on monetary stability. If money is in
    NEAR_COLLAPSE, the investment framework will flag that the
    investment cannot be evaluated as an investment -- it is
    effectively a bet against the monetary substrate.
    """
    money_context: MoneyContext
    attribution: InvestmentAttribution
    derivative_distance: DerivativeDistance
    time_binding: TimeBinding

    def describe(self) -> str:
        """Human-readable summary for debugging and logs."""
        return (
            f"[attribution={self.attribution.value}, "
            f"derivative_distance={self.derivative_distance.value}, "
            f"time_binding={self.time_binding.value}, "
            f"money={self.money_context.describe()}]"
        )


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    from ..money_signal.dimensions import (
        TemporalScope, CulturalScope, AttributedValue,
        ObserverPosition, Substrate, StateRegime,
    )

    # Example: a paycheck-to-paycheck worker putting money into a
    # retirement fund that is a claim on claims on claims
    # (401k -> mutual fund -> index -> underlying equities).
    example_money = MoneyContext(
        temporal=TemporalScope.GENERATIONAL,
        cultural=CulturalScope.ATOMIZED_MARKET,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.STRESSED,
    )

    example_investment = InvestmentContext(
        money_context=example_money,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.TWO_LAYER,
        time_binding=TimeBinding.GENERATIONAL,
    )

    print("Example investment context:")
    print(" ", example_investment.describe())
    print()

    # Substrate count sanity check.
    print(f"Investment substrates:    {len(InvestmentSubstrate)}")
    print(f"Investment attributions:  {len(InvestmentAttribution)}")
    print(f"Derivative distances:     {len(DerivativeDistance)}")
    print(f"Time bindings:            {len(TimeBinding)}")
    print()

    # Show all substrates.
    print("The seven substrates:")
    for s in InvestmentSubstrate:
        print(f"  - {s.value}")
