“””
term_audit/incentive_analysis.py

Horizontal analysis of incentive structures across all term audits.

Core claim: measurement systems do not stay captured randomly. They are
captured by identifiable incentive structures, at identifiable rates,
through identifiable pathways. A term audit identifies the capture in
one term. An incentive analysis across many terms identifies the
patterns that produced the capture and predicts which measurement
systems are next.

This module reads term audits as data. It extracts standard-setter
information, computes capture metrics per term and per setter-type,
ranks capture severity, identifies cross-term patterns, and surfaces
structural resistance opportunities.

It also produces a falsifiable prediction: given the observed capture
pattern, which currently-uncaptured measurement systems are structurally
most vulnerable to capture next?

CC0. Stdlib only.
“””

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from term_audit.schema import TermAudit, StandardSetter

# ===========================================================================

# Part 1. Setter archetypes

# ===========================================================================

# 

# Standard-setters across term audits fall into a small number of

# structural archetypes. Classifying them this way lets us aggregate

# across terms and see which archetypes most consistently drive capture.

# —————————————————————————

SETTER_ARCHETYPES = [
“credentialed_profession”,       # accountants, doctors, engineers,
# economists, consultants
“statutory_authority”,           # central banks, tax agencies,
# regulatory bodies, statistical
# offices
“market_infrastructure”,         # exchanges, clearinghouses,
# pricing agencies, rating agencies
“ownership_position”,            # capital owners, shareholders,
# rentiers
“academic_discipline”,           # economics, clinical medicine as
# taught, law as taught
“physical_instrumentation”,      # calibrated measurement devices
# and their operators
“practitioner_domain”,           # first-person or domain-specific
# knowledge holders (the person
# with the need; craftspeople;
# ecologists; farmers)
“physical_law”,                  # thermodynamics, conservation,
# biogeochemistry as discipline
“legal_enforcement”,             # courts, police, regulatory
# enforcement
“administrative_bureaucracy”,    # HR, compliance, school systems,
# insurance administrators
]

def classify_setter(setter: StandardSetter) -> str:
“””
Heuristic classification of a StandardSetter into an archetype.
Based on keyword match on name and authority_basis.
“””
name = setter.name.lower()
authority = setter.authority_basis.lower()
combined = name + “ “ + authority

```
rules = [
    ("physical_law", [
        "thermodynamic", "biogeochemistry", "ecology as", "physics",
        "conservation law",
    ]),
    ("physical_instrumentation", [
        "instrumentation", "imaging", "laboratory measurement",
        "calibrated"
    ]),
    ("practitioner_domain", [
        "person with the need", "craftspe", "practitioner",
        "domain", "farmer", "ecologist", "first-person",
    ]),
    ("market_infrastructure", [
        "market makers", "exchange", "clearing", "rating agenc",
        "pricing agenc", "financial market",
    ]),
    ("statutory_authority", [
        "central bank", "tax authorit", "regulatory", "statistical",
        "bureau of labor", "ada", "statutory",
    ]),
    ("credentialed_profession", [
        "accounting", "auditing", "consult", "engineering prof",
        "industrial engineering", "management account", "clinical",
        "credentialed practice",
    ]),
    ("academic_discipline", [
        "academic", "economics profession", "economic modeling",
        "macroeconomic",
    ]),
    ("ownership_position", [
        "capital owner", "shareholder", "ownership",
    ]),
    ("legal_enforcement", [
        "court", "police", "enforcement",
    ]),
    ("administrative_bureaucracy", [
        "hr ", "human resources", "compliance", "insurance",
        "school system", "administra",
    ]),
]

for archetype, keywords in rules:
    for kw in keywords:
        if kw in combined:
            return archetype

return "credentialed_profession"  # default; most setters are this
```

# ===========================================================================

# Part 2. Per-term incentive profile

# ===========================================================================

