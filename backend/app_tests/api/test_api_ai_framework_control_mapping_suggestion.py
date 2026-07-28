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
    RequirementNode,
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
        / f"test_ai_framework_control_mapping_suggestion_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_FRAMEWORK_CONTROL_MAPPING_SUGGESTION", raising=False)
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


CANDIDATE_IAM = {
    "reference": "urn:sanad:req-node:sama-ecc:2-3-1",
    "code": "ECC-2-3-1",
    "title": "Identity and Access Management",
    "description": "Cybersecurity requirements for identity and access management shall be defined.",
    "domain": "Cybersecurity Defence",
    "section": "2-3",
    "source": "SAMA ECC-1:2018",
}

CANDIDATE_MFA = {
    "reference": "urn:sanad:req-node:sama-ecc:2-3-3-2",
    "code": "ECC-2-3-3-2",
    "title": "Multi-Factor Authentication for Remote Access",
    "description": "Multi-factor authentication shall be applied for remote access.",
    "domain": "Cybersecurity Defence",
    "section": "2-3-3",
    "source": "SAMA ECC-1:2018",
}

CANDIDATE_ACCESS_REVIEW = {
    "reference": "urn:sanad:req-node:sama-ecc:2-3-3-5",
    "code": "ECC-2-3-3-5",
    "title": "Periodic Access Control Review",
    "description": "User access rights shall be reviewed periodically.",
    "domain": "Cybersecurity Defence",
    "section": "2-3-3",
    "source": "SAMA ECC-1:2018",
}

CANDIDATE_CONTROLS = [CANDIDATE_IAM, CANDIDATE_MFA, CANDIDATE_ACCESS_REVIEW]


