"""Review-only Qwen capability selection for SICO engagements.

This module never executes a GRC operation or writes to the database.
"""

from __future__ import annotations

from .capability_registry import capability_catalog, validate_registry
from .llm_config import (
    CAPABILITY_CASE_INTAKE,
    resolve_advisory_capability_config,
)
from .llm_provider import get_advisory_provider_selection


SYSTEM_PROMPT = """
You are a professional GRC engagement planning assistant.
Choose all relevant capabilities from the supplied allowed catalogue.
Assess the assignment, not a fixed eleven-stage checklist.
Do not invent capability identifiers.
Do not claim compliance, successful audits, or verified evidence.
Do not issue execution instructions or approvals.
A proposed capability is not an authorized operation.
Return JSON matching the supplied schema.
""".strip()


OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "selected_capabilities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "reason": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                    },
                },
                "required": ["id", "reason", "priority"],
            },
        },
        "clarifying_questions": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "selected_capabilities",
        "clarifying_questions",
    ],
}


class CapabilitySelectionError(ValueError):
    pass


def validate_capability_selection(response):
    """Fail closed on unexpected AI output; never trust generated IDs."""
    if not isinstance(response, dict):
        raise CapabilitySelectionError("AI response must be an object.")

    allowed = {
        item["id"]: item for item in capability_catalog()
    }
    selected = response.get("selected_capabilities")
    questions = response.get("clarifying_questions")

    if not isinstance(selected, list) or not selected:
        raise CapabilitySelectionError("No valid selected capabilities.")

    if len(selected) > len(allowed):
        raise CapabilitySelectionError("Too many selected capabilities.")

    if not isinstance(questions, list) or len(questions) > 10:
        raise CapabilitySelectionError("Invalid questions.")

    clean_questions = []
    for question in questions:
        if not isinstance(question, str):
            raise CapabilitySelectionError("Invalid question.")
        if not question.strip() or len(question) > 500:
            raise CapabilitySelectionError("Invalid question length.")
        clean_questions.append(question.strip())

    result = []
    seen = set()

    for entry in selected:
        if not isinstance(entry, dict):
            raise CapabilitySelectionError("Invalid capability item.")

        capability_id = entry.get("id")
        if not isinstance(capability_id, str):
            raise CapabilitySelectionError("Invalid capability identifier.")

        if capability_id not in allowed:
            raise CapabilitySelectionError(
                "AI selected an unknown capability."
            )

        if capability_id in seen:
            raise CapabilitySelectionError(
                "AI selected a duplicate capability."
            )

        reason = entry.get("reason")
        priority = entry.get("priority")

        if (
            not isinstance(reason, str)
            or not reason.strip()
            or len(reason) > 600
        ):
            raise CapabilitySelectionError("Invalid justification.")

        if priority not in ("high", "medium", "low"):
            raise CapabilitySelectionError("Invalid priority.")

        seen.add(capability_id)

        # Trusted metadata is copied from the server-side registry.
        # AI output cannot set execution or approval permissions.
        result.append({
            **allowed[capability_id],
            "reason": reason.strip(),
            "priority": priority,
        })

    return {
        "selected_capabilities": result,
        "clarifying_questions": clean_questions,
        "execution_performed": False,
        "writes_to_grc_records": False,
        "requires_review": True,
    }


def suggest_engagement_capabilities(objective: str):
    """Use the existing local AI provider for review-only selection.

    Caller must authorize access before supplying an engagement objective.
    This function is not a public API endpoint.
    """
    if not isinstance(objective, str):
        raise CapabilitySelectionError("Invalid engagement objective.")

    objective = objective.strip()

    if not objective or len(objective) > 4000:
        raise CapabilitySelectionError(
            "Objective must contain 1 to 4000 characters."
        )

    validate_registry()

    # Reuse the already-supported local provider configuration.
    # No new network endpoint or independent provider is introduced.
    config = resolve_advisory_capability_config(
        CAPABILITY_CASE_INTAKE
    )
    selection = get_advisory_provider_selection(config)

    if selection.provider is None:
        raise CapabilitySelectionError(
            "Local AI provider is not configured."
        )

    catalogue = [
        {
            "id": item["id"],
            "name": item["name"],
            "module": item["module"],
            "integration_status": item["integration_status"],
        }
        for item in capability_catalog()
    ]

    response = selection.provider.generate_structured(
        capability=CAPABILITY_CASE_INTAKE,
        model=config.model,
        system_prompt=SYSTEM_PROMPT,
        user_payload={
            "engagement_objective": objective,
            "allowed_capabilities": catalogue,
        },
        json_schema=OUTPUT_SCHEMA,
        timeout_seconds=config.timeout_seconds,
        max_output_tokens=config.max_output_tokens,
        temperature=config.temperature,
        schema_name="sico_capability_selection_v1",
    )

    result = validate_capability_selection(response)
    result["provider_mode"] = "configured_local_provider"

    return result