import uuid

import pytest
from django.conf import settings as django_settings
from django.urls import reverse
from knox.models import AuthToken

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
    import uuid
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR) / "db" / f"test_ai_case_setup_{uuid.uuid4().hex}.sqlite3"
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
def authenticated_client(app_config):
    admin = User.objects.create_superuser(
        f"admin-{uuid.uuid4().hex[:8]}@tests.com",
        is_published=True,
    )
    admin_group = UserGroup.objects.get(name="BI-UG-ADM")
    admin.folder = admin_group.folder
    admin.save()
    admin_group.user_set.add(admin)

    from rest_framework.test import APIClient

    client = APIClient()
    auth_token = AuthToken.objects.create(user=admin)[1]
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


def _request_payload(framework, risk_matrix=None, **overrides):
    unique_suffix = uuid.uuid4().hex[:8]
    payload = {
        "draft_type": "AiCaseSetupApprovalRequest",
        "schema_version": "0.1.0",
        "approved_by_user": False,
        "source_step1_draft_hash": "sha256:" + "a" * 64,
        "source_step1_schema_version": "0.2.0",
        "dry_run": True,
        "idempotency_key": None,
        "framework_resolution": {
            "requested_framework_name": framework.name,
            "selected_framework_id": str(framework.id),
            "selected_stored_library_urn": None,
            "user_confirmed": True,
            "allow_auto_load": False,
        },
        "folder_domain_decision": {
            "action": "create",
            "platform_entity": "Folder",
            "selected_existing_id": None,
            "proposed_fields": {
                "name": f"AI Step 2 Domain {unique_suffix}",
                "description": "Domain created by the Step 2 setup flow",
                "create_iam_groups": False,
            },
            "human_approved": True,
            "rationale": "Human approved domain setup.",
            "source_reference": "Step 1 draft",
        },
        "perimeter_decision": {
            "action": "create",
            "platform_entity": "Perimeter",
            "selected_existing_id": None,
            "proposed_fields": {
                "name": f"AI Step 2 Perimeter {unique_suffix}",
                "description": "Perimeter for the payment platform",
                "ref_id": f"PER-AI-STEP2-{unique_suffix}",
                "lc_status": "in_prod",
            },
            "human_approved": True,
            "rationale": "Human approved perimeter setup.",
            "source_reference": "Step 1 draft",
        },
        "compliance_assessment_decision": {
            "action": "create",
            "platform_entity": "ComplianceAssessment",
            "selected_existing_id": None,
            "proposed_fields": {
                "name": f"AI Step 2 Compliance Assessment {unique_suffix}",
                "description": "Initial approved compliance assessment",
                "ref_id": f"AUD-AI-STEP2-{unique_suffix}",
                "version": "1.0",
                "status": "planned",
            },
            "human_approved": True,
            "rationale": "Human approved audit setup.",
            "source_reference": "Step 1 draft",
        },
    }
    if risk_matrix is not None:
        payload["risk_assessment_decision"] = {
            "action": "create",
            "platform_entity": "RiskAssessment",
            "selected_existing_id": None,
            "proposed_fields": {
                "name": f"AI Step 2 Risk Assessment {unique_suffix}",
                "description": "Optional risk assessment",
                "ref_id": f"RA-AI-STEP2-{unique_suffix}",
                "version": "1.0",
                "status": "planned",
                "selected_risk_matrix_id": str(risk_matrix.id),
            },
            "human_approved": True,
            "rationale": "Human approved risk assessment setup.",
            "source_reference": "Step 1 draft",
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
def test_ai_case_setup_requires_authentication(client, framework, risk_matrix):
    response = client.post(
        reverse("ai-case-setup"),
        _request_payload(framework, risk_matrix),
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_success_returns_200_and_no_records_are_created(authenticated_client, framework, risk_matrix):
    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-case-setup"),
        _request_payload(framework, risk_matrix),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["operation_type"] == "dry_run"
    assert body["created_objects"] == []
    assert before == after


@pytest.mark.django_db
def test_dry_run_proves_no_write_to_counts(authenticated_client, framework, risk_matrix):
    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-case-setup"),
        _request_payload(framework, risk_matrix),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_write_mode_requires_approval(authenticated_client, framework, risk_matrix):
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=False,
        idempotency_key="trace-1",
    )
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 400
    assert "approved_by_user" in response.json()


@pytest.mark.django_db
def test_write_mode_requires_idempotency_key(authenticated_client, framework, risk_matrix):
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=True,
        idempotency_key=None,
    )
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 400
    assert "idempotency_key" in response.json()


