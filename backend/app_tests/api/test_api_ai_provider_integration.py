import json
import uuid

import pytest
from django.conf import settings as django_settings
from django.urls import reverse
from knox.models import AuthToken

from ai_onboarding.applied_control_suggestion_provider import (
    AppliedControlSuggestionProviderError,
    get_applied_control_suggestion_provider,
)
from ai_onboarding.applied_control_suggestion_service import (
    build_applied_control_suggestion_fallback_draft,
)
from ai_onboarding.asset_suggestion_provider import (
    AssetSuggestionProviderError,
    get_asset_suggestion_provider,
)
from ai_onboarding.asset_suggestion_service import build_asset_suggestion_fallback_draft
from ai_onboarding.case_intake_provider import CaseIntakeProviderError, get_case_intake_provider
from ai_onboarding.case_intake_service import build_case_intake_fallback_draft
from ai_onboarding.llm_config import (
    CAPABILITY_APPLIED_CONTROL_SUGGESTION,
    CAPABILITY_ASSET_SUGGESTION,
    CAPABILITY_CASE_INTAKE,
    resolve_advisory_capability_config,
)
from ai_onboarding.llm_provider import LocalAiProvider
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
    "Al-Rawasi Fintech is preparing for its annual NCA ECC-1:2018 compliance assessment in Q4 2026. "
    "The scope is Core Banking Platform - User Access Management. Known weaknesses include no MFA for remote access, "
    "no PAM for privileged admin accounts, and no periodic access review records."
)


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR) / "db" / f"test_ai_provider_integration_{uuid.uuid4().hex}.sqlite3"
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
        name=f"AI Provider Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    perimeter = Perimeter.objects.create(
        folder=folder,
        name=f"AI Provider Perimeter {uuid.uuid4().hex[:8]}",
        ref_id=f"PER-PROV-{uuid.uuid4().hex[:8]}",
        description="Provider integration perimeter",
        lc_status="in_prod",
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        framework=framework,
        name=f"AI Provider Compliance Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    risk_assessment = RiskAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        risk_matrix=risk_matrix,
        name=f"AI Provider Risk Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    assets = [
        Asset.objects.create(
            folder=folder,
            name="Core Banking Application",
            type=Asset.Type.PRIMARY,
            ref_id=f"AST-CBA-{uuid.uuid4().hex[:6].upper()}",
            description="Primary core banking application",
        ),
        Asset.objects.create(
            folder=folder,
            name="Production User Accounts",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-PUA-{uuid.uuid4().hex[:6].upper()}",
            description="Production user account estate",
        ),
        Asset.objects.create(
            folder=folder,
            name="Privileged Admin Accounts",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-PAA-{uuid.uuid4().hex[:6].upper()}",
            description="Privileged administrative accounts",
        ),
        Asset.objects.create(
            folder=folder,
            name="Access Review Records",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-ARR-{uuid.uuid4().hex[:6].upper()}",
            description="Access review records and approvals",
        ),
        Asset.objects.create(
            folder=folder,
            name="Remote Access / VPN Service",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-VPN-{uuid.uuid4().hex[:6].upper()}",
            description="Remote access service",
        ),
        Asset.objects.create(
            folder=folder,
            name="Identity Provider / IAM System",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-IAM-{uuid.uuid4().hex[:6].upper()}",
            description="IAM service",
        ),
        Asset.objects.create(
            folder=folder,
            name="IAM Policies and Procedures",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-POL-{uuid.uuid4().hex[:6].upper()}",
            description="IAM policy and procedure library",
        ),
        Asset.objects.create(
            folder=folder,
            name="User Provisioning Records",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-UPR-{uuid.uuid4().hex[:6].upper()}",
            description="Provisioning and deprovisioning records",
        ),
    ]

    return {
        "folder": folder,
        "perimeter": perimeter,
        "compliance_assessment": compliance_assessment,
        "risk_assessment": risk_assessment,
        "framework": framework,
        "assets": assets,
    }


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


