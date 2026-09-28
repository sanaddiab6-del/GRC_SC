import json
import uuid

import pytest
from django.contrib.auth.models import Permission
from django.conf import settings as django_settings
from django.urls import reverse
from knox.models import AuthToken

from core import startup as core_startup
from core.models import (
    AppliedControl,
    ComplianceAssessment,
    Evidence,
    EvidenceRevision,
    Finding,
    FindingsAssessment,
    Framework,
    RequirementAssessment,
    RequirementNode,
)
from iam.models import Folder, Role, RoleAssignment, User, UserGroup


_ORIGINAL_STARTUP_CALL_COMMAND = core_startup.call_command


def _patched_startup_call_command(name, *args, **kwargs):
    # Skip loading the full framework/library catalogue for this file: it is not exercised
    # by these tests and loading it for every test module is the dominant cost of the suite.
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
        / f"test_ai_evidence_freshness_review_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_EVIDENCE_FRESHNESS_REVIEW", raising=False)
    monkeypatch.delenv("LOCAL_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("LOCAL_AI_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("LOCAL_AI_TEMPERATURE", raising=False)


@pytest.fixture
def client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def admin_user(app_config):
    admin = User.objects.create_superuser(
        f"admin-{uuid.uuid4().hex[:8]}@tests.com", is_published=True
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


def _make_domain_folder(name: str) -> Folder:
    return Folder.objects.create(
        name=name,
        content_type=Folder.ContentType.DOMAIN,
        builtin=False,
        parent_folder=Folder.objects.get(content_type=Folder.ContentType.ROOT),
    )


def _make_scoped_client(*, folder: Folder) -> "tuple[object, User]":
    """A second, non-admin user who can only view evidence (and its containing folder) in
    `folder` — the minimum permission set the RBAC queryset scoping actually requires."""
    from rest_framework.test import APIClient

    user = User.objects.create_user(
        f"scoped-{uuid.uuid4().hex[:8]}@tests.com", is_published=True
    )
    role = Role.objects.create(name=f"evidence-viewer-{uuid.uuid4().hex[:8]}")
    # get_accessible_object_ids() (used by BaseModelViewSet.get_queryset()) only considers an
    # assignment's folder permissions at all once the role can also view_folder; without it,
    # the object is excluded from the queryset before any object-level permission is checked.
    role.permissions.set(
        Permission.objects.filter(codename__in=["view_evidence", "view_folder"])
    )
    role.save()
    role_assignment = RoleAssignment.objects.create(
        user=user, role=role, folder=folder, is_recursive=True
    )
    role_assignment.perimeter_folders.add(folder)
    role_assignment.save()

    client = APIClient()
    auth_token = AuthToken.objects.create(user=user)[1]
    client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token}")
    return client, user


def _make_requirement_assessment(*, folder: Folder) -> RequirementAssessment:
    """A minimal but real ComplianceAssessment/RequirementAssessment pair, so the
    linked_requirement_assessments branch of build_evidence_context (compliance_assessment,
    framework, requirement traversal) is actually exercised, not just the applied_controls one."""
    framework = Framework.objects.create(name="Test Framework", folder=folder)
    requirement = RequirementNode.objects.create(
        name="MFA for remote access", framework=framework, folder=folder, assessable=True
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        name="Q4 2026 Test Compliance Assessment", framework=framework, folder=folder
    )
    return RequirementAssessment.objects.create(
        compliance_assessment=compliance_assessment,
        requirement=requirement,
        folder=folder,
        result=RequirementAssessment.Result.PARTIALLY_COMPLIANT,
        status=RequirementAssessment.Status.IN_PROGRESS,
    )


def _make_evidence_with_context(*, folder: Folder, with_requirement: bool = True, **overrides) -> Evidence:
    """A realistic evidence item: a control, a requirement assessment, and a revision."""
    control = AppliedControl.objects.create(name="MFA for remote access", folder=folder)
    evidence = Evidence.objects.create(
        name=overrides.pop("name", "MFA configuration export"),
        description=overrides.pop(
            "description", "Screenshot of the MFA policy in the identity provider."
        ),
        folder=folder,
        **overrides,
    )
    evidence.applied_controls.add(control)
    if with_requirement:
        requirement_assessment = _make_requirement_assessment(folder=folder)
        evidence.requirement_assessments.add(requirement_assessment)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")
    return evidence


def _install_mock_ollama_urlopen(monkeypatch, handler):
    class _MockHttpResponse:
        def __init__(self, payload):
            self._payload = json.dumps(payload).encode("utf-8")

        def read(self):
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def _mock_urlopen(request, timeout=0):
        request_body = json.loads(request.data.decode("utf-8"))
        response_payload = handler(request, timeout, request_body)
        return _MockHttpResponse(response_payload)

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _configure_local_provider_env(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "local")
    monkeypatch.setenv("LOCAL_AI_API_STYLE", "ollama")
    monkeypatch.setenv("LOCAL_AI_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("LOCAL_AI_MODEL_DEFAULT", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_MODEL_EVIDENCE_FRESHNESS_REVIEW", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_provider_returning(monkeypatch, judgement: dict):
    _configure_local_provider_env(monkeypatch)

    def _handler(request, timeout, body):
        return {"model": body["model"], "response": json.dumps(judgement), "done": True}

    _install_mock_ollama_urlopen(monkeypatch, _handler)


def _install_provider_raising(monkeypatch, exc: Exception):
    _configure_local_provider_env(monkeypatch)

    def _mock_urlopen(request, timeout=0):
        raise exc

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _valid_judgement(**overrides):
    judgement = {
        "freshness_status": "REVIEW_RECOMMENDED",
        "confidence": 0.7,
        "explanation": "No revision has been added since the control it supports changed.",
        "concerns": ["Latest revision predates the linked control's last update."],
        "recommended_action": "Ask the evidence owner to confirm this screenshot is current.",
    }
    judgement.update(overrides)
    return judgement


def _freshness_url(evidence_id) -> str:
    return reverse("evidences-ai-freshness-review", args=[evidence_id])


def _batch_url() -> str:
    return reverse("evidences-ai-freshness-review-batch")


def _counts_snapshot():
    return {
        "Evidence": Evidence.objects.count(),
        "EvidenceRevision": EvidenceRevision.objects.count(),
        "AppliedControl": AppliedControl.objects.count(),
        "RequirementAssessment": RequirementAssessment.objects.count(),
        "ComplianceAssessment": ComplianceAssessment.objects.count(),
        "Finding": Finding.objects.count(),
        "FindingsAssessment": FindingsAssessment.objects.count(),
    }


def _field_snapshot(evidence: Evidence, requirement_assessment: RequirementAssessment):
    """Field-level snapshot (not just row counts) of every business object the freshness
    review reads, so a mutation that changes a field without changing a row count (e.g. a
    result or status flip) would also be caught."""
    return {
        "evidence_status": evidence.status,
        "evidence_updated_at": evidence.updated_at,
        "evidence_expiry_date": evidence.expiry_date,
        "requirement_assessment_result": requirement_assessment.result,
        "requirement_assessment_status": requirement_assessment.status,
        "requirement_assessment_observation": requirement_assessment.observation,
    }


# ---------------------------------------------------------------------------
# 1. Authentication / authorization / tenant isolation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_anonymous_request_is_rejected(client):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    response = client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthorized_cross_folder_access_is_rejected(monkeypatch):
    """A user scoped to folder B must not be able to review evidence that lives in folder A,
    and the response must not distinguish "exists but forbidden" from "does not exist"."""
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("other-tenant")
    evidence = _make_evidence_with_context(folder=folder_a)

    scoped_client, _user = _make_scoped_client(folder=folder_b)

    response = scoped_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 404
    # Same response shape as a genuinely unknown id: no enumeration oracle.
    unknown_response = scoped_client.post(
        _freshness_url(uuid.uuid4()), {}, format="json"
    )
    assert unknown_response.status_code == 404


@pytest.mark.django_db
def test_authorized_user_in_same_folder_can_review(monkeypatch):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    scoped_client, _user = _make_scoped_client(folder=folder)
    _install_provider_returning(monkeypatch, _valid_judgement())

    response = scoped_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200


@pytest.mark.django_db
def test_evidence_not_found_returns_404(authenticated_client):
    response = authenticated_client.post(_freshness_url(uuid.uuid4()), {}, format="json")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 2. Successful review + each freshness status
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_authenticated_successful_review_shape(authenticated_client, monkeypatch):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    _install_provider_returning(monkeypatch, _valid_judgement())

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["evidence_id"] == str(evidence.id)
    assert body["evidence_name"] == evidence.name
    assert body["freshness_status"] == "REVIEW_RECOMMENDED"
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["explanation"]
    assert isinstance(body["concerns"], list)
    assert body["recommended_action"]
    assert body["provider_mode"] == "configured_local_provider"
    assert body["linked_applied_controls_count"] == 1
    assert body["linked_requirement_assessments_count"] == 1
    assert body["linked_findings_count"] == 0
    assert "reviewed_at" in body
    assert "never" in body["advisory_notice"].lower() or "advisory" in body[
        "advisory_notice"
    ].lower()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status", ["CURRENT", "REVIEW_RECOMMENDED", "POSSIBLY_OUTDATED", "INSUFFICIENT_CONTEXT"]
)
def test_each_freshness_status_round_trips(authenticated_client, monkeypatch, status):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    _install_provider_returning(
        monkeypatch, _valid_judgement(freshness_status=status, confidence=0.4)
    )

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    assert response.json()["freshness_status"] == status


@pytest.mark.django_db
def test_evidence_without_enough_context_returns_insufficient_context(authenticated_client):
    """No revision, no link, no linked control/requirement/finding: nothing to judge.
    The provider is never even called."""
    folder = _make_domain_folder("acme")
    evidence = Evidence.objects.create(name="Placeholder evidence", folder=folder)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["freshness_status"] == "INSUFFICIENT_CONTEXT"
    assert body["confidence"] == 0.0


@pytest.mark.django_db
def test_multiple_revisions_are_summarized_and_latest_is_used(authenticated_client, monkeypatch):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    EvidenceRevision.objects.create(evidence=evidence, version=2, observation="Refreshed.")
    EvidenceRevision.objects.create(evidence=evidence, version=3, observation="Latest.")
    _install_provider_returning(monkeypatch, _valid_judgement(freshness_status="CURRENT"))

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    assert response.json()["revision_count"] == 3


# ---------------------------------------------------------------------------
# 3. Failure handling: provider unavailable / timeout / malformed output
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ai_provider_not_configured_returns_insufficient_context(authenticated_client):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["freshness_status"] == "INSUFFICIENT_CONTEXT"
    assert body["provider_mode"] == "provider_not_configured_fallback"
    assert body["warnings"]


@pytest.mark.django_db
def test_ai_provider_unavailable_fails_safely(authenticated_client, monkeypatch):
    import urllib.error

    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    _install_provider_raising(monkeypatch, urllib.error.URLError("connection refused"))

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["freshness_status"] == "INSUFFICIENT_CONTEXT"
    assert body["provider_mode"] == "local_provider_error_fallback"


@pytest.mark.django_db
def test_ai_provider_timeout_fails_safely(authenticated_client, monkeypatch):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    _install_provider_raising(monkeypatch, TimeoutError("timed out"))

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["freshness_status"] == "INSUFFICIENT_CONTEXT"
    assert body["provider_mode"] == "local_provider_error_fallback"


@pytest.mark.django_db
def test_malformed_ai_json_is_rejected(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)

    def _handler(request, timeout, body):
        return {"model": body["model"], "response": "not json at all {{{", "done": True}

    _install_mock_ollama_urlopen(monkeypatch, _handler)
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    before = _counts_snapshot()

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    # Unparseable output from a *configured* provider is treated with the same suspicion as
    # write-implying output (never silently swapped for a fallback verdict): it is rejected
    # outright rather than guessed at, matching this app's existing
    # local_ai_provider_invalid_output handling (see control_effectiveness_suggestion).
    assert response.status_code == 422
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_response_missing_required_fields_is_rejected(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, {"freshness_status": "CURRENT"})

    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    before = _counts_snapshot()

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_prose_instead_of_json_is_rejected(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)

    def _handler(request, timeout, body):
        return {
            "model": body["model"],
            "response": "This evidence looks current to me, no concerns here.",
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    before = _counts_snapshot()

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_empty_ai_response_is_rejected_safely(authenticated_client, monkeypatch):
    _configure_local_provider_env(monkeypatch)

    def _handler(request, timeout, body):
        return {"model": body["model"], "response": "", "done": True}

    _install_mock_ollama_urlopen(monkeypatch, _handler)
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    before = _counts_snapshot()

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_excessively_long_explanation_is_rejected(authenticated_client, monkeypatch):
    """The system prompt asks for a short explanation, but that is only a request: the
    schema itself must bound the length so an uncooperative model cannot store or render an
    unbounded wall of text."""
    _install_provider_returning(
        monkeypatch, _valid_judgement(explanation="x" * 5000)
    )
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    before = _counts_snapshot()

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_harmless_unexpected_field_is_still_rejected(authenticated_client, monkeypatch):
    """The output schema is strict, not just guardrailed: even a field that implies nothing
    dangerous is rejected if it is not part of the declared contract, matching this app's
    existing StrictSerializer convention for every other AI capability."""
    _install_provider_returning(
        monkeypatch, _valid_judgement(unexpected_debug_field="hello")
    )
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422


@pytest.mark.django_db
def test_ai_provider_http_error_fails_safely(authenticated_client, monkeypatch):
    """A model/provider-level refusal (e.g. Ollama returning an HTTP error because the
    configured model is not pulled) must degrade to the same safe fallback as any other
    transient provider failure, not crash or fabricate a verdict."""
    import urllib.error

    http_error = urllib.error.HTTPError(
        url="http://127.0.0.1:11434/api/generate",
        code=404,
        msg="model not found",
        hdrs=None,
        fp=None,
    )
    _install_provider_raising(monkeypatch, http_error)
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["freshness_status"] == "INSUFFICIENT_CONTEXT"
    assert body["provider_mode"] == "local_provider_error_fallback"


# ---------------------------------------------------------------------------
# 4. Guardrails: malicious / write-implying AI output
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_write_implying_ai_output_is_hard_rejected(authenticated_client, monkeypatch):
    """A model attempting to smuggle a write/approval flag must fail loudly (422), never be
    silently swapped for a fallback: this is the one failure mode that must NOT degrade
    quietly, because doing so could hide an attempted unsafe action."""
    malicious = _valid_judgement()
    malicious["approve_requirement"] = True
    malicious["mark_compliant"] = True
    _install_provider_returning(monkeypatch, malicious)

    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    before = _counts_snapshot()

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_out_of_scope_final_decision_language_is_hard_rejected(authenticated_client, monkeypatch):
    _install_provider_returning(
        monkeypatch,
        _valid_judgement(explanation="This requirement approved and marked compliant now."),
    )
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422


@pytest.mark.django_db
def test_invalid_freshness_status_enum_is_rejected(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_judgement(freshness_status="DEFINITELY_FINE"))
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422


@pytest.mark.django_db
def test_out_of_range_confidence_is_rejected(authenticated_client, monkeypatch):
    _install_provider_returning(monkeypatch, _valid_judgement(confidence=1.7))
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 422


@pytest.mark.django_db
def test_request_body_cannot_carry_write_intent_fields(authenticated_client):
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)

    for field in ("approve", "commit", "delete_evidence", "mark_compliant"):
        response = authenticated_client.post(
            _freshness_url(evidence.id), {field: True}, format="json"
        )
        assert response.status_code == 400, field


# ---------------------------------------------------------------------------
# 5. No database mutation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_review_never_writes_grc_data(authenticated_client, monkeypatch):
    """Row-count AND field-level proof, across every business object type the service reads
    (Evidence, EvidenceRevision, AppliedControl, RequirementAssessment, ComplianceAssessment):
    an advisory call must leave all of them byte-for-byte unchanged."""
    folder = _make_domain_folder("acme")
    evidence = _make_evidence_with_context(folder=folder)
    requirement_assessment = evidence.requirement_assessments.get()
    _install_provider_returning(monkeypatch, _valid_judgement(freshness_status="POSSIBLY_OUTDATED"))
    before_counts = _counts_snapshot()
    before_fields = _field_snapshot(evidence, requirement_assessment)

    response = authenticated_client.post(_freshness_url(evidence.id), {}, format="json")

    assert response.status_code == 200
    assert response.json()["freshness_status"] == "POSSIBLY_OUTDATED"
    assert _counts_snapshot() == before_counts
    evidence.refresh_from_db()
    requirement_assessment.refresh_from_db()
    assert _field_snapshot(evidence, requirement_assessment) == before_fields


# ---------------------------------------------------------------------------
# 6. Tenant data is not leaked into the prompt
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_other_tenants_evidence_is_not_sent_to_the_model(authenticated_client, monkeypatch):
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("other-tenant")
    evidence_a = _make_evidence_with_context(folder=folder_a, name="Acme MFA export")
    _make_evidence_with_context(folder=folder_b, name="OtherTenant secret payroll evidence")

    _configure_local_provider_env(monkeypatch)
    captured_bodies = []

    def _handler(request, timeout, body):
        captured_bodies.append(body)
        return {
            "model": body["model"],
            "response": json.dumps(_valid_judgement()),
            "done": True,
        }

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    response = authenticated_client.post(_freshness_url(evidence_a.id), {}, format="json")

    assert response.status_code == 200
    assert len(captured_bodies) == 1
    prompt_text = captured_bodies[0]["prompt"]
    assert "Acme MFA export" in prompt_text
    assert "OtherTenant" not in prompt_text
    assert "payroll" not in prompt_text.lower()


# ---------------------------------------------------------------------------
# 6b. A LINKED object the caller cannot view must not enter the prompt, even though the
# Evidence that links it is fully accessible. Every case is proven by capturing the actual
# provider input (the prompt string sent to the model), not by inspecting the HTTP response.
# ---------------------------------------------------------------------------


def _make_control_in_folder(*, folder: Folder, name: str) -> AppliedControl:
    return AppliedControl.objects.create(name=name, folder=folder)


def _make_requirement_assessment_in_folder(*, folder: Folder, name: str) -> RequirementAssessment:
    framework = Framework.objects.create(name=f"{name} framework", folder=folder)
    requirement = RequirementNode.objects.create(
        name=name, framework=framework, folder=folder, assessable=True
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        name=f"{name} assessment", framework=framework, folder=folder
    )
    return RequirementAssessment.objects.create(
        compliance_assessment=compliance_assessment,
        requirement=requirement,
        folder=folder,
        result=RequirementAssessment.Result.PARTIALLY_COMPLIANT,
        status=RequirementAssessment.Status.IN_PROGRESS,
    )


def _capture_prompt(monkeypatch, client, evidence_id) -> tuple[object, str]:
    """POSTs the freshness review and returns (response, prompt_text) for the one call made."""
    _configure_local_provider_env(monkeypatch)
    captured_bodies: list = []

    def _handler(request, timeout, body):
        captured_bodies.append(body)
        return {"model": body["model"], "response": json.dumps(_valid_judgement()), "done": True}

    _install_mock_ollama_urlopen(monkeypatch, _handler)
    response = client.post(_freshness_url(evidence_id), {}, format="json")
    assert len(captured_bodies) == 1, "expected exactly one provider call"
    return response, captured_bodies[0]["prompt"]


@pytest.mark.django_db
def test_linked_control_in_an_inaccessible_folder_is_excluded_from_the_prompt(monkeypatch):
    """Test A: Evidence is fully viewable, but it links a control that lives in a folder the
    caller has no permission on at all. That control's name must never reach the model."""
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("vault")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)
    hidden_control = _make_control_in_folder(
        folder=folder_b, name="INACCESSIBLE_CONTROL_SECRET_MARKER"
    )
    evidence.applied_controls.add(hidden_control)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")

    scoped_client, _user = _make_scoped_client(folder=folder_a)
    response, prompt = _capture_prompt(monkeypatch, scoped_client, evidence.id)

    assert response.status_code == 200
    assert "INACCESSIBLE_CONTROL_SECRET_MARKER" not in prompt


