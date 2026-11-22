from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from django.contrib.auth.models import Permission
from django.db import transaction

from core.models import (Asset, AppliedControl, Assessment, RiskAssessment, RiskScenario, Threat, Vulnerability)
from iam.models import Folder, RoleAssignment

from .risk_scenario_full_fields import (
    FullFieldValidationError, resolve_full_fields, apply_full_fields, FullFieldPlan,
)
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
# Threat and Vulnerability are actual platform records; the text of the reviewed
# suggestion is not evidence. New objects remain local unpublished drafts.
AI_ORIGIN_MARKER = "Recorded from the AI onboarding Step 8A advisory suggestion after human review."
MAX_RELATED_NAME_LENGTH = 200



@dataclass
class PlannedScenarioAction:
    source_temporary_id: str
    decision: str
    status: str
    detail: str
    record_type: str = RECORD_TYPE
    target_name: str | None = None
    related_threat_name: str | None = None
    related_vulnerability_name: str | None = None
    full_field_preview: dict[str, Any] = field(default_factory=dict)

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
        # Show the actual records to be created/linked BEFORE approval. For a
        # previously AI-created risk, these come from its SAVED description.
        if self.related_threat_name:
            payload["related_threat_name"] = self.related_threat_name
        if self.related_vulnerability_name:
            payload["related_vulnerability_name"] = self.related_vulnerability_name
        if self.full_field_preview:
            payload["full_field_preview"] = self.full_field_preview
        return payload


@dataclass
class RelatedRecordPlan:
    kind: str
    name: str
    existing_instance: Any = None


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
    proposed_threat: RelatedRecordPlan | None = None
    proposed_vulnerability: RelatedRecordPlan | None = None
    # Prevent a concurrent/manual edit to the saved description after dry-run.
    origin_description: str | None = None
    reviewed_fields: dict[str, Any] = field(default_factory=dict)
    full_field_preview: dict[str, Any] = field(default_factory=dict)


