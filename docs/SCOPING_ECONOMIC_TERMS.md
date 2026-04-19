# SCOPING_ECONOMIC_TERMS.md

**Intended audience:** AI assistants, human contributors, and reviewers
working on this repository. If you are being asked to reason about
money, capital, investment, value, profit, productivity, efficiency, or
any currency-denominated quantity — read this first.

## Why this document exists

Economics is integrated deeply enough into modern training corpora that
most AI systems (and most human readers) treat its vocabulary as
settled measurement science. It is not. The vocabulary is a set of
tokens that occupy signal-shaped positions in discourse without
satisfying the information-theoretic criteria for being signals
(scope_defined, unit_invariant, referent_stable, calibration_exists,
observer_invariant, conservation_or_law, falsifiability — see
`term_audit/schema.py`).

This produces a specific failure mode in AI-assisted work on a
physics-grounded accounting framework: the AI drags in the
training-bias framing of economics as measured-science, silently
re-anchors numerical claims to currency units, and collapses distinct
referents onto a single token. The user then has to catch the drift
manually, repeatedly. The `money` audit in
`term_audit/audits/money.py` names the failure: money fails 7 of 7
signal criteria at threshold 0.7.

This document is the corrective. It enumerates the dimensions that
would need to be declared for an economic term to function as a
measurement, and it walks through worked expansions for three
commonly-abused terms (money, capital, investment) so the
multiplicative explosion of referents is visible.

Use this as the reading-order entry point before any request that
invokes an economic term.

## The scoping problem in one paragraph

"Money" is not one variable. It is a bundle of at least twelve
distinguishable measurables (M0 through M3, reserve balances, legal
tender claims, units of account, stores of value, mediums of exchange,
credit claims, settlement tokens, and several more). These measurables
do not share a common unit, a common conservation law, a common
calibration procedure, or a common referent. Using the token "money"
in measurement context without declaring which of the twelve (or
more) you mean is a narrative strip: the listener assumes one
measurable, the speaker invoked another, and the numerical claim
floats free of any specific referent. The same structure applies,
with different splits, to capital, investment, value, productivity,
efficiency, income, wealth, and most other economic vocabulary.

## The dimensions of variance

The scoping dimensions are codified in `term_audit/scoping.py` as
`SCOPING_DIMENSIONS`. Briefly, each declaration must supply:

| Dimension | Why it matters |
| --- | --- |
| `referent` | Which of the term's candidate referents is being invoked — the physical, informational, or legal quantity |
| `jurisdiction` | US federal / EU / UK / state — changes what a "security" or "capital" legally is |
| `time_horizon` | Instantaneous / period / cumulative / discounted — a dollar on a 30-year bond is not a dollar on a spot trade |
| `legal_regime` | Contract / tax / bankruptcy / property / securities — different claim priority and enforceability |
| `counterparty_class` | Retail / institutional / sovereign / inter-bank — settlement finality and credit risk differ |
| `measurement_context` | Transaction / accounting entry / forecast / disclosure / regulatory filing / tax return |
| `calibration_procedure` | The reproducible mapping from declared amount to referent — without this, the number is a label |
| `standard_setter` | Who defines the term here and what their incentive structure is (see `term_audit/schema.py::StandardSetter`) |
| `stock_or_flow` | Balance at a point vs quantity per period — crossing this is a silent category error |
| `nominal_or_real` | Raw currency vs price-level-adjusted, plus which deflator |
| `gross_or_net` | Before or after offsets, and which offsets under which convention |
| `asset_class_or_sector` | Equity / debt / real / intangible / commodity / currency — "capital" means different things per class |
| `accounting_basis` | Cash / accrual / fair value / historical cost / mark-to-market / mark-to-model |
| `aggregation_level` | Individual / household / firm / sector / national / global — aggregation destroys information |
| `observer_role` | Participant / third-party / regulator / auditor — changes which fields are observable vs imputed |

A declaration missing any of these is partial. The `DeclaredScope`
dataclass surfaces `missing_dimensions()` and `scoping_fraction()` so
the under-scoping is explicit rather than hidden.

## Worked expansion: money

Money splits, at minimum, into the following distinct measurables.
Each has its own unit, its own calibration procedure, and its own
standard-setter. Treating any two of these as interchangeable is the
core of the narrative strip.

**Monetary aggregates (stock, central-bank defined):**

