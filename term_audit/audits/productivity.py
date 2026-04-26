"""
term_audit/audits/productivity.py

Audit of the term 'productivity' against signal-definition criteria,
and redefinition from first principles as a ratio of output to
full-dependency input.

Core finding: the conventional productivity ratio (output_in_dollars /
hours_worked) is a failed signal divided by a truncated input. Neither
numerator nor denominator is a defined quantity. The ratio rewards
substrate-depletion operations and penalizes regenerative ones.

Redefinition: real productivity is output divided by the full
dependency chain required to sustainably deliver that output without
drawdown on organism, family, commons, or deferred maintenance.

Under the redefinition, a job is productive iff pay >= true_input.
Otherwise the job is extractive and the apparent productivity gain is
substrate conversion rate.

External operationalizations: docs/EXTERNAL_OPERATIONALIZATIONS.md
maps the gap between conventional and redefined productivity onto
math-econ's VE/VL, LWR, and ER equations in combination (pinned at
Mathematic-economics @ equations-v1). A falling LWR with a rising
ER is the population-scale signature of substrate conversion.

CC0. Stdlib only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from term_audit.schema import (
TermAudit, SignalScore, StandardSetter, FirstPrinciplesPurpose,
)

# ===========================================================================

# Part 1. Audit of conventional productivity as a signal

# ===========================================================================

CONVENTIONAL_PRODUCTIVITY_AUDIT = TermAudit(
term="productivity_conventional",
claimed_signal=(
"output per unit of input, typically measured as dollar value "
"of output per hour of labor input"
),
standard_setters=[
StandardSetter(
name="Bureau of Labor Statistics / national statistical offices",
authority_basis="statutory measurement authority",
incentive_structure=(
"measurement continuity is prioritized over measurement "
"validity; methodology revisions are rare because they "
"break historical series"
),
independence_from_measured=0.4,
),
StandardSetter(
name="management accounting profession",
authority_basis="credentialed practice",
incentive_structure=(
"the measurement is the product. Productivity ratios "
"justify management decisions, including compensation "
"and headcount; incentive to preserve the framing"
),
independence_from_measured=0.1,
),
StandardSetter(
name="economic modeling / macroeconomic profession",
authority_basis="academic credentialing",
incentive_structure=(
"published models depend on aggregate productivity as "
"an input; challenging the measurement invalidates "
"large bodies of existing work"
),
independence_from_measured=0.2,
),
StandardSetter(
name="capital owners and shareholders",
authority_basis="ownership position",
incentive_structure=(
"productivity measured as output-per-wage-hour justifies "
"extraction of surplus; strong incentive to keep the "
"numerator in dollars and the denominator truncated "
"to paid hours"
),
independence_from_measured=0.05,
),
],
signal_scores=[
SignalScore(
criterion="scope_defined",
score=0.1,
justification=(
"numerator 'output' is undefined across contexts. A "
"truck-mile, a completed surgery, a front-run trade, "
"and a social-media post are all booked as 'output' "
"via dollar value. Denominator 'hours' excludes "
"commute, setup, sleep recovery, family maintenance, "
"and every substrate labor required to produce the "
"counted hours. Scope is declared nowhere."
),
),
SignalScore(
criterion="unit_invariant",
score=0.05,
justification=(
"productivity in dollars-per-hour is not invariant "
"across jurisdictions, industries, time periods, or "
"regime changes. The same physical output yields "
"different productivity numbers depending on where "
"and when it was produced."
),
),
SignalScore(
criterion="referent_stable",
score=0.1,
justification=(
"the referent shifts under regime changes without "
"notice. During COVID, productivity rose because fewer "
"workers produced the same dollar output; the referent "
"silently changed from 'output per worker-hour' to "
"'output per remaining worker-hour'. No flag was "
"raised because the word stayed the same."
),
),
SignalScore(
criterion="calibration_exists",
score=0.15,
justification=(
"calibration procedures exist on paper but are "
"undermined by the drift of the underlying unit "
"(dollars) and by methodological revisions to the "
"output basket."
),
),
SignalScore(
criterion="observer_invariant",
score=0.2,
justification=(
"a farmer measuring bushels-per-acre, a manager "
"measuring revenue-per-employee, and an economist "
"measuring real-GDP-per-hour-worked produce "
"incompatible numbers for the same physical activity."
),
),
SignalScore(
criterion="conservation_or_law",
score=0.1,
justification=(
"productivity rises when cost is externalized to the "
"commons or to uncounted substrate. A factory that "
"pollutes measures higher productivity than one that "
"does not, because pollution cost is not in the "
"denominator. This violates any plausible conservation "
"law connecting the ratio to physical reality."
),
),
SignalScore(
criterion="falsifiability",
score=0.2,
justification=(
"productivity claims cannot be falsified as long as "
"the numerator and denominator are free to be "
"redefined. The Cambridge capital controversy "
"(1950s-70s) showed aggregate productivity cannot be "
"derived without circular assumptions."
),
source_refs=[
"Cambridge capital controversy, Robinson 1953, "
"Sraffa 1960"
],
),
],
first_principles=FirstPrinciplesPurpose(
stated_purpose=(
"measure real gains in output per real input, to identify "
"where technology, organization, or practice improvements "
"are producing more with less"
),
physical_referent=(
"ratio of physical goods and services produced to total "
"physical resources and labor consumed, including "
"substrate maintenance"
),
informational_referent=(
"efficiency of transformation from input substrate to "
"output substrate"
),
drift_score=0.85,
drift_justification=(
"current usage drifted from physical efficiency measurement "
"to a financial ratio that rewards substrate externalization. "
"A job that destroys topsoil, depletes worker health, and "
"offloads cost to public infrastructure can score higher "
"than one that regenerates all three. The drift reverses "
"the direction of the measurement relative to its stated "
"purpose."
),
),
correlation_to_real_signal=0.2,
correlation_justification=(
"weakly and inconsistently correlated with real physical "
"efficiency gains. Correlation is dominated by unit drift, "
"cost externalization, and measurement-basket revisions "
"rather than by actual transformation efficiency."
),
notes=(
"conventional productivity fails 7 of 7 signal criteria. "
"It is not a signal. It is a ratio whose numerator and "
"denominator are both captured. It consistently rewards "
"extractive activity and penalizes regenerative activity, "
"which is the opposite of what a thermodynamically honest "
"efficiency measurement would do."
),
)

# ===========================================================================

# Part 2. Dependency-based redefinition

# ===========================================================================

# 

# A job produces output by consuming inputs. The conventional measurement

# counts only paid hours as input. The actual thermodynamic input is the

# full dependency chain required to sustainably deliver the output.

# 

# If pay covers the full dependency chain, the job is productive.

# If pay does not cover it, the difference is drawn from:

# - the organism's own substrate (health, sleep, lifespan)

# - unpaid labor of others (family, community)

# - public subsidy (healthcare, housing, food assistance)

# - deferred maintenance (on organism, on home, on tools, on relationships)

# - ecological commons (soil, air, water, biology)

# 

# The difference is not a productivity gain. It is substrate conversion.

# -------------------------

@dataclass
class DependencyItem:
    """One input required to sustainably deliver the output."""
    name: str
    category: str                       # one of: caloric, sleep, shelter,
    # transport, equipment, medical,
    # social, knowledge, recovery,
    # replacement
    cost_per_unit_output: float         # cost in dollars per unit of output
    optional: bool = False              # if True, short-term absence does
    # not immediately produce drawdown
    drawdown_source: str = ""           # where the cost goes if unpaid:
    # organism, family, commons,
    # public, deferred
    justification: str = ""

DEPENDENCY_CATEGORIES = [
"caloric",         # food sufficient for the physical and cognitive load
"sleep",           # rest sufficient for recovery from the load
"shelter",         # housing that permits recovery
"transport",       # commute to and from the work site
"equipment",       # clothing and tools for the work
"medical",         # maintenance of the substrate
"social",          # relationships that regulate stress
"knowledge",       # learning to stay current in the work
"recovery",        # vacation, weekends, actual rest
"replacement",     # child-rearing, eventual organism replacement
]

@dataclass
class JobDependencyProfile:
    """Full dependency chain for sustainable delivery of a job's output."""
    job_name: str
    output_description: str
    time_basis: str                     # 'hour', 'week', 'year'
    dependencies: List[DependencyItem]
    pay_per_time_basis: float

    def true_input(self) -> float:
        """Sum of all dependency costs."""
        return sum(d.cost_per_unit_output for d in self.dependencies)

    def productivity_verdict(self) -> Dict:
        true_in = self.true_input()
        pay = self.pay_per_time_basis
        gap = pay - true_in
        return {
            "job": self.job_name,
            "pay": pay,
            "true_input": true_in,
            "gap": gap,
            "is_productive": gap >= 0,
            "extraction_rate": -gap if gap < 0 else 0.0,
            "substrate_conversion_rate": -gap if gap < 0 else 0.0,
        }

    def drawdown_breakdown(self) -> Dict[str, float]:
        """If pay < true_input, where is the gap being drawn from?"""
        gap = self.pay_per_time_basis - self.true_input()
        if gap >= 0:
            return {}
        # allocate the gap proportionally across dependencies whose
        # drawdown source is set
        total_cost_with_source = sum(
            d.cost_per_unit_output for d in self.dependencies
            if d.drawdown_source
        )
        if total_cost_with_source == 0:
            return {}
        breakdown: Dict[str, float] = {}
        for d in self.dependencies:
            if not d.drawdown_source:
                continue
            share = d.cost_per_unit_output / total_cost_with_source
            breakdown.setdefault(d.drawdown_source, 0.0)
            breakdown[d.drawdown_source] += share * (-gap)
        return breakdown

