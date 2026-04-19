"""
social_cascade/signatures.py

Behavioral cascade signatures — the primary-damage outputs that appear
when community reserves exhaust and social tertiary pools cross cliff.

These are the social analog of environmental cascade signatures (aquifer
collapse, pollinator extinction, soil desertification). When a community
basin's secondary reserves exhaust and its tertiary pools are depleted,
the stress does not disappear — it reappears in measurable human signatures:

  - deaths of despair (drug, alcohol, suicide)
  - violent crime elevation
  - property crime elevation
  - problem gambling prevalence
  - family collapse (divorce, child welfare cases, single-parent hardship)
  - youth disengagement (school dropout, unemployment, out-of-labor-force)
  - domestic violence

Literature anchors:

  US Joint Economic Committee (2019); CDC WONDER data — deaths of despair
    rose from ~65,000 (1995) to ~158,000 (2018), a 2.43x increase over
    23 years (~3.9% annual growth during basin-destruction period).

  Case & Deaton (2020) — rural / low-education cohort shows ~2x baseline
    despair mortality; mechanism is economic decline → social disintegration
    → behavioral cascade.

  Kim (2024, Social Science Research) — social infrastructure is
    PROTECTIVE but only above a threshold. Below the threshold, protective
    effects disappear — nonlinear cliff behavior matching our physics.

  Wan et al. (2024, Addiction) — gambling expenditure shows panel ARDL
    relationship with crime; effect operates through problem gambling
    pathway (criminal to fund debts + angriness-lowered threshold for
    violence), 0-15 month lag averaging ~4.5 months.

  Grinols & Mustard (2006) — problem gambling increases individual crime
    likelihood by 4.3-8.6%; communities with high gambling venues show
    measurably elevated property crime and embezzlement.

  UNODC (2012) — economic-predictor-to-crime lag: 0-15 months across
    nations, average 4.5 months. Social substrate responds faster to
    basin collapse than the environmental substrate responds to the
    same stress.

Framework treatment:

  Signature rates scale with community basin state and reserve exhaustion,
  following the same physics the environmental cascade uses. The
  per-period signature rate is a function of:
    - current basin state relative to cliff (ramp)
    - fraction remaining of protective social tertiary pool
    - cumulative stress already absorbed (trajectory amplification)

  Baseline rates anchored to published US data; delta-from-baseline
  is the signal we care about (the externalized cost of community
  collapse, above the population-level baseline).

  Just like environmental cascade, the framework does NOT predict
  which individuals exhibit the behavior — it predicts the rate
  elevation at the population level as a function of substrate state.
"""

from dataclasses import dataclass, field
from math import exp
from typing import Dict, List, Optional

from basin_states.base import BasinState


# ---------- baseline rates (US population-level, per 100k per period) ----------
# Anchored to US national data for a GREEN-tier community. Elevation of
# these rates above baseline is what the framework reports as externalized
# cost from community collapse.

BASELINE_DEATHS_OF_DESPAIR = 48.0        # ~158k / 330M pop * 100k, 2018
BASELINE_VIOLENT_CRIME = 400.0            # FBI UCR approximate national rate
BASELINE_PROPERTY_CRIME = 2100.0          # FBI UCR approximate national rate
BASELINE_PROBLEM_GAMBLING_PCT = 1.2       # US adult population pct
BASELINE_DIVORCE_PER_1000 = 2.5           # US marriages per 1000 pop
BASELINE_YOUTH_DISENGAGEMENT_PCT = 11.0   # US 16-24 NEET rate approximate
BASELINE_DV_PER_1000 = 4.0                # US rate per 1000 women, approximate

# rural/low-ed cohort multiplier — the documented ~2x vulnerability
# (CDC, Case & Deaton; Wikipedia DoD demographics)
RURAL_COHORT_MULTIPLIER = 2.0


# ---------- signature elevation calculations ----------


