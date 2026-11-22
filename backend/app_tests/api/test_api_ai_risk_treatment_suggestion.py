import json
import urllib.error
import uuid

import pytest
from django.conf import settings as django_settings
from django.contrib.auth.models import Permission
from django.urls import reverse
from knox.models import AuthToken

from ai_onboarding.risk_treatment_suggestion_serializers import (
    MAX_MITIGATING_ACTIONS,
    MAX_RATIONALE_LENGTH,
    SUGGESTABLE_TREATMENT_CHOICES,
)
from core import startup as core_startup
from core.models import (
    AppliedControl,
    Asset,
    ComplianceAssessment,
    Evidence,
    Finding,
    RequirementAssessment,
    RiskAcceptance,
    RiskAssessment,
    RiskMatrix,
    RiskScenario,
    Threat,
    Vulnerability,
)
from iam.models import Folder, Role, RoleAssignment, User, UserGroup
from test_fixtures import RISK_MATRIX_JSON_DEFINITION


_ORIGINAL_STARTUP_CALL_COMMAND = core_startup.call_command


def _patched_startup_call_command(name, *args, **kwargs):
    # The library catalogue is not exercised here and dominates per-module setup cost.
    if name in {"storelibraries", "autoloadlibraries", "sync_event_types", "backfill_builtin_metrics"}:
        return None
    return _ORIGINAL_STARTUP_CALL_COMMAND(name, *args, **kwargs)


core_startup.call_command = _patched_startup_call_command


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR) / "db" / f"test_ai_risk_treatment_suggestion_{uuid.uuid4().hex}.sqlite3"
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
    for name in (
        "AI_PROVIDER",
        "LOCAL_AI_API_STYLE",
        "LOCAL_AI_BASE_URL",
        "LOCAL_AI_MODEL_DEFAULT",
        "LOCAL_AI_MODEL_RISK_TREATMENT_SUGGESTION",
        "LOCAL_AI_TIMEOUT_SECONDS",
        "LOCAL_AI_MAX_OUTPUT_TOKENS",
        "LOCAL_AI_TEMPERATURE",
    ):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def admin_user(app_config):
    admin = User.objects.create_superuser(f"admin-{uuid.uuid4().hex[:8]}@tests.com", is_published=True)
    admin_group = UserGroup.objects.get(name="BI-UG-ADM")
    admin.folder = admin_group.folder
    admin.save()
    admin_group.user_set.add(admin)
    return admin


@pytest.fixture
def authenticated_client(admin_user):
    from rest_framework.test import APIClient

    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {AuthToken.objects.create(user=admin_user)[1]}")
    return api_client


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_domain_folder(name: str) -> Folder:
    return Folder.objects.create(
        name=f"{name}-{uuid.uuid4().hex[:6]}",
        content_type=Folder.ContentType.DOMAIN,
        builtin=False,
        parent_folder=Folder.objects.get(content_type=Folder.ContentType.ROOT),
    )


def _make_scoped_client(*, folder: Folder, extra_perms: tuple[str, ...] = ()):
    """A non-admin user who can view risk scenarios (and their folder) in `folder` only.

    view_folder is required by get_accessible_object_ids(), which BaseModelViewSet.get_queryset()
    uses; without it the scenario is excluded before any object permission is checked.
    """
    from rest_framework.test import APIClient

    user = User.objects.create_user(f"scoped-{uuid.uuid4().hex[:8]}@tests.com", is_published=True)
    role = Role.objects.create(name=f"risk-viewer-{uuid.uuid4().hex[:8]}")
    role.permissions.set(
        Permission.objects.filter(codename__in=["view_riskscenario", "view_folder", *extra_perms])
    )
    role.save()
    assignment = RoleAssignment.objects.create(user=user, role=role, folder=folder, is_recursive=True)
    assignment.perimeter_folders.add(folder)
    assignment.save()

    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {AuthToken.objects.create(user=user)[1]}")
    return api_client, user


