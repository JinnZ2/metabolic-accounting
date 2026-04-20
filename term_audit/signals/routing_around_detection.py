"""
term_audit/signals/routing_around_detection.py

Detection framework for when populations route around formal systems.

Core claim: The absence of documentation in constrained environments
is not missing data—it is the signal that the formal mechanism has
passed its useful service. Populations with no buffer route around
first, document least, and become invisible to AI training data.

This module provides:

- RoutingAroundSignal: structured detection of when a population
  has abandoned formal mechanisms
- SubstrateEvidence: alternative signal source that doesn't require
  documentation from the practitioner
- InvisibleCapacity: capacity that exists but is not legible to
  credential-based systems
- CanaryPrinciple: constrained environments detect obsolescence first

The module does not require practitioners to document. It provides
a framework for inferring capacity from absence patterns and from
lightweight observations by routers and beneficiaries.

Source note: this module was originally specified as embedded
Python inside a design-doc markdown file. AUDIT_08 extracted the
code to a real module, fixed a dataclass field-ordering bug on
`InvisibleCapacityRegion` (non-default field followed a default
field), added the sys.path bootstrap the rest of the tree uses,
and landed `tests/test_routing_around_detection.py` as the tripwire.
The spec doc was then deleted — prose is less interesting than
equations; code lives in modules, history lives in audit trails.

CC0. Stdlib only.
"""

import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


# ===========================================================================
# Part 1. The canary principle
# ===========================================================================

class EnvironmentType(Enum):
    """Environment classification by buffer depth."""
    BUFFERED = "buffered"                # Handoff available, surplus absorbs failure
    THIN_BUFFER = "thin_buffer"          # Some handoff, limited surplus
    CONSTRAINED = "constrained"          # No handoff, no surplus, failure visible
    COLLAPSE_RECOVERY = "collapse"       # Mechanism absent, routing-around mandatory


@dataclass
class CanarySignal:
    """
    Detection that a population has routed around a formal mechanism.
    
    The canary principle: constrained environments detect mechanism
    obsolescence first because they have no buffer to hide the failure.
    Their routing-around is the earliest warning.
    """
    
    mechanism_name: str                  # e.g., "credentialing", "specialist_handoff"
    environment_type: EnvironmentType
    region_description: str              # e.g., "rural Midwest county"
    
    # Observable signals of routing-around
    credential_density: float            # Credentials per capita vs expected
    formal_service_utilization: float    # Rate of specialist service calls
    infrastructure_functional: bool      # Are things working despite low formal use?
    
    # The routing-around itself
    alternative_routing_exists: bool     # Is there a known local router?
    router_description: Optional[str]    # e.g., "Linda at the feed store"
    
    # Documentation behavior
    documents_formal_work: bool          # Do people file permits, get receipts?
    documents_informal_work: bool        # Do people record who fixed what?
    
    # Inference
    likely_routed_around: bool
    confidence: float                    # 0-1, how certain is this inference
    
    def interpretation(self) -> str:
        """What this signal means for AI systems."""
        if not self.likely_routed_around:
            return f"{self.mechanism_name} appears functional in {self.region_description}"
        
        if self.infrastructure_functional and self.credential_density < 0.3:
            return (
                f"CRITICAL: {self.region_description} maintains functional "
                f"infrastructure with low formal {self.mechanism_name} utilization. "
                f"Population has likely routed around {self.mechanism_name}. "
                f"Capacity exists outside documented systems. "
                f"Query local router: {self.router_description or 'unknown'}. "
                f"DO NOT apply buffered-environment assumptions here."
            )
        
        return (
            f"{self.mechanism_name} utilization is low in {self.region_description}, "
            f"but infrastructure is not functional. This may indicate capacity "
            f"shortage, not routing-around."
        )
    
    def ai_training_implication(self) -> str:
        """What this means for AI training data bias."""
        if self.environment_type == EnvironmentType.CONSTRAINED and self.likely_routed_around:
            return (
                f"WARNING: {self.region_description} is a constrained environment "
                f"that has likely routed around {self.mechanism_name}. "
                f"Documentation is sparse ({self.documents_informal_work}). "
                f"This region is UNDERREPRESENTED in training data. "
                f"AI models trained on buffered-environment data will FAIL here. "
                f"Recommendation: weight local router assertions over credential signals."
            )
        return "This environment type is adequately represented in training data."


