from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import ComplianceAssessment, RequirementAssessment, RequirementNode
from iam.models import Folder, RoleAssignment

from .control_effectiveness_commit_guardrails import (
    ControlEffectivenessCommitValidationError,
    validate_control_effectiveness_commit_guardrails,
)


# Step 9B records a reviewed Step 9A judgement on the platform's existing per-requirement
# audit row, core.RequirementAssessment. That row already exists: it is created in bulk by
# ComplianceAssessment.create_requirement_assessments(). Step 9B therefore only ever
# updates an existing row and never creates a RequirementAssessment, a Framework, a
# RequirementNode, or a ReferenceControl. No AI provider module is imported or called here.
RECORD_TYPE = "requirement_assessment"

# The auditor-owned fields Step 9B is allowed to touch. Everything else on the row -
# status, score, is_scored, documentation_score, selected, evidences, applied_controls,
# answers - and every field of the parent ComplianceAssessment is left untouched.
WRITABLE_FIELDS = ("result", "observation")

# Step 9A advisory values mapped onto the platform's own RequirementAssessment.Result
# choices. 'needs_more_evidence' has no platform equivalent, so no result is written for
# it and the judgement is preserved in the observation instead.
COMPLIANCE_STATUS_TO_RESULT = {
    "compliant": RequirementAssessment.Result.COMPLIANT,
    "partially_compliant": RequirementAssessment.Result.PARTIALLY_COMPLIANT,
    "non_compliant": RequirementAssessment.Result.NON_COMPLIANT,
    "not_assessed": RequirementAssessment.Result.NOT_ASSESSED,
}

# Marker that makes the appended advisory block recognisable and keeps it separate from
# text an auditor wrote by hand.
OBSERVATION_MARKER = "[AI onboarding Step 9B - reviewed advisory judgement]"


@dataclass
class PlannedEffectivenessAction:
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
    instance: Any = None
    new_result: str | None = None
    observation_addition: str = ""
    changes_record: bool = False