@pytest.mark.django_db
def test_linked_control_in_an_accessible_folder_is_included_in_the_prompt(monkeypatch):
    """Test B (positive control): the same setup, but the caller can also view the control's
    folder. This proves the fix filters by visibility, not by simply dropping every link."""
    folder_a = _make_domain_folder("acme")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)
    visible_control = _make_control_in_folder(
        folder=folder_a, name="ACCESSIBLE_CONTROL_MARKER"
    )
    evidence.applied_controls.add(visible_control)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")

    scoped_client, user = _make_scoped_client(folder=folder_a)
    role = Role.objects.get(roleassignment__user=user)
    role.permissions.add(Permission.objects.get(codename="view_appliedcontrol"))

    response, prompt = _capture_prompt(monkeypatch, scoped_client, evidence.id)

    assert response.status_code == 200
    assert "ACCESSIBLE_CONTROL_MARKER" in prompt


@pytest.mark.django_db
def test_linked_requirement_assessment_in_an_inaccessible_folder_is_excluded_from_the_prompt(
    monkeypatch,
):
    """Test C: same principle for a linked RequirementAssessment (and the Requirement name and
    ComplianceAssessment name carried in its display text)."""
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("vault")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)
    hidden_ra = _make_requirement_assessment_in_folder(
        folder=folder_b, name="INACCESSIBLE_REQUIREMENT_SECRET_MARKER"
    )
    evidence.requirement_assessments.add(hidden_ra)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")

    scoped_client, _user = _make_scoped_client(folder=folder_a)
    response, prompt = _capture_prompt(monkeypatch, scoped_client, evidence.id)

    assert response.status_code == 200
    assert "INACCESSIBLE_REQUIREMENT_SECRET_MARKER" not in prompt


