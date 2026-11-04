"""Read-only, same-folder/full-risk review choices for the existing SICO AI panel."""
from __future__ import annotations

from uuid import UUID
from django.apps import apps

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import (
    AppliedControl, Asset, FilteringLabel, RiskAssessment, RiskScenario,
    SecurityException, Terminology,
)
from iam.models import Folder, RoleAssignment

from .risk_scenario_full_fields import safe_label


def _as_uuid(value):
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError):
        return None


def _choice_item(item):
    return {"reference": str(item.pk), "label": safe_label(item)}


def _readable_choices(user, model, qs):
    # Filter before exposing a name. Bounded to avoid whole-database scans.
    output = []
    for item in qs.order_by("pk")[:150]:
        if RoleAssignment.is_object_readable(user, model, item.pk):
            output.append(_choice_item(item))
        if len(output) >= 60:
            break
    return output


def _matrix_choices(entries):
    values = []
    for index, entry in enumerate(entries):
        if isinstance(entry, dict):
            label = entry.get("name") or entry.get("abbreviation") or str(index)
            if not isinstance(label, str):
                label = str(index)
        else:
            label = str(entry)
        values.append({"value": index, "label": f"{index}: {label}"})
    return values


class AiRiskFullContextView(APIView):
    """Only authorized records in this exact folder and assessment; no writes."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        data = request.data
        if not isinstance(data, dict) or set(data) - {
            "folder_reference", "assessment_reference", "scenario_title",
            "asset_title", "linked_applied_control_title",
        }:
            return Response({"detail": "Only approved lookup fields are allowed."}, status=400)
        folder_ref = _as_uuid(data.get("folder_reference"))
        assessment_ref = _as_uuid(data.get("assessment_reference"))
        if not folder_ref or not assessment_ref:
            return Response({"detail": "Valid folder and risk assessment are required."}, status=400)

        folder = Folder.objects.filter(id=folder_ref).first()
        assessment = RiskAssessment.objects.filter(
            id=assessment_ref, folder_id=folder_ref
        ).select_related("risk_matrix").first()
        if (folder is None or assessment is None
                or not RoleAssignment.is_object_readable(request.user, Folder, folder_ref)
                or not RoleAssignment.is_object_readable(request.user, RiskAssessment, assessment_ref)):
            # Keep missing and unauthorized indistinguishable.
            return Response({"detail": "The selected assessment is not accessible."}, status=404)

        selected_assessment = assessment
        scope = {"folder_id": folder.id}
        existing_title = str(data.get("scenario_title") or "").strip()[:200]
        existing = (RiskScenario.objects.filter(risk_assessment=assessment,
                    name__iexact=existing_title).first() if existing_title else None)
        existing_display = None
        if existing and RoleAssignment.is_object_readable(request.user, RiskScenario, existing.id):
            existing_display = _choice_item(existing)

        # Actor has no organizational folder. Do NOT enumerate global actors.
        # Only the current user's Actor may be suggested here.
        self_actor = getattr(request.user, "actor", None)
        self_owner = [_choice_item(self_actor)] if self_actor else []

        # EBIOS operational scenarios are included only if that model exposes
        # a true Folder FK. Otherwise never guess its tenant ownership.
        operational_options = []
        ebios_model = apps.get_model("ebios_rm", "OperationalScenario")
        if any(field.name == "folder" for field in ebios_model._meta.get_fields()):
            operational_options = _readable_choices(
                request.user, ebios_model, ebios_model.objects.filter(**scope)
            )
        catalogs = {
            "operational_scenarios": operational_options,
            "assets": _readable_choices(request.user, Asset, Asset.objects.filter(**scope)),
            "existing_controls": _readable_choices(request.user, AppliedControl,
                AppliedControl.objects.filter(**scope, status=AppliedControl.Status.ACTIVE)),
            "extra_controls": _readable_choices(request.user, AppliedControl,
                AppliedControl.objects.filter(**scope)),
            "risk_origins": _readable_choices(request.user, Terminology, Terminology.objects.filter(
                **scope, field_path=Terminology.FieldPath.ROTO_RISK_ORIGIN, is_visible=True)),
            "qualifications": _readable_choices(request.user, Terminology, Terminology.objects.filter(
                **scope, field_path=Terminology.FieldPath.QUALIFICATIONS, is_visible=True)),
            "exceptions": _readable_choices(request.user, SecurityException, SecurityException.objects.filter(**scope)),
            "labels": _readable_choices(request.user, FilteringLabel, FilteringLabel.objects.filter(**scope)),
            "antecedents": _readable_choices(request.user, RiskScenario,
                RiskScenario.objects.filter(**scope, risk_assessment=assessment).exclude(
                    id=existing.id if existing else None)),
            "owners": self_owner,
        }
        # Automatic suggestions ONLY for exact-name matches, never fuzzy
        # keyword guesses or fabricated records.
        def exact_match(options, title):
            found = [opt["reference"] for opt in options if title and opt["label"].casefold() == title.casefold()]
            return found[:1]

        suggestions = {
            "asset_references": exact_match(catalogs["assets"], str(data.get("asset_title") or "").strip()),
            "existing_control_references": exact_match(
                catalogs["existing_controls"], str(data.get("linked_applied_control_title") or "").strip()
            ),
        }
        matrix = selected_assessment.risk_matrix.parse_json()
        return Response({
            "folder": {"reference": folder_ref, "name": folder.name},
            "assessment": {"reference": assessment_ref, "name": assessment.name},
            "existing_risk": existing_display,
            "catalogs": catalogs,
            "suggestions": suggestions,
            "matrix": {
                "probability": _matrix_choices(matrix.get("probability", [])),
                "impact": _matrix_choices(matrix.get("impact", [])),
            },
            "warnings": [
                "Automatic links require exact existing names. Other matches need human review.",
                "Proposed AI risk labels are not official matrix scores. Unverified scores stay unrated.",
                "Owners are restricted to the current user's Actor; other assignments need an authorized company-aware workflow.",
            ],
        }, status=status.HTTP_200_OK)