@dataclass
class CommunitySignatures:
    """Per-period behavioral signatures from a community basin and its
    reserves. Rates are expressed relative to the same units as the
    BASELINE_ constants above (deaths per 100k, crimes per 100k, etc.)
    for easy comparison to published population-level data.
    """
    # scalar rates
    deaths_of_despair_rate: float = 0.0          # per 100k per period
    violent_crime_rate: float = 0.0               # per 100k per period
    property_crime_rate: float = 0.0              # per 100k per period
    problem_gambling_prevalence: float = 0.0      # percent of population
    family_collapse_rate: float = 0.0             # per 1000 per period
    youth_disengagement_pct: float = 0.0          # percent
    domestic_violence_rate: float = 0.0           # per 1000 per period

    # deltas from baseline — the externalized-cost signal
    despair_delta: float = 0.0                    # rate - baseline
    violent_crime_delta: float = 0.0
    property_crime_delta: float = 0.0
    gambling_delta: float = 0.0
    family_collapse_delta: float = 0.0
    youth_disengagement_delta: float = 0.0
    dv_delta: float = 0.0

    # composite
    aggregate_externalized_load: float = 0.0      # sum of non-dim deltas

    # state context
    driven_by_metrics: List[str] = field(default_factory=list)  # which
                                                                  # basin
                                                                  # metrics
                                                                  # most
                                                                  # drove the
                                                                  # cascade
    notes: str = ""

    def any_elevated(self, threshold_ratio: float = 0.1) -> bool:
        """True if any signature is elevated more than threshold_ratio
        above baseline (default 10%)."""
        return any([
            self.despair_delta / BASELINE_DEATHS_OF_DESPAIR > threshold_ratio,
            self.violent_crime_delta / BASELINE_VIOLENT_CRIME > threshold_ratio,
            self.property_crime_delta / BASELINE_PROPERTY_CRIME > threshold_ratio,
            self.gambling_delta / BASELINE_PROBLEM_GAMBLING_PCT > threshold_ratio,
            self.family_collapse_delta / BASELINE_DIVORCE_PER_1000 > threshold_ratio,
            self.youth_disengagement_delta / BASELINE_YOUTH_DISENGAGEMENT_PCT > threshold_ratio,
            self.dv_delta / BASELINE_DV_PER_1000 > threshold_ratio,
        ])


def _cliff_distance(state: float, cliff: float, healthy: float = 1.0) -> float:
    """Distance from healthy to cliff, normalized [0..1].
    0 = healthy, 1 = at or past cliff."""
    if healthy <= cliff:
        return 1.0
    return max(0.0, min(1.0, (healthy - state) / (healthy - cliff)))


def _amplification_from_tertiary(
    tertiary_pools: Optional[Dict],
    pool_names: List[str],
) -> float:
    """Amplification factor based on protective tertiary pool status.

    When the protective tertiary is healthy, amplification is near 1.0
    (baseline-like rates). When the tertiary crosses its cliff,
    amplification climbs exponentially up to the rural-cohort
    multiplier, because the community has lost its protective
    social infrastructure (Kim 2024 threshold effect).
    """
    if not tertiary_pools or not pool_names:
        return 1.0
    factors = []
    for name in pool_names:
        pool = tertiary_pools.get(name)
        if pool is None:
            continue
        frac = pool.fraction_remaining()
        # below cliff fraction (0.3 for social pools), amplification
        # grows exponentially toward RURAL_COHORT_MULTIPLIER
        cliff_frac = pool.cliff / pool.capacity if pool.capacity > 0 else 0.3
        if frac >= 1.0:
            factors.append(1.0)
        elif frac > cliff_frac:
            # linear interpolation from 1.0 at healthy to 1.3 at cliff
            below_healthy = 1.0 - frac
            span = 1.0 - cliff_frac
            factors.append(1.0 + 0.3 * (below_healthy / span))
        else:
            # past cliff — exponential climb up to the multiplier
            deficit = (cliff_frac - frac) / cliff_frac if cliff_frac > 0 else 1.0
            amp = 1.3 + (RURAL_COHORT_MULTIPLIER - 1.3) * (1.0 - exp(-3.0 * deficit))
            factors.append(amp)
    if not factors:
        return 1.0
    # take max — the most-depleted pool drives the amplification
    return max(factors)


