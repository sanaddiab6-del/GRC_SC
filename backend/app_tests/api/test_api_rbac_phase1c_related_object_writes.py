"""
Phase 1C: related-object write authorization for the sync_to_applied_controls /
create_suggested_applied_controls workflows.

These endpoints were suspected of letting a user who can access a parent assessment cause
unauthorized creation, modification, or linkage of AppliedControl records in another folder.
Tracing the model methods behind each endpoint (RiskAssessment/RiskScenario/
ComplianceAssessment.sync_to_applied_controls, RequirementAssessment
.create_applied_controls_from_suggestions) shows none of them accept an externally supplied
AppliedControl id: they only act on relations already attached to the authorized parent, or
create new AppliedControls scoped to the parent's own folder. The tests below exercise that
claim directly (attempted injection has no effect) and separately reproduce/fix the
nonexistent-vs-inaccessible status-code inconsistency found during tracing.
"""

import uuid

import pytest
from django.conf import settings as django_settings
from knox.models import AuthToken
from rest_framework.test import APIClient

from core.models import (
    AppliedControl,
    ComplianceAssessment,
    Framework,
    ReferenceControl,
    RequirementAssessment,
    RequirementNode,
    RiskAssessment,
    RiskMatrix,
    RiskScenario,
)
from iam.models import Folder, Permission, Role, RoleAssignment, User, UserGroup


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_rbac_phase1c_related_object_writes_{uuid.uuid4().hex}.sqlite3"
    )


@pytest.fixture(autouse=True)
def app_config():
    original_allowed_hosts = list(django_settings.ALLOWED_HOSTS)
    django_settings.ALLOWED_HOSTS = [*original_allowed_hosts, "testserver"]
    try:
        yield
    finally:
        django_settings.ALLOWED_HOSTS = original_allowed_hosts


def _make_domain_folder(name: str) -> Folder:
    return Folder.objects.create(
        name=f"{name}-{uuid.uuid4().hex[:6]}",
        content_type=Folder.ContentType.DOMAIN,
        builtin=False,
        parent_folder=Folder.objects.get(content_type=Folder.ContentType.ROOT),
    )


