from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction
from rest_framework import serializers

from core.models import Actor, Asset, ComplianceAssessment, Framework, Perimeter, RiskAssessment
from core.serializers import AssetWriteSerializer
from iam.models import Folder, RoleAssignment

from .asset_commit_guardrails import AssetCommitValidationError, validate_asset_commit_guardrails


@dataclass
class PlannedAction:
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


class AiAssetCommitService:
    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedAction] = []
        self.created_assets: list[dict[str, Any]] = []
        self.reused_assets: list[dict[str, Any]] = []
        self.rejected_assets: list[dict[str, Any]] = []
        self.deferred_assets: list[dict[str, Any]] = []
        self.skipped_assets: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    def execute(self) -> dict[str, Any]:
        validate_asset_commit_guardrails(self.payload)

        resolved = self._plan_and_validate()
        if self.payload["dry_run"]:
            return self._build_response(
                operation_type="dry_run",
                status=self._dry_run_status(),
                needs_human_review=bool(self.blocking_errors),
            )

        if self.blocking_errors:
            raise AssetCommitValidationError(
                "ai_asset_commit_blocked",
                "The approved Step 3B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(
                    operation_type="create",
                    status="blocked",
                    needs_human_review=True,
                ),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(resolved)
        except AssetCommitValidationError:
            raise
        except Exception as exc:
            self._mark_transaction_rolled_back(resolved)
            raise AssetCommitValidationError(
                "transaction_aborted",
                "Step 3B transaction failed and all writes were rolled back.",
                status_code=422,
                blocking_errors=[
                    {
                        "code": "transaction_aborted",
                        "detail": str(exc),
                        "field": None,
                    }
                ],
                response_payload=self._build_response(
                    operation_type="create",
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
            operation_type="create",
            status=self._write_status(),
            needs_human_review=False,
        )

    def _plan_and_validate(self) -> dict[str, Any]:
        context = self._resolve_context(self.payload["case_setup_reference"])
        folder_assets = self._visible_folder_assets(context["folder"])
        plans = []
        self._validate_human_approval()
        self._warn_idempotency_trace_only()
        for index, decision in enumerate(self.payload["asset_decisions"]):
            plans.append(self._resolve_asset_decision(index, decision, context, folder_assets))
        return {"context": context, "plans": plans}

    def _warn_idempotency_trace_only(self) -> None:
        if not self.payload["dry_run"]:
            self.warnings.append(
                {
                    "code": "idempotency_trace_only",
                    "detail": "This Step 3B implementation requires idempotency_key for traceability and uses duplicate detection, but it does not persist idempotency receipts.",
                }
            )

    def _validate_human_approval(self) -> None:
        if self.payload["dry_run"]:
            return
        for index, decision in enumerate(self.payload["asset_decisions"]):
            if decision["action"] in {"create", "reuse"} and not decision["human_approved"]:
                self.blocking_errors.append(
                    {
                        "code": "human_approval_required",
                        "detail": "create and reuse decisions must be human approved for write mode.",
                        "field": f"asset_decisions[{index}].human_approved",
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

    def _resolve_asset_decision(
        self,
        index: int,
        decision: dict[str, Any],
        context: dict[str, Any],
        folder_assets: list[Asset],
    ) -> dict[str, Any]:
        field_prefix = f"asset_decisions[{index}]"
        action = decision["action"]
        temporary_id = decision["temporary_id"]
        original_summary = decision["original_suggestion_summary"]
        target_name = self._target_name(decision)

        if action == "reject":
            self.rejected_assets.append(
                {
                    "source_temporary_id": temporary_id,
                    "action": "reject",
                    "name": original_summary.get("proposed_name"),
                }
            )
            self.planned_actions.append(
                PlannedAction(temporary_id, "reject", "ok", "Candidate asset rejected by reviewer.", target_name)
            )
            return {"action": action, "source_temporary_id": temporary_id}

        if action == "defer":
            self.deferred_assets.append(
                {
                    "source_temporary_id": temporary_id,
                    "action": "defer",
                    "name": original_summary.get("proposed_name"),
                }
            )
            self.planned_actions.append(
                PlannedAction(temporary_id, "defer", "ok", "Candidate asset deferred by reviewer.", target_name)
            )
            return {"action": action, "source_temporary_id": temporary_id}

        if context.get("folder") is None:
            self.blocking_errors.append(
                {
                    "code": "missing_context_folder",
                    "detail": "A valid folder_id is required before Step 3B can create or reuse assets.",
                    "field": "case_setup_reference.folder_id",
                }
            )
            self.planned_actions.append(
                PlannedAction(temporary_id, action, "blocked", "Folder context is unavailable.", target_name)
            )
            return {"action": action, "source_temporary_id": temporary_id}

        if action == "reuse":
            return self._resolve_reuse_decision(field_prefix, decision, context["folder"], target_name)

        return self._resolve_create_decision(
            field_prefix,
            decision,
            context["folder"],
            folder_assets,
            target_name,
        )

    def _resolve_reuse_decision(self, field_prefix: str, decision: dict[str, Any], folder: Folder, target_name: str | None) -> dict[str, Any]:
        temporary_id = decision["temporary_id"]
        if not self.payload["dry_run"] and self._requires_ambiguity_resolution(decision) and not decision.get("ambiguity_resolution"):
            self.blocking_errors.append(
                {
                    "code": "ambiguity_resolution_required",
                    "detail": "Ambiguous asset candidates require ambiguity_resolution before reuse in write mode.",
                    "field": f"{field_prefix}.ambiguity_resolution",
                }
            )

        asset = Asset.objects.filter(id=decision["selected_existing_asset_id"]).select_related("folder").first()
        if asset is None:
            self.blocking_errors.append(
                {
                    "code": "asset_not_found",
                    "detail": "selected_existing_asset_id does not match an existing Asset.",
                    "field": f"{field_prefix}.selected_existing_asset_id",
                }
            )
            self.planned_actions.append(
                PlannedAction(temporary_id, "reuse", "blocked", "Selected Asset was not found.", target_name)
            )
            return {"action": "reuse", "source_temporary_id": temporary_id, "existing_asset": None}

        if not RoleAssignment.is_object_readable(self.user, Asset, asset.id):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to reuse the selected Asset.",
                    "field": f"{field_prefix}.selected_existing_asset_id",
                }
            )
        elif asset.folder_id != folder.id:
            self.blocking_errors.append(
                {
                    "code": "reuse_out_of_scope",
                    "detail": "selected_existing_asset_id must belong to the selected folder_id in Step 3B v1.",
                    "field": f"{field_prefix}.selected_existing_asset_id",
                }
            )

        self.reused_assets.append(self._asset_summary(asset, action="reuse", source_temporary_id=temporary_id))
        self.planned_actions.append(
            PlannedAction(temporary_id, "reuse", "planned", "Existing Asset will be reused without mutation.", asset.name)
        )
        return {"action": "reuse", "source_temporary_id": temporary_id, "existing_asset": asset}

    def _resolve_create_decision(
        self,
        field_prefix: str,
        decision: dict[str, Any],
        folder: Folder,
        folder_assets: list[Asset],
        target_name: str | None,
    ) -> dict[str, Any]:
        temporary_id = decision["temporary_id"]
        if not self.payload["dry_run"] and self._requires_ambiguity_resolution(decision) and not decision.get("ambiguity_resolution"):
            self.blocking_errors.append(
                {
                    "code": "ambiguity_resolution_required",
                    "detail": "Ambiguous asset candidates require ambiguity_resolution before create in write mode.",
                    "field": f"{field_prefix}.ambiguity_resolution",
                }
            )

        matches = self._find_candidate_matches(decision, folder_assets)
        if matches:
            self.warnings.append(
                {
                    "code": "duplicate_candidate_detected",
                    "field": field_prefix,
                    "detail": f"Folder-scoped duplicate candidates were found for {target_name or decision['original_suggestion_summary'].get('proposed_name')}.",
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
                        "detail": "Step 3B v1 does not allow create-anyway when a folder-scoped duplicate match exists. Choose reuse, rename, reject, or defer.",
                        "field": f"{field_prefix}.approved_fields.name",
                        "matches": matches,
                    }
                )

        self._check_add_permission(folder, "add_asset", f"{field_prefix}.approved_fields")
        create_payload = self._build_asset_create_payload(decision["approved_fields"], folder)
        serializer = AssetWriteSerializer(data=create_payload, context={"request": self.request})
        if not serializer.is_valid():
            self.blocking_errors.append(
                {
                    "code": "invalid_asset_payload",
                    "detail": "Approved asset fields did not pass platform Asset validation.",
                    "field": f"{field_prefix}.approved_fields",
                    "errors": serializer.errors,
                }
            )
            self.planned_actions.append(
                PlannedAction(temporary_id, "create", "blocked", "Approved asset fields failed validation.", target_name)
            )
            return {"action": "create", "source_temporary_id": temporary_id, "create_payload": create_payload}

        self.planned_actions.append(
            PlannedAction(temporary_id, "create", "planned", "Asset create is valid and ready for execution.", create_payload.get("name"))
        )
        return {"action": "create", "source_temporary_id": temporary_id, "create_payload": create_payload}

    def _visible_folder_assets(self, folder: Folder) -> list[Asset]:
        accessible_ids = self._visible_asset_ids()
        queryset = Asset.objects.filter(folder=folder).select_related("folder")
        if accessible_ids is not None:
            queryset = queryset.filter(id__in=accessible_ids)
        return list(queryset)

    def _visible_asset_ids(self):
        try:
            return RoleAssignment.get_accessible_object_ids(
                folder=Folder.get_root_folder(),
                user=self.user,
                object_type=Asset,
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

    def _build_asset_create_payload(self, approved_fields: dict[str, Any], folder: Folder) -> dict[str, Any]:
        payload: dict[str, Any] = {"folder": str(folder.id)}
        for field in (
            "name",
            "description",
            "type",
            "ref_id",
            "reference_link",
            "observation",
        ):
            value = approved_fields.get(field)
            if value is not None:
                payload[field] = value

        asset_class = approved_fields.get("asset_class")
        if asset_class is not None:
            payload["asset_class"] = str(asset_class)

        owner = approved_fields.get("owner")
        if owner:
            payload["owner"] = [str(item) for item in owner]

        return payload

    def _find_candidate_matches(self, decision: dict[str, Any], folder_assets: list[Asset]) -> list[dict[str, Any]]:
        approved_fields = decision.get("approved_fields") or {}
        summary = decision.get("original_suggestion_summary") or {}
        proposed_name = str(approved_fields.get("name") or summary.get("proposed_name") or "").strip()
        proposed_ref = str(approved_fields.get("ref_id") or summary.get("proposed_reference_id") or "").strip()
        normalized_name = self._normalize_token(proposed_name)

        matches: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for asset in folder_assets:
            match_type = None
            match_score = 0.0
            if proposed_name and asset.name == proposed_name:
                match_type = "exact_name_same_folder"
                match_score = 0.99
            elif proposed_name and self._normalize_token(asset.name) == normalized_name:
                match_type = "normalized_name_same_folder"
                match_score = 0.9
            elif proposed_ref and asset.ref_id and asset.ref_id.strip().lower() == proposed_ref.lower():
                match_type = "reference_id_same_folder"
                match_score = 0.97

            if match_type and str(asset.id) not in seen_ids:
                seen_ids.add(str(asset.id))
                matches.append(
                    {
                        "existing_asset_id": str(asset.id),
                        "existing_name": asset.name,
                        "existing_ref_id": asset.ref_id or None,
                        "existing_type": asset.get_type_display(),
                        "folder_id": str(asset.folder_id),
                        "folder_name": asset.folder.name,
                        "match_type": match_type,
                        "match_score": match_score,
                        "scope_relevance": "high",
                        "warning": "Potential duplicate within the selected folder.",
                    }
                )
        return matches

    def _normalize_token(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())

    def _requires_ambiguity_resolution(self, decision: dict[str, Any]) -> bool:
        summary = decision.get("original_suggestion_summary") or {}
        return bool(summary.get("ambiguity_flags"))

    def _target_name(self, decision: dict[str, Any]) -> str | None:
        approved_fields = decision.get("approved_fields") or {}
        if approved_fields.get("name"):
            return approved_fields["name"]
        summary = decision.get("original_suggestion_summary") or {}
        return summary.get("proposed_name")

    def _create_asset_from_plan(self, plan: dict[str, Any]) -> Asset:
        serializer = AssetWriteSerializer(data=plan["create_payload"], context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def _execute_write_plan(self, resolved: dict[str, Any]) -> None:
        for plan in resolved["plans"]:
            if plan["action"] != "create":
                continue
            asset = self._create_asset_from_plan(plan)
            self.created_assets.append(
                self._asset_summary(asset, action="create", source_temporary_id=plan["source_temporary_id"])
            )

    def _mark_transaction_rolled_back(self, resolved: dict[str, Any]) -> None:
        self.created_assets = []
        self.reused_assets = []
        for plan in resolved.get("plans", []):
            if plan.get("action") in {"create", "reuse"}:
                self.skipped_assets.append(
                    {
                        "source_temporary_id": plan.get("source_temporary_id"),
                        "action": plan.get("action"),
                        "skip_reason": "transaction_rolled_back",
                    }
                )

    def _asset_summary(self, asset: Asset, *, action: str, source_temporary_id: str) -> dict[str, Any]:
        return {
            "asset_id": str(asset.id),
            "name": asset.name,
            "ref_id": asset.ref_id or None,
            "reference_id": asset.ref_id or None,
            "folder_id": str(asset.folder_id),
            "action": action,
            "source_temporary_id": source_temporary_id,
            "type": asset.type,
        }

    def _dry_run_status(self) -> str:
        if self.blocking_errors:
            return "blocked"
        if self.warnings:
            return "passed_with_warnings"
        return "validated"

    def _write_status(self) -> str:
        if self.created_assets and self.reused_assets:
            return "created_and_reused"
        if self.created_assets:
            return "created"
        if self.reused_assets:
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
            "source_step1_draft_hash": self.payload["source_step1_draft_hash"],
            "source_asset_draft_hash": self.payload["source_asset_draft_hash"],
            "idempotency_key": self.payload.get("idempotency_key"),
            "created_assets": [] if operation_type == "dry_run" else self.created_assets,
            "reused_assets": self.reused_assets,
            "rejected_assets": self.rejected_assets,
            "deferred_assets": self.deferred_assets,
            "skipped_assets": self.skipped_assets,
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
                    "Resolve the blocking errors and rerun Step 3B dry-run.",
                ]
            return [
                "If the reviewed payload is final, submit the same request with dry_run=false and approved_by_user=true.",
            ]
        if blocking_errors:
            return [
                "Review the blocking errors, rerun dry-run, and resubmit only after the issue is resolved.",
            ]
        return [
            "Step 3B asset commit is complete.",
            "Future control and vulnerability steps remain out of scope for this endpoint.",
        ]


def execute_asset_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiAssetCommitService(request=request, payload=payload)
    return service.execute()