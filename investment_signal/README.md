# investment_signal

**Subfolder of `metabolic-accounting`. Sibling of `money_signal`. CC0. Stdlib-only. Falsifiable. Machine-readable.**

A coupled-dynamics framework that models investment as **substrate-of-self committed against substrate-of-future**. Investment is not a stock, not a store of value, and not a monetary return. It is a cross-substrate commitment process with measurable conversion reliability, realization reliability, time binding integrity, and derivative-distance degradation.

This module makes those dimensions explicit, composable, and testable. It depends on `money_signal`, because investment is money-plus-time and money-signal instability propagates through the investment signal.

---

## Core thesis

Conventional finance collapses all investment to a money-in / money-out calculation. That collapse is the primary measurement failure this module exists to expose. What an investor actually commits is one or more of seven substrates: time, resource, energy, labor, attention, money, relational capital. What they actually receive is also one or more of those seven. Conversion between them is lossy and context-dependent.

Investment is modeled as **two seven-dimensional substrate vectors plus a context**. The input vector is what is committed. The output vector is what is expected. The context determines attribution, derivative distance, time binding, and the full money-signal state.

The complete signal decomposes into five distinct failure-mode diagnostics:

- `conversion_reliability` — did the input substrate actually become the vehicle?
- `realization_reliability` — did the vehicle actually produce the expected return?
- `time_binding_integrity` — does the temporal commitment hold at the evaluation scope?
- `derivative_signal` — how much signal survives the abstraction layers?
- `money_coupling` — inherited money-signal dynamics; failures here break investment by definition

No single-number collapse is provided. Collapsing these is the error the framework refuses to participate in.

---

## Why this framework exists

Conventional investment analysis produces a return number, maybe a risk-adjusted return number, and treats that as the whole answer. This hides:

- That a worker investing time into a job converts that time into money at a rate set by measurement failures unrelated to productivity
- That a community investing relational capital cannot realize returns in money without destroying the relational capital
- That time, attention, and relational capital cannot be meaningfully derivatized — attempting to do so produces something structurally different
- That short-binding long-scope investments are operating on a liquidity illusion
- That long-binding short-scope investments are walking into the infrastructure-depreciation trap
- That at high derivative distance the financial layer starts governing the substrate (reverse causation) rather than the other way around
- That if money is in near-collapse, no investment analysis is valid regardless of its internal numbers

The framework does not argue these points. It encodes them as structural invariants enforced by validation tests. An edit that silently collapses any of them breaks the tests.

---

## Architecture

investment_signal/
├── init.py
├── dimensions.py              # InvestmentSubstrate (7), InvestmentAttribution (7),
│                              # DerivativeDistance (5), TimeBinding (6), InvestmentContext
├── substrate_vectors.py       # SubstrateVector (frozen, 7-dim), arithmetic, diagnostics
├── conversion_matrix.py       # C[in][vehicle]: 7x7 conversion reliability
├── realization_matrix.py      # R[vehicle][return]: 7x7 realization reliability
├── time_binding.py            # binding×scope integrity, substrate modifiers, mismatch detectors
├── derivative_distance.py     # signal, visibility, cascade, reverse-causation at 5 distances
├── coupling.py                # InvestmentSignal assembly, dependency-broken detection
└── README.md                  # this file


Each file is independent of the others except through well-defined imports. All composition happens in `coupling.py`. This makes each module independently testable, replaceable, and auditable.

---

## The seven substrates

These are the fungible-but-not-equivalent carriers that can be invested or received as return:

- `TIME` — hours of life allocated
- `RESOURCE` — physical material committed
- `ENERGY` — work capacity (biological, thermal, electrical)
- `LABOR` — applied skill and effort
- `ATTENTION` — cognitive bandwidth
- `MONEY` — the multiplexed carrier from `money_signal`
- `RELATIONAL_CAPITAL` — trust built up in a network

Every investment is natively a seven-dimensional vector. Single-substrate investments are sparse vectors. No collapse to money unless the investor specifically chose money-in money-out.

---

## Calibration conventions

The base matrices assume a specific default configuration. Each named option is a deviation from this baseline:

- **Conversion matrix**: atomized-market institutional baseline
- **Realization matrix**: institutional, one derivative layer, matched time binding, healthy money
- **Time binding**: the diagonal (binding matches scope) is the calibration anchor
- **Derivative distance**: `DIRECT` is the reference; each step introduces documented degradation
- **Money context inheritance**: every money-signal calibration convention applies transitively