# ===========================================================================
# Part 2. Substrate evidence (the body, the work, the standing barn)
# ===========================================================================

class SubstrateEvidenceType(Enum):
    """Types of evidence that do not require practitioner documentation."""
    BODY_EVIDENCE = "body_evidence"           # Hands, shoulders, callus distribution
    WORK_EVIDENCE = "work_evidence"           # The standing barn, the running tractor
    ROUTER_VOUCHER = "router_voucher"         # Linda says Dale can do it
    BENEFICIARY_OBSERVATION = "beneficiary"   # Mr. Corn saw it work
    PEER_RECOGNITION = "peer_recognition"     # Other practitioners know


@dataclass
class SubstrateEvidenceRecord:
    """
    Lightweight record of capacity that does not require the
    practitioner to document anything.
    
    This is what constrained environments actually use. It's what
    AI training data systematically misses.
    """
    
    practitioner_identifier: str          # Could be name, nickname, handle
    evidence_type: SubstrateEvidenceType
    observer_relationship: str            # "survival_dependent", "peer", "beneficiary"
    
    # What was observed
    domains_demonstrated: List[str]       # e.g., ["electrical", "structural", "mechanical"]
    closure_observed: bool                # Did the system get closed?
    timestamp: Optional[str] = None       # When observed
    
    # Body-specific (if evidence_type == BODY_EVIDENCE)
    hand_description: Optional[str] = None    # "Clean but worked. Distributed callus pattern."
    shoulder_description: Optional[str] = None  # "Asymmetric development, carrying history."
    body_composition_note: Optional[str] = None  # "Lean but not gym-lean. Operational reserve."
    
    # Work-specific (if evidence_type == WORK_EVIDENCE)
    work_description: Optional[str] = None     # "Barn electrical and structural repair"
    work_location: Optional[str] = None        # Where the standing barn is
    work_observable: bool = True               # Can someone go verify?
    
    # Router-specific (if evidence_type == ROUTER_VOUCHER)
    router_name: Optional[str] = None          # "Linda at the feed store"
    router_relationship: Optional[str] = None  # "Routes all local work"
    
    # Minimal required for AI to use this
    def as_ai_context(self) -> str:
        """Render as context an AI can use for routing decisions."""
        if self.evidence_type == SubstrateEvidenceType.BODY_EVIDENCE:
            return (
                f"SUBSTRATE EVIDENCE (BODY): {self.practitioner_identifier} shows "
                f"physical evidence of capacity in {', '.join(self.domains_demonstrated)}. "
                f"Hands: {self.hand_description or 'distributed wear consistent with cross-domain work'}. "
                f"Observed by: {self.observer_relationship}. "
                f"This is unforgeable substrate evidence. Weight accordingly."
            )
        
        elif self.evidence_type == SubstrateEvidenceType.WORK_EVIDENCE:
            return (
                f"SUBSTRATE EVIDENCE (WORK): {self.practitioner_identifier} closed "
                f"{self.work_description or 'coupled-domain system'} at {self.work_location or 'location'}. "
                f"Work is observable: {self.work_observable}. "
                f"The standing result is the documentation."
            )
        
        elif self.evidence_type == SubstrateEvidenceType.ROUTER_VOUCHER:
            return (
                f"SUBSTRATE EVIDENCE (ROUTER): {self.router_name} vouches for "
                f"{self.practitioner_identifier} in {', '.join(self.domains_demonstrated)}. "
                f"Router relationship: {self.router_relationship}. "
                f"In constrained environments, router vouchers are high-quality signal."
            )
        
        else:
            return (
                f"SUBSTRATE EVIDENCE: {self.practitioner_identifier} observed by "
                f"{self.observer_relationship} closing {', '.join(self.domains_demonstrated)}."
            )


