"""
reserves/pools.py

Reserve state layer.

The framework models three tiers of stress absorption:

  PRIMARY     the basin metric itself (soil.bearing_capacity, air.particulate_load, ...)
              — already modeled in basin_states.

  SECONDARY   a reserve attached to each primary metric. Absorbs stress that
              does not yet register as primary damage. Depletes under load and
              slowly regenerates. Finite, cliff-bearing, same structure as
              basins but one level down.

  TERTIARY    site-shared pools. Shared across basins at a single site:
              - landscape_reserve     (shared by soil + biology)
              - watershed_reserve     (shared by soil + water + biology)
              - airshed_reserve       (shared by air + biology)
              - organizational_reserve (cross-cutting: operator attention,
                                        institutional knowledge — couples
                                        to labor-thermodynamics repo)
              Entropy leaks from secondary into tertiary, and from tertiary
              into the environment, irreversibly.

Everything accumulates in EXERGY-DESTRUCTION-EQUIVALENT UNITS (xdu).
See thermodynamics/exergy.py for the unit basis.

Why per-metric secondary (not pooled per basin):
  Pooling across metrics within a basin would allow bearing-capacity
  reserves to freely cover carbon-fraction depletion, which violates
  the second law — different forms of stored order cannot freely
  convert. Per-metric keeps the physics honest.

Why site-shared tertiary:
  Tertiary reserves are landscape- or institution-scale and genuinely
  are shared across basins at a site. A depleted landscape buffer
  reduces what is available to soil AND biology simultaneously.

Literature anchors for the default rates (see docs/LITERATURE.md):
  - entropy tax scales with cliff distance (Dakos et al. 2019,
    Bärtschi et al. 2024): drift_rate = base + slope * cliff_distance
  - environment loss is small but non-zero even at low degradation
    (Sciubba 2021): base 2% per period
  - past tertiary cliff, environment loss jumps to 20-30% per period
    (hysteresis asymmetry ~1.65x from Nature Water 2025 on drought
    recovery; pollinator recovery requires conditions "much more
    improved" than pre-collapse, Royal Society Interface 2019)
"""

from dataclasses import dataclass, field
from math import inf, isinf
from typing import Dict, List, Optional, Tuple

from thermodynamics.exergy import (
    ExergyFlow, check_nonnegative_destruction, check_closure,
)


# ---------- default rate functions ----------

def default_leak_to_tertiary(cliff_distance: float) -> float:
    """Fraction of secondary drawdown that leaks to tertiary each period.

    Increases with cliff distance — hysteresis worsens with depth of
    degradation (Dakos 2019; Bärtschi 2024).

    At cliff_distance=0 (healthy): 10% base tax
    At cliff_distance=1 (at cliff): 25% tax
    """
    cd = max(0.0, min(1.0, cliff_distance))
    return 0.10 + 0.15 * cd


def default_environment_loss(
    tertiary_fraction_remaining: float,
    past_cliff: bool,
) -> float:
    """Fraction of tertiary pool that dissipates to the environment each period.

    Baseline: 2% per period at any degradation.
    Past cliff: jumps to 25% per period, encoding the
    hysteresis / unrestorability finding. At compound decay this
    produces effectively total loss within a handful of periods,
    which is the honest signal for landscape-scale collapse.
    """
    if past_cliff:
        return 0.25
    # optional mild scaling with depletion even before cliff
    frac_depleted = 1.0 - max(0.0, min(1.0, tertiary_fraction_remaining))
    return 0.02 + 0.03 * frac_depleted


# ---------- secondary reserves ----------

