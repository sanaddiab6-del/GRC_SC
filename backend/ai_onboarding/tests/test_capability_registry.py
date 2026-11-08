import unittest

from ai_onboarding.capability_registry import (
    ADDITIONAL_CAPABILITIES,
    EXISTING_STAGES,
    capability_catalog,
    capability_by_id,
    validate_registry,
)


class CapabilityRegistryTests(unittest.TestCase):

    def test_matches_existing_engagement_stages(self):
        self.assertTrue(validate_registry())
        self.assertEqual(len(EXISTING_STAGES), 11)

    def test_additional_capabilities_are_catalogued(self):
        records = capability_catalog()
        ids = {item["id"] for item in records}
        self.assertTrue(set(ADDITIONAL_CAPABILITIES).issubset(ids))

    def test_unconnected_modules_cannot_execute(self):
        for entry in capability_catalog():
            self.assertFalse(
                entry["execution_available_from_registry"]
            )
            self.assertTrue(
                entry["human_approval_required_for_writes"]
            )

    def test_unknown_capabilities_rejected(self):
        with self.assertRaises(KeyError):
            capability_by_id("invented_unrestricted_executor")

    def test_catalogue_returns_independent_records(self):
        first = capability_catalog()
        first[0]["name"] = "Changed by caller"
        second = capability_catalog()
        self.assertNotEqual(first[0]["name"], second[0]["name"])


if __name__ == "__main__":
    unittest.main(verbosity=2)