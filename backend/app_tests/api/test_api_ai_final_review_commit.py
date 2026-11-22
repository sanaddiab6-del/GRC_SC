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
        / f"test_ai_final_review_commit_{uuid.uuid4().hex}.sqlite3"
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
    """An existing folder, framework, and audit. Step 12B only notes on the audit."""
    root = Folder.get_root_folder()
    folder = Folder.objects.create(
        name=f"Al-Rawasi Fintech {uuid.uuid4().hex[:6]}",
        parent_folder=root,
        content_type=Folder.ContentType.DOMAIN,
    )
    perimeter = Perimeter.objects.create(name="Core Banking Platform", folder=folder)
    framework = Framework.objects.create(
        name=f"SAMA Cyber Security Fundamentals {uuid.uuid4().hex[:6]}",
        folder=root,
        urn=f"urn:test:framework:{uuid.uuid4().hex}",
    )
    RequirementNode.objects.create(
        framework=framework,
        folder=root,
        urn=f"urn:test:req-node:mfa:{uuid.uuid4().hex}",
        ref_id="3.3.5-4.e",
        name="Multi-factor authentication for sensitive and critical systems",
        assessable=True,
        order_id=1,
    )
    assessment = ComplianceAssessment.objects.create(
        name="Q4 2026 ECC Compliance Assessment",
        folder=folder,
        perimeter=perimeter,
        framework=framework,
    )
    assessment.create_requirement_assessments()
    return {"folder": folder, "framework": framework, "assessment": assessment}


def _handoff_payload(**overrides):
    payload = {
        "temporary_id": "final_review_1",
        "completion_summary": (
            "Steps 3B, 4B, and 9B recorded results; Step 7B is blocked because the framework "
            "library is not loaded."
        ),
        "completed_steps": ["3B: created", "4B: created"],
        "incomplete_steps": ["7B: blocked"],
        "created_or_reused_records_summary": ["Created asset: Core Banking Platform"],
        "blocked_items": ["Framework control 3.3.5-4.e is not loaded in the platform."],
        "human_review_required": ["Confirm the preliminary findings with their owners."],
        "recommended_next_steps": ["Load the framework library, then rerun Step 7B."],
        "demo_readiness_status": "partially_ready",
        "confidence": 0.7,
        "review_status": "pending_review",
    }
    payload.update(overrides)
    return payload


def _decision(**overrides):
    payload_overrides = overrides.pop("payload_overrides", {})
    decision = {
        "temporary_id": "final_review_1",
        "selected": True,
        "decision": "create",
        "existing_record_reference": "",
        "payload": _handoff_payload(**payload_overrides),
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
        "assessment_reference": str(context["assessment"].id),
        "decisions": decisions if decisions is not None else [_decision()],
    }
    payload.update(overrides)
    return payload


def _post(client, payload):
    return client.post(reverse("ai-final-review-commit"), payload, format="json")


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
        "RiskAssessment": RiskAssessment.objects.count(),
        "RiskScenario": RiskScenario.objects.count(),
        "Evidence": Evidence.objects.count(),
        "Finding": Finding.objects.count(),
        "RiskAcceptance": RiskAcceptance.objects.count(),
    }


def _assessment_state(context):
    assessment = ComplianceAssessment.objects.get(id=context["assessment"].id)
    return {
        "status": assessment.status,
        "is_locked": assessment.is_locked,
        "name": assessment.name,
        "due_date": assessment.due_date,
        "requirement_results": sorted(
            RequirementAssessment.objects.filter(compliance_assessment=assessment).values_list(
                "result", flat=True
            )
        ),
    }


# ---- contract ------------------------------------------------------------------------


@pytest.mark.django_db
def test_requires_authentication(client, grc_context):
    response = client.post(
        reverse("ai-final-review-commit"),
        _request_payload(grc_context),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_validates_and_writes_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()
    observation_before = grc_context["assessment"].observation

    response = _post(authenticated_client, _request_payload(grc_context))

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
    assert body["blocking_errors"] == []
    assert before == _counts_snapshot()
    assert (
        ComplianceAssessment.objects.get(id=grc_context["assessment"].id).observation
        == observation_before
    )


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
        assert body["error_code"] == "ai_final_review_commit_guardrails_failed"
        assert any(error["field"] == field for error in body["blocking_errors"])


@pytest.mark.django_db
def test_write_intent_and_completion_fields_are_rejected(authenticated_client, grc_context):
    for field in (
        "auto_approve",
        "mark_complete",
        "complete_workflow",
        "mark_ready",
        "set_assessment_status",
        "close_audit",
        "certify_compliance",
        "accept_risk",
    ):
        response = _post(authenticated_client, _request_payload(grc_context, **{field: True}))
        assert response.status_code == 422, field
        assert any(error["field"] == field for error in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_raw_database_identifier_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, compliance_assessment_id=str(uuid.uuid4())),
    )
    assert response.status_code == 422
    assert any(
        error["code"] == "raw_database_identifier"
        for error in response.json()["blocking_errors"]
    )


@pytest.mark.django_db
def test_invalid_enum_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[_decision(payload_overrides={"demo_readiness_status": "almost_ready"})],
        ),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


@pytest.mark.django_db
def test_invalid_confidence_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context, decisions=[_decision(payload_overrides={"confidence": 1.7})]
        ),
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
        authenticated_client, _request_payload(grc_context, decisions=[_decision(), _decision()])
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


# ---- decisions -----------------------------------------------------------------------


