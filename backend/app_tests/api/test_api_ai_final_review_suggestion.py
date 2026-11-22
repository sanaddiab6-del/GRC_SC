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


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_ai_final_review_suggestion_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_FINAL_REVIEW_SUGGESTION", raising=False)
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
        "case_summary": "Al-Rawasi Fintech SAMA ECC-1:2018 onboarding.",
        "scenario_name": "Core Banking Platform - User Access Management",
        "folder_reference": {
            "folder_id": str(uuid.uuid4()),
            "folder_name": "Al-Rawasi Fintech",
        },
        "assessment_reference": {
            "assessment_id": str(uuid.uuid4()),
            "assessment_name": "Q4 2026 ECC Compliance Assessment",
        },
        "step_outcomes": [
            {"step": "3B", "status": "created", "detail": "Assets committed."},
            {"step": "4B", "status": "created", "detail": "Applied controls committed."},
            {"step": "7B", "status": "blocked", "detail": "Framework control not in database."},
            {"step": "9B", "status": "completed_with_warnings", "detail": "Results recorded."},
        ],
        "created_records": [
            {"record_type": "asset", "name": "Core Banking Platform", "action": "create"},
            {
                "record_type": "applied_control",
                "name": "Multi-Factor Authentication for Remote Access",
                "action": "create",
            },
        ],
        "reused_records": [
            {"record_type": "evidence", "name": "MFA configuration evidence", "action": "reuse"}
        ],
        "blocked_items": ["Framework control 3.3.5-4.e is not loaded in the platform."],
        "outstanding_items": ["MFA configuration export has not been collected."],
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
    monkeypatch.setenv("LOCAL_AI_MODEL_FINAL_REVIEW_SUGGESTION", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_mock_ollama_urlopen(monkeypatch, handler):
    def _mock_urlopen(request, timeout=0):
        request_body = json.loads(request.data.decode("utf-8"))
        response_payload = handler(request, timeout, request_body)
        return _MockHttpResponse(response_payload)

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _valid_provider_draft(**overrides):
    draft = {
        "completion_summary": (
            "Steps 3B, 4B, and 9B recorded results; Step 7B is blocked because the framework "
            "library is not loaded. Everything recorded remains advisory."
        ),
        "completed_steps": ["3B: created", "4B: created", "9B: completed_with_warnings"],
        "incomplete_steps": ["7B: blocked"],
        "created_or_reused_records_summary": [
            "Created asset: Core Banking Platform",
            "Reused evidence: MFA configuration evidence",
        ],
        "blocked_items": ["Framework control 3.3.5-4.e is not loaded in the platform."],
        "human_review_required": [
            "Confirm the preliminary findings with their owners.",
            "Rate the suggested risk scenarios on the platform risk matrix.",
        ],
        "recommended_next_steps": ["Load the framework library, then rerun Step 7B."],
        "demo_readiness_status": "partially_ready",
        "review_status": "pending_review",
    }
    draft.update(overrides)
    return draft


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
def test_ai_final_review_suggestion_requires_authentication(client):
    response = client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_step12a_returns_advisory_no_write_response(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert sorted(body.keys()) == [
        "ambiguity_flags",
        "blocked_items",
        "completed_steps",
        "completion_summary",
        "created_or_reused_records_summary",
        "demo_readiness_status",
        "human_review_required",
        "incomplete_steps",
        "overall_confidence",
        "provider_mode",
        "recommended_next_steps",
        "review_status",
        "warnings",
    ]
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["review_status"] == "pending_review"
    assert body["demo_readiness_status"] in {
        "ready",
        "partially_ready",
        "not_ready",
        "blocked",
    }
    assert body["completion_summary"]
    assert body["completed_steps"]
    assert body["incomplete_steps"]
    assert body["human_review_required"]
    # The blocked Step 7B outcome is surfaced, not hidden.
    assert body["demo_readiness_status"] == "blocked"
    assert body["blocked_items"]
    serialized = json.dumps(body)
    for forbidden in (
        "mark_complete",
        "close_audit",
        "certify_compliance",
        "final_audit_opinion",
        "approved_by_user",
        "compliance_assessment_id",
    ):
        assert f'"{forbidden}":' not in serialized


@pytest.mark.django_db
def test_configured_local_provider_path_uses_mocked_ollama(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)
    calls = []

    def _handler(request, timeout, body):
        calls.append({"url": request.full_url, "body": body})
        return {
            "model": body["model"],
            "response": json.dumps(_valid_provider_draft(), default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert body["demo_readiness_status"] == "partially_ready"
    assert body["completed_steps"] == [
        "3B: created",
        "4B: created",
        "9B: completed_with_warnings",
    ]
    assert body["incomplete_steps"] == ["7B: blocked"]
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert before == after


@pytest.mark.django_db
def test_invalid_demo_readiness_status_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch, _valid_provider_draft(demo_readiness_status="almost_ready")
    )

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_final_review_suggestion_guardrails_failed"
    assert any("demo_readiness_status" in error for error in body["errors"])
    assert before == after


@pytest.mark.django_db
def test_missing_required_fields_are_guarded(authenticated_client, monkeypatch):
    incomplete = _valid_provider_draft()
    del incomplete["completion_summary"]
    del incomplete["demo_readiness_status"]
    _install_provider_returning(monkeypatch, incomplete)

    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("completion_summary is required" in error for error in errors)
    assert any("demo_readiness_status is required" in error for error in errors)


@pytest.mark.django_db
def test_non_list_summary_field_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch, _valid_provider_draft(completed_steps="3B: created")
    )

    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("completed_steps must be a list" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_invalid_confidence_is_guarded(authenticated_client, monkeypatch):
    # A provider-supplied overall_confidence outside 0-1 must be rejected, never clamped.
    _install_provider_returning(monkeypatch, _valid_provider_draft(overall_confidence=1.6))

    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("overall_confidence" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_non_pending_review_status_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_provider_draft(review_status="approved"))

    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any(
        "review_status must be 'pending_review'" in error
        for error in response.json()["errors"]
    )


@pytest.mark.django_db
def test_completion_and_closure_language_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        _valid_provider_draft(
            completion_summary="The audit is complete, so we certify compliance and close audit."
        ),
    )

    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("out-of-scope" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_write_intent_fields_are_rejected(authenticated_client):
    for field in ("mark_complete", "close_audit", "certify_compliance", "complete_workflow"):
        response = authenticated_client.post(
            reverse("ai-final-review-suggestion"),
            _request_payload(**{field: True}),
            format="json",
        )
        assert response.status_code == 400, field
        assert field in response.json()


@pytest.mark.django_db
def test_provider_write_intent_output_is_blocked(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_provider_draft(mark_complete=True))

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
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
def test_missing_context_returns_blocked_advisory_response(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
        _request_payload(
            step_outcomes=[],
            created_records=[],
            reused_records=[],
            blocked_items=[],
            outstanding_items=[],
        ),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "final_review_context_missing_blocked"
    assert body["demo_readiness_status"] == "blocked"
    assert body["completed_steps"] == []
    assert any(
        warning["code"] == "no_final_review_input_context" for warning in body["warnings"]
    )


@pytest.mark.django_db
def test_step12a_does_not_write_grc_records(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_provider_draft())

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-final-review-suggestion"),
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
        reverse("ai-final-review-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "local_provider_error_fallback"
    assert any(warning["code"] == "local_provider_error_fallback" for warning in body["warnings"])
    assert body["completion_summary"]
    assert before == after