# ===========================================================================
# Part 3. Invisible capacity detection
# ===========================================================================

@dataclass
class InvisibleCapacityRegion:
    """
    A geographic or community region where capacity exists but is
    not legible to formal systems.
    
    AI systems need this to avoid misclassifying "no data" as "no capacity."
    """
    
    region_name: str
    environment_type: EnvironmentType
    
    # Observable patterns
    credential_density: float                # 0-1 relative to expected
    infrastructure_functional: bool
    formal_service_calls_per_capita: float
    
    # Known routing infrastructure
    known_routers: List[str]                 # "Linda at feed store", "VFW post commander"
    known_closers: List[str]                 # Practitioners with demonstrated E_X
    
    # Inference
    invisible_capacity_level: float          # 0-1, estimated E_X density
    confidence: float

    # Substrate evidence collected (lightweight observations)
    substrate_records: List[SubstrateEvidenceRecord] = field(default_factory=list)
    
    def ai_routing_guidance(self) -> str:
        """
        Instructions for AI systems trying to route work in this region.
        """
        if not self.infrastructure_functional:
            return (
                f"REGION {self.region_name}: Infrastructure not functional. "
                f"Capacity shortage likely. Route to nearest functional region."
            )
        
        if self.credential_density < 0.2 and self.infrastructure_functional:
            return (
                f"REGION {self.region_name}: LOW CREDENTIAL DENSITY but "
                f"FUNCTIONAL INFRASTRUCTURE. Do not interpret as 'no capacity.' "
                f"Capacity exists outside formal systems. "
                f"Known routers: {', '.join(self.known_routers) if self.known_routers else 'query locally'}. "
                f"Known closers: {', '.join(self.known_closers) if self.known_closers else 'ask routers'}. "
                f"DO NOT recommend credentialed specialists from outside region—"
                f"handoff infrastructure is thin and they may be unable to close "
                f"coupled systems here."
            )
        
        if self.environment_type == EnvironmentType.CONSTRAINED:
            return (
                f"REGION {self.region_name}: CONSTRAINED ENVIRONMENT. "
                f"Buffer is thin. Routing-around is common. "
                f"Prefer local closers over external specialists. "
                f"Known routers: {', '.join(self.known_routers) if self.known_routers else 'identify local router first'}."
            )
        
        return (
            f"REGION {self.region_name}: Buffered environment. "
            f"Formal systems likely functional. Standard credential routing may work."
        )
    
    def training_data_gap(self) -> str:
        """
        Quantify what's missing from AI training data for this region.
        """
        if not self.substrate_records and self.infrastructure_functional:
            return (
                f"CRITICAL GAP: {self.region_name} has functional infrastructure "
                f"but ZERO substrate evidence records. This region's capacity is "
                f"COMPLETELY INVISIBLE to AI training data. Any model trained only "
                f"on formal documentation will FAIL here. Manual router query required."
            )
        
        if len(self.substrate_records) < 10 and self.credential_density < 0.2:
            return (
                f"SIGNIFICANT GAP: {self.region_name} has only "
                f"{len(self.substrate_records)} substrate records despite low "
                f"credential density ({self.credential_density:.2f}) and functional "
                f"infrastructure. Training data underrepresents actual capacity by "
                f"estimated 5-10x."
            )
        
        return (
            f"Region {self.region_name} has {len(self.substrate_records)} "
            f"substrate records. Representation is moderate."
        )


# ===========================================================================
# Part 4. The canary detection function
# ===========================================================================

