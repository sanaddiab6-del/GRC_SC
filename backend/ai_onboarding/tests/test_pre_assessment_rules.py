"""Offline tests: SICO AI Pre-Assessment verification and result rules.

No DB, Docker or model calls.
"""
import unittest
from datetime import date

from ai_onboarding import pre_assessment_service as rules
from ai_onboarding.pre_assessment_topics import (
    CONTEXT_ONLY,
    TOPIC_ENUM,
    is_conditional_requirement,
    is_uncertain,
    states_deficiency,
)

PETRA = (
    "We are an online store in Amman selling electronics. Customers pay by card on our website "
    "and we also have 3 shops with card machines. Our website runs on a hosting company server "
    "and the developer still uses the same admin password since 2022. We keep customer orders in "
    "a database but not sure if card numbers are saved there. We need PCI DSS compliance because "
    "the bank asked us."
)
PCI_836 = (
    "If passwords/passphrases are used as authentication factors to meet Requirement 8.3.1, they "
    "meet the following minimum level of complexity:\n• A minimum length of 12 characters."
)
ECC_111 = (
    "A cybersecurity strategy must be defined, documented and approved. It must be supported by "
    "the head of the organization or his/her delegate."
)


class QuoteVerificationTests(unittest.TestCase):
    def test_quote_in_objective_is_accepted_with_its_whole_sentence(self):
        found = rules.verify_quote("the developer still uses the same admin password since 2022", PETRA)
        self.assertIsNotNone(found)
        self.assertEqual(found.quote, "the developer still uses the same admin password since 2022")
        self.assertTrue(found.sentence.startswith("Our website runs on a hosting company server"))
        self.assertTrue(found.sentence.endswith("since 2022."))

    def test_quote_not_in_objective_is_rejected(self):
        self.assertIsNone(rules.verify_quote("card numbers are encrypted in the database", PETRA))
        self.assertIsNone(rules.verify_quote("the developer changed the admin password in 2023", PETRA))

    def test_case_spacing_and_smart_quotes_do_not_break_a_real_quote(self):
        self.assertIsNotNone(rules.verify_quote("  CUSTOMERS PAY   BY CARD on our website ", PETRA))
        objective = "Our admin’s password  is\nshared by the whole team and nobody has changed it for years."
        found = rules.verify_quote("our admin's password is shared", objective)
        self.assertIsNotNone(found)

    def test_line_break_ends_a_sentence(self):
        objective = "We have two offices in Amman\nnobody changes their passwords at all"
        found = rules.verify_quote("nobody changes their passwords", objective)
        self.assertEqual(found.sentence, "nobody changes their passwords at all")

    def test_quote_after_character_450_is_still_verified(self):
        long_objective = ("We sell furniture online. " * 20) + "Our firewall rules were never reviewed."
        self.assertGreater(long_objective.index("firewall"), 450)
        self.assertIsNotNone(rules.verify_quote("firewall rules were never reviewed", long_objective))

    def test_too_short_or_too_long_quotes_are_rejected(self):
        self.assertIsNone(rules.verify_quote("card", PETRA))
        self.assertIsNone(rules.verify_quote(PETRA, PETRA))

    def test_shortened_quote_still_shows_the_uncertain_sentence(self):
        # The model drops "not sure if"; the observation must still show the full sentence.
        found = rules.verify_quote("card numbers are saved there", PETRA)
        self.assertIn("not sure if card numbers are saved there", found.sentence)

    def test_clause_must_be_in_the_requirement(self):
        self.assertEqual(
            rules.verify_clause("A cybersecurity strategy must be defined", ECC_111),
            "A cybersecurity strategy must be defined",
        )
        self.assertIsNone(rules.verify_clause("passwords must be changed every 90 days", ECC_111))
        self.assertIsNone(rules.verify_clause("strategy", ECC_111))