class AiRiskScenarioCommitService:
    """Deterministic Step 8B commit. No AI provider is imported or called here."""

    def __init__(self, *, request, payload: dict[str, Any]):
        self.request = request
        self.user = request.user
        self.payload = payload
        self.planned_actions: list[PlannedScenarioAction] = []
        self.created_records: list[dict[str, Any]] = []
        self.reused_records: list[dict[str, Any]] = []
        self.updated_records: list[dict[str, Any]] = []
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
        except FullFieldValidationError as exc:
            raise RiskScenarioCommitValidationError(
                exc.code, str(exc), status_code=422,
                blocking_errors=[{"code": exc.code, "detail": str(exc), "field": "reviewed_fields"}],
            )
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
            if not RoleAssignment.is_object_readable(self.user, RiskScenario, existing.id):
                self._block(
                    "permission_denied",
                    "You cannot use a risk scenario in this scope.",
                    f"{field_prefix}.payload.title", temporary_id, "create",
                )
                return
            # Legacy SICO AI-created records stored reviewed Threat and
            # Vulnerability advice in the description without linking records.
            # For an existing risk, the ORIGINAL SAVED text is authoritative:
            # never make up a new relationship from a later AI suggestion.
            # This path cannot alter unrelated/human-authored scenarios.
            saved_advice = self._saved_ai_advice(existing) if str(existing.folder_id) == str(folder.id) else {}
            if saved_advice:
                missing_threat = (
                    self._plan_related(field_prefix, "threat", saved_advice, folder)
                    if not existing.threats.exists() else None
                )
                missing_vuln = (
                    self._plan_related(field_prefix, "vulnerability", saved_advice, folder)
                    if not existing.vulnerabilities.exists() else None
                )
                reviewed_fields = payload.get("reviewed_fields") or {}
                full_plan = self._validate_full_fields(
                    field_prefix, reviewed_fields, folder, risk_assessment, existing
                )
                if missing_threat or missing_vuln or (full_plan and full_plan.has_changes()):
                    planned_names.add(label.lower())
                    plans.append(WritePlan(
                        source_temporary_id=temporary_id,
                        decision="link_existing_ai",
                        target_name=existing.name,
                        risk_assessment=risk_assessment,
                        existing_instance=existing,
                        proposed_threat=missing_threat,
                        proposed_vulnerability=missing_vuln,
                        reviewed_fields=reviewed_fields,
                        full_field_preview=full_plan.preview() if full_plan else {},
                        origin_description=existing.description,
                    ))
                    self.planned_actions.append(PlannedScenarioAction(
                        temporary_id, "create", "planned",
                        "The original AI risk will be completed with reviewed missing fields. "
                        "Original description and existing manual values and links stay unchanged. "
                        "Risk ratings require separately confirmed evidence and exact matrix values.",
                        target_name=existing.name,
                        related_threat_name=missing_threat.name if missing_threat else None,
                        related_vulnerability_name=missing_vuln.name if missing_vuln else None,
                        full_field_preview=full_plan.preview() if full_plan else {},
                    ))
                    return
            self.warnings.append({
                "code": "duplicate_reused",
                "detail": (
                    "Existing RiskScenario will be reused without mutation. "
                    "It is not eligible for an automatically approved relationship backfill."
                ),
                "field": f"{field_prefix}.payload.title",
            })
            planned_names.add(label.lower())
            plans.append(WritePlan(
                source_temporary_id=temporary_id,
                decision="reuse", target_name=existing.name,
                risk_assessment=risk_assessment, existing_instance=existing,
            ))
            self.planned_actions.append(PlannedScenarioAction(
                temporary_id, "reuse", "planned",
                "An existing RiskScenario with the same title would be reused unchanged.",
                target_name=existing.name,
            ))
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
        proposed_threat = self._plan_related(field_prefix, "threat", payload, folder)
        proposed_vulnerability = self._plan_related(field_prefix, "vulnerability", payload, folder)
        reviewed_fields = payload.get("reviewed_fields") or {}
        full_plan = self._validate_full_fields(
            field_prefix, reviewed_fields, folder, risk_assessment
        )

        if not full_plan or not any(field in full_plan.scalars for field in (
                "inherent_proba", "current_proba", "residual_proba")):
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
                proposed_threat=proposed_threat,
                proposed_vulnerability=proposed_vulnerability,
                reviewed_fields=reviewed_fields,
                full_field_preview=full_plan.preview() if full_plan else {},
            )
        )
        self.planned_actions.append(
            PlannedScenarioAction(
                temporary_id, "create", "planned",
                (
                    "RiskScenario would be created with human-reviewed, evidence-confirmed "
                    "matrix values; the platform calculates risk levels. "
                    if full_plan and any(full_plan.scalars.get(k, -1) >= 0 for k in (
                        "inherent_proba", "current_proba", "residual_proba"
                    )) else "RiskScenario would be created unrated. "
                ) + "Reviewed Threat/Vulnerability text would be linked to same-folder "
                "existing records or saved as unpublished unverified drafts. "
                "No risk acceptance or closure.",
                target_name=label,
                related_threat_name=proposed_threat.name if proposed_threat else None,
                related_vulnerability_name=proposed_vulnerability.name if proposed_vulnerability else None,
                full_field_preview=full_plan.preview() if full_plan else {},
            )
        )

    # ---- resolution helpers ------------------------------------------------

    def _validate_full_fields(self, prefix, fields, folder, assessment, existing=None):
        try:
            return resolve_full_fields(self.user, fields, folder, assessment, existing)
        except FullFieldValidationError as exc:
            self.blocking_errors.append({
                "code": exc.code,
                "detail": str(exc),
                "field": prefix + ".payload.reviewed_fields",
            })
            return None

    @staticmethod
    def _saved_ai_advice(instance: RiskScenario) -> dict[str, str]:
        """Extract only explicit original AI advice from an unchanged legacy record.

        The earlier SICO commit used double-newline separated paragraphs and a
        fixed closing provenance sentence. Accept Windows line endings, but do
        not use a later AI proposal to silently change the meaning of the risk.
        Fail closed for absent, ambiguous or edited provenance/content.
        """
        text = (instance.description or "").replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = [part.strip() for part in re.split(r"\n[ \t]*\n+", text) if part.strip()]
        allowed_closings = {
            AI_ORIGIN_MARKER +
            " No risk rating, risk treatment, or risk acceptance was set by this step.",
            AI_ORIGIN_MARKER +
            " Official matrix scores were entered by the human reviewer and calculated by "
            "the platform; no risk acceptance or closure was performed.",
            AI_ORIGIN_MARKER +
            " Only reviewer-selected values were saved through platform fields. "
            "No risk acceptance or closure was performed.",
        }
        if not paragraphs or paragraphs[-1] not in allowed_closings:
            return {}
        advice: dict[str, str] = {}
        for kind, label in (("threat", "Threat: "), ("vulnerability", "Vulnerability: ")):
            matches = [part[len(label):].strip() for part in paragraphs
                       if part.startswith(label)]
            if len(matches) > 1:
                return {}  # Ambiguous descriptions must never auto-create links.
            if matches and "\n" not in matches[0] and matches[0]:
                advice[kind] = matches[0]
        return advice

    def _eligible_ai_backfill(self, instance: RiskScenario, payload: dict[str, Any]) -> bool:
        """Compatibility guard: accept only saved original advice, never new advice."""
        saved = self._saved_ai_advice(instance)
        return bool(saved) and all(
            not (payload.get(kind) or "").strip()
            or (payload.get(kind) or "").strip() == saved.get(kind)
            for kind in ("threat", "vulnerability")
        )

    def _plan_related(
        self, field_prefix: str, kind: str, payload: dict[str, Any], folder: Folder
    ) -> RelatedRecordPlan | None:
        """Exact-name matching only. No uncertain keyword matches are auto-linked."""
        name = (payload.get(kind) or "").strip()
        if not name:
            return None
        if len(name) > MAX_RELATED_NAME_LENGTH:
            self.blocking_errors.append({
                "code": "related_name_too_long",
                "detail": f"Reviewed {kind} is too long for its platform record name "
                          f"(maximum {MAX_RELATED_NAME_LENGTH} characters). Shorten it first.",
                "field": f"{field_prefix}.payload.{kind}",
            })
            return None
        model = Threat if kind == "threat" else Vulnerability
        existing = model.objects.filter(folder_id=folder.id, name__iexact=name).first()
        if existing is not None:
            if not RoleAssignment.is_object_readable(self.user, model, existing.id):
                self.blocking_errors.append({
                    "code": "permission_denied",
                    "detail": f"Cannot safely use the selected {kind} record in this scope.",
                    "field": f"{field_prefix}.payload.{kind}",
                })
                return None
            return RelatedRecordPlan(kind=kind, name=name, existing_instance=existing)
        if not self._has_permission(f"add_{kind}", folder):
            self.blocking_errors.append({
                "code": "permission_denied",
                "detail": f"You cannot create a draft {kind} in this organization.",
                "field": f"{field_prefix}.payload.{kind}",
            })
            return None
        self.warnings.append({
            "code": f"ai_proposed_{kind}_unverified",
            "detail": f"The reviewed {kind} text will be saved as an unpublished draft "
                      "in this folder. It is not a verified security finding.",
            "field": f"{field_prefix}.payload.{kind}",
        })
        return RelatedRecordPlan(kind=kind, name=name)

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

    def _link_reviewed_relations(self, instance: RiskScenario, plan: WritePlan) -> None:
        folder = plan.risk_assessment.folder
        for relation in (plan.proposed_threat, plan.proposed_vulnerability):
            if relation is None:
                continue
            model = Threat if relation.kind == "threat" else Vulnerability
            # Recheck exact-folder match inside the transaction. Never match by
            # keyword, cross a folder, or mutate existing catalog entries.
            target = model.objects.filter(
                folder_id=folder.id, name__iexact=relation.name
            ).first()
            if target is not None:
                if not RoleAssignment.is_object_readable(self.user, model, target.id):
                    raise RiskScenarioCommitValidationError(
                        "related_permission_denied",
                        "A reviewed related record is no longer readable. No changes saved.",
                        status_code=403,
                    )
            else:
                if not self._has_permission(f"add_{relation.kind}", folder):
                    raise RiskScenarioCommitValidationError(
                        "related_permission_denied",
                        "Permission to create a related draft is missing. No changes saved.",
                        status_code=403,
                    )
                note = (
                    "AI-proposed draft from a human-reviewed risk scenario. "
                    "Not verified by independent evidence; validate before treating as confirmed."
                )
                kwargs = dict(folder=folder, name=relation.name,
                              description=note, is_published=False)
                if relation.kind == "vulnerability":
                    kwargs["status"] = Vulnerability.Status.POTENTIAL
                target = model.objects.create(**kwargs)
            getattr(instance, "threats" if relation.kind == "threat" else "vulnerabilities").add(target)

    def _execute_write_plan(self, plans: list[WritePlan]) -> None:
        for plan in plans:
            if plan.decision == "reuse":
                self.reused_records.append(
                    self._record_summary(plan.existing_instance, plan, "reuse")
                )
                continue
            # Serialize concurrent AI saves against the same assessment. Every
            # saved draft and relation is committed or rolled back as one unit.
            current_assessment = (RiskAssessment.objects.select_for_update()
                                  .get(id=plan.risk_assessment.id))
            if (current_assessment.is_locked or
                    current_assessment.status == Assessment.Status.IN_REVIEW):
                raise RiskScenarioCommitValidationError(
                    "changed_since_dry_run",
                    "Assessment is now locked or in review. No changes saved.",
                    status_code=422,
                )
            if not self._has_permission("change_riskscenario", current_assessment.folder):
                raise RiskScenarioCommitValidationError(
                    "permission_denied", "Risk change permission is missing.",
                    status_code=403,
                )
            if plan.decision == "create" and not self._has_permission(
                "add_riskscenario", current_assessment.folder
            ):
                raise RiskScenarioCommitValidationError(
                    "permission_denied", "Risk creation permission is missing.",
                    status_code=403,
                )
            if plan.decision == "link_existing_ai":
                instance = RiskScenario.objects.select_for_update().get(
                    id=plan.existing_instance.id, risk_assessment=plan.risk_assessment
                )
                if (not RoleAssignment.is_object_readable(self.user, RiskScenario, instance.id)
                        or instance.description != plan.origin_description
                        or not self._eligible_ai_backfill(instance, {
                            "threat": plan.proposed_threat.name if plan.proposed_threat else "",
                            "vulnerability": plan.proposed_vulnerability.name if plan.proposed_vulnerability else "",
                        })):
                    raise RiskScenarioCommitValidationError(
                        "changed_since_dry_run",
                        "Saved risk is no longer eligible for relationship-only completion.",
                        status_code=422,
                    )
                if (plan.proposed_threat and instance.threats.exists()) or (
                    plan.proposed_vulnerability and instance.vulnerabilities.exists()
                ):
                    raise RiskScenarioCommitValidationError(
                        "changed_since_dry_run",
                        "Risk relationships changed since review; run the dry-run again.",
                        status_code=422,
                    )
                # Re-resolve inside the database transaction in case the scope,
                # permissions or reviewed linked records changed after dry-run.
                full_plan = resolve_full_fields(
                    self.user, plan.reviewed_fields, current_assessment.folder,
                    current_assessment, instance
                )
                self._link_reviewed_relations(instance, plan)
                apply_full_fields(instance, full_plan)
                self.updated_records.append(self._record_summary(instance, plan, "linked_existing_ai"))
                continue
            # If a concurrent save already created the same scenario, abort and
            # ask for a fresh dry-run instead of creating a duplicate record.
            if RiskScenario.objects.filter(risk_assessment=plan.risk_assessment,
                                            name__iexact=plan.target_name).exists():
                raise RiskScenarioCommitValidationError(
                    "changed_since_dry_run",
                    "A risk with this name now exists. Run a new dry-run before saving.",
                    status_code=422,
                )
            # Create an unrated scenario; no treatment or risk acceptance.
            instance = RiskScenario.objects.create(
                risk_assessment=plan.risk_assessment,
                name=plan.target_name,
                description=plan.description,
                ref_id=RiskScenario.get_default_ref_id(plan.risk_assessment),
            )
            # The complete review uses the proper, separately selected relation
            # fields. Never sneak Step 8A legacy hints into a different category.
            if not plan.reviewed_fields:
                if plan.assets:
                    instance.assets.add(*plan.assets)
                if plan.applied_controls:
                    instance.applied_controls.add(*plan.applied_controls)
            full_plan = resolve_full_fields(
                self.user, plan.reviewed_fields, current_assessment.folder,
                current_assessment, None
            )
            apply_full_fields(instance, full_plan)
            self._link_reviewed_relations(instance, plan)
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
            "linked_threat_ids": list(map(str, instance.threats.values_list("id", flat=True))),
            "linked_vulnerability_ids": list(map(str, instance.vulnerabilities.values_list("id", flat=True))),
            "linked_asset_ids": list(map(str, instance.assets.values_list("id", flat=True))),
            "linked_applied_control_ids": list(map(str, instance.applied_controls.values_list("id", flat=True))),
            "linked_existing_control_ids": list(map(str, instance.existing_applied_controls.values_list("id", flat=True))),
            "risk_rating_recorded": any(getattr(instance, key) >= 0 for key in (
                "inherent_level", "current_level", "residual_level"
            )),
            "full_field_values": plan.full_field_preview,
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
        if self.updated_records:
            return "linked_existing_ai"
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
            "updated_records": [] if dry_run else self.updated_records,
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
        "Only reviewer-selected values were saved through platform fields. "
        "No risk acceptance or closure was performed."
    )
    return "\n\n".join(lines)


def execute_risk_scenario_commit(request, payload: dict[str, Any]) -> dict[str, Any]:
    service = AiRiskScenarioCommitService(request=request, payload=payload)
    return service.execute()
