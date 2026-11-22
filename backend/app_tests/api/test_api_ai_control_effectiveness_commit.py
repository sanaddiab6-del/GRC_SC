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
        / f"test_ai_control_effectiveness_commit_{uuid.uuid4().hex}.sqlite3"
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
    """An existing framework, audit, and requirement assessments.

    Step 9B only ever updates rows like these; it never creates them.
    """
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
    mfa_requirement = RequirementNode.objects.create(
        framework=framework,
        folder=root,
        urn=f"urn:test:req-node:mfa:{uuid.uuid4().hex}",
        ref_id="3.3.5-4.e",
        name="Multi-factor authentication for sensitive and critical systems",
        assessable=True,
        order_id=1,
    )
    iam_requirement = RequirementNode.objects.create(
        framework=framework,
        folder=root,
        urn=f"urn:test:req-node:iam:{uuid.uuid4().hex}",
        ref_id="3.3.5-1",
        name="Identity and access management policy",
        assessable=True,
        order_id=2,
    )
    assessment = ComplianceAssessment.objects.create(
        name="Q4 2026 ECC Compliance Assessment",
        folder=folder,
        perimeter=perimeter,
        framework=framework,
    )
    # The platform creates the RequirementAssessment pairings with the audit.
    assessment.create_requirement_assessments()
    mfa_requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=assessment, requirement=mfa_requirement
    )
    iam_requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=assessment, requirement=iam_requirement
    )
    return {
        "folder": folder,
        "framework": framework,
        "assessment": assessment,
        "mfa_requirement": mfa_requirement,
        "iam_requirement": iam_requirement,
        "mfa_requirement_assessment": mfa_requirement_assessment,
        "iam_requirement_assessment": iam_requirement_assessment,
    }


def _suggestion_payload(context, requirement=None, **overrides):
    requirement = requirement or context["mfa_requirement"]
    payload = {
        "temporary_id": "effectiveness_1",
        "framework_control_reference": requirement.urn,
        "framework_control_code": requirement.ref_id,
        "framework_control_title": requirement.name,
        "linked_requirement_assessment_reference": "",
        "linked_applied_control_reference": "CTL-MFA-001",
        "linked_applied_control_title": "Multi-Factor Authentication for Remote Access",
        "linked_finding_reference": "FND-CAND-001",
        "linked_finding_title": "MFA is not documented or not enforced for remote access.",
        "suggested_effectiveness": "partially_effective",
        "suggested_compliance_status": "partially_compliant",
        "evidence_summary": "MFA configuration evidence has been requested but not reviewed.",
        "gaps": ["MFA enforcement for remote access is not evidenced."],
        "recommended_auditor_action": "Collect the MFA configuration export and review it.",
        "rationale": "The control is defined but its supporting evidence is not verified.",
        "confidence": 0.74,
        "review_status": "pending_review",
    }
    payload.update(overrides)
    return payload


def _decision(context, requirement=None, **overrides):
    payload_overrides = overrides.pop("payload_overrides", {})
    decision = {
        "temporary_id": "effectiveness_1",
        "selected": True,
        "decision": "create",
        "existing_record_reference": "",
        "payload": _suggestion_payload(context, requirement, **payload_overrides),
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
        "decisions": decisions if decisions is not None else [_decision(context)],
    }
    payload.update(overrides)
    return payload


def _post(client, payload):
    return client.post(reverse("ai-control-effectiveness-commit"), payload, format="json")


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
    other = RequirementAssessment.objects.get(id=context["iam_requirement_assessment"].id)
    return {
        "audit_status": assessment.status,
        "audit_is_locked": assessment.is_locked,
        "audit_observation": assessment.observation,
        "other_result": other.result,
        "other_status": other.status,
        "other_observation": other.observation,
    }


# ---- contract ------------------------------------------------------------------------


@pytest.mark.django_db
def test_requires_authentication(client, grc_context):
    response = client.post(
        reverse("ai-control-effectiveness-commit"),
        _request_payload(grc_context),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_validates_and_writes_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()
    target_before = RequirementAssessment.objects.get(
        id=grc_context["mfa_requirement_assessment"].id
    )
    result_before, observation_before = target_before.result, target_before.observation

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
    assert body["blocking_errors"] == []
    assert before == after

    target_after = RequirementAssessment.objects.get(
        id=grc_context["mfa_requirement_assessment"].id
    )
    assert target_after.result == result_before
    assert target_after.observation == observation_before


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
        assert body["error_code"] == "ai_control_effectiveness_commit_guardrails_failed"
        assert any(error["field"] == field for error in body["blocking_errors"])


@pytest.mark.django_db
def test_write_intent_and_closure_fields_are_rejected(authenticated_client, grc_context):
    for field in (
        "auto_approve",
        "create_requirement_assessment",
        "create_framework",
        "close_audit",
        "certify_compliance",
        "accept_risk",
        "final_audit_opinion",
        "set_assessment_status",
    ):
        response = _post(authenticated_client, _request_payload(grc_context, **{field: True}))
        assert response.status_code == 422, field
        assert any(
            error["field"] == field for error in response.json()["blocking_errors"]
        )


@pytest.mark.django_db
def test_raw_database_identifier_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, requirement_assessment_id=str(uuid.uuid4())),
    )
    assert response.status_code == 422
    assert any(
        error["code"] == "raw_database_identifier"
        for error in response.json()["blocking_errors"]
    )