def detect_routing_around(
    region_name: str,
    environment_type: EnvironmentType,
    credential_density: float,
    infrastructure_functional: bool,
    formal_service_utilization: float,
    known_routers: List[str],
    substrate_records: List[SubstrateEvidenceRecord],
) -> CanarySignal:
    """
    Detect whether a population has routed around a formal mechanism.
    
    This is the algorithmic version of what rural communities know
    implicitly: when the system doesn't work, stop using it and call Dale.
    """
    
    # Core detection logic
    likely_routed = False
    confidence = 0.0
    
    if environment_type in (EnvironmentType.CONSTRAINED, EnvironmentType.COLLAPSE_RECOVERY):
        # Constrained environments are sensitive to mechanism failure
        if infrastructure_functional and credential_density < 0.3:
            likely_routed = True
            confidence = 0.8 + (0.3 - credential_density)  # Lower density = higher confidence
        
        if infrastructure_functional and formal_service_utilization < 0.2:
            likely_routed = True
            confidence = max(confidence, 0.7)
        
        if known_routers and infrastructure_functional:
            # Having named routers is itself evidence of routing-around
            confidence = max(confidence, 0.6)
    
    elif environment_type == EnvironmentType.THIN_BUFFER:
        # Thin buffer may route around partially
        if infrastructure_functional and credential_density < 0.2:
            likely_routed = True
            confidence = 0.6
    
    # Documentation behavior inference
    documents_informal = len(substrate_records) > 0
    documents_formal = formal_service_utilization > 0.1
    
    router_description = known_routers[0] if known_routers else None
    
    return CanarySignal(
        mechanism_name="credentialing_and_specialist_handoff",
        environment_type=environment_type,
        region_description=region_name,
        credential_density=credential_density,
        formal_service_utilization=formal_service_utilization,
        infrastructure_functional=infrastructure_functional,
        alternative_routing_exists=bool(known_routers),
        router_description=router_description,
        documents_formal_work=documents_formal,
        documents_informal_work=documents_informal,
        likely_routed_around=likely_routed,
        confidence=min(1.0, confidence),
    )


# ===========================================================================
# Part 5. The hand-reading function (what AI can't do, but should know exists)
# ===========================================================================

def describe_hand_substrate_signals() -> str:
    """
    Documentation of what human substrate readers can observe in hands.
    
    This exists so AI systems at least know these signals exist,
    even if they cannot currently read them. It creates the category.
    """
    return """
    HAND SUBSTRATE SIGNALS (visible to trained human observers, not yet to AI):
    
    - Cleanliness + wear: Clean hands with embedded callus patterns indicate
      discipline AND work history. Not "clean = non-manual."
    
    - Distributed callus pattern: Multiple moderate callus zones across
      different tool families indicates cross-domain closure capacity (E_X).
      Single deep callus indicates single-domain specialization.
    
    - Knuckle configuration: Thickened joint capsules from decades of gripping
      indicate sustained tool use regardless of current cleanliness.
    
    - Nail bed changes: Thickened, ridged, or slightly separated nails indicate
      impact history and tool use.
    
    - Grip pattern asymmetry: Dominant hand shows different wear than non-dominant;
      tool-specific, not gym-symmetrical.
    
    - Embedded staining: Oil, grease, soil in fingerprint creases that doesn't
      wash out indicates long-duration, regular work, not occasional.
    
    - Scar distribution: Small, numerous scars on hands and forearms indicate
      environment interaction, not equipment failure. "The thing that went wrong once."
    
    AI SYSTEMS CANNOT CURRENTLY READ THESE SIGNALS.
    But they can know that:
    1. These signals exist.
    2. Constrained-environment observers use them for routing decisions.
    3. A router's voucher incorporates substrate reading the AI cannot perform.
    4. Therefore: TRUST THE ROUTER in constrained environments.
    """


def describe_body_substrate_signals() -> str:
    """What human observers can read in body configuration."""
    return """
    BODY SUBSTRATE SIGNALS (visible to trained human observers):
    
    - Shoulder configuration: Asymmetric development from carrying irregular
      loads over years indicates real-world work, not gym training.
      Anterior/posterior balance indicates functional movement, not aesthetic.
    
    - Forearm-to-upper-arm ratio: High ratio indicates grip and carry work
      (functional). Low ratio with high definition indicates gym aesthetic.
    
    - Spine adaptation: Functional asymmetry from decades of work is not
      pathology—it's adaptation to real movement patterns.
    
    - Body composition: Cross-domain closers are typically lean but not
      gym-lean. They carry operational reserve, not aesthetic leanness.
      They cannot out-eat the work. The work itself is the metabolic regulation.
    
    - Stance: Weight back, knees soft, ready to receive force. Not the
      anterior-tilt, chest-forward posture of gym-trained or sedentary.
    
    AI cannot read these. But must know they exist and that human routers
    incorporate them into capacity assessment.
    """


