import unittest

from ai_onboarding.capability_selection import (
    CapabilitySelectionError,
    validate_capability_selection,
)


class CapabilityQuestionLimitTests(unittest.TestCase):

    def response(self, questions):
        return {
            "selected_capabilities": [
                {
                    "id": "case_setup",
                    "reason": "Establish engagement scope",
                    "priority": "high",
                }
            ],
            "clarifying_questions": questions,
        }

    def test_preserves_more_than_ten_questions(self):
        questions = [
            f"Clarification question {i}?"
            for i in range(1, 16)
        ]
        result = validate_capability_selection(
            self.response(questions)
        )
        self.assertEqual(
            result["clarifying_questions"],
            questions,
        )

    def test_preserves_fifty_questions(self):
        questions = [
            f"Question {i}?"
            for i in range(1, 51)
        ]
        result = validate_capability_selection(
            self.response(questions)
        )
        self.assertEqual(
            len(result["clarifying_questions"]),
            50,
        )

    def test_rejects_more_than_fifty_questions(self):
        questions = [
            f"Question {i}?"
            for i in range(1, 52)
        ]
        with self.assertRaises(CapabilitySelectionError):
            validate_capability_selection(
                self.response(questions)
            )

    def test_rejects_invalid_question_content(self):
        with self.assertRaises(CapabilitySelectionError):
            validate_capability_selection(
                self.response(["Valid question?", 123])
            )

    def test_preserves_security_flags(self):
        result = validate_capability_selection(
            self.response(["What is the scope?"])
        )
        self.assertFalse(result["execution_performed"])
        self.assertFalse(result["writes_to_grc_records"])
        self.assertTrue(result["requires_review"])


if __name__ == "__main__":
    unittest.main(verbosity=2)