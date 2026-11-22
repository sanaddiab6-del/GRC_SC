"""SICO AI initial control reviews persisted to EXISTING RequirementAssessment rows.

This is deliberately not a compliance-grading engine. No evidence is assumed or
invented. The only possible saved verdict is NOT_ASSESSED; existing observations,
answers, controls, evidences, and human classifications are never overwritten.

No tenant can be created here. Requires an existing authorized SICO engagement,
its saved ComplianceAssessment, a user-initiated save, a separate opt-in flag,
and the platform's native RequirementAssessmentWriteSerializer and RBAC.
"""
from __future__ import annotations

import hashlib
import json
import os
from uuid import UUID

from django.contrib.auth.models import Permission
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from jsonschema import Draft202012Validator, ValidationError as SchemaError

from core.models import ComplianceAssessment, RequirementAssessment
from core.serializers import RequirementAssessmentWriteSerializer
from iam.models import RoleAssignment
from .models import Engagement, EngagementExecution
from .engagement_service import authorized_engagement
from .sico_ai_workflow_views import verify_principal, readable
from .llm_config import CAPABILITY_GRC_CAPABILITY_SELECTION, resolve_advisory_capability_config
from .llm_provider import get_advisory_provider_selection
from .llm_errors import AiProviderError

STAGE = 'ai_requirement_initial_review'
MARKER = '[SICO AI: preliminary evidence request; NOT ASSESSED]'
SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['review_question', 'evidence_request'],
    'properties': {
        'review_question': {'type': 'string', 'minLength': 20, 'maxLength': 360},
        'evidence_request': {'type': 'string', 'minLength': 20, 'maxLength': 360},
    },
}
PROMPT = '''You are SICO AI preparing ONE initial audit-control review.
Use the REAL requirement ID/title/description supplied by the backend and the
user's assessment objective. Return ONE focused review_question and ONE precise
evidence_request as JSON. Distinguish facts from hypotheses. Never say a
requirement is compliant, partially compliant, noncompliant or inapplicable;
there is no verified evidence here. Do not invent evidence, policies, controls,
control identifiers, interviews or assessment outcomes. Name concrete records
or tests an assessor should gather. Be specific to the supplied requirement.
'''


class ReviewInput(serializers.Serializer):
    action = serializers.ChoiceField(choices=['status', 'generate_and_save'])
    engagement_id = serializers.UUIDField(required=False)
    confirm_preliminary_write = serializers.BooleanField(required=False, default=False)


def _engagement_for_user(user, engagement_id=None):
    """An omitted ID resolves only this user's recent already-SAVED cases."""
    if engagement_id:
        engagement = authorized_engagement(user, engagement_id)
        verify_principal(user, engagement.folder_id)
        return engagement
    recent = Engagement.objects.filter(
        created_by_id=str(user.pk), compliance_assessment_id__isnull=False,
    ).order_by('-created_at')[:30]
    for candidate in recent:
        try:
            engagement = authorized_engagement(user, candidate.pk)
            verify_principal(user, engagement.folder_id)
            return engagement
        except Exception:
            continue
    return None


def _scoped_case(user, engagement):
    case = ComplianceAssessment.objects.filter(
        pk=engagement.compliance_assessment_id,
        folder_id=engagement.folder_id,
        framework_id=engagement.framework_id,
    ).first()
    if case is None or not readable(user, ComplianceAssessment, case.pk):
        return None
    return case


def _can_edit(user, folder):
    try:
        perm = Permission.objects.get(
            codename='change_requirementassessment', content_type__app_label='core')
        return bool(RoleAssignment.is_access_allowed(user, perm, folder))
    except Exception:
        return False


def _eligible(case):
    """Only never-reviewed, empty, assessable requirement rows are candidates."""
    return RequirementAssessment.objects.filter(
        compliance_assessment_id=case.pk,
        folder_id=case.folder_id,
        requirement__framework_id=case.framework_id,
        requirement__assessable=True, selected=True,
        result=RequirementAssessment.Result.NOT_ASSESSED,
        status=RequirementAssessment.Status.TODO,
    ).filter(Q(observation__isnull=True) | Q(observation='')).select_related('requirement').order_by('requirement__ref_id', 'pk')