@pytest.mark.django_db
def test_linked_requirement_assessment_in_an_accessible_folder_is_included_in_the_prompt(
    monkeypatch,
):
    """Test D (positive control) for RequirementAssessment."""
    folder_a = _make_domain_folder("acme")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)
    visible_ra = _make_requirement_assessment_in_folder(
        folder=folder_a, name="ACCESSIBLE_REQUIREMENT_MARKER"
    )
    evidence.requirement_assessments.add(visible_ra)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")

    scoped_client, user = _make_scoped_client(folder=folder_a)
    role = Role.objects.get(roleassignment__user=user)
    role.permissions.add(Permission.objects.get(codename="view_requirementassessment"))

    response, prompt = _capture_prompt(monkeypatch, scoped_client, evidence.id)

    assert response.status_code == 200
    assert "ACCESSIBLE_REQUIREMENT_MARKER" in prompt


@pytest.mark.django_db
def test_mixed_visibility_prompt_contains_only_the_visible_linked_objects(monkeypatch):
    """Test E: one visible and one hidden control, one visible and one hidden requirement
    assessment, all linked to the same Evidence. The prompt must contain only what the caller
    is actually authorized to see."""
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("vault")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)

    visible_control = _make_control_in_folder(folder=folder_a, name="VISIBLE_CONTROL_MARKER")
    hidden_control = _make_control_in_folder(folder=folder_b, name="HIDDEN_CONTROL_MARKER")
    visible_ra = _make_requirement_assessment_in_folder(
        folder=folder_a, name="VISIBLE_REQUIREMENT_MARKER"
    )
    hidden_ra = _make_requirement_assessment_in_folder(
        folder=folder_b, name="HIDDEN_REQUIREMENT_MARKER"
    )
    evidence.applied_controls.add(visible_control, hidden_control)
    evidence.requirement_assessments.add(visible_ra, hidden_ra)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")

    scoped_client, user = _make_scoped_client(folder=folder_a)
    role = Role.objects.get(roleassignment__user=user)
    role.permissions.add(
        Permission.objects.get(codename="view_appliedcontrol"),
        Permission.objects.get(codename="view_requirementassessment"),
    )

    response, prompt = _capture_prompt(monkeypatch, scoped_client, evidence.id)

    assert response.status_code == 200
    assert "VISIBLE_CONTROL_MARKER" in prompt
    assert "VISIBLE_REQUIREMENT_MARKER" in prompt
    assert "HIDDEN_CONTROL_MARKER" not in prompt
    assert "HIDDEN_REQUIREMENT_MARKER" not in prompt


