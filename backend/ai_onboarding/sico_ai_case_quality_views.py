"""Authenticated single-record SICO quality drafting, read-only GRC business data.

Reuses the real Qwen quality-gated generator from the offline HTML runner.
Every request rechecks SICO framework RBAC and the exact source snapshot.
Client-provided prior drafts are only untrusted context; no saved IDs or business
record writers are accepted or invoked.
"""
from __future__ import annotations

import re
from rest_framework import permissions, serializers
from jsonschema import ValidationError as JsonSchemaError
from rest_framework.response import Response
from rest_framework.views import APIView

from .llm_config import CAPABILITY_GRC_CAPABILITY_SELECTION, resolve_advisory_capability_config
from .llm_provider import get_advisory_provider_selection
from .llm_errors import AiProviderError
from .sico_ai_case_draft_views import DRAFT_ACTIVITIES
from .sico_ai_framework_batch_v3 import _load_authorized_requirements, _page_and_digest
from .quality_sico_drafts_v5 import generate_quality_draft

# Accept an intentionally small amount of untrusted case context. All drafts
# are unsaved client-side objects and cannot grant access to SICO records.
DRAFT_REF = re.compile(r'^draft-(?:0[1-9]|1[0-6])-(?:0[1-9]|1[0-2])$')
MAX_CONTEXT = 45

class PreviousDraft(serializers.Serializer):
    draft_reference = serializers.CharField(max_length=12)
    title = serializers.CharField(min_length=5, max_length=110)
    record_type = serializers.CharField(max_length=90)
    content = serializers.CharField(required=False, allow_blank=True, max_length=670)

    def validate_draft_reference(self, value):
        if not DRAFT_REF.fullmatch(value):
            raise serializers.ValidationError('Invalid draft reference.')
        return value

class QualityDraftInput(serializers.Serializer):
    organization_name = serializers.CharField(min_length=2, max_length=150)
    framework_name = serializers.CharField(min_length=2, max_length=150)
    problem = serializers.CharField(min_length=20, max_length=4000)
    activity_number = serializers.IntegerField(min_value=1, max_value=16)
    draft_index = serializers.IntegerField(min_value=1, max_value=12)
    source_digest = serializers.RegexField(regex=r'^[0-9a-f]{64}$')
    requirement_reference = serializers.CharField(required=False, allow_blank=True, max_length=100)
    previous_drafts = PreviousDraft(many=True, required=False)
    focus_attempt = serializers.IntegerField(required=False, min_value=0, max_value=30, default=0)

    def validate_previous_drafts(self, rows):
        if len(rows) > MAX_CONTEXT:
            raise serializers.ValidationError('Too many previous draft records.')
        ids = [row['draft_reference'] for row in rows]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError('Duplicate context references.')
        for row in rows:
            step = int(row['draft_reference'][6:8])
            if row['record_type'] != DRAFT_ACTIVITIES[step-1][2]:
                raise serializers.ValidationError('Previous record type does not match its activity.')
        return rows

    def validate(self, values):
        step = values['activity_number']
        index = values['draft_index']
        if any(row['draft_reference'] == f'draft-{step:02d}-{index:02d}' for row in values.get('previous_drafts', [])):
            raise serializers.ValidationError('This draft already exists in the checkpoint.')
        if values.get('requirement_reference') and step != 10:
            raise serializers.ValidationError('Requirement selection is only for requirement reviews.')
        return values

# Full framework coverage is tracked independently. A selected record is only
# an authorized requirement, not a compliance verdict.
class SicoQualityDraftOneView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        form = QualityDraftInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        if not request.user.is_active:
            return Response({'detail': 'Account inactive.'}, status=403)
        meta, stream = _load_authorized_requirements(request.user, values['framework_name'])
        if meta.get('status') != 'matched':
            return Response({'detail': 'The exact framework is unavailable to this user.',
                             'business_records_written': False}, status=403)
        # Materialize only readable rows from the existing RBAC-filtered query.
        # Source is hashed again on EVERY call, including resumed calls.
        _, count, digest = _page_and_digest(stream, start=0, batch_size=0)
        # Re-read through the original authorization gate; do not truncate large
        # framework catalogs at an arbitrary number of requirements.
        meta_again, full_stream = _load_authorized_requirements(request.user, values['framework_name'])
        if meta_again.get('status') != 'matched' or meta_again.get('framework_id') != meta['framework_id']:
            return Response({'detail': 'Framework access changed. Reload requirements.', 'business_records_written': False}, status=409)
        rows, count_again, digest_again = _page_and_digest(full_stream, start=0, batch_size=count)
        if digest != values['source_digest'] or not rows or count != count_again or digest != digest_again:
            return Response({'detail': 'The authorized framework source changed or is incomplete. Reload requirements.',
                             'business_records_written': False}, status=409)
        step = values['activity_number']; index = values['draft_index']
        code, _, model, _, dependencies, _ = DRAFT_ACTIVITIES[step-1]
        chosen = None
        if step == 10:
            ref = values.get('requirement_reference', '')
            chosen = next((r for r in rows if r.get('reference') == ref), None)
            if not chosen:
                return Response({'detail': 'Select an exact authorized framework requirement.',
                                 'business_records_written': False}, status=400)
        prior = []
        context = []
        for row in values.get('previous_drafts', []):
            item = dict(row)
            ref = item['draft_reference']
            position = int(ref[6:8])
            if position == step:
                prior.append(item)
            if position in dependencies:
                context.append(item)
        # The generator checks category contracts, uniqueness and draft links;
        # saved SICO functions remain uncalled until a separate future approval.
        try:
            config = resolve_advisory_capability_config(CAPABILITY_GRC_CAPABILITY_SELECTION)
            selection = get_advisory_provider_selection(config)
            result = generate_quality_draft(
                selection, organization=values['organization_name'],
                framework=values['framework_name'], objective=values['problem'],
                phase=step-1, draft_index=index, prior_drafts=prior,
                case_context=context, authorized_requirements=rows,
                chosen_requirement=chosen,
                focus_attempt=values['focus_attempt'],
            )
        except (AiProviderError, JsonSchemaError, ValueError, TimeoutError, TypeError, KeyError) as exc:
            # No secret provider URLs or sensitive prompts in the response.
            reason = str(exc)[:80] if isinstance(exc, ValueError) else 'model_or_provider_error'
            return Response({'detail': 'One Qwen draft was rejected; previous drafts are retained.',
                             'failure_reason': reason, 'business_records_written': False}, status=503)
        result.update({
            'framework_id': meta['framework_id'],
            'source_digest': digest,
            'authorized_requirement_count': count,
            'source_grounding': 'read_from_SICO_with_request_user_permissions',
            'framework_edition_independently_verified': False,
            'full_framework_assessed': False,
            'provenance': 'qwen_quality_single_authenticated_v7',
        })
        return Response(result)
