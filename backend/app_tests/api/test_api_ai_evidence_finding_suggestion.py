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
    "Al-Rawasi Fintech is preparing for its annual SAMA ECC-1:2018 compliance assessment in Q4 2026. "
    "The scope is Core Banking Platform - User Access Management. Known weaknesses include no MFA for remote access, "
    "no PAM for privileged admin accounts, no periodic access review records, and no formal access review documentation."
)


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_ai_evidence_finding_suggestion_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_EVIDENCE_FINDING_SUGGESTION", raising=False)
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
def setup_context(framework, risk_matrix):
    folder = Folder.objects.create(
        name=f"AI Step 5A Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    perimeter = Perimeter.objects.create(
        folder=folder,
        name=f"AI Step 5A Perimeter {uuid.uuid4().hex[:8]}",
        ref_id=f"PER-STEP5A-{uuid.uuid4().hex[:8]}",
        description="Step 5A evidence/finding suggestion scope perimeter",
        lc_status="in_prod",
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        framework=framework,
        name=f"AI Step 5A Compliance Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    risk_assessment = RiskAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        risk_matrix=risk_matrix,
        name=f"AI Step 5A Risk Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    assets = [
        Asset.objects.create(
            folder=folder,
            name="Core Banking Platform",
            type=Asset.Type.PRIMARY,
            ref_id=f"AST-CBP-{uuid.uuid4().hex[:6].upper()}",
            description="Primary core banking platform.",
        ),
        Asset.objects.create(
            folder=folder,
            name="Remote Access / VPN Service",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-VPN-{uuid.uuid4().hex[:6].upper()}",
            description="Remote access service.",
        ),
    ]
    applied_controls = [
        AppliedControl.objects.create(
            folder=folder,
            name="Multi-Factor Authentication for Remote Access",
            category="technical",
            status="to_do",
            ref_id="CTL-MFA-001",
        ),
        AppliedControl.objects.create(
            folder=folder,
            name="Privileged Access Management",
            category="technical",
            status="to_do",
            ref_id="CTL-PAM-001",
        ),
    ]
    for control in applied_controls:
        control.assets.set(assets)

    return {
        "folder": folder,
        "perimeter": perimeter,
        "compliance_assessment": compliance_assessment,
        "risk_assessment": risk_assessment,
        "framework": framework,
        "assets": assets,
        "applied_controls": applied_controls,
    }


def _asset_reference(asset):
    return {
        "asset_id": str(asset.id),
        "name": asset.name,
        "ref_id": asset.ref_id,
        "asset_class": None,
        "type": asset.type,
        "source_temporary_id": f"asset-ref-{asset.ref_id.lower()}",
    }


def _applied_control_reference(control):
    return {
        "applied_control_id": str(control.id),
        "name": control.name,
        "ref_id": control.ref_id,
        "category": control.category,
        "status": control.status,
        "source_temporary_id": f"ctl-ref-{control.ref_id.lower()}",
    }


