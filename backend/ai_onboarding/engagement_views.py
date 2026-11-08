"""Authenticated SICO multi-module engagement endpoints.

These are intentionally separate from /onboarding/*: the existing endpoints stay
unchanged and continue to work for manual users.
"""
from __future__ import annotations

import re
from django.http import Http404
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .engagement_rules import STAGES_BY_NAME
from .engagement_service import (
    EngagementBlocked, authorized_engagement, create_engagement,
    execute_stage, summary,
)
from .models import Engagement


class EngagementResumeInput(serializers.Serializer):
    engagement_id = serializers.UUIDField(required=False, allow_null=True)


class AiEngagementResumeView(APIView):
    """Read-only POST endpoint for the existing authenticated SvelteKit proxy.

    No new GRC record is created and no engagement contents are disclosed before
    the same creator-and-current-folder authorization as the ordinary detail API.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        form = EngagementResumeInput(data=request.data)
        form.is_valid(raise_exception=True)
        engagement_id = form.validated_data.get('engagement_id')
        if engagement_id:
            return Response({'engagement': summary(request.user, engagement_id)})
        matches = []
        for item in Engagement.objects.filter(created_by_id=str(request.user.pk)).order_by('-created_at')[:60]:
            try:
                authorized_engagement(request.user, item.pk)
            except Http404:
                continue
            matches.append({'id': str(item.pk), 'title': item.title,
                            'status': item.status, 'folder_id': str(item.folder_id)})
            if len(matches) >= 25:
                break
        return Response({'engagements': matches})


class EngagementCreateInput(serializers.Serializer):
    folder_id = serializers.UUIDField()
    title = serializers.CharField(min_length=4, max_length=200)
    objective = serializers.CharField(min_length=20, max_length=4000)
    framework_id = serializers.UUIDField(required=False, allow_null=True)
    compliance_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    risk_assessment_id = serializers.UUIDField(required=False, allow_null=True)


class EngagementOperationInput(serializers.Serializer):
    stage = serializers.ChoiceField(choices=list(STAGES_BY_NAME))
    batch_key = serializers.RegexField(regex=re.compile(r'^[a-zA-Z0-9_-]{1,80}$'), default='default')
    mode = serializers.ChoiceField(choices=['dry_run', 'commit'])
    explicitly_approved = serializers.BooleanField(default=False)
    operation_payload = serializers.JSONField()

    def validate(self, attrs):
        if not isinstance(attrs['operation_payload'], dict):
            raise serializers.ValidationError({'operation_payload': 'A JSON object is required.'})
        if attrs['mode'] == 'dry_run' and attrs['explicitly_approved']:
            raise serializers.ValidationError({'explicitly_approved': 'Dry-runs cannot be approved writes.'})
        if attrs['mode'] == 'commit' and not attrs['explicitly_approved']:
            raise serializers.ValidationError({'explicitly_approved': 'Human approval required.'})
        return attrs


class AiEngagementListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        rows = []
        for item in Engagement.objects.filter(created_by_id=str(request.user.pk)).order_by('-created_at')[:60]:
            try:
                authorized_engagement(request.user, item.pk)
            except Http404:
                continue
            rows.append({
                'id': str(item.pk), 'title': item.title, 'status': item.status,
                'folder_id': str(item.folder_id),
            })
            if len(rows) >= 25:
                break
        return Response({'engagements': rows})

    def post(self, request, format=None):
        form = EngagementCreateInput(data=request.data)
        form.is_valid(raise_exception=True)
        engagement = create_engagement(request.user, **form.validated_data)
        return Response(summary(request.user, engagement.pk), status=status.HTTP_201_CREATED)


class AiEngagementDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, engagement_id, format=None):
        return Response(summary(request.user, engagement_id))


class AiEngagementOperationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, engagement_id, format=None):
        form = EngagementOperationInput(data=request.data)
        form.is_valid(raise_exception=True)
        args = form.validated_data

        # SICO AI engagement commits require independent, server-recorded
        # human authorization. Caller-supplied approval flags are not proof.
        # Keep preparation available while that workflow is implemented.
        if args['mode'] == 'commit':
            return Response(
                {
                    'detail': (
                        'SICO AI engagement commits are disabled until '
                        'independent human approval is implemented.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            result = execute_stage(
                request, engagement_id, stage=args['stage'], batch_key=args['batch_key'],
                mode=args['mode'], payload=args['operation_payload'],
                explicitly_approved=args['explicitly_approved'],
            )
        except EngagementBlocked as exc:
            return Response({'detail': str(exc)}, status=exc.http_status)
        except Exception as exc:
            # Delegate the original service's structured validation errors
            # unchanged. Never invent an exception response contract.
            if hasattr(exc, 'to_response') and hasattr(exc, 'status_code'):
                return Response(exc.to_response(), status=exc.status_code)
            raise
        return Response(result)

class EngagementPlanInput(serializers.Serializer):
    use_local_ai = serializers.BooleanField(default=False)


class AiEngagementPlanView(APIView):
    """Prepare a real-record work plan; does not create/alter GRC business records."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, engagement_id, format=None):
        form = EngagementPlanInput(data=request.data)
        form.is_valid(raise_exception=True)
        from .engagement_plan import prepare_engagement_plan
        result = prepare_engagement_plan(
            request, engagement_id,
            use_local_ai=form.validated_data['use_local_ai'],
        )
        return Response(result)
