"""
notifications/views.py

DRF views for the notifications app.

Endpoints:
  GET    /api/notifications/                   List notifications for current user
  POST   /api/notifications/mark-read/         Mark one, many, or all as read
  GET    /api/notifications/unread-count/      Badge count helper
  GET    /api/notifications/preferences/       Retrieve current user's preferences
  PATCH  /api/notifications/preferences/       Update current user's preferences
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

import structlog

from .models import Notification, NotificationPreference
from .serializers import (
    MarkReadSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
    UnreadCountSerializer,
)

logger = structlog.get_logger(__name__)


class NotificationPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class NotificationListView(APIView):
    """
    GET /api/notifications/

    Returns a paginated list of notifications for the authenticated user,
    newest first.

    Query parameters:
      status=unread|read   (optional filter)
      page, page_size      (pagination)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        qs = (
            Notification.objects.filter(user=request.user)
            .select_related("event")
            .prefetch_related("delivery_logs")
            .order_by("-created_at")
        )

        status_filter = request.query_params.get("status")
        if status_filter in (Notification.Status.UNREAD, Notification.Status.READ):
            qs = qs.filter(status=status_filter)

        paginator = NotificationPagination()
        page = paginator.paginate_queryset(qs, request)
        unread_count = Notification.objects.filter(
            user=request.user, status=Notification.Status.UNREAD
        ).count()

        serializer = NotificationSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        # Inject unread_count at the top level for convenience
        response.data["unread_count"] = unread_count
        return response


class MarkNotificationsReadView(APIView):
    """
    POST /api/notifications/mark-read/

    Body (JSON):
      { "ids": ["uuid", ...] }   — mark specific notifications
      { "all": true }            — mark all unread notifications for user
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mark_all = serializer.validated_data.get("all", False)
        ids = serializer.validated_data.get("ids", [])

        now = timezone.now()

        if mark_all:
            updated = Notification.objects.filter(
                user=request.user,
                status=Notification.Status.UNREAD,
            ).update(status=Notification.Status.READ, read_at=now, updated_at=now)
        elif ids:
            updated = Notification.objects.filter(
                user=request.user,
                id__in=ids,
                status=Notification.Status.UNREAD,
            ).update(status=Notification.Status.READ, read_at=now, updated_at=now)
        else:
            return Response(
                {"detail": "Provide 'ids' or set 'all' to true."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"updated": updated}, status=status.HTTP_200_OK)


class UnreadCountView(APIView):
    """
    GET /api/notifications/unread-count/

    Lightweight endpoint for the UI badge counter.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        count = Notification.objects.filter(
            user=request.user,
            status=Notification.Status.UNREAD,
        ).count()
        serializer = UnreadCountSerializer({"unread_count": count})
        return Response(serializer.data)


class NotificationPreferenceView(APIView):
    """
    GET   /api/notifications/preferences/   Retrieve preferences
    PATCH /api/notifications/preferences/   Update preferences (partial)
    """

    permission_classes = [IsAuthenticated]

    def _get_preference(self, user):
        return NotificationPreference.get_or_create_for_user(user)

    def get(self, request: Request) -> Response:
        preference = self._get_preference(request.user)
        serializer = NotificationPreferenceSerializer(preference)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        preference = self._get_preference(request.user)
        serializer = NotificationPreferenceSerializer(
            preference,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(
            "Notification preferences updated",
            user_id=str(request.user.id),
        )
        return Response(serializer.data)
