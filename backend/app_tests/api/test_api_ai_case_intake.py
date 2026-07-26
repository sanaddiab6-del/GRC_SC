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
    Perimeter,
    RequirementAssessment,
    RiskAcceptance,
    RiskAssessment,
    RiskScenario,
    Vulnerability,
)
from iam.models import Folder, User, UserGroup

from ai_onboarding.case_intake_service import build_case_intake_fallback_draft


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
    "Al-Rawasi Fintech is preparing for an ECC-1:2018 readiness review before launching "
    "its Saudi payment services expansion. The scope should cover the payment platform, "
    "IAM, cloud operations, and supporting evidence for the KSA launch window."
)


def _request_payload(**overrides):
    payload = {
        "scenario_text": AL_RAWASI_SCENARIO,
        "preferred_framework": "ECC-1:2018",
        "assessment_period": {
            "label": "Q4 2026 readiness review",
            "start_date": "2026-10-01",
            "end_date": "2026-12-15",
        },
        "organization_hint": "Al-Rawasi Fintech",
        "scope_hint": "Core payment platform, IAM, cloud operations, and supporting evidence for KSA launch",
        "known_deadline": "2026-12-15",
        "known_trigger": "pre-regulatory-readiness review",
        "user_locale": "en",
        "strict_mode": True,
    }
    payload.update(overrides)
    return payload


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    import uuid
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR) / "db" / f"test_ai_case_intake_{uuid.uuid4().hex}.sqlite3"
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


def _counts_snapshot():
    return {
        "Folder": Folder.objects.count(),
        "Perimeter": Perimeter.objects.count(),
        "ComplianceAssessment": ComplianceAssessment.objects.count(),
        "Asset": Asset.objects.count(),
        "AppliedControl": AppliedControl.objects.count(),
        "Vulnerability": Vulnerability.objects.count(),
        "RiskAssessment": RiskAssessment.objects.count(),
        "RiskScenario": RiskScenario.objects.count(),
        "Evidence": Evidence.objects.count(),
        "Finding": Finding.objects.count(),
        "RiskAcceptance": RiskAcceptance.objects.count(),
        "RequirementAssessment": RequirementAssessment.objects.count(),
    }


class FakeProvider:
    available = True

    def __init__(self, payload):
        self.payload = payload

    def build_case_intake_draft(self, request_payload):
        return self.payload


