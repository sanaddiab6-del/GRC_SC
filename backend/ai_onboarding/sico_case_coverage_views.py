"""Read-only, permission-checked API adapter for the SICO AI coverage engine.

IMPORTANT: This module is additive and is NOT activated until the current
ai_onboarding/urls.py is explicitly updated and verified. No ORM writers.
"""
from __future__ import annotations

from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .sico_ai_framework_batch_v3 import _load_authorized_requirements, _page_and_digest
from .sico_case_coverage import make_coverage_plan


class SicoCoveragePlanInput(serializers.Serializer):
    organization_name = serializers.CharField(min_length=2, max_length=150)
    framework_name = serializers.CharField(min_length=2, max_length=150)
    problem = serializers.CharField(min_length=20, max_length=4000)
    source_digest = serializers.RegexField(regex=r'^[0-9a-f]{64}$')


class SicoCaseCoveragePlanView(APIView):
    """Return 1 unassessed, source-grounded work item / authorized requirement.

    The organization name is an unverified planning label; this view does NOT
    read organizational evidence, policies or risk matrices from a name. Those
    require a separately resolved tenant-authorized assessment/perimeter.
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = SicoCoveragePlanInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        if not request.user.is_active:
            return Response({'detail': 'Account inactive.', 'business_records_written': False}, status=403)
        meta, stream = _load_authorized_requirements(request.user, values['framework_name'])
        if meta.get('status') != 'matched':
            return Response({'detail': 'Framework unavailable to this user.',
                             'business_records_written': False}, status=403)
        # Match the existing quality-one endpoint's digest recheck: a client
        # source export cannot grant access or silently choose a new edition.
        _, count, digest = _page_and_digest(stream, start=0, batch_size=0)
        meta_again, stream_again = _load_authorized_requirements(request.user, values['framework_name'])
        if (meta_again.get('status') != 'matched' or
                meta_again.get('framework_id') != meta.get('framework_id')):
            return Response({'detail': 'Framework access changed; reload source.',
                             'business_records_written': False}, status=409)
        rows, count_again, digest_again = _page_and_digest(stream_again, start=0, batch_size=count)
        if (digest != values['source_digest'] or not rows or
                count != count_again or digest != digest_again):
            return Response({'detail': 'Authorized framework source changed or is incomplete.',
                             'business_records_written': False}, status=409)
        try:
            plan = make_coverage_plan(
                organization=values['organization_name'],
                framework=values['framework_name'],
                objective=values['problem'],
                framework_id=meta['framework_id'], source_digest=digest,
                authorized_requirements=rows,
            )
        except ValueError:
            # Don't echo source data or internal permission state.
            return Response({'detail': 'Framework coverage cannot be prepared from this source.',
                             'business_records_written': False}, status=422)
        plan['organization_context_status'] = 'not_resolved_from_name_only'
        plan['risk_matrix_status'] = 'requires_authorized_risk_assessment_selection'
        plan['full_framework_assessed'] = False
        return Response(plan)
