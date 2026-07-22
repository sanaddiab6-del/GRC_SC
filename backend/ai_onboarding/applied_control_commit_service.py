from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import AppliedControl, Asset, ComplianceAssessment, Framework, Perimeter, RiskAssessment
from core.serializers import AppliedControlWriteSerializer
from iam.models import Folder, RoleAssignment

from .applied_control_commit_guardrails import (
	AppliedControlCommitValidationError,
	validate_applied_control_commit_guardrails,
)
from .applied_control_suggestion_service import _find_candidate_matches


@dataclass
class PlannedAppliedControlAction:
	source_temporary_id: str
	action: str
	status: str
	detail: str
	target_name: str | None = None

	def as_dict(self) -> dict[str, Any]:
		payload = {
			"source_temporary_id": self.source_temporary_id,
			"action": self.action,
			"status": self.status,
			"detail": self.detail,
		}
		if self.target_name:
			payload["target_name"] = self.target_name
		return payload


class AiAppliedControlCommitService:
	def __init__(self, *, request, payload: dict[str, Any]):
		self.request = request
		self.user = request.user
		self.payload = payload
		self.planned_actions: list[PlannedAppliedControlAction] = []
		self.created_applied_controls: list[dict[str, Any]] = []
		self.reused_applied_controls: list[dict[str, Any]] = []
		self.rejected_applied_controls: list[dict[str, Any]] = []
		self.deferred_applied_controls: list[dict[str, Any]] = []
		self.skipped_applied_controls: list[dict[str, Any]] = []
		self.warnings: list[dict[str, Any]] = []
		self.blocking_errors: list[dict[str, Any]] = []

	def execute(self) -> dict[str, Any]:
		validate_applied_control_commit_guardrails(self.payload)

		resolved = self._plan_and_validate()
		if self.payload["dry_run"]:
			return self._build_response(
				operation_type="dry_run",
				status=self._dry_run_status(),
				needs_human_review=bool(self.blocking_errors),
			)

		if self.blocking_errors:
			raise AppliedControlCommitValidationError(
				"ai_applied_control_commit_blocked",
				"The approved Step 4B payload is blocked and cannot be executed.",
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
		except AppliedControlCommitValidationError:
			raise
		except Exception as exc:
			self._mark_transaction_rolled_back(resolved)
			raise AppliedControlCommitValidationError(
				"transaction_aborted",
				"Step 4B transaction failed and all writes were rolled back.",
				status_code=422,
				blocking_errors=[
					{
						"code": "transaction_aborted",
						"detail": str(exc),
						"field": None,
					}
				],
				response_payload=self._build_response(
					operation_type="commit",
					status="rolled_back",
					needs_human_review=True,
					extra_blocking_errors=[
						{
							"code": "transaction_aborted",
							"detail": str(exc),
							"field": None,
						}
					],
				),
			)

		return self._build_response(
			operation_type="commit",
			status=self._write_status(),
			needs_human_review=False,
		)

	def _plan_and_validate(self) -> dict[str, Any]:
		context = self._resolve_context(self.payload["case_setup_reference"])
		approved_assets = self._resolve_asset_references(
			self.payload["asset_references"],
			context.get("folder"),
		)
		folder_controls = self._visible_folder_controls(context["folder"]) if context.get("folder") else []
		plans = []
		self._validate_human_approval()
		self._warn_idempotency_trace_only()
		for index, decision in enumerate(self.payload["applied_control_decisions"]):
			plans.append(
				self._resolve_applied_control_decision(
					index,
					decision,
					context,
					folder_controls,
					approved_assets,
				)
			)
		return {"context": context, "plans": plans}

	def _warn_idempotency_trace_only(self) -> None:
		if not self.payload["dry_run"]:
			self.warnings.append(
				{
					"code": "idempotency_trace_only",
					"detail": "This Step 4B implementation requires idempotency_key for traceability and uses duplicate detection, but it does not persist idempotency receipts.",
				}
			)

	def _validate_human_approval(self) -> None:
		if self.payload["dry_run"]:
			return
		for index, decision in enumerate(self.payload["applied_control_decisions"]):
			if decision["action"] in {"create", "reuse"} and not decision["human_approved"]:
				self.blocking_errors.append(
					{
						"code": "human_approval_required",
						"detail": "create and reuse decisions must be human approved for write mode.",
						"field": f"applied_control_decisions[{index}].human_approved",
					}
				)

	def _resolve_context(self, reference: dict[str, Any]) -> dict[str, Any]:
		folder = Folder.objects.filter(id=reference["folder_id"]).first()
		if folder is None:
			self.blocking_errors.append(
				{
					"code": "folder_not_found",
					"detail": "folder_id does not match an existing Folder.",
					"field": "case_setup_reference.folder_id",
				}
			)
		elif not RoleAssignment.is_object_readable(self.user, Folder, folder.id):
			self.blocking_errors.append(
				{
					"code": "permission_denied",
					"detail": "You do not have permission to use the selected Folder.",
					"field": "case_setup_reference.folder_id",
				}
			)
			folder = None

		perimeter = self._resolve_context_object(
			Perimeter,
			reference.get("perimeter_id"),
			"case_setup_reference.perimeter_id",
			"Perimeter",
		)
		compliance_assessment = self._resolve_context_object(
			ComplianceAssessment,
			reference.get("compliance_assessment_id"),
			"case_setup_reference.compliance_assessment_id",
			"ComplianceAssessment",
		)
		risk_assessment = self._resolve_context_object(
			RiskAssessment,
			reference.get("risk_assessment_id"),
			"case_setup_reference.risk_assessment_id",
			"RiskAssessment",
		)
		framework = self._resolve_context_object(
			Framework,
			reference.get("selected_framework_id"),
			"case_setup_reference.selected_framework_id",
			"Framework",
		)

		if folder is not None and perimeter is not None and perimeter.folder_id != folder.id:
			self.blocking_errors.append(
				{
					"code": "invalid_context_reference",
					"detail": "perimeter_id must belong to the selected folder_id.",
					"field": "case_setup_reference.perimeter_id",
				}
			)

		if folder is not None and compliance_assessment is not None:
			if compliance_assessment.folder_id != folder.id:
				self.blocking_errors.append(
					{
						"code": "invalid_context_reference",
						"detail": "compliance_assessment_id must belong to the selected folder_id.",
						"field": "case_setup_reference.compliance_assessment_id",
					}
				)
			if perimeter is not None and compliance_assessment.perimeter_id != perimeter.id:
				self.blocking_errors.append(
					{
						"code": "invalid_context_reference",
						"detail": "compliance_assessment_id must belong to the selected perimeter_id.",
						"field": "case_setup_reference.compliance_assessment_id",
					}
				)

		if folder is not None and risk_assessment is not None:
			if risk_assessment.folder_id != folder.id:
				self.blocking_errors.append(
					{
						"code": "invalid_context_reference",
						"detail": "risk_assessment_id must belong to the selected folder_id.",
						"field": "case_setup_reference.risk_assessment_id",
					}
				)
			if perimeter is not None and risk_assessment.perimeter_id != perimeter.id:
				self.blocking_errors.append(
					{
						"code": "invalid_context_reference",
						"detail": "risk_assessment_id must belong to the selected perimeter_id.",
						"field": "case_setup_reference.risk_assessment_id",
					}
				)

		if framework is not None and compliance_assessment is not None and compliance_assessment.framework_id != framework.id:
			self.blocking_errors.append(
				{
					"code": "invalid_context_reference",
					"detail": "selected_framework_id must match the ComplianceAssessment framework when both are provided.",
					"field": "case_setup_reference.selected_framework_id",
				}
			)

		return {
			"folder": folder,
			"perimeter": perimeter,
			"compliance_assessment": compliance_assessment,
			"risk_assessment": risk_assessment,
			"framework": framework,
		}

	def _resolve_context_object(self, model, object_id, field: str, label: str):
		if object_id is None:
			return None
		instance = model.objects.filter(id=object_id).first()
		if instance is None:
			self.blocking_errors.append(
				{
					"code": f"{label.lower()}_not_found",
					"detail": f"{field.split('.')[-1]} does not match an existing {label}.",
					"field": field,
				}
			)
			return None
		if not RoleAssignment.is_object_readable(self.user, model, instance.id):
			self.blocking_errors.append(
				{
					"code": "permission_denied",
					"detail": f"You do not have permission to use the selected {label}.",
					"field": field,
				}
			)
			return None
		return instance

	def _resolve_asset_references(self, asset_references: list[dict[str, Any]], folder: Folder | None) -> dict[str, Asset]:
		resolved_assets: dict[str, Asset] = {}
		for index, reference in enumerate(asset_references):
			field_name = f"asset_references[{index}].asset_id"
			asset = Asset.objects.filter(id=reference["asset_id"]).select_related("folder").first()
			if asset is None:
				self.blocking_errors.append(
					{
						"code": "asset_not_found",
						"detail": "asset_id does not match an existing Asset.",
						"field": field_name,
					}
				)
				continue

			if not RoleAssignment.is_object_readable(self.user, Asset, asset.id):
				self.blocking_errors.append(
					{
						"code": "permission_denied",
						"detail": "You do not have permission to use the selected Asset reference.",
						"field": field_name,
					}
				)
				continue

			if folder is not None and asset.folder_id != folder.id:
				self.blocking_errors.append(
					{
						"code": "invalid_context_reference",
						"detail": "asset_id must belong to case_setup_reference.folder_id.",
						"field": field_name,
					}
				)
				continue

			resolved_assets[str(asset.id)] = asset

		return resolved_assets

	def _resolve_applied_control_decision(
		self,
		index: int,
		decision: dict[str, Any],
		context: dict[str, Any],
		folder_controls: list[AppliedControl],
		approved_assets: dict[str, Asset],
	) -> dict[str, Any]:
		field_prefix = f"applied_control_decisions[{index}]"
		action = decision["action"]
		temporary_id = decision["temporary_id"]
		original_summary = decision["original_suggestion_summary"]
		target_name = self._target_name(decision)

		if not decision.get("selected", False):
			self.blocking_errors.append(
				{
					"code": "candidate_not_selected",
					"detail": "Submitted Step 4B decisions must have selected=true.",
					"field": f"{field_prefix}.selected",
				}
			)
			self.planned_actions.append(
				PlannedAppliedControlAction(
					temporary_id,
					action,
					"blocked",
					"Candidate was not selected for Step 4B.",
					target_name,
				)
			)
			return {"action": action, "source_temporary_id": temporary_id}

		if action == "reject":
			self.rejected_applied_controls.append(
				{
					"source_temporary_id": temporary_id,
					"action": "reject",
					"name": original_summary.get("proposed_name"),
				}
			)
			self.planned_actions.append(
				PlannedAppliedControlAction(
					temporary_id,
					"reject",
					"ok",
					"Candidate applied control rejected by reviewer.",
					target_name,
				)
			)
			return {"action": action, "source_temporary_id": temporary_id}

		if action == "defer":
			self.deferred_applied_controls.append(
				{
					"source_temporary_id": temporary_id,
					"action": "defer",
					"name": original_summary.get("proposed_name"),
				}
			)
			self.planned_actions.append(
				PlannedAppliedControlAction(
					temporary_id,
					"defer",
					"ok",
					"Candidate applied control deferred by reviewer.",
					target_name,
				)
			)
			return {"action": action, "source_temporary_id": temporary_id}

		if context.get("folder") is None:
			self.blocking_errors.append(
				{
					"code": "missing_context_folder",
					"detail": "A valid folder_id is required before Step 4B can create or reuse applied controls.",
					"field": "case_setup_reference.folder_id",
				}
			)
			self.planned_actions.append(
				PlannedAppliedControlAction(
					temporary_id,
					action,
					"blocked",
					"Folder context is unavailable.",
					target_name,
				)
			)
			return {"action": action, "source_temporary_id": temporary_id}

		if action == "reuse":
			return self._resolve_reuse_decision(
				field_prefix,
				decision,
				context["folder"],
				approved_assets,
				target_name,
			)

		return self._resolve_create_decision(
			field_prefix,
			decision,
			context["folder"],
			folder_controls,
			approved_assets,
			target_name,
		)

	def _resolve_reuse_decision(
		self,
		field_prefix: str,
		decision: dict[str, Any],
		folder: Folder,
		approved_assets: dict[str, Asset],
		target_name: str | None,
	) -> dict[str, Any]:
		temporary_id = decision["temporary_id"]
		if not self.payload["dry_run"] and self._requires_ambiguity_resolution(decision) and not decision.get("ambiguity_resolution"):
			self.blocking_errors.append(
				{
					"code": "ambiguity_resolution_required",
					"detail": "Ambiguous applied-control candidates require ambiguity_resolution before reuse in write mode.",
					"field": f"{field_prefix}.ambiguity_resolution",
				}
			)

		self._resolve_linked_assets(field_prefix, decision, approved_assets)

		applied_control = (
			AppliedControl.objects.filter(id=decision["selected_existing_applied_control_id"])
			.select_related("folder")
			.prefetch_related("assets")
			.first()
		)
		if applied_control is None:
			self.blocking_errors.append(
				{
					"code": "applied_control_not_found",
					"detail": "selected_existing_applied_control_id does not match an existing AppliedControl.",
					"field": f"{field_prefix}.selected_existing_applied_control_id",
				}
			)
			self.planned_actions.append(
				PlannedAppliedControlAction(
					temporary_id,
					"reuse",
					"blocked",
					"Selected AppliedControl was not found.",
					target_name,
				)
			)
			return {
				"action": "reuse",
				"source_temporary_id": temporary_id,
				"existing_applied_control": None,
			}

		if not RoleAssignment.is_object_readable(self.user, AppliedControl, applied_control.id):
			self.blocking_errors.append(
				{
					"code": "permission_denied",
					"detail": "You do not have permission to reuse the selected AppliedControl.",
					"field": f"{field_prefix}.selected_existing_applied_control_id",
				}
			)
		elif applied_control.folder_id != folder.id:
			self.blocking_errors.append(
				{
					"code": "reuse_out_of_scope",
					"detail": "selected_existing_applied_control_id must belong to the selected folder_id in Step 4B v1.",
					"field": f"{field_prefix}.selected_existing_applied_control_id",
				}
			)

		self.reused_applied_controls.append(
			self._applied_control_summary(
				applied_control,
				action="reuse",
				source_temporary_id=temporary_id,
			)
		)
		self.planned_actions.append(
			PlannedAppliedControlAction(
				temporary_id,
				"reuse",
				"planned",
				"Existing AppliedControl will be reused without mutation.",
				applied_control.name,
			)
		)
		return {
			"action": "reuse",
			"source_temporary_id": temporary_id,
			"existing_applied_control": applied_control,
		}

	def _resolve_create_decision(
		self,
		field_prefix: str,
		decision: dict[str, Any],
		folder: Folder,
		folder_controls: list[AppliedControl],
		approved_assets: dict[str, Asset],
		target_name: str | None,
	) -> dict[str, Any]:
		temporary_id = decision["temporary_id"]
		if not self.payload["dry_run"] and self._requires_ambiguity_resolution(decision) and not decision.get("ambiguity_resolution"):
			self.blocking_errors.append(
				{
					"code": "ambiguity_resolution_required",
					"detail": "Ambiguous applied-control candidates require ambiguity_resolution before create in write mode.",
					"field": f"{field_prefix}.ambiguity_resolution",
				}
			)

		resolved_linked_assets = self._resolve_linked_assets(field_prefix, decision, approved_assets)
		candidate_for_matching = self._candidate_for_matching(decision, resolved_linked_assets)
		matches = _find_candidate_matches(candidate_for_matching, folder_controls)
		if matches:
			self.warnings.append(
				{
					"code": "duplicate_candidate_detected",
					"field": field_prefix,
					"detail": f"Folder-scoped duplicate applied-control candidates were found for {target_name or decision['original_suggestion_summary'].get('proposed_name') }.",
					"matches": matches,
				}
			)
			if not self.payload["dry_run"]:
				if not decision.get("duplicate_resolution"):
					self.blocking_errors.append(
						{
							"code": "duplicate_resolution_required",
							"detail": "Duplicate candidates require duplicate_resolution before create in write mode.",
							"field": f"{field_prefix}.duplicate_resolution",
						}
					)
				self.blocking_errors.append(
					{
						"code": "duplicate_conflict",
						"detail": "Step 4B v1 does not allow create-anyway when a folder-scoped duplicate match exists. Choose reuse, rename, reject, or defer.",
						"field": f"{field_prefix}.approved_fields.name",
						"matches": matches,
					}
				)

		self._check_add_permission(folder, "add_appliedcontrol", f"{field_prefix}.approved_fields")
		create_payload = self._build_applied_control_create_payload(
			decision["approved_fields"],
			folder,
			resolved_linked_assets,
		)
		serializer = AppliedControlWriteSerializer(data=create_payload, context={"request": self.request})
		if not serializer.is_valid():
			self.blocking_errors.append(
				{
					"code": "invalid_applied_control_payload",
					"detail": "Approved applied-control fields did not pass platform AppliedControl validation.",
					"field": f"{field_prefix}.approved_fields",
					"errors": serializer.errors,
				}
			)
			self.planned_actions.append(
				PlannedAppliedControlAction(
					temporary_id,
					"create",
					"blocked",
					"Approved applied-control fields failed validation.",
					target_name,
				)
			)
			return {
				"action": "create",
				"source_temporary_id": temporary_id,
				"create_payload": create_payload,
			}

		self.planned_actions.append(
			PlannedAppliedControlAction(
				temporary_id,
				"create",
				"planned",
				"AppliedControl create is valid and ready for execution.",
				create_payload.get("name"),
			)
		)
		return {
			"action": "create",
			"source_temporary_id": temporary_id,
			"create_payload": create_payload,
		}

	def _visible_folder_controls(self, folder: Folder) -> list[AppliedControl]:
		accessible_ids = self._visible_applied_control_ids()
		queryset = AppliedControl.objects.filter(folder=folder).select_related("folder").prefetch_related("assets")
		if accessible_ids is not None:
			queryset = queryset.filter(id__in=accessible_ids)
		return list(queryset)

	def _visible_applied_control_ids(self):
		try:
			return RoleAssignment.get_accessible_object_ids(
				folder=Folder.get_root_folder(),
				user=self.user,
				object_type=AppliedControl,
			)[0]
		except Exception:
			return None

	def _check_add_permission(self, folder: Folder, codename: str, field: str) -> None:
		permission = Permission.objects.get(codename=codename)
		if not RoleAssignment.is_access_allowed(self.user, permission, folder):
			self.blocking_errors.append(
				{
					"code": "permission_denied",
					"detail": f"You do not have permission to {codename} in the selected scope.",
					"field": field,
				}
			)

	def _resolve_linked_assets(
		self,
		field_prefix: str,
		decision: dict[str, Any],
		approved_assets: dict[str, Asset],
	) -> list[Asset]:
		linked_asset_ids = self._decision_linked_asset_ids(decision)
		field_name = self._linked_assets_field_name(decision, field_prefix)
		if not linked_asset_ids:
			self.blocking_errors.append(
				{
					"code": "linked_asset_required",
					"detail": "At least one linked asset id is required for Step 4B decisions.",
					"field": field_name,
				}
			)
			return []

		resolved_assets: list[Asset] = []
		seen_ids: set[str] = set()
		for asset_id in linked_asset_ids:
			if asset_id in seen_ids:
				continue
			seen_ids.add(asset_id)
			asset = approved_assets.get(asset_id)
			if asset is None:
				self.blocking_errors.append(
					{
						"code": "invalid_linked_asset",
						"detail": "linked_asset_ids must reference approved Step 3B assets in the selected folder.",
						"field": field_name,
					}
				)
				continue
			resolved_assets.append(asset)

		return resolved_assets

	def _linked_assets_field_name(self, decision: dict[str, Any], field_prefix: str) -> str:
		if decision.get("approved_fields") and "linked_asset_ids" in decision["approved_fields"]:
			return f"{field_prefix}.approved_fields.linked_asset_ids"
		return f"{field_prefix}.original_suggestion_summary.linked_asset_ids"

	def _decision_linked_asset_ids(self, decision: dict[str, Any]) -> list[str]:
		approved_fields = decision.get("approved_fields") or {}
		if approved_fields.get("linked_asset_ids"):
			return [str(asset_id) for asset_id in approved_fields.get("linked_asset_ids") or []]
		summary = decision.get("original_suggestion_summary") or {}
		return [str(asset_id) for asset_id in summary.get("linked_asset_ids") or []]

	def _build_applied_control_create_payload(
		self,
		approved_fields: dict[str, Any],
		folder: Folder,
		linked_assets: list[Asset],
	) -> dict[str, Any]:
		payload: dict[str, Any] = {
			"folder": str(folder.id),
			"assets": [str(asset.id) for asset in linked_assets],
		}
		for field in ("name", "description", "ref_id", "category", "status"):
			value = approved_fields.get(field)
			if value is not None:
				payload[field] = value
		return payload

	def _candidate_for_matching(self, decision: dict[str, Any], linked_assets: list[Asset]) -> dict[str, Any]:
		approved_fields = decision.get("approved_fields") or {}
		summary = decision.get("original_suggestion_summary") or {}
		return {
			"proposed_name": approved_fields.get("name") or summary.get("proposed_name") or "",
			"proposed_reference_id": approved_fields.get("ref_id") or summary.get("proposed_reference_id") or "",
			"linked_asset_ids": [str(asset.id) for asset in linked_assets],
		}

	def _requires_ambiguity_resolution(self, decision: dict[str, Any]) -> bool:
		summary = decision.get("original_suggestion_summary") or {}
		return bool(summary.get("ambiguity_flags"))

	def _target_name(self, decision: dict[str, Any]) -> str | None:
		approved_fields = decision.get("approved_fields") or {}
		if approved_fields.get("name"):
			return approved_fields["name"]
		summary = decision.get("original_suggestion_summary") or {}
		return summary.get("proposed_name")

	def _create_applied_control_from_plan(self, plan: dict[str, Any]) -> AppliedControl:
		serializer = AppliedControlWriteSerializer(data=plan["create_payload"], context={"request": self.request})
		serializer.is_valid(raise_exception=True)
		return serializer.save()

	def _execute_write_plan(self, resolved: dict[str, Any]) -> None:
		for plan in resolved["plans"]:
			if plan["action"] != "create":
				continue
			applied_control = self._create_applied_control_from_plan(plan)
			self.created_applied_controls.append(
				self._applied_control_summary(
					applied_control,
					action="create",
					source_temporary_id=plan["source_temporary_id"],
				)
			)

	def _mark_transaction_rolled_back(self, resolved: dict[str, Any]) -> None:
		self.created_applied_controls = []
		self.reused_applied_controls = []
		for plan in resolved.get("plans", []):
			if plan.get("action") in {"create", "reuse"}:
				self.skipped_applied_controls.append(
					{
						"source_temporary_id": plan.get("source_temporary_id"),
						"action": plan.get("action"),
						"skip_reason": "transaction_rolled_back",
					}
				)

	def _applied_control_summary(
		self,
		applied_control: AppliedControl,
		*,
		action: str,
		source_temporary_id: str,
	) -> dict[str, Any]:
		return {
			"applied_control_id": str(applied_control.id),
			"name": applied_control.name,
			"ref_id": applied_control.ref_id or None,
			"folder_id": str(applied_control.folder_id),
			"action": action,
			"source_temporary_id": source_temporary_id,
			"category": applied_control.category,
			"status": applied_control.status,
			"linked_asset_ids": [str(asset_id) for asset_id in applied_control.assets.values_list("id", flat=True)],
		}

	def _dry_run_status(self) -> str:
		if self.blocking_errors:
			return "blocked"
		if self.warnings:
			return "passed_with_warnings"
		return "validated"

	def _write_status(self) -> str:
		if self.created_applied_controls and self.reused_applied_controls:
			return "created_and_reused"
		if self.created_applied_controls:
			return "created"
		if self.reused_applied_controls:
			return "reused_only"
		return "completed"

	def _blocking_status_code(self) -> int:
		if any(item.get("code") == "permission_denied" for item in self.blocking_errors):
			return 403
		if any("duplicate" in str(item.get("code")) for item in self.blocking_errors):
			return 409
		return 422

	def _build_response(
		self,
		*,
		operation_type: str,
		status: str,
		needs_human_review: bool,
		extra_blocking_errors: list[dict[str, Any]] | None = None,
	) -> dict[str, Any]:
		blocking_errors = [*self.blocking_errors]
		if extra_blocking_errors:
			blocking_errors.extend(extra_blocking_errors)

		return {
			"operation_type": operation_type,
			"status": status,
			"dry_run": self.payload["dry_run"],
			"no_write": self.payload["dry_run"],
			"source_step1_draft_hash": self.payload["source_step1_draft_hash"],
			"source_asset_commit_hash": self.payload["source_asset_commit_hash"],
			"source_applied_control_draft_hash": self.payload["source_applied_control_draft_hash"],
			"idempotency_key": self.payload.get("idempotency_key"),
			"created_applied_controls": [] if operation_type == "dry_run" else self.created_applied_controls,
			"reused_applied_controls": self.reused_applied_controls,
			"rejected_applied_controls": self.rejected_applied_controls,
			"deferred_applied_controls": self.deferred_applied_controls,
			"skipped_applied_controls": self.skipped_applied_controls,
			"planned_actions": [item.as_dict() for item in self.planned_actions],
			"warnings": self.warnings,
			"blocking_errors": blocking_errors,
			"needs_human_review": needs_human_review,
			"next_allowed_steps": self._next_allowed_steps(operation_type, blocking_errors),
		}

	def _next_allowed_steps(self, operation_type: str, blocking_errors: list[dict[str, Any]]) -> list[str]:
		if operation_type == "dry_run":
			if blocking_errors:
				return [
					"Resolve the blocking errors and rerun Step 4B dry-run.",
				]
			return [
				"If the reviewed payload is final, submit the same request with dry_run=false and approved_by_user=true.",
			]
		if blocking_errors:
			return [
				"Review the blocking errors, rerun dry-run, and resubmit only after the issue is resolved.",
			]
		return [
			"Step 4B applied-control commit is complete.",
			"Future vulnerability steps remain out of scope for this endpoint.",
		]


def execute_applied_control_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
	service = AiAppliedControlCommitService(request=request, payload=payload)
	return service.execute()