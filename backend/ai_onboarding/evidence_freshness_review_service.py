from __future__ import annotations

from typing import Any

from django.utils import timezone

from core.models import AppliedControl, Finding, RequirementAssessment

from .rbac_context import filter_visible
from .evidence_freshness_review_guardrails import (
    EvidenceFreshnessReviewValidationError,
    validate_provider_output_guardrails,
)
from .evidence_freshness_review_provider import (
    EvidenceFreshnessReviewProviderError,
    get_evidence_freshness_review_provider,
)
from .evidence_freshness_review_serializers import (
    ADVISORY_NOTICE,
    EvidenceFreshnessReviewResultSerializer,
    FRESHNESS_STATUS_INSUFFICIENT_CONTEXT,
    MAX_LINKED_ITEMS_PER_RELATION,
    MAX_TEXT_FIELD_LENGTH,
    ProviderFreshnessJudgementSerializer,
)


def _truncate(value: Any, *, max_length: int = MAX_TEXT_FIELD_LENGTH) -> str | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text if len(text) <= max_length else f"{text[: max_length - 1]}…"


def _visible(related_manager, model, user):
    """Linked objects of `model` the requesting user can actually view.

    Evidence is commonly linked to controls, requirement assessments, and findings that live
    in a different folder than the Evidence itself (a control shared across domains, a
    requirement assessment in a compliance-only folder, and so on). The user being authorized
    to view this Evidence does not by itself authorize them to see those linked objects' names,
    statuses, or observations, so every linked relation is intersected with the user's own
    RBAC-accessible object ids (the same engine BaseModelViewSet.get_queryset() uses for the
    Evidence itself) before anything is read into the prompt.
    """
    return filter_visible(related_manager, model, user)


def build_evidence_context(evidence, user) -> dict[str, Any]:
    """Build the AI-facing context for one Evidence, reading only what is already on the
    object and only the linked relations `user` is independently authorized to view.

    Nothing here is trusted from client input. Nothing outside this evidence's own linked
    objects is read, and nothing the requesting user cannot themselves view is read either, so
    context from another tenant/folder — whether the Evidence's own folder or a linked object's
    folder — cannot enter the prompt.
    """
    now = timezone.now()
    last_revision = evidence.last_revision

    age_days = (now.date() - evidence.created_at.date()).days if evidence.created_at else None
    is_expired = bool(evidence.expiry_date and evidence.expiry_date < now.date())

    revision_context = None
    if last_revision is not None:
        revision_age_days = (
            (now.date() - last_revision.created_at.date()).days
            if last_revision.created_at
            else None
        )
        attachment_name = last_revision.attachment.name if last_revision.attachment else None
        revision_context = {
            "version": last_revision.version,
            "has_attachment": bool(last_revision.attachment),
            "attachment_extension": (
                attachment_name.rsplit(".", 1)[-1].lower()
                if attachment_name and "." in attachment_name
                else None
            ),
            "has_link": bool(last_revision.link),
            "observation": _truncate(last_revision.observation),
            "revision_age_days": revision_age_days,
        }

    visible_applied_controls = _visible(evidence.applied_controls, AppliedControl, user)
    visible_requirement_assessments = _visible(
        evidence.requirement_assessments, RequirementAssessment, user
    ).select_related("requirement", "compliance_assessment", "compliance_assessment__framework")
    visible_findings = _visible(evidence.findings, Finding, user)

    applied_controls = list(visible_applied_controls[:MAX_LINKED_ITEMS_PER_RELATION])
    requirement_assessments = list(
        visible_requirement_assessments[:MAX_LINKED_ITEMS_PER_RELATION]
    )
    findings = list(visible_findings[:MAX_LINKED_ITEMS_PER_RELATION])

    return {
        "evidence": {
            "name": _truncate(evidence.name, max_length=200),
            "description": _truncate(evidence.description),
            "status": evidence.status,
            "status_display": evidence.get_status_display(),
            "age_days": age_days,
            "expiry_date": evidence.expiry_date.isoformat() if evidence.expiry_date else None,
            "is_past_expiry_date": is_expired,
        },
        "latest_revision": revision_context,
        "revision_count": evidence.revisions.count(),
        "linked_applied_controls": [
            {"name": _truncate(control.name, max_length=200), "detail": control.status or ""}
            for control in applied_controls
        ],
        "linked_requirement_assessments": [
            {
                "name": _truncate(
                    getattr(assessment.requirement, "name", None)
                    or getattr(assessment.requirement, "urn", "")
                    or "",
                    max_length=200,
                ),
                "detail": (
                    f"{assessment.get_result_display()} / {assessment.get_status_display()} "
                    f"({assessment.compliance_assessment.name})"
                ),
            }
            for assessment in requirement_assessments
        ],
        "linked_findings": [
            {"name": _truncate(finding.name, max_length=200), "detail": finding.status or ""}
            for finding in findings
        ],
        "counts": {
            # Counts of what `user` can see, not the true totals: a count of hidden linked
            # objects would itself disclose that they exist.
            "linked_applied_controls": visible_applied_controls.count(),
            "linked_requirement_assessments": visible_requirement_assessments.count(),
            "linked_findings": visible_findings.count(),
        },
    }


def _has_reviewable_context(evidence_context: dict[str, Any]) -> bool:
    """Nothing to review: an evidence record with no revision and no linked control,
    requirement, or finding gives the model nothing to reason about."""
    counts = evidence_context["counts"]
    return bool(
        evidence_context["latest_revision"]
        or counts["linked_applied_controls"]
        or counts["linked_requirement_assessments"]
        or counts["linked_findings"]
    )