@dataclass
class SecondaryReserve:
    """One reserve attached to one primary metric.

    capacity: maximum xdu this reserve can hold when fully charged
    stock:    current xdu stored; starts at capacity
    cliff:    stock below this value is considered exhausted;
              primary damage no longer absorbed, cascade accelerates
    regen_rate_per_period: passive replenishment when not under load,
              in xdu/period (absolute, NOT fraction)
    leak_fn:  function cliff_distance -> fraction leaked to tertiary
    """
    metric_key: str
    basin_name: str
    capacity: float = 100.0
    stock: float = 100.0
    cliff: float = 20.0
    regen_rate_per_period: float = 1.0
    # tertiary pools this reserve leaks to; names reference TertiaryPool
    tertiary_targets: List[str] = field(default_factory=list)

    def fraction_remaining(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return max(0.0, min(1.0, self.stock / self.capacity))

    def is_exhausted(self) -> bool:
        return self.stock <= self.cliff

    def available_headroom(self) -> float:
        """How much more stress the reserve can absorb before hitting cliff."""
        return max(0.0, self.stock - self.cliff)


# ---------- tertiary pools ----------

@dataclass
class TertiaryPool:
    """Site-shared reserve pool. Drawn by multiple secondary reserves.

    environment_loss_fn: function (fraction_remaining, past_cliff) -> per-period
      loss fraction. This is the second-law signature — some fraction of
      tertiary stock is permanently dissipated no matter what.
    """
    name: str
    capacity: float = 1000.0
    stock: float = 1000.0
    cliff: float = 200.0

    def fraction_remaining(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return max(0.0, min(1.0, self.stock / self.capacity))

    def past_cliff(self) -> bool:
        return self.stock <= self.cliff


# ---------- stress flow: primary ↔ secondary ↔ tertiary ↔ environment ----------

@dataclass
class StressPartition:
    """Result of partitioning one period's stress on one primary metric.

    Every period, a primary metric sees `stress_imposed` xdu of stress.
    This function decides how much shows up as primary damage, how much
    is absorbed by the secondary reserve, and (via the leak mechanism)
    how much of the secondary absorption transmits to the tertiary pool
    and how much of that transmits to the environment.

    The invariant:
        stress_imposed == primary_damage
                        + secondary_drawdown_kept
                        + tertiary_drawdown_kept
                        + environment_loss
    """
    metric_key: str
    basin_name: str
    stress_imposed: float
    primary_damage: float
    secondary_absorbed_total: float
    secondary_drawdown_kept: float         # stayed in secondary
    tertiary_drawdown_kept: float          # reached tertiary, stayed there
    environment_loss: float                 # dissipated beyond recovery
    flows: List[ExergyFlow] = field(default_factory=list)


def partition_stress(
    stress_imposed: float,
    primary_fraction: float,
    secondary: SecondaryReserve,
    tertiary_pools: Dict[str, TertiaryPool],
    overflow_spread_fraction: float = 0.30,
) -> StressPartition:
    """Partition one period's stress on one primary metric.

    primary_fraction: fraction of stress that registers as primary damage
                      given the ramp shape and current cliff distance.
                      Equals ramp(cliff_distance).
    secondary: the reserve for this metric (mutated).
    tertiary_pools: site tertiary pools (mutated) keyed by name. Only
                    the pools in secondary.tertiary_targets are touched.
    overflow_spread_fraction: when the secondary reserve is exhausted,
                    this fraction of the overflow damage ALSO propagates
                    to the tertiary pools before being absorbed at
                    primary. Models the physical reality that unbuffered
                    local damage does not stay local — a collapsed
                    landscape buffer transmits stress outward.

                    Default 0.30 anchored to the hysteresis-asymmetry
                    literature: once past a local tipping point,
                    roughly 25-35% of additional damage manifests as
                    landscape-scale rather than point-scale effects
                    (Scheffer et al. 2009; Dakos et al. 2019).

    The function mutates the reserve stocks and returns the partition.
    Second-law checks are performed by the caller via
    check_closure / check_nonnegative_destruction.
    """
    flows: List[ExergyFlow] = []

    # 1. primary damage: what shows up at the primary metric
    primary_damage = primary_fraction * stress_imposed
    flows.append(ExergyFlow(
        source=f"stress",
        sink=f"{secondary.basin_name}.{secondary.metric_key}:primary",
        amount=primary_damage,
        destroyed=primary_damage,   # primary damage is exergy destruction
        note="primary damage (cascade / failure rate contribution)",
    ))

    # 2. the complement is absorbed by the secondary reserve
    absorbed = max(0.0, stress_imposed - primary_damage)

    # 3. secondary cannot hold more than its headroom; overflow is the
    # damage that would have been absorbed but cannot be.
    # overflow normally routes entirely to primary, but a fraction
    # (overflow_spread_fraction) propagates to tertiary pools instead,
    # modeling the real-world finding that unbuffered damage spreads.
    headroom = secondary.available_headroom()
    overflow_to_tertiary = 0.0
    if absorbed > headroom:
        overflow = absorbed - headroom
        absorbed = headroom
        if secondary.tertiary_targets and overflow_spread_fraction > 0:
            overflow_to_tertiary = overflow * overflow_spread_fraction
            overflow_to_primary = overflow - overflow_to_tertiary
        else:
            overflow_to_primary = overflow
        primary_damage += overflow_to_primary
        flows.append(ExergyFlow(
            source="secondary_overflow",
            sink=f"{secondary.basin_name}.{secondary.metric_key}:primary",
            amount=overflow_to_primary,
            destroyed=overflow_to_primary,
            note=(f"secondary reserve exhausted; "
                  f"{(1.0-overflow_spread_fraction)*100:.0f}% of overflow "
                  "routed to primary"),
        ))
        if overflow_to_tertiary > 0:
            flows.append(ExergyFlow(
                source="secondary_overflow",
                sink="tertiary_spread",
                amount=overflow_to_tertiary,
                destroyed=0.0,    # destruction accounted at tertiary routing below
                note=(f"secondary exhausted; {overflow_spread_fraction*100:.0f}% "
                      "of overflow spreads to tertiary pools"),
            ))

    # 4. compute cliff distance BEFORE drawdown for the leak rate
    frac_before = secondary.fraction_remaining()
    cliff_distance = 1.0 - frac_before

    # 5. fraction of the absorbed stress that leaks onward to tertiary,
    # plus the overflow-spread portion that bypassed secondary entirely
    leak_fraction = default_leak_to_tertiary(cliff_distance)
    leaked = absorbed * leak_fraction + overflow_to_tertiary
    kept_secondary = absorbed - absorbed * leak_fraction

    # 6. draw the kept fraction from secondary stock
    secondary.stock -= kept_secondary
    if secondary.stock < 0:
        # numerical floor — absorbed already clamped at headroom so
        # this should not fire; the guard is defensive
        kept_secondary += secondary.stock
        secondary.stock = 0.0

    flows.append(ExergyFlow(
        source="stress",
        sink=f"{secondary.basin_name}.{secondary.metric_key}:secondary",
        amount=kept_secondary,
        destroyed=kept_secondary,
        note=f"secondary absorption (cliff_distance={cliff_distance:.3f})",
    ))

    # 7. route leaked portion to tertiary pools (evenly split across targets)
    tertiary_kept_total = 0.0
    env_loss_total = 0.0
    targets = secondary.tertiary_targets
    if not targets or leaked <= 0:
        # no tertiary configured -> everything that "leaks" goes straight
        # to environment as honest disclosure of unmodeled destinations
        env_loss_total = leaked
        if leaked > 0:
            flows.append(ExergyFlow(
                source=f"{secondary.basin_name}.{secondary.metric_key}:leak",
                sink="environment",
                amount=leaked,
                destroyed=leaked,
                note="no tertiary pool configured; treated as environment loss",
            ))
    else:
        share = leaked / len(targets)
        for tname in targets:
            pool = tertiary_pools.get(tname)
            if pool is None:
                # configured target doesn't exist; route to environment
                env_loss_total += share
                flows.append(ExergyFlow(
                    source=f"{secondary.basin_name}.{secondary.metric_key}:leak",
                    sink="environment",
                    amount=share,
                    destroyed=share,
                    note=f"tertiary pool '{tname}' not found; environment loss",
                ))
                continue

            # at tertiary, apply environment loss rate
            frac_t = pool.fraction_remaining()
            env_rate = default_environment_loss(frac_t, pool.past_cliff())
            env_from_this = share * env_rate
            kept_in_pool = share - env_from_this

            # reduce pool stock by kept portion
            pool.stock -= kept_in_pool
            if pool.stock < 0:
                # pool overflow — the share exceeded pool headroom;
                # excess goes to environment
                excess = -pool.stock
                pool.stock = 0.0
                env_from_this += excess
                kept_in_pool -= excess

            tertiary_kept_total += kept_in_pool
            env_loss_total += env_from_this
            flows.append(ExergyFlow(
                source=f"{secondary.basin_name}.{secondary.metric_key}:leak",
                sink=f"tertiary:{tname}",
                amount=kept_in_pool,
                destroyed=kept_in_pool,
                note=f"tertiary absorption (env_rate={env_rate:.3f}, "
                     f"past_cliff={pool.past_cliff()})",
            ))
            if env_from_this > 0:
                flows.append(ExergyFlow(
                    source=f"tertiary:{tname}",
                    sink="environment",
                    amount=env_from_this,
                    destroyed=env_from_this,
                    note="tertiary → environment (Gouy-Stodola loss)",
                ))

    return StressPartition(
        metric_key=secondary.metric_key,
        basin_name=secondary.basin_name,
        stress_imposed=stress_imposed,
        primary_damage=primary_damage,
        secondary_absorbed_total=absorbed,
        secondary_drawdown_kept=kept_secondary,
        tertiary_drawdown_kept=tertiary_kept_total,
        environment_loss=env_loss_total,
        flows=flows,
    )


# ---------- per-period passive regeneration ----------

def regenerate_secondary(secondary: SecondaryReserve, periods: float = 1.0) -> float:
    """Passive replenishment when not under load. Returns amount regenerated."""
    if secondary.stock >= secondary.capacity:
        return 0.0
    delta = secondary.regen_rate_per_period * periods
    delta = min(delta, secondary.capacity - secondary.stock)
    secondary.stock += delta
    return delta
