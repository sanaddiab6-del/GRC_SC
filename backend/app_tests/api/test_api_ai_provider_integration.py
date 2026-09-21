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
    CAPABILITY_AUDIT_REPORT_SUGGESTION,
    CAPABILITY_CASE_INTAKE,
    CAPABILITY_EVIDENCE_FINDING_SUGGESTION,
    CAPABILITY_RISK_SCENARIO_SUGGESTION,
    SUPPORTED_CAPABILITIES,
    resolve_advisory_capability_config,
)
from ai_onboarding.llm_prompts import get_system_prompt
from ai_onboarding.llm_errors import AiProviderExecutionError
from ai_onboarding.llm_provider import (
    PROMPT_CHARS_PER_TOKEN,
    LocalAiProvider,
    _build_ollama_prompt,
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


# The shape the local model actually returns for Step 1: real findings, but plain strings and
# flat objects instead of the full explainable contract.
OFF_CONTRACT_STEP1_OUTPUT = {
    "draft_type": "AiCaseIntakeDraft",
    "overall_confidence": 0.5,
    "needs_human_review": True,
    "blocking_questions": ["Which administrators still sign in without MFA?"],
    "case_context": {"organization": "Al-Rawasi Fintech"},
    "vulnerability_drafts": [
        {
            "description": "Privileged users sign in without multi-factor authentication",
            "severity": "High",
            "impact": "Account takeover of administrator sessions",
            "mitigation": "Enforce MFA for all privileged accounts",
        }
    ],
    "human_review_checklist": ["Confirm the list of privileged administrators."],
}


@pytest.mark.django_db
def test_step1_keeps_off_contract_provider_findings_and_does_not_write(
    authenticated_client, monkeypatch
):
    _configure_local_provider_env(monkeypatch)
    _install_mock_ollama_urlopen(
        monkeypatch,
        lambda request, timeout, body: {
            "model": body["model"],
            "response": json.dumps(OFF_CONTRACT_STEP1_OUTPUT),
            "done": True,
        },
    )

    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-case-intake"), _step1_payload(), format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["source_summary"]["provider_mode"] == "configured_local_provider"
    assert [item["name"] for item in body["vulnerability_drafts"]] == [
        "Privileged users sign in without multi-factor authentication"
    ]
    vulnerability = body["vulnerability_drafts"][0]
    assert vulnerability["platform_entity"] == "Vulnerability"
    assert vulnerability["needs_review"] is True
    assert "Enforce MFA for all privileged accounts" in vulnerability["rationale"]
    assert "Which administrators still sign in without MFA?" in [
        question["question_text"] for question in body["blocking_questions"]
    ]
    assert "Confirm the list of privileged administrators." in [
        item["label"] for item in body["human_review_checklist"]
    ]
    warning = next(
        item for item in body["warnings"] if item["code"] == "configured_local_provider_shape_normalized"
    )
    assert "vulnerability_drafts" in warning["affected_fields"]
    assert before == after


@pytest.mark.django_db
def test_step1_labels_unusable_provider_output_as_discarded(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)
    _install_mock_ollama_urlopen(
        monkeypatch,
        lambda request, timeout, body: {
            "model": body["model"],
            "response": json.dumps(
                {"draft_type": "AiCaseIntakeDraft", "overall_confidence": 0.5, "needs_human_review": True}
            ),
            "done": True,
        },
    )

    response = authenticated_client.post(reverse("ai-case-intake"), _step1_payload(), format="json")

    assert response.status_code == 200
    body = response.json()
    # Deterministic text must never be presented as a local AI result.
    assert body["source_summary"]["provider_mode"] == "configured_local_provider_output_discarded"
    assert any(item["code"] == "configured_local_provider_output_discarded" for item in body["warnings"])
    assert body["vulnerability_drafts"] == []


@pytest.mark.django_db(transaction=True)
def test_suggestion_does_not_hold_the_sqlite_write_lock_during_the_model_call(
    authenticated_client, monkeypatch
):
    # A suggestion used to hold BEGIN IMMEDIATE for the whole model call, so any concurrent
    # write (the auth token refresh) failed with "database is locked" and the UI logged out.
    import sqlite3

    from django.db import connection

    if connection.vendor != "sqlite":
        pytest.skip("The write lock only exists on SQLite.")

    _configure_local_provider_env(monkeypatch)
    draft = build_case_intake_fallback_draft(_step1_payload())
    concurrent_writes = []

    def _handler(request, timeout, body):
        probe = sqlite3.connect(str(connection.settings_dict["NAME"]), timeout=1)
        try:
            probe.execute("CREATE TABLE IF NOT EXISTS ai_lock_probe (id INTEGER)")
            probe.execute("DROP TABLE ai_lock_probe")
            probe.commit()
            concurrent_writes.append("ok")
        except sqlite3.OperationalError as exc:
            concurrent_writes.append(str(exc))
        finally:
            probe.close()
        return {"model": body["model"], "response": json.dumps(draft, default=str), "done": True}

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    before = _counts_snapshot()
    response = authenticated_client.post(reverse("ai-case-intake"), _step1_payload(), format="json")

    assert response.status_code == 200
    assert concurrent_writes == ["ok"]
    assert _counts_snapshot() == before


@pytest.mark.parametrize("capability", sorted(SUPPORTED_CAPABILITIES))
def test_every_capability_prompt_forbids_echoing_the_instruction_envelope(capability):
    # A small local model given the instruction envelope without this rule returned the
    # envelope itself (capability/schema_name/input/output_contract) instead of an answer.
    prompt = _build_ollama_prompt(
        capability=capability,
        system_prompt="system",
        user_payload={"request": {}},
        json_schema={"required": []},
        schema_name="schema",
    )

    assert "Do not echo this instruction" in prompt
    for wrapper_key in ("capability", "schema_name", "input", "output_contract"):
        assert wrapper_key in prompt.split("Do not echo this instruction", 1)[1].split("\n", 1)[0]


_GENERATE_KWARGS = dict(
    capability=CAPABILITY_CASE_INTAKE,
    model="qwen3:4b-instruct",
    system_prompt="system",
    json_schema={"required": []},
    timeout_seconds=60,
    max_output_tokens=2000,
    temperature=0.1,
    schema_name="schema",
)


def test_local_provider_sizes_the_context_window_only_when_the_prompt_needs_it(monkeypatch):
    # Ollama's default window silently truncated the Step 7A prompt (9189 tokens to 2050),
    # dropping the system prompt and most of the candidate list.
    bodies = []
    _install_mock_ollama_urlopen(
        monkeypatch,
        lambda request, timeout, body: bodies.append(body)
        or {"model": body["model"], "response": "{}", "done": True},
    )
    provider = LocalAiProvider(
        base_url="http://127.0.0.1:11434", base_url_safe=True, base_url_warning=None
    )

    provider.generate_structured(user_payload={"request": {"note": "short"}}, **_GENERATE_KWARGS)
    provider.generate_structured(
        user_payload={"request": {"note": "x" * 30000}}, **_GENERATE_KWARGS
    )

    assert "num_ctx" not in bodies[0]["options"]
    large = bodies[1]
    assert large["options"]["num_ctx"] > 4096
    room_for_prompt = large["options"]["num_ctx"] - large["options"]["num_predict"]
    assert room_for_prompt * PROMPT_CHARS_PER_TOKEN >= len(large["prompt"])


def test_local_provider_refuses_a_prompt_larger_than_the_context_limit(monkeypatch):
    calls = []
    _install_mock_ollama_urlopen(
        monkeypatch, lambda request, timeout, body: calls.append(body) or {"response": "{}"}
    )
    provider = LocalAiProvider(
        base_url="http://127.0.0.1:11434",
        base_url_safe=True,
        base_url_warning=None,
        context_window_max=8192,
    )

    with pytest.raises(AiProviderExecutionError) as excinfo:
        provider.generate_structured(
            user_payload={"request": {"note": "x" * 60000}}, **_GENERATE_KWARGS
        )

    assert excinfo.value.error_code == "local_ai_prompt_exceeds_context"
    assert calls == []


def test_step11a_prompt_keeps_the_response_within_the_output_budget():
    # Up to 20 prose sections filled the whole output budget (done_reason "length"), so the
    # report JSON was cut off and Step 11A was rejected, after a generation longer than the proxy allows.
    prompt = get_system_prompt(CAPABILITY_AUDIT_REPORT_SUGGESTION)

    assert "Return at most 10 sections" in prompt
    assert "Keep each section's content to at most two short sentences." in prompt
    # The guardrails require recommended_next_steps; the model left it out when only the
    # schema's shorter required list named the top-level fields.
    assert "recommended_next_steps must be an array of at most 5 short strings." in prompt
    assert "Keep the whole response short so it is a single complete JSON object." in prompt


def test_step8a_prompt_keeps_the_response_within_the_output_budget():
    # Five verbose scenarios filled the whole output budget (done_reason "length"), so the
    # JSON was cut off and Step 8A was rejected, after a generation longer than the proxy allows.
    prompt = get_system_prompt(CAPABILITY_RISK_SCENARIO_SUGGESTION)

    assert "Return at most 3 risk scenarios" in prompt
    assert "recommended_next_steps must be an array of at most 2 short strings." in prompt
    assert "Keep the whole response short so it is a single complete JSON object." in prompt


def test_step5a_prompt_keeps_the_response_within_the_output_budget():
    # Without an item cap and the compact-reference rule, the local model filled the whole
    # output budget and its JSON was cut off (done_reason "length"), so Step 5A was blocked.
    prompt = get_system_prompt(CAPABILITY_EVIDENCE_FINDING_SUGGESTION)

    assert "Return at most 3 evidence_requests, at most 3 audit_questions" in prompt
    assert "must be arrays of the provided id strings only" in prompt
    assert "Keep the whole response short so it is a single complete JSON object." in prompt


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
