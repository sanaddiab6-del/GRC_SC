"""SICO AI operation hub for ALL source-reviewed engagement services.

This is a reusable coordinator -> existing GRC service bridge, not a new GRC
writer. Never execute an arbitrary URL, import path, or model-suggested method.
Only STAGES_BY_NAME can be dispatched. The rest of the platform is discovered
separately and remains unavailable for AI execution until reviewed.

Safety: no GRC commit by default; a commit needs two independent feature flags,
server-recorded approval for the exact prepared digest, current RBAC, and an
existing verified platform service. The original service owns final permissions.
"""
from __future__ import annotations

import copy
import hmac
import re

from django.conf import settings
from django.db import transaction
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .engagement_approval_views import get_prepared_receipt, verified_review_snapshot
from .engagement_rules import STAGES, STAGES_BY_NAME, reviewed_payload_digest
from .engagement_service import EngagementBlocked, execute_stage

BATCH_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,80}$')


class HubOperationInput(serializers.Serializer):
    engagement_id = serializers.UUIDField()
    stage = serializers.ChoiceField(choices=tuple(STAGES_BY_NAME))
    batch_key = serializers.RegexField(regex=BATCH_PATTERN)
    operation_payload = serializers.JSONField()

    def validate_operation_payload(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('The prepared operation must be an object.')
        if value.get('dry_run') is not True:
            raise serializers.ValidationError('Only dry-run preparation is accepted.')
        return value


class HubCommitInput(serializers.Serializer):
    engagement_id = serializers.UUIDField()
    stage = serializers.ChoiceField(choices=tuple(STAGES_BY_NAME))
    batch_key = serializers.RegexField(regex=BATCH_PATTERN)
    prepared_digest = serializers.RegexField(regex=r'^[a-f0-9]{64}$')
    confirm_commit = serializers.BooleanField()

    def validate_confirm_commit(self, value):
        if value is not True:
            raise serializers.ValidationError('A separate human confirmation is required.')
        return value


def _enabled_for_commit(stage):
    if not getattr(settings, 'SICO_ENGAGEMENT_COMMITS_ENABLED', False):
        return False
    enabled = getattr(settings, 'SICO_AI_EXECUTION_STAGE_ALLOWLIST', ())
    # Deliberately disallow a loose env-var string and arbitrary iterables.
    if not isinstance(enabled, (tuple, list, frozenset, set)):
        return False
    # Case setup has a separate, more constrained path; never bypass it here.
    return stage != 'case_setup' and stage in enabled


def _approved_operation_payload(prepared):
    """Change ONLY review flags in a server-stored exact verified snapshot.

    Never add new fields, change IDs, decide actions, or create data from AI text.
    The actual serializer still validates the exact payload as commit mode.
    """
    value = copy.deepcopy(prepared)
    if not isinstance(value, dict) or value.get('dry_run') is not True:
        raise EngagementBlocked('Invalid prepared operation.', http_status=409)

    def set_existing_review_flags(obj):
        if isinstance(obj, dict):
            for key, child in obj.items():
                if key in {'human_approved', 'approved_by_user', 'approved'}:
                    # Do not silently authorize an approval-valued string.
                    if type(child) is not bool:
                        raise EngagementBlocked('Invalid review flag.', http_status=409)
                    obj[key] = True
                elif isinstance(child, (dict, list)):
                    set_existing_review_flags(child)
        elif isinstance(obj, list):
            for child in obj:
                if isinstance(child, (dict, list)):
                    set_existing_review_flags(child)

    set_existing_review_flags(value)
    value['dry_run'] = False
    # These are the pre-existing review flag fields accepted by the registry.
    value['approved_by_user'] = True
    return value


class SicoAiToolCatalogView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        # A catalog, not a claim that the user may write to every listed GRC object.
        from .sico_ai_agent_tools import GrcReadRegistry
        try:
            read_tools = GrcReadRegistry(request.user).catalog()
        except Exception:
            read_tools = []  # Fail closed; never imply unverified read authority.
        return Response({
            'catalog_kind': 'reviewed_engagement_services',
            'reviewed_count': len(STAGES),
            'tools': [
                {
                    'stage': stage.slug,
                    'source_serializer': stage.serializer,
                    'source_service': stage.service,
                    'can_prepare': True,
                    'can_commit': _enabled_for_commit(stage.slug),
                    'permission': 'checked again for the exact operation and target record',
                }
                for stage in STAGES
            ],
            'platform_wide_discovery': (
                'Additional platform API functions require source review before AI dispatch; '
                'this registry never implies full-platform execution coverage.'
            ),
            'grc_records_changed': False,
            'agent_read_tools': read_tools,
            'agent_execution_endpoint': 'workforce/assistant/execute/',
        })


class SicoAiToolPrepareView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = HubOperationInput(data=request.data)
        form.is_valid(raise_exception=True)
        data = form.validated_data
        try:
            receipt = execute_stage(
                request, data['engagement_id'], stage=data['stage'],
                batch_key=data['batch_key'], mode='dry_run',
                payload=data['operation_payload'], explicitly_approved=False,
            )
        except EngagementBlocked as exc:
            return Response({'detail': str(exc)}, status=exc.http_status)
        if not isinstance(receipt, dict):
            return Response({'detail': 'Unexpected dry-run response.'}, status=422)
        result = receipt.get('result')
        review = result.get('_sico_review') if isinstance(result, dict) else None
        if not isinstance(review, dict) or not review.get('prepared_digest'):
            return Response({'detail': 'A verified review snapshot was not produced.'}, status=422)
        return Response({
            'engagement_id': str(data['engagement_id']),
            'stage': data['stage'], 'batch_key': data['batch_key'],
            'prepared_digest': review['prepared_digest'],
            'review': review,
            'dry_run_result': result,
            'grc_records_changed': False,
            'next_step': 'Human must review and approve through the existing approval endpoint.',
        })


class SicoAiToolCommitView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = HubCommitInput(data=request.data)
        form.is_valid(raise_exception=True)
        data = form.validated_data
        stage = data['stage']
        if not _enabled_for_commit(stage):
            return Response({
                'detail': 'This GRC tool is not enabled for approved commits.',
            }, status=status.HTTP_403_FORBIDDEN)
        try:
            # One transaction covers verification, application and existing receipt.
            with transaction.atomic():
                receipt = get_prepared_receipt(
                    request.user, data['engagement_id'], stage,
                    data['batch_key'], lock=True,
                )
                review = verified_review_snapshot(receipt)
                if receipt.approved_by_id != str(request.user.pk):
                    return Response({'detail': 'Independent human approval is missing.'}, status=403)
                if not hmac.compare_digest(receipt.prepared_digest, data['prepared_digest']):
                    return Response({'detail': 'Prepared operation changed. Review again.'}, status=409)
                # Server-side reconstruction: the caller cannot change payload IDs
                # or fields after reviewing the exact persisted snapshot.
                payload = _approved_operation_payload(review['operation_payload'])
                if not hmac.compare_digest(
                    reviewed_payload_digest(payload), receipt.prepared_digest
                ):
                    return Response({'detail': 'Commit payload differs from review.'}, status=409)
                outcome = execute_stage(
                    request, data['engagement_id'], stage=stage,
                    batch_key=data['batch_key'], mode='commit',
                    payload=payload, explicitly_approved=True,
                )
        except EngagementBlocked as exc:
            return Response({'detail': str(exc)}, status=exc.http_status)
        return Response({
            'engagement_id': str(data['engagement_id']),
            'stage': stage,
            'batch_key': data['batch_key'],
            'result': outcome,
            'grc_commit_recorded': True,
            'note': 'Original GRC service result. Verify target records and linked data.',
        })
