from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
MAX_CASE_SUMMARY_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")

ADVISORY_NOTICE = (
    "AI suggestions only. Step 10A never marks an assessment ready, never closes anything, "
    "and never certifies compliance."
)

REVIEW_STATUS_CHOICES = ("pending_review",)

READINESS_STATUS_CHOICES = (
    "ready",
    "partially_ready",
    "not_ready",
    "blocked",
    "needs_more_evidence",
)

MIN_READINESS_SCORE = 0
MAX_READINESS_SCORE = 100

# Keeps the advisory summary short enough to stay reviewable and inside the local model's
# timeout.
MAX_SUMMARY_LIST_ITEMS = 10

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
    "local_provider_error_blocked",
    # Step 10A refuses to run the model when there is no reviewed onboarding context.
    "readiness_context_missing_blocked",
)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 10A."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 10A."] for field in unknown_fields}
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


class ContextItemSerializer(StrictSerializer):
    """Readable context row carried over from the earlier onboarding steps."""

    reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=255
    )
    title = serializers.CharField(required=True, max_length=500)
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=5000
    )
    status = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["title"] = attrs["title"].strip()
        return _strip_optional(attrs, ("reference", "description", "status"))


class AiAuditReadinessSuggestionInputSerializer(StrictSerializer):
    case_summary = serializers.CharField(
        required=False, allow_blank=True, max_length=MAX_CASE_SUMMARY_LENGTH
    )
    scenario_name = serializers.CharField(required=False, allow_blank=True, max_length=500)
    folder_reference = FolderReferenceSerializer(required=False, allow_null=True)
    assessment_reference = AssessmentReferenceSerializer(required=False, allow_null=True)
    assets = ContextItemSerializer(many=True, required=False, allow_empty=True)
    applied_controls = ContextItemSerializer(many=True, required=False, allow_empty=True)
    evidence_requests = ContextItemSerializer(many=True, required=False, allow_empty=True)
    audit_questions = ContextItemSerializer(many=True, required=False, allow_empty=True)
    preliminary_findings = ContextItemSerializer(many=True, required=False, allow_empty=True)
    remediation_actions = ContextItemSerializer(many=True, required=False, allow_empty=True)
    framework_mappings = ContextItemSerializer(many=True, required=False, allow_empty=True)
    risk_scenarios = ContextItemSerializer(many=True, required=False, allow_empty=True)
    control_effectiveness_suggestions = ContextItemSerializer(
        many=True, required=False, allow_empty=True
    )
    known_weaknesses = serializers.ListField(
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

        known_weaknesses = []
        for item in attrs.get("known_weaknesses") or []:
            trimmed = item.strip()
            if trimmed:
                known_weaknesses.append(trimmed)
        attrs["known_weaknesses"] = known_weaknesses

        for field in (
            "assets",
            "applied_controls",
            "evidence_requests",
            "audit_questions",
            "preliminary_findings",
            "remediation_actions",
            "framework_mappings",
            "risk_scenarios",
            "control_effectiveness_suggestions",
        ):
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


class AiAuditReadinessSuggestionDraftSerializer(StrictSerializer):
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
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
    warnings = WarningSerializer(many=True)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)