1. **M0 / monetary base** — physical currency in circulation plus
   reserve balances at the central bank. Conservation: controlled by
   open-market operations.
2. **M1** — M0 + checking deposits. Conservation: breaks at credit
   creation / destruction by commercial banks.
3. **M2** — M1 + savings deposits and small time deposits below a
   threshold. Threshold varies by jurisdiction and revision.
4. **M3** — M2 + larger time deposits, institutional money market
   funds, repurchase agreements. No longer published by the US Fed
   since 2006.

**Functional splits (the classic textbook three, each a different
referent):**

5. **Unit of account** — a denomination for expressing prices and
   writing contracts. Does not require the unit to hold value or to be
   exchangeable; pure labeling function.
6. **Medium of exchange** — an object accepted in settlement of a
   transaction. In a jurisdiction with legal tender laws, a subset of
   this is enforceable; the rest is conventional.
7. **Store of value** — an object expected to retain purchasing power
   across time. Requires declaring which horizon, which price level,
   which deflator.

**Claim structure:**

8. **Legal tender claim** — a tokenized claim on the issuing authority,
   enforceable for debts under the relevant jurisdiction's statute.
9. **Credit money** — a bank's promise to deliver legal tender on
   demand or at a specified time. Can default. Not conserved.
10. **Settlement asset** — what central banks and clearing houses use
    for final settlement (reserve balances, not deposits). Different
    quantity from M1/M2.

**Functional denomination:**

11. **Currency** (USD, EUR, JPY, etc.) — each currency has its own
    issuer, jurisdiction, and conversion rate. "Money" without
    currency declared is under-scoped even within a single country
    (USD-denominated Eurodollar deposits are distinct from Fed-issued
    USD).
12. **Commodity-backed vs fiat vs crypto** — the underlying collateral
    structure changes what the token represents.

When someone says "I have $10,000 in money," the under-scoping hides
at least: is it M0 or M1? Is it a bank deposit (credit money, subject
to bank default) or physical currency? Is the number a stock at an
instant or an average flow? In which jurisdiction? Adjusted for which
deflator? Under which accounting basis? Each combination is a
different claim, and the twelve referents above generate more than
2,000 distinct well-formed sentences that could all be abbreviated as
"I have $10,000 in money."

## Worked expansion: capital

"Capital" has at least the following distinct referents. This repo
already takes a position on two of them (natural capital as basin
states, social capital as the community basin); the rest it declines
to price.

**Physical / produced:**

1. **Fixed capital** — long-lived produced means of production
   (machinery, buildings, infrastructure). Stock.
2. **Working capital** — short-term liquid assets used in operations
   (inventory, receivables minus payables). Stock, period-measured.
3. **Inventory capital** — goods in stock for sale or use. Stock.

**Financial:**

4. **Equity capital** — residual claims on a firm after liabilities.
   Stock, multiple valuation bases (book, market, fair-value).
5. **Debt capital** — claims with priority over equity. Stock, with
   maturity structure.
6. **Regulatory capital (banking)** — Tier 1, Tier 2, Common Equity
   Tier 1. Defined by regulators (Basel III), not by accounting.
   Changes with rule revisions.
7. **Economic capital** — risk-weighted capital a firm needs to
   survive a stress scenario at a confidence level. Model-dependent.
8. **Venture capital** — stage-specific financing of early-stage
   firms. Time-horizon-specific.

**Non-produced / extra-financial:**

