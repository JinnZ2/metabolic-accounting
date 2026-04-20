"""
term_audit/governance_design_principles.py

Design constraints for measurement systems that resist capture.

Core claim: The audits across this repository identify recurring
failure patterns in how measurement systems become captured. These
patterns are not random; they follow from specific design choices
that can be avoided. A measurement system designed according to
these principles will resist capture; a system that violates them
will predictably drift.

This module extracts design principles from the full audit corpus:

money audit               → anchor to real substrate, not recursive claims
productivity audit        → measure outputs against inputs, not inputs alone
efficiency audit          → bound by conservation laws, not unbounded
expertise audit           → separate E_A (capacity) from E_B (credential)
value audit               → separate use, exchange, and substrate value
systemic_necessity audit  → authority tracks function necessity
incentive_analysis        → standard-setters must be practitioner-domain
civilization_scaling      → scale-match measurement to coordination problem
collapse_propensity       → preserve smaller-scale functions, prohibit atrophy

Each principle is:

- derived from specific audit findings
- falsifiable (a system violating it should show measurable capture)
- actionable (can be implemented as a design constraint)

This module does not prescribe policy. It provides constraints that
any governance system must satisfy to avoid the documented capture
pathways.

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# ===========================================================================
# Part 1. Design principles
# ===========================================================================

class PrincipleCategory(Enum):
    """Categories of design principles."""
    REFERENT_ANCHORING = "referent_anchoring"      # what is measured
    STANDARD_SETTER = "standard_setter"            # who defines the measure
    SCALE_MATCHING = "scale_matching"              # at what scale applied
    FEEDBACK = "feedback"                          # how reality corrects
    AUTHORITY = "authority"                        # who acts on measurement
    PRESERVATION = "preservation"                  # what must survive


@dataclass
class DesignPrinciple:
    """A falsifiable design constraint for capture-resistant measurement."""
    id: str
    category: PrincipleCategory
    principle: str
    derived_from: List[str]  # which audits produced this principle
    rationale: str
    falsification_test: str  # how to test if violating this matters
    implementation_constraint: str  # what a system must do to satisfy
    violation_example: str  # current systems that violate this


DESIGN_PRINCIPLES = [
    DesignPrinciple(
        id="REF-1",
        category=PrincipleCategory.REFERENT_ANCHORING,
        principle=(
            "Every measurement must have a stable physical or "
            "informational referent. Recursive measurement (measuring "
            "other measurements) produces drift."
        ),
        derived_from=["money", "productivity", "efficiency", "value"],
        rationale=(
            "When a measurement measures only other measurements (e.g., "
            "money measuring money via financial instruments, "
            "productivity measuring GDP which measures transactions), "
            "there is no external anchor. Drift is unbounded. The "
            "referent must be outside the measurement system."
        ),
        falsification_test=(
            "Take a measurement system with only recursive referents. "
            "Show that it does NOT drift from its claimed signal over "
            "50+ years."
        ),
        implementation_constraint=(
            "For any measurement M, there must exist an observable "
            "physical or informational quantity Q such that M is "
            "calibrated against Q, and Q is not itself defined in "
            "terms of M or other measurements in the same system."
        ),
        violation_example=(
            "Financial derivatives whose value references other "
            "financial instruments; GDP which measures transactions "
            "valued in money; university rankings which measure other "
            "rankings and reputation surveys."
        ),
    ),
    DesignPrinciple(
        id="REF-2",
        category=PrincipleCategory.REFERENT_ANCHORING,
        principle=(
            "Collapsed signals must be decomposed. Measurements that "
            "fuse multiple distinct referents into a single token "
            "hide information and enable capture."
        ),
        derived_from=["expertise", "value", "disability"],
        rationale=(
            "When 'expertise' fuses E_A (capacity), E_B (credential), "
            "and E_C (transmission), the token can be relocated to "
            "whichever referent serves the measurer's interest. "
            "Decomposition makes the relocation visible."
        ),
        falsification_test=(
            "Identify a collapsed signal that has not been decomposed. "
            "Show that its usage does NOT drift toward the referent "
            "that serves the standard-setter's interests."
        ),
        implementation_constraint=(
            "Measurements must report components separately. A system "
            "claiming to measure X must report X_A, X_B, X_C if those "
            "are distinct referents. Collapsed reporting is prohibited."
        ),
        violation_example=(
            "Current 'productivity' measures (output/input collapsed); "
            "current 'expert' designation (capacity, credential, "
            "transmission collapsed); current 'value' (use, exchange, "
            "substrate collapsed)."
        ),
    ),
    DesignPrinciple(
        id="REF-3",
        category=PrincipleCategory.REFERENT_ANCHORING,
        principle=(
            "Conservation laws bound legitimate measurement. Claims of "
            "unbounded efficiency, unbounded growth, or unbounded "
            "productivity signal measurement failure."
        ),
        derived_from=["efficiency", "productivity", "thermodynamics"],
        rationale=(
            "Physical processes are bounded by conservation of energy "
            "and mass. Informational processes are bounded by substrate "
            "capacity. A measurement that shows unbounded anything is "
            "either measuring a non-conserved abstraction or is "
            "mis-measuring."
        ),
        falsification_test=(
            "Identify a measurement claiming unbounded growth or "
            "efficiency. Demonstrate that the underlying physical "
            "substrate is not being drawn down."
        ),
        implementation_constraint=(
            "Every measurement must declare its conservation structure. "
            "If no conservation law applies, the measurement must "
            "declare itself non-conserved and report the substrate "
            "cost of its own operation."
        ),
        violation_example=(
            "GDP growth reported without resource throughput; "
            "productivity gains reported without energy input tracking; "
            "efficiency improvements claimed without waste stream "
            "accounting."
        ),
    ),
    DesignPrinciple(
        id="SET-1",
        category=PrincipleCategory.STANDARD_SETTER,
        principle=(
            "Standard-setters must be drawn from practitioner-domain "
            "archetypes, not credentialed-profession or ownership-"
            "position archetypes."
        ),
        derived_from=["incentive_analysis", "expertise", "systemic_necessity"],
        rationale=(
            "The incentive_analysis cross-term audit demonstrates that "
            "credentialed_profession, market_infrastructure, and "
            "ownership_position archetypes have mean independence "
            "scores below 0.3. They reliably produce capture. "
            "Practitioner_domain and physical_law archetypes have mean "
            "independence above 0.7."
        ),
        falsification_test=(
            "Establish a standard-setting body dominated by "
            "credentialed_profession archetype. Measure its drift over "
            "20 years. Show no capture drift."
        ),
        implementation_constraint=(
            "Standard-setting bodies must have majority representation "
            "from currently-practicing practitioners of the measured "
            "domain. Credentialed professionals who do not currently "
            "practice are limited to advisory roles."
        ),
        violation_example=(
            "Accounting standards (FASB, IASB) set by credentialed "
            "accountants, not by users of financial statements; "
            "medical boards set by physicians no longer in practice; "
            "central banks set by economists, not by practitioners of "
            "production and exchange."
        ),
    ),
    DesignPrinciple(
        id="SET-2",
        category=PrincipleCategory.STANDARD_SETTER,
        principle=(
            "Standard-setter recursion depth must be zero. A body that "
            "accredits other bodies that accredit other bodies cannot "
            "maintain calibration to the referent."
        ),
        derived_from=["incentive_analysis", "expertise"],
        rationale=(
            "Each level of recursion adds independent drift. A "
            "credentialing body that is accredited by a body that is "
            "accredited by a body has three levels of unmeasured drift "
            "from the operational referent. The incentive_analysis "
            "shows recursion depth of 3-5 is standard in captured "
            "systems."
        ),
        falsification_test=(
            "Identify a measurement system with recursion depth ≥ 3. "
            "Measure its correlation to operational outcomes. Show "
            "correlation remains high over 30+ years."
        ),
        implementation_constraint=(
            "The body that defines the measurement standard must be "
            "directly accountable to the referent. No intermediate "
            "accrediting bodies. If a body accredits another body, "
            "the referent is the accreditation, not the original "
            "measurement."
        ),
        violation_example=(
            "University accreditation (regional bodies accredit "
            "universities which grant degrees which signal capacity); "
            "professional licensing (state boards accredit exams which "
            "credential practitioners); financial auditing (PCAOB "
            "oversees audit firms which audit companies)."
        ),
    ),
    DesignPrinciple(
        id="SET-3",
        category=PrincipleCategory.STANDARD_SETTER,
        principle=(
            "Cost-gating must not be the primary filter for "
            "standard-setter participation or for access to the "
            "measured status."
        ),
        derived_from=["expertise", "systemic_necessity"],
        rationale=(
            "When access to a credential or to standard-setting "
            "requires substantial payment, the filter selects for "
            "willingness-to-pay, which correlates with class background "
            "and has near-zero correlation with operational capacity. "
            "The measurement becomes a class marker, not a capacity "
            "signal."
        ),
        falsification_test=(
            "Identify a credential with high cost-gating (> $10k). "
            "Measure E_A (operational capacity) distribution in "
            "credentialed vs. non-credentialed populations matched for "
            "practice hours. Show no difference."
        ),
        implementation_constraint=(
            "Cost to participate in standard-setting or to obtain "
            "measured status must not exceed the marginal cost of "
            "administration. Training costs must be separable from "
            "credentialing costs. Alternative pathways to demonstrate "
            "capacity without cost-gating must exist."
        ),
        violation_example=(
            "Medical school tuition ($200k+) as gate to practice; "
            "law school tuition as gate to bar; graduate school as "
            "gate to research; professional certification fees as "
            "ongoing rent."
        ),
    ),
    DesignPrinciple(
        id="SCA-1",
        category=PrincipleCategory.SCALE_MATCHING,
        principle=(
            "Measurements must be applied only at scales where their "
            "coordination problem exists. Applying a measurement at "
            "smaller or larger scales produces capture."
        ),
        derived_from=["civilization_scaling", "collapse_propensity"],
        rationale=(
            "The civilization_scaling audit shows that each measurement "
            "system emerged to solve a specific coordination problem at "
            "a specific scale. Applied at smaller scales, it crowds out "
            "appropriate mechanisms. Applied at larger scales, it "
            "decouples from its referent."
        ),
        falsification_test=(
            "Apply a measurement at a scale outside its appropriate "
            "range. Measure capture drift over time. Show no increased "
            "drift compared to application within appropriate range."
        ),
        implementation_constraint=(
            "Every measurement system must declare its scale of "
            "emergence and its appropriate range. Application outside "
            "that range requires explicit justification and continuous "
            "recalibration against the referent."
        ),
        violation_example=(
            "Commodity money applied at global scale (decoupled from "
            "commodity); guild certification applied at national scale "
            "(cost-gated credentialing); university credentialing "
            "applied at national/global scale (class reproduction)."
        ),
    ),
    DesignPrinciple(
        id="SCA-2",
        category=PrincipleCategory.SCALE_MATCHING,
        principle=(
            "Smaller-scale substrate functions must not be allowed to "
            "atrophy. A system that loses village-scale food, water, or "
            "knowledge functions is vulnerable to multi-tier collapse."
        ),
        derived_from=["collapse_propensity", "civilization_scaling"],
        rationale=(
            "The collapse_propensity audit demonstrates that atrophy of "
            "smaller-scale functions is the primary amplifier of "
            "collapse depth. When larger-scale coordination fails, "
            "systems fall to the scale where functions are still "
            "maintained."
        ),
        falsification_test=(
            "Identify a civilization that has atrophied village-scale "
            "subsistence functions. Show that collapse of national "
            "coordination would NOT propagate below regional scale."
        ),
        implementation_constraint=(
            "Governance systems must track atrophy of substrate "
            "functions at each scale tier. Atrophy below MAINTAINED "
            "level at any tier requires remediation. Functions in "
            "MINIMUM_VIABLE_CIVILIZATION_FUNCTIONS must be maintained "
            "at ROBUST level at village scale."
        ),
        violation_example=(
            "Current civilization: subsistence food production is "
            "THIN at village scale; ecological observation is "
            "VESTIGIAL; long-horizon stewardship is ATROPHIED below "
            "national scale."
        ),
    ),
    DesignPrinciple(
        id="FEE-1",
        category=PrincipleCategory.FEEDBACK,
        principle=(
            "Feedback timescale must match the consequence timescale. "
            "Measurements with generational feedback loops cannot "
            "constrain annual decision-making."
        ),
        derived_from=["incentive_analysis", "expertise", "collapse_propensity"],
        rationale=(
            "The incentive_analysis shows that capture severity "
            "correlates with feedback timescale (r = -0.75). When "
            "consequences of a bad measurement arrive after the "
            "decision-makers have retired, the measurement drifts "
            "without correction."
        ),
        falsification_test=(
            "Identify a measurement system with generational feedback "
            "timescale. Show that it has NOT drifted from its referent "
            "over 50+ years."
        ),
        implementation_constraint=(
            "For any measurement used in decision-making with "
            "consequence horizon H, the feedback loop confirming or "
            "disconfirming the measurement's validity must operate on "
            "timescale ≤ H/10."
        ),
        violation_example=(
            "Soil degradation measured on generational timescale but "
            "farming decisions made annually; climate models with "
            "century horizons but policy made in 4-year election "
            "cycles; credentialing with career-length feedback but "
            "hiring decisions made immediately."
        ),
    ),
    DesignPrinciple(
        id="FEE-2",
        category=PrincipleCategory.FEEDBACK,
        principle=(
            "Financialization of failure detection is prohibited. "
            "Insurance, hedging, and liability transfer do not "
            "substitute for operational feedback."
        ),
        derived_from=["collapse_propensity", "metabolic_accounting"],
        rationale=(
            "When failure detection is financialized, the signal of "
            "failure becomes a claim on a counterparty rather than "
            "information about the system. The system continues to "
            "degrade while claims accumulate. Collapse depth amplifies."
        ),
        falsification_test=(
            "Identify a system where failure detection is primarily "
            "financialized. Show that it detects and corrects failures "
            "faster than a system with direct operational feedback."
        ),
        implementation_constraint=(
            "Systems must maintain direct operational feedback loops. "
            "Financial instruments may supplement but not replace "
            "operational monitoring. A firm that insures against a "
            "failure must still measure and report the underlying "
            "failure probability."
        ),
        violation_example=(
            "Firms that insure against environmental liability rather "
            "than monitoring environmental performance; banks that "
            "hedge credit risk rather than assessing borrower capacity; "
            "pension funds that transfer longevity risk rather than "
            "tracking demographic substrate."
        ),
    ),
    DesignPrinciple(
        id="AUT-1",
        category=PrincipleCategory.AUTHORITY,
        principle=(
            "Authority over a function must track function necessity. "
            "Roles with higher function_necessity scores must have "
            "authority over decisions that affect that function."
        ),
        derived_from=["systemic_necessity"],
        rationale=(
            "The systemic_necessity audit documents systematic "
            "inversion: roles with highest function necessity (farmer, "
            "nurse, driver, operator) have lowest formal authority. "
            "Roles with lowest function necessity (executive, "
            "administrator) have highest formal authority. This "
            "inversion routes decisions through actors with no "
            "operational capacity in the domain."
        ),
        falsification_test=(
            "Compare decision quality in systems where authority tracks "
            "function necessity vs. systems where it is inverted. Show "
            "no difference in operational outcomes."
        ),
        implementation_constraint=(
            "For any domain D, the body with authority over decisions "
            "affecting D must have majority representation from "
            "practitioners whose function_necessity score for D is "
            "≥ 0.7."
        ),
        violation_example=(
            "Hospital administrators (necessity 0.3) with authority "
            "over ICU nurses (necessity 0.95); corporate executives "
            "(necessity 0.2) with authority over farmers (necessity "
            "1.0); policy architects (necessity 0.35) with authority "
            "over hazmat firefighters (necessity 0.9)."
        ),
    ),
    DesignPrinciple(
        id="AUT-2",
        category=PrincipleCategory.AUTHORITY,
        principle=(
            "Compensation must reflect function necessity and substrate "
            "cost, not capture rent. The current inversion (low-"
            "necessity roles paid more) is a measurement failure."
        ),
        derived_from=["systemic_necessity", "value"],
        rationale=(
            "When compensation inverts function necessity, the "
            "incentive structure pulls talent away from necessary "
            "functions toward captured coordination roles. This "
            "accelerates atrophy of substrate functions."
        ),
        falsification_test=(
            "Identify a civilization where compensation inverted "
            "function necessity for >100 years. Show no acceleration "
            "of substrate function atrophy."
        ),
        implementation_constraint=(
            "Compensation systems must report the function_necessity "
            "score of each role. Inversion (higher pay for lower "
            "necessity) must be explicitly justified by factors other "
            "than capture rent. Substrate cost of compensation must be "
            "accounted."
        ),
        violation_example=(
            "Current compensation across all industrial economies: "
            "financial services workers (necessity 0.3) paid multiples "
            "of farmers (necessity 1.0) and nurses (necessity 0.95)."
        ),
    ),
    DesignPrinciple(
        id="PRE-1",
        category=PrincipleCategory.PRESERVATION,
        principle=(
            "Minimum viable civilization functions must be preserved "
            "at village scale regardless of larger-scale efficiency. "
            "These functions are non-optional substrate."
        ),
        derived_from=["civilization_scaling", "collapse_propensity", "recovery_pathways"],
        rationale=(
            "The recovery_pathways audit shows that preservation of "
            "these functions through collapse is the primary "
            "determinant of recovery speed. Atrophy of these functions "
            "extends recovery by generations or makes it impossible."
        ),
        falsification_test=(
            "Identify a civilization that allowed village-scale "
            "subsistence functions to atrophy completely. Show that "
            "recovery from collapse was still possible within one "
            "generation."
        ),
        implementation_constraint=(
            "Governance systems must maintain MINIMUM_VIABLE_"
            "CIVILIZATION_FUNCTIONS at ROBUST level at village scale. "
            "Efficiency gains at larger scales may not come at the "
            "expense of these functions' viability at smaller scales."
        ),
        violation_example=(
            "Current civilization: subsistence food production at "
            "village scale is THIN; ecological observation is "
            "VESTIGIAL; long-horizon stewardship is ATROPHIED."
        ),
    ),
    DesignPrinciple(
        id="PRE-2",
        category=PrincipleCategory.PRESERVATION,
        principle=(
            "Knowledge transmission must be maintained in multiple "
            "redundant forms, including non-digital and non-"
            "institutional forms. Single-point-of-failure knowledge "
            "systems produce generational collapse when the point fails."
        ),
        derived_from=["recovery_pathways", "civilization_scaling"],
        rationale=(
            "Historical recoveries show that loss of writing (Bronze "
            "Age, post-Roman Britain, Classic Maya) extended recovery "
            "by centuries. Current civilization has concentrated "
            "knowledge in digital forms dependent on continuous "
            "infrastructure and in institutions dependent on continuous "
            "funding."
        ),
        falsification_test=(
            "Identify a civilization that lost its primary knowledge "
            "transmission system and recovered full knowledge within "
            "one generation without external preservation."
        ),
        implementation_constraint=(
            "Critical knowledge (food production, water access, "
            "ecological observation, substrate stewardship) must be "
            "maintained in at least three redundant forms: "
            "(1) practicing human communities, (2) durable physical "
            "records, (3) landscape-encoded or oral tradition."
        ),
        violation_example=(
            "Current civilization: most agricultural knowledge exists "
            "in digital form and institutional research stations; few "
            "practicing communities maintain full subsistence knowledge; "
            "oral and landscape-encoded traditions are atrophied."
        ),
    ),
]


# ===========================================================================
# Part 2. Principle compliance assessment
# ===========================================================================

@dataclass
class ComplianceAssessment:
    """Assessment of a system against a design principle."""
    principle_id: str
    system_name: str
    compliance_score: float  # 0.0 fully violates, 1.0 fully complies
    evidence: str
    violation_severity: str  # "critical", "major", "moderate", "minor"
    remediation_possible: bool
    remediation_path: str


def assess_system_compliance(
    system_name: str,
    assessments: List[ComplianceAssessment],
) -> Dict:
    """Aggregate compliance across principles."""
    by_category: Dict[PrincipleCategory, List[float]] = {}
    for ass in assessments:
        for p in DESIGN_PRINCIPLES:
            if p.id == ass.principle_id:
                cat = p.category
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(ass.compliance_score)
                break

    category_scores = {
        cat.value: sum(scores) / len(scores) if scores else 0.0
        for cat, scores in by_category.items()
    }

    overall = (
        sum(category_scores.values()) / len(category_scores)
        if category_scores else 0.0
    )

    critical_violations = [
        ass for ass in assessments
        if ass.violation_severity == "critical" and ass.compliance_score < 0.3
    ]

    return {
        "system": system_name,
        "overall_compliance": overall,
        "category_scores": category_scores,
        "critical_violations": critical_violations,
        "assessment_count": len(assessments),
    }


# ===========================================================================
# Part 3. Example assessments
# ===========================================================================

# Example: assessing current financial accounting against principles

CURRENT_FINANCIAL_ACCOUNTING_ASSESSMENT = [
    ComplianceAssessment(
        principle_id="REF-1",
        system_name="GAAP/IFRS Financial Accounting",
        compliance_score=0.2,
        evidence=(
            "Financial accounting measures money claims on money claims. "
            "Assets are valued at 'fair value' which is often mark-to-"
            "model referencing other financial instruments. No stable "
            "physical referent. The money audit documents this failure."
        ),
        violation_severity="critical",
        remediation_possible=True,
        remediation_path=(
            "Adopt metabolic accounting principles: report basin state "
            "alongside financial state; anchor asset values to physical "
            "substrate where applicable."
        ),
    ),
    ComplianceAssessment(
        principle_id="REF-3",
        system_name="GAAP/IFRS Financial Accounting",
        compliance_score=0.1,
        evidence=(
            "Financial accounting has no conservation structure. Profit "
            "can be reported while consuming non-renewable substrate. "
            "There is no first-law closure on the balance sheet."
        ),
        violation_severity="critical",
        remediation_possible=True,
        remediation_path=(
            "Require thermodynamic closure on all reserve partitions; "
            "report environment loss as extraordinary item."
        ),
    ),
    ComplianceAssessment(
        principle_id="SET-1",
        system_name="GAAP/IFRS Financial Accounting",
        compliance_score=0.15,
        evidence=(
            "Standard-setters (FASB, IASB) are credentialed accountants, "
            "not users of financial statements and not practitioners of "
            "the firms being accounted for."
        ),
        violation_severity="major",
        remediation_possible=True,
        remediation_path=(
            "Restructure standard-setting bodies to include majority "
            "representation from firm operators, basin stewards, and "
            "affected communities."
        ),
    ),
    ComplianceAssessment(
        principle_id="FEE-1",
        system_name="GAAP/IFRS Financial Accounting",
        compliance_score=0.3,
        evidence=(
            "Accounting standards change on generational timescales. "
            "Feedback from accounting failures arrives decades after "
            "standards are set (e.g., pension accounting, lease "
            "accounting, off-balance-sheet entities)."
        ),
        violation_severity="major",
        remediation_possible=True,
        remediation_path=(
            "Shorten standard revision cycle; require continuous "
            "validation against operational outcomes."
        ),
    ),
]


# ===========================================================================
# Part 4. Falsifiable predictions
# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
    {
        "id": 1,
        "claim": (
            "Systems that comply with these principles will show lower "
            "capture drift over 20+ year horizons than systems that "
            "violate them"
        ),
        "falsification": (
            "Track compliance scores and drift metrics across a sample "
            "of measurement systems over 20 years; show no correlation"
        ),
    },
    {
        "id": 2,
        "claim": (
            "Violation of SET-1 (standard-setter archetype) is the "
            "strongest single predictor of capture; systems with "
            "credentialed-profession dominated standard-setters will "
            "drift faster than systems with practitioner-domain "
            "standard-setters, holding other principles constant"
        ),
        "falsification": (
            "Identify systems with different setter archetypes but "
            "similar compliance on other principles; measure drift; "
            "show no difference"
        ),
    },
    {
        "id": 3,
        "claim": (
            "Systems that violate SCA-2 (atrophy of smaller-scale "
            "functions) will experience deeper collapse when larger-"
            "scale coordination fails"
        ),
        "falsification": (
            "Compare collapse depth across systems with different "
            "atrophy patterns; show no correlation"
        ),
    },
    {
        "id": 4,
        "claim": (
            "No existing large-scale measurement system (national "
            "accounts, financial accounting, productivity statistics, "
            "credentialing) achieves compliance score above 0.4 across "
            "all principles"
        ),
        "falsification": (
            "Identify a large-scale measurement system with overall "
            "compliance > 0.6 across all categories"
        ),
    },
    {
        "id": 5,
        "claim": (
            "Systems designed from scratch to satisfy these principles "
            "will face immediate opposition from incumbent archetypes "
            "(credentialed_profession, market_infrastructure, "
            "ownership_position) because compliance threatens their "
            "capture rent"
        ),
        "falsification": (
            "Propose a principle-compliant system and observe no "
            "opposition from incumbent archetypes"
        ),
    },
]


# ===========================================================================
# Part 5. Rendering
# ===========================================================================

def render_principles_by_category() -> str:
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("GOVERNANCE DESIGN PRINCIPLES")
    lines.append("=" * 80)
    lines.append("")

    for cat in PrincipleCategory:
        lines.append(f"\n--- {cat.value.upper()} ---")
        for p in DESIGN_PRINCIPLES:
            if p.category == cat:
                lines.append(f"\n[{p.id}] {p.principle}")
                lines.append(f"    Derived from: {', '.join(p.derived_from)}")
                lines.append(f"    Constraint: {p.implementation_constraint[:100]}...")

    return "\n".join(lines)


def render_compliance_assessment(assessment: Dict) -> str:
    lines: List[str] = []
    lines.append("=" * 80)
    lines.append(f"COMPLIANCE ASSESSMENT: {assessment['system']}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Overall compliance: {assessment['overall_compliance']:.2f}")
    lines.append("")
    lines.append("Category scores:")
    for cat, score in assessment['category_scores'].items():
        lines.append(f"  {cat}: {score:.2f}")
    lines.append("")
    if assessment['critical_violations']:
        lines.append("Critical violations:")
        for v in assessment['critical_violations']:
            lines.append(f"  [{v.principle_id}] {v.evidence[:80]}...")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_principles_by_category())
    print()
    print(render_compliance_assessment(
        assess_system_compliance(
            "GAAP/IFRS",
            CURRENT_FINANCIAL_ACCOUNTING_ASSESSMENT,
        )
    ))
    print()
    print(f"=== falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