# ===========================================================================

# Part 3. Worked example: long-haul food distribution driver

# ===========================================================================

def long_haul_driver_example() -> JobDependencyProfile:
    """
    Worked example for a long-haul food distribution driver running
    70-hour weeks on a Tomah-Superior corridor.

    Numbers are illustrative, scaled per week. Real calibration would
    require cost-of-living data, actual sleep-debt cost estimates,
    and regional dependency pricing.
    """
    return JobDependencyProfile(
        job_name="long_haul_food_distribution_driver",
        output_description=(
            "weekly delivery of perishable food loads on Upper Midwest "
            "corridor routes"
        ),
        time_basis="week",
        pay_per_time_basis=1600.0,   # illustrative weekly net pay
        dependencies=[
            DependencyItem(
                name="food_for_driver",
                category="caloric",
                cost_per_unit_output=210.0,
                drawdown_source="organism",
                justification=(
                    "caloric load for 70-hour week of sedentary-plus-"
                    "physical work requires higher-quality food than "
                    "fuel-stop diet provides"
                ),
            ),
            DependencyItem(
                name="sleep_recovery",
                category="sleep",
                cost_per_unit_output=300.0,
                drawdown_source="organism",
                justification=(
                    "sleep debt from 70-hour weeks accumulates as "
                    "cardiovascular, metabolic, and cognitive cost; "
                    "recovery requires time not provided"
                ),
            ),
            DependencyItem(
                name="housing",
                category="shelter",
                cost_per_unit_output=350.0,
                drawdown_source="organism",
                justification=(
                    "housing that permits recovery sleep and food "
                    "preparation; current pay covers basic housing "
                    "but not maintenance time"
                ),
            ),
            DependencyItem(
                name="transport_to_work",
                category="transport",
                cost_per_unit_output=60.0,
                drawdown_source="organism",
            ),
            DependencyItem(
                name="work_equipment",
                category="equipment",
                cost_per_unit_output=40.0,
                drawdown_source="organism",
            ),
            DependencyItem(
                name="medical_maintenance",
                category="medical",
                cost_per_unit_output=200.0,
                drawdown_source="public",
                justification=(
                    "cardiovascular, musculoskeletal, and metabolic "
                    "maintenance for a body under sustained 70-hour "
                    "load; often drawn from public healthcare or "
                    "deferred entirely"
                ),
            ),
            DependencyItem(
                name="family_social_maintenance",
                category="social",
                cost_per_unit_output=250.0,
                drawdown_source="family",
                justification=(
                    "partner and family absorb the maintenance of "
                    "relationships and home that the driver has no "
                    "time to perform; this is uncounted labor"
                ),
            ),
            DependencyItem(
                name="knowledge_and_licensing",
                category="knowledge",
                cost_per_unit_output=30.0,
                drawdown_source="organism",
            ),
            DependencyItem(
                name="recovery_time",
                category="recovery",
                cost_per_unit_output=400.0,
                drawdown_source="deferred",
                justification=(
                    "actual rest required to prevent cumulative "
                    "load damage; 70-hour weeks do not permit it; "
                    "the cost is deferred to eventual health failure"
                ),
            ),
            DependencyItem(
                name="organism_replacement",
                category="replacement",
                cost_per_unit_output=150.0,
                drawdown_source="family",
                justification=(
                    "child-rearing and eventual replacement of the "
                    "labor force; currently subsidized by family and "
                    "unpaid partner labor"
                ),
            ),
            DependencyItem(
                name="home_and_tool_maintenance",
                category="equipment",
                cost_per_unit_output=80.0,
                drawdown_source="deferred",
                justification=(
                    "home, vehicle, and tool maintenance deferred "
                    "due to no time; cost accumulates as eventual "
                    "failure"
                ),
            ),
        ],
    )

