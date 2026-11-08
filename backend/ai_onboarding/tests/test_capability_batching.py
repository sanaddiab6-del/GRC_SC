import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ciso_assistant.settings"
)

import django
django.setup()

from ai_onboarding.capability_selection import (
    CapabilitySelectionError,
    suggest_engagement_capabilities,
)


class CapabilityBatchingTests(unittest.TestCase):

    def setUp(self):
        self.provider = Mock()
        self.config = SimpleNamespace(
            model="mock-qwen",
            timeout_seconds=300,
            max_output_tokens=2400,
            temperature=0.1,
        )
        self.resolve = patch(
            "ai_onboarding.capability_selection."
            "resolve_advisory_capability_config",
            return_value=self.config,
        )
        self.select = patch(
            "ai_onboarding.capability_selection."
            "get_advisory_provider_selection",
            return_value=SimpleNamespace(provider=self.provider),
        )
        self.resolve.start()
        self.select.start()
        self.addCleanup(self.resolve.stop)
        self.addCleanup(self.select.stop)

    def test_all_catalogue_batches_are_processed(self):
        def answer(**kwargs):
            first = kwargs["user_payload"]["allowed_capabilities"][0]
            return {
                "selected_capabilities": [{
                    "id": first["id"],
                    "reason": "Relevant to the engagement.",
                    "priority": "high",
                }],
                "clarifying_questions": [],
            }

        self.provider.generate_structured.side_effect = answer

        result = suggest_engagement_capabilities(
            "Complete the full applicable GRC assessment."
        )

        self.assertEqual(result["batches_processed"], 5)
        self.assertEqual(
            self.provider.generate_structured.call_count, 5
        )
        self.assertEqual(len(result["selected_capabilities"]), 5)
        self.assertFalse(result["writes_to_grc_records"])
        self.assertFalse(result["execution_performed"])

        for call in self.provider.generate_structured.call_args_list:
            self.assertLessEqual(
                len(call.kwargs["user_payload"]["allowed_capabilities"]),
                5,
            )
            self.assertLessEqual(
                call.kwargs["max_output_tokens"], 512
            )

    def test_empty_batch_is_allowed(self):
        count = 0

        def answer(**kwargs):
            nonlocal count
            count += 1
            entries = []
            if count == 1:
                first = kwargs["user_payload"]["allowed_capabilities"][0]
                entries = [{
                    "id": first["id"],
                    "reason": "Applicable.",
                    "priority": "high",
                }]
            return {
                "selected_capabilities": entries,
                "clarifying_questions": [],
            }

        self.provider.generate_structured.side_effect = answer
        result = suggest_engagement_capabilities(
            "Assess relevant GRC capabilities."
        )
        self.assertEqual(len(result["selected_capabilities"]), 1)
        self.assertEqual(result["batches_processed"], 5)

    def test_out_of_batch_selection_rejected(self):
        self.provider.generate_structured.return_value = {
            "selected_capabilities": [{
                "id": "privacy",
                "reason": "Attempted wrong batch.",
                "priority": "high",
            }],
            "clarifying_questions": [],
        }
        with self.assertRaises(CapabilitySelectionError):
            suggest_engagement_capabilities(
                "Review all relevant GRC functions."
            )

    def test_failed_batch_does_not_return_partial_result(self):
        responses = 0

        def answer(**kwargs):
            nonlocal responses
            responses += 1
            if responses == 2:
                raise RuntimeError("Simulated provider failure")
            first = kwargs["user_payload"]["allowed_capabilities"][0]
            return {
                "selected_capabilities": [{
                    "id": first["id"],
                    "reason": "Relevant.",
                    "priority": "high",
                }],
                "clarifying_questions": [],
            }

        self.provider.generate_structured.side_effect = answer
        with self.assertRaises(RuntimeError):
            suggest_engagement_capabilities(
                "Review the complete GRC engagement."
            )

    def test_no_selected_capabilities_fails_closed(self):
        self.provider.generate_structured.return_value = {
            "selected_capabilities": [],
            "clarifying_questions": [],
        }
        with self.assertRaises(CapabilitySelectionError):
            suggest_engagement_capabilities(
                "Review applicable GRC capabilities."
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)