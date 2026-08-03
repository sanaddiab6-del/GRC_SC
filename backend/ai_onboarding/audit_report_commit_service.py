from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import ComplianceAssessment, Evidence
from core.serializers import EvidenceWriteSerializer
from iam.models import Folder, RoleAssignment

from .audit_report_commit_guardrails import (
    AuditReportCommitValidationError,
    validate_audit_report_commit_guardrails,
)
from .audit_report_commit_serializers import MAX_REPORT_NAME_LENGTH


# Step 11B saves a reviewed Step 11A report draft as a platform document. The platform has
# no dedicated report object for this flow, so the existing core.Evidence record - the same
# model Step 5B already writes - is the safe target: the rendered draft is stored as its
# description and the record stays at the platform's own DRAFT status. Step 11B never marks
# a report final, never publishes or signs anything, never changes the audit status, and
# never certifies compliance. No AI provider module is imported or called here.
RECORD_TYPE = "evidence"

# The saved document always opens with this marker so a reader can tell at a glance that it
# is an AI-assisted draft awaiting human review.
REPORT_MARKER = "[AI onboarding Step 11B - reviewed report draft, pending human review]"


@dataclass
class PlannedReportAction:
    source_temporary_id: str
    decision: str
    status: str
    detail: str
    record_type: str = RECORD_TYPE
    target_name: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "source_temporary_id": self.source_temporary_id,
            "decision": self.decision,
            "status": self.status,
            "detail": self.detail,
            "record_type": self.record_type,
        }
        if self.target_name:
            payload["target_name"] = self.target_name
        return payload


@dataclass
class WritePlan:
    source_temporary_id: str
    decision: str
    target_name: str
    create_payload: dict[str, Any] | None = None
    existing_instance: Any = None
    assessment: Any = None


