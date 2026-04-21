"""
investment_signal/realization_matrix.py

Realization reliability matrix.

Once an investor's substrate has been converted into the investment
vehicle, a second question arises: will the expected return
substrate actually materialize? The realization matrix R[vehicle]
[return] measures the probability that the expected return arrives
in a usable form, conditional on the vehicle being in the claimed
state.

Failure modes captured by this matrix:

  Vehicle functions correctly but return does not materialize: the
  farm produces the crop (vehicle works), but the expected monetary
  return is absent because the market for the crop collapsed.
  R[RESOURCE][MONEY] = low in such a context.

  Return arrives in a substrate the investor cannot use: an
  investment produces RELATIONAL_CAPITAL but the investor needed
  MONEY for rent. The return realized, but not in the substrate
  that matters to the investor.

  Return arrives degraded: the crop is harvested but storage losses
  reduce usable resource. The vehicle delivered, but realization
  was partial.

  Return is mathematically realized but physically unavailable: a
  retirement fund "earns" a nominal return, but by the time the
  investor can access it, inflation has degraded the time and
  resource purchasing power. Nominal realization ≠ substrate
  realization.

Realization reliability is DISTINCT from conversion reliability
(conversion_matrix.py). Conversion asks "did the investment go in
at all?" Realization asks "once in, did the expected return come
out?" Both fail, for different reasons, with different remedies.

The matrix R[vehicle][return] tells you the probability that a
unit of vehicle produces a unit of the expected return substrate,
in the baseline institutional case. Context modifiers in the
coupling module will adjust these values based on full
InvestmentContext.

CC0. Stdlib-only.
"""

from typing import Dict, Tuple
from .dimensions import InvestmentSubstrate


# ============================================================================
# CALIBRATION CASE
# ============================================================================
#
# The base realization matrix assumes:
#
#   - Institutional market structure (the calibration case)
#   - Healthy monetary state
#   - Derivative distance of at most one layer
#   - Time binding matched to substrate natural cycle
#
# Any deviation from these defaults will modify the realization
# reliability through the coupling module.
#
# Baseline expectations encoded here:
#
#   Same-substrate realization is high but NOT 1.0. Even holding
#   the same substrate has attrition from storage, spoilage, decay,
#   opportunity cost.
#
#   Cross-substrate realization is lower than conversion. It is
#   easier to commit a substrate to a vehicle than it is for that
#   vehicle to then produce a different substrate as return.
#
#   Physical-to-abstract returns (RESOURCE→MONEY, LABOR→MONEY) are
#   well-established baseline paths with moderate-high realization.
#
#   Abstract-to-physical returns (MONEY→RESOURCE, MONEY→TIME) are
#   typically high in institutional markets because the
#   infrastructure exists for these conversions on exit.
#
#   Relational returns and relational sources are institutionally
#   discounted and have low baseline realization against abstract
#   or physical vehicles.


# ============================================================================
# BASE REALIZATION MATRIX
# ============================================================================

# R_BASE[vehicle_substrate][return_substrate] = probability that one
# unit of vehicle_substrate produces one unit of return_substrate
# as realized return, in the calibration case.
#
# Diagonal is high but not 1.0 -- substrates decay, spoil, or lose
# value even in their own native form over the investment period.
#
# Off-diagonal values are the realization coefficients for
# cross-substrate return paths.

