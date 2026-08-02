import json
import uuid

import pytest
from django.conf import settings as django_settings
from django.urls import reverse
from knox.models import AuthToken

from ai_onboarding.applied_control_suggestion_service import (
    build_applied_control_suggestion_fallback_draft,
)
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
        / f"test_ai_applied_control_suggestion_{uuid.uuid4().hex}.sqlite3"
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
def setup_context(framework, risk_matrix):
    folder = Folder.objects.create(
        name=f"AI Step 4A Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    perimeter = Perimeter.objects.create(
        folder=folder,
        name=f"AI Step 4A Perimeter {uuid.uuid4().hex[:8]}",
        ref_id=f"PER-STEP4A-{uuid.uuid4().hex[:8]}",
        description="Step 4A applied-control suggestion scope perimeter",
        lc_status="in_prod",
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        framework=framework,
        name=f"AI Step 4A Compliance Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    risk_assessment = RiskAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        risk_matrix=risk_matrix,
        name=f"AI Step 4A Risk Assessment {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    assets = [
        Asset.objects.create(
            folder=folder,
            name="Core Banking Application",
            type=Asset.Type.PRIMARY,
            ref_id=f"AST-CBA-{uuid.uuid4().hex[:6].upper()}",
            description="Primary core banking application.",
        ),
        Asset.objects.create(
            folder=folder,
            name="Production User Accounts",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-PUA-{uuid.uuid4().hex[:6].upper()}",
            description="Production user account estate.",
        ),
        Asset.objects.create(
            folder=folder,
            name="Privileged Admin Accounts",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-PAA-{uuid.uuid4().hex[:6].upper()}",
            description="Privileged administrative accounts.",
        ),
        Asset.objects.create(
            folder=folder,
            name="Access Review Records",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-ARR-{uuid.uuid4().hex[:6].upper()}",
            description="Access review records and approvals.",
        ),
        Asset.objects.create(
            folder=folder,
            name="Remote Access / VPN Service",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-VPN-{uuid.uuid4().hex[:6].upper()}",
            description="Remote access service.",
        ),
        Asset.objects.create(
            folder=folder,
            name="Identity Provider / IAM System",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-IAM-{uuid.uuid4().hex[:6].upper()}",
            description="IAM service.",
        ),
        Asset.objects.create(
            folder=folder,
            name="IAM Policies and Procedures",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-POL-{uuid.uuid4().hex[:6].upper()}",
            description="IAM policy and procedure library.",
        ),
        Asset.objects.create(
            folder=folder,
            name="User Provisioning Records",
            type=Asset.Type.SUPPORT,
            ref_id=f"AST-UPR-{uuid.uuid4().hex[:6].upper()}",
            description="Provisioning and deprovisioning records.",
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


def _asset_source_temporary_id(asset):
    return f"asset-ref-{asset.ref_id.lower()}"


def _asset_reference(asset):
    return {
        "asset_id": str(asset.id),
        "name": asset.name,
        "ref_id": asset.ref_id,
        "asset_class": None,
        "type": asset.type,
        "source_temporary_id": _asset_source_temporary_id(asset),
    }


def _resolved_assets(setup_context):
    return [
        {
            "instance": asset,
            "reference": _asset_reference(asset),
        }
        for asset in setup_context["assets"]
    ]


def _request_payload(setup_context, **overrides):
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
        "asset_references": [_asset_reference(asset) for asset in setup_context["assets"]],
        "scenario_text": AL_RAWASI_SCENARIO,
        "scope_summary": "Core Banking Platform user access management scope for the Q4 2026 ECC review.",
        "known_weaknesses": [
            "No MFA for remote access",
            "No PAM for privileged admin accounts",
            "No periodic user access review",
            "Formal access review documentation is missing",
        ],
        "selected_framework_id": str(setup_context["framework"].id),
        "user_locale": "en",
        "strict_mode": True,
    }
    payload.update(overrides)
    return payload


def _fallback_draft(setup_context, request_payload):
    return build_applied_control_suggestion_fallback_draft(
        request_payload,
        {
            "folder": setup_context["folder"],
            "perimeter": setup_context["perimeter"],
            "compliance_assessment": setup_context["compliance_assessment"],
            "risk_assessment": setup_context["risk_assessment"],
            "framework": setup_context["framework"],
        },
        _resolved_assets(setup_context),
    )


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

    def build_applied_control_suggestion_draft(self, request_payload):
        return self.payload


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
    monkeypatch.setenv("LOCAL_AI_MODEL_APPLIED_CONTROL_SUGGESTION", "qwen3:4b-instruct")
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
def test_ai_applied_control_suggestion_requires_authentication(client, setup_context):
    response = client.post(
        reverse("ai-applied-control-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_valid_al_rawasi_scenario_returns_structured_step4a_advisory_draft(
    authenticated_client,
    setup_context,
):
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["draft_type"] == "AiAppliedControlSuggestionDraft"
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["source_summary"]["provider_mode"] == "provider_not_configured_fallback"
    assert body["needs_human_review"] is True
    assert isinstance(body["candidate_applied_controls"], list)
    assert body["candidate_applied_controls"]
    assert "overall_confidence" in body
    assert "prepare_applied_control_commit_dry_run" in body["next_allowed_steps"]


@pytest.mark.django_db
def test_configured_local_provider_path_uses_mocked_ollama_and_does_not_write(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)
    request_payload = _request_payload(setup_context)
    provider_draft = {
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
            "response": json.dumps(provider_draft, default=str),
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
    assert body["source_summary"]["provider_mode"] == "configured_local_provider"
    assert len(body["candidate_applied_controls"]) == 1
    candidate = body["candidate_applied_controls"][0]
    assert candidate["linked_asset_ids"]
    assert candidate["linked_asset_temporary_ids"]
    assert candidate["proposed_control_category"] == "technical"
    assert candidate["proposed_status"] == "to_do"
    assert candidate["proposed_implementation_state"] == "planned"
    assert candidate["related_framework_requirements"] == []
    assert candidate["source_text_references"]
    assert candidate["human_review_status"] == "pending_review"
    assert candidate["ambiguity_flags"] == []
    assert candidate["allowed_next_actions"]
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    prompt = calls[0]["body"]["prompt"]
    assert "step4a_minimal_contract" in prompt
    assert "step4a_compact_skeleton" not in prompt
    assert before == after


@pytest.mark.django_db
def test_provider_output_missing_asset_links_is_normalized_before_guardrails_without_writes(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    request_payload = _request_payload(setup_context)
    provider_draft = {
        "candidate_applied_controls": [
            {
                "temporary_id": f"CTL-CAND-{index:03d}",
                "proposed_name": f"Control Candidate {index}",
                "proposed_description": "Suggested control.",
                "rationale": "Addresses an approved weakness.",
                "related_weaknesses": ["No MFA for remote access"],
                "confidence": 0.8,
                "linked_asset_ids": [],
                "linked_asset_temporary_ids": [],
            }
            for index in range(1, 7)
        ]
    }

    monkeypatch.setattr(
        "ai_onboarding.applied_control_suggestion_service.get_applied_control_suggestion_provider",
        lambda: FakeProvider(provider_draft),
    )

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
    assert len(body["candidate_applied_controls"]) == 4

    approved_asset_ids = {str(asset.id) for asset in setup_context["assets"]}
    approved_temporary_ids = {_asset_source_temporary_id(asset) for asset in setup_context["assets"]}
    for candidate in body["candidate_applied_controls"]:
        assert {str(asset_id) for asset_id in candidate["linked_asset_ids"]} == approved_asset_ids
        assert set(candidate["linked_asset_temporary_ids"]) == approved_temporary_ids

    assert before == after


@pytest.mark.django_db
def test_response_includes_relevant_candidate_applied_controls(authenticated_client, setup_context):
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    candidates = body["candidate_applied_controls"]
    combined_candidates = [
        " ".join(
            [
                item["proposed_name"],
                item.get("proposed_description") or "",
                item["rationale"],
                " ".join(item["related_weaknesses"]),
            ]
        ).lower()
        for item in candidates
    ]

    assert candidates
    assert any("multi-factor authentication" in item and "remote access" in item for item in combined_candidates)
    assert any("privileged access management" in item and "admin" in item for item in combined_candidates)
    assert any("periodic user access review" in item for item in combined_candidates)
    assert any("formal" in item and "document" in item and "access review" in item for item in combined_candidates)


@pytest.mark.django_db
def test_step4a_links_suggestions_to_approved_asset_and_case_context(
    authenticated_client,
    setup_context,
):
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        _request_payload(setup_context),
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    source_summary = body["source_summary"]
    assert source_summary["folder_id"] == str(setup_context["folder"].id)
    assert source_summary["perimeter_id"] == str(setup_context["perimeter"].id)
    assert source_summary["compliance_assessment_id"] == str(setup_context["compliance_assessment"].id)
    assert source_summary["risk_assessment_id"] == str(setup_context["risk_assessment"].id)
    assert source_summary["selected_framework_id"] == str(setup_context["framework"].id)
    assert source_summary["asset_count"] == len(setup_context["assets"])

    allowed_asset_ids = {str(asset.id) for asset in setup_context["assets"]}
    allowed_temporary_ids = {_asset_source_temporary_id(asset) for asset in setup_context["assets"]}
    candidates = body["candidate_applied_controls"]

    assert all(item["linked_asset_ids"] for item in candidates)
    for item in candidates:
        assert set(str(asset_id) for asset_id in item["linked_asset_ids"]).issubset(allowed_asset_ids)
        assert set(item["linked_asset_temporary_ids"]).issubset(allowed_temporary_ids)
    assert any(item["linked_asset_temporary_ids"] for item in candidates)


@pytest.mark.django_db
def test_step4a_does_not_write_grc_records(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_malformed_local_provider_output_is_rejected_safely_without_writes(
    authenticated_client,
    setup_context,
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
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        _request_payload(setup_context),
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "local_ai_provider_invalid_output"
    assert body["provider_mode"] == "local_provider_error_blocked"
    assert calls
    assert before == after


@pytest.mark.django_db
def test_unsafe_provider_output_is_guardrail_rejected_without_writes(
    authenticated_client,
    setup_context,
    monkeypatch,
):
    _configure_local_provider_env(monkeypatch)
    request_payload = _request_payload(setup_context)
    unsafe_draft = _fallback_draft(setup_context, request_payload)
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name, value",
    [
        ("compliance_result", "compliant"),
        ("final_result", "approved"),
        ("result", "compliant"),
        ("risk_acceptance", {"decision": "accept"}),
        ("risk_decision", "accept"),
        ("audit_closure", True),
        ("close_audit", True),
        ("status", "closed"),
        ("evidence_drafts", [{"name": "forbidden"}]),
        ("finding_drafts", [{"name": "forbidden"}]),
        ("vulnerability_drafts", [{"name": "forbidden"}]),
        ("remediation_drafts", [{"name": "forbidden"}]),
        ("risk_scenario_drafts", [{"name": "forbidden"}]),
    ],
)
def test_step4a_rejects_out_of_scope_request_fields_without_writes(
    authenticated_client,
    setup_context,
    field_name,
    value,
):
    before = _counts_snapshot()
    payload = _request_payload(setup_context)
    payload[field_name] = value

    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        payload,
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 400
    assert field_name in response.json()
    assert before == after


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name, value",
    [
        ("compliance_result", "compliant"),
        ("final_result", "approved"),
        ("result", "compliant"),
        ("risk_acceptance", {"decision": "accept"}),
        ("audit_closure", True),
        ("evidence_drafts", [{"name": "forbidden"}]),
        ("finding_drafts", [{"name": "forbidden"}]),
        ("vulnerability_drafts", [{"name": "forbidden"}]),
        ("remediation_drafts", [{"name": "forbidden"}]),
        ("risk_scenario_drafts", [{"name": "forbidden"}]),
    ],
)
def test_provider_output_rejects_forbidden_top_level_fields_without_writes(
    authenticated_client,
    setup_context,
    monkeypatch,
    field_name,
    value,
):
    request_payload = _request_payload(setup_context)
    invalid_draft = _fallback_draft(setup_context, request_payload)
    invalid_draft[field_name] = value
    monkeypatch.setattr(
        "ai_onboarding.applied_control_suggestion_service.get_applied_control_suggestion_provider",
        lambda: FakeProvider(invalid_draft),
    )

    before = _counts_snapshot()
    response = authenticated_client.post(
        reverse("ai-applied-control-suggestion"),
        request_payload,
        format="json",
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    assert response.json()["error_code"] == "ai_applied_control_suggestion_draft_validation_failed"
    assert before == after
