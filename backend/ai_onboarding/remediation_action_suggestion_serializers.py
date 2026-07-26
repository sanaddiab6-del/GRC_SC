from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
MAX_CASE_SUMMARY_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")

ADVISORY_NOTICE = (
    "AI suggestions only. No remediation records are created in Step 6A."
)

REVIEW_STATUS_CHOICES = ("pending_review",)

PRIORITY_CHOICES = (
    "low",
    "medium",
    "high",
    "critical",
)

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
    "local_provider_error_blocked",
)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {
                        field: ["This field is not allowed in Step 6A."]
                        for field in unknown_fields
                    }
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {
                        field: ["This field is not allowed in Step 6A."]
                        for field in unknown_fields
                    }
                )
        return attrs


class FolderReferenceSerializer(StrictSerializer):
    """Optional, advisory-only folder pointer.

    Step 6A performs no database reads or writes, so the folder reference is carried
    as readable context only and is never resolved against the database.
    """

    folder_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=64,
    )
    folder_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=200,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        for field in ("folder_id", "folder_name"):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None
        return attrs


class ContextItemSerializer(StrictSerializer):
    """Readable context row for assets, controls, evidence, questions, and findings.

    Every field except ``title`` is optional so the demo is never blocked by a
    missing reference id.
    """

    reference = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=200,
    )
    title = serializers.CharField(required=True, max_length=500)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=5000,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["title"] = attrs["title"].strip()
        for field in ("reference", "description"):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None
        return attrs


class AiRemediationActionSuggestionInputSerializer(StrictSerializer):
    case_summary = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=MAX_CASE_SUMMARY_LENGTH,
    )
    scenario_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )
    folder_reference = FolderReferenceSerializer(required=False, allow_null=True)
    assets = ContextItemSerializer(many=True, required=False, allow_empty=True)
    applied_controls = ContextItemSerializer(many=True, required=False, allow_empty=True)
    evidence_requests = ContextItemSerializer(many=True, required=False, allow_empty=True)
    audit_questions = ContextItemSerializer(many=True, required=False, allow_empty=True)
    preliminary_findings = ContextItemSerializer(many=True, required=False, allow_empty=True)
    known_weaknesses = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
    )
    framework_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=200,
    )
    assessment_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=200,
    )
    user_locale = serializers.CharField(
        required=False,
        allow_blank=True,
        default=DEFAULT_USER_LOCALE,
        max_length=16,
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

        for field in ("framework_name", "assessment_name"):
            value = attrs.get(field)
            attrs[field] = value.strip() or None if isinstance(value, str) else value

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
        child=serializers.CharField(max_length=128),
        allow_empty=True,
    )
    needs_review = serializers.BooleanField()


class RemediationActionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    linked_finding_reference = serializers.CharField(allow_blank=True, max_length=200)
    linked_finding_title = serializers.CharField(allow_blank=True, max_length=500)
    linked_asset_reference = serializers.CharField(allow_blank=True, max_length=200)
    linked_asset_title = serializers.CharField(allow_blank=True, max_length=500)
    linked_control_reference = serializers.CharField(allow_blank=True, max_length=200)
    linked_control_title = serializers.CharField(allow_blank=True, max_length=500)
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)
    suggested_owner = serializers.CharField(max_length=200)
    target_timeline = serializers.CharField(max_length=200)
    success_criteria = serializers.ListField(
        child=serializers.CharField(max_length=500),
        allow_empty=True,
    )
    required_follow_up_evidence = serializers.ListField(
        child=serializers.CharField(max_length=500),
        allow_empty=True,
    )
    rationale = serializers.CharField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)


class AiRemediationActionSuggestionDraftSerializer(StrictSerializer):
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    remediation_actions = RemediationActionSerializer(many=True)
    warnings = WarningSerializer(many=True)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
