from __future__ import annotations

import uuid

from rest_framework import serializers

from .audit_report_suggestion_serializers import (
    MAX_LIST_ITEMS,
    MAX_REPORT_SECTIONS,
    MAX_SECTION_CONTENT_LENGTH,
)


DECISION_CHOICES = ("create", "reuse", "reject", "defer")

REVIEW_STATUS_CHOICES = ("pending_review",)

MAX_REPORT_NAME_LENGTH = 200


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 11B."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 11B."] for field in unknown_fields}
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


class ReportSectionPayloadSerializer(StrictSerializer):
    heading = serializers.CharField(max_length=200)
    content = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=MAX_SECTION_CONTENT_LENGTH
    )
    source_items = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["heading"] = (attrs.get("heading") or "").strip()
        if not attrs["heading"]:
            raise serializers.ValidationError({"heading": ["heading must not be blank."]})
        content = attrs.get("content")
        attrs["content"] = content.strip() if isinstance(content, str) else ""
        entries = []
        for entry in attrs.get("source_items") or []:
            trimmed = entry.strip()
            if trimmed:
                entries.append(trimmed)
        attrs["source_items"] = entries
        return attrs


class AuditReportPayloadSerializer(StrictSerializer):
    """The reviewed Step 11A report draft carried into the deterministic write.

    Range validation happens here so an out-of-range section confidence or a review_status
    other than pending_review is rejected before any planning or write work starts.
    Step 11B never edits these values.
    """

    temporary_id = serializers.CharField(max_length=64)
    report_title = serializers.CharField(max_length=300)
    executive_summary = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    report_sections = ReportSectionPayloadSerializer(
        many=True, required=False, allow_empty=True, max_length=MAX_REPORT_SECTIONS
    )
    limitations = serializers.ListField(
        child=serializers.CharField(max_length=1000),
        required=True,
        allow_empty=False,
        max_length=MAX_LIST_ITEMS,
    )
    recommended_next_steps = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    # Carried over from the Step 11A overall_confidence so the saved draft keeps the
    # advisory confidence it was reviewed at.
    confidence = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        title = (attrs.get("report_title") or "").strip()
        if not title:
            raise serializers.ValidationError(
                {"report_title": ["report_title must not be blank."]}
            )
        attrs["report_title"] = title

        executive_summary = attrs.get("executive_summary")
        attrs["executive_summary"] = (
            executive_summary.strip() if isinstance(executive_summary, str) else ""
        )

        for field in ("limitations", "recommended_next_steps"):
            entries = []
            for entry in attrs.get(field) or []:
                trimmed = entry.strip()
                if trimmed:
                    entries.append(trimmed)
            attrs[field] = entries

        if not attrs["limitations"]:
            raise serializers.ValidationError(
                {
                    "limitations": [
                        "limitations must not be empty: the saved draft must carry its own "
                        "limitations."
                    ]
                }
            )

        return attrs


class AuditReportDecisionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    selected = serializers.BooleanField(required=True)
    decision = serializers.ChoiceField(choices=DECISION_CHOICES)
    existing_record_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    payload = AuditReportPayloadSerializer(required=False, allow_null=True)

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


class AiAuditReportCommitInputSerializer(StrictSerializer):
    dry_run = serializers.BooleanField(required=True)
    approved = serializers.BooleanField(required=True)
    folder_reference = serializers.CharField(required=True, max_length=64)
    assessment_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    decisions = AuditReportDecisionSerializer(many=True, allow_empty=False)

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
                        "approved must be false for a Step 11B dry-run; the dry-run never writes."
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
