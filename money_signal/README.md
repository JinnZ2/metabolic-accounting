# money_signal

**Subfolder of `metabolic-accounting`. CC0. Stdlib-only. Falsifiable. Machine-readable.**

A coupled-dynamics framework that models money as a **bidirectional commitment token** with measurable reversal reliability, rather than as a stock, a store of value, or a unit of account.

Money is treated as a **multiplexed signal carrier**, not a signal. What money actually measures depends on scope, substrate, cultural context, attributed value, observer position, and current state regime. Scope mismatch across these dimensions is the core failure mode in conventional monetary modeling.

This module makes that dimensional structure explicit, composable, and testable.

---

## Core thesis

An object functions as money if and only if it can be exchanged back for comparable value across a network, within a bounded latency and cost, at measurable reliability. The invariant is **bidirectional commitment reliability**, not storage, not accounting, not exchange.

Four terms carry the signal:

- `R` reversal reliability — probability of successful re-exchange
- `N` network acceptance — fraction of the relevant network that will accept
- `C` cost of reversal — fraction of value lost to reverse
- `L` latency of reversal — time required to complete re-exchange

These four terms are coupled. A coupling matrix `K` encodes how each term responds when another changes. The coupling is not constant. It is a function of six dimensions:

- **Temporal scope** — transaction, seasonal, generational, epochal
- **Cultural scope** — high-reciprocity, community-trust, institutional, atomized-market, mixed
- **Attributed value** — labor-stored, commodity-backed, state-enforced, network-agreed, reciprocity-token, divine-sanctioned, speculative-claim
- **Observer position** — substrate producer, substrate consumer, deep holder, thin holder, issuer, intermediary
- **Substrate** — biological, metal, paper, digital, trust-ledger
- **State regime** — healthy, stressed, near-collapse, recovering

`K_ij(context) = K_ij_base × temporal × cultural × attribution × observer × substrate × state`

Self-couplings (diagonal) are fixed at 1.0. Off-diagonals are signed. Only `state` may flip signs, and only in the near-collapse regime, where reflexive dynamics produce direction inversions that are physically real.

---

## Why this framework exists

Conventional monetary modeling collapses to a **single-observer aggregate** and treats money as a stable unit. That collapse is itself a measurement failure. It hides:

- That the same system produces different `M(t)` for different observers simultaneously
- That trust collapses faster than it rebuilds (Minsky asymmetry)
- That post-collapse systems do not return to pre-collapse coupling even after metrics recover (hysteresis)
- That substrate and attributed value change the coupling signature independently of the institutional framework
- That reciprocity-based systems have built-in repair protocols which monetary systems lack

The framework does not argue these points. It encodes them as **structural invariants enforced by validation tests**. An edit that silently collapses any of them breaks the tests.

---

## Architecture

money_signal/
├── init.py
├── dimensions.py               # enums and DimensionalContext
├── coupling_base.py            # K_ij_base (first-principles matrix)
├── coupling_temporal.py        # temporal factor matrices
├── coupling_cultural.py        # cultural factor matrices
├── coupling_attribution.py     # attribution factor matrices
├── coupling_observer.py        # observer factor matrices
├── coupling_substrate.py       # substrate factor matrices
├── coupling_state.py           # state regime factor matrices (sign flips allowed)
├── coupling.py                 # composition, memoization, diagnostics
└── README.md                   # this file


Each factor module is independent. None imports from another factor module. All composition happens in `coupling.py`. This makes each module independently testable, independently replaceable, and independently auditable.

---

## Calibration conventions

Each factor module has one designated **calibration case** where all factors equal 1.0. These cases define what the base matrix implicitly assumes:

- Temporal: `SEASONAL`
- Cultural: `INSTITUTIONAL`
- Attribution: `STATE_ENFORCED`
- Substrate: `METAL` (factors allowed within +/- 0.15)
- State: `HEALTHY`
- Observer: no calibration case — every observer is a real position, no measurement fiction

The base matrix is therefore calibrated against **metal-substrate, state-enforced, institutional, seasonal, healthy-regime monetary systems**. Every other configuration is a named deviation from that baseline. This makes the framework compatible with classical monetary literature while exposing where that literature silently assumes the baseline.

---

## Falsifiable claims

These claims are encoded as validation invariants. A code edit that silently violates them breaks the test suite.

1. **Minsky asymmetry**: `K[N][R] >= K[R][N]` in every regime except near-collapse. Trust never rebuilds faster than it collapses. Structural invariant; not a fit.

2. **Hysteresis**: `RECOVERING` state has off-diagonal coupling factors strictly less than `HEALTHY` state. Post-collapse systems operate with damped coupling regardless of nominal metric recovery.

3. **Reciprocity damping**: `TRUST_LEDGER` substrate and `RECIPROCITY_TOKEN` attribution both damp `K[N][R]` below the metal/state-enforced baseline. Relational substrates contain repair protocols that physical substrates lack.

4. **Speculative amplification**: `SPECULATIVE_CLAIM` attribution amplifies `K[N][R]` above baseline. Pure financialization has no substrate floor, institutional floor, relational floor, or sacred floor to catch collapse.

5. **Observer asymmetry**: `TOKEN_HOLDER_THIN` experiences amplified coupling on `K[R][C]`, `K[R][L]`, and `K[N][R]` relative to `TOKEN_HOLDER_DEEP`. The same system state produces more fragile `M(t)` for thin holders than aggregate metrics reveal.

