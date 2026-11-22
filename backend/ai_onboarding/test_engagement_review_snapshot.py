from types import SimpleNamespace
from unittest.mock import patch
from django.http import Http404
from django.test import SimpleTestCase

from .engagement_rules import reviewed_payload_digest
from .engagement_approval_views import (
    verified_review_snapshot,
    get_prepared_receipt,
)


FOLDER = "11111111-1111-4111-8111-111111111111"
ENGAGEMENT = "22222222-2222-4222-8222-222222222222"


def make_receipt():
    payload = {"folder": FOLDER, "name": "SICO Test Assessment"}
    digest = reviewed_payload_digest(payload)

    review = {
        "engagement_id": ENGAGEMENT,
        "folder_id": FOLDER,
        "stage": "case_setup",
        "batch_key": "test_batch",
        "operation_payload": payload,
        "prepared_digest": digest,
    }

    return SimpleNamespace(
        engagement_id=ENGAGEMENT,
        engagement=SimpleNamespace(folder_id=FOLDER),
        stage="case_setup",
        batch_key="test_batch",
        prepared_digest=digest,
        prepared_result={"_sico_review": review},
    )


class ReviewSnapshotSecurityTests(SimpleTestCase):

    def test_valid_review(self):
        receipt = make_receipt()
        result = verified_review_snapshot(receipt)
        self.assertEqual(result["folder_id"], FOLDER)

    def test_missing_review_rejected(self):
        receipt = make_receipt()
        del receipt.prepared_result["_sico_review"]
        with self.assertRaises(Http404):
            verified_review_snapshot(receipt)

    def test_invalid_review_types_rejected(self):
        for value in (None, [], "invalid"):
            with self.subTest(value=value):
                receipt = make_receipt()
                receipt.prepared_result["_sico_review"] = value
                with self.assertRaises(Http404):
                    verified_review_snapshot(receipt)

    def test_wrong_scope_or_identity_rejected(self):
        for field in (
            "engagement_id",
            "folder_id",
            "stage",
            "batch_key",
            "prepared_digest",
        ):
            with self.subTest(field=field):
                receipt = make_receipt()
                receipt.prepared_result["_sico_review"][field] = "wrong"
                with self.assertRaises(Http404):
                    verified_review_snapshot(receipt)

    def test_changed_business_operation_rejected(self):
        receipt = make_receipt()
        receipt.prepared_result["_sico_review"][
            "operation_payload"
        ]["name"] = "Unauthorized Assessment"

        with self.assertRaises(Http404):
            verified_review_snapshot(receipt)

    def test_invalid_operation_payload_rejected(self):
        receipt = make_receipt()
        receipt.prepared_result["_sico_review"][
            "operation_payload"
        ] = []

        with self.assertRaises(Http404):
            verified_review_snapshot(receipt)

    def test_tampered_receipt_digest_rejected(self):
        receipt = make_receipt()
        receipt.prepared_digest = "f" * 64

        with self.assertRaises(Http404):
            verified_review_snapshot(receipt)

    @patch(
        "ai_onboarding.engagement_approval_views._result_is_blocked",
        return_value=False,
    )
    @patch(
        "ai_onboarding.engagement_approval_views.EngagementExecution.objects.filter"
    )
    @patch(
        "ai_onboarding.engagement_approval_views.authorized_engagement"
    )
    def test_receipt_lookup_rejects_missing_preview(
        self, authorization, query, blocked
    ):
        receipt = make_receipt()
        receipt.prepared_result = {}

        authorization.return_value = receipt.engagement
        query.return_value.first.return_value = receipt

        with self.assertRaises(Http404):
            get_prepared_receipt(
                SimpleNamespace(),
                ENGAGEMENT,
                "case_setup",
                "test_batch",
            )