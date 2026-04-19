"""
basin_states/community.py

Community vitality as a load-bearing state variable — the social substrate
on which every firm's operations depend for labor, institutional stability,
permitting cooperation, and local supply-chain function.

Treats social capital the same way we treat environmental capital: as a
thermodynamically-grounded stock that degrades under stress, has finite
capacity, and exhibits cliff behavior below which cascade failure triggers.

Key state properties:

  - economic_security       — employment diversity, wage stability, income
                              adequacy in the surrounding community
  - social_capital          — civic participation, institutional trust, voluntary
                              association density (libraries, unions, religious
                              institutions, clubs)
  - family_formation        — marriage rates, household stability, two-parent
                              household fraction, divorce stability
  - youth_retention         — fraction of youth who remain in or return to
                              the community as adults; inverse of brain-drain
  - generational_knowledge  — capacity of the community to transmit skills,
                              institutional knowledge, and trade competencies
                              across generations
  - civic_engagement        — voting rates, volunteerism, local-meeting attendance,
                              community-board participation

Literature anchors:

  Case & Deaton (2020) — economic decline precedes despair mortality by
    approximately a decade, consistent with a depleting reserve structure
    before primary damage manifests.

  US Joint Economic Committee (2019) — deaths of despair grew from ~65,000
    (1995) to ~158,000 (2018), a 2.43x rise in 23 years, approximately 3.9%
    annual growth during the basin-destruction period.

  Wikipedia / CDC — white non-Hispanic rural/low-education cohort shows
    near 2x national death rate (~1,000/100k vs ~500/100k), indicating
    strong differential vulnerability based on community-vitality depletion.

  Kim (2024, Social Science Research) — higher density of social infrastructure
    (libraries, religious organizations) is associated with lower deaths of
    despair, but the protective effect is observed ONLY in less-disadvantaged
    counties. Nonlinear threshold effect matching cliff physics.

  Penn State CTSI — "decades of loss of industry, loss of social safety
    nets, reduced union membership, stagnant wages, reduced access to higher
    education and the infiltration of opioid drugs" as a stacked-pressure
    mechanism — multi-metric coupled degradation.

Community vitality is not a line item. It is the upstream state that governs:
  labor pool availability and skill depth, permitting cooperation, local
  supply-chain function, institutional reliability, workforce stability,
  and the capacity of the surrounding region to supply the firm with the
  conditions under which it can operate.
"""

from .base import BasinState


def new_community_basin(name: str = "site_community") -> BasinState:
    """A GREEN-tier community vitality basin for a stable, healthy community.

    All metrics normalized 0..1 where 1.0 represents a fully healthy
    GREEN-tier community with strong social infrastructure, low despair
    mortality, high generational retention, and active civic engagement.

    Capacity values above 1.0 represent metrics that can theoretically
    exceed current-baseline "healthy" levels (e.g. a community with
    exceptional civic engagement beyond the current US average).

    Cliff thresholds anchored to literature:
      - economic_security cliff at 0.5: below this level the rural /
        low-education cohort death-rate multiplier engages (Wikipedia,
        Case & Deaton)
      - social_capital cliff at 0.4: below this level the protective
        effect of social infrastructure disappears (Kim 2024)
      - family_formation cliff at 0.5: two-parent household fraction
        and marriage stability are strongly coupled to despair outcomes
      - youth_retention cliff at 0.3: below this, community loses its
        capacity to reproduce labor force and skill base
      - generational_knowledge cliff at 0.3: below this, institutional
        knowledge transfer fails irreversibly within one generation
      - civic_engagement cliff at 0.35: below this, community institutions
        lose capacity to organize collective response to stressors
    """
    return BasinState(
        name=name,
        basin_type="community",
        state={
            "economic_security": 1.0,
            "social_capital": 1.0,
            "family_formation": 1.0,
            "youth_retention": 1.0,
            "generational_knowledge": 1.0,
            "civic_engagement": 1.0,
        },
        capacity={
            "economic_security": 1.0,
            "social_capital": 1.2,         # can exceed baseline in healthy
            "family_formation": 1.0,
            "youth_retention": 1.0,
            "generational_knowledge": 1.2, # can exceed with active transmission
            "civic_engagement": 1.2,
        },
        trajectory={
            "economic_security": 0.0,
            "social_capital": 0.0,
            "family_formation": 0.0,
            "youth_retention": 0.0,
            "generational_knowledge": 0.0,
            "civic_engagement": 0.0,
        },
        cliff_thresholds={
            "economic_security": 0.5,
            "social_capital": 0.4,
            "family_formation": 0.5,
            "youth_retention": 0.3,
            "generational_knowledge": 0.3,
            "civic_engagement": 0.35,
        },
        high_is_bad=set(),   # all community metrics: higher is healthier
        notes=(
            "Community vitality substrate. Upstream of labor pool availability, "
            "permitting cooperation, institutional reliability, and the capacity "
            "of the surrounding region to supply firm operational conditions. "
            "Cliff-crossing triggers behavioral cascade signatures (deaths of "
            "despair, violent crime elevation, family collapse, youth "
            "disengagement, problem gambling prevalence)."
        ),
    )


def new_rural_community_basin(name: str = "rural_community") -> BasinState:
    """A community vitality basin calibrated for rural / low-education context.

    Same structure as new_community_basin, but with starting state closer
    to AMBER baseline reflecting the documented vulnerability of rural
    communities (Wikipedia: ~2x national death rate; Case & Deaton 2020).

    Useful for sites operating in communities already under stress from
    historical industrial decline (Appalachia, Rust Belt, resource-extraction
    regions) where the protective buffers are already partially depleted.
    """
    basin = new_community_basin(name)
    # partial pre-depletion matching rural-cohort literature
    basin.state.update({
        "economic_security": 0.75,
        "social_capital": 0.70,
        "family_formation": 0.65,
        "youth_retention": 0.55,        # brain-drain signature
        "generational_knowledge": 0.60,  # industrial-decline signature
        "civic_engagement": 0.70,
    })
    basin.notes = (
        "Community vitality basin calibrated for rural / low-education context. "
        "Reflects documented pre-depletion in communities affected by "
        "historical industrial decline. Approximately 2x vulnerability "
        "multiplier compared to new_community_basin baseline, matching "
        "rural cohort despair-mortality differential (Case & Deaton 2020; "
        "CDC DoD statistics)."
    )
    return basin
