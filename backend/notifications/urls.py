"""
notifications/urls.py
"""
from django.urls import path

from .views import (
    MarkNotificationsReadView,
    NotificationListView,
    NotificationPreferenceView,
    UnreadCountView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("mark-read/", MarkNotificationsReadView.as_view(), name="notification-mark-read"),
    path("unread-count/", UnreadCountView.as_view(), name="notification-unread-count"),
    path(
        "preferences/",
        NotificationPreferenceView.as_view(),
        name="notification-preferences",
    ),
]
