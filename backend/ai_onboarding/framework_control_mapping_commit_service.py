from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import (
    AppliedControl,
    ComplianceAssessment,
    RequirementAssessment,
    RequirementNode,
)
from iam.models import Folder, RoleAssignment

from .framework_control_mapping_commit_guardrails import (
    FrameworkControlMappingCommitValidationError,
    validate_framework_control_mapping_commit_guardrails,
)


# Step 7B persists a reviewed Step 7A mapping onto the platform's existing framework
# structure. There is no dedicated "framework control mapping" table: the platform links a
# framework control (core.RequirementNode) to an audit through core.RequirementAssessment,
# and links the organisation's own controls through RequirementAssessment.applied_controls.
# That existing pair is the write target.
#
# RequirementAssessment rows are normally created in bulk by
# ComplianceAssessment.create_requirement_assessments(), so Step 7B reuses the existing row
# whenever it is present and only creates the missing pairing as a fallback. No Framework,
# RequirementNode, ReferenceControl, or AppliedControl is ever created here, and no AI
# provider module is imported or called.
RECORD_TYPE = "requirement_assessment"

# Advisory Step 7A context with no dedicated platform column. It is deliberately not
# written anywhere rather than being forced into an auditor-owned field such as
# observation, and each occurrence is reported as a warning.
UNPERSISTED_ADVISORY_FIELDS = (
    "mapping_type",
    "rationale",
    "evidence_needed",
    "confidence",
)


@dataclass
class PlannedMappingAction:
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
    requirement: Any = None
    compliance_assessment: Any = None
    existing_instance: Any = None
    applied_control: Any = None
    creates_requirement_assessment: bool = False


