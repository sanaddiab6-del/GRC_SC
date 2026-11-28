"""SICO AI Pre-Assessment extract/judge endpoints with a fake model provider.

Checks the feature flag, one model call per request with no retry, and that the code's
rules (not the model) decide what may be written. No DB writes and no real model calls.
"""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding import pre_assessment_views as views
from ai_onboarding.llm_errors import AiProviderExecutionError
from ai_onboarding.pre_assessment_topics import build_candidates

USER = SimpleNamespace(pk="u1", is_active=True, is_authenticated=True)
FRAMEWORK = SimpleNamespace(id="11111111-1111-1111-1111-111111111111", name="Essential Cybersecurity Controls")
NAJD = (
    "We are a water utility company in Riyadh with 150 employees. We do not have a documented "
    "cybersecurity strategy. Our IT manager is also responsible for cybersecurity because we have "
    "no separate cybersecurity team. Employees have never received any security awareness training. "
    "We are not sure if our vendor uses MFA. We need to comply with ECC this year."
)
NODES = [
    {"urn": "s1", "assessable": False, "ref_id": "1-1", "name": "Cybersecurity Strategy"},
    {"urn": "r1", "parent_urn": "s1", "assessable": True, "ref_id": "1-1-1", "key": "ra-1",
     "description": "A cybersecurity strategy must be defined, documented and approved."},
    {"urn": "r2", "parent_urn": "s1", "assessable": True, "ref_id": "1-1-2", "key": "ra-2",
     "description": "A roadmap must be executed to implement the cybersecurity strategy."},
    {"urn": "r3", "assessable": True, "ref_id": "2-2-3", "key": "ra-3",
     "description": "If remote access is used, multi-factor authentication must be required for remote access."},
]
CONFIG = SimpleNamespace(model="qwen3:4b-instruct", timeout_seconds=600, max_output_tokens=2000)


class FakeProvider:
    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = []

    def generate_structured(self, **kwargs):
        self.calls.append(kwargs)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


def _post(view_class, path, data):
    request = APIRequestFactory().post(path, data, format="json")
    force_authenticate(request, user=USER)
    return view_class.as_view()(request)