class AiAuditReportCommitService:
    """Deterministic Step 11B commit. No AI provider is imported or called here."""

    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedReportAction] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.rejected_records: list[dict[str, Any]] = []
        self.deferred_records: list[dict[str, Any]] = []
        self.skipped_records: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    # ---- entry point -------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        validate_audit_report_commit_guardrails(self.payload)

        plans = self._plan_and_validate()

        if self.payload["dry_run"]:
            return self._build_response(dry_run=True, commit_status=self._dry_run_status())

        if self.blocking_errors:
            raise AuditReportCommitValidationError(
                "ai_audit_report_commit_blocked",
                "The approved Step 11B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(dry_run=False, commit_status="blocked"),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(plans)
        except AuditReportCommitValidationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a rolled-back commit
            self.created_records = []
            self.reused_records = []
            raise AuditReportCommitValidationError(
                "transaction_aborted",
                "Step 11B transaction failed and all writes were rolled back.",
                status_code=422,
                response_payload=self._build_response(
                    dry_run=False,
                    commit_status="blocked",
                    extra_blocking_errors=[
                        {"code": "transaction_aborted", "detail": str(exc), "field": None}
                    ],
                ),
            )

        return self._build_response(dry_run=False, commit_status=self._write_status())

    # ---- planning ----------------------------------------------------------

    def _plan_and_validate(self) -> list[WritePlan]:
        folder = self._resolve_folder()
        assessment = self._resolve_assessment(folder)

        plans: list[WritePlan] = []
        planned_names: set[str] = set()

        for index, decision in enumerate(self.payload.get("decisions") or []):
            self._plan_decision(index, decision, folder, assessment, plans, planned_names)

        return plans

    def _plan_decision(
        self,
        index: int,
        decision: dict[str, Any],
        folder: Folder | None,
        assessment: ComplianceAssessment | None,
        plans: list[WritePlan],
        planned_names: set[str],
    ) -> None:
        field_prefix = f"decisions[{index}]"
        temporary_id = decision["temporary_id"]
        action = decision["decision"]
        payload = decision.get("payload") or {}
        label = (payload.get("report_title") or "").strip()[:MAX_REPORT_NAME_LENGTH]

        if not decision.get("selected"):
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": label or None,
                    "skip_reason": "not_selected",
                }
            )
            self.planned_actions.append(
                PlannedReportAction(
                    temporary_id, action, "skipped",
                    "Decision was not selected by the reviewer.", target_name=label or None,
                )
            )
            return

        if action == "reject":
            self.rejected_records.append(
                {"source_temporary_id": temporary_id, "title": label or None}
            )
            self.planned_actions.append(
                PlannedReportAction(
                    temporary_id, "reject", "ok",
                    "Report draft rejected by reviewer.", target_name=label or None,
                )
            )
            return

        if action == "defer":
            self.deferred_records.append(
                {"source_temporary_id": temporary_id, "title": label or None}
            )
            self.planned_actions.append(
                PlannedReportAction(
                    temporary_id, "defer", "ok",
                    "Report draft deferred by reviewer.", target_name=label or None,
                )
            )
            return

        if folder is None:
            self.planned_actions.append(
                PlannedReportAction(
                    temporary_id, action, "blocked",
                    "A valid folder_reference is required before Step 11B can save a report "
                    "draft.",
                    target_name=label or None,
                )
            )
            return

        if action == "reuse":
            self._plan_reuse(field_prefix, temporary_id, decision, folder, assessment, plans)
            return

        self._plan_create(
            field_prefix, temporary_id, payload, label, folder, assessment, plans, planned_names
        )

    def _plan_reuse(
        self,
        field_prefix: str,
        temporary_id: str,
        decision: dict[str, Any],
        folder: Folder,
        assessment: ComplianceAssessment | None,
        plans: list[WritePlan],
    ) -> None:
        existing_id = decision["existing_record_reference"]
        instance = (
            Evidence.objects.filter(id=existing_id).select_related("folder").first()
        )

        if instance is None:
            self._block(
                "reuse_target_not_found",
                "existing_record_reference does not match an existing Evidence document.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        if not RoleAssignment.is_object_readable(self.user, Evidence, instance.id):
            self._block(
                "permission_denied",
                "You do not have permission to reuse the selected Evidence document.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        if str(instance.folder_id) != str(folder.id):
            self._block(
                "reuse_out_of_scope",
                "existing_record_reference must belong to folder_reference.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="reuse",
                target_name=instance.name,
                existing_instance=instance,
                assessment=assessment,
            )
        )
        self.planned_actions.append(
            PlannedReportAction(
                temporary_id, "reuse", "planned",
                "The existing report document would be reused without mutation.",
                target_name=instance.name,
            )
        )

    def _plan_create(
        self,
        field_prefix: str,
        temporary_id: str,
        payload: dict[str, Any],
        label: str,
        folder: Folder,
        assessment: ComplianceAssessment | None,
        plans: list[WritePlan],
        planned_names: set[str],
    ) -> None:
        if label.lower() in planned_names:
            self.warnings.append(
                {
                    "code": "duplicate_in_batch_skipped",
                    "detail": (
                        f"Another selected decision already saves a report named '{label}'; "
                        "this duplicate was skipped."
                    ),
                    "field": f"{field_prefix}.payload.report_title",
                }
            )
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": label,
                    "skip_reason": "duplicate_in_batch",
                }
            )
            self.planned_actions.append(
                PlannedReportAction(
                    temporary_id, "create", "skipped",
                    "Duplicate report title within the submitted batch.", target_name=label,
                )
            )
            return

        # Duplicate reuse: an existing document with the same name in the same folder is
        # reused rather than overwritten, so a previously saved report is never replaced.
        existing = Evidence.objects.filter(folder=folder, name__iexact=label).first()
        if existing is not None:
            self.warnings.append(
                {
                    "code": "duplicate_reused",
                    "detail": (
                        f"An existing document named '{label}' was found in the folder and "
                        "will be reused. Step 11B never overwrites a previously saved report."
                    ),
                    "field": f"{field_prefix}.payload.report_title",
                }
            )
            planned_names.add(label.lower())
            plans.append(
                WritePlan(
                    source_temporary_id=temporary_id,
                    decision="reuse",
                    target_name=existing.name,
                    existing_instance=existing,
                    assessment=assessment,
                )
            )
            self.planned_actions.append(
                PlannedReportAction(
                    temporary_id, "reuse", "planned",
                    "An existing report document with the same title would be reused.",
                    target_name=existing.name,
                )
            )
            return

        if not self._has_permission("add_evidence", folder):
            self._block(
                "permission_denied",
                "You do not have permission to add documents in the selected scope.",
                f"{field_prefix}.payload.report_title",
                temporary_id,
                "create",
            )
            return

        create_payload = {
            "name": label,
            "description": _render_report(payload),
            "folder": str(folder.id),
            # The platform's own draft status: Step 11B never marks a report final.
            "status": Evidence.Status.DRAFT,
        }
        if not self._create_payload_is_valid(create_payload, field_prefix):
            return

        self.warnings.append(
            {
                "code": "report_saved_as_draft_document",
                "detail": (
                    "The platform has no dedicated audit report object for this flow, so the "
                    "reviewed draft is saved as a DRAFT document record with the rendered "
                    "report as its description. The report is not marked final, not "
                    "published, and no audit status is changed."
                ),
                "field": f"{field_prefix}.payload",
            }
        )

        planned_names.add(label.lower())
        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="create",
                target_name=label,
                create_payload=create_payload,
                assessment=assessment,
            )
        )
        self.planned_actions.append(
            PlannedReportAction(
                temporary_id, "create", "planned",
                "A DRAFT document holding the reviewed report draft would be created.",
                target_name=label,
            )
        )

    # ---- resolution helpers ------------------------------------------------

    def _resolve_folder(self) -> Folder | None:
        folder = Folder.objects.filter(id=self.payload["folder_reference"]).first()
        if folder is None:
            self.blocking_errors.append(
                {
                    "code": "folder_not_found",
                    "detail": "folder_reference does not match an existing Folder.",
                    "field": "folder_reference",
                }
            )
            return None
        if not RoleAssignment.is_object_readable(self.user, Folder, folder.id):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to use the selected Folder.",
                    "field": "folder_reference",
                }
            )
            return None
        return folder

    def _resolve_assessment(self, folder: Folder | None) -> ComplianceAssessment | None:
        """Optional: when supplied, the saved document is linked to the audit."""
        reference = self.payload.get("assessment_reference")
        if not reference:
            self.warnings.append(
                {
                    "code": "assessment_link_not_applied",
                    "detail": (
                        "No assessment_reference was supplied, so the saved report document is "
                        "not linked to an audit."
                    ),
                    "field": "assessment_reference",
                }
            )
            return None

        assessment = (
            ComplianceAssessment.objects.filter(id=reference)
            .select_related("folder")
            .first()
        )
        if assessment is None:
            self.blocking_errors.append(
                {
                    "code": "assessment_not_found",
                    "detail": (
                        "assessment_reference does not match an existing ComplianceAssessment."
                    ),
                    "field": "assessment_reference",
                }
            )
            return None

        if not RoleAssignment.is_object_readable(self.user, ComplianceAssessment, assessment.id):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to use the selected ComplianceAssessment.",
                    "field": "assessment_reference",
                }
            )
            return None

        if folder is not None and str(assessment.folder_id) != str(folder.id):
            self.blocking_errors.append(
                {
                    "code": "assessment_out_of_scope",
                    "detail": "assessment_reference must belong to folder_reference.",
                    "field": "assessment_reference",
                }
            )
            return None

        if assessment.is_locked:
            self.blocking_errors.append(
                {
                    "code": "assessment_locked",
                    "detail": "The selected audit is locked and cannot be modified.",
                    "field": "assessment_reference",
                }
            )
            return None

        return assessment

    def _has_permission(self, codename: str, folder: Folder) -> bool:
        permission = Permission.objects.filter(codename=codename).first()
        if permission is None:
            return False
        return RoleAssignment.is_access_allowed(self.user, permission, folder)

    def _create_payload_is_valid(self, payload: dict[str, Any], field_prefix: str) -> bool:
        serializer = EvidenceWriteSerializer(data=payload, context={"request": self.request})
        if serializer.is_valid():
            return True
        self.blocking_errors.append(
            {
                "code": "invalid_record_payload",
                "detail": "The reviewed report draft did not pass platform validation.",
                "field": field_prefix,
                "errors": serializer.errors,
            }
        )
        return False

    def _block(
        self,
        code: str,
        detail: str,
        field_name: str,
        temporary_id: str,
        action: str,
    ) -> None:
        self.blocking_errors.append({"code": code, "detail": detail, "field": field_name})
        self.planned_actions.append(
            PlannedReportAction(temporary_id, action, "blocked", detail)
        )

    # ---- write phase -------------------------------------------------------

    def _execute_write_plan(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            if plan.decision == "reuse":
                # Reuse never mutates the existing document; it is only reported.
                self.reused_records.append(
                    self._record_summary(plan.existing_instance, plan, "reuse", linked=False)
                )
                continue

            serializer = EvidenceWriteSerializer(
                data=plan.create_payload, context={"request": self.request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            linked = False
            if plan.assessment is not None:
                # M2M add() is idempotent, so re-running Step 11B never duplicates a link.
                if not plan.assessment.evidences.filter(id=instance.id).exists():
                    plan.assessment.evidences.add(instance)
                    linked = True

            self.created_records.append(
                self._record_summary(instance, plan, "create", linked=linked)
            )

    def _record_summary(self, instance, plan: WritePlan, action: str, *, linked: bool):
        return {
            "record_type": RECORD_TYPE,
            "action": action,
            "record_id": str(instance.id),
            "name": instance.name,
            "folder_id": str(instance.folder_id),
            "source_temporary_id": plan.source_temporary_id,
            "status": instance.status,
            "linked_assessment_ids": (
                [str(plan.assessment.id)] if plan.assessment is not None else []
            ),
            "assessment_link_added": linked,
            # Saved as a draft on purpose: Step 11B never finalizes or publishes a report.
            "report_marked_final": False,
            "audit_status_changed": False,
        }

    # ---- response ----------------------------------------------------------

    def _dry_run_status(self) -> str:
        if self.blocking_errors:
            return "blocked"
        if self.warnings:
            return "validated_with_warnings"
        return "validated"

    def _write_status(self) -> str:
        if self.warnings:
            return "completed_with_warnings"
        if self.created_records:
            return "created"
        if self.reused_records:
            return "reused_only"
        return "completed"

    def _blocking_status_code(self) -> int:
        if any(item.get("code") == "permission_denied" for item in self.blocking_errors):
            return 403
        return 422

    def _build_response(
        self,
        *,
        dry_run: bool,
        commit_status: str,
        extra_blocking_errors: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        blocking_errors = [*self.blocking_errors]
        if extra_blocking_errors:
            blocking_errors.extend(extra_blocking_errors)

        return {
            "commit_status": commit_status,
            "dry_run": dry_run,
            "planned_actions": [action.as_dict() for action in self.planned_actions],
            # A dry-run never writes, so created/reused stay empty until the approved commit.
            "created_records": [] if dry_run else self.created_records,
            "reused_records": [] if dry_run else self.reused_records,
            "rejected_records": self.rejected_records,
            "deferred_records": self.deferred_records,
            "skipped_records": self.skipped_records,
            "warnings": self.warnings,
            "blocking_errors": blocking_errors,
        }


def _render_report(payload: dict[str, Any]) -> str:
    """Render the reviewed draft as readable markdown stored on the document record."""
    lines = [REPORT_MARKER, "", f"# {payload.get('report_title') or 'Report draft'}", ""]

    executive_summary = payload.get("executive_summary")
    if isinstance(executive_summary, str) and executive_summary.strip():
        lines.extend(["## Executive Summary", "", executive_summary.strip(), ""])

    for section in payload.get("report_sections") or []:
        if not isinstance(section, dict):
            continue
        heading = (section.get("heading") or "").strip()
        if not heading:
            continue
        lines.extend([f"## {heading}", ""])
        content = (section.get("content") or "").strip()
        if content:
            lines.extend([content, ""])
        source_items = section.get("source_items") or []
        if source_items:
            lines.append("Source items: " + "; ".join(source_items))
            lines.append("")

    limitations = payload.get("limitations") or []
    if limitations:
        lines.extend(["## Limitations / Human Review Required", ""])
        lines.extend(f"- {entry}" for entry in limitations)
        lines.append("")

    next_steps = payload.get("recommended_next_steps") or []
    if next_steps:
        lines.extend(["## Recommended Next Steps", ""])
        lines.extend(f"- {entry}" for entry in next_steps)
        lines.append("")

    confidence = payload.get("confidence")
    if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
        lines.append(f"Advisory confidence at review time: {confidence}.")

    return "\n".join(lines).strip()


def execute_audit_report_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiAuditReportCommitService(request=request, payload=payload)
    return service.execute()