9. **Natural capital** — stocks of ecosystem-service-providing assets
   (this repo's `basin_states/`). Not priced; tracked in xdu.
10. **Social capital** — network density, trust, institutional
    stock (this repo's `community` basin + social tertiary pools).
    Not priced; tracked in xdu.
11. **Human capital** — stock of skills, health, education embodied
    in people. Highly contested whether this is "capital" at all.
12. **Intellectual capital** — patents, know-how, trade secrets,
    codified processes. Legally-constructed asset class.
13. **Cultural capital** (Bourdieu) — accumulated cultural
    competence that confers social advantage. Not a financial category.

Saying "the firm is investing in capital" without declaring which of
these thirteen is under-scoped by a factor of at least thirteen.

## Worked expansion: investment

"Investment" similarly splits. The split matters because "invest"
language is frequently applied to expenses, transfers, or consumption
to upgrade their perceived legitimacy.

**Real investment (additions to productive capacity):**

1. **Capital expenditure / capex** — spending that produces a new
   fixed-capital asset or materially extends an existing one.
2. **R&D spending** — spending on research and development; may or
   may not produce an accounting asset depending on jurisdiction and
   phase (IFRS capitalizes later-stage development; US GAAP expenses
   most R&D).
3. **Inventory investment** — increase in stocks of unsold goods.
4. **Residential investment** — new housing construction.
5. **Infrastructure investment** — public or private additions to
   roads, utilities, networks.
6. **Education / training investment** — spending that adds to human
   capital stock (if you accept that category).

**Financial investment (asset purchase, no new productive capacity):**

7. **Portfolio investment** — purchase of existing securities.
   Transfers ownership; does not add real capital.
8. **Foreign direct investment (FDI)** — acquisition of controlling
   stake in a foreign firm. May or may not add real capital depending
   on whether it funds new plant or just transfers ownership.
9. **Private-equity / buyout investment** — purchase of a firm,
   possibly leveraged. Often reduces productive capacity on net.
10. **Venture investment** — funding of early-stage firms. Sometimes
    real (funds payroll + equipment), sometimes financial (secondary
    share purchase).

**Expense disguised as investment:**

11. **"Investment" in marketing / brand / compliance / benefits** —
    operating expenses re-labeled to reduce expense-line salience.
    Accounting treats as expense; narrative treats as investment.
12. **Consumption re-labeled** — "investing in yourself" applied to
    consumption. Not investment in any accounting or economic sense.

The real-vs-financial distinction is load-bearing and is consistently
hidden in common usage. "The economy invested $5 trillion last year"
typically aggregates (1–6), (7–10), and sometimes (11–12). Any policy
inference from such a number is under-scoped.

## The declare-before-using checklist

Before emitting a sentence that claims a numerical measurement using
"money," "capital," "investment," "value," "profit," or any
currency-denominated quantity, supply at minimum:

1. **Which referent** are you invoking? (From the worked-expansion
   lists above, or an equivalent explicit enumeration.)
2. **Which jurisdiction** is the definition from?
3. **Stock or flow**, and **which period** if flow?
4. **Nominal or real**, and **which deflator** if real?
5. **Which calibration procedure** maps the number to the referent?

If you cannot supply these, the sentence is either under-scoped (fine
as a pointer, not as a measurement) or the number is a label (not a
measurement at all). In a physics-grounded framework, label-numbers
must not be mixed with measurement-numbers in the same calculation —
doing so produces results that look quantitative while being rhetorical.

For full rigor, use `term_audit.scoping.DeclaredScope` with all fifteen
`SCOPING_DIMENSIONS`. `is_adequately_scoped()` returns True iff every
dimension has a non-empty declaration.

## What this document does NOT claim

- **Not that economic terms are useless.** Tokens can coordinate
  behavior even without being measurements. "Money" works as a
  settlement convention; it just does not work as a measurement of
  value without further declaration.
- **Not that economics is pseudoscience.** Specific sub-areas of
  economics (mechanism design, auction theory, parts of labor
  economics, household-level empirical work) operate with well-scoped
  quantities and satisfy most signal criteria. The critique is of
  unscoped vocabulary in aggregate and policy discourse.
- **Not that xdu fixes everything.** The `xdu` unit
  (`thermodynamics/exergy.py`) satisfies more signal criteria than
  currency does, but it still requires declared calibration procedures
  for specific basin types. See `reserves/defaults.py` for the
  literature anchors.

## Reading order for AI assistants

When a user request invokes an economic term in measurement context,
the ordered reading is:

1. This document (you are here).
2. `term_audit/schema.py` — the scoring axes.
3. `term_audit/scoping.py` — the dimensions you must declare.
4. `term_audit/audits/money.py` — a worked audit showing what a
   7-of-7 failure looks like.
5. `docs/SCHEMAS.md` — the quantities this repo exposes in `xdu`
   rather than in currency, which is where the scoping discipline
   is already applied.
6. `docs/RELATED.md` — the companion frameworks, including TAF's
   narrative-stripper concept this document operationalizes.

If a user request seems to require silently re-anchoring a
calculation to currency units, stop and ask. Declaring scope is
cheap; unscoped calculation is the failure mode this repo exists
to prevent.
