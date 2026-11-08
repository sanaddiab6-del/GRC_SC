import unittest
from ai_onboarding.llm_provider import _build_ollama_prompt
from ai_onboarding.llm_config import CAPABILITY_CASE_INTAKE


SCHEMA = {
    "type": "object",
    "properties": {
        "selected_capabilities": {"type": "array"},
        "clarifying_questions": {"type": "array"},
    },
    "required": [
        "selected_capabilities",
        "clarifying_questions",
    ],
}


def make_prompt(schema_name):
    return _build_ollama_prompt(
        capability=CAPABILITY_CASE_INTAKE,
        system_prompt="Select relevant capabilities.",
        user_payload={
            "engagement_objective": "Complete a GRC assessment."
        },
        json_schema=SCHEMA,
        schema_name=schema_name,
    )


class CapabilityPromptContractTests(unittest.TestCase):

    def test_batch_uses_its_own_schema(self):
        prompt = make_prompt("sico_capability_batch_v1")
        self.assertIn('"json_schema"', prompt)
        self.assertIn('"selected_capabilities"', prompt)
        self.assertNotIn('"step1_compact_skeleton"', prompt)

    def test_selection_uses_its_own_schema(self):
        prompt = make_prompt("sico_capability_selection_v1")
        self.assertIn('"json_schema"', prompt)
        self.assertNotIn('"step1_compact_skeleton"', prompt)

    def test_existing_case_intake_contract_preserved(self):
        prompt = make_prompt("existing_case_intake_contract")
        self.assertIn('"step1_compact_skeleton"', prompt)
        self.assertIn('"step1_hard_rules"', prompt)

    def test_unrelated_schema_is_not_exempted(self):
        prompt = make_prompt("unrelated_schema")
        self.assertIn('"step1_compact_skeleton"', prompt)


if __name__ == "__main__":
    unittest.main(verbosity=2)