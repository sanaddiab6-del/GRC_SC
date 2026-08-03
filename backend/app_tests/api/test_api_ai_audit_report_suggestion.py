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
    "The scope is Core Banking Platform - User Access Management."
)


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_ai_audit_report_suggestion_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_AUDIT_REPORT_SUGGESTION", raising=False)
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
        "organization_name": "Al-Rawasi Fintech",
        "framework_name": "SAMA ECC-1:2018",
        "folder_reference": {
            "folder_id": str(uuid.uuid4()),
            "folder_name": "Al-Rawasi Fintech",
        },
        "assessment_reference": {
            "assessment_id": str(uuid.uuid4()),
            "assessment_name": "Q4 2026 ECC Compliance Assessment",
        },
        "assets": [{"reference": "AST-CBP-001", "title": "Core Banking Platform"}],
        "applied_controls": [
            {
                "reference": "CTL-MFA-001",
                "title": "Multi-Factor Authentication for Remote Access",
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
            }
        ],
        "remediation_actions": [
            {"reference": "REM-CAND-001", "title": "Implement and enforce MFA for remote access"}
        ],
        "framework_mappings": [
            {"reference": "urn:sama:ecc:3.3.5-4.e", "title": "SAMA control 3.3.5-4.e"}
        ],
        "risk_scenarios": [
            {
                "reference": "risk_scenario_1",
                "title": "Unauthorized remote access to the Core Banking Platform",
            }
        ],
        "control_effectiveness_suggestions": [
            {
                "reference": "effectiveness_1",
                "title": "Multi-factor authentication for sensitive and critical systems",
                "status": "needs_more_evidence",
            }
        ],
        "evidence_gaps": ["MFA configuration export has not been collected."],
        "audit_readiness": {
            "readiness_status": "partially_ready",
            "readiness_score": 55,
            "summary": "Evidence collection is still outstanding.",
        },
        "known_weaknesses": ["No MFA for remote access"],
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
    monkeypatch.setenv("LOCAL_AI_MODEL_AUDIT_REPORT_SUGGESTION", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_mock_ollama_urlopen(monkeypatch, handler):
    def _mock_urlopen(request, timeout=0):
        request_body = json.loads(request.data.decode("utf-8"))
        response_payload = handler(request, timeout, request_body)
        return _MockHttpResponse(response_payload)

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


HUMAN_REVIEW_LIMITATION = (
    "This is an AI-assisted draft. Human review by the accountable auditor is required "
    "before any part of it is used."
)


def _valid_provider_draft(**overrides):
    draft = {
        "report_title": "Al-Rawasi Fintech - Core Banking Platform onboarding report draft",
        "executive_summary": (
            "The onboarding flow captured the scope, controls, findings, and risks for the "
            "Core Banking Platform. Evidence collection is still outstanding."
        ),
        "report_sections": [
            {
                "heading": "Executive Summary",
                "content": "Onboarding captured scope, controls, findings, and risks.",
                "source_items": ["Core Banking Platform"],
                "confidence": 0.7,
            },
            {
                "heading": "Preliminary Findings",
                "content": "MFA is not documented or not enforced for remote access.",
                "source_items": ["MFA is not documented or not enforced for remote access."],
                "confidence": 0.8,
            },
        ],
        "limitations": [
            HUMAN_REVIEW_LIMITATION,
            "The draft is based only on the captured onboarding context.",
        ],
        "recommended_next_steps": ["Collect the MFA configuration export."],
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
def test_ai_audit_report_suggestion_requires_authentication(client):
    response = client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_step11a_returns_advisory_no_write_response(authenticated_client):
    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert sorted(body.keys()) == [
        "ambiguity_flags",
        "executive_summary",
        "limitations",
        "overall_confidence",
        "provider_mode",
        "recommended_next_steps",
        "report_sections",
        "report_title",
        "review_status",
        "warnings",
    ]
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["review_status"] == "pending_review"
    assert body["report_title"]
    assert body["report_sections"]
    assert body["limitations"]
    # The draft must always say human review is required.
    assert any("human review" in entry.lower() for entry in body["limitations"])
    headings = [section["heading"] for section in body["report_sections"]]
    for expected in (
        "Executive Summary",
        "Scope",
        "Assets in Scope",
        "Preliminary Findings",
        "Risk Scenarios",
        "Audit Readiness",
        "Limitations / Human Review Required",
    ):
        assert expected in headings
    for section in body["report_sections"]:
        assert 0.0 <= section["confidence"] <= 1.0
        assert isinstance(section["source_items"], list)
    serialized = json.dumps(body)
    for forbidden in (
        "report_id",
        "save_report",
        "publish_report",
        "mark_report_final",
        "certify_compliance",
        "close_audit",
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
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert body["report_title"].startswith("Al-Rawasi Fintech")
    assert len(body["report_sections"]) == 2
    assert body["overall_confidence"] == 0.75
    # Sections the model did not cover are reported, never invented.
    assert any(
        warning["code"] == "report_sections_incomplete" for warning in body["warnings"]
    )
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert before == after


@pytest.mark.django_db
def test_missing_required_fields_are_guarded(authenticated_client, monkeypatch):
    incomplete = _valid_provider_draft()
    del incomplete["report_title"]
    del incomplete["executive_summary"]
    _install_provider_returning(monkeypatch, incomplete)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_audit_report_suggestion_guardrails_failed"
    errors = body["errors"]
    assert any("report_title is required" in error for error in errors)
    assert any("executive_summary is required" in error for error in errors)
    assert before == after


@pytest.mark.django_db
def test_empty_limitations_are_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_provider_draft(limitations=[]))

    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("limitations must not be empty" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_limitations_without_human_review_statement_are_guarded(
    authenticated_client, monkeypatch
):
    _install_provider_returning(
        monkeypatch,
        _valid_provider_draft(limitations=["The draft is based on the captured context."]),
    )

    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any(
        "human review is required" in error for error in response.json()["errors"]
    )


@pytest.mark.django_db
def test_invalid_section_confidence_is_guarded(authenticated_client, monkeypatch):
    draft = _valid_provider_draft()
    draft["report_sections"][0]["confidence"] = 1.8
    _install_provider_returning(monkeypatch, draft)

    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("confidence" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_missing_section_fields_are_guarded(authenticated_client, monkeypatch):
    draft = _valid_provider_draft()
    del draft["report_sections"][0]["heading"]
    _install_provider_returning(monkeypatch, draft)

    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("heading is required" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_report_sections_must_be_a_list(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch, _valid_provider_draft(report_sections={"heading": "Scope"})
    )

    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert "report_sections must be a list." in response.json()["errors"]


@pytest.mark.django_db
def test_non_pending_review_status_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_provider_draft(review_status="approved"))

    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any(
        "review_status must be 'pending_review'" in error
        for error in response.json()["errors"]
    )


@pytest.mark.django_db
def test_final_opinion_and_certification_language_is_guarded(
    authenticated_client, monkeypatch
):
    _install_provider_returning(
        monkeypatch,
        _valid_provider_draft(
            executive_summary=(
                "Our final audit opinion is unqualified and we hereby certify compliance."
            )
        ),
    )

    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )

    assert response.status_code == 422
    assert any("out-of-scope" in error for error in response.json()["errors"])


@pytest.mark.django_db
def test_write_intent_fields_are_rejected(authenticated_client):
    for field in ("save_report", "publish_report", "mark_report_final", "certify_compliance"):
        response = authenticated_client.post(
            reverse("ai-audit-report-suggestion"),
            _request_payload(**{field: True}),
            format="json",
        )
        assert response.status_code == 400, field
        assert field in response.json()


@pytest.mark.django_db
def test_provider_write_intent_output_is_blocked(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_provider_draft(publish_report=True))

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
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
        reverse("ai-audit-report-suggestion"),
        _request_payload(
            assets=[],
            applied_controls=[],
            evidence_requests=[],
            audit_questions=[],
            preliminary_findings=[],
            remediation_actions=[],
            framework_mappings=[],
            risk_scenarios=[],
            control_effectiveness_suggestions=[],
            evidence_gaps=[],
            known_weaknesses=[],
        ),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "report_context_missing_blocked"
    assert body["report_sections"] == []
    assert body["limitations"]
    assert any(warning["code"] == "no_report_input_context" for warning in body["warnings"])


@pytest.mark.django_db
def test_step11a_does_not_write_grc_records(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_provider_draft())

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-audit-report-suggestion"),
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
        reverse("ai-audit-report-suggestion"),
        _request_payload(),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "local_provider_error_fallback"
    assert any(warning["code"] == "local_provider_error_fallback" for warning in body["warnings"])
    assert body["report_sections"]
    assert before == after
