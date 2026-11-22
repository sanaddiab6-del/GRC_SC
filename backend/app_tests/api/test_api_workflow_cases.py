import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission

from core.models import WorkflowCase, WorkflowCaseApprovalStep
from iam.models import Folder, Role, RoleAssignment, User


@pytest.fixture
def workflow_folder(authenticated_client):
    folder = Folder.objects.create(
        name="workflow-api-domain", parent_folder=Folder.get_root_folder()
    )
    user = User.objects.get(email="admin@tests.com")
    codes = {
        "view_folder", "view_workflowcase", "add_workflowcase", "change_workflowcase",
        "view_workflowcaseapprovalstep", "add_workflowcaseapprovalstep",
    }
    permissions = Permission.objects.filter(codename__in=codes)
    assert permissions.count() == len(codes)
    role = Role.objects.create(name="workflow-api-test-role")
    role.permissions.set(permissions)
    assignment = RoleAssignment.objects.create(
        user=user, role=role, folder=folder, is_recursive=True
    )
    assignment.perimeter_folders.add(folder)
    return folder


@pytest.mark.django_db
def test_workflow_case_create_and_block_close(authenticated_client, workflow_folder):
    folder = workflow_folder

    create_response = authenticated_client.post(
        reverse("workflow-cases-list"),
        {
            "name": "Privileged Access Review Not Performed for Critical Systems",
            "description": "Admin accounts were not reviewed for two quarters.",
            "folder": str(folder.id),
            "workflow_type": WorkflowCase.WorkflowType.FINDING,
            "classification": WorkflowCase.Classification.CONTROL_DEFICIENCY,
            "status": WorkflowCase.Status.OPEN,
        },
        format="json",
    )

    assert create_response.status_code == 201

    workflow_case_id = create_response.json()["id"]
    close_response = authenticated_client.patch(
        reverse("workflow-cases-detail", args=[workflow_case_id]),
        {"status": WorkflowCase.Status.CLOSED},
        format="json",
    )

    assert close_response.status_code == 400
    assert "missing_closure_requirements" in close_response.json()
    workflow_case = WorkflowCase.objects.get(pk=workflow_case_id)
    assert workflow_case.status == WorkflowCase.Status.OPEN
    assert workflow_case.closed_at is None


@pytest.mark.django_db
def test_workflow_case_approval_step_approve_endpoint(authenticated_client, workflow_folder):
    admin_user = User.objects.get(email="admin@tests.com")
    folder = workflow_folder
    workflow_case = WorkflowCase.objects.create(
        name="Approval workflow case",
        folder=folder,
        status=WorkflowCase.Status.IN_REVIEW,
        require_approval_for_closure=True,
        require_evidence_for_closure=False,
        require_task_completion_for_closure=False,
    )
    step = WorkflowCaseApprovalStep.objects.create(
        workflow_case=workflow_case,
        approver=admin_user,
        sequence=1,
        folder=folder,
    )

    assert RoleAssignment.is_object_readable(admin_user, WorkflowCaseApprovalStep, step.id)
    approve_response = authenticated_client.post(
        reverse("workflow-case-approval-steps-approve", args=[step.id]),
        {"notes": "Approved after validating evidence chain."},
        format="json",
    )

    assert approve_response.status_code == 200
    step.refresh_from_db()
    assert step.status == WorkflowCaseApprovalStep.Status.APPROVED
    assert step.acted_at is not None


@pytest.mark.django_db
def test_workflow_case_residual_risk_reassessment_endpoint(authenticated_client, workflow_folder):
    folder = workflow_folder
    workflow_case = WorkflowCase.objects.create(
        name="Residual risk workflow case",
        folder=folder,
        status=WorkflowCase.Status.IN_PROGRESS,
    )

    user = User.objects.get(email="admin@tests.com")
    assert RoleAssignment.is_object_readable(user, WorkflowCase, workflow_case.id)
    response = authenticated_client.post(
        reverse("workflow-cases-reassess-residual-risk", args=[workflow_case.id]),
        {"summary": "Residual risk reduced from high to low after review restoration."},
        format="json",
    )

    assert response.status_code == 200
    workflow_case.refresh_from_db()
    assert workflow_case.residual_risk_summary.startswith("Residual risk reduced")
    assert workflow_case.residual_risk_reassessed_at is not None
    assert workflow_case.residual_risk_reassessed_by is not None


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["approve", "reassess"])
def test_workflow_actions_deny_outside_role_scope(authenticated_client, workflow_folder, action):
    user = User.objects.get(email="admin@tests.com")
    outside = Folder.objects.create(
        name="outside-workflow-domain", parent_folder=Folder.get_root_folder()
    )
    case = WorkflowCase.objects.create(name="Outside case", folder=outside)
    step = WorkflowCaseApprovalStep.objects.create(
        workflow_case=case, folder=outside, approver=user
    )
    if action == "approve":
        url = reverse("workflow-case-approval-steps-approve", args=[step.id])
        payload = {"notes": "Must not be saved"}
    else:
        url = reverse("workflow-cases-reassess-residual-risk", args=[case.id])
        payload = {"summary": "Must not be saved"}
    assert not RoleAssignment.is_object_readable(user, WorkflowCase, case.id)
    assert authenticated_client.post(url, payload, format="json").status_code == 404
    step.refresh_from_db()
    case.refresh_from_db()
    assert step.status == WorkflowCaseApprovalStep.Status.PENDING
    assert step.acted_at is None
    assert case.residual_risk_reassessed_at is None
    assert not case.events.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("restriction, expected", [("unassigned", 403), ("previous_pending", 400)])
def test_workflow_approval_keeps_actor_and_sequence_guards(
    authenticated_client, workflow_folder, restriction, expected
):
    user = User.objects.get(email="admin@tests.com")
    case = WorkflowCase.objects.create(name="Restricted approval", folder=workflow_folder)
    approver = user
    if restriction == "unassigned":
        approver = User.objects.create_user("other-approver@tests.com")
    else:
        WorkflowCaseApprovalStep.objects.create(
            workflow_case=case, folder=workflow_folder, approver=user, sequence=1
        )
    step = WorkflowCaseApprovalStep.objects.create(
        workflow_case=case, folder=workflow_folder, approver=approver, sequence=2
    )
    response = authenticated_client.post(
        reverse("workflow-case-approval-steps-approve", args=[step.id]), {}, format="json"
    )
    assert response.status_code == expected
    step.refresh_from_db()
    assert step.status == WorkflowCaseApprovalStep.Status.PENDING
    assert step.acted_at is None
    assert not case.events.exists()


@pytest.mark.django_db
def test_workflow_case_create_denies_outside_role_scope(authenticated_client, workflow_folder):
    outside = Folder.objects.create(
        name="outside-workflow-create-domain", parent_folder=Folder.get_root_folder()
    )
    response = authenticated_client.post(
        reverse("workflow-cases-list"), {"name": "Denied case", "folder": str(outside.id)},
        format="json",
    )
    assert response.status_code == 403
    assert not WorkflowCase.objects.filter(name="Denied case").exists()
