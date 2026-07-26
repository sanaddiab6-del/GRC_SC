import uuid

import pytest
from django.conf import settings as django_settings
from django.urls import reverse
from knox.models import AuthToken

from ai_onboarding.asset_commit_service import AiAssetCommitService
from core import startup as core_startup
from core.models import (
    AppliedControl,
    Asset,
    ComplianceAssessment,
    Evidence,
    Finding,
    Framework,
    Perimeter,
    RequirementAssessment,
    RiskAcceptance,
    RiskAssessment,
    RiskMatrix,
    RiskScenario,
    Vulnerability,
)
from iam.models import Folder, User, UserGroup

from test_fixtures import RISK_MATRIX_JSON_DEFINITION


_ORIGINAL_STARTUP_CALL_COMMAND = core_startup.call_command


def _patched_startup_call_command(name, *args, **kwargs):
    if name in {
        "storelibraries",
        "autoloadlibraries",
        "sync_event_types",
        "backfill_builtin_metrics",
    }:
        return None
    return _ORIGINAL_STARTUP_CALL_COMMAND(name, *args, **kwargs)


core_startup.call_command = _patched_startup_call_command


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR) / "db" / f"test_ai_asset_commit_{uuid.uuid4().hex}.sqlite3"
    )


@pytest.fixture(autouse=True)
def app_config():
    original_allowed_hosts = list(django_settings.ALLOWED_HOSTS)
    django_settings.ALLOWED_HOSTS = [*original_allowed_hosts, "testserver"]
    try:
        yield
    finally:
        django_settings.ALLOWED_HOSTS = original_allowed_hosts


@pytest.fixture
def admin_user(app_config):
    admin = User.objects.create_superuser(
        f"admin-{uuid.uuid4().hex[:8]}@tests.com",
        is_published=True,
    )
    admin_group = UserGroup.objects.get(name="BI-UG-ADM")
    admin.folder = admin_group.folder
    admin.save()
    admin_group.user_set.add(admin)
    return admin


@pytest.fixture
def authenticated_client(admin_user):
    from rest_framework.test import APIClient

    client = APIClient()
    auth_token = AuthToken.objects.create(user=admin_user)[1]
    client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token}")
    return client


@pytest.fixture
def framework():
    root_folder = Folder.get_root_folder()
    return Framework.objects.create(
        folder=root_folder,
        name="SAMA ECC-1:2018",
        ref_id="ECC-1:2018",
        provider="Local tests",
        locale="en",
        default_locale=True,
    )


@pytest.fixture
def risk_matrix():
    root_folder = Folder.get_root_folder()
    return RiskMatrix.objects.create(
        folder=root_folder,
        name="Standard 5x5 Matrix",
        ref_id="RM-5X5",
        provider="Local tests",
        locale="en",
        default_locale=True,
        json_definition=RISK_MATRIX_JSON_DEFINITION,
    )


@pytest.fixture
def setup_context(framework, risk_matrix):
    folder = Folder.objects.create(
        name=f"AI Step 3B Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    perimeter = Perimeter.objects.create(
        folder=folder,
        name=f"AI Step 3B Perimeter {uuid.uuid4().hex[:8]}",
        ref_id=f"PER-STEP3B-{uuid.uuid4().hex[:8]}",
        description="Step 3B asset commit scope perimeter",
        lc_status="in_prod",
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        framework=framework,
        name=f"AI Step 3B Compliance Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    risk_assessment = RiskAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        risk_matrix=risk_matrix,
        name=f"AI Step 3B Risk Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    return {
        "folder": folder,
        "perimeter": perimeter,
        "compliance_assessment": compliance_assessment,
        "risk_assessment": risk_assessment,
        "framework": framework,
    }


def _case_setup_reference(setup_context):
    return {
        "folder_id": str(setup_context["folder"].id),
        "perimeter_id": str(setup_context["perimeter"].id),
        "compliance_assessment_id": str(setup_context["compliance_assessment"].id),
        "risk_assessment_id": str(setup_context["risk_assessment"].id),
        "selected_framework_id": str(setup_context["framework"].id),
    }


