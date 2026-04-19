"""
thermodynamics/exergy.py

Thermodynamic foundation for metabolic-accounting.

Reserves accumulate in EXERGY-DESTRUCTION-EQUIVALENT UNITS (xdu), not currency.
Currency is a downstream conversion layer. This separation matters because:

  - exergy is the proper thermodynamic quantifier for ecosystem buffer capacity
    (Joergensen 1977; Sciubba 2021)
  - the second-law invariants (closure, irreversibility, directionality) are
    stated in exergy terms; stating them in currency would confuse physics
    with policy
  - different firms, regions, and time periods will assign different
    currency values to the same exergy destruction; the framework must
    not bake a particular conversion into the physics

Canonical reference for the law we're enforcing:
  Gouy-Stodola theorem: exergy destruction Exd = T0 * S_gen
  where T0 is the reference (environment) temperature and S_gen is the
  entropy produced by the process. Consequences:
    Exd > 0  process is real (irreversible)        [allowed]
    Exd = 0  process is reversible (ideal limit)   [allowed]
    Exd < 0  process is impossible                 [REFUSED by this framework]

Source: Sciubba & Wall (2007); reviewed in Frontiers in Sustainability
(Sciubba 2021) and summarized in the Exergy Wikipedia entry.
"""

from dataclasses import dataclass
from math import isinf
from typing import Optional


# Canonical unit name. Every reserve quantity in this framework is xdu.
UNIT = "xdu"   # exergy-destruction-equivalent


# Reference temperature (K). Used only when exergy is computed from
# thermal flows; for the ecosystem-reserve accounting we operate on
# normalized xdu, so T0 appears only in physical conversions.
DEFAULT_T0_KELVIN = 298.15


@dataclass
class ExergyFlow:
    """A single exergy transfer event in the ledger.

    source, sink are free-form identifiers ("air.particulate_load",
    "landscape_reserve", "environment", etc).

    amount is in xdu. Positive = source loses, sink gains.
    destroyed is the exergy destruction incurred by the transfer
    (second-law loss, Gouy-Stodola). Must be >= 0. destroyed > 0
    tells you how irreversible the transfer was.
    """
    source: str
    sink: str
    amount: float
    destroyed: float = 0.0
    note: str = ""


class ThermodynamicViolation(Exception):
    """Raised when the framework is asked to perform a computation that
    would violate the second law (negative exergy destruction, regen
    cheaper than damage, closure failure beyond tolerance)."""
    pass


def check_nonnegative_destruction(amount: float, context: str = "") -> None:
    """Gouy-Stodola floor. Any claimed exergy destruction must be >= 0."""
    if isinf(amount):
        return  # inf is allowed — represents unrestorable state
    if amount < -1e-9:
        raise ThermodynamicViolation(
            f"negative exergy destruction ({amount:.6g} xdu) at {context} — "
            "this would require entropy to decrease spontaneously, which "
            "violates the second law. The computation that produced this "
            "value has a bug."
        )


def check_regen_floor(
    regen_cost_xdu: float,
    damage_energy_xdu: float,
    context: str = "",
) -> None:
    """Directional invariant: regeneration must cost STRICTLY MORE exergy
    than the damage cost, because reversing degradation requires work
    against the entropy gradient.

    Formal statement: for a reversal of damage Δ produced by energy flow E,
    the regeneration cost must satisfy regen > E. Equality is only allowed
    in the reversible (idealized) limit.

    This catches regen functions that return costs below the thermodynamic
    floor — a frequent failure mode of ad-hoc regeneration scalars.
    """
    if isinf(regen_cost_xdu):
        return  # inf is the honest signal for unrestorable state
    if damage_energy_xdu <= 0:
        return  # no damage to reverse, nothing to check
    if regen_cost_xdu < damage_energy_xdu:
        raise ThermodynamicViolation(
            f"regeneration cost {regen_cost_xdu:.4g} xdu is less than damage "
            f"cost {damage_energy_xdu:.4g} xdu at {context} — this would "
            "produce net-negative entropy. Regen cost functions must "
            "return values at or above the damage cost; a ratio > 1 is "
            "expected per published hysteresis measurements."
        )


def check_closure(
    imposed: float,
    primary: float,
    secondary: float,
    tertiary: float,
    environment: float,
    tolerance: float = 1e-6,
    context: str = "",
) -> None:
    """First-law mass balance at the reserve hierarchy.

    imposed == primary + secondary + tertiary + environment

    If this fails, stress was either invented or destroyed. Either way
    the computation is wrong.
    """
    if any(isinf(x) for x in (imposed, primary, secondary, tertiary, environment)):
        return  # infinity paths are handled separately by irreversibility
    total = primary + secondary + tertiary + environment
    if abs(total - imposed) > tolerance:
        raise ThermodynamicViolation(
            f"closure failure at {context}: imposed={imposed:.6g} xdu, "
            f"distributed={total:.6g} xdu "
            f"(primary={primary:.4g}, secondary={secondary:.4g}, "
            f"tertiary={tertiary:.4g}, environment={environment:.4g}). "
            "Mass balance broken — computation is wrong."
        )


# --- currency conversion layer ---

@dataclass
class XduConverter:
    """Converts between xdu (physical) and currency (policy).

    The conversion is a declared parameter, NOT a physical constant.
    Different firms, regions, and time periods may set this differently.
    Documenting it explicitly keeps the physics separate from the policy.

    xdu_per_currency_unit: how many xdu one dollar buys at current
    restoration technology / labor / energy prices. A higher value means
    restoration is cheap per xdu (e.g., low-energy regions, abundant
    labor); a lower value means expensive (e.g., high-energy or
    deeply-degraded contexts where remediation is energy-intensive).

    Recommended starting default is 1.0 (xdu and currency numerically
    identical) so the framework's reported numbers are interpretable
    either way without a cognitive cost. Set explicitly when real
    pricing is needed.
    """
    xdu_per_currency_unit: float = 1.0
    label: str = "1:1 placeholder"

    def to_currency(self, xdu: float) -> float:
        if self.xdu_per_currency_unit == 0:
            raise ValueError("xdu_per_currency_unit must not be zero")
        if isinf(xdu):
            return xdu
        return xdu / self.xdu_per_currency_unit

    def to_xdu(self, currency: float) -> float:
        if isinf(currency):
            return currency
        return currency * self.xdu_per_currency_unit
