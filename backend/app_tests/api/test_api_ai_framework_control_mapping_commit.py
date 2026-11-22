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
        / f"test_ai_framework_control_mapping_commit_{uuid.uuid4().hex}.sqlite3"
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
    """An existing framework, audit, requirement nodes, and applied control.

    Step 7B only ever maps onto records like these; it never creates them.
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
    applied_control = AppliedControl.objects.create(
        name="Multi-Factor Authentication for Remote Access",
        ref_id="CTL-MFA-001",
        folder=folder,
    )
    return {
        "folder": folder,
        "framework": framework,
        "assessment": assessment,
        "mfa_requirement": mfa_requirement,
        "iam_requirement": iam_requirement,
        "applied_control": applied_control,
    }


def _mapping_payload(context, requirement=None, **overrides):
    requirement = requirement or context["mfa_requirement"]
    payload = {
        "temporary_id": "framework_mapping_1",
        "framework_control_reference": requirement.urn,
        "framework_control_code": requirement.ref_id,
        "framework_control_title": requirement.name,
        "framework_control_description": "",
        "framework_name": context["framework"].name,
        "mapping_type": "supports_finding",
        "linked_finding_reference": "FND-CAND-001",
        "linked_finding_title": "MFA is not documented or not enforced for remote access.",
        "linked_applied_control_reference": "CTL-MFA-001",
        "linked_applied_control_title": "Multi-Factor Authentication for Remote Access",
        "linked_remediation_action_reference": "",
        "linked_remediation_action_title": "",
        "rationale": "The finding relates to the existing multi-factor authentication requirement.",
        "evidence_needed": ["MFA policy", "MFA configuration evidence"],
        "confidence": 0.88,
        "review_status": "pending_review",
    }
    payload.update(overrides)
    return payload


def _decision(context, requirement=None, **overrides):
    payload_overrides = overrides.pop("payload_overrides", {})
    decision = {
        "temporary_id": "framework_mapping_1",
        "selected": True,
        "decision": "create",
        "existing_record_reference": "",
        "payload": _mapping_payload(context, requirement, **payload_overrides),
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
        "framework_reference": str(context["framework"].id),
        "decisions": decisions if decisions is not None else [_decision(context)],
    }
    payload.update(overrides)
    return payload


def _post(client, payload):
    return client.post(
        reverse("ai-framework-control-mapping-commit"),
        payload,
        format="json",
    )


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


def _mapping_link_count(context):
    return (
        RequirementAssessment.objects.filter(compliance_assessment=context["assessment"])
        .filter(applied_controls__isnull=False)
        .count()
    )


# ---- contract ------------------------------------------------------------------------


@pytest.mark.django_db
def test_requires_authentication(client, grc_context):
    response = client.post(
        reverse("ai-framework-control-mapping-commit"),
        _request_payload(grc_context),
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_validates_and_writes_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()
    links_before = _mapping_link_count(grc_context)

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
    assert _mapping_link_count(grc_context) == links_before


@pytest.mark.django_db
def test_approved_false_with_dry_run_false_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=False),
    )
    assert response.status_code == 400
    assert "approved" in response.json()


@pytest.mark.django_db
def test_approved_true_with_dry_run_true_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=True, approved=True),
    )
    assert response.status_code == 400
    assert "approved" in response.json()


@pytest.mark.django_db
def test_ai_and_provider_fields_are_rejected(authenticated_client, grc_context):
    for field in ("use_ai", "ai_provider", "provider_mode", "llm", "model", "prompt",
                 "system_prompt", "temperature"):
        response = _post(
            authenticated_client, _request_payload(grc_context, **{field: "x"})
        )
        assert response.status_code == 422, field
        body = response.json()
        assert body["error_code"] == "ai_framework_control_mapping_commit_guardrails_failed"
        assert any(error["field"] == field for error in body["blocking_errors"])


@pytest.mark.django_db
def test_write_intent_fields_are_rejected(authenticated_client, grc_context):
    for field in (
        "create_framework",
        "create_requirement",
        "create_control",
        "create_reference_control",
        "create_framework_control",
        "approve_mapping",
        "auto_approve",
        "close_audit",
        "accept_risk",
    ):
        response = _post(
            authenticated_client, _request_payload(grc_context, **{field: True})
        )
        assert response.status_code == 422, field
        assert any(
            error["field"] == field for error in response.json()["blocking_errors"]
        )


@pytest.mark.django_db
def test_raw_database_identifiers_are_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, compliance_assessment_id=str(uuid.uuid4())),
    )
    assert response.status_code == 422
    body = response.json()
    assert any(
        error["code"] == "raw_database_identifier" for error in body["blocking_errors"]
    )


@pytest.mark.django_db
def test_temporary_id_is_not_treated_as_a_raw_identifier(authenticated_client, grc_context):
    response = _post(authenticated_client, _request_payload(grc_context))
    assert response.status_code == 200


@pytest.mark.django_db
def test_invalid_mapping_type_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[_decision(grc_context, payload_overrides={"mapping_type": "satisfies"})],
        ),
    )
    assert response.status_code == 400
    assert "mapping_type" in str(response.json())


@pytest.mark.django_db
def test_invalid_confidence_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[_decision(grc_context, payload_overrides={"confidence": 1.7})],
        ),
    )
    assert response.status_code == 400
    assert "confidence" in str(response.json())


@pytest.mark.django_db
def test_review_status_must_be_pending_review(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[_decision(grc_context, payload_overrides={"review_status": "approved"})],
        ),
    )
    assert response.status_code == 400
    assert "review_status" in str(response.json())


@pytest.mark.django_db
def test_evidence_needed_must_be_a_list(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[
                _decision(grc_context, payload_overrides={"evidence_needed": "MFA policy"})
            ],
        ),
    )
    assert response.status_code == 400
    assert "evidence_needed" in str(response.json())


@pytest.mark.django_db
def test_duplicate_temporary_id_is_rejected(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[_decision(grc_context), _decision(grc_context)],
        ),
    )
    assert response.status_code == 400
    assert "decisions" in response.json()


# ---- decision semantics --------------------------------------------------------------


@pytest.mark.django_db
def test_reject_decision_writes_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()
    links_before = _mapping_link_count(grc_context)

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[_decision(grc_context, decision="reject")],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["rejected_records"]) == 1
    assert body["rejected_records"][0]["source_temporary_id"] == "framework_mapping_1"
    assert body["created_records"] == []
    assert _counts_snapshot() == before
    assert _mapping_link_count(grc_context) == links_before


@pytest.mark.django_db
def test_defer_decision_writes_nothing(authenticated_client, grc_context):
    before = _counts_snapshot()
    links_before = _mapping_link_count(grc_context)

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            dry_run=False,
            approved=True,
            decisions=[_decision(grc_context, decision="defer")],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["deferred_records"]) == 1
    assert body["created_records"] == []
    assert _counts_snapshot() == before
    assert _mapping_link_count(grc_context) == links_before


@pytest.mark.django_db
def test_unselected_decision_is_skipped(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, decisions=[_decision(grc_context, selected=False)]),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["skipped_records"]) == 1
    assert body["skipped_records"][0]["skip_reason"] == "not_selected"


# ---- persistence ---------------------------------------------------------------------


@pytest.mark.django_db
def test_approved_commit_maps_existing_requirement_assessment_to_applied_control(
    authenticated_client, grc_context
):
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is False
    assert body["commit_status"] in {"completed", "completed_with_warnings", "reused_only"}
    assert body["blocking_errors"] == []
    # The platform already created the RequirementAssessment with the audit, so Step 7B
    # reuses it and only adds the applied control link.
    assert len(body["reused_records"]) == 1
    record = body["reused_records"][0]
    assert record["record_type"] == "requirement_assessment"
    assert record["applied_control_link_added"] is True
    assert body["created_records"] == []

    requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=grc_context["assessment"],
        requirement=grc_context["mfa_requirement"],
    )
    assert list(requirement_assessment.applied_controls.all()) == [
        grc_context["applied_control"]
    ]
    # No new domain records were created anywhere.
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_rerunning_the_commit_reuses_the_mapping_without_duplicating(
    authenticated_client, grc_context
):
    payload = _request_payload(grc_context, dry_run=False, approved=True)

    first = _post(authenticated_client, payload)
    assert first.status_code == 200
    after_first = _counts_snapshot()

    second = _post(authenticated_client, payload)
    assert second.status_code == 200
    body = second.json()

    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    assert body["reused_records"][0]["applied_control_link_added"] is False
    assert any(
        warning["code"] == "mapping_already_exists" for warning in body["warnings"]
    )

    requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=grc_context["assessment"],
        requirement=grc_context["mfa_requirement"],
    )
    assert requirement_assessment.applied_controls.count() == 1
    assert _counts_snapshot() == after_first


@pytest.mark.django_db
def test_missing_applied_control_link_is_warned_not_created(
    authenticated_client, grc_context
):
    before_controls = AppliedControl.objects.count()

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
                        "linked_applied_control_reference": "CTL-DOES-NOT-EXIST",
                        "linked_applied_control_title": "Missing control",
                    },
                )
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert any(
        warning["code"] == "applied_control_linkage_not_applied"
        for warning in body["warnings"]
    )
    assert len(body["reused_records"]) == 1
    assert body["reused_records"][0]["applied_control_link_added"] is False
    # Step 7B never creates an AppliedControl to satisfy a link.
    assert AppliedControl.objects.count() == before_controls


@pytest.mark.django_db
def test_reuse_decision_does_not_mutate_the_existing_mapping(
    authenticated_client, grc_context
):
    requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=grc_context["assessment"],
        requirement=grc_context["mfa_requirement"],
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
                    grc_context,
                    decision="reuse",
                    existing_record_reference=str(requirement_assessment.id),
                    payload=None,
                )
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["reused_records"]) == 1
    assert body["created_records"] == []
    requirement_assessment.refresh_from_db()
    assert requirement_assessment.applied_controls.count() == 0
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_csv_only_framework_control_is_not_persisted(authenticated_client, grc_context):
    """A candidate that exists only in the CSV export must never be created in the DB."""
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(
            grc_context,
            decisions=[
                _decision(
                    grc_context,
                    payload_overrides={
                        "framework_control_reference": (
                            "urn:intuitem:risk:req_node:sama-csf-1.0:3.3.13-4.b"
                        ),
                        "framework_control_code": "3.3.13-4.b",
                        "framework_control_title": "SAMA control 3.3.13-4.b",
                    },
                )
            ],
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert any(
        error["code"] == "framework_control_not_in_database"
        for error in body["blocking_errors"]
    )
    assert any(
        record["skip_reason"] == "framework_control_not_in_database"
        for record in body["skipped_records"]
    )
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_approved_commit_with_csv_only_control_is_blocked_without_writes(
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
                        "framework_control_reference": "urn:not:loaded:9.9.9",
                        "framework_control_code": "9.9.9",
                    },
                )
            ],
        ),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert body["created_records"] == []
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_missing_assessment_reference_is_blocked(authenticated_client, grc_context):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, assessment_reference="", framework_reference=""),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert any(
        error["code"] == "assessment_reference_required"
        for error in body["blocking_errors"]
    )


@pytest.mark.django_db
def test_framework_reference_mismatch_is_blocked(authenticated_client, grc_context):
    other_framework = Framework.objects.create(
        name="Other framework",
        folder=Folder.get_root_folder(),
        urn=f"urn:test:framework:{uuid.uuid4().hex}",
    )

    response = _post(
        authenticated_client,
        _request_payload(grc_context, framework_reference=str(other_framework.id)),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert any(error["code"] == "framework_mismatch" for error in body["blocking_errors"])


@pytest.mark.django_db
def test_locked_assessment_is_blocked(authenticated_client, grc_context):
    grc_context["assessment"].is_locked = True
    grc_context["assessment"].save()
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True),
    )

    assert response.status_code == 422
    assert any(
        error["code"] == "assessment_locked"
        for error in response.json()["blocking_errors"]
    )
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_duplicate_mapping_within_batch_is_skipped(authenticated_client, grc_context):
    decisions = [
        _decision(grc_context, temporary_id="framework_mapping_1"),
        _decision(grc_context, temporary_id="framework_mapping_2"),
    ]

    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True, decisions=decisions),
    )

    assert response.status_code == 200
    body = response.json()
    assert any(
        record["skip_reason"] == "duplicate_in_batch" for record in body["skipped_records"]
    )
    requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=grc_context["assessment"],
        requirement=grc_context["mfa_requirement"],
    )
    assert requirement_assessment.applied_controls.count() == 1


@pytest.mark.django_db
def test_approved_commit_makes_no_hidden_mutations(authenticated_client, grc_context):
    """Only RequirementAssessment.applied_controls may change."""
    framework = grc_context["framework"]
    requirement = grc_context["mfa_requirement"]
    applied_control = grc_context["applied_control"]
    assessment = grc_context["assessment"]
    requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=assessment, requirement=requirement
    )

    snapshot = {
        "framework_name": framework.name,
        "requirement_name": requirement.name,
        "requirement_description": requirement.description,
        "applied_control_name": applied_control.name,
        "applied_control_status": applied_control.status,
        "assessment_status": assessment.status,
        "ra_result": requirement_assessment.result,
        "ra_status": requirement_assessment.status,
        "ra_score": requirement_assessment.score,
        "ra_observation": requirement_assessment.observation,
        "ra_mapping_inference": requirement_assessment.mapping_inference,
        "ra_evidence_count": requirement_assessment.evidences.count(),
    }
    before = _counts_snapshot()

    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True),
    )
    assert response.status_code == 200

    framework.refresh_from_db()
    requirement.refresh_from_db()
    applied_control.refresh_from_db()
    assessment.refresh_from_db()
    requirement_assessment.refresh_from_db()

    assert framework.name == snapshot["framework_name"]
    assert requirement.name == snapshot["requirement_name"]
    assert requirement.description == snapshot["requirement_description"]
    assert applied_control.name == snapshot["applied_control_name"]
    assert applied_control.status == snapshot["applied_control_status"]
    assert assessment.status == snapshot["assessment_status"]
    # No compliance decision is made by Step 7B.
    assert requirement_assessment.result == snapshot["ra_result"]
    assert requirement_assessment.status == snapshot["ra_status"]
    assert requirement_assessment.score == snapshot["ra_score"]
    assert requirement_assessment.observation == snapshot["ra_observation"]
    assert requirement_assessment.mapping_inference == snapshot["ra_mapping_inference"]
    assert requirement_assessment.evidences.count() == snapshot["ra_evidence_count"]
    # Only the applied-control link changed; no record counts moved.
    assert requirement_assessment.applied_controls.count() == 1
    assert _counts_snapshot() == before


@pytest.mark.django_db
def test_advisory_context_is_not_persisted_and_is_reported(
    authenticated_client, grc_context
):
    response = _post(
        authenticated_client,
        _request_payload(grc_context, dry_run=False, approved=True),
    )

    assert response.status_code == 200
    body = response.json()
    assert any(
        warning["code"] == "advisory_mapping_context_not_persisted"
        for warning in body["warnings"]
    )
    requirement_assessment = RequirementAssessment.objects.get(
        compliance_assessment=grc_context["assessment"],
        requirement=grc_context["mfa_requirement"],
    )
    assert not requirement_assessment.observation


# ---- no AI in Step 7B ----------------------------------------------------------------


def test_step7b_modules_do_not_import_any_provider_or_llm_module():
    import ast
    from pathlib import Path

    module_dir = Path(__file__).resolve().parents[2] / "ai_onboarding"
    forbidden_markers = ("llm", "provider", "prompt", "ollama")

    for filename in (
        "framework_control_mapping_commit_service.py",
        "framework_control_mapping_commit_serializers.py",
        "framework_control_mapping_commit_guardrails.py",
    ):
        source = (module_dir / filename).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
                imported.extend(alias.name for alias in node.names)

        for name in imported:
            lowered = name.lower()
            assert not any(marker in lowered for marker in forbidden_markers), (
                f"{filename} imports '{name}', which looks like AI/provider code"
            )
