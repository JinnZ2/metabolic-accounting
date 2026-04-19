“””
term_audit/integration/metabolic_accounting_adapter.py

One-way adapter connecting term_audit outputs to metabolic-accounting
inputs.

Dataflow direction: term_audit -> metabolic-accounting (one-way).
term_audit is upstream measurement infrastructure. metabolic-accounting
consumes it. Reverse dataflow is deliberately not supported because it
would let accounting results capture the audits.

Mapping summary:
V_C substrate-value audit        -> basin_state variables
K_A productive-capital audit     -> infrastructure state variables
K_B -> K_A linkage (negative)    -> forced drawdown rate
V_B -> V_C linkage (negative)    -> cascade coupling strength
status_extraction support flow   -> regeneration rate
status_extraction labeled fract. -> human substrate degradation
signal-criteria failure mode     -> assumption_validator flag

The adapter does not import metabolic-accounting directly. It produces
dataclasses that match the shape metabolic-accounting expects. The
metabolic-accounting repo can import this adapter and consume its
output, or any other downstream system can use the same interface.

CC0. Stdlib only.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from term_audit.schema import TermAudit, SignalScore

# ===========================================================================

# Part 1. Target shapes for metabolic-accounting

# ===========================================================================

# 

# These dataclasses mirror the shape metabolic-accounting expects in its

# basin_states, infrastructure, cascade, accounting, and verdict modules.

# The adapter produces these; the accounting engine consumes them.

# —————————————————————————

class BasinCategory(Enum):
SOIL = “soil”
WATER = “water”
AIR = “air”
BIOLOGY = “biology”
HUMAN_SUBSTRATE = “human_substrate”    # organism-level basin:
# health, sleep, skill,
# family, community
KNOWLEDGE = “knowledge”                 # transmitted knowledge as
# substrate
INFRASTRUCTURE = “infrastructure”       # built substrate: tools,
# buildings, roads

@dataclass
class BasinStateInput:
“”“Input to metabolic-accounting basin_states layer.”””
name: str
category: BasinCategory
current_level: float                    # 0.0 depleted, 1.0 full
regeneration_rate: float                # per time unit, in [-1, +1]
extraction_rate: float                  # per time unit, non-negative
carrying_capacity: float                # maximum level achievable
signal_quality: float                   # 0.0-1.0, how well-measured
# this basin is; driven by
# underlying audit signal
# score
assumption_boundary: Optional[str]      # known regime boundary
# beyond which the basin
# model breaks down

@dataclass
class InfrastructureInput:
“”“Input to metabolic-accounting infrastructure layer.”””
name: str
basin_dependencies: List[str]           # basins this infrastructure
# depends on for function
condition: float                        # 0.0 failed, 1.0 as-new
maintenance_debt: float                 # accumulated deferred
# maintenance cost in
# substrate-equivalent units
failure_coupling: Dict[str, float]      # name -> coupling strength

@dataclass
class CascadeCouplingInput:
“”“Input to metabolic-accounting cascade layer.”””
source: str                             # basin or infrastructure name
target: str                             # basin or infrastructure name
coupling_strength: float                # how strongly source failure
# drives target failure
time_lag: float                         # time units from source
# trigger to target onset
mechanism: str                          # physical or informational
# mechanism

@dataclass
class GlucoseFlowInput:
“”“Input to metabolic-accounting accounting layer.”””
entity: str                             # firm, operation, household
extraction_rate: float                  # basin-equivalent units /
# time
regeneration_rate: float                # basin-equivalent units /
# time
reported_profit: float                  # in monetary units (K_B)
forced_drawdown: float                  # regeneration debt owed
# per time unit
net_glucose: float                      # reported_profit minus
# forced_drawdown in
# consistent units

@dataclass
class VerdictInput:
“”“Input to metabolic-accounting verdict layer.”””
entity: str
sustainable_yield: float                # extraction level at which
# basins remain steady
current_yield: float                    # actual extraction level
basin_trajectory: float                 # aggregate in [-1, +1]
time_to_red: Optional[float]            # time until a basin hits
# critical threshold; None
# if no basin is trending
# toward red
confidence: float                       # driven by signal quality
# of underlying audits

@dataclass
class AssumptionValidatorFlag:
“”“Flag passed to assumption_validator when a signal-criteria
failure means the accounting model is operating outside its
validity regime.”””
source_audit: str
failure_mode: str                       # which signal criterion
# failed
severity: float                         # 0.0 negligible, 1.0 model
# invalidating
message: str

