# EXTERNAL_OPERATIONALIZATIONS.md

This document maps the abstract Tier 1 / Tier 2 term audits in
`term_audit/audits/` to candidate operational measurement equations
shipped by the companion repo
[`Mathematic-economics`](https://github.com/JinnZ2/Mathematic-economics)
under its `equations-v1` stable-surface tag.

**Status: pointer document only.** This repo does not import any
math-econ code. The mapping is structural, not a runtime dependency.
A consumer who wants the actual measurements imports from
`Mathematic-economics @ equations-v1`; the audit modules in this repo
remain stdlib-only.

The relationship is documented in `docs/RELATED.md` § "Relationship
to Mathematic-economics". Math-econ already imports this repo's
`money_signal` leaf modules; this doc is the reverse-direction
*citation* contract — what to read in math-econ when an audit here
needs an operationalization.

## The pre-condition: signal-quality discount on currency-denominated equations

Most of the 13 math-econ equations are denominated in dollars or
percentages of dollar quantities. That is exactly the failure mode
this repo's `money_signal/` framework was built to surface: the
unit's signal quality is itself context-dependent (Weimar 1923,
Cyprus 2013, healthy modern fiat all couple very differently — see
`money_signal/historical_cases.py`).

**A money-denominated equation read straight as a measurement
re-introduces the currency bias.** The canonical defensive workflow
is:

1. Construct a `DimensionalContext` for the regime being measured
   (`money_signal/dimensions.py`).
2. Compute the three primitives — minsky coefficient, coupling
   magnitude, sign-flip — via `money_signal/coupling.py` and
   `money_signal/accounting_bridge.signal_quality()`.
3. Treat the math-econ equation's output as the *raw* measurement and
   the signal-quality score as a `[0, 1]` discount factor on its
   informational weight.
4. Carry both the raw value and the discount alongside each other; do
   not collapse them into a single number.

`accounting_bridge.adjust_glucose_flow()` already implements the
analogous discount for `GlucoseFlow.revenue` and related fields; the
same pattern applies here.

## Tier 1 mappings

| Audit module | Audited term | Math-econ candidate measurement(s) | Notes / caveats |
| --- | --- | --- | --- |
| `term_audit/audits/money.py` | `money` | **MSI** (Money Socialist Index, fraction of money supply originating through state or state-licensed mechanisms), **MM** (Money Multiplier, fractional-reserve creation factor), **BSC** (Bailout Socialism Coefficient, ratio of collective rescue to private losses) | Directly addresses `MONEY_AUDIT.signal_scores["conservation_or_law"]` (currently 0.2) — MSI + MM together quantify *why* there is no conservation. BSC operationalizes the regime-shift point in `MONEY_AUDIT.signal_scores["referent_stable"]`. All three are state/year specific and require regime-context flagging via `coupling_state.py`. |
| `term_audit/audits/capital.py` | `capital` (split into K_A productive / K_B financial / K_C institutional) | **VE/VL** (Value-Extraction-to-Labor ratio) bears directly on K_A→K_B substitution; **HHI** (Herfindahl-Hirschman) measures K_B concentration; **SID** (Socialist Infrastructure Dependency) measures K_C's substrate. | The audit's load-bearing claim is that K_A and K_B are reported in identical units yet anti-correlate. VE/VL is one falsifiable expression of that anti-correlation; values >0.1 falsify "Smith's productive-capitalism" framing per math-econ's worked example. |
| `term_audit/audits/value.py` | `value` (split into V_A use / V_B exchange / V_C substrate) | **ER** (Labor Value Extraction Rate, non-labor share of revenue) operationalizes the V_B→V_C negative linkage; **LWR** (Labor Wealth Ratio) operationalizes the V_C→V_B substitution rate at population scale. | The audit's NEGATIVE B→C linkage (exchange-value substitutes for substrate-value) is the load-bearing finding for the entire Tier 1 stack. ER and LWR are the cleanest scalar instrumentations of it shipped in math-econ. |
| (not yet audited here) | `wealth` | **UFR** (Upward Flow Rate, top-1% vs bottom-50% accumulation ratio); **LWR** | When this term is audited, UFR is the falsification anchor for "wealth is generated symmetrically" framing — math-econ measures it ≈30:1 for the current US system. |
| (not yet audited here) | `gross_domestic_product`, `economic_growth` | **OSDI** (composite of SID, MSI, ISR, BSC, MM); the **Smith-compliance scorecard** (0/8 criteria met for current US system) | Both are constructive falsifications of "GDP measures productive capacity" and "growth = capitalist productive expansion" claims. The Smith scorecard pattern is mirrored locally in `term_audit/falsification.py::ComplianceScorecard` — see the cross-reference there. |