@dataclass
class TermIncentiveProfile:
“”“Incentive analysis of a single term audit.”””
term: str
setters: List[Tuple[str, StandardSetter]]   # (archetype, setter)
mean_independence: float
weakest_setter: Optional[Tuple[str, StandardSetter]]
strongest_setter: Optional[Tuple[str, StandardSetter]]
capture_risk: float                         # 0.0 low, 1.0 high
dominant_archetype: str
archetype_count: Dict[str, int]

def analyze_term(audit: TermAudit) -> TermIncentiveProfile:
classified: List[Tuple[str, StandardSetter]] = [
(classify_setter(s), s) for s in audit.standard_setters
]

```
if not classified:
    return TermIncentiveProfile(
        term=audit.term,
        setters=[],
        mean_independence=0.0,
        weakest_setter=None,
        strongest_setter=None,
        capture_risk=1.0,
        dominant_archetype="none",
        archetype_count={},
    )

independences = [s.independence_from_measured for _, s in classified]
mean_ind = sum(independences) / len(independences)

weakest = min(classified, key=lambda x: x[1].independence_from_measured)
strongest = max(classified, key=lambda x: x[1].independence_from_measured)

# capture risk: inverse of mean independence, weighted by how
# concentrated the standard-setting is among captured archetypes
captured_archetypes = {
    "credentialed_profession",
    "market_infrastructure",
    "ownership_position",
    "academic_discipline",
    "administrative_bureaucracy",
}
captured_share = sum(
    1 for arch, _ in classified if arch in captured_archetypes
) / len(classified)
capture_risk = min(1.0, (1.0 - mean_ind) * 0.7 + captured_share * 0.3)

counts: Dict[str, int] = defaultdict(int)
for arch, _ in classified:
    counts[arch] += 1
dominant = max(counts.items(), key=lambda x: x[1])[0]

return TermIncentiveProfile(
    term=audit.term,
    setters=classified,
    mean_independence=mean_ind,
    weakest_setter=weakest,
    strongest_setter=strongest,
    capture_risk=capture_risk,
    dominant_archetype=dominant,
    archetype_count=dict(counts),
)
```

# ===========================================================================

# Part 3. Cross-term pattern analysis

# ===========================================================================

@dataclass
class ArchetypeAggregate:
“”“Aggregate behavior of an archetype across all terms.”””
archetype: str
appearance_count: int
mean_independence: float
min_independence: float
max_independence: float
terms_appeared_in: List[str]

@dataclass
class CrossTermReport:
term_profiles: List[TermIncentiveProfile]
archetype_aggregates: Dict[str, ArchetypeAggregate]
highest_capture_risk: List[Tuple[str, float]]        # (term, risk)
lowest_capture_risk: List[Tuple[str, float]]
most_captured_archetypes: List[Tuple[str, float]]    # by mean ind
least_captured_archetypes: List[Tuple[str, float]]
structural_resistance_opportunities: List[Dict]
capture_vulnerability_predictions: List[Dict]

def analyze_cross_term(audits: List[TermAudit]) -> CrossTermReport:
profiles = [analyze_term(a) for a in audits]

