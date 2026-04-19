"""
regulatory/frameworks.py

Regulatory framework definitions and toe-in points.

Each framework is defined by:
  - jurisdiction and statutory authority
  - the triggering condition (what crosses the threshold)
  - what actions/liabilities the crossing creates
  - the relevant basin dimensions our framework tracks that correspond
    to the framework's triggering pathway

These are INFORMATIONAL TOE-IN POINTS, not legal advice. The framework
does NOT claim to:
  - determine actual regulatory liability
  - replace legal counsel
  - produce regulatory-grade risk assessments

What it DOES do: show a firm whose metabolic-accounting state has hit
BLACK or near-BLACK signals, the real-world regulatory frameworks
their condition would plausibly engage in each jurisdiction. This
turns a thermodynamic signal into a map: "your tertiary pool is past
cliff AND aquifer contamination crosses the cliff — here are the four
regulatory regimes this could plausibly trigger, with reference links
and the condition each uses."

The goal is STANDARDIZATION and COMPARABILITY across corporate ecological
failure, not legal prediction.
"""

from dataclasses import dataclass, field
from typing import List, Set


@dataclass(frozen=True)
class RegulatoryFramework:
    """One jurisdiction's framework for handling corporate-caused
    ecological damage at or approaching landscape scale."""

    # identity
    jurisdiction: str              # country / region / supranational body
    short_name: str                # e.g. "CERCLA/Superfund"
    full_name: str
    statute: str                   # legal citation
    authority: str                 # regulatory body

    # triggering condition
    pathway_types: Set[str]        # "groundwater", "surface_water",
                                    # "soil_exposure", "air", "biodiversity"
    trigger_description: str       # human-readable summary
    threshold_mechanism: str       # e.g. "HRS score >= 28.5" or
                                    # "significant adverse effect on favourable
                                    #  conservation status"
    quantitative_threshold: str    # specific number where one exists

    # what the crossing creates
    liability_scheme: str          # "strict joint and several" / "strict" / "fault-based"
    financial_mechanism: str       # how cleanup is funded
    typical_actions: List[str]

    # metabolic-accounting correspondence
    corresponds_to_basins: Set[str]     # which of our basin types this
                                         # framework most engages
    corresponds_to_reserves: Set[str]   # which tertiary pools align
    # severity indicators
    triggers_on_primary_irreversibility: bool
    triggers_on_tertiary_cliff: bool
    notes: str

    # documentation
    source_url: str


# ---- United States: CERCLA / Superfund ----

CERCLA_SUPERFUND = RegulatoryFramework(
    jurisdiction="United States",
    short_name="CERCLA/Superfund",
    full_name="Comprehensive Environmental Response, Compensation, and Liability Act",
    statute="42 U.S.C. §§ 9601-9675 (1980), amended by SARA 1986",
    authority="US Environmental Protection Agency (EPA)",
    pathway_types={"groundwater", "surface_water", "soil_exposure", "air"},
    trigger_description=(
        "Release or threatened release of hazardous substances, pollutants, "
        "or contaminants. Site assessed via Hazard Ranking System (HRS) "
        "evaluating four pathways; sites scoring >= 28.5 on the 0-100 scale "
        "are eligible for the National Priorities List (NPL)."
    ),
    threshold_mechanism="HRS score aggregated over four pathway scores",
    quantitative_threshold="HRS score >= 28.5 (on 0-100 scale)",
    liability_scheme="strict, joint and several",
    financial_mechanism=(
        "Potentially Responsible Parties (PRPs) pay cleanup costs; federal "
        "Superfund backstop since 1995 funded by Congressional appropriations "
        "after petroleum/chemical feedstock taxes expired"
    ),
    typical_actions=[
        "NPL listing (informational, not liability-assigning)",
        "PRP identification and cost-recovery action",
        "Remedial Investigation / Feasibility Study (RI/FS)",
        "Record of Decision (ROD) on cleanup remedy",
        "Long-term remedial action financed by PRPs or Superfund",
    ],
    corresponds_to_basins={"soil", "water", "air", "biology"},
    corresponds_to_reserves={"watershed_reserve", "landscape_reserve",
                             "airshed_reserve"},
    triggers_on_primary_irreversibility=True,
    triggers_on_tertiary_cliff=True,
    notes=(
        "HRS uses three factor categories per pathway: likelihood of release, "
        "waste characteristics (toxicity/persistence/quantity), and targets "
        "(people and sensitive environments exposed). The 28.5 threshold was "
        "set originally to yield approximately 400 NPL sites as Congress "
        "requested; it has no direct biophysical meaning. Placement on NPL "
        "is informational but signals likely PRP action."
    ),
    source_url="https://www.epa.gov/superfund",
)


