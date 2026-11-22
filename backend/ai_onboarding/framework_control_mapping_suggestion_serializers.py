from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
MAX_CASE_SUMMARY_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")

ADVISORY_NOTICE = (
    "AI suggestions only. No framework controls and no mappings are created in Step 7A."
)

REVIEW_STATUS_CHOICES = ("pending_review",)

# Step 7A asks for a short, reviewable set of mappings rather than an exhaustive matrix.
# Keeping the answer small is also what keeps the local model inside its timeout.
MAX_FRAMEWORK_CONTROL_MAPPINGS = 5

MAPPING_TYPE_CHOICES = (
    "supports_finding",
    "supports_applied_control",
    "supports_remediation",
    "compliance_gap_mapping",
    "evidence_mapping",
)

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
    "local_provider_error_blocked",
    # Step 7A refuses to run the model when there is nothing safe to map against.
    "candidate_controls_missing_blocked",
)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {
                        field: ["This field is not allowed in Step 7A."]
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
                        field: ["This field is not allowed in Step 7A."]
                        for field in unknown_fields
                    }
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


class FrameworkReferenceSerializer(StrictSerializer):
    """Optional pointer used for safe read-only candidate control discovery."""

    framework_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    framework_urn = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=255
    )
    framework_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )

    def validate(self, attrs):
        return _strip_optional(
            super().validate(attrs), ("framework_id", "framework_urn", "framework_name")
        )


class LoadedLibraryReferenceSerializer(StrictSerializer):
    """Optional pointer to an already loaded library, read-only."""

    library_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    library_urn = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=255
    )
    library_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )

    def validate(self, attrs):
        return _strip_optional(
            super().validate(attrs), ("library_id", "library_urn", "library_name")
        )


class ContextItemSerializer(StrictSerializer):
    """Readable context row for assets, controls, remediation, evidence, and findings."""

    reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    title = serializers.CharField(required=True, max_length=500)
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=5000
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["title"] = attrs["title"].strip()
        return _strip_optional(attrs, ("reference", "description"))


class CandidateFrameworkControlSerializer(StrictSerializer):
    """An existing framework control the caller already has.

    Step 7A never creates framework controls: this list (plus any safe read-only
    discovery) is the only set the AI is allowed to map to.
    """

    reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=255
    )
    code = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    title = serializers.CharField(required=True, max_length=500)
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=5000
    )
    domain = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    section = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    source = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["title"] = attrs["title"].strip()
        attrs = _strip_optional(
            attrs, ("reference", "code", "description", "domain", "section", "source")
        )
        if not attrs["title"]:
            raise serializers.ValidationError(
                {"title": ["A candidate framework control requires a readable title."]}
            )
        return attrs


class AiFrameworkControlMappingSuggestionInputSerializer(StrictSerializer):
    case_summary = serializers.CharField(
        required=False, allow_blank=True, max_length=MAX_CASE_SUMMARY_LENGTH
    )
    scenario_name = serializers.CharField(required=False, allow_blank=True, max_length=500)
    folder_reference = FolderReferenceSerializer(required=False, allow_null=True)
    framework_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    assessment_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    loaded_library_reference = LoadedLibraryReferenceSerializer(
        required=False, allow_null=True
    )
    framework_reference = FrameworkReferenceSerializer(required=False, allow_null=True)
    assets = ContextItemSerializer(many=True, required=False, allow_empty=True)
    applied_controls = ContextItemSerializer(many=True, required=False, allow_empty=True)
    remediation_actions = ContextItemSerializer(many=True, required=False, allow_empty=True)
    evidence_requests = ContextItemSerializer(many=True, required=False, allow_empty=True)
    audit_questions = ContextItemSerializer(many=True, required=False, allow_empty=True)
    preliminary_findings = ContextItemSerializer(many=True, required=False, allow_empty=True)
    known_weaknesses = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    candidate_framework_controls = CandidateFrameworkControlSerializer(
        many=True, required=False, allow_empty=True
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
            "remediation_actions",
            "evidence_requests",
            "audit_questions",
            "preliminary_findings",
            "candidate_framework_controls",
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


class FrameworkControlMappingSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    framework_control_reference = serializers.CharField(max_length=255)
    framework_control_code = serializers.CharField(allow_blank=True, max_length=200)
    framework_control_title = serializers.CharField(max_length=500)
    framework_control_description = serializers.CharField(allow_blank=True)
    framework_name = serializers.CharField(allow_blank=True, max_length=200)
    mapping_type = serializers.ChoiceField(choices=MAPPING_TYPE_CHOICES)
    linked_finding_reference = serializers.CharField(allow_blank=True, max_length=200)
    linked_finding_title = serializers.CharField(allow_blank=True, max_length=500)
    linked_applied_control_reference = serializers.CharField(allow_blank=True, max_length=200)
    linked_applied_control_title = serializers.CharField(allow_blank=True, max_length=500)
    linked_remediation_action_reference = serializers.CharField(
        allow_blank=True, max_length=200
    )
    linked_remediation_action_title = serializers.CharField(allow_blank=True, max_length=500)
    rationale = serializers.CharField()
    evidence_needed = serializers.ListField(
        child=serializers.CharField(max_length=500), allow_empty=True
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)


class AiFrameworkControlMappingSuggestionDraftSerializer(StrictSerializer):
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    framework_control_mappings = FrameworkControlMappingSerializer(many=True)
    warnings = WarningSerializer(many=True)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
