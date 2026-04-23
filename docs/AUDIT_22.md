# AUDIT 22

Twenty-second audit pass. Scope: extend the historical-case anchor
sets with three more Todo.md priority-1 candidates (Andean ayni,
Tolai tambu shell-money, Amazon rubber boom).

Status key: `[CLOSED]` — fix present and tripwired; `[OPEN]` —
scoped but not implemented.


## Part A — Two new money_signal anchors

### A.1 ANDEAN_AYNI

- **Counter-example** (the fourth in the money_signal set, joining
  Yap, Kula, Haudenosaunee).
- Distinctive for tracking **labor reciprocity** rather than
  shell/object reciprocity — demonstrates the
  RECIPROCITY_TOKEN + TRUST_LEDGER + HIGH_RECIPROCITY combination
  works for LABOR substrate directly.
- Literature: Alberti & Mayer 1974 (*Reciprocidad e intercambio
  en los Andes peruanos*, IEP), Mayer 2002 (*The Articulated
  Peasant*, Westview), Harris 1985 (in Masuda ed. *Andean Ecology
  and Civilization*).
- Scope caveat recorded: Spanish-language primary literature
  carries detail the English-language secondary sources do not.

### A.2 TAMBU_TOLAI

- **Counter-example with a twist**: tambu coexists with PNG kina
  (modern fiat) in Tolai communities, rather than standing alone.
- Distinctive for the **dual-regime** encoding — the test of the
  framework's claim is that TRUST_LEDGER substrates don't require
  monopoly to persist; they occupy a coordination niche alongside
  different-substrate instruments.
- Literature: Epstein 1969 (*Matupit: Land, Politics, and Change
  among the Tolai of New Britain*), Errington & Gewertz 1987,
  Martin 2013 (*The Death of the Big Men and the Rise of the Big
  Shots*, Berghahn).


## Part B — One new investment_signal anchor

### B.1 AMAZON_RUBBER_BOOM_1879_1912

- **Paired with CONGO_RUBBER_1885_1908** — same commodity-demand
  cycle (1890s-1910s global rubber boom), same SYNTHETIC distance
  + EXTRACTIVE_CLAIM structural signature, different colonial
  regimes (Peruvian Amazon Company / Casa Arana at London-listed
  joint-stock vs Leopold's personal kingdom).
- Observed failures: `substrate_invisible_at_distance` (London
  shareholders could not see Huitoto and Bora forced labor until
  Casement 1912), `financialized_reverse_causation` (London yields
  drove concession quotas drove on-the-ground violence),
  `substrate_abstraction_destroys_nature` (30-50k+ Putumayo
  regional mortality; language-group extinction thresholds).
- Literature: Casement 1912 Putumayo Report (Parliamentary Papers
  1913), Hardenburg 1912 (*The Putumayo: The Devil's Paradise*),
  Taussig 1987 (*Shamanism, Colonialism, and the Wild Man*),
  Stanfield 1998 (*Red Rubber, Bleeding Trees*).

**Structural finding.** The Congo + Amazon rubber pair
demonstrates that the framework's structural classification of
SYNTHETIC + EXTRACTIVE regimes is **context-driven, not
regime-specific**. The same Casement who exposed the Congo
atrocities in 1904 was sent to Putumayo in 1910-1911 and found
the same structural failure signature under a different colonial
state. The framework predicts this similarity from the context
shape alone — confirming (at anchor level) that claim #16 / #17 /
#18 / #21 are structural predictions, not post-hoc curve-fits.


## Part C — Match counts and role partitioning

Post-AUDIT_22:

| Subsystem | Anchor cases | Framework match |
| --- | --- | --- |
| money_signal | 13 | **12/13** (Cyprus remains the documented observer-asymmetry outlier) |
| investment_signal | 11 | **11/11** |

Money_signal role partitioning: 6 near-collapse, 2 stressed,
**5 counter-examples** (Yap, Kula, Haudenosaunee, Andean ayni,
Tambu Tolai). The counter-example set is now rich enough to
span four distinct substrate types (shell-disk, armband-necklace
pair, wampum belt, labor-obligation) and two distinct
institutional contexts (standalone and dual-regime-with-fiat).


## Part D — Tests

`tests/test_historical_cases.py`: test 1 expects 13 anchors;
test 6 expects 12/13 match; partitioning updated to include the
two new counter-examples.

`tests/test_investment_historical_cases.py`: test 1 expects 11
anchors; test 5 renamed to `test_5_all_match_post_audit_22`,
expects 11/11 match, with Congo + Amazon paired as the
structural-signature test.

Full regression: **51/51 PASS**.


## Part E — What's NOT done

### E.1 Remaining Todo.md candidates   `[OPEN]`

Still unanchored from Todo.md priority 1:

- **Kina shell-money** in other PNG groups (distinct from the
  Tolai tambu case) — overlapping but distinct dynamics per
  Martin 2013 et al.
- **Caribbean sugar plantations** — could be a separate
  investment_signal anchor paired with the Congo / Amazon rubber
  cases. Literature (Williams 1944, Mintz 1985) is mature;
  shipping it requires the kind of careful multi-century encoding
  AUDIT_20 Part B's COLONIAL_RESOURCE_EXTRACTION case already
  partially covers.
- **Post-colonial successor-state extraction** — Mobutu-era
  Zaire, post-independence African mining concessions — the
  literature is extensive but less commonly integrated into
  framework-style anchors.

Each remains `[OPEN]` for a per-anchor research pass.

### E.2 Empirical K-value extraction   `[OPEN]`

Still research work, not code. Per-case retirement_paths name
the datasets (IEP labor panels, Casement archival materials,
PNG central bank kina/tambu series). Extraction lies outside
this codebase's scope.


## Close-out

- Todo.md priority 1 substantially advanced — 13 money_signal
  anchors + 11 investment_signal anchors with full literature
  grounding and honest-placeholder discipline.
- **Amazon + Congo structural pairing** demonstrates the
  framework's classification is context-driven, not regime-
  specific — an anchor-level validation signal for claims
  #16/#17/#18/#21.
- No regression on any earlier load-bearing invariant.
- Regression: **51/51 PASS**.