def _create_decision(*, temporary_id="AST-CAND-001", name="Core Banking Application", **overrides):
    decision = {
        "temporary_id": temporary_id,
        "action": "create",
        "human_approved": True,
        "approved_fields": {
            "name": name,
            "type": "PR",
            "description": "Primary banking application in approved scope.",
            "ref_id": f"AST-{uuid.uuid4().hex[:8].upper()}",
            "reference_link": "https://example.local/assets/core-banking",
            "observation": "Approved after Step 3A review.",
        },
        "original_suggestion_summary": {
            "proposed_name": name,
            "proposed_asset_type": {"value": "PR", "label": "Primary"},
            "confidence": 0.92,
            "ambiguity_flags": [],
        },
        "reviewer_notes": "Confirmed asset candidate.",
        "ambiguity_resolution": None,
        "duplicate_resolution": None,
    }
    decision.update(overrides)
    return decision


def _reuse_decision(existing_asset, **overrides):
    decision = {
        "temporary_id": "AST-CAND-006",
        "action": "reuse",
        "human_approved": True,
        "selected_existing_asset_id": str(existing_asset.id),
        "approved_fields": None,
        "original_suggestion_summary": {
            "proposed_name": existing_asset.name,
            "confidence": 0.88,
            "ambiguity_flags": [],
        },
        "reviewer_notes": "Reuse existing asset.",
        "ambiguity_resolution": None,
        "duplicate_resolution": {"decision": "reuse_existing", "reviewed_match_ids": [str(existing_asset.id)]},
    }
    decision.update(overrides)
    return decision


def _request_payload(setup_context, **overrides):
    payload = {
        "dry_run": True,
        "approved_by_user": False,
        "idempotency_key": None,
        "source_step1_draft_hash": "sha256:" + "d" * 64,
        "source_asset_draft_hash": "sha256:" + "e" * 64,
        "case_setup_reference": _case_setup_reference(setup_context),
        "asset_decisions": [_create_decision()],
    }
    payload.update(overrides)
    return payload


def _counts_snapshot():
    return {
        "Folder": Folder.objects.count(),
        "Perimeter": Perimeter.objects.count(),
        "ComplianceAssessment": ComplianceAssessment.objects.count(),
        "RequirementAssessment": RequirementAssessment.objects.count(),
        "Asset": Asset.objects.count(),
        "AppliedControl": AppliedControl.objects.count(),
        "Vulnerability": Vulnerability.objects.count(),
        "RiskAssessment": RiskAssessment.objects.count(),
        "RiskScenario": RiskScenario.objects.count(),
        "Evidence": Evidence.objects.count(),
        "Finding": Finding.objects.count(),
        "RiskAcceptance": RiskAcceptance.objects.count(),
    }


