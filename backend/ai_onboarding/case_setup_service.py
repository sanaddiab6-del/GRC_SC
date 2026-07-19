from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction
from rest_framework import serializers

from core.models import ComplianceAssessment, Framework, Perimeter, RiskAssessment, RiskMatrix, StoredLibrary
from core.serializers import (
    ComplianceAssessmentWriteSerializer,
    FolderWriteSerializer,
    PerimeterWriteSerializer,
    RiskAssessmentWriteSerializer,
)
from iam.models import Folder, RoleAssignment

from .case_setup_guardrails import CaseSetupValidationError, validate_case_setup_guardrails


@dataclass
class PlannedAction:
    object_key: str
    platform_entity: str
    action: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {
            "object_key": self.object_key,
            "platform_entity": self.platform_entity,
            "action": self.action,
            "status": self.status,
            "detail": self.detail,
        }


class AiCaseSetupService:
    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedAction] = []
        self.created_objects: list[dict[str, Any]] = []
        self.reused_objects: list[dict[str, Any]] = []
        self.skipped_objects: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    def execute(self) -> dict[str, Any]:
        validate_case_setup_guardrails(self.payload)

        resolved = self._plan_and_validate()
        if self.payload["dry_run"]:
            return self._build_response(
                operation_type="dry_run",
                status=self._dry_run_status(),
                needs_human_review=True,
            )

        if self.blocking_errors:
            raise CaseSetupValidationError(
                "ai_case_setup_blocked",
                "The approved Step 2 payload is blocked and cannot be executed.",
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
        except CaseSetupValidationError:
            raise
        except Exception as exc:
            raise CaseSetupValidationError(
                "transaction_aborted",
                "Step 2 transaction failed and all writes were rolled back.",
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
        framework = self._resolve_framework(self.payload["framework_resolution"])
        folder_plan = self._resolve_folder_decision(self.payload["folder_domain_decision"])
        perimeter_plan = self._resolve_perimeter_decision(
            self.payload["perimeter_decision"],
            folder_plan,
        )
        compliance_plan = self._resolve_compliance_assessment_decision(
            self.payload["compliance_assessment_decision"],
            folder_plan,
            perimeter_plan,
            framework,
        )
        risk_plan = self._resolve_risk_assessment_decision(
            self.payload["risk_assessment_decision"],
            folder_plan,
            perimeter_plan,
        )
        self._validate_human_approval()
        self._warn_idempotency_trace_only()
        return {
            "framework": framework,
            "folder": folder_plan,
            "perimeter": perimeter_plan,
            "compliance_assessment": compliance_plan,
            "risk_assessment": risk_plan,
        }

    def _warn_idempotency_trace_only(self) -> None:
        if not self.payload["dry_run"]:
            self.warnings.append(
                {
                    "code": "idempotency_trace_only",
                    "detail": "This Step 2 implementation requires idempotency_key for traceability and combines it with duplicate detection, but it does not persist idempotency receipts.",
                }
            )

    def _validate_human_approval(self) -> None:
        if self.payload["dry_run"]:
            return
        for field in (
            "folder_domain_decision",
            "perimeter_decision",
            "compliance_assessment_decision",
            "risk_assessment_decision",
        ):
            decision = self.payload[field]
            if decision["action"] in {"create", "reuse"} and not decision["human_approved"]:
                self.blocking_errors.append(
                    {
                        "code": "human_approval_required",
                        "detail": f"{field} must be human approved for write mode.",
                        "field": field,
                    }
                )

    def _resolve_framework(self, decision: dict[str, Any]) -> Framework | None:
        selected_id = decision.get("selected_framework_id")
        requested_name = (decision.get("requested_framework_name") or "").strip()
        stored_library_urn = (decision.get("selected_stored_library_urn") or "").strip()

        framework = None
        if selected_id:
            framework = Framework.objects.filter(id=selected_id).first()
            if framework is None:
                self.blocking_errors.append(
                    {
                        "code": "framework_not_found",
                        "detail": "selected_framework_id does not match an existing Framework.",
                        "field": "framework_resolution.selected_framework_id",
                    }
                )
            elif not RoleAssignment.is_object_readable(self.user, Framework, framework.id):
                self.blocking_errors.append(
                    {
                        "code": "permission_denied",
                        "detail": "You do not have permission to use the selected Framework.",
                        "field": "framework_resolution.selected_framework_id",
                    }
                )
                framework = None
        elif requested_name:
            exact_matches = list(
                Framework.objects.filter(name__iexact=requested_name).order_by("name", "id")
            )
            if not exact_matches:
                exact_matches = list(
                    Framework.objects.filter(ref_id__iexact=requested_name).order_by("name", "id")
                )
            if len(exact_matches) > 1:
                self.blocking_errors.append(
                    {
                        "code": "multiple_framework_candidates",
                        "detail": "Multiple Framework candidates match the approved framework selection. Choose one explicitly.",
                        "field": "framework_resolution.requested_framework_name",
                        "candidate_ids": [str(item.id) for item in exact_matches],
                    }
                )
            elif len(exact_matches) == 1:
                framework = exact_matches[0]
                if not RoleAssignment.is_object_readable(self.user, Framework, framework.id):
                    self.blocking_errors.append(
                        {
                            "code": "permission_denied",
                            "detail": "You do not have permission to use the resolved Framework.",
                            "field": "framework_resolution.requested_framework_name",
                        }
                    )
                    framework = None
            else:
                if stored_library_urn and StoredLibrary.objects.filter(urn=stored_library_urn).exists():
                    self.blocking_errors.append(
                        {
                            "code": "framework_not_loaded",
                            "detail": "The selected StoredLibrary exists but no loaded Framework is available for Step 2.",
                            "field": "framework_resolution.selected_stored_library_urn",
                        }
                    )
                else:
                    self.blocking_errors.append(
                        {
                            "code": "framework_not_found",
                            "detail": "No matching Framework could be resolved from the approved Step 1 draft.",
                            "field": "framework_resolution.requested_framework_name",
                        }
                    )

        if framework is not None:
            self.reused_objects.append(self._object_summary("Framework", framework))
            self.planned_actions.append(
                PlannedAction(
                    object_key="framework",
                    platform_entity="Framework",
                    action="reuse",
                    status="resolved",
                    detail=f"Framework '{framework.name}' will be reused.",
                )
            )
        return framework

    def _resolve_folder_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        action = decision["action"]
        if action in {"skip", "reject"}:
            self.skipped_objects.append(
                {
                    "platform_entity": "Folder",
                    "action": action,
                    "detail": "Folder setup is required for Step 2 and cannot be skipped or rejected.",
                }
            )
            self.blocking_errors.append(
                {
                    "code": "folder_required",
                    "detail": "Folder / Domain decision must be create or reuse for Step 2.",
                    "field": "folder_domain_decision.action",
                }
            )
            self.planned_actions.append(
                PlannedAction("folder", "Folder", action, "blocked", "Folder setup is required.")
            )
            return {"action": action, "object": None, "parent_folder": None, "create_payload": None}

        if action == "reuse":
            folder = Folder.objects.filter(id=decision["selected_existing_id"]).first()
            if folder is None:
                self.blocking_errors.append(
                    {
                        "code": "folder_not_found",
                        "detail": "selected_existing_id does not match an existing Folder.",
                        "field": "folder_domain_decision.selected_existing_id",
                    }
                )
                self.planned_actions.append(
                    PlannedAction("folder", "Folder", "reuse", "blocked", "Selected folder does not exist.")
                )
                return {"action": action, "object": None, "parent_folder": None, "create_payload": None}
            if folder.content_type != Folder.ContentType.DOMAIN:
                self.blocking_errors.append(
                    {
                        "code": "folder_not_domain",
                        "detail": "Reused Folder must be a domain folder.",
                        "field": "folder_domain_decision.selected_existing_id",
                    }
                )
            if not RoleAssignment.is_object_readable(self.user, Folder, folder.id):
                self.blocking_errors.append(
                    {
                        "code": "permission_denied",
                        "detail": "You do not have permission to reuse the selected Folder.",
                        "field": "folder_domain_decision.selected_existing_id",
                    }
                )
            self.reused_objects.append(self._object_summary("Folder", folder))
            self.planned_actions.append(
                PlannedAction("folder", "Folder", "reuse", "ok", f"Folder '{folder.name}' will be reused.")
            )
            return {"action": action, "object": folder, "parent_folder": folder.parent_folder, "create_payload": None}

        create_payload = decision["proposed_fields"]
        parent_folder = Folder.objects.filter(id=create_payload.get("parent_folder_id")).first()
        if parent_folder is None:
            parent_folder = Folder.get_root_folder()

        self._check_add_permission(parent_folder, "add_folder", "folder_domain_decision.proposed_fields.parent_folder_id")
        duplicate = Folder.objects.filter(
            parent_folder=parent_folder,
            content_type=Folder.ContentType.DOMAIN,
            name__iexact=create_payload["name"],
        ).first()
        if duplicate is not None:
            self.blocking_errors.append(
                {
                    "code": "duplicate_folder",
                    "detail": "A domain Folder with the same name already exists in the selected parent scope.",
                    "field": "folder_domain_decision.proposed_fields.name",
                    "existing_id": str(duplicate.id),
                }
            )
        self.planned_actions.append(
            PlannedAction("folder", "Folder", "create", "ok", f"Folder '{create_payload['name']}' would be created.")
        )
        return {"action": action, "object": None, "parent_folder": parent_folder, "create_payload": create_payload}

    def _resolve_perimeter_decision(self, decision: dict[str, Any], folder_plan: dict[str, Any]) -> dict[str, Any]:
        action = decision["action"]
        if action in {"skip", "reject"}:
            self.skipped_objects.append(
                {
                    "platform_entity": "Perimeter",
                    "action": action,
                    "detail": "Perimeter setup is required for Step 2 and cannot be skipped or rejected.",
                }
            )
            self.blocking_errors.append(
                {
                    "code": "perimeter_required",
                    "detail": "Perimeter decision must be create or reuse for Step 2.",
                    "field": "perimeter_decision.action",
                }
            )
            self.planned_actions.append(
                PlannedAction("perimeter", "Perimeter", action, "blocked", "Perimeter setup is required.")
            )
            return {"action": action, "object": None, "create_payload": None}

        target_folder = folder_plan.get("object")
        if folder_plan["action"] == "create":
            target_folder = None

        if action == "reuse":
            perimeter = Perimeter.objects.filter(id=decision["selected_existing_id"]).first()
            if perimeter is None:
                self.blocking_errors.append(
                    {
                        "code": "perimeter_not_found",
                        "detail": "selected_existing_id does not match an existing Perimeter.",
                        "field": "perimeter_decision.selected_existing_id",
                    }
                )
                self.planned_actions.append(
                    PlannedAction("perimeter", "Perimeter", "reuse", "blocked", "Selected perimeter does not exist.")
                )
                return {"action": action, "object": None, "create_payload": None}
            if not RoleAssignment.is_object_readable(self.user, Perimeter, perimeter.id):
                self.blocking_errors.append(
                    {
                        "code": "permission_denied",
                        "detail": "You do not have permission to reuse the selected Perimeter.",
                        "field": "perimeter_decision.selected_existing_id",
                    }
                )
            if target_folder is not None and perimeter.folder_id != target_folder.id:
                self.blocking_errors.append(
                    {
                        "code": "perimeter_folder_mismatch",
                        "detail": "The selected Perimeter does not belong to the approved Folder.",
                        "field": "perimeter_decision.selected_existing_id",
                    }
                )
            self.reused_objects.append(self._object_summary("Perimeter", perimeter))
            self.planned_actions.append(
                PlannedAction("perimeter", "Perimeter", "reuse", "ok", f"Perimeter '{perimeter.name}' will be reused.")
            )
            return {"action": action, "object": perimeter, "create_payload": None}

        create_payload = decision["proposed_fields"]
        if folder_plan["action"] == "reuse" and target_folder is not None:
            self._check_add_permission(target_folder, "add_perimeter", "perimeter_decision")
            duplicate = Perimeter.objects.filter(
                folder=target_folder,
                name__iexact=create_payload["name"],
            ).first()
            if duplicate is not None:
                self.blocking_errors.append(
                    {
                        "code": "duplicate_perimeter",
                        "detail": "A Perimeter with the same name already exists in the approved Folder.",
                        "field": "perimeter_decision.proposed_fields.name",
                        "existing_id": str(duplicate.id),
                    }
                )
        self.planned_actions.append(
            PlannedAction("perimeter", "Perimeter", "create", "ok", f"Perimeter '{create_payload['name']}' would be created.")
        )
        return {"action": action, "object": None, "create_payload": create_payload}

    def _resolve_compliance_assessment_decision(
        self,
        decision: dict[str, Any],
        folder_plan: dict[str, Any],
        perimeter_plan: dict[str, Any],
        framework: Framework | None,
    ) -> dict[str, Any]:
        action = decision["action"]
        if action in {"skip", "reject"}:
            self.skipped_objects.append(
                {
                    "platform_entity": "ComplianceAssessment",
                    "action": action,
                    "detail": "ComplianceAssessment setup is required for Step 2 and cannot be skipped or rejected.",
                }
            )
            self.blocking_errors.append(
                {
                    "code": "compliance_assessment_required",
                    "detail": "ComplianceAssessment decision must be create or reuse for Step 2.",
                    "field": "compliance_assessment_decision.action",
                }
            )
            self.planned_actions.append(
                PlannedAction("compliance_assessment", "ComplianceAssessment", action, "blocked", "ComplianceAssessment setup is required.")
            )
            return {"action": action, "object": None, "create_payload": None}

        target_folder = folder_plan.get("object")
        target_perimeter = perimeter_plan.get("object")

        if action == "reuse":
            assessment = ComplianceAssessment.objects.filter(id=decision["selected_existing_id"]).first()
            if assessment is None:
                self.blocking_errors.append(
                    {
                        "code": "compliance_assessment_not_found",
                        "detail": "selected_existing_id does not match an existing ComplianceAssessment.",
                        "field": "compliance_assessment_decision.selected_existing_id",
                    }
                )
                self.planned_actions.append(
                    PlannedAction("compliance_assessment", "ComplianceAssessment", "reuse", "blocked", "Selected ComplianceAssessment does not exist.")
                )
                return {"action": action, "object": None, "create_payload": None}
            if not RoleAssignment.is_object_readable(self.user, ComplianceAssessment, assessment.id):
                self.blocking_errors.append(
                    {
                        "code": "permission_denied",
                        "detail": "You do not have permission to reuse the selected ComplianceAssessment.",
                        "field": "compliance_assessment_decision.selected_existing_id",
                    }
                )
            if framework is not None and assessment.framework_id != framework.id:
                self.blocking_errors.append(
                    {
                        "code": "framework_mismatch",
                        "detail": "The selected ComplianceAssessment does not use the approved Framework.",
                        "field": "compliance_assessment_decision.selected_existing_id",
                    }
                )
            if target_perimeter is not None and assessment.perimeter_id != target_perimeter.id:
                self.blocking_errors.append(
                    {
                        "code": "perimeter_mismatch",
                        "detail": "The selected ComplianceAssessment does not belong to the approved Perimeter.",
                        "field": "compliance_assessment_decision.selected_existing_id",
                    }
                )
            if target_folder is not None and assessment.folder_id != target_folder.id:
                self.blocking_errors.append(
                    {
                        "code": "folder_mismatch",
                        "detail": "The selected ComplianceAssessment does not belong to the approved Folder.",
                        "field": "compliance_assessment_decision.selected_existing_id",
                    }
                )
            self.reused_objects.append(self._object_summary("ComplianceAssessment", assessment))
            self.planned_actions.append(
                PlannedAction("compliance_assessment", "ComplianceAssessment", "reuse", "ok", f"ComplianceAssessment '{assessment.name}' will be reused.")
            )
            return {"action": action, "object": assessment, "create_payload": None}

        create_payload = decision["proposed_fields"]
        if framework is None:
            self.blocking_errors.append(
                {
                    "code": "framework_required",
                    "detail": "A resolved Framework is required before ComplianceAssessment creation.",
                    "field": "framework_resolution",
                }
            )
        if folder_plan["action"] == "reuse" and target_folder is not None:
            self._check_add_permission(target_folder, "add_complianceassessment", "compliance_assessment_decision")
        if perimeter_plan["action"] == "reuse" and target_perimeter is not None:
            duplicate = ComplianceAssessment.objects.filter(
                perimeter=target_perimeter,
                name__iexact=create_payload["name"],
                version__iexact=create_payload.get("version") or "1.0",
            ).first()
            if duplicate is not None:
                self.blocking_errors.append(
                    {
                        "code": "duplicate_compliance_assessment",
                        "detail": "A ComplianceAssessment with the same name and version already exists in the approved Perimeter.",
                        "field": "compliance_assessment_decision.proposed_fields.name",
                        "existing_id": str(duplicate.id),
                    }
                )
        self.planned_actions.append(
            PlannedAction(
                "compliance_assessment",
                "ComplianceAssessment",
                "create",
                "ok",
                f"ComplianceAssessment '{create_payload['name']}' would be created.",
            )
        )
        return {"action": action, "object": None, "create_payload": create_payload}

    def _resolve_risk_assessment_decision(self, decision: dict[str, Any], folder_plan: dict[str, Any], perimeter_plan: dict[str, Any]) -> dict[str, Any]:
        action = decision["action"]
        if action in {"skip", "reject"}:
            self.skipped_objects.append(
                {
                    "platform_entity": "RiskAssessment",
                    "action": action,
                    "detail": "Optional RiskAssessment will not be created in Step 2.",
                }
            )
            self.planned_actions.append(
                PlannedAction("risk_assessment", "RiskAssessment", action, "ok", "Optional RiskAssessment skipped.")
            )
            if action == "reject":
                self.warnings.append(
                    {
                        "code": "optional_risk_assessment_rejected",
                        "detail": "The optional RiskAssessment was explicitly rejected and will not be created.",
                    }
                )
            return {"action": action, "object": None, "create_payload": None, "risk_matrix": None}

        target_folder = folder_plan.get("object")
        target_perimeter = perimeter_plan.get("object")

        if action == "reuse":
            assessment = RiskAssessment.objects.filter(id=decision["selected_existing_id"]).first()
            if assessment is None:
                self.blocking_errors.append(
                    {
                        "code": "risk_assessment_not_found",
                        "detail": "selected_existing_id does not match an existing RiskAssessment.",
                        "field": "risk_assessment_decision.selected_existing_id",
                    }
                )
                self.planned_actions.append(
                    PlannedAction("risk_assessment", "RiskAssessment", "reuse", "blocked", "Selected RiskAssessment does not exist.")
                )
                return {"action": action, "object": None, "create_payload": None, "risk_matrix": None}
            if not RoleAssignment.is_object_readable(self.user, RiskAssessment, assessment.id):
                self.blocking_errors.append(
                    {
                        "code": "permission_denied",
                        "detail": "You do not have permission to reuse the selected RiskAssessment.",
                        "field": "risk_assessment_decision.selected_existing_id",
                    }
                )
            if target_perimeter is not None and assessment.perimeter_id != target_perimeter.id:
                self.blocking_errors.append(
                    {
                        "code": "perimeter_mismatch",
                        "detail": "The selected RiskAssessment does not belong to the approved Perimeter.",
                        "field": "risk_assessment_decision.selected_existing_id",
                    }
                )
            if target_folder is not None and assessment.folder_id != target_folder.id:
                self.blocking_errors.append(
                    {
                        "code": "folder_mismatch",
                        "detail": "The selected RiskAssessment does not belong to the approved Folder.",
                        "field": "risk_assessment_decision.selected_existing_id",
                    }
                )
            self.reused_objects.append(self._object_summary("RiskAssessment", assessment))
            self.planned_actions.append(
                PlannedAction("risk_assessment", "RiskAssessment", "reuse", "ok", f"RiskAssessment '{assessment.name}' will be reused.")
            )
            return {"action": action, "object": assessment, "create_payload": None, "risk_matrix": assessment.risk_matrix}

        create_payload = decision["proposed_fields"]
        risk_matrix = RiskMatrix.objects.filter(id=create_payload["selected_risk_matrix_id"]).first()
        if risk_matrix is None:
            self.blocking_errors.append(
                {
                    "code": "risk_matrix_not_found",
                    "detail": "selected_risk_matrix_id does not match an existing RiskMatrix.",
                    "field": "risk_assessment_decision.proposed_fields.selected_risk_matrix_id",
                }
            )
        elif not RoleAssignment.is_object_readable(self.user, RiskMatrix, risk_matrix.id):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to use the selected RiskMatrix.",
                    "field": "risk_assessment_decision.proposed_fields.selected_risk_matrix_id",
                }
            )
            risk_matrix = None
        if folder_plan["action"] == "reuse" and target_folder is not None:
            self._check_add_permission(target_folder, "add_riskassessment", "risk_assessment_decision")
        if perimeter_plan["action"] == "reuse" and target_perimeter is not None:
            duplicate = RiskAssessment.objects.filter(
                perimeter=target_perimeter,
                name__iexact=create_payload["name"],
                version__iexact=create_payload.get("version") or "1.0",
            ).first()
            if duplicate is not None:
                self.blocking_errors.append(
                    {
                        "code": "duplicate_risk_assessment",
                        "detail": "A RiskAssessment with the same name and version already exists in the approved Perimeter.",
                        "field": "risk_assessment_decision.proposed_fields.name",
                        "existing_id": str(duplicate.id),
                    }
                )
        self.planned_actions.append(
            PlannedAction("risk_assessment", "RiskAssessment", "create", "ok", f"RiskAssessment '{create_payload['name']}' would be created.")
        )
        return {"action": action, "object": None, "create_payload": create_payload, "risk_matrix": risk_matrix}

    def _execute_write_plan(self, resolved: dict[str, Any]) -> None:
        folder = self._apply_folder_decision(resolved["folder"])
        perimeter = self._apply_perimeter_decision(resolved["perimeter"], folder)
        framework = resolved["framework"]
        compliance_assessment = self._apply_compliance_assessment_decision(
            resolved["compliance_assessment"],
            folder,
            perimeter,
            framework,
        )
        self._apply_risk_assessment_decision(resolved["risk_assessment"], folder, perimeter)
        if compliance_assessment is not None and resolved["compliance_assessment"]["action"] == "create":
            self.warnings.append(
                {
                    "code": "requirement_assessments_autogenerated",
                    "detail": "RequirementAssessment records were auto-generated by ComplianceAssessment creation and no result updates were applied in Step 2.",
                }
            )

    def _apply_folder_decision(self, plan: dict[str, Any]) -> Folder:
        if plan["action"] == "reuse":
            return plan["object"]

        data = {
            "name": plan["create_payload"]["name"],
            "description": plan["create_payload"].get("description"),
            "parent_folder": str(plan["parent_folder"].id),
            "create_iam_groups": plan["create_payload"].get("create_iam_groups", False),
        }
        serializer = FolderWriteSerializer(data=data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        folder = serializer.save()
        if data["create_iam_groups"]:
            Folder.create_default_ug_and_ra(folder)
        self.created_objects.append(self._object_summary("Folder", folder))
        return folder

    def _apply_perimeter_decision(self, plan: dict[str, Any], folder: Folder) -> Perimeter:
        if plan["action"] == "reuse":
            return plan["object"]

        data = {
            "folder": str(folder.id),
            "name": plan["create_payload"]["name"],
            "ref_id": plan["create_payload"].get("ref_id"),
            "description": plan["create_payload"].get("description"),
            "lc_status": plan["create_payload"].get("lc_status", "in_design"),
        }
        serializer = PerimeterWriteSerializer(data=data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        perimeter = serializer.save()
        self.created_objects.append(self._object_summary("Perimeter", perimeter))
        return perimeter

    def _apply_compliance_assessment_decision(
        self,
        plan: dict[str, Any],
        folder: Folder,
        perimeter: Perimeter,
        framework: Framework,
    ) -> ComplianceAssessment:
        if plan["action"] == "reuse":
            return plan["object"]

        data = {
            "folder": str(folder.id),
            "perimeter": str(perimeter.id),
            "framework": str(framework.id),
            "name": plan["create_payload"]["name"],
            "ref_id": plan["create_payload"].get("ref_id"),
            "version": plan["create_payload"].get("version") or "1.0",
            "status": plan["create_payload"].get("status") or "planned",
            "description": plan["create_payload"].get("description"),
        }
        serializer = ComplianceAssessmentWriteSerializer(data=data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        assessment = serializer.save()
        assessment.create_requirement_assessments()
        self.created_objects.append(self._object_summary("ComplianceAssessment", assessment))
        return assessment

    def _apply_risk_assessment_decision(self, plan: dict[str, Any], folder: Folder, perimeter: Perimeter) -> RiskAssessment | None:
        if plan["action"] in {"skip", "reject"}:
            return None
        if plan["action"] == "reuse":
            return plan["object"]

        data = {
            "folder": str(folder.id),
            "perimeter": str(perimeter.id),
            "risk_matrix": str(plan["risk_matrix"].id),
            "name": plan["create_payload"]["name"],
            "ref_id": plan["create_payload"].get("ref_id"),
            "version": plan["create_payload"].get("version") or "1.0",
            "status": plan["create_payload"].get("status") or "planned",
            "description": plan["create_payload"].get("description"),
        }
        serializer = RiskAssessmentWriteSerializer(data=data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        assessment = serializer.save()
        self.created_objects.append(self._object_summary("RiskAssessment", assessment))
        return assessment

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

    def _object_summary(self, platform_entity: str, obj: Any) -> dict[str, Any]:
        summary = {
            "platform_entity": platform_entity,
            "id": str(obj.id),
            "name": getattr(obj, "name", str(obj)),
        }
        if hasattr(obj, "ref_id"):
            summary["ref_id"] = getattr(obj, "ref_id", None)
        return summary

    def _dry_run_status(self) -> str:
        if self.blocking_errors:
            return "blocked"
        if self.warnings:
            return "passed_with_warnings"
        return "validated"

    def _write_status(self) -> str:
        if self.created_objects and self.reused_objects:
            return "created_and_reused"
        if self.created_objects:
            return "created"
        if self.reused_objects:
            return "reused"
        return "completed"

    def _blocking_status_code(self) -> int:
        if any(item.get("code") == "permission_denied" for item in self.blocking_errors):
            return 403
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
            "source_step1_draft_hash": self.payload["source_step1_draft_hash"],
            "idempotency_key": self.payload.get("idempotency_key"),
            "status": status,
            "created_objects": [] if operation_type == "dry_run" else self.created_objects,
            "reused_objects": self.reused_objects,
            "skipped_objects": self.skipped_objects,
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
                    "Resolve the blocking errors and rerun Step 2 dry-run.",
                    "Step 3 is not implemented in this endpoint.",
                ]
            return [
                "If the human-approved payload is final, submit the same request with dry_run=false and approved_by_user=true.",
                "Future Step 3 candidates include assets, applied controls, vulnerabilities, risk scenarios, and evidence, but Step 3 is not implemented here.",
            ]
        return [
            "Step 2 setup is complete.",
            "Future Step 3 candidates include assets, applied controls, vulnerabilities, risk scenarios, and evidence, but Step 3 is not implemented here.",
        ]


def execute_case_setup(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiCaseSetupService(request=request, payload=payload)
    return service.execute()