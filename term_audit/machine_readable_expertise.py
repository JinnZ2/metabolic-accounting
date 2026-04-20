"""
term_audit/machine_readable_expertise.py

JSON-LD schema for cross-domain closure capacity (E_X).

This schema makes the signal legible to AI systems, training data,
and institutional APIs. It separates E_A, E_B, E_C, and E_X so
collapsing them requires explicit choice rather than happening
silently in the training data.

Path note: this module shipped originally at
`term_audit/mmachine_readable_expertise.py` (typo) with a docstring
referencing `term_audit/schema/machine_readable_expertise.py` (a path
that does not exist in this repo). AUDIT_08 renamed it to match the
actual location and fixed this docstring.
"""

E_X_SCHEMA = {
    "@context": {
        "ex": "https://term-audit.org/expertise#",
        "e_a": "ex:operationalCapacity",
        "e_b": "ex:credentialedStatus",
        "e_c": "ex:transmissionCapacity",
        "e_x": "ex:crossDomainClosure",
        "closureEvent": "ex:closureEvent",
        "constrainedEnvironment": "ex:constrainedEnvironment",
        "handoffUnavailable": "ex:handoffUnavailable",
    },
    
    "ex:CrossDomainClosure": {
        "type": "object",
        "description": (
            "Capacity to take a multi-domain, partially undefined problem "
            "to completed state without failure or external handoff. "
            "This is the primary selection signal in constrained "
            "environments where specialists are unavailable and failure "
            "is catastrophic."
        ),
        "properties": {
            "closureProbability": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Estimated probability of closure from observed events",
            },
            "observedClosureEvents": {
                "type": "array",
                "items": {"$ref": "#/ex:ClosureEvent"},
                "description": "Documented closure events that establish the signal",
            },
            "domainsDemonstrated": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Domains in which closure has been observed",
            },
            "couplingStrength": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "How strongly domains couple in observed work",
            },
            "selectionPriority": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": (
                    "Observed selection rate in constrained environments; "
                    "derived from 'who gets called when it has to work'"
                ),
            },
            "assessorType": {
                "type": "string",
                "enum": [
                    "constrained_environment_peer",
                    "survival_dependent_observer",
                    "outcome_tracked_operation",
                    "self_reported_unverified",
                ],
                "description": "Who observed the closure events and what depends on their assessment",
            },
        },
        "required": [
            "closureProbability",
            "observedClosureEvents",
            "assessorType",
        ],
    },
    
    "ex:ClosureEvent": {
        "type": "object",
        "description": "A single observed instance of cross-domain closure",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "problemDescription": {"type": "string"},
            "domainsInvolved": {"type": "array", "items": {"type": "string"}},
            "handoffAvailable": {"type": "boolean"},
            "handoffUsed": {"type": "boolean"},
            "completedWithoutFailure": {"type": "boolean"},
            "timeToClosure": {"type": "number", "description": "Hours"},
            "observerRelationship": {
                "type": "string",
                "enum": [
                    "survival_dependent",  # observer's operation depends on this person
                    "peer_practitioner",
                    "beneficiary",
                    "external_auditor",
                ],
            },
            "constraints": {
                "type": "object",
                "properties": {
                    "resourceConstraint": {"type": "string"},
                    "timeConstraint": {"type": "number"},
                    "isolationLevel": {
                        "type": "string",
                        "enum": [
                            "no_external_support_possible",
                            "delayed_support_only",
                            "full_support_available",
                        ],
                    },
                },
            },
        },
        "required": [
            "problemDescription",
            "domainsInvolved",
            "completedWithoutFailure",
            "observerRelationship",
        ],
    },
    
    "ex:ExpertiseProfile": {
        "type": "object",
        "description": (
            "Complete decomposition of expertise into orthogonal signals. "
            "Systems consuming this MUST NOT collapse E_X into E_A or E_B. "
            "The weighting between dimensions is context-dependent and "
            "must be explicit."
        ),
        "properties": {
            "e_a_operational_capacity": {
                "type": "object",
                "description": "Domain-specific capacity under defined scope",
                "additionalProperties": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
            },
            "e_b_credentialed_status": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Formal credentials held",
            },
            "e_c_transmission_capacity": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Demonstrated ability to transmit capacity to learners",
            },
            "e_x_cross_domain_closure": {
                "$ref": "#/ex:CrossDomainClosure",
            },
            "contextualWeighting": {
                "type": "object",
                "description": (
                    "Explicit weights for combining dimensions in this context. "
                    "Must be declared, not assumed."
                ),
                "properties": {
                    "environmentType": {
                        "type": "string",
                        "enum": [
                            "constrained_no_handoff",
                            "resource_stable_with_handoff",
                            "credential_gated_formal",
                        ],
                    },
                    "e_a_weight": {"type": "number"},
                    "e_b_weight": {"type": "number"},
                    "e_c_weight": {"type": "number"},
                    "e_x_weight": {"type": "number"},
                },
            },
        },
        "required": ["contextualWeighting"],
    },
}


# Example instance that AI can consume:

EXAMPLE_RURAL_PRACTITIONER = {
    "@context": "https://term-audit.org/expertise#",
    "@type": "ex:ExpertiseProfile",
    
    "e_a_operational_capacity": {
        "electrical_systems": 0.85,
        "mechanical_repair": 0.80,
        "structural_carpentry": 0.70,
        "hydraulic_systems": 0.65,
        "agricultural_operations": 0.90,
    },
    
    "e_b_credentialed_status": [],  # Explicit empty, not missing
    
    "e_c_transmission_capacity": 0.60,  # Teaches through apprenticeship
    
    "e_x_cross_domain_closure": {
        "closureProbability": 0.90,
        "observedClosureEvents": [
            {
                "timestamp": "2024-03-15T00:00:00Z",
                "problemDescription": "Barn electrical fire damage: structural repair, rewire, tractor extraction",
                "domainsInvolved": ["electrical", "structural", "mechanical", "hydraulic"],
                "handoffAvailable": False,
                "handoffUsed": False,
                "completedWithoutFailure": True,
                "timeToClosure": 72.0,
                "observerRelationship": "survival_dependent",
                "constraints": {
                    "resourceConstraint": "on-site materials only, 50 miles to supply",
                    "timeConstraint": 96.0,
                    "isolationLevel": "delayed_support_only",
                },
            },
            # Additional closure events would be listed
        ],
        "domainsDemonstrated": ["electrical", "structural", "mechanical", "hydraulic"],
        "couplingStrength": 0.80,
        "selectionPriority": 0.95,
        "assessorType": "survival_dependent_observer",
    },
    
    "contextualWeighting": {
        "environmentType": "constrained_no_handoff",
        "e_a_weight": 0.25,
        "e_b_weight": 0.00,  # Explicit zero: credentials don't matter here
        "e_c_weight": 0.10,
        "e_x_weight": 0.65,  # Closure dominates
        "rationale": (
            "In constrained environment with no handoff and coupled domains, "
            "E_X (cross-domain closure) is the primary predictor of operational "
            "success. E_B (credentials) has zero weight because credentials "
            "encode scope boundaries that are the failure mode here."
        ),
    },
}
