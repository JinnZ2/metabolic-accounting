"""
money_signal/dimensions.py

Core dimensional types for the money-as-signal framework.

Every coupling coefficient K_ij in this framework is a function of:
  - temporal scope
  - cultural scope
  - attributed value
  - observer position
  - substrate
  - state regime

This module defines those dimensions as explicit enums. Nothing here
computes anything. These are the parameter spaces that the coupling
functions live in.

CC0. Stdlib-only.
"""

from dataclasses import dataclass
from enum import Enum


# ============================================================================
# SCOPE DIMENSIONS
# ============================================================================

class TemporalScope(Enum):
    """
    The time horizon over which the money signal is being evaluated.

    A token that is stable at TRANSACTION scope may be catastrophically
    unstable at GENERATIONAL scope. Scope mismatch is the core failure
    mode in monetary modeling.
    """
    TRANSACTION = "transaction"      # seconds to days
    SEASONAL = "seasonal"            # weeks to ~1 year
    GENERATIONAL = "generational"    # ~20-30 years, one human generation
    EPOCHAL = "epochal"              # centuries, civilizational timescale


class CulturalScope(Enum):
    """
    The cultural substrate of the network using the token.

    The same token in two different cultural contexts has different
    coupling dynamics. A fiat dollar in a high-reciprocity indigenous
    network couples differently than in an atomized consumer market.

    This is NOT the substrate of the token itself (see Substrate enum).
    This is the substrate of the social network USING the token.
    """
    HIGH_RECIPROCITY = "high_reciprocity"      # kin/gift economies, strong obligation networks
    COMMUNITY_TRUST = "community_trust"        # small-scale, face-to-face accountability
    INSTITUTIONAL = "institutional"            # formal enforcement, contract-based
    ATOMIZED_MARKET = "atomized_market"        # transactional, low relational binding
    MIXED = "mixed"                            # heterogeneous network, multiple modes


class AttributedValue(Enum):
    """
    What the culture using the token BELIEVES the token represents.

    Attribution changes behavior. Behavior changes coupling. Two tokens
    with identical physical and institutional properties can have
    different coupling signatures if the attributed value differs.
    """
    LABOR_STORED = "labor_stored"              # hours-of-work, sweat equity
    COMMODITY_BACKED = "commodity_backed"      # gold, silver, physical scarce
    STATE_ENFORCED = "state_enforced"          # fiat, legal tender
    NETWORK_AGREED = "network_agreed"          # crypto, community currency
    RECIPROCITY_TOKEN = "reciprocity_token"    # gift economies, trust-ledger
    DIVINE_SANCTIONED = "divine_sanctioned"    # temple economies, sacred obligation
    SPECULATIVE_CLAIM = "speculative_claim"    # pure financialization, no underlying


class ObserverPosition(Enum):
    """
    WHOSE measurement of M(t) is being computed.

    Money is observer-relative. A billionaire and a minimum-wage worker
    are not measuring the same signal even when they hold nominally
    identical tokens. Encoding observer position as a scope parameter
    makes this formal rather than implicit.

    Most conventional monetary modeling collapses to a single observer
    (aggregate, central bank, "the economy"). That collapse is itself
    a measurement failure.
    """
    SUBSTRATE_PRODUCER = "substrate_producer"      # makes the physical goods
    SUBSTRATE_CONSUMER = "substrate_consumer"      # uses the physical goods
    TOKEN_HOLDER_DEEP = "token_holder_deep"        # deep reserves, long horizon
    TOKEN_HOLDER_THIN = "token_holder_thin"        # paycheck-to-paycheck, short horizon
    TOKEN_ISSUER = "token_issuer"                  # state, central bank, protocol
    TOKEN_INTERMEDIARY = "token_intermediary"      # banks, exchanges, clearinghouses


# ============================================================================
# SUBSTRATE DIMENSION
# ============================================================================