R_BASE: Dict[InvestmentSubstrate, Dict[InvestmentSubstrate, float]] = {

    # ----------------------------------------------------------------
    # Vehicle: TIME
    # Time as vehicle (e.g., sabbatical, deliberate slow-down) rarely
    # produces institutional returns; returns are typically relational
    # or attentional. Time-as-vehicle returning as money is the
    # most institutionally suspect path -- "time off" and "money earned"
    # are framed as opposites.
    # ----------------------------------------------------------------
    InvestmentSubstrate.TIME: {
        InvestmentSubstrate.TIME: 0.9,             # rested time compounds on further time
        InvestmentSubstrate.RESOURCE: 0.2,         # time alone rarely produces physical resource
        InvestmentSubstrate.ENERGY: 0.5,           # rested time restores energy
        InvestmentSubstrate.LABOR: 0.4,            # restored time improves future labor quality
        InvestmentSubstrate.ATTENTION: 0.7,        # time recovers attention strongly
        InvestmentSubstrate.MONEY: 0.1,            # time-off rarely monetizes in institutional framing
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.6,  # time with others builds relation
    },

    # ----------------------------------------------------------------
    # Vehicle: RESOURCE
    # Physical capital. Resource vehicles realize back into resource,
    # energy, and money well. They realize poorly into time, attention,
    # and relational capital -- those require human agency, not just
    # material.
    # ----------------------------------------------------------------
    InvestmentSubstrate.RESOURCE: {
        InvestmentSubstrate.TIME: 0.3,             # resource frees up some time
        InvestmentSubstrate.RESOURCE: 0.85,        # storage and spoilage losses
        InvestmentSubstrate.ENERGY: 0.7,           # resource becomes energy thermodynamically
        InvestmentSubstrate.LABOR: 0.2,            # resource does not become labor directly
        InvestmentSubstrate.ATTENTION: 0.1,
        InvestmentSubstrate.MONEY: 0.6,            # resource sells, with market frictions
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.2,
    },

    # ----------------------------------------------------------------
    # Vehicle: ENERGY
    # Raw energy in the investment vehicle (stored fuel, charged
    # batteries, biological reserve) realizes back into energy with
    # storage losses, into resource through work application, and
    # into money through energy markets.
    # ----------------------------------------------------------------
    InvestmentSubstrate.ENERGY: {
        InvestmentSubstrate.TIME: 0.2,
        InvestmentSubstrate.RESOURCE: 0.5,         # energy applied produces resource
        InvestmentSubstrate.ENERGY: 0.7,           # energy storage is lossy
        InvestmentSubstrate.LABOR: 0.5,            # energy powers labor
        InvestmentSubstrate.ATTENTION: 0.2,
        InvestmentSubstrate.MONEY: 0.4,            # energy markets exist but are thin per-unit
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.1,
    },

    # ----------------------------------------------------------------
    # Vehicle: LABOR
    # Applied skill in the vehicle (a working business, a
    # cooperative, a skilled team) realizes well into resource,
    # money, and relational capital. Realizes poorly into time --
    # running a labor-vehicle typically consumes time rather than
    # restoring it.
    # ----------------------------------------------------------------
    InvestmentSubstrate.LABOR: {
        InvestmentSubstrate.TIME: 0.1,             # labor vehicles consume time
        InvestmentSubstrate.RESOURCE: 0.7,         # labor produces resource reliably
        InvestmentSubstrate.ENERGY: 0.3,
        InvestmentSubstrate.LABOR: 0.8,            # labor compounds into more skilled labor
        InvestmentSubstrate.ATTENTION: 0.4,
        InvestmentSubstrate.MONEY: 0.7,            # labor-vehicle-to-money is institutional baseline
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.6,  # cooperative labor builds relation
    },

    # ----------------------------------------------------------------
    # Vehicle: ATTENTION
    # Attention as vehicle means the investment is held in mindful
    # focus -- studying, maintaining relationships, tending to
    # something actively. Realizes well into labor, attention, and
    # relational capital. Realizes poorly into physical substrates
    # without mediating labor.
    # ----------------------------------------------------------------
    InvestmentSubstrate.ATTENTION: {
        InvestmentSubstrate.TIME: 0.3,             # attention paid well returns clarity, freeing time later
        InvestmentSubstrate.RESOURCE: 0.2,
        InvestmentSubstrate.ENERGY: 0.2,
        InvestmentSubstrate.LABOR: 0.6,            # attention becomes skilled labor over time
        InvestmentSubstrate.ATTENTION: 0.8,        # attended things deepen attention
        InvestmentSubstrate.MONEY: 0.3,            # attention rarely monetizes without an intermediary
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.7,  # attended relationships compound
    },

    # ----------------------------------------------------------------
    # Vehicle: MONEY
    # Money as vehicle is the institutional baseline. Realizes well
    # into money (interest/return on capital) and into most
    # substrates through market purchase at realization time.
    # Realizes poorly into relational capital and into genuine time
    # restoration. These are the institutional blind spots.
    # ----------------------------------------------------------------
    InvestmentSubstrate.MONEY: {
        InvestmentSubstrate.TIME: 0.3,             # money buys time institutionally but with overhead
        InvestmentSubstrate.RESOURCE: 0.7,         # money buys resource at exit
        InvestmentSubstrate.ENERGY: 0.6,
        InvestmentSubstrate.LABOR: 0.7,            # money hires labor at exit
        InvestmentSubstrate.ATTENTION: 0.3,        # money rarely buys genuine attention
        InvestmentSubstrate.MONEY: 0.9,            # nominal return is easy; real value is another question
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.1,  # money rarely produces genuine trust
    },

    # ----------------------------------------------------------------
    # Vehicle: RELATIONAL_CAPITAL
    # Trust and relationship as vehicle. Realizes very well into
    # other relational, attentional, and labor returns because the
    # network cooperates. Realizes modestly into resource and money
    # through reciprocity flows. Does NOT realize strongly into
    # time, energy, or attention extraction.
    #
    # Critically: relational vehicles have realization reliability
    # that matches or exceeds money vehicles for many return
    # substrates, even though institutional accounting cannot see
    # the flows. This is one of the framework's main falsifiable
    # claims.
    # ----------------------------------------------------------------
    InvestmentSubstrate.RELATIONAL_CAPITAL: {
        InvestmentSubstrate.TIME: 0.6,             # community covers each other's time needs
        InvestmentSubstrate.RESOURCE: 0.6,         # reciprocity delivers resource reliably
        InvestmentSubstrate.ENERGY: 0.5,
        InvestmentSubstrate.LABOR: 0.8,            # trusted networks work together
        InvestmentSubstrate.ATTENTION: 0.8,        # trusted others pay attention in return
        InvestmentSubstrate.MONEY: 0.3,            # relational-to-money is lossy; monetizing destroys trust
        InvestmentSubstrate.RELATIONAL_CAPITAL: 0.95,  # relational capital compounds strongly
    },
}