```
# Aggregate by archetype
arch_collect: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
for p in profiles:
    for arch, setter in p.setters:
        arch_collect[arch].append(
            (p.term, setter.independence_from_measured)
        )

aggregates: Dict[str, ArchetypeAggregate] = {}
for arch, entries in arch_collect.items():
    inds = [e[1] for e in entries]
    terms = sorted(set(e[0] for e in entries))
    aggregates[arch] = ArchetypeAggregate(
        archetype=arch,
        appearance_count=len(entries),
        mean_independence=sum(inds) / len(inds),
        min_independence=min(inds),
        max_independence=max(inds),
        terms_appeared_in=terms,
    )

# Risk rankings
risks = [(p.term, p.capture_risk) for p in profiles]
risks_sorted = sorted(risks, key=lambda x: x[1], reverse=True)
highest = risks_sorted[:5]
lowest = sorted(risks, key=lambda x: x[1])[:5]

# Archetype capture rankings
arch_rankings = [
    (a.archetype, a.mean_independence)
    for a in aggregates.values()
]
most_captured = sorted(arch_rankings, key=lambda x: x[1])[:5]
least_captured = sorted(
    arch_rankings, key=lambda x: x[1], reverse=True
)[:5]

# Structural resistance opportunities: archetypes that appear in
# multiple terms with high independence scores. These are the
# natural allies for auditing across the whole tier.
resistance = []
for arch, agg in aggregates.items():
    if agg.mean_independence >= 0.6 and agg.appearance_count >= 2:
        resistance.append({
            "archetype": arch,
            "mean_independence": agg.mean_independence,
            "appearance_count": agg.appearance_count,
            "terms": agg.terms_appeared_in,
            "note": (
                "high-independence setters; candidate allies for "
                "audit work; their credibility is not downstream "
                "of the captured measurement"
            ),
        })

# Capture vulnerability predictions: terms whose dominant archetype
# is in the most-captured list are at highest risk of further drift
vulnerability = []
captured_archetypes = set(a for a, _ in most_captured)
for p in profiles:
    if p.dominant_archetype in captured_archetypes:
        vulnerability.append({
            "term": p.term,
            "dominant_archetype": p.dominant_archetype,
            "capture_risk": p.capture_risk,
            "prediction": (
                "further drift expected unless structural "
                "resistance is introduced; watch for new "
                "measurement methodologies that further serve "
                "the dominant archetype's incentives"
            ),
        })

return CrossTermReport(
    term_profiles=profiles,
    archetype_aggregates=aggregates,
    highest_capture_risk=highest,
    lowest_capture_risk=lowest,
    most_captured_archetypes=most_captured,
    least_captured_archetypes=least_captured,
    structural_resistance_opportunities=resistance,
    capture_vulnerability_predictions=vulnerability,
)
```

# ===========================================================================

# Part 4. Falsifiable predictions

# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
{
“id”: 1,
“claim”: (
“capture risk is higher for terms whose dominant setter “
“archetype is credentialed_profession, market_”
“infrastructure, or ownership_position than for terms “
“dominated by physical_law or practitioner_domain”
),
“falsification”: (
“rank terms by measured drift_score across a sample; show “
“the ranking does not correlate with dominant archetype”
),
},
{
“id”: 2,
“claim”: (
“measurement systems captured by low-independence “
“archetypes drift faster than those anchored by high-”
“independence archetypes”
),
“falsification”: (
“longitudinal measurement of methodology revisions; show “
“revision rate does not track archetype independence”
),
},
{
“id”: 3,
“claim”: (
“across all Tier 1 economic terms, the same small set of “
“archetypes dominates the setter population: credentialed_”
“profession, market_infrastructure, statutory_authority, “
“ownership_position”
),
“falsification”: (
“audit Tier 1 terms and show dominant archetypes are “
“distributed across all ten categories”
),
},
{
“id”: 4,
“claim”: (
“physical_law and practitioner_domain archetypes appear “
“rarely in Tier 1 economic terms and more frequently in “
“Tier 4 (capacity measurement) and Tier 7 (environmental) “
“terms”
),
“falsification”: (
“measure archetype distribution across tiers; show uniform “
“distribution”
),
},
{
“id”: 5,
“claim”: (
“terms with zero physical_law or physical_instrumentation “
“setters are systematically unfalsifiable”
),
“falsification”: (
“find a term with no physical_law or instrumentation “
“setters that is nevertheless falsifiable in the formal “
“sense”
),
},
{
“id”: 6,
“claim”: (
“the structural_resistance_opportunities identified by “
“this analysis are the same communities that have “
“historically produced measurement reform from outside “
“the captured profession”
),
“falsification”: (
“historical analysis of measurement reforms shows reform “
“came from captured archetypes at the same rate as from “
“high-independence archetypes”
),
},
]

# ===========================================================================

# Part 5. Text report

# ===========================================================================

