from __future__ import annotations

import uuid

from rest_framework import serializers


DECISION_CHOICES = ("create", "reuse", "reject", "defer")

PRIORITY_CHOICES = (
    "low",
    "medium",
    "high",
    "critical",
)

REVIEW_STATUS_CHOICES = ("pending_review",)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 6B."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 6B."] for field in unknown_fields}
                )
        return attrs


def _normalized_uuid(value: str, field_name: str) -> str:
    candidate = (value or "").strip()
    try:
        return str(uuid.UUID(candidate))
    except (TypeError, ValueError):
        raise serializers.ValidationError(
            {field_name: [f"{field_name} must be a valid UUID."]}
        )


class RemediationActionPayloadSerializer(StrictSerializer):
    """The reviewed Step 6A remediation action carried into the deterministic write.

    Enum and range validation happens here so an invalid priority, an out-of-range
    confidence, or a review_status other than pending_review is rejected before any
    planning or write work starts.
    """

    temporary_id = serializers.CharField(max_length=64)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linked_finding_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    linked_finding_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    linked_asset_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    linked_asset_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    linked_control_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    linked_control_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)
    suggested_owner = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    target_timeline = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    success_criteria = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    required_follow_up_evidence = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    rationale = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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
            "linked_finding_reference",
            "linked_finding_title",
            "linked_asset_reference",
            "linked_asset_title",
            "linked_control_reference",
            "linked_control_title",
            "suggested_owner",
            "target_timeline",
            "rationale",
        ):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None

        for field in ("success_criteria", "required_follow_up_evidence"):
            entries = []
            for entry in attrs.get(field) or []:
                trimmed = entry.strip()
                if trimmed:
                    entries.append(trimmed)
            attrs[field] = entries

        return attrs


class RemediationActionDecisionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    selected = serializers.BooleanField(required=True)
    decision = serializers.ChoiceField(choices=DECISION_CHOICES)
    existing_record_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    payload = RemediationActionPayloadSerializer(required=False, allow_null=True)

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
            existing_reference = _normalized_uuid(
                existing_reference, "existing_record_reference"
            )

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


class AiRemediationActionCommitInputSerializer(StrictSerializer):
    dry_run = serializers.BooleanField(required=True)
    approved = serializers.BooleanField(required=True)
    folder_reference = serializers.CharField(required=True, max_length=64)
    decisions = RemediationActionDecisionSerializer(many=True, allow_empty=False)

    def validate_folder_reference(self, value):
        return _normalized_uuid(value, "folder_reference")

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
                        "approved must be false for a Step 6B dry-run; the dry-run never writes."
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
