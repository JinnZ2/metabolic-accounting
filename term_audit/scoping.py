"""
term_audit/scoping.py

Codified scoping dimensions for economic terms.

An economic term used without a declared scope — jurisdiction, referent,
time horizon, measurement context, etc. — is not a measurement. It is a
token that occupies a signal-shaped position in discourse. The
term_audit schema (term_audit/schema.py) scores a term's signal-hood
after the fact; this module codifies what WOULD need to be declared
in advance for the term to qualify as a measurement in a given use.

See docs/SCOPING_ECONOMIC_TERMS.md for the full argument, worked
expansions of money / capital / investment, and the reading order
for AI assistants working on this repo.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Scoping dimensions
# ---------------------------------------------------------------------------
#
# Each tuple is (name, description). The order is deliberate — dimensions
# listed first constrain the later ones. A declaration that supplies the
# later dimensions without the earlier ones is still under-scoped.
#
# This list is append-only. Removing a dimension silently weakens the
# scoping discipline. Add new dimensions at the end; if one is obsoleted,
# mark it deprecated in the description but leave it in place.
# ---------------------------------------------------------------------------

SCOPING_DIMENSIONS: List[Tuple[str, str]] = [
    ("referent", (
        "the physical, informational, or legal quantity the term claims "
        "to measure. A term can have multiple candidate referents "
        "(money: unit of account, medium of exchange, store of value, "
        "legal claim); the declaration must pick one."
    )),
    ("jurisdiction", (
        "the legal and regulatory regime under which the term is defined "
        "(US federal, EU, UK, state/province, specific treaty). Changes "
        "the meaning of 'currency', 'security', 'capital adequacy', "
        "'investment', 'income'."
    )),
    ("time_horizon", (
        "instantaneous, period (and which period), cumulative, discounted, "
        "or lifetime. A dollar on a labor contract, a dollar on a 30-year "
        "bond, and a dollar on a derivative clearing today are not the "
        "same quantity across time."
    )),
    ("legal_regime", (
        "contract law, tax law, bankruptcy law, property law, securities "
        "law. The same nominal amount has different enforceability and "
        "claim priority under each regime."
    )),
    ("counterparty_class", (
        "retail, institutional, sovereign, inter-bank, central bank, "
        "or none. Settlement finality, credit risk, and what the token "
        "actually means all vary by counterparty."
    )),
    ("measurement_context", (
        "transaction, accounting entry, forecast, disclosure, regulatory "
        "filing, tax return, appraisal, audit. The same underlying event "
        "is booked differently in each context."
    )),
    ("calibration_procedure", (
        "the reproducible procedure mapping the declared amount to the "
        "referent. Without this, the number is not calibrated; it is a "
        "label."
    )),
    ("standard_setter", (
        "who defines the term in this context (central bank, FASB, IASB, "
        "IRS, BEA, appraisal body, contract counterparty). Include their "
        "incentive structure — see term_audit/schema.py::StandardSetter."
    )),
    ("stock_or_flow", (
        "stock (balance at a point in time) or flow (quantity per period). "
        "Using a stock number as a flow — or vice versa — is a category "
        "error that the terminology often hides."
    )),
    ("nominal_or_real", (
        "nominal (raw currency units) or real (price-level-adjusted). "
        "'Real' adjustment requires declaring the deflator; CPI, PPI, "
        "GDP deflator, and sector-specific indices all give different "
        "answers."
    )),
    ("gross_or_net", (
        "gross (before offsetting items) or net (after). The offset "
        "rules themselves require declaration: net of what, under which "
        "accounting convention."
    )),
    ("asset_class_or_sector", (
        "which asset class (equity, debt, real, intangible, commodity, "
        "currency) or economic sector the term applies to. 'Capital' "
        "means different things for each."
    )),
    ("accounting_basis", (
        "cash, accrual, fair value, historical cost, mark-to-market, "
        "mark-to-model. The same transaction produces different numbers "
        "under each basis."
    )),
    ("aggregation_level", (
        "individual, household, firm, sector, sub-national, national, "
        "regional, global. Aggregation destroys information; the level "
        "must be declared."
    )),
    ("observer_role", (
        "participant, third-party, regulator, auditor, analyst. Observer "
        "role changes which fields are observable and which are imputed."
    )),
]


SCOPING_DIMENSION_NAMES = [name for name, _ in SCOPING_DIMENSIONS]


# ---------------------------------------------------------------------------
# DeclaredScope
# ---------------------------------------------------------------------------

@dataclass
class DeclaredScope:
    """A declared scope for using an economic term in a measurement context.

    Using the term without supplying a DeclaredScope (or equivalent
    explicit declaration in prose, docstring, or code comment) is a
    narrative strip: treating a bundle of measurables as a single
    measurement.

    A DeclaredScope may be partial — that is the point. The
    `missing_dimensions()` method surfaces which dimensions have not
    yet been declared, so the under-scoping is explicit rather than
    hidden.
    """
    term: str
    declarations: Dict[str, str] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self):
        # reject unknown dimensions — typos silently weaken the
        # discipline. Adding a new dimension requires editing
        # SCOPING_DIMENSIONS above.
        unknown = set(self.declarations) - set(SCOPING_DIMENSION_NAMES)
        if unknown:
            raise ValueError(
                f"unknown scoping dimensions in declaration for "
                f"'{self.term}': {sorted(unknown)}. Valid dimensions: "
                f"{SCOPING_DIMENSION_NAMES}"
            )

    def missing_dimensions(self) -> List[str]:
        """Scoping dimensions not present in this declaration."""
        return [
            name for name in SCOPING_DIMENSION_NAMES
            if name not in self.declarations
               or not self.declarations[name].strip()
        ]

    def is_adequately_scoped(self) -> bool:
        """True iff every SCOPING_DIMENSIONS entry has a non-empty
        declaration. A term is a measurement in this context only when
        adequately scoped."""
        return not self.missing_dimensions()

    def scoping_fraction(self) -> float:
        """Fraction of dimensions declared. 0.0 = token; 1.0 = measurement."""
        if not SCOPING_DIMENSION_NAMES:
            return 1.0
        declared = len(SCOPING_DIMENSION_NAMES) - len(self.missing_dimensions())
        return declared / len(SCOPING_DIMENSION_NAMES)
