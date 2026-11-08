"""Database-backed SICO case setup checks.

Run only against the isolated sico_integration_test database.
No production or historical database may be used.
"""

import unittest
import uuid

from django.conf import settings
from django.db import connection, transaction
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from iam.models import Folder, Permission, Role, RoleAssignment, User
from core.models import (
    Framework, RequirementNode, Perimeter, ComplianceAssessment
)
from ai_onboarding.models import Engagement, EngagementExecution
from ai_onboarding.sico_case_setup_views import (
    SicoCaseSetupAutoPrepareView
)


class SicoCaseSetupDatabaseIntegrationTests(unittest.TestCase):

    def test_actual_api_scope_receipt_and_dry_run(self):
        expected = {
            "NAME": "sico_integration_test",
            "USER": "sico_integration_user",
            "HOST": "sico-ai-integration-postgres",
            "PORT": "5432",
        }

        config = settings.DATABASES["default"]

        for key, value in expected.items():
            self.assertEqual(
                str(config.get(key)), value,
                "Refusing an unexpected database configuration"
            )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user"
            )
            self.assertEqual(
                cursor.fetchone(),
                (expected["NAME"], expected["USER"]),
            )

        original_engagements = Engagement.objects.count()
        original_receipts = EngagementExecution.objects.count()

        # Deliberately use a single rollback-only transaction.
        with transaction.atomic():
            try:
                marker = uuid.uuid4().hex[:10]
                root = Folder.get_root_folder()

                authorized_folder = Folder.objects.create(
                    name="SICO authorized " + marker,
                    content_type=Folder.ContentType.DOMAIN,
                    parent_folder=root,
                    builtin=False,
                )

                other_folder = Folder.objects.create(
                    name="SICO other company " + marker,
                    content_type=Folder.ContentType.DOMAIN,
                    parent_folder=root,
                    builtin=False,
                )

                framework = Framework.objects.create(
                    name="SICO integration framework " + marker,
                    urn="urn:sico:regression:" + marker,
                    ref_id="SICO-" + marker,
                    folder=authorized_folder,
                )

                RequirementNode.objects.create(
                    framework=framework,
                    folder=authorized_folder,
                    name="Integration control",
                    urn="urn:sico:control:" + marker,
                    ref_id="TEST-1",
                    assessable=True,
                )

                owner = User.objects.create_user(
                    "sico-owner-" + marker + "@tests.invalid",
                    is_published=True,
                )

                outsider = User.objects.create_user(
                    "sico-other-" + marker + "@tests.invalid",
                    is_published=True,
                )

                role = Role.objects.create(
                    name="SICO permitted role " + marker
                )

                role.permissions.set(
                    Permission.objects.filter(codename__in=[
                        "view_folder",
                        "view_framework",
                        "add_perimeter",
                        "view_perimeter",
                        "add_complianceassessment",
                        "view_complianceassessment",
                    ])
                )

                owner_assignment = RoleAssignment.objects.create(
                    user=owner,
                    role=role,
                    folder=authorized_folder,
                    is_recursive=True,
                )
                owner_assignment.perimeter_folders.add(
                    authorized_folder
                )

                outsider_assignment = RoleAssignment.objects.create(
                    user=outsider,
                    role=role,
                    folder=other_folder,
                    is_recursive=True,
                )
                outsider_assignment.perimeter_folders.add(
                    other_folder
                )

                engagement = Engagement.objects.create(
                    folder_id=authorized_folder.pk,
                    created_by_id=str(owner.pk),
                    title="SICO integration test",
                    objective=(
                        "Assess cybersecurity compliance "
                        "controls and operational risks"
                    ),
                    framework_id=framework.pk,
                )

                url = reverse(
                    "sico-engagement-case-setup-auto-prepare",
                    kwargs={"engagement_id": engagement.pk},
                )
                factory = APIRequestFactory()

                def post_as(user, data):
                    request = factory.post(
                        url, data, format="json"
                    )
                    force_authenticate(request, user=user)
                    return SicoCaseSetupAutoPrepareView.as_view()(
                        request,
                        engagement_id=engagement.pk,
                    )

                payload = {"batch_key": "db_regression_01"}

                # User has a legitimate role in a different
                # organization but no access to this engagement.
                denied = post_as(outsider, payload)
                self.assertEqual(denied.status_code, 404)

                self.assertFalse(
                    EngagementExecution.objects.filter(
                        engagement=engagement
                    ).exists()
                )

                # No caller-controlled ID or approval bypass.
                invalid = post_as(owner, {
                    "batch_key": "db_regression_01",
                    "explicitly_approved": True,
                })
                self.assertEqual(invalid.status_code, 400)

                first = post_as(owner, payload)
                self.assertEqual(
                    first.status_code, 200,
                    getattr(first, "data", None)
                )

                self.assertEqual(
                    first.data["preparation"]["mode"],
                    "dry_run",
                )

                receipt = EngagementExecution.objects.get(
                    engagement=engagement,
                    stage="case_setup",
                    batch_key="db_regression_01",
                )

                self.assertEqual(receipt.status, "prepared")
                self.assertIn(
                    receipt.prepared_result.get("status"),
                    ("validated", "passed_with_warnings"),
                )
                self.assertFalse(receipt.committed_digest)
                self.assertFalse(receipt.approved_by_id)

                repeated = post_as(owner, payload)
                self.assertEqual(repeated.status_code, 200)

                self.assertEqual(
                    EngagementExecution.objects.filter(
                        engagement=engagement,
                        stage="case_setup",
                        batch_key="db_regression_01",
                    ).count(),
                    1,
                )

                self.assertEqual(
                    Perimeter.objects.filter(
                        folder=authorized_folder
                    ).count(),
                    0,
                )
                self.assertEqual(
                    ComplianceAssessment.objects.filter(
                        folder=authorized_folder
                    ).count(),
                    0,
                )

                print(
                    "REAL API, CROSS-FOLDER DENIAL, "
                    "RECEIPT AND DRY RUN: PASSED",
                    flush=True,
                )

            finally:
                transaction.set_rollback(True)

        self.assertEqual(
            Engagement.objects.count(),
            original_engagements,
        )
        self.assertEqual(
            EngagementExecution.objects.count(),
            original_receipts,
        )

        print(
            "TEST FIXTURE ROLLBACK: VERIFIED",
            flush=True,
        )