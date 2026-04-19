"""
accounting/regeneration.py

Per-metric regeneration cost functions.

Replaces the single-scalar rate_per_unit_degradation placeholder (old
equation 8) with per-metric cost functions that honor the physics of
each basin variable.

A regeneration cost function maps a BasinState + metric key -> cost
to regenerate one unit of degradation in that metric for one period.

Each function encodes three things:

  1. BASE COST PER UNIT DEGRADATION
     How expensive is it to close one unit of degradation gap?
     Soil carbon: cheap per unit. Aquifer: expensive. Pollinator: very
     expensive. Apex indicator: unbounded.

  2. NONLINEARITY
     Small degradation is usually cheap to reverse. Large degradation
     accelerates cost (exponential, power-law, or hard wall).
     This is the OPPOSITE of the failure cascade, which also accelerates
     — meaning deferred regeneration is doubly punished.

  3. IRREVERSIBILITY
     Some thresholds cannot be crossed and reversed. Once apex predators
     are extinct locally, aquifers collapse structurally, or soil passes
     a desertification threshold, regeneration cost is INFINITE. The
     framework reports this honestly rather than pretending money fixes it.

All functions return a finite cost or math.inf. Math.inf propagates
through required_regeneration_cost and surfaces in the verdict as a
regeneration debt that cannot be paid — which is exactly the truth.
"""

from dataclasses import dataclass
from math import inf, exp
from typing import Callable, Dict, Tuple

from basin_states.base import BasinState


# A regeneration function: takes (basin, key, degradation_fraction) and
# returns cost per unit time to fully close the current degradation gap.
RegenFn = Callable[[BasinState, str, float], float]


@dataclass
class RegenCost:
    """Detailed breakdown of a single regeneration cost calculation."""
    basin_name: str
    metric_key: str
    degradation: float       # 0..1
    base_cost: float         # cost per unit degradation, small-gap limit
    nonlinearity_factor: float   # multiplier applied by the nonlinearity
    irreversible: bool
    total_cost: float        # final reported cost (may be inf)
    notes: str = ""


def _linear_nonlinearity(deg: float) -> float:
    """Linear. No amplification. Useful for well-buffered metrics."""
    return deg


def _convex_nonlinearity(deg: float, power: float = 2.0) -> float:
    """Power-law convex. Small gaps cheap, large gaps expensive."""
    if deg <= 0:
        return 0.0
    return deg ** power


def _exponential_nonlinearity(deg: float, steepness: float = 3.0) -> float:
    """Exponential. Cheap far from cliff, explosive near cliff."""
    if deg <= 0:
        return 0.0
    # normalized so deg=0 -> 0, deg=1 -> exp(steepness)-1 bounded term
    return (exp(steepness * deg) - 1.0) / (exp(steepness) - 1.0) * deg


# ---------- per-metric cost functions ----------

def regen_soil_carbon(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Soil organic carbon. Cheap per unit (cover crops, no-till, compost).
    Time-bounded but not money-bounded. Linear."""
    base = 30.0
    nl = _linear_nonlinearity(deg)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Cover crop, residue retention, compost. Linear cost.",
    )


def regen_soil_bearing(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Bearing capacity. Can be restored via stabilization, re-compaction,
    or geotechnical intervention. Convex — cheap light grading, expensive
    foundation-scale repair."""
    base = 200.0
    nl = _convex_nonlinearity(deg, power=2.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Stabilization, regrading. Convex: accelerates near cliff.",
    )


def regen_soil_aggregation(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Soil aggregation index. Restorable via biology + no-till. Moderate
    cost, slow response. Convex."""
    base = 60.0
    nl = _convex_nonlinearity(deg, power=1.5)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Biological aggregation restoration. Convex.",
    )


def regen_soil_permeability(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Permeability. Restorable while aggregation is intact. Convex. Becomes
    effectively irreversible if aggregation has crossed its cliff —
    you can't regain permeability on dead soil."""
    # check aggregation for structural irreversibility
    agg = basin.state.get("aggregation_index")
    agg_cliff = basin.cliff_thresholds.get("aggregation_index")
    if agg is not None and agg_cliff is not None and agg <= agg_cliff:
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible: aggregation collapsed, permeability cannot "
                  "be restored without rebuilding structure first.",
        )
    base = 80.0
    nl = _convex_nonlinearity(deg, power=1.8)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Requires aggregation to be intact.",
    )