def _summary(user, engagement, case):
    base = RequirementAssessment.objects.filter(
        compliance_assessment_id=case.pk,
        folder_id=case.folder_id,
        requirement__framework_id=case.framework_id,
        requirement__assessable=True, selected=True,
    )
    receipts = list(EngagementExecution.objects.filter(
        engagement_id=engagement.pk, stage=STAGE,
        status=EngagementExecution.Status.COMMITTED,
    ).order_by('created_at')[:150])
    rows = []
    for receipt in receipts:
        obj = base.filter(pk=receipt.batch_key).select_related('requirement').first()
        if obj is None or not readable(user, RequirementAssessment, obj.pk):
            continue
        expected = receipt.committed_result or {}
        # Verify persisted field values, not just a receipt's assertion.
        if (obj.observation != expected.get('observation') or
                obj.result != RequirementAssessment.Result.NOT_ASSESSED):
            continue
        rows.append({
            'requirement_assessment_id': str(obj.pk),
            'requirement_id': str(obj.requirement_id),
            'control_id': str(obj.requirement.ref_id or ''),
            'control_name': str(obj.requirement.name or ''),
            'result': obj.result,
            'status': obj.status,
            'observation': obj.observation,
            'saved_and_verified': True,
        })
    return {
        'case_id': str(case.pk), 'case_name': str(case.name),
        'framework_id': str(case.framework_id),
        'total_assessable_requirements': base.count(),
        'ai_reviews_saved_and_verified': len(rows),
        'remaining_blank_to_do': _eligible(case).count(),
        'saved_reviews': rows,
        'compliance_conclusion': 'not_established',
        'note': 'These are saved preliminary reviews, NOT compliance verdicts. Existing human assessments were not changed.',
    }


def _generate_specific_review(case, engagement, ra):
    config = resolve_advisory_capability_config(CAPABILITY_GRC_CAPABILITY_SELECTION)
    selection = get_advisory_provider_selection(config)
    if selection.provider is None:
        raise ValueError('No configured local AI provider.')
    data = selection.provider.generate_structured(
        capability=CAPABILITY_GRC_CAPABILITY_SELECTION,
        model=selection.config.model,
        system_prompt=PROMPT,
        user_payload={
            'assessment_objective': engagement.objective[:1600],
            'framework_name_from_saved_case': str(case.framework.name)[:160],
            'requirement_ref_id_from_saved_library': str(ra.requirement.ref_id or '')[:80],
            'requirement_name_from_saved_library': str(ra.requirement.name or '')[:220],
            'requirement_description_from_saved_library': str(ra.requirement.description or '')[:700],
            'typical_evidence_from_saved_library': str(ra.requirement.typical_evidence or '')[:350],
            'evidence_verification': 'No evidence is evaluated by this step. Result must remain not_assessed.',
        },
        json_schema=SCHEMA,
        timeout_seconds=min(150, selection.config.timeout_seconds),
        max_output_tokens=min(450, selection.config.max_output_tokens),
        temperature=0.0,
        schema_name='sico_requirement_preliminary_review_v1',
    )
    Draft202012Validator(SCHEMA).validate(data)
    return {k: v.strip() for k, v in data.items()}


def _format_observation(generated):
    return '\n'.join((
        MARKER,
        'AI-generated review question: ' + generated['review_question'],
        'Evidence required before any compliance decision: ' + generated['evidence_request'],
        'Compliance result: NOT ASSESSED. Requires verified evidence and authorized assessor review.',
    ))


