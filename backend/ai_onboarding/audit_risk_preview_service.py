"""Read-only audit and risk preview built on existing SICO GRC models.

Does NOT call Ollama, interpret attachment bytes, conclude compliance, or write to
models. Results are a factual source inventory for a later evidence-analysis agent.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import Http404

from core.models import ComplianceAssessment, RiskAssessment, RiskScenario

from .audit_risk_rules import preview_risk_ratings, review_evidence_metadata
from .rbac_context import is_visible_to_user


def _get_visible(user, model, pk):
    try:
        instance = model.objects.get(pk=pk)
    except (model.DoesNotExist, ValueError, TypeError):
        raise Http404("Record not found.") from None
    if not is_visible_to_user(user, instance):
        # Do not reveal whether an inaccessible record exists.
        raise Http404("Record not found.")
    return instance


def build_assessment_audit_preview(user, assessment_id, *, offset: int, limit: int) -> dict[str, Any]:
    assessment = _get_visible(user, ComplianceAssessment, assessment_id)
    queryset = (
        assessment.requirement_assessments
        .filter(selected=True)
        .select_related("requirement")
        .prefetch_related("evidences__revisions", "applied_controls")
        .order_by("id")
    )
    total = queryset.count()
    rows = []
    inaccessible_rows = 0
    for item in queryset[offset:offset + limit]:
        if not is_visible_to_user(user, item):
            inaccessible_rows += 1
            continue
        evidence_rows = []
        restricted_evidence_count = 0
        for evidence in item.evidences.all():
            if not is_visible_to_user(user, evidence):
                restricted_evidence_count += 1
                continue
            revision = max(evidence.revisions.all(), key=lambda r: r.version, default=None)
            evidence_rows.append({
                "id": str(evidence.pk),
                "name": evidence.name,
                "status": evidence.status,
                "expiry_date": evidence.expiry_date.isoformat() if evidence.expiry_date else None,
                "has_attachment": bool(revision and revision.attachment),
                "has_link": bool(revision and revision.link),
                "revision_version": revision.version if revision else None,
                "attachment_hash": revision.attachment_hash if revision else None,
                # No raw attachment, free-text observations, or external link URL in this endpoint.
                "content_reviewed": False,
            })
        controls = [
            {"id": str(control.pk), "name": control.name}
            for control in item.applied_controls.all()
            if is_visible_to_user(user, control)
        ]
        review = review_evidence_metadata(evidence_rows)
        if restricted_evidence_count:
            review["review_flags"].append("some_evidence_inaccessible")
            review["review_flags"].sort()
        requirement = item.requirement
        rows.append({
            "requirement_assessment_id": str(item.pk),
            "requirement_id": str(requirement.pk),
            "requirement_code": requirement.ref_id or "",
            "requirement_name": requirement.name,
            "current_recorded_result": item.result,
            "current_workflow_status": item.status,
            "applied_controls": controls,
            "evidence": evidence_rows,
            "evidence_review": review,
        })
    return {
        "kind": "sico_audit_read_only_preview_v1",
        "assessment": {
            "id": str(assessment.pk),
            "name": assessment.name,
            "framework_id": str(assessment.framework_id),
        },
        "page": {"offset": offset, "limit": limit, "total_selected_requirements": total, "returned": len(rows), "inaccessible_rows": inaccessible_rows},
        "requirements": rows,
        "caveats": [
            "Existing recorded results are shown, not reassessed.",
            "Evidence attachment content has NOT been inspected.",
            "No compliance, audit, risk acceptance, or closure decision was made.",
        ],
        "writes_performed": False,
    }


def build_risk_matrix_preview(user, scenario_id, ratings: dict[str, Any]) -> dict[str, Any]:
    scenario = _get_visible(user, RiskScenario, scenario_id)
    assessment = _get_visible(user, RiskAssessment, scenario.risk_assessment_id)
    matrix = assessment.risk_matrix
    if not is_visible_to_user(user, matrix):
        raise Http404("Record not found.")
    calculated = preview_risk_ratings(matrix.json_definition, ratings)
    return {
        "kind": "sico_risk_matrix_read_only_preview_v1",
        "risk_scenario": {"id": str(scenario.pk), "name": scenario.name},
        "risk_assessment": {"id": str(assessment.pk), "name": assessment.name},
        "matrix": {"id": str(matrix.pk), "name": matrix.name},
        "current_recorded_ratings": {
            "inherent": {"probability": scenario.inherent_proba, "impact": scenario.inherent_impact, "risk_level_index": scenario.inherent_level},
            "current": {"probability": scenario.current_proba, "impact": scenario.current_impact, "risk_level_index": scenario.current_level},
            "residual": {"probability": scenario.residual_proba, "impact": scenario.residual_impact, "risk_level_index": scenario.residual_level},
        },
        "preview": calculated,
        "writes_performed": False,
    }
