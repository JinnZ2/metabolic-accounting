"""
investment_signal/conversion_matrix.py

Conversion reliability matrix.

When an investor commits a substrate, that substrate must be
converted into the investment vehicle before it starts working as
investment. This conversion is lossy. The conversion matrix
C[in][vehicle] measures the fraction of the in-substrate that
actually arrives as the vehicle-substrate, in [0, 1].

Failure modes captured by this matrix:

  Labor misvalued: a worker invests 40 hours of skilled labor, but
  the measurement system prices it as unskilled, so only 60% of
  the labor value arrives as money-vehicle investment. C[LABOR][MONEY]
  = 0.6 for this worker.

  Attention extracted: a reader invests 2 hours of attention into
  a platform, but most is captured as ad revenue for the platform
  rather than reaching whatever the reader intended to invest in.
  C[ATTENTION][RELATIONAL_CAPITAL] might be 0.1 in such a system.

  Time stolen by administrative overhead: a farmer invests 400 hours
  into a crop, but 80 hours are consumed by regulatory paperwork
  that converts neither into the crop nor into anything else useful.
  C[TIME][RESOURCE] = 0.8.

  Energy lost in thermodynamically long conversion chains: biological
  energy converted to money requires labor markets, which have high
  loss rates. C[ENERGY][MONEY] is typically much lower than
  C[LABOR][MONEY] because energy must first become labor.

  Relational capital decaying under institutional frameworks: trust
  built in a community cannot be easily converted to money because
  the conversion destroys the thing being converted. C[RELATIONAL_CAPITAL]
  [MONEY] is low and conversion is often irreversible.

Conversion reliability is DISTINCT from realization reliability
(handled in realization_matrix.py). Conversion is "did the substrate
get into the vehicle at all?" Realization is "once in the vehicle,
did the expected return materialize?" Both fail, for different
reasons, and combining them loses information.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import InvestmentSubstrate


# ============================================================================
# CALIBRATION CASE
# ============================================================================
#
# The calibration case for conversion reliability is:
#
#   - Substrate-in flows to itself with reliability 1.0 (no conversion)
#   - Same-category substrates convert well
#   - Cross-category substrates convert lossily
#   - Substrates requiring relational knowledge convert poorly to
#     non-relational vehicles, and vice versa
#
# Substrate categories (informal):
#
#   Physical:     TIME, RESOURCE, ENERGY
#   Human-applied: LABOR, ATTENTION
#   Abstract:     MONEY
#   Relational:   RELATIONAL_CAPITAL
#
# Within-category conversion is more efficient than cross-category.


# ============================================================================
# BASE CONVERSION MATRIX
# ============================================================================

# C_BASE[in_substrate][vehicle_substrate] = fraction of in_substrate that
# arrives as vehicle_substrate under institutional/atomized-market
# calibration conditions.
#
# Diagonal (same substrate in and out) is 1.0 -- no conversion is needed.
# Off-diagonal values are the lossy conversion coefficients.

C_BASE: Dict[InvestmentSubstrate, Dict[InvestmentSubstrate, float]] = {

    # ----------------------------------------------------------------
    # TIME as input
    # Time converts to labor if applied skillfully, to energy if
    # applied physically, but cannot directly produce resource,
    # money, or relational capital without intermediate conversion.
    # ----------------------------------------------------------------
    InvestmentSubstrate.TIME: {
        InvestmentSubstrate.TIME: 1.0,
        InvestmentSubstrate.RESOURCE: 0.3,         # requires labor+energy to produce resource from time
        InvestmentSubstrate.ENERGY: 0.5,           # time can be directly metabolized as energy use
        InvestmentSubstrate.LABOR: 0.7,            # time readily becomes labor with applied skill
        InvestmentSubstrate.ATTENTION: 0.6,        # time enables attention, but attention is not the same
        InvestmentSubstrate.MONEY: 0.4,            # time-to-money has many intermediate loss points
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.5,  # time builds relational capital if applied relationally
    },

    # ----------------------------------------------------------------
    # RESOURCE as input
    # Physical material converts readily to itself and to energy
    # (thermodynamically), converts moderately to money (market
    # conversion), and converts poorly to labor, time, or attention
    # (requires agents, not just material).
    # ----------------------------------------------------------------
    InvestmentSubstrate.RESOURCE: {
        InvestmentSubstrate.TIME: 0.2,             # resource buys some time, but lossily
        InvestmentSubstrate.RESOURCE: 1.0,
        InvestmentSubstrate.ENERGY: 0.8,           # thermodynamic conversion is well-understood
        InvestmentSubstrate.LABOR: 0.3,
        InvestmentSubstrate.ATTENTION: 0.2,
        InvestmentSubstrate.MONEY: 0.7,            # resource-to-money conversion is mature
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.3,  # resource given as gift can build relation
    },

    # ----------------------------------------------------------------
    # ENERGY as input
    # Raw energy (kcal, kWh) is fundamental but bare energy without
    # applied skill converts poorly to higher-order vehicles.
    # ----------------------------------------------------------------
    InvestmentSubstrate.ENERGY: {
        InvestmentSubstrate.TIME: 0.3,
        InvestmentSubstrate.RESOURCE: 0.6,
        InvestmentSubstrate.ENERGY: 1.0,
        InvestmentSubstrate.LABOR: 0.6,            # energy becomes labor when skill is applied
        InvestmentSubstrate.ATTENTION: 0.3,        # energy enables attention but is not it
        InvestmentSubstrate.MONEY: 0.3,            # energy-to-money is lossy without labor layer
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.2,
    },

    # ----------------------------------------------------------------
    # LABOR as input
    # Applied skill and effort. Converts well to most vehicles when
    # labor markets function correctly. Calibration is against modern
    # institutional labor markets, which systematically undervalue
    # certain labor types -- this module does not correct for that
    # here; the observer factor in the coupling module does.
    # ----------------------------------------------------------------
    InvestmentSubstrate.LABOR: {
        InvestmentSubstrate.TIME: 0.2,             # labor cannot easily be converted back to free time
        InvestmentSubstrate.RESOURCE: 0.7,         # labor produces resource effectively
        InvestmentSubstrate.ENERGY: 0.4,           # labor is energy plus skill; reversing loses the skill
        InvestmentSubstrate.LABOR: 1.0,
        InvestmentSubstrate.ATTENTION: 0.4,
        InvestmentSubstrate.MONEY: 0.6,            # labor-to-money is institutional baseline
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.5,  # skilled labor in a community builds relation
    },

    # ----------------------------------------------------------------
    # ATTENTION as input
    # Cognitive bandwidth. Converts to labor and relational capital
    # well; converts poorly to physical substrates. Extraction is a
    # major failure mode: attention invested in commercial platforms
    # is often captured by the platform rather than reaching the
    # intended vehicle. This is the baseline; the state/substrate
    # context will modify it.
    # ----------------------------------------------------------------
    InvestmentSubstrate.ATTENTION: {
        InvestmentSubstrate.TIME: 0.2,
        InvestmentSubstrate.RESOURCE: 0.1,         # attention alone produces little physical material
        InvestmentSubstrate.ENERGY: 0.1,
        InvestmentSubstrate.LABOR: 0.5,            # attention becomes labor when directed to work
        InvestmentSubstrate.ATTENTION: 1.0,
        InvestmentSubstrate.MONEY: 0.3,            # attention is usually extracted before reaching money
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.6,  # attention invested relationally builds trust strongly
    },

    # ----------------------------------------------------------------
    # MONEY as input
    # The most fungible substrate in modern systems. Converts well
    # to most vehicles because institutional infrastructure exists
    # for every conversion. Does NOT convert well to relational
    # capital or to time in ways that reverse institutional
    # framing (e.g. cannot buy genuine trust or genuine unhurried
    # time in atomized markets).
    # ----------------------------------------------------------------
    InvestmentSubstrate.MONEY: {
        InvestmentSubstrate.TIME: 0.5,             # money buys time but institutional overhead eats a lot
        InvestmentSubstrate.RESOURCE: 0.8,         # money-to-resource conversion is mature
        InvestmentSubstrate.ENERGY: 0.7,
        InvestmentSubstrate.LABOR: 0.7,            # money readily hires labor
        InvestmentSubstrate.ATTENTION: 0.4,        # attention-as-sold is lossy relative to attention-as-given
        InvestmentSubstrate.MONEY: 1.0,
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.2,  # cannot purchase genuine trust -- low conversion
    },

    # ----------------------------------------------------------------
    # RELATIONAL_CAPITAL as input
    # Trust in a network. Converts to labor, attention, and (in
    # reciprocity systems) to resource and time through gift and
    # obligation cycles. Converts poorly to money because the
    # conversion destroys the thing being converted -- a relationship
    # monetized typically collapses.
    # ----------------------------------------------------------------
    InvestmentSubstrate.RELATIONAL_CAPITAL: {
        InvestmentSubstrate.TIME: 0.6,             # people give time to trusted others
        InvestmentSubstrate.RESOURCE: 0.5,         # gift economies transfer resource on relational basis
        InvestmentSubstrate.ENERGY: 0.4,
        InvestmentSubstrate.LABOR: 0.7,            # trusted communities cooperate readily
        InvestmentSubstrate.ATTENTION: 0.7,        # people attend to those they trust
        InvestmentSubstrate.MONEY: 0.2,            # monetizing a relationship tends to destroy it
        InvestmentSubstrate.RELATIONAL_CAPITAL: 1.0,
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def base_conversion(
    in_substrate: InvestmentSubstrate,
    vehicle_substrate: InvestmentSubstrate,
) -> float:
    """
    Return the base conversion reliability for converting
    in_substrate into vehicle_substrate.

    Returns a value in [0, 1]. 1.0 means perfect conversion;
    0.0 means the conversion is not possible in the baseline
    institutional framework.

    The base matrix assumes atomized-market cultural scope,
    institutional attribution, and healthy monetary state. Context
    modifiers applied in coupling.py will modify this value based
    on the full InvestmentContext.
    """
    return C_BASE[in_substrate][vehicle_substrate]


def iter_base_conversion() -> Tuple[
    Tuple[InvestmentSubstrate, InvestmentSubstrate, float], ...
]:
    """Iterate over all (in_substrate, vehicle_substrate, reliability) triples."""
    return tuple(
        (i, j, C_BASE[i][j])
        for i in InvestmentSubstrate
        for j in InvestmentSubstrate
    )


# ============================================================================
# APPLYING CONVERSION TO A SUBSTRATE VECTOR
# ============================================================================

def apply_conversion(
    input_vec,  # SubstrateVector; imported below to avoid circular import
    vehicle_substrate: InvestmentSubstrate,
) -> float:
    """
    Apply the conversion matrix to an input substrate vector to
    compute how much of the vehicle_substrate arrives as investment.

    Returns the total magnitude of vehicle_substrate produced by
    converting each component of input_vec through C_BASE.

    Units are in the vehicle_substrate's native unit. The caller is
    responsible for ensuring this unit makes sense for downstream
    use.

    Imports SubstrateVector lazily to avoid circular imports. This
    is the only function in this module that needs the vector type.
    """
    from .substrate_vectors import SubstrateVector
    assert isinstance(input_vec, SubstrateVector), (
        f"apply_conversion expected SubstrateVector, got {type(input_vec).__name__}"
    )

    total = 0.0
    for in_sub, magnitude in input_vec.components:
        if magnitude == 0.0:
            continue
        reliability = C_BASE[in_sub][vehicle_substrate]
        total += magnitude * reliability
    return total


def apply_conversion_to_vector(
    input_vec,  # SubstrateVector
):
    """
    Convert an input substrate vector into the full vector of
    potential vehicle substrates.

    For each of the seven possible vehicle substrates, computes how
    much of that substrate would arrive if the entire input vector
    were converted to that vehicle.

    Returns a new SubstrateVector.

    This is useful for asking: "If an investor commits this input
    bundle, what is the maximum vehicle substrate they can produce
    in each possible vehicle?"
    """
    from .substrate_vectors import SubstrateVector
    result = {
        vehicle: apply_conversion(input_vec, vehicle)
        for vehicle in InvestmentSubstrate
    }
    return SubstrateVector.from_dict(result)


# ============================================================================
# VALIDATION
# ============================================================================

def validate_conversion_matrix() -> None:
    """
    Check structural invariants for the base conversion matrix.

    Raises AssertionError on violation.
    """
    # 1. Every substrate must have a full row of 7 conversion values.
    for in_sub in InvestmentSubstrate:
        assert in_sub in C_BASE, (
            f"Missing conversion row for {in_sub.value}"
        )
        for out_sub in InvestmentSubstrate:
            assert out_sub in C_BASE[in_sub], (
                f"Missing conversion C[{in_sub.value}][{out_sub.value}]"
            )

    # 2. Diagonal entries must be exactly 1.0.
    #    Same-substrate conversion is no conversion at all.
    for sub in InvestmentSubstrate:
        v = C_BASE[sub][sub]
        assert v == 1.0, (
            f"Self-conversion C[{sub.value}][{sub.value}] must be 1.0, "
            f"got {v}"
        )

    # 3. All conversion reliabilities must be in [0, 1].
    for in_sub in InvestmentSubstrate:
        for out_sub in InvestmentSubstrate:
            v = C_BASE[in_sub][out_sub]
            assert 0.0 <= v <= 1.0, (
                f"Conversion C[{in_sub.value}][{out_sub.value}] = {v} "
                f"outside [0, 1]"
            )

    # 4. Monetizing relational capital must be low.
    #    This encodes the claim that monetizing a relationship tends
    #    to destroy it. If someone edits C_BASE to make this high,
    #    the test fails loud.
    assert C_BASE[InvestmentSubstrate.RELATIONAL_CAPITAL][InvestmentSubstrate.MONEY] <= 0.3, (
        "Monetizing relational capital must have low conversion reliability; "
        "the conversion destroys the thing being converted"
    )

    # 5. Money cannot efficiently purchase genuine relational capital.
    #    Symmetric to the above -- you cannot buy trust in atomized markets.
    assert C_BASE[InvestmentSubstrate.MONEY][InvestmentSubstrate.RELATIONAL_CAPITAL] <= 0.3, (
        "Money-to-relational-capital conversion must be low; "
        "genuine trust is not purchasable in the institutional default"
    )

    # 6. Attention extraction: attention-to-money is low because
    #    attention is usually captured by intermediaries before it
    #    reaches any vehicle the investor intended.
    assert C_BASE[InvestmentSubstrate.ATTENTION][InvestmentSubstrate.MONEY] <= 0.4, (
        "Attention-to-money conversion must be low; "
        "attention is typically extracted by intermediaries"
    )

    # 7. Thermodynamic conversions (resource-to-energy, energy-to-resource)
    #    must be reasonably efficient, reflecting that these are
    #    well-understood physical processes.
    assert C_BASE[InvestmentSubstrate.RESOURCE][InvestmentSubstrate.ENERGY] >= 0.6, (
        "Resource-to-energy conversion is a mature thermodynamic process "
        "and must be >= 0.6 in the base matrix"
    )


# ============================================================================
# DISPLAY
# ============================================================================

def format_conversion_matrix() -> str:
    """
    Return a human-readable string of the base conversion matrix.

    Rows are input substrates, columns are vehicle substrates.
    Entry [i][j] is the fraction of input substrate i that arrives
    as vehicle substrate j.
    """
    substrates = list(InvestmentSubstrate)
    # Short labels for compact display.
    labels = {
        InvestmentSubstrate.TIME: "TIM",
        InvestmentSubstrate.RESOURCE: "RES",
        InvestmentSubstrate.ENERGY: "ENE",
        InvestmentSubstrate.LABOR: "LAB",
        InvestmentSubstrate.ATTENTION: "ATT",
        InvestmentSubstrate.MONEY: "MON",
        InvestmentSubstrate.RELATIONAL_CAPITAL: "REL",
    }
    header = "         " + "  ".join(f"{labels[s]:>5}" for s in substrates)
    lines = [
        "Base conversion matrix C[in][vehicle]:",
        header,
        "         " + "-" * (7 * len(substrates)),
    ]
    for in_sub in substrates:
        row = f"{labels[in_sub]:>6} |"
        for vehicle in substrates:
            row += f"  {C_BASE[in_sub][vehicle]:.2f}"
        lines.append(row)
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    from .substrate_vectors import SubstrateVector

    validate_conversion_matrix()
    print("Conversion matrix validated.")
    print()
    print(format_conversion_matrix())
    print()

    # Case A: farmer converting mixed inputs into MONEY vehicle.
    farmer_in = SubstrateVector.from_dict({
        InvestmentSubstrate.TIME: 400.0,
        InvestmentSubstrate.RESOURCE: 50.0,
        InvestmentSubstrate.ENERGY: 8000.0,
        InvestmentSubstrate.LABOR: 400.0,
    })
    money_arriving = apply_conversion(farmer_in, InvestmentSubstrate.MONEY)
    print(f"Farmer committing {farmer_in.describe()}")
    print(f"  -> vehicle MONEY arrives as: {money_arriving:.1f}")
    print(f"  (units are the input substrates' native units weighted by C_BASE)")
    print()

    # Case B: attention-heavy investor (reader of free content).
    reader_in = SubstrateVector.from_dict({
        InvestmentSubstrate.ATTENTION: 100.0,
        InvestmentSubstrate.TIME: 100.0,
    })
    money_from_reader = apply_conversion(reader_in, InvestmentSubstrate.MONEY)
    relational_from_reader = apply_conversion(
        reader_in, InvestmentSubstrate.RELATIONAL_CAPITAL
    )
    print(f"Reader committing {reader_in.describe()}")
    print(f"  -> vehicle MONEY arrives as:               {money_from_reader:.1f}")
    print(f"  -> vehicle RELATIONAL_CAPITAL arrives as:  {relational_from_reader:.1f}")
    print(f"  (attention-to-money is extracted; attention-to-relational is preserved)")
    print()

    # Case C: full conversion vector for the farmer input.
    farmer_full_conversion = apply_conversion_to_vector(farmer_in)
    print(f"Farmer full conversion across all vehicles:")
    print(f"  {farmer_full_conversion}")