# ---- European Union: Environmental Liability Directive ----

EU_ELD = RegulatoryFramework(
    jurisdiction="European Union (27 Member States)",
    short_name="EU ELD",
    full_name="Environmental Liability Directive 2004/35/EC",
    statute="Directive 2004/35/EC of 21 April 2004",
    authority=(
        "Member State competent authorities; European Commission oversight"
    ),
    pathway_types={"groundwater", "surface_water", "soil_exposure",
                   "biodiversity"},
    trigger_description=(
        "Environmental damage or imminent threat thereof. Three damage "
        "categories: damage to protected species and natural habitats, to "
        "water, and to soil. Each category has a 'significance threshold'. "
        "Strict liability for Annex III activities (industrial/hazardous); "
        "fault-based for others (biodiversity damage only)."
    ),
    threshold_mechanism=(
        "'Significant adverse effect' on favourable conservation status "
        "(biodiversity), significant adverse effect on ecological/chemical "
        "status under Water Framework Directive (water), or significant risk "
        "of adverse effect on human health (soil/land contamination)"
    ),
    quantitative_threshold=(
        "No single numeric threshold. 'Significance' determined by Member "
        "States applying WFD ecological status classes, Habitats Directive "
        "conservation status, or national contaminated-soil standards."
    ),
    liability_scheme="strict (Annex III) or fault-based (non-Annex III)",
    financial_mechanism=(
        "Polluter pays. Operator responsible for prevention and remediation "
        "costs. Member States may (not must) require mandatory financial "
        "security/insurance."
    ),
    typical_actions=[
        "Imminent threat notification to competent authority",
        "Preventive measures (obligation, no threshold required)",
        "Remediation plan submitted to and approved by authority",
        "Primary, complementary, and compensatory remediation",
        "Cost recovery action by authority if operator fails to act",
    ],
    corresponds_to_basins={"soil", "water", "biology"},
    corresponds_to_reserves={"watershed_reserve", "landscape_reserve"},
    triggers_on_primary_irreversibility=True,
    triggers_on_tertiary_cliff=True,
    notes=(
        "The ELD deals with 'pure ecological damage' and does not cover "
        "criminal liability (separate Environmental Crime Directive) or "
        "civil property/personal injury damage. The upcoming Soil Monitoring "
        "and Resilience Directive will create Member-State registers of "
        "contaminated and potentially contaminated sites, tightening the "
        "identification side of the ELD framework."
    ),
    source_url=(
        "https://environment.ec.europa.eu/law-and-governance/"
        "environmental-compliance-assurance/environmental-liability_en"
    ),
)


# ---- United Kingdom: Part 2A Contaminated Land Regime ----