# ===========================================================================

# Part 4. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
"id": 1,
"claim": (
"conventional productivity measurements are positively "
"correlated with cost externalization"
),
"falsification": (
"industries with highest measured productivity gains show "
"no higher externalization than those with lowest gains"
),
},
{
"id": 2,
"claim": (
"under dependency-based definition, most jobs currently "
"labeled high-productivity fail the pay >= true_input test"
),
"falsification": (
"systematic accounting of dependency chains shows pay >= "
"true_input for majority of high-productivity-scored jobs"
),
},
{
"id": 3,
"claim": (
"regenerative work (care, maintenance, teaching, ecological "
"restoration) scores low on conventional productivity "
"because its output is regeneration rather than conversion"
),
"falsification": (
"regenerative work shows high conventional productivity "
"scores when its ecological or social output is properly "
"priced"
),
},
{
"id": 4,
"claim": (
"aggregate productivity gains post-1970 are dominated by "
"substrate conversion and cost externalization, not by "
"real efficiency improvements"
),
"falsification": (
"decomposition of productivity gains shows real efficiency "
"improvements dominate, with externalization a minor term"
),
},
{
"id": 5,
"claim": (
"when true_input is held constant, pay has a non-linear "
"relationship with sustainable output: below true_input, "
"output is sustained only by substrate drawdown"
),
"falsification": (
"workers paid below dependency-chain cost show no elevated "
"health, family, or home-maintenance deterioration relative "
"to workers paid above"
),
},
]