---

## Falsifiable claims

These claims are encoded as validation invariants. An edit that silently violates them breaks the test suite.

### Conversion claims

1. **Monetizing relational capital destroys it.** `C[RELATIONAL_CAPITAL][MONEY] ≤ 0.3`. The conversion destroys the thing being converted.
2. **Money cannot purchase genuine relational capital.** `C[MONEY][RELATIONAL_CAPITAL] ≤ 0.3`. Symmetric to the above.
3. **Attention is extracted before reaching money.** `C[ATTENTION][MONEY] ≤ 0.4`. Intermediaries capture attention value before the attention-investor can realize monetary return.
4. **Thermodynamic conversions are well-understood.** `C[RESOURCE][ENERGY] ≥ 0.6`. Physics sets a floor on this conversion.

### Realization claims

5. **Same-substrate realization is high but never perfect.** `0.5 ≤ R[i][i] < 1.0` for every substrate. Attrition exists even in identity.
6. **Money vehicles cannot produce genuine trust as return.** `R[MONEY][RELATIONAL_CAPITAL] ≤ 0.2`.
7. **Relational vehicles cannot realize as money.** `R[RELATIONAL_CAPITAL][MONEY] ≤ 0.4`. Monetizing destroys the vehicle.
8. **Relational capital compounds in its own substrate.** `R[RELATIONAL_CAPITAL][RELATIONAL_CAPITAL] ≥ 0.9`. Institutional accounting misses this.
9. **Money nominal realization is high.** `R[MONEY][MONEY] ≥ 0.85`. Note: nominal. Real-substrate realization is handled by the money context.
10. **Labor vehicles consume time rather than producing it.** `R[LABOR][TIME] ≤ 0.3`. Contradicts common small-business-as-investment framings.

### Time binding claims

11. **Short-binding / long-scope mismatch is severe.** For `IMMEDIATE` or `SHORT_CYCLE` binding at `GENERATIONAL` or `EPOCHAL` scope, mismatch severity ≥ 0.5. This is the liquidity-illusion claim.
12. **Only multi-generational bindings survive epochal horizons.** `MULTI_GENERATIONAL` binding has strictly higher integrity at epochal scope than any other binding.
13. **Time and attention cannot be meaningfully bound long-term.** Substrate modifiers for both are strictly less than 1.0.
14. **Relational capital has the highest binding modifier.** Only substrate that structurally compounds across generations.

### Derivative distance claims

15. **Signal reliability decreases monotonically with distance.** No layer can accidentally improve signal.
16. **Substrate visibility decreases monotonically with distance.** Opacity grows with abstraction.
17. **Cascade coupling increases monotonically with distance.** Higher abstraction, more cross-substrate contagion risk.
18. **Reverse causation increases monotonically with distance.** At sufficient distance, the financial layer governs the substrate.
19. **DIRECT distance has zero reverse causation and near-perfect substrate visibility.** Baseline for all distance comparisons.
20. **SYNTHETIC distance is financialized by definition.** Reverse causation ≥ 0.5.
21. **Time, attention, and relational capital cannot be derivatized without losing their nature.** Abstraction tolerance for each is below 0.35.
22. **Money has the highest abstraction tolerance.** Money is already abstract; derivatives extend that.

### Dependency claims

23. **Investment cannot be evaluated when money is in near-collapse.** `dependency_broken = True` and all return figures are flagged unreliable.

---

## Diagnostic outputs

`coupling.py` produces an `InvestmentSignal` dataclass with twenty fields. No single collapse is provided. Key diagnostics:

- **Failure count**: number of structural failure flags that are True. Zero for healthy, 7+ for collapsed-regime synthetic derivatives.
- **Failure reasons**: named list of every failure mode triggered. Used for targeted diagnostic reports.
- **Vehicle vector**: what the input actually became across all seven substrates.
- **Realized output vector**: what the vehicle actually produces across all seven substrates.

The vectors allow comparison with the `expected_output_vector` the caller provided. Gap analysis between expected and realized is the concrete output of the framework.

---

## Relation to other repos

This module is one leg of a three-repo analysis of monetary and investment signals.

### `metabolic-accounting/money_signal/` (dependency)

