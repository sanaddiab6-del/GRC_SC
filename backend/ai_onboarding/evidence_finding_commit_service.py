from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import (
    AppliedControl,
    Asset,
    ComplianceAssessment,
    Evidence,
    Finding,
    FindingsAssessment,
    Framework,
    Perimeter,
    RiskAssessment,
)
from core.serializers import (
    EvidenceWriteSerializer,
    FindingWriteSerializer,
    FindingsAssessmentWriteSerializer,
)
from iam.models import Folder, RoleAssignment

from .evidence_finding_commit_guardrails import (
    EvidenceFindingCommitValidationError,
    validate_evidence_finding_commit_guardrails,
)


# audit_question suggestions have no dedicated platform model; they are persisted as
# Evidence placeholders (the platform pattern for "evidence to request/collect").
KIND_TO_RECORD_TYPE = {
    "evidence_request": "evidence",
    "audit_question": "evidence",
    "preliminary_finding": "finding",
}


@dataclass
class DecisionOutcome:
    kind: str
    action: str
    source_temporary_id: str
    record_type: str
    status: str
    detail: str
    name: str | None = None
    record_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "kind": self.kind,
            "action": self.action,
            "source_temporary_id": self.source_temporary_id,
            "record_type": self.record_type,
            "status": self.status,
            "detail": self.detail,
        }
        if self.name:
            payload["name"] = self.name
        if self.record_id:
            payload["record_id"] = self.record_id
        return payload


@dataclass
class WritePlan:
    kind: str
    action: str
    source_temporary_id: str
    record_type: str
    # For create:
    create_payload: dict[str, Any] | None = None
    linked_applied_control_ids: list[str] = field(default_factory=list)
    # For reuse:
    existing_instance: Any = None