## Tier 2 mappings

| Audit module | Audited term | Math-econ candidate measurement(s) | Notes / caveats |
| --- | --- | --- | --- |
| `term_audit/audits/productivity.py` | `productivity` | **VE/VL**, **LWR**, **ER** in combination | The audit redefines real productivity as `output / full_dependency_chain`. The math-econ equations measure the gap between that ratio and the conventional `output_in_dollars / hours_worked`: a falling LWR and rising ER together are the signature of "apparent productivity gain via substrate conversion". |
| `term_audit/audits/efficiency.py` | `efficiency` | **HHI** (concentration as anti-coupling proxy); **ISR** (Infrastructure Subsidy Ratio, market value of public infrastructure consumed vs paid) | The audit reframes efficiency as substrate-coupling density at thermodynamic limit. HHI rising is one symptom of low coupling (concentration kills coupling diversity); ISR rising is direct externalization of substrate cost. Neither is the full vector-space metric the audit wants, but both are falsifiable scalar projections of it. |

## Tier 1 → Tier 2 → Tier 3+ propagation

The math-econ equations inherit the same dependency structure as
this repo's tiers (see `docs/TERMS_TO_AUDIT.md` § "The tiers are not
independent"):

- **Tier 1 equations** (VE/VL, MSI, MM, BSC, HHI) measure the
  foundational fictions directly.
- **Tier 2 equations** (LWR, ER) ride on the currency unit Tier 1
  defines, and inherit its signal-quality limitations.
- **Composite indices** (OSDI) collapse five equations into one
  scalar; this is the same reduction-to-overall pattern flagged in
  `distributional/tiers.py::TierAssignment.overall_tier()` and
  caused Bug 4 in `docs/AUDIT_04.md`. Composite indices should be
  read alongside their components, not in place of them.

## The Semantic Drift Rate (SD) hook

Math-econ ships an SD equation that quantifies how a term's meaning
shifts over time using embedding distance. SD is the cleanest
external operationalization for this repo's `term_audit/scoping.py`
"narrative strip" defense: a term whose SD is high *and* whose
declared scope has not been re-anchored is precisely the failure
mode `term_audit/contradictions.py::detect_narrative_strip` was
written to catch.

There is no integration here yet; this is a noted hook for future
work. A consumer that wants to compute SD for a term in the Tier 1
or Tier 2 list constructs the embeddings externally and passes the
score in alongside the audit.

## What is NOT a candidate measurement

For completeness, math-econ equations that do **not** map cleanly
into this repo's audits as of the date of this document:

- **RI** (Risk Inequality): rides on probability estimates of job
  loss / healthcare loss / wage volatility that are themselves
  measured in an institutional frame the framework audits as
  unstable. Consumers wanting RI should also consume math-econ's
  declaration of its data sources and apply their own scope check.
- **DI** (Democratic Power Distribution variance): operationalizes
  the political-power side; this repo does not yet carry a Tier 3
  political-legitimacy audit that DI would feed into.
- **ISR** as a standalone for `externality` (Tier 7): closer to the
  domain of `reserves/` and `accounting/regeneration.py`. Worth
  noting but not load-bearing here.

## Versioning

Pin to `Mathematic-economics @ equations-v1`. Per math-econ's
`SURFACE.md`, the locked surface includes the 13 equation names,
formulas, top-level YAML keys, unit strings, and dataclass fields
for `FieldSystemState` / `YieldAnalysis` / `FieldSystemReport`.
Calibration knobs (component weights, normalization constants,
threshold choices) may shift without a version bump; therefore,
record the math-econ commit SHA alongside any reproduced numerical
result.

This repo's reciprocal stable-surface tag is `money_signal-v1`
(see `docs/SCHEMAS.md` § "Stable surface tags").
