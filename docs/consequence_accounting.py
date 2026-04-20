“””
term_audit/consequence_accounting.py

Horizontal measurement tool for Tier 3 (institutional legitimacy)
terms. Defines consequence-exposure scoring, cumulative-exposure
computation, authority-alignment measurement, and measurement-
inversion detection.

Core claim: formal authority in modern organizations is systematically
anti-correlated with cumulative consequence exposure. Actors bearing
the highest integrated consequence-decision density per career have
the least decision authority over their working conditions. Actors
with the least consequence exposure hold the most formal authority.
This is not an accident. It is a structural feature of measurement
systems that reward substrate non-burn as a signal of capacity.

This module is consumed by expertise.py, and by future audits of
authority, accountability, leadership, governance, compliance, and
compensation. It operates horizontally across all Tier 3 terms the
same way incentive_analysis.py operates across signal audits.

CC0. Stdlib only.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math

# ===========================================================================

# Part 1. Scoring axes

# ===========================================================================

# 

# Six axes, each scored independently. Each axis is a scalar in [0,1]

# where 1.0 represents maximum of that quantity. The axes are not

# aggregated into a single score; they are kept separate because they

# measure different things and lossy aggregation would recreate the

# measurement failure the module exists to expose.

# —————————————————————————

CONSEQUENCE_AXES = [
“consequence_per_event”,
“event_frequency”,
“cumulative_career_exposure”,
“system_coupling_of_errors”,
“substrate_expenditure_per_event”,
“authority_alignment_with_exposure”,
]

# Reference scales for consequence_per_event:

# 

# 0.0    no meaningful consequence (paperwork redo, minor rework)

# 0.2    single-person minor harm (injury, financial loss recoverable)

# 0.4    single-person major harm (death, severe injury, asset loss)

# 0.6    small-group casualties (under 10 people) or localized

# ecological / infrastructure damage

# 0.8    large-group casualties (10-1000) or regional ecosystem

# impact or major infrastructure loss

# 1.0    mass-casualty (1000+) or watershed / airshed / regional

# ecosystem collapse or multi-generational contamination

# 

# Reference scales for event_frequency:

# 

# events per year (log-scaled):

# 0.0    < 1 per career        (one-time irreversible decision)

# 0.2    1-10 per year         (quarterly board decisions)

# 0.4    10-100 per year       (weekly operational calls)

# 0.6    100-1000 per year     (daily operational decisions)

# 0.8    1000-10000 per year   (hourly decisions)

# 1.0    10000-100000 per year (minute-scale decisions)

# * values above 1.0 are clipped

def score_event_frequency(events_per_year: float) -> float:
“”“Log-scaled frequency score in [0,1].”””
if events_per_year <= 0:
return 0.0
# log10(events_per_year) normalized so 1/year -> 0.2, 100000/year -> 1.0
log = math.log10(events_per_year)
if log < 0:
return 0.0
return min(1.0, 0.2 * log / 1.0 if log < 1 else 0.2 + 0.16 * (log - 1))

def cumulative_exposure(
consequence_per_event: float,
event_frequency_score: float,
career_years: float,
coupling: float,
) -> float:
“””
Cumulative integrated career exposure.

```
This is the product of per-event severity, frequency, career
duration, and system coupling. Coupling enters multiplicatively
because one error that propagates through coupled systems has
larger effective consequence than one error that stays contained.

Normalized by dividing by a reference career product
(severity=0.8, frequency=0.6, 20 years, coupling=0.5 = 4.8).
"""
reference = 0.8 * 0.6 * 20.0 * 0.5
raw = (
    consequence_per_event
    * event_frequency_score
    * career_years
    * coupling
)
return min(1.0, raw / reference)
```

# ===========================================================================

# Part 2. Role profile

# ===========================================================================

