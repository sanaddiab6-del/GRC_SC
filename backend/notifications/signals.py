"""
notifications/signals.py

Django signal handlers that create NotificationEvent records in response to
changes in core models.

IMPORTANT: This module must NOT import anything at module level that would
cause circular imports.  All model imports are inside the handler functions.
The module is loaded by NotificationsConfig.ready() in apps.py.

We deliberately listen with dispatch_uid strings so the signals are
idempotent even if this module is accidentally imported multiple times.
"""
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

import structlog

logger = structlog.get_logger(__name__)


def _schedule_fan_out(event_id: str) -> None:
    """Enqueue the fan-out task after the current DB transaction commits."""
    from .tasks import fan_out_notifications

    transaction.on_commit(
        lambda: fan_out_notifications.schedule(args=(event_id,), delay=1)
    )


def _create_event(instance, event_type: str) -> None:
    """
    Build a NotificationEvent from a model instance and schedule fan-out.
    Runs inside the same transaction as the save that triggered the signal.
    """
    from .models import NotificationEvent

    folder = getattr(instance, "folder", None)
    payload = {
        "object_type": instance.__class__.__name__.lower(),
        "object_id": str(instance.pk),
        "object_name": str(instance.name) if hasattr(instance, "name") else "",
    }

    event = NotificationEvent.objects.create(
        event_type=event_type,
        object_type=instance.__class__.__name__.lower(),
        object_id=instance.pk,
        object_name=str(instance.name) if hasattr(instance, "name") else "",
        folder=folder,
        payload=payload,
    )

    _schedule_fan_out(str(event.id))


# ---------------------------------------------------------------------------
# Evidence signals
# ---------------------------------------------------------------------------

@receiver(
    post_save,
    sender="core.Evidence",
    dispatch_uid="notifications.evidence_post_save",
)
def on_evidence_saved(sender, instance, created: bool, **kwargs) -> None:
    from .models import EVENT_TYPE_EVIDENCE_CREATED, EVENT_TYPE_EVIDENCE_UPDATED

    try:
        event_type = EVENT_TYPE_EVIDENCE_CREATED if created else EVENT_TYPE_EVIDENCE_UPDATED
        _create_event(instance, event_type)
    except Exception:
        logger.exception("on_evidence_saved: failed to create notification event")


# ---------------------------------------------------------------------------
# Finding signals
# ---------------------------------------------------------------------------

@receiver(
    post_save,
    sender="core.Finding",
    dispatch_uid="notifications.finding_post_save",
)
def on_finding_saved(sender, instance, created: bool, **kwargs) -> None:
    from .models import EVENT_TYPE_FINDING_CREATED, EVENT_TYPE_FINDING_UPDATED

    try:
        event_type = EVENT_TYPE_FINDING_CREATED if created else EVENT_TYPE_FINDING_UPDATED
        _create_event(instance, event_type)
    except Exception:
        logger.exception("on_finding_saved: failed to create notification event")


# ---------------------------------------------------------------------------
# RiskScenario signals
# ---------------------------------------------------------------------------

@receiver(
    post_save,
    sender="core.RiskScenario",
    dispatch_uid="notifications.risk_scenario_post_save",
)
def on_risk_scenario_saved(sender, instance, created: bool, **kwargs) -> None:
    from .models import (
        EVENT_TYPE_RISK_SCENARIO_CREATED,
        EVENT_TYPE_RISK_SCENARIO_UPDATED,
    )

    try:
        event_type = (
            EVENT_TYPE_RISK_SCENARIO_CREATED
            if created
            else EVENT_TYPE_RISK_SCENARIO_UPDATED
        )
        _create_event(instance, event_type)
    except Exception:
        logger.exception("on_risk_scenario_saved: failed to create notification event")


# ---------------------------------------------------------------------------
# AppliedControl signals
# ---------------------------------------------------------------------------

@receiver(
    post_save,
    sender="core.AppliedControl",
    dispatch_uid="notifications.applied_control_post_save",
)
def on_applied_control_saved(sender, instance, created: bool, **kwargs) -> None:
    from .models import (
        EVENT_TYPE_APPLIED_CONTROL_CREATED,
        EVENT_TYPE_APPLIED_CONTROL_UPDATED,
    )

    try:
        event_type = (
            EVENT_TYPE_APPLIED_CONTROL_CREATED
            if created
            else EVENT_TYPE_APPLIED_CONTROL_UPDATED
        )
        _create_event(instance, event_type)
    except Exception:
        logger.exception(
            "on_applied_control_saved: failed to create notification event"
        )


# ---------------------------------------------------------------------------
# ComplianceAssessment signals
# ---------------------------------------------------------------------------

@receiver(
    post_save,
    sender="core.ComplianceAssessment",
    dispatch_uid="notifications.compliance_assessment_post_save",
)
def on_compliance_assessment_saved(sender, instance, created: bool, **kwargs) -> None:
    from .models import (
        EVENT_TYPE_COMPLIANCE_ASSESSMENT_CREATED,
        EVENT_TYPE_COMPLIANCE_ASSESSMENT_UPDATED,
    )

    try:
        event_type = (
            EVENT_TYPE_COMPLIANCE_ASSESSMENT_CREATED
            if created
            else EVENT_TYPE_COMPLIANCE_ASSESSMENT_UPDATED
        )
        _create_event(instance, event_type)
    except Exception:
        logger.exception(
            "on_compliance_assessment_saved: failed to create notification event"
        )
