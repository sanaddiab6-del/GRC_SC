from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import AppliedControl, Asset, Finding
from core.serializers import AppliedControlWriteSerializer
from iam.models import Folder, RoleAssignment

from .remediation_action_commit_guardrails import (
    RemediationActionCommitValidationError,
    validate_remediation_action_commit_guardrails,
)


# Step 6B writes remediation actions to core.AppliedControl, the platform model for
# corrective/remediation measures. Finding linkage uses AppliedControl.findings, the
# reverse side of Finding.applied_controls, so the write only ever touches the new
# AppliedControl row and its own m2m rows. Findings themselves are never mutated.
RECORD_TYPE = "applied_control"

# Step 6A advisory priority -> AppliedControl.PRIORITY (P1 is the most urgent).
PRIORITY_MAP = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}

# Step 6A fields with no equivalent AppliedControl column. They are preserved in the
# description instead of being forced into an unrelated field, and each occurrence is
# reported as a warning.
UNMAPPED_FIELD_LABELS = {
    "suggested_owner": "Suggested owner",
    "target_timeline": "Target timeline",
    "success_criteria": "Success criteria",
    "required_follow_up_evidence": "Required follow-up evidence",
    "rationale": "Rationale",
}


@dataclass
class PlannedRemediationAction:
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
    linked_finding_ids: list[str] = field(default_factory=list)
    linked_asset_ids: list[str] = field(default_factory=list)


