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
    ReferenceControl,
    RequirementAssessment,
    RequirementNode,
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


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_ai_risk_scenario_commit_{uuid.uuid4().hex}.sqlite3"
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
def grc_context(admin_user):
    """An existing folder, risk assessment, asset, and applied control.

    Step 8B only ever writes a RiskScenario under records like these; it never creates a
    RiskAssessment, a RiskMatrix, or a RiskAcceptance.
    """
    root = Folder.get_root_folder()
    folder = Folder.objects.create(
        name=f"Al-Rawasi Fintech {uuid.uuid4().hex[:6]}",
        parent_folder=root,
        content_type=Folder.ContentType.DOMAIN,
    )
    perimeter = Perimeter.objects.create(name="Core Banking Platform", folder=folder)
    risk_matrix = RiskMatrix.objects.create(
        name=f"Test matrix {uuid.uuid4().hex[:6]}",
        folder=root,
        json_definition=RISK_MATRIX_JSON_DEFINITION,
    )
    risk_assessment = RiskAssessment.objects.create(
        name="Q4 2026 Risk Assessment",
        folder=folder,
        perimeter=perimeter,
        risk_matrix=risk_matrix,
    )
    asset = Asset.objects.create(
        name="Core Banking Platform",
        ref_id="AST-CBP-001",
        folder=folder,
    )
    applied_control = AppliedControl.objects.create(
        name="Multi-Factor Authentication for Remote Access",
        ref_id="CTL-MFA-001",
        folder=folder,
    )
    return {
        "folder": folder,
        "perimeter": perimeter,
        "risk_matrix": risk_matrix,
        "risk_assessment": risk_assessment,
        "asset": asset,
        "applied_control": applied_control,
    }


def _scenario_payload(**overrides):
    payload = {
        "temporary_id": "risk_scenario_1",
        "title": "Unauthorized remote access to the Core Banking Platform",
        "description": (
            "Weak or missing MFA enforcement could allow an actor to reach the Core Banking "
            "Platform over remote access channels."
        ),
        "asset_reference": "AST-CBP-001",
        "asset_title": "Core Banking Platform",
        "linked_finding_reference": "FND-CAND-001",
        "linked_finding_title": "MFA is not documented or not enforced for remote access.",
        "linked_applied_control_reference": "CTL-MFA-001",
        "linked_applied_control_title": "Multi-Factor Authentication for Remote Access",
        "linked_remediation_action_reference": "REM-CAND-001",
        "linked_remediation_action_title": "Implement and enforce MFA for remote access",
        "linked_framework_control_reference": "urn:sama:ecc:3.3.5",
        "linked_framework_control_code": "3.3.5",
        "linked_framework_control_title": "SAMA control 3.3.5",
        "threat": "Unauthorized access by an external actor",
        "vulnerability": "No MFA for remote access",
        "impact_description": "Potential unauthorized transactions and data disclosure.",
        "likelihood": "high",
        "impact": "high",
        "risk_level": "high",
        "rationale": "Derived from the reviewed preliminary finding.",
        "recommended_next_steps": ["Confirm the MFA configuration with the platform owner."],
        "confidence": 0.82,
        "review_status": "pending_review",
    }
    payload.update(overrides)
    return payload


def _decision(**overrides):
    payload_overrides = overrides.pop("payload_overrides", {})
    decision = {
        "temporary_id": "risk_scenario_1",
        "selected": True,
        "decision": "create",
        "existing_record_reference": "",
        "payload": _scenario_payload(**payload_overrides),
    }
    decision.update(overrides)
    if decision.get("payload") and decision["payload"].get("temporary_id") != decision[
        "temporary_id"
    ]:
        decision["payload"]["temporary_id"] = decision["temporary_id"]
    return decision


