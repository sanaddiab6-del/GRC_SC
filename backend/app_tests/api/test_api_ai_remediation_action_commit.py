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
    FindingsAssessment,
    Framework,
    Perimeter,
    RequirementAssessment,
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
        / f"test_ai_remediation_action_commit_{uuid.uuid4().hex}.sqlite3"
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
    monkeypatch.delenv("LOCAL_AI_MODEL_REMEDIATION_ACTION_SUGGESTION", raising=False)


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
def setup_context():
    folder = Folder.objects.create(
        name=f"AI Step 6B Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    perimeter = Perimeter.objects.create(
        folder=folder,
        name=f"AI Step 6B Perimeter {uuid.uuid4().hex[:8]}",
        ref_id=f"PER-STEP6B-{uuid.uuid4().hex[:8]}",
        description="Step 6B remediation action commit scope perimeter",
        lc_status="in_prod",
    )
    asset = Asset.objects.create(
        folder=folder,
        name="Core Banking Platform",
        type=Asset.Type.PRIMARY,
        ref_id=f"AST-CBP-{uuid.uuid4().hex[:6].upper()}",
        description="Primary core banking platform.",
    )
    findings_assessment = FindingsAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        name=f"AI Step 6B Findings Assessment {uuid.uuid4().hex[:8]}",
        category=FindingsAssessment.Category.AUDIT,
        status="planned",
    )
    finding = Finding.objects.create(
        findings_assessment=findings_assessment,
        folder=folder,
        name="MFA is not documented or not enforced for remote access.",
        ref_id="FND-MFA-001",
        status=Finding.Status.IDENTIFIED,
    )

    return {
        "folder": folder,
        "perimeter": perimeter,
        "asset": asset,
        "findings_assessment": findings_assessment,
        "finding": finding,
    }


def _action_payload(**overrides):
    payload = {
        "temporary_id": "remediation_action_1",
        "title": "Implement and enforce MFA for remote access",
        "description": (
            "Enable and enforce multi-factor authentication for all remote access users "
            "of the Core Banking Platform."
        ),
        "linked_finding_reference": "FND-MFA-001",
        "linked_finding_title": "MFA is not documented or not enforced for remote access.",
        "linked_asset_reference": "",
        "linked_asset_title": "Core Banking Platform",
        "linked_control_reference": "",
        "linked_control_title": "",
        "priority": "high",
        "suggested_owner": "IAM / Security Operations",
        "target_timeline": "30-60 days",
        "success_criteria": ["All remote access users authenticate using MFA."],
        "required_follow_up_evidence": ["MFA policy"],
        "rationale": "The finding indicates MFA enforcement is not sufficiently evidenced.",
        "confidence": 0.85,
        "review_status": "pending_review",
    }
    payload.update(overrides)
    return payload


def _decision(**overrides):
    decision = {
        "temporary_id": "remediation_action_1",
        "selected": True,
        "decision": "create",
        "existing_record_reference": "",
        "payload": _action_payload(),
    }
    decision.update(overrides)
    return decision


def _request_payload(setup_context, *, dry_run=True, approved=False, decisions=None):
    return {
        "dry_run": dry_run,
        "approved": approved,
        "folder_reference": str(setup_context["folder"].id),
        "decisions": decisions if decisions is not None else [_decision()],
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
        "FindingsAssessment": FindingsAssessment.objects.count(),
        "Framework": Framework.objects.count(),
        "RiskAcceptance": RiskAcceptance.objects.count(),
    }


def _post(client, payload):
    return client.post(
        reverse("ai-remediation-action-commit"),
        payload,
        format="json",
    )


# --- 1. dry-run validates and returns planned_actions without writes ---------