# ===========================================================================

# Part 2. Mapping from V_C (substrate-value) audit to basin state

# ===========================================================================

def basin_from_v_c_audit(
audit: TermAudit,
basin_name: str,
category: BasinCategory,
current_level: float,
regeneration_rate: float,
extraction_rate: float,
carrying_capacity: float = 1.0,
assumption_boundary: Optional[str] = None,
) -> BasinStateInput:
“””
Convert a V_C-class audit into a BasinStateInput.

```
Signal quality of the resulting basin state is driven by the
audit's mean score on the signal criteria. High-quality audits
produce high-confidence basin measurements.
"""
if not audit.signal_scores:
    signal_quality = 0.0
else:
    signal_quality = sum(
        s.score for s in audit.signal_scores
    ) / len(audit.signal_scores)

return BasinStateInput(
    name=basin_name,
    category=category,
    current_level=current_level,
    regeneration_rate=regeneration_rate,
    extraction_rate=extraction_rate,
    carrying_capacity=carrying_capacity,
    signal_quality=signal_quality,
    assumption_boundary=assumption_boundary,
)
```

# ===========================================================================

# Part 3. Mapping from K_A (productive capital) audit to infrastructure

# ===========================================================================

def infrastructure_from_k_a_audit(
audit: TermAudit,
infra_name: str,
basin_dependencies: List[str],
condition: float,
maintenance_debt: float = 0.0,
failure_coupling: Optional[Dict[str, float]] = None,
) -> InfrastructureInput:
“””
Convert a K_A-class audit into an InfrastructureInput.

```
The audit's signal quality informs how reliably we can report
condition and maintenance_debt. Low audit quality should make
downstream accounting flag these values as uncertain.
"""
return InfrastructureInput(
    name=infra_name,
    basin_dependencies=basin_dependencies,
    condition=condition,
    maintenance_debt=maintenance_debt,
    failure_coupling=failure_coupling or {},
)
```

# ===========================================================================

# Part 4. Mapping from V_B -> V_C and K_B -> K_A linkages to cascade

# ===========================================================================

@dataclass
class LinkageRecord:
“”“Generic record for a linkage between measurements, matching the
shape produced by audits/value.py and audits/capital.py.”””
source: str
target: str
relation: str
strength_estimate: float
mechanism: str

def cascade_from_negative_linkage(
linkage: LinkageRecord,
source_entity: str,
target_entity: str,
time_lag: float,
) -> Optional[CascadeCouplingInput]:
“””
Convert a negative linkage (K_B -> K_A, V_B -> V_C, K_B -> K_C)
into a cascade coupling.

```
Only negative linkages produce cascade couplings because they
represent measurable substrate depletion driven by the source.
Positive and conditional linkages are not forced cascades; they
may or may not flow depending on other conditions.
"""
if linkage.strength_estimate >= 0:
    return None
return CascadeCouplingInput(
    source=source_entity,
    target=target_entity,
    coupling_strength=abs(linkage.strength_estimate),
    time_lag=time_lag,
    mechanism=linkage.mechanism,
)
```

# ===========================================================================

# Part 5. Mapping from status_extraction to human substrate and

# regeneration rate

# ===========================================================================

@dataclass
class StatusExtractionSnapshot:
“”“Minimal snapshot of status_extraction model state; matches the
shape StatusExtractionModel.history entries produce.”””
support_fraction: float
production_fraction: float
distinction_fraction: float
tolerance_width: float
labeled_fraction: float
avg_capture: float

def human_substrate_basin_from_status(
snapshot: StatusExtractionSnapshot,
baseline_regeneration: float = 0.05,
baseline_extraction: float = 0.05,
) -> BasinStateInput:
“””
Convert a status_extraction snapshot into a human substrate basin
measurement.

```
The mapping:
  - current_level is driven by fraction inside tolerance band
  - regeneration_rate scales with support_fraction
  - extraction_rate scales with distinction_fraction
"""
current_level = 1.0 - snapshot.labeled_fraction
regeneration_rate = (
    baseline_regeneration * (snapshot.support_fraction / 0.5)
)
extraction_rate = (
    baseline_extraction
    * (1.0 + snapshot.distinction_fraction / 0.1)
)

return BasinStateInput(
    name="human_substrate_population",
    category=BasinCategory.HUMAN_SUBSTRATE,
    current_level=current_level,
    regeneration_rate=regeneration_rate,
    extraction_rate=extraction_rate,
    carrying_capacity=1.0,
    signal_quality=0.7,   # status_extraction is a dynamic model,
                          # not a direct measurement; mid-confidence
    assumption_boundary=(
        "model assumes tolerance-band contraction is a monotone "
        "function of support flow; may break at very low support "
        "levels where support collapses discontinuously"
    ),
)
```

