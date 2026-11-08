import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, "/code")
sys.path.insert(0, "/code/ciso_assistant")

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ciso_assistant.settings"
)

import django
django.setup()

from django.http import Http404

from ai_onboarding.engagement_service import (
    authorized_engagement,
    execute_stage,
    EngagementBlocked,
)
from ai_onboarding.engagement_rules import (
    scope_is_exact,
    human_review_flags,
)


class EngagementSecurityTests(unittest.TestCase):

    def setUp(self):
        self.owner = SimpleNamespace(
            pk=uuid4(),
            is_authenticated=True,
        )
        self.other = SimpleNamespace(
            pk=uuid4(),
            is_authenticated=True,
        )
        self.engagement_id = uuid4()
        self.folder_id = uuid4()

        self.engagement = Mock()
        self.engagement.pk = self.engagement_id
        self.engagement.folder_id = self.folder_id
        self.engagement.created_by_id = str(self.owner.pk)
        self.engagement.compliance_assessment_id = None
        self.engagement.risk_assessment_id = None

    def test_other_user_cannot_read_engagement(self):
        with patch(
            "ai_onboarding.engagement_service.Engagement.objects"
        ) as manager:
            manager.filter.return_value.first.return_value = None

            with self.assertRaises(Http404):
                authorized_engagement(
                    self.other, self.engagement_id
                )

    def test_creator_with_folder_access_can_read(self):
        with patch(
            "ai_onboarding.engagement_service.Engagement.objects"
        ) as manager, patch(
            "ai_onboarding.engagement_service._folder_or_404"
        ), patch(
            "ai_onboarding.engagement_service._scoped_assessment"
        ):
            manager.filter.return_value.first.return_value = (
                self.engagement
            )

            result = authorized_engagement(
                self.owner, self.engagement_id
            )

            self.assertIs(result, self.engagement)

    def test_revoked_folder_access_blocks_creator(self):
        with patch(
            "ai_onboarding.engagement_service.Engagement.objects"
        ) as manager, patch(
            "ai_onboarding.engagement_service._folder_or_404",
            side_effect=Http404("Folder access revoked"),
        ):
            manager.filter.return_value.first.return_value = (
                self.engagement
            )

            with self.assertRaises(Http404):
                authorized_engagement(
                    self.owner, self.engagement_id
                )

    def test_wrong_folder_rejected(self):
        self.assertFalse(
            scope_is_exact(
                {"folder_reference": str(uuid4())},
                self.folder_id,
                "audit_readiness",
            )
        )

    def test_missing_approval_rejected(self):
        self.assertFalse(
            human_review_flags({
                "dry_run": False,
                "approved": False,
            })
        )

        request = SimpleNamespace(user=self.owner)

        with self.assertRaises(EngagementBlocked):
            execute_stage(
                request,
                self.engagement_id,
                stage="audit_readiness",
                batch_key="security-test",
                mode="commit",
                payload={
                    "dry_run": False,
                    "approved": True,
                },
                explicitly_approved=False,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)