@pytest.mark.django_db
def test_reject_and_defer_write_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()
    state_before = _assessment_state(grc_context)
    observation_before = grc_context["assessment"].observation

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(temporary_id="final_review_1", decision="reject"),
                _decision(temporary_id="final_review_2", decision="defer"),
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert len(body["rejected_records"]) == 1
    assert len(body["deferred_records"]) == 1
    assert before == _counts_snapshot()
    assert state_before == _assessment_state(grc_context)
    assert (
        ComplianceAssessment.objects.get(id=grc_context["assessment"].id).observation
        == observation_before
    )


@pytest.mark.django_db
def test_unselected_decision_is_skipped_without_write(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context, dry_run=False, approved=True, decisions=[_decision(selected=False)]
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert body["skipped_records"][0]["skip_reason"] == "not_selected"
    assert not ComplianceAssessment.objects.get(id=grc_context["assessment"].id).observation


# ---- approved write ------------------------------------------------------------------


@pytest.mark.django_db
def test_approved_commit_appends_handoff_note_only(authenticated_client, grc_context):
    before = _counts_snapshot()
    state_before = _assessment_state(grc_context)

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is False
    assert body["commit_status"] in {"created", "completed_with_warnings"}
    assert len(body["created_records"]) == 1
    record = body["created_records"][0]
    assert record["record_type"] == "compliance_assessment_observation"
    assert record["updated_fields"] == ["observation"]
    assert record["audit_status_changed"] is False
    assert record["workflow_marked_complete"] is False
    assert record["audit_closed"] is False
    assert any(
        warning["code"] == "handoff_recorded_as_note_only" for warning in body["warnings"]
    )

    assessment = ComplianceAssessment.objects.get(id=grc_context["assessment"].id)
    assert "[AI onboarding Step 12B" in assessment.observation
    assert "partially_ready" in assessment.observation
    assert "Blocked items:" in assessment.observation
    assert "Human review required:" in assessment.observation
    # The audit status, lock flag, and requirement results are untouched, and no record was
    # created anywhere.
    assert state_before == _assessment_state(grc_context)
    assert before == _counts_snapshot()


@pytest.mark.django_db
def test_existing_observation_is_appended_not_overwritten(authenticated_client, grc_context):
    assessment = grc_context["assessment"]
    assessment.observation = "Auditor-owned note that must survive."
    assessment.save(update_fields=["observation"])

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 200
    assert any(
        warning["code"] == "observation_appended" for warning in response.json()["warnings"]
    )
    assessment.refresh_from_db()
    assert assessment.observation.startswith("Auditor-owned note that must survive.")
    assert "[AI onboarding Step 12B" in assessment.observation


@pytest.mark.django_db
def test_rerunning_the_same_handoff_changes_nothing(authenticated_client, grc_context):
    first = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )
    assert first.status_code == 200
    assessment = ComplianceAssessment.objects.get(id=grc_context["assessment"].id)
    observation_after_first = assessment.observation

    second = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert second.status_code == 200
    body = second.json()
    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    assessment.refresh_from_db()
    assert assessment.observation == observation_after_first


@pytest.mark.django_db
def test_duplicate_in_batch_is_skipped(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[_decision(), _decision(temporary_id="final_review_2")],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["created_records"]) == 1
    assert any(
        record["skip_reason"] == "duplicate_in_batch" for record in body["skipped_records"]
    )


@pytest.mark.django_db
def test_reuse_decision_does_not_mutate_observation(authenticated_client, grc_context):
    assessment = grc_context["assessment"]
    assessment.observation = "Auditor-owned note."
    assessment.save(update_fields=["observation"])

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(
                    decision="reuse",
                    existing_record_reference=str(assessment.id),
                    payload=None,
                )
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    assessment.refresh_from_db()
    assert assessment.observation == "Auditor-owned note."


# ---- blocked paths -------------------------------------------------------------------


@pytest.mark.django_db
def test_missing_assessment_reference_is_blocked(authenticated_client, grc_context):
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True, assessment_reference=""),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert any(
        error["code"] == "assessment_reference_required"
        for error in body["blocking_errors"]
    )
    assert before == _counts_snapshot()


@pytest.mark.django_db
def test_unknown_assessment_reference_is_blocked(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context, dry_run=False, approved=True, assessment_reference=str(uuid.uuid4())
        ),
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "assessment_not_found" for error in response.json()["blocking_errors"]
    )


@pytest.mark.django_db
def test_locked_audit_is_blocked(authenticated_client, grc_context):
    grc_context["assessment"].is_locked = True
    grc_context["assessment"].save()

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "assessment_locked" for error in response.json()["blocking_errors"]
    )
    assert not ComplianceAssessment.objects.get(id=grc_context["assessment"].id).observation


@pytest.mark.django_db
def test_audit_in_review_is_blocked(authenticated_client, grc_context):
    grc_context["assessment"].status = ComplianceAssessment.Status.IN_REVIEW
    grc_context["assessment"].save()

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "assessment_in_review"
        for error in response.json()["blocking_errors"]
    )


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
            grc_context, dry_run=False, approved=True, folder_reference=str(other_folder.id)
        ),
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "assessment_out_of_scope"
        for error in response.json()["blocking_errors"]
    )


# ---- step isolation ------------------------------------------------------------------


def test_step12b_service_does_not_import_ai_modules():
    """Step 12B is deterministic: it must not reach any provider, LLM, or prompt module."""
    from pathlib import Path

    source = Path(
        __file__
    ).resolve().parents[2] / "ai_onboarding" / "final_review_commit_service.py"
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