@pytest.mark.django_db
def test_write_mode_requires_source_step1_draft_hash(authenticated_client, framework, risk_matrix):
    payload = _request_payload(framework, risk_matrix)
    payload.pop("source_step1_draft_hash")
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 400
    assert "source_step1_draft_hash" in response.json()


@pytest.mark.django_db
@pytest.mark.parametrize("field_name", ["asset_drafts", "applied_control_drafts", "risk_scenario_drafts"])
def test_rejects_out_of_scope_fields(authenticated_client, framework, risk_matrix, field_name):
    payload = _request_payload(framework, risk_matrix)
    payload[field_name] = [{"name": "forbidden"}]
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 400
    assert field_name in response.json()


@pytest.mark.django_db
def test_rejects_final_compliance_decision(authenticated_client, framework, risk_matrix):
    payload = _request_payload(framework, risk_matrix)
    payload["compliance_assessment_decision"]["proposed_fields"]["result"] = "compliant"
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 400
    assert "result" in response.json()["compliance_assessment_decision"]["proposed_fields"]


@pytest.mark.django_db
def test_rejects_risk_acceptance_field(authenticated_client, framework, risk_matrix):
    payload = _request_payload(framework, risk_matrix)
    payload["risk_acceptance"] = {"decision": "accept"}
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 400
    assert "risk_acceptance" in response.json()


@pytest.mark.django_db
def test_rejects_audit_closure_status(authenticated_client, framework, risk_matrix):
    payload = _request_payload(framework, risk_matrix)
    payload["compliance_assessment_decision"]["proposed_fields"]["status"] = "closed"
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 422
    assert response.json()["blocking_errors"][0]["code"] == "final_status_forbidden"


@pytest.mark.django_db
def test_framework_not_found_returns_blocked_validation_and_no_writes(authenticated_client, framework, risk_matrix):
    payload = _request_payload(framework, risk_matrix)
    payload["framework_resolution"]["selected_framework_id"] = None
    payload["framework_resolution"]["requested_framework_name"] = "Unknown Framework"
    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    after = _counts_snapshot()
    assert response.status_code == 200
    assert response.json()["status"] == "blocked"
    assert before == after


@pytest.mark.django_db
def test_multiple_framework_candidates_returns_ambiguity(authenticated_client, framework, risk_matrix):
    Framework.objects.create(
        folder=Folder.get_root_folder(),
        name=framework.name,
        ref_id="ECC-1:2018-B",
        provider="Local tests",
        locale="en",
        default_locale=True,
    )
    payload = _request_payload(framework, risk_matrix)
    payload["framework_resolution"]["selected_framework_id"] = None
    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    after = _counts_snapshot()
    assert response.status_code == 200
    assert any(item["code"] == "multiple_framework_candidates" for item in response.json()["blocking_errors"])
    assert before == after


@pytest.mark.django_db
def test_valid_write_mode_creates_folder_perimeter_compliance_and_risk(authenticated_client, framework, risk_matrix):
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="trace-create-1",
    )
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 200
    body = response.json()
    assert body["operation_type"] == "create"
    assert any(obj["platform_entity"] == "Folder" for obj in body["created_objects"])
    assert any(obj["platform_entity"] == "Perimeter" for obj in body["created_objects"])
    assert any(obj["platform_entity"] == "ComplianceAssessment" for obj in body["created_objects"])
    assert any(obj["platform_entity"] == "RiskAssessment" for obj in body["created_objects"])