# ============================================================================
# ACCESS FUNCTIONS
# ============================================================================

def base_realization(
    vehicle_substrate: InvestmentSubstrate,
    return_substrate: InvestmentSubstrate,
) -> float:
    """
    Return the base realization reliability for a vehicle_substrate
    producing return_substrate as the realized return.

    Returns a value in [0, 1]. 1.0 means certain realization;
    0.0 means the return path is not realizable in the baseline
    institutional framework.

    The base matrix assumes institutional cultural scope, healthy
    monetary state, at most one derivative layer, and matched
    time binding. Context modifiers in coupling.py modify this.
    """
    return R_BASE[vehicle_substrate][return_substrate]


def iter_base_realization() -> Tuple[
    Tuple[InvestmentSubstrate, InvestmentSubstrate, float], ...
]:
    """Iterate over all (vehicle, return, reliability) triples."""
    return tuple(
        (v, r, R_BASE[v][r])
        for v in InvestmentSubstrate
        for r in InvestmentSubstrate
    )


# ============================================================================
# APPLYING REALIZATION TO A VEHICLE VECTOR
# ============================================================================

def apply_realization(
    vehicle_vec,  # SubstrateVector; imported lazily below
    return_substrate: InvestmentSubstrate,
) -> float:
    """
    Apply the realization matrix to a vehicle vector to compute
    how much of return_substrate is realized as return.

    Returns the total magnitude of return_substrate produced by
    realizing each component of the vehicle vector through R_BASE.

    Units are in the return_substrate's native unit. The caller is
    responsible for unit consistency.
    """
    from .substrate_vectors import SubstrateVector
    assert isinstance(vehicle_vec, SubstrateVector), (
        f"apply_realization expected SubstrateVector, got {type(vehicle_vec).__name__}"
    )

    total = 0.0
    for vehicle, magnitude in vehicle_vec.components:
        if magnitude == 0.0:
            continue
        reliability = R_BASE[vehicle][return_substrate]
        total += magnitude * reliability
    return total