class FactTests(unittest.TestCase):
    def test_only_verified_facts_with_known_topics_are_kept(self):
        facts, dropped = rules.verify_facts(
            [
                {"quote": "we also have 3 shops with card machines", "claim_en": "3 shops with card machines",
                 "topics": ["payment_terminals"], "certainty": "stated"},
                {"quote": "card data is stored unencrypted", "claim_en": "x", "topics": ["sensitive_data_storage"],
                 "certainty": "stated"},
                {"quote": "Our website runs on a hosting company server", "claim_en": "hosting",
                 "topics": ["made_up_topic"], "certainty": "stated"},
            ],
            PETRA,
        )
        self.assertEqual([f.quote for f in facts], ["we also have 3 shops with card machines"])
        self.assertEqual({d["reason"] for d in dropped}, {"quote_not_in_objective", "no_known_topic"})

    def test_uncertain_sentence_stays_uncertain_even_if_model_says_stated(self):
        facts, _ = rules.verify_facts(
            [{"quote": "card numbers are saved there", "claim_en": "card numbers may be stored",
              "topics": ["sensitive_data_storage"], "certainty": "stated"}],
            PETRA,
        )
        self.assertTrue(facts[0].uncertain)

    def test_missing_certainty_counts_as_uncertain(self):
        facts, _ = rules.verify_facts(
            [{"quote": "the developer still uses the same admin password since 2022",
              "topics": ["authentication_passwords"]}],
            PETRA,
        )
        self.assertTrue(facts[0].uncertain)

    def test_at_most_six_facts_and_no_duplicates(self):
        objective = ". ".join(f"Finding number {i} is about our backups" for i in range(10)) + "."
        raw = [{"quote": f"Finding number {i} is about our backups", "topics": ["backup_continuity"],
                "certainty": "stated"} for i in range(10)]
        raw.append(dict(raw[0]))
        facts, dropped = rules.verify_facts(raw, objective)
        self.assertEqual(len(facts), rules.MAX_FACTS)
        self.assertTrue(any(d["reason"] == "too_many_facts" for d in dropped))

    def test_topic_copied_with_its_meaning_is_read_as_the_bare_name(self):
        # Seen with qwen3:4b-instruct: it returned the whole hint line as the topic.
        facts, _ = rules.verify_facts(
            [{"quote": "the developer still uses the same admin password since 2022",
              "topics": ["authentication_passwords: password", " Governance_Policy : polic",
                         "made_up: authentication_passwords"],
              "certainty": "stated"}],
            PETRA,
        )
        self.assertEqual(facts[0].topics, ("authentication_passwords", "governance_policy"))

    def test_odd_key_spelling_from_the_model_is_read(self):
        # Seen with qwen3:4b-instruct: {"ref- id": "A2.1.1", ...}.
        self.assertEqual(rules.item_fields({"ref- id": "A2.1.1", "Relation": "not_related", "x": 1}),
                         {"ref_id": "A2.1.1", "relation": "not_related"})
        facts, _ = rules.verify_facts(
            [{"Quote": "we also have 3 shops with card machines", "claim en": "3 shops",
              "topics": ["payment_terminals"], "certainty": "stated"}],
            PETRA,
        )
        self.assertEqual(facts[0].claim, "3 shops")

    def test_context_only_fact_is_not_judged(self):
        facts, _ = rules.verify_facts(
            [{"quote": "We need PCI DSS compliance because the bank asked us", "topics": [CONTEXT_ONLY],
              "certainty": "stated"}],
            PETRA,
        )
        self.assertFalse(facts[0].judgeable)

    def test_not_a_list_is_handled(self):
        facts, dropped = rules.verify_facts({"quote": "x"}, PETRA)
        self.assertEqual(facts, [])
        self.assertEqual(dropped[0]["reason"], "facts_not_a_list")


