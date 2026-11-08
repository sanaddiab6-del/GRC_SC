"""Build a review-only case-setup proposal from trusted engagement data."""

from __future__ import annotations

import hashlib
import json
import re

from django.http import Http404

from core.models import Framework
from iam.models import Folder, RoleAssignment

from .case_setup_serializers import AiCaseSetupInputSerializer
from .engagement_service import authorized_engagement
from .sico_case_setup_adapter import prepare_ai_case_setup


class SicoProposalError(ValueError):
    pass


def build_case_setup_proposal(engagement, folder, framework):
    """Never infer IDs, approvals, framework applicability or evidence."""
    if folder is None or framework is None:
        raise SicoProposalError(
            "An accessible folder and selected framework are required."
        )

    if not engagement.framework_id:
        raise SicoProposalError(
            "Select an existing framework before preparing case setup."
        )

    if str(engagement.folder_id) != str(folder.pk):
        raise SicoProposalError("Engagement folder mismatch.")

    if str(engagement.framework_id) != str(framework.pk):
        raise SicoProposalError("Engagement framework mismatch.")

    objective = str(engagement.objective or "").strip()
    if not objective or len(objective) > 4000:
        raise SicoProposalError("Invalid engagement objective.")

    organization = str(folder.name or "").strip()
    if not organization:
        raise SicoProposalError("The selected folder has no name.")

    # Names are proposals, not evidence of actual scope or applicability.
    short_scope = re.sub(r"\s+", " ", objective)[:90].strip()
    perimeter_name = f"{organization} - {short_scope}"[:200]
    assessment_name = (
        f"{organization} - {framework.name} - {short_scope}"
    )[:200]

    # This is a deterministic ENGAGEMENT OBJECTIVE fingerprint.
    # It is not a claim that a separate Step 1 AI draft was reviewed.
    provenance = {
        "source": "sico_engagement_objective_v1",
        "engagement_id": str(engagement.pk),
        "folder_id": str(folder.pk),
        "framework_id": str(framework.pk),
        "objective": objective,
    }
    encoded = json.dumps(
        provenance, sort_keys=True, ensure_ascii=False
    ).encode("utf-8")

    source_hash = "sha256:" + hashlib.sha256(encoded).hexdigest()

    def decision(entity, action, *, existing_id=None, fields=None):
        result = {
            "platform_entity": entity,
            "action": action,
            "human_approved": False,
        }
        if existing_id is not None:
            result["selected_existing_id"] = str(existing_id)
        if fields is not None:
            result["proposed_fields"] = fields
        return result

    existing_assessment_id = getattr(
        engagement, "compliance_assessment_id", None
    )

    if existing_assessment_id:
        perimeter = decision("Perimeter", "skip")
        assessment = decision(
            "ComplianceAssessment",
            "reuse",
            existing_id=existing_assessment_id,
        )
    else:
        perimeter = decision(
            "Perimeter",
            "create",
            fields={
                "name": perimeter_name,
                "description": objective[:500],
            },
        )
        assessment = decision(
            "ComplianceAssessment",
            "create",
            fields={
                "name": assessment_name,
                "version": "1.0",
                "description": objective[:500],
            },
        )

    payload = {
        "dry_run": True,
        "approved_by_user": False,
        "source_step1_draft_hash": source_hash,
        "framework_resolution": {
            "selected_framework_id": str(framework.pk),
            "requested_framework_name": str(framework.name)[:255],
            "user_confirmed": False,
            "allow_auto_load": False,
        },
        "folder_domain_decision": decision(
            "Folder",
            "reuse",
            existing_id=folder.pk,
        ),
        "perimeter_decision": perimeter,
        "compliance_assessment_decision": assessment,
        "risk_assessment_decision": decision(
            "RiskAssessment", "skip"
        ),
    }

    serializer = AiCaseSetupInputSerializer(data=payload)
    serializer.is_valid(raise_exception=True)

    return {
        "proposed_payload": payload,
        "source": "existing_authenticated_engagement",
        "source_hash_kind": "engagement_objective_fingerprint",
        "requires_human_review": True,
        "execution_performed": False,
        "writes_to_grc_records": False,
    }


def prepare_case_setup_from_engagement(
    request, engagement_id, *, batch_key
):
    """Verify current access, then request ONLY a dry run."""
    engagement = authorized_engagement(request.user, engagement_id)

    folder = Folder.objects.filter(
        pk=engagement.folder_id
    ).first()

    if folder is None or not RoleAssignment.is_object_readable(
        request.user, Folder, folder.pk
    ):
        raise Http404("Engagement folder unavailable.")

    if not engagement.framework_id:
        raise SicoProposalError(
            "Select an existing authorized framework first."
        )

    framework = Framework.objects.filter(
        pk=engagement.framework_id
    ).first()

    if framework is None or not RoleAssignment.is_object_readable(
        request.user, Framework, framework.pk
    ):
        raise Http404("Selected framework unavailable.")

    proposal = build_case_setup_proposal(
        engagement, folder, framework
    )

    preparation = prepare_ai_case_setup(
        request,
        engagement_id,
        batch_key=batch_key,
        proposed_payload=proposal["proposed_payload"],
    )

    return {
        **proposal,
        "preparation": preparation,
    }