"""
Regression tests for RBAC gaps found by the architecture-discovery review: a handful of
custom DRF actions/views fetch objects directly (``Model.objects.get(...)``) instead of going
through ``self.get_object()`` / ``BaseModelViewSet.get_queryset()``, so they never reach
``RoleAssignment.get_accessible_object_ids`` / ``is_access_allowed`` at all.

Each class below proves one finding is real against the *current* code before any fix is
applied (that proof is this file's own git history), then protects the fix going forward.
"""

import uuid

import pytest
from django.conf import settings as django_settings
from knox.models import AuthToken
from rest_framework.test import APIClient

from core.apps import startup as core_startup
from core.models import (
    AppliedControl,
    ComplianceAssessment,
    Evidence,
    Finding,
    FindingsAssessment,
    Framework,
    TaskNode,
    TaskTemplate,
    Actor,
)
from crq.models import (
    QuantitativeRiskHypothesis,
    QuantitativeRiskScenario,
    QuantitativeRiskStudy,
)
from privacy.models import Processing, RightRequest
from iam.models import Folder, Permission, Role, RoleAssignment, User, UserGroup


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_rbac_security_hardening_{uuid.uuid4().hex}.sqlite3"
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
        f"admin-{uuid.uuid4().hex[:8]}@tests.com", is_published=True
    )
    admin_group = UserGroup.objects.get(name="BI-UG-ADM")
    admin.folder = admin_group.folder
    admin.save()
    admin_group.user_set.add(admin)
    return admin


def _make_domain_folder(name: str) -> Folder:
    return Folder.objects.create(
        name=name,
        content_type=Folder.ContentType.DOMAIN,
        builtin=False,
        parent_folder=Folder.objects.get(content_type=Folder.ContentType.ROOT),
    )


def _make_scoped_client(*, folder: Folder, extra_codenames: list[str]) -> "tuple[APIClient, User]":
    """A non-admin user who can only view/change the given codenames within `folder` —
    the same minimum-permission pattern used by test_api_ai_evidence_freshness_review.py."""
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
    return client, user


# ---------------------------------------------------------------------------
# Finding A — TaskNodeViewSet.remove_evidence: zero RBAC check, unchecked write.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFindingARemoveEvidence:
    def _make_task_node(self, *, folder: Folder) -> tuple[TaskNode, Evidence]:
        template = TaskTemplate.objects.create(name="Quarterly review", folder=folder)
        node = TaskNode.objects.create(task_template=template, folder=folder)
        evidence = Evidence.objects.create(name="Screenshot", folder=folder)
        node.evidences.add(evidence)
        return node, evidence

    def test_cross_folder_user_cannot_remove_evidence_from_inaccessible_task_node(self):
        """The requesting user has no assignment at all on the folder that owns the
        TaskNode/Evidence being modified. The write must be denied and must not happen."""
        hidden_folder = _make_domain_folder("hidden-tasknode-folder")
        node, evidence = self._make_task_node(folder=hidden_folder)

        other_folder = _make_domain_folder("unrelated-folder")
        client, _user = _make_scoped_client(
            folder=other_folder, extra_codenames=["view_tasknode", "change_tasknode"]
        )

        response = client.post(
            f"/api/task-nodes/{node.id}/remove_evidence/",
            {"evidence_id": str(evidence.id)},
            format="json",
        )

        assert response.status_code in (403, 404), (
            "a user with no permission on the TaskNode's folder was able to reach "
            f"remove_evidence (got {response.status_code})"
        )
        node.refresh_from_db()
        assert evidence in node.evidences.all(), (
            "the evidence relationship was mutated despite the request being unauthorized"
        )

    def test_view_only_user_cannot_remove_evidence(self):
        """A user who can see the TaskNode (view_tasknode) but was not granted change rights
        must not be able to perform this write — view and change are different permissions."""
        folder = _make_domain_folder("view-only-tasknode-folder")
        node, evidence = self._make_task_node(folder=folder)

        client, _user = _make_scoped_client(folder=folder, extra_codenames=["view_tasknode"])

        response = client.post(
            f"/api/task-nodes/{node.id}/remove_evidence/",
            {"evidence_id": str(evidence.id)},
            format="json",
        )

        assert response.status_code == 403
        node.refresh_from_db()
        assert evidence in node.evidences.all()

    def test_authorized_user_can_still_remove_evidence(self):
        """Positive control: a user with change_tasknode on the owning folder can still
        perform the exact same operation that used to work unconditionally."""
        folder = _make_domain_folder("authorized-tasknode-folder")
        node, evidence = self._make_task_node(folder=folder)

        client, _user = _make_scoped_client(
            folder=folder, extra_codenames=["view_tasknode", "change_tasknode", "view_evidence"]
        )

        response = client.post(
            f"/api/task-nodes/{node.id}/remove_evidence/",
            {"evidence_id": str(evidence.id)},
            format="json",
        )

        assert response.status_code == 200
        node.refresh_from_db()
        assert evidence not in node.evidences.all()

    def test_authorized_user_can_still_move_evidence_to_template(self):
        """Positive control for the `move=True` branch: still works end-to-end for an
        authorized user, same as before the fix."""
        folder = _make_domain_folder("authorized-move-folder")
        node, evidence = self._make_task_node(folder=folder)

        client, _user = _make_scoped_client(
            folder=folder, extra_codenames=["view_tasknode", "change_tasknode", "view_evidence"]
        )

        response = client.post(
            f"/api/task-nodes/{node.id}/remove_evidence/",
            {"evidence_id": str(evidence.id), "move": True},
            format="json",
        )

        assert response.status_code == 200
        node.task_template.refresh_from_db()
        assert evidence in node.task_template.evidences.all()