def _request_payload(context, *, dry_run=True, approved=False, decisions=None, **overrides):
    payload = {
        "dry_run": dry_run,
        "approved": approved,
        "folder_reference": str(context["folder"].id),
        "assessment_reference": str(context["risk_assessment"].id),
        "decisions": decisions if decisions is not None else [_decision()],
    }
    payload.update(overrides)
    return payload


def _post(client, payload):
    return client.post(reverse("ai-risk-scenario-commit"), payload, format="json")


def _counts_snapshot():
    return {
        "Folder": Folder.objects.count(),
        "Perimeter": Perimeter.objects.count(),
        "Framework": Framework.objects.count(),
        "RequirementNode": RequirementNode.objects.count(),
        "ReferenceControl": ReferenceControl.objects.count(),
        "ComplianceAssessment": ComplianceAssessment.objects.count(),
        "RequirementAssessment": RequirementAssessment.objects.count(),
        "Asset": Asset.objects.count(),
        "AppliedControl": AppliedControl.objects.count(),
        "Vulnerability": Vulnerability.objects.count(),
        "RiskMatrix": RiskMatrix.objects.count(),
        "RiskAssessment": RiskAssessment.objects.count(),
        "RiskScenario": RiskScenario.objects.count(),
        "Evidence": Evidence.objects.count(),
        "Finding": Finding.objects.count(),
        "RiskAcceptance": RiskAcceptance.objects.count(),
    }


# ---- contract ------------------------------------------------------------------------


@pytest.mark.django_db
def test_requires_authentication(client, grc_context):
    response = client.post(
        reverse("ai-risk-scenario-commit"),
        _request_payload(grc_context),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_validates_and_writes_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()

    response = _post(authenticated_client, _request_payload(grc_context))

    after = _counts_snapshot()
    assert response.status_code == 200
    body = response.json()
    assert sorted(body.keys()) == [
        "blocking_errors",
        "commit_status",
        "created_records",
        "deferred_records",
        "dry_run",
        "planned_actions",
        "rejected_records",
        "reused_records",
        "skipped_records",
        "warnings",
    ]
    assert body["dry_run"] is True
    assert body["commit_status"] in {"validated", "validated_with_warnings"}
    assert body["planned_actions"]
    assert body["created_records"] == []
    assert body["reused_records"] == []
    assert body["blocking_errors"] == []
    assert before == after


@pytest.mark.django_db
def test_approved_false_with_dry_run_false_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=False)
    )
    assert response.status_code == 400
    assert "approved" in response.json()


@pytest.mark.django_db
def test_approved_true_with_dry_run_true_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=True, approved=True)
    )
    assert response.status_code == 400
    assert "approved" in response.json()


@pytest.mark.django_db
def test_ai_and_provider_fields_are_rejected(authenticated_client, grc_context):
    for field in (
        "use_ai",
        "run_ai",
        "ai_provider",
        "provider_mode",
        "llm",
        "model",
        "prompt",
        "system_prompt",
        "temperature",
    ):
        response = _post(authenticated_client, _request_payload(grc_context, **{field: "x"}))
        assert response.status_code == 422, field
        body = response.json()
        assert body["error_code"] == "ai_risk_scenario_commit_guardrails_failed"
        assert any(error["field"] == field for error in body["blocking_errors"])


@pytest.mark.django_db
def test_write_intent_and_risk_decision_fields_are_rejected(authenticated_client, grc_context):
    for field in (
        "auto_approve",
        "create_risk_assessment",
        "create_risk_acceptance",
        "risk_acceptance",
        "accept_risk",
        "close_risk",
        "treatment",
        "close_audit",
        "certify_compliance",
    ):
        response = _post(authenticated_client, _request_payload(grc_context, **{field: True}))
        assert response.status_code == 422, field
        body = response.json()
        assert any(error["field"] == field for error in body["blocking_errors"])


@pytest.mark.django_db
def test_raw_database_identifier_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, risk_assessment_id=str(uuid.uuid4())),
    )
    assert response.status_code == 422
    body = response.json()
    assert any(
        error["code"] == "raw_database_identifier" for error in body["blocking_errors"]
    )