def compute_community_signatures(
    basin: BasinState,
    secondary_reserves: Optional[Dict] = None,
    tertiary_pools: Optional[Dict] = None,
) -> CommunitySignatures:
    """Compute behavioral cascade signatures from a community basin's
    current state, reserves, and the site's social tertiary pools.

    Each signature is derived from the basin metrics most closely
    coupled to the behavior in the literature:

      - deaths_of_despair: driven by economic_security + social_capital
        + family_formation (all three depleted accelerates the cascade,
        matching the Case & Deaton stacked-pressure mechanism)
      - violent_crime: driven by economic_security + civic_engagement
        + family_formation (UNODC: economic stress plus loss of
        community oversight)
      - property_crime: driven by economic_security + social_capital
        (financial distress + reduced social control)
      - problem_gambling: driven by economic_security + civic_engagement
        (financial desperation + loss of community accountability)
      - family_collapse: driven by family_formation + economic_security
        (direct coupling)
      - youth_disengagement: driven by youth_retention +
        generational_knowledge (brain drain + lost role models)
      - domestic_violence: driven by economic_security + family_formation
        (financial stress + family instability) + problem-gambling pathway
    """
    sig = CommunitySignatures()

    if basin.basin_type != "community":
        sig.notes = ("compute_community_signatures called on non-community "
                     "basin; no signatures computed.")
        return sig

    def _cd(key: str) -> float:
        state = basin.state.get(key, 1.0)
        cliff = basin.cliff_thresholds.get(key, 0.0)
        return _cliff_distance(state, cliff)

    # normalized cliff distances per community metric
    cd_econ = _cd("economic_security")
    cd_social = _cd("social_capital")
    cd_family = _cd("family_formation")
    cd_youth = _cd("youth_retention")
    cd_gen = _cd("generational_knowledge")
    cd_civic = _cd("civic_engagement")

    # amplification from social tertiary pool status
    fabric_amp = _amplification_from_tertiary(
        tertiary_pools, ["social_fabric_reserve"])
    inst_amp = _amplification_from_tertiary(
        tertiary_pools, ["institutional_stock"])
    gen_amp = _amplification_from_tertiary(
        tertiary_pools, ["generational_transmission"])
    trust_amp = _amplification_from_tertiary(
        tertiary_pools, ["civic_trust_reserve"])

    # --- deaths of despair ---
    # triple-driver (economic + social + family), amplified by fabric_amp
    despair_driver = (cd_econ + cd_social + cd_family) / 3.0
    despair_multiplier = 1.0 + despair_driver * (fabric_amp - 1.0 + despair_driver * 2.0)
    sig.deaths_of_despair_rate = BASELINE_DEATHS_OF_DESPAIR * despair_multiplier
    sig.despair_delta = sig.deaths_of_despair_rate - BASELINE_DEATHS_OF_DESPAIR

    # --- violent crime ---
    vcrime_driver = (cd_econ * 0.5 + cd_civic * 0.3 + cd_family * 0.2)
    vcrime_multiplier = 1.0 + vcrime_driver * (trust_amp - 1.0 + vcrime_driver * 1.5)
    sig.violent_crime_rate = BASELINE_VIOLENT_CRIME * vcrime_multiplier
    sig.violent_crime_delta = sig.violent_crime_rate - BASELINE_VIOLENT_CRIME

    # --- property crime ---
    pcrime_driver = (cd_econ * 0.6 + cd_social * 0.4)
    pcrime_multiplier = 1.0 + pcrime_driver * (inst_amp - 1.0 + pcrime_driver * 1.0)
    sig.property_crime_rate = BASELINE_PROPERTY_CRIME * pcrime_multiplier
    sig.property_crime_delta = sig.property_crime_rate - BASELINE_PROPERTY_CRIME

    # --- problem gambling ---
    pg_driver = (cd_econ * 0.5 + cd_civic * 0.5)
    pg_multiplier = 1.0 + pg_driver * 1.5 * trust_amp
    sig.problem_gambling_prevalence = BASELINE_PROBLEM_GAMBLING_PCT * pg_multiplier
    sig.gambling_delta = (sig.problem_gambling_prevalence
                          - BASELINE_PROBLEM_GAMBLING_PCT)

    # --- family collapse ---
    fc_driver = (cd_family * 0.7 + cd_econ * 0.3)
    fc_multiplier = 1.0 + fc_driver * (fabric_amp - 1.0 + fc_driver * 1.2)
    sig.family_collapse_rate = BASELINE_DIVORCE_PER_1000 * fc_multiplier
    sig.family_collapse_delta = (sig.family_collapse_rate
                                  - BASELINE_DIVORCE_PER_1000)

    # --- youth disengagement ---
    yd_driver = (cd_youth * 0.5 + cd_gen * 0.5)
    yd_multiplier = 1.0 + yd_driver * (gen_amp - 1.0 + yd_driver * 1.5)
    sig.youth_disengagement_pct = BASELINE_YOUTH_DISENGAGEMENT_PCT * yd_multiplier
    sig.youth_disengagement_delta = (sig.youth_disengagement_pct
                                      - BASELINE_YOUTH_DISENGAGEMENT_PCT)

    # --- domestic violence ---
    # Economic + family stress, amplified by problem gambling pathway
    # (Wan et al. 2024 — gambling-induced domestic violence)
    gambling_pathway = sig.problem_gambling_prevalence / BASELINE_PROBLEM_GAMBLING_PCT
    dv_driver = (cd_econ * 0.4 + cd_family * 0.6)
    dv_multiplier = 1.0 + dv_driver * (fabric_amp - 1.0 + dv_driver * 1.0) \
                   * (0.5 + 0.5 * gambling_pathway)
    sig.domestic_violence_rate = BASELINE_DV_PER_1000 * dv_multiplier
    sig.dv_delta = sig.domestic_violence_rate - BASELINE_DV_PER_1000

    # --- driven_by_metrics: rank by cliff distance ---
    metric_cds = [
        ("economic_security", cd_econ),
        ("social_capital", cd_social),
        ("family_formation", cd_family),
        ("youth_retention", cd_youth),
        ("generational_knowledge", cd_gen),
        ("civic_engagement", cd_civic),
    ]
    metric_cds.sort(key=lambda x: -x[1])
    sig.driven_by_metrics = [m for m, cd in metric_cds if cd > 0.1][:3]

    # --- aggregate externalized load (non-dimensionalized) ---
    # express each delta as a fraction of its baseline, then sum
    sig.aggregate_externalized_load = sum([
        sig.despair_delta / BASELINE_DEATHS_OF_DESPAIR,
        sig.violent_crime_delta / BASELINE_VIOLENT_CRIME,
        sig.property_crime_delta / BASELINE_PROPERTY_CRIME,
        sig.gambling_delta / BASELINE_PROBLEM_GAMBLING_PCT,
        sig.family_collapse_delta / BASELINE_DIVORCE_PER_1000,
        sig.youth_disengagement_delta / BASELINE_YOUTH_DISENGAGEMENT_PCT,
        sig.dv_delta / BASELINE_DV_PER_1000,
    ])

    return sig