@dataclass
class RoleProfile:
“”“Consequence-accounting profile for a specific role.”””
role_name: str
consequence_per_event: float
events_per_year: float
career_years: float
system_coupling_of_errors: float
substrate_expenditure_per_event: float
authority_over_working_conditions: float
examples: List[str] = field(default_factory=list)
notes: str = “”

```
def event_frequency_score(self) -> float:
    return score_event_frequency(self.events_per_year)

def cumulative_career_exposure(self) -> float:
    return cumulative_exposure(
        self.consequence_per_event,
        self.event_frequency_score(),
        self.career_years,
        self.system_coupling_of_errors,
    )

def authority_alignment_score(self) -> float:
    """
    Alignment score: how well does formal authority track
    consequence exposure?

    High alignment (1.0): actors with high exposure have high
        authority over their conditions (solo practitioner with
        owned equipment and route control).
    Low alignment (0.0): high-exposure actor has no authority;
        conditions are set by insulated actor elsewhere.

    Computed as the difference between authority_over_working_
    conditions and cumulative_career_exposure, centered at zero.
    A large negative value means authority is far below what
    exposure would justify. Returned rescaled to [0,1] where
    0.5 = neutral, > 0.5 = authority above exposure, < 0.5 =
    authority below exposure.
    """
    diff = self.authority_over_working_conditions - \
           self.cumulative_career_exposure()
    return max(0.0, min(1.0, 0.5 + diff / 2.0))

def all_scores(self) -> Dict[str, float]:
    return {
        "consequence_per_event": self.consequence_per_event,
        "event_frequency": self.event_frequency_score(),
        "cumulative_career_exposure":
            self.cumulative_career_exposure(),
        "system_coupling_of_errors": self.system_coupling_of_errors,
        "substrate_expenditure_per_event":
            self.substrate_expenditure_per_event,
        "authority_alignment_with_exposure":
            self.authority_alignment_score(),
    }
```

# ===========================================================================

# Part 3. Reference role profiles

# ===========================================================================

# 

# Illustrative values for common roles. Numbers are rounded and

# deliberately conservative. Calibration would require per-role

# empirical study; these are starting points for the measurement

# framework, not claims about specific individuals.

# —————————————————————————