class Substrate(Enum):
    """
    The physical or informational substrate of the token itself.

    Each substrate has distinct failure modes. Shells cannot be
    counterfeited at scale but can be inflated by discovery. Digital
    tokens cannot be inflated by discovery but can be terminated by
    infrastructure collapse. The coupling matrix reflects these
    differences.
    """
    BIOLOGICAL = "biological"      # shells, rare organic materials
    METAL = "metal"                # gold, silver, specie coinage
    PAPER = "paper"                # printed fiat, bearer notes
    DIGITAL = "digital"            # modern fiat ledgers, crypto
    TRUST_LEDGER = "trust_ledger"  # hawala, indigenous reciprocity networks


# ============================================================================
# STATE DIMENSION
# ============================================================================

class StateRegime(Enum):
    """
    The current dynamic regime of the monetary system.

    Coupling coefficients shift based on where the system currently is.
    The RECOVERING regime is distinct from HEALTHY because of hysteresis:
    post-collapse systems do not return to pre-collapse coupling even
    after nominal metrics recover. Trust rebuilds slower than it
    collapsed. Scar tissue remains.
    """
    HEALTHY = "healthy"                # base coupling applies
    STRESSED = "stressed"              # off-diagonals amplify, margins thin
    NEAR_COLLAPSE = "near_collapse"    # nonlinear regime, coupling may flip sign
    RECOVERING = "recovering"          # damped coupling, hysteresis, scar tissue


# ============================================================================
# TERM DIMENSION
# ============================================================================

class MoneyTerm(Enum):
    """
    The four terms of the money signal equation.

    M(t) couples these four terms via the K matrix. This enum exists
    so coupling coefficients can be indexed by name rather than integer,
    which prevents sign-flip bugs when reading K[i][j].
    """
    R = "reversal_reliability"     # probability of successful re-exchange
    N = "network_acceptance"       # fraction of network that will accept
    C = "cost_of_reversal"         # fraction of value lost to reverse
    L = "latency_of_reversal"      # time to complete re-exchange


# ============================================================================
# DIMENSIONAL CONTEXT
# ============================================================================

@dataclass(frozen=True)
class DimensionalContext:
    """
    The full dimensional context for a money signal evaluation.

    Every call to compute M(t) or any coupling coefficient K_ij must
    provide this context. No defaults. Scope mismatch is the core
    failure mode, so the framework forces scope to be declared.

    Frozen so contexts can be used as dict keys for memoization.
    """
    temporal: TemporalScope
    cultural: CulturalScope
    attribution: AttributedValue
    observer: ObserverPosition
    substrate: Substrate
    state: StateRegime

    def describe(self) -> str:
        """Human-readable summary for debugging and logs."""
        return (
            f"[temporal={self.temporal.value}, "
            f"cultural={self.cultural.value}, "
            f"attribution={self.attribution.value}, "
            f"observer={self.observer.value}, "
            f"substrate={self.substrate.value}, "
            f"state={self.state.value}]"
        )


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    # Example: a paycheck-to-paycheck worker holding US fiat dollars
    # in an atomized market, at transaction scope, in a stressed regime.
    example = DimensionalContext(
        temporal=TemporalScope.TRANSACTION,
        cultural=CulturalScope.ATOMIZED_MARKET,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_THIN,
        substrate=Substrate.DIGITAL,
        state=StateRegime.STRESSED,
    )
    print("Example context:")
    print(" ", example.describe())

    # Enum counts as sanity check
    print(f"\nTemporal scopes:   {len(TemporalScope)}")
    print(f"Cultural scopes:   {len(CulturalScope)}")
    print(f"Attributed values: {len(AttributedValue)}")
    print(f"Observer positions:{len(ObserverPosition)}")
    print(f"Substrates:        {len(Substrate)}")
    print(f"State regimes:     {len(StateRegime)}")
    print(f"Money terms:       {len(MoneyTerm)}")
