import unittest

from ai_onboarding.llm_config import (
    CAPABILITY_GRC_CAPABILITY_SELECTION,
    SUPPORTED_CAPABILITIES,
    resolve_advisory_capability_config,
)
from ai_onboarding.llm_provider import _build_ollama_prompt


class CapabilityProviderIdentityTests(unittest.TestCase):

    def test_new_task_is_registered(self):
        self.assertIn(
            CAPABILITY_GRC_CAPABILITY_SELECTION,
            SUPPORTED_CAPABILITIES,
        )
        config = resolve_advisory_capability_config(
            CAPABILITY_GRC_CAPABILITY_SELECTION
        )
        self.assertEqual(
            config.capability,
            CAPABILITY_GRC_CAPABILITY_SELECTION,
        )

    def test_prompt_does_not_expose_internal_task_identity(self):
        prompt = _build_ollama_prompt(
            capability=CAPABILITY_GRC_CAPABILITY_SELECTION,
            system_prompt="Select relevant GRC capabilities.",
            user_payload={
                "allowed_capabilities": [
                    {"id": "assets", "name": "Asset management"}
                ]
            },
            json_schema={
                "type": "object",
                "properties": {
                    "selected_capabilities": {"type": "array"},
                    "clarifying_questions": {"type": "array"},
                },
                "required": [
                    "selected_capabilities",
                    "clarifying_questions",
                ],
            },
            schema_name="sico_capability_batch_v1",
        )
        self.assertIn('"assets"', prompt)
        self.assertIn('"selected_capabilities"', prompt)
        self.assertNotIn('"grc_capability_selection"', prompt)
        self.assertNotIn('"step1_compact_skeleton"', prompt)


if __name__ == "__main__":
    unittest.main(verbosity=2)