@pytest.mark.django_db
def test_dry_run_returns_planned_actions_without_writes(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = _post(authenticated_client, _request_payload(setup_context))
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
    assert body["planned_actions"][0]["decision"] == "create"
    assert body["planned_actions"][0]["status"] == "planned"
    assert body["planned_actions"][0]["record_type"] == "applied_control"
    assert body["created_records"] == []
    assert body["reused_records"] == []
    assert body["blocking_errors"] == []
    assert before == after


# --- 13. dry-run preserves database counts ----------------------------------


@pytest.mark.django_db
def test_dry_run_preserves_database_counts_for_all_decision_types(
    authenticated_client, setup_context
):
    decisions = [
        _decision(),
        _decision(
            temporary_id="remediation_action_2",
            decision="reject",
            payload=_action_payload(temporary_id="remediation_action_2", title="Rejected action"),
        ),
        _decision(
            temporary_id="remediation_action_3",
            decision="defer",
            payload=_action_payload(temporary_id="remediation_action_3", title="Deferred action"),
        ),
        _decision(
            temporary_id="remediation_action_4",
            selected=False,
            payload=_action_payload(temporary_id="remediation_action_4", title="Unselected action"),
        ),
    ]

    before = _counts_snapshot()
    response = _post(
        authenticated_client, _request_payload(setup_context, decisions=decisions)
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert before == after
    assert [item["source_temporary_id"] for item in body["rejected_records"]] == [
        "remediation_action_2"
    ]
    assert [item["source_temporary_id"] for item in body["deferred_records"]] == [
        "remediation_action_3"
    ]
    assert [item["source_temporary_id"] for item in body["skipped_records"]] == [
        "remediation_action_4"
    ]


# --- 2. approved commit requires approved=true ------------------------------


@pytest.mark.django_db
def test_commit_requires_approved_true(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = _post(
        authenticated_client,
        _request_payload(setup_context, dry_run=False, approved=False),
    )
    after = _counts_snapshot()

    assert response.status_code == 400
    assert "approved" in response.json()
    assert before == after


@pytest.mark.django_db
def test_dry_run_rejects_approved_true(authenticated_client, setup_context):
    response = _post(
        authenticated_client,
        _request_payload(setup_context, dry_run=True, approved=True),
    )

    assert response.status_code == 400
    assert "approved" in response.json()


# --- 3. Step 6B does not call AI / provider ---------------------------------


@pytest.mark.django_db
def test_commit_does_not_call_ai_provider(authenticated_client, setup_context, monkeypatch):
    def _explode(*args, **kwargs):
        raise AssertionError("Step 6B must not call any AI provider.")

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _explode)
    monkeypatch.setattr(
        "ai_onboarding.remediation_action_suggestion_provider."
        "get_remediation_action_suggestion_provider",
        _explode,
    )
    monkeypatch.setattr(
        "ai_onboarding.remediation_action_suggestion_service."
        "get_remediation_action_suggestion_provider",
        _explode,
    )

    dry_run = _post(authenticated_client, _request_payload(setup_context))
    commit = _post(
        authenticated_client,
        _request_payload(setup_context, dry_run=False, approved=True),
    )

    assert dry_run.status_code == 200
    assert commit.status_code == 200
    assert commit.json()["created_records"]


@pytest.mark.django_db
def test_ai_fields_are_rejected_by_guardrails(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["use_ai"] = True

    response = _post(authenticated_client, payload)

    assert response.status_code == 400
    assert "use_ai" in response.json()


# --- 4. invalid decision enum is rejected -----------------------------------


@pytest.mark.django_db
def test_invalid_decision_enum_is_rejected(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = _post(
        authenticated_client,
        _request_payload(setup_context, decisions=[_decision(decision="delete")]),
    )
    after = _counts_snapshot()

    assert response.status_code == 400
    assert "decision" in response.json()["decisions"][0]
    assert before == after


# --- 5. selected create requires payload ------------------------------------


@pytest.mark.django_db
def test_selected_create_requires_payload(authenticated_client, setup_context):
    response = _post(
        authenticated_client,
        _request_payload(setup_context, decisions=[_decision(payload=None)]),
    )

    assert response.status_code == 400
    assert "payload" in response.json()["decisions"][0]


@pytest.mark.django_db
def test_selected_reuse_requires_existing_record_reference(
    authenticated_client, setup_context
):
    response = _post(
        authenticated_client,
        _request_payload(
            setup_context,
            decisions=[_decision(decision="reuse", existing_record_reference="")],
        ),
    )

    assert response.status_code == 400
    assert "existing_record_reference" in response.json()["decisions"][0]


# --- 6. invalid priority is rejected ----------------------------------------


@pytest.mark.django_db
def test_invalid_priority_is_rejected(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = _post(
        authenticated_client,
        _request_payload(
            setup_context,
            decisions=[_decision(payload=_action_payload(priority="urgent"))],
        ),
    )
    after = _counts_snapshot()

    assert response.status_code == 400
    assert "priority" in response.json()["decisions"][0]["payload"]
    assert before == after


# --- 7. invalid confidence is rejected --------------------------------------


@pytest.mark.django_db
def test_invalid_confidence_is_rejected(authenticated_client, setup_context):
    response = _post(
        authenticated_client,
        _request_payload(
            setup_context,
            decisions=[_decision(payload=_action_payload(confidence=1.7))],
        ),
    )

    assert response.status_code == 400
    assert "confidence" in response.json()["decisions"][0]["payload"]


@pytest.mark.django_db
def test_non_pending_review_status_is_rejected(authenticated_client, setup_context):
    response = _post(
        authenticated_client,
        _request_payload(
            setup_context,
            decisions=[_decision(payload=_action_payload(review_status="approved"))],
        ),
    )

    assert response.status_code == 400
    assert "review_status" in response.json()["decisions"][0]["payload"]


# --- 8. duplicate existing record is reused safely --------------------------


@pytest.mark.django_db
def test_duplicate_existing_applied_control_is_reused(authenticated_client, setup_context):
    existing = AppliedControl.objects.create(
        folder=setup_context["folder"],
        name="Implement and enforce MFA for remote access",
        description="Pre-existing remediation action.",
        status=AppliedControl.Status.IN_PROGRESS,
    )

    dry_run = _post(authenticated_client, _request_payload(setup_context))
    assert dry_run.status_code == 200
    dry_body = dry_run.json()
    assert dry_body["planned_actions"][0]["decision"] == "reuse"
    assert any(warning["code"] == "duplicate_reused" for warning in dry_body["warnings"])

    before = AppliedControl.objects.count()
    commit = _post(
        authenticated_client,
        _request_payload(setup_context, dry_run=False, approved=True),
    )
    after = AppliedControl.objects.count()

    assert commit.status_code == 200
    body = commit.json()
    assert body["created_records"] == []
    assert len(body["reused_records"]) == 1
    assert body["reused_records"][0]["record_id"] == str(existing.id)
    assert before == after


# --- 9. reuse does not mutate existing records ------------------------------


@pytest.mark.django_db
def test_reuse_does_not_mutate_existing_record(authenticated_client, setup_context):
    existing = AppliedControl.objects.create(
        folder=setup_context["folder"],
        name="Existing MFA remediation",
        description="Original description that must not change.",
        status=AppliedControl.Status.IN_PROGRESS,
        priority=4,
    )
    snapshot = {
        "name": existing.name,
        "description": existing.description,
        "status": existing.status,
        "priority": existing.priority,
        "updated_at": existing.updated_at,
        "finding_ids": set(existing.findings.values_list("id", flat=True)),
        "asset_ids": set(existing.assets.values_list("id", flat=True)),
    }

    response = _post(
        authenticated_client,
        _request_payload(
            setup_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(decision="reuse", existing_record_reference=str(existing.id))
            ],
        ),
    )

    assert response.status_code == 200
    assert response.json()["reused_records"][0]["record_id"] == str(existing.id)

    existing.refresh_from_db()
    assert existing.name == snapshot["name"]
    assert existing.description == snapshot["description"]
    assert existing.status == snapshot["status"]
    assert existing.priority == snapshot["priority"]
    assert existing.updated_at == snapshot["updated_at"]
    assert set(existing.findings.values_list("id", flat=True)) == snapshot["finding_ids"]
    assert set(existing.assets.values_list("id", flat=True)) == snapshot["asset_ids"]


# --- 10. approved commit creates record in the discovered model -------------


@pytest.mark.django_db
def test_approved_commit_creates_applied_control(authenticated_client, setup_context):
    before = _counts_snapshot()
    response = _post(
        authenticated_client,
        _request_payload(setup_context, dry_run=False, approved=True),
    )
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["dry_run"] is False
    assert body["commit_status"] in {"created", "completed_with_warnings"}
    assert len(body["created_records"]) == 1
    record = body["created_records"][0]
    assert record["record_type"] == "applied_control"
    assert record["source_temporary_id"] == "remediation_action_1"

    created = AppliedControl.objects.get(id=record["record_id"])
    assert created.name == "Implement and enforce MFA for remote access"
    assert created.folder_id == setup_context["folder"].id
    assert created.status == AppliedControl.Status.TO_DO
    assert created.priority == 2  # high -> P2
    # Advisory-only fields have no AppliedControl column and are preserved as text.
    assert "IAM / Security Operations" in created.description
    assert "30-60 days" in created.description
    assert any(
        warning["code"] == "advisory_fields_preserved_as_text" for warning in body["warnings"]
    )

    # Only the AppliedControl count changed.
    expected = dict(before)
    expected["AppliedControl"] = before["AppliedControl"] + 1
    assert after == expected


# --- 11. folder/finding linkage applied where safely supported --------------


@pytest.mark.django_db
def test_finding_and_asset_linkage_is_applied(authenticated_client, setup_context):
    finding = setup_context["finding"]
    asset = setup_context["asset"]
    finding_updated_at = finding.updated_at

    response = _post(
        authenticated_client,
        _request_payload(setup_context, dry_run=False, approved=True),
    )

    assert response.status_code == 200
    record = response.json()["created_records"][0]
    created = AppliedControl.objects.get(id=record["record_id"])

    assert created.folder_id == setup_context["folder"].id
    assert list(created.findings.values_list("id", flat=True)) == [finding.id]
    assert list(created.assets.values_list("id", flat=True)) == [asset.id]
    assert record["linked_finding_ids"] == [str(finding.id)]
    assert record["linked_asset_ids"] == [str(asset.id)]

    # The linkage is an additive m2m row; the Finding's own fields are untouched.
    finding.refresh_from_db()
    assert finding.updated_at == finding_updated_at
    assert finding.name == "MFA is not documented or not enforced for remote access."
    assert finding.status == Finding.Status.IDENTIFIED


@pytest.mark.django_db
def test_unresolvable_linkage_warns_instead_of_inventing(authenticated_client, setup_context):
    payload = _action_payload(
        linked_finding_reference="FND-DOES-NOT-EXIST",
        linked_finding_title="",
        linked_asset_reference="AST-DOES-NOT-EXIST",
        linked_asset_title="",
        linked_control_reference="CTL-MFA-001",
        linked_control_title="Multi-Factor Authentication for Remote Access",
    )

    response = _post(
        authenticated_client,
        _request_payload(
            setup_context, dry_run=False, approved=True, decisions=[_decision(payload=payload)]
        ),
    )

    assert response.status_code == 200
    body = response.json()
    codes = {warning["code"] for warning in body["warnings"]}
    assert "finding_linkage_not_applied" in codes
    assert "asset_linkage_not_applied" in codes
    assert "control_linkage_not_supported" in codes

    created = AppliedControl.objects.get(id=body["created_records"][0]["record_id"])
    assert created.findings.count() == 0
    assert created.assets.count() == 0
    # The unsupported control linkage is preserved as readable text, not invented schema.
    assert "Multi-Factor Authentication for Remote Access" in created.description


# --- 12. blocking errors for an unsafe write target -------------------------


@pytest.mark.django_db
def test_unknown_folder_reference_blocks_dry_run(authenticated_client, setup_context):
    payload = _request_payload(setup_context)
    payload["folder_reference"] = str(uuid.uuid4())

    before = _counts_snapshot()
    response = _post(authenticated_client, payload)
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert body["blocking_errors"][0]["code"] == "folder_not_found"
    assert body["created_records"] == []
    assert before == after


@pytest.mark.django_db
def test_unknown_folder_reference_blocks_commit(authenticated_client, setup_context):
    payload = _request_payload(setup_context, dry_run=False, approved=True)
    payload["folder_reference"] = str(uuid.uuid4())

    before = _counts_snapshot()
    response = _post(authenticated_client, payload)
    after = _counts_snapshot()

    assert response.status_code == 422
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert body["blocking_errors"][0]["code"] == "folder_not_found"
    assert body["created_records"] == []
    assert before == after


@pytest.mark.django_db
def test_reuse_target_outside_folder_is_blocked(authenticated_client, setup_context):
    other_folder = Folder.objects.create(
        name=f"Other Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    outside = AppliedControl.objects.create(
        folder=other_folder,
        name="Out-of-scope control",
        status=AppliedControl.Status.TO_DO,
    )

    response = _post(
        authenticated_client,
        _request_payload(
            setup_context,
            dry_run=False,
            approved=True,
            decisions=[
                _decision(decision="reuse", existing_record_reference=str(outside.id))
            ],
        ),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["commit_status"] == "blocked"
    assert body["blocking_errors"][0]["code"] == "reuse_out_of_scope"


@pytest.mark.django_db
def test_requires_authentication(client, setup_context):
    response = client.post(
        reverse("ai-remediation-action-commit"),
        _request_payload(setup_context),
        content_type="application/json",
    )
    assert response.status_code == 401