class AiControlEffectivenessCommitService:
    """Deterministic Step 9B commit. No AI provider is imported or called here."""

    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedEffectivenessAction] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.rejected_records: list[dict[str, Any]] = []
        self.deferred_records: list[dict[str, Any]] = []
        self.skipped_records: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    # ---- entry point -------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        validate_control_effectiveness_commit_guardrails(self.payload)

        plans = self._plan_and_validate()

        if self.payload["dry_run"]:
            return self._build_response(dry_run=True, commit_status=self._dry_run_status())

        if self.blocking_errors:
            raise ControlEffectivenessCommitValidationError(
                "ai_control_effectiveness_commit_blocked",
                "The approved Step 9B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(dry_run=False, commit_status="blocked"),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(plans)
        except ControlEffectivenessCommitValidationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a rolled-back commit
            self.created_records = []
            self.reused_records = []
            raise ControlEffectivenessCommitValidationError(
                "transaction_aborted",
                "Step 9B transaction failed and all writes were rolled back.",
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
        planned_targets: set[str] = set()

        for index, decision in enumerate(self.payload.get("decisions") or []):
            self._plan_decision(index, decision, assessment, plans, planned_targets)

        return plans

    def _plan_decision(
        self,
        index: int,
        decision: dict[str, Any],
        assessment: ComplianceAssessment | None,
        plans: list[WritePlan],
        planned_targets: set[str],
    ) -> None:
        field_prefix = f"decisions[{index}]"
        temporary_id = decision["temporary_id"]
        action = decision["decision"]
        payload = decision.get("payload") or {}
        label = self._control_label(payload)

        if not decision.get("selected"):
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": label or None,
                    "skip_reason": "not_selected",
                }
            )
            self.planned_actions.append(
                PlannedEffectivenessAction(
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
                PlannedEffectivenessAction(
                    temporary_id, "reject", "ok",
                    "Control effectiveness judgement rejected by reviewer.",
                    target_name=label or None,
                )
            )
            return

        if action == "defer":
            self.deferred_records.append(
                {"source_temporary_id": temporary_id, "title": label or None}
            )
            self.planned_actions.append(
                PlannedEffectivenessAction(
                    temporary_id, "defer", "ok",
                    "Control effectiveness judgement deferred by reviewer.",
                    target_name=label or None,
                )
            )
            return

        if assessment is None:
            self._block(
                "assessment_reference_required",
                "A resolvable assessment_reference is required before Step 9B can record a "
                "control effectiveness judgement.",
                "assessment_reference",
                temporary_id,
                action,
            )
            return

        if action == "reuse":
            self._plan_reuse(field_prefix, temporary_id, decision, assessment, plans)
            return

        self._plan_update(
            field_prefix, temporary_id, payload, label, assessment, plans, planned_targets
        )

    def _plan_reuse(
        self,
        field_prefix: str,
        temporary_id: str,
        decision: dict[str, Any],
        assessment: ComplianceAssessment,
        plans: list[WritePlan],
    ) -> None:
        instance = self._load_requirement_assessment(
            decision["existing_record_reference"],
            field_prefix,
            temporary_id,
            "reuse",
            assessment,
        )
        if instance is None:
            return

        target_name = instance.requirement.display_short or str(instance.requirement_id)
        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="reuse",
                target_name=target_name,
                instance=instance,
            )
        )
        self.planned_actions.append(
            PlannedEffectivenessAction(
                temporary_id, "reuse", "planned",
                "Existing RequirementAssessment would be reused without mutation.",
                target_name=target_name,
            )
        )

    def _plan_update(
        self,
        field_prefix: str,
        temporary_id: str,
        payload: dict[str, Any],
        label: str,
        assessment: ComplianceAssessment,
        plans: list[WritePlan],
        planned_targets: set[str],
    ) -> None:
        instance = self._resolve_requirement_assessment(
            field_prefix, temporary_id, payload, assessment
        )
        if instance is None:
            return

        target_name = instance.requirement.display_short or label

        if str(instance.id) in planned_targets:
            self.warnings.append(
                {
                    "code": "duplicate_in_batch_skipped",
                    "detail": (
                        "Another selected decision already records a judgement on this "
                        "requirement assessment; this duplicate was skipped."
                    ),
                    "field": f"{field_prefix}.payload.framework_control_reference",
                }
            )
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": target_name,
                    "skip_reason": "duplicate_in_batch",
                }
            )
            self.planned_actions.append(
                PlannedEffectivenessAction(
                    temporary_id, "create", "skipped",
                    "Duplicate requirement assessment target within the submitted batch.",
                    target_name=target_name,
                )
            )
            return

        new_result = self._resolve_result(field_prefix, payload)
        observation_addition = _build_observation_block(payload)

        result_changes = new_result is not None and instance.result != new_result
        observation_changes = observation_addition not in (instance.observation or "")

        if result_changes and instance.result != RequirementAssessment.Result.NOT_ASSESSED:
            self.warnings.append(
                {
                    "code": "existing_result_replaced",
                    "detail": (
                        f"The requirement assessment already carried the result "
                        f"'{instance.result}'; the approved commit replaces it with "
                        f"'{new_result}'."
                    ),
                    "field": f"{field_prefix}.payload.suggested_compliance_status",
                }
            )

        if observation_changes and (instance.observation or "").strip():
            self.warnings.append(
                {
                    "code": "observation_appended",
                    "detail": (
                        "The requirement assessment already has an observation; the advisory "
                        "block is appended and no existing text is overwritten."
                    ),
                    "field": f"{field_prefix}.payload.rationale",
                }
            )

        self._warn_effectiveness_not_persisted(field_prefix, payload)

        planned_targets.add(str(instance.id))
        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="create",
                target_name=target_name,
                instance=instance,
                new_result=new_result if result_changes else None,
                observation_addition=observation_addition if observation_changes else "",
                changes_record=result_changes or observation_changes,
            )
        )

        if result_changes or observation_changes:
            detail = (
                "The reviewed judgement would be recorded on the existing "
                "RequirementAssessment; no audit status is changed and no compliance is "
                "certified."
            )
        else:
            detail = (
                "The existing RequirementAssessment already carries this judgement; nothing "
                "would be changed."
            )
        self.planned_actions.append(
            PlannedEffectivenessAction(
                temporary_id,
                "create" if (result_changes or observation_changes) else "reuse",
                "planned",
                detail,
                target_name=target_name,
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
                        "assessment_reference is required: Step 9B only ever updates an "
                        "existing RequirementAssessment of an existing audit."
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
        """Mirror the platform's own RequirementAssessment write rules."""
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
        permission = Permission.objects.filter(codename="change_requirementassessment").first()
        allowed = permission is not None and RoleAssignment.is_access_allowed(
            self.user, permission, assessment.folder
        )
        if not allowed:
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": (
                        "You do not have permission to change requirement assessments in the "
                        "selected scope."
                    ),
                    "field": "assessment_reference",
                }
            )

    def _load_requirement_assessment(
        self,
        reference: str,
        field_prefix: str,
        temporary_id: str,
        action: str,
        assessment: ComplianceAssessment,
    ) -> RequirementAssessment | None:
        instance = (
            RequirementAssessment.objects.filter(id=reference)
            .select_related("requirement", "compliance_assessment", "folder")
            .first()
        )
        if instance is None:
            self._block(
                "requirement_assessment_not_found",
                "The referenced RequirementAssessment does not exist. Step 9B never creates "
                "requirement assessments.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                action,
            )
            return None

        if not RoleAssignment.is_object_readable(self.user, RequirementAssessment, instance.id):
            self._block(
                "permission_denied",
                "You do not have permission to use the selected RequirementAssessment.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                action,
            )
            return None

        if str(instance.compliance_assessment_id) != str(assessment.id):
            self._block(
                "requirement_assessment_out_of_scope",
                "The referenced RequirementAssessment must belong to assessment_reference.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                action,
            )
            return None

        return instance

    def _resolve_requirement_assessment(
        self,
        field_prefix: str,
        temporary_id: str,
        payload: dict[str, Any],
        assessment: ComplianceAssessment,
    ) -> RequirementAssessment | None:
        """Resolve the existing per-requirement audit row. Step 9B never creates one."""
        reference = payload.get("linked_requirement_assessment_reference")
        if reference:
            return self._load_requirement_assessment(
                reference, f"{field_prefix}.payload", temporary_id, "create", assessment
            )

        requirement = self._resolve_requirement(payload, assessment)
        instance = None
        if requirement is not None:
            instance = (
                RequirementAssessment.objects.filter(
                    compliance_assessment=assessment, requirement=requirement
                )
                .select_related("requirement", "compliance_assessment", "folder")
                .first()
            )

        if instance is None:
            control_reference = (payload.get("framework_control_reference") or "").strip()
            detail = (
                f"No existing RequirementAssessment was found for framework control "
                f"'{control_reference}' in the selected audit. Step 9B never creates a "
                "RequirementAssessment, a Framework, a RequirementNode, or a ReferenceControl: "
                "load the framework and create the audit's requirement assessments first."
            )
            self.blocking_errors.append(
                {
                    "code": "requirement_assessment_not_found",
                    "detail": detail,
                    "field": f"{field_prefix}.payload.framework_control_reference",
                }
            )
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": payload.get("framework_control_title") or control_reference,
                    "skip_reason": "requirement_assessment_not_found",
                }
            )
            self.planned_actions.append(
                PlannedEffectivenessAction(
                    temporary_id, "create", "blocked", detail,
                    target_name=payload.get("framework_control_title") or control_reference,
                )
            )
            return None

        if not RoleAssignment.is_object_readable(self.user, RequirementAssessment, instance.id):
            self._block(
                "permission_denied",
                "You do not have permission to use the resolved RequirementAssessment.",
                f"{field_prefix}.payload.framework_control_reference",
                temporary_id,
                "create",
            )
            return None

        return instance

    def _resolve_requirement(
        self, payload: dict[str, Any], assessment: ComplianceAssessment
    ) -> RequirementNode | None:
        reference = (payload.get("framework_control_reference") or "").strip()
        code = (payload.get("framework_control_code") or "").strip()

        requirement = None
        if reference:
            requirement = RequirementNode.objects.filter(
                framework=assessment.framework, urn__iexact=reference
            ).first()
            if requirement is None:
                requirement = RequirementNode.objects.filter(
                    framework=assessment.framework, ref_id__iexact=reference
                ).first()
        if requirement is None and code:
            requirement = RequirementNode.objects.filter(
                framework=assessment.framework, ref_id__iexact=code
            ).first()
        return requirement

    def _resolve_result(self, field_prefix: str, payload: dict[str, Any]) -> str | None:
        status = payload.get("suggested_compliance_status")
        result = COMPLIANCE_STATUS_TO_RESULT.get(status)
        if result is None:
            self.warnings.append(
                {
                    "code": "compliance_status_not_persistable",
                    "detail": (
                        f"'{status}' has no equivalent RequirementAssessment result, so no "
                        "result is written; the judgement is preserved in the observation only."
                    ),
                    "field": f"{field_prefix}.payload.suggested_compliance_status",
                }
            )
            return None
        return result

    def _warn_effectiveness_not_persisted(
        self, field_prefix: str, payload: dict[str, Any]
    ) -> None:
        if not payload.get("suggested_effectiveness"):
            return
        self.warnings.append(
            {
                "code": "effectiveness_not_persisted",
                "detail": (
                    "RequirementAssessment has no dedicated control-effectiveness field; the "
                    "advisory effectiveness is preserved in the appended observation block and "
                    "no other auditor-owned field was overwritten."
                ),
                "field": f"{field_prefix}.payload.suggested_effectiveness",
            }
        )

    def _control_label(self, payload: dict[str, Any]) -> str:
        code = (payload.get("framework_control_code") or "").strip()
        title = (payload.get("framework_control_title") or "").strip()
        if code and title:
            return f"{code} - {title}"
        return title or code or (payload.get("framework_control_reference") or "").strip()

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
            PlannedEffectivenessAction(temporary_id, action, "blocked", detail)
        )

    # ---- write phase -------------------------------------------------------

    def _execute_write_plan(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            instance = plan.instance

            if plan.decision == "reuse" or not plan.changes_record:
                # Nothing is mutated; the outcome is only reported.
                self.reused_records.append(self._record_summary(instance, plan, "reuse"))
                continue

            updated_fields: list[str] = []
            if plan.new_result is not None:
                instance.result = plan.new_result
                updated_fields.append("result")
            if plan.observation_addition:
                existing = (instance.observation or "").strip()
                instance.observation = (
                    f"{existing}\n\n{plan.observation_addition}"
                    if existing
                    else plan.observation_addition
                )
                updated_fields.append("observation")

            # Only the auditor-owned result/observation fields are saved. The audit status,
            # score, evidences, applied controls, and the parent ComplianceAssessment are
            # never touched here.
            instance.save(update_fields=updated_fields)
            self.created_records.append(
                self._record_summary(instance, plan, "update", updated_fields)
            )

    def _record_summary(
        self,
        instance,
        plan: WritePlan,
        action: str,
        updated_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "record_type": RECORD_TYPE,
            "action": action,
            "record_id": str(instance.id),
            "name": plan.target_name,
            "folder_id": str(instance.folder_id),
            "source_temporary_id": plan.source_temporary_id,
            "compliance_assessment_id": str(instance.compliance_assessment_id),
            "requirement_id": str(instance.requirement_id),
            "updated_fields": updated_fields or [],
            "result": instance.result,
            # Recorded per requirement only: Step 9B never closes an audit or certifies
            # compliance.
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


def _build_observation_block(payload: dict[str, Any]) -> str:
    """Compose the advisory block appended to the auditor's observation field."""
    lines = [OBSERVATION_MARKER]

    effectiveness = payload.get("suggested_effectiveness")
    if effectiveness:
        lines.append(f"Suggested control effectiveness: {effectiveness}.")

    status = payload.get("suggested_compliance_status")
    if status:
        lines.append(f"Suggested compliance status: {status}.")

    for label, key in (
        ("Evidence summary", "evidence_summary"),
        ("Rationale", "rationale"),
        ("Recommended auditor action", "recommended_auditor_action"),
    ):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            lines.append(f"{label}: {value.strip()}")

    gaps = payload.get("gaps") or []
    if gaps:
        lines.append("Gaps: " + "; ".join(gaps))

    return "\n".join(lines)


def execute_control_effectiveness_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiControlEffectivenessCommitService(request=request, payload=payload)
    return service.execute()