# ---------------------------------------------------------------------------
# Finding B — ComplianceAssessmentViewSet.frameworks: zero RBAC check, cross-folder leak.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFindingBComplianceAssessmentFrameworks:
    def _make_assessment(self, *, folder: Folder) -> ComplianceAssessment:
        framework = Framework.objects.create(name="Test Framework", folder=folder)
        return ComplianceAssessment.objects.create(
            name="Confidential audit", framework=framework, folder=folder
        )

    def test_cross_folder_user_cannot_read_frameworks_for_inaccessible_assessment(self):
        hidden_folder = _make_domain_folder("hidden-audit-folder")
        assessment = self._make_assessment(folder=hidden_folder)

        other_folder = _make_domain_folder("unrelated-audit-folder")
        client, _user = _make_scoped_client(
            folder=other_folder, extra_codenames=["view_complianceassessment"]
        )

        response = client.get(f"/api/compliance-assessments/{assessment.id}/frameworks/")

        assert response.status_code in (403, 404), (
            "a user with no visibility into the ComplianceAssessment's folder could read "
            f"its frameworks mapping data (got {response.status_code})"
        )

    def test_authorized_user_can_still_read_frameworks(self):
        folder = _make_domain_folder("authorized-audit-folder")
        assessment = self._make_assessment(folder=folder)

        client, _user = _make_scoped_client(
            folder=folder, extra_codenames=["view_complianceassessment"]
        )

        response = client.get(f"/api/compliance-assessments/{assessment.id}/frameworks/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# Finding C — QuantitativeRiskStudyActionPlanList: zero RBAC filtering.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFindingCQuantitativeRiskStudyActionPlan:
    def _make_study_with_control(self, *, folder: Folder) -> tuple[QuantitativeRiskStudy, AppliedControl]:
        study = QuantitativeRiskStudy.objects.create(name="Study", folder=folder)
        scenario = QuantitativeRiskScenario.objects.create(
            name="Scenario", folder=folder, quantitative_risk_study=study
        )
        control = AppliedControl.objects.create(name="Control", folder=folder)
        hypothesis = QuantitativeRiskHypothesis.objects.create(
            name="Hypothesis",
            folder=folder,
            quantitative_risk_scenario=scenario,
            is_selected=True,
        )
        hypothesis.added_applied_controls.add(control)
        return study, control

    def test_cross_folder_user_cannot_list_action_plan_for_inaccessible_study(self):
        hidden_folder = _make_domain_folder("hidden-crq-folder")
        study, _control = self._make_study_with_control(folder=hidden_folder)

        other_folder = _make_domain_folder("unrelated-crq-folder")
        client, _user = _make_scoped_client(
            folder=other_folder,
            extra_codenames=["view_quantitativeriskstudy", "view_appliedcontrol"],
        )

        response = client.get(f"/api/crq/quantitative-risk-studies/{study.id}/action-plan/")

        assert response.status_code in (403, 404), (
            "a user with no visibility into the QuantitativeRiskStudy's folder could list "
            f"its action plan (got {response.status_code})"
        )

    def test_authorized_user_sees_accessible_control_only(self):
        folder = _make_domain_folder("authorized-crq-folder")
        study, control = self._make_study_with_control(folder=folder)

        client, _user = _make_scoped_client(
            folder=folder,
            extra_codenames=["view_quantitativeriskstudy", "view_appliedcontrol"],
        )

        response = client.get(f"/api/crq/quantitative-risk-studies/{study.id}/action-plan/")

        assert response.status_code == 200
        returned_ids = {str(item["id"]) for item in response.json()["results"]} if isinstance(
            response.json(), dict
        ) and "results" in response.json() else {
            str(item["id"]) for item in response.json()
        }
        assert str(control.id) in returned_ids


# ---------------------------------------------------------------------------
# Finding D — owner/assigned_to actions: unfiltered actor exposure across folders.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFindingDOwnerActions:
    def _make_actor(self) -> Actor:
        # ActorSyncMixin.save() on User auto-creates a matching Actor; fetch it rather than
        # creating a second one, which would violate the OneToOne(user) constraint.
        u = User.objects.create_user(f"actor-{uuid.uuid4().hex[:8]}@tests.com", is_published=True)
        return Actor.objects.get(user=u)

    def test_applied_control_owner_excludes_actor_from_inaccessible_folder(self):
        hidden_folder = _make_domain_folder("hidden-ac-owner-folder")
        hidden_control = AppliedControl.objects.create(name="Hidden control", folder=hidden_folder)
        hidden_actor = self._make_actor()
        hidden_control.owner.add(hidden_actor)

        visible_folder = _make_domain_folder("visible-ac-owner-folder")
        visible_control = AppliedControl.objects.create(name="Visible control", folder=visible_folder)
        visible_actor = self._make_actor()
        visible_control.owner.add(visible_actor)

        client, _user = _make_scoped_client(
            folder=visible_folder, extra_codenames=["view_appliedcontrol"]
        )

        response = client.get("/api/applied-controls/owner/")
        assert response.status_code == 200
        returned_ids = {item["id"] for item in response.json()}
        assert str(visible_actor.id) in returned_ids
        assert str(hidden_actor.id) not in returned_ids, (
            "an actor only linked to an AppliedControl outside the user's accessible "
            "perimeter was enumerated through the owner endpoint"
        )

    def test_evidence_owner_excludes_actor_from_inaccessible_folder(self):
        hidden_folder = _make_domain_folder("hidden-ev-owner-folder")
        hidden_evidence = Evidence.objects.create(name="Hidden evidence", folder=hidden_folder)
        hidden_actor = self._make_actor()
        hidden_evidence.owner.add(hidden_actor)

        visible_folder = _make_domain_folder("visible-ev-owner-folder")
        visible_evidence = Evidence.objects.create(name="Visible evidence", folder=visible_folder)
        visible_actor = self._make_actor()
        visible_evidence.owner.add(visible_actor)

        client, _user = _make_scoped_client(folder=visible_folder, extra_codenames=["view_evidence"])

        response = client.get("/api/evidences/owner/")
        assert response.status_code == 200
        returned_ids = {item["id"] for item in response.json()}
        assert str(visible_actor.id) in returned_ids
        assert str(hidden_actor.id) not in returned_ids

    def test_finding_owner_excludes_actor_from_inaccessible_folder(self):
        hidden_folder = _make_domain_folder("hidden-finding-owner-folder")
        hidden_assessment = FindingsAssessment.objects.create(
            name="Hidden assessment", folder=hidden_folder
        )
        hidden_finding = Finding.objects.create(
            name="Hidden finding", folder=hidden_folder, findings_assessment=hidden_assessment
        )
        hidden_actor = self._make_actor()
        hidden_finding.owner.add(hidden_actor)

        visible_folder = _make_domain_folder("visible-finding-owner-folder")
        visible_assessment = FindingsAssessment.objects.create(
            name="Visible assessment", folder=visible_folder
        )
        visible_finding = Finding.objects.create(
            name="Visible finding", folder=visible_folder, findings_assessment=visible_assessment
        )
        visible_actor = self._make_actor()
        visible_finding.owner.add(visible_actor)

        client, _user = _make_scoped_client(folder=visible_folder, extra_codenames=["view_finding"])

        response = client.get("/api/findings/owner/")
        assert response.status_code == 200
        returned_ids = {item["id"] for item in response.json()}
        assert str(visible_actor.id) in returned_ids
        assert str(hidden_actor.id) not in returned_ids

    def test_task_template_assigned_to_excludes_actor_from_inaccessible_folder(self):
        hidden_folder = _make_domain_folder("hidden-tt-assigned-folder")
        hidden_template = TaskTemplate.objects.create(name="Hidden template", folder=hidden_folder)
        hidden_actor = self._make_actor()
        hidden_template.assigned_to.add(hidden_actor)

        visible_folder = _make_domain_folder("visible-tt-assigned-folder")
        visible_template = TaskTemplate.objects.create(name="Visible template", folder=visible_folder)
        visible_actor = self._make_actor()
        visible_template.assigned_to.add(visible_actor)

        client, _user = _make_scoped_client(folder=visible_folder, extra_codenames=["view_tasktemplate"])

        response = client.get("/api/task-templates/assigned_to/")
        assert response.status_code == 200
        returned_ids = {item["id"] for item in response.json()}
        assert str(visible_actor.id) in returned_ids
        assert str(hidden_actor.id) not in returned_ids

    def test_right_request_owner_excludes_actor_from_inaccessible_folder(self):
        import datetime

        hidden_folder = _make_domain_folder("hidden-rr-owner-folder")
        hidden_rr = RightRequest.objects.create(
            name="Hidden right request", folder=hidden_folder, requested_on=datetime.date.today()
        )
        hidden_actor = self._make_actor()
        hidden_rr.owner.add(hidden_actor)

        visible_folder = _make_domain_folder("visible-rr-owner-folder")
        visible_rr = RightRequest.objects.create(
            name="Visible right request", folder=visible_folder, requested_on=datetime.date.today()
        )
        visible_actor = self._make_actor()
        visible_rr.owner.add(visible_actor)

        client, _user = _make_scoped_client(folder=visible_folder, extra_codenames=["view_rightrequest"])

        response = client.get("/api/privacy/right-requests/owner/")
        assert response.status_code == 200
        returned_ids = {item["id"] for item in response.json()}
        assert str(visible_actor.id) in returned_ids
        assert str(hidden_actor.id) not in returned_ids

    def test_processing_assigned_to_excludes_actor_from_inaccessible_folder(self):
        hidden_folder = _make_domain_folder("hidden-proc-assigned-folder")
        hidden_processing = Processing.objects.create(name="Hidden processing", folder=hidden_folder)
        hidden_actor = self._make_actor()
        hidden_processing.assigned_to.add(hidden_actor)

        visible_folder = _make_domain_folder("visible-proc-assigned-folder")
        visible_processing = Processing.objects.create(name="Visible processing", folder=visible_folder)
        visible_actor = self._make_actor()
        visible_processing.assigned_to.add(visible_actor)

        client, _user = _make_scoped_client(folder=visible_folder, extra_codenames=["view_processing"])

        response = client.get("/api/privacy/processings/assigned_to/")
        assert response.status_code == 200
        returned_ids = {item["id"] for item in response.json()}
        assert str(visible_actor.id) in returned_ids
        assert str(hidden_actor.id) not in returned_ids
