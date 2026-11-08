"""Review-only Qwen capability selection for SICO engagements.

This module never executes a GRC operation or writes to the database.
"""

from __future__ import annotations

from .capability_registry import capability_catalog, validate_registry
from .llm_config import (
    CAPABILITY_GRC_CAPABILITY_SELECTION,
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

    if not isinstance(questions, list) or len(questions) > 50:
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


BATCH_SIZE = 5
BATCH_OUTPUT_TOKENS = 512
BATCH_TIMEOUT_SECONDS = 120


def suggest_engagement_capabilities(objective: str):
    """Select relevant capabilities in bounded, review-only batches.

    Every batch must succeed. No partial response is accepted as complete.
    """
    if not isinstance(objective, str):
        raise CapabilitySelectionError("Invalid engagement objective.")

    objective = objective.strip()
    if not objective or len(objective) > 4000:
        raise CapabilitySelectionError(
            "Objective must contain 1 to 4000 characters."
        )

    validate_registry()

    config = resolve_advisory_capability_config(
        CAPABILITY_GRC_CAPABILITY_SELECTION
    )
    selection = get_advisory_provider_selection(config)
    if selection.provider is None:
        raise CapabilitySelectionError(
            "Local AI provider is not configured."
        )

    catalogue = capability_catalog()
    batches = [
        catalogue[i:i + BATCH_SIZE]
        for i in range(0, len(catalogue), BATCH_SIZE)
    ]

    selected = []
    questions = []
    seen = set()

    for index, batch in enumerate(batches, start=1):
        permitted = {item["id"] for item in batch}

        response = selection.provider.generate_structured(
            capability=CAPABILITY_GRC_CAPABILITY_SELECTION,
            model=config.model,
            system_prompt=(
                SYSTEM_PROMPT
                + "\nThis is one portion of the full platform catalogue. "
                + "Evaluate every listed capability for applicability. "
                + "Select only relevant entries from THIS portion. "
                + "An empty selected_capabilities list is allowed. "
                + "Keep reasons short (maximum 100 characters). "
                + "Return at most two concise clarifying questions. "
                + "Do not infer that other platform capabilities are absent."
            ),
            user_payload={
                "engagement_objective": objective,
                "batch_number": index,
                "total_batches": len(batches),
                "allowed_capabilities": [
                    {
                        "id": item["id"],
                        "name": item["name"],
                    }
                    for item in batch
                ],
            },
            json_schema=OUTPUT_SCHEMA,
            timeout_seconds=min(
                config.timeout_seconds, BATCH_TIMEOUT_SECONDS
            ),
            max_output_tokens=min(
                config.max_output_tokens, BATCH_OUTPUT_TOKENS
            ),
            temperature=config.temperature,
            schema_name="sico_capability_batch_v1",
        )

        if not isinstance(response, dict):
            raise CapabilitySelectionError(
                "Invalid response from capability batch."
            )

        entries = response.get("selected_capabilities")
        batch_questions = response.get("clarifying_questions")

        if not isinstance(entries, list):
            raise CapabilitySelectionError(
                "Invalid selected capabilities in batch."
            )
        if not isinstance(batch_questions, list):
            raise CapabilitySelectionError(
                "Invalid clarifying questions in batch."
            )
        if len(entries) > len(batch) or len(batch_questions) > 2:
            raise CapabilitySelectionError(
                "AI batch exceeded its limits."
            )

        for entry in entries:
            if not isinstance(entry, dict):
                raise CapabilitySelectionError(
                    "Invalid capability selection item."
                )

            capability_id = entry.get("id")
            if not isinstance(capability_id, str):
                raise CapabilitySelectionError(
                    "Invalid capability identifier."
                )
            if capability_id not in permitted:
                raise CapabilitySelectionError(
                    "AI selected a capability outside its batch."
                )
            if capability_id in seen:
                raise CapabilitySelectionError(
                    "Duplicate AI capability selection."
                )

            seen.add(capability_id)
            selected.append(entry)

        for question in batch_questions:
            if not isinstance(question, str):
                raise CapabilitySelectionError(
                    "Invalid clarifying question."
                )
            if not question.strip() or len(question) > 500:
                raise CapabilitySelectionError(
                    "Invalid clarifying question length."
                )
            if question not in questions:
                questions.append(question)

    result = validate_capability_selection({
        "selected_capabilities": selected,
        "clarifying_questions": questions,
    })
    result["provider_mode"] = "configured_local_provider"
    result["batches_processed"] = len(batches)
    result["total_catalogued_capabilities"] = len(catalogue)
    return result