def _make_risk_scenario(*, folder: Folder, label: str = "Acme", rated: bool = True, linked: bool = True):
    """A realistic scenario: rated current/residual risk, a threat, an asset, a vulnerability,
    an existing control, and a planned control, all in `folder`."""
    risk_matrix = RiskMatrix.objects.create(
        name=f"{label} matrix {uuid.uuid4().hex[:6]}",
        folder=Folder.get_root_folder(),
        json_definition=RISK_MATRIX_JSON_DEFINITION,
    )
    risk_assessment = RiskAssessment.objects.create(
        name=f"{label} Risk Assessment", folder=folder, risk_matrix=risk_matrix
    )
    scenario = RiskScenario.objects.create(
        name=f"{label} unauthorized privileged access",
        description=f"{label}: compromised privileged credentials could expose customer data.",
        risk_assessment=risk_assessment,
        current_proba=2 if rated else -1,
        current_impact=2 if rated else -1,
        residual_proba=1 if rated else -1,
        residual_impact=2 if rated else -1,
    )
    if linked:
        scenario.threats.add(Threat.objects.create(name=f"{label} credential theft", folder=folder))
        scenario.assets.add(Asset.objects.create(name=f"{label} identity provider", folder=folder))
        scenario.vulnerabilities.add(
            Vulnerability.objects.create(name=f"{label} shared admin accounts", folder=folder)
        )
        scenario.existing_applied_controls.add(
            AppliedControl.objects.create(name=f"{label} MFA for admins", folder=folder, status="active")
        )
        scenario.applied_controls.add(
            AppliedControl.objects.create(name=f"{label} privileged access management", folder=folder)
        )
    return scenario


# ---------------------------------------------------------------------------
# Mock provider helpers
# ---------------------------------------------------------------------------


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
    monkeypatch.setenv("LOCAL_AI_MODEL_RISK_TREATMENT_SUGGESTION", "qwen3:4b-instruct")
    monkeypatch.setenv("LOCAL_AI_TIMEOUT_SECONDS", "60")
    monkeypatch.setenv("LOCAL_AI_TEMPERATURE", "0.1")
    monkeypatch.setenv("LOCAL_AI_MAX_OUTPUT_TOKENS", "1200")


def _install_raw_response(monkeypatch, raw_text: str, captured: list | None = None):
    _configure_local_provider_env(monkeypatch)

    def _mock_urlopen(request, timeout=0):
        body = json.loads(request.data.decode("utf-8"))
        if captured is not None:
            captured.append(body)
        return _MockHttpResponse({"model": body["model"], "response": raw_text, "done": True})

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _install_provider_returning(monkeypatch, suggestion: dict, captured: list | None = None):
    _install_raw_response(monkeypatch, json.dumps(suggestion), captured)


def _install_provider_raising(monkeypatch, exc: Exception):
    _configure_local_provider_env(monkeypatch)

    def _mock_urlopen(request, timeout=0):
        raise exc

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _mock_urlopen)


def _valid_suggestion(**overrides):
    suggestion = {
        "suggested_treatment": "mitigate",
        "confidence": 0.72,
        "rationale": "Current risk is above tolerance and a planned control would reduce it.",
        "mitigating_actions": [
            {
                "title": "Complete privileged access management rollout",
                "description": "Recommend finishing the planned PAM control for all admin accounts.",
                "priority": "P1",
            }
        ],
        "considerations": ["Assumes the planned control can be funded this quarter."],
    }
    suggestion.update(overrides)
    return suggestion


def _url(risk_scenario_id) -> str:
    return reverse("risk-scenarios-ai-treatment-suggestion", args=[risk_scenario_id])


def _post(api_client, risk_scenario_id, body=None):
    return api_client.post(_url(risk_scenario_id), body or {}, format="json")


def _counts_snapshot():
    return {
        model.__name__: model.objects.count()
        for model in (
            RiskScenario,
            RiskAssessment,
            RiskAcceptance,
            AppliedControl,
            Asset,
            Threat,
            Vulnerability,
            Evidence,
            Finding,
            RequirementAssessment,
            ComplianceAssessment,
        )
    }


# ---------------------------------------------------------------------------
# 1. Authentication, authorization, tenant scoping
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_anonymous_request_is_rejected(client):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))

    assert _post(client, scenario.id).status_code == 401