def render_report(report: CrossTermReport) -> str:
lines: List[str] = []
lines.append(”=” * 72)
lines.append(“CROSS-TERM INCENTIVE ANALYSIS”)
lines.append(”=” * 72)
lines.append(””)
lines.append(f”terms analyzed: {len(report.term_profiles)}”)
lines.append(f”unique setter archetypes: “
f”{len(report.archetype_aggregates)}”)
lines.append(””)

```
lines.append("--- per-term capture risk ---")
for p in sorted(report.term_profiles,
                key=lambda x: x.capture_risk, reverse=True):
    lines.append(
        f"  {p.term[:45]:45s}  "
        f"risk={p.capture_risk:.2f}  "
        f"mean_ind={p.mean_independence:.2f}  "
        f"dominant={p.dominant_archetype}"
    )
lines.append("")

lines.append("--- archetype aggregates ---")
agg_sorted = sorted(
    report.archetype_aggregates.values(),
    key=lambda a: a.mean_independence,
)
for a in agg_sorted:
    lines.append(
        f"  {a.archetype:32s}  "
        f"appearances={a.appearance_count:2d}  "
        f"mean_ind={a.mean_independence:.2f}  "
        f"range=[{a.min_independence:.2f},{a.max_independence:.2f}]"
    )
lines.append("")

lines.append("--- most captured archetypes (lowest independence) ---")
for arch, ind in report.most_captured_archetypes:
    lines.append(f"  {arch:32s}  mean_ind={ind:.2f}")
lines.append("")

lines.append("--- least captured archetypes (highest independence) ---")
for arch, ind in report.least_captured_archetypes:
    lines.append(f"  {arch:32s}  mean_ind={ind:.2f}")
lines.append("")

lines.append("--- structural resistance opportunities ---")
for opp in report.structural_resistance_opportunities:
    lines.append(
        f"  {opp['archetype']:32s}  "
        f"mean_ind={opp['mean_independence']:.2f}  "
        f"appearances={opp['appearance_count']}"
    )
lines.append("")

lines.append("--- capture vulnerability predictions ---")
for v in report.capture_vulnerability_predictions:
    lines.append(
        f"  {v['term'][:45]:45s}  "
        f"via {v['dominant_archetype']}  "
        f"risk={v['capture_risk']:.2f}"
    )
lines.append("")

return "\n".join(lines)
```

# ===========================================================================

# Part 6. Run across existing audits

# ===========================================================================

def load_all_existing_audits() -> List[TermAudit]:
“”“Import and return all TermAudit objects from the audits package.”””
audits: List[TermAudit] = []

```
from term_audit.audits.money import MONEY_AUDIT
audits.append(MONEY_AUDIT)

from term_audit.audits.productivity import (
    CONVENTIONAL_PRODUCTIVITY_AUDIT,
)
audits.append(CONVENTIONAL_PRODUCTIVITY_AUDIT)

from term_audit.audits.efficiency import (
    CONVENTIONAL_EFFICIENCY_AUDIT,
)
audits.append(CONVENTIONAL_EFFICIENCY_AUDIT)

from term_audit.audits.disability import (
    DISABILITY_A, DISABILITY_B, DISABILITY_C,
)
audits.extend([DISABILITY_A, DISABILITY_B, DISABILITY_C])

from term_audit.audits.value import (
    COLLAPSED_VALUE_AUDIT, USE_VALUE_AUDIT,
    EXCHANGE_VALUE_AUDIT, SUBSTRATE_VALUE_AUDIT,
)
audits.extend([
    COLLAPSED_VALUE_AUDIT, USE_VALUE_AUDIT,
    EXCHANGE_VALUE_AUDIT, SUBSTRATE_VALUE_AUDIT,
])

return audits
```

if **name** == “**main**”:
import json

```
audits = load_all_existing_audits()
report = analyze_cross_term(audits)

print(render_report(report))
print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
for p in FALSIFIABLE_PREDICTIONS:
    print(f"  [{p['id']}] {p['claim'][:70]}")
```