class _Base(unittest.TestCase):
    def setUp(self):
        patches = [
            patch.dict(os.environ, {views.FEATURE_FLAG: "true"}),
            patch.object(views, "readable_framework", lambda user, fid: FRAMEWORK),
            patch.object(views, "load_authorized_candidates", lambda user, fw: build_candidates(NODES)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def use_provider(self, provider):
        p = patch.object(views, "provider_selection", lambda: SimpleNamespace(provider=provider, config=CONFIG))
        p.start()
        self.addCleanup(p.stop)
        return provider

    def extract(self, objective=NAJD):
        return _post(views.PreAssessmentExtractView, "/extract/", {
            "framework_id": FRAMEWORK.id, "organization_name": "Najd Water Services", "objective": objective})

    def judge(self, fact, index=0, objective=NAJD):
        return _post(views.PreAssessmentJudgeView, "/judge/", {
            "framework_id": FRAMEWORK.id, "objective": objective, "fact_index": index, "fact": fact})


STRATEGY_FACT = {"quote": "We do not have a documented cybersecurity strategy",
                 "claim_en": "No documented cybersecurity strategy.", "topics": ["governance_policy"],
                 "uncertain": False}


class FlagTests(_Base):
    def test_feature_is_on_by_default(self):
        with patch.dict(os.environ, {}):
            os.environ.pop(views.FEATURE_FLAG, None)
            self.assertTrue(views.pre_assessment_enabled())
        for value in ("", "true", "1", "yes"):
            with self.subTest(value=value), patch.dict(os.environ, {views.FEATURE_FLAG: value}):
                self.assertTrue(views.pre_assessment_enabled())

    def test_emergency_off_switch(self):
        for value in ("false", "FALSE", "0", "no", "off", " false "):
            with self.subTest(value=value), patch.dict(os.environ, {views.FEATURE_FLAG: value}):
                self.assertFalse(views.pre_assessment_enabled())
        provider = self.use_provider(FakeProvider())
        with patch.dict(os.environ, {views.FEATURE_FLAG: "false"}):
            reply = self.extract()
        self.assertEqual(reply.status_code, 403)
        self.assertEqual(reply.data["failure_reason"], "pre_assessment_disabled")
        self.assertEqual(provider.calls, [])

    def test_django_setting_wins_over_environment(self):
        with patch.dict(os.environ, {views.FEATURE_FLAG: "true"}), \
                self.settings_value(False):
            self.assertFalse(views.pre_assessment_enabled())

    def settings_value(self, value):
        return patch.object(views.settings, views.FEATURE_FLAG, value, create=True)


class ExtractTests(_Base):
    def test_one_model_call_and_only_verified_facts(self):
        provider = self.use_provider(FakeProvider({"facts": [
            {"quote": "We do not have a documented cybersecurity strategy", "claim_en": "No strategy.",
             "topics": ["governance_policy"], "certainty": "stated"},
            {"quote": "Our strategy was approved in 2023", "claim_en": "Invented.",
             "topics": ["governance_policy"], "certainty": "stated"},
            {"quote": "We are not sure if our vendor uses MFA", "claim_en": "Vendor MFA unknown.",
             "topics": ["mfa", "third_party_providers"], "certainty": "stated"},
        ]}))
        reply = self.extract()
        self.assertEqual(reply.status_code, 200)
        self.assertEqual(len(provider.calls), 1)
        self.assertEqual(provider.calls[0]["schema_name"], "sico_ai_pre_assessment_facts_v1")
        self.assertIn(NAJD, provider.calls[0]["user_payload"].values())
        quotes = [f["quote"] for f in reply.data["facts"]]
        self.assertEqual(quotes, ["We do not have a documented cybersecurity strategy",
                                  "We are not sure if our vendor uses MFA"])
        self.assertTrue(reply.data["facts"][1]["uncertain"])
        self.assertEqual(reply.data["dropped"][0]["reason"], "quote_not_in_objective")
        self.assertFalse(reply.data["business_records_written"])

    def test_unreadable_framework_is_refused_before_any_model_call(self):
        provider = self.use_provider(FakeProvider())
        with patch.object(views, "readable_framework", lambda user, fid: None):
            reply = self.extract()
        self.assertEqual(reply.status_code, 403)
        self.assertEqual(reply.data["failure_reason"], "framework_unavailable")
        self.assertEqual(provider.calls, [])

    def test_provider_failure_is_reported_once_without_retry(self):
        provider = self.use_provider(FakeProvider(
            AiProviderExecutionError("local_ai_provider_schema_mismatch", "bad"), {"facts": []}))
        reply = self.extract()
        self.assertEqual(reply.status_code, 503)
        self.assertEqual(reply.data["failure_reason"], "local_ai_provider_schema_mismatch")
        self.assertEqual(len(provider.calls), 1)
        self.assertFalse(reply.data["business_records_written"])

    def test_missing_provider_is_reported(self):
        self.use_provider(None)
        reply = self.extract()
        self.assertEqual(reply.status_code, 503)
        self.assertEqual(reply.data["failure_reason"], "provider_unavailable")


class JudgeTests(_Base):
    def test_rules_decide_the_result_not_the_model(self):
        provider = self.use_provider(FakeProvider({"judgements": [
            {"ref_id": "1-1-1", "relation": "gap_explicit",
             "violated_clause": "A cybersecurity strategy must be defined, documented and approved"},
            {"ref_id": "1-1-2", "relation": "compliant", "violated_clause": ""},
            {"ref_id": "9-9-9", "relation": "gap_explicit", "violated_clause": "made up requirement text"},
        ]}))
        reply = self.judge(STRATEGY_FACT, index=1)
        self.assertEqual(reply.status_code, 200)
        self.assertEqual(len(provider.calls), 1)
        self.assertEqual(provider.calls[0]["schema_name"], "sico_ai_pre_assessment_judgement_v1")
        self.assertIn("1-1-1", reply.data["short_list"])
        self.assertEqual(reply.data["fact_index"], 1)
        self.assertEqual(reply.data["results"], [{
            "ref_id": "1-1-1", "rank": reply.data["short_list"].index("1-1-1"), "kind": "non_compliant",
            "result": "non_compliant", "status": "in_review",
            "clause": "A cybersecurity strategy must be defined, documented and approved"}])
        self.assertEqual({i["reason"] for i in reply.data["ignored"]}, {"unknown_relation", "ref_not_in_short_list"})
        self.assertFalse(reply.data["business_records_written"])

    def test_uncertain_fact_can_only_be_to_be_confirmed(self):
        self.use_provider(FakeProvider({"judgements": [
            {"ref_id": "2-2-3", "relation": "gap_explicit",
             "violated_clause": "multi-factor authentication must be required for remote access"},
        ]}))
        # The page claims the fact is certain; the sentence says "not sure".
        reply = self.judge({"quote": "not sure if our vendor uses MFA", "claim_en": "Vendor has no MFA.",
                            "topics": ["mfa"], "uncertain": False})
        self.assertEqual([r["kind"] for r in reply.data["results"]], ["to_be_confirmed"])

    def test_conditional_requirement_becomes_potential_gap(self):
        objective = NAJD + " Our maintenance vendor connects remotely with a password only and no MFA at all."
        self.use_provider(FakeProvider({"judgements": [
            {"ref_id": "2-2-3", "relation": "gap_explicit",
             "violated_clause": "multi-factor authentication must be required for remote access"},
        ]}))
        reply = self.judge({"quote": "connects remotely with a password only and no MFA at all",
                            "claim_en": "Remote vendor access without MFA.", "topics": ["mfa"],
                            "uncertain": False}, objective=objective)
        self.assertEqual([r["kind"] for r in reply.data["results"]], ["potential_gap"])

    def test_fact_not_in_objective_is_refused_without_model_call(self):
        provider = self.use_provider(FakeProvider())
        reply = self.judge({**STRATEGY_FACT, "quote": "We have a documented cybersecurity strategy"})
        self.assertEqual(reply.status_code, 400)
        self.assertEqual(reply.data["failure_reason"], "fact_not_in_objective")
        self.assertEqual(provider.calls, [])

    def test_context_only_fact_needs_no_model_call(self):
        provider = self.use_provider(FakeProvider())
        reply = self.judge({"quote": "We need to comply with ECC this year", "topics": ["context_only"],
                            "uncertain": False})
        self.assertEqual(reply.status_code, 200)
        self.assertEqual(reply.data["results"], [])
        self.assertEqual(provider.calls, [])

    def test_unknown_topic_is_rejected_by_input_validation(self):
        provider = self.use_provider(FakeProvider())
        reply = self.judge({**STRATEGY_FACT, "topics": ["compliant"]})
        self.assertEqual(reply.status_code, 400)
        self.assertEqual(provider.calls, [])

    def test_provider_timeout(self):
        self.use_provider(FakeProvider(TimeoutError()))
        reply = self.judge(STRATEGY_FACT)
        self.assertEqual(reply.status_code, 503)
        self.assertEqual(reply.data["failure_reason"], "provider_timeout")


class ImplementationGroupTests(unittest.TestCase):
    def test_default_groups_follow_the_platform_rule(self):
        framework = SimpleNamespace(implementation_groups_definition=[
            {"ref_id": "Clauses", "name": "Clauses"}, {"ref_id": "SoA", "default_selected": True}])
        self.assertEqual(views.default_implementation_groups(framework), {"SoA"})
        self.assertEqual(views.default_implementation_groups(SimpleNamespace(implementation_groups_definition=None)), set())


if __name__ == "__main__":
    unittest.main()
