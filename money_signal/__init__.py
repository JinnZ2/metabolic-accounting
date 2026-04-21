"""
money_signal/

Coupled-dynamics framework modeling money as a bidirectional
commitment token with measurable reversal reliability, rather than
as a stock / store-of-value / unit-of-account. Full thesis, architecture,
usage, and nine falsifiable claims in `money_signal/README.md`.

Module map:
  - dimensions.py            enums + DimensionalContext
  - coupling_base.py         K_ij_base (first-principles matrix)
  - coupling_temporal.py     temporal factor matrices
  - coupling_cultural.py     cultural factor matrices
  - coupling_attribution.py  attribution factor matrices
  - coupling_observer.py     observer factor matrices
  - coupling_substrate.py    substrate factor matrices
  - coupling_state.py        state-regime factor matrices (sign flips allowed)
  - coupling.py              composition + memoization + diagnostics

Factor modules do not import each other; composition happens only in
coupling.py. Each module is independently testable, replaceable, and
auditable.

See docs/AUDIT_10.md and docs/AUDIT_11.md for intake history and
the two ship-breaking bugs ([CLOSED] as of AUDIT_11 addendum).
"""