REFERENCE_ROLES = [
RoleProfile(
role_name=“hazmat_long_haul_driver”,
consequence_per_event=0.85,
events_per_year=165000.0,     # 11h driving * 60 decisions/h *
# 5 days * 50 weeks
career_years=20.0,
system_coupling_of_errors=0.85,
substrate_expenditure_per_event=0.75,
authority_over_working_conditions=0.15,
examples=[
“tanker driver on lift bridges”,
“chemical haulers on winter corridors”,
“LNG and anhydrous ammonia carriers”,
],
notes=(
“cargo rupture in populated corridor produces mass “
“casualty, watershed contamination, infrastructure “
“destruction, cascading transport lockout. Authority “
“over schedule, rest, routing, and load acceptance “
“typically resides with logistics dispatch, not driver.”
),
),
RoleProfile(
role_name=“great_lakes_freighter_captain”,
consequence_per_event=0.95,
events_per_year=5000.0,        # ~seasonal voyages * decisions
career_years=25.0,
system_coupling_of_errors=0.9,
substrate_expenditure_per_event=0.7,
authority_over_working_conditions=0.45,
examples=[
“1000-foot ore carrier on Superior”,
“container ships in narrow channels”,
],
notes=(
“vessel loss contaminates largest freshwater reserve on “
“Earth; crew deaths; cargo dispersion; shipping lane “
“closure. Captain holds more authority than truckers “
“but still constrained by shipping-company schedule and “
“insurance regime.”
),
),
RoleProfile(
role_name=“barge_pilot_mississippi”,
consequence_per_event=0.9,
events_per_year=20000.0,
career_years=25.0,
system_coupling_of_errors=0.95,
substrate_expenditure_per_event=0.7,
authority_over_working_conditions=0.5,
notes=(
“tow of 15-40 barges carrying grain, petroleum, fertilizer “
“through river system. Bridge strike or grounding closes “
“navigation from Minneapolis to New Orleans; chemical “
“cargo contaminates drinking water for downstream cities.”
),
),
RoleProfile(
role_name=“nuclear_plant_operator”,
consequence_per_event=1.0,
events_per_year=8760.0,        # continuous monitoring
career_years=25.0,
system_coupling_of_errors=1.0,
substrate_expenditure_per_event=0.8,
authority_over_working_conditions=0.35,
notes=(
“multi-generational geographic-scale consequence; event “
“frequency is effectively continuous because the control “
“room is never allowed to lose attention. Authority over “
“staffing, procedures, and schedule resides with plant “
“management and regulators.”
),
),
RoleProfile(
role_name=“surgeon”,
consequence_per_event=0.4,
events_per_year=300.0,
career_years=25.0,
system_coupling_of_errors=0.3,
substrate_expenditure_per_event=0.7,
authority_over_working_conditions=0.7,
notes=(
“per-event consequence is one patient life plus recovery; “
“consequence space is bounded by operating room scope. “
“Surgeon has moderate-to-high authority in solo or “
“partnership practice; lower in hospital employment.”
),
),
RoleProfile(
role_name=“nurse_icu”,
consequence_per_event=0.4,
events_per_year=8000.0,        # shifts * decisions per shift
career_years=30.0,
system_coupling_of_errors=0.3,
substrate_expenditure_per_event=0.75,
authority_over_working_conditions=0.25,
notes=(
“more patient-contact hours than physicians; more “
“medication administration; more opportunity for fatal “
“error. Authority over staffing, scheduling, and workload “
“resides with nursing administration and hospital “
“management.”
),
),
RoleProfile(
role_name=“commercial_airline_pilot”,
consequence_per_event=0.85,
events_per_year=3000.0,
career_years=25.0,
system_coupling_of_errors=0.5,
substrate_expenditure_per_event=0.7,
authority_over_working_conditions=0.55,
notes=(
“per-event consequence is hundreds of lives plus aircraft “
“loss; authority over route, schedule, and operational “
“conditions partially shared with dispatch and airline “
“operations.”
),
),
RoleProfile(
role_name=“structural_engineer_in_field”,
consequence_per_event=0.75,
events_per_year=200.0,
career_years=30.0,
system_coupling_of_errors=0.6,
substrate_expenditure_per_event=0.5,
authority_over_working_conditions=0.6,
notes=(
“bridge, building, or infrastructure failure can kill “
“hundreds; engineer holds design authority but often not “
“construction-phase authority.”
),
),
RoleProfile(
role_name=“hazmat_firefighter”,
consequence_per_event=0.7,
events_per_year=500.0,
career_years=25.0,
system_coupling_of_errors=0.6,
substrate_expenditure_per_event=0.9,
authority_over_working_conditions=0.45,
notes=(
“incident commander has operational authority at scene; “
“no control over staffing, equipment, or call volume.”
),
),
RoleProfile(
role_name=“hazmat_rail_engineer”,
consequence_per_event=0.9,
events_per_year=50000.0,
career_years=25.0,
system_coupling_of_errors=0.85,
substrate_expenditure_per_event=0.7,
authority_over_working_conditions=0.2,
notes=(
“East Palestine, Lac-Megantic scale consequence per “
“derailment. Authority over train composition, crew “
“size, rest schedule, brake maintenance resides with “
“rail company management and regulators.”
),
),
RoleProfile(
role_name=“hospital_administrator”,
consequence_per_event=0.6,
events_per_year=50.0,
career_years=25.0,
system_coupling_of_errors=0.5,
substrate_expenditure_per_event=0.2,
authority_over_working_conditions=0.9,
notes=(
“staffing ratio and budget decisions affect patient “
“mortality at scale; feedback timescale is annual; “
“full authority over conditions for downstream “
“consequence-exposed actors (nurses, physicians, “
“support staff).”
),
),
RoleProfile(
role_name=“logistics_vp”,
consequence_per_event=0.5,
events_per_year=30.0,
career_years=25.0,
system_coupling_of_errors=0.6,
substrate_expenditure_per_event=0.15,
authority_over_working_conditions=0.9,
notes=(
“schedule, route, load, and rest-period policies affect “
“consequence exposure of thousands of drivers. Feedback “
“timescale quarterly. Insulated from direct consequence.”
),
),
RoleProfile(
role_name=“corporate_executive”,
consequence_per_event=0.7,
events_per_year=12.0,
career_years=25.0,
system_coupling_of_errors=0.6,
substrate_expenditure_per_event=0.15,
authority_over_working_conditions=0.95,
notes=(
“capital allocation and strategic decisions affect “
“thousands of downstream actors; feedback timescale “
“multi-year; fully insulated from direct consequence.”
),
),
RoleProfile(
role_name=“policy_architect”,
consequence_per_event=0.85,
events_per_year=15.0,
career_years=30.0,
system_coupling_of_errors=0.8,
substrate_expenditure_per_event=0.15,
authority_over_working_conditions=0.8,
notes=(
“policy decisions can produce population-scale outcomes; “
“feedback timescale 5-30 years; by the time consequences “
“arrive the architect has retired or moved roles.”
),
),
RoleProfile(
role_name=“central_bank_governor”,
consequence_per_event=0.9,
events_per_year=12.0,
career_years=10.0,
system_coupling_of_errors=0.9,
substrate_expenditure_per_event=0.2,
authority_over_working_conditions=0.9,
notes=(
“rate decisions affect employment, housing, and household “
“solvency at national scale; feedback timescale 1-5 years; “
“insulated from direct household-level consequence.”
),
),
RoleProfile(
role_name=“academic_researcher”,
consequence_per_event=0.15,
events_per_year=50.0,
career_years=35.0,
system_coupling_of_errors=0.15,
substrate_expenditure_per_event=0.25,
authority_over_working_conditions=0.75,
notes=(
“per-event consequence usually bounded to narrow academic “
“domain; high authority over own research program; “
“insulated from practical consequence of theoretical claims.”
),
),
RoleProfile(
role_name=“middle_manager”,
consequence_per_event=0.15,
events_per_year=1000.0,
career_years=25.0,
system_coupling_of_errors=0.25,
substrate_expenditure_per_event=0.25,
authority_over_working_conditions=0.55,
notes=(
“per-event consequence bounded to team outcomes; moderate “
“authority over immediate team; constrained by upper “
“management on resources and schedule.”
),
),
RoleProfile(
role_name=“barista”,
consequence_per_event=0.03,
events_per_year=80000.0,
career_years=5.0,
system_coupling_of_errors=0.05,
substrate_expenditure_per_event=0.2,
authority_over_working_conditions=0.1,
notes=(
“high event frequency, near-zero per-event consequence, “
“low authority. Included as baseline for comparison.”
),
),
]