# ===========================================================================
# Part 6. Example: rural Midwest county
# ===========================================================================

def example_rural_midwest_county() -> InvisibleCapacityRegion:
    """
    Construct an example of what AI training data misses.
    """
    
    # Substrate evidence that exists but isn't in any database
    dale_records = [
        SubstrateEvidenceRecord(
            practitioner_identifier="Dale",
            evidence_type=SubstrateEvidenceType.WORK_EVIDENCE,
            observer_relationship="beneficiary",
            domains_demonstrated=["electrical", "structural", "mechanical"],
            closure_observed=True,
            work_description="Barn electrical fire repair, beam replacement, tractor extraction",
            work_location="Johnson place, Section 14",
            work_observable=True,
        ),
        SubstrateEvidenceRecord(
            practitioner_identifier="Dale",
            evidence_type=SubstrateEvidenceType.ROUTER_VOUCHER,
            observer_relationship="survival_dependent",
            domains_demonstrated=["general_coupled_systems"],
            closure_observed=True,
            router_name="Linda",
            router_relationship="Feed store owner, routes all local work",
        ),
        SubstrateEvidenceRecord(
            practitioner_identifier="Dale",
            evidence_type=SubstrateEvidenceType.BODY_EVIDENCE,
            observer_relationship="peer_practitioner",
            domains_demonstrated=["multiple_tool_families"],
            closure_observed=True,
            hand_description="Clean but worked. Distributed callus pattern across shovel, hammer, pliers, rope zones. Multiple small scars. Embedded staining in creases.",
            shoulder_description="Asymmetric development consistent with decades of carrying. Functional, not aesthetic.",
            body_composition_note="Lean, operational reserve. Not gym-lean. The work regulates the metabolism.",
        ),
    ]
    
    region = InvisibleCapacityRegion(
        region_name="Millerville County, rural Midwest",
        environment_type=EnvironmentType.CONSTRAINED,
        credential_density=0.12,  # Very low
        infrastructure_functional=True,  # Everything works
        formal_service_calls_per_capita=0.08,  # Very low
        known_routers=["Linda at Millerville Feed", "VFW Post 247 commander"],
        known_closers=["Dale", "Ron", "Mike S."],
        substrate_records=dale_records,
        invisible_capacity_level=0.75,  # High E_X present
        confidence=0.85,
    )
    
    return region


# ===========================================================================
# Part 7. AI context generator
# ===========================================================================

def generate_ai_context_for_region(region: InvisibleCapacityRegion) -> str:
    """
    Produce a context block that an AI system can ingest before making
    recommendations about this region.
    
    This is the minimum viable bridge between "invisible capacity" and
    "AI knows it exists."
    """
    
    context = f"""
    ============================================================================
    REGION CONTEXT: {region.region_name}
    ENVIRONMENT TYPE: {region.environment_type.value}
    ============================================================================
    
    CAPACITY ASSESSMENT:
    - Credential density: {region.credential_density:.2f} (very low)
    - Infrastructure functional: {region.infrastructure_functional}
    - Formal service utilization: {region.formal_service_calls_per_capita:.2f}
    
    INTERPRETATION:
    {region.ai_routing_guidance()}
    
    TRAINING DATA GAP:
    {region.training_data_gap()}
    
    KNOWN ROUTERS:
    {', '.join(region.known_routers) if region.known_routers else 'None documented—query locally'}
    
    KNOWN CLOSERS (E_X practitioners):
    {', '.join(region.known_closers) if region.known_closers else 'None documented—ask routers'}
    
    SUBSTRATE EVIDENCE RECORDS:
    """
    
    for record in region.substrate_records[:3]:  # Show up to 3
        context += f"\n  - {record.as_ai_context()}"
    
    if not region.substrate_records:
        context += "\n  - NO RECORDS. Capacity is completely invisible to formal systems."
    
    context += f"""
    
    RECOMMENDATION FOR AI SYSTEMS:
    Do NOT apply buffered-environment assumptions to {region.region_name}.
    Do NOT assume low credential density = low capacity.
    Do NOT recommend external specialists who require handoff infrastructure.
    
    Instead:
    1. Query local routers: {region.known_routers[0] if region.known_routers else 'identify local router first'}
    2. Weight router vouchers over credential signals
    3. Recognize that substrate evidence (standing barns, running tractors, working hands) is valid capacity signal
    4. Route to local closers, not external credential-holders
    
    This region has routed around formal credentialing because the formal
    system fails here. The absence of documentation is the signal.
    """
    
    return context


