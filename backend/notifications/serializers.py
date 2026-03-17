"""
notifications/serializers.py

DRF serializers for the notifications app.
We intentionally do NOT inherit BaseModelSerializer because that class
enforces folder-based permission checks, which do not apply to per-user
notifications.  Simple ModelSerializer + IsAuthenticated is correct here.
"""
from rest_framework import serializers

from .models import (
    Notification,
    NotificationDeliveryLog,
    NotificationEvent,
    NotificationPreference,
)


class NotificationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationEvent
        fields = [
            "id",
            "event_type",
            "object_type",
            "object_id",
            "object_name",
            "payload",
            "created_at",
        ]
        read_only_fields = fields


class NotificationDeliveryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDeliveryLog
        fields = [
            "id",
            "channel",
            "status",
            "attempted_at",
            "error_message",
        ]
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    event = NotificationEventSerializer(read_only=True)
    delivery_logs = NotificationDeliveryLogSerializer(many=True, read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "status",
            "read_at",
            "created_at",
            "updated_at",
            "event",
            "delivery_logs",
        ]
        read_only_fields = fields


class MarkReadSerializer(serializers.Serializer):
    """
    Request body for POST /notifications/mark-read/
    Either supply a list of UUIDs or set all=true.
    """

    ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
        help_text="List of notification UUIDs to mark as read.  Ignored when all=true.",
    )
    all = serializers.BooleanField(
        required=False,
        default=False,
        help_text="If true, mark ALL unread notifications for the current user as read.",
    )


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "in_app_enabled",
            "email_enabled",
            "slack_enabled",
            "slack_webhook_url",
            "teams_enabled",
            "teams_webhook_url",
            "event_type_overrides",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_slack_webhook_url(self, value: str) -> str:
        if value and not value.startswith("https://hooks.slack.com/"):
            raise serializers.ValidationError(
                "Slack webhook URL must start with https://hooks.slack.com/"
            )
        return value

    def validate_teams_webhook_url(self, value: str) -> str:
        if value and "outlook.office.com" not in value and "office365.com" not in value:
            raise serializers.ValidationError(
                "Teams webhook URL must be a valid Microsoft Teams incoming webhook URL."
            )
        return value

    def validate_event_type_overrides(self, value: dict) -> dict:
        from .models import ALL_EVENT_TYPES

        allowed_channels = {"in_app", "email", "slack", "teams"}
        for key, val in value.items():
            parts = key.rsplit(".", 1)
            if len(parts) != 2:
                raise serializers.ValidationError(
                    f"Key '{key}' must be in format '<event_type>.<channel>'."
                )
            event_part, channel_part = parts
            if event_part not in ALL_EVENT_TYPES:
                raise serializers.ValidationError(
                    f"Unknown event type '{event_part}' in overrides key '{key}'."
                )
            if channel_part not in allowed_channels:
                raise serializers.ValidationError(
                    f"Unknown channel '{channel_part}' in overrides key '{key}'."
                )
            if not isinstance(val, bool):
                raise serializers.ValidationError(
                    f"Value for key '{key}' must be a boolean."
                )
        return value


class UnreadCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField(read_only=True)