# ===========================================================================

# Part 4. Inversion detection

# ===========================================================================

@dataclass
class InversionPair:
“”“Two roles where authority is inverted relative to exposure.”””
high_exposure_role: str
low_exposure_role: str
exposure_gap: float                 # exposure difference (high - low)
authority_gap: float                # authority difference (high - low,
# should be negative for inversion)
inversion_severity: float           # magnitude of the inversion
description: str

def detect_inversions(
roles: List[RoleProfile],
authority_structural_pairs: List[Tuple[str, str]],
) -> List[InversionPair]:
“””
For each structural pair (A, B) where B holds organizational
authority over A’s working conditions, check whether authority
alignment is inverted relative to consequence exposure.

```
structural_pairs entries are (exposed_role, insulated_role)
expected by the org chart.
"""
role_map = {r.role_name: r for r in roles}
pairs: List[InversionPair] = []

for exposed_name, insulated_name in authority_structural_pairs:
    if exposed_name not in role_map or insulated_name not in role_map:
        continue
    exposed = role_map[exposed_name]
    insulated = role_map[insulated_name]

    exp_exposure = exposed.cumulative_career_exposure()
    ins_exposure = insulated.cumulative_career_exposure()
    exposure_gap = exp_exposure - ins_exposure

    exp_authority = exposed.authority_over_working_conditions
    ins_authority = insulated.authority_over_working_conditions
    authority_gap = exp_authority - ins_authority

    # inversion: exposed role has higher exposure AND lower authority
    if exposure_gap > 0 and authority_gap < 0:
        severity = exposure_gap * abs(authority_gap)
        pairs.append(InversionPair(
            high_exposure_role=exposed_name,
            low_exposure_role=insulated_name,
            exposure_gap=exposure_gap,
            authority_gap=authority_gap,
            inversion_severity=severity,
            description=(
                f"{exposed_name} bears "
                f"{exp_exposure:.2f} cumulative exposure but "
                f"only {exp_authority:.2f} authority over "
                f"working conditions; {insulated_name} bears "
                f"{ins_exposure:.2f} exposure and holds "
                f"{ins_authority:.2f} authority"
            ),
        ))

return pairs
```

