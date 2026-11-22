"""Approval-gated, resumable GRC execution in the EXISTING SICO AI Next page.

This is not an alternate writer. Case setup uses the existing serializer, service,
and engagement ledger. The ledger also exposes status across the 11 reviewed
stages; unimplemented stage-drafting adapters are NEVER represented as done.

There is no company provisioning, automatic human approval, inference of
compliance, migration, or direct model-to-database write capability here.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import Permission
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import ComplianceAssessment, Framework, Perimeter, RequirementAssessment, RiskAssessment, RiskMatrix
from iam.models import Folder, RoleAssignment

from .engagement_approval_views import get_prepared_receipt, verified_review_snapshot
from .engagement_rules import STAGES, safe_result
from .sico_ai_agent_tools import GrcReadRegistry
from .models import EngagementExecution
from .engagement_service import (
    EngagementBlocked, authorized_engagement, create_engagement, execute_stage,
)

STAGE = 'case_setup'
BATCH = 'initial'


def verify_principal(user, folder_id=None):
    """Reuse existing live membership, focus, active-user, and expiry checks."""
    try:
        GrcReadRegistry(user, folder_id=folder_id).authorize()
    except Exception:
        raise Http404('Current organization membership or access cannot be verified.') from None



def readable(user, model, record_id):
    try:
        return bool(RoleAssignment.is_object_readable(user, model, record_id))
    except Exception:
        return False


def add_allowed(user, folder, codename):
    try:
        permission = Permission.objects.get(codename=codename, content_type__app_label='core')
        return bool(RoleAssignment.is_access_allowed(user, permission, folder))
    except Exception:
        return False


def allowed_folder(user, identifier):
    folder = Folder.objects.filter(pk=identifier, content_type=Folder.ContentType.DOMAIN).first()
    if folder is None or not readable(user, Folder, folder.pk):
        raise Http404('Organization unavailable.')
    return folder


def workflow_status(user, engagement):
    """Never count an uncommitted stage as completed business work."""
    authorized_engagement(user, engagement.pk)
    receipts = list(engagement.executions.all())
    rows = []
    for stage in STAGES:
        related = [r for r in receipts if r.stage == stage.slug]
        if any(r.status == 'committed' for r in related):
            state = 'committed'
        elif any(r.status == 'prepared' and r.approved_by_id for r in related):
            state = 'approved_not_committed'
        elif any(r.status == 'prepared' for r in related):
            state = 'prepared_needs_approval'
        else:
            state = 'not_prepared'
        rows.append({'stage': stage.slug, 'status': state})
    return {
        'engagement_id': str(engagement.pk),
        'folder_id': str(engagement.folder_id),
        'framework_id': str(engagement.framework_id) if engagement.framework_id else None,
        'compliance_assessment_id': str(engagement.compliance_assessment_id) if engagement.compliance_assessment_id else None,
        'risk_assessment_id': str(engagement.risk_assessment_id) if engagement.risk_assessment_id else None,
        'workflow': rows,
        'next': [r['stage'] for r in rows if r['status'] == 'not_prepared'],
        'limitations': 'Unprepared stages require validated GRC service payloads and separate review; no evidence or compliance result was inferred.',
    }


class OptionsInput(serializers.Serializer):
    organization_query = serializers.CharField(required=False, allow_blank=True, max_length=150)
    framework_query = serializers.CharField(required=False, allow_blank=True, max_length=100)
    folder_id = serializers.UUIDField(required=False)


class WorkflowOptionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = OptionsInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        verify_principal(request.user, values.get('folder_id'))
        query = Folder.objects.filter(content_type=Folder.ContentType.DOMAIN)
        if values.get('organization_query'):
            query = query.filter(name__icontains=values['organization_query'])
        folders = []
        for row in query.order_by('name', 'pk')[:201]:
            if readable(request.user, Folder, row.pk) and add_allowed(request.user, row, 'add_complianceassessment'):
                folders.append({'id': str(row.pk), 'name': str(row.name)[:200]})
                if len(folders) == 75:
                    break

        query = Framework.objects.all()
        if values.get('framework_query'):
            needle = values['framework_query'].strip()
            query = query.filter(Q(name__icontains=needle) | Q(ref_id__icontains=needle))
        frameworks = []
        for row in query.order_by('name', 'pk')[:301]:
            if readable(request.user, Framework, row.pk):
                frameworks.append({'id': str(row.pk), 'name': str(row.name)[:200],
                                   'ref_id': str(getattr(row, 'ref_id', '') or '')[:100]})
                if len(frameworks) == 75:
                    break

        perimeters, matrices = [], []
        if values.get('folder_id'):
            folder = allowed_folder(request.user, values['folder_id'])
            if not add_allowed(request.user, folder, 'add_complianceassessment'):
                raise Http404('Insufficient permissions for the selected scope.')
            for row in Perimeter.objects.filter(folder_id=folder.pk).order_by('name', 'pk')[:100]:
                if readable(request.user, Perimeter, row.pk):
                    perimeters.append({'id': str(row.pk), 'name': str(row.name)[:200]})
            for row in RiskMatrix.objects.all().order_by('name', 'pk')[:100]:
                if readable(request.user, RiskMatrix, row.pk):
                    matrices.append({'id': str(row.pk), 'name': str(row.name)[:200]})
        return Response({'organizations': folders, 'frameworks': frameworks,
                         'perimeters': perimeters, 'risk_matrices': matrices,
                         'bounded': True, 'business_records_written': False})


class PrepareInput(serializers.Serializer):
    instruction = serializers.CharField(min_length=20, max_length=4000)
    folder_id = serializers.UUIDField()
    framework_id = serializers.UUIDField()
    assessment_name = serializers.CharField(min_length=4, max_length=200)
    perimeter_id = serializers.UUIDField(required=False)
    new_perimeter_name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    risk_matrix_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        if bool(attrs.get('perimeter_id')) == bool(attrs.get('new_perimeter_name', '').strip()):
            raise serializers.ValidationError('Select an existing perimeter OR a new perimeter name.')
        return attrs


def case_payload(values, framework):
    """Only selected, server-verified IDs enter the GRC writer; model text is context."""
    fingerprint = {
        'instruction': values['instruction'], 'folder': str(values['folder_id']),
        'framework': str(values['framework_id']), 'perimeter': str(values.get('perimeter_id') or ''),
        'new_perimeter_name': values.get('new_perimeter_name', ''),
        'risk_matrix': str(values.get('risk_matrix_id') or ''),
        'assessment_name': values['assessment_name'],
    }
    h = hashlib.sha256(json.dumps(fingerprint, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    def reuse(entity, record_id):
        return {'action': 'reuse', 'platform_entity': entity,
                'selected_existing_id': str(record_id), 'human_approved': False}
    def create(entity, name):
        return {'action': 'create', 'platform_entity': entity, 'human_approved': False,
                'proposed_fields': {'name': name}}
    risk = {'action': 'skip', 'platform_entity': 'RiskAssessment', 'human_approved': False}
    if values.get('risk_matrix_id'):
        risk = create('RiskAssessment', values['assessment_name'] + ' — Risk assessment')
        risk['proposed_fields']['selected_risk_matrix_id'] = str(values['risk_matrix_id'])
    return {
        'draft_type': 'sico-user-request-scoped-case-setup',
        'schema_version': 'sico-existing-grc-services-v1',
        'source_step1_draft_hash': 'sha256:' + h,
        'idempotency_key': str(uuid4()),
        'dry_run': True, 'approved_by_user': False,
        'framework_resolution': {'requested_framework_name': str(framework.name),
                                 'selected_framework_id': str(framework.pk),
                                 'user_confirmed': True, 'allow_auto_load': False},
        'folder_domain_decision': reuse('Folder', values['folder_id']),
        'perimeter_decision': (reuse('Perimeter', values['perimeter_id']) if values.get('perimeter_id')
                               else create('Perimeter', values['new_perimeter_name'].strip())),
        'compliance_assessment_decision': create('ComplianceAssessment', values['assessment_name']),
        'risk_assessment_decision': risk,
    }


def business_error(exc):
    if isinstance(exc, EngagementBlocked):
        return Response({'detail': str(exc)}, status=exc.http_status)
    if hasattr(exc, 'to_response') and hasattr(exc, 'status_code'):
        return Response(exc.to_response(), status=exc.status_code)
    return None


def prepare_workflow(request, values):
    """Single validated case-setup writer shared by both intake routes."""
    verify_principal(request.user, values['folder_id'])
    folder = allowed_folder(request.user, values['folder_id'])
    if not add_allowed(request.user, folder, 'add_complianceassessment'):
        return Response({'detail': 'Not authorized to create assessments in this organization.'}, status=403)
    if values.get('perimeter_id'):
        perimeter = Perimeter.objects.filter(pk=values['perimeter_id'], folder_id=folder.pk).first()
        if not perimeter or not readable(request.user, Perimeter, perimeter.pk):
            raise Http404('Perimeter not accessible in selected organization.')
    elif not add_allowed(request.user, folder, 'add_perimeter'):
        return Response({'detail': 'Not authorized to create the proposed perimeter.'}, status=403)
    framework = Framework.objects.filter(pk=values['framework_id']).first()
    if not framework or not readable(request.user, Framework, framework.pk):
        raise Http404('Selected framework is not accessible.')
    if values.get('risk_matrix_id'):
        matrix = RiskMatrix.objects.filter(pk=values['risk_matrix_id']).first()
        if not matrix or not readable(request.user, RiskMatrix, matrix.pk):
            raise Http404('Selected risk matrix is not accessible.')
        if not add_allowed(request.user, folder, 'add_riskassessment'):
            return Response({'detail': 'Not authorized to create a risk assessment.'}, status=403)
    payload = case_payload(values, framework)
    try:
        with transaction.atomic():
            engagement = create_engagement(
                request.user, folder_id=folder.pk, title=values['assessment_name'],
                objective=values['instruction'], framework_id=framework.pk,
            )
            result = execute_stage(
                request, engagement.pk, stage=STAGE, batch_key=BATCH,
                mode='dry_run', payload=payload,
            )
            review = result['result']['_sico_review']
    except Exception as exc:
        response = business_error(exc)
        if response is not None:
            return response
        raise
    return Response({
        'engagement_id': str(engagement.pk), 'stage': STAGE, 'batch_key': BATCH,
        'prepared_digest': review['prepared_digest'],
        'planned_actions': result['result'].get('planned_actions', []),
        'warnings': result['result'].get('warnings', []),
        'review': review,
        'scope': {'folder': {'id': str(folder.pk), 'name': folder.name},
                  'framework': {'id': str(framework.pk), 'name': framework.name}},
        'workflow': workflow_status(request.user, engagement),
        'business_records_written': False, 'needs_review': True,
    }, status=status.HTTP_201_CREATED)


class WorkflowPrepareView(APIView):
    """Persist a resumable engagement and validated preview, not GRC business data."""
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = PrepareInput(data=request.data)
        form.is_valid(raise_exception=True)
        return prepare_workflow(request, form.validated_data)


class ReviewInput(serializers.Serializer):
    engagement_id = serializers.UUIDField()


class WorkflowReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = ReviewInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        engagement = authorized_engagement(request.user, values['engagement_id'])
        verify_principal(request.user, engagement.folder_id)
        receipt = get_prepared_receipt(request.user, values['engagement_id'], STAGE, BATCH)
        return Response({'engagement_id': str(values['engagement_id']),
                         'review': verified_review_snapshot(receipt),
                         'prepared_digest': receipt.prepared_digest,
                         'planned_actions': receipt.prepared_result.get('planned_actions', []),
                         'approved': bool(receipt.approved_by_id),
                         'commit_enabled': getattr(settings, 'SICO_CASE_SETUP_COMMITS_ENABLED', False) is True,
                         'business_records_written': False})


class ApproveInput(ReviewInput):
    prepared_digest = serializers.RegexField(regex=r'^[a-f0-9]{64}$')
    confirm_reviewed = serializers.BooleanField(required=True)


class WorkflowApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = ApproveInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        if values['confirm_reviewed'] is not True:
            return Response({'detail': 'Review and explicit confirmation are required.'}, status=400)
        engagement = authorized_engagement(request.user, values['engagement_id'])
        verify_principal(request.user, engagement.folder_id)
        with transaction.atomic():
            receipt = get_prepared_receipt(request.user, values['engagement_id'], STAGE, BATCH, lock=True)
            if not hmac.compare_digest(receipt.prepared_digest, values['prepared_digest']):
                return Response({'detail': 'The preview changed; review again.'}, status=409)
            receipt.approved_by_id = str(request.user.pk)
            receipt.save(update_fields=['approved_by_id', 'updated_at'])
        return Response({'approved': True, 'prepared_digest': receipt.prepared_digest,
                         'engagement_id': str(values['engagement_id']),
                         'business_records_written': False,
                         'commit_enabled': getattr(settings, 'SICO_CASE_SETUP_COMMITS_ENABLED', False) is True})


def _committed_case_replay(user, engagement, receipt, requested_digest):
    """Return the ALREADY committed case after independent scope and RBAC checks.

    Only this commit endpoint can use a committed receipt. Do not change
    get_prepared_receipt(): its review and approval endpoints deliberately refuse
    already committed operations. This replay never invokes the GRC writer.
    """
    if receipt.approved_by_id != str(user.pk):
        return Response({'detail': 'The committed operation was not approved by this user.'}, status=403)
    if not (receipt.prepared_digest and receipt.committed_digest and
            hmac.compare_digest(receipt.prepared_digest, requested_digest) and
            hmac.compare_digest(receipt.committed_digest, requested_digest)):
        return Response({'detail': 'The committed operation fingerprint does not match.'}, status=409)
    review = verified_review_snapshot(receipt)
    payload = review['operation_payload']
    folder_choice = payload.get('folder_domain_decision')
    framework_choice = payload.get('framework_resolution')
    if (not isinstance(folder_choice, dict) or not isinstance(framework_choice, dict) or
            folder_choice.get('action') != 'reuse' or
            folder_choice.get('selected_existing_id') != str(engagement.folder_id) or
            framework_choice.get('selected_framework_id') != str(engagement.framework_id)):
        return Response({'detail': 'The saved operation scope could not be verified.'}, status=409)

    # A previous successful write is NOT permission to disclose its result later.
    folder = allowed_folder(user, engagement.folder_id)
    if not add_allowed(user, folder, 'add_complianceassessment'):
        return Response({'detail': 'The current user cannot access this operation.'}, status=403)
    framework = Framework.objects.filter(pk=engagement.framework_id).first()
    if framework is None or not readable(user, Framework, framework.pk):
        raise Http404('Framework is no longer accessible.')
    case = ComplianceAssessment.objects.filter(
        pk=engagement.compliance_assessment_id,
        folder_id=engagement.folder_id, framework_id=engagement.framework_id,
    ).first()
    if case is None or not readable(user, ComplianceAssessment, case.pk):
        raise Http404('Previously created assessment is no longer accessible in this organization.')
    perimeter = Perimeter.objects.filter(pk=case.perimeter_id, folder_id=engagement.folder_id).first()
    if perimeter is None or not readable(user, Perimeter, perimeter.pk):
        raise Http404('Assessment perimeter is no longer accessible.')
    choice = payload.get('perimeter_decision', {})
    if (isinstance(choice, dict) and choice.get('action') == 'reuse' and
            choice.get('selected_existing_id') != str(perimeter.pk)):
        return Response({'detail': 'Assessment perimeter no longer matches the reviewed request.'}, status=409)

    committed = receipt.committed_result
    if not safe_result(committed, expected_mode='commit'):
        return Response({'detail': 'Committed operation receipt is invalid.'}, status=409)
    created = committed.get('created_objects', [])
    if not isinstance(created, list) or not all(isinstance(item, dict) for item in created):
        return Response({'detail': 'Committed record references are invalid.'}, status=409)
    case_ids = [str(item.get('id')) for item in created
                if item.get('platform_entity') == 'ComplianceAssessment']
    if case_ids != [str(case.pk)]:
        return Response({'detail': 'Committed assessment does not match its receipt.'}, status=409)
    risk_ids = [str(item.get('id')) for item in created
                if item.get('platform_entity') == 'RiskAssessment']
    if len(risk_ids) > 1 or (risk_ids and risk_ids != [str(engagement.risk_assessment_id)]):
        return Response({'detail': 'Committed risk assessment does not match its receipt.'}, status=409)
    if engagement.risk_assessment_id:
        risk = RiskAssessment.objects.filter(
            pk=engagement.risk_assessment_id, folder_id=engagement.folder_id,
        ).first()
        if risk is None or not readable(user, RiskAssessment, risk.pk):
            raise Http404('Previously created risk assessment is no longer accessible.')
    for item in created:
        kind = item.get('platform_entity')
        if kind == 'Perimeter':
            if str(item.get('id')) != str(perimeter.pk):
                return Response({'detail': 'Committed perimeter does not match its assessment.'}, status=409)
        elif kind not in ('ComplianceAssessment', 'RiskAssessment'):
            return Response({'detail': 'Unexpected committed record type.'}, status=409)

    return Response({
        'business_records_written': True,
        'replay': True,
        'new_business_records_written': False,
        'created_objects': created,
        'requirement_assessments_count': RequirementAssessment.objects.filter(
            compliance_assessment_id=case.pk,
        ).count(),
        'workflow': workflow_status(user, engagement),
        'note': 'The earlier approved case was already saved. No additional GRC records were created by this retry.',
    })


class WorkflowCommitView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = ApproveInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        if values['confirm_reviewed'] is not True:
            return Response({'detail': 'Explicit final confirmation is required.'}, status=400)
        if getattr(settings, 'SICO_CASE_SETUP_COMMITS_ENABLED', False) is not True:
            return Response({'detail': 'Case setup writes are disabled until separately validated.'}, status=403)
        try:
            engagement = authorized_engagement(request.user, values['engagement_id'])
            verify_principal(request.user, engagement.folder_id)
            with transaction.atomic():
                engagement = authorized_engagement(request.user, values['engagement_id'], lock=True)
                existing = EngagementExecution.objects.select_for_update().filter(
                    engagement=engagement, stage=STAGE, batch_key=BATCH,
                ).first()
                if existing is not None and existing.status == EngagementExecution.Status.COMMITTED:
                    return _committed_case_replay(
                        request.user, engagement, existing, values['prepared_digest'],
                    )
                receipt = get_prepared_receipt(request.user, engagement.pk, STAGE, BATCH, lock=True)
                review = verified_review_snapshot(receipt)
                if not hmac.compare_digest(receipt.prepared_digest, values['prepared_digest']):
                    return Response({'detail': 'The prepared operation changed; review again.'}, status=409)
                if receipt.approved_by_id != str(request.user.pk):
                    return Response({'detail': 'Independent server-recorded approval is required.'}, status=403)
                payload = copy.deepcopy(review['operation_payload'])
                payload['dry_run'] = False
                payload['approved_by_user'] = True
                payload['framework_resolution']['user_confirmed'] = True
                for key in ('folder_domain_decision', 'perimeter_decision',
                            'compliance_assessment_decision', 'risk_assessment_decision'):
                    payload[key]['human_approved'] = True
                result = execute_stage(
                    request, engagement.pk, stage=STAGE, batch_key=BATCH,
                    mode='commit', payload=payload, explicitly_approved=True,
                    trusted_case_setup_workflow=True,
                )
                created = result['result'].get('created_objects', [])
                compliance_ids = [r['id'] for r in created if r.get('platform_entity') == 'ComplianceAssessment']
                risk_ids = [r['id'] for r in created if r.get('platform_entity') == 'RiskAssessment']
                if len(compliance_ids) != 1 or len(risk_ids) > 1:
                    raise EngagementBlocked('Original service did not confirm the intended assessment records.', http_status=422)
                case = ComplianceAssessment.objects.filter(
                    pk=compliance_ids[0], folder_id=engagement.folder_id,
                    framework_id=engagement.framework_id,
                ).first()
                if case is None or not readable(request.user, ComplianceAssessment, case.pk):
                    raise EngagementBlocked('Created assessment could not be independently verified.', http_status=422)
                if risk_ids:
                    risk = RiskAssessment.objects.filter(pk=risk_ids[0], folder_id=engagement.folder_id).first()
                    if risk is None or not readable(request.user, RiskAssessment, risk.pk):
                        raise EngagementBlocked('Created risk assessment could not be independently verified.', http_status=422)
                    engagement.risk_assessment_id = risk.pk
                engagement.compliance_assessment_id = case.pk
                engagement.save(update_fields=['compliance_assessment_id', 'risk_assessment_id', 'updated_at'])
                requirement_count = RequirementAssessment.objects.filter(
                    compliance_assessment_id=case.pk,
                ).count()
                # If post-write authorization or status verification fails, rollback
                # the business records AND the SICO receipt in the same transaction.
                progress = workflow_status(request.user, engagement)
        except Exception as exc:
            response = business_error(exc)
            if response is not None:
                return response
            raise
        result_data = {'business_records_written': True, 'created_objects': created,
                       'requirement_assessments_count': requirement_count,
                       'workflow': progress,
                       'note': 'Initial GRC records saved and verified; requirement results, controls, findings, evidence and compliance outcomes remain unassessed.'}
        if isinstance(engagement.plan, dict) and engagement.plan.get('version') == 'sico-multi-module-lifecycle-v1':
            # Refresh the same 16-activity record immediately after the approved
            # transaction so users do not need to type an internal UUID.
            from .sico_ai_lifecycle_views import _summary
            result_data['lifecycle'] = _summary(request.user, engagement)
        return Response(result_data)


class WorkflowResumeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = ReviewInput(data=request.data)
        form.is_valid(raise_exception=True)
        engagement = authorized_engagement(request.user, form.validated_data['engagement_id'])
        verify_principal(request.user, engagement.folder_id)
        return Response(workflow_status(request.user, engagement))