def _request_payload(**overrides):
    payload = {
        "case_summary": AL_RAWASI_CASE_SUMMARY,
        "scenario_name": "Core Banking Platform - User Access Management",
        "folder_reference": {
            "folder_id": str(uuid.uuid4()),
            "folder_name": "Al-Rawasi Fintech",
        },
        "framework_name": "SAMA ECC-1:2018",
        "assessment_name": "Q4 2026 ECC Compliance Assessment",
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
        "remediation_actions": [
            {
                "reference": "RMD-MFA-001",
                "title": "Implement and enforce MFA for remote access",
                "description": "Enable and enforce MFA for all remote access users.",
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
        "candidate_framework_controls": [dict(control) for control in CANDIDATE_CONTROLS],
        "user_locale": "en",
        "strict_mode": True,
    }
    payload.update(overrides)
    return payload


def _counts_snapshot():
    return {
        "Folder": Folder.objects.count(),
        "Perimeter": Perimeter.objects.count(),
        "Framework": Framework.objects.count(),
        "RequirementNode": RequirementNode.objects.count(),
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
    monkeypatch.setenv(
        "LOCAL_AI_MODEL_FRAMEWORK_CONTROL_MAPPING_SUGGESTION", "qwen3:4b-instruct"
    )
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_mock_ollama_urlopen(monkeypatch, handler):
    def _mock_urlopen(request, timeout=0):
        request_body = json.loads(request.data.decode("utf-8"))
        response_payload = handler(request, timeout, request_body)
        return _MockHttpResponse(response_payload)

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _valid_provider_mapping(**overrides):
    mapping = {
        "temporary_id": "framework_mapping_1",
        "framework_control_reference": CANDIDATE_MFA["reference"],
        "framework_control_code": CANDIDATE_MFA["code"],
        "framework_control_title": CANDIDATE_MFA["title"],
        "framework_control_description": CANDIDATE_MFA["description"],
        "framework_name": "SAMA ECC-1:2018",
        "mapping_type": "supports_finding",
        "linked_finding_reference": "FND-CAND-001",
        "linked_finding_title": "MFA is not documented or not enforced for remote access.",
        "linked_applied_control_reference": "CTL-MFA-001",
        "linked_applied_control_title": "Multi-Factor Authentication for Remote Access",
        "linked_remediation_action_reference": "RMD-MFA-001",
        "linked_remediation_action_title": "Implement and enforce MFA for remote access",
        "rationale": (
            "The finding about unenforced MFA for remote access relates to the existing "
            "framework control on multi-factor authentication for remote access."
        ),
        "evidence_needed": [
            "MFA policy",
            "MFA configuration evidence for remote access",
        ],
        "confidence": 0.88,
        "review_status": "pending_review",
    }
    mapping.update(overrides)
    return mapping


def _install_provider_returning(monkeypatch, provider_draft):
    _configure_local_provider_env(monkeypatch)

    def _handler(request, timeout, body):
        return {
            "model": body["model"],
            "response": json.dumps(provider_draft, default=str),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)


def _post(client, **overrides):
    return client.post(
        reverse("ai-framework-control-mapping-suggestion"),
        _request_payload(**overrides),
        format="json",
    )


@pytest.mark.django_db
def test_ai_framework_control_mapping_suggestion_requires_authentication(client):
    response = client.post(
        reverse("ai-framework-control-mapping-suggestion"),
        _request_payload(),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_step7a_returns_advisory_no_write_response(authenticated_client):
    before = _counts_snapshot()
    response = _post(authenticated_client)
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert sorted(body.keys()) == [
        "ambiguity_flags",
        "framework_control_mappings",
        "overall_confidence",
        "provider_mode",
        "warnings",
    ]
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["framework_control_mappings"]

    allowed_references = {control["reference"] for control in CANDIDATE_CONTROLS}
    for mapping in body["framework_control_mappings"]:
        assert mapping["review_status"] == "pending_review"
        assert mapping["mapping_type"] in {
            "supports_finding",
            "supports_applied_control",
            "supports_remediation",
            "compliance_gap_mapping",
            "evidence_mapping",
        }
        assert 0.0 <= mapping["confidence"] <= 1.0
        assert isinstance(mapping["evidence_needed"], list)
        assert mapping["framework_control_reference"] in allowed_references

    # No committed record identifiers or write/approval flags leak into the response.
    serialized = json.dumps(body)
    for forbidden in (
        "framework_control_id",
        "requirement_id",
        "mapping_id",
        "approved_by_user",
        "idempotency_key",
        "dry_run",
    ):
        assert forbidden not in serialized
    assert before == after


@pytest.mark.django_db
def test_configured_local_provider_path_uses_mocked_ollama(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)
    provider_draft = {"framework_control_mappings": [_valid_provider_mapping()]}
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
    response = _post(authenticated_client)
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert len(body["framework_control_mappings"]) == 1
    mapping = body["framework_control_mappings"][0]
    assert mapping["framework_control_reference"] == CANDIDATE_MFA["reference"]
    assert mapping["framework_control_code"] == CANDIDATE_MFA["code"]
    assert mapping["framework_control_title"] == CANDIDATE_MFA["title"]
    assert mapping["framework_name"] == "SAMA ECC-1:2018"
    assert mapping["mapping_type"] == "supports_finding"
    assert mapping["linked_finding_reference"] == "FND-CAND-001"
    assert mapping["linked_remediation_action_reference"] == "RMD-MFA-001"
    assert mapping["review_status"] == "pending_review"
    assert body["overall_confidence"] == 0.88
    assert calls
    assert calls[0]["url"].endswith("/api/generate")
    assert calls[0]["body"]["model"] == "qwen3:4b-instruct"
    # Only existing candidate controls are handed to the local model.
    assert before == after


@pytest.mark.django_db
def test_invalid_mapping_type_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"framework_control_mappings": [_valid_provider_mapping(mapping_type="satisfies")]},
    )

    before = _counts_snapshot()
    response = _post(authenticated_client)
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_framework_control_mapping_suggestion_guardrails_failed"
    assert any("mapping_type" in error for error in body["errors"])
    assert before == after


@pytest.mark.django_db
def test_invalid_confidence_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"framework_control_mappings": [_valid_provider_mapping(confidence=1.7)]},
    )

    response = _post(authenticated_client)

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_framework_control_mapping_suggestion_guardrails_failed"
    assert any("confidence" in error for error in body["errors"])


