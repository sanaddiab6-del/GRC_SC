# Generated migration for notifications app
# Hand-written to avoid container package incompatibilities.

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("iam", "0021_fix_auditee_iam_groups"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Created at",
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        db_index=True,
                        help_text="Dot-separated string, e.g. 'evidence.created'.",
                        max_length=100,
                        verbose_name="Event type",
                    ),
                ),
                (
                    "object_type",
                    models.CharField(
                        help_text="Lowercase model name, e.g. 'evidence'.",
                        max_length=100,
                        verbose_name="Object type",
                    ),
                ),
                (
                    "object_id",
                    models.UUIDField(
                        help_text="UUID of the model instance that triggered the event.",
                        verbose_name="Object ID",
                    ),
                ),
                (
                    "object_name",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Human-readable name snapshot at event time.",
                        max_length=255,
                        verbose_name="Object name",
                    ),
                ),
                (
                    "payload",
                    models.JSONField(
                        default=dict,
                        help_text="Lightweight JSON snapshot of the changed object.",
                        verbose_name="Payload",
                    ),
                ),
                (
                    "folder",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notification_events",
                        to="iam.folder",
                        verbose_name="Originating folder",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification event",
                "verbose_name_plural": "Notification events",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="NotificationPreference",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "in_app_enabled",
                    models.BooleanField(
                        default=True,
                        verbose_name="In-app notifications enabled",
                    ),
                ),
                (
                    "email_enabled",
                    models.BooleanField(
                        default=False,
                        help_text="Requires EMAIL_HOST to be configured.",
                        verbose_name="Email notifications enabled",
                    ),
                ),
                (
                    "slack_enabled",
                    models.BooleanField(
                        default=False,
                        verbose_name="Slack notifications enabled",
                    ),
                ),
                (
                    "slack_webhook_url",
                    models.URLField(
                        blank=True,
                        default="",
                        max_length=512,
                        verbose_name="Slack incoming webhook URL",
                    ),
                ),
                (
                    "teams_enabled",
                    models.BooleanField(
                        default=False,
                        verbose_name="Microsoft Teams notifications enabled",
                    ),
                ),
                (
                    "teams_webhook_url",
                    models.URLField(
                        blank=True,
                        default="",
                        max_length=512,
                        verbose_name="Microsoft Teams incoming webhook URL",
                    ),
                ),
                (
                    "event_type_overrides",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            "Map of event_type → bool.  Overrides the global channel toggles "
                            "for specific event types when present."
                        ),
                        verbose_name="Per-event-type overrides",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_preference",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification preference",
                "verbose_name_plural": "Notification preferences",
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Created at",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "read_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Read at",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("unread", "Unread"), ("read", "Read")],
                        db_index=True,
                        default="unread",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_index=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="notifications.notificationevent",
                        verbose_name="Event",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="NotificationDeliveryLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "attempted_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Attempted at",
                    ),
                ),
                (
                    "channel",
                    models.CharField(
                        choices=[
                            ("in_app", "In-App"),
                            ("email", "Email"),
                            ("slack", "Slack"),
                            ("teams", "Teams"),
                        ],
                        db_index=True,
                        max_length=20,
                        verbose_name="Channel",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("delivered", "Delivered"),
                            ("failed", "Failed"),
                            ("skipped", "Skipped"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Delivery status",
                    ),
                ),
                (
                    "error_message",
                    models.TextField(
                        blank=True,
                        default="",
                        verbose_name="Error message",
                    ),
                ),
                (
                    "notification",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="delivery_logs",
                        to="notifications.notification",
                        verbose_name="Notification",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification delivery log",
                "verbose_name_plural": "Notification delivery logs",
                "ordering": ["-attempted_at"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="notification",
            unique_together={("user", "event")},
        ),
    ]