# Known structural authority pairs in current organizational systems

KNOWN_STRUCTURAL_PAIRS = [
(“hazmat_long_haul_driver”, “logistics_vp”),
(“hazmat_long_haul_driver”, “corporate_executive”),
(“nurse_icu”, “hospital_administrator”),
(“nurse_icu”, “corporate_executive”),
(“hazmat_rail_engineer”, “corporate_executive”),
(“hazmat_rail_engineer”, “logistics_vp”),
(“nuclear_plant_operator”, “corporate_executive”),
(“commercial_airline_pilot”, “corporate_executive”),
(“hazmat_firefighter”, “policy_architect”),
(“barge_pilot_mississippi”, “corporate_executive”),
(“great_lakes_freighter_captain”, “corporate_executive”),
(“structural_engineer_in_field”, “corporate_executive”),
]

# ===========================================================================

# Part 5. Integration with expertise audit

# ===========================================================================

def operational_capacity_boost_from_exposure(
profile: RoleProfile,
) -> float:
“””
Consequence-density increases the value of demonstrated
operational capacity. Capacity demonstrated under high-
consequence, high-frequency conditions is thermodynamically
more expensive to develop and more rigorous evidence of E_A
than capacity demonstrated in low-consequence conditions.

```
This function returns a multiplier that expertise.py can apply
to E_A measurements sourced from high-exposure roles.

Returns a value in [1.0, 2.0]: 1.0 means no boost (baseline),
2.0 means the demonstrated capacity counts twice in E_A scoring.
"""
density_product = (
    profile.consequence_per_event
    * profile.event_frequency_score()
    * profile.system_coupling_of_errors
)
return 1.0 + min(1.0, density_product)
```

# ===========================================================================