def _step1_payload(**overrides):
    payload = {
        "scenario_text": AL_RAWASI_SCENARIO,
        "preferred_framework": "ECC-1:2018",
        "assessment_period": {
            "label": "Q4 2026 readiness review",
            "start_date": "2026-10-01",
            "end_date": "2026-12-15",
        },
        "organization_hint": "Al-Rawasi Fintech",
        "scope_hint": "Core Banking Platform user access management scope.",
        "known_deadline": "2026-12-15",
        "known_trigger": "annual compliance review",
        "user_locale": "en",
        "strict_mode": True,
    }
    payload.update(overrides)
    return payload


def _step3a_payload(setup_context, **overrides):
    payload = {
        "source_step1_draft_hash": "sha256:" + "c" * 64,
        "case_setup_reference": {
            "folder_id": str(setup_context["folder"].id),
            "perimeter_id": str(setup_context["perimeter"].id),
            "compliance_assessment_id": str(setup_context["compliance_assessment"].id),
            "risk_assessment_id": str(setup_context["risk_assessment"].id),
        },
        "scenario_text": AL_RAWASI_SCENARIO,
        "scope_summary": "Core Banking Platform user access management scope for Q4 2026.",
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


def _step4a_payload(setup_context, **overrides):
    payload = {
        "source_step1_draft_hash": "sha256:" + "a" * 64,
        "source_asset_commit_hash": "sha256:" + "b" * 64,
        "case_setup_reference": {
            "folder_id": str(setup_context["folder"].id),
            "perimeter_id": str(setup_context["perimeter"].id),
            "compliance_assessment_id": str(setup_context["compliance_assessment"].id),
            "risk_assessment_id": str(setup_context["risk_assessment"].id),
            "selected_framework_id": str(setup_context["framework"].id),
        },
        "asset_references": [
            {
                "asset_id": str(asset.id),
                "name": asset.name,
                "ref_id": asset.ref_id,
                "asset_class": None,
                "type": asset.type,
            }
            for asset in setup_context["assets"]
        ],
        "scenario_text": AL_RAWASI_SCENARIO,
        "scope_summary": "Core Banking Platform user access management scope for Q4 2026.",
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


def _step2_payload(setup_context, **overrides):
    payload = {
        "approved_by_user": False,
        "source_step1_draft_hash": "sha256:" + "d" * 64,
        "source_step1_schema_version": "0.2.0",
        "dry_run": True,
        "idempotency_key": None,
        "framework_resolution": {
            "requested_framework_name": setup_context["framework"].name,
            "selected_framework_id": str(setup_context["framework"].id),
            "selected_loaded_library_id": None,
            "selected_stored_library_urn": None,
            "candidate_framework_ids": [str(setup_context["framework"].id)],
            "user_confirmed": True,
            "allow_auto_load": False,
        },
        "folder_domain_decision": {
            "action": "reuse",
            "platform_entity": "Folder",
            "selected_existing_id": str(setup_context["folder"].id),
            "human_approved": False,
            "rationale": "Reuse existing folder for dry-run",
            "source_reference": "step1",
        },
        "perimeter_decision": {
            "action": "reuse",
            "platform_entity": "Perimeter",
            "selected_existing_id": str(setup_context["perimeter"].id),
            "human_approved": False,
            "rationale": "Reuse existing perimeter for dry-run",
            "source_reference": "step1",
        },
        "compliance_assessment_decision": {
            "action": "reuse",
            "platform_entity": "ComplianceAssessment",
            "selected_existing_id": str(setup_context["compliance_assessment"].id),
            "human_approved": False,
            "rationale": "Reuse existing assessment for dry-run",
            "source_reference": "step1",
        },
        "risk_assessment_decision": {
            "action": "reuse",
            "platform_entity": "RiskAssessment",
            "selected_existing_id": str(setup_context["risk_assessment"].id),
            "human_approved": False,
            "rationale": "Reuse existing risk assessment for dry-run",
            "source_reference": "step1",
        },
    }
    payload.update(overrides)
    return payload


def _step3b_payload(setup_context, **overrides):
    payload = {
        "dry_run": True,
        "approved_by_user": False,
        "idempotency_key": None,
        "source_step1_draft_hash": "sha256:" + "e" * 64,
        "source_asset_draft_hash": "sha256:" + "f" * 64,
        "case_setup_reference": {
            "folder_id": str(setup_context["folder"].id),
            "perimeter_id": str(setup_context["perimeter"].id),
            "compliance_assessment_id": str(setup_context["compliance_assessment"].id),
            "risk_assessment_id": str(setup_context["risk_assessment"].id),
            "selected_framework_id": str(setup_context["framework"].id),
        },
        "asset_decisions": [
            {
                "temporary_id": "AST-CAND-001",
                "action": "defer",
                "human_approved": False,
                "original_suggestion_summary": {
                    "proposed_name": "Core Banking Application",
                    "proposed_asset_type": {"value": "PR", "label": "Primary"},
                    "confidence": 0.9,
                    "ambiguity_flags": [],
                },
                "reviewer_notes": "defer in dry-run",
                "ambiguity_resolution": None,
                "duplicate_resolution": None,
            }
        ],
    }
    payload.update(overrides)
    return payload


class _MockHttpResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _configure_local_provider_env(
    monkeypatch,
    *,
    base_url: str = "http://127.0.0.1:11434",
    default_model: str = "qwen3:4b-instruct",
    case_model: str = "qwen3:4b-instruct",
    asset_model: str = "qwen3:4b-instruct",
    control_model: str = "qwen3:4b-instruct",
):
    monkeypatch.setenv("AI_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_AI_API_STYLE", "ollama")
    monkeypatch.setenv("LOCAL_AI_BASE_URL", base_url)
    monkeypatch.setenv("LOCAL_AI_MODEL_DEFAULT", default_model)
    monkeypatch.setenv("LOCAL_AI_MODEL_CASE_INTAKE", case_model)
    monkeypatch.setenv("LOCAL_AI_MODEL_ASSET_SUGGESTION", asset_model)
    monkeypatch.setenv("LOCAL_AI_MODEL_APPLIED_CONTROL_SUGGESTION", control_model)
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
def test_provider_fallback_when_not_configured(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.delenv("LOCAL_AI_API_STYLE", raising=False)
    monkeypatch.delenv("LOCAL_AI_BASE_URL", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_DEFAULT", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_CASE_INTAKE", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_ASSET_SUGGESTION", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_APPLIED_CONTROL_SUGGESTION", raising=False)

    assert get_case_intake_provider() is None
    assert get_asset_suggestion_provider() is None
    assert get_applied_control_suggestion_provider() is None


@pytest.mark.django_db
def test_step1_configured_local_provider_path_and_no_write(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)
    draft = build_case_intake_fallback_draft(_step1_payload())

    calls = []

    def _handler(request, timeout, body):
        calls.append({"url": request.full_url, "body": body})
        return {
            "model": body["model"],
            "response": json.dumps(draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-case-intake"), _step1_payload(), format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["source_summary"]["provider_mode"] == "configured_local_provider"
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    assert before == after


@pytest.mark.django_db
def test_step3a_configured_local_provider_path_duplicate_detection_and_no_write(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)
    request_payload = _step3a_payload(setup_context)
    fallback_draft = build_asset_suggestion_fallback_draft(
        request_payload,
        {
            "folder": setup_context["folder"],
            "perimeter": setup_context["perimeter"],
            "compliance_assessment": setup_context["compliance_assessment"],
            "risk_assessment": setup_context["risk_assessment"],
            "framework": setup_context["framework"],
        },
    )

    calls = []

    def _handler(request, timeout, body):
        calls.append({"url": request.full_url, "body": body})
        return {
            "model": body["model"],
            "response": json.dumps(fallback_draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-asset-suggestion"), request_payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert body["duplicate_candidates"]
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    assert before == after


@pytest.mark.django_db
def test_step4a_configured_local_provider_path_asset_linking_and_no_write(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)
    request_payload = _step4a_payload(setup_context)
    minimal_draft = {
        "candidate_applied_controls": [
            {
                "temporary_id": "CTL-CAND-001",
                "proposed_name": "Multi-Factor Authentication for Remote Access",
                "proposed_description": "Require MFA for remote access.",
                "rationale": "Addresses remote access weakness.",
                "related_weaknesses": ["No MFA for remote access"],
                "confidence": 0.9,
            }
        ]
    }

    calls = []

    def _handler(request, timeout, body):
        calls.append({"url": request.full_url, "body": body})
        return {
            "model": body["model"],
            "response": json.dumps(minimal_draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        request_payload,
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert len(body["candidate_applied_controls"]) == 1

    allowed_ids = {str(asset.id) for asset in setup_context["assets"]}
    for item in body["candidate_applied_controls"]:
        assert set(str(asset_id) for asset_id in item["linked_asset_ids"]).issubset(allowed_ids)
        assert item["source_text_references"]
        assert item["allowed_next_actions"]

    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    assert "step4a_minimal_contract" in calls[0]["body"]["prompt"]
    assert "step4a_compact_skeleton" not in calls[0]["body"]["prompt"]
    assert before == after


@pytest.mark.django_db
def test_malformed_provider_output_is_rejected_without_writes(
    authenticated_client,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)

    calls = []

    def _handler(request, timeout, body):
        calls.append({"url": request.full_url, "body": body})
        return {
            "model": body["model"],
            "response": "not json",
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-case-intake"), _step1_payload(), format="json")
    after = _counts_snapshot()

    assert response.status_code == 422
    assert response.json()["provider_mode"] == "local_provider_error_blocked"
    assert calls
    assert before == after


@pytest.mark.django_db
def test_unsafe_provider_output_is_guardrail_rejected_without_writes(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)
    request_payload = _step4a_payload(setup_context)
    resolved_assets = [
        {
            "instance": asset,
            "reference": {
                "asset_id": str(asset.id),
                "name": asset.name,
                "ref_id": asset.ref_id,
                "asset_class": None,
                "type": asset.type,
            },
        }
        for asset in setup_context["assets"]
    ]
    unsafe_draft = build_applied_control_suggestion_fallback_draft(
        request_payload,
        {
            "folder": setup_context["folder"],
            "perimeter": setup_context["perimeter"],
            "compliance_assessment": setup_context["compliance_assessment"],
            "risk_assessment": setup_context["risk_assessment"],
            "framework": setup_context["framework"],
        },
        resolved_assets,
    )
    unsafe_draft["candidate_applied_controls"][0]["allowed_next_actions"].append("create_now")

    calls = []

    def _handler(request, timeout, body):
        calls.append({"url": request.full_url, "body": body})
        return {
            "model": body["model"],
            "response": json.dumps(unsafe_draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        request_payload,
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    assert response.json()["error_code"] == "ai_applied_control_suggestion_guardrails_failed"
    assert calls
    assert before == after


def test_ollama_outer_response_parses_inner_json_string(monkeypatch):
    provider = LocalAiProvider(
        base_url="http://127.0.0.1:11434",
        base_url_safe=True,
        base_url_warning=None,
    )

    def _handler(request, timeout, body):
        return {
            "model": body["model"],
            "response": "{\"ok\": true, \"cloud_used\": false}",
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    parsed = provider.generate_structured(
        capability="case_intake",
        model="qwen3:4b-instruct",
        system_prompt="Return JSON only.",
        user_payload={"x": 1},
        json_schema={"type": "object"},
        timeout_seconds=5,
        max_output_tokens=100,
        temperature=0.1,
        schema_name="demo",
    )

    assert parsed == {"ok": True, "cloud_used": False}


@pytest.mark.django_db
def test_cloud_base_url_is_blocked_without_http_call(authenticated_client, monkeypatch):
    _configure_local_provider_env(
        monkeypatch,
        base_url="https://api.openai.com",
    )

    called = {"count": 0}

    def _handler(request, timeout, body):
        called["count"] += 1
        return {
            "model": body["model"],
            "response": "{}",
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-case-intake"), _step1_payload(), format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["source_summary"]["provider_mode"] == "local_provider_error_fallback"
    assert any(item["code"] == "local_provider_error_fallback" for item in body.get("warnings", []))
    assert called["count"] == 0
    assert before == after


@pytest.mark.django_db
def test_provider_exception_falls_back_with_sanitized_message(
    authenticated_client,
    monkeypatch,
):
    class RuntimeFailureProvider:
        available = True

        def build_case_intake_draft(self, request_payload):
            raise CaseIntakeProviderError(
                "ai_provider_request_failed",
                "The local AI provider timed out before returning a response.",
                allow_fallback=True,
            )

    monkeypatch.setattr(
        "ai_onboarding.case_intake_service.get_case_intake_provider",
        lambda: RuntimeFailureProvider(),
    )

    response = authenticated_client.post(reverse("ai-case-intake"), _step1_payload(), format="json")
    assert response.status_code == 200

    body = response.json()
    assert body["source_summary"]["provider_mode"] == "local_provider_error_fallback"
    warning_codes = {item["code"] for item in body.get("warnings", [])}
    assert "local_provider_error_fallback" in warning_codes


def test_model_selection_prefers_capability_specific_env_and_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("LOCAL_AI_MODEL_DEFAULT", "default-model")
    monkeypatch.setenv("LOCAL_AI_MODEL_CASE_INTAKE", "case-model")
    monkeypatch.setenv("LOCAL_AI_MODEL_ASSET_SUGGESTION", "asset-model")
    monkeypatch.setenv("LOCAL_AI_MODEL_APPLIED_CONTROL_SUGGESTION", "control-model")

    assert resolve_advisory_capability_config(CAPABILITY_CASE_INTAKE).model == "case-model"
    assert resolve_advisory_capability_config(CAPABILITY_ASSET_SUGGESTION).model == "asset-model"
    assert (
        resolve_advisory_capability_config(CAPABILITY_APPLIED_CONTROL_SUGGESTION).model
        == "control-model"
    )

    monkeypatch.delenv("LOCAL_AI_MODEL_CASE_INTAKE", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_ASSET_SUGGESTION", raising=False)
    monkeypatch.delenv("LOCAL_AI_MODEL_APPLIED_CONTROL_SUGGESTION", raising=False)

    assert resolve_advisory_capability_config(CAPABILITY_CASE_INTAKE).model == "default-model"
    assert resolve_advisory_capability_config(CAPABILITY_ASSET_SUGGESTION).model == "default-model"
    assert (
        resolve_advisory_capability_config(CAPABILITY_APPLIED_CONTROL_SUGGESTION).model
        == "default-model"
    )


@pytest.mark.django_db
def test_write_endpoints_do_not_invoke_advisory_ai_provider(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    call_count = {"count": 0}

    def fail_if_called(*args, **kwargs):
        call_count["count"] += 1
        raise AssertionError("Write endpoints must not invoke advisory AI generation")

    monkeypatch.setenv("AI_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_AI_API_STYLE", "ollama")
    monkeypatch.setenv("LOCAL_AI_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("LOCAL_AI_MODEL_DEFAULT", "qwen3:4b-instruct")
    monkeypatch.setattr("ai_onboarding.llm_provider.LocalAiProvider.generate_structured", fail_if_called)

    step2_response = authenticated_client.post(
        reverse("ai-case-setup"),
        _step2_payload(setup_context),
        format="json",
    )
    assert step2_response.status_code == 200

    step3b_response = authenticated_client.post(
        reverse("ai-asset-commit"),
        _step3b_payload(setup_context),
        format="json",
    )
    assert step3b_response.status_code == 200

    assert call_count["count"] == 0
