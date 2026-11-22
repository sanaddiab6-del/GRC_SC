"""Authenticated, read-only capability selection for SICO engagements."""

from django.http import Http404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .capability_selection import (
    CapabilitySelectionError,
    suggest_engagement_capabilities,
)
from .engagement_service import authorized_engagement


class AiEngagementCapabilitiesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, engagement_id, format=None):
        # The trusted engagement is loaded by server-side creator
        # and current folder authorization, not by a client-supplied ID.
        engagement = authorized_engagement(request.user, engagement_id)

        # Never accept an arbitrary objective or permission metadata
        # from the caller.
        try:
            selection = suggest_engagement_capabilities(
                engagement.objective
            )
        except CapabilitySelectionError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({
            "engagement_id": str(engagement.pk),
            "capability_selection": selection,
            "execution_performed": False,
            "writes_to_grc_records": False,
        })