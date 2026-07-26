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
        / f"test_ai_evidence_finding_commit_{uuid.uuid4().hex}.sqlite3"
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
def block_ai_provider(monkeypatch):
    """Step 5B must never call an AI provider; make any HTTP call to the local AI fail."""

    def _boom(*args, **kwargs):
        raise AssertionError("Step 5B must not call any AI provider.")

    monkeypatch.setattr("ai_onboarding.llm_provider.urllib.request.urlopen", _boom)
    monkeypatch.delenv("AI_PROVIDER", raising=False)


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
        name=f"AI Step 5B Domain {uuid.uuid4().hex[:8]}",
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=Folder.get_root_folder(),
        create_iam_groups=False,
    )
    perimeter = Perimeter.objects.create(
        folder=folder,
        name=f"AI Step 5B Perimeter {uuid.uuid4().hex[:8]}",
        ref_id=f"PER-STEP5B-{uuid.uuid4().hex[:8]}",
        lc_status="in_prod",
    )
    compliance_assessment = ComplianceAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        framework=framework,
        name=f"AI Step 5B Compliance {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    risk_assessment = RiskAssessment.objects.create(
        folder=folder,
        perimeter=perimeter,
        risk_matrix=risk_matrix,
        name=f"AI Step 5B Risk {uuid.uuid4().hex[:8]}",
        version="1.0",
        status="planned",
    )
    assets = [
        Asset.objects.create(
            folder=folder,
            name="Core Banking Platform",
            type=Asset.Type.PRIMARY,
            ref_id=f"AST-CBP-{uuid.uuid4().hex[:6].upper()}",
        ),
    ]
    applied_controls = [
        AppliedControl.objects.create(
            folder=folder,
            name="Multi-Factor Authentication for Remote Access",
            category="technical",
            status="to_do",
            ref_id="CTL-MFA-001",
        ),
    ]
    for control in applied_controls:
        control.assets.set(assets)

    return {
        "folder": folder,
        "perimeter": perimeter,
        "compliance_assessment": compliance_assessment,
        "risk_assessment": risk_assessment,
        "framework": framework,
        "assets": assets,
        "applied_controls": applied_controls,
    }


def _asset_reference(asset):
    return {"asset_id": str(asset.id), "name": asset.name, "ref_id": asset.ref_id}


def _applied_control_reference(control):
    return {
        "applied_control_id": str(control.id),
        "name": control.name,
        "ref_id": control.ref_id,
        "category": control.category,
        "status": control.status,
    }


def _evidence_decision(setup_context, *, temporary_id="EVR-CAND-001", name="MFA Evidence Request", **overrides):
    control_ids = [str(c.id) for c in setup_context["applied_controls"]]
    asset_ids = [str(a.id) for a in setup_context["assets"]]
    decision = {
        "temporary_id": temporary_id,
        "kind": "evidence_request",
        "selected": True,
        "action": "create",
        "human_approved": True,
        "approved_fields": {"name": name, "description": "Request MFA configuration evidence."},
        "original_suggestion_summary": {
            "title": name,
            "rationale": "Evidence needed to demonstrate MFA control.",
            "review_status": "pending_review",
            "confidence": 0.8,
            "linked_asset_ids": asset_ids,
            "linked_applied_control_ids": control_ids,
        },
    }
    decision.update(overrides)
    return decision


def _audit_question_decision(setup_context, *, temporary_id="AUQ-CAND-001", **overrides):
    control_ids = [str(c.id) for c in setup_context["applied_controls"]]
    question = "How is MFA enforced for remote access?"
    decision = {
        "temporary_id": temporary_id,
        "kind": "audit_question",
        "selected": True,
        "action": "create",
        "human_approved": True,
        "approved_fields": {"name": question},
        "original_suggestion_summary": {
            "question_text": question,
            "rationale": "Confirm operating effectiveness.",
            "review_status": "pending_review",
            "confidence": 0.8,
            "linked_applied_control_ids": control_ids,
        },
    }
    decision.update(overrides)
    return decision


def _finding_decision(setup_context, *, temporary_id="FND-CAND-001", name="Remote access MFA gap", **overrides):
    control_ids = [str(c.id) for c in setup_context["applied_controls"]]
    decision = {
        "temporary_id": temporary_id,
        "kind": "preliminary_finding",
        "selected": True,
        "action": "create",
        "human_approved": True,
        "approved_fields": {"name": name},
        "original_suggestion_summary": {
            "title": name,
            "rationale": "Reported weakness pending confirmation.",
            "review_status": "pending_review",
            "confidence": 0.7,
            "linked_applied_control_ids": control_ids,
        },
    }
    decision.update(overrides)
    return decision


