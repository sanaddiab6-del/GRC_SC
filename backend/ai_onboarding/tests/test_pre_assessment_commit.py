"""SICO AI Pre-Assessment commit: real database (Django's separate test database).

Domain, Perimeter and Audit creation, version and SICO-AUD numbering, permissions, the
platform's write serializers and the single transaction. No model call.
"""
import os
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from ai_onboarding import pre_assessment_service as service
from ai_onboarding import pre_assessment_views as views

OBJECTIVE = (
    "We are a water utility company in Riyadh with 150 employees. We do not have a documented "
    "cybersecurity strategy. Our maintenance vendor connects remotely with a password only and no "
    "MFA at all. We need to comply with ECC this year."
)
FACTS = [
    {"quote": "We do not have a documented cybersecurity strategy", "claim_en": "No documented cybersecurity strategy.",
     "topics": ["governance_policy"], "uncertain": False},
    {"quote": "connects remotely with a password only and no MFA at all", "claim_en": "Remote access without MFA.",
     "topics": ["mfa"], "uncertain": False},
    {"quote": "We need to comply with ECC this year", "topics": ["context_only"], "uncertain": False},
]
JUDGEMENTS = [
    {"fact_index": 0, "items": [
        {"ref_id": "T-1-1", "relation": "gap_explicit",
         "violated_clause": "A cybersecurity strategy must be defined, documented and approved"},
        {"ref_id": "T-1-2", "relation": "related_unknown", "violated_clause": ""},
        {"ref_id": "T-9-9", "relation": "gap_explicit", "violated_clause": "Visitors are escorted at all times"},
    ]},
    {"fact_index": 1, "items": [
        {"ref_id": "T-2-3", "relation": "gap_explicit",
         "violated_clause": "multi-factor authentication must be required for remote access"},
    ]},
]
ORG = "Najd Water Services"
MODEL = SimpleNamespace(model="qwen3:4b-instruct")


class PreAssessmentCommitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from core.models import Framework, RequirementNode
        from iam.models import Folder, User

        root = Folder.get_root_folder()
        cls.admin = User.objects.create_superuser(f"sico-pa-{uuid4().hex[:8]}@example.test", is_published=True)
        cls.plain_user = User.objects.create_user(f"sico-pa-user-{uuid4().hex[:8]}@example.test", is_published=True)
        cls.framework = Framework.objects.create(
            name="Pre-assessment test framework", ref_id="PA-TEST 1.0", folder=root,
            provider="Unit test", locale="en", default_locale=True, urn=f"urn:test:pa:{uuid4().hex[:8]}",
        )
        nodes = [
            ("s1", None, False, "T-1", "Cybersecurity Strategy", ""),
            ("n1", "s1", True, "T-1-1", "", "A cybersecurity strategy must be defined, documented and approved."),
            ("n2", "s1", True, "T-1-2", "", "A roadmap must be executed to implement the cybersecurity strategy."),
            ("n3", None, True, "T-2-3", "",
             "If remote access is used, multi-factor authentication must be required for remote access."),
            ("n4", None, True, "T-9-9", "", "Visitors are escorted at all times in secure areas."),
        ]
        cls.nodes = {}
        for order, (key, parent, assessable, ref, name, description) in enumerate(nodes):
            urn = f"{cls.framework.urn}:{key}"
            cls.nodes[ref] = RequirementNode.objects.create(
                framework=cls.framework, folder=root, urn=urn,
                parent_urn=f"{cls.framework.urn}:{parent}" if parent else None,
                assessable=assessable, ref_id=ref, name=name or None, description=description or None,
                order_id=order,
            )

    def setUp(self):
        for p in (patch.dict(os.environ, {views.FEATURE_FLAG: "true"}),
                  patch.object(views, "resolve_advisory_capability_config", lambda capability: MODEL)):
            p.start()
            self.addCleanup(p.stop)

    def commit(self, user=None, organization=ORG, facts=FACTS, judgements=JUDGEMENTS, objective=OBJECTIVE):
        request = APIRequestFactory().post("/commit/", {
            "framework_id": str(self.framework.id), "organization_name": organization, "objective": objective,
            "facts": facts, "judgements": judgements}, format="json")
        force_authenticate(request, user=user or self.admin)
        return views.PreAssessmentCommitView.as_view()(request)

    def ra(self, audit_id, ref):
        from core.models import RequirementAssessment
        return RequirementAssessment.objects.get(compliance_assessment_id=audit_id, requirement__ref_id=ref)

    def counts(self):
        from core.models import ComplianceAssessment, Perimeter
        from iam.models import Folder
        return (Folder.objects.count(), Perimeter.objects.count(), ComplianceAssessment.objects.count())

    # ------------------------------------------------------------------ the happy path

    def test_first_run_creates_domain_perimeter_audit_and_results(self):
        from core.models import ComplianceAssessment, Perimeter
        from iam.models import Folder, UserGroup

        reply = self.commit()
        self.assertEqual(reply.status_code, 201, reply.data)
        year = timezone.localdate().year
        self.assertTrue(reply.data["domain"]["created"])
        self.assertTrue(reply.data["perimeter"]["created"])
        self.assertTrue(reply.data["business_records_written"])

        domain = Folder.objects.get(id=reply.data["domain"]["id"])
        self.assertEqual(domain.name, ORG)
        self.assertEqual(domain.content_type, Folder.ContentType.DOMAIN)
        self.assertTrue(domain.create_iam_groups)
        self.assertTrue(UserGroup.objects.filter(folder=domain).exists())

        perimeter = Perimeter.objects.get(id=reply.data["perimeter"]["id"])
        self.assertEqual(perimeter.name, f"{ORG} – PA-TEST 1.0 scope")
        self.assertIn('"We do not have a documented cybersecurity strategy."', perimeter.description)

        audit = ComplianceAssessment.objects.get(id=reply.data["audit"]["id"])
        self.assertEqual((audit.name, audit.version, audit.ref_id, audit.status),
                         (ORG, "1.0", f"SICO-AUD-{year}-0001", "in_progress"))
        self.assertTrue(audit.description.startswith("SICO AI Pre-Assessment · qwen3:4b-instruct ·"))
        self.assertEqual(audit.framework_id, self.framework.id)
        self.assertEqual(audit.perimeter_id, perimeter.id)

        strategy = self.ra(audit.id, "T-1-1")
        self.assertEqual((strategy.result, strategy.status), ("non_compliant", "in_review"))
        self.assertTrue(strategy.observation.startswith("[SICO AI · qwen3:4b-instruct ·"))
        self.assertIn('requirement says "A cybersecurity strategy must be defined, documented and approved"',
                      strategy.observation)
        roadmap = self.ra(audit.id, "T-1-2")
        self.assertEqual((roadmap.result, roadmap.status), ("not_assessed", "in_review"))
        self.assertIn("To be confirmed", roadmap.observation)
        mfa = self.ra(audit.id, "T-2-3")  # conditional requirement
        self.assertEqual((mfa.result, mfa.status), ("not_assessed", "in_review"))
        self.assertIn("Potential gap", mfa.observation)
        visitors = self.ra(audit.id, "T-9-9")  # not in the strategy fact's short list
        self.assertEqual((visitors.result, visitors.status, visitors.observation), ("not_assessed", "to_do", None))

        self.assertEqual(reply.data["summary"]["non_compliant"], 1)
        self.assertEqual(reply.data["summary"]["potential_gap"], 1)
        self.assertEqual(reply.data["summary"]["to_be_confirmed"], 1)
        self.assertEqual(reply.data["summary"]["not_assessed_untouched"], 1)

    def test_second_run_reuses_domain_and_perimeter_with_next_version(self):
        first = self.commit()
        second = self.commit(organization="  najd   WATER services ")
        self.assertEqual(second.status_code, 201, second.data)
        year = timezone.localdate().year
        self.assertEqual(second.data["domain"]["id"], first.data["domain"]["id"])
        self.assertEqual(second.data["perimeter"]["id"], first.data["perimeter"]["id"])
        self.assertFalse(second.data["domain"]["created"])
        self.assertFalse(second.data["perimeter"]["created"])
        self.assertEqual(second.data["audit"]["version"], "2.0")
        self.assertEqual(second.data["audit"]["ref_id"], f"SICO-AUD-{year}-0002")
        self.assertNotEqual(second.data["audit"]["id"], first.data["audit"]["id"])
        # The first audit is not touched by the second run.
        self.assertEqual(self.ra(first.data["audit"]["id"], "T-1-1").result, "non_compliant")

    def test_human_audit_is_untouched_and_counted_for_version_and_number(self):
        from core.models import ComplianceAssessment, Perimeter
        from iam.models import Folder

        root = Folder.get_root_folder()
        domain = Folder.objects.create(name=ORG, parent_folder=root, content_type=Folder.ContentType.DOMAIN)
        perimeter = Perimeter.objects.create(name=f"{ORG} – PA-TEST 1.0 scope", folder=domain,
                                             description="Written by a person.")
        year = timezone.localdate().year
        human = ComplianceAssessment.objects.create(
            name=ORG, version="1.1", ref_id=f"sico-aud-{year}-0007", framework=self.framework,
            folder=domain, perimeter=perimeter, status="in_progress")
        human.create_requirement_assessments()

        reply = self.commit()
        self.assertEqual(reply.status_code, 201, reply.data)
        self.assertEqual(reply.data["domain"]["id"], str(domain.id))
        self.assertEqual(reply.data["perimeter"]["id"], str(perimeter.id))
        self.assertEqual(reply.data["audit"]["version"], "2.0")
        self.assertEqual(reply.data["audit"]["ref_id"], f"SICO-AUD-{year}-0008")
        perimeter.refresh_from_db()
        self.assertEqual(perimeter.description, "Written by a person.")
        self.assertEqual(self.ra(human.id, "T-1-1").result, "not_assessed")
        self.assertEqual(self.ra(human.id, "T-1-1").status, "to_do")

    # ------------------------------------------------------------------ refusals

    def test_user_without_rights_gets_one_message_for_new_and_existing_organization(self):
        from iam.models import Folder

        before = self.counts()
        # The plain user may read the framework here; only the organization is refused.
        original_loader = views.load_authorized_candidates
        with patch.object(views, "readable_framework", lambda user, fid: self.framework), \
                patch.object(views, "load_authorized_candidates",
                             lambda user, fw: original_loader(self.admin, fw)):
            new_org = self.commit(user=self.plain_user, organization="A brand new organization")
            Folder.objects.create(name="Hidden Org", parent_folder=Folder.get_root_folder(),
                                  content_type=Folder.ContentType.DOMAIN)
            before_hidden = self.counts()
            hidden_org = self.commit(user=self.plain_user, organization="hidden org")
        self.assertEqual(new_org.status_code, 403)
        self.assertEqual(hidden_org.status_code, 403)
        self.assertEqual(new_org.data, hidden_org.data)
        self.assertEqual(new_org.data["failure_reason"], "organization_unavailable")
        self.assertNotIn("exist", new_org.data["detail"].lower())
        self.assertEqual(self.counts()[1:], before[1:])
        self.assertEqual(self.counts(), before_hidden)

    def test_failure_in_the_middle_leaves_nothing_behind(self):
        before = self.counts()
        with patch.object(service, "build_observation", side_effect=RuntimeError("boom")):
            reply = self.commit()
        self.assertEqual(reply.status_code, 422)
        self.assertEqual(reply.data["failure_reason"], "transaction_aborted")
        self.assertFalse(reply.data["business_records_written"])
        self.assertEqual(self.counts(), before)

    def test_fact_not_in_objective_is_refused_and_nothing_is_written(self):
        before = self.counts()
        reply = self.commit(facts=[{**FACTS[0], "quote": "We have an approved cybersecurity strategy"}])
        self.assertEqual(reply.status_code, 400)
        self.assertEqual(reply.data["failure_reason"], "fact_not_in_objective")
        self.assertEqual(self.counts(), before)

    def test_compliant_or_not_applicable_from_the_page_is_never_written(self):
        reply = self.commit(judgements=[{"fact_index": 0, "items": [
            {"ref_id": "T-1-1", "relation": "compliant", "violated_clause": ""},
            {"ref_id": "T-1-2", "relation": "not_applicable", "violated_clause": ""},
        ]}])
        self.assertEqual(reply.status_code, 201, reply.data)
        self.assertEqual(reply.data["results"], [])
        for ref in ("T-1-1", "T-1-2"):
            row = self.ra(reply.data["audit"]["id"], ref)
            self.assertEqual((row.result, row.status), ("not_assessed", "to_do"))

    def test_feature_off_writes_nothing(self):
        before = self.counts()
        with patch.dict(os.environ, {views.FEATURE_FLAG: "false"}):
            reply = self.commit()
        self.assertEqual(reply.status_code, 403)
        self.assertEqual(reply.data["failure_reason"], "pre_assessment_disabled")
        self.assertEqual(self.counts(), before)
