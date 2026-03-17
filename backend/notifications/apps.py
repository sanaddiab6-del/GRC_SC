"""
notifications/apps.py
"""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = "Notifications"

    def ready(self) -> None:
        # Import signal handlers so they are registered when Django starts.
        # The import must live here (not at module level on signals.py) to
        # avoid circular imports with core models.
        import notifications.signals  # noqa: F401