# Part 6. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
“id”: 1,
“claim”: (
“across organizational roles, cumulative career exposure “
“negatively correlates with authority over working “
“conditions”
),
“falsification”: (
“sample roles across sectors; compute both quantities; “
“show positive or null correlation”
),
},
{
“id”: 2,
“claim”: (
“structural authority pairs (exposed, insulated) show “
“inversion as the default, not the exception, in modern “
“organizational hierarchies”
),
“falsification”: (
“sample structural pairs; show non-inverted pairs “
“dominate”
),
},
{
“id”: 3,
“claim”: (
“substrate expenditure per event correlates strongly with “
“cumulative career exposure, producing visible organism-”
“level cost in exposed actors (health, sleep, family time, “
“recovery capacity) that insulated actors do not bear”
),
“falsification”: (
“measure health, sleep, family stability, and recovery “
“capacity across matched-income exposed and insulated “
“actors; show no difference”
),
},
{
“id”: 4,
“claim”: (
“operational capacity at high consequence density is “
“systematically undervalued in compensation and formal “
“status relative to operational capacity at low “
“consequence density”
),
“falsification”: (
“measure compensation-per-unit-exposure across role “
“samples; show exposure is rewarded proportionally”
),
},
{
“id”: 5,
“claim”: (
“measurement systems that reward substrate non-burn as a “
“signal of capacity will produce authority structures “
“that inversely track consequence exposure”
),
“falsification”: (
“find a measurement system that explicitly rewards “
“substrate non-burn and does not produce inversion”
),
},
{
“id”: 6,
“claim”: (
“event_frequency and consequence_per_event are approximately “
“independent axes; roles exist at every combination”
),
“falsification”: (
“show that events_per_year and consequence_per_event are “
“strongly correlated across role samples”
),
},
{
“id”: 7,
“claim”: (
“role categories commanding formal authority (executive, “
“administrator, policy, academic) show systematically “
“lower substrate_expenditure_per_event than categories “
“bearing direct consequence (driver, nurse, operator, “
“pilot, firefighter)”
),
“falsification”: (
“measure substrate expenditure across role categories; “
“show parity”
),
},
]

# ===========================================================================

# Part 7. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
“attack”: (
“executives bear consequence for the whole organization, “
“which is larger than any single operational role”
),
“response”: (
“executive consequence is typically filtered through “
“legal liability limitations, insurance structures, “
“severance packages, and reputational recovery pathways “
“that operational actors do not have. The claim that “
“they ‘bear consequence’ conflates legal exposure with “
“substrate exposure. The substrate_expenditure_per_event “
“axis separates these: executives score low because they “
“do not burn body, sleep, or stress regulation at the “
“rate operational actors do.”
),
},
{
“attack”: (
“surgeons’ errors are worse per event than drivers’ errors, “
“so surgeon status is justified”
),
“response”: (
“per-event consequence for surgeons (one patient life) is “
“in fact lower than per-event consequence for hazmat “
“truckers (potential mass casualty). The comparison is “
“inverted in the common framing. Further, surgeons “
“operate with redundancy layers (team, monitoring, “
“anesthesiology, imaging, backup) that truckers do not “
“have. Even if surgeon per-event consequence were higher, “
“the cumulative career product (events x severity x “
“coupling) favors high-frequency operational roles.”
),
},
{
“attack”: (
“drivers, operators, and nurses volunteered for the work, “
“so the authority gap reflects choice, not inversion”
),
“response”: (
“volunteering into a role does not justify a measurement “
“system that misrepresents the role’s exposure. Workers “
“accept positions under information asymmetry about “
“substrate cost and authority conditions. The audit “
“documents the inversion regardless of whether workers “
“consented. Consent does not change what the measurement “
“measures.”
),
},
{
“attack”: (
“this framework undervalues decision complexity, strategic “
“thinking, and long-horizon planning that insulated roles “
“perform”
),
“response”: (
“the framework measures consequence exposure, not decision “
“complexity. These are different quantities and should be “
“measured separately. The claim that insulated roles do “
“more complex or longer-horizon thinking is an empirical “
“claim that requires evidence; much insulated decision-”
“making has shorter effective horizons (quarterly “
“earnings) than operational work (route planning across “
“seasons, equipment maintenance across years, skill “
“development across decades).”
),
},
{
“attack”: (
“authority over working conditions is a reward for “
“competence, so the correlation with exposure is not “
“an inversion but a signal”
),
“response”: (
“this claim requires that authority be assigned through “
“a measurement of competence. It isn’t. Authority is “
“assigned through credentialing pipelines (see expertise “
“audit) that fail to track operational capacity, and “
“through capital ownership and political position. The “
“correlation between authority and insulation from “
“consequence is evidence that the assignment mechanism “
“is not competence-tracking.”
),
},
{
“attack”: (
“some consequence-exposed roles (surgeons, engineers, “
“pilots) do hold substantial authority, so the pattern “
“is not universal”
),
“response”: (
“authority alignment varies by role. The audit documents “
“a distribution, not a universal rule. The roles where “
“alignment exists (solo practice surgeons, captains on “
“their vessels, field engineers with design authority) “
“are specifically the ones where organizational “
“hierarchies have not fully captured the work. They are “
“the exceptions that show the default pattern by contrast.”
),
},
{
“attack”: (
“if high-consequence-exposure roles deserved higher “
“authority, labor markets would already have priced this “
“in”
),
“response”: (
“labor markets price roles in the unit (money) whose “
“measurement failure is documented in earlier audits. “
“The unit does not cleanly measure substrate cost, “
“consequence exposure, or authority asymmetry. Market “
“pricing reflects bargaining power distribution, which “
“is itself a function of the authority structure the “
“audit is measuring. The argument is circular: the “
“market price is used to justify the authority that “
“sets the market price.”
),
},
]