def apply_realization_to_vector(
    vehicle_vec,  # SubstrateVector
):
    """
    Realize a vehicle vector into the full seven-dimensional return
    vector.

    For each possible return substrate, computes how much of that
    substrate would be realized from the vehicle vector.

    Returns a new SubstrateVector representing the realized returns
    across all substrate dimensions.
    """
    from .substrate_vectors import SubstrateVector
    result = {
        return_sub: apply_realization(vehicle_vec, return_sub)
        for return_sub in InvestmentSubstrate
    }
    return SubstrateVector.from_dict(result)


# ============================================================================
# VALIDATION
# ============================================================================

def validate_realization_matrix() -> None:
    """
    Check structural invariants for the base realization matrix.

    Raises AssertionError on violation.
    """
    # 1. Every substrate must have a full row of 7 realization values.
    for vehicle in InvestmentSubstrate:
        assert vehicle in R_BASE, (
            f"Missing realization row for vehicle {vehicle.value}"
        )
        for return_sub in InvestmentSubstrate:
            assert return_sub in R_BASE[vehicle], (
                f"Missing realization R[{vehicle.value}][{return_sub.value}]"
            )

    # 2. All realization reliabilities must be in [0, 1].
    for vehicle in InvestmentSubstrate:
        for return_sub in InvestmentSubstrate:
            v = R_BASE[vehicle][return_sub]
            assert 0.0 <= v <= 1.0, (
                f"Realization R[{vehicle.value}][{return_sub.value}] = {v} "
                f"outside [0, 1]"
            )

    # 3. Diagonal entries must be high but NOT exactly 1.0.
    #    Even same-substrate realization has attrition (storage loss,
    #    spoilage, decay, opportunity cost). A diagonal of exactly 1.0
    #    would encode a perfect-preservation claim that doesn't hold.
    for sub in InvestmentSubstrate:
        v = R_BASE[sub][sub]
        assert 0.5 <= v < 1.0, (
            f"Self-realization R[{sub.value}][{sub.value}] = {v} "
            f"must be in [0.5, 1.0) -- same-substrate realization is "
            f"high but never perfect"
        )

    # 4. Money-to-relational-capital realization must be low.
    #    Investment in money vehicles rarely produces genuine trust
    #    as realized return. This encodes the institutional blind
    #    spot that cannot purchase community.
    assert R_BASE[InvestmentSubstrate.MONEY][InvestmentSubstrate.RELATIONAL_CAPITAL] <= 0.2, (
        "Money-to-relational-capital realization must be low; "
        "money vehicles cannot produce genuine trust as return"
    )

    # 5. Relational-to-money realization must be low.
    #    Relational vehicles do not cleanly convert to money as
    #    realized return; monetizing destroys the trust that
    #    produced the return.
    assert R_BASE[InvestmentSubstrate.RELATIONAL_CAPITAL][InvestmentSubstrate.MONEY] <= 0.4, (
        "Relational-to-money realization must be low; "
        "monetizing destroys the relational vehicle"
    )

    # 6. Relational-to-relational realization must be very high.
    #    Trust invested in trust-networks compounds strongly. This
    #    is the structural signature of reciprocity systems that
    #    institutional accounting misses.
    assert R_BASE[InvestmentSubstrate.RELATIONAL_CAPITAL][InvestmentSubstrate.RELATIONAL_CAPITAL] >= 0.9, (
        "Relational-to-relational realization must be very high; "
        "reciprocity compounds"
    )

    # 7. Money nominal self-realization must be high.
    #    Money-as-money returns are the easiest institutional path
    #    to realize nominally (not necessarily in real substrate
    #    terms -- the state regime and inflation context will modify
    #    this downstream).
    assert R_BASE[InvestmentSubstrate.MONEY][InvestmentSubstrate.MONEY] >= 0.85, (
        "Money-to-money nominal realization must be high in baseline"
    )

    # 8. Labor-vehicle realization into time must be LOW.
    #    Running a labor-based vehicle (a business, a cooperative)
    #    consumes the investor's time rather than returning it. This
    #    is a distributional truth institutional investment framing
    #    tends to obscure.
    assert R_BASE[InvestmentSubstrate.LABOR][InvestmentSubstrate.TIME] <= 0.3, (
        "Labor-vehicle-to-time realization must be low; "
        "labor vehicles consume time rather than restoring it"
    )