@pytest.mark.django_db
def test_missing_required_mapping_fields_are_guarded(authenticated_client, monkeypatch):
    incomplete_mapping = _valid_provider_mapping()
    del incomplete_mapping["rationale"]
    del incomplete_mapping["evidence_needed"]
    del incomplete_mapping["confidence"]
    _install_provider_returning(
        monkeypatch, {"framework_control_mappings": [incomplete_mapping]}
    )

    response = _post(authenticated_client)

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_framework_control_mapping_suggestion_guardrails_failed"
    errors = body["errors"]
    assert any("rationale is required" in error for error in errors)
    assert any("evidence_needed is required" in error for error in errors)
    assert any("confidence is required" in error for error in errors)


@pytest.mark.django_db
def test_framework_control_mappings_must_be_a_list(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"framework_control_mappings": {"temporary_id": "framework_mapping_1"}},
    )

    response = _post(authenticated_client)

    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "ai_framework_control_mapping_suggestion_guardrails_failed"
    assert "framework_control_mappings must be a list." in body["errors"]


@pytest.mark.django_db
def test_mapping_to_non_candidate_framework_control_is_rejected(
    authenticated_client, monkeypatch
):
    """A real-looking but unsupplied control reference must not be accepted."""
    _install_provider_returning(
        monkeypatch,
        {
            "framework_control_mappings": [
                _valid_provider_mapping(
                    framework_control_reference="urn:sanad:req-node:sama-ecc:9-9-9",
                    framework_control_code="ECC-9-9-9",
                    framework_control_title="Network Segmentation",
                    framework_control_description="Networks shall be segmented.",
                )
            ]
        },
    )

    before = _counts_snapshot()
    response = _post(authenticated_client)
    after = _counts_snapshot()

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any(
        "is not an existing candidate framework control" in error for error in errors
    )
    assert before == after


@pytest.mark.django_db
def test_invented_framework_control_reference_is_rejected(authenticated_client, monkeypatch):
    """An invented clause number with borrowed candidate text is still rejected."""
    _install_provider_returning(
        monkeypatch,
        {
            "framework_control_mappings": [
                _valid_provider_mapping(
                    framework_control_reference="SAMA-ECC-1-2018-4.2.7-INVENTED",
                    framework_control_code="ECC-4-2-7",
                    framework_control_title="Invented Strong Authentication Clause",
                )
            ]
        },
    )

    response = _post(authenticated_client)

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("SAMA-ECC-1-2018-4.2.7-INVENTED" in error for error in errors)


@pytest.mark.django_db
def test_invented_framework_clause_text_is_rejected(authenticated_client, monkeypatch):
    """A known candidate reference may not carry rewritten official clause text."""
    _install_provider_returning(
        monkeypatch,
        {
            "framework_control_mappings": [
                _valid_provider_mapping(
                    framework_control_title="Clause 2.3.3.2 - Mandatory MFA everywhere",
                    framework_control_description=(
                        "The organization must apply MFA to every system without exception."
                    ),
                )
            ]
        },
    )

    response = _post(authenticated_client)

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("may not invent framework clause text" in error for error in errors)


@pytest.mark.django_db
def test_non_pending_review_status_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"framework_control_mappings": [_valid_provider_mapping(review_status="approved")]},
    )

    response = _post(authenticated_client)

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("review_status must be 'pending_review'" in error for error in errors)


@pytest.mark.django_db
def test_non_list_evidence_needed_is_guarded(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        {"framework_control_mappings": [_valid_provider_mapping(evidence_needed="MFA policy")]},
    )

    response = _post(authenticated_client)

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("evidence_needed must be a list" in error for error in errors)


@pytest.mark.django_db
def test_write_intent_fields_are_rejected(authenticated_client):
    for forbidden_field in ("approved_by_user", "dry_run", "commit", "create_framework"):
        response = _post(authenticated_client, **{forbidden_field: True})
        assert response.status_code == 400, forbidden_field
        assert forbidden_field in response.json()


