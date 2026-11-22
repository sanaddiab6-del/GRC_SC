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
        / f"test_ai_remediation_action_suggestion_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_REMEDIATION_ACTION_SUGGESTION", raising=False)
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
        "known_weaknesses": [
            "No MFA for remote access",
            "No PAM for privileged admin accounts",
        ],
        "framework_name": "SAMA ECC-1:2018",
        "assessment_name": "Q4 2026 ECC Compliance Assessment",
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
    monkeypatch.setenv("LOCAL_AI_MODEL_REMEDIATION_ACTION_SUGGESTION", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_mock_ollama_urlopen(monkeypatch, handler):
    def _mock_urlopen(request, timeout=0):
        request_body = json.loads(request.data.decode("utf-8"))
        response_payload = handler(request, timeout, request_body)
        return _MockHttpResponse(response_payload)

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _valid_provider_action(**overrides):
    action = {
        "temporary_id": "remediation_action_1",
        "title": "Implement and enforce MFA for remote access",
        "description": (
            "Enable and enforce multi-factor authentication for all remote access users "
            "of the Core Banking Platform."
        ),
        "linked_finding_reference": "FND-CAND-001",
        "linked_finding_title": "MFA is not documented or not enforced for remote access.",
        "linked_asset_reference": "AST-CBP-001",
        "linked_asset_title": "Core Banking Platform",
        "linked_control_reference": "CTL-MFA-001",
        "linked_control_title": "Multi-Factor Authentication for Remote Access",
        "priority": "high",
        "suggested_owner": "IAM / Security Operations",
        "target_timeline": "30-60 days",
        "success_criteria": [
            "All remote access users authenticate using MFA.",
            "Any MFA exceptions are documented and approved.",
        ],
        "required_follow_up_evidence": [
            "MFA policy",
            "MFA configuration screenshots",
        ],
        "rationale": (
            "The finding indicates that MFA enforcement is not sufficiently evidenced "
            "for remote access to the Core Banking Platform."
        ),
        "confidence": 0.85,
        "review_status": "pending_review",
    }
    action.update(overrides)
    return action


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
def test_ai_remediation_action_suggestion_requires_authentication(client):
    response = client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_step6a_returns_advisory_no_write_response(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert sorted(body.keys()) == [
        "ambiguity_flags",
        "overall_confidence",
        "provider_mode",
        "remediation_actions",
        "warnings",
    ]
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["remediation_actions"]
    for action in body["remediation_actions"]:
        assert action["review_status"] == "pending_review"
        assert action["priority"] in {"low", "medium", "high", "critical"}
        assert 0.0 <= action["confidence"] <= 1.0
        assert isinstance(action["success_criteria"], list)
        assert isinstance(action["required_follow_up_evidence"], list)
    # No committed record identifiers or write/approval flags leak into the response.
    serialized = json.dumps(body)
    for forbidden in ("finding_id", "evidence_id", "approved_by_user", "idempotency_key"):
        assert forbidden not in serialized


@pytest.mark.django_db
def test_step6a_keeps_review_status_pending_review(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"remediation_actions": [_valid_provider_action(review_status="pending_review")]},
    )

    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["remediation_actions"][0]["review_status"] == "pending_review"


@pytest.mark.django_db
def test_configured_local_provider_path_uses_mocked_ollama(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)
    provider_draft = {"remediation_actions": [_valid_provider_action()]}
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
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert len(body["remediation_actions"]) == 1
    action = body["remediation_actions"][0]
    assert action["title"] == "Implement and enforce MFA for remote access"
    assert action["priority"] == "high"
    assert action["suggested_owner"] == "IAM / Security Operations"
    assert action["target_timeline"] == "30-60 days"
    assert action["linked_finding_reference"] == "FND-CAND-001"
    assert body["overall_confidence"] == 0.85
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    assert before == after


@pytest.mark.django_db
def test_invalid_priority_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"remediation_actions": [_valid_provider_action(priority="urgent")]},
    )

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_remediation_action_suggestion_guardrails_failed"
    assert any("priority" in error for error in body["errors"])
    assert before == after


@pytest.mark.django_db
def test_invalid_confidence_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"remediation_actions": [_valid_provider_action(confidence=1.7)]},
    )

    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_remediation_action_suggestion_guardrails_failed"
    assert any("confidence" in error for error in body["errors"])


@pytest.mark.django_db
def test_missing_required_action_fields_are_guarded(authenticated_client, monkeypatch):
    incomplete_action = _valid_provider_action()
    del incomplete_action["title"]
    del incomplete_action["suggested_owner"]
    del incomplete_action["success_criteria"]
    _install_provider_returning(monkeypatch, {"remediation_actions": [incomplete_action]})

    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_remediation_action_suggestion_guardrails_failed"
    errors = body["errors"]
    assert any("title is required" in error for error in errors)
    assert any("suggested_owner is required" in error for error in errors)
    assert any("success_criteria is required" in error for error in errors)


@pytest.mark.django_db
def test_remediation_actions_must_be_a_list(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"remediation_actions": {"temporary_id": "remediation_action_1"}},
    )

    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_remediation_action_suggestion_guardrails_failed"
    assert "remediation_actions must be a list." in body["errors"]


@pytest.mark.django_db
def test_non_list_success_criteria_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {
            "remediation_actions": [
                _valid_provider_action(
                    success_criteria="All remote access users authenticate using MFA.",
                    required_follow_up_evidence="MFA policy",
                )
            ]
        },
    )

    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("success_criteria must be a list" in error for error in errors)
    assert any("required_follow_up_evidence must be a list" in error for error in errors)


@pytest.mark.django_db
def test_non_pending_review_status_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"remediation_actions": [_valid_provider_action(review_status="approved")]},
    )

    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("review_status must be 'pending_review'" in error for error in errors)


@pytest.mark.django_db
def test_step6a_does_not_write_grc_records(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch, {"remediation_actions": [_valid_provider_action()]}
    )

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_step6a_fallback_without_provider_does_not_write(authenticated_client):
    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after
    assert response.json()["remediation_actions"][0]["review_status"] == "pending_review"


@pytest.mark.django_db
def test_write_intent_fields_are_rejected(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-remediation-action-suggestion"),
        _request_payload(approved_by_user=True),
        format="json",
    )

    assert response.status_code == 400
    assert "approved_by_user" in response.json()


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
        reverse("ai-remediation-action-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "local_provider_error_fallback"
    assert any(warning["code"] == "local_provider_error_fallback" for warning in body["warnings"])
    assert body["remediation_actions"]
    assert before == after
