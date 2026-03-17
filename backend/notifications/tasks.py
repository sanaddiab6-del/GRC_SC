"""
notifications/tasks.py

Huey background tasks for the notification delivery pipeline.

Fan-out flow
────────────
1. A Django signal fires when a core model changes.
2. The signal handler creates a NotificationEvent record synchronously,
   then schedules `fan_out_notifications` via transaction.on_commit so the
   event is committed before the task runs.
3. `fan_out_notifications`:
     - Finds every user who can access the originating folder.
     - Filters those users by their NotificationPreference settings.
     - Creates Notification rows in bulk.
     - Schedules per-channel delivery tasks for each Notification.
4. Per-channel tasks (in_app / email / slack / teams) perform the actual
   delivery and write a NotificationDeliveryLog row.

Using `db_task` ensures the task has access to the Django ORM and retries
on failure with exponential back-off.
"""
import uuid

import structlog
from huey.contrib.djhuey import db_task

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Fan-out task
# ---------------------------------------------------------------------------

@db_task(retries=3, retry_delay=30, retry_backoff=2.0)
def fan_out_notifications(event_id: str) -> None:
    """
    Given a NotificationEvent UUID, create per-user Notification rows and
    schedule delivery tasks for each enabled channel.
    """
    from django.contrib.auth import get_user_model
    from iam.models import Folder, RoleAssignment

    from .models import (
        Notification,
        NotificationDeliveryLog,
        NotificationEvent,
        NotificationPreference,
    )

    User = get_user_model()

    try:
        event = NotificationEvent.objects.select_related("folder").get(id=event_id)
    except NotificationEvent.DoesNotExist:
        logger.warning("fan_out_notifications: event not found", event_id=event_id)
        return

    # -----------------------------------------------------------------------
    # Determine which users can access the folder that the event originated in.
    # We walk RoleAssignment records: any user whose role assignment covers this
    # folder (directly or via an ancestor with is_recursive=True) is eligible.
    # -----------------------------------------------------------------------
    if event.folder is not None:
        eligible_user_ids = _get_users_for_folder(event.folder)
    else:
        # System-level event with no folder → notify all active users.
        eligible_user_ids = set(
            User.objects.filter(is_active=True).values_list("id", flat=True)
        )

    if not eligible_user_ids:
        return

    # -----------------------------------------------------------------------
    # For each eligible user, check preferences and create Notification rows.
    # -----------------------------------------------------------------------
    # Bulk-fetch preferences in one query.
    pref_map = {
        p.user_id: p
        for p in NotificationPreference.objects.filter(user_id__in=eligible_user_ids)
    }

    notifications_to_create = []
    for user_id in eligible_user_ids:
        pref = pref_map.get(user_id)
        if pref is None:
            # Auto-create defaults (in-app only) to avoid creating a pref on
            # every event for every user; just use default values inline.
            in_app_enabled = True
        else:
            in_app_enabled = pref.is_channel_enabled("in_app", event.event_type)

        # Skip users who have disabled all channels for this event type.
        if pref is not None:
            any_channel = any(
                pref.is_channel_enabled(ch, event.event_type)
                for ch in ("in_app", "email", "slack", "teams")
            )
            if not any_channel:
                continue

        notifications_to_create.append(
            Notification(user_id=user_id, event=event)
        )

    if not notifications_to_create:
        return

    # Bulk create; ignore_conflicts skips duplicates (same user+event pair).
    created = Notification.objects.bulk_create(
        notifications_to_create,
        ignore_conflicts=True,
    )

    # -----------------------------------------------------------------------
    # Schedule per-channel delivery for each newly created Notification.
    # -----------------------------------------------------------------------
    # Re-fetch created notifications to get their real PKs after bulk_create.
    notification_ids = list(
        Notification.objects.filter(
            event=event,
            user_id__in=eligible_user_ids,
        ).values_list("id", flat=True)
    )

    for notif_id in notification_ids:
        notif_id_str = str(notif_id)
        user_id = None
        for n in notifications_to_create:
            # Match the user from our in-memory list.
            pass  # resolved below via DB query

        deliver_in_app_notification(notif_id_str)

    # For email / slack / teams we need the preference per notification.
    notif_queryset = Notification.objects.filter(id__in=notification_ids).select_related(
        "user"
    )
    for notif in notif_queryset:
        pref = pref_map.get(notif.user_id)
        if pref is None:
            pref, _ = NotificationPreference.objects.get_or_create(user_id=notif.user_id)

        notif_id_str = str(notif.id)

        if pref.is_channel_enabled("email", event.event_type):
            deliver_email_notification(notif_id_str)

        if pref.is_channel_enabled("slack", event.event_type) and pref.slack_webhook_url:
            deliver_slack_notification(notif_id_str)

        if pref.is_channel_enabled("teams", event.event_type) and pref.teams_webhook_url:
            deliver_teams_notification(notif_id_str)


