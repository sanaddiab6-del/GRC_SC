"""Offline tests: SICO AI Pre-Assessment subject anchor, replayed on the real libraries.

The "drop" cases are the exact clauses qwen3:4b-instruct cited in the baseline measurement
(2026-11-25) for findings about another subject, or citing a clause the quote does not
contradict. The "keep" cases are correct GRC findings. No DB, Docker or model calls.
"""
import unittest
from pathlib import Path

import yaml

from ai_onboarding import pre_assessment_service as rules
from ai_onboarding.pre_assessment_topics import build_candidates, missing_anchors, requirement_subject

LIBRARIES = Path(__file__).resolve().parents[2] / "library" / "libraries"

NAJD = (
    "We are a water utility company in Riyadh with 150 employees. We do not have a documented cybersecurity "
    "strategy. Our IT manager is also responsible for cybersecurity because we have no separate cybersecurity "
    "team. Employees have never received any security awareness training. We take backups once a week to an "
    "external hard drive kept in the same server room. Our maintenance vendor connects remotely using one "
    "shared VPN account. We need to comply with ECC this year."
)
PETRA = (
    "We are an online store in Amman selling electronics. Customers pay by card on our website and we also have "
    "3 shops with card machines. Our website runs on a hosting company server and the developer still uses the "
    "same admin password since 2022. We keep customer orders in a database but not sure if card numbers are "
    "saved there. We need PCI DSS compliance because the bank asked us."
)
QUOTES = {
    "strategy": "We do not have a documented cybersecurity strategy",
    "it_manager": "Our IT manager is also responsible for cybersecurity because we have no separate cybersecurity team",
    "awareness": "Employees have never received any security awareness training",
    "backups": "We take backups once a week to an external hard drive kept in the same server room",
    "vpn": "Our maintenance vendor connects remotely using one shared VPN account",
    "password": "the developer still uses the same admin password since 2022",
}

# (library, objective, quote key, ref, relation, clause cited, expected kind)
KEEP = [
    ("ecc-1.yaml", NAJD, "strategy", "1-1-1", "gap_explicit",
     "A cybersecurity strategy must be defined, documented and approved", rules.KIND_NON_COMPLIANT),
    ("ecc-1.yaml", NAJD, "it_manager", "1-2-1", "gap_explicit",
     "A dedicated cybersecurity function (e.g., division, department) must be established within the organization",
     rules.KIND_NON_COMPLIANT),
    ("ecc-1.yaml", NAJD, "awareness", "1-10-2", "gap_explicit", "must be implemented", rules.KIND_NON_COMPLIANT),
    # The clause the quote really contradicts.
    ("ecc-1.yaml", NAJD, "awareness", "1-10-1", "gap_explicit",
     "The program must be conducted periodically through multiple channels", rules.KIND_NON_COMPLIANT),
    ("ecc-1.yaml", NAJD, "vpn", "2-2-3", "gap_explicit",
     "User authentication based on username and password", rules.KIND_NON_COMPLIANT),
    ("ecc-1.yaml", NAJD, "backups", "2-9-3", "partial_explicit",
     "Ability to perform quick recovery of data and systems after cybersecurity incidents", rules.KIND_PARTIAL),
    # Conditional requirement: stays a Potential gap.
    ("pcidss-4_0.yaml", PETRA, "password", "8.3.9", "gap_explicit",
     "Passwords/passphrases are changed at least once every 90 days", rules.KIND_POTENTIAL_GAP),
]
DROP = [
    # Another subject.
    ("pcidss-4_0.yaml", PETRA, "password", "8.6.3", "gap_explicit", "Passwords/passphrases are changed periodically"),
    ("ecc-1.yaml", NAJD, "it_manager", "1-2-3", "gap_explicit",
     "The committee must include the head of the cybersecurity function as one of its members"),
    ("ecc-1.yaml", NAJD, "it_manager", "1-4-1", "gap_explicit",
     "Cybersecurity organizational structure and related roles and responsibilities must be defined, documented, "
     "approved, supported and assigned by the Authorizing Official"),
    ("ecc-1.yaml", NAJD, "awareness", "1-10-3", "gap_explicit",
     "must cover the latest cyber threats and how to protect against them"),
    # A clause the quote does not contradict.
    ("ecc-1.yaml", NAJD, "awareness", "1-10-1", "gap_explicit", "must be developed and approved"),
    ("ecc-1.yaml", NAJD, "vpn", "2-2-3", "gap_explicit", "Multi-factor authentication for remote access"),
    ("ecc-1.yaml", NAJD, "backups", "2-9-3", "partial_explicit",
     "Scope and coverage of backups to cover critical technology and information assets"),
]


def _candidate(library, ref):
    nodes = yaml.safe_load((LIBRARIES / library).read_text(encoding="utf-8"))["objects"]["framework"]["requirement_nodes"]
    return next(c for c in build_candidates(nodes) if c.ref_id == ref)


def _decide(library, objective, quote_key, ref, relation, clause):
    facts, _ = rules.verify_facts([{"quote": QUOTES[quote_key], "topics": ["governance_policy"],
                                    "certainty": "stated"}], objective)
    candidate = _candidate(library, ref)
    results, _ = rules.plan_fact_results(facts[0], [candidate], [
        {"ref_id": ref, "relation": relation, "violated_clause": clause}])
    return results[0].outcome.kind


@unittest.skipUnless(LIBRARIES.is_dir(), "framework libraries are not available")
class SubjectAnchorReplayTests(unittest.TestCase):
    def test_correct_findings_are_kept(self):
        for library, objective, quote_key, ref, relation, clause, expected in KEEP:
            with self.subTest(ref=ref, clause=clause):
                self.assertEqual(_decide(library, objective, quote_key, ref, relation, clause), expected)

    def test_other_subject_or_wrong_clause_becomes_to_be_confirmed(self):
        for library, objective, quote_key, ref, relation, clause in DROP:
            with self.subTest(ref=ref, clause=clause):
                self.assertEqual(_decide(library, objective, quote_key, ref, relation, clause),
                                 rules.KIND_TO_BE_CONFIRMED)


class SubjectAnchorUnitTests(unittest.TestCase):
    def test_requirement_subject_is_the_text_before_the_first_verb(self):
        self.assertEqual(
            requirement_subject(None, "Passwords/passphrases for any application and system accounts are protected"),
            "passwords/passphrases for any application and system accounts")
        self.assertEqual(requirement_subject("Access control", "This control implements access control"),
                         "access control this control")

    def test_missing_anchor_names_the_concept(self):
        self.assertEqual(missing_anchors("a cybersecurity steering committee", "", "no separate cybersecurity team"),
                         ["committee"])
        self.assertEqual(missing_anchors("", "Multi-factor authentication for remote access",
                                         "connects remotely using one shared VPN account"), ["mfa"])
        self.assertEqual(missing_anchors("a cybersecurity strategy", "", "We do not have a documented cybersecurity strategy"), [])

    def test_incidents_in_a_clause_are_context_not_subject(self):
        self.assertEqual(missing_anchors("backup and recovery management",
                                         "quick recovery of data and systems after cybersecurity incidents",
                                         "We take backups once a week"), [])
        self.assertEqual(missing_anchors("cybersecurity incident management", "", "We take backups once a week"),
                         ["incidents"])

    def test_arabic_quote_shows_no_english_anchor(self):
        # Recorded for phase 3: Arabic objectives fall back to To be confirmed.
        self.assertEqual(missing_anchors("a cybersecurity strategy", "", "ما عنا استراتيجية أمن سيبراني موثقة"),
                         ["strategy"])


if __name__ == "__main__":
    unittest.main()
