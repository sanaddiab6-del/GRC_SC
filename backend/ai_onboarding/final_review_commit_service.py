from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import ComplianceAssessment
from iam.models import Folder, RoleAssignment

from .final_review_commit_guardrails import (
    FinalReviewCommitValidationError,
    validate_final_review_commit_guardrails,
)


# Step 12B records a reviewed Step 12A handoff summary on the platform's existing
# assessment note field, ComplianceAssessment.observation (inherited from core.Assessment).
# That is the only safe existing write target: the platform has no case-handoff object, and
# Step 12B never creates one, never changes the audit status, and never marks the workflow
# or the audit complete. No AI provider module is imported or called here.
RECORD_TYPE = "compliance_assessment_observation"

# Marker that makes the appended handoff block recognisable and keeps it separate from text
# an auditor wrote by hand and from the Step 10B readiness block.
OBSERVATION_MARKER = "[AI onboarding Step 12B - reviewed case handoff summary]"

SUMMARY_SECTIONS = (
    ("Completed steps", "completed_steps"),
    ("Incomplete steps", "incomplete_steps"),
    ("Created or reused records", "created_or_reused_records_summary"),
    ("Blocked items", "blocked_items"),
    ("Human review required", "human_review_required"),
    ("Recommended next steps", "recommended_next_steps"),
)


@dataclass
class PlannedHandoffAction:
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
    assessment: Any = None
    observation_addition: str = ""
    changes_record: bool = False


