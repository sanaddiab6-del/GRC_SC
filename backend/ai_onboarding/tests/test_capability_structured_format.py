import unittest

from ai_onboarding.llm_provider import _ollama_output_format


class CapabilityStructuredFormatTests(unittest.TestCase):

    def setUp(self):
        self.schema = {
            "type": "object",
            "required": [
                "selected_capabilities",
                "clarifying_questions",
            ],
        }

    def test_capability_batch_uses_schema(self):
        self.assertEqual(
            _ollama_output_format(
                "sico_capability_batch_v1",
                self.schema,
            ),
            self.schema,
        )

    def test_capability_selection_uses_schema(self):
        self.assertEqual(
            _ollama_output_format(
                "sico_capability_selection_v1",
                self.schema,
            ),
            self.schema,
        )

    def test_existing_case_intake_format_unchanged(self):
        self.assertEqual(
            _ollama_output_format(
                "existing_case_intake_contract",
                self.schema,
            ),
            "json",
        )

    def test_other_gRC_capabilities_unchanged(self):
        self.assertEqual(
            _ollama_output_format(
                "asset_suggestion_v1",
                self.schema,
            ),
            "json",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)