class AiRemediationActionCommitService:
    """Deterministic Step 6B commit. No AI provider is imported or called here."""

    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedRemediationAction] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.rejected_records: list[dict[str, Any]] = []
        self.deferred_records: list[dict[str, Any]] = []
        self.skipped_records: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    # ---- entry point -------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        validate_remediation_action_commit_guardrails(self.payload)

        plans = self._plan_and_validate()

        if self.payload["dry_run"]:
            return self._build_response(dry_run=True, commit_status=self._dry_run_status())

        if self.blocking_errors:
            raise RemediationActionCommitValidationError(
                "ai_remediation_action_commit_blocked",
                "The approved Step 6B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(dry_run=False, commit_status="blocked"),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(plans)
        except RemediationActionCommitValidationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a rolled-back commit
            self.created_records = []
            self.reused_records = []
            raise RemediationActionCommitValidationError(
                "transaction_aborted",
                "Step 6B transaction failed and all writes were rolled back.",
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
        if folder is not None:
            self._check_add_permission(folder)

        plans: list[WritePlan] = []
        planned_names: set[str] = set()

        for index, decision in enumerate(self.payload.get("decisions") or []):
            self._plan_decision(index, decision, folder, plans, planned_names)

        return plans

    def _plan_decision(
        self,
        index: int,
        decision: dict[str, Any],
        folder: Folder | None,
        plans: list[WritePlan],
        planned_names: set[str],
    ) -> None:
        field_prefix = f"decisions[{index}]"
        temporary_id = decision["temporary_id"]
        action = decision["decision"]
        payload = decision.get("payload") or {}
        title = (payload.get("title") or "").strip()

        if not decision.get("selected"):
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": title or None,
                    "skip_reason": "not_selected",
                }
            )
            self.planned_actions.append(
                PlannedRemediationAction(
                    temporary_id, action, "skipped",
                    "Decision was not selected by the reviewer.", target_name=title or None,
                )
            )
            return

        if action == "reject":
            self.rejected_records.append(
                {"source_temporary_id": temporary_id, "title": title or None}
            )
            self.planned_actions.append(
                PlannedRemediationAction(
                    temporary_id, "reject", "ok",
                    "Remediation action rejected by reviewer.", target_name=title or None,
                )
            )
            return

        if action == "defer":
            self.deferred_records.append(
                {"source_temporary_id": temporary_id, "title": title or None}
            )
            self.planned_actions.append(
                PlannedRemediationAction(
                    temporary_id, "defer", "ok",
                    "Remediation action deferred by reviewer.", target_name=title or None,
                )
            )
            return

        if folder is None:
            self.planned_actions.append(
                PlannedRemediationAction(
                    temporary_id, action, "blocked",
                    "A valid folder_reference is required before Step 6B can create or reuse records.",
                    target_name=title or None,
                )
            )
            return

        if action == "reuse":
            self._plan_reuse(field_prefix, temporary_id, decision, folder, plans)
            return

        self._plan_create(
            field_prefix, temporary_id, payload, title, folder, plans, planned_names
        )

    def _plan_reuse(
        self,
        field_prefix: str,
        temporary_id: str,
        decision: dict[str, Any],
        folder: Folder,
        plans: list[WritePlan],
    ) -> None:
        existing_id = decision["existing_record_reference"]
        instance = (
            AppliedControl.objects.filter(id=existing_id).select_related("folder").first()
        )

        if instance is None:
            self._block(
                "reuse_target_not_found",
                "existing_record_reference does not match an existing AppliedControl.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        if not RoleAssignment.is_object_readable(self.user, AppliedControl, instance.id):
            self._block(
                "permission_denied",
                "You do not have permission to reuse the selected AppliedControl.",
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
            )
        )
        self.planned_actions.append(
            PlannedRemediationAction(
                temporary_id, "reuse", "planned",
                "Existing AppliedControl would be reused without mutation.",
                target_name=instance.name,
            )
        )

    def _plan_create(
        self,
        field_prefix: str,
        temporary_id: str,
        payload: dict[str, Any],
        title: str,
        folder: Folder,
        plans: list[WritePlan],
        planned_names: set[str],
    ) -> None:
        # Duplicate detection: an existing folder-scoped AppliedControl with the same
        # name is reused rather than duplicated.
        duplicate = AppliedControl.objects.filter(folder=folder, name__iexact=title).first()
        if duplicate is not None:
            self.warnings.append(
                {
                    "code": "duplicate_reused",
                    "detail": (
                        f"An existing AppliedControl named '{title}' was found in the folder "
                        "and will be reused instead of creating a duplicate."
                    ),
                    "field": f"{field_prefix}.payload.title",
                }
            )
            plans.append(
                WritePlan(
                    source_temporary_id=temporary_id,
                    decision="reuse",
                    target_name=duplicate.name,
                    existing_instance=duplicate,
                )
            )
            self.planned_actions.append(
                PlannedRemediationAction(
                    temporary_id, "reuse", "planned",
                    "A folder-scoped duplicate exists; it would be reused without mutation.",
                    target_name=duplicate.name,
                )
            )
            return

        if title.lower() in planned_names:
            self.warnings.append(
                {
                    "code": "duplicate_in_batch_skipped",
                    "detail": (
                        f"Another selected decision already creates a remediation action named "
                        f"'{title}'; this duplicate was skipped."
                    ),
                    "field": f"{field_prefix}.payload.title",
                }
            )
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": title,
                    "skip_reason": "duplicate_in_batch",
                }
            )
            self.planned_actions.append(
                PlannedRemediationAction(
                    temporary_id, "create", "skipped",
                    "Duplicate title within the submitted batch.", target_name=title,
                )
            )
            return

        linked_finding_ids = self._resolve_linked_findings(field_prefix, payload, folder)
        linked_asset_ids = self._resolve_linked_assets(field_prefix, payload, folder)
        self._warn_unsupported_control_linkage(field_prefix, payload)

        create_payload = {
            "folder": str(folder.id),
            "name": title[:200],
            "description": self._build_description(field_prefix, payload),
            "status": AppliedControl.Status.TO_DO,
            "priority": PRIORITY_MAP[payload["priority"]],
            "findings": linked_finding_ids,
            "assets": linked_asset_ids,
        }

        serializer = AppliedControlWriteSerializer(
            data=create_payload, context={"request": self.request}
        )
        if not serializer.is_valid():
            self.blocking_errors.append(
                {
                    "code": "invalid_remediation_action_payload",
                    "detail": "The reviewed remediation action did not pass platform AppliedControl validation.",
                    "field": f"{field_prefix}.payload",
                    "errors": serializer.errors,
                }
            )
            self.planned_actions.append(
                PlannedRemediationAction(
                    temporary_id, "create", "blocked",
                    "Reviewed remediation action failed platform validation.", target_name=title,
                )
            )
            return

        planned_names.add(title.lower())
        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="create",
                target_name=title,
                create_payload=create_payload,
                linked_finding_ids=linked_finding_ids,
                linked_asset_ids=linked_asset_ids,
            )
        )
        self.planned_actions.append(
            PlannedRemediationAction(
                temporary_id, "create", "planned",
                "AppliedControl remediation action is valid and ready for execution.",
                target_name=title,
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

    def _check_add_permission(self, folder: Folder) -> None:
        permission = Permission.objects.filter(codename="add_appliedcontrol").first()
        if permission is None or not RoleAssignment.is_access_allowed(
            self.user, permission, folder
        ):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to add applied controls in the selected scope.",
                    "field": "folder_reference",
                }
            )

    def _resolve_linked_findings(
        self, field_prefix: str, payload: dict[str, Any], folder: Folder
    ) -> list[str]:
        reference = payload.get("linked_finding_reference")
        title = payload.get("linked_finding_title")
        if not reference and not title:
            return []

        instance = self._lookup_in_folder(Finding, folder, reference, title)
        if instance is None:
            self.warnings.append(
                {
                    "code": "finding_linkage_not_applied",
                    "detail": (
                        "The referenced finding was not found in the selected folder; the "
                        "remediation action was created without finding linkage."
                    ),
                    "field": f"{field_prefix}.payload.linked_finding_reference",
                }
            )
            return []

        if not RoleAssignment.is_object_readable(self.user, Finding, instance.id):
            self.warnings.append(
                {
                    "code": "finding_linkage_not_applied",
                    "detail": (
                        "You do not have permission to read the referenced finding; the "
                        "remediation action was created without finding linkage."
                    ),
                    "field": f"{field_prefix}.payload.linked_finding_reference",
                }
            )
            return []

        return [str(instance.id)]

    def _resolve_linked_assets(
        self, field_prefix: str, payload: dict[str, Any], folder: Folder
    ) -> list[str]:
        reference = payload.get("linked_asset_reference")
        title = payload.get("linked_asset_title")
        if not reference and not title:
            return []

        instance = self._lookup_in_folder(Asset, folder, reference, title)
        if instance is None:
            self.warnings.append(
                {
                    "code": "asset_linkage_not_applied",
                    "detail": (
                        "The referenced asset was not found in the selected folder; the "
                        "remediation action was created without asset linkage."
                    ),
                    "field": f"{field_prefix}.payload.linked_asset_reference",
                }
            )
            return []

        if not RoleAssignment.is_object_readable(self.user, Asset, instance.id):
            self.warnings.append(
                {
                    "code": "asset_linkage_not_applied",
                    "detail": (
                        "You do not have permission to read the referenced asset; the "
                        "remediation action was created without asset linkage."
                    ),
                    "field": f"{field_prefix}.payload.linked_asset_reference",
                }
            )
            return []

        return [str(instance.id)]

    def _warn_unsupported_control_linkage(
        self, field_prefix: str, payload: dict[str, Any]
    ) -> None:
        if not payload.get("linked_control_reference") and not payload.get(
            "linked_control_title"
        ):
            return
        # AppliedControl has no applied-control-to-applied-control relation. Rather than
        # invent schema, the linkage is reported and preserved in the description.
        self.warnings.append(
            {
                "code": "control_linkage_not_supported",
                "detail": (
                    "AppliedControl has no applied-control-to-applied-control link field; the "
                    "linked control was preserved in the description instead."
                ),
                "field": f"{field_prefix}.payload.linked_control_reference",
            }
        )

    def _lookup_in_folder(self, model, folder: Folder, reference, title):
        if reference:
            instance = model.objects.filter(folder=folder, ref_id__iexact=reference).first()
            if instance is not None:
                return instance
            instance = model.objects.filter(folder=folder, name__iexact=reference).first()
            if instance is not None:
                return instance
        if title:
            return model.objects.filter(folder=folder, name__iexact=title).first()
        return None

    def _build_description(self, field_prefix: str, payload: dict[str, Any]) -> str:
        """Compose the AppliedControl description from the reviewed remediation action.

        Step 6A carries advisory context (owner, timeline, criteria, evidence,
        rationale) that has no dedicated AppliedControl column. It is preserved as
        readable text and reported through a warning rather than written into an
        unrelated field.
        """
        sections: list[str] = []
        base = payload.get("description")
        if base:
            sections.append(base)

        preserved: list[str] = []

        for key in ("rationale", "suggested_owner", "target_timeline"):
            value = payload.get(key)
            if value:
                sections.append(f"{UNMAPPED_FIELD_LABELS[key]}: {value}")
                preserved.append(key)

        for key in ("success_criteria", "required_follow_up_evidence"):
            entries = payload.get(key) or []
            if entries:
                bullet_list = "\n".join(f"- {entry}" for entry in entries)
                sections.append(f"{UNMAPPED_FIELD_LABELS[key]}:\n{bullet_list}")
                preserved.append(key)

        linked_control = payload.get("linked_control_title") or payload.get(
            "linked_control_reference"
        )
        if linked_control:
            sections.append(f"Related applied control: {linked_control}")

        sections.append(
            "Source: AI Step 6A remediation suggestion "
            f"{payload.get('temporary_id')} (advisory, confidence "
            f"{payload.get('confidence')}, review_status {payload.get('review_status')}). "
            "Written deterministically in Step 6B after human approval."
        )

        if preserved:
            self.warnings.append(
                {
                    "code": "advisory_fields_preserved_as_text",
                    "detail": (
                        "AppliedControl has no dedicated field for "
                        f"{', '.join(preserved)}; the values were preserved in the description."
                    ),
                    "field": f"{field_prefix}.payload",
                }
            )

        return "\n\n".join(sections)

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
            PlannedRemediationAction(temporary_id, action, "blocked", detail)
        )

    # ---- write phase -------------------------------------------------------

    def _execute_write_plan(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            if plan.decision == "reuse":
                # Reuse never mutates the existing record; it is only reported.
                instance = plan.existing_instance
                self.reused_records.append(self._record_summary(instance, plan, "reuse"))
                continue

            serializer = AppliedControlWriteSerializer(
                data=plan.create_payload, context={"request": self.request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            self.created_records.append(self._record_summary(instance, plan, "create"))

    def _record_summary(self, instance, plan: WritePlan, action: str) -> dict[str, Any]:
        return {
            "record_type": RECORD_TYPE,
            "action": action,
            "record_id": str(instance.id),
            "name": instance.name,
            "folder_id": str(instance.folder_id),
            "source_temporary_id": plan.source_temporary_id,
            "linked_finding_ids": list(plan.linked_finding_ids),
            "linked_asset_ids": list(plan.linked_asset_ids),
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


def execute_remediation_action_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiRemediationActionCommitService(request=request, payload=payload)
    return service.execute()