class AiFinalReviewCommitService:
    """Deterministic Step 12B commit. No AI provider is imported or called here."""

    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedHandoffAction] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.rejected_records: list[dict[str, Any]] = []
        self.deferred_records: list[dict[str, Any]] = []
        self.skipped_records: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    # ---- entry point -------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        validate_final_review_commit_guardrails(self.payload)

        plans = self._plan_and_validate()

        if self.payload["dry_run"]:
            return self._build_response(dry_run=True, commit_status=self._dry_run_status())

        if self.blocking_errors:
            raise FinalReviewCommitValidationError(
                "ai_final_review_commit_blocked",
                "The approved Step 12B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(dry_run=False, commit_status="blocked"),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(plans)
        except FinalReviewCommitValidationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a rolled-back commit
            self.created_records = []
            self.reused_records = []
            raise FinalReviewCommitValidationError(
                "transaction_aborted",
                "Step 12B transaction failed and all writes were rolled back.",
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
        if assessment is not None:
            self._check_assessment_writable(assessment)
            self._check_change_permission(assessment)

        plans: list[WritePlan] = []
        already_planned = False

        for index, decision in enumerate(self.payload.get("decisions") or []):
            planned = self._plan_decision(index, decision, assessment, plans, already_planned)
            already_planned = already_planned or planned

        return plans

    def _plan_decision(
        self,
        index: int,
        decision: dict[str, Any],
        assessment: ComplianceAssessment | None,
        plans: list[WritePlan],
        already_planned: bool,
    ) -> bool:
        field_prefix = f"decisions[{index}]"
        temporary_id = decision["temporary_id"]
        action = decision["decision"]
        payload = decision.get("payload") or {}
        label = (payload.get("demo_readiness_status") or "case handoff").strip()

        if not decision.get("selected"):
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": label,
                    "skip_reason": "not_selected",
                }
            )
            self.planned_actions.append(
                PlannedHandoffAction(
                    temporary_id, action, "skipped",
                    "Decision was not selected by the reviewer.", target_name=label,
                )
            )
            return False

        if action == "reject":
            self.rejected_records.append(
                {"source_temporary_id": temporary_id, "title": label}
            )
            self.planned_actions.append(
                PlannedHandoffAction(
                    temporary_id, "reject", "ok",
                    "Case handoff summary rejected by reviewer.", target_name=label,
                )
            )
            return False

        if action == "defer":
            self.deferred_records.append(
                {"source_temporary_id": temporary_id, "title": label}
            )
            self.planned_actions.append(
                PlannedHandoffAction(
                    temporary_id, "defer", "ok",
                    "Case handoff summary deferred by reviewer.", target_name=label,
                )
            )
            return False

        if assessment is None:
            self._block(
                "assessment_reference_required",
                "A resolvable assessment_reference is required before Step 12B can record a "
                "case handoff summary.",
                "assessment_reference",
                temporary_id,
                action,
            )
            return False

        if action == "reuse":
            self._plan_reuse(field_prefix, temporary_id, decision, assessment, plans)
            return True

        if already_planned:
            self.warnings.append(
                {
                    "code": "duplicate_in_batch_skipped",
                    "detail": (
                        "Another selected decision already records a case handoff summary on "
                        "this audit; this duplicate was skipped."
                    ),
                    "field": f"{field_prefix}.payload",
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
                PlannedHandoffAction(
                    temporary_id, "create", "skipped",
                    "Duplicate case handoff summary within the submitted batch.",
                    target_name=label,
                )
            )
            return False

        observation_addition = _build_observation_block(payload)
        observation_changes = observation_addition not in (assessment.observation or "")

        if observation_changes and (assessment.observation or "").strip():
            self.warnings.append(
                {
                    "code": "observation_appended",
                    "detail": (
                        "The audit already has an observation; the case handoff summary is "
                        "appended and no existing text is overwritten."
                    ),
                    "field": f"{field_prefix}.payload.completion_summary",
                }
            )

        self.warnings.append(
            {
                "code": "handoff_recorded_as_note_only",
                "detail": (
                    "The platform has no case-handoff object, so the reviewed summary is "
                    "recorded as readable text in the audit observation only. The workflow is "
                    "not marked complete, the audit status is not changed, the audit is not "
                    "closed, and no compliance is certified."
                ),
                "field": f"{field_prefix}.payload.demo_readiness_status",
            }
        )

        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="create",
                target_name=assessment.name,
                assessment=assessment,
                observation_addition=observation_addition if observation_changes else "",
                changes_record=observation_changes,
            )
        )
        self.planned_actions.append(
            PlannedHandoffAction(
                temporary_id,
                "create" if observation_changes else "reuse",
                "planned",
                (
                    "The reviewed case handoff summary would be appended to the audit "
                    "observation; no audit status is changed."
                )
                if observation_changes
                else (
                    "The audit observation already carries this case handoff summary; nothing "
                    "would be changed."
                ),
                target_name=assessment.name,
            )
        )
        return True

    def _plan_reuse(
        self,
        field_prefix: str,
        temporary_id: str,
        decision: dict[str, Any],
        assessment: ComplianceAssessment,
        plans: list[WritePlan],
    ) -> None:
        existing_id = decision["existing_record_reference"]
        if str(existing_id) != str(assessment.id):
            self._block(
                "reuse_out_of_scope",
                "existing_record_reference must be the assessment_reference whose observation "
                "carries the case handoff summary.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="reuse",
                target_name=assessment.name,
                assessment=assessment,
            )
        )
        self.planned_actions.append(
            PlannedHandoffAction(
                temporary_id, "reuse", "planned",
                "The existing audit observation would be reused without mutation.",
                target_name=assessment.name,
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
        reference = self.payload.get("assessment_reference")
        if not reference:
            self.blocking_errors.append(
                {
                    "code": "assessment_reference_required",
                    "detail": (
                        "assessment_reference is required: the audit observation is the only "
                        "safe existing target for a case handoff summary, and Step 12B never "
                        "creates a handoff record."
                    ),
                    "field": "assessment_reference",
                }
            )
            return None

        assessment = (
            ComplianceAssessment.objects.filter(id=reference)
            .select_related("framework", "folder")
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

        return assessment

    def _check_assessment_writable(self, assessment: ComplianceAssessment) -> None:
        """Mirror the platform's own audit write rules."""
        if assessment.is_locked:
            self.blocking_errors.append(
                {
                    "code": "assessment_locked",
                    "detail": "The selected audit is locked and cannot be modified.",
                    "field": "assessment_reference",
                }
            )
        if assessment.status == ComplianceAssessment.Status.IN_REVIEW:
            self.blocking_errors.append(
                {
                    "code": "assessment_in_review",
                    "detail": "The selected audit is in review and cannot be modified.",
                    "field": "assessment_reference",
                }
            )

    def _check_change_permission(self, assessment: ComplianceAssessment) -> None:
        permission = Permission.objects.filter(codename="change_complianceassessment").first()
        allowed = permission is not None and RoleAssignment.is_access_allowed(
            self.user, permission, assessment.folder
        )
        if not allowed:
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": (
                        "You do not have permission to change the compliance assessment in the "
                        "selected scope."
                    ),
                    "field": "assessment_reference",
                }
            )

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
            PlannedHandoffAction(temporary_id, action, "blocked", detail)
        )

    # ---- write phase -------------------------------------------------------

    def _execute_write_plan(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            assessment = plan.assessment

            if plan.decision == "reuse" or not plan.changes_record:
                # Nothing is mutated; the outcome is only reported.
                self.reused_records.append(self._record_summary(assessment, plan, "reuse", []))
                continue

            existing = (assessment.observation or "").strip()
            assessment.observation = (
                f"{existing}\n\n{plan.observation_addition}"
                if existing
                else plan.observation_addition
            )
            # Only the observation note is saved. The audit status, is_locked flag, dates,
            # requirement assessments, and every other field are never touched here.
            assessment.save(update_fields=["observation"])
            self.created_records.append(
                self._record_summary(assessment, plan, "update", ["observation"])
            )

    def _record_summary(
        self,
        assessment,
        plan: WritePlan,
        action: str,
        updated_fields: list[str],
    ) -> dict[str, Any]:
        return {
            "record_type": RECORD_TYPE,
            "action": action,
            "record_id": str(assessment.id),
            "name": plan.target_name,
            "folder_id": str(assessment.folder_id),
            "source_temporary_id": plan.source_temporary_id,
            "updated_fields": updated_fields,
            # Recorded as a note only: Step 12B never completes or closes anything.
            "audit_status_changed": False,
            "workflow_marked_complete": False,
            "audit_closed": False,
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


def _build_observation_block(payload: dict[str, Any]) -> str:
    """Compose the case handoff block appended to the audit's observation field."""
    lines = [OBSERVATION_MARKER]

    status = payload.get("demo_readiness_status")
    if status is not None:
        lines.append(
            f"Advisory onboarding handoff status: {status}. This is a review aid; the "
            "workflow and the audit remain open."
        )

    summary = payload.get("completion_summary")
    if isinstance(summary, str) and summary.strip():
        lines.append(f"Summary: {summary.strip()}")

    for label, key in SUMMARY_SECTIONS:
        entries = payload.get(key) or []
        if entries:
            lines.append(f"{label}: " + "; ".join(entries))

    confidence = payload.get("confidence")
    if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
        lines.append(f"Advisory confidence at review time: {confidence}.")

    return "\n".join(lines)


def execute_final_review_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiFinalReviewCommitService(request=request, payload=payload)
    return service.execute()
