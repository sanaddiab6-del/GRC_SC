"""Disconnected checks + isolated-database tests for the ONLY safe first write."""
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import SimpleTestCase, TestCase

from ai_onboarding.sico_ai_requirement_review_views import (
    MARKER, STAGE, ReviewInput, _format_observation, _save_preliminary_review,
)


class RequirementReviewNoDbTests(SimpleTestCase):
    def test_non_evidence_response_explicitly_unassessed(self):
        text = _format_observation({
            'review_question': 'Confirm if privileged accounts are reviewed by approved personnel.',
            'evidence_request': 'Obtain dated IAM review extracts and sign-off records.',
        })
        self.assertIn(MARKER, text)
        self.assertIn('NOT ASSESSED', text)
        self.assertIn('IAM review extracts', text)

    def test_save_requires_explicit_user_action(self):
        form = ReviewInput(data={'action': 'generate_and_save'})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.validated_data['confirm_preliminary_write'])

    def test_unsupported_action_cannot_validate(self):
        self.assertFalse(ReviewInput(data={'action': 'delete'}).is_valid())

    def test_status_does_not_require_uuid(self):
        form = ReviewInput(data={'action': 'status'})
        self.assertTrue(form.is_valid())
        self.assertNotIn('engagement_id', form.validated_data)


class RequirementReviewTransactionalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from core.models import ComplianceAssessment, Framework, Perimeter, RequirementAssessment, RequirementNode
        from iam.models import Folder, User
        from ai_onboarding.models import Engagement
        root = Folder.get_root_folder()
        cls.folder = Folder.objects.create(name='SICO isolated case', parent_folder=root,
                                          content_type=Folder.ContentType.DOMAIN, create_iam_groups=False)
        cls.user = User.objects.create_superuser(
            f'sico-ai-{uuid4().hex[:8]}@example.test', is_published=True,
        )
        cls.framework = Framework.objects.create(
            name='Isolated example framework', folder=root, provider='Unit test', locale='en', default_locale=True,
        )
        cls.perimeter = Perimeter.objects.create(name='Isolated perimeter', folder=cls.folder)
        cls.case = ComplianceAssessment.objects.create(
            name='Isolated audit', perimeter=cls.perimeter, framework=cls.framework, folder=cls.folder,
        )
        cls.req = RequirementNode.objects.create(
            name='Privileged account review', folder=root, framework=cls.framework,
            assessable=True, ref_id='ISOLATED-1',
        )
        cls.ra = RequirementAssessment.objects.create(
            folder=cls.folder, compliance_assessment=cls.case, requirement=cls.req,
        )
        cls.eng = Engagement.objects.create(
            folder_id=cls.folder.pk, created_by_id=str(cls.user.pk),
            title='Isolated case', objective='Check privileged access control evidence without inventing facts.',
            framework_id=cls.framework.pk, compliance_assessment_id=cls.case.pk,
        )

    def _attempt(self, text):
        request = SimpleNamespace(user=self.user, data={})
        with patch('ai_onboarding.sico_ai_requirement_review_views.authorized_engagement', return_value=self.eng), \
             patch('ai_onboarding.sico_ai_requirement_review_views.verify_principal'), \
             patch('ai_onboarding.sico_ai_requirement_review_views._scoped_case', return_value=self.case), \
             patch('ai_onboarding.sico_ai_requirement_review_views._can_edit', return_value=True), \
             patch('ai_onboarding.sico_ai_requirement_review_views.readable', return_value=True):
            return _save_preliminary_review(request, self.eng, self.case, self.ra.pk, text)

    def test_native_serializer_saves_real_review_once_and_receipt(self):
        from core.models import RequirementAssessment
        from ai_onboarding.models import EngagementExecution
        text = _format_observation({
            'review_question': 'Does this assessment include a sample of dated privileged-access reviews?',
            'evidence_request': 'Obtain approved periodic review reports and the exceptions register.',
        })
        pk = self._attempt(text)
        self.assertEqual(pk, str(self.ra.pk))
        row = RequirementAssessment.objects.get(pk=self.ra.pk)
        self.assertEqual(row.result, RequirementAssessment.Result.NOT_ASSESSED)
        self.assertEqual(row.status, RequirementAssessment.Status.IN_PROGRESS)
        self.assertEqual(row.observation, text)
        self.assertTrue(EngagementExecution.objects.filter(engagement=self.eng, stage=STAGE,
                                                           batch_key=str(row.pk), status='committed').exists())
        with self.assertRaises(ValueError):
            self._attempt('A second attempt must be blocked.')
        row.refresh_from_db()
        self.assertEqual(row.observation, text)

    def test_existing_human_observation_is_not_overwritten(self):
        from core.models import RequirementAssessment
        RequirementAssessment.objects.filter(pk=self.ra.pk).update(observation='Human assessment')
        with self.assertRaises(ValueError):
            self._attempt('New generated text')
        self.ra.refresh_from_db()
        self.assertEqual(self.ra.observation, 'Human assessment')

    def test_human_compliance_verdict_is_not_overwritten(self):
        from core.models import RequirementAssessment
        RequirementAssessment.objects.filter(pk=self.ra.pk).update(
            result=RequirementAssessment.Result.COMPLIANT,
        )
        with self.assertRaises(ValueError):
            self._attempt('This must never replace a human assessment.')
        self.ra.refresh_from_db()
        self.assertEqual(self.ra.result, RequirementAssessment.Result.COMPLIANT)

    def test_unrelated_requirement_id_cannot_be_modified(self):
        from core.models import RequirementAssessment
        request = SimpleNamespace(user=self.user, data={})
        with patch('ai_onboarding.sico_ai_requirement_review_views.authorized_engagement', return_value=self.eng), \
             patch('ai_onboarding.sico_ai_requirement_review_views.verify_principal'), \
             patch('ai_onboarding.sico_ai_requirement_review_views._scoped_case', return_value=self.case), \
             patch('ai_onboarding.sico_ai_requirement_review_views._can_edit', return_value=True), \
             patch('ai_onboarding.sico_ai_requirement_review_views.readable', return_value=True):
            with self.assertRaises(PermissionError):
                _save_preliminary_review(request, self.eng, self.case, uuid4(), 'Cannot create a new row.')
        self.assertEqual(RequirementAssessment.objects.filter(pk=self.ra.pk).count(), 1)