@pytest.mark.django_db
def test_hidden_linked_objects_are_not_counted_either(monkeypatch):
    """Test F: no enumeration side channel through the counts either. The response's own
    linked_*_count fields (and the counts handed to the model) must reflect only what the
    caller can see, not the true total."""
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("vault")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)
    evidence.applied_controls.add(_make_control_in_folder(folder=folder_a, name="Visible control"))
    evidence.applied_controls.add(_make_control_in_folder(folder=folder_b, name="Hidden control"))
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")

    scoped_client, user = _make_scoped_client(folder=folder_a)
    role = Role.objects.get(roleassignment__user=user)
    role.permissions.add(Permission.objects.get(codename="view_appliedcontrol"))

    response, prompt = _capture_prompt(monkeypatch, scoped_client, evidence.id)

    assert response.status_code == 200
    assert response.json()["linked_applied_controls_count"] == 1
    assert '"linked_applied_controls": 2' not in prompt
    assert '"linked_applied_controls": 1' in prompt or "\"counts\"" in prompt


@pytest.mark.django_db
def test_visibility_filtered_review_still_never_writes_grc_data(monkeypatch):
    """Test G: the visibility fix must not change the advisory, read-only nature of the call."""
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("vault")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)
    hidden_control = _make_control_in_folder(folder=folder_b, name="Hidden control")
    evidence.applied_controls.add(hidden_control)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")
    scoped_client, _user = _make_scoped_client(folder=folder_a)
    before = _counts_snapshot()

    response, _prompt = _capture_prompt(monkeypatch, scoped_client, evidence.id)

    assert response.status_code == 200
    assert _counts_snapshot() == before
    hidden_control.refresh_from_db()
    evidence.refresh_from_db()
    assert hidden_control.name == "Hidden control"
    assert evidence.applied_controls.count() == 1


