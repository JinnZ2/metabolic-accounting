"""
investment_signal/

Coupled-dynamics framework modeling investment as substrate-of-self
committed against substrate-of-future. Sibling of money_signal.
Depends on money_signal for the monetary context underneath the
investment — investment cannot be evaluated if money is in
near-collapse.

Full thesis, architecture, seven substrates, 23 falsifiable claims,
and usage in `investment_signal/README.md`.

Module map:
  - dimensions.py            InvestmentSubstrate (7), InvestmentAttribution (7),
                             DerivativeDistance (5), TimeBinding (6),
                             InvestmentContext
  - substrate_vectors.py     SubstrateVector (frozen 7-dim)
  - conversion_matrix.py     C[in][vehicle]: 7x7
  - realization_matrix.py    R[vehicle][return]: 7x7
  - time_binding.py          binding × scope integrity + modifiers
  - derivative_distance.py   5-level abstraction degradation
  - coupling.py              InvestmentSignal assembly + validators

See docs/AUDIT_13.md for intake and the import-convention bug fix
that was required before the package would load.
"""
