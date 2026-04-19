"""
reserves/site.py

Site-level reserve coordinator.

One Site holds:
  - basin states (primary metrics)                    [from basin_states]
  - secondary reserves (per basin, per metric)        [reserves.pools]
  - tertiary pools (site-shared)                      [reserves.pools]
  - an exergy flow ledger                             [thermodynamics.exergy]

step(stress) advances one period:
  1. computes primary_fraction for each metric (ramp(cliff_distance))
  2. partitions stress through primary / secondary / tertiary / environment
  3. verifies first-law closure at every metric
  4. applies passive regeneration on all secondary reserves
  5. records the full flow ledger

The site exposes an aggregated view that can feed back into the
existing cascade + accounting pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from basin_states.base import BasinState
from cascade.ramp import RampFn, DEFAULT_RAMP
from cascade.detector import _cliff_distance
from thermodynamics.exergy import (
    ExergyFlow, ThermodynamicViolation,
    check_closure, check_nonnegative_destruction,
)

from .pools import (
    SecondaryReserve, TertiaryPool, StressPartition,
    partition_stress, regenerate_secondary,
)
from .defaults import (
    new_standard_tertiary_pools, new_secondary_reserves_for_basin,
)


@dataclass
class SiteStepResult:
    """Result of one step(stress) call on a site."""
    partitions: List[StressPartition] = field(default_factory=list)
    total_imposed: float = 0.0
    total_primary: float = 0.0
    total_secondary_kept: float = 0.0
    total_tertiary_kept: float = 0.0
    total_environment: float = 0.0
    flows: List[ExergyFlow] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Site:
    """A site is one coherent location. It binds basins to their
    reserves and tertiary pools.

    Carries cumulative counters so a BLACK verdict can be triggered on
    cumulative environment loss even when no single period was severe.
    """
    name: str
    basins: Dict[str, BasinState] = field(default_factory=dict)
    secondary: Dict[str, Dict[str, SecondaryReserve]] = field(default_factory=dict)
    # ^ secondary[basin_name][metric_key] -> SecondaryReserve
    tertiary: Dict[str, TertiaryPool] = field(default_factory=dict)
    ramp: Optional[RampFn] = None   # uses DEFAULT_RAMP if None
    strict: bool = False            # raises on thermodynamic violations if True
    # cumulative counters — cross-period memory for irreversible quantities
    cumulative_environment_loss: float = 0.0
    cumulative_tertiary_drawdown: float = 0.0
    periods_elapsed: int = 0

    def attach_defaults(self) -> None:
        """Populate secondary reserves and tertiary pools for all
        basins currently on the site using the library defaults."""
        if not self.tertiary:
            self.tertiary = new_standard_tertiary_pools()
        for name, basin in self.basins.items():
            if name in self.secondary:
                continue
            b_type = getattr(basin, "basin_type", "") or ""
            self.secondary[name] = new_secondary_reserves_for_basin(
                basin_type=b_type,
                basin_name=name,
                metric_keys=list(basin.state.keys()),
            )

    def step(
        self,
        stress: Dict[Tuple[str, str], float],
        regenerate: bool = True,
    ) -> SiteStepResult:
        """Advance one period.

        stress: mapping (basin_name, metric_key) -> xdu of stress imposed
                on that primary metric this period. Values must be >= 0.

        Returns a SiteStepResult with the full partition, flows, and
        totals. Raises ThermodynamicViolation in strict mode; warns
        otherwise.
        """
        ramp = self.ramp if self.ramp is not None else DEFAULT_RAMP
        result = SiteStepResult()

        for (basin_name, key), imposed in stress.items():
            if imposed < 0:
                msg = (f"negative stress {imposed} at "
                       f"{basin_name}.{key} — ignored")
                if self.strict:
                    raise ThermodynamicViolation(msg)
                result.warnings.append(msg)
                continue
            if imposed == 0:
                continue

            basin = self.basins.get(basin_name)
            if basin is None:
                result.warnings.append(
                    f"stress targeted {basin_name}.{key} but basin "
                    f"{basin_name} not found on site {self.name}"
                )
                continue
            reserves_for_basin = self.secondary.get(basin_name, {})
            reserve = reserves_for_basin.get(key)
            if reserve is None:
                result.warnings.append(
                    f"no secondary reserve for {basin_name}.{key} — "
                    "routing full stress to primary damage"
                )
                # synthesize a partition that dumps everything as primary
                result.partitions.append(StressPartition(
                    metric_key=key, basin_name=basin_name,
                    stress_imposed=imposed, primary_damage=imposed,
                    secondary_absorbed_total=0.0,
                    secondary_drawdown_kept=0.0,
                    tertiary_drawdown_kept=0.0,
                    environment_loss=0.0,
                    flows=[ExergyFlow(
                        source="stress",
                        sink=f"{basin_name}.{key}:primary",
                        amount=imposed, destroyed=imposed,
                        note="no secondary reserve configured",
                    )],
                ))
                result.total_imposed += imposed
                result.total_primary += imposed
                continue

            # compute primary fraction from current cliff distance
            cd = _cliff_distance(basin, key)
            primary_fraction = ramp(cd)

            partition = partition_stress(
                stress_imposed=imposed,
                primary_fraction=primary_fraction,
                secondary=reserve,
                tertiary_pools=self.tertiary,
            )
            result.partitions.append(partition)
            result.flows.extend(partition.flows)

            # second-law checks
            for flow in partition.flows:
                try:
                    check_nonnegative_destruction(
                        flow.destroyed,
                        context=f"{flow.source}->{flow.sink}",
                    )
                except ThermodynamicViolation as e:
                    if self.strict:
                        raise
                    result.warnings.append(f"[thermo] {e}")

            # closure invariant on this metric
            try:
                check_closure(
                    imposed=partition.stress_imposed,
                    primary=partition.primary_damage,
                    secondary=partition.secondary_drawdown_kept,
                    tertiary=partition.tertiary_drawdown_kept,
                    environment=partition.environment_loss,
                    context=f"{basin_name}.{key}",
                )
            except ThermodynamicViolation as e:
                if self.strict:
                    raise
                result.warnings.append(f"[closure] {e}")

            # tally
            result.total_imposed += partition.stress_imposed
            result.total_primary += partition.primary_damage
            result.total_secondary_kept += partition.secondary_drawdown_kept
            result.total_tertiary_kept += partition.tertiary_drawdown_kept
            result.total_environment += partition.environment_loss

        # passive regeneration of secondary reserves
        if regenerate:
            for basin_name, reserves in self.secondary.items():
                for key, reserve in reserves.items():
                    regenerate_secondary(reserve)

        # cumulative counters — cross-period memory
        self.cumulative_environment_loss += result.total_environment
        self.cumulative_tertiary_drawdown += result.total_tertiary_kept
        self.periods_elapsed += 1

        return result

    # --- aggregate views ---

    def reserve_status(self) -> Dict[str, Dict[str, float]]:
        """Fraction remaining for every secondary reserve, grouped by basin."""
        return {
            basin_name: {
                key: r.fraction_remaining()
                for key, r in reserves.items()
            }
            for basin_name, reserves in self.secondary.items()
        }

    def tertiary_status(self) -> Dict[str, float]:
        return {
            name: pool.fraction_remaining()
            for name, pool in self.tertiary.items()
        }

    def exhausted_reserves(self) -> List[Tuple[str, str]]:
        """List of (basin, metric) reserves currently at or below cliff."""
        out: List[Tuple[str, str]] = []
        for bname, reserves in self.secondary.items():
            for key, r in reserves.items():
                if r.is_exhausted():
                    out.append((bname, key))
        return out

    def tertiary_past_cliff(self) -> List[str]:
        return [name for name, p in self.tertiary.items() if p.past_cliff()]