# ===========================================================================

# Part 6. Glucose flow and forced drawdown from productivity audit

# ===========================================================================

def glucose_flow_from_productivity_profile(
entity: str,
pay: float,
true_input: float,
drawdown_breakdown: Dict[str, float],
) -> GlucoseFlowInput:
“””
Convert a JobDependencyProfile result into a glucose flow record.

```
extraction_rate: sum of dependency costs (true_input).
regeneration_rate: paid portion of dependencies (up to true_input).
forced_drawdown: unpaid dependency costs that become substrate
                 conversion.
reported_profit: pay minus paid dependencies; this is what
                 conventional accounting reports.
net_glucose: pay minus true_input; negative values are substrate
             conversion rate.
"""
paid_dependencies = min(pay, true_input)
forced_drawdown = max(0.0, true_input - pay)
reported_profit = max(0.0, pay - paid_dependencies)
net_glucose = pay - true_input

return GlucoseFlowInput(
    entity=entity,
    extraction_rate=true_input,
    regeneration_rate=paid_dependencies,
    reported_profit=reported_profit,
    forced_drawdown=forced_drawdown,
    net_glucose=net_glucose,
)
```

# ===========================================================================

# Part 7. Verdict from combined inputs

# ===========================================================================

def verdict_from_basins(
entity: str,
basins: List[BasinStateInput],
current_yield: float,
) -> VerdictInput:
“””
Combine basin states into a verdict for an entity.

```
sustainable_yield: sum of basin regeneration rates weighted by
                  their current level.
basin_trajectory: weighted average of (regeneration - extraction)
                  across basins.
time_to_red: time to first basin hitting level 0.0 at current
             net rate; None if no basin is trending red.
confidence: product of basin signal qualities (conservative
            compounding).
"""
if not basins:
    return VerdictInput(
        entity=entity,
        sustainable_yield=0.0,
        current_yield=current_yield,
        basin_trajectory=0.0,
        time_to_red=None,
        confidence=0.0,
    )

sustainable = sum(
    b.regeneration_rate * b.current_level for b in basins
)

weighted_traj = 0.0
total_weight = 0.0
for b in basins:
    weight = b.carrying_capacity
    net = b.regeneration_rate - b.extraction_rate
    weighted_traj += net * weight
    total_weight += weight
basin_trajectory = (
    weighted_traj / total_weight if total_weight > 0 else 0.0
)

times: List[float] = []
for b in basins:
    net = b.regeneration_rate - b.extraction_rate
    if net < 0 and b.current_level > 0:
        times.append(b.current_level / abs(net))
time_to_red = min(times) if times else None

confidence = 1.0
for b in basins:
    confidence *= b.signal_quality
if len(basins) > 0:
    confidence = confidence ** (1.0 / len(basins))  # geometric mean

return VerdictInput(
    entity=entity,
    sustainable_yield=sustainable,
    current_yield=current_yield,
    basin_trajectory=basin_trajectory,
    time_to_red=time_to_red,
    confidence=confidence,
)
```

# ===========================================================================

# Part 8. Assumption validator flags from signal-criteria failures

# ===========================================================================

FAILURE_SEVERITY = {
“scope_defined”:        0.8,
“unit_invariant”:       0.7,
“referent_stable”:      0.8,
“calibration_exists”:   0.6,
“observer_invariant”:   0.5,
“conservation_or_law”:  0.9,
“falsifiability”:       0.9,
}

def assumption_flags_from_audit(
audit: TermAudit,
failure_threshold: float = 0.5,
) -> List[AssumptionValidatorFlag]:
“””
Generate assumption_validator flags for every signal criterion
that falls below the failure threshold in the audit.

