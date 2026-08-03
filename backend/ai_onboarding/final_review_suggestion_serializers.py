from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
MAX_CASE_SUMMARY_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")

ADVISORY_NOTICE = (
    "AI summary only. Step 12A never marks the workflow complete, never closes an audit, "
    "and never certifies compliance."
)

REVIEW_STATUS_CHOICES = ("pending_review",)

DEMO_READINESS_STATUS_CHOICES = ("ready", "partially_ready", "not_ready", "blocked")

# Keeps the advisory summary short enough to stay reviewable and inside the local model's
# timeout.
MAX_SUMMARY_LIST_ITEMS = 20

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
    "local_provider_error_blocked",
    # Step 12A refuses to run the model when there is no recorded flow outcome to review.
    "final_review_context_missing_blocked",
)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 12A."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 12A."] for field in unknown_fields}
                )
        return attrs


def _strip_optional(attrs: dict, fields: tuple[str, ...]) -> dict:
    for field in fields:
        value = attrs.get(field)
        if isinstance(value, str):
            attrs[field] = value.strip() or None
    return attrs


class FolderReferenceSerializer(StrictSerializer):
    """Optional, advisory-only folder pointer carried as readable context."""

    folder_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    folder_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )

    def validate(self, attrs):
        return _strip_optional(super().validate(attrs), ("folder_id", "folder_name"))


class AssessmentReferenceSerializer(StrictSerializer):
    """Optional, advisory-only assessment pointer carried as readable context."""

    assessment_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    assessment_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )

    def validate(self, attrs):
        return _strip_optional(super().validate(attrs), ("assessment_id", "assessment_name"))


class StepOutcomeSerializer(StrictSerializer):
    """What one onboarding step actually produced, as reported by the caller."""

    step = serializers.CharField(required=True, max_length=64)
    status = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    detail = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=2000
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["step"] = attrs["step"].strip()
        return _strip_optional(attrs, ("status", "detail"))


class RecordSummarySerializer(StrictSerializer):
    """A record the commit steps created or reused, carried read-only as context."""

    record_type = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    name = serializers.CharField(required=True, max_length=500)
    action = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["name"] = attrs["name"].strip()
        return _strip_optional(attrs, ("record_type", "action"))


class AiFinalReviewSuggestionInputSerializer(StrictSerializer):
    case_summary = serializers.CharField(
        required=False, allow_blank=True, max_length=MAX_CASE_SUMMARY_LENGTH
    )
    scenario_name = serializers.CharField(required=False, allow_blank=True, max_length=500)
    folder_reference = FolderReferenceSerializer(required=False, allow_null=True)
    assessment_reference = AssessmentReferenceSerializer(required=False, allow_null=True)
    step_outcomes = StepOutcomeSerializer(many=True, required=False, allow_empty=True)
    created_records = RecordSummarySerializer(many=True, required=False, allow_empty=True)
    reused_records = RecordSummarySerializer(many=True, required=False, allow_empty=True)
    blocked_items = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    outstanding_items = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    user_locale = serializers.CharField(
        required=False, allow_blank=True, default=DEFAULT_USER_LOCALE, max_length=16
    )
    strict_mode = serializers.BooleanField(required=False, default=True)

    def validate_user_locale(self, value: str) -> str:
        normalized = (value or DEFAULT_USER_LOCALE).strip()
        if not normalized:
            return DEFAULT_USER_LOCALE
        if len(normalized) == 5 and normalized[2] == "-":
            normalized = f"{normalized[:2].lower()}-{normalized[3:].upper()}"
        else:
            normalized = normalized.lower()
        if not LOCALE_RE.match(normalized):
            return DEFAULT_USER_LOCALE
        return normalized

    def validate(self, attrs):
        attrs = super().validate(attrs)

        attrs["case_summary"] = (attrs.get("case_summary") or "").strip()
        attrs["scenario_name"] = (attrs.get("scenario_name") or "").strip()

        for field in ("blocked_items", "outstanding_items"):
            entries = []
            for item in attrs.get(field) or []:
                trimmed = item.strip()
                if trimmed:
                    entries.append(trimmed)
            attrs[field] = entries

        for field in ("step_outcomes", "created_records", "reused_records"):
            attrs[field] = list(attrs.get(field) or [])

        return attrs


class AmbiguityFlagSerializer(StrictSerializer):
    code = serializers.CharField(max_length=64)
    message = serializers.CharField()


class WarningSerializer(StrictSerializer):
    code = serializers.CharField(max_length=64)
    message = serializers.CharField()
    affected_fields = serializers.ListField(
        child=serializers.CharField(max_length=128), allow_empty=True
    )
    needs_review = serializers.BooleanField()


def _summary_list_field():
    return serializers.ListField(
        child=serializers.CharField(max_length=500), allow_empty=True
    )


class AiFinalReviewSuggestionDraftSerializer(StrictSerializer):
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    completion_summary = serializers.CharField(allow_blank=True)
    completed_steps = _summary_list_field()
    incomplete_steps = _summary_list_field()
    created_or_reused_records_summary = _summary_list_field()
    blocked_items = _summary_list_field()
    human_review_required = _summary_list_field()
    recommended_next_steps = _summary_list_field()
    demo_readiness_status = serializers.ChoiceField(choices=DEMO_READINESS_STATUS_CHOICES)
    warnings = WarningSerializer(many=True)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)