@pytest.mark.django_db
def test_invalid_enum_is_rejected(authenticated_client, grc_context):
    for field, value in (
        ("suggested_effectiveness", "mostly_effective"),
        ("suggested_compliance_status", "mostly_compliant"),
    ):
        response = _post(
            authenticated_client,
            _request_payload(
                grc_context, decisions=[_decision(grc_context, payload_overrides={field: value})]
            ),
        )
        assert response.status_code == 400, field
        assert "decisions" in response.json()


@pytest.mark.django_db
def test_invalid_confidence_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context, decisions=[_decision(grc_context, payload_overrides={"confidence": 1.4})]
        ),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


@pytest.mark.django_db
def test_non_pending_review_status_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[_decision(grc_context, payload_overrides={"review_status": "approved"})],
        ),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


@pytest.mark.django_db
def test_duplicate_temporary_id_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, decisions=[_decision(grc_context), _decision(grc_context)]),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


# ---- decisions -----------------------------------------------------------------------


@pytest.mark.django_db
def test_reject_and_defer_write_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()
    state_before = _assessment_state(grc_context)
    target_before = RequirementAssessment.objects.get(
        id=grc_context["mfa_requirement_assessment"].id
    ).result

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(grc_context, temporary_id="effectiveness_1", decision="reject"),
                _decision(grc_context, temporary_id="effectiveness_2", decision="defer"),
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
        RequirementAssessment.objects.get(
            id=grc_context["mfa_requirement_assessment"].id
        ).result
        == target_before
    )


@pytest.mark.django_db
def test_unselected_decision_is_skipped_without_write(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[_decision(grc_context, selected=False)],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert body["skipped_records"][0]["skip_reason"] == "not_selected"
    assert (
        RequirementAssessment.objects.get(
            id=grc_context["mfa_requirement_assessment"].id
        ).result
        == RequirementAssessment.Result.NOT_ASSESSED
    )


# ---- approved write ------------------------------------------------------------------


@pytest.mark.django_db
def test_approved_commit_updates_only_result_and_observation(
    authenticated_client, grc_context
):
    before = _counts_snapshot()
    state_before = _assessment_state(grc_context)
    target = RequirementAssessment.objects.get(id=grc_context["mfa_requirement_assessment"].id)
    status_before, score_before, selected_before = (
        target.status,
        target.score,
        target.selected,
    )

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is False
    assert body["commit_status"] in {"created", "completed_with_warnings"}
    assert len(body["created_records"]) == 1
    record = body["created_records"][0]
    assert record["record_type"] == "requirement_assessment"
    assert record["action"] == "update"
    assert sorted(record["updated_fields"]) == ["observation", "result"]
    assert record["audit_status_changed"] is False

    target.refresh_from_db()
    assert target.result == RequirementAssessment.Result.PARTIALLY_COMPLIANT
    assert "[AI onboarding Step 9B" in target.observation
    assert "partially_effective" in target.observation
    # Every other field of the row is untouched.
    assert target.status == status_before
    assert target.score == score_before
    assert target.selected == selected_before
    assert list(target.applied_controls.all()) == []
    assert list(target.evidences.all()) == []
    # No record was created anywhere, and the audit itself is untouched.
    assert before == _counts_snapshot()
    assert state_before == _assessment_state(grc_context)


@pytest.mark.django_db
def test_needs_more_evidence_writes_no_result_but_keeps_observation(
    authenticated_client, grc_context
):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(
                    grc_context,
                    payload_overrides={
                        "suggested_compliance_status": "needs_more_evidence",
                        "suggested_effectiveness": "needs_more_evidence",
                    },
                )
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert any(
        warning["code"] == "compliance_status_not_persistable"
        for warning in body["warnings"]
    )
    target = RequirementAssessment.objects.get(id=grc_context["mfa_requirement_assessment"].id)
    assert target.result == RequirementAssessment.Result.NOT_ASSESSED
    assert "needs_more_evidence" in target.observation


@pytest.mark.django_db
def test_existing_observation_is_appended_not_overwritten(authenticated_client, grc_context):
    target = RequirementAssessment.objects.get(id=grc_context["mfa_requirement_assessment"].id)
    target.observation = "Auditor-owned note that must survive."
    target.save(update_fields=["observation"])

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 200
    assert any(
        warning["code"] == "observation_appended" for warning in response.json()["warnings"]
    )
    target.refresh_from_db()
    assert target.observation.startswith("Auditor-owned note that must survive.")
    assert "[AI onboarding Step 9B" in target.observation


@pytest.mark.django_db
def test_existing_result_replacement_is_warned(authenticated_client, grc_context):
    target = RequirementAssessment.objects.get(id=grc_context["mfa_requirement_assessment"].id)
    target.result = RequirementAssessment.Result.COMPLIANT
    target.save(update_fields=["result"])

    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 200
    assert any(
        warning["code"] == "existing_result_replaced"
        for warning in response.json()["warnings"]
    )
    target.refresh_from_db()
    assert target.result == RequirementAssessment.Result.PARTIALLY_COMPLIANT


@pytest.mark.django_db
def test_rerunning_the_same_judgement_changes_nothing(authenticated_client, grc_context):
    first = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )
    assert first.status_code == 200
    target = RequirementAssessment.objects.get(id=grc_context["mfa_requirement_assessment"].id)
    observation_after_first = target.observation

    second = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert second.status_code == 200
    body = second.json()
    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    target.refresh_from_db()
    assert target.observation == observation_after_first


