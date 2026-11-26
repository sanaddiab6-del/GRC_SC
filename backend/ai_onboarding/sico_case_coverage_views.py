"""Read-only, permission-checked API adapter for the SICO AI coverage engine."""
from __future__ import annotations

from django.http import Http404
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .sico_ai_framework_batch_v3 import _load_authorized_requirements, _page_and_digest
from .sico_case_coverage import make_coverage_plan


class SicoCoveragePlanInput(serializers.Serializer):
    organization_name = serializers.CharField(min_length=2, max_length=150)
    framework_name = serializers.CharField(min_length=2, max_length=150)
    problem = serializers.CharField(min_length=20, max_length=4000, trim_whitespace=False)
    source_digest = serializers.RegexField(regex=r'^[0-9a-f]{64}$')


def _authorized_scaffold_context(user, *, organization, framework_name, meta, digest, objective=''):
    """Bind unsaved work to a principal/case; names never authorize DB access."""
    import json
    from django.utils.crypto import salted_hmac
    from .sico_ai_lifecycle_views import _framework_candidates, _scope_candidates
    from .sico_ai_workflow_views import verify_principal

    if not getattr(user, 'is_authenticated', False) or not user.is_active or not getattr(user, 'pk', None):
        return None
    frameworks = _framework_candidates(user, framework_name)
    if len(frameworks) != 1 or str(frameworks[0].pk) != meta['framework_id']:
        return None
    framework = frameworks[0]
    reference = framework.urn or framework.ref_id
    version = getattr(framework.library, 'version', None)
    if not (framework.name and reference and type(version) is int):
        return None
    binding = json.dumps([str(user.pk), organization.strip().casefold(), str(framework.pk),
                          digest, objective.strip()], separators=(',', ':'))
    scope_id = 'draft-case:' + salted_hmac('sico.draft-only-case.v1', binding, algorithm='sha256').hexdigest()
    context = {
        'organization_name': organization.strip(), 'framework_id': str(framework.pk),
        'framework_name': framework.name, 'framework_reference': reference,
        'library_version': version, 'source_digest': digest,
        'draft_case_scope_id': scope_id, 'scope_kind': 'draft_only_case',
    }
    # This lookup returns only IAM-visible candidates. A name match alone
    # never supplies authorization or triggers asset/evidence/catalog reads.
    organizations = _scope_candidates(user, organization)
    if len(organizations) == 1:
        domain = organizations[0]
        try:
            verify_principal(user, domain.pk)
        except Http404:
            return None
        context.update(organization_id=str(domain.pk), organization_name=domain.name,
                       scope_kind='authorized_existing_organization')
    return context


class SicoCaseCoveragePlanView(APIView):
    """Return 1 unassessed, source-grounded work item / authorized requirement.

    New organization names receive an authenticated, non-persisted case scope.
    Existing domains are bound only after the original membership checks.
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = SicoCoveragePlanInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        if not request.user.is_active:
            return Response({'detail': 'Account inactive.', 'business_records_written': False}, status=403)
        if any(field in request.data for field in ('tenant_id', 'organization_id', 'folder_id',
                                                    'selected_organization_id', 'draft_case_scope_id')):
            return Response({'detail': 'Organization scope must be resolved by SICO.',
                             'business_records_written': False}, status=403)
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
            authorized_context = _authorized_scaffold_context(
                request.user, organization=values['organization_name'],
                framework_name=values['framework_name'], meta=meta, digest=digest, objective=values['problem'],
            )
            if authorized_context is None:
                return Response({'detail': 'Case scope could not be authorized.', 'business_records_written': False}, status=403)
            plan = make_coverage_plan(
                organization=values['organization_name'],
                framework=values['framework_name'],
                objective=values['problem'],
                framework_id=meta['framework_id'], source_digest=digest,
                authorized_requirements=rows,
                authorized_case_context=authorized_context,
            )
        except ValueError:
            # Don't echo source data or internal permission state.
            return Response({'detail': 'Framework coverage cannot be prepared from this source.',
                             'business_records_written': False}, status=422)
        plan['organization_context_status'] = authorized_context['scope_kind']
        plan['draft_case_scope_id'] = authorized_context['draft_case_scope_id']
        for task in plan['generation_queue']:
            task['draft_case_scope_id'] = authorized_context['draft_case_scope_id']
            task['case_scope_kind'] = authorized_context['scope_kind']
        plan['risk_matrix_status'] = 'requires_authorized_risk_assessment_selection'
        plan['full_framework_assessed'] = False
        return Response(plan)