def regen_soil_microbial(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Microbial load. Returns quickly if soil chemistry and moisture are
    workable. Linear with a small base cost."""
    base = 40.0
    nl = _linear_nonlinearity(deg)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Inoculation, organic input. Linear.",
    )


def regen_air_particulate(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Particulate load. Reducible via source control. Linear."""
    base = 100.0
    nl = _linear_nonlinearity(deg)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Source control, emission reduction.",
    )


def regen_air_chemical(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Chemical load (NOx, SOx, VOC). Convex — cheap to cut easy sources,
    expensive to cut residual after low-hanging fruit."""
    base = 150.0
    nl = _convex_nonlinearity(deg, power=1.7)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Emission control. Convex: marginal cost rises.",
    )


def regen_air_oxygen(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Oxygen availability. Site-local recovery is essentially a vegetation
    problem, not an engineering one. Moderate cost, slow."""
    base = 50.0
    nl = _linear_nonlinearity(deg)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Vegetation restoration. Slow but not expensive per unit.",
    )


def regen_air_filter_burden(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Filter burden is a consequence, not a basin. Included so the
    accounting is complete, but the cost is really the cost of reducing
    the upstream loads. Here we charge a token maintenance cost."""
    base = 10.0
    nl = _linear_nonlinearity(deg)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Downstream of air loads. Token accounting only.",
    )


def regen_water_aquifer(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Aquifer level. Expensive and slow. Exponential near cliff because
    collapse of aquifer structure (subsidence, salt intrusion) becomes
    irreversible."""
    # if aquifer is past its cliff and temperature anomaly is severe,
    # structural collapse may have begun — treat as irreversible.
    t_anom = basin.state.get("temperature_anomaly")
    t_cliff = basin.cliff_thresholds.get("temperature_anomaly")
    at_cliff = False
    level = basin.state.get("aquifer_level")
    level_cliff = basin.cliff_thresholds.get("aquifer_level")
    if level is not None and level_cliff is not None and level <= level_cliff * 0.8:
        at_cliff = True
    if at_cliff and t_anom is not None and t_cliff is not None and t_anom >= t_cliff:
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible: aquifer past cliff with thermal stress; "
                  "structural collapse suspected.",
        )
    base = 500.0
    nl = _exponential_nonlinearity(deg, steepness=3.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Managed recharge, extraction reduction. Exponential near cliff.",
    )


def regen_water_surface_flow(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Surface flow. Policy-driven, not engineering-driven. Moderate cost,
    convex."""
    base = 200.0
    nl = _convex_nonlinearity(deg, power=1.5)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Diversion reduction, upstream habitat restoration.",
    )


def regen_water_contamination(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Contamination. Depends on contaminant class. Exponential —
    removing residual concentrations is far more expensive per unit
    than initial cleanup."""
    base = 300.0
    nl = _exponential_nonlinearity(deg, steepness=2.5)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Remediation. Exponential: residual cleanup is expensive.",
    )


def regen_water_temperature(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Temperature anomaly. Local interventions (shading, riparian cover)
    have limited effect if the driver is regional. Moderate cost,
    bounded effectiveness — modeled as convex."""
    base = 100.0
    nl = _convex_nonlinearity(deg, power=1.8)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Riparian shading, intake management. Bounded effectiveness.",
    )


def regen_pollinator(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Pollinator index. Slow to restore. If vegetation cover is also
    past its cliff, treat as irreversible on the firm's time horizon."""
    veg = basin.state.get("vegetation_cover")
    veg_cliff = basin.cliff_thresholds.get("vegetation_cover")
    if veg is not None and veg_cliff is not None and veg <= veg_cliff:
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible on firm horizon: vegetation substrate "
                  "collapsed, pollinators cannot recover without habitat.",
        )
    base = 400.0
    nl = _exponential_nonlinearity(deg, steepness=3.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Habitat restoration, pesticide reduction.",
    )