@pytest.mark.django_db
def test_ai_asset_commit_requires_authentication(client, setup_context):
    response = client.post(reverse("ai-asset-commit"), _request_payload(setup_context), format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_success_returns_200_and_planned_actions(authenticated_client, setup_context):
    response = authenticated_client.post(
        reverse("ai-asset-commit"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["operation_type"] == "dry_run"
    assert body["created_assets"] == []
    assert body["planned_actions"]
    assert body["blocking_errors"] == []


@pytest.mark.django_db
def test_dry_run_proves_no_write_to_counts(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-asset-commit"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_write_mode_requires_approval(authenticated_client, setup_context):
    payload = _request_payload(setup_context, dry_run=False, approved_by_user=False, idempotency_key="asset-commit-1")
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    assert response.status_code == 400
    assert "approved_by_user" in response.json()


@pytest.mark.django_db
def test_write_mode_requires_idempotency_key(authenticated_client, setup_context):
    payload = _request_payload(setup_context, dry_run=False, approved_by_user=True, idempotency_key=None)
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    assert response.status_code == 400
    assert "idempotency_key" in response.json()


@pytest.mark.django_db
def test_missing_source_step1_draft_hash_fails(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload.pop("source_step1_draft_hash")
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    assert response.status_code == 400
    assert "source_step1_draft_hash" in response.json()


@pytest.mark.django_db
def test_missing_source_asset_draft_hash_fails(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload.pop("source_asset_draft_hash")
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    assert response.status_code == 400
    assert "source_asset_draft_hash" in response.json()


@pytest.mark.django_db
def test_missing_folder_id_fails(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["case_setup_reference"].pop("folder_id")
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    assert response.status_code == 400
    assert "folder_id" in response.json()["case_setup_reference"]


@pytest.mark.django_db
def test_empty_asset_decisions_fails(authenticated_client, setup_context):
    payload = _request_payload(setup_context, asset_decisions=[])
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    assert response.status_code == 400
    assert "asset_decisions" in response.json()


@pytest.mark.django_db
def test_create_approved_asset(authenticated_client, setup_context):
    before = _counts_snapshot()
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-create-1",
    )
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["operation_type"] == "create"
    assert body["created_assets"]
    assert len(body["created_assets"]) == 1
    assert after["Asset"] == before["Asset"] + 1
    for key, value in before.items():
        if key == "Asset":
            continue
        assert after[key] == value


@pytest.mark.django_db
def test_reuse_existing_asset_does_not_update_it(authenticated_client, setup_context):
    existing_asset = Asset.objects.create(
        folder=setup_context["folder"],
        name="Identity Provider / IAM System",
        type="SP",
        ref_id="IAM-001",
        observation="Before reuse",
    )
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-reuse-1",
        asset_decisions=[_reuse_decision(existing_asset)],
    )
    before_updated_at = existing_asset.updated_at

    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    existing_asset.refresh_from_db()

    assert response.status_code == 200
    body = response.json()
    assert body["created_assets"] == []
    assert len(body["reused_assets"]) == 1
    assert body["reused_assets"][0]["asset_id"] == str(existing_asset.id)
    assert existing_asset.observation == "Before reuse"
    assert existing_asset.updated_at == before_updated_at


@pytest.mark.django_db
def test_reject_decision_creates_nothing(authenticated_client, setup_context):
    before = _counts_snapshot()
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-reject-1",
        asset_decisions=[
            _create_decision(
                action="reject",
                approved_fields=None,
                selected_existing_asset_id=None,
            )
        ],
    )
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    assert response.json()["created_assets"] == []
    assert before == after


@pytest.mark.django_db
def test_defer_decision_creates_nothing(authenticated_client, setup_context):
    before = _counts_snapshot()
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-defer-1",
        asset_decisions=[
            _create_decision(
                action="defer",
                approved_fields=None,
                selected_existing_asset_id=None,
            )
        ],
    )
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    assert response.json()["created_assets"] == []
    assert before == after


@pytest.mark.django_db
def test_duplicate_detection_in_dry_run_returns_warning(authenticated_client, setup_context):
    Asset.objects.create(folder=setup_context["folder"], name="Core Banking Application", type="PR")
    response = authenticated_client.post(reverse("ai-asset-commit"), _request_payload(setup_context), format="json")

    assert response.status_code == 200
    warnings = response.json()["warnings"]
    assert any(item["code"] == "duplicate_candidate_detected" for item in warnings)


@pytest.mark.django_db
def test_duplicate_blocking_in_write_mode_without_explicit_resolution_fails(authenticated_client, setup_context):
    Asset.objects.create(folder=setup_context["folder"], name="Core Banking Application", type="PR")
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-duplicate-1",
    )
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 409
    assert any(item["code"] == "duplicate_conflict" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_duplicate_create_with_create_anyway_resolution_still_fails(authenticated_client, setup_context):
    Asset.objects.create(folder=setup_context["folder"], name="Core Banking Application", type="PR")
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-duplicate-2",
    )
    payload["asset_decisions"][0]["duplicate_resolution"] = {
        "decision": "create_anyway",
        "reviewed_match_ids": [],
    }
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 409
    assert any(item["code"] == "duplicate_conflict" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_ambiguous_candidate_requires_resolution_in_write_mode(authenticated_client, setup_context):
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-ambiguous-1",
    )
    payload["asset_decisions"][0]["original_suggestion_summary"]["ambiguity_flags"] = [
        {"code": "asset_or_evidence", "message": "Needs human classification."}
    ]
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 422
    assert any(item["code"] == "ambiguity_resolution_required" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_invalid_existing_asset_reuse_id_fails(authenticated_client, setup_context):
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-reuse-missing-1",
        asset_decisions=[
            _reuse_decision(type("Dummy", (), {"id": uuid.uuid4(), "name": "Ghost"})(), selected_existing_asset_id=str(uuid.uuid4()))
        ],
    )
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 422
    assert any(item["code"] == "asset_not_found" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
@pytest.mark.parametrize("field_name, value", [("criticality", {"value": "high"}), ("status", "closed"), ("tags", ["pci"]), ("perimeter_id", str(uuid.uuid4()))])
def test_unsupported_asset_field_rejected(authenticated_client, setup_context, field_name, value):
    payload = _request_payload(setup_context)
    payload["asset_decisions"][0]["approved_fields"][field_name] = value
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 400
    assert field_name in response.json()["asset_decisions"][0]["approved_fields"]


@pytest.mark.django_db
def test_unknown_top_level_fields_rejected(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["unexpected_top_level"] = True
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 400
    assert "unexpected_top_level" in response.json()


@pytest.mark.django_db
def test_unknown_nested_fields_rejected(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["case_setup_reference"]["unexpected_nested"] = "nope"
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 400
    assert "unexpected_nested" in response.json()["case_setup_reference"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name, value",
    [
        ("applied_control_drafts", [{"name": "forbidden"}]),
        ("evidence_drafts", [{"name": "forbidden"}]),
        ("vulnerability_drafts", [{"name": "forbidden"}]),
        ("risk_scenario_drafts", [{"name": "forbidden"}]),
    ],
)
def test_forbidden_non_asset_payload_fields_rejected(authenticated_client, setup_context, field_name, value):
    payload = _request_payload(setup_context)
    payload[field_name] = value
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 400
    assert field_name in response.json()


@pytest.mark.django_db
def test_final_compliance_decision_rejected(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["compliance_result"] = "compliant"
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 400
    assert "compliance_result" in response.json()


@pytest.mark.django_db
def test_risk_acceptance_rejected(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["risk_acceptance"] = {"decision": "accept"}
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 400
    assert "risk_acceptance" in response.json()


@pytest.mark.django_db
def test_audit_closure_rejected(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["audit_closure"] = True
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")

    assert response.status_code == 400
    assert "audit_closure" in response.json()


@pytest.mark.django_db
def test_transaction_rollback(authenticated_client, setup_context, monkeypatch):
    decisions = [
        _create_decision(temporary_id="AST-CAND-001", name="Asset One"),
        _create_decision(temporary_id="AST-CAND-002", name="Asset Two"),
    ]
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-rollback-1",
        asset_decisions=decisions,
    )
    before = Asset.objects.count()

    original_create = AiAssetCommitService._create_asset_from_plan
    call_count = {"value": 0}

    def patched_create(self, plan):
        call_count["value"] += 1
        asset = original_create(self, plan)
        if call_count["value"] == 2:
            raise RuntimeError("forced rollback")
        return asset

    monkeypatch.setattr(AiAssetCommitService, "_create_asset_from_plan", patched_create)

    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    after = Asset.objects.count()

    assert response.status_code == 422
    assert response.json()["status"] == "rolled_back"
    assert after == before


@pytest.mark.django_db
def test_no_out_of_scope_objects_created_in_write_mode(authenticated_client, setup_context):
    before = _counts_snapshot()
    payload = _request_payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="asset-commit-scope-1",
    )
    response = authenticated_client.post(reverse("ai-asset-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    assert after["Asset"] == before["Asset"] + 1
    for key, value in before.items():
        if key == "Asset":
            continue
        assert after[key] == value