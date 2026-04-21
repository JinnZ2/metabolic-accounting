"""
investment_signal/substrate_vectors.py

Seven-dimensional substrate vectors.

Every investment has an input vector (what is committed) and an
output vector (what is expected back). Each vector is a mapping
from the seven InvestmentSubstrate values to nonneg floats.

Units are intentionally unspecified and caller-dependent. A time
component might be hours. A resource component might be kilograms
or cubic meters. A labor component might be skilled-hours. The
framework does not force a unit system because substrate-specific
unit choices are where measurement failures usually enter. What
the framework requires is that a given analysis uses consistent
units within a given substrate across its inputs and outputs.

The vector type is frozen and hashable so it can be used in
memoization keys downstream. Arithmetic produces new vectors
rather than mutating.

CC0. Stdlib-only.
"""

from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

from .dimensions import InvestmentSubstrate


# ============================================================================
# SUBSTRATE VECTOR
# ============================================================================

@dataclass(frozen=True)
class SubstrateVector:
    """
    A seven-dimensional vector over the investment substrates.

    Stored as a frozen tuple of (substrate, magnitude) pairs in
    canonical substrate order. All seven substrates are always
    present in the storage, even when their magnitude is zero --
    this keeps vector arithmetic trivial and removes sparse/dense
    ambiguity.

    Magnitudes are non-negative floats. A zero magnitude means the
    investment does not use that substrate. Negative magnitudes are
    not permitted here; flows that represent loss or extraction
    belong in the conversion or realization matrices, not in the
    substrate vector itself.
    """
    components: Tuple[Tuple[InvestmentSubstrate, float], ...] = field(default=())

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def zero(cls) -> "SubstrateVector":
        """Return a vector with zero magnitude in every substrate."""
        return cls(components=tuple(
            (s, 0.0) for s in InvestmentSubstrate
        ))

    @classmethod
    def from_dict(cls, data: Dict[InvestmentSubstrate, float]) -> "SubstrateVector":
        """
        Construct a SubstrateVector from a dict.

        Missing substrates default to 0.0. Extra keys raise. Negative
        values raise.
        """
        for key in data:
            if not isinstance(key, InvestmentSubstrate):
                raise TypeError(
                    f"SubstrateVector keys must be InvestmentSubstrate, "
                    f"got {type(key).__name__}: {key}"
                )
        for key, value in data.items():
            if value < 0.0:
                raise ValueError(
                    f"SubstrateVector magnitudes must be non-negative; "
                    f"got {key.value}={value}. "
                    f"Losses and extractions belong in conversion or "
                    f"realization matrices, not in the substrate vector."
                )
        return cls(components=tuple(
            (s, float(data.get(s, 0.0))) for s in InvestmentSubstrate
        ))

    @classmethod
    def single(cls, substrate: InvestmentSubstrate, magnitude: float) -> "SubstrateVector":
        """Construct a vector with one nonzero substrate."""
        return cls.from_dict({substrate: magnitude})

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get(self, substrate: InvestmentSubstrate) -> float:
        """Return the magnitude for the given substrate."""
        for s, v in self.components:
            if s == substrate:
                return v
        return 0.0

    def as_dict(self) -> Dict[InvestmentSubstrate, float]:
        """Return the vector as a fresh dict. Caller may mutate safely."""
        return {s: v for s, v in self.components}

    def nonzero_components(self) -> Tuple[Tuple[InvestmentSubstrate, float], ...]:
        """Return only the substrate-magnitude pairs with nonzero magnitude."""
        return tuple((s, v) for s, v in self.components if v != 0.0)

    def is_zero(self) -> bool:
        """Return True if every magnitude is zero."""
        return all(v == 0.0 for _, v in self.components)

    def support(self) -> Tuple[InvestmentSubstrate, ...]:
        """
        Return the substrates with nonzero magnitude.

        The support of a substrate vector tells you which substrates
        are actually involved. A farmer planting seeds has a support
        of {TIME, RESOURCE, ENERGY, LABOR}. A derivatives trader has
        a support of {MONEY, ATTENTION}. Different supports indicate
        structurally different investments.
        """
        return tuple(s for s, v in self.components if v != 0.0)

    def sparsity(self) -> float:
        """
        Return the fraction of substrates that are zero.

        1.0 means the vector is all zeros. 0.0 means all seven
        substrates are nonzero.
        """
        total = len(self.components)
        zeros = sum(1 for _, v in self.components if v == 0.0)
        return zeros / total if total > 0 else 0.0

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def scaled(self, factor: float) -> "SubstrateVector":
        """
        Return a new vector with every magnitude multiplied by factor.

        Factor must be non-negative; negative scaling would violate
        the non-negativity invariant.
        """
        if factor < 0.0:
            raise ValueError(
                f"SubstrateVector scaling factor must be non-negative, "
                f"got {factor}"
            )
        return SubstrateVector(components=tuple(
            (s, v * factor) for s, v in self.components
        ))

    def added(self, other: "SubstrateVector") -> "SubstrateVector":
        """Return a new vector that is the substrate-wise sum."""
        self_dict = self.as_dict()
        other_dict = other.as_dict()
        return SubstrateVector(components=tuple(
            (s, self_dict[s] + other_dict[s]) for s in InvestmentSubstrate
        ))

    def substracted(self, other: "SubstrateVector") -> "SubstrateVector":
        """
        Return a new vector that is self minus other, substrate-wise.

        Raises ValueError if any component of other exceeds the
        corresponding component of self, because the result would
        violate non-negativity.

        Use this for tracking substrate balance over time, not for
        representing losses. A loss belongs in the conversion matrix.
        """
        self_dict = self.as_dict()
        other_dict = other.as_dict()
        for s in InvestmentSubstrate:
            if other_dict[s] > self_dict[s]:
                raise ValueError(
                    f"SubstrateVector subtraction would produce negative "
                    f"magnitude for {s.value}: "
                    f"{self_dict[s]} - {other_dict[s]} < 0"
                )
        return SubstrateVector(components=tuple(
            (s, self_dict[s] - other_dict[s]) for s in InvestmentSubstrate
        ))

    def l1_magnitude(self) -> float:
        """
        Return the sum of all substrate magnitudes.

        This is NOT a meaningful total because the substrates have
        incommensurable units. It is useful only as a rough size
        signal for comparing vectors with identical support.
        """
        return sum(v for _, v in self.components)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def describe(self, only_nonzero: bool = True) -> str:
        """
        Return a human-readable string of the vector.

        By default only nonzero substrates are shown.
        """
        items = (
            self.nonzero_components() if only_nonzero else self.components
        )
        if not items:
            return "SubstrateVector(zero)"
        parts = [f"{s.value}={v:g}" for s, v in items]
        return "SubstrateVector(" + ", ".join(parts) + ")"

    def __str__(self) -> str:
        return self.describe()