def regen_microbial_diversity(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Microbial diversity. Partially restorable. Convex."""
    base = 150.0
    nl = _convex_nonlinearity(deg, power=2.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Organic matter input, reduced disturbance.",
    )


def regen_apex_indicator(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Apex indicator species. Past a threshold this is irreversible on the
    firm's horizon — you cannot pay to restore local extinction
    within a planning cycle. Below the cliff: infinite. Above: costly
    but finite."""
    cliff = basin.cliff_thresholds.get(key)
    state = basin.state.get(key)
    if cliff is not None and state is not None and state <= cliff:
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible: apex species below local viability cliff.",
        )
    base = 800.0
    nl = _exponential_nonlinearity(deg, steepness=4.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Habitat, corridor connectivity, prey base management.",
    )


def regen_vegetation_cover(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Vegetation cover. Restorable with time and water. Convex."""
    base = 100.0
    nl = _convex_nonlinearity(deg, power=1.5)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Planting, grazing management. Convex.",
    )


# ---------- community vitality regeneration ----------
#
# Social capital regenerates MORE SLOWLY than environmental capital
# once depleted. Literature (Case & Deaton 2020) shows social-capital
# decline preceding despair mortality by roughly a decade, and the
# institutions that host social capital (unions, religious communities,
# local press, fraternal organizations) do not reconstitute within a
# firm's planning horizon once hollowed out.
#
# Base costs are calibrated at approximately 3x environmental costs
# on a per-unit-degradation basis, reflecting the ~0.3x regeneration
# rate noted in research (social institutions take ~3x as long to
# rebuild as comparable environmental stocks).
#
# Cliff-crossing triggers irreversibility for TWO metrics in particular:
#   - generational_knowledge: competence extinction, per Kavik's
#     labor-thermodynamics work. Once the Mighty Atoms are gone,
#     no amount of firm spend reconstitutes their knowledge within
#     a generation.
#   - youth_retention: below the cliff, brain-drain becomes
#     self-reinforcing. Each departing cohort further reduces the
#     peer network that would retain the next cohort. Self-reinforcing
#     depletion, not recoverable by firm action alone.


def regen_economic_security(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Economic security. Partially restorable through wage stabilization,
    employment diversification, local procurement. Convex cost structure."""
    base = 300.0
    nl = _convex_nonlinearity(deg, power=2.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Wage stabilization, local procurement, employment diversification.",
    )


def regen_social_capital(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Social capital (civic participation, institutional trust).
    Slow to restore — institutions take years to re-establish once
    hollowed out. Exponential near cliff because the protective
    effect of social infrastructure disappears below a threshold
    (Kim 2024, Social Science Research)."""
    cliff = basin.cliff_thresholds.get(key)
    state = basin.state.get(key)
    if cliff is not None and state is not None and state <= cliff * 0.5:
        # deep past the cliff — institutional reconstitution is outside
        # the firm's planning horizon
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible on firm horizon: social infrastructure "
                  "below protective threshold; institutions take >1 "
                  "generation to reconstitute.",
        )
    base = 450.0
    nl = _exponential_nonlinearity(deg, steepness=3.5)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Supporting local institutions, civic infrastructure, "
              "voluntary associations. Exponential near cliff.",
    )


def regen_family_formation(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Family formation stability. Strongly coupled to economic security
    and social capital — cannot be regenerated independently if those
    are depleted. Convex."""
    econ = basin.state.get("economic_security")
    econ_cliff = basin.cliff_thresholds.get("economic_security")
    if econ is not None and econ_cliff is not None and econ <= econ_cliff:
        # economic substrate collapsed — family formation cannot stabilize
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible without restoring economic substrate: "
                  "family formation collapse tracks economic despair.",
        )
    base = 350.0
    nl = _convex_nonlinearity(deg, power=2.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Household stability support, childcare infrastructure, "
              "housing affordability.",
    )


def regen_youth_retention(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Youth retention. Below cliff this is self-reinforcing
    (brain-drain cascade): each departing cohort reduces the peer
    network that would retain the next. Treat as irreversible on
    firm horizon once past cliff."""
    cliff = basin.cliff_thresholds.get(key)
    state = basin.state.get(key)
    if cliff is not None and state is not None and state <= cliff:
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible: brain-drain cascade below self-sustaining "
                  "threshold. Each departing cohort reduces the peer "
                  "network that would retain the next cohort.",
        )
    base = 500.0
    nl = _exponential_nonlinearity(deg, steepness=4.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Local opportunity creation, housing affordability, career "
              "pathways. Exponential near cliff.",
    )


def regen_generational_knowledge(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Generational knowledge transfer capacity.

    Competence extinction (per labor-thermodynamics framework): once
    the knowledge-holders are gone, no amount of firm spend
    reconstitutes their knowledge within a generation. The Mighty Atom
    archetype — high actual capacity, near-zero certification signal —
    is exactly the kind of knowledge that evaporates first under
    community-vitality stress.

    Past cliff: infinite. Approaching cliff: exponential."""
    cliff = basin.cliff_thresholds.get(key)
    state = basin.state.get(key)
    if cliff is not None and state is not None and state <= cliff:
        return RegenCost(
            basin_name=basin.name, metric_key=key, degradation=deg,
            base_cost=inf, nonlinearity_factor=1.0, irreversible=True,
            total_cost=inf,
            notes="Irreversible: competence extinction. Knowledge-holders "
                  "who leave a collapsing community take institutional and "
                  "trade knowledge that cannot be reconstituted within a "
                  "firm's planning horizon.",
        )
    base = 700.0
    nl = _exponential_nonlinearity(deg, steepness=4.5)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Apprenticeship programs, local trade schools, mentorship "
              "pipelines. High base cost, strong nonlinearity near cliff.",
    )


def regen_civic_engagement(basin: BasinState, key: str, deg: float) -> RegenCost:
    """Civic engagement (voting, volunteerism, local-meeting attendance).
    More recoverable than deep institutional capital but still convex —
    re-engagement takes sustained effort and credibility that firms
    with recent BLACK history lack."""
    base = 250.0
    nl = _convex_nonlinearity(deg, power=2.0)
    return RegenCost(
        basin_name=basin.name, metric_key=key, degradation=deg,
        base_cost=base, nonlinearity_factor=nl, irreversible=False,
        total_cost=base * nl,
        notes="Local institutional support, transparent engagement, "
              "community-board funding. Convex.",
    )


# ---------- registry ----------

# Mapping from (basin_type, metric_key) to regeneration function.
# basin_type is a normalized identifier ("soil", "air", "water", "biology"),
# NOT the user-given basin name ("site_soil", "farm_north_soil", etc).
# This means the registry works regardless of how a firm names its basins.
#
# Defaults can be overridden per site or per firm by constructing a
# custom registry and passing it to required_regeneration_cost_detailed.

DEFAULT_REGISTRY: Dict[Tuple[str, str], RegenFn] = {
    ("soil", "carbon_fraction"): regen_soil_carbon,
    ("soil", "bearing_capacity"): regen_soil_bearing,
    ("soil", "aggregation_index"): regen_soil_aggregation,
    ("soil", "permeability"): regen_soil_permeability,
    ("soil", "microbial_load"): regen_soil_microbial,

    ("air", "particulate_load"): regen_air_particulate,
    ("air", "chemical_load"): regen_air_chemical,
    ("air", "oxygen_availability"): regen_air_oxygen,
    ("air", "filter_burden"): regen_air_filter_burden,

    ("water", "aquifer_level"): regen_water_aquifer,
    ("water", "surface_flow"): regen_water_surface_flow,
    ("water", "contamination_load"): regen_water_contamination,
    ("water", "temperature_anomaly"): regen_water_temperature,

    ("biology", "pollinator_index"): regen_pollinator,
    ("biology", "microbial_diversity"): regen_microbial_diversity,
    ("biology", "apex_indicator"): regen_apex_indicator,
    ("biology", "vegetation_cover"): regen_vegetation_cover,

    ("community", "economic_security"): regen_economic_security,
    ("community", "social_capital"): regen_social_capital,
    ("community", "family_formation"): regen_family_formation,
    ("community", "youth_retention"): regen_youth_retention,
    ("community", "generational_knowledge"): regen_generational_knowledge,
    ("community", "civic_engagement"): regen_civic_engagement,
}


# Set of known (basin_type, metric_key) pairs. Used by strict mode to
# detect silent misses — a basin of a known type with a known metric key
# should always match a registered function.
KNOWN_METRICS = frozenset(DEFAULT_REGISTRY.keys())


class UnregisteredMetricError(LookupError):
    """Raised in strict mode when a known basin-type metric has no
    registered regeneration function. This catches the silent-miss
    failure mode where a user renames a basin or adds a metric without
    registering its cost function."""
    pass
