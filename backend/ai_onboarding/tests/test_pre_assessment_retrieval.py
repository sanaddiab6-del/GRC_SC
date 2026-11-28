"""Offline tests: SICO AI Pre-Assessment short lists on the real framework libraries.

Each case is a fact from the gold scenarios (Petra / PCI DSS, ISO CITY / ISO 27001,
Najd Water Services / ECC, Zaytouna Medical Labs / ISO 27001) with the requirements a GRC reviewer expects to be checked.
At least one of them must be in the short list. No DB, Docker or model calls.
"""
import unittest
from pathlib import Path

import yaml

from ai_onboarding.pre_assessment_topics import (
    SHORTLIST_SIZE,
    build_candidates,
    shortlist_requirements,
)

LIBRARIES = Path(__file__).resolve().parents[2] / "library" / "libraries"

CASES = {
    "pcidss-4_0.yaml": [
        ("admin password unchanged", ["authentication_passwords", "access_control"],
         "The developer has used the same admin password since 2022.", {"8.3.9", "8.6.3"}),
        ("card machines", ["payment_terminals"],
         "The company has 3 shops with card machines.", {"9.5.1.1", "9.5.1.2", "9.5.1.3"}),
        ("hosting company", ["third_party_providers"],
         "The website runs on a server of a hosting company.",
         {"12.8.1", "12.8.2", "12.8.3", "12.8.4", "12.8.5"}),
        ("card numbers maybe stored", ["sensitive_data_storage"],
         "Not sure whether card numbers are stored in the customer orders database.",
         {"3.2.1", "3.3.1", "3.5.1", "3.4.1"}),
        ("card payment on website", ["web_application_security"],
         "Customers pay by card on the company website.", {"6.4.3", "11.6.1", "6.4.1", "6.4.2"}),
    ],
    "iso27001-2022.yaml": [
        ("access to student data", ["access_control"],
         "Access control to student data must be the focus.", {"A.5.15", "A.8.3", "A.5.18"}),
        ("student and parent records", ["sensitive_data_storage"],
         "Student and parent records are hosted on internal on-premise servers.", {"A.5.34", "A.5.12"}),
        ("trade secrets", ["sensitive_data_storage"],
         "Confidential manufacturing data and trade secrets must be protected.",
         {"A.5.12", "A.8.12", "A.5.14", "A.5.32", "A.5.33"}),
        ("new policy", ["governance_policy"],
         "A new internal data protection policy was approved and must be implemented within 2 months.",
         {"A.5.1", "5.2"}),
        # Zaytouna (2026-11-28): leavers' accounts are about revoking access rights.
        ("leavers not removed", ["access_control"],
         "Accounts of employees who left the company are not removed.", {"A.5.18"}),
    ],
    "ecc-1.yaml": [
        ("no strategy", ["governance_policy"],
         "The company does not have a documented cybersecurity strategy.", {"1-1-1"}),
        ("IT manager does cybersecurity", ["governance_policy"],
         "The IT manager is also responsible for cybersecurity; there is no separate cybersecurity team.",
         {"1-2-1"}),
        ("no awareness training", ["awareness_training"],
         "Employees have never received any security awareness training.", {"1-10-1", "1-10-2"}),
        ("weekly backups in the same room", ["backup_continuity"],
         "Backups are taken once a week to an external hard drive kept in the same server room.",
         {"2-9-3", "2-9-2"}),
        ("shared VPN account for vendor", ["access_control", "third_party_providers"],
         "The maintenance vendor connects remotely using one shared VPN account.",
         {"2-2-3", "4-1-2", "4-1-3"}),
    ],
}


def _load(file_name):
    data = yaml.safe_load((LIBRARIES / file_name).read_text(encoding="utf-8"))
    nodes = data["objects"]["framework"]["requirement_nodes"]
    return build_candidates(nodes), {n.get("ref_id") for n in nodes if n.get("assessable")}


@unittest.skipUnless(LIBRARIES.is_dir(), "framework libraries are not available")
class GoldShortListTests(unittest.TestCase):
    def test_expected_requirement_is_in_the_short_list(self):
        for file_name, cases in CASES.items():
            candidates, assessable = _load(file_name)
            for label, topics, claim, expected in cases:
                with self.subTest(framework=file_name, fact=label):
                    # The expectation itself must use real requirement numbers.
                    self.assertTrue(expected & assessable, f"no expected ref exists: {expected}")
                    short = shortlist_requirements(candidates, topics, claim)
                    refs = [c.ref_id for c in short]
                    self.assertLessEqual(len(refs), SHORTLIST_SIZE)
                    self.assertTrue(expected & set(refs), f"{label}: got {refs}, expected one of {sorted(expected)}")

    def test_pci_password_fact_does_not_rank_8_3_6_first(self):
        # 8.3.6 is about password length/complexity, not about a password that never changes.
        candidates, _ = _load("pcidss-4_0.yaml")
        short = shortlist_requirements(candidates, ["authentication_passwords", "access_control"],
                                       "The developer has used the same admin password since 2022.")
        self.assertNotEqual(short[0].ref_id, "8.3.6")


class ShortListBehaviourTests(unittest.TestCase):
    NODES = [
        {"urn": "s1", "assessable": False, "ref_id": "1", "name": "Backup and Recovery Management"},
        {"urn": "r1", "parent_urn": "s1", "assessable": True, "ref_id": "1-1",
         "description": "Requirements must be defined, documented and approved."},
        {"urn": "r2", "parent_urn": "s1", "assessable": True, "ref_id": "1-2",
         "description": "Backups are tested periodically."},
        {"urn": "r3", "assessable": True, "ref_id": "2", "description": "Passwords are protected."},
        {"urn": "r3a", "parent_urn": "r3", "assessable": True, "ref_id": "2.1",
         "description": "Passwords are changed every 90 days."},
    ]

    def test_parent_section_name_counts_for_its_children(self):
        refs = [c.ref_id for c in shortlist_requirements(build_candidates(self.NODES), ["backup_continuity"])]
        self.assertEqual(refs[0], "1-2")
        self.assertIn("1-1", refs)

    def test_requirement_with_assessable_children_is_skipped(self):
        refs = [c.ref_id for c in shortlist_requirements(build_candidates(self.NODES), ["authentication_passwords"])]
        self.assertEqual(refs, ["2.1"])

    def test_context_only_or_unknown_topic_gives_nothing(self):
        candidates = build_candidates(self.NODES)
        self.assertEqual(shortlist_requirements(candidates, ["context_only"]), [])
        self.assertEqual(shortlist_requirements(candidates, ["not_a_topic"]), [])

    def test_same_input_same_short_list(self):
        candidates = build_candidates(self.NODES)
        first = shortlist_requirements(candidates, ["backup_continuity"], "weekly backup")
        second = shortlist_requirements(candidates, ["backup_continuity"], "weekly backup")
        self.assertEqual([c.ref_id for c in first], [c.ref_id for c in second])


if __name__ == "__main__":
    unittest.main()