class AiFrameworkControlMappingCommitService:
    """Deterministic Step 7B commit. No AI provider is imported or called here."""

    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedMappingAction] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.rejected_records: list[dict[str, Any]] = []
        self.deferred_records: list[dict[str, Any]] = []
        self.skipped_records: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    # ---- entry point -------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        validate_framework_control_mapping_commit_guardrails(self.payload)

        plans = self._plan_and_validate()

        if self.payload["dry_run"]:
            return self._build_response(dry_run=True, commit_status=self._dry_run_status())

        if self.blocking_errors:
            raise FrameworkControlMappingCommitValidationError(
                "ai_framework_control_mapping_commit_blocked",
                "The approved Step 7B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(dry_run=False, commit_status="blocked"),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(plans)
        except FrameworkControlMappingCommitValidationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a rolled-back commit
            self.created_records = []
            self.reused_records = []
            raise FrameworkControlMappingCommitValidationError(
                "transaction_aborted",
                "Step 7B transaction failed and all writes were rolled back.",
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
            self._check_framework_reference(assessment)
            self._check_assessment_writable(assessment)
            self._check_change_permission(assessment)

        plans: list[WritePlan] = []
        planned_keys: set[tuple[str, str, str]] = set()

        for index, decision in enumerate(self.payload.get("decisions") or []):
            self._plan_decision(index, decision, folder, assessment, plans, planned_keys)

        return plans

    def _plan_decision(
        self,
        index: int,
        decision: dict[str, Any],
        folder: Folder | None,
        assessment: ComplianceAssessment | None,
        plans: list[WritePlan],
        planned_keys: set[tuple[str, str, str]],
    ) -> None:
        field_prefix = f"decisions[{index}]"
        temporary_id = decision["temporary_id"]
        action = decision["decision"]
        payload = decision.get("payload") or {}
        label = self._mapping_label(payload)

        if not decision.get("selected"):
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": label or None,
                    "skip_reason": "not_selected",
                }
            )
            self.planned_actions.append(
                PlannedMappingAction(
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
                PlannedMappingAction(
                    temporary_id, "reject", "ok",
                    "Framework control mapping rejected by reviewer.", target_name=label or None,
                )
            )
            return

        if action == "defer":
            self.deferred_records.append(
                {"source_temporary_id": temporary_id, "title": label or None}
            )
            self.planned_actions.append(
                PlannedMappingAction(
                    temporary_id, "defer", "ok",
                    "Framework control mapping deferred by reviewer.", target_name=label or None,
                )
            )
            return

        if folder is None:
            self.planned_actions.append(
                PlannedMappingAction(
                    temporary_id, action, "blocked",
                    "A valid folder_reference is required before Step 7B can create or reuse records.",
                    target_name=label or None,
                )
            )
            return

        if assessment is None:
            self._block(
                "assessment_reference_required",
                "A resolvable assessment_reference is required before Step 7B can persist a "
                "framework control mapping.",
                "assessment_reference",
                temporary_id,
                action,
            )
            return

        if action == "reuse":
            self._plan_reuse(field_prefix, temporary_id, decision, folder, assessment, plans)
            return

        self._plan_create(
            field_prefix, temporary_id, payload, label, folder, assessment, plans, planned_keys
        )

    def _plan_reuse(
        self,
        field_prefix: str,
        temporary_id: str,
        decision: dict[str, Any],
        folder: Folder,
        assessment: ComplianceAssessment,
        plans: list[WritePlan],
    ) -> None:
        existing_id = decision["existing_record_reference"]
        instance = (
            RequirementAssessment.objects.filter(id=existing_id)
            .select_related("requirement", "compliance_assessment", "folder")
            .first()
        )

        if instance is None:
            self._block(
                "reuse_target_not_found",
                "existing_record_reference does not match an existing RequirementAssessment.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        if not RoleAssignment.is_object_readable(self.user, RequirementAssessment, instance.id):
            self._block(
                "permission_denied",
                "You do not have permission to reuse the selected RequirementAssessment.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        if str(instance.compliance_assessment_id) != str(assessment.id):
            self._block(
                "reuse_out_of_scope",
                "existing_record_reference must belong to assessment_reference.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        target_name = instance.requirement.display_short or str(instance.requirement_id)
        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="reuse",
                target_name=target_name,
                requirement=instance.requirement,
                compliance_assessment=assessment,
                existing_instance=instance,
            )
        )
        self.planned_actions.append(
            PlannedMappingAction(
                temporary_id, "reuse", "planned",
                "Existing RequirementAssessment mapping would be reused without mutation.",
                target_name=target_name,
            )
        )

    def _plan_create(
        self,
        field_prefix: str,
        temporary_id: str,
        payload: dict[str, Any],
        label: str,
        folder: Folder,
        assessment: ComplianceAssessment,
        plans: list[WritePlan],
        planned_keys: set[tuple[str, str, str]],
    ) -> None:
        requirement = self._resolve_requirement(field_prefix, temporary_id, payload, assessment)
        if requirement is None:
            return

        target_name = requirement.display_short or label

        applied_control = self._resolve_applied_control(field_prefix, payload, folder)

        batch_key = (
            str(assessment.id),
            str(requirement.id),
            str(applied_control.id) if applied_control is not None else "",
        )
        if batch_key in planned_keys:
            self.warnings.append(
                {
                    "code": "duplicate_in_batch_skipped",
                    "detail": (
                        "Another selected decision already maps this framework control to the "
                        "same audit and applied control; this duplicate was skipped."
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
                PlannedMappingAction(
                    temporary_id, "create", "skipped",
                    "Duplicate framework control mapping within the submitted batch.",
                    target_name=target_name,
                )
            )
            return

        existing = (
            RequirementAssessment.objects.filter(
                compliance_assessment=assessment, requirement=requirement
            )
            .select_related("requirement")
            .first()
        )

        if existing is None and not self._check_add_permission(assessment):
            self._block(
                "permission_denied",
                "You do not have permission to add requirement assessments in the selected scope.",
                f"{field_prefix}.payload.framework_control_reference",
                temporary_id,
                "create",
            )
            return

        self._warn_unpersisted_advisory_context(field_prefix, payload)

        planned_keys.add(batch_key)
        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="create",
                target_name=target_name,
                requirement=requirement,
                compliance_assessment=assessment,
                existing_instance=existing,
                applied_control=applied_control,
                creates_requirement_assessment=existing is None,
            )
        )

        if existing is None:
            self.warnings.append(
                {
                    "code": "requirement_assessment_created",
                    "detail": (
                        "No RequirementAssessment existed for this framework control in the "
                        "selected audit; the platform pairing will be created without changing "
                        "any compliance result."
                    ),
                    "field": f"{field_prefix}.payload.framework_control_reference",
                }
            )
            detail = "RequirementAssessment mapping would be created for this framework control."
        elif applied_control is not None and existing.applied_controls.filter(
            id=applied_control.id
        ).exists():
            self.warnings.append(
                {
                    "code": "mapping_already_exists",
                    "detail": (
                        "The framework control is already mapped to this applied control in the "
                        "selected audit; the existing mapping will be reused."
                    ),
                    "field": f"{field_prefix}.payload.linked_applied_control_reference",
                }
            )
            detail = "Existing RequirementAssessment mapping already carries this applied control."
        else:
            detail = "Existing RequirementAssessment would be reused for this framework control."

        self.planned_actions.append(
            PlannedMappingAction(
                temporary_id,
                "create" if existing is None else "reuse",
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
                    "detail": "assessment_reference does not match an existing ComplianceAssessment.",
                    "field": "assessment_reference",
                }
            )
            return None

        if not RoleAssignment.is_object_readable(
            self.user, ComplianceAssessment, assessment.id
        ):
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

    def _check_framework_reference(self, assessment: ComplianceAssessment) -> None:
        reference = self.payload.get("framework_reference")
        if reference and str(assessment.framework_id) != str(reference):
            self.blocking_errors.append(
                {
                    "code": "framework_mismatch",
                    "detail": (
                        "framework_reference does not match the framework of the selected "
                        "ComplianceAssessment."
                    ),
                    "field": "framework_reference",
                }
            )

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
        if not self._has_permission("change_requirementassessment", assessment.folder):
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

    def _check_add_permission(self, assessment: ComplianceAssessment) -> bool:
        return self._has_permission("add_requirementassessment", assessment.folder)

    def _has_permission(self, codename: str, folder: Folder) -> bool:
        permission = Permission.objects.filter(codename=codename).first()
        if permission is None:
            return False
        return RoleAssignment.is_access_allowed(self.user, permission, folder)

    def _resolve_requirement(
        self,
        field_prefix: str,
        temporary_id: str,
        payload: dict[str, Any],
        assessment: ComplianceAssessment,
    ) -> RequirementNode | None:
        """Resolve the existing framework control. Step 7B never creates one."""
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

        if requirement is None:
            # The Step 7A candidate may have come from the read-only CSV export. Step 7B
            # never creates a Framework, RequirementNode, or ReferenceControl to make a
            # mapping fit, so the item is blocked and reported as skipped instead.
            detail = (
                f"Framework control '{reference or code}' does not exist as a requirement of the "
                "selected audit's framework. Step 7B never creates framework controls: load the "
                "framework library into the platform before persisting this mapping."
            )
            self.blocking_errors.append(
                {
                    "code": "framework_control_not_in_database",
                    "detail": detail,
                    "field": f"{field_prefix}.payload.framework_control_reference",
                }
            )
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": payload.get("framework_control_title") or reference or code,
                    "skip_reason": "framework_control_not_in_database",
                }
            )
            self.planned_actions.append(
                PlannedMappingAction(
                    temporary_id, "create", "blocked", detail,
                    target_name=payload.get("framework_control_title") or reference or code,
                )
            )
            return None

        return requirement

    def _resolve_applied_control(
        self, field_prefix: str, payload: dict[str, Any], folder: Folder
    ) -> AppliedControl | None:
        reference = payload.get("linked_applied_control_reference")
        title = payload.get("linked_applied_control_title")
        if not reference and not title:
            self.warnings.append(
                {
                    "code": "applied_control_linkage_not_applied",
                    "detail": (
                        "No applied control was referenced, so the framework control mapping is "
                        "recorded without an applied control link."
                    ),
                    "field": f"{field_prefix}.payload.linked_applied_control_reference",
                }
            )
            return None

        instance = self._lookup_applied_control(folder, reference, title)
        if instance is None:
            self.warnings.append(
                {
                    "code": "applied_control_linkage_not_applied",
                    "detail": (
                        "The referenced applied control was not found in the selected folder; the "
                        "framework control mapping is recorded without an applied control link. "
                        "Step 7B never creates applied controls."
                    ),
                    "field": f"{field_prefix}.payload.linked_applied_control_reference",
                }
            )
            return None

        if not RoleAssignment.is_object_readable(self.user, AppliedControl, instance.id):
            self.warnings.append(
                {
                    "code": "applied_control_linkage_not_applied",
                    "detail": (
                        "You do not have permission to read the referenced applied control; the "
                        "framework control mapping is recorded without an applied control link."
                    ),
                    "field": f"{field_prefix}.payload.linked_applied_control_reference",
                }
            )
            return None

        return instance

    def _lookup_applied_control(self, folder: Folder, reference, title):
        if reference:
            instance = AppliedControl.objects.filter(
                folder=folder, ref_id__iexact=reference
            ).first()
            if instance is not None:
                return instance
            instance = AppliedControl.objects.filter(
                folder=folder, name__iexact=reference
            ).first()
            if instance is not None:
                return instance
        if title:
            return AppliedControl.objects.filter(folder=folder, name__iexact=title).first()
        return None

    def _warn_unpersisted_advisory_context(
        self, field_prefix: str, payload: dict[str, Any]
    ) -> None:
        present = [field for field in UNPERSISTED_ADVISORY_FIELDS if payload.get(field)]
        if not present:
            return
        self.warnings.append(
            {
                "code": "advisory_mapping_context_not_persisted",
                "detail": (
                    "RequirementAssessment has no dedicated field for "
                    f"{', '.join(present)}; the Step 7A advisory context was not written and no "
                    "auditor-owned field was overwritten."
                ),
                "field": f"{field_prefix}.payload",
            }
        )

    def _mapping_label(self, payload: dict[str, Any]) -> str:
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
            PlannedMappingAction(temporary_id, action, "blocked", detail)
        )

    # ---- write phase -------------------------------------------------------

    def _execute_write_plan(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            if plan.decision == "reuse":
                # Reuse never mutates the existing record; it is only reported.
                self.reused_records.append(
                    self._record_summary(plan.existing_instance, plan, "reuse", linked=False)
                )
                continue

            instance = plan.existing_instance
            created = False
            if instance is None:
                # Same construction the platform uses in
                # ComplianceAssessment.create_requirement_assessments(): no result, score, or
                # status is set, so no compliance decision is made here.
                instance = RequirementAssessment.objects.create(
                    compliance_assessment=plan.compliance_assessment,
                    requirement=plan.requirement,
                    folder_id=plan.compliance_assessment.folder_id,
                )
                created = True

            linked = False
            if plan.applied_control is not None:
                # M2M add() is idempotent, so re-running Step 7B never duplicates a mapping.
                if not instance.applied_controls.filter(id=plan.applied_control.id).exists():
                    instance.applied_controls.add(plan.applied_control)
                    linked = True

            summary = self._record_summary(
                instance, plan, "create" if created else "reuse", linked=linked
            )
            if created:
                self.created_records.append(summary)
            else:
                self.reused_records.append(summary)

    def _record_summary(self, instance, plan: WritePlan, action: str, *, linked: bool) -> dict[str, Any]:
        return {
            "record_type": RECORD_TYPE,
            "action": action,
            "record_id": str(instance.id),
            "name": plan.target_name,
            "folder_id": str(instance.folder_id),
            "source_temporary_id": plan.source_temporary_id,
            "compliance_assessment_id": str(instance.compliance_assessment_id),
            "requirement_id": str(instance.requirement_id),
            "linked_applied_control_ids": (
                [str(plan.applied_control.id)] if plan.applied_control is not None else []
            ),
            "applied_control_link_added": linked,
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


def execute_framework_control_mapping_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiFrameworkControlMappingCommitService(request=request, payload=payload)
    return service.execute()