@pytest.mark.django_db
def test_authorized_same_folder_user_can_request_a_suggestion(monkeypatch):
    folder = _make_domain_folder("acme")
    scenario = _make_risk_scenario(folder=folder)
    scoped_client, _user = _make_scoped_client(folder=folder)
    _install_provider_returning(monkeypatch, _valid_suggestion())

    response = _post(scoped_client, scenario.id)

    assert response.status_code == 200
    assert response.json()["outcome"] == "suggested"


@pytest.mark.django_db
def test_cross_folder_scenario_is_indistinguishable_from_a_missing_one(monkeypatch):
    folder_a = _make_domain_folder("acme")
    folder_b = _make_domain_folder("other")
    scenario_a = _make_risk_scenario(folder=folder_a)
    scoped_client_b, _user = _make_scoped_client(folder=folder_b)
    _install_provider_returning(monkeypatch, _valid_suggestion())

    forbidden = _post(scoped_client_b, scenario_a.id)
    missing = _post(scoped_client_b, uuid.uuid4())

    assert forbidden.status_code == 404
    assert missing.status_code == 404
    assert forbidden.json() == missing.json()


@pytest.mark.django_db
def test_nonexistent_scenario_returns_404(authenticated_client):
    assert _post(authenticated_client, uuid.uuid4()).status_code == 404


@pytest.mark.django_db
def test_request_body_cannot_carry_write_intent_fields(authenticated_client):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))

    for field in ("treatment", "update_treatment", "commit", "approve", "risk_scenario_id"):
        assert _post(authenticated_client, scenario.id, {field: "accept"}).status_code == 400, field


# ---------------------------------------------------------------------------
# 2. Successful suggestions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_valid_suggestion_shape(authenticated_client, monkeypatch):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    _install_provider_returning(monkeypatch, _valid_suggestion())

    response = _post(authenticated_client, scenario.id)

    assert response.status_code == 200
    body = response.json()
    assert body["risk_scenario_id"] == str(scenario.id)
    assert body["risk_scenario_name"] == scenario.name
    assert body["current_treatment"] == "open"
    assert body["outcome"] == "suggested"
    assert body["suggested_treatment"] == "mitigate"
    assert body["confidence"] == pytest.approx(0.72)
    assert body["rationale"]
    assert body["mitigating_actions"][0]["priority"] == "P1"
    assert body["considerations"]
    assert body["is_rated"] is True
    assert body["linked_threats_count"] == 1
    assert body["linked_assets_count"] == 1
    assert body["existing_controls_count"] == 1
    assert body["planned_controls_count"] == 1
    assert body["provider_mode"] == "configured_local_provider"
    assert "has not changed" in body["advisory_notice"]
    assert body["reviewed_at"]


@pytest.mark.django_db
@pytest.mark.parametrize("treatment", SUGGESTABLE_TREATMENT_CHOICES)
def test_every_real_treatment_value_is_accepted(authenticated_client, monkeypatch, treatment):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    actions = [] if treatment != "mitigate" else _valid_suggestion()["mitigating_actions"]
    _install_provider_returning(
        monkeypatch, _valid_suggestion(suggested_treatment=treatment, mitigating_actions=actions)
    )

    response = _post(authenticated_client, scenario.id)

    assert response.status_code == 200
    assert response.json()["suggested_treatment"] == treatment


@pytest.mark.django_db
def test_suggestion_wording_is_not_mistaken_for_a_claimed_action(authenticated_client, monkeypatch):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    _install_provider_returning(
        monkeypatch,
        _valid_suggestion(
            rationale=(
                "Recommend mitigating the risk. Consider accepting the residual risk only if it "
                "stays within tolerance; the risk could also be transferred through insurance."
            )
        ),
    )

    assert _post(authenticated_client, scenario.id).status_code == 200


@pytest.mark.django_db
def test_insufficient_context_returns_no_suggestion_without_calling_the_model(
    authenticated_client, monkeypatch
):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"), rated=False, linked=False)
    scenario.description = ""
    scenario.save()
    captured: list = []
    _install_provider_returning(monkeypatch, _valid_suggestion(), captured)

    response = _post(authenticated_client, scenario.id)

    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "insufficient_context"
    assert body["suggested_treatment"] is None
    assert body["confidence"] == 0.0
    assert body["provider_mode"] == "not_called_insufficient_context"
    assert captured == []