class AiEvidenceFindingCommitService:
    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []
        self.outcomes: list[DecisionOutcome] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.rejected_items: list[dict[str, Any]] = []
        self.deferred_items: list[dict[str, Any]] = []
        self.skipped_items: list[dict[str, Any]] = []

    # ---- entry point -------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        validate_evidence_finding_commit_guardrails(self.payload)

        resolved = self._plan_and_validate()

        if self.payload["dry_run"]:
            return self._build_response(
                operation_type="dry_run",
                status=self._dry_run_status(),
                needs_human_review=bool(self.blocking_errors),
            )

        if self.blocking_errors:
            raise EvidenceFindingCommitValidationError(
                "ai_evidence_finding_commit_blocked",
                "The approved Step 5B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(
                    operation_type="commit",
                    status="blocked",
                    needs_human_review=True,
                ),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(resolved)
        except EvidenceFindingCommitValidationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a rolled-back commit
            raise EvidenceFindingCommitValidationError(
                "transaction_aborted",
                "Step 5B transaction failed and all writes were rolled back.",
                status_code=422,
                response_payload=self._build_response(
                    operation_type="commit",
                    status="rolled_back",
                    needs_human_review=True,
                    extra_blocking_errors=[
                        {"code": "transaction_aborted", "detail": str(exc), "field": None}
                    ],
                ),
            )

        return self._build_response(
            operation_type="commit",
            status=self._write_status(),
            needs_human_review=False,
        )

    # ---- planning ----------------------------------------------------------

    def _plan_and_validate(self) -> dict[str, Any]:
        context = self._resolve_context(self.payload["case_setup_reference"])
        folder = context.get("folder")
        approved_assets = self._resolve_asset_references(
            self.payload.get("asset_references") or [], folder
        )
        approved_controls = self._resolve_applied_control_references(
            self.payload.get("applied_control_references") or [], folder
        )
        findings_assessment = self._resolve_findings_assessment_reference(
            self.payload.get("findings_assessment_reference"), folder
        )

        self._validate_human_approval()
        self._warn_idempotency_trace_only()

        plans: list[WritePlan] = []
        planned_evidence_names: set[str] = set()

        decision_groups = (
            ("evidence_request_decisions", "evidence_request"),
            ("audit_question_decisions", "audit_question"),
            ("preliminary_finding_decisions", "preliminary_finding"),
        )
        needs_findings_assessment = any(
            decision["action"] == "create"
            for decision in (self.payload.get("preliminary_finding_decisions") or [])
            if decision.get("selected")
        )

        # Create/reuse a FindingsAssessment container only when we will create findings.
        if needs_findings_assessment and findings_assessment is None and folder is not None:
            findings_assessment = self._plan_findings_assessment_container(context, plans)

        for field_name, kind in decision_groups:
            for index, decision in enumerate(self.payload.get(field_name) or []):
                self._plan_decision(
                    field_name,
                    index,
                    kind,
                    decision,
                    context,
                    approved_assets,
                    approved_controls,
                    findings_assessment,
                    plans,
                    planned_evidence_names,
                )

        # Record planned_actions for every create/reuse plan so dry-run (which never
        # runs the write phase) still describes what would happen for each decision.
        self._record_planned_outcomes(plans)

        return {"context": context, "plans": plans, "findings_assessment": findings_assessment}

    def _record_planned_outcomes(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            if plan.action == "create":
                self.outcomes.append(
                    DecisionOutcome(
                        plan.kind, "create", plan.source_temporary_id, plan.record_type,
                        "planned", f"{plan.record_type} would be created.",
                        (plan.create_payload or {}).get("name"),
                    )
                )
            elif plan.action == "create_container":
                self.outcomes.append(
                    DecisionOutcome(
                        plan.kind, "create", plan.source_temporary_id, plan.record_type,
                        "planned", "FindingsAssessment container would be created.",
                        (plan.create_payload or {}).get("name"),
                    )
                )
            elif plan.action == "reuse":
                instance = plan.existing_instance
                self.outcomes.append(
                    DecisionOutcome(
                        plan.kind, "reuse", plan.source_temporary_id, plan.record_type,
                        "planned", f"Existing {plan.record_type} would be reused without mutation.",
                        getattr(instance, "name", None),
                        str(getattr(instance, "id", "")) or None,
                    )
                )

    def _plan_decision(
        self,
        field_name: str,
        index: int,
        kind: str,
        decision: dict[str, Any],
        context: dict[str, Any],
        approved_assets: dict[str, Asset],
        approved_controls: dict[str, AppliedControl],
        findings_assessment: FindingsAssessment | None,
        plans: list[WritePlan],
        planned_evidence_names: set[str],
    ) -> None:
        field_prefix = f"{field_name}[{index}]"
        action = decision["action"]
        temporary_id = decision["temporary_id"]
        record_type = KIND_TO_RECORD_TYPE[kind]
        name = self._resolve_name(decision)

        if not decision.get("selected"):
            self.blocking_errors.append(
                {
                    "code": "candidate_not_selected",
                    "detail": "Submitted Step 5B decisions must have selected=true.",
                    "field": f"{field_prefix}.selected",
                }
            )
            return

        if action == "reject":
            self.rejected_items.append(
                {"kind": kind, "source_temporary_id": temporary_id, "name": name}
            )
            self.outcomes.append(
                DecisionOutcome(kind, "reject", temporary_id, record_type, "ok",
                                "Suggestion rejected by reviewer.", name)
            )
            return

        if action == "defer":
            self.deferred_items.append(
                {"kind": kind, "source_temporary_id": temporary_id, "name": name}
            )
            self.outcomes.append(
                DecisionOutcome(kind, "defer", temporary_id, record_type, "ok",
                                "Suggestion deferred by reviewer.", name)
            )
            return

        if context.get("folder") is None:
            self.blocking_errors.append(
                {
                    "code": "missing_context_folder",
                    "detail": "A valid folder_id is required before Step 5B can create or reuse records.",
                    "field": "case_setup_reference.folder_id",
                }
            )
            return

        linked_control_ids = self._resolve_linked_control_ids(
            field_prefix, decision, approved_controls
        )

        if action == "reuse":
            self._plan_reuse(field_prefix, kind, record_type, decision, context["folder"],
                             findings_assessment, plans)
            return

        # action == "create"
        self._plan_create(
            field_prefix,
            kind,
            record_type,
            decision,
            name,
            context,
            findings_assessment,
            linked_control_ids,
            plans,
            planned_evidence_names,
        )

    def _plan_reuse(self, field_prefix, kind, record_type, decision, folder,
                    findings_assessment, plans) -> None:
        temporary_id = decision["temporary_id"]
        existing_id = decision["selected_existing_id"]
        if record_type == "evidence":
            instance = Evidence.objects.filter(id=existing_id).select_related("folder").first()
            model = Evidence
        else:
            instance = Finding.objects.filter(id=existing_id).select_related("folder").first()
            model = Finding

        if instance is None:
            self.blocking_errors.append(
                {
                    "code": "reuse_target_not_found",
                    "detail": "selected_existing_id does not match an existing record.",
                    "field": f"{field_prefix}.selected_existing_id",
                }
            )
            return

        if not RoleAssignment.is_object_readable(self.user, model, instance.id):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to reuse the selected record.",
                    "field": f"{field_prefix}.selected_existing_id",
                }
            )
            return

        if str(instance.folder_id) != str(folder.id):
            self.blocking_errors.append(
                {
                    "code": "reuse_out_of_scope",
                    "detail": "selected_existing_id must belong to case_setup_reference.folder_id.",
                    "field": f"{field_prefix}.selected_existing_id",
                }
            )
            return

        plans.append(
            WritePlan(kind=kind, action="reuse", source_temporary_id=temporary_id,
                      record_type=record_type, existing_instance=instance)
        )

    def _plan_create(self, field_prefix, kind, record_type, decision, name, context,
                     findings_assessment, linked_control_ids, plans, planned_evidence_names) -> None:
        temporary_id = decision["temporary_id"]
        folder = context["folder"]
        approved_fields = decision.get("approved_fields") or {}
        summary = decision.get("original_suggestion_summary") or {}
        description = approved_fields.get("description") or summary.get("rationale") or summary.get("summary") or ""

        if record_type == "evidence":
            # Duplicate detection: reuse an existing folder-scoped Evidence with the same name.
            duplicate = Evidence.objects.filter(folder=folder, name__iexact=name).first()
            if duplicate is not None:
                self.warnings.append(
                    {
                        "code": "duplicate_reused",
                        "detail": f"An existing Evidence named '{name}' was found in the folder and will be reused.",
                        "field": f"{field_prefix}.approved_fields.name",
                    }
                )
                plans.append(
                    WritePlan(kind=kind, action="reuse", source_temporary_id=temporary_id,
                              record_type=record_type, existing_instance=duplicate)
                )
                return

            if name.lower() in planned_evidence_names:
                self.warnings.append(
                    {
                        "code": "duplicate_in_batch_skipped",
                        "detail": f"Another selected decision already creates Evidence named '{name}'; this duplicate was skipped.",
                        "field": f"{field_prefix}.approved_fields.name",
                    }
                )
                self.skipped_items.append(
                    {"kind": kind, "source_temporary_id": temporary_id, "name": name,
                     "skip_reason": "duplicate_in_batch"}
                )
                self.outcomes.append(
                    DecisionOutcome(kind, "create", temporary_id, record_type, "skipped",
                                    "Duplicate name within the submitted batch.", name)
                )
                return

            create_payload = {
                "name": name,
                "description": description,
                "folder": str(folder.id),
                "status": Evidence.Status.DRAFT,
                "applied_controls": linked_control_ids,
            }
            if not self._create_payload_is_valid(EvidenceWriteSerializer, create_payload, field_prefix):
                return
            planned_evidence_names.add(name.lower())
            plans.append(
                WritePlan(kind=kind, action="create", source_temporary_id=temporary_id,
                          record_type=record_type, create_payload=create_payload,
                          linked_applied_control_ids=linked_control_ids)
            )
            return

        # record_type == "finding"
        if findings_assessment is None:
            self.blocking_errors.append(
                {
                    "code": "findings_assessment_unavailable",
                    "detail": "A FindingsAssessment container is required before findings can be created.",
                    "field": f"{field_prefix}.action",
                }
            )
            return

        duplicate = self._find_duplicate_finding(findings_assessment, name)
        if duplicate is not None:
            self.warnings.append(
                {
                    "code": "duplicate_reused",
                    "detail": f"An existing Finding named '{name}' was found in the findings assessment and will be reused.",
                    "field": f"{field_prefix}.approved_fields.name",
                }
            )
            plans.append(
                WritePlan(kind=kind, action="reuse", source_temporary_id=temporary_id,
                          record_type=record_type, existing_instance=duplicate)
            )
            return

        severity = approved_fields.get("severity")
        # findings_assessment is injected at write time; the plan payload omits it so a
        # not-yet-created container does not require an id during planning.
        create_payload = {
            "name": name,
            "description": description,
            "status": Finding.Status.IDENTIFIED,
            "observation": summary.get("rationale") or "",
            "applied_controls": linked_control_ids,
        }
        if severity is not None:
            create_payload["severity"] = severity
        # Validate up-front only when the findings assessment already exists.
        if not isinstance(findings_assessment, _PlannedContainer):
            validation_payload = dict(create_payload, findings_assessment=str(findings_assessment.id))
            if not self._create_payload_is_valid(FindingWriteSerializer, validation_payload, field_prefix):
                return
        plans.append(
            WritePlan(kind=kind, action="create", source_temporary_id=temporary_id,
                      record_type=record_type, create_payload=create_payload,
                      linked_applied_control_ids=linked_control_ids)
        )

    def _plan_findings_assessment_container(self, context, plans) -> FindingsAssessment | None:
        folder = context["folder"]
        perimeter = context.get("perimeter")
        name = "AI Step 5B Preliminary Findings"
        # Reuse an existing container with the same name in the folder if present.
        existing = FindingsAssessment.objects.filter(folder=folder, name=name).first()
        if existing is not None:
            return existing

        payload = {
            "name": name,
            "folder": str(folder.id),
            "category": FindingsAssessment.Category.AUDIT,
            "status": "planned",
        }
        if perimeter is not None:
            payload["perimeter"] = str(perimeter.id)
        if not self._create_payload_is_valid(
            FindingsAssessmentWriteSerializer, payload, "findings_assessment_reference"
        ):
            return None
        plans.append(
            WritePlan(kind="preliminary_finding", action="create_container",
                      source_temporary_id="findings-assessment-container",
                      record_type="findings_assessment", create_payload=payload)
        )
        # Return a lightweight marker so finding creates can proceed during planning;
        # the real instance is created first in the write phase.
        return _PlannedContainer(folder=folder)

    # ---- resolution helpers ------------------------------------------------

    def _resolve_context(self, reference: dict[str, Any]) -> dict[str, Any]:
        folder = Folder.objects.filter(id=reference["folder_id"]).first()
        if folder is None:
            self.blocking_errors.append(
                {"code": "folder_not_found", "detail": "folder_id does not match an existing Folder.",
                 "field": "case_setup_reference.folder_id"}
            )
        elif not RoleAssignment.is_object_readable(self.user, Folder, folder.id):
            self.blocking_errors.append(
                {"code": "permission_denied", "detail": "You do not have permission to use the selected Folder.",
                 "field": "case_setup_reference.folder_id"}
            )
            folder = None

        perimeter = self._resolve_context_object(
            Perimeter, reference.get("perimeter_id"), "case_setup_reference.perimeter_id", "Perimeter"
        )
        compliance_assessment = self._resolve_context_object(
            ComplianceAssessment, reference.get("compliance_assessment_id"),
            "case_setup_reference.compliance_assessment_id", "ComplianceAssessment"
        )
        risk_assessment = self._resolve_context_object(
            RiskAssessment, reference.get("risk_assessment_id"),
            "case_setup_reference.risk_assessment_id", "RiskAssessment"
        )
        framework = self._resolve_context_object(
            Framework, reference.get("selected_framework_id"),
            "case_setup_reference.selected_framework_id", "Framework"
        )

        if folder is not None and perimeter is not None and perimeter.folder_id != folder.id:
            self.blocking_errors.append(
                {"code": "invalid_context_reference",
                 "detail": "perimeter_id must belong to the selected folder_id.",
                 "field": "case_setup_reference.perimeter_id"}
            )

        return {
            "folder": folder,
            "perimeter": perimeter,
            "compliance_assessment": compliance_assessment,
            "risk_assessment": risk_assessment,
            "framework": framework,
        }

    def _resolve_context_object(self, model, object_id, field, label):
        if object_id is None:
            return None
        instance = model.objects.filter(id=object_id).first()
        if instance is None:
            self.blocking_errors.append(
                {"code": f"{label.lower()}_not_found",
                 "detail": f"{field.split('.')[-1]} does not match an existing {label}.", "field": field}
            )
            return None
        if not RoleAssignment.is_object_readable(self.user, model, instance.id):
            self.blocking_errors.append(
                {"code": "permission_denied",
                 "detail": f"You do not have permission to use the selected {label}.", "field": field}
            )
            return None
        return instance

    def _resolve_asset_references(self, asset_references, folder) -> dict[str, Asset]:
        resolved: dict[str, Asset] = {}
        for index, reference in enumerate(asset_references):
            field_name = f"asset_references[{index}].asset_id"
            asset = Asset.objects.filter(id=reference["asset_id"]).select_related("folder").first()
            if asset is None:
                self.blocking_errors.append(
                    {"code": "asset_not_found", "detail": "asset_id does not match an existing Asset.",
                     "field": field_name}
                )
                continue
            if not RoleAssignment.is_object_readable(self.user, Asset, asset.id):
                self.blocking_errors.append(
                    {"code": "permission_denied", "detail": "You do not have permission to use the selected Asset.",
                     "field": field_name}
                )
                continue
            if folder is not None and asset.folder_id != folder.id:
                self.blocking_errors.append(
                    {"code": "invalid_context_reference",
                     "detail": "asset_id must belong to case_setup_reference.folder_id.", "field": field_name}
                )
                continue
            resolved[str(asset.id)] = asset
        return resolved

    def _resolve_applied_control_references(self, control_references, folder) -> dict[str, AppliedControl]:
        resolved: dict[str, AppliedControl] = {}
        for index, reference in enumerate(control_references):
            field_name = f"applied_control_references[{index}].applied_control_id"
            control = (
                AppliedControl.objects.filter(id=reference["applied_control_id"])
                .select_related("folder").first()
            )
            if control is None:
                self.blocking_errors.append(
                    {"code": "applied_control_not_found",
                     "detail": "applied_control_id does not match an existing AppliedControl.", "field": field_name}
                )
                continue
            if not RoleAssignment.is_object_readable(self.user, AppliedControl, control.id):
                self.blocking_errors.append(
                    {"code": "permission_denied",
                     "detail": "You do not have permission to use the selected AppliedControl.", "field": field_name}
                )
                continue
            if folder is not None and control.folder_id != folder.id:
                self.blocking_errors.append(
                    {"code": "invalid_context_reference",
                     "detail": "applied_control_id must belong to case_setup_reference.folder_id.", "field": field_name}
                )
                continue
            resolved[str(control.id)] = control
        return resolved

    def _resolve_findings_assessment_reference(self, reference, folder) -> FindingsAssessment | None:
        if not reference:
            return None
        fa = FindingsAssessment.objects.filter(id=reference["findings_assessment_id"]).select_related("folder").first()
        if fa is None:
            self.blocking_errors.append(
                {"code": "findings_assessment_not_found",
                 "detail": "findings_assessment_id does not match an existing FindingsAssessment.",
                 "field": "findings_assessment_reference.findings_assessment_id"}
            )
            return None
        if not RoleAssignment.is_object_readable(self.user, FindingsAssessment, fa.id):
            self.blocking_errors.append(
                {"code": "permission_denied",
                 "detail": "You do not have permission to use the selected FindingsAssessment.",
                 "field": "findings_assessment_reference.findings_assessment_id"}
            )
            return None
        if folder is not None and fa.folder_id != folder.id:
            self.blocking_errors.append(
                {"code": "invalid_context_reference",
                 "detail": "findings_assessment_id must belong to case_setup_reference.folder_id.",
                 "field": "findings_assessment_reference.findings_assessment_id"}
            )
            return None
        return fa

    def _resolve_linked_control_ids(self, field_prefix, decision, approved_controls) -> list[str]:
        summary = decision.get("original_suggestion_summary") or {}
        requested = [str(cid) for cid in summary.get("linked_applied_control_ids") or []]
        resolved: list[str] = []
        for cid in requested:
            if cid in approved_controls:
                resolved.append(cid)
            else:
                self.warnings.append(
                    {"code": "linked_control_dropped",
                     "detail": "A linked applied control was not in applied_control_references and was dropped.",
                     "field": f"{field_prefix}.original_suggestion_summary.linked_applied_control_ids"}
                )
        return resolved

    def _find_duplicate_finding(self, findings_assessment, name) -> Finding | None:
        if isinstance(findings_assessment, _PlannedContainer):
            return None
        return Finding.objects.filter(findings_assessment=findings_assessment, name__iexact=name).first()

    def _resolve_name(self, decision) -> str:
        approved_fields = decision.get("approved_fields") or {}
        summary = decision.get("original_suggestion_summary") or {}
        name = (
            approved_fields.get("name")
            or summary.get("title")
            or summary.get("question_text")
            or "Untitled Step 5B item"
        )
        return str(name).strip()[:200]

    def _create_payload_is_valid(self, serializer_class, payload, field_prefix) -> bool:
        serializer = serializer_class(data=payload, context={"request": self.request})
        if serializer.is_valid():
            return True
        self.blocking_errors.append(
            {
                "code": "invalid_record_payload",
                "detail": "Approved fields did not pass platform validation.",
                "field": field_prefix,
                "errors": serializer.errors,
            }
        )
        return False

    def _validate_human_approval(self) -> None:
        if self.payload["dry_run"]:
            return
        for field_name in (
            "evidence_request_decisions",
            "audit_question_decisions",
            "preliminary_finding_decisions",
        ):
            for index, decision in enumerate(self.payload.get(field_name) or []):
                if decision["action"] in {"create", "reuse"} and not decision["human_approved"]:
                    self.blocking_errors.append(
                        {
                            "code": "human_approval_required",
                            "detail": "create and reuse decisions must be human approved for write mode.",
                            "field": f"{field_name}[{index}].human_approved",
                        }
                    )

    def _warn_idempotency_trace_only(self) -> None:
        if not self.payload["dry_run"]:
            self.warnings.append(
                {
                    "code": "idempotency_trace_only",
                    "detail": "Step 5B uses idempotency_key for traceability and folder-scoped duplicate reuse, but does not persist idempotency receipts.",
                }
            )

    # ---- write phase -------------------------------------------------------

    def _execute_write_plan(self, resolved) -> None:
        findings_assessment = resolved.get("findings_assessment")

        # Create the FindingsAssessment container first if one was planned.
        container_plan = next(
            (p for p in resolved["plans"] if p.action == "create_container"), None
        )
        real_findings_assessment = findings_assessment
        if container_plan is not None:
            real_findings_assessment = self._save_from_payload(
                FindingsAssessmentWriteSerializer, container_plan.create_payload
            )
            self.created_records.append(
                self._record_summary(real_findings_assessment, "findings_assessment",
                                      "preliminary_finding", "create", container_plan.source_temporary_id)
            )
        elif isinstance(findings_assessment, _PlannedContainer):
            real_findings_assessment = None

        for plan in resolved["plans"]:
            if plan.action == "create_container":
                continue
            if plan.action == "reuse":
                self._record_reuse(plan)
                continue
            if plan.action != "create":
                continue

            if plan.record_type == "evidence":
                instance = self._save_from_payload(EvidenceWriteSerializer, plan.create_payload)
            else:
                payload = dict(plan.create_payload)
                payload["findings_assessment"] = str(real_findings_assessment.id)
                instance = self._save_from_payload(FindingWriteSerializer, payload)

            self.created_records.append(
                self._record_summary(instance, plan.record_type, plan.kind, "create",
                                     plan.source_temporary_id)
            )

    def _record_reuse(self, plan) -> None:
        instance = plan.existing_instance
        self.reused_records.append(
            self._record_summary(instance, plan.record_type, plan.kind, "reuse",
                                 plan.source_temporary_id)
        )

    def _save_from_payload(self, serializer_class, payload):
        serializer = serializer_class(data=payload, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def _record_summary(self, instance, record_type, kind, action, source_temporary_id) -> dict[str, Any]:
        return {
            "record_type": record_type,
            "kind": kind,
            "action": action,
            "record_id": str(instance.id),
            "name": instance.name,
            "folder_id": str(instance.folder_id),
            "source_temporary_id": source_temporary_id,
        }

    # ---- response ----------------------------------------------------------

    def _counts(self) -> dict[str, int]:
        return {
            "created": len(self.created_records),
            "reused": len(self.reused_records),
            "rejected": len(self.rejected_items),
            "deferred": len(self.deferred_items),
            "skipped": len(self.skipped_items),
        }

    def _dry_run_status(self) -> str:
        if self.blocking_errors:
            return "blocked"
        if self.warnings:
            return "validated_with_warnings"
        return "validated"

    def _write_status(self) -> str:
        if self.created_records and self.reused_records:
            return "created_and_reused"
        if self.created_records:
            return "created"
        if self.reused_records:
            return "reused_only"
        return "completed"

    def _blocking_status_code(self) -> int:
        if any(item.get("code") == "permission_denied" for item in self.blocking_errors):
            return 403
        return 422

    def _build_response(self, *, operation_type, status, needs_human_review,
                        extra_blocking_errors=None) -> dict[str, Any]:
        blocking_errors = [*self.blocking_errors]
        if extra_blocking_errors:
            blocking_errors.extend(extra_blocking_errors)

        return {
            "operation_type": operation_type,
            "status": status,
            "dry_run": self.payload["dry_run"],
            "no_ai_used": True,
            "no_write": self.payload["dry_run"],
            "idempotency_key": self.payload.get("idempotency_key"),
            "source_step1_draft_hash": self.payload["source_step1_draft_hash"],
            "source_asset_commit_hash": self.payload["source_asset_commit_hash"],
            "source_applied_control_commit_hash": self.payload["source_applied_control_commit_hash"],
            "source_evidence_finding_draft_hash": self.payload["source_evidence_finding_draft_hash"],
            "created_records": [] if operation_type == "dry_run" else self.created_records,
            "reused_records": [] if operation_type == "dry_run" else self.reused_records,
            "rejected_items": self.rejected_items,
            "deferred_items": self.deferred_items,
            "skipped_items": self.skipped_items,
            "counts": self._counts() if operation_type != "dry_run" else {
                "created": 0,
                "reused": 0,
                "rejected": len(self.rejected_items),
                "deferred": len(self.deferred_items),
                "skipped": len(self.skipped_items),
            },
            "planned_actions": [outcome.as_dict() for outcome in self.outcomes],
            "warnings": self.warnings,
            "blocking_errors": blocking_errors,
            "needs_human_review": needs_human_review,
            "next_allowed_steps": self._next_allowed_steps(operation_type, blocking_errors),
        }

    def _next_allowed_steps(self, operation_type, blocking_errors) -> list[str]:
        if operation_type == "dry_run":
            if blocking_errors:
                return ["Resolve the blocking errors and rerun the Step 5B dry-run."]
            return [
                "If the reviewed payload is final, resubmit with dry_run=false and approved_by_user=true."
            ]
        if blocking_errors:
            return ["Review the blocking errors, rerun dry-run, and resubmit once resolved."]
        return ["Step 5B evidence/finding commit is complete."]


class _PlannedContainer:
    """Marker used during planning to represent a not-yet-created FindingsAssessment."""

    def __init__(self, folder):
        self.folder = folder
        self.folder_id = folder.id


def execute_evidence_finding_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiEvidenceFindingCommitService(request=request, payload=payload)
    return service.execute()