@pytest.mark.django_db
def test_folder_reuse_supported(authenticated_client, framework, risk_matrix):
    existing_folder = Folder.objects.create(name=f"Existing Step 2 Domain {uuid.uuid4().hex[:8]}")
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="trace-reuse-folder",
    )
    payload["folder_domain_decision"] = {
        "action": "reuse",
        "platform_entity": "Folder",
        "selected_existing_id": str(existing_folder.id),
        "human_approved": True,
        "rationale": "Reuse existing domain.",
        "source_reference": "Step 1 draft",
    }
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 200
    assert any(obj["id"] == str(existing_folder.id) for obj in response.json()["reused_objects"])


@pytest.mark.django_db
def test_perimeter_reuse_supported(authenticated_client, framework, risk_matrix):
    existing_folder = Folder.objects.create(name=f"Existing Perimeter Domain {uuid.uuid4().hex[:8]}")
    existing_perimeter = Perimeter.objects.create(
        name=f"Existing Perimeter {uuid.uuid4().hex[:8]}",
        folder=existing_folder,
    )
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="trace-reuse-perimeter",
    )
    payload["folder_domain_decision"] = {
        "action": "reuse",
        "platform_entity": "Folder",
        "selected_existing_id": str(existing_folder.id),
        "human_approved": True,
        "rationale": "Reuse existing domain.",
        "source_reference": "Step 1 draft",
    }
    payload["perimeter_decision"] = {
        "action": "reuse",
        "platform_entity": "Perimeter",
        "selected_existing_id": str(existing_perimeter.id),
        "human_approved": True,
        "rationale": "Reuse existing perimeter.",
        "source_reference": "Step 1 draft",
    }
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 200
    assert any(obj["id"] == str(existing_perimeter.id) for obj in response.json()["reused_objects"])


@pytest.mark.django_db
def test_compliance_assessment_creation_uses_selected_framework_and_perimeter(authenticated_client, framework, risk_matrix):
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="trace-compliance-create",
    )
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 200
    created = ComplianceAssessment.objects.get(
        name=payload["compliance_assessment_decision"]["proposed_fields"]["name"]
    )
    assert created.framework_id == framework.id
    assert created.perimeter.name == payload["perimeter_decision"]["proposed_fields"]["name"]


@pytest.mark.django_db
def test_optional_risk_assessment_creation_only_when_requested(authenticated_client, framework, risk_matrix):
    before = RiskAssessment.objects.count()
    payload = _request_payload(
        framework,
        risk_matrix=None,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="trace-no-risk",
    )
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    assert response.status_code == 200
    assert RiskAssessment.objects.count() == before


@pytest.mark.django_db
def test_transaction_rolls_back_when_late_operation_fails(authenticated_client, framework, risk_matrix, monkeypatch):
    from ai_onboarding.case_setup_service import RiskAssessmentWriteSerializer

    original_save = RiskAssessmentWriteSerializer.save

    def _failing_save(self, **kwargs):
        raise RuntimeError("forced risk assessment failure")

    monkeypatch.setattr(RiskAssessmentWriteSerializer, "save", _failing_save)

    before = _counts_snapshot()
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="trace-rollback",
    )
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    after = _counts_snapshot()
    assert response.status_code == 422
    assert response.json()["status"] == "rolled_back"
    assert before == after


@pytest.mark.django_db
def test_write_mode_does_not_create_out_of_scope_objects(authenticated_client, framework, risk_matrix):
    before = _counts_snapshot()
    payload = _request_payload(
        framework,
        risk_matrix,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="trace-scope-check",
    )
    response = authenticated_client.post(reverse("ai-case-setup"), payload, format="json")
    after = _counts_snapshot()
    assert response.status_code == 200
    for key in ("Asset", "AppliedControl", "Vulnerability", "RiskScenario", "Evidence", "Finding", "RiskAcceptance"):
        assert before[key] == after[key]
    assert after["Folder"] == before["Folder"] + 1
    assert after["Perimeter"] == before["Perimeter"] + 1
    assert after["ComplianceAssessment"] == before["ComplianceAssessment"] + 1
    assert after["RiskAssessment"] == before["RiskAssessment"] + 1
    assert after["RequirementAssessment"] >= before["RequirementAssessment"]