```
These flags tell metabolic-accounting (via the assumption_validator)
that the underlying measurement is not reliable in the regime being
modeled, and that downstream conclusions should carry a confidence
penalty.
"""
flags: List[AssumptionValidatorFlag] = []
for s in audit.signal_scores:
    if s.score < failure_threshold:
        severity = FAILURE_SEVERITY.get(s.criterion, 0.5)
        # scale severity by how badly the criterion failed
        effective = severity * (1.0 - s.score / failure_threshold)
        flags.append(AssumptionValidatorFlag(
            source_audit=audit.term,
            failure_mode=s.criterion,
            severity=effective,
            message=(
                f"signal criterion '{s.criterion}' fails at "
                f"score {s.score:.2f} (threshold "
                f"{failure_threshold}). "
                f"Rationale: {s.justification[:160]}"
            ),
        ))
return flags
```

# ===========================================================================

# Part 9. End-to-end example

# ===========================================================================

def end_to_end_example() -> Dict:
“””
Worked end-to-end example using the existing audits.

```
Pipeline:
  1. Load V_C substrate-value audit -> soil basin state
  2. Load K_A productive-capital audit -> infrastructure state
  3. Load productivity profile -> glucose flow
  4. Synthesize verdict
  5. Extract assumption flags from collapsed-value audit
"""
from term_audit.audits.value import SUBSTRATE_VALUE_AUDIT
from term_audit.audits.capital import PRODUCTIVE_CAPITAL_AUDIT
from term_audit.audits.value import COLLAPSED_VALUE_AUDIT
from term_audit.audits.productivity import long_haul_driver_example

soil_basin = basin_from_v_c_audit(
    audit=SUBSTRATE_VALUE_AUDIT,
    basin_name="property_topsoil",
    category=BasinCategory.SOIL,
    current_level=0.55,
    regeneration_rate=0.04,
    extraction_rate=0.02,
    carrying_capacity=1.0,
    assumption_boundary=(
        "substrate accounting assumes Holocene-regime soil "
        "dynamics; may not hold under rapid climate-driven "
        "shifts in microbial community structure"
    ),
)

water_basin = basin_from_v_c_audit(
    audit=SUBSTRATE_VALUE_AUDIT,
    basin_name="property_groundwater",
    category=BasinCategory.WATER,
    current_level=0.70,
    regeneration_rate=0.03,
    extraction_rate=0.025,
    carrying_capacity=1.0,
)

human_basin = basin_from_v_c_audit(
    audit=SUBSTRATE_VALUE_AUDIT,
    basin_name="driver_organism_substrate",
    category=BasinCategory.HUMAN_SUBSTRATE,
    current_level=0.65,
    regeneration_rate=0.02,
    extraction_rate=0.05,
    carrying_capacity=1.0,
)

truck_infra = infrastructure_from_k_a_audit(
    audit=PRODUCTIVE_CAPITAL_AUDIT,
    infra_name="truck_equipment",
    basin_dependencies=["driver_organism_substrate"],
    condition=0.7,
    maintenance_debt=0.1,
    failure_coupling={
        "driver_organism_substrate": 0.4,
    },
)

profile = long_haul_driver_example()
glucose = glucose_flow_from_productivity_profile(
    entity="long_haul_driver",
    pay=profile.pay_per_time_basis,
    true_input=profile.true_input(),
    drawdown_breakdown=profile.drawdown_breakdown(),
)

basins = [soil_basin, water_basin, human_basin]
verdict = verdict_from_basins(
    entity="driver_household_operation",
    basins=basins,
    current_yield=profile.pay_per_time_basis,
)

flags = assumption_flags_from_audit(COLLAPSED_VALUE_AUDIT)

return {
    "basins": basins,
    "infrastructure": [truck_infra],
    "glucose_flow": glucose,
    "verdict": verdict,
    "assumption_flags": flags,
}
```

if **name** == “**main**”:
import json
from dataclasses import asdict

```
result = end_to_end_example()

print("=" * 72)
print("TERM_AUDIT -> METABOLIC_ACCOUNTING ADAPTER")
print("=" * 72)
print()
print("--- basin states ---")
for b in result["basins"]:
    d = asdict(b)
    d["category"] = b.category.value
    print(json.dumps(d, indent=2))
    print()
print("--- infrastructure ---")
for i in result["infrastructure"]:
    print(json.dumps(asdict(i), indent=2))
    print()
print("--- glucose flow ---")
print(json.dumps(asdict(result["glucose_flow"]), indent=2))
print()
print("--- verdict ---")
print(json.dumps(asdict(result["verdict"]), indent=2))
print()
print(f"--- assumption flags: {len(result['assumption_flags'])} ---")
for f in result["assumption_flags"][:3]:
    print(f"  [{f.failure_mode}] severity={f.severity:.2f}")
    print(f"    {f.message[:100]}")
```
