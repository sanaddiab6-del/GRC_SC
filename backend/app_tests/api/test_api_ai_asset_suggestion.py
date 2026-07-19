import uuid

import pytest
from django.conf import settings as django_settings
from django.urls import reverse
from knox.models import AuthToken

from ai_onboarding.asset_suggestion_service import build_asset_suggestion_fallback_draft
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


AL_RAWASI_SCENARIO = (
    "Al-Rawasi Fintech is preparing for an annual NCA ECC-1:2018 compliance assessment in Q4 2026. "
    "The scope is Core Banking Platform - User Access Management. Known weaknesses include no MFA for remote access, "
    "no PAM for privileged admin accounts, no periodic access review records, and previous review found user access had never been formally reviewed or documented."
)


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR) / "db" / f"test_ai_asset_suggestion_{uuid.uuid4().hex}.sqlite3"
    )


@pytest.fixture(autouse=True)
def app_config():
    original_allowed_hosts = list(django_settings.ALLOWED_HOSTS)
    django_settings.ALLOWED_HOSTS = [*original_allowed_hosts, "testserver"]
    try:
        yield
    finally:
        django_settings.ALLOWED_HOSTS = original_allowed_hosts


@pytest.fixture(autouse=True)
def clear_real_ai_provider_env(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("LOCAL_AI_API_STYLE", raising=False)
    monkeypatch.delenv("LOCAL_AI_BASE_URL", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_DEFAULT", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_CASE_INTAKE", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_ASSET_SUGGESTION", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_APPLIED_CONTROL_SUGGESTION", raising=False)
    monkeypatch.delenv("LOCAL_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("LOCAL_AI_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("LOCAL_AI_TEMPERATURE", raising=False)


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
def setup_context(admin_user, framework, risk_matrix):
    folder = Folder.objects.create(
        name=f"AI Step 3 Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    perimeter = Perimeter.objects.create(
        folder=folder,
        name=f"AI Step 3 Perimeter {uuid.uuid4().hex[:8]}",
        ref_id=f"PER-STEP3-{uuid.uuid4().hex[:8]}",
        description="Step 3 asset suggestion scope perimeter",
        lc_status="in_prod",
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        framework=framework,
        name=f"AI Step 3 Compliance Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    risk_assessment = RiskAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        risk_matrix=risk_matrix,
        name=f"AI Step 3 Risk Assessment {uuid.uuid4().hex[:8]}",
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


def _request_payload(setup_context, **overrides):
    payload = {
        "source_step1_draft_hash": "sha256:" + "c" * 64,
        "case_setup_reference": {
            "folder_id": str(setup_context["folder"].id),
            "perimeter_id": str(setup_context["perimeter"].id),
            "compliance_assessment_id": str(setup_context["compliance_assessment"].id),
            "risk_assessment_id": str(setup_context["risk_assessment"].id),
        },
        "scenario_text": AL_RAWASI_SCENARIO,
        "scope_summary": "Core Banking Platform user access management scope for the Q4 2026 ECC review.",
        "known_weaknesses": [
            "No MFA for remote access",
            "No PAM for privileged admin accounts",
            "No periodic access review records",
        ],
        "selected_framework_id": str(setup_context["framework"].id),
        "user_locale": "en",
        "strict_mode": True,
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


class FakeProvider:
    available = True

    def __init__(self, payload):
        self.payload = payload

    def build_asset_suggestion_draft(self, request_payload):
        return self.payload


@pytest.mark.django_db
def test_ai_asset_suggestion_requires_authentication(client, setup_context):
    response = client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_valid_asset_suggestion_returns_structured_draft(authenticated_client, setup_context):
    response = authenticated_client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["draft_type"] == "AiAssetSuggestionDraft"
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["needs_human_review"] is True
    assert isinstance(body["candidate_assets"], list)
    assert body["candidate_assets"]
    assert "overall_confidence" in body


@pytest.mark.django_db
def test_fallback_returns_expected_asset_candidates(authenticated_client, setup_context):
    response = authenticated_client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    candidate_names = {item["proposed_name"] for item in body["candidate_assets"]}
    assert "Core Banking Application" in candidate_names
    assert "Production User Accounts" in candidate_names
    assert "Identity Provider / IAM System" in candidate_names


@pytest.mark.django_db
def test_asset_suggestion_does_not_write_grc_records(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_rejects_unknown_top_level_fields(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["unexpected_top_level"] = True

    response = authenticated_client.post(reverse("ai-asset-suggestion"), payload, format="json")
    assert response.status_code == 400
    assert "unexpected_top_level" in response.json()


@pytest.mark.django_db
def test_rejects_unknown_nested_fields(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["case_setup_reference"]["unexpected_nested"] = "nope"

    response = authenticated_client.post(reverse("ai-asset-suggestion"), payload, format="json")
    assert response.status_code == 400
    assert "unexpected_nested" in response.json()["case_setup_reference"]


@pytest.mark.django_db
@pytest.mark.parametrize("field_name", ["approved_by_user", "idempotency_key", "create_records"])
def test_rejects_write_intent_fields(authenticated_client, setup_context, field_name):
    payload = _request_payload(setup_context)
    payload[field_name] = True

    response = authenticated_client.post(reverse("ai-asset-suggestion"), payload, format="json")
    assert response.status_code == 400
    assert field_name in response.json()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name",
    [
        "applied_control_drafts",
        "vulnerability_drafts",
        "risk_scenario_drafts",
        "evidence_drafts",
        "risk_acceptance",
    ],
)
def test_rejects_out_of_scope_fields(authenticated_client, setup_context, field_name):
    payload = _request_payload(setup_context)
    payload[field_name] = [{"name": "forbidden"}] if field_name.endswith("_drafts") else {"decision": "accept"}

    response = authenticated_client.post(reverse("ai-asset-suggestion"), payload, format="json")
    assert response.status_code == 400
    assert field_name in response.json()


@pytest.mark.django_db
@pytest.mark.parametrize("field_name", ["compliance_result", "final_result"])
def test_rejects_final_compliance_fields(authenticated_client, setup_context, field_name):
    payload = _request_payload(setup_context)
    payload[field_name] = "compliant"

    response = authenticated_client.post(reverse("ai-asset-suggestion"), payload, format="json")
    assert response.status_code == 400
    assert field_name in response.json()


@pytest.mark.django_db
@pytest.mark.parametrize("field_name, field_value", [("audit_closure", True), ("status", "closed")])
def test_rejects_audit_closure_fields(authenticated_client, setup_context, field_name, field_value):
    payload = _request_payload(setup_context)
    payload[field_name] = field_value

    response = authenticated_client.post(reverse("ai-asset-suggestion"), payload, format="json")
    assert response.status_code == 400
    assert field_name in response.json()


@pytest.mark.django_db
def test_ambiguous_candidates_are_flagged(authenticated_client, setup_context):
    response = authenticated_client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    ambiguous = {item["proposed_name"]: item for item in body["candidate_assets"] if item["ambiguity_flags"]}
    assert "Access Review Records" in ambiguous or "IAM Policies and Procedures" in ambiguous


@pytest.mark.django_db
def test_candidate_actions_are_review_safe_only(authenticated_client, setup_context):
    response = authenticated_client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    safe_actions = {
        "accept_for_later_commit",
        "edit_before_commit",
        "reuse_existing_asset",
        "reject",
        "mark_as_evidence_candidate",
        "mark_as_control_candidate",
        "mark_as_vulnerability_candidate",
        "defer",
    }
    for item in body["candidate_assets"]:
        assert set(item["allowed_next_actions"]).issubset(safe_actions)
        assert "create_now" not in item["allowed_next_actions"]
        assert "auto_create" not in item["allowed_next_actions"]


@pytest.mark.django_db
def test_duplicate_detection_returns_duplicate_candidates(authenticated_client, setup_context):
    Asset.objects.create(
        folder=setup_context["folder"],
        name="Core Banking Application",
        type=Asset.Type.PRIMARY,
        description="Existing folder-scoped asset",
    )

    response = authenticated_client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["duplicate_candidates"]
    assert any(item["proposed_name"] == "Core Banking Application" for item in body["duplicate_candidates"])


@pytest.mark.django_db
def test_malformed_provider_output_is_rejected(authenticated_client, setup_context, monkeypatch):
    monkeypatch.setattr(
        "ai_onboarding.asset_suggestion_service.get_asset_suggestion_provider",
        lambda: FakeProvider({"draft_type": "AiAssetSuggestionDraft"}),
    )

    response = authenticated_client.post(
        reverse("ai-asset-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] in {
        "ai_asset_suggestion_draft_validation_failed",
        "ai_asset_suggestion_guardrails_failed",
    }