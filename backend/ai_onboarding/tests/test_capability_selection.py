import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ciso_assistant.settings",
)

import django
django.setup()

from ai_onboarding.capability_selection import (
    CapabilitySelectionError,
    validate_capability_selection,
    suggest_engagement_capabilities,
)


def valid_response():
    return {
        "selected_capabilities": [
            {
                "id": "assets",
                "reason": "Establish the in-scope asset inventory.",
                "priority": "high",
            },
            {
                "id": "privacy",
                "reason": "Review applicable data protection duties.",
                "priority": "medium",
            },
        ],
        "clarifying_questions": [],
    }


class CapabilitySelectionTests(unittest.TestCase):

    def test_valid_capabilities_are_selected(self):
        result = validate_capability_selection(valid_response())
        self.assertEqual(
            len(result["selected_capabilities"]), 2
        )
        self.assertFalse(result["writes_to_grc_records"])

    def test_unconnected_module_remains_unavailable(self):
        result = validate_capability_selection(valid_response())
        privacy = result["selected_capabilities"][1]
        self.assertEqual(
            privacy["integration_status"],
            "requires_reviewed_integration",
        )
        self.assertFalse(
            privacy["execution_available_from_registry"]
        )

    def test_invented_capability_is_rejected(self):
        payload = valid_response()
        payload["selected_capabilities"][0]["id"] = (
            "execute_any_database_query"
        )
        with self.assertRaises(CapabilitySelectionError):
            validate_capability_selection(payload)

    def test_duplicate_capability_is_rejected(self):
        payload = valid_response()
        payload["selected_capabilities"].append(
            payload["selected_capabilities"][0].copy()
        )
        with self.assertRaises(CapabilitySelectionError):
            validate_capability_selection(payload)

    def test_ai_cannot_override_permissions(self):
        payload = valid_response()
        payload["selected_capabilities"][0][
            "execution_available_from_registry"
        ] = True
        payload["selected_capabilities"][0][
            "human_approval_required_for_writes"
        ] = False

        result = validate_capability_selection(payload)
        item = result["selected_capabilities"][0]

        self.assertFalse(
            item["execution_available_from_registry"]
        )
        self.assertTrue(
            item["human_approval_required_for_writes"]
        )

    @patch(
        "ai_onboarding.capability_selection."
        "get_advisory_provider_selection"
    )
    @patch(
        "ai_onboarding.capability_selection."
        "resolve_advisory_capability_config"
    )
    def test_existing_provider_is_called(
        self, resolve_config, select_provider
    ):
        config = SimpleNamespace(
            model="test-local-model",
            timeout_seconds=30,
            max_output_tokens=1024,
            temperature=0.1,
        )
        provider = Mock()
        provider.generate_structured.return_value = valid_response()

        resolve_config.return_value = config
        select_provider.return_value = SimpleNamespace(
            provider=provider
        )

        result = suggest_engagement_capabilities(
            "Perform a complete GRC assessment."
        )

        self.assertEqual(
            len(result["selected_capabilities"]), 2
        )
        provider.generate_structured.assert_called_once()
        self.assertFalse(result["execution_performed"])

    @patch(
        "ai_onboarding.capability_selection."
        "get_advisory_provider_selection"
    )
    @patch(
        "ai_onboarding.capability_selection."
        "resolve_advisory_capability_config"
    )
    def test_missing_provider_fails_closed(
        self, resolve_config, select_provider
    ):
        resolve_config.return_value = Mock()
        select_provider.return_value = SimpleNamespace(
            provider=None
        )

        with self.assertRaises(CapabilitySelectionError):
            suggest_engagement_capabilities(
                "Perform a GRC assessment."
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)