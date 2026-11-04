from __future__ import annotations

import uuid

from rest_framework import serializers

from .risk_scenario_suggestion_serializers import (
    IMPACT_CHOICES,
    LIKELIHOOD_CHOICES,
    RISK_LEVEL_CHOICES,
)


DECISION_CHOICES = ("create", "reuse", "reject", "defer")

REVIEW_STATUS_CHOICES = ("pending_review",)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 8B."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 8B."] for field in unknown_fields}
                )
        return attrs


def _normalized_uuid(value: str, field_name: str) -> str:
    candidate = (value or "").strip()
    try:
        return str(uuid.UUID(candidate))
    except (TypeError, ValueError):
        raise serializers.ValidationError({field_name: [f"{field_name} must be a valid UUID."]})


def _optional_uuid(value, field_name: str) -> str | None:
    candidate = (value or "").strip() if isinstance(value, str) else value
    if not candidate:
        return None
    return _normalized_uuid(candidate, field_name)


# Human-reviewed actual platform fields. Unknown fields and identifiers fail closed.
# Score pairs are validated against the SELECTED assessment's risk matrix by
# the deterministic commit service, never by the AI's advisory label.
class ReviewedRiskFieldsSerializer(StrictSerializer):
    asset_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    owner_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    existing_control_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    extra_control_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    antecedent_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    qualification_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    exception_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    label_references = serializers.ListField(child=serializers.UUIDField(), required=False, max_length=30)
    risk_origin_reference = serializers.UUIDField(required=False, allow_null=True)
    operational_scenario_reference = serializers.UUIDField(required=False, allow_null=True)
    justification = serializers.CharField(required=False, allow_blank=True, max_length=2000)
    existing_controls = serializers.CharField(required=False, allow_blank=True, max_length=2000)
    reviewed_treatment = serializers.ChoiceField(required=False, choices=["open", "mitigate", "avoid", "transfer"])
    strength_of_knowledge = serializers.IntegerField(required=False, min_value=-1, max_value=2)
    reviewer_evidence_confirmed = serializers.BooleanField(required=False, default=False)
    inherent_proba = serializers.IntegerField(required=False, min_value=-1, max_value=20)
    inherent_impact = serializers.IntegerField(required=False, min_value=-1, max_value=20)
    current_proba = serializers.IntegerField(required=False, min_value=-1, max_value=20)
    current_impact = serializers.IntegerField(required=False, min_value=-1, max_value=20)
    residual_proba = serializers.IntegerField(required=False, min_value=-1, max_value=20)
    residual_impact = serializers.IntegerField(required=False, min_value=-1, max_value=20)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # DRF's UUIDField returns UUID objects; normalize to text for JSON
        # responses and for the service's immutable reference contract.
        for field in (
            "asset_references", "owner_references", "existing_control_references",
            "extra_control_references", "antecedent_references",
            "qualification_references", "exception_references", "label_references",
        ):
            if field in attrs:
                attrs[field] = [str(item) for item in attrs[field]]
        for key in ("risk_origin_reference", "operational_scenario_reference"):
            if attrs.get(key):
                attrs[key] = str(attrs[key])
        return attrs


