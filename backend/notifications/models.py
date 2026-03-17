"""
notifications/models.py

Platform-wide notification system.
Deliberately does NOT use FolderMixin on Notification/NotificationPreference
because notifications and preferences are per-user, not per-folder.
NotificationEvent carries an optional folder FK so we know where an event
originated, but it is never used as an access-control boundary.
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from iam.models import Folder

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EVENT_TYPE_EVIDENCE_CREATED = "evidence.created"
EVENT_TYPE_EVIDENCE_UPDATED = "evidence.updated"
EVENT_TYPE_EVIDENCE_EXPIRED = "evidence.expired"

EVENT_TYPE_FINDING_CREATED = "finding.created"
EVENT_TYPE_FINDING_UPDATED = "finding.updated"

EVENT_TYPE_RISK_SCENARIO_CREATED = "risk_scenario.created"
EVENT_TYPE_RISK_SCENARIO_UPDATED = "risk_scenario.updated"

EVENT_TYPE_APPLIED_CONTROL_CREATED = "applied_control.created"
EVENT_TYPE_APPLIED_CONTROL_UPDATED = "applied_control.updated"

EVENT_TYPE_COMPLIANCE_ASSESSMENT_CREATED = "compliance_assessment.created"
EVENT_TYPE_COMPLIANCE_ASSESSMENT_UPDATED = "compliance_assessment.updated"

ALL_EVENT_TYPES = [
    EVENT_TYPE_EVIDENCE_CREATED,
    EVENT_TYPE_EVIDENCE_UPDATED,
    EVENT_TYPE_EVIDENCE_EXPIRED,
    EVENT_TYPE_FINDING_CREATED,
    EVENT_TYPE_FINDING_UPDATED,
    EVENT_TYPE_RISK_SCENARIO_CREATED,
    EVENT_TYPE_RISK_SCENARIO_UPDATED,
    EVENT_TYPE_APPLIED_CONTROL_CREATED,
    EVENT_TYPE_APPLIED_CONTROL_UPDATED,
    EVENT_TYPE_COMPLIANCE_ASSESSMENT_CREATED,
    EVENT_TYPE_COMPLIANCE_ASSESSMENT_UPDATED,
]


# ---------------------------------------------------------------------------
# NotificationEvent
# ---------------------------------------------------------------------------

class NotificationEvent(models.Model):
    """
    A single platform event produced by a change to a core model.
    One event may fan-out to many per-user Notification records.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        db_index=True,
    )

    event_type = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Event type"),
        help_text=_("Dot-separated string, e.g. 'evidence.created'."),
    )
    object_type = models.CharField(
        max_length=100,
        verbose_name=_("Object type"),
        help_text=_("Lowercase model name, e.g. 'evidence'."),
    )
    object_id = models.UUIDField(
        verbose_name=_("Object ID"),
        help_text=_("UUID of the model instance that triggered the event."),
    )
    object_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Object name"),
        help_text=_("Human-readable name snapshot at event time."),
    )

    # Optional folder reference so delivery tasks can scope user lookup.
    folder = models.ForeignKey(
        Folder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notification_events",
        verbose_name=_("Originating folder"),
    )

    payload = models.JSONField(
        default=dict,
        verbose_name=_("Payload"),
        help_text=_("Lightweight JSON snapshot of the changed object."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Notification event")
        verbose_name_plural = _("Notification events")

    def __str__(self) -> str:
        return f"{self.event_type} / {self.object_name or self.object_id}"


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------

class Notification(models.Model):
    """
    A per-user notification derived from a NotificationEvent.
    """

    class Status(models.TextChoices):
        UNREAD = "unread", _("Unread")
        READ = "read", _("Read")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Read at"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
        db_index=True,
    )
    event = models.ForeignKey(
        NotificationEvent,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Event"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNREAD,
        db_index=True,
        verbose_name=_("Status"),
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("user", "event")]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self) -> str:
        return f"[{self.status}] {self.user_id} / {self.event_id}"

    def mark_read(self) -> None:
        from django.utils import timezone

        if self.status != self.Status.READ:
            self.status = self.Status.READ
            self.read_at = timezone.now()
            self.save(update_fields=["status", "read_at", "updated_at"])


# ---------------------------------------------------------------------------
# NotificationPreference
# ---------------------------------------------------------------------------

class NotificationPreference(models.Model):
    """
    Per-user preferences controlling which channels are active and,
    optionally, overrides per event-type.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preference",
        verbose_name=_("User"),
    )

    # --- Global channel toggles -----------------------------------------
    in_app_enabled = models.BooleanField(
        default=True,
        verbose_name=_("In-app notifications enabled"),
    )
    email_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Email notifications enabled"),
        help_text=_("Requires EMAIL_HOST to be configured."),
    )
    slack_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Slack notifications enabled"),
    )
    slack_webhook_url = models.URLField(
        blank=True,
        default="",
        max_length=512,
        verbose_name=_("Slack incoming webhook URL"),
    )
    teams_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Microsoft Teams notifications enabled"),
    )
    teams_webhook_url = models.URLField(
        blank=True,
        default="",
        max_length=512,
        verbose_name=_("Microsoft Teams incoming webhook URL"),
    )

    # --- Per-event-type overrides ----------------------------------------
    # JSON structure: {"evidence.created": false, "finding.created": true, ...}
    # If a key is absent, the global channel toggle applies.
    event_type_overrides = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Per-event-type overrides"),
        help_text=_(
            "Map of event_type → bool.  Overrides the global channel toggles "
            "for specific event types when present."
        ),
    )

    class Meta:
        verbose_name = _("Notification preference")
        verbose_name_plural = _("Notification preferences")

    def __str__(self) -> str:
        return f"Preferences for {self.user_id}"

    def is_channel_enabled(self, channel: str, event_type: str) -> bool:
        """
        Returns True if *channel* is active for *event_type*.
        Per-event-type overrides take precedence over the global toggle.
        """
        override_key = f"{event_type}.{channel}"
        if override_key in self.event_type_overrides:
            return bool(self.event_type_overrides[override_key])
        return bool(getattr(self, f"{channel}_enabled", False))

    @classmethod
    def get_or_create_for_user(cls, user) -> "NotificationPreference":
        obj, _ = cls.objects.get_or_create(user=user)
        return obj


# ---------------------------------------------------------------------------
# NotificationDeliveryLog
# ---------------------------------------------------------------------------

class NotificationDeliveryLog(models.Model):
    """
    Immutable audit record of each delivery attempt for a Notification.
    """

    class Channel(models.TextChoices):
        IN_APP = "in_app", _("In-App")
        EMAIL = "email", _("Email")
        SLACK = "slack", _("Slack")
        TEAMS = "teams", _("Teams")

    class DeliveryStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        DELIVERED = "delivered", _("Delivered")
        FAILED = "failed", _("Failed")
        SKIPPED = "skipped", _("Skipped")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Attempted at"),
        db_index=True,
    )

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="delivery_logs",
        verbose_name=_("Notification"),
    )
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        verbose_name=_("Channel"),
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        verbose_name=_("Delivery status"),
    )
    error_message = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Error message"),
    )

    class Meta:
        ordering = ["-attempted_at"]
        verbose_name = _("Notification delivery log")
        verbose_name_plural = _("Notification delivery logs")

    def __str__(self) -> str:
        return f"{self.channel} / {self.status} / {self.attempted_at}"