def _payload(setup_context, **overrides):
    payload = {
        "dry_run": True,
        "approved_by_user": False,
        "idempotency_key": None,
        "source_step1_draft_hash": "sha256:" + "a" * 64,
        "source_asset_commit_hash": "sha256:" + "b" * 64,
        "source_applied_control_commit_hash": "sha256:" + "c" * 64,
        "source_evidence_finding_draft_hash": "sha256:" + "d" * 64,
        "case_setup_reference": {
            "folder_id": str(setup_context["folder"].id),
            "perimeter_id": str(setup_context["perimeter"].id),
        },
        "asset_references": [_asset_reference(a) for a in setup_context["assets"]],
        "applied_control_references": [
            _applied_control_reference(c) for c in setup_context["applied_controls"]
        ],
        "evidence_request_decisions": [_evidence_decision(setup_context)],
        "audit_question_decisions": [],
        "preliminary_finding_decisions": [],
    }
    payload.update(overrides)
    return payload


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
        "RiskAcceptance": RiskAcceptance.objects.count(),
    }


@pytest.mark.django_db
def test_ai_evidence_finding_commit_requires_authentication(client, setup_context):
    response = client.post(reverse("ai-evidence-finding-commit"), _payload(setup_context), format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_validates_but_creates_nothing(authenticated_client, setup_context):
    before = _counts_snapshot()
    payload = _payload(
        setup_context,
        evidence_request_decisions=[_evidence_decision(setup_context)],
        audit_question_decisions=[_audit_question_decision(setup_context)],
        preliminary_finding_decisions=[_finding_decision(setup_context)],
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200
    body = response.json()
    assert body["operation_type"] == "dry_run"
    assert body["no_write"] is True
    assert body["no_ai_used"] is True
    assert body["created_records"] == []
    assert body["planned_actions"]
    assert before == after


@pytest.mark.django_db
def test_write_requires_top_level_approval(authenticated_client, setup_context):
    payload = _payload(
        setup_context,
        dry_run=False,
        approved_by_user=False,
        idempotency_key="efc-approval-1",
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")
    assert response.status_code == 400
    assert "approved_by_user" in response.json()


@pytest.mark.django_db
def test_missing_human_approval_blocks_write(authenticated_client, setup_context):
    payload = _payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="efc-approval-2",
        evidence_request_decisions=[_evidence_decision(setup_context, human_approved=False)],
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")
    assert response.status_code == 422
    assert any(item["code"] == "human_approval_required" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_approved_commit_creates_records(authenticated_client, setup_context):
    before = _counts_snapshot()
    payload = _payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="efc-create-1",
        evidence_request_decisions=[_evidence_decision(setup_context)],
        audit_question_decisions=[_audit_question_decision(setup_context)],
        preliminary_finding_decisions=[_finding_decision(setup_context)],
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200, response.json()
    body = response.json()
    assert body["operation_type"] == "commit"
    assert body["no_ai_used"] is True
    # 1 evidence_request + 1 audit_question -> 2 Evidence records
    assert after["Evidence"] == before["Evidence"] + 2
    assert after["Finding"] == before["Finding"] + 1
    assert after["FindingsAssessment"] == before["FindingsAssessment"] + 1
    assert body["counts"]["created"] >= 3
    assert body["counts"]["reused"] == 0


@pytest.mark.django_db
def test_duplicate_commit_reuses_existing_evidence(authenticated_client, setup_context):
    Evidence.objects.create(folder=setup_context["folder"], name="MFA Evidence Request")
    before = _counts_snapshot()
    payload = _payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="efc-dup-1",
        evidence_request_decisions=[_evidence_decision(setup_context, name="MFA Evidence Request")],
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200, response.json()
    body = response.json()
    assert after["Evidence"] == before["Evidence"]  # no new Evidence created
    assert body["counts"]["reused"] == 1
    assert body["counts"]["created"] == 0
    assert any(w["code"] == "duplicate_reused" for w in body["warnings"])


@pytest.mark.django_db
def test_reject_and_defer_do_not_write(authenticated_client, setup_context):
    before = _counts_snapshot()
    payload = _payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="efc-rejectdefer-1",
        evidence_request_decisions=[
            _evidence_decision(setup_context, temporary_id="EVR-R", action="reject"),
        ],
        preliminary_finding_decisions=[
            _finding_decision(setup_context, temporary_id="FND-D", action="defer"),
        ],
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")
    after = _counts_snapshot()

    assert response.status_code == 200, response.json()
    body = response.json()
    assert body["counts"]["rejected"] == 1
    assert body["counts"]["deferred"] == 1
    assert body["counts"]["created"] == 0
    assert before == after


@pytest.mark.django_db
def test_invalid_reference_returns_blocking_errors(authenticated_client, setup_context):
    payload = _payload(
        setup_context,
        applied_control_references=[{"applied_control_id": str(uuid.uuid4()), "name": "Ghost Control"}],
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert any(item["code"] == "applied_control_not_found" for item in body["blocking_errors"])


@pytest.mark.django_db
def test_no_ai_provider_is_called_during_commit(authenticated_client, setup_context):
    # block_ai_provider fixture raises if urlopen is called; a successful commit proves no AI call.
    payload = _payload(
        setup_context,
        dry_run=False,
        approved_by_user=True,
        idempotency_key="efc-noai-1",
        evidence_request_decisions=[_evidence_decision(setup_context)],
    )
    response = authenticated_client.post(reverse("ai-evidence-finding-commit"), payload, format="json")

    assert response.status_code == 200, response.json()
    body = response.json()
    assert body["no_ai_used"] is True
    assert body["counts"]["created"] >= 1