def _make_scoped_client(*, folder: Folder, extra_codenames: list[str]) -> APIClient:
    user = User.objects.create_user(
        f"scoped-{uuid.uuid4().hex[:8]}@tests.com", is_published=True
    )
    role = Role.objects.create(name=f"scoped-role-{uuid.uuid4().hex[:8]}")
    role.permissions.set(
        Permission.objects.filter(codename__in=["view_folder", *extra_codenames])
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
    return client


def _make_risk_matrix(*, folder: Folder) -> RiskMatrix:
    return RiskMatrix.objects.create(
        name=f"matrix-{uuid.uuid4().hex[:6]}",
        folder=folder,
        json_definition={
            "grid": [[0]],
            "probability": [{"abbreviation": "1", "name": "low", "value": 1}],
            "impact": [{"abbreviation": "1", "name": "low", "value": 1}],
            "risk": [{"abbreviation": "1", "name": "low", "value": 1}],
        },
    )


# ---------------------------------------------------------------------------
# RiskAssessment.sync_to_applied_controls / RiskScenario.sync_to_applied_controls
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRiskScenarioSyncToAppliedControls:
    def _make_scenario(
        self, *, folder: Folder
    ) -> tuple[RiskAssessment, RiskScenario, AppliedControl]:
        matrix = _make_risk_matrix(folder=folder)
        risk_assessment = RiskAssessment.objects.create(
            name="RA", folder=folder, risk_matrix=matrix
        )
        scenario = RiskScenario.objects.create(
            name="Scenario", risk_assessment=risk_assessment, folder=folder
        )
        extra_control = AppliedControl.objects.create(
            name="Extra control",
            folder=folder,
            status=AppliedControl.Status.ACTIVE,
        )
        scenario.applied_controls.add(extra_control)
        return risk_assessment, scenario, extra_control

    def test_cannot_inject_foreign_applied_control_via_request_body(self):
        """The endpoint takes no AppliedControl id from the client — only dry_run /
        reset_residual — so a Folder B AppliedControl id in the payload must have zero effect."""
        folder_a = _make_domain_folder("riskscenario-sync-a")
        folder_b = _make_domain_folder("riskscenario-sync-b")
        _ra, scenario, _extra = self._make_scenario(folder=folder_a)
        foreign_control = AppliedControl.objects.create(
            name="Foreign control", folder=folder_b
        )
        client = _make_scoped_client(
            folder=folder_a,
            extra_codenames=["view_riskscenario", "change_riskscenario"],
        )

        response = client.post(
            f"/api/risk-scenarios/{scenario.id}/sync-to-actions/?dry_run=false",
            {
                "applied_control_id": str(foreign_control.id),
                "applied_controls": [str(foreign_control.id)],
                "existing_applied_controls": [str(foreign_control.id)],
            },
        )

        assert response.status_code == 200, response.content
        foreign_control.refresh_from_db()
        scenario.refresh_from_db()
        assert foreign_control not in scenario.applied_controls.all()
        assert foreign_control not in scenario.existing_applied_controls.all()

    def test_authorized_sync_only_moves_controls_already_on_the_scenario(self):
        folder_a = _make_domain_folder("riskscenario-sync-positive")
        _ra, scenario, extra_control = self._make_scenario(folder=folder_a)
        client = _make_scoped_client(
            folder=folder_a,
            extra_codenames=["view_riskscenario", "change_riskscenario"],
        )

        response = client.post(
            f"/api/risk-scenarios/{scenario.id}/sync-to-actions/?dry_run=false"
            )

        assert response.status_code == 200, response.content
        scenario.refresh_from_db()
        assert extra_control in scenario.existing_applied_controls.all()
        assert extra_control not in scenario.applied_controls.all()

    def test_cross_folder_user_cannot_trigger_sync_and_db_state_is_unchanged(self):
        hidden = _make_domain_folder("riskscenario-sync-hidden")
        visible = _make_domain_folder("riskscenario-sync-visible")
        _ra, scenario, extra_control = self._make_scenario(folder=hidden)
        client = _make_scoped_client(
            folder=visible,
            extra_codenames=["view_riskscenario", "change_riskscenario"],
        )

        response = client.post(
            f"/api/risk-scenarios/{scenario.id}/sync-to-actions/?dry_run=false"
            )

        assert response.status_code == 403, response.content
        scenario.refresh_from_db()
        assert extra_control in scenario.applied_controls.all()
        assert extra_control not in scenario.existing_applied_controls.all()

    def test_nonexistent_and_inaccessible_scenario_are_indistinguishable(self):
        hidden = _make_domain_folder("riskscenario-sync-oracle-hidden")
        visible = _make_domain_folder("riskscenario-sync-oracle-visible")
        _ra, scenario, _extra = self._make_scenario(folder=hidden)
        client = _make_scoped_client(
            folder=visible,
            extra_codenames=["view_riskscenario", "change_riskscenario"],
        )

        inaccessible = client.post(
            f"/api/risk-scenarios/{scenario.id}/sync-to-actions/", {"dry_run": "false"}
        )
        nonexistent = client.post(
            f"/api/risk-scenarios/{uuid.uuid4()}/sync-to-actions/", {"dry_run": "false"}
        )

        assert inaccessible.status_code == nonexistent.status_code, (
            inaccessible.status_code,
            nonexistent.status_code,
        )


@pytest.mark.django_db
class TestRiskAssessmentSyncToAppliedControls:
    def test_nonexistent_and_inaccessible_risk_assessment_are_indistinguishable(self):
        hidden = _make_domain_folder("riskassessment-sync-oracle-hidden")
        visible = _make_domain_folder("riskassessment-sync-oracle-visible")
        matrix = _make_risk_matrix(folder=hidden)
        risk_assessment = RiskAssessment.objects.create(
            name="RA", folder=hidden, risk_matrix=matrix
        )
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_riskassessment"]
        )

        inaccessible = client.post(
            f"/api/risk-assessments/{risk_assessment.id}/sync-to-actions/?dry_run=false"
            )
        nonexistent = client.post(
            f"/api/risk-assessments/{uuid.uuid4()}/sync-to-actions/?dry_run=false"
            )

        assert inaccessible.status_code == nonexistent.status_code, (
            inaccessible.status_code,
            nonexistent.status_code,
        )

    def test_authorized_user_can_still_sync(self):
        visible = _make_domain_folder("riskassessment-sync-positive")
        matrix = _make_risk_matrix(folder=visible)
        risk_assessment = RiskAssessment.objects.create(
            name="RA", folder=visible, risk_matrix=matrix
        )
        scenario = RiskScenario.objects.create(
            name="Scenario", risk_assessment=risk_assessment, folder=visible
        )
        extra_control = AppliedControl.objects.create(
            name="Extra control",
            folder=visible,
            status=AppliedControl.Status.ACTIVE,
        )
        scenario.applied_controls.add(extra_control)
        client = _make_scoped_client(
            folder=visible,
            extra_codenames=["view_riskassessment", "change_riskassessment"],
        )

        response = client.post(
            f"/api/risk-assessments/{risk_assessment.id}/sync-to-actions/?dry_run=false"
            )

        assert response.status_code == 200, response.content
        scenario.refresh_from_db()
        assert extra_control in scenario.existing_applied_controls.all()