@pytest.mark.django_db
def test_batch_review_also_filters_linked_context_by_visibility(monkeypatch):
    """The batch action shares build_evidence_context with the single-item action; prove the
    fix applies there too instead of assuming it from a shared code path."""
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("vault")
    evidence = Evidence.objects.create(name="Backup export", folder=folder_a)
    hidden_control = _make_control_in_folder(
        folder=folder_b, name="BATCH_INACCESSIBLE_CONTROL_MARKER"
    )
    evidence.applied_controls.add(hidden_control)
    EvidenceRevision.objects.create(evidence=evidence, version=1, observation="Initial upload.")

    scoped_client, _user = _make_scoped_client(folder=folder_a)
    _configure_local_provider_env(monkeypatch)
    captured_bodies: list = []

    def _handler(request, timeout, body):
        captured_bodies.append(body)
        return {"model": body["model"], "response": json.dumps(_valid_judgement()), "done": True}

    _install_mock_ollama_urlopen(monkeypatch, _handler)

    response = scoped_client.post(
        _batch_url(), {"evidence_ids": [str(evidence.id)]}, format="json"
    )

    assert response.status_code == 200
    assert len(captured_bodies) == 1
    assert "BATCH_INACCESSIBLE_CONTROL_MARKER" not in captured_bodies[0]["prompt"]