class DetectorTests(unittest.TestCase):
    def test_conditional_requirements(self):
        self.assertTrue(is_conditional_requirement(PCI_836))
        self.assertTrue(is_conditional_requirement("Where applicable, logs are reviewed daily."))
        self.assertFalse(is_conditional_requirement(ECC_111))
        self.assertFalse(is_conditional_requirement("MFA is implemented for all non-console access into the CDE."))

    def test_condition_after_a_scope_prefix_is_found(self):
        # PCI 8.3.10.1 was judged Non-compliant for a merchant before this rule.
        self.assertTrue(is_conditional_requirement(
            "Additional requirement for service providers only: If passwords/passphrases are used as "
            "the only authentication factor for customer user access then either: ..."))
        self.assertTrue(is_conditional_requirement(
            "Additional requirement for service providers only: Reviews are performed at least once every three months."))
        # "if" deep inside a long requirement is not its condition.
        self.assertFalse(is_conditional_requirement(
            "Audit logs are reviewed at least once daily. " * 8 + "Escalate if anomalies are found."))

    def test_stated_deficiency_including_contractions(self):
        stated = [
            "We don't have a documented policy",
            "We dont have a documented policy",
            "We don’t have a documented policy",
            "We do not have a documented cybersecurity strategy",
            "Employees have never received any security awareness training",
            "connects remotely using one shared VPN account",
            "the developer still uses the same admin password since 2022",
            "We have no separate cybersecurity team",
            "Backups are kept without encryption",
            "Nobody reviews the logs",
            "There is none", "MFA is missing", "Logging is absent", "We lack a backup policy",
            "lacking an incident plan", "The firewall is no longer maintained", "We have only one administrator",
            "We are unable to restore data", "We cannot restore data",
            "It doesn't", "We didn't", "We haven't", "It hasn't", "It isn't", "They aren't", "It wasn't",
            "They weren't", "We can't", "we cant", "we havent", "it isnt",
        ]
        for text in stated:
            with self.subTest(text=text):
                self.assertTrue(states_deficiency(text))
        neutral = [
            "Customers pay by card on our website",
            "we also have 3 shops with card machines",
            "Our website runs on a hosting company server",
            "A new internal data protection policy was approved and must be implemented within 2 months",
            "Focus on access control to student data and protection of trade secrets",
            "All data is hosted on internal on-premise servers",
            "We take backups once a week to an external hard drive",
            "Our notebook inventory is known", "snowfall", "Nora's cannoli",
        ]
        for text in neutral:
            with self.subTest(text=text):
                self.assertFalse(states_deficiency(text))

    def test_contraction_deficiency_becomes_non_compliant_end_to_end(self):
        from ai_onboarding.pre_assessment_topics import build_candidates

        objective = "We are a small clinic in Irbid with 20 staff. We don't have a documented policy for information security."
        facts, _ = rules.verify_facts(
            [{"quote": "We don't have a documented policy for information security",
              "claim_en": "No documented information security policy.", "topics": ["governance_policy"],
              "certainty": "stated"}],
            objective,
        )
        candidates = build_candidates([{"urn": "p", "assessable": True, "ref_id": "P-1", "key": "p1",
                                        "description": "An information security policy must be documented and approved."}])
        results, _ = rules.plan_fact_results(facts[0], candidates, [
            {"ref_id": "P-1", "relation": "gap_explicit",
             "violated_clause": "An information security policy must be documented and approved"}])
        self.assertEqual([r.outcome.kind for r in results], [rules.KIND_NON_COMPLIANT])

    def test_deficiency_is_checked_on_the_quote_not_the_sentence(self):
        # One sentence, two facts: hosting (neutral) and the admin password (deficiency).
        facts, _ = rules.verify_facts(
            [{"quote": "Our website runs on a hosting company server", "topics": ["third_party_providers"],
              "certainty": "stated"},
             {"quote": "the developer still uses the same admin password since 2022",
              "topics": ["authentication_passwords"], "certainty": "stated"}],
            PETRA,
        )
        self.assertEqual(facts[0].sentence, facts[1].sentence)
        self.assertFalse(facts[0].states_deficiency)
        self.assertTrue(facts[1].states_deficiency)

    def test_uncertainty_in_english_and_arabic(self):
        for text in ("not sure if card numbers are saved", "I think we use AWS", "maybe weekly",
                     "We don't know who has access", "مش متأكد إذا البطاقات محفوظة"):
            with self.subTest(text=text):
                self.assertTrue(is_uncertain(text))
        for text in ("We do not have a documented cybersecurity strategy.",
                     "Employees have never received any security awareness training."):
            with self.subTest(text=text):
                self.assertFalse(is_uncertain(text))


