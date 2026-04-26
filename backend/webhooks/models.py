import ipaddress
import socket
import uuid
from urllib.parse import urlparse
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.base_models import NameDescriptionMixin
from core.models import Actor
from iam.models import Folder, FolderMixin


def _is_ssrf_unsafe_ip(ip_str: str) -> bool:
    """
    Return True if the IP address belongs to any range that must not receive
    outbound webhook traffic (loopback, private, link-local, multicast, reserved).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_loopback
            or ip.is_private
            or ip.is_reserved
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_unspecified
        )
    except ValueError:
        return True  # Unparseable → treat as unsafe


class WebhookEventType(models.Model):
    """
    Represents a single, subscribable event type (e.g., "appliedcontrol.created").
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The event type string, e.g., 'appliedcontrol.created'",
    )

    def __str__(self):
        return self.name


class WebhookEndpoint(NameDescriptionMixin, FolderMixin):
    """
    Represents a single consumer endpoint for receiving webhooks.
    """

    class PayloadFormats(models.TextChoices):
        THIN = "thin", "Thin"
        FULL = "full", "Full"

    payload_format = models.CharField(
        verbose_name="Payload Format",
        max_length=10,
        choices=PayloadFormats.choices,
        default=PayloadFormats.FULL,
        help_text="The format of the webhook payload sent to this endpoint.",
    )

    owner = models.ForeignKey(
        Actor,
        related_name="webhook_endpoints",
        on_delete=models.CASCADE,
        help_text="The actor that owns this endpoint.",
        blank=True,
        null=True,
    )

    url = models.URLField(
        max_length=512, help_text="The consumer URL to send webhook events to."
    )

    secret = models.CharField(max_length=100, help_text="HMAC signing secret.")

    event_types = models.ManyToManyField(
        WebhookEventType,
        blank=True,
        help_text="A list of event types this endpoint subscribes to.",
    )

    target_folders = models.ManyToManyField(
        Folder,
        blank=True,
        help_text="Folders to which this webhook endpoint is scoped. If empty, the endpoint applies to all folders the owner has access to.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Global toggle to enable/disable sending events to this endpoint.",
    )

    def __str__(self):
        return f"{self.owner} - {self.url}"

    def clean(self):
        """
        Model-level validation for SSRF mitigation.

        Checks:
        1. Reject literal private/loopback/reserved IP addresses in the URL.
        2. Resolve the hostname via DNS and reject any result that maps to an
           internal address — prevents DNS-rebinding and indirect SSRF.
        """
        super().clean()

        parsed = urlparse(self.url)
        hostname = parsed.hostname
        if not hostname:
            raise ValidationError("The URL provided is invalid.")

        if not settings.WEBHOOK_ALLOW_PRIVATE_IPS:
            # --- Check 1: literal IP address ---
            try:
                ip_literal = ipaddress.ip_address(hostname)
                if _is_ssrf_unsafe_ip(str(ip_literal)):
                    raise ValidationError(
                        "The URL cannot point to an internal, loopback, link-local, "
                        "or reserved IP address."
                    )
            except ValueError:
                # Hostname is a domain name — proceed to DNS check.
                pass

            # --- Check 2: DNS resolution ---
            try:
                resolved = socket.getaddrinfo(hostname, None)
                for family, _type, _proto, _canonname, sockaddr in resolved:
                    resolved_ip = sockaddr[0]
                    if _is_ssrf_unsafe_ip(resolved_ip):
                        raise ValidationError(
                            f"The hostname '{hostname}' resolves to an internal address "
                            f"({resolved_ip}), which is not permitted."
                        )
            except ValidationError:
                raise
            except OSError:
                # DNS resolution failed — treat as invalid URL.
                raise ValidationError(
                    f"The hostname '{hostname}' could not be resolved."
                )

    def save(self, *args, **kwargs):
        """
        On save, ensure a secret exists if one wasn't provided.
        """
        self.full_clean()  # Run validation
        super().save(*args, **kwargs)