# ============================================================================
# VALIDATION
# ============================================================================

def validate_vector_storage(v: SubstrateVector) -> None:
    """
    Check structural invariants for a substrate vector.

    Called from downstream validation in coupling.py and tests.
    Raises AssertionError on violation.
    """
    # 1. Must have exactly seven components, one per substrate.
    assert len(v.components) == len(InvestmentSubstrate), (
        f"SubstrateVector must have exactly {len(InvestmentSubstrate)} "
        f"components, got {len(v.components)}"
    )

    # 2. Components must be in canonical InvestmentSubstrate order.
    expected_order = list(InvestmentSubstrate)
    actual_order = [s for s, _ in v.components]
    assert actual_order == expected_order, (
        f"SubstrateVector components out of canonical order. "
        f"Expected {[s.value for s in expected_order]}, "
        f"got {[s.value for s in actual_order]}"
    )

    # 3. All magnitudes must be non-negative.
    for s, value in v.components:
        assert value >= 0.0, (
            f"SubstrateVector component {s.value}={value} is negative"
        )


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def vector_overlap(a: SubstrateVector, b: SubstrateVector) -> Tuple[InvestmentSubstrate, ...]:
    """
    Return the substrates where BOTH vectors have nonzero magnitude.

    Useful for detecting substrate-in / substrate-out matches --
    if an investment expects to receive a substrate it also put in,
    the overlap is where that happens.
    """
    a_support = set(a.support())
    b_support = set(b.support())
    overlap = a_support & b_support
    return tuple(s for s in InvestmentSubstrate if s in overlap)


