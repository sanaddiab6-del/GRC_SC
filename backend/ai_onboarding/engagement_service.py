"""Central SICO engagement execution ledger using EXISTING GRC commit services.

This component is a coordination layer, not an AI model and not an alternate GRC
write path. It runs the original per-module serializers/guardrails/services.

Security rules:
 * only the original creator with CURRENT folder RBAC may read or execute;
 * every GRC stage payload MUST identify precisely the engagement's folder;
 * approved writes require a matching, successful dry-run of unchanged content;
 * one successful write per (engagement, stage, batch), protected by PostgreSQL
   row locking and an atomic receipt in the SAME transaction as the GRC write;
 * returning a stored result requires reauthorization first;
 * no legacy record is reassigned, reset, deleted, or touched on engagement create.
"""
from __future__ import annotations

import importlib
import json
from typing import Any
from uuid import UUID

from django.db import transaction
from django.http import Http404
from rest_framework.exceptions import ValidationError

from core.models import ComplianceAssessment, Framework, RiskAssessment
from iam.models import Folder, RoleAssignment

from .engagement_rules import (
    STAGES_BY_NAME, human_review_flags, reviewed_payload_digest,
    safe_result, scope_is_exact, stage_catalog,
)
from .models import Engagement, EngagementExecution


class EngagementBlocked(Exception):
    def __init__(self, message: str, *, http_status: int = 409):
        super().__init__(message)
        self.http_status = http_status


def _readable(user, obj: Any) -> bool:
    if obj is None or not getattr(user, 'is_authenticated', False):
        return False
    try:
        return bool(RoleAssignment.is_object_readable(user, type(obj), obj.pk))
    except Exception:
        return False


def _folder_or_404(user, folder_id):
    folder = Folder.objects.filter(pk=folder_id).first()
    if not _readable(user, folder):
        raise Http404('Engagement not accessible.')
    return folder


def _scoped_assessment(user, model, item_id, folder_id):
    if item_id is None:
        return None
    instance = model.objects.filter(pk=item_id, folder_id=folder_id).first()
    if not _readable(user, instance):
        raise Http404('Selected assessment unavailable or inaccessible.')
    return instance


def create_engagement(user, *, folder_id, title, objective,
                      framework_id=None, compliance_assessment_id=None,
                      risk_assessment_id=None):
    """Creating a workflow receipt never creates a GRC case or alters a manual record."""
    folder = _folder_or_404(user, folder_id)
    if framework_id is not None:
        framework = Framework.objects.filter(pk=framework_id).first()
        if not _readable(user, framework):
            raise Http404('Selected framework unavailable or inaccessible.')
    _scoped_assessment(user, ComplianceAssessment, compliance_assessment_id, folder.pk)
    _scoped_assessment(user, RiskAssessment, risk_assessment_id, folder.pk)
    return Engagement.objects.create(
        folder_id=folder.pk, created_by_id=str(user.pk), title=title, objective=objective,
        framework_id=framework_id,
        compliance_assessment_id=compliance_assessment_id,
        risk_assessment_id=risk_assessment_id,
    )


def authorized_engagement(user, engagement_id, *, lock=False):
    qs = Engagement.objects
    if lock:
        qs = qs.select_for_update()
    instance = qs.filter(pk=engagement_id, created_by_id=str(user.pk)).first()
    if instance is None or not getattr(user, 'is_authenticated', False):
        raise Http404('Engagement not accessible.')
    _folder_or_404(user, instance.folder_id)
    _scoped_assessment(user, ComplianceAssessment,
                       instance.compliance_assessment_id, instance.folder_id)
    _scoped_assessment(user, RiskAssessment,
                       instance.risk_assessment_id, instance.folder_id)
    return instance


def _response_data(value):
    # JSONFields must never store Django model instances or provider raw objects.
    return json.loads(json.dumps(value, default=str, ensure_ascii=False))


def _resolve_attribute(path: str):
    """Only fixed, source-reviewed registry paths, NEVER user-provided imports."""
    module, attribute = path.split('.', 1)
    return getattr(importlib.import_module(f'ai_onboarding.{module}'), attribute)


def _validate_payload(stage, payload):
    definition = STAGES_BY_NAME[stage]
    if definition.guardrail:
        # Match the existing individual API: raw guardrails first.
        _resolve_attribute(definition.guardrail)(payload)
    serializer = _resolve_attribute(definition.serializer)(data=payload)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def _check_payload_scope(user, instance, stage, payload):
    if not scope_is_exact(payload, instance.folder_id, stage):
        raise EngagementBlocked(
            'The operation must target the existing, authorized engagement folder. '
            'Creating a new organization folder through this coordinator is disabled.',
            http_status=403,
        )
    # If an assessment is supplied, verify its current folder AND RBAC before
    # returning any receipt or executing a service. Services re-check all links.
    ref = payload.get('assessment_reference')
    if not ref and isinstance(payload.get('case_setup_reference'), dict):
        ref = payload['case_setup_reference'].get('compliance_assessment_id')
    if not ref:
        return
    try:
        assessment_id = UUID(str(ref))
    except (TypeError, ValueError):
        raise EngagementBlocked('Invalid assessment reference.', http_status=400)
    model = RiskAssessment if stage == 'risk_scenarios' else ComplianceAssessment
    # Some original services may support other assessment types. Never grant access
    # on the basis of that ambiguity: reject rather than attempt a cross-type lookup.
    _scoped_assessment(user, model, assessment_id, instance.folder_id)


def _result_is_blocked(value, mode):
    return not safe_result(value, expected_mode=mode)


