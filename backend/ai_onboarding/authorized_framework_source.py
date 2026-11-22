"""Read-only SICO framework requirement catalog, using existing RBAC and signed cursors.

A source snapshot is not an ISO edition certification or a compliance assessment.
Never allow a caller to supply RequirementNode IDs to bypass the SICO RBAC query.
"""
from __future__ import annotations

from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .sico_ai_framework_batch_v3 import (
    FrameworkBatchError,
    _decode_cursor,
    _fingerprint,
    _load_authorized_requirements,
    _make_cursor,
    _page_and_digest,
    _signer,
)


class AuthorizedSourceInput(serializers.Serializer):
    framework_name = serializers.CharField(min_length=2, max_length=150, trim_whitespace=True)
    page_size = serializers.IntegerField(min_value=1, max_value=25, default=20)
    cursor = serializers.CharField(required=False, allow_blank=True, max_length=2048)


def read_authorized_source_page(*, user, framework_name, page_size=20, cursor='', signer=None):
    """Return source rows read from the existing authorized SICO queryset, never guessed IDs.

    Cursor remains bound to the user, exact framework, request and source digest.
    Source change or permission change invalidates the cursor.
    """
    if not getattr(user, 'is_active', False) or not getattr(user, 'is_authenticated', False):
        raise FrameworkBatchError('not_authenticated_or_inactive')
    if type(page_size) is not int or not 1 <= page_size <= 25:
        raise FrameworkBatchError('invalid_page_size')
    meta, rows = _load_authorized_requirements(user, framework_name)
    if meta['status'] != 'matched':
        if cursor:
            raise FrameworkBatchError('invalid_or_stale_cursor')
        return {
            'status': meta['status'],
            'candidates': meta.get('candidates', []),
            'requirements': [], 'next_cursor': None,
            'coverage': {'accessible_total': 0, 'exported_through': 0,
                         'complete': False},
            'business_records_written': False,
        }

    framework_id = meta['framework_id']
    _, total, digest = _page_and_digest(rows, start=0, batch_size=0)
    identity = _fingerprint(['sico-authorized-framework-source-v1', framework_name.strip()])
    signer = signer or _signer()
    start = _decode_cursor(cursor, signer=signer,
                           identity=identity, user_id=str(user.pk),
                           framework_id=framework_id, digest=digest, total=total) if cursor else 0
    meta_again, permitted_again = _load_authorized_requirements(user, framework_name)
    if meta_again.get('status') != 'matched' or meta_again['framework_id'] != framework_id:
        raise FrameworkBatchError('permission_or_library_changed')
    page, second_total, second_digest = _page_and_digest(
        permitted_again, start=start, batch_size=page_size)
    if total != second_total or digest != second_digest:
        raise FrameworkBatchError('permission_or_library_changed')

    offset = start + len(page)
    complete = offset == total
    return {
        'status': 'complete' if complete else 'partial',
        'matched_framework': meta['matched_framework'],
        'framework_id': framework_id,
        'requirements': page,
        'next_cursor': None if complete else _make_cursor(
            signer=signer, identity=identity, user_id=str(user.pk),
            framework_id=framework_id, digest=digest, offset=offset),
        'coverage': {'accessible_total': total, 'exported_through': offset,
                     'complete': complete},
        'source_digest': digest,
        'framework_edition_independently_verified': False,
        'compliance_verdict': 'not_established',
        'business_records_written': False,
    }


class AuthorizedFrameworkSourcePageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options']

    def post(self, request, format=None):
        incoming = AuthorizedSourceInput(data=request.data)
        incoming.is_valid(raise_exception=True)
        try:
            result = read_authorized_source_page(
                user=request.user, **incoming.validated_data)
        except FrameworkBatchError as exc:
            return Response({'detail': 'Authorized framework source is unavailable or changed.',
                             'error_kind': exc.reason, 'business_records_written': False},
                            status=409)
        return Response(result)
