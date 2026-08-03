from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import Asset, AppliedControl, Assessment, RiskAssessment, RiskScenario
from iam.models import Folder, RoleAssignment

from .risk_scenario_commit_guardrails import (
    RiskScenarioCommitValidationError,
    validate_risk_scenario_commit_guardrails,
)


# Step 8B persists a reviewed Step 8A suggestion onto the platform's existing risk model.
# core.RiskScenario is the write target and it always belongs to an existing
# core.RiskAssessment, so Step 8B requires a resolvable assessment_reference and never
# creates a RiskAssessment, a RiskMatrix, or a RiskAcceptance. No AI provider module is
# imported or called here.
RECORD_TYPE = "risk_scenario"

MAX_NAME_LENGTH = 200

# Advisory Step 8A ratings. The platform rates risk on the ordinal scale of the risk
# assessment's RiskMatrix, so a low/medium/high/critical label cannot be mapped to a
# platform rating without inventing one. The scenario is created unrated (the platform's
# own "not rated" default) and the advisory ratings are preserved as readable text in the
# new record's description instead.
UNRATED_ADVISORY_FIELDS = ("likelihood", "impact", "risk_level")


@dataclass
class PlannedScenarioAction:
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
    risk_assessment: Any = None
    existing_instance: Any = None
    description: str = ""
    assets: list[Any] = field(default_factory=list)
    applied_controls: list[Any] = field(default_factory=list)


