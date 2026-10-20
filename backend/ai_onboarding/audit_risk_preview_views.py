"""Authenticated read-only assessment and risk-score preview endpoints."""

from __future__ import annotations

from django.http import Http404
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .audit_risk_preview_service import (
    build_assessment_audit_preview,
    build_risk_matrix_preview,
)
from .audit_risk_rules import PreviewInputError


class AssessmentPreviewQuery(serializers.Serializer):
    assessment_id = serializers.UUIDField()
    offset = serializers.IntegerField(min_value=0, default=0)
    limit = serializers.IntegerField(min_value=1, max_value=50, default=20)


class RiskScorePreviewInput(serializers.Serializer):
    scenario_id = serializers.UUIDField()
    ratings = serializers.DictField(child=serializers.DictField())


class AiAssessmentAuditPreviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        form = AssessmentPreviewQuery(data=request.query_params)
        form.is_valid(raise_exception=True)
        try:
            data = build_assessment_audit_preview(
                request.user,
                form.validated_data["assessment_id"],
                offset=form.validated_data["offset"],
                limit=form.validated_data["limit"],
            )
        except Http404:
            return Response({"detail": "Assessment not found or not accessible."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)


class AiRiskMatrixPreviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        form = RiskScorePreviewInput(data=request.data)
        form.is_valid(raise_exception=True)
        try:
            data = build_risk_matrix_preview(
                request.user, form.validated_data["scenario_id"], form.validated_data["ratings"]
            )
        except Http404:
            return Response({"detail": "Risk scenario not found or not accessible."}, status=status.HTTP_404_NOT_FOUND)
        except PreviewInputError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)