# ---------- BLACK signature logic ----------

def is_social_black(signatures: CommunitySignatures) -> bool:
    """Social BLACK: the community-level irreversibility signal.

    Mirrors environmental BLACK but on the social substrate. Triggers when:
      - deaths of despair rate at or above rural-cohort multiplier
        (~2x baseline), OR
      - aggregate externalized load >= 3.0 (equivalent of 3 signatures
        each at baseline or 1 signature at 3x baseline), OR
      - any single signature >= 2x baseline
    """
    if signatures.deaths_of_despair_rate >= (
            BASELINE_DEATHS_OF_DESPAIR * RURAL_COHORT_MULTIPLIER):
        return True
    if signatures.aggregate_externalized_load >= 3.0:
        return True
    # any single signature past 2x baseline
    ratios = [
        signatures.deaths_of_despair_rate / BASELINE_DEATHS_OF_DESPAIR,
        signatures.violent_crime_rate / BASELINE_VIOLENT_CRIME,
        signatures.property_crime_rate / BASELINE_PROPERTY_CRIME,
        signatures.problem_gambling_prevalence / BASELINE_PROBLEM_GAMBLING_PCT,
        signatures.family_collapse_rate / BASELINE_DIVORCE_PER_1000,
        signatures.youth_disengagement_pct / BASELINE_YOUTH_DISENGAGEMENT_PCT,
        signatures.domestic_violence_rate / BASELINE_DV_PER_1000,
    ]
    return any(r >= 2.0 for r in ratios)
