from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
MAX_SCENARIO_TEXT_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
SOURCE_DRAFT_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

SAFE_NEXT_ACTIONS = (
    "accept_for_later_commit",
    "edit_before_commit",
    "reuse_existing_asset",
    "reject",
    "mark_as_evidence_candidate",
    "mark_as_control_candidate",
    "mark_as_vulnerability_candidate",
    "defer",
)

HUMAN_REVIEW_STATUS_CHOICES = (
    "pending_review",
    "review_required",
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
                        field: ["This field is not allowed in Step 3A."]
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
                        field: ["This field is not allowed in Step 3A."]
                        for field in unknown_fields
                    }
                )
        return attrs


class CaseSetupReferenceSerializer(StrictSerializer):
    folder_id = serializers.UUIDField(required=True)
    perimeter_id = serializers.UUIDField(required=True)
    compliance_assessment_id = serializers.UUIDField(required=True)
    risk_assessment_id = serializers.UUIDField(required=False, allow_null=True)


class AiAssetSuggestionInputSerializer(StrictSerializer):
    source_step1_draft_hash = serializers.CharField(required=True, max_length=71)
    case_setup_reference = CaseSetupReferenceSerializer(required=True)
    folder_id = serializers.UUIDField(required=False, allow_null=True)
    perimeter_id = serializers.UUIDField(required=False, allow_null=True)
    compliance_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    risk_assessment_id = serializers.UUIDField(required=False, allow_null=True)
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

    def validate_source_step1_draft_hash(self, value: str) -> str:
        normalized = value.strip()
        if not SOURCE_DRAFT_HASH_RE.match(normalized):
            raise serializers.ValidationError(
                "source_step1_draft_hash must be in the form 'sha256:<64 lowercase hex chars>'."
            )
        return normalized

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
        raw_locale = self.initial_data.get("user_locale") if hasattr(self, "initial_data") else None
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

        if not scenario_text and not scope_summary:
            raise serializers.ValidationError(
                {
                    "scenario_text": ["Provide scenario_text or scope_summary for Step 3A."],
                    "scope_summary": ["Provide scenario_text or scope_summary for Step 3A."],
                }
            )

        reference = attrs.get("case_setup_reference") or {}
        for field in ("folder_id", "perimeter_id", "compliance_assessment_id", "risk_assessment_id"):
            top_level_value = attrs.get(field)
            nested_value = reference.get(field)
            if top_level_value is None and nested_value is not None:
                attrs[field] = nested_value
            elif top_level_value is not None and nested_value is not None and str(top_level_value) != str(nested_value):
                raise serializers.ValidationError(
                    {field: [f"{field} must match case_setup_reference.{field} when both are provided."]}
                )

        missing = {}
        for field in ("folder_id", "perimeter_id", "compliance_assessment_id"):
            if attrs.get(field) is None:
                missing[field] = [f"{field} is required for Step 3A."]
        if missing:
            raise serializers.ValidationError(missing)

        if isinstance(raw_locale, str):
            normalized_raw = raw_locale.strip()
            if normalized_raw:
                if len(normalized_raw) == 5 and normalized_raw[2] == "-":
                    normalized_raw = f"{normalized_raw[:2].lower()}-{normalized_raw[3:].upper()}"
                else:
                    normalized_raw = normalized_raw.lower()
                attrs["_user_locale_fallback_applied"] = (
                    attrs.get("user_locale") == DEFAULT_USER_LOCALE
                    and normalized_raw != DEFAULT_USER_LOCALE
                    and not LOCALE_RE.match(normalized_raw)
                )
            else:
                attrs["_user_locale_fallback_applied"] = False
        else:
            attrs["_user_locale_fallback_applied"] = False
        return attrs


class SourceTextReferenceSerializer(StrictSerializer):
    ref_id = serializers.CharField(max_length=32)
    excerpt = serializers.CharField()
    char_start = serializers.IntegerField(min_value=0)
    char_end = serializers.IntegerField(min_value=0)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["char_end"] < attrs["char_start"]:
            raise serializers.ValidationError(
                "char_end must be greater than or equal to char_start"
            )
        return attrs


class WarningSerializer(StrictSerializer):
    code = serializers.CharField(max_length=64)
    message = serializers.CharField()
    affected_fields = serializers.ListField(
        child=serializers.CharField(max_length=128),
        allow_empty=True,
    )
    needs_review = serializers.BooleanField()


