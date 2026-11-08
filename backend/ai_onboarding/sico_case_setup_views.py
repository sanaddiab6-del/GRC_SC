"""Authenticated, dry-run-only SICO case setup endpoint."""

import re

from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .engagement_service import EngagementBlocked
from .sico_case_setup_adapter import (
    SicoCaseSetupPreparationError,
    prepare_ai_case_setup,
)


class StrictPreparationInput(serializers.Serializer):
    batch_key = serializers.RegexField(
        regex=re.compile(r"^[A-Za-z0-9_-]{1,80}$")
    )
    proposed_payload = serializers.JSONField()

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                "A JSON object is required."
            )
        unexpected = set(data) - {
            "batch_key", "proposed_payload"
        }
        if unexpected:
            raise serializers.ValidationError({
                "detail": "Unexpected request fields are forbidden."
            })
        return super().to_internal_value(data)

    def validate_proposed_payload(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "The proposal must be an object."
            )
        return value


class SicoCaseSetupPrepareView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, engagement_id, format=None):
        form = StrictPreparationInput(data=request.data)
        form.is_valid(raise_exception=True)

        try:
            result = prepare_ai_case_setup(
                request,
                engagement_id,
                batch_key=form.validated_data["batch_key"],
                proposed_payload=form.validated_data[
                    "proposed_payload"
                ],
            )
        except SicoCaseSetupPreparationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EngagementBlocked as exc:
            return Response(
                {"detail": str(exc)},
                status=exc.http_status,
            )
        except Exception as exc:
            if (
                hasattr(exc, "to_response")
                and hasattr(exc, "status_code")
            ):
                return Response(
                    exc.to_response(),
                    status=exc.status_code,
                )
            raise

        return Response({
            "engagement_id": str(engagement_id),
            "preparation": result,
            "execution_performed": False,
            "writes_to_grc_records": False,
            "requires_human_review": True,
        })

# Automatic preparation from an existing authorized engagement.
# The caller cannot submit record IDs, approvals, or a commit mode.
from .sico_case_setup_proposal import (
    SicoProposalError,
    prepare_case_setup_from_engagement,
)


class AutomaticCaseSetupInput(serializers.Serializer):
    batch_key = serializers.RegexField(
        regex=r"^[A-Za-z0-9_-]{1,80}$"
    )

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                "A JSON object is required."
            )
        if set(data) != {"batch_key"}:
            raise serializers.ValidationError(
                {"detail": ["Only batch_key is accepted."]}
            )
        return super().to_internal_value(data)


class SicoCaseSetupAutoPrepareView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, engagement_id, format=None):
        form = AutomaticCaseSetupInput(data=request.data)
        form.is_valid(raise_exception=True)

        try:
            result = prepare_case_setup_from_engagement(
                request,
                engagement_id,
                batch_key=form.validated_data["batch_key"],
            )
        except SicoProposalError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SicoCaseSetupPreparationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EngagementBlocked as exc:
            return Response(
                {"detail": str(exc)},
                status=exc.http_status,
            )

        return Response(result)