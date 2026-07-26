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
	"Al-Rawasi Fintech is preparing for its annual SAMA ECC-1:2018 compliance assessment in Q4 2026. "
	"The scope is Core Banking Platform - User Access Management. Known weaknesses include no MFA for remote access, "
	"no PAM for privileged admin accounts, no periodic access review records, and no formal access review documentation."
)


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
	from pathlib import Path

	import ciso_assistant.settings as settings

	settings.DATABASES["default"]["TEST"]["NAME"] = (
		Path(settings.BASE_DIR)
		/ "db"
		/ f"test_ai_applied_control_commit_{uuid.uuid4().hex}.sqlite3"
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
		name=f"AI Step 4B Domain {uuid.uuid4().hex[:8]}",
		content_type=Folder.ContentType.DOMAIN,
		parent_folder=Folder.get_root_folder(),
		create_iam_groups=False,
	)
	perimeter = Perimeter.objects.create(
		folder=folder,
		name=f"AI Step 4B Perimeter {uuid.uuid4().hex[:8]}",
		ref_id=f"PER-STEP4B-{uuid.uuid4().hex[:8]}",
		description="Step 4B applied-control commit scope perimeter",
		lc_status="in_prod",
	)
	compliance_assessment = ComplianceAssessment.objects.create(
		folder=folder,
		perimeter=perimeter,
		framework=framework,
		name=f"AI Step 4B Compliance Assessment {uuid.uuid4().hex[:8]}",
		version="1.0",
		status="planned",
	)
	risk_assessment = RiskAssessment.objects.create(
		folder=folder,
		perimeter=perimeter,
		risk_matrix=risk_matrix,
		name=f"AI Step 4B Risk Assessment {uuid.uuid4().hex[:8]}",
		version="1.0",
		status="planned",
	)
	assets = [
		Asset.objects.create(
			folder=folder,
			name="Core Banking Platform",
			type=Asset.Type.PRIMARY,
			ref_id=f"AST-CBP-{uuid.uuid4().hex[:6].upper()}",
			description="Primary core banking platform.",
		),
		Asset.objects.create(
			folder=folder,
			name="Remote Access / VPN Service",
			type=Asset.Type.SUPPORT,
			ref_id=f"AST-VPN-{uuid.uuid4().hex[:6].upper()}",
			description="Remote access service.",
		),
		Asset.objects.create(
			folder=folder,
			name="Identity Provider / IAM System",
			type=Asset.Type.SUPPORT,
			ref_id=f"AST-IAM-{uuid.uuid4().hex[:6].upper()}",
			description="IAM service.",
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


def _case_setup_reference(setup_context):
	return {
		"folder_id": str(setup_context["folder"].id),
		"perimeter_id": str(setup_context["perimeter"].id),
		"compliance_assessment_id": str(setup_context["compliance_assessment"].id),
		"risk_assessment_id": str(setup_context["risk_assessment"].id),
		"selected_framework_id": str(setup_context["framework"].id),
	}


def _asset_source_temporary_id(asset):
	return f"asset-ref-{asset.ref_id.lower()}"


def _asset_reference(asset):
	return {
		"asset_id": str(asset.id),
		"name": asset.name,
		"ref_id": asset.ref_id,
		"asset_class": None,
		"type": asset.type,
		"source_temporary_id": _asset_source_temporary_id(asset),
	}


def _create_decision(setup_context, *, temporary_id="CTL-CAND-001", name="Multi-Factor Authentication for Remote Access", **overrides):
	linked_assets = setup_context["assets"][:2]
	decision = {
		"temporary_id": temporary_id,
		"selected": True,
		"action": "create",
		"human_approved": True,
		"approved_fields": {
			"name": name,
			"description": "Require MFA for remote access to core banking systems.",
			"ref_id": f"CTL-{uuid.uuid4().hex[:8].upper()}",
			"category": "technical",
			"status": "to_do",
			"linked_asset_ids": [str(asset.id) for asset in linked_assets],
		},
		"selected_existing_applied_control_id": None,
		"original_suggestion_summary": {
			"proposed_name": name,
			"proposed_description": "Require MFA for remote access to core banking systems.",
			"proposed_reference_id": None,
			"proposed_control_type": "safeguard",
			"proposed_control_category": "technical",
			"proposed_status": "to_do",
			"proposed_implementation_state": "planned",
			"linked_asset_ids": [str(asset.id) for asset in linked_assets],
			"linked_asset_temporary_ids": [_asset_source_temporary_id(asset) for asset in linked_assets],
			"related_weaknesses": ["No MFA for remote access"],
			"confidence": 0.93,
			"ambiguity_flags": [],
		},
		"reviewer_notes": "Approved for deterministic applied-control commit.",
		"ambiguity_resolution": None,
		"duplicate_resolution": None,
	}
	decision.update(overrides)
	return decision


def _reuse_decision(setup_context, existing_applied_control, **overrides):
	linked_assets = setup_context["assets"][:2]
	decision = {
		"temporary_id": "CTL-CAND-002",
		"selected": True,
		"action": "reuse",
		"human_approved": True,
		"approved_fields": None,
		"selected_existing_applied_control_id": str(existing_applied_control.id),
		"original_suggestion_summary": {
			"proposed_name": existing_applied_control.name,
			"proposed_description": existing_applied_control.description,
			"proposed_reference_id": existing_applied_control.ref_id,
			"proposed_control_type": "safeguard",
			"proposed_control_category": existing_applied_control.category,
			"proposed_status": existing_applied_control.status,
			"proposed_implementation_state": "existing",
			"linked_asset_ids": [str(asset.id) for asset in linked_assets],
			"linked_asset_temporary_ids": [_asset_source_temporary_id(asset) for asset in linked_assets],
			"related_weaknesses": ["No MFA for remote access"],
			"confidence": 0.88,
			"ambiguity_flags": [],
		},
		"reviewer_notes": "Reuse existing applied control.",
		"ambiguity_resolution": None,
		"duplicate_resolution": {
			"decision": "reuse_existing",
			"reviewed_match_ids": [str(existing_applied_control.id)],
		},
	}
	decision.update(overrides)
	return decision


def _request_payload(setup_context, **overrides):
	payload = {
		"dry_run": True,
		"approved_by_user": False,
		"idempotency_key": None,
		"source_step1_draft_hash": "sha256:" + "a" * 64,
		"source_asset_commit_hash": "sha256:" + "b" * 64,
		"source_applied_control_draft_hash": "sha256:" + "c" * 64,
		"case_setup_reference": _case_setup_reference(setup_context),
		"asset_references": [_asset_reference(asset) for asset in setup_context["assets"]],
		"applied_control_decisions": [_create_decision(setup_context)],
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
		"RiskAcceptance": RiskAcceptance.objects.count(),
	}


@pytest.mark.django_db
def test_ai_applied_control_commit_requires_authentication(client, setup_context):
	response = client.post(reverse("ai-applied-control-commit"), _request_payload(setup_context), format="json")
	assert response.status_code == 401


@pytest.mark.django_db
def test_dry_run_does_not_write_and_returns_planned_actions(authenticated_client, setup_context):
	before = _counts_snapshot()
	response = authenticated_client.post(
		reverse("ai-applied-control-commit"),
		_request_payload(setup_context),
		format="json",
	)
	after = _counts_snapshot()

	assert response.status_code == 200
	body = response.json()
	assert body["operation_type"] == "dry_run"
	assert body["no_write"] is True
	assert body["created_applied_controls"] == []
	assert body["planned_actions"]
	assert before == after


@pytest.mark.django_db
def test_write_mode_requires_top_level_approval(authenticated_client, setup_context):
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=False,
		idempotency_key="applied-control-commit-1",
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")
	assert response.status_code == 400
	assert "approved_by_user" in response.json()


@pytest.mark.django_db
def test_missing_human_approval_blocks_write(authenticated_client, setup_context):
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=True,
		idempotency_key="applied-control-commit-approval-1",
		applied_control_decisions=[_create_decision(setup_context, human_approved=False)],
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")

	assert response.status_code == 422
	assert any(item["code"] == "human_approval_required" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_invalid_linked_asset_blocks_write(authenticated_client, setup_context):
	decision = _create_decision(
		setup_context,
		approved_fields={
			"name": "Multi-Factor Authentication for Remote Access",
			"description": "Require MFA for remote access to core banking systems.",
			"ref_id": "CTL-LINK-001",
			"category": "technical",
			"status": "to_do",
			"linked_asset_ids": [str(uuid.uuid4())],
		},
	)
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=True,
		idempotency_key="applied-control-commit-link-1",
		applied_control_decisions=[decision],
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")

	assert response.status_code == 422
	assert any(item["code"] == "invalid_linked_asset" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_valid_create_creates_applied_control(authenticated_client, setup_context):
	before = _counts_snapshot()
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=True,
		idempotency_key="applied-control-commit-create-1",
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")
	after = _counts_snapshot()

	assert response.status_code == 200
	body = response.json()
	assert body["operation_type"] == "commit"
	assert len(body["created_applied_controls"]) == 1
	created = AppliedControl.objects.get(id=body["created_applied_controls"][0]["applied_control_id"])
	assert created.assets.count() == 2
	assert after["AppliedControl"] == before["AppliedControl"] + 1
	for key, value in before.items():
		if key == "AppliedControl":
			continue
		assert after[key] == value


@pytest.mark.django_db
def test_duplicate_create_is_blocked(authenticated_client, setup_context):
	existing = AppliedControl.objects.create(
		folder=setup_context["folder"],
		name="Multi-Factor Authentication for Remote Access",
		category="technical",
		status="to_do",
	)
	existing.assets.set(setup_context["assets"][:2])
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=True,
		idempotency_key="applied-control-commit-duplicate-1",
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")

	assert response.status_code == 409
	assert any(item["code"] == "duplicate_conflict" for item in response.json()["blocking_errors"])


@pytest.mark.django_db
def test_valid_reuse_reuses_existing_applied_control(authenticated_client, setup_context):
	existing = AppliedControl.objects.create(
		folder=setup_context["folder"],
		name="Multi-Factor Authentication for Remote Access",
		category="technical",
		status="active",
		description="Before reuse",
	)
	existing.assets.set(setup_context["assets"][:2])
	before_updated_at = existing.updated_at
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=True,
		idempotency_key="applied-control-commit-reuse-1",
		applied_control_decisions=[_reuse_decision(setup_context, existing)],
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")
	existing.refresh_from_db()

	assert response.status_code == 200
	body = response.json()
	assert body["created_applied_controls"] == []
	assert len(body["reused_applied_controls"]) == 1
	assert body["reused_applied_controls"][0]["applied_control_id"] == str(existing.id)
	assert existing.description == "Before reuse"
	assert existing.updated_at == before_updated_at


@pytest.mark.django_db
def test_reject_and_defer_do_not_write(authenticated_client, setup_context):
	before = _counts_snapshot()
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=True,
		idempotency_key="applied-control-commit-reject-defer-1",
		applied_control_decisions=[
			_create_decision(
				setup_context,
				temporary_id="CTL-CAND-003",
				action="reject",
				approved_fields=None,
				selected_existing_applied_control_id=None,
			),
			_create_decision(
				setup_context,
				temporary_id="CTL-CAND-004",
				action="defer",
				approved_fields=None,
				selected_existing_applied_control_id=None,
			),
		],
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")
	after = _counts_snapshot()

	assert response.status_code == 200
	body = response.json()
	assert body["created_applied_controls"] == []
	assert len(body["rejected_applied_controls"]) == 1
	assert len(body["deferred_applied_controls"]) == 1
	assert before == after


@pytest.mark.django_db
def test_unselected_candidate_blocks_write(authenticated_client, setup_context):
	payload = _request_payload(
		setup_context,
		dry_run=False,
		approved_by_user=True,
		idempotency_key="applied-control-commit-selected-1",
		applied_control_decisions=[_create_decision(setup_context, selected=False)],
	)
	response = authenticated_client.post(reverse("ai-applied-control-commit"), payload, format="json")

	assert response.status_code == 400
	assert "selected" in response.json()["applied_control_decisions"][0]


@pytest.mark.django_db
def test_step4a_regression_remains_advisory_no_write(authenticated_client, setup_context):
	before = _counts_snapshot()
	response = authenticated_client.post(
		reverse("ai-applied-control-suggestion"),
		{
			"source_step1_draft_hash": "sha256:" + "a" * 64,
			"source_asset_commit_hash": "sha256:" + "b" * 64,
			"case_setup_reference": _case_setup_reference(setup_context),
			"asset_references": [_asset_reference(asset) for asset in setup_context["assets"]],
			"scenario_text": AL_RAWASI_SCENARIO,
			"scope_summary": "Core Banking Platform user access management scope.",
			"known_weaknesses": ["No MFA for remote access"],
			"selected_framework_id": str(setup_context["framework"].id),
			"user_locale": "en",
			"strict_mode": True,
		},
		format="json",
	)
	after = _counts_snapshot()

	assert response.status_code == 200
	assert before == after