class BlockingQuestionSerializer(StrictSerializer):
    question_id = serializers.CharField(max_length=64)
    question_text = serializers.CharField()
    reason = serializers.CharField()
    affected_fields = serializers.ListField(
        child=serializers.CharField(max_length=128),
        allow_empty=False,
    )
    severity = serializers.ChoiceField(choices=("blocking",))


class ProposedAssetTypeSerializer(StrictSerializer):
    value = serializers.ChoiceField(choices=("PR", "SP"))
    label = serializers.CharField(max_length=32)


class CriticalitySerializer(StrictSerializer):
    value = serializers.CharField(max_length=32)
    is_platform_writable = serializers.BooleanField()
    mapping_note = serializers.CharField()


class AmbiguityFlagSerializer(StrictSerializer):
    code = serializers.CharField(max_length=64)
    message = serializers.CharField()


class CandidateAssetSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    proposed_name = serializers.CharField(max_length=200)
    proposed_description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    proposed_reference_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )
    proposed_asset_type = ProposedAssetTypeSerializer(required=False, allow_null=True)
    proposed_asset_category = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )
    criticality = CriticalitySerializer(required=False, allow_null=True)
    folder_id = serializers.UUIDField()
    perimeter_id = serializers.UUIDField(required=False, allow_null=True)
    compliance_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    source_text_references = SourceTextReferenceSerializer(many=True)
    rationale = serializers.CharField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    human_review_status = serializers.ChoiceField(choices=HUMAN_REVIEW_STATUS_CHOICES)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
    allowed_next_actions = serializers.ListField(
        child=serializers.ChoiceField(choices=SAFE_NEXT_ACTIONS),
        allow_empty=False,
    )


class DuplicateMatchSerializer(StrictSerializer):
    existing_asset_id = serializers.UUIDField()
    existing_name = serializers.CharField(max_length=200)
    existing_ref_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )
    existing_type = serializers.CharField(max_length=32)
    folder_id = serializers.UUIDField()
    folder_name = serializers.CharField(max_length=200)
    match_type = serializers.CharField(max_length=64)
    match_score = serializers.FloatField(min_value=0.0, max_value=1.0)
    scope_relevance = serializers.CharField(max_length=32)
    warning = serializers.CharField()


class DuplicateCandidateSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    proposed_name = serializers.CharField(max_length=200)
    matches = DuplicateMatchSerializer(many=True)
    recommended_human_action = serializers.CharField(max_length=64)


class AmbiguousCandidateSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    proposed_name = serializers.CharField(max_length=200)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
    recommended_actions = serializers.ListField(
        child=serializers.ChoiceField(choices=SAFE_NEXT_ACTIONS),
        allow_empty=False,
    )


class RejectedCandidateSerializer(StrictSerializer):
    source_label = serializers.CharField(max_length=200)
    recommended_reclassification = serializers.CharField(max_length=64)
    reason = serializers.CharField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)


class SourceSummarySerializer(StrictSerializer):
    detected_language = serializers.CharField(max_length=16)
    input_char_count = serializers.IntegerField(min_value=0)
    strict_mode_applied = serializers.BooleanField()
    scenario_excerpt = serializers.CharField()
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    folder_id = serializers.UUIDField()
    perimeter_id = serializers.UUIDField()
    compliance_assessment_id = serializers.UUIDField()
    risk_assessment_id = serializers.UUIDField(required=False, allow_null=True)
    parser_notes = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class AiAssetSuggestionDraftSerializer(StrictSerializer):
    draft_type = serializers.ChoiceField(choices=("AiAssetSuggestionDraft",))
    schema_version = serializers.CharField(max_length=32)
    source_summary = SourceSummarySerializer()
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    candidate_assets = CandidateAssetSerializer(many=True)
    duplicate_candidates = DuplicateCandidateSerializer(many=True)
    ambiguous_candidates = AmbiguousCandidateSerializer(many=True)
    rejected_candidates = RejectedCandidateSerializer(many=True)
    warnings = WarningSerializer(many=True)
    blocking_questions = BlockingQuestionSerializer(many=True)
    needs_human_review = serializers.BooleanField()
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    next_allowed_steps = serializers.ListField(
        child=serializers.CharField(max_length=128),
        allow_empty=True,
    )