# ===========================================================================

# Part 5. Attack-response matrix

# ===========================================================================

ATTACK_RESPONSES = [
{
"attack": (
"productivity captures real gains when methodology is "
"held constant"
),
"response": (
"methodology is never held constant across regimes. The "
"CPI basket, the labor-hour definition, and the dollar "
"unit all drift. 'Held constant methodology' is a "
"counterfactual, not a property of the measurement."
),
},
{
"attack": (
"productivity is strongly correlated with material "
"wellbeing, therefore it measures something real"
),
"response": (
"decompose the correlation. How much is real substrate "
"gain? How much is cost externalization? How much is unit "
"drift? The correlation exists; its causal structure is "
"unresolved. Claiming the measurement is valid because of "
"the correlation is the fallacy of affirming the "
"consequent."
),
},
{
"attack": (
"without productivity measurement, cross-industry and "
"cross-country comparisons are impossible"
),
"response": (
"this defends the measurement on convenience grounds. "
"Convenience is not validity. A measurement that is "
"convenient and wrong is worse than no measurement, "
"because it guides decisions in wrong directions."
),
},
{
"attack": (
"productivity gains enable leisure and abundance"
),
"response": (
"test empirically. Since 1970, are productivity gains "
"correlated with per-worker leisure time, disposable "
"income adjusted for full dependency cost, or substrate "
"health (ecosystem, family stability, physical health)? "
"For most of the post-1970 period the correlations are "
"weak to negative. The claim is ideological, not empirical."
),
},
{
"attack": (
"dependency-based input is subjective; every person's "
"dependencies are different"
),
"response": (
"dependencies vary across individuals; this does not make "
"them subjective. Caloric requirement, sleep requirement, "
"medical maintenance cost, and replacement cost are "
"measurable per-individual quantities. Measurement "
"requires individual-level data rather than aggregates. "
"The current measurement is aggregate precisely because "
"individual-level accounting would reveal the extraction."
),
},
{
"attack": (
"extractive jobs pay below dependency cost because the "
"market clears at that price, therefore the price is correct"
),
"response": (
"market clearing does not imply thermodynamic sustainability. "
"A market can clear at a price that converts substrate into "
"product, as long as substrate holders have no alternative. "
"Clearing is an equilibrium property of the market, not a "
"validity property of the measurement."
),
},
]

if __name__ == "__main__":
    import json
    print("=== conventional productivity audit ===")
    print(json.dumps(CONVENTIONAL_PRODUCTIVITY_AUDIT.summary(), indent=2))
    print()
    print("failure modes:", CONVENTIONAL_PRODUCTIVITY_AUDIT.failure_modes())
    print()
    print("=== long-haul driver dependency profile ===")
    profile = long_haul_driver_example()
    verdict = profile.productivity_verdict()
    print(json.dumps(verdict, indent=2))
    print()
    print("drawdown breakdown (who pays the gap):")
    for source, amount in profile.drawdown_breakdown().items():
        print(f"  {source:12s}  {amount:8.2f}")
    print()
    print("=== falsifiable predictions:", len(FALSIFIABLE_PREDICTIONS))
    for p in FALSIFIABLE_PREDICTIONS:
        print(f"  [{p['id']}] {p['claim']}")
    print()
    print("=== attack-response matrix:", len(ATTACK_RESPONSES), "entries")