UK_PART_2A = RegulatoryFramework(
    jurisdiction="United Kingdom (England/Wales; separate regimes in Scotland, NI)",
    short_name="UK Part 2A",
    full_name=(
        "Part 2A of the Environmental Protection Act 1990 "
        "(contaminated land regime)"
    ),
    statute=(
        "Environmental Protection Act 1990, Part 2A (inserted by "
        "Environment Act 1995)"
    ),
    authority="Local authorities; Environment Agency for special sites",
    pathway_types={"groundwater", "surface_water", "soil_exposure"},
    trigger_description=(
        "Land appearing to the local authority to be in such a condition, by "
        "reason of substances in, on or under it, that 'significant harm' "
        "or 'significant possibility of significant harm' (SPOSH) is being "
        "caused or is a significant possibility. Alternatively, where "
        "'significant pollution of controlled waters' is being caused or "
        "is likely."
    ),
    threshold_mechanism=(
        "Source-Pathway-Receptor (SPR) assessment; harm categorised A/B/C/D "
        "per statutory guidance"
    ),
    quantitative_threshold=(
        "No single numeric threshold. Category A harm (most severe) triggers "
        "determination. Guideline values (Soil Guideline Values, GAC) used "
        "as risk-based screening; exceedance alone does not determine land "
        "as contaminated."
    ),
    liability_scheme=(
        "Tiered: Class A (polluter) first, Class B (landowner/occupier) if "
        "polluter not found. 'Appropriate person' doctrine."
    ),
    financial_mechanism=(
        "Remediation notice served on appropriate person. Where no appropriate "
        "person identifiable, local authority may recover costs from orphan-site "
        "fund (limited) or bear cost."
    ),
    typical_actions=[
        "Risk assessment and SPR analysis",
        "Formal determination as contaminated land (Part 2A designation)",
        "Remediation notice or voluntary remediation agreement",
        "Enforcement action for non-compliance",
        "Entry on public register of contaminated land",
    ],
    corresponds_to_basins={"soil", "water"},
    corresponds_to_reserves={"watershed_reserve", "landscape_reserve"},
    triggers_on_primary_irreversibility=True,
    triggers_on_tertiary_cliff=False,
    notes=(
        "Part 2A is being used less over time as voluntary remediation through "
        "the planning system has become the primary pathway. But for orphan "
        "sites and active pollution cases, Part 2A remains the statutory "
        "backstop."
    ),
    source_url=(
        "https://www.legislation.gov.uk/ukpga/1990/43/part/IIA"
    ),
)


# ---- Germany: Bundes-Bodenschutzgesetz (BBodSchG) ----

GERMANY_BBODSCHG = RegulatoryFramework(
    jurisdiction="Germany",
    short_name="BBodSchG (Altlasten)",
    full_name=(
        "Bundes-Bodenschutzgesetz (Federal Soil Protection Act) and "
        "Bundes-Bodenschutz- und Altlastenverordnung (Federal Soil Protection "
        "and Contaminated Sites Ordinance, BBodSchV)"
    ),
    statute=(
        "BBodSchG 17 March 1998 (BGBl. I 502); BBodSchV 12 July 1999 "
        "(BGBl. I 1554), most recently substantially revised 2021"
    ),
    authority="Länder (state) environmental authorities",
    pathway_types={"groundwater", "surface_water", "soil_exposure"},
    trigger_description=(
        "Harmful soil alterations or legacy contamination (Altlasten). "
        "Three-stage assessment: precautionary values (Vorsorgewerte), "
        "trigger values (Prüfwerte), and action values (Massnahmenwerte). "
        "Exceedance of trigger values requires investigation; exceedance of "
        "action values requires remediation."
    ),
    threshold_mechanism=(
        "Three-tier numerical threshold system per pathway and contaminant"
    ),
    quantitative_threshold=(
        "Specific Prüfwerte and Massnahmenwerte per substance and pathway "
        "(soil-human contact, soil-plant, soil-groundwater) in BBodSchV "
        "Annexes 1-4. Examples: lead Massnahmenwert for residential garden "
        "soil 400 mg/kg; TPH groundwater Prüfwert 200 µg/L."
    ),
    liability_scheme="strict (polluter and landowner)",
    financial_mechanism=(
        "Polluter pays primarily; landowner secondarily. State-funded "
        "Altlasten programs in each Land for orphan historical sites."
    ),
    typical_actions=[
        "Historical investigation (Historische Erkundung)",
        "Orientierende Untersuchung (orientational investigation) at trigger exceedance",
        "Detailuntersuchung (detailed investigation)",
        "Sanierungsuntersuchung (remediation investigation)",
        "Sanierungsplan (remediation plan) approval and execution",
    ],
    corresponds_to_basins={"soil", "water"},
    corresponds_to_reserves={"watershed_reserve", "landscape_reserve"},
    triggers_on_primary_irreversibility=True,
    triggers_on_tertiary_cliff=False,
    notes=(
        "Germany's framework is among the most quantitatively detailed in the "
        "world. Each Land maintains its own Altlasten register. The three-tier "
        "threshold system is one of the cleanest examples of stepped "
        "regulatory response to progressive contamination."
    ),
    source_url=(
        "https://www.gesetze-im-internet.de/bbodschg/"
    ),
)