class OutcomeTests(unittest.TestCase):
    def _decide(self, relation, *, uncertain=False, deficiency=True, conditional=False,
                clause="A cybersecurity strategy must be defined", text=ECC_111,
                subject="a cybersecurity strategy", quote="We do not have a documented cybersecurity strategy"):
        return rules.decide_outcome(relation, fact_uncertain=uncertain, fact_states_deficiency=deficiency,
                                    requirement_conditional=conditional, clause=clause, requirement_text=text,
                                    requirement_subject=subject, fact_quote=quote)

    def test_no_stated_deficiency_means_to_be_confirmed(self):
        # Seen in the baseline: "Customers pay by card on our website" -> PCI 6.4.2 Non-compliant.
        for relation in ("gap_explicit", "partial_explicit"):
            with self.subTest(relation=relation):
                self.assertEqual(self._decide(relation, deficiency=False).kind, rules.KIND_TO_BE_CONFIRMED)
        # Not even a Potential gap on a conditional requirement.
        self.assertEqual(self._decide("gap_explicit", deficiency=False, conditional=True).kind,
                         rules.KIND_TO_BE_CONFIRMED)

    def test_mapping_table(self):
        self.assertIsNone(self._decide("not_related"))
        self.assertEqual(self._decide("related_unknown").kind, rules.KIND_TO_BE_CONFIRMED)
        self.assertEqual(self._decide("gap_explicit").kind, rules.KIND_NON_COMPLIANT)
        self.assertEqual(self._decide("partial_explicit").kind, rules.KIND_PARTIAL)
        self.assertEqual(self._decide("gap_explicit", conditional=True).kind, rules.KIND_POTENTIAL_GAP)
        self.assertEqual(self._decide("gap_explicit", uncertain=True).kind, rules.KIND_TO_BE_CONFIRMED)
        self.assertEqual(self._decide("gap_explicit", clause="not in the requirement text").kind,
                         rules.KIND_TO_BE_CONFIRMED)

    def test_compliant_and_not_applicable_can_never_be_produced(self):
        for relation in ("compliant", "not_applicable", "COMPLIANT", "", None, "gap"):
            with self.subTest(relation=relation):
                self.assertIsNone(self._decide(relation))
        for kind in rules.RESULT_FOR_KIND:
            self.assertNotIn(rules.RESULT_FOR_KIND[kind], {"compliant", "not_applicable"})
        self.assertEqual(rules.ALLOWED_RESULTS, {"non_compliant", "partially_compliant", "not_assessed"})

    def test_written_status_is_in_review(self):
        self.assertEqual(self._decide("gap_explicit").status, "in_review")
        self.assertEqual(self._decide("related_unknown").result, "not_assessed")

    def test_caps_and_strongest_result_per_requirement(self):
        def planned(key, fact, rank, kind):
            return rules.PlannedResult(key, key, fact, rank, rules.Outcome(kind, "c" * 20), "s")

        items = [planned(f"r{i}", 0, i, rules.KIND_TO_BE_CONFIRMED) for i in range(5)]
        items.append(planned("r4", 1, 0, rules.KIND_NON_COMPLIANT))
        kept = rules.apply_caps(items)
        self.assertEqual(sum(1 for k in kept if k.fact_index == 0), rules.MAX_RESULTS_PER_FACT)
        r4 = [k for k in kept if k.requirement_key == "r4"]
        self.assertEqual(len(r4), 1)
        self.assertEqual(r4[0].outcome.kind, rules.KIND_NON_COMPLIANT)

        many = [planned(f"x{f}-{r}", f, r, rules.KIND_TO_BE_CONFIRMED) for f in range(6) for r in range(3)]
        self.assertEqual(len(rules.apply_caps(many)), rules.MAX_RESULTS_PER_RUN)


class ObservationTests(unittest.TestCase):
    DAY = date(2026, 11, 25)
    MODEL = "qwen3:4b-instruct"

    def test_templates_contain_only_verified_text(self):
        sentence = "We do not have a documented cybersecurity strategy."
        non = rules.build_observation(rules.Outcome(rules.KIND_NON_COMPLIANT, "A cybersecurity strategy must be defined"),
                                      model=self.MODEL, day=self.DAY, sentence=sentence)
        self.assertEqual(
            non,
            '[SICO AI · qwen3:4b-instruct · 2026-11-25] Non-compliant: requirement says '
            '"A cybersecurity strategy must be defined" — objective says '
            '"We do not have a documented cybersecurity strategy."',
        )
        gap = rules.build_observation(rules.Outcome(rules.KIND_POTENTIAL_GAP, "x" * 20), model=self.MODEL,
                                      day=self.DAY, sentence=sentence)
        self.assertIn("Potential gap: conditional requirement", gap)
        tbc = rules.build_observation(rules.Outcome(rules.KIND_TO_BE_CONFIRMED), model=self.MODEL,
                                      day=self.DAY, sentence=sentence)
        self.assertIn("To be confirmed:", tbc)
        self.assertTrue(tbc.startswith("[SICO AI · qwen3:4b-instruct · 2026-11-25]"))

    def test_long_sentence_is_shortened_on_a_word(self):
        text = "word " * 200
        out = rules.shorten(text)
        self.assertLessEqual(len(out), rules.MAX_QUOTED_CHARS)
        self.assertTrue(out.endswith("…"))
        self.assertFalse(out.endswith(" …"))

    def test_summary_counts(self):
        items = [rules.PlannedResult("a", "a", 0, 0, rules.Outcome(rules.KIND_POTENTIAL_GAP), "s"),
                 rules.PlannedResult("b", "b", 0, 1, rules.Outcome(rules.KIND_TO_BE_CONFIRMED), "s")]
        counts = rules.summarize(items, 351)
        self.assertEqual(counts["potential_gap"], 1)
        self.assertEqual(counts["to_be_confirmed"], 1)
        self.assertEqual(counts["non_compliant"], 0)
        self.assertEqual(counts["not_assessed_untouched"], 349)