def _save_preliminary_review(request, engagement, case, selected_id, observation):
    """Native serializer + atomic receipt + record re-read, never a raw AI ORM write."""
    user = request.user
    with transaction.atomic():
        # Lock the scoped engagement and target before writing; RBAC re-evaluated.
        engagement = authorized_engagement(user, engagement.pk, lock=True)
        verify_principal(user, engagement.folder_id)
        current = _scoped_case(user, engagement)
        if current is None or current.pk != case.pk or current.is_locked or current.status == 'in_review':
            raise ValueError('Assessment is unavailable or locked.')
        if not _can_edit(user, current.folder):
            raise PermissionError('You cannot update requirement assessments for this organization.')
        obj = RequirementAssessment.objects.select_for_update().select_related('requirement').filter(
            pk=selected_id, compliance_assessment_id=current.pk,
            folder_id=engagement.folder_id, requirement__framework_id=current.framework_id,
            requirement__assessable=True, selected=True,
        ).first()
        if obj is None or not readable(user, RequirementAssessment, obj.pk):
            raise PermissionError('Requirement assessment is inaccessible.')
        existing_receipt = EngagementExecution.objects.select_for_update().filter(
            engagement=engagement, stage=STAGE, batch_key=str(obj.pk),
        ).first()
        if existing_receipt is not None:
            raise ValueError('This control has already been processed by SICO AI.')
        if (obj.status != RequirementAssessment.Status.TODO or
                obj.result != RequirementAssessment.Result.NOT_ASSESSED or
                (obj.observation or '').strip() or
                obj.evidences.exists() or obj.applied_controls.exists()):
            raise ValueError('A human or existing evidence has changed this control. It will not be overwritten.')
        serializer = RequirementAssessmentWriteSerializer(
            instance=obj,
            data={
                'observation': observation,
                'status': RequirementAssessment.Status.IN_PROGRESS,
                'result': RequirementAssessment.Result.NOT_ASSESSED,
            },
            partial=True, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        obj.refresh_from_db()
        if (obj.observation != observation or
                obj.result != RequirementAssessment.Result.NOT_ASSESSED or
                obj.status != RequirementAssessment.Status.IN_PROGRESS):
            raise ValueError('Persisted control review did not match the safe expected state.')
        digest = hashlib.sha256(observation.encode('utf-8')).hexdigest()
        EngagementExecution.objects.create(
            engagement=engagement, stage=STAGE, batch_key=str(obj.pk),
            status=EngagementExecution.Status.COMMITTED,
            committed_digest=digest,
            committed_result={
                'requirement_assessment_id': str(obj.pk),
                'observation': obj.observation,
                'result': obj.result,
                'status': obj.status,
                'evidence_verified': False,
            },
            approved_by_id=str(user.pk),
        )
        return str(obj.pk)


class SicoAiRequirementReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = ReviewInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        if not request.user.is_active:
            return Response({'detail': 'Inactive account.'}, status=403)
        engagement = _engagement_for_user(request.user, values.get('engagement_id'))
        if engagement is None:
            return Response({'detail': 'No accessible, saved GRC case yet. Save an authorized case first.',
                             'business_records_written': False}, status=404)
        case = _scoped_case(request.user, engagement)
        if case is None:
            return Response({'detail': 'Saved compliance assessment cannot be verified.',
                             'business_records_written': False}, status=403)
        if values['action'] == 'status':
            return Response({'business_records_written': False, 'progress': _summary(request.user, engagement, case)})
        if values['confirm_preliminary_write'] is not True:
            return Response({'detail': 'Explicit user confirmation is required for writing preliminary reviews.'}, status=403)
        if os.environ.get('SICO_AI_REQUIREMENT_DRAFT_WRITES_ENABLED', '').lower() != 'true':
            return Response({'detail': 'Control-review writes are disabled by the operator.',
                             'business_records_written': False}, status=403)
        if not _can_edit(request.user, case.folder):
            return Response({'detail': 'Current user cannot change requirement assessments.'}, status=403)
        if case.is_locked or case.status == 'in_review':
            return Response({'detail': 'This audit is locked or in review.'}, status=409)
        candidates = _eligible(case)
        # Existing evidence/controls, even on a blank row, must be left to a reviewer.
        selected = next((row for row in candidates[:40]
                         if not row.evidences.exists() and not row.applied_controls.exists() and
                         readable(request.user, RequirementAssessment, row.pk)), None)
        if selected is None:
            return Response({'detail': 'No untouched requirement is eligible for preliminary AI review.',
                             'business_records_written': False,
                             'progress': _summary(request.user, engagement, case)}, status=409)
        try:
            generated = _generate_specific_review(case, engagement, selected)
        except (AiProviderError, SchemaError, TimeoutError, ValueError, KeyError, TypeError):
            return Response({'detail': 'Local Qwen failed to produce a valid control-specific review. No record changed.',
                             'business_records_written': False}, status=503)
        observation = _format_observation(generated)
        try:
            record_id = _save_preliminary_review(request, engagement, case, selected.pk, observation)
        except PermissionError:
            return Response({'detail': 'Permission changed or this control is inaccessible. No record changed.',
                             'business_records_written': False}, status=403)
        except ValueError as exc:
            return Response({'detail': str(exc), 'business_records_written': False}, status=409)
        progress = _summary(request.user, engagement, case)
        row = next((r for r in progress['saved_reviews'] if r['requirement_assessment_id'] == record_id), None)
        if row is None:
            return Response({'detail': 'Write succeeded but result could not be read back. Check the audit before retrying.',
                             'business_records_written': True, 'verified': False}, status=409)
        return Response({'business_records_written': True, 'verified': True,
                         'record': row, 'progress': progress,
                         'note': 'One real RequirementAssessment was updated and read back. Verdict remains NOT ASSESSED.'})