@pytest.mark.django_db
def test_duplicate_target_in_batch_is_skipped(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(grc_context),
                _decision(grc_context, temporary_id="effectiveness_2"),
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["created_records"]) == 1
    assert any(
        record["skip_reason"] == "duplicate_in_batch" for record in body["skipped_records"]
    )


@pytest.mark.django_db
def test_reuse_decision_does_not_mutate_requirement_assessment(
    authenticated_client, grc_context
):
    target = RequirementAssessment.objects.get(id=grc_context["mfa_requirement_assessment"].id)
    target.observation = "Auditor-owned note."
    target.save(update_fields=["observation"])

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(
                    grc_context,
                    decision="reuse",
                    existing_record_reference=str(target.id),
                    payload=None,
                )
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    target.refresh_from_db()
    assert target.observation == "Auditor-owned note."
    assert target.result == RequirementAssessment.Result.NOT_ASSESSED


# ---- blocked paths -------------------------------------------------------------------


@pytest.mark.django_db
def test_unknown_framework_control_is_blocked_and_creates_nothing(
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
                    grc_context,
                    payload_overrides={
                        "framework_control_reference": "urn:not:in:database",
                        "framework_control_code": "9.9.9",
                    },
                )
            ],
        ),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert any(
        error["code"] == "requirement_assessment_not_found"
        for error in body["blocking_errors"]
    )
    assert before == _counts_snapshot()


@pytest.mark.django_db
def test_missing_assessment_reference_is_blocked(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True, assessment_reference=""),
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "assessment_reference_required"
        for error in response.json()["blocking_errors"]
    )


@pytest.mark.django_db
def test_locked_audit_is_blocked(authenticated_client, grc_context):
    grc_context["assessment"].is_locked = True
    grc_context["assessment"].save()

    state_before = _assessment_state(grc_context)
    response = _post(
        authenticated_client, _request_payload(grc_context, dry_run=False, approved=True)
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "assessment_locked" for error in response.json()["blocking_errors"]
    )
    assert (
        RequirementAssessment.objects.get(
            id=grc_context["mfa_requirement_assessment"].id
        ).result
        == RequirementAssessment.Result.NOT_ASSESSED
    )
    assert state_before == _assessment_state(grc_context)


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
def test_requirement_assessment_outside_audit_is_blocked(authenticated_client, grc_context):
    other_assessment = ComplianceAssessment.objects.create(
        name="Unrelated audit",
        folder=grc_context["folder"],
        perimeter=None,
        framework=grc_context["framework"],
    )
    other_assessment.create_requirement_assessments()
    foreign = RequirementAssessment.objects.filter(
        compliance_assessment=other_assessment
    ).first()

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(
                    grc_context,
                    payload_overrides={
                        "linked_requirement_assessment_reference": str(foreign.id)
                    },
                )
            ],
        ),
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "requirement_assessment_out_of_scope"
        for error in response.json()["blocking_errors"]
    )


# ---- step isolation ------------------------------------------------------------------


def test_step9b_service_does_not_import_ai_modules():
    """Step 9B is deterministic: it must not reach any provider, LLM, or prompt module."""
    from pathlib import Path

    source = Path(
        __file__
    ).resolve().parents[2] / "ai_onboarding" / "control_effectiveness_commit_service.py"
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