def _get_users_for_folder(folder) -> set:
    """
    Return the set of User PKs that have at least one RoleAssignment
    covering *folder* (directly or via ancestor with is_recursive=True).
    """
    from iam.models import Folder, RoleAssignment

    # Collect folder + all ancestor folders.
    folder_ids = {folder.id}
    current = folder
    while current.parent_folder_id is not None:
        folder_ids.add(current.parent_folder_id)
        try:
            current = Folder.objects.get(id=current.parent_folder_id)
        except Folder.DoesNotExist:
            break

    user_ids: set = set()

    # Direct assignments on the exact folder.
    direct = RoleAssignment.objects.filter(
        perimeter_folders__id=folder.id,
    ).values_list("user_id", flat=True)
    user_ids.update(u for u in direct if u is not None)

    # Recursive assignments on ancestor folders.
    recursive = RoleAssignment.objects.filter(
        perimeter_folders__id__in=folder_ids,
        is_recursive=True,
    ).values_list("user_id", flat=True)
    user_ids.update(u for u in recursive if u is not None)

    # UserGroup-based assignments — resolve groups → users.
    from iam.models import UserGroup

    group_direct = RoleAssignment.objects.filter(
        perimeter_folders__id=folder.id,
        user__isnull=True,
    ).values_list("user_group_id", flat=True)
    group_recursive = RoleAssignment.objects.filter(
        perimeter_folders__id__in=folder_ids,
        is_recursive=True,
        user__isnull=True,
    ).values_list("user_group_id", flat=True)

    group_ids = set(list(group_direct) + list(group_recursive)) - {None}
    if group_ids:
        from django.conf import settings as _settings
        UserModel = __import__("django.apps", fromlist=["apps"]).apps.get_model(_settings.AUTH_USER_MODEL)
        group_user_ids = UserModel.objects.filter(
            user_groups__id__in=group_ids
        ).values_list("id", flat=True)
        user_ids.update(u for u in group_user_ids if u is not None)

    return user_ids


# ---------------------------------------------------------------------------
# In-app delivery task
# (Just records a delivery log; the UI polls the Notification list endpoint.)
# ---------------------------------------------------------------------------

@db_task(retries=2, retry_delay=10)
def deliver_in_app_notification(notification_id: str) -> None:
    from .models import Notification, NotificationDeliveryLog

    try:
        notif = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        logger.warning("deliver_in_app: notification not found", id=notification_id)
        return

    NotificationDeliveryLog.objects.create(
        notification=notif,
        channel=NotificationDeliveryLog.Channel.IN_APP,
        status=NotificationDeliveryLog.DeliveryStatus.DELIVERED,
    )


# ---------------------------------------------------------------------------
# Email delivery task
# ---------------------------------------------------------------------------

@db_task(retries=3, retry_delay=60, retry_backoff=2.0)
def deliver_email_notification(notification_id: str) -> None:
    from django.conf import settings
    from django.core.mail import send_mail

    from .models import Notification, NotificationDeliveryLog

    try:
        notif = Notification.objects.select_related("event", "user").get(
            id=notification_id
        )
    except Notification.DoesNotExist:
        logger.warning("deliver_email: notification not found", id=notification_id)
        return

    email_address = getattr(notif.user, "email", None)
    if not email_address:
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.EMAIL,
            status=NotificationDeliveryLog.DeliveryStatus.SKIPPED,
            error_message="User has no email address.",
        )
        return

    event = notif.event
    subject = f"[CISO Assistant] {event.event_type.replace('.', ' ').title()}"
    body = (
        f"A new event has occurred on the CISO Assistant platform.\n\n"
        f"Event type : {event.event_type}\n"
        f"Object     : {event.object_name or event.object_id}\n"
        f"Time       : {event.created_at.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"Log in to review the details."
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_address],
            fail_silently=False,
        )
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.EMAIL,
            status=NotificationDeliveryLog.DeliveryStatus.DELIVERED,
        )
        logger.info("Email notification sent", notification_id=notification_id)
    except Exception as exc:
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.EMAIL,
            status=NotificationDeliveryLog.DeliveryStatus.FAILED,
            error_message=str(exc),
        )
        logger.error(
            "Email notification failed",
            notification_id=notification_id,
            error=str(exc),
        )
        raise  # re-raise so Huey retries


