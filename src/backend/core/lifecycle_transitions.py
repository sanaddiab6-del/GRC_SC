# Strict lifecycle transition maps for GRC entities

# Controls: draft → review → approved → archived
CONTROL_TRANSITIONS = {
    "draft": ["review"],
    "review": ["approved"],
    "approved": ["archived"],
    "archived": []
}

# Evidence: uploaded → under_review → approved/rejected
EVIDENCE_TRANSITIONS = {
    "uploaded": ["under_review"],
    "under_review": ["approved", "rejected"],
    "approved": [],
    "rejected": []
}

# Risks: open → assessed → mitigating → resolved → closed
RISK_TRANSITIONS = {
    "open": ["assessed"],
    "assessed": ["mitigating"],
    "mitigating": ["resolved"],
    "resolved": ["closed"],
    "closed": []
}

# Findings: open → in_progress → remediated → verified → closed
FINDING_TRANSITIONS = {
    "open": ["in_progress"],
    "in_progress": ["remediated"],
    "remediated": ["verified"],
    "verified": ["closed"],
    "closed": []
}

# Incidents: open → investigating → contained → resolved → closed
INCIDENT_TRANSITIONS = {
    "open": ["investigating"],
    "investigating": ["contained"],
    "contained": ["resolved"],
    "resolved": ["closed"],
    "closed": []
}

# Helper to check if a transition is allowed
def is_transition_allowed(entity_type: str, current: str, target: str) -> bool:
    transitions = {
        "control": CONTROL_TRANSITIONS,
        "evidence": EVIDENCE_TRANSITIONS,
        "risk": RISK_TRANSITIONS,
        "finding": FINDING_TRANSITIONS,
        "incident": INCIDENT_TRANSITIONS,
    }
    entity_map = transitions.get(entity_type)
    if not entity_map:
        return False
    return target in entity_map.get(current, [])
