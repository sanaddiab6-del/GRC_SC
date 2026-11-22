"""SICO AI capability inventory.

This is a catalogue, not an execution router.
Unconnected modules must never be invoked through this registry.
"""

from __future__ import annotations

from .engagement_rules import STAGES


# These are already represented in the existing engagement dispatcher.
EXISTING_STAGES = {
    "case_setup": ("Case setup", "core"),
    "assets": ("Asset management", "core"),
    "applied_controls": ("Applied controls", "core"),
    "evidence_findings": ("Evidence and findings", "core"),
    "remediation": ("Remediation actions", "core"),
    "framework_control_mappings": ("Framework mappings", "core"),
    "risk_scenarios": ("Risk scenarios", "core"),
    "control_effectiveness": ("Control effectiveness", "core"),
    "audit_readiness": ("Audit readiness", "core"),
    "audit_report": ("Audit reporting", "core"),
    "final_review": ("Final review", "core"),
}

# Modules/workstreams requiring additional reviewed AI integration.
# Listing a capability does not mean AI is authorized to execute it.
ADDITIONAL_CAPABILITIES = {
    "governance_policies": ("Governance and policy lifecycle", "core"),
    "requirement_assessment": ("Detailed compliance assessment", "core"),
    "third_party_risk": ("Third-party risk management", "tprm"),
    "privacy": ("Privacy and data protection", "privacy"),
    "resilience": ("Resilience and continuity", "resilience"),
    "ebios_risk": ("EBIOS risk methodology", "ebios_rm"),
    "quantitative_risk": ("Quantitative cyber risk", "crq"),
    "project_management": ("Project management", "pmbok"),
    "calibration": ("CAL capabilities", "cal"),
    "measurement": ("Measurement and metrology", "metrology"),
    "integrations": ("External integrations", "integrations"),
    "data_import": ("Data import and preparation", "data_wizard"),
    "incident_governance": ("Incident readiness and governance", "core"),
    "formal_exports": ("Formal GRC reports and exports", "core"),
}


def capability_catalog():
    """Return an independent JSON-safe capability inventory."""
    result = []

    for stage, (name, module) in EXISTING_STAGES.items():
        result.append({
            "id": stage,
            "name": name,
            "module": module,
            "integration_status": "existing_engagement_stage",
            "engagement_stage": stage,
            "execution_available_from_registry": False,
            "human_approval_required_for_writes": True,
        })

    for capability_id, (name, module) in ADDITIONAL_CAPABILITIES.items():
        result.append({
            "id": capability_id,
            "name": name,
            "module": module,
            "integration_status": "requires_reviewed_integration",
            "engagement_stage": None,
            "execution_available_from_registry": False,
            "human_approval_required_for_writes": True,
        })

    return result


def capability_by_id(capability_id: str):
    """Look up a declared capability; never dynamically import code."""
    if not isinstance(capability_id, str):
        raise KeyError("Unknown SICO capability")

    for item in capability_catalog():
        if item["id"] == capability_id:
            return item

    raise KeyError("Unknown SICO capability")


def validate_registry():
    """Verify that the catalogue matches the existing stage contract."""
    stage_ids = {step.slug for step in STAGES}
    declared = set(EXISTING_STAGES)

    if stage_ids != declared:
        raise ValueError(
            "Capability registry and engagement stages are out of sync"
        )

    identifiers = [item["id"] for item in capability_catalog()]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Duplicate SICO capability identifiers")

    return True