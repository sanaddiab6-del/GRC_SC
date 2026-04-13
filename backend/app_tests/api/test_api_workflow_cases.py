import pytest
from django.urls import reverse
from django.utils import timezone

from core.models import WorkflowCase, WorkflowCaseApprovalStep
from iam.models import Folder, User


@pytest.mark.django_db
def test_workflow_case_create_and_block_close(authenticated_client):
    folder = Folder.objects.create(name="workflow-case-api-folder")

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


@pytest.mark.django_db
def test_workflow_case_approval_step_approve_endpoint(authenticated_client):
    admin_user = User.objects.get(email="admin@tests.com")
    folder = Folder.objects.create(name="workflow-case-approval-folder")
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
def test_workflow_case_residual_risk_reassessment_endpoint(authenticated_client):
    folder = Folder.objects.create(name="workflow-case-risk-folder")
    workflow_case = WorkflowCase.objects.create(
        name="Residual risk workflow case",
        folder=folder,
        status=WorkflowCase.Status.IN_PROGRESS,
    )

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