@pytest.mark.django_db
def test_ai_case_intake_requires_authentication(client):
    response = client.post(reverse("ai-case-intake"), _request_payload(), format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_valid_al_rawasi_scenario_returns_draft_structure(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-case-intake"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    for key in (
        "draft_type",
        "schema_version",
        "source_summary",
        "overall_confidence",
        "needs_human_review",
        "blocking_questions",
        "warnings",
        "canonical_mappings_used",
        "case_context",
        "framework_resolution",
        "case_setup_draft",
        "asset_drafts",
        "applied_control_drafts",
        "vulnerability_drafts",
        "risk_assessment_draft",
        "risk_scenario_drafts",
        "requirement_focus_drafts",
        "evidence_expectation_drafts",
        "human_review_checklist",
        "next_system_actions",
    ):
        assert key in body

    assert body["draft_type"] == "AiCaseIntakeDraft"
    assert body["needs_human_review"] is True
    assert body["source_summary"]["provider_mode"] == "provider_not_configured_fallback"
    assert body["case_setup_draft"]["folder_domain_draft"]["platform_entity"] == "Folder"
    assert (
        body["case_setup_draft"]["compliance_assessment_draft"]["platform_entity"]
        == "ComplianceAssessment"
    )
    assert body["framework_resolution"]["candidate_frameworks"][0]["candidate_label"] == "ECC-1:2018"
    assert any(
        mapping["platform_entity"] == "RequirementNode"
        for mapping in body["canonical_mappings_used"]
    )
    assert any(
        warning["code"] == "provider_not_configured_fallback"
        for warning in body["warnings"]
    )


@pytest.mark.django_db
def test_empty_scenario_text_is_rejected(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-case-intake"),
        _request_payload(scenario_text="   "),
        format="json",
    )

    assert response.status_code == 400
    assert "scenario_text" in response.json()


@pytest.mark.django_db
def test_overlong_scenario_text_is_rejected(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-case-intake"),
        _request_payload(scenario_text="A" * 20001),
        format="json",
    )

    assert response.status_code == 400
    assert "scenario_text" in response.json()


@pytest.mark.django_db
def test_invalid_user_locale_falls_back_safely(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-case-intake"),
        _request_payload(user_locale="english-ksa"),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source_summary"]["detected_language"] == "en"
    assert any(warning["code"] == "user_locale_fallback" for warning in body["warnings"])


@pytest.mark.django_db
def test_ai_case_intake_does_not_write_grc_records(authenticated_client):
    before = _counts_snapshot()

    response = authenticated_client.post(
        reverse("ai-case-intake"),
        _request_payload(),
        format="json",
    )

    after = _counts_snapshot()
    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_guardrail_rejects_final_compliance_decision(authenticated_client, monkeypatch):
    invalid_draft = build_case_intake_fallback_draft(_request_payload())
    invalid_draft["requirement_focus_drafts"][0]["status"] = "compliant"
    monkeypatch.setattr(
        "ai_onboarding.case_intake_service.get_case_intake_provider",
        lambda: FakeProvider(invalid_draft),
    )

    response = authenticated_client.post(
        reverse("ai-case-intake"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "ai_draft_guardrails_failed"


@pytest.mark.django_db
def test_guardrail_rejects_risk_acceptance_output(authenticated_client, monkeypatch):
    invalid_draft = build_case_intake_fallback_draft(_request_payload())
    invalid_draft["risk_scenario_drafts"].append(
        {
            "platform_entity": "RiskAcceptance",
            "name": "Residual risk accepted",
            "risk_assessment_dependency": None,
            "linked_asset_refs": [],
            "treatment": "accept",
            "suggested_action": "propose_create",
            "confidence": 0.9,
            "rationale": "Invalid guardrail test payload.",
            "source_text_refs": [
                {"ref_id": "T9", "excerpt": "accept risk", "char_start": 0, "char_end": 11}
            ],
            "needs_review": True,
        }
    )
    monkeypatch.setattr(
        "ai_onboarding.case_intake_service.get_case_intake_provider",
        lambda: FakeProvider(invalid_draft),
    )

    response = authenticated_client.post(reverse("ai-case-intake"), _request_payload(), format="json")

    assert response.status_code == 422
    assert response.json()["error_code"] in {
        "ai_draft_validation_failed",
        "ai_draft_guardrails_failed",
    }


@pytest.mark.django_db
def test_guardrail_rejects_audit_closure(authenticated_client, monkeypatch):
    invalid_draft = build_case_intake_fallback_draft(_request_payload())
    invalid_draft["case_setup_draft"]["compliance_assessment_draft"]["status"] = "closed"
    monkeypatch.setattr(
        "ai_onboarding.case_intake_service.get_case_intake_provider",
        lambda: FakeProvider(invalid_draft),
    )

    response = authenticated_client.post(reverse("ai-case-intake"), _request_payload(), format="json")

    assert response.status_code == 422
    assert response.json()["error_code"] == "ai_draft_guardrails_failed"


@pytest.mark.django_db
def test_invented_platform_entity_is_rejected(authenticated_client, monkeypatch):
    invalid_draft = build_case_intake_fallback_draft(_request_payload())
    invalid_draft["asset_drafts"][0]["platform_entity"] = "AuditCase"
    monkeypatch.setattr(
        "ai_onboarding.case_intake_service.get_case_intake_provider",
        lambda: FakeProvider(invalid_draft),
    )

    response = authenticated_client.post(reverse("ai-case-intake"), _request_payload(), format="json")

    assert response.status_code == 422
    assert response.json()["error_code"] == "ai_draft_validation_failed"


@pytest.mark.django_db
def test_malformed_provider_output_returns_controlled_error(authenticated_client, monkeypatch):
    monkeypatch.setattr(
        "ai_onboarding.case_intake_service.get_case_intake_provider",
        lambda: FakeProvider({"draft_type": "not-a-valid-draft"}),
    )

    response = authenticated_client.post(reverse("ai-case-intake"), _request_payload(), format="json")

    assert response.status_code == 422
    assert response.json()["error_code"] == "ai_draft_validation_failed"


@pytest.mark.django_db
def test_ambiguous_scenario_returns_blocking_questions(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-case-intake"),
        _request_payload(
            scenario_text="We need a review before an upcoming milestone.",
            preferred_framework=None,
            organization_hint=None,
            scope_hint=None,
            known_trigger=None,
        ),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["needs_human_review"] is True
    assert body["blocking_questions"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name, field_value",
    [
        ("compliance_result", "compliant"),
        ("final_compliance_result", "approved"),
        ("audit_closure", True),
        ("close_audit", True),
        ("risk_acceptance", {"decision": "accept"}),
        ("risk_decision", "accept"),
        ("create_now", True),
        ("auto_create", True),
    ],
)
def test_step1_rejects_unsafe_final_decision_like_input_fields(
    authenticated_client,
    field_name,
    field_value,
):
    before = _counts_snapshot()
    payload = _request_payload()
    payload[field_name] = field_value

    response = authenticated_client.post(reverse("ai-case-intake"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 400
    assert field_name in response.json()
    assert before == after