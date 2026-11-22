"""Independent human review of prepared SICO AI operations.

Approval is stored on the server, not inferred from AI-supplied flags.
GRC commits remain disabled until approval enforcement is tested.
"""
from __future__ import annotations

import hmac
import re

from django.db import transaction
from django.http import Http404
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .engagement_rules import STAGES_BY_NAME, reviewed_payload_digest
from .engagement_service import authorized_engagement, _result_is_blocked
from .models import EngagementExecution


class ApprovalLookupInput(serializers.Serializer):
    stage = serializers.ChoiceField(choices=list(STAGES_BY_NAME))
    batch_key = serializers.RegexField(
        regex=re.compile(r"^[a-zA-Z0-9_-]{1,80}$")
    )


class ApprovalDecisionInput(ApprovalLookupInput):
    prepared_digest = serializers.RegexField(
        regex=re.compile(r"^[a-f0-9]{64}$")
    )
    confirm_reviewed = serializers.BooleanField(required=True)


def verified_review_snapshot(receipt):
    """Reject missing, altered, or incorrectly scoped review snapshots."""
    result = receipt.prepared_result
    review = result.get("_sico_review") if isinstance(result, dict) else None

    if not isinstance(review, dict) or not isinstance(
        review.get("operation_payload"), dict
    ):
        raise Http404("Verified operation preview is required.")

    expected = {
        "engagement_id": str(receipt.engagement_id),
        "folder_id": str(receipt.engagement.folder_id),
        "stage": receipt.stage,
        "batch_key": receipt.batch_key,
        "prepared_digest": receipt.prepared_digest,
    }

    if any(review.get(key) != value for key, value in expected.items()):
        raise Http404("Operation preview does not match its receipt.")

    try:
        actual_digest = reviewed_payload_digest(
            review["operation_payload"]
        )
    except (TypeError, ValueError):
        raise Http404("Invalid operation preview.") from None

    if not hmac.compare_digest(actual_digest, receipt.prepared_digest):
        raise Http404("Operation preview fingerprint mismatch.")

    return review


def get_prepared_receipt(user, engagement_id, stage, batch_key, lock=False):
    engagement = authorized_engagement(user, engagement_id, lock=lock)

    qs = EngagementExecution.objects.filter(
        engagement=engagement,
        stage=stage,
        batch_key=batch_key,
        status=EngagementExecution.Status.PREPARED,
    )

    if lock:
        qs = qs.select_for_update()

    receipt = qs.first()

    if (
        receipt is None
        or not receipt.prepared_digest
        or _result_is_blocked(receipt.prepared_result, "dry_run")
    ):
        raise Http404("Prepared operation not available.")

    verified_review_snapshot(receipt)
    return receipt


class AiEngagementApprovalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, engagement_id, format=None):
        form = ApprovalLookupInput(data=request.query_params)
        form.is_valid(raise_exception=True)
        values = form.validated_data

        receipt = get_prepared_receipt(
            request.user,
            engagement_id,
            values["stage"],
            values["batch_key"],
        )

        return Response({
            "stage": receipt.stage,
            "batch_key": receipt.batch_key,
            "prepared_digest": receipt.prepared_digest,
            "prepared_result": receipt.prepared_result,
            "review": verified_review_snapshot(receipt),
            "approved": bool(receipt.approved_by_id),
        })

    def post(self, request, engagement_id, format=None):
        form = ApprovalDecisionInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data

        if values["confirm_reviewed"] is not True:
            return Response(
                {"detail": "Explicit human review is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            receipt = get_prepared_receipt(
                request.user,
                engagement_id,
                values["stage"],
                values["batch_key"],
                lock=True,
            )

            if not hmac.compare_digest(
                receipt.prepared_digest,
                values["prepared_digest"],
            ):
                return Response(
                    {"detail": "Prepared operation has changed. Review again."},
                    status=status.HTTP_409_CONFLICT,
                )

            receipt.approved_by_id = str(request.user.pk)
            receipt.save(update_fields=["approved_by_id", "updated_at"])

        return Response({
            "approved": True,
            "stage": values["stage"],
            "batch_key": values["batch_key"],
            "prepared_digest": values["prepared_digest"],
        })
