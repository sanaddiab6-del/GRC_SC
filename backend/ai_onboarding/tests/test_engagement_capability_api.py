import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ciso_assistant.settings",
)

import django
django.setup()

from django.http import Http404
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding.engagement_capability_views import (
    AiEngagementCapabilitiesView,
)


class EngagementCapabilityApiTests(unittest.TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.engagement_id = uuid4()
        self.user = SimpleNamespace(
            pk=uuid4(),
            is_authenticated=True,
        )
        self.url = reverse(
            "sico-engagement-capabilities",
            kwargs={"engagement_id": self.engagement_id},
        )

    def request(self, authenticated=True):
        request = self.factory.post(
            self.url,
            {},
            format="json",
            HTTP_HOST="localhost:9443",
        )
        if authenticated:
            force_authenticate(request, user=self.user)
        return request

    def test_route_exists(self):
        self.assertIn(
            "/capabilities/",
            self.url,
        )

    def test_anonymous_user_rejected(self):
        response = AiEngagementCapabilitiesView.as_view()(
            self.request(authenticated=False),
            engagement_id=self.engagement_id,
        )
        self.assertIn(response.status_code, (401, 403))

    @patch(
        "ai_onboarding.engagement_capability_views."
        "authorized_engagement",
        side_effect=Http404(),
    )
    @patch(
        "ai_onboarding.engagement_capability_views."
        "suggest_engagement_capabilities"
    )
    def test_unauthorized_engagement_rejected(
        self, selector, authorization
    ):
        response = AiEngagementCapabilitiesView.as_view()(
            self.request(),
            engagement_id=self.engagement_id,
        )
        self.assertEqual(response.status_code, 404)
        selector.assert_not_called()

    @patch(
        "ai_onboarding.engagement_capability_views."
        "authorized_engagement"
    )
    @patch(
        "ai_onboarding.engagement_capability_views."
        "suggest_engagement_capabilities"
    )
    def test_authorized_engagement_uses_saved_objective(
        self, selector, authorization
    ):
        authorization.return_value = SimpleNamespace(
            pk=self.engagement_id,
            objective="Perform a complete NCA ECC GRC assessment.",
        )
        selector.return_value = {
            "selected_capabilities": [],
            "execution_performed": False,
            "writes_to_grc_records": False,
        }

        response = AiEngagementCapabilitiesView.as_view()(
            self.request(),
            engagement_id=self.engagement_id,
        )

        self.assertEqual(response.status_code, 200)
        selector.assert_called_once_with(
            "Perform a complete NCA ECC GRC assessment."
        )
        self.assertFalse(
            response.data["writes_to_grc_records"]
        )
        self.assertFalse(
            response.data["execution_performed"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)