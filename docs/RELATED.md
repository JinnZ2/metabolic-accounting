# RELATED.md

How `metabolic-accounting` sits among its companion frameworks. All four
repos share an author and an ethos — measurement before narrative, physics
before policy — but they operate at different layers of abstraction and
across different artifact types. This document maps the relationship so a
reader can place any one of them in the context of the others.

## The four repos

| Repo | Layer | What it produces |
| --- | --- | --- |
| [`thermodynamic-accountability-framework`](https://github.com/JinnZ2/thermodynamic-accountability-framework) | **Meta / parent** — organism-agnostic | Methodology for evaluating any system (biological, mechanical, institutional) against five axioms of energy accounting |
| `metabolic-accounting` (this repo) | **Specialization for living systems** | Glucose flow, basin state variables, forced drawdown, verdicts on firm-basin coupling |
| [`PhysicsGuard`](https://github.com/JinnZ2/PhysicsGuard) | **Verification / guardrail** | CLEAN / SUSPECT / CORRUPTED verdicts on claims checked against first law, second law, mass conservation, resilience thresholds |
| [`Logic-Ferret`](https://github.com/JinnZ2/Logic-Ferret) | **Narrative audit** | Fallacy detection and annotation in text / transcripts |

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

Do not attempt to clone or modify the companion repos from this
session. GitHub MCP access in this repo's sessions is scoped to
`jinnz2/metabolic-accounting` only.