@pytest.mark.django_db
def test_invalid_enum_is_rejected(authenticated_client, grc_context):
    for field in ("likelihood", "impact", "risk_level"):
        response = _post(
            authenticated_client,
            _request_payload(
                grc_context,
                decisions=[_decision(payload_overrides={field: "catastrophic"})],
            ),
        )
        assert response.status_code == 400, field
        assert "decisions" in response.json()


@pytest.mark.django_db
def test_invalid_confidence_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, decisions=[_decision(payload_overrides={"confidence": 1.4})]),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


@pytest.mark.django_db
def test_non_pending_review_status_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context, decisions=[_decision(payload_overrides={"review_status": "approved"})]
        ),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


@pytest.mark.django_db
def test_duplicate_temporary_id_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, decisions=[_decision(), _decision()]),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


# ---- decisions -----------------------------------------------------------------------


@pytest.mark.django_db
def test_reject_and_defer_write_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(temporary_id="risk_scenario_1", decision="reject"),
                _decision(temporary_id="risk_scenario_2", decision="defer"),
            ],
        ),
    )

    after = _counts_snapshot()
    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert len(body["rejected_records"]) == 1
    assert len(body["deferred_records"]) == 1
    assert before == after


@pytest.mark.django_db
def test_unselected_decision_is_skipped_without_write(authenticated_client, grc_context):
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context, dry_run=False, approved=True, decisions=[_decision(selected=False)]
        ),
    )

    after = _counts_snapshot()
    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert body["skipped_records"][0]["skip_reason"] == "not_selected"
    assert before == after


# ---- approved write ------------------------------------------------------------------


@pytest.mark.django_db
def test_approved_commit_creates_risk_scenario_only(authenticated_client, grc_context):
    before = _counts_snapshot()

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    after = _counts_snapshot()
    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is False
    assert body["commit_status"] in {"created", "completed_with_warnings"}
    assert len(body["created_records"]) == 1
    record = body["created_records"][0]
    assert record["record_type"] == "risk_scenario"
    assert record["risk_rating_recorded"] is False

    scenario = RiskScenario.objects.get(id=record["record_id"])
    assert scenario.risk_assessment_id == grc_context["risk_assessment"].id
    assert scenario.name == "Unauthorized remote access to the Core Banking Platform"
    # The platform "not rated" defaults are untouched: Step 8B sets no risk rating.
    assert scenario.current_proba == -1
    assert scenario.current_impact == -1
    assert scenario.current_level == -1
    assert scenario.residual_proba == -1
    assert scenario.inherent_proba == -1
    # No risk decision is taken: treatment keeps the platform default.
    assert scenario.treatment == "open"
    # Advisory context with no platform column is preserved as readable description text.
    assert "Threat: Unauthorized access by an external actor" in scenario.description
    assert "not a platform risk rating" in scenario.description
    # Only the risk scenario is new; no other domain record was created.
    assert after["RiskScenario"] == before["RiskScenario"] + 1
    assert {key: value for key, value in after.items() if key != "RiskScenario"} == {
        key: value for key, value in before.items() if key != "RiskScenario"
    }


@pytest.mark.django_db
def test_approved_commit_links_existing_asset_and_applied_control(
    authenticated_client, grc_context
):
    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 200
    record = response.json()["created_records"][0]
    scenario = RiskScenario.objects.get(id=record["record_id"])
    assert list(scenario.assets.values_list("id", flat=True)) == [grc_context["asset"].id]
    assert list(scenario.applied_controls.values_list("id", flat=True)) == [
        grc_context["applied_control"].id
    ]


