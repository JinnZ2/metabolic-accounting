# RELATED.md

How `metabolic-accounting` sits among its companion frameworks. All five
repos share an author and an ethos — measurement before narrative, physics
before policy — but they operate at different layers of abstraction and
across different artifact types. This document maps the relationship so a
reader can place any one of them in the context of the others.

## The five repos

| Repo | Layer | What it produces |
| --- | --- | --- |
| [`thermodynamic-accountability-framework`](https://github.com/JinnZ2/thermodynamic-accountability-framework) | **Meta / parent** — organism-agnostic | Methodology for evaluating any system (biological, mechanical, institutional) against five axioms of energy accounting |
| `metabolic-accounting` (this repo) | **Specialization for living systems** | Glucose flow, basin state variables, forced drawdown, verdicts on firm-basin coupling |
| [`PhysicsGuard`](https://github.com/JinnZ2/PhysicsGuard) | **Verification / guardrail** | CLEAN / SUSPECT / CORRUPTED verdicts on claims checked against first law, second law, mass conservation, resilience thresholds |
| [`Logic-Ferret`](https://github.com/JinnZ2/Logic-Ferret) | **Narrative audit** | Fallacy detection and annotation in text / transcripts |
| [`Mathematic-economics`](https://github.com/JinnZ2/Mathematic-economics) | **Downstream consumer** — falsifiable economic measurements | 13 versioned structural equations (VE/VL, SID, RI, DI, LWR, MSI, BSC, MM, ISR, UFR, ER, HHI, SD) and the OSDI composite, each with declared data source and falsification clause; pinned via `equations-v1` tag |

## Relationship to TAF (parent)

TAF establishes the general framework: energy in ≥ energy out, entropy
never decreases, narrative labels do not substitute for measurement,
organism-agnosticism (the same physics applies to a bacterium, a firm, or
a civilization). TAF is deliberately domain-free.

`metabolic-accounting` is the specialization to living systems. The mapping:

| TAF concept                    | Expression in `metabolic-accounting`                  |
| ------------------------------ | ----------------------------------------------------- |
| Energy accountant              | `accounting/glucose.py` — `GlucoseFlow`, `compute_flow` |
| Friction / overhead accounting | `cascade/detector.py::cascade_cost`                   |
| Narrative stripper             | Two profit lines (reported vs metabolic) — see `verdict/assess.py` |
| Social overhead accountant     | `distributional/` — per-cohort structural load, institutional fit |
| Root cause depth analyzer      | `cascade/` coupling matrix → basin-state roots of infrastructure failure |
| Organism agnosticism           | `basin_states/base.py::BasinState` is type-agnostic; `basin_type` is declarative |

The specialization adds thermodynamic-reserve accounting (secondary and
tertiary pools in `reserves/`), irreversibility propagation via `math.inf`,
and the specific social substrate (`basin_states/community.py`) that TAF
treats abstractly.

## Relationship to PhysicsGuard (verification)

PhysicsGuard and `metabolic-accounting` enforce the same class of
invariants but at different scopes:

- `thermodynamics/exergy.py` enforces Gouy-Stodola **locally** on every
  reserve partition via `check_closure` and `check_nonnegative_destruction`.
  Exergy destruction ≥ 0 is refused at the source.
- PhysicsGuard enforces Gouy-Stodola **globally** on claims expressed in
  natural language or via its dataclass claim schema, translating them into
  physical constraint equations and returning CLEAN / SUSPECT / CORRUPTED.

A concrete verification interface (see `docs/SCHEMAS.md` for the exact
types): `metabolic-accounting`'s `GlucoseFlow`, `Verdict`, and
`ExergyFlow.destroyed` fields all expose quantities PhysicsGuard could
ingest as physical claims. If `metabolic-accounting` is wired correctly,
PhysicsGuard should return CLEAN on every period's output; a SUSPECT or
CORRUPTED verdict from PhysicsGuard would indicate a bug in the local
check or a configuration error upstream.

There is no runtime integration between the two repos. The interface is
structural (shared invariants, compatible quantities) not code-level.
Neither repo imports from the other and neither should — PhysicsGuard is
a broader claim-verifier; `metabolic-accounting` is a stdlib-only
accounting pipeline.

## Relationship to Mathematic-economics (downstream consumer)

`Mathematic-economics` already imports from this repo. Its
`audit/money_signal_bridge.py` selectively imports
`money_signal.dimensions` and `money_signal.coupling` (deliberately
skipping `money_signal.accounting_bridge` to avoid the `term_audit`
sys.path mutation), constructs a `default_context()` neutral
`DimensionalContext`, and exposes the three primitives — `minsky
coefficient`, `coupling_magnitude`, `sign_flip` — that this repo's
`accounting_bridge.signal_quality()` collapses into a `[0, 1]` score.

The dependency direction is one-way:

- `Mathematic-economics` → `metabolic-accounting`: imports
  `money_signal` leaf modules.
- `metabolic-accounting` → `Mathematic-economics`: cites equations
  (see `docs/EXTERNAL_OPERATIONALIZATIONS.md`); does **not** import
  any code.

There are two practical consequences of this relationship:

1. **Falsifiable per-term operationalizations.** The 13 equations
   under `equations-v1` are the operational measurement layer the
   abstract Tier 1/2 audits in this repo's `term_audit/audits/` were
   waiting for. `docs/EXTERNAL_OPERATIONALIZATIONS.md` maps each
   audited term to its candidate equation(s), with the explicit
   caveat that money-denominated equations must pass through
   `money_signal/accounting_bridge.py` for a signal-quality discount
   before they are read as measurements. Naively adopting them
   re-introduces the currency bias the framework is built to defend
   against.
2. **Stable-surface obligation.** Because the bridge already exists,
   this repo owes downstream a versioned surface. `docs/SCHEMAS.md`
   carries that contract; the working tag for `money_signal` is
   `money_signal-v1`.

`Mathematic-economics` ships its own thermodynamic essays
(`ideology-thermodynamics.md`, `thermodynamic-governance.md`,
`labor_thermodynamics/`) and a vendored `physics_guard/` subtree,
which means PhysicsGuard-style local invariant checking is reachable
from a math-econ session without depending on this repo. That is
the intended topology — none of the five repos depend at runtime on
any other.

## Relationship to Logic-Ferret (narrative audit)

Logic-Ferret is philosophically aligned but not a data-level peer.
`metabolic-accounting` audits the physics of a firm's operations;
Logic-Ferret audits the rhetoric of a firm's (or researcher's)
description of those operations. The two can be used in sequence by a
human analyst:

1. Run `metabolic-accounting` against site data to get verdicts and
   warnings.
2. Run Logic-Ferret against the firm's public communications
   (sustainability reports, regulatory filings, investor decks) to
   flag fallacy patterns.
3. Compare: a firm whose physics verdict is BLACK but whose public
   communications show no matching signal in Logic-Ferret is
   narrative-stripped in TAF's terms.

No code interface exists or needs to. Both tools output annotated
artifacts a human can read side by side.

## What is NOT shared

To avoid accidental coupling:

- **No git submodules.** The repos are independent and will stay
  independent. A submodule would drag TAF's numpy/matplotlib into a
  stdlib-only codebase, Logic-Ferret's Tkinter GUI into a headless
  accounting pipeline, and so on.
- **No shared Python package.** Claims about cross-framework types are
  expressed in `docs/SCHEMAS.md` (shape-level, human-readable), not as
  an enforced import.
- **No reciprocal-edit guarantee.** Links from this repo OUT are
  maintained here; links from the other three repos back are the
  author's choice and live in those repos.

## Pointer map (for AI assistants)

If you are working in `metabolic-accounting` and a user asks you to
reach into or reason about the companion frameworks:

| User intent | Go here |
| --- | --- |
| Theory / axioms for why any of this is physically grounded | TAF `docs/` |
| Verify a specific claim about conservation or entropy | PhysicsGuard |
| Detect rhetorical fallacy in a firm's narrative | Logic-Ferret |
| The accounting pipeline, basins, reserves, verdicts | this repo |
| Falsifiable measurement equations for Tier 1/2 economic terms (with FRED/BLS/Census data sources) | Mathematic-economics @ `equations-v1`; mapped here in `docs/EXTERNAL_OPERATIONALIZATIONS.md` |

Do not attempt to clone or modify the companion repos from this
session. GitHub MCP access in this repo's sessions is scoped to
`jinnz2/metabolic-accounting` only.