# ---------------------------------------------------------------------------
# Slack delivery task
# ---------------------------------------------------------------------------

@db_task(retries=3, retry_delay=60, retry_backoff=2.0)
def deliver_slack_notification(notification_id: str) -> None:
    import json

    import requests

    from .models import Notification, NotificationDeliveryLog, NotificationPreference

    try:
        notif = Notification.objects.select_related("event", "user").get(
            id=notification_id
        )
    except Notification.DoesNotExist:
        logger.warning("deliver_slack: notification not found", id=notification_id)
        return

    try:
        pref = NotificationPreference.objects.get(user=notif.user)
    except NotificationPreference.DoesNotExist:
        return

    webhook_url = pref.slack_webhook_url
    if not webhook_url:
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.SLACK,
            status=NotificationDeliveryLog.DeliveryStatus.SKIPPED,
            error_message="No Slack webhook URL configured.",
        )
        return

    event = notif.event
    payload = {
        "text": (
            f"*CISO Assistant Notification*\n"
            f"*Event:* {event.event_type}\n"
            f"*Object:* {event.object_name or str(event.object_id)}\n"
            f"*Time:* {event.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )
    }

    try:
        resp = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.SLACK,
            status=NotificationDeliveryLog.DeliveryStatus.DELIVERED,
        )
        logger.info("Slack notification sent", notification_id=notification_id)
    except Exception as exc:
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.SLACK,
            status=NotificationDeliveryLog.DeliveryStatus.FAILED,
            error_message=str(exc),
        )
        logger.error(
            "Slack notification failed",
            notification_id=notification_id,
            error=str(exc),
        )
        raise


# ---------------------------------------------------------------------------
# Microsoft Teams delivery task
# ---------------------------------------------------------------------------

@db_task(retries=3, retry_delay=60, retry_backoff=2.0)
def deliver_teams_notification(notification_id: str) -> None:
    import json

    import requests

    from .models import Notification, NotificationDeliveryLog, NotificationPreference

    try:
        notif = Notification.objects.select_related("event", "user").get(
            id=notification_id
        )
    except Notification.DoesNotExist:
        logger.warning("deliver_teams: notification not found", id=notification_id)
        return

    try:
        pref = NotificationPreference.objects.get(user=notif.user)
    except NotificationPreference.DoesNotExist:
        return

    webhook_url = pref.teams_webhook_url
    if not webhook_url:
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.TEAMS,
            status=NotificationDeliveryLog.DeliveryStatus.SKIPPED,
            error_message="No Teams webhook URL configured.",
        )
        return

    event = notif.event
    # Teams Adaptive Card (simple MessageCard format for maximum compatibility).
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": f"CISO Assistant: {event.event_type}",
        "sections": [
            {
                "activityTitle": "CISO Assistant Notification",
                "activitySubtitle": event.event_type,
                "facts": [
                    {"name": "Event", "value": event.event_type},
                    {
                        "name": "Object",
                        "value": event.object_name or str(event.object_id),
                    },
                    {
                        "name": "Time",
                        "value": event.created_at.strftime("%Y-%m-%d %H:%M UTC"),
                    },
                ],
            }
        ],
    }

    try:
        resp = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.TEAMS,
            status=NotificationDeliveryLog.DeliveryStatus.DELIVERED,
        )
        logger.info("Teams notification sent", notification_id=notification_id)
    except Exception as exc:
        NotificationDeliveryLog.objects.create(
            notification=notif,
            channel=NotificationDeliveryLog.Channel.TEAMS,
            status=NotificationDeliveryLog.DeliveryStatus.FAILED,
            error_message=str(exc),
        )
        logger.error(
            "Teams notification failed",
            notification_id=notification_id,
            error=str(exc),
        )
        raise
