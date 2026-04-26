Where this goes from here, in priority order:

1. `historical_cases.py` for both `money_signal/` and `investment_signal/`. Populate with Weimar, Argentina, 2008, Bitcoin flash crashes, Roman denarius, Pacific shell networks, Indigenous reciprocity systems, colonial resource-extraction investments, 401k realization rates across generations. Each case tests the framework against measured outcomes. This is the falsifiability work that turns qualitative structure into quantitative claim.

2. `thermodynamic-accountability-framework/money_distribution/` and `investment_distribution/`. Distributional analysis. Who gets what, who bears what risk, who extracts what from whom.

3. `earth-systems-physics/coupling/money_as_constraint/` and `investment_as_forcing/`. Physical coupling into the Earth-system stack. Most structurally dependent; built last.


---

## Audit cross-reference

Priority items as they land across the audit trail:

- **Priority 1 — historical cases**:
  - `money_signal/historical_cases.py`: AUDIT_12 (5: Weimar, Zimbabwe, GFC, Cyprus, Argentina) → AUDIT_18 (+4: Bitcoin, Roman denarius, Yap, Kula) → AUDIT_20 (+2: Haudenosaunee wampum, potlatch suppression) → **AUDIT_22 (+2: Andean ayni, Tambu Tolai)**. Total: **13 anchors**; match 12/13 (Cyprus outlier).
  - `investment_signal/historical_cases.py`: AUDIT_14 Part B (5) → AUDIT_18 (+2: VOC/EIC, 401k) → AUDIT_20 (Congo rubber + ZIRP decomposed into retail/PE/CLO) → **AUDIT_22 (+1: Amazon rubber boom)**. Total: **11 anchors**; match **11/11**.
  - Still `[OPEN]` for future passes: non-Tolai PNG shell-money (kina in other groups), Caribbean sugar plantations, post-colonial successor-state extraction (Mobutu-era Zaire, post-independence African mining concessions). Each remains a per-anchor research pass.

- **Priority 2 — distributional analysis**:
  - Homed in the sister repo per this document. In the metabolic-accounting repo, `distributional/signal_asymmetry.py` ships **in AUDIT_14** (E.4) as an **interface stub + literature index**, not an implementation. The real analytic work is expected to live in `thermodynamic-accountability-framework/money_distribution/` and `investment_distribution/`.
  - Literature anchors identified for the sister-repo work: Piketty-Saez-Zucman Distributional National Accounts (WID.world); Kaplan-Moll-Violante HANK heterogeneity; Darity-Hamilton stratification economics; Harberger fiscal incidence.

- **Priority 3 — earth-systems-physics coupling**:
  - Not yet started. Blocked on priorities 1 and 2 being stable per this document's own sequencing.


---

## Side-quests landed

- **AUDIT_23 § A — Tier 1 morphism graph**: closes AUDIT_07 § C.2
  (inheritance invariant as code). `term_audit/morphism_graph.py`
  + `tests/test_morphism_graph.py`. 9 nodes / 20 edges; weakly
  connected; inheritance invariant HOLDS over all 5 claim pairs.
- **AUDIT_23 § B — counts-consistency table**: 15 load-bearing
  counts declared in `scripts/counts_consistency.py`, tripwired by
  `tests/test_counts_consistency.py`. Catches silent drift between
  STATUS.md / audit-doc claims and codebase reality. 15/15 rows
  match baseline.
- **AUDIT_24 — name-set consistency (bidirectional)**: pattern
  borrowed from Geometric-to-Binary-Computational-Bridge's
  `validate_bridge_contract.py`. `scripts/name_set_consistency.py`
  + `tests/test_name_set_consistency.py`. 3 declared pairs: Tier 1
  audits ↔ morphism graph nodes; counts DECLARED ↔ live keys;
  graph nodes ↔ audit-backed nodes. Complements AUDIT_23 § E
  (scalar) with structural set-equality. 3/3 pairs agree.