class AiRiskScenarioCommitService:
    """Deterministic Step 8B commit. No AI provider is imported or called here."""

    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedScenarioAction] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.rejected_records: list[dict[str, Any]] = []
        self.deferred_records: list[dict[str, Any]] = []
        self.skipped_records: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.blocking_errors: list[dict[str, Any]] = []

    # ---- entry point -------------------------------------------------------

    def execute(self) -> dict[str, Any]:
        validate_risk_scenario_commit_guardrails(self.payload)

        plans = self._plan_and_validate()

        if self.payload["dry_run"]:
            return self._build_response(dry_run=True, commit_status=self._dry_run_status())

        if self.blocking_errors:
            raise RiskScenarioCommitValidationError(
                "ai_risk_scenario_commit_blocked",
                "The approved Step 8B payload is blocked and cannot be executed.",
                status_code=self._blocking_status_code(),
                response_payload=self._build_response(dry_run=False, commit_status="blocked"),
            )

        try:
            with transaction.atomic():
                self._execute_write_plan(plans)
        except RiskScenarioCommitValidationError:
            raise
        except Exception as exc:  # noqa: BLE001 - surfaced as a rolled-back commit
            self.created_records = []
            self.reused_records = []
            raise RiskScenarioCommitValidationError(
                "transaction_aborted",
                "Step 8B transaction failed and all writes were rolled back.",
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
        risk_assessment = self._resolve_risk_assessment(folder)
        if risk_assessment is not None:
            self._check_assessment_writable(risk_assessment)
            self._check_change_permission(risk_assessment)

        plans: list[WritePlan] = []
        planned_names: set[str] = set()

        for index, decision in enumerate(self.payload.get("decisions") or []):
            self._plan_decision(
                index, decision, folder, risk_assessment, plans, planned_names
            )

        return plans

    def _plan_decision(
        self,
        index: int,
        decision: dict[str, Any],
        folder: Folder | None,
        risk_assessment: RiskAssessment | None,
        plans: list[WritePlan],
        planned_names: set[str],
    ) -> None:
        field_prefix = f"decisions[{index}]"
        temporary_id = decision["temporary_id"]
        action = decision["decision"]
        payload = decision.get("payload") or {}
        label = (payload.get("title") or "").strip()[:MAX_NAME_LENGTH]

        if not decision.get("selected"):
            self.skipped_records.append(
                {
                    "source_temporary_id": temporary_id,
                    "title": label or None,
                    "skip_reason": "not_selected",
                }
            )
            self.planned_actions.append(
                PlannedScenarioAction(
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
                PlannedScenarioAction(
                    temporary_id, "reject", "ok",
                    "Risk scenario rejected by reviewer.", target_name=label or None,
                )
            )
            return

        if action == "defer":
            self.deferred_records.append(
                {"source_temporary_id": temporary_id, "title": label or None}
            )
            self.planned_actions.append(
                PlannedScenarioAction(
                    temporary_id, "defer", "ok",
                    "Risk scenario deferred by reviewer.", target_name=label or None,
                )
            )
            return

        if folder is None:
            self.planned_actions.append(
                PlannedScenarioAction(
                    temporary_id, action, "blocked",
                    "A valid folder_reference is required before Step 8B can create or reuse "
                    "records.",
                    target_name=label or None,
                )
            )
            return

        if risk_assessment is None:
            self._block(
                "risk_assessment_reference_required",
                "A resolvable assessment_reference pointing at an existing RiskAssessment is "
                "required before Step 8B can persist a risk scenario. Step 8B never creates a "
                "RiskAssessment or a RiskMatrix.",
                "assessment_reference",
                temporary_id,
                action,
            )
            return

        if action == "reuse":
            self._plan_reuse(field_prefix, temporary_id, decision, risk_assessment, plans)
            return

        self._plan_create(
            field_prefix, temporary_id, payload, label, folder, risk_assessment, plans,
            planned_names,
        )

    def _plan_reuse(
        self,
        field_prefix: str,
        temporary_id: str,
        decision: dict[str, Any],
        risk_assessment: RiskAssessment,
        plans: list[WritePlan],
    ) -> None:
        existing_id = decision["existing_record_reference"]
        instance = (
            RiskScenario.objects.filter(id=existing_id)
            .select_related("risk_assessment", "folder")
            .first()
        )

        if instance is None:
            self._block(
                "reuse_target_not_found",
                "existing_record_reference does not match an existing RiskScenario.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        if not RoleAssignment.is_object_readable(self.user, RiskScenario, instance.id):
            self._block(
                "permission_denied",
                "You do not have permission to reuse the selected RiskScenario.",
                f"{field_prefix}.existing_record_reference",
                temporary_id,
                "reuse",
            )
            return

        if str(instance.risk_assessment_id) != str(risk_assessment.id):
            self._block(
                "reuse_out_of_scope",
                "existing_record_reference must belong to assessment_reference.",
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
                risk_assessment=risk_assessment,
                existing_instance=instance,
            )
        )
        self.planned_actions.append(
            PlannedScenarioAction(
                temporary_id, "reuse", "planned",
                "Existing RiskScenario would be reused without mutation.",
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
        risk_assessment: RiskAssessment,
        plans: list[WritePlan],
        planned_names: set[str],
    ) -> None:
        if label.lower() in planned_names:
            self.warnings.append(
                {
                    "code": "duplicate_in_batch_skipped",
                    "detail": (
                        f"Another selected decision already creates a risk scenario named "
                        f"'{label}'; this duplicate was skipped."
                    ),
                    "field": f"{field_prefix}.payload.title",
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
                PlannedScenarioAction(
                    temporary_id, "create", "skipped",
                    "Duplicate risk scenario title within the submitted batch.",
                    target_name=label,
                )
            )
            return

        # Duplicate reuse: an existing scenario with the same name in the same risk
        # assessment is reused rather than duplicated, and it is never mutated.
        existing = RiskScenario.objects.filter(
            risk_assessment=risk_assessment, name__iexact=label
        ).first()

        if existing is not None:
            self.warnings.append(
                {
                    "code": "duplicate_reused",
                    "detail": (
                        f"An existing RiskScenario named '{label}' was found in the selected "
                        "risk assessment and will be reused without mutation."
                    ),
                    "field": f"{field_prefix}.payload.title",
                }
            )
            planned_names.add(label.lower())
            plans.append(
                WritePlan(
                    source_temporary_id=temporary_id,
                    decision="reuse",
                    target_name=existing.name,
                    risk_assessment=risk_assessment,
                    existing_instance=existing,
                )
            )
            self.planned_actions.append(
                PlannedScenarioAction(
                    temporary_id, "reuse", "planned",
                    "An existing RiskScenario with the same title would be reused.",
                    target_name=existing.name,
                )
            )
            return

        if not self._check_add_permission(risk_assessment):
            self._block(
                "permission_denied",
                "You do not have permission to add risk scenarios in the selected scope.",
                f"{field_prefix}.payload.title",
                temporary_id,
                "create",
            )
            return

        assets = self._resolve_assets(field_prefix, payload, folder)
        applied_controls = self._resolve_applied_controls(field_prefix, payload, folder)

        self._warn_unrated_advisory_context(field_prefix)

        planned_names.add(label.lower())
        plans.append(
            WritePlan(
                source_temporary_id=temporary_id,
                decision="create",
                target_name=label,
                risk_assessment=risk_assessment,
                description=_build_description(payload),
                assets=assets,
                applied_controls=applied_controls,
            )
        )
        self.planned_actions.append(
            PlannedScenarioAction(
                temporary_id, "create", "planned",
                "RiskScenario would be created unrated under the selected risk assessment; "
                "no risk treatment and no risk acceptance is recorded.",
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

    def _resolve_risk_assessment(self, folder: Folder | None) -> RiskAssessment | None:
        reference = self.payload.get("assessment_reference")
        if not reference:
            self.blocking_errors.append(
                {
                    "code": "risk_assessment_reference_required",
                    "detail": (
                        "assessment_reference is required: a RiskScenario can only be created "
                        "under an existing RiskAssessment, and Step 8B never creates one."
                    ),
                    "field": "assessment_reference",
                }
            )
            return None

        assessment = (
            RiskAssessment.objects.filter(id=reference)
            .select_related("folder", "risk_matrix")
            .first()
        )
        if assessment is None:
            self.blocking_errors.append(
                {
                    "code": "risk_assessment_not_found",
                    "detail": (
                        "assessment_reference does not match an existing RiskAssessment. "
                        "Step 8B never creates a RiskAssessment or a RiskMatrix."
                    ),
                    "field": "assessment_reference",
                }
            )
            return None

        if not RoleAssignment.is_object_readable(self.user, RiskAssessment, assessment.id):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": "You do not have permission to use the selected RiskAssessment.",
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

    def _check_assessment_writable(self, assessment: RiskAssessment) -> None:
        """Mirror the platform's own RiskScenario write rules."""
        if assessment.is_locked:
            self.blocking_errors.append(
                {
                    "code": "assessment_locked",
                    "detail": "The selected risk assessment is locked and cannot be modified.",
                    "field": "assessment_reference",
                }
            )
        if assessment.status == Assessment.Status.IN_REVIEW:
            self.blocking_errors.append(
                {
                    "code": "assessment_in_review",
                    "detail": "The selected risk assessment is in review and cannot be modified.",
                    "field": "assessment_reference",
                }
            )

    def _check_change_permission(self, assessment: RiskAssessment) -> None:
        if not self._has_permission("change_riskscenario", assessment.folder):
            self.blocking_errors.append(
                {
                    "code": "permission_denied",
                    "detail": (
                        "You do not have permission to change risk scenarios in the selected "
                        "scope."
                    ),
                    "field": "assessment_reference",
                }
            )

    def _check_add_permission(self, assessment: RiskAssessment) -> bool:
        return self._has_permission("add_riskscenario", assessment.folder)

    def _has_permission(self, codename: str, folder: Folder) -> bool:
        permission = Permission.objects.filter(codename=codename).first()
        if permission is None:
            return False
        return RoleAssignment.is_access_allowed(self.user, permission, folder)

    def _resolve_assets(
        self, field_prefix: str, payload: dict[str, Any], folder: Folder
    ) -> list[Asset]:
        reference = payload.get("asset_reference")
        title = payload.get("asset_title")
        if not reference and not title:
            return []

        instance = self._lookup_by_reference(Asset, folder, reference, title)
        if instance is None:
            self.warnings.append(
                {
                    "code": "asset_linkage_not_applied",
                    "detail": (
                        "The referenced asset was not found in the selected folder; the risk "
                        "scenario is recorded without an asset link. Step 8B never creates "
                        "assets."
                    ),
                    "field": f"{field_prefix}.payload.asset_reference",
                }
            )
            return []

        if not RoleAssignment.is_object_readable(self.user, Asset, instance.id):
            self.warnings.append(
                {
                    "code": "asset_linkage_not_applied",
                    "detail": (
                        "You do not have permission to read the referenced asset; the risk "
                        "scenario is recorded without an asset link."
                    ),
                    "field": f"{field_prefix}.payload.asset_reference",
                }
            )
            return []

        return [instance]

    def _resolve_applied_controls(
        self, field_prefix: str, payload: dict[str, Any], folder: Folder
    ) -> list[AppliedControl]:
        reference = payload.get("linked_applied_control_reference")
        title = payload.get("linked_applied_control_title")
        if not reference and not title:
            return []

        instance = self._lookup_by_reference(AppliedControl, folder, reference, title)
        if instance is None:
            self.warnings.append(
                {
                    "code": "applied_control_linkage_not_applied",
                    "detail": (
                        "The referenced applied control was not found in the selected folder; "
                        "the risk scenario is recorded without an applied control link. Step 8B "
                        "never creates applied controls."
                    ),
                    "field": f"{field_prefix}.payload.linked_applied_control_reference",
                }
            )
            return []

        if not RoleAssignment.is_object_readable(self.user, AppliedControl, instance.id):
            self.warnings.append(
                {
                    "code": "applied_control_linkage_not_applied",
                    "detail": (
                        "You do not have permission to read the referenced applied control; the "
                        "risk scenario is recorded without an applied control link."
                    ),
                    "field": f"{field_prefix}.payload.linked_applied_control_reference",
                }
            )
            return []

        return [instance]

    def _lookup_by_reference(self, model, folder: Folder, reference, title):
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

    def _warn_unrated_advisory_context(self, field_prefix: str) -> None:
        self.warnings.append(
            {
                "code": "advisory_rating_not_persisted",
                "detail": (
                    "The advisory "
                    f"{', '.join(UNRATED_ADVISORY_FIELDS)} labels are not platform risk ratings; "
                    "the risk scenario is created unrated on the risk matrix and the advisory "
                    "values are preserved as readable text in its description."
                ),
                "field": f"{field_prefix}.payload",
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
            PlannedScenarioAction(temporary_id, action, "blocked", detail)
        )

    # ---- write phase -------------------------------------------------------

    def _execute_write_plan(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            if plan.decision == "reuse":
                # Reuse never mutates the existing record; it is only reported.
                self.reused_records.append(
                    self._record_summary(plan.existing_instance, plan, "reuse")
                )
                continue

            # No proba/impact/level is set: the platform's own "not rated" defaults apply, so
            # Step 8B records no risk rating. treatment keeps its "open" default, so no risk
            # is accepted, transferred, avoided, or closed here.
            instance = RiskScenario.objects.create(
                risk_assessment=plan.risk_assessment,
                name=plan.target_name,
                description=plan.description,
                ref_id=RiskScenario.get_default_ref_id(plan.risk_assessment),
            )
            if plan.assets:
                instance.assets.add(*plan.assets)
            if plan.applied_controls:
                instance.applied_controls.add(*plan.applied_controls)

            self.created_records.append(self._record_summary(instance, plan, "create"))

    def _record_summary(self, instance, plan: WritePlan, action: str) -> dict[str, Any]:
        return {
            "record_type": RECORD_TYPE,
            "action": action,
            "record_id": str(instance.id),
            "name": instance.name,
            "folder_id": str(instance.folder_id),
            "source_temporary_id": plan.source_temporary_id,
            "risk_assessment_id": str(instance.risk_assessment_id),
            "ref_id": instance.ref_id,
            "linked_asset_ids": [str(asset.id) for asset in plan.assets],
            "linked_applied_control_ids": [
                str(control.id) for control in plan.applied_controls
            ],
            # Recorded unrated on purpose: Step 8B never sets a platform risk rating.
            "risk_rating_recorded": False,
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


def _build_description(payload: dict[str, Any]) -> str:
    """Compose the new record's description from the reviewed advisory context.

    Only a freshly created record's own description is written, so nothing authored by a
    human is ever overwritten. Advisory context with no dedicated platform column is kept
    here as readable text rather than being forced into a rating column.
    """
    lines: list[str] = []
    for label, key in (
        ("", "description"),
        ("Threat", "threat"),
        ("Vulnerability", "vulnerability"),
        ("Potential impact", "impact_description"),
        ("Rationale", "rationale"),
    ):
        value = (payload.get(key) or "").strip() if isinstance(payload.get(key), str) else ""
        if not value:
            continue
        lines.append(value if not label else f"{label}: {value}")

    advisory_rating = ", ".join(
        f"{key.replace('_', ' ')}={payload.get(key)}"
        for key in UNRATED_ADVISORY_FIELDS
        if payload.get(key)
    )
    if advisory_rating:
        lines.append(
            f"Advisory pre-rating for human review (not a platform risk rating): "
            f"{advisory_rating}."
        )

    next_steps = payload.get("recommended_next_steps") or []
    if next_steps:
        lines.append("Recommended next steps: " + "; ".join(next_steps))

    lines.append(
        "Recorded from the AI onboarding Step 8A advisory suggestion after human review. "
        "No risk rating, risk treatment, or risk acceptance was set by this step."
    )
    return "\n\n".join(lines)


def execute_risk_scenario_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiRiskScenarioCommitService(request=request, payload=payload)
    return service.execute()
