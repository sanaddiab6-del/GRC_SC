from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    Evidence,
    Finding,
    FindingsAssessment,
    Incident,
    RequirementAssessment,
    RiskScenario,
    SecurityException,
    WorkflowCase,
    WorkflowCaseApprovalStep,
    WorkflowCaseEvent,
)


class Command(BaseCommand):
    help = (
        "Backfill workflow cases from existing findings, assessments, risks, incidents, "
        "and security exceptions."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview the workflow-case backfill without committing changes.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional per-model limit when backfilling objects.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        dry_run = options["dry_run"]
        stats = defaultdict(lambda: {"created": 0, "updated": 0})

        with transaction.atomic():
            for findings_assessment in self._limited_queryset(
                FindingsAssessment.objects.prefetch_related(
                    "authors",
                    "reviewers",
                    "evidences",
                    "findings__owner",
                    "findings__evidences",
                    "findings__applied_controls",
                ),
                limit,
            ):
                created = self._backfill_findings_assessment(findings_assessment)
                stats["findings_assessments"]["created" if created else "updated"] += 1

            requirement_queryset = RequirementAssessment.objects.prefetch_related(
                "evidences",
                "applied_controls",
                "security_exceptions",
                "assignments__actor",
                "compliance_assessment__authors",
                "compliance_assessment__reviewers",
            ).exclude(result=RequirementAssessment.Result.COMPLIANT)
            for requirement_assessment in self._limited_queryset(
                requirement_queryset,
                limit,
            ):
                created = self._backfill_requirement_assessment(requirement_assessment)
                stats["requirement_assessments"][
                    "created" if created else "updated"
                ] += 1

            for risk_scenario in self._limited_queryset(
                RiskScenario.objects.prefetch_related(
                    "assets",
                    "owner",
                    "applied_controls",
                    "security_exceptions",
                ),
                limit,
            ):
                created = self._backfill_risk_scenario(risk_scenario)
                stats["risk_scenarios"]["created" if created else "updated"] += 1

            for incident in self._limited_queryset(
                Incident.objects.prefetch_related("assets", "owners"),
                limit,
            ):
                created = self._backfill_incident(incident)
                stats["incidents"]["created" if created else "updated"] += 1

            for security_exception in self._limited_queryset(
                SecurityException.objects.prefetch_related("owners"),
                limit,
            ):
                created = self._backfill_security_exception(security_exception)
                stats["security_exceptions"]["created" if created else "updated"] += 1

            if dry_run:
                transaction.set_rollback(True)

        for label, values in stats.items():
            self.stdout.write(
                self.style.SUCCESS(
                    f"{label}: created={values['created']} updated={values['updated']}"
                )
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run complete. No changes were committed."))

    @staticmethod
    def _limited_queryset(queryset, limit):
        return queryset[:limit] if limit else queryset

    @staticmethod
    def _set_many_to_many(manager, values):
        items = [value for value in values if value is not None]
        if items:
            manager.add(*items)

    @staticmethod
    def _incident_severity_to_case_severity(value):
        mapping = {
            Incident.Severity.SEV1: 4,
            Incident.Severity.SEV2: 3,
            Incident.Severity.SEV3: 2,
            Incident.Severity.SEV4: 1,
            Incident.Severity.SEV5: 0,
            Incident.Severity.UNDEFINED: -1,
        }
        return mapping.get(value, -1)

    @staticmethod
    def _assessment_status_to_case_status(value):
        mapping = {
            "planned": WorkflowCase.Status.OPEN,
            "in_progress": WorkflowCase.Status.IN_PROGRESS,
            "in_review": WorkflowCase.Status.IN_REVIEW,
            "done": WorkflowCase.Status.CLOSED,
            "deprecated": WorkflowCase.Status.CLOSED,
        }
        return mapping.get(value, WorkflowCase.Status.OPEN)

    @staticmethod
    def _finding_status_to_case_status(value):
        mapping = {
            Finding.Status.UNDEFINED: WorkflowCase.Status.OPEN,
            Finding.Status.IDENTIFIED: WorkflowCase.Status.OPEN,
            Finding.Status.CONFIRMED: WorkflowCase.Status.OPEN,
            Finding.Status.ASSIGNED: WorkflowCase.Status.IN_PROGRESS,
            Finding.Status.IN_PROGRESS: WorkflowCase.Status.IN_PROGRESS,
            Finding.Status.MITIGATED: WorkflowCase.Status.IN_REVIEW,
            Finding.Status.RESOLVED: WorkflowCase.Status.CLOSED,
            Finding.Status.CLOSED: WorkflowCase.Status.CLOSED,
            Finding.Status.DISMISSED: WorkflowCase.Status.CLOSED,
            Finding.Status.DEPRECATED: WorkflowCase.Status.CLOSED,
        }
        return mapping.get(value, WorkflowCase.Status.OPEN)

    @staticmethod
    def _incident_status_to_case_status(value):
        mapping = {
            Incident.Status.NEW: WorkflowCase.Status.OPEN,
            Incident.Status.ONGOING: WorkflowCase.Status.IN_PROGRESS,
            Incident.Status.RESOLVED: WorkflowCase.Status.IN_REVIEW,
            Incident.Status.CLOSED: WorkflowCase.Status.CLOSED,
            Incident.Status.DISMISSED: WorkflowCase.Status.CLOSED,
        }
        return mapping.get(value, WorkflowCase.Status.OPEN)

    @staticmethod
    def _security_exception_status_to_case_status(value):
        mapping = {
            SecurityException.Status.DRAFT: WorkflowCase.Status.DRAFT,
            SecurityException.Status.IN_REVIEW: WorkflowCase.Status.IN_REVIEW,
            SecurityException.Status.APPROVED: WorkflowCase.Status.CLOSED_WITH_MONITORING,
            SecurityException.Status.RESOLVED: WorkflowCase.Status.CLOSED,
            SecurityException.Status.EXPIRED: WorkflowCase.Status.CLOSED,
            SecurityException.Status.DEPRECATED: WorkflowCase.Status.CLOSED,
        }
        return mapping.get(value, WorkflowCase.Status.OPEN)

    @staticmethod
    def _risk_treatment_to_decision(value):
        mapping = {
            "accept": WorkflowCase.TreatmentDecision.ACCEPT,
            "mitigate": WorkflowCase.TreatmentDecision.REMEDIATE,
            "avoid": WorkflowCase.TreatmentDecision.ESCALATE,
            "transfer": WorkflowCase.TreatmentDecision.ESCALATE,
            "open": WorkflowCase.TreatmentDecision.UNDECIDED,
        }
        return mapping.get(value, WorkflowCase.TreatmentDecision.UNDECIDED)

    def _create_backfill_event(self, workflow_case, source_name):
        WorkflowCaseEvent.objects.get_or_create(
            workflow_case=workflow_case,
            event_type="backfilled",
            event_notes=source_name,
            defaults={"folder": workflow_case.folder},
        )

    def _sync_workflow_case(self, workflow_case, *, status, severity, treatment_decision, monitoring_required=False):
        fields_to_update = []
        if workflow_case.status != status:
            workflow_case.status = status
            fields_to_update.extend(["status", "closed_at"])
        if workflow_case.severity != severity:
            workflow_case.severity = severity
            fields_to_update.append("severity")
        if workflow_case.treatment_decision != treatment_decision:
            workflow_case.treatment_decision = treatment_decision
            fields_to_update.append("treatment_decision")
        if workflow_case.monitoring_required != monitoring_required:
            workflow_case.monitoring_required = monitoring_required
            fields_to_update.append("monitoring_required")
        if fields_to_update:
            workflow_case.save(update_fields=fields_to_update)

    def _backfill_findings_assessment(self, findings_assessment):
        defaults = {
            "name": findings_assessment.name,
            "description": findings_assessment.description,
            "folder": findings_assessment.folder,
            "workflow_type": WorkflowCase.WorkflowType.FINDING,
            "classification": (
                WorkflowCase.Classification.AUDIT_FINDING
                if findings_assessment.category == FindingsAssessment.Category.AUDIT
                else WorkflowCase.Classification.CONTROL_DEFICIENCY
            ),
            "status": self._assessment_status_to_case_status(findings_assessment.status),
            "severity": max(
                [-1] + [finding.severity for finding in findings_assessment.findings.all()]
            ),
            "treatment_decision": WorkflowCase.TreatmentDecision.REMEDIATE,
            "domain": getattr(findings_assessment.folder, "name", ""),
            "require_evidence_for_closure": True,
            "require_approval_for_closure": True,
            "require_task_completion_for_closure": True,
            "eta": findings_assessment.eta,
            "due_date": findings_assessment.due_date,
        }
        workflow_case, created = WorkflowCase.objects.get_or_create(
            findings_assessments=findings_assessment,
            defaults=defaults,
        )
        self._sync_workflow_case(
            workflow_case,
            status=defaults["status"],
            severity=defaults["severity"],
            treatment_decision=defaults["treatment_decision"],
        )
        self._set_many_to_many(workflow_case.findings_assessments, [findings_assessment])
        self._set_many_to_many(workflow_case.reviewers, findings_assessment.reviewers.all())
        self._set_many_to_many(workflow_case.owners, findings_assessment.authors.all())
        self._set_many_to_many(workflow_case.evidences, findings_assessment.evidences.all())

        findings = list(findings_assessment.findings.all())
        self._set_many_to_many(workflow_case.findings, findings)
        for finding in findings:
            self._set_many_to_many(workflow_case.owners, finding.owner.all())
            self._set_many_to_many(workflow_case.evidences, finding.evidences.all())
            self._set_many_to_many(workflow_case.applied_controls, finding.applied_controls.all())

        self._create_backfill_event(workflow_case, str(findings_assessment))
        return created

    def _backfill_requirement_assessment(self, requirement_assessment):
        defaults = {
            "name": str(requirement_assessment),
            "description": requirement_assessment.observation,
            "folder": requirement_assessment.folder,
            "workflow_type": WorkflowCase.WorkflowType.FINDING,
            "classification": WorkflowCase.Classification.COMPLIANCE_GAP,
            "status": self._assessment_status_to_case_status(requirement_assessment.status),
            "severity": 3
            if requirement_assessment.result == RequirementAssessment.Result.NON_COMPLIANT
            else 2,
            "treatment_decision": WorkflowCase.TreatmentDecision.REMEDIATE,
            "domain": getattr(requirement_assessment.folder, "name", ""),
            "require_evidence_for_closure": True,
            "require_approval_for_closure": True,
            "require_task_completion_for_closure": True,
            "eta": requirement_assessment.eta,
            "due_date": requirement_assessment.due_date,
        }
        workflow_case, created = WorkflowCase.objects.get_or_create(
            requirement_assessments=requirement_assessment,
            defaults=defaults,
        )
        self._sync_workflow_case(
            workflow_case,
            status=defaults["status"],
            severity=defaults["severity"],
            treatment_decision=defaults["treatment_decision"],
        )
        self._set_many_to_many(
            workflow_case.requirement_assessments,
            [requirement_assessment],
        )
        self._set_many_to_many(workflow_case.evidences, requirement_assessment.evidences.all())
        self._set_many_to_many(
            workflow_case.applied_controls,
            requirement_assessment.applied_controls.all(),
        )
        self._set_many_to_many(
            workflow_case.security_exceptions,
            requirement_assessment.security_exceptions.all(),
        )
        self._set_many_to_many(
            workflow_case.reviewers,
            requirement_assessment.compliance_assessment.reviewers.all(),
        )
        self._set_many_to_many(
            workflow_case.owners,
            requirement_assessment.compliance_assessment.authors.all(),
        )
        for assignment in requirement_assessment.assignments.all():
            self._set_many_to_many(workflow_case.owners, assignment.actor.all())

        self._create_backfill_event(workflow_case, str(requirement_assessment))
        return created

    def _backfill_risk_scenario(self, risk_scenario):
        defaults = {
            "name": risk_scenario.name,
            "description": risk_scenario.description or risk_scenario.justification,
            "folder": risk_scenario.folder,
            "workflow_type": WorkflowCase.WorkflowType.RISK,
            "classification": WorkflowCase.Classification.RISK_OBSERVATION,
            "status": self._assessment_status_to_case_status(risk_scenario.risk_assessment.status),
            "severity": max(-1, min(risk_scenario.current_level, 4)),
            "treatment_decision": self._risk_treatment_to_decision(risk_scenario.treatment),
            "domain": getattr(risk_scenario.folder, "name", ""),
            "require_evidence_for_closure": False,
            "require_approval_for_closure": False,
            "require_task_completion_for_closure": True,
            "require_residual_risk_reassessment": True,
            "monitoring_required": risk_scenario.treatment == "accept",
        }
        workflow_case, created = WorkflowCase.objects.get_or_create(
            risk_scenarios=risk_scenario,
            defaults=defaults,
        )
        self._sync_workflow_case(
            workflow_case,
            status=defaults["status"],
            severity=defaults["severity"],
            treatment_decision=defaults["treatment_decision"],
            monitoring_required=defaults["monitoring_required"],
        )
        self._set_many_to_many(workflow_case.risk_scenarios, [risk_scenario])
        self._set_many_to_many(workflow_case.affected_assets, risk_scenario.assets.all())
        self._set_many_to_many(workflow_case.applied_controls, risk_scenario.applied_controls.all())
        self._set_many_to_many(workflow_case.owners, risk_scenario.owner.all())
        self._set_many_to_many(
            workflow_case.security_exceptions,
            risk_scenario.security_exceptions.all(),
        )

        self._create_backfill_event(workflow_case, str(risk_scenario))
        return created

    def _backfill_incident(self, incident):
        defaults = {
            "name": incident.name,
            "description": incident.description,
            "folder": incident.folder,
            "workflow_type": WorkflowCase.WorkflowType.INCIDENT,
            "classification": WorkflowCase.Classification.INCIDENT,
            "status": self._incident_status_to_case_status(incident.status),
            "severity": self._incident_severity_to_case_severity(incident.severity),
            "treatment_decision": WorkflowCase.TreatmentDecision.REMEDIATE,
            "domain": getattr(incident.folder, "name", ""),
            "require_evidence_for_closure": False,
            "require_approval_for_closure": False,
            "require_task_completion_for_closure": True,
        }
        workflow_case, created = WorkflowCase.objects.get_or_create(
            incidents=incident,
            defaults=defaults,
        )
        self._sync_workflow_case(
            workflow_case,
            status=defaults["status"],
            severity=defaults["severity"],
            treatment_decision=defaults["treatment_decision"],
        )
        self._set_many_to_many(workflow_case.incidents, [incident])
        self._set_many_to_many(workflow_case.affected_assets, incident.assets.all())
        self._set_many_to_many(workflow_case.owners, incident.owners.all())

        self._create_backfill_event(workflow_case, str(incident))
        return created

    def _backfill_security_exception(self, security_exception):
        defaults = {
            "name": security_exception.name,
            "description": security_exception.description or security_exception.observation,
            "folder": security_exception.folder,
            "workflow_type": WorkflowCase.WorkflowType.EXCEPTION,
            "classification": WorkflowCase.Classification.SECURITY_EXCEPTION,
            "status": self._security_exception_status_to_case_status(security_exception.status),
            "severity": security_exception.severity,
            "treatment_decision": WorkflowCase.TreatmentDecision.MONITOR,
            "domain": getattr(security_exception.folder, "name", ""),
            "require_evidence_for_closure": False,
            "require_approval_for_closure": True,
            "require_task_completion_for_closure": False,
            "monitoring_required": security_exception.status == SecurityException.Status.APPROVED,
        }
        workflow_case, created = WorkflowCase.objects.get_or_create(
            security_exceptions=security_exception,
            defaults=defaults,
        )
        self._sync_workflow_case(
            workflow_case,
            status=defaults["status"],
            severity=defaults["severity"],
            treatment_decision=defaults["treatment_decision"],
            monitoring_required=defaults["monitoring_required"],
        )
        self._set_many_to_many(workflow_case.security_exceptions, [security_exception])
        self._set_many_to_many(workflow_case.owners, security_exception.owners.all())

        if security_exception.approver:
            approval_step, approval_created = WorkflowCaseApprovalStep.objects.get_or_create(
                workflow_case=workflow_case,
                sequence=1,
                defaults={
                    "approver": security_exception.approver,
                    "folder": workflow_case.folder,
                    "status": (
                        WorkflowCaseApprovalStep.Status.APPROVED
                        if security_exception.status
                        in (
                            SecurityException.Status.APPROVED,
                            SecurityException.Status.RESOLVED,
                            SecurityException.Status.EXPIRED,
                        )
                        else WorkflowCaseApprovalStep.Status.PENDING
                    ),
                },
            )
            if not approval_created and approval_step.approver != security_exception.approver:
                approval_step.approver = security_exception.approver
                approval_step.save(update_fields=["approver"])

        self._create_backfill_event(workflow_case, str(security_exception))
        return created