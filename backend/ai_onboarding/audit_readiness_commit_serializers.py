from __future__ import annotations

import uuid

from rest_framework import serializers

from .audit_readiness_suggestion_serializers import (
    MAX_READINESS_SCORE,
    MIN_READINESS_SCORE,
    READINESS_STATUS_CHOICES,
)


DECISION_CHOICES = ("create", "reuse", "reject", "defer")

REVIEW_STATUS_CHOICES = ("pending_review",)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 10B."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 10B."] for field in unknown_fields}
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


def _summary_list_field():
    return serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )


class AuditReadinessPayloadSerializer(StrictSerializer):
    """The reviewed Step 10A readiness summary carried into the deterministic write.

    Enum and range validation happens here so an unknown readiness_status, an out-of-range
    readiness_score or confidence, or a review_status other than pending_review is rejected
    before any planning or write work starts. Step 10B never edits these values.
    """

    temporary_id = serializers.CharField(max_length=64)
    readiness_status = serializers.ChoiceField(choices=READINESS_STATUS_CHOICES)
    readiness_score = serializers.IntegerField(
        min_value=MIN_READINESS_SCORE, max_value=MAX_READINESS_SCORE
    )
    summary = serializers.CharField(allow_blank=True)
    ready_items = _summary_list_field()
    missing_evidence = _summary_list_field()
    open_findings = _summary_list_field()
    open_risks = _summary_list_field()
    blocked_controls = _summary_list_field()
    recommended_next_steps = _summary_list_field()
    priority_actions = _summary_list_field()
    # Carried over from the Step 10A overall_confidence so the recorded note keeps the
    # advisory confidence it was reviewed at.
    confidence = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        summary = attrs.get("summary")
        attrs["summary"] = summary.strip() if isinstance(summary, str) else ""

        for field in (
            "ready_items",
            "missing_evidence",
            "open_findings",
            "open_risks",
            "blocked_controls",
            "recommended_next_steps",
            "priority_actions",
        ):
            entries = []
            for entry in attrs.get(field) or []:
                trimmed = entry.strip()
                if trimmed:
                    entries.append(trimmed)
            attrs[field] = entries

        return attrs


class AuditReadinessDecisionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    selected = serializers.BooleanField(required=True)
    decision = serializers.ChoiceField(choices=DECISION_CHOICES)
    existing_record_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    payload = AuditReadinessPayloadSerializer(required=False, allow_null=True)

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


class AiAuditReadinessCommitInputSerializer(StrictSerializer):
    dry_run = serializers.BooleanField(required=True)
    approved = serializers.BooleanField(required=True)
    folder_reference = serializers.CharField(required=True, max_length=64)
    assessment_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    decisions = AuditReadinessDecisionSerializer(many=True, allow_empty=False)

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
                        "approved must be false for a Step 10B dry-run; the dry-run never writes."
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