# ===========================================================================

# Part 8. Rendering and summary

# ===========================================================================

def render_role_table(roles: List[RoleProfile]) -> str:
lines: List[str] = []
header = (
f”{‘role’:36s}  “
f”{‘cons’:>5s}  “
f”{‘freq’:>5s}  “
f”{‘cumul’:>6s}  “
f”{‘coup’:>5s}  “
f”{‘subst’:>6s}  “
f”{‘auth’:>5s}  “
f”{‘align’:>6s}”
)
lines.append(header)
lines.append(”-” * len(header))

```
rows = [(r, r.cumulative_career_exposure()) for r in roles]
rows.sort(key=lambda x: x[1], reverse=True)

for r, cumul in rows:
    lines.append(
        f"{r.role_name[:36]:36s}  "
        f"{r.consequence_per_event:5.2f}  "
        f"{r.event_frequency_score():5.2f}  "
        f"{cumul:6.3f}  "
        f"{r.system_coupling_of_errors:5.2f}  "
        f"{r.substrate_expenditure_per_event:6.2f}  "
        f"{r.authority_over_working_conditions:5.2f}  "
        f"{r.authority_alignment_score():6.2f}"
    )
return "\n".join(lines)
```

def render_inversion_report(
inversions: List[InversionPair],
) -> str:
if not inversions:
return “no structural inversions detected.”
lines: List[str] = []
lines.append(“STRUCTURAL AUTHORITY INVERSIONS DETECTED”)
lines.append(”=” * 60)
inversions_sorted = sorted(
inversions, key=lambda i: i.inversion_severity, reverse=True
)
for inv in inversions_sorted:
lines.append(
f”  {inv.high_exposure_role[:30]:30s} “
f”vs {inv.low_exposure_role[:25]:25s}”
)
lines.append(
f”    exposure_gap={inv.exposure_gap:+.3f}  “
f”authority_gap={inv.authority_gap:+.3f}  “
f”severity={inv.inversion_severity:.3f}”
)
return “\n”.join(lines)

if **name** == “**main**”:
import json

```
print("=" * 72)
print("CONSEQUENCE ACCOUNTING: ROLE PROFILES")
print("=" * 72)
print()
print(render_role_table(REFERENCE_ROLES))
print()

print("=" * 72)
print("STRUCTURAL AUTHORITY INVERSION DETECTION")
print("=" * 72)
inversions = detect_inversions(REFERENCE_ROLES, KNOWN_STRUCTURAL_PAIRS)
print(render_inversion_report(inversions))
print()
print(f"inversions found: {len(inversions)} of "
      f"{len(KNOWN_STRUCTURAL_PAIRS)} structural pairs checked")
print()

print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
for p in FALSIFIABLE_PREDICTIONS[:3]:
    print(f"  [{p['id']}] {p['claim'][:68]}")
print(f"=== attack-response matrix: {len(ATTACK_RESPONSES)} entries")
```
