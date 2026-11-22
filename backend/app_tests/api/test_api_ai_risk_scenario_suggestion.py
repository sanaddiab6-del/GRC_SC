import json
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


AL_RAWASI_CASE_SUMMARY = (
    "Al-Rawasi Fintech is preparing for its annual SAMA ECC-1:2018 compliance assessment in Q4 2026. "
    "The scope is Core Banking Platform - User Access Management. Known weaknesses include no MFA for "
    "remote access and no PAM for privileged admin accounts."
)


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_ai_risk_scenario_suggestion_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_RISK_SCENARIO_SUGGESTION", raising=False)
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


def _request_payload(**overrides):
    payload = {
        "case_summary": AL_RAWASI_CASE_SUMMARY,
        "scenario_name": "Core Banking Platform - User Access Management",
        "folder_reference": {
            "folder_id": str(uuid.uuid4()),
            "folder_name": "Al-Rawasi Fintech",
        },
        "assessment_reference": {
            "assessment_id": str(uuid.uuid4()),
            "assessment_name": "Q4 2026 ECC Compliance Assessment",
        },
        "assets": [
            {
                "reference": "AST-CBP-001",
                "title": "Core Banking Platform",
                "description": "Primary core banking platform.",
            }
        ],
        "applied_controls": [
            {
                "reference": "CTL-MFA-001",
                "title": "Multi-Factor Authentication for Remote Access",
                "description": "Require MFA for remote access.",
            }
        ],
        "evidence_requests": [
            {"reference": "EVR-CAND-001", "title": "MFA configuration evidence"}
        ],
        "audit_questions": [
            {"reference": "AUQ-CAND-001", "title": "How is MFA enforced for remote access?"}
        ],
        "preliminary_findings": [
            {
                "reference": "FND-CAND-001",
                "title": "MFA is not documented or not enforced for remote access.",
                "description": "Remote access to the Core Banking Platform is not evidenced as MFA protected.",
            }
        ],
        "remediation_actions": [
            {
                "reference": "REM-CAND-001",
                "title": "Implement and enforce MFA for remote access",
            }
        ],
        "framework_mappings": [
            {
                "reference": "urn:sama:ecc:3.3.5",
                "code": "3.3.5",
                "title": "SAMA control 3.3.5",
            }
        ],
        "known_weaknesses": [
            "No MFA for remote access",
            "No PAM for privileged admin accounts",
        ],
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


class _MockHttpResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _configure_local_provider_env(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_AI_API_STYLE", "ollama")
    monkeypatch.setenv("LOCAL_AI_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("LOCAL_AI_MODEL_DEFAULT", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_MODEL_RISK_SCENARIO_SUGGESTION", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_mock_ollama_urlopen(monkeypatch, handler):
    def _mock_urlopen(request, timeout=0):
        request_body = json.loads(request.data.decode("utf-8"))
        response_payload = handler(request, timeout, request_body)
        return _MockHttpResponse(response_payload)

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _valid_provider_scenario(**overrides):
    scenario = {
        "temporary_id": "risk_scenario_1",
        "title": "Unauthorized remote access to the Core Banking Platform",
        "description": (
            "Weak or missing MFA enforcement could allow an actor to reach the Core Banking "
            "Platform over remote access channels."
        ),
        "asset_reference": "AST-CBP-001",
        "asset_title": "Core Banking Platform",
        "linked_finding_reference": "FND-CAND-001",
        "linked_finding_title": "MFA is not documented or not enforced for remote access.",
        "linked_applied_control_reference": "CTL-MFA-001",
        "linked_applied_control_title": "Multi-Factor Authentication for Remote Access",
        "linked_remediation_action_reference": "REM-CAND-001",
        "linked_remediation_action_title": "Implement and enforce MFA for remote access",
        "linked_framework_control_reference": "urn:sama:ecc:3.3.5",
        "linked_framework_control_code": "3.3.5",
        "linked_framework_control_title": "SAMA control 3.3.5",
        "threat": "Unauthorized access by an external actor",
        "vulnerability": "No MFA for remote access",
        "impact_description": "Potential unauthorized transactions and data disclosure.",
        "likelihood": "high",
        "impact": "high",
        "risk_level": "high",
        "rationale": (
            "The preliminary finding indicates remote access is not evidenced as MFA "
            "protected, which is a common path to unauthorized access."
        ),
        "recommended_next_steps": [
            "Confirm the MFA configuration with the platform owner.",
            "Collect remote access authentication logs for the review period.",
        ],
        "confidence": 0.82,
        "review_status": "pending_review",
    }
    scenario.update(overrides)
    return scenario


def _install_provider_returning(monkeypatch, provider_draft):
    _configure_local_provider_env(monkeypatch)

    def _handler(request, timeout, body):
        return {
            "model": body["model"],
            "response": json.dumps(provider_draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)


@pytest.mark.django_db
def test_ai_risk_scenario_suggestion_requires_authentication(client):
    response = client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_step8a_returns_advisory_no_write_response(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert sorted(body.keys()) == [
        "ambiguity_flags",
        "overall_confidence",
        "provider_mode",
        "risk_scenarios",
        "warnings",
    ]
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["risk_scenarios"]
    for scenario in body["risk_scenarios"]:
        assert scenario["review_status"] == "pending_review"
        assert scenario["likelihood"] in {"low", "medium", "high", "critical"}
        assert scenario["impact"] in {"low", "medium", "high", "critical"}
        assert scenario["risk_level"] in {"low", "medium", "high", "critical"}
        assert 0.0 <= scenario["confidence"] <= 1.0
        assert isinstance(scenario["recommended_next_steps"], list)
    # No committed record identifiers, write flags, or risk decision fields leak into the
    # response. Advisory prose may mention a concept; only a real key would be a leak.
    serialized = json.dumps(body)
    for forbidden in (
        "risk_scenario_id",
        "risk_assessment_id",
        "risk_acceptance",
        "treatment",
        "approved_by_user",
        "idempotency_key",
    ):
        assert f'"{forbidden}":' not in serialized


@pytest.mark.django_db
def test_configured_local_provider_path_uses_mocked_ollama(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)
    provider_draft = {"risk_scenarios": [_valid_provider_scenario()]}
    calls = []

    def _handler(request, timeout, body):
        calls.append({"url": request.full_url, "body": body})
        return {
            "model": body["model"],
            "response": json.dumps(provider_draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert len(body["risk_scenarios"]) == 1
    scenario = body["risk_scenarios"][0]
    assert scenario["title"] == "Unauthorized remote access to the Core Banking Platform"
    assert scenario["likelihood"] == "high"
    assert scenario["risk_level"] == "high"
    assert scenario["linked_finding_reference"] == "FND-CAND-001"
    assert scenario["linked_framework_control_code"] == "3.3.5"
    assert body["overall_confidence"] == 0.82
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    assert before == after


@pytest.mark.django_db
def test_invalid_likelihood_enum_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"risk_scenarios": [_valid_provider_scenario(likelihood="very-high")]},
    )

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_risk_scenario_suggestion_guardrails_failed"
    assert any("likelihood" in error for error in body["errors"])
    assert before == after


@pytest.mark.django_db
def test_invalid_risk_level_enum_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"risk_scenarios": [_valid_provider_scenario(risk_level="severe")]},
    )

    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("risk_level" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_invalid_confidence_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"risk_scenarios": [_valid_provider_scenario(confidence=1.7)]},
    )

    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_risk_scenario_suggestion_guardrails_failed"
    assert any("confidence" in error for error in body["errors"])


@pytest.mark.django_db
def test_missing_required_scenario_fields_are_guarded(authenticated_client, monkeypatch):
    incomplete = _valid_provider_scenario()
    del incomplete["title"]
    del incomplete["threat"]
    del incomplete["recommended_next_steps"]
    _install_provider_returning(monkeypatch, {"risk_scenarios": [incomplete]})

    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("title is required" in error for error in errors)
    assert any("threat is required" in error for error in errors)
    assert any("recommended_next_steps is required" in error for error in errors)


@pytest.mark.django_db
def test_risk_scenarios_must_be_a_list(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch, {"risk_scenarios": {"temporary_id": "risk_scenario_1"}}
    )

    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert "risk_scenarios must be a list." in response.json()["errors"]


@pytest.mark.django_db
def test_non_pending_review_status_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch, {"risk_scenarios": [_valid_provider_scenario(review_status="approved")]}
    )

    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any(
        "review_status must be 'pending_review'" in error
        for error in response.json()["errors"]
    )


@pytest.mark.django_db
def test_risk_decision_language_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {
            "risk_scenarios": [
                _valid_provider_scenario(
                    rationale="The auditor should accept the risk and close this risk now."
                )
            ]
        },
    )

    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("out-of-scope" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_write_intent_fields_are_rejected(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(accept_risk=True),
        format="json",
    )

    assert response.status_code == 400
    assert "accept_risk" in response.json()


@pytest.mark.django_db
def test_provider_write_intent_output_is_blocked(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {
            "risk_scenarios": [_valid_provider_scenario()],
            "accept_risk": True,
        },
    )

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "local_ai_provider_invalid_output"
    assert body["provider_mode"] == "local_provider_error_blocked"
    assert before == after


@pytest.mark.django_db
def test_missing_risk_context_returns_blocked_advisory_response(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(
            assets=[], preliminary_findings=[], known_weaknesses=[]
        ),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "risk_context_missing_blocked"
    assert body["risk_scenarios"] == []
    assert any(warning["code"] == "no_risk_input_context" for warning in body["warnings"])


@pytest.mark.django_db
def test_step8a_does_not_write_grc_records(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, {"risk_scenarios": [_valid_provider_scenario()]})

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_provider_failure_returns_safe_fallback_without_writes(
    authenticated_client, monkeypatch
):
    import urllib.error

    _configure_local_provider_env(monkeypatch)

    def _mock_urlopen(request, timeout=0):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-risk-scenario-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "local_provider_error_fallback"
    assert any(warning["code"] == "local_provider_error_fallback" for warning in body["warnings"])
    assert body["risk_scenarios"]
    assert before == after