@pytest.mark.django_db
def test_missing_candidate_controls_returns_blocked_advisory_without_inventing(
    authenticated_client,
):
    before = _counts_snapshot()
    response = _post(
        authenticated_client,
        candidate_framework_controls=[],
        framework_name="Framework That Does Not Exist Here",
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "candidate_controls_missing_blocked"
    assert body["framework_control_mappings"] == []
    assert body["overall_confidence"] == 0.0
    assert any(
        warning["code"] == "no_candidate_framework_controls" for warning in body["warnings"]
    )
    assert before == after


@pytest.mark.django_db
def test_step7a_does_not_write_any_record(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch, {"framework_control_mappings": [_valid_provider_mapping()]}
    )

    before = _counts_snapshot()
    response = _post(authenticated_client)
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
    response = _post(authenticated_client)
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "local_provider_error_fallback"
    assert any(warning["code"] == "local_provider_error_fallback" for warning in body["warnings"])
    assert before == after


# ---- Read-only CSV export fallback ---------------------------------------------------

CSV_HEADER = [
    "Framework Name",
    "Framework URN",
    "Total Controls",
    "Assessable Controls",
    "Control Ref ID",
    "Control URN",
    "Control Name",
    "Control Description",
    "Is Assessable",
    "Parent Ref ID",
    "Typical Evidence",
]

SAMA_CSV_FRAMEWORK_NAME = "SAMA Cyber Security Fundamentals "
SAMA_CSV_FRAMEWORK_URN = "urn:intuitem:risk:framework:sama-csf-1.0"
SAMA_MFA_URN = "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.5-4.e"
SAMA_MFA_DESCRIPTION = (
    "e. multi-factor authentication for sensitive and critical systems and profiles;"
)
SAMA_IAM_URN = "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.5-1"
SAMA_IAM_DESCRIPTION = (
    "The identity and access management policy, including the responsibilities and "
    "accountabilities, should be defined, approved and implemented."
)


def _csv_row(**overrides):
    row = {
        "Framework Name": SAMA_CSV_FRAMEWORK_NAME,
        "Framework URN": SAMA_CSV_FRAMEWORK_URN,
        "Total Controls": "290",
        "Assessable Controls": "250",
        "Control Ref ID": "",
        "Control URN": "",
        "Control Name": "",
        "Control Description": "",
        "Is Assessable": "Yes",
        "Parent Ref ID": "",
        "Typical Evidence": "",
    }
    row.update(overrides)
    return row


def _write_frameworks_csv(tmp_path, rows):
    import csv as csv_module

    path = tmp_path / "all_frameworks_export.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv_module.DictWriter(handle, fieldnames=CSV_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _default_csv_rows():
    return [
        # Blank control name, identity/access clause text: the real SAMA export shape.
        _csv_row(
            **{
                "Control Ref ID": "3.3.5-1",
                "Control URN": SAMA_IAM_URN,
                "Control Description": SAMA_IAM_DESCRIPTION,
            }
        ),
        _csv_row(
            **{
                "Control Ref ID": "3.3.5-4.e",
                "Control URN": SAMA_MFA_URN,
                "Control Description": SAMA_MFA_DESCRIPTION,
                "Typical Evidence": "MFA configuration export",
            }
        ),
        # Named control that also matches a context term.
        _csv_row(
            **{
                "Control Ref ID": "3.3.5-9",
                "Control URN": "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.5-9",
                "Control Name": "Periodic user access review",
                "Control Description": "User access rights should be reviewed periodically.",
                "Parent Ref ID": "3.3.5",
            }
        ),
        # Assessable but irrelevant to the context terms.
        _csv_row(
            **{
                "Control Ref ID": "3.1.1-1",
                "Control URN": "urn:intuitem:risk:req_node:sama-csf-1.0:3.1.1-1",
                "Control Description": "A cyber security governance framework should be defined.",
            }
        ),
        # Not assessable: must never become a candidate.
        _csv_row(
            **{
                "Control Ref ID": "3.3.5",
                "Control URN": "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.5",
                "Control Name": "Identity and Access Management",
                "Is Assessable": "No",
            }
        ),
        # Another framework: filtered out when the request names SAMA.
        _csv_row(
            **{
                "Framework Name": "ISO/IEC 27001:2022",
                "Framework URN": "urn:intuitem:risk:framework:iso27001-2022",
                "Control Ref ID": "A.5.15",
                "Control URN": "urn:intuitem:risk:req_node:iso27001-2022:A.5.15",
                "Control Name": "Access control",
                "Control Description": "Rules to control physical and logical access shall be established.",
            }
        ),
    ]


def _install_csv_export(monkeypatch, path):
    monkeypatch.setattr(
        "ai_onboarding.framework_control_mapping_suggestion_service._locate_frameworks_csv",
        lambda base_dir: path,
    )


def _csv_provider_mapping(**overrides):
    """A mapping to a blank-name CSV row: the model can only propose a working label."""
    mapping = _valid_provider_mapping(
        framework_control_reference=SAMA_MFA_URN,
        framework_control_code="3.3.5-4.e",
        framework_control_title="Multi-factor authentication for sensitive systems",
        framework_control_description="",
        framework_name="SAMA Cyber Security Fundamentals",
    )
    mapping.update(overrides)
    return mapping


@pytest.mark.django_db
def test_csv_fallback_supplies_candidates_and_calls_provider(
    authenticated_client, monkeypatch, tmp_path
):
    _install_csv_export(monkeypatch, _write_frameworks_csv(tmp_path, _default_csv_rows()))
    _install_provider_returning(
        monkeypatch, {"framework_control_mappings": [_csv_provider_mapping()]}
    )

    response = _post(authenticated_client, candidate_framework_controls=[])

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "configured_local_provider"
    assert any(
        warning["code"] == "framework_controls_loaded_from_csv_export"
        for warning in body["warnings"]
    )
    assert len(body["framework_control_mappings"]) == 1
    mapping = body["framework_control_mappings"][0]
    assert mapping["framework_control_reference"] == SAMA_MFA_URN
    assert mapping["framework_control_code"] == "3.3.5-4.e"
    assert mapping["framework_name"] == "SAMA Cyber Security Fundamentals"
    assert mapping["review_status"] == "pending_review"


@pytest.mark.django_db
def test_blank_csv_control_name_gets_safe_title_and_backfilled_description(
    authenticated_client, monkeypatch, tmp_path
):
    _install_csv_export(monkeypatch, _write_frameworks_csv(tmp_path, _default_csv_rows()))
    _install_provider_returning(
        monkeypatch, {"framework_control_mappings": [_csv_provider_mapping()]}
    )

    response = _post(authenticated_client, candidate_framework_controls=[])

    assert response.status_code == 200
    mapping = response.json()["framework_control_mappings"][0]
    # The model's working label is replaced by the safe generated candidate title, and the
    # authoritative clause text is restored from the CSV row.
    assert mapping["framework_control_title"] == "SAMA control 3.3.5-4.e"
    assert mapping["framework_control_description"] == SAMA_MFA_DESCRIPTION


@pytest.mark.django_db
def test_csv_fallback_does_not_write_any_record(authenticated_client, monkeypatch, tmp_path):
    _install_csv_export(monkeypatch, _write_frameworks_csv(tmp_path, _default_csv_rows()))
    _install_provider_returning(
        monkeypatch, {"framework_control_mappings": [_csv_provider_mapping()]}
    )

    before = _counts_snapshot()
    response = _post(authenticated_client, candidate_framework_controls=[])
    after = _counts_snapshot()

    assert response.status_code == 200
    assert before == after


@pytest.mark.django_db
def test_mapping_to_control_absent_from_csv_is_rejected(
    authenticated_client, monkeypatch, tmp_path
):
    _install_csv_export(monkeypatch, _write_frameworks_csv(tmp_path, _default_csv_rows()))
    _install_provider_returning(
        monkeypatch,
        {
            "framework_control_mappings": [
                _csv_provider_mapping(
                    framework_control_reference="urn:intuitem:risk:req_node:sama-csf-1.0:9.9.9-1",
                    framework_control_code="9.9.9-1",
                )
            ]
        },
    )

    before = _counts_snapshot()
    response = _post(authenticated_client, candidate_framework_controls=[])
    after = _counts_snapshot()

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("is not an existing candidate framework control" in error for error in errors)
    assert before == after


@pytest.mark.django_db
def test_invented_clause_text_on_csv_candidate_is_rejected(
    authenticated_client, monkeypatch, tmp_path
):
    _install_csv_export(monkeypatch, _write_frameworks_csv(tmp_path, _default_csv_rows()))
    _install_provider_returning(
        monkeypatch,
        {
            "framework_control_mappings": [
                _csv_provider_mapping(
                    framework_control_description=(
                        "MFA must be enforced on every system in the organization without exception."
                    )
                )
            ]
        },
    )

    response = _post(authenticated_client, candidate_framework_controls=[])

    assert response.status_code == 422
    errors = response.json()["errors"]
    assert any("may not invent framework clause text" in error for error in errors)


@pytest.mark.django_db
def test_missing_csv_export_keeps_blocked_advisory(authenticated_client, monkeypatch):
    monkeypatch.setattr(
        "ai_onboarding.framework_control_mapping_suggestion_service._locate_frameworks_csv",
        lambda base_dir: None,
    )

    before = _counts_snapshot()
    response = _post(authenticated_client, candidate_framework_controls=[])
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "candidate_controls_missing_blocked"
    assert body["framework_control_mappings"] == []
    assert before == after


def test_csv_loader_filters_sama_rows_and_relevant_controls(tmp_path):
    """Assessable + framework + context-term filtering, without touching the database."""
    from ai_onboarding.framework_control_mapping_suggestion_service import (
        _load_csv_candidate_controls,
        _locate_frameworks_csv,
    )

    _write_frameworks_csv(tmp_path, _default_csv_rows())
    assert _locate_frameworks_csv(str(tmp_path)) is not None

    candidates = _load_csv_candidate_controls(str(tmp_path), ["sama ecc-1:2018"])

    assert candidates
    assert len(candidates) <= 50
    references = {candidate["reference"] for candidate in candidates}
    # Loose SAMA match keeps the SAMA rows and drops the other framework.
    assert SAMA_IAM_URN in references
    assert SAMA_MFA_URN in references
    assert not any("iso27001" in reference for reference in references)
    # Non-assessable and context-irrelevant rows are excluded.
    assert not any(reference.endswith(":3.3.5") for reference in references)
    assert not any(reference.endswith(":3.1.1-1") for reference in references)

    by_reference = {candidate["reference"]: candidate for candidate in candidates}
    assert by_reference[SAMA_IAM_URN]["title"] == "SAMA control 3.3.5-1"
    assert by_reference[SAMA_IAM_URN]["title_is_generated"] is True
    assert by_reference[SAMA_IAM_URN]["description"] == SAMA_IAM_DESCRIPTION
    assert by_reference[SAMA_IAM_URN]["framework_name"] == "SAMA Cyber Security Fundamentals"
    assert by_reference[SAMA_IAM_URN]["source"] == "all_frameworks_export.csv"
    assert by_reference[SAMA_MFA_URN]["typical_evidence"] == "MFA configuration export"


def test_csv_loader_falls_back_to_head_slice_when_no_context_match(tmp_path):
    from ai_onboarding.framework_control_mapping_suggestion_service import (
        _load_csv_candidate_controls,
    )

    rows = [
        _csv_row(
            **{
                "Control Ref ID": "3.1.1-1",
                "Control URN": "urn:intuitem:risk:req_node:sama-csf-1.0:3.1.1-1",
                "Control Description": "A cyber security governance framework should be defined.",
            }
        )
    ]
    _write_frameworks_csv(tmp_path, rows)

    candidates = _load_csv_candidate_controls(str(tmp_path), ["sama"])

    assert len(candidates) == 1
    assert candidates[0]["code"] == "3.1.1-1"


# ---- Provider payload / mapping-count optimisation -----------------------------------


def _numbered_csv_rows(count, *, prefix="3.3.9", description="User access control clause."):
    return [
        _csv_row(
            **{
                "Control Ref ID": f"{prefix}-{index}",
                "Control URN": f"urn:intuitem:risk:req_node:sama-csf-1.0:{prefix}-{index}",
                "Control Description": description,
            }
        )
        for index in range(1, count + 1)
    ]


def test_csv_candidates_are_capped_at_twelve_and_prioritised(tmp_path):
    from ai_onboarding.framework_control_mapping_suggestion_service import (
        MAX_CSV_CANDIDATES,
        _load_csv_candidate_controls,
    )

    # Twenty generic access-control rows first, then the strong remote-access/MFA rows so
    # only ranking (not export order) can bring them into the candidate set.
    rows = [
        *_numbered_csv_rows(20),
        _csv_row(
            **{
                "Control Ref ID": "3.3.5-4.f",
                "Control URN": "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.5-4.f",
                "Control Description": (
                    "f. privileged and remote access management, which should address: "
                    "multi-factor authentication should be used for all remote access."
                ),
            }
        ),
        _csv_row(
            **{
                "Control Ref ID": "3.3.5-4.e",
                "Control URN": SAMA_MFA_URN,
                "Control Description": SAMA_MFA_DESCRIPTION,
            }
        ),
        _csv_row(
            **{
                "Control Ref ID": "3.3.5-1",
                "Control URN": SAMA_IAM_URN,
                "Control Description": SAMA_IAM_DESCRIPTION,
            }
        ),
    ]
    _write_frameworks_csv(tmp_path, rows)

    candidates = _load_csv_candidate_controls(str(tmp_path), ["sama"])

    assert MAX_CSV_CANDIDATES == 12
    assert len(candidates) == 12
    codes = [candidate["code"] for candidate in candidates]
    # Strongest exact matches lead, ahead of the generic access-control rows.
    assert codes[0] == "3.3.5-4.f"
    assert codes[1] == "3.3.5-4.e"
    assert codes[2] == "3.3.5-1"


@pytest.mark.django_db
def test_provider_payload_is_trimmed_and_full_clause_text_is_restored(
    authenticated_client, monkeypatch, tmp_path
):
    from ai_onboarding.framework_control_mapping_suggestion_service import (
        MAX_PROVIDER_DESCRIPTION_CHARS,
    )

    long_description = (
        "f. privileged and remote access management, which should address: "
        + "multi-factor authentication should be used for all remote access. " * 40
    ).strip()
    _write_frameworks_csv(
        tmp_path,
        [
            _csv_row(
                **{
                    "Control Ref ID": "3.3.5-4.f",
                    "Control URN": "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.5-4.f",
                    "Control Description": long_description,
                }
            )
        ],
    )
    _install_csv_export(monkeypatch, tmp_path / "all_frameworks_export.csv")
    _configure_local_provider_env(monkeypatch)

    prompts = []

    def _handler(request, timeout, body):
        prompts.append(body.get("prompt") or "")
        return {
            "model": body["model"],
            "response": json.dumps(
                {
                    "framework_control_mappings": [
                        _csv_provider_mapping(
                            framework_control_reference=(
                                "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.5-4.f"
                            ),
                            framework_control_code="3.3.5-4.f",
                            # The model can only echo the shortened copy it was given.
                            framework_control_description=long_description[
                                :MAX_PROVIDER_DESCRIPTION_CHARS
                            ],
                        )
                    ]
                }
            ),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    response = _post(authenticated_client, candidate_framework_controls=[])

    assert response.status_code == 200
    assert prompts
    # The full clause never reaches the model.
    assert long_description not in prompts[0]
    assert long_description[:200] in prompts[0]
    # The response still carries the complete authoritative clause text.
    mapping = response.json()["framework_control_mappings"][0]
    assert mapping["framework_control_description"] == long_description


@pytest.mark.django_db
def test_duplicate_mappings_for_the_same_control_are_deduplicated(
    authenticated_client, monkeypatch, tmp_path
):
    _install_csv_export(monkeypatch, _write_frameworks_csv(tmp_path, _default_csv_rows()))
    _install_provider_returning(
        monkeypatch,
        {
            "framework_control_mappings": [
                _csv_provider_mapping(temporary_id="framework_mapping_1", confidence=0.6),
                # Exact repeat of the same control, type, and linked finding: noise.
                _csv_provider_mapping(temporary_id="framework_mapping_2", confidence=0.9),
                # Same control and linked finding but a clearly different mapping type.
                _csv_provider_mapping(
                    temporary_id="framework_mapping_3",
                    mapping_type="supports_remediation",
                    confidence=0.7,
                ),
            ]
        },
    )

    response = _post(authenticated_client, candidate_framework_controls=[])

    assert response.status_code == 200
    mappings = response.json()["framework_control_mappings"]
    assert len(mappings) == 2
    by_type = {mapping["mapping_type"]: mapping for mapping in mappings}
    assert set(by_type) == {"supports_finding", "supports_remediation"}
    # The stronger of the two duplicates is the one kept.
    assert by_type["supports_finding"]["confidence"] == 0.9


@pytest.mark.django_db
def test_mappings_are_capped_at_five_with_a_warning(
    authenticated_client, monkeypatch, tmp_path
):
    from ai_onboarding.framework_control_mapping_suggestion_service import MAX_MAPPINGS

    rows = _numbered_csv_rows(7)
    _install_csv_export(monkeypatch, _write_frameworks_csv(tmp_path, rows))
    _install_provider_returning(
        monkeypatch,
        {
            "framework_control_mappings": [
                _csv_provider_mapping(
                    temporary_id=f"framework_mapping_{index}",
                    framework_control_reference=(
                        f"urn:intuitem:risk:req_node:sama-csf-1.0:3.3.9-{index}"
                    ),
                    framework_control_code=f"3.3.9-{index}",
                )
                for index in range(1, 8)
            ]
        },
    )

    response = _post(authenticated_client, candidate_framework_controls=[])

    assert response.status_code == 200
    body = response.json()
    assert MAX_MAPPINGS == 5
    assert len(body["framework_control_mappings"]) == 5
    assert any(
        warning["code"] == "framework_control_mappings_trimmed" for warning in body["warnings"]
    )


def test_csv_loader_reads_the_repository_export_read_only():
    """The real repository export is readable and yields SAMA identity/access controls."""
    from pathlib import Path

    from ai_onboarding.framework_control_mapping_suggestion_service import (
        CSV_CONTEXT_TERMS,
        _load_csv_candidate_controls,
        _locate_frameworks_csv,
    )

    repository_root = str(Path(__file__).resolve().parents[3])
    if _locate_frameworks_csv(repository_root) is None:
        pytest.skip("all_frameworks_export.csv is not present in this checkout")

    candidates = _load_csv_candidate_controls(repository_root, ["sama ecc-1:2018"])

    assert candidates
    assert len(candidates) <= 50
    for candidate in candidates:
        assert "sama" in candidate["framework_name"].lower()
        assert candidate["title"]
        assert candidate["reference"]
        haystack = f"{candidate['title']} {candidate['description']}".lower()
        assert any(term in haystack for term in CSV_CONTEXT_TERMS)


@pytest.mark.django_db
def test_read_only_discovery_uses_existing_framework_requirements(authenticated_client):
    """With no supplied candidates, Step 7A may read existing framework controls only."""
    framework = Framework.objects.create(
        name="SAMA ECC-1:2018 Test Framework",
        folder=Folder.get_root_folder(),
        urn=f"urn:test:framework:{uuid.uuid4().hex}",
    )
    RequirementNode.objects.create(
        framework=framework,
        folder=Folder.get_root_folder(),
        urn=f"urn:test:req-node:{uuid.uuid4().hex}",
        ref_id="ECC-2-3-3-2",
        name="Multi-Factor Authentication for Remote Access",
        description="Multi-factor authentication shall be applied for remote access.",
        assessable=True,
        order_id=1,
    )

    before = _counts_snapshot()
    response = _post(
        authenticated_client,
        candidate_framework_controls=[],
        framework_name=None,
        framework_reference={"framework_id": str(framework.id)},
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["framework_control_mappings"]
    for mapping in body["framework_control_mappings"]:
        assert mapping["framework_control_code"] == "ECC-2-3-3-2"
        assert mapping["framework_name"] == "SAMA ECC-1:2018 Test Framework"
        assert mapping["review_status"] == "pending_review"
    assert before == after