# ---------------------------------------------------------------------------
# ComplianceAssessment.sync_to_applied_controls
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestComplianceAssessmentSyncToAppliedControls:
    def _make_assessment_with_ra(
        self, *, folder: Folder
    ) -> tuple[ComplianceAssessment, RequirementAssessment, AppliedControl]:
        framework = Framework.objects.create(name="fw", folder=folder)
        node = RequirementNode.objects.create(
            framework=framework,
            urn=f"urn:phase1c:rn:{uuid.uuid4().hex}",
            ref_id="1",
            name="req",
            assessable=True,
            folder=folder,
        )
        audit = ComplianceAssessment.objects.create(
            name="Audit", framework=framework, folder=folder
        )
        ra = RequirementAssessment.objects.create(
            requirement=node, compliance_assessment=audit, folder=folder
        )
        control = AppliedControl.objects.create(
            name="Control", folder=folder, status=AppliedControl.Status.ACTIVE
        )
        ra.applied_controls.add(control)
        return audit, ra, control

    def test_nonexistent_and_inaccessible_assessment_are_indistinguishable(self):
        hidden = _make_domain_folder("ca-sync-oracle-hidden")
        visible = _make_domain_folder("ca-sync-oracle-visible")
        audit, _ra, _control = self._make_assessment_with_ra(folder=hidden)
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_requirementassessment"]
        )

        inaccessible = client.post(
            f"/api/compliance-assessments/{audit.id}/syncToActions/?dry_run=false"
            )
        nonexistent = client.post(
            f"/api/compliance-assessments/{uuid.uuid4()}/syncToActions/?dry_run=false"
            )

        assert inaccessible.status_code == nonexistent.status_code, (
            inaccessible.status_code,
            nonexistent.status_code,
        )

    def test_cross_folder_user_cannot_trigger_sync_and_result_is_unchanged(self):
        hidden = _make_domain_folder("ca-sync-hidden")
        visible = _make_domain_folder("ca-sync-visible")
        audit, ra, _control = self._make_assessment_with_ra(folder=hidden)
        original_result = ra.result
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_requirementassessment"]
        )

        response = client.post(
            f"/api/compliance-assessments/{audit.id}/syncToActions/?dry_run=false"
            )

        assert response.status_code == 403, response.content
        ra.refresh_from_db()
        assert ra.result == original_result

    def test_authorized_user_can_still_sync_result(self):
        visible = _make_domain_folder("ca-sync-positive")
        audit, ra, _control = self._make_assessment_with_ra(folder=visible)
        client = _make_scoped_client(
            folder=visible, extra_codenames=["change_requirementassessment"]
        )

        response = client.post(
            f"/api/compliance-assessments/{audit.id}/syncToActions/?dry_run=false"
            )

        assert response.status_code == 200, response.content
        ra.refresh_from_db()
        assert ra.result == RequirementAssessment.Result.COMPLIANT


