from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
DRAFT_TYPE = "AiEvidenceFindingSuggestionDraft"
MAX_SCENARIO_TEXT_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
SOURCE_DRAFT_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

ADVISORY_NOTICE = (
    "AI suggestions only. No findings or evidence records are created in Step 5A."
)

REVIEW_STATUS_CHOICES = ("pending_review",)

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
                        field: ["This field is not allowed in Step 5A."]
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
                        field: ["This field is not allowed in Step 5A."]
                        for field in unknown_fields
                    }
                )
        return attrs


class CaseSetupReferenceSerializer(StrictSerializer):
    folder_id = serializers.UUIDField(required=True)
    perimeter_id = serializers.UUIDField(required=False, allow_null=True)
    compliance_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    risk_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    selected_framework_id = serializers.UUIDField(required=False, allow_null=True)


class AssetReferenceSerializer(StrictSerializer):
    asset_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, max_length=200)
    ref_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )
    asset_class = serializers.UUIDField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=("PR", "SP"), required=False, allow_null=True)
    source_temporary_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=64,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["name"] = attrs["name"].strip()
        for field in ("ref_id", "source_temporary_id"):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None
        return attrs


class AppliedControlReferenceSerializer(StrictSerializer):
    applied_control_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, max_length=200)
    ref_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )
    category = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=64,
    )
    status = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=64,
    )
    source_temporary_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=64,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["name"] = attrs["name"].strip()
        for field in ("ref_id", "category", "status", "source_temporary_id"):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None
        return attrs


class AiEvidenceFindingSuggestionInputSerializer(StrictSerializer):
    source_step1_draft_hash = serializers.CharField(required=True, max_length=71)
    source_asset_commit_hash = serializers.CharField(required=True, max_length=71)
    source_applied_control_draft_hash = serializers.CharField(required=True, max_length=71)
    source_applied_control_commit_hash = serializers.CharField(required=True, max_length=71)
    case_setup_reference = CaseSetupReferenceSerializer(required=True)
    asset_references = AssetReferenceSerializer(many=True, allow_empty=False)
    applied_control_references = AppliedControlReferenceSerializer(many=True, allow_empty=False)
    scenario_text = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=MAX_SCENARIO_TEXT_LENGTH,
    )
    scope_summary = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )
    known_weaknesses = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
    )
    selected_framework_id = serializers.UUIDField(required=False, allow_null=True)
    user_locale = serializers.CharField(
        required=False,
        allow_blank=True,
        default=DEFAULT_USER_LOCALE,
        max_length=16,
    )
    strict_mode = serializers.BooleanField(required=False, default=True)

    def _validate_hash(self, value: str, field_name: str) -> str:
        normalized = (value or "").strip()
        if not SOURCE_DRAFT_HASH_RE.match(normalized):
            raise serializers.ValidationError(
                f"{field_name} must be in the form 'sha256:<64 lowercase hex chars>'."
            )
        return normalized

    def validate_source_step1_draft_hash(self, value: str) -> str:
        return self._validate_hash(value, "source_step1_draft_hash")

    def validate_source_asset_commit_hash(self, value: str) -> str:
        return self._validate_hash(value, "source_asset_commit_hash")

    def validate_source_applied_control_draft_hash(self, value: str) -> str:
        return self._validate_hash(value, "source_applied_control_draft_hash")

    def validate_source_applied_control_commit_hash(self, value: str) -> str:
        return self._validate_hash(value, "source_applied_control_commit_hash")

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

        scenario_text = (attrs.get("scenario_text") or "").strip()
        scope_summary = (attrs.get("scope_summary") or "").strip()
        known_weaknesses = []
        for item in attrs.get("known_weaknesses") or []:
            trimmed = item.strip()
            if trimmed:
                known_weaknesses.append(trimmed)

        attrs["scenario_text"] = scenario_text
        attrs["scope_summary"] = scope_summary
        attrs["known_weaknesses"] = known_weaknesses

        if not attrs.get("asset_references"):
            raise serializers.ValidationError(
                {"asset_references": ["asset_references must not be empty for Step 5A."]}
            )

        if not attrs.get("applied_control_references"):
            raise serializers.ValidationError(
                {
                    "applied_control_references": [
                        "applied_control_references must not be empty for Step 5A."
                    ]
                }
            )

        reference = attrs.get("case_setup_reference") or {}
        top_level_framework_id = attrs.get("selected_framework_id")
        nested_framework_id = reference.get("selected_framework_id")
        if top_level_framework_id is None and nested_framework_id is not None:
            attrs["selected_framework_id"] = nested_framework_id
        elif (
            top_level_framework_id is not None
            and nested_framework_id is not None
            and str(top_level_framework_id) != str(nested_framework_id)
        ):
            raise serializers.ValidationError(
                {
                    "selected_framework_id": [
                        "selected_framework_id must match case_setup_reference.selected_framework_id when both are provided."
                    ]
                }
            )

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


class EvidenceRequestSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linked_asset_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)
    linked_applied_control_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=True
    )
    rationale = serializers.CharField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)


class AuditQuestionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    question_text = serializers.CharField()
    rationale = serializers.CharField()
    linked_asset_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)
    linked_applied_control_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=True
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)


class PreliminaryFindingSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    title = serializers.CharField(max_length=200)
    summary = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    severity = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=32)
    rationale = serializers.CharField()
    linked_asset_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)
    linked_applied_control_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=True
    )
    related_weaknesses = serializers.ListField(
        child=serializers.CharField(max_length=500),
        allow_empty=True,
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)


class SourceSummarySerializer(StrictSerializer):
    detected_language = serializers.CharField(max_length=16)
    input_char_count = serializers.IntegerField(min_value=0)
    strict_mode_applied = serializers.BooleanField()
    scenario_excerpt = serializers.CharField(allow_blank=True)
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    folder_id = serializers.UUIDField()
    perimeter_id = serializers.UUIDField(required=False, allow_null=True)
    compliance_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    risk_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    selected_framework_id = serializers.UUIDField(required=False, allow_null=True)
    asset_count = serializers.IntegerField(min_value=0)
    applied_control_count = serializers.IntegerField(min_value=0)
    parser_notes = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class AiEvidenceFindingSuggestionDraftSerializer(StrictSerializer):
    draft_type = serializers.ChoiceField(choices=(DRAFT_TYPE,))
    schema_version = serializers.CharField(max_length=32)
    advisory_notice = serializers.CharField()
    no_write = serializers.BooleanField()
    source_summary = SourceSummarySerializer()
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    evidence_requests = EvidenceRequestSerializer(many=True)
    audit_questions = AuditQuestionSerializer(many=True)
    preliminary_findings = PreliminaryFindingSerializer(many=True)
    warnings = WarningSerializer(many=True)
    needs_human_review = serializers.BooleanField()
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)
    next_allowed_steps = serializers.ListField(
        child=serializers.CharField(max_length=128),
        allow_empty=True,
    )