6. **Issuer insulation**: `TOKEN_ISSUER` experiences damped coupling on all cost and latency driving terms relative to thin holders. Central banks looking at their own coupling experience of the system will systematically underestimate system fragility.

7. **Near-collapse sign inversion**: `NEAR_COLLAPSE` regime permits `K[N][C]` to flip negative. Panic-buying dynamics where rising cost briefly increases acceptance are real and must be modeled, not smoothed over.

8. **Minsky dominance in collapse**: In `NEAR_COLLAPSE`, `|K[N][R]|` dominates all other off-diagonal coefficients in magnitude. Trust collapse becomes the only thing that matters; every other dynamic is a second-order effect.

9. **Digital infrastructure coupling**: `DIGITAL` substrate amplifies `K[R][N]` above metal baseline. Reliability is coupled to infrastructure continuity in a way physical substrates never were. Infrastructure collapse is a qualitatively distinct failure mode.

Each claim can be tested against historical cases. Any claim that fails empirical test requires the framework to be revised, not the test dismissed.

---

## Diagnostic outputs

`coupling.py` exposes three primary diagnostics:

- **Minsky coefficient**: `|K[N][R]| / |K[R][N]|`. Baseline ~1.14. Stressed systems climb above 2.0. Near-collapse exceeds 5.0.

- **Coupling magnitude**: mean `|K[i][j]|` across off-diagonals. Distinguishes `RECOVERING` (damped, mean < 1.0) from `HEALTHY` (moderate) from `STRESSED` (elevated) from `NEAR_COLLAPSE` (very high, sign flips present).

- **Sign flips present**: boolean. True only in `NEAR_COLLAPSE`. A non-collapse system with sign flips is a bug, not a finding.

These diagnostics are the interface the rest of the `metabolic-accounting` repo consumes. The cascade module reads coupling signatures to predict cascade propagation. The verdict module reads them to produce sustainable-yield assessments. The distributional module reads them to produce observer-asymmetry reports.

---

## Relation to other repos

This module is one leg of a three-repo analysis of money as a signal.

### `metabolic-accounting/money_signal/` (this module)

Native home for the core equation and coupling matrices. Money-as-signal couples directly into the existing glucose-flow metaphor: reversal reliability is the metabolic signal. When reversal fails, the organism cannot cycle glucose and must draw down from reserves. That drawdown is the forced-drawdown concept already present in this repo.

### `thermodynamic-accountability-framework/money_distribution/`

Distributional analysis and attribution tracing. Asks different questions than this module:

- For any given `M(t)`, who holds tokens with high `R` and who holds tokens with low `R`?
- Who benefits from current `L` tolerance? Who pays current `C`?
- What is the asymmetry score between best-case and worst-case observer positions in the same system?
- Tracing extraction flows upstream: which actors set the terms that determined the current coupling?

Consumes coupling matrices produced here. Produces distributional reports.

### `earth-systems-physics/coupling/money_as_constraint/`

Physical coupling layer. Treats money signal as a **forcing function** on biosphere and lithosphere extraction rate. Not a natural Earth-system layer but an induced one.

- When money over-succeeds (hyperliquidity), physical extraction accelerates.
- When money fails, extraction patterns change abruptly.
- Physical collapse degrades reversal reliability, which changes the forcing.

This is where money-as-signal couples back into the physical Earth-system stack. Slowest-moving and hardest to build. Requires the other two modules to be stable first.

---

## Usage

```python
from money_signal.dimensions import (
    DimensionalContext,
    TemporalScope, CulturalScope, AttributedValue,
    ObserverPosition, Substrate, StateRegime,
)
from money_signal.coupling import (
    coupling_matrix_as_dict,
    minsky_coefficient,
    coupling_magnitude,
    has_sign_flips,
    validate_all_factor_modules,
)

# Always validate at startup.
validate_all_factor_modules()

# Build a context. No defaults. Scope must be declared.
ctx = DimensionalContext(
    temporal=TemporalScope.SEASONAL,
    cultural=CulturalScope.INSTITUTIONAL,
    attribution=AttributedValue.STATE_ENFORCED,
    observer=ObserverPosition.TOKEN_HOLDER_THIN,
    substrate=Substrate.DIGITAL,
    state=StateRegime.STRESSED,
)

# Get the composed coupling matrix.
K = coupling_matrix_as_dict(ctx)

# Get diagnostic summaries.
minsky = minsky_coefficient(ctx)
mag = coupling_magnitude(ctx)
flips = has_sign_flips(ctx)



Known limitations
	1.	Factor values are first-principles estimates, not empirical fits. Historical case calibration is planned as a separate historical_cases.py module. Until that is populated, factor magnitudes should be treated as qualitative rather than quantitative.
	2.	Composition is multiplicative, not additive. This is a modeling choice. Additive composition would produce different dynamics under stacked deviations. Multiplicative was chosen because it preserves sign more cleanly and matches the intuition that factors compound rather than sum. This choice may need revision after historical calibration.
	3.	MIXED cultural scope is a mean. Heterogeneous networks have high variance that a single factor matrix cannot capture. Subpopulation analysis belongs in the distributional module, not here.
	4.	No temporal integration. This module produces static coupling matrices for given contexts. Cascade dynamics (how M(t) evolves over time under coupled feedback) belongs in the cascade module of the parent repo.
	5.	No distributional aggregation. This module computes coupling for one observer at a time. Cross-observer asymmetry analysis belongs in the accountability repo.


License
CC0. Public domain. No attribution required. No warranty.