class RiskScenarioPayloadSerializer(StrictSerializer):
    """The reviewed Step 8A risk scenario carried into the deterministic write.

    Enum and range validation happens here so an unknown likelihood/impact/risk_level, an
    out-of-range confidence, or a review_status other than pending_review is rejected
    before any planning or write work starts. Step 8B never edits these values.
    """

    temporary_id = serializers.CharField(max_length=64)
    reviewed_fields = ReviewedRiskFieldsSerializer(required=False)
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    asset_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    asset_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    linked_finding_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    linked_finding_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    linked_applied_control_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    linked_applied_control_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    linked_remediation_action_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    linked_remediation_action_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    linked_framework_control_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=255
    )
    linked_framework_control_code = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    linked_framework_control_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    threat = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    vulnerability = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    impact_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    likelihood = serializers.ChoiceField(choices=LIKELIHOOD_CHOICES)
    impact = serializers.ChoiceField(choices=IMPACT_CHOICES)
    risk_level = serializers.ChoiceField(choices=RISK_LEVEL_CHOICES)
    rationale = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recommended_next_steps = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        title = (attrs.get("title") or "").strip()
        if not title:
            raise serializers.ValidationError({"title": ["title must not be blank."]})
        attrs["title"] = title

        for field in (
            "description",
            "asset_reference",
            "asset_title",
            "linked_finding_reference",
            "linked_finding_title",
            "linked_applied_control_reference",
            "linked_applied_control_title",
            "linked_remediation_action_reference",
            "linked_remediation_action_title",
            "linked_framework_control_reference",
            "linked_framework_control_code",
            "linked_framework_control_title",
            "threat",
            "vulnerability",
            "impact_description",
            "rationale",
        ):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None

        entries = []
        for entry in attrs.get("recommended_next_steps") or []:
            trimmed = entry.strip()
            if trimmed:
                entries.append(trimmed)
        attrs["recommended_next_steps"] = entries

        return attrs


class RiskScenarioDecisionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    selected = serializers.BooleanField(required=True)
    decision = serializers.ChoiceField(choices=DECISION_CHOICES)
    existing_record_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    payload = RiskScenarioPayloadSerializer(required=False, allow_null=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        decision = attrs.get("decision")
        selected = attrs.get("selected")
        payload = attrs.get("payload")
        existing_reference = (attrs.get("existing_record_reference") or "").strip() or None

        if selected and decision == "create" and not payload:
            raise serializers.ValidationError(
                {"payload": ["payload is required when decision is create and selected is true."]}
            )

        if selected and decision == "reuse":
            if not existing_reference:
                raise serializers.ValidationError(
                    {
                        "existing_record_reference": [
                            "existing_record_reference is required when decision is reuse."
                        ]
                    }
                )
            existing_reference = _normalized_uuid(existing_reference, "existing_record_reference")

        if decision != "reuse":
            existing_reference = None
        attrs["existing_record_reference"] = existing_reference

        if payload and payload.get("temporary_id") != attrs.get("temporary_id"):
            raise serializers.ValidationError(
                {
                    "payload": {
                        "temporary_id": [
                            "payload.temporary_id must match the decision temporary_id."
                        ]
                    }
                }
            )

        return attrs


class AiRiskScenarioCommitInputSerializer(StrictSerializer):
    dry_run = serializers.BooleanField(required=True)
    approved = serializers.BooleanField(required=True)
    folder_reference = serializers.CharField(required=True, max_length=64)
    assessment_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    decisions = RiskScenarioDecisionSerializer(many=True, allow_empty=False)

    def validate_folder_reference(self, value):
        return _normalized_uuid(value, "folder_reference")

    def validate_assessment_reference(self, value):
        return _optional_uuid(value, "assessment_reference")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        dry_run = attrs.get("dry_run")
        approved = attrs.get("approved")

        if not dry_run and not approved:
            raise serializers.ValidationError(
                {"approved": ["approved must be true when dry_run is false."]}
            )

        if dry_run and approved:
            raise serializers.ValidationError(
                {
                    "approved": [
                        "approved must be false for a Step 8B dry-run; the dry-run never writes."
                    ]
                }
            )

        duplicate_ids = _duplicate_temporary_ids(attrs.get("decisions") or [])
        if duplicate_ids:
            raise serializers.ValidationError(
                {
                    "decisions": [
                        "Each decision temporary_id must be unique: "
                        f"{', '.join(sorted(duplicate_ids))}."
                    ]
                }
            )

        return attrs


def _duplicate_temporary_ids(decisions: list[dict]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for decision in decisions:
        temporary_id = decision.get("temporary_id")
        if temporary_id in seen:
            duplicates.add(temporary_id)
        seen.add(temporary_id)
    return duplicates
