import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai_onboarding import capability_selection as selector


class FullAggregationTests(unittest.TestCase):

    def run_selection(self, catalogue, questions_per_batch=2):
        provider = Mock()

        def generate(**kwargs):
            payload = kwargs["user_payload"]
            batch_number = payload["batch_number"]
            first = payload["allowed_capabilities"][0]

            return {
                "selected_capabilities": [
                    {
                        "id": first["id"],
                        "reason": "Relevant to the engagement",
                        "priority": "high",
                    }
                ],
                "clarifying_questions": [
                    f"Batch {batch_number} question {i}?"
                    for i in range(questions_per_batch)
                ],
            }

        provider.generate_structured.side_effect = generate

        config = SimpleNamespace(
            model="test-model",
            timeout_seconds=120,
            max_output_tokens=512,
            temperature=0.1,
        )

        with (
            patch.object(
                selector,
                "capability_catalog",
                return_value=catalogue,
            ),
            patch.object(
                selector,
                "validate_registry",
                return_value=True,
            ),
            patch.object(
                selector,
                "resolve_advisory_capability_config",
                return_value=config,
            ),
            patch.object(
                selector,
                "get_advisory_provider_selection",
                return_value=SimpleNamespace(
                    provider=provider
                ),
            ),
        ):
            result = selector.suggest_engagement_capabilities(
                "Hypothetical complete NCA ECC engagement"
            )

        return result, provider

    def test_five_batches_end_to_end(self):
        catalogue = selector.capability_catalog()

        result, provider = self.run_selection(catalogue)

        self.assertEqual(provider.generate_structured.call_count, 5)
        self.assertEqual(result["batches_processed"], 5)
        self.assertEqual(result["total_catalogued_capabilities"], 25)
        self.assertEqual(len(result["selected_capabilities"]), 5)
        self.assertEqual(len(result["clarifying_questions"]), 10)

        self.assertFalse(result["execution_performed"])
        self.assertFalse(result["writes_to_grc_records"])
        self.assertTrue(result["requires_review"])

    def test_more_than_ten_questions_are_preserved(self):
        catalogue = selector.capability_catalog() + [
            {
                "id": f"future_capability_{i}",
                "name": f"Future capability {i}",
                "module": "future",
                "integration_status": "catalogued",
                "execution_available_from_registry": False,
                "human_approval_required_for_writes": True,
            }
            for i in range(5)
        ]

        result, provider = self.run_selection(catalogue)

        self.assertEqual(provider.generate_structured.call_count, 6)
        self.assertEqual(result["batches_processed"], 6)
        self.assertEqual(len(result["clarifying_questions"]), 12)

    def test_more_than_two_questions_per_batch_fails_closed(self):
        catalogue = selector.capability_catalog()

        with self.assertRaises(selector.CapabilitySelectionError):
            self.run_selection(
                catalogue,
                questions_per_batch=3,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)