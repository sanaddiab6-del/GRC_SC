"""Authenticated, bounded read-only SICO workforce discovery API."""
from __future__ import annotations

from django.http import Http404
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .workforce_discovery_service import discover_existing_grc_records


class DiscoveryInputSerializer(serializers.Serializer):
    organization = serializers.CharField(min_length=3, max_length=150, trim_whitespace=True)
    framework_hint = serializers.CharField(max_length=150, allow_blank=True, required=False, default="")
    selected_folder_id = serializers.UUIDField(required=False, allow_null=True)


class AiWorkforceDiscoveryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = DiscoveryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = discover_existing_grc_records(request.user, **serializer.validated_data)
        except Http404:
            return Response({"detail": "Organization not found or not accessible."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