# ---------------------------------------------------------------------------
# 3. Provider failures degrade safely, without leaking provider details
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_provider_not_configured_returns_no_suggestion(authenticated_client):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))

    body = _post(authenticated_client, scenario.id).json()

    assert body["outcome"] == "provider_unavailable"
    assert body["suggested_treatment"] is None
    assert body["provider_mode"] == "provider_not_configured_fallback"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "exc",
    [
        urllib.error.URLError("connection refused"),
        TimeoutError("timed out"),
        urllib.error.HTTPError(
            url="http://127.0.0.1:11434/api/generate", code=500, msg="boom", hdrs=None, fp=None
        ),
    ],
    ids=["unavailable", "timeout", "http_error"],
)
def test_provider_transport_failures_fail_safely_without_leaking_details(
    authenticated_client, monkeypatch, exc
):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    _install_provider_raising(monkeypatch, exc)

    response = _post(authenticated_client, scenario.id)

    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "provider_unavailable"
    assert body["suggested_treatment"] is None
    assert body["provider_mode"] == "local_provider_error_fallback"
    for leaked in ("11434", "127.0.0.1", "connection refused", "boom", "Traceback"):
        assert leaked not in response.content.decode(), leaked


# ---------------------------------------------------------------------------
# 4. Untrusted model output: malformed, incomplete, or out of contract -> 422
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raw_text",
    ["not json at all {{{", "I suggest mitigating this risk with MFA.", ""],
    ids=["malformed_json", "prose", "empty"],
)
def test_unparseable_model_output_is_rejected(authenticated_client, monkeypatch, raw_text):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    _install_raw_response(monkeypatch, raw_text)
    before = _counts_snapshot()

    response = _post(authenticated_client, scenario.id)

    assert response.status_code == 422
    assert _counts_snapshot() == before


@pytest.mark.django_db
@pytest.mark.parametrize(
    "suggestion",
    [
        {"suggested_treatment": "mitigate", "confidence": 0.5},
        _valid_suggestion(suggested_treatment="ignore"),
        _valid_suggestion(suggested_treatment="open"),
        _valid_suggestion(confidence=1.5),
        _valid_suggestion(confidence="high"),
        _valid_suggestion(
            mitigating_actions=[{"title": "Do it", "description": "Now.", "priority": "urgent"}]
        ),
        _valid_suggestion(rationale="x" * (MAX_RATIONALE_LENGTH + 1)),
        _valid_suggestion(
            mitigating_actions=[
                {"title": f"Action {i}", "description": "Recommend it.", "priority": "P2"}
                for i in range(MAX_MITIGATING_ACTIONS + 1)
            ]
        ),
        _valid_suggestion(unexpected_debug_field="hello"),
    ],
    ids=[
        "missing_required_field",
        "unknown_treatment",
        "undecided_open_is_not_a_treatment",
        "confidence_out_of_range",
        "confidence_not_a_number",
        "invalid_action_priority",
        "excessively_long_rationale",
        "too_many_actions",
        "undeclared_field",
    ],
)
def test_out_of_contract_output_is_rejected(authenticated_client, monkeypatch, suggestion):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    _install_provider_returning(monkeypatch, suggestion)

    assert _post(authenticated_client, scenario.id).status_code == 422


# ---------------------------------------------------------------------------
# 5. Guardrails: write-implying keys and claimed actions -> hard 422, never a fallback
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize(
    "suggestion",
    [
        {**_valid_suggestion(), "update_treatment": True},
        {**_valid_suggestion(), "close_risk": True},
        _valid_suggestion(
            mitigating_actions=[
                {"title": "PAM", "description": "Recommend PAM.", "priority": "P1", "create_control": True}
            ]
        ),
    ],
    ids=["top_level_write_key", "close_risk_key", "nested_write_key_in_action"],
)
def test_write_implying_keys_are_hard_rejected(authenticated_client, monkeypatch, suggestion):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    _install_provider_returning(monkeypatch, suggestion)
    before = _counts_snapshot()

    response = _post(authenticated_client, scenario.id)

    assert response.status_code == 422
    assert response.json()["provider_mode"] == "local_provider_error_blocked"
    assert _counts_snapshot() == before