# ---------------------------------------------------------------------------
# create_suggested_applied_controls — ComplianceAssessment and RequirementAssessment
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateSuggestedAppliedControls:
    def _make_assessment_with_suggestion(
        self, *, folder: Folder
    ) -> tuple[ComplianceAssessment, RequirementAssessment]:
        framework = Framework.objects.create(name="fw", folder=folder)
        reference_control = ReferenceControl.objects.create(
            name="Reference control", folder=folder
        )
        node = RequirementNode.objects.create(
            framework=framework,
            urn=f"urn:phase1c:sugg:{uuid.uuid4().hex}",
            ref_id="1",
            name="req",
            assessable=True,
            folder=folder,
        )
        node.reference_controls.add(reference_control)
        audit = ComplianceAssessment.objects.create(
            name="Audit", framework=framework, folder=folder
        )
        ra = RequirementAssessment.objects.create(
            requirement=node, compliance_assessment=audit, folder=folder
        )
        return audit, ra

    def test_compliance_assessment_nonexistent_and_inaccessible_are_indistinguishable(
        self,
    ):
        hidden = _make_domain_folder("ca-suggest-oracle-hidden")
        visible = _make_domain_folder("ca-suggest-oracle-visible")
        audit, _ra = self._make_assessment_with_suggestion(folder=hidden)
        client = _make_scoped_client(
            folder=visible, extra_codenames=["add_appliedcontrol"]
        )

        inaccessible = client.post(
            f"/api/compliance-assessments/{audit.id}/suggestions/applied-controls/?dry_run=false"
            )
        nonexistent = client.post(
            f"/api/compliance-assessments/{uuid.uuid4()}/suggestions/applied-controls/?dry_run=false"
            )

        assert inaccessible.status_code == nonexistent.status_code, (
            inaccessible.status_code,
            nonexistent.status_code,
        )

    def test_cross_folder_user_cannot_trigger_control_creation(self):
        hidden = _make_domain_folder("ca-suggest-hidden")
        visible = _make_domain_folder("ca-suggest-visible")
        audit, _ra = self._make_assessment_with_suggestion(folder=hidden)
        before_count = AppliedControl.objects.filter(folder=hidden).count()
        client = _make_scoped_client(
            folder=visible, extra_codenames=["add_appliedcontrol"]
        )

        response = client.post(
            f"/api/compliance-assessments/{audit.id}/suggestions/applied-controls/?dry_run=false"
            )

        assert response.status_code == 403, response.content
        assert AppliedControl.objects.filter(folder=hidden).count() == before_count

    def test_authorized_user_creates_controls_scoped_to_the_assessment_folder(self):
        visible = _make_domain_folder("ca-suggest-positive")
        other_folder = _make_domain_folder("ca-suggest-positive-other")
        audit, _ra = self._make_assessment_with_suggestion(folder=visible)
        client = _make_scoped_client(
            folder=visible, extra_codenames=["add_appliedcontrol"]
        )

        response = client.post(
            f"/api/compliance-assessments/{audit.id}/suggestions/applied-controls/?dry_run=false"
            )

        assert response.status_code == 200, response.content
        created = AppliedControl.objects.filter(folder=visible)
        assert created.exists()
        assert not AppliedControl.objects.filter(folder=other_folder).exists()

    def test_requirement_assessment_cross_folder_user_cannot_trigger_control_creation(
        self,
    ):
        hidden = _make_domain_folder("ra-suggest-hidden")
        visible = _make_domain_folder("ra-suggest-visible")
        _audit, ra = self._make_assessment_with_suggestion(folder=hidden)
        before_count = AppliedControl.objects.filter(folder=hidden).count()
        client = _make_scoped_client(
            folder=visible, extra_codenames=["add_appliedcontrol"]
        )

        response = client.post(
            f"/api/requirement-assessments/{ra.id}/suggestions/applied-controls/?dry_run=false"
            )

        assert response.status_code == 403, response.content
        assert AppliedControl.objects.filter(folder=hidden).count() == before_count

    def test_requirement_assessment_nonexistent_and_inaccessible_are_indistinguishable(
        self,
    ):
        hidden = _make_domain_folder("ra-suggest-oracle-hidden")
        visible = _make_domain_folder("ra-suggest-oracle-visible")
        _audit, ra = self._make_assessment_with_suggestion(folder=hidden)
        client = _make_scoped_client(
            folder=visible, extra_codenames=["add_appliedcontrol"]
        )

        inaccessible = client.post(
            f"/api/requirement-assessments/{ra.id}/suggestions/applied-controls/?dry_run=false"
            )
        nonexistent = client.post(
            f"/api/requirement-assessments/{uuid.uuid4()}/suggestions/applied-controls/?dry_run=false"
            )

        assert inaccessible.status_code == nonexistent.status_code, (
            inaccessible.status_code,
            nonexistent.status_code,
        )