@pytest.mark.django_db
def test_unknown_asset_reference_warns_and_does_not_create_asset(
    authenticated_client, grc_context
):
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(
                    payload_overrides={
                        "asset_reference": "AST-DOES-NOT-EXIST",
                        "asset_title": "Unknown platform",
                    }
                )
            ],
        ),
    )

    after = _counts_snapshot()
    assert response.status_code == 200
    body = response.json()
    assert any(
        warning["code"] == "asset_linkage_not_applied" for warning in body["warnings"]
    )
    assert after["Asset"] == before["Asset"]


@pytest.mark.django_db
def test_duplicate_scenario_is_reused_not_duplicated(authenticated_client, grc_context):
    first = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )
    assert first.status_code == 200
    created_id = first.json()["created_records"][0]["record_id"]

    before = _counts_snapshot()
    second = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )
    after = _counts_snapshot()

    assert second.status_code == 200
    body = second.json()
    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    assert body["reused_records"][0]["record_id"] == created_id
    assert any(warning["code"] == "duplicate_reused" for warning in body["warnings"])
    assert before == after


@pytest.mark.django_db
def test_duplicate_in_batch_is_skipped(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[_decision(), _decision(temporary_id="risk_scenario_2")],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["created_records"]) == 1
    assert any(
        record["skip_reason"] == "duplicate_in_batch" for record in body["skipped_records"]
    )


@pytest.mark.django_db
def test_reuse_decision_does_not_mutate_existing_scenario(authenticated_client, grc_context):
    existing = RiskScenario.objects.create(
        risk_assessment=grc_context["risk_assessment"],
        name="Existing reviewed scenario",
        description="Author-owned description.",
    )

    before = _counts_snapshot()
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(
                    decision="reuse", existing_record_reference=str(existing.id), payload=None
                )
            ],
        ),
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    existing.refresh_from_db()
    assert existing.description == "Author-owned description."
    assert before == after


# ---- blocked paths -------------------------------------------------------------------


@pytest.mark.django_db
def test_missing_assessment_reference_is_blocked(authenticated_client, grc_context):
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True, assessment_reference=""),
    )

    after = _counts_snapshot()
    assert response.status_code == 422
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert any(
        error["code"] == "risk_assessment_reference_required"
        for error in body["blocking_errors"]
    )
    assert before == after


@pytest.mark.django_db
def test_unknown_assessment_reference_is_blocked(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            assessment_reference=str(uuid.uuid4()),
        ),
    )

    assert response.status_code == 422
    body = response.json()
    assert any(
        error["code"] == "risk_assessment_not_found" for error in body["blocking_errors"]
    )


@pytest.mark.django_db
def test_locked_risk_assessment_is_blocked(authenticated_client, grc_context):
    grc_context["risk_assessment"].is_locked = True
    grc_context["risk_assessment"].save()

    before = _counts_snapshot()
    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert any(error["code"] == "assessment_locked" for error in body["blocking_errors"])
    assert before == after


@pytest.mark.django_db
def test_assessment_outside_folder_is_blocked(authenticated_client, grc_context):
    other_folder = Folder.objects.create(
        name=f"Other domain {uuid.uuid4().hex[:6]}",
        parent_folder=Folder.get_root_folder(),
        content_type=Folder.ContentType.DOMAIN,
    )

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            folder_reference=str(other_folder.id),
        ),
    )

    assert response.status_code == 422
    body = response.json()
    assert any(
        error["code"] == "assessment_out_of_scope" for error in body["blocking_errors"]
    )


# ---- step isolation ------------------------------------------------------------------


def test_step8b_service_does_not_import_ai_modules():
    """Step 8B is deterministic: it must not reach any provider, LLM, or prompt module."""
    from pathlib import Path

    source = Path(
        __file__
    ).resolve().parents[2] / "ai_onboarding" / "risk_scenario_commit_service.py"
    text = source.read_text(encoding="utf-8")
    for forbidden in (
        "import llm",
        "from .llm",
        "_provider import",
        "llm_prompts",
        "llm_provider",
        "llm_config",
        "get_system_prompt",
        "generate_structured",
    ):
        assert forbidden not in text, forbidden