@pytest.mark.django_db
@pytest.mark.parametrize(
    "overrides",
    [
        {"rationale": "The risk has been accepted by the platform."},
        {"considerations": ["Treatment was applied to this scenario."]},
        {
            "mitigating_actions": [
                {"title": "PAM", "description": "I have created a remediation action.", "priority": "P1"}
            ]
        },
    ],
    ids=["risk_accepted_claim", "treatment_applied_claim", "remediation_created_claim"],
)
def test_claimed_action_language_is_hard_rejected(authenticated_client, monkeypatch, overrides):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    _install_provider_returning(monkeypatch, _valid_suggestion(**overrides))

    assert _post(authenticated_client, scenario.id).status_code == 422


@pytest.mark.django_db
def test_model_cannot_spoof_the_scenario_identifier(authenticated_client, monkeypatch):
    scenario_a = _make_risk_scenario(folder=_make_domain_folder("acme"), label="Acme")
    scenario_b = _make_risk_scenario(folder=_make_domain_folder("other"), label="Other")
    _install_provider_returning(
        monkeypatch, {**_valid_suggestion(), "risk_scenario_id": str(scenario_b.id)}
    )

    response = _post(authenticated_client, scenario_a.id)

    assert response.status_code == 422
    assert str(scenario_b.id) not in response.content.decode()


# ---------------------------------------------------------------------------
# 6. Tenant isolation of the prompt itself
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_other_tenants_data_never_enters_the_prompt(authenticated_client, monkeypatch):
    """Even for a caller who can see both folders, only scenario A's own context is sent."""
    scenario_a = _make_risk_scenario(folder=_make_domain_folder("acme"), label="Acme")
    _make_risk_scenario(folder=_make_domain_folder("other"), label="OtherTenant")
    captured: list = []
    _install_provider_returning(monkeypatch, _valid_suggestion(), captured)

    response = _post(authenticated_client, scenario_a.id)

    assert response.status_code == 200
    assert len(captured) == 1
    prompt = captured[0]["prompt"]
    assert "Acme unauthorized privileged access" in prompt
    assert "Acme MFA for admins" in prompt
    assert "OtherTenant" not in prompt


@pytest.mark.django_db
def test_linked_objects_the_caller_cannot_view_are_excluded_from_the_prompt(monkeypatch):
    """A caller who can view the scenario but not applied controls, assets, threats, or
    vulnerabilities gets none of their names in the prompt, and zero counts back."""
    folder = _make_domain_folder("acme")
    scenario = _make_risk_scenario(folder=folder)
    scoped_client, _user = _make_scoped_client(folder=folder)
    captured: list = []
    _install_provider_returning(monkeypatch, _valid_suggestion(), captured)

    response = _post(scoped_client, scenario.id)

    assert response.status_code == 200
    prompt = captured[0]["prompt"]
    for hidden in ("MFA for admins", "privileged access management", "identity provider",
                   "credential theft", "shared admin accounts"):
        assert hidden not in prompt, hidden
    body = response.json()
    assert body["existing_controls_count"] == 0
    assert body["linked_assets_count"] == 0


# ---------------------------------------------------------------------------
# 7. No business-data mutation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_suggestion_never_writes_grc_data(authenticated_client, monkeypatch):
    scenario = _make_risk_scenario(folder=_make_domain_folder("acme"))
    control = scenario.existing_applied_controls.get()
    risk_assessment = scenario.risk_assessment
    risk_assessment.refresh_from_db()
    _install_provider_returning(monkeypatch, _valid_suggestion(suggested_treatment="accept", mitigating_actions=[]))

    def fields():
        scenario.refresh_from_db()
        control.refresh_from_db()
        risk_assessment.refresh_from_db()
        return {
            "treatment": scenario.treatment,
            "current_level": scenario.current_level,
            "residual_level": scenario.residual_level,
            "justification": scenario.justification,
            "scenario_updated_at": scenario.updated_at,
            "control_status": control.status,
            "control_updated_at": control.updated_at,
            "risk_assessment_updated_at": risk_assessment.updated_at,
        }

    before_counts, before_fields = _counts_snapshot(), fields()

    response = _post(authenticated_client, scenario.id)

    assert response.status_code == 200
    assert response.json()["suggested_treatment"] == "accept"
    assert _counts_snapshot() == before_counts
    assert fields() == before_fields