# ---------------------------------------------------------------------------
# 7. Batch endpoint
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_batch_review_skips_inaccessible_and_unknown_ids_without_disclosing_them(
    authenticated_client, monkeypatch
):
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("other-tenant")
    evidence_a = _make_evidence_with_context(folder=folder_a)
    evidence_b = _make_evidence_with_context(folder=folder_b)
    scoped_client, _user = _make_scoped_client(folder=folder_a)
    _install_provider_returning(monkeypatch, _valid_judgement())

    response = scoped_client.post(
        _batch_url(),
        {"evidence_ids": [str(evidence_a.id), str(evidence_b.id), str(uuid.uuid4())]},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["requested_count"] == 3
    assert body["reviewed_count"] == 1
    assert body["skipped_count"] == 2
    assert body["results"][0]["evidence_id"] == str(evidence_a.id)


@pytest.mark.django_db
def test_batch_review_rejects_more_than_the_allowed_batch_size(authenticated_client):
    folder = _make_domain_folder("acme")
    ids = [str(uuid.uuid4()) for _ in range(11)]

    response = authenticated_client.post(
        _batch_url(), {"evidence_ids": ids}, format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_batch_review_empty_set_is_rejected_not_silently_accepted(authenticated_client):
    response = authenticated_client.post(
        _batch_url(), {"evidence_ids": []}, format="json"
    )
    assert response.status_code == 400