# ============================================================================
# DISPLAY
# ============================================================================

def format_realization_matrix() -> str:
    """
    Return a human-readable string of the base realization matrix.

    Rows are vehicle substrates, columns are return substrates.
    Entry [v][r] is the fraction of vehicle v realized as return r.
    """
    substrates = list(InvestmentSubstrate)
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
        "Base realization matrix R[vehicle][return]:",
        header,
        "         " + "-" * (7 * len(substrates)),
    ]
    for vehicle in substrates:
        row = f"{labels[vehicle]:>6} |"
        for return_sub in substrates:
            row += f"  {R_BASE[vehicle][return_sub]:.2f}"
        lines.append(row)
    return "\n".join(lines)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    from .substrate_vectors import SubstrateVector

    validate_realization_matrix()
    print("Realization matrix validated.")
    print()
    print(format_realization_matrix())
    print()

    # Case A: farmer's labor-based vehicle realizes returns.
    farm_vehicle = SubstrateVector.from_dict({
        InvestmentSubstrate.LABOR: 400.0,
        InvestmentSubstrate.RESOURCE: 50.0,
    })
    money_realized = apply_realization(farm_vehicle, InvestmentSubstrate.MONEY)
    relational_realized = apply_realization(
        farm_vehicle, InvestmentSubstrate.RELATIONAL_CAPITAL
    )
    time_realized = apply_realization(farm_vehicle, InvestmentSubstrate.TIME)
    print(f"Farm vehicle: {farm_vehicle.describe()}")
    print(f"  realizes MONEY:               {money_realized:.1f}")
    print(f"  realizes RELATIONAL_CAPITAL:  {relational_realized:.1f}")
    print(f"  realizes TIME:                {time_realized:.1f}")
    print(f"  (labor-vehicles consume time rather than restoring it)")
    print()

    # Case B: money vehicle with retirement-fund structure.
    retirement_vehicle = SubstrateVector.single(
        InvestmentSubstrate.MONEY, 100000.0
    )
    print(f"Retirement vehicle: {retirement_vehicle.describe()}")
    full_returns = apply_realization_to_vector(retirement_vehicle)
    print(f"  realizes full return vector: {full_returns}")
    print()

    # Case C: relational capital vehicle (community investment).
    community_vehicle = SubstrateVector.single(
        InvestmentSubstrate.RELATIONAL_CAPITAL, 100.0
    )
    print(f"Community vehicle: {community_vehicle.describe()}")
    community_returns = apply_realization_to_vector(community_vehicle)
    print(f"  realizes full return vector: {community_returns}")
    print(f"  (note: low MONEY realization, high LABOR and RELATIONAL returns)")