def cross_substrate_investment(
    input_vec: SubstrateVector, output_vec: SubstrateVector
) -> bool:
    """
    Return True if the investment requires substrate conversion.

    An investment that puts in TIME and expects back MONEY is
    cross-substrate. An investment that puts in MONEY and expects
    back MONEY is same-substrate. Cross-substrate investments
    always involve conversion losses; same-substrate investments
    can in principle avoid them.

    This is a structural property, not a numeric one: the question
    is whether output substrates are a subset of input substrates.
    """
    input_support = set(input_vec.support())
    output_support = set(output_vec.support())
    return not output_support.issubset(input_support)


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    # A farmer planting seeds: invests TIME, RESOURCE, ENERGY, LABOR.
    # Expects back RESOURCE (food), RELATIONAL_CAPITAL (land relationship),
    # and small MONEY (sale of surplus).
    farmer_in = SubstrateVector.from_dict({
        InvestmentSubstrate.TIME: 400.0,        # hours across season
        InvestmentSubstrate.RESOURCE: 50.0,     # seeds, fertilizer in kg
        InvestmentSubstrate.ENERGY: 8000.0,     # kcal of labor-energy
        InvestmentSubstrate.LABOR: 400.0,       # skilled-hours
    })
    farmer_out = SubstrateVector.from_dict({
        InvestmentSubstrate.RESOURCE: 2000.0,   # kg of crop
        InvestmentSubstrate.RELATIONAL_CAPITAL: 5.0,  # arbitrary unit
        InvestmentSubstrate.MONEY: 1500.0,      # surplus sold
    })

    # A derivatives trader: invests MONEY, ATTENTION. Expects MONEY.
    trader_in = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 10000.0,
        InvestmentSubstrate.ATTENTION: 100.0,   # cognitive-hours
    })
    trader_out = SubstrateVector.from_dict({
        InvestmentSubstrate.MONEY: 11000.0,
    })

    validate_vector_storage(farmer_in)
    validate_vector_storage(farmer_out)
    validate_vector_storage(trader_in)
    validate_vector_storage(trader_out)

    print("Farmer investment:")
    print(f"  in:  {farmer_in}")
    print(f"  out: {farmer_out}")
    print(f"  support overlap: {vector_overlap(farmer_in, farmer_out)}")
    print(f"  cross-substrate: {cross_substrate_investment(farmer_in, farmer_out)}")
    print(f"  in sparsity:  {farmer_in.sparsity():.2f}")
    print(f"  out sparsity: {farmer_out.sparsity():.2f}")
    print()

    print("Trader investment:")
    print(f"  in:  {trader_in}")
    print(f"  out: {trader_out}")
    print(f"  support overlap: {vector_overlap(trader_in, trader_out)}")
    print(f"  cross-substrate: {cross_substrate_investment(trader_in, trader_out)}")
    print(f"  in sparsity:  {trader_in.sparsity():.2f}")
    print(f"  out sparsity: {trader_out.sparsity():.2f}")
    print()

    # Arithmetic sanity check.
    combined = farmer_in.added(trader_in)
    print(f"Combined input: {combined}")
    print(f"Scaled farmer in x2: {farmer_in.scaled(2.0)}")