# ---- Japan: Soil Contamination Countermeasures Act ----

JAPAN_SCCA = RegulatoryFramework(
    jurisdiction="Japan",
    short_name="Japan SCCA",
    full_name=(
        "Soil Contamination Countermeasures Act (土壌汚染対策法, "
        "Dojo Osen Taisaku Ho)"
    ),
    statute="Act No. 53 of 2002, amended 2009, 2017, 2019",
    authority="Ministry of the Environment; prefectural governors",
    pathway_types={"groundwater", "soil_exposure"},
    trigger_description=(
        "Designated hazardous substances in soil exceeding specified limits. "
        "Triggers: cessation of specified-facility operations, large-scale "
        "land modification, or investigation order when contamination "
        "suspected from health impact standpoint."
    ),
    threshold_mechanism=(
        "Soil elution standards (for groundwater protection pathway) and "
        "soil content standards (for direct ingestion pathway), per "
        "specified hazardous substance"
    ),
    quantitative_threshold=(
        "Elution standards and content standards for 26 designated "
        "substances in the Act's annexes. Example: arsenic elution standard "
        "0.01 mg/L; content standard 150 mg/kg."
    ),
    liability_scheme="strict (polluter); secondary (landowner)",
    financial_mechanism=(
        "Polluter pays; landowner may bear cost if polluter cannot be "
        "identified. National support programs for small businesses and "
        "orphan-site cases."
    ),
    typical_actions=[
        "Soil investigation report",
        "Designation as Area Requiring Action (Formed Category I) "
        "or Area Requiring Notification (Category II)",
        "Removal, containment, or risk management measures",
        "Cancellation of designation upon remediation",
    ],
    corresponds_to_basins={"soil", "water"},
    corresponds_to_reserves={"watershed_reserve", "landscape_reserve"},
    triggers_on_primary_irreversibility=True,
    triggers_on_tertiary_cliff=False,
    notes=(
        "Japan SCCA is narrowly focused on human-health-pathway "
        "contamination (not ecological damage per se). Ecosystem damage "
        "engages separately under the Basic Environment Law and species "
        "protection statutes."
    ),
    source_url=(
        "https://www.env.go.jp/en/water/soil/contami_law.html"
    ),
)


# ---- Master list ----

ALL_FRAMEWORKS: List[RegulatoryFramework] = [
    CERCLA_SUPERFUND,
    EU_ELD,
    UK_PART_2A,
    GERMANY_BBODSCHG,
    JAPAN_SCCA,
]


def frameworks_for_basin(basin_type: str) -> List[RegulatoryFramework]:
    """Return frameworks that engage a given basin type."""
    return [f for f in ALL_FRAMEWORKS if basin_type in f.corresponds_to_basins]


def frameworks_for_tertiary(pool_name: str) -> List[RegulatoryFramework]:
    """Return frameworks that engage a given tertiary reserve pool."""
    return [
        f for f in ALL_FRAMEWORKS
        if pool_name in f.corresponds_to_reserves
    ]


def frameworks_by_jurisdiction(jurisdiction: str) -> List[RegulatoryFramework]:
    """Return frameworks for a specific jurisdiction (fuzzy match)."""
    j_lower = jurisdiction.lower()
    return [
        f for f in ALL_FRAMEWORKS
        if j_lower in f.jurisdiction.lower()
        or j_lower in f.short_name.lower()
    ]