def _insufficient_context_judgement(reason: str) -> dict[str, Any]:
    return {
        "freshness_status": FRESHNESS_STATUS_INSUFFICIENT_CONTEXT,
        "confidence": 0.0,
        "explanation": reason,
        "concerns": [],
        "recommended_action": "Review this evidence manually.",
    }


def _judge_evidence_context(
    evidence_context: dict[str, Any], *, provider=None
) -> tuple[dict[str, Any], str, list[str]]:
    """Returns (judgement, provider_mode, warnings) for one already-built context. Never
    writes; takes a pre-built context so a caller reviewing several items builds each
    evidence's context exactly once."""
    warnings: list[str] = []

    if not _has_reviewable_context(evidence_context):
        return (
            _insufficient_context_judgement(
                "This evidence has no attachment, link, or observation, and no linked "
                "control, requirement, or finding to evaluate against."
            ),
            "configured_local_provider",
            warnings,
        )

    resolved_provider = (
        provider if provider is not None else get_evidence_freshness_review_provider()
    )

    if resolved_provider is None:
        warnings.append(
            "No local AI provider is configured; freshness could not be assessed "
            "automatically."
        )
        return (
            _insufficient_context_judgement(
                "No local AI provider is configured, so this evidence was not reviewed "
                "automatically."
            ),
            "provider_not_configured_fallback",
            warnings,
        )

    try:
        judgement = resolved_provider.judge_evidence_freshness(evidence_context)
        provider_mode = "configured_local_provider"
    except EvidenceFreshnessReviewProviderError as exc:
        if not exc.allow_fallback:
            raise
        warnings.append(f"AI review could not be completed: {exc.detail}")
        judgement = _insufficient_context_judgement(
            "The local AI provider could not be reached or timed out, so this evidence "
            "was not reviewed automatically."
        )
        provider_mode = "local_provider_error_fallback"

    serializer = ProviderFreshnessJudgementSerializer(data=judgement)
    if not serializer.is_valid():
        raise EvidenceFreshnessReviewValidationError(
            "ai_evidence_freshness_review_draft_validation_failed",
            "Generated advisory evidence freshness output did not pass contract validation.",
            serializer.errors,
        )
    validated_judgement = dict(serializer.validated_data)
    validate_provider_output_guardrails(validated_judgement)

    return validated_judgement, provider_mode, warnings


def review_evidence_freshness(evidence, user, *, provider=None) -> dict[str, Any]:
    """Advisory, read-only freshness review of one existing Evidence.

    `user` is required, not optional: it is the sole basis for deciding which linked controls,
    requirement assessments, and findings may enter the prompt (see `_visible`). There is no
    "no user" fallback that reads everything — every caller must supply the real requesting
    user, exactly like the equivalent parameter on `suggest_risk_treatment`.

    Never writes to Evidence, EvidenceRevision, or any linked record. Returns the final,
    schema-validated result; evidence_id/evidence_name/counts/reviewed_at are attached by
    this function from the real object, never taken from the model's output.
    """
    evidence_context = build_evidence_context(evidence, user)
    judgement, provider_mode, warnings = _judge_evidence_context(
        evidence_context, provider=provider
    )

    result = {
        "evidence_id": str(evidence.id),
        "evidence_name": evidence.name or "",
        "freshness_status": judgement["freshness_status"],
        "confidence": judgement["confidence"],
        "explanation": judgement["explanation"],
        "concerns": judgement.get("concerns") or [],
        "recommended_action": judgement["recommended_action"],
        "linked_applied_controls_count": evidence_context["counts"]["linked_applied_controls"],
        "linked_requirement_assessments_count": evidence_context["counts"][
            "linked_requirement_assessments"
        ],
        "linked_findings_count": evidence_context["counts"]["linked_findings"],
        "revision_count": evidence_context["revision_count"],
        "provider_mode": provider_mode,
        "warnings": warnings,
        "advisory_notice": ADVISORY_NOTICE,
        "reviewed_at": timezone.now(),
    }

    serializer = EvidenceFreshnessReviewResultSerializer(data=result)
    if not serializer.is_valid():
        raise EvidenceFreshnessReviewValidationError(
            "ai_evidence_freshness_review_result_validation_failed",
            "Evidence freshness review result did not pass contract validation.",
            serializer.errors,
        )
    # `.data` (the rendered representation), not `.validated_data`, matches this app's
    # convention for the value returned to the API (see e.g. control_effectiveness's
    # `_finalize`) and formats reviewed_at the same way every other timestamp in the API is.
    return serializer.data


def review_evidence_freshness_batch(evidences, user, *, provider=None) -> dict[str, Any]:
    """Advisory, read-only freshness review of a bounded list of Evidence.

    One local-model call per evidence item (never one prompt for the whole batch), so each
    item stays inside the local model's context window and each result stays traceable to
    the evidence it came from. `evidences` must already be filtered to what the requesting
    user may access; nothing outside that queryset is reviewed. `user` is passed through to
    `review_evidence_freshness` for each item, so linked-object visibility is enforced exactly
    the same way as the single-item action.
    """
    results = [
        review_evidence_freshness(evidence, user, provider=provider) for evidence in evidences
    ]
    return {"results": results, "reviewed_count": len(results)}
