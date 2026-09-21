"""Regression tests for the production exposure of core.debug_views.recommendation_test_view.

The view is decorated @permission_classes([AllowAny]) and used to be registered
unconditionally in ciso_assistant/urls.py, so any anonymous caller in any environment
(DEBUG on or off) could reach it and read internal AI-provider/framework-source state.
It must now resolve only when settings.DEBUG is true.
"""

import importlib

import pytest
from django.test import override_settings


@pytest.mark.django_db
def test_debug_recommendation_endpoint_is_not_reachable_by_anonymous_user(client):
    # The test run itself uses the project's default settings, where DEBUG is False,
    # the same as a production deployment (docker-compose.prod.yml sets DJANGO_DEBUG=False).
    response = client.get("/debug/recommendation-test/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_debug_recommendation_endpoint_is_not_reachable_by_authenticated_user(
    authenticated_client,
):
    response = authenticated_client.get("/debug/recommendation-test/")
    assert response.status_code == 404


def test_debug_recommendation_path_is_only_registered_when_debug_is_true():
    """Exercise the actual module-level conditional in ciso_assistant/urls.py directly,
    without touching Django's live URL resolver (which is cached process-wide and shared
    by every other test)."""
    from ciso_assistant import urls as urls_module

    def _has_debug_path():
        return any(
            getattr(pattern, "name", None) == "recommendation-test"
            for pattern in urls_module.urlpatterns
        )

    try:
        with override_settings(DEBUG=True):
            importlib.reload(urls_module)
            assert _has_debug_path()
    finally:
        # Reload once more with the real (DEBUG=False) settings restored, before any other
        # test imports this module, since the reload above mutated shared module state.
        importlib.reload(urls_module)

    assert not _has_debug_path()