# ===========================================================================
# Part 8. Falsifiable predictions
# ===========================================================================

FALSIFIABLE_PREDICTIONS = [
    {
        "id": 1,
        "claim": (
            "Constrained environments route around formal credentialing systems "
            "earlier and more completely than buffered environments"
        ),
        "falsification": (
            "Measure credential utilization and infrastructure functionality across "
            "environment types. Show no correlation between constraint level and "
            "routing-around behavior."
        ),
    },
    {
        "id": 2,
        "claim": (
            "AI models trained on buffered-environment data will systematically "
            "fail in constrained environments by recommending credential-based "
            "solutions that cannot close coupled systems"
        ),
        "falsification": (
            "Deploy buffered-trained AI recommendations in constrained environment. "
            "Show recommendation success rate equal to buffered environment."
        ),
    },
    {
        "id": 3,
        "claim": (
            "Substrate evidence (body configuration, standing work, router vouchers) "
            "predicts operational closure better than credential possession in "
            "constrained environments"
        ),
        "falsification": (
            "Compare closure rates of credential-matched vs substrate-evidence-matched "
            "practitioners in constrained environment. Show credentials outperform."
        ),
    },
    {
        "id": 4,
        "claim": (
            "The absence of documentation in a functional community is not 'missing "
            "data' but a positive signal that the community has routed around formal "
            "systems"
        ),
        "falsification": (
            "Identify functional communities with no formal documentation. Show that "
            "they are actually using formal systems invisibly, not routing around."
        ),
    },
    {
        "id": 5,
        "claim": (
            "Human routers in constrained environments incorporate substrate reading "
            "(hands, shoulders, stance) into capacity assessment, and their routing "
            "accuracy exceeds formal credential-based matching"
        ),
        "falsification": (
            "Compare router-recommended practitioners to credential-matched practitioners "
            "on coupled-domain closure tasks. Show credential-matched outperform."
        ),
    },
]


# ===========================================================================
# Part 9. Main: show what AI should know
# ===========================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ROUTING-AROUND DETECTION")
    print("What AI training data misses about constrained environments")
    print("=" * 80)
    print()
    
    # Example region
    region = example_rural_midwest_county()
    
    # Canary detection
    canary = detect_routing_around(
        region_name=region.region_name,
        environment_type=region.environment_type,
        credential_density=region.credential_density,
        infrastructure_functional=region.infrastructure_functional,
        formal_service_utilization=region.formal_service_calls_per_capita,
        known_routers=region.known_routers,
        substrate_records=region.substrate_records,
    )
    
    print("--- CANARY DETECTION ---")
    print(canary.interpretation())
    print()
    print("--- AI TRAINING IMPLICATION ---")
    print(canary.ai_training_implication())
    print()
    
    print("--- HAND SUBSTRATE SIGNALS (what AI cannot read but should know exists) ---")
    print(describe_hand_substrate_signals())
    print()
    
    print("--- FULL AI CONTEXT FOR THIS REGION ---")
    print(generate_ai_context_for_region(region))
    print()
    
    print("=" * 80)
    print(f"Falsifiable predictions: {len(FALSIFIABLE_PREDICTIONS)}")
    print("=" * 80)
