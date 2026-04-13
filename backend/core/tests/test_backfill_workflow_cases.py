from django.core.management import call_command

from core.models import Evidence, Finding, FindingsAssessment, WorkflowCase
from iam.models import Folder


def test_backfill_workflow_cases_command_is_idempotent(db):
    folder = Folder.objects.create(name="workflow-backfill-folder")
    findings_assessment = FindingsAssessment.objects.create(
        name="Quarterly privileged access review",
        folder=folder,
        category=FindingsAssessment.Category.AUDIT,
        status=FindingsAssessment.Status.IN_PROGRESS,
    )
    evidence = Evidence.objects.create(name="Access review extract", folder=folder)
    findings_assessment.evidences.add(evidence)
    finding = Finding.objects.create(
        name="Privileged accounts were not reviewed",
        folder=folder,
        findings_assessment=findings_assessment,
        severity=3,
        status=Finding.Status.IN_PROGRESS,
    )
    finding.evidences.add(evidence)

    call_command("backfill_workflow_cases")

    workflow_case = WorkflowCase.objects.get(findings_assessments=findings_assessment)
    assert workflow_case.workflow_type == WorkflowCase.WorkflowType.FINDING
    assert workflow_case.classification == WorkflowCase.Classification.AUDIT_FINDING
    assert workflow_case.status == WorkflowCase.Status.IN_PROGRESS
    assert workflow_case.findings.filter(id=finding.id).exists()
    assert workflow_case.evidences.filter(id=evidence.id).exists()

    call_command("backfill_workflow_cases")

    assert WorkflowCase.objects.filter(findings_assessments=findings_assessment).count() == 1