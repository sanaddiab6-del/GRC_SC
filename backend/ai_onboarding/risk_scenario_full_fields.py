"""Reviewed full-form RiskScenario fields, resolved against REAL authorized records.

No AI provider. No implicit ratings, owners, or control claims. This module is only
called by the existing human-approved Step 8B service, in its transaction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from django.apps import apps
from typing import Any

from core.models import (
    Actor, AppliedControl, Asset, FilteringLabel, RiskScenario, SecurityException,
    Terminology,
)
from iam.models import RoleAssignment


# Explicit, auditable mapping to actual RiskScenario model relationships.
# Never accept model names or field names from a client request.
COLLECTIONS = {
    "asset_references": (Asset, "assets"),
    "existing_control_references": (AppliedControl, "existing_applied_controls"),
    "extra_control_references": (AppliedControl, "applied_controls"),
    "antecedent_references": (RiskScenario, "antecedent_scenarios"),
    "qualification_references": (Terminology, "qualifications"),
    "exception_references": (SecurityException, "security_exceptions"),
    "label_references": (FilteringLabel, "filtering_labels"),
    "owner_references": (Actor, "owner"),
}

SCORES = (
    "inherent_proba", "inherent_impact", "current_proba", "current_impact",
    "residual_proba", "residual_impact",
)
OPTIONAL_TEXT = ("justification", "existing_controls")
SINGLE_RECORDS = ("risk_origin_reference", "operational_scenario_reference")
TREATMENT_CHOICES = {"open", "mitigate", "avoid", "transfer"}


class FullFieldValidationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class FullFieldPlan:
    scalars: dict[str, Any] = field(default_factory=dict)
    singles: dict[str, Any] = field(default_factory=dict)
    collections: dict[str, list[Any]] = field(default_factory=dict)

    def preview(self) -> dict[str, Any]:
        return {
            "scalar_fields": dict(self.scalars),
            "linked_records": {
                key: [{"id": str(item.id), "name": safe_label(item)} for item in items]
                for key, items in self.collections.items()
            },
            "single_records": {
                key: {"id": str(item.id), "name": safe_label(item)}
                for key, item in self.singles.items()
            },
        }

    def has_changes(self) -> bool:
        return bool(self.scalars or self.singles or any(self.collections.values()))


def safe_label(obj) -> str:
    if isinstance(obj, FilteringLabel):
        return str(obj.label)
    if isinstance(obj, Actor):
        if obj.user_id:
            return str(getattr(obj.user, "email", None) or getattr(obj.user, "username", None) or obj.pk)
        return "Other actor (not selectable by AI)"
    return str(getattr(obj, "name", None) or getattr(obj, "ref_id", None) or obj.pk)


def validate_ratings(fields: dict[str, Any], assessment) -> dict[str, int]:
    """Never translate model's advisory high/medium labels to matrix indices."""
    selected = {name: fields[name] for name in SCORES if name in fields}
    if not selected:
        return {}
    matrix = assessment.risk_matrix.parse_json()
    for prefix in ("inherent", "current", "residual"):
        proba = selected.get(prefix + "_proba", -1)
        impact = selected.get(prefix + "_impact", -1)
        if (proba < 0) != (impact < 0):
            raise FullFieldValidationError("partial_risk_rating", f"{prefix} probability and impact must both be rated or both remain unrated.")
        if proba >= 0:
            if proba >= len(matrix.get("probability", [])) or impact >= len(matrix.get("impact", [])):
                raise FullFieldValidationError("invalid_risk_matrix_index", f"{prefix} rating is outside the selected assessment's risk matrix.")
            try:
                _ = matrix["grid"][proba][impact]
            except (IndexError, KeyError, TypeError):
                raise FullFieldValidationError("invalid_risk_matrix_grid", "The selected matrix does not define that probability-impact combination.")
    if any(value >= 0 for value in selected.values()):
        if not fields.get("reviewer_evidence_confirmed"):
            raise FullFieldValidationError("rating_not_supported", "Official risk ratings require explicit confirmation of evidence-based review.")
        if len((fields.get("justification") or "").strip()) < 20:
            raise FullFieldValidationError("rating_justification_required", "Add a specific evidence-based justification (at least 20 characters) before rating a risk.")
    return selected


def _get_record(user, model, uuid, folder, assessment, instance):
    if model is Actor:
        # Actor is global, not FolderMixin. Cross-company assignments must NOT be
        # inferred. Only the authenticated user's own Actor is accepted here.
        candidate = Actor.objects.filter(id=uuid, user=user).first()
    elif model is RiskScenario:
        candidate = RiskScenario.objects.filter(
            id=uuid, risk_assessment_id=assessment.id, folder_id=folder.id
        ).first()
    else:
        candidate = model.objects.filter(id=uuid, folder_id=folder.id).first()

    if candidate is None:
        raise FullFieldValidationError("record_out_of_scope", "A selected record is missing or outside this exact organizational folder/assessment.")
    if model is not Actor and not RoleAssignment.is_object_readable(user, model, candidate.id):
        raise FullFieldValidationError("record_not_readable", "A selected record is no longer readable by your account.")
    if model is RiskScenario:
        if instance and (candidate.pk == instance.pk or instance.pk in set(candidate.ancestors_plus_self().values_list("id", flat=True))):
            raise FullFieldValidationError("risk_cycle", "A risk cannot reference itself or create an antecedent cycle.")
    if model is Terminology and candidate.field_path != Terminology.FieldPath.QUALIFICATIONS:
        raise FullFieldValidationError("wrong_qualification_type", "The selected qualification is not a qualification term.")
    if model is AppliedControl and candidate.status not in list(AppliedControl.Status.values):
        raise FullFieldValidationError("invalid_control", "The selected control has an invalid status.")
    return candidate


def resolve_full_fields(user, fields: dict[str, Any], folder, assessment, existing=None) -> FullFieldPlan:
    """Fail closed for any unsupported relationship. No writes in this function."""
    plan = FullFieldPlan()
    if not fields:
        return plan
    unknown = set(fields) - set(COLLECTIONS) - set(SCORES) - set(OPTIONAL_TEXT) - set(SINGLE_RECORDS) - {
        "reviewed_treatment", "strength_of_knowledge", "reviewer_evidence_confirmed",
    }
    if unknown:
        raise FullFieldValidationError("unsupported_full_field", "Unsupported full-risk field: " + ", ".join(sorted(unknown)))

    for name, value in validate_ratings(fields, assessment).items():
        if value >= 0:
            plan.scalars[name] = value
    for name in OPTIONAL_TEXT:
        value = (fields.get(name) or "").strip()
        if value:
            if len(value) > 2000:
                raise FullFieldValidationError("text_too_long", f"{name} exceeds 2000 characters.")
            plan.scalars[name] = value
    if "strength_of_knowledge" in fields and fields["strength_of_knowledge"] >= 0:
        if fields["strength_of_knowledge"] not in (0, 1, 2):
            raise FullFieldValidationError("knowledge_out_of_range", "Unsupported knowledge strength.")
        plan.scalars["strength_of_knowledge"] = fields["strength_of_knowledge"]
    treatment = fields.get("reviewed_treatment", "open")
    if treatment not in TREATMENT_CHOICES:
        raise FullFieldValidationError("unsafe_treatment", "Treatment must be open, mitigate, avoid or transfer. Acceptance requires its separate approval workflow.")
    if treatment != "open":
        plan.scalars["treatment"] = treatment

    origin_id = fields.get("risk_origin_reference")
    if origin_id:
        origin = Terminology.objects.filter(id=origin_id, folder_id=folder.id,
            field_path=Terminology.FieldPath.ROTO_RISK_ORIGIN).first()
        if not origin or not RoleAssignment.is_object_readable(user, Terminology, origin.pk):
            raise FullFieldValidationError("invalid_risk_origin", "Risk origin must be an authorized origin term in the same folder.")
        plan.singles["risk_origin"] = origin

    operational_id = fields.get("operational_scenario_reference")
    if operational_id:
        model = apps.get_model("ebios_rm", "OperationalScenario")
        if not any(f.name == "folder" for f in model._meta.get_fields()):
            raise FullFieldValidationError("ebios_scope_unavailable", "The EBIOS scenario model has no direct folder scope; link it through the existing EBIOS workflow.")
        scenario = model.objects.filter(id=operational_id, folder_id=folder.id).first()
        if not scenario or not RoleAssignment.is_object_readable(user, model, scenario.pk):
            raise FullFieldValidationError("ebios_out_of_scope", "The referenced EBIOS scenario is not readable in this organization.")
        plan.singles["operational_scenario"] = scenario

    for request_name, (model, relationship) in COLLECTIONS.items():
        requested = fields.get(request_name) or []
        if len(requested) > 30 or len(requested) != len(set(requested)):
            raise FullFieldValidationError("duplicate_or_excessive_refs", f"Invalid number of {request_name} selections.")
        records = []
        for uuid in requested:
            target = _get_record(user, model, uuid, folder, assessment, existing)
            if request_name == "existing_control_references" and target.status != AppliedControl.Status.ACTIVE:
                raise FullFieldValidationError("unverified_existing_control", "Existing controls must have ACTIVE status in the platform.")
            records.append(target)
        if records:
            plan.collections[relationship] = records

    if existing is not None:
        # A prior AI risk can be completed; no human-written scalar or manual
        # relationship may ever be replaced or silently extended.
        for key, value in list(plan.scalars.items()):
            baseline = -1 if key in SCORES or key == "strength_of_knowledge" else ("open" if key == "treatment" else "")
            current = getattr(existing, key)
            if current not in (None, baseline, value):
                raise FullFieldValidationError("existing_value_preserved", f"Existing value for {key} must not be overwritten.")
            if current == value:
                del plan.scalars[key]
        for key, obj in list(plan.singles.items()):
            current_id = getattr(existing, f"{key}_id", None)
            if current_id and current_id != obj.pk:
                raise FullFieldValidationError("existing_link_preserved", f"Existing {key} must not be replaced.")
            if current_id == obj.pk:
                del plan.singles[key]
        for key, targets in list(plan.collections.items()):
            linked_ids = set(getattr(existing, key).values_list("id", flat=True))
            selected_ids = {obj.pk for obj in targets}
            if linked_ids and not selected_ids.issubset(linked_ids):
                raise FullFieldValidationError("existing_links_preserved", f"Existing {key} relationships cannot be changed by AI completion.")
            if selected_ids.issubset(linked_ids):
                del plan.collections[key]
    return plan


def apply_full_fields(instance: RiskScenario, plan: FullFieldPlan) -> None:
    """Must run inside the caller's approved atomic transaction after lock/recheck."""
    dirty = False
    for key, value in plan.scalars.items():
        if getattr(instance, key) != value:
            setattr(instance, key, value)
            dirty = True
    for key, item in plan.singles.items():
        if getattr(instance, key + "_id") != item.pk:
            setattr(instance, key, item)
            dirty = True
    if dirty:
        instance.save()  # model calculates official risk levels via its matrix
    for key, records in plan.collections.items():
        getattr(instance, key).add(*records)