def _request_payload(setup_context, **overrides):
    payload = {
        "source_step1_draft_hash": "sha256:" + "a" * 64,
        "source_asset_commit_hash": "sha256:" + "b" * 64,
        "source_applied_control_draft_hash": "sha256:" + "c" * 64,
        "source_applied_control_commit_hash": "sha256:" + "d" * 64,
        "case_setup_reference": {
            "folder_id": str(setup_context["folder"].id),
            "perimeter_id": str(setup_context["perimeter"].id),
            "compliance_assessment_id": str(setup_context["compliance_assessment"].id),
            "risk_assessment_id": str(setup_context["risk_assessment"].id),
            "selected_framework_id": str(setup_context["framework"].id),
        },
        "asset_references": [_asset_reference(asset) for asset in setup_context["assets"]],
        "applied_control_references": [
            _applied_control_reference(control) for control in setup_context["applied_controls"]
        ],
        "scenario_text": AL_RAWASI_SCENARIO,
        "scope_summary": "Core Banking Platform user access management scope for the Q4 2026 ECC review.",
        "known_weaknesses": [
            "No MFA for remote access",
            "No PAM for privileged admin accounts",
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
    monkeypatch.setenv("LOCAL_AI_MODEL_EVIDENCE_FINDING_SUGGESTION", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_mock_ollama_urlopen(monkeypatch, handler):
    def _mock_urlopen(request, timeout=0):
        request_body = json.loads(request.data.decode("utf-8"))
        response_payload = handler(request, timeout, request_body)
        return _MockHttpResponse(response_payload)

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


@pytest.mark.django_db
def test_ai_evidence_finding_suggestion_requires_authentication(client, setup_context):
    response = client.post(
        reverse("ai-evidence-finding-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_valid_request_returns_evidence_questions_and_findings(authenticated_client, setup_context):
    response = authenticated_client.post(
        reverse("ai-evidence-finding-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["draft_type"] == "AiEvidenceFindingSuggestionDraft"
    assert body["no_write"] is True
    assert body["review_status"] == "pending_review"
    assert body["needs_human_review"] is True
    assert body["advisory_notice"] == (
        "AI suggestions only. No findings or evidence records are created in Step 5A."
    )
    assert body["evidence_requests"]
    assert body["audit_questions"]
    assert body["preliminary_findings"]
    approved_asset_ids = {str(asset.id) for asset in setup_context["assets"]}
    approved_control_ids = {str(control.id) for control in setup_context["applied_controls"]}
    for group in ("evidence_requests", "audit_questions", "preliminary_findings"):
        for item in body[group]:
            assert item["review_status"] == "pending_review"
            assert {str(a) for a in item["linked_asset_ids"]}.issubset(approved_asset_ids)
            assert {str(c) for c in item["linked_applied_control_ids"]}.issubset(approved_control_ids)


@pytest.mark.django_db
def test_step5a_does_not_write_grc_records(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-evidence-finding-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_configured_local_provider_path_uses_mocked_ollama_and_does_not_write(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)
    provider_draft = {
        "evidence_requests": [
            {
                "temporary_id": "EVR-CAND-001",
                "title": "MFA configuration evidence",
                "rationale": "Confirm MFA is enforced for remote access.",
                "confidence": 0.85,
            }
        ],
        "audit_questions": [
            {
                "temporary_id": "AUQ-CAND-001",
                "question_text": "How is MFA enforced for remote access?",
                "rationale": "Confirm operating effectiveness.",
                "confidence": 0.8,
            }
        ],
        "preliminary_findings": [
            {
                "temporary_id": "FND-CAND-001",
                "title": "Remote access MFA gap",
                "rationale": "Reported weakness pending confirmation.",
                "confidence": 0.7,
            }
        ],
    }
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
        reverse("ai-evidence-finding-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert body["source_summary"]["provider_mode"] == "configured_local_provider"
    assert len(body["evidence_requests"]) == 1
    assert len(body["audit_questions"]) == 1
    assert len(body["preliminary_findings"]) == 1
    # provider omitted asset/control links; the service normalizes them to the approved sets.
    assert body["evidence_requests"][0]["linked_asset_ids"]
    assert body["evidence_requests"][0]["linked_applied_control_ids"]
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    assert before == after


@pytest.mark.django_db
def test_provider_string_ambiguity_flags_are_normalized(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)
    provider_draft = {
        "evidence_requests": [
            {
                "temporary_id": "EVR-CAND-001",
                "title": "MFA configuration evidence",
                "rationale": "Confirm MFA is enforced for remote access.",
                "confidence": 0.85,
                "ambiguity_flags": ["scope of remote access is unclear"],
            }
        ],
        "audit_questions": [
            {
                "temporary_id": "AUQ-CAND-001",
                "question_text": "How is MFA enforced for remote access?",
                "rationale": "Confirm operating effectiveness.",
                "confidence": 0.8,
                "ambiguity_flags": ["timing of enforcement is unclear"],
            }
        ],
        "preliminary_findings": [
            {
                "temporary_id": "FND-CAND-001",
                "title": "Remote access MFA gap",
                "rationale": "Reported weakness pending confirmation.",
                "confidence": 0.7,
                "ambiguity_flags": ["severity is unclear"],
            }
        ],
    }

    def _handler(request, timeout, body):
        return {
            "model": body["model"],
            "response": json.dumps(provider_draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-evidence-finding-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert body["evidence_requests"][0]["ambiguity_flags"] == [
        {"code": "provider_ambiguity", "message": "scope of remote access is unclear"}
    ]
    assert body["audit_questions"][0]["ambiguity_flags"][0] == {
        "code": "provider_ambiguity",
        "message": "timing of enforcement is unclear",
    }
    assert body["preliminary_findings"][0]["ambiguity_flags"][0] == {
        "code": "provider_ambiguity",
        "message": "severity is unclear",
    }
    assert before == after


@pytest.mark.django_db
def test_missing_source_hash_blocks_request(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    del payload["source_applied_control_commit_hash"]

    response = authenticated_client.post(
        reverse("ai-evidence-finding-suggestion"),
        payload,
        format="json",
    )

    assert response.status_code == 400
    assert "source_applied_control_commit_hash" in response.json()


@pytest.mark.django_db
def test_invalid_linked_asset_blocks_request(authenticated_client, setup_context):
    payload = _request_payload(
        setup_context,
        asset_references=[{"asset_id": str(uuid.uuid4()), "name": "Ghost Asset"}],
    )

    response = authenticated_client.post(
        reverse("ai-evidence-finding-suggestion"),
        payload,
        format="json",
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "ai_evidence_finding_suggestion_asset_references_invalid"


@pytest.mark.django_db
def test_invalid_linked_applied_control_blocks_request(authenticated_client, setup_context):
    payload = _request_payload(
        setup_context,
        applied_control_references=[
            {"applied_control_id": str(uuid.uuid4()), "name": "Ghost Control"}
        ],
    )

    response = authenticated_client.post(
        reverse("ai-evidence-finding-suggestion"),
        payload,
        format="json",
    )

    assert response.status_code == 422
    assert (
        response.json()["error_code"]
        == "ai_evidence_finding_suggestion_applied_control_references_invalid"
    )


@pytest.mark.django_db
def test_provider_failure_returns_safe_fallback_without_writes(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    import urllib.error

    _configure_local_provider_env(monkeypatch)

    def _mock_urlopen(request, timeout=0):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-evidence-finding-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "local_provider_error_fallback"
    assert body["no_write"] is True
    assert any(
        warning["code"] == "local_provider_error_fallback" for warning in body["warnings"]
    )
    assert body["evidence_requests"]
    assert before == after
