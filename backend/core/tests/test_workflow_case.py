import pytest
from django.utils import timezone

from core.models import (
    Evidence,
    TaskNode,
    TaskTemplate,
    WorkflowCase,
    WorkflowCaseApprovalStep,
)
from iam.models import Folder, User


@pytest.mark.django_db
class TestWorkflowCase:
    def test_workflow_case_blocks_closure_until_criteria_are_met(self):
        folder = Folder.objects.create(name="workflow-folder")
        approver = User.objects.create_user("approver@tests.com", is_published=True)

        task_template = TaskTemplate.objects.create(
            name="Perform privileged access review",
            folder=folder,
            is_recurrent=False,
            task_date=timezone.now().date(),
        )
        TaskNode.objects.create(
            task_template=task_template,
            due_date=timezone.now().date(),
            scheduled_date=timezone.now().date(),
            status="pending",
            folder=folder,
        )

        workflow_case = WorkflowCase.objects.create(
            name="Privileged Access Review Not Performed",
            folder=folder,
            status=WorkflowCase.Status.IN_PROGRESS,
            require_evidence_for_closure=True,
            require_approval_for_closure=True,
            require_task_completion_for_closure=True,
            require_residual_risk_reassessment=True,
            require_recurring_control_for_closure=True,
        )
        workflow_case.task_templates.add(task_template)

        approval_step = WorkflowCaseApprovalStep.objects.create(
            workflow_case=workflow_case,
            approver=approver,
            sequence=1,
            folder=folder,
        )

        can_close, missing = workflow_case.can_close()

        assert can_close is False
        assert set(missing) == {
            "evidence",
            "approval",
            "tasks",
            "recurring_control",
            "residual_risk_reassessment",
        }

        evidence = Evidence.objects.create(name="Review evidence", folder=folder)
        workflow_case.evidences.add(evidence)
        approval_step.status = WorkflowCaseApprovalStep.Status.APPROVED
        approval_step.save()
        task_node = task_template.tasknode_set.get()
        task_node.status = "completed"
        task_node.save()
        workflow_case.recurring_control_confirmed = True
        workflow_case.residual_risk_reassessed_at = timezone.now()
        workflow_case.residual_risk_summary = "Residual risk reduced to acceptable level."
        workflow_case.save()

        can_close, missing = workflow_case.can_close()

        assert can_close is True
        assert missing == []

    def test_workflow_case_approval_state_reflects_step_progress(self):
        folder = Folder.objects.create(name="approval-folder")
        approver_one = User.objects.create_user("approver1@tests.com", is_published=True)
        approver_two = User.objects.create_user("approver2@tests.com", is_published=True)

        workflow_case = WorkflowCase.objects.create(
            name="Approval chain case",
            folder=folder,
            status=WorkflowCase.Status.IN_REVIEW,
        )

        first_step = WorkflowCaseApprovalStep.objects.create(
            workflow_case=workflow_case,
            approver=approver_one,
            sequence=1,
            folder=folder,
        )
        second_step = WorkflowCaseApprovalStep.objects.create(
            workflow_case=workflow_case,
            approver=approver_two,
            sequence=2,
            folder=folder,
        )

        assert workflow_case.approval_state == "pending"

        first_step.status = WorkflowCaseApprovalStep.Status.APPROVED
        first_step.save()
        workflow_case.refresh_from_db()
        assert workflow_case.approval_state == "pending"

        second_step.status = WorkflowCaseApprovalStep.Status.APPROVED
        second_step.save()
        workflow_case.refresh_from_db()
        assert workflow_case.approval_state == "approved"