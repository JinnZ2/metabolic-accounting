"""
term_audit/integration/temporal_adapter.py

Time-series wrapper for metabolic_accounting_adapter.py.

Core claim: the audits in term_audit/ produce static snapshots of
measurement system state. Metabolic-accounting operates on time
series. This module bridges that gap by:

1. Taking a sequence of audit snapshots (e.g., annual productivity
   profiles, quarterly basin assessments)
2. Producing a sequence of metabolic-accounting inputs
3. Computing derived temporal signals (trends, accelerations,
   threshold crossings)
4. Detecting when signal quality degradation precedes basin
   degradation (early warning)

The adapter maintains no state; it is a pure function from
sequence-of-audit-snapshots to sequence-of-accounting-inputs.
This prevents the temporal adapter from becoming a hidden state
variable that could be captured.

CC0. Stdlib only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum

from term_audit.integration.metabolic_accounting_adapter import (
    BasinStateInput,
    InfrastructureInput,
    CascadeCouplingInput,
    GlucoseFlowInput,
    VerdictInput,
    AssumptionValidatorFlag,
    BasinCategory,
    basin_from_v_c_audit,
    infrastructure_from_k_a_audit,
    glucose_flow_from_productivity_profile,
    verdict_from_basins,
    assumption_flags_from_audit,
)


# ===========================================================================
# Part 1. Temporal sequences
# ===========================================================================

@dataclass
class TimestampedBasinState:
    """Basin state at a specific time."""
    timestamp: float                    # e.g., year, quarter, simulation step
    state: BasinStateInput


@dataclass
class TimestampedInfrastructure:
    """Infrastructure state at a specific time."""
    timestamp: float
    state: InfrastructureInput


@dataclass
class TimestampedGlucoseFlow:
    """Glucose flow at a specific time."""
    timestamp: float
    flow: GlucoseFlowInput


@dataclass
class BasinTrajectory:
    """Derived temporal signals for a single basin."""
    basin_name: str
    timestamps: List[float]
    levels: List[float]
    regeneration_rates: List[float]
    extraction_rates: List[float]
    signal_qualities: List[float]

    def net_rate(self, idx: int) -> float:
        """Regeneration minus extraction at given index."""
        return self.regeneration_rates[idx] - self.extraction_rates[idx]

    def trend_slope(self, window: int = 3) -> Optional[float]:
        """Linear trend in level over recent window. None if insufficient data."""
        if len(self.levels) < window:
            return None
        recent = self.levels[-window:]
        if len(recent) < 2:
            return None
        # simple linear regression slope
        n = len(recent)
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(recent) / n
        num = sum((x[i] - mean_x) * (recent[i] - mean_y) for i in range(n))
        den = sum((x[i] - mean_x) ** 2 for i in range(n))
        return num / den if den != 0 else 0.0

    def acceleration(self, window: int = 5) -> Optional[float]:
        """Second derivative: is degradation accelerating?"""
        if len(self.levels) < window:
            return None
        # difference of differences
        if len(self.levels) < 3:
            return None
        rates = [
            self.levels[i+1] - self.levels[i]
            for i in range(len(self.levels) - 1)
        ]
        if len(rates) < 2:
            return None
        recent_rates = rates[-window+1:] if len(rates) >= window-1 else rates
        if len(recent_rates) < 2:
            return None
        return recent_rates[-1] - recent_rates[-2]

    def threshold_crossing_estimate(
        self,
        threshold: float = 0.2,
    ) -> Optional[float]:
        """
        Estimate time until level crosses threshold, assuming current
        net rate continues linearly. Returns None if not trending
        toward threshold or insufficient data.
        """
        if len(self.levels) < 2:
            return None
        current = self.levels[-1]
        net = self.net_rate(-1)
        if net >= 0 and current >= threshold:
            return None  # not trending down toward threshold
        if net <= 0 and current <= threshold:
            return None  # not trending up toward threshold
        if net == 0:
            return None
        return (threshold - current) / net

    def signal_quality_trend(self, window: int = 3) -> Optional[float]:
        """Is signal quality degrading? Negative means degradation."""
        if len(self.signal_qualities) < window:
            return None
        recent = self.signal_qualities[-window:]
        if len(recent) < 2:
            return None
        n = len(recent)
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(recent) / n
        num = sum((x[i] - mean_x) * (recent[i] - mean_y) for i in range(n))
        den = sum((x[i] - mean_x) ** 2 for i in range(n))
        return num / den if den != 0 else 0.0


@dataclass
class TemporalVerdict:
    """Verdict that incorporates temporal trends."""
    entity: str
    current_verdict: VerdictInput
    trend_slope: float                      # aggregate basin trend
    acceleration: Optional[float]           # is degradation accelerating?
    signal_quality_degrading: bool          # early warning flag
    threshold_crossings: Dict[str, Optional[float]]  # basin -> time to threshold
    confidence_penalty: float               # reduced by signal quality trend
    temporal_notes: List[str]


# ===========================================================================
# Part 2. Sequence builders
# ===========================================================================

def build_basin_trajectory(
    snapshots: List[TimestampedBasinState],
) -> Dict[str, BasinTrajectory]:
    """
    Group timestamped basin states by basin name and build trajectories.
    """
    by_name: Dict[str, List[TimestampedBasinState]] = {}
    for ts in snapshots:
        name = ts.state.name
        if name not in by_name:
            by_name[name] = []
        by_name[name].append(ts)

    trajectories: Dict[str, BasinTrajectory] = {}
    for name, states in by_name.items():
        # sort by timestamp
        states.sort(key=lambda s: s.timestamp)
        trajectories[name] = BasinTrajectory(
            basin_name=name,
            timestamps=[s.timestamp for s in states],
            levels=[s.state.current_level for s in states],
            regeneration_rates=[s.state.regeneration_rate for s in states],
            extraction_rates=[s.state.extraction_rate for s in states],
            signal_qualities=[s.state.signal_quality for s in states],
        )

    return trajectories


def build_temporal_verdict(
    entity: str,
    trajectories: Dict[str, BasinTrajectory],
    current_yield: float,
    threshold: float = 0.2,
) -> TemporalVerdict:
    """
    Combine basin trajectories into a temporal verdict.

    This extends the static verdict with:
    - aggregate trend slope (weighted by carrying capacity)
    - acceleration signal (are things getting worse faster?)
    - signal quality degradation (early warning of measurement failure)
    - per-basin threshold crossing estimates
    - confidence penalty if signal quality is degrading
    """
    if not trajectories:
        return TemporalVerdict(
            entity=entity,
            current_verdict=verdict_from_basins(entity, [], current_yield),
            trend_slope=0.0,
            acceleration=None,
            signal_quality_degrading=False,
            threshold_crossings={},
            confidence_penalty=0.0,
            temporal_notes=["no basin trajectories available"],
        )

    # Build static verdict from current states
    current_basins = [
        BasinStateInput(
            name=name,
            category=BasinCategory.HUMAN_SUBSTRATE,  # placeholder, would need actual category
            current_level=traj.levels[-1],
            regeneration_rate=traj.regeneration_rates[-1],
            extraction_rate=traj.extraction_rates[-1],
            carrying_capacity=1.0,
            signal_quality=traj.signal_qualities[-1],
            assumption_boundary=None,
        )
        for name, traj in trajectories.items()
    ]
    current_verdict = verdict_from_basins(entity, current_basins, current_yield)

    # Weighted aggregate trend slope
    total_weight = 0.0
    weighted_slope = 0.0
    for traj in trajectories.values():
        slope = traj.trend_slope()
        if slope is not None:
            weight = 1.0  # could use carrying capacity
            weighted_slope += slope * weight
            total_weight += weight

    trend_slope = weighted_slope / total_weight if total_weight > 0 else 0.0

    # Aggregate acceleration
    accels = []
    for traj in trajectories.values():
        acc = traj.acceleration()
        if acc is not None:
            accels.append(acc)
    acceleration = sum(accels) / len(accels) if accels else None

    # Signal quality degradation check
    sq_degrading = False
    sq_trends = []
    for traj in trajectories.values():
        trend = traj.signal_quality_trend()
        if trend is not None:
            sq_trends.append(trend)
    if sq_trends:
        mean_sq_trend = sum(sq_trends) / len(sq_trends)
        sq_degrading = mean_sq_trend < -0.01  # negative trend = degrading
        confidence_penalty = abs(mean_sq_trend) * 2.0 if sq_degrading else 0.0
    else:
        confidence_penalty = 0.0

    # Threshold crossings
    crossings = {}
    for name, traj in trajectories.items():
        crossings[name] = traj.threshold_crossing_estimate(threshold)

    # Temporal notes
    notes = []
    if trend_slope < -0.01:
        notes.append(f"basins degrading at aggregate rate {trend_slope:.3f}/timestep")
    if acceleration is not None and acceleration < -0.001:
        notes.append(f"degradation accelerating ({acceleration:.4f}/timestep²)")
    if sq_degrading:
        notes.append("signal quality degrading: measurements becoming less reliable")
    for name, ttr in crossings.items():
        if ttr is not None and ttr > 0:
            notes.append(f"{name}: {ttr:.1f} timesteps to threshold {threshold}")

    return TemporalVerdict(
        entity=entity,
        current_verdict=current_verdict,
        trend_slope=trend_slope,
        acceleration=acceleration,
        signal_quality_degrading=sq_degrading,
        threshold_crossings=crossings,
        confidence_penalty=confidence_penalty,
        temporal_notes=notes,
    )


# ===========================================================================
# Part 3. Synthetic sequence generators for testing and simulation
# ===========================================================================

def generate_linear_sequence(
    basin_name: str,
    category: BasinCategory,
    start_level: float,
    end_level: float,
    regeneration_rate: float,
    extraction_rate: float,
    signal_quality: float,
    n_steps: int,
    timestep: float = 1.0,
) -> List[TimestampedBasinState]:
    """
    Generate a linear trajectory for testing.
    """
    states: List[TimestampedBasinState] = []
    for i in range(n_steps):
        t = i * timestep
        frac = i / (n_steps - 1) if n_steps > 1 else 0.0
        level = start_level + frac * (end_level - start_level)

        state = BasinStateInput(
            name=basin_name,
            category=category,
            current_level=level,
            regeneration_rate=regeneration_rate,
            extraction_rate=extraction_rate,
            carrying_capacity=1.0,
            signal_quality=signal_quality,
            assumption_boundary=None,
        )
        states.append(TimestampedBasinState(timestamp=t, state=state))

    return states


def generate_accelerating_sequence(
    basin_name: str,
    category: BasinCategory,
    start_level: float,
    regeneration_rate: float,
    base_extraction: float,
    extraction_acceleration: float,
    signal_quality: float,
    n_steps: int,
    timestep: float = 1.0,
) -> List[TimestampedBasinState]:
    """
    Generate a trajectory where extraction accelerates over time.
    This produces the acceleration signal that temporal_verdict detects.
    """
    states: List[TimestampedBasinState] = []
    level = start_level

    for i in range(n_steps):
        t = i * timestep
        extraction = base_extraction + extraction_acceleration * i

        state = BasinStateInput(
            name=basin_name,
            category=category,
            current_level=max(0.0, min(1.0, level)),
            regeneration_rate=regeneration_rate,
            extraction_rate=extraction,
            carrying_capacity=1.0,
            signal_quality=signal_quality,
            assumption_boundary=None,
        )
        states.append(TimestampedBasinState(timestamp=t, state=state))

        # update level for next step
        net = regeneration_rate - extraction
        level = level + net * timestep

    return states


def generate_signal_quality_degradation_sequence(
    basin_name: str,
    category: BasinCategory,
    level: float,
    regeneration_rate: float,
    extraction_rate: float,
    start_quality: float,
    quality_degradation_rate: float,
    n_steps: int,
    timestep: float = 1.0,
) -> List[TimestampedBasinState]:
    """
    Generate a trajectory where signal quality degrades over time
    while the basin level remains stable. This is the early warning
    pattern: measurement system failing before basin fails.
    """
    states: List[TimestampedBasinState] = []

    for i in range(n_steps):
        t = i * timestep
        quality = max(0.1, start_quality - quality_degradation_rate * i)

        state = BasinStateInput(
            name=basin_name,
            category=category,
            current_level=level,
            regeneration_rate=regeneration_rate,
            extraction_rate=extraction_rate,
            carrying_capacity=1.0,
            signal_quality=quality,
            assumption_boundary=None,
        )
        states.append(TimestampedBasinState(timestamp=t, state=state))

    return states


# ===========================================================================
# Part 4. Audit sequence to metabolic sequence

# ===========================================================================

@dataclass
class AuditSnapshot:
    """A snapshot of all relevant audits at a point in time."""
    timestamp: float
    v_c_audit: Optional[TermAudit] = None      # substrate value
    k_a_audit: Optional[TermAudit] = None      # productive capital
    productivity_profile: Optional[object] = None  # JobDependencyProfile
    entity_name: str = "default_entity"


def audit_sequence_to_basin_sequence(
    snapshots: List[AuditSnapshot],
    basin_name: str,
    category: BasinCategory,
    level_extractor: Callable[[AuditSnapshot], float],
    regeneration_extractor: Callable[[AuditSnapshot], float],
    extraction_extractor: Callable[[AuditSnapshot], float],
    carrying_capacity: float = 1.0,
) -> List[TimestampedBasinState]:
    """
    Convert a sequence of audit snapshots into a basin trajectory.

    The extractor functions allow the caller to specify how to pull
    basin metrics from the audit snapshot. This is the bridge from
    static audit data to temporal basin state.
    """
    states: List[TimestampedBasinState] = []

    for snap in snapshots:
        if snap.v_c_audit is None:
            continue

        state = basin_from_v_c_audit(
            audit=snap.v_c_audit,
            basin_name=basin_name,
            category=category,
            current_level=level_extractor(snap),
            regeneration_rate=regeneration_extractor(snap),
            extraction_rate=extraction_extractor(snap),
            carrying_capacity=carrying_capacity,
        )
        states.append(TimestampedBasinState(
            timestamp=snap.timestamp,
            state=state,
        ))

    return states


def audit_sequence_to_glucose_sequence(
    snapshots: List[AuditSnapshot],
) -> List[TimestampedGlucoseFlow]:
    """
    Convert a sequence of productivity profiles into glucose flows.
    """
    flows: List[TimestampedGlucoseFlow] = []

    for snap in snapshots:
        if snap.productivity_profile is None:
            continue

        profile = snap.productivity_profile
        flow = glucose_flow_from_productivity_profile(
            entity=snap.entity_name,
            pay=profile.pay_per_time_basis,
            true_input=profile.true_input(),
            drawdown_breakdown=profile.drawdown_breakdown(),
        )
        flows.append(TimestampedGlucoseFlow(
            timestamp=snap.timestamp,
            flow=flow,
        ))

    return flows


# ===========================================================================
# Part 5. Early warning detection

# ===========================================================================

@dataclass
class EarlyWarningSignal:
    """A detected early warning of impending basin failure."""
    basin_name: str
    signal_type: str                    # "signal_quality_degradation",
                                        # "acceleration", "trend_reversal"
    detected_at: float
    confidence: float
    estimated_time_to_threshold: Optional[float]
    recommended_action: str


def detect_early_warnings(
    trajectories: Dict[str, BasinTrajectory],
    threshold: float = 0.2,
) -> List[EarlyWarningSignal]:
    """
    Scan basin trajectories for early warning signals.

    Three signal types:
    1. Signal quality degradation: measurement system failing before basin
    2. Acceleration: net degradation rate increasing
    3. Trend reversal: stable basin beginning to degrade
    """
    warnings: List[EarlyWarningSignal] = []

    for name, traj in trajectories.items():
        if len(traj.levels) < 3:
            continue

        # Signal quality degradation
        sq_trend = traj.signal_quality_trend(window=3)
        if sq_trend is not None and sq_trend < -0.02:
            ttr = traj.threshold_crossing_estimate(threshold)
            warnings.append(EarlyWarningSignal(
                basin_name=name,
                signal_type="signal_quality_degradation",
                detected_at=traj.timestamps[-1],
                confidence=min(1.0, abs(sq_trend) * 10),
                estimated_time_to_threshold=ttr,
                recommended_action=(
                    f"measurement system for {name} is degrading faster than "
                    f"the basin. Audit the standard-setters before basin "
                    f"failure becomes invisible."
                ),
            ))

        # Acceleration
        acc = traj.acceleration(window=5)
        if acc is not None and acc < -0.001 and traj.net_rate(-1) < 0:
            ttr = traj.threshold_crossing_estimate(threshold)
            warnings.append(EarlyWarningSignal(
                basin_name=name,
                signal_type="acceleration",
                detected_at=traj.timestamps[-1],
                confidence=min(1.0, abs(acc) * 100),
                estimated_time_to_threshold=ttr,
                recommended_action=(
                    f"degradation of {name} is accelerating. Current net rate "
                    f"understates future drawdown. Revise extraction downward "
                    f"immediately."
                ),
            ))

        # Trend reversal
        if len(traj.levels) >= 4:
            recent_slope = traj.trend_slope(window=3)
            prior_slope = None
            if len(traj.levels) >= 6:
                # compare recent to earlier period
                prior_levels = traj.levels[:-3]
                if len(prior_levels) >= 3:
                    n = len(prior_levels)
                    x = list(range(n))
                    mean_x = sum(x) / n
                    mean_y = sum(prior_levels) / n
                    num = sum((x[i] - mean_x) * (prior_levels[i] - mean_y) for i in range(n))
                    den = sum((x[i] - mean_x) ** 2 for i in range(n))
                    prior_slope = num / den if den != 0 else 0.0

            if (recent_slope is not None and prior_slope is not None and
                prior_slope >= -0.005 and recent_slope < -0.01):
                ttr = traj.threshold_crossing_estimate(threshold)
                warnings.append(EarlyWarningSignal(
                    basin_name=name,
                    signal_type="trend_reversal",
                    detected_at=traj.timestamps[-1],
                    confidence=min(1.0, abs(recent_slope - prior_slope) * 20),
                    estimated_time_to_threshold=ttr,
                    recommended_action=(
                        f"{name} has reversed from stable to degrading. "
                        f"Investigate what changed in extraction or "
                        f"regeneration regime."
                    ),
                ))

    return warnings


# ===========================================================================
# Part 6. Falsifiable predictions
# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
    {
        "id": 1,
        "claim": (
            "Signal quality degradation precedes basin degradation in "
            "captured measurement systems. The measurement fails before "
            "the basin fails."
        ),
        "falsification": (
            "Track signal quality and basin level across multiple systems. "
            "Show no correlation between signal quality trend and subsequent "
            "basin trend."
        ),
    },
    {
        "id": 2,
        "claim": (
            "Acceleration in extraction rate produces nonlinear basin "
            "drawdown that linear trend analysis underestimates."
        ),
        "falsification": (
            "Compare linear projections to actual basin trajectories under "
            "accelerating extraction. Show no systematic underestimation."
        ),
    },
    {
        "id": 3,
        "claim": (
            "Temporal verdict confidence_penalty correctly identifies when "
            "static verdict confidence should be reduced due to degrading "
            "measurement quality."
        ),
        "falsification": (
            "Compare temporal verdicts to actual outcomes. Show that "
            "confidence_penalty does not improve predictive accuracy."
        ),
    },
    {
        "id": 4,
        "claim": (
            "Early warning signals (signal quality degradation, acceleration, "
            "trend reversal) provide actionable lead time before threshold "
            "crossing."
        ),
        "falsification": (
            "Measure lead time from first warning to threshold crossing. "
            "Show lead time is zero or negative (warning after crossing)."
        ),
    },
    {
        "id": 5,
        "claim": (
            "Audit sequence to basin sequence conversion preserves the "
            "signal quality trends present in the underlying audits."
        ),
        "falsification": (
            "Feed audits with known signal quality degradation through "
            "the adapter. Show output signal quality does not track "
            "input degradation."
        ),
    },
]


# ===========================================================================
# Part 7. End-to-end temporal example
# ===========================================================================

def temporal_end_to_end_example() -> Dict:
    """
    Worked example showing a 10-period sequence with:
    - soil basin degrading linearly
    - human substrate basin accelerating degradation
    - signal quality degrading in water basin (early warning)
    """
    from term_audit.audits.value import SUBSTRATE_VALUE_AUDIT
    from term_audit.audits.productivity import long_haul_driver_example

    # Create 10 synthetic audit snapshots
    snapshots: List[AuditSnapshot] = []
    for i in range(10):
        snap = AuditSnapshot(
            timestamp=float(i),
            v_c_audit=SUBSTRATE_VALUE_AUDIT,
            productivity_profile=long_haul_driver_example(),
            entity_name="driver_operation",
        )
        snapshots.append(snap)

    # Soil basin: linear degradation
    def soil_level(snap: AuditSnapshot) -> float:
        return 0.8 - 0.03 * snap.timestamp

    def soil_regen(snap: AuditSnapshot) -> float:
        return 0.04

    def soil_extract(snap: AuditSnapshot) -> float:
        return 0.06

    soil_sequence = audit_sequence_to_basin_sequence(
        snapshots=snapshots,
        basin_name="topsoil",
        category=BasinCategory.SOIL,
        level_extractor=soil_level,
        regeneration_extractor=soil_regen,
        extraction_extractor=soil_extract,
    )

    # Human substrate: accelerating degradation
    def human_level(snap: AuditSnapshot) -> float:
        base = 0.75
        accel = 0.005 * (snap.timestamp ** 2)
        return max(0.1, base - accel)

    def human_regen(snap: AuditSnapshot) -> float:
        return 0.02

    def human_extract(snap: AuditSnapshot) -> float:
        return 0.04 + 0.005 * snap.timestamp

    human_sequence = audit_sequence_to_basin_sequence(
        snapshots=snapshots,
        basin_name="driver_organism_substrate",
        category=BasinCategory.HUMAN_SUBSTRATE,
        level_extractor=human_level,
        regeneration_extractor=human_regen,
        extraction_extractor=human_extract,
    )

    # Water basin: stable level but degrading signal quality
    def water_level(snap: AuditSnapshot) -> float:
        return 0.7

    def water_regen(snap: AuditSnapshot) -> float:
        return 0.03

    def water_extract(snap: AuditSnapshot) -> float:
        return 0.025

    water_sequence = []
    for snap in snapshots:
        state = basin_from_v_c_audit(
            audit=snap.v_c_audit,
            basin_name="groundwater",
            category=BasinCategory.WATER,
            current_level=0.7,
            regeneration_rate=0.03,
            extraction_rate=0.025,
            carrying_capacity=1.0,
        )
        # manually degrade signal quality
        state.signal_quality = max(0.3, 0.9 - 0.06 * snap.timestamp)
        water_sequence.append(TimestampedBasinState(
            timestamp=snap.timestamp,
            state=state,
        ))

    # Build trajectories
    all_snapshots = soil_sequence + human_sequence + water_sequence
    trajectories = build_basin_trajectory(all_snapshots)

    # Temporal verdict at final timestep
    temporal_verdict = build_temporal_verdict(
        entity="driver_operation",
        trajectories=trajectories,
        current_yield=1600.0,
        threshold=0.2,
    )

    # Early warnings
    warnings = detect_early_warnings(trajectories, threshold=0.2)

    return {
        "trajectories": {
            name: {
                "timestamps": traj.timestamps,
                "levels": traj.levels,
                "net_rates": [traj.net_rate(i) for i in range(len(traj.levels))],
                "signal_qualities": traj.signal_qualities,
            }
            for name, traj in trajectories.items()
        },
        "temporal_verdict": {
            "trend_slope": temporal_verdict.trend_slope,
            "acceleration": temporal_verdict.acceleration,
            "signal_quality_degrading": temporal_verdict.signal_quality_degrading,
            "threshold_crossings": temporal_verdict.threshold_crossings,
            "confidence_penalty": temporal_verdict.confidence_penalty,
            "notes": temporal_verdict.temporal_notes,
        },
        "early_warnings": [
            {
                "basin": w.basin_name,
                "type": w.signal_type,
                "confidence": w.confidence,
                "ttr": w.estimated_time_to_threshold,
                "action": w.recommended_action,
            }
            for w in warnings
        ],
    }


if __name__ == "__main__":
    import json

    result = temporal_end_to_end_example()

    print("=" * 72)
    print("TEMPORAL ADAPTER: END-TO-END EXAMPLE")
    print("=" * 72)
    print()

    print("--- basin trajectories (final 3 timesteps) ---")
    for name, traj in result["trajectories"].items():
        print(f"\n{name}:")
        for i in range(max(0, len(traj["timestamps"]) - 3), len(traj["timestamps"])):
            print(f"  t={traj['timestamps'][i]:.0f}: "
                  f"level={traj['levels'][i]:.3f}, "
                  f"net={traj['net_rates'][i]:+.3f}, "
                  f"sq={traj['signal_qualities'][i]:.3f}")

    print("\n--- temporal verdict ---")
    for key, val in result["temporal_verdict"].items():
        print(f"  {key}: {val}")

    print("\n--- early warnings ---")
    for w in result["early_warnings"]:
        print(f"  [{w['type']}] {w['basin']}: {w['action'][:80]}...")

    print(f"\n=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)} ===")