class NameAndIdTests(unittest.TestCase):
    def test_organization_name_normalization(self):
        self.assertEqual(rules.normalize_name("  Petra   Online\tStore "), "Petra Online Store")
        self.assertEqual(rules.name_key("PETRA online  store"), rules.name_key("Petra Online Store"))

    def test_perimeter_name(self):
        # No organization name: the platform already shows "<Domain>/<Perimeter>".
        self.assertEqual(
            rules.perimeter_name("Payment Card Industry Data Security Standard (PCI-DSS) 4.0.1", "PCI DSS 4.0.1"),
            "PCI DSS 4.0.1 scope",
        )
        self.assertEqual(
            rules.perimeter_name("Essential Cybersecurity Controls", "essential-cybersecurity-controls"),
            "Essential Cybersecurity Controls scope",
        )
        self.assertEqual(
            rules.perimeter_name("International standard ISO/IEC 27001:2022", "ISO/IEC 27001:2022"),
            "ISO-IEC 27001:2022 scope",  # "/" is refused in a Perimeter name
        )
        self.assertNotIn("/", rules.perimeter_name("x", "Y/Z 1.0"))
        self.assertLessEqual(len(rules.perimeter_name("y" * 250, None)), rules.NAME_MAX_CHARS)

    def test_perimeter_and_audit_descriptions(self):
        sentences = ["Customers pay by card on our website and we also have 3 shops with card machines.",
                     "Customers pay by card on our website and we also have 3 shops with card machines."]
        perimeter = rules.perimeter_description(sentences)
        self.assertEqual(perimeter.count("•"), 1)
        self.assertIn("to be confirmed", perimeter)
        audit = rules.audit_description(model="qwen3:4b-instruct", day=date(2026, 11, 25), sentences=sentences)
        self.assertTrue(audit.startswith("SICO AI Pre-Assessment · qwen3:4b-instruct · 2026-11-25"))
        self.assertIn("not a formal audit", audit)

    def test_next_version(self):
        self.assertEqual(rules.next_version([]), "1.0")
        self.assertEqual(rules.next_version(["1.0"]), "2.0")
        self.assertEqual(rules.next_version(["1.0", "1.1", "2", None, "abc", "v3"]), "4.0")

    def test_next_audit_ref_id(self):
        self.assertEqual(rules.next_audit_ref_id(2026, []), "SICO-AUD-2026-0001")
        self.assertEqual(
            rules.next_audit_ref_id(2026, ["SICO-AUD-2026-0001", "sico-aud-2026-0007", "SICO-AUD-2025-0042",
                                           "SICO-AUD-2026-12", "OTHER-2026-0099", None]),
            "SICO-AUD-2026-0008",
        )
        self.assertEqual(rules.next_audit_ref_id(2027, ["SICO-AUD-2026-0008"]), "SICO-AUD-2027-0001")


class TopicListTests(unittest.TestCase):
    def test_topic_enum_has_twenty_one_topics_and_context_only(self):
        self.assertEqual(len(TOPIC_ENUM), 22)
        self.assertEqual(TOPIC_ENUM[-1], CONTEXT_ONLY)
        self.assertEqual(len(set(TOPIC_ENUM)), len(TOPIC_ENUM))


if __name__ == "__main__":
    unittest.main()