def execute_stage(request, engagement_id, *, stage, batch_key, mode,
                  payload, explicitly_approved=False):
    """Atomic dry-run receipt + approved commit through the existing GRC service.

    Dry-run changes inside the existing service are rolled back while the prepared
    result is stored. On commit, the GRC write and success receipt share one DB
    transaction; concurrent retries cannot repeat the GRC write on PostgreSQL.
    """
    user = request.user
    if stage not in STAGES_BY_NAME:
        raise EngagementBlocked('Unknown or unsupported GRC stage.', http_status=400)
    if not isinstance(payload, dict) or mode not in {'dry_run', 'commit'}:
        raise EngagementBlocked('Invalid operation.', http_status=400)
    # Fail closed: caller-supplied flags are not independent human approval.
    # Keep all SICO engagement commits disabled until the server verifies
    # a separately recorded approval for the exact prepared operation.
    if mode == 'commit':
        raise EngagementBlocked(
            'SICO AI engagement commits require independently verified human approval.',
            http_status=403,
        )
    if payload.get('dry_run') is not (mode == 'dry_run'):
        raise EngagementBlocked('The existing service dry_run must agree with the operation mode.', http_status=400)
    if mode == 'dry_run' and explicitly_approved:
        raise EngagementBlocked('A dry-run cannot be approved for saving.', http_status=400)
    if mode == 'commit' and (not explicitly_approved or not human_review_flags(payload)):
        raise EngagementBlocked('Explicit human approval is required for a GRC write.', http_status=403)

    # Validate the exact original service schema and raw guardrails; no substitute
    # serializers, no shortcut route that bypasses existing protections.
    validated = _validate_payload(stage, payload)
    digest = reviewed_payload_digest(validated)

    with transaction.atomic():
        engagement = authorized_engagement(user, engagement_id, lock=True)
        # For current RBAC and assessment checks even on receipt replay.
        _check_payload_scope(user, engagement, stage, validated)
        receipt = EngagementExecution.objects.filter(
            engagement=engagement, stage=stage, batch_key=batch_key
        ).first()

        if receipt is not None and receipt.status == EngagementExecution.Status.COMMITTED:
            if mode == 'commit' and receipt.committed_digest == digest:
                return {'replay': True, 'mode': 'commit', 'stage': stage,
                        'batch_key': batch_key, 'result': receipt.committed_result}
            raise EngagementBlocked('This batch is already committed. Choose a new batch for new work.')

        if mode == 'commit':
            if receipt is None or receipt.prepared_digest != digest:
                raise EngagementBlocked(
                    'A successful dry-run for EXACTLY these reviewed values is required before saving.'
                )
            if _result_is_blocked(receipt.prepared_result, 'dry_run'):
                raise EngagementBlocked('The dry-run is blocked and cannot be committed.')

        handler = _resolve_attribute(STAGES_BY_NAME[stage].service)
        if mode == 'dry_run':
            # Save ONLY a receipt; rollback even accidental changes made by an
            # existing service during an advisory dry-run.
            with transaction.atomic():
                result = handler(request, validated)
                transaction.set_rollback(True)
        else:
            # The outer transaction includes original handler's nested atomic()
            # and this receipt. If receipt storage fails, GRC write also rolls back.
            result = handler(request, validated)
        result = _response_data(result)
        if _result_is_blocked(result, mode):
            raise EngagementBlocked('The existing GRC service blocked this operation.', http_status=422)

        if receipt is None:
            receipt = EngagementExecution(
                engagement=engagement, stage=stage, batch_key=batch_key,
            )
        if mode == 'dry_run':
            receipt.status = EngagementExecution.Status.PREPARED
            receipt.prepared_digest = digest
            receipt.prepared_result = result
            # Repeat dry-run invalidates an earlier preparation, never a commit.
        else:
            receipt.status = EngagementExecution.Status.COMMITTED
            receipt.committed_digest = digest
            receipt.committed_result = result
            receipt.approved_by_id = str(user.pk)
            if engagement.status == Engagement.Status.DRAFT:
                engagement.status = Engagement.Status.IN_PROGRESS
                engagement.save(update_fields=['status', 'updated_at'])
        receipt.save()
        return {'replay': False, 'mode': mode, 'stage': stage,
                'batch_key': batch_key, 'result': result}


def summary(user, engagement_id):
    instance = authorized_engagement(user, engagement_id)
    rows = []
    for item in instance.executions.all():
        rows.append({'stage': item.stage, 'batch_key': item.batch_key,
                     'status': item.status, 'updated_at': item.updated_at.isoformat(),
                     'approved_by_id': item.approved_by_id if item.status == 'committed' else None})
    return {
        'id': str(instance.pk), 'title': instance.title,
        'objective': instance.objective,
        'folder_id': str(instance.folder_id),
        'framework_id': str(instance.framework_id) if instance.framework_id else None,
        'compliance_assessment_id': str(instance.compliance_assessment_id) if instance.compliance_assessment_id else None,
        'risk_assessment_id': str(instance.risk_assessment_id) if instance.risk_assessment_id else None,
        'status': instance.status, 'plan': instance.plan, 'operations': rows,
        'supported_stages': stage_catalog(),
        'limitations': [
            'The coordinator is not a substitute for evidence verification or regulatory assessment.',
            'No module is marked complete merely because a suggestion was generated.',
            'Only reviewed service operations are logged; unfinished manual work is not claimed complete.',
            'The current integration does not yet run an autonomous cross-module plan or analyze uploaded evidence.',
        ],
    }