The money layer underneath. Investment imports `DimensionalContext` (as `MoneyContext`), uses the money-signal coupling module to evaluate the monetary stability underlying any investment, and flags `dependency_broken` when the money is in near-collapse.

### `metabolic-accounting/investment_signal/` (this module)

Native home for the investment equation and all five failure-mode diagnostics. Sits alongside `money_signal` because investment depends on money; both share the `metabolic-accounting` repo's glucose-flow framing (money signal is short-term flow; investment signal is binding-of-flow across time).

### `thermodynamic-accountability-framework/investment_distribution/`

Not yet built. Distributional analysis of investment asymmetry. Questions it will ask:

- For any investment context, how is the return distributed across observer positions?
- Whose time is converted to money at what rate?
- Who bears the cascade coupling risk?
- Who benefits from the reverse-causation pressure on substrates?
- What does the investment extract from which substrate, and from whose substrate specifically?

Will consume `InvestmentSignal` and produce distributional reports.

### `earth-systems-physics/coupling/investment_as_forcing/`

Not yet built. The physical coupling layer. Investment flows as forcing functions on biosphere, lithosphere, and hydrosphere extraction rates. Key questions:

- What substrate extraction rate does a given investment portfolio imply?
- At what derivative distance does the investment lose visibility into the substrate it extracts from?
- When the investment is financialized (reverse causation), what direction does substrate-use change?

Most structurally dependent of the three. Requires both money-signal and investment-signal to be stable first.

---

## Usage

```python
from investment_signal.dimensions import (
    InvestmentContext, InvestmentSubstrate,
    InvestmentAttribution, DerivativeDistance, TimeBinding,
)
from investment_signal.substrate_vectors import SubstrateVector
from investment_signal.coupling import (
    assemble_investment_signal,
    signal_failure_count,
    signal_failure_reasons,
    validate_all_investment_modules,
)
from money_signal.dimensions import (
    DimensionalContext as MoneyContext,
    TemporalScope, CulturalScope, AttributedValue,
    ObserverPosition, Substrate, StateRegime,
)

# Always validate at startup.
validate_all_investment_modules()

# Build the money context the investment sits inside.
money = MoneyContext(
    temporal=TemporalScope.GENERATIONAL,
    cultural=CulturalScope.INSTITUTIONAL,
    attribution=AttributedValue.STATE_ENFORCED,
    observer=ObserverPosition.TOKEN_HOLDER_THIN,
    substrate=Substrate.DIGITAL,
    state=StateRegime.STRESSED,
)

# Build the investment context.
ctx = InvestmentContext(
    money_context=money,
    attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
    derivative_distance=DerivativeDistance.TWO_LAYER,
    time_binding=TimeBinding.IMMEDIATE,
)

# Describe what is committed and what is expected back.
input_vec = SubstrateVector.from_dict({
    InvestmentSubstrate.MONEY: 50000.0,
    InvestmentSubstrate.ATTENTION: 20.0,
})
expected_vec = SubstrateVector.from_dict({
    InvestmentSubstrate.MONEY: 150000.0,
    InvestmentSubstrate.TIME: 1000.0,
})

# Assemble the signal.
signal = assemble_investment_signal(input_vec, expected_vec, ctx)

print(signal.describe())
print("failure count:", signal_failure_count(signal))
print("failure reasons:", signal_failure_reasons(signal))

Known limitations
	1.	Factor values are first-principles estimates. Empirical calibration against historical investment cases is not yet implemented. Values should be treated as qualitative until a historical_cases.py module is added with measured parameter fits.
	2.	Unit compatibility is the caller’s responsibility. SubstrateVector does not enforce units across substrates because the substrates have incommensurable native units. Callers must document their own unit conventions.
	3.	Composition is multiplicative for the coupling components and additive for vector assembly. Alternative compositions would produce different dynamics. Current choice was made for consistency with money-signal.
	4.	No temporal integration. This module produces a static signal snapshot for a given context. Evolution of the signal across time (rolling, rebalancing, reinvesting) belongs in a future trajectory.py module or in the parent repo’s cascade module.
	5.	No multi-investor modeling. Each InvestmentSignal is produced from a single investor’s observer position. Aggregate behavior (market dynamics, herding, runs) belongs in the distributional module in the accountability repo.
	6.	MIXED cultural scope is a mean. Same caveat as in money_signal; variance across heterogeneous networks is modeled elsewhere.

License
CC0. Public domain. No attribution required. No warranty.
