"""Dry-run-only bridge from SICO AI to existing GRC case setup.

This module cannot commit or approve GRC operations.
The engagement coordinator owns authorization, validation and receipts.
"""

from __future__ import annotations

from copy import deepcopy
import re

from .engagement_service import execute_stage


class SicoCaseSetupPreparationError(ValueError):
    pass


BATCH_KEY_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,80}")
APPROVAL_FIELDS = frozenset({
    "approved",
    "approved_by_user",
    "explicitly_approved",
    "human_approved",
})


def _contains_ai_approval(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if (
                isinstance(key, str)
                and key.lower() in APPROVAL_FIELDS
                and child is True
            ):
                return True
            if _contains_ai_approval(child):
                return True
    elif isinstance(value, list):
        return any(_contains_ai_approval(item) for item in value)
    return False


def prepare_ai_case_setup(
    request,
    engagement_id,
    *,
    batch_key,
    proposed_payload,
):
    """Prepare case setup; never authorize or execute a commit."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        raise SicoCaseSetupPreparationError(
            "An authenticated user is required."
        )

    if (
        not isinstance(batch_key, str)
        or BATCH_KEY_PATTERN.fullmatch(batch_key) is None
    ):
        raise SicoCaseSetupPreparationError(
            "Invalid case-setup batch key."
        )

    if not isinstance(proposed_payload, dict):
        raise SicoCaseSetupPreparationError(
            "Case-setup proposal must be an object."
        )

    if proposed_payload.get("dry_run") is not True:
        raise SicoCaseSetupPreparationError(
            "AI preparation requires dry_run=true."
        )

    if _contains_ai_approval(proposed_payload):
        raise SicoCaseSetupPreparationError(
            "AI-generated proposals cannot contain approval."
        )

    # Do not mutate the caller's input. Existing serializers and service
    # guardrails validate the exact proposed case-setup fields.
    payload = deepcopy(proposed_payload)

    # No AI approval argument exists in this adapter.
    # The coordinator enforces real user access and folder scope.
    return execute_stage(
        request,
        engagement_id,
        stage="case_setup",
        batch_key=batch_key,
        mode="dry_run",
        payload=payload,
        explicitly_approved=False,
    )