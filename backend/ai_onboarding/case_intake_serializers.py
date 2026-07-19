from __future__ import annotations

import re

from rest_framework import serializers


MAX_SCENARIO_TEXT_LENGTH = 20_000
SCHEMA_VERSION = "0.2.0"
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")

CANONICAL_PLATFORM_ENTITIES = (
    "Folder",
    "Perimeter",
    "ComplianceAssessment",
    "RequirementNode",
    "RequirementAssessment",
    "Asset",
    "AppliedControl",
    "Evidence",
    "EvidenceRevision",
    "Vulnerability",
    "Threat",
    "RiskAssessment",
    "RiskScenario",
    "Finding",
    "FindingsAssessment",
    "RiskAcceptance",
    "ValidationFlow",
    "StoredLibrary",
    "LoadedLibrary",
    "Framework",
    "WorkflowCase",
)

PROHIBITED_STEP1_REQUEST_FIELDS = {
    "compliance_result",
    "final_compliance_result",
    "audit_closure",
    "close_audit",
    "risk_acceptance",
    "risk_decision",
    "create_now",
    "auto_create",
}


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {
                        field: ["This field is not allowed in Step 1."]
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
                        field: ["This field is not allowed in Step 1."]
                        for field in unknown_fields
                    }
                )
        return attrs


class AssessmentPeriodInputSerializer(StrictSerializer):
    label = serializers.CharField(required=False, allow_blank=True, max_length=255)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "assessment_period.end_date must be on or after assessment_period.start_date"
            )
        return attrs


class AiCaseIntakeInputSerializer(StrictSerializer):
    scenario_text = serializers.CharField(max_length=MAX_SCENARIO_TEXT_LENGTH)
    preferred_framework = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    assessment_period = AssessmentPeriodInputSerializer(required=False, allow_null=True)
    organization_hint = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    scope_hint = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=2000,
    )
    known_deadline = serializers.DateField(required=False, allow_null=True)
    known_trigger = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    user_locale = serializers.CharField(
        required=False,
        allow_blank=True,
        default=DEFAULT_USER_LOCALE,
        max_length=16,
    )
    strict_mode = serializers.BooleanField(required=False, default=True)

    def validate_scenario_text(self, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("This field may not be blank.")
        return trimmed

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
        if isinstance(self.initial_data, dict):
            prohibited = sorted(
                field for field in PROHIBITED_STEP1_REQUEST_FIELDS if field in self.initial_data
            )
            if prohibited:
                raise serializers.ValidationError(
                    {
                        field: ["This field is not allowed in Step 1."]
                        for field in prohibited
                    }
                )

        raw_locale = self.initial_data.get("user_locale") if hasattr(self, "initial_data") else None
        for field in (
            "preferred_framework",
            "organization_hint",
            "scope_hint",
            "known_trigger",
        ):
            value = attrs.get(field)
            if isinstance(value, str):
                trimmed = value.strip()
                attrs[field] = trimmed or None
        assessment_period = attrs.get("assessment_period")
        if assessment_period and not any(assessment_period.values()):
            attrs["assessment_period"] = None
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


class SourceTextRefSerializer(serializers.Serializer):
    ref_id = serializers.CharField(max_length=32)
    excerpt = serializers.CharField()
    char_start = serializers.IntegerField(min_value=0)
    char_end = serializers.IntegerField(min_value=0)

    def validate(self, attrs):
        if attrs["char_end"] < attrs["char_start"]:
            raise serializers.ValidationError("char_end must be greater than or equal to char_start")
        return attrs


class WarningSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64)
    message = serializers.CharField()
    affected_fields = serializers.ListField(
        child=serializers.CharField(max_length=128),
        allow_empty=True,
    )
    needs_review = serializers.BooleanField()


class BlockingQuestionSerializer(serializers.Serializer):
    question_id = serializers.CharField(max_length=64)
    question_text = serializers.CharField()
    reason = serializers.CharField()
    affected_fields = serializers.ListField(
        child=serializers.CharField(max_length=128),
        allow_empty=False,
    )
    severity = serializers.ChoiceField(choices=("blocking",))


class CanonicalMappingSerializer(serializers.Serializer):
    business_term = serializers.CharField(max_length=128)
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    api_endpoint = serializers.CharField(max_length=255)
    note = serializers.CharField()


class SourceSummarySerializer(serializers.Serializer):
    detected_language = serializers.CharField(max_length=16)
    input_char_count = serializers.IntegerField(min_value=0)
    strict_mode_applied = serializers.BooleanField()
    scenario_excerpt = serializers.CharField()
    provider_mode = serializers.CharField(max_length=64, required=False)
    parser_notes = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class ExplainableSerializer(serializers.Serializer):
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    rationale = serializers.CharField()
    source_text_refs = SourceTextRefSerializer(many=True)
    needs_review = serializers.BooleanField()


class CaseContextSerializer(ExplainableSerializer):
    organization_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    industry = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    geography = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    regulatory_context = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    assessment_period = AssessmentPeriodInputSerializer(required=False, allow_null=True)
    deadline = serializers.DateField(required=False, allow_null=True)
    trigger = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    business_objective = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class FrameworkCandidateSerializer(serializers.Serializer):
    candidate_label = serializers.CharField()
    stored_library_urn = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    loaded_library_urn_or_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    framework_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    match_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    needs_review = serializers.BooleanField()
    rationale = serializers.CharField()


class FrameworkResolutionSerializer(ExplainableSerializer):
    requested_framework_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    canonical_framework_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    stored_library_lookup_required = serializers.BooleanField()
    loaded_library_lookup_required = serializers.BooleanField()
    framework_lookup_required = serializers.BooleanField()
    candidate_frameworks = FrameworkCandidateSerializer(many=True)
    selected_framework_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class FolderDomainDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    display_label = serializers.CharField()
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    content_type = serializers.CharField()
    existing_record_lookup_required = serializers.BooleanField()
    suggested_action = serializers.CharField()


class PerimeterDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    reference_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    folder_dependency = serializers.CharField()
    lifecycle_status_if_known = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    suggested_action = serializers.CharField()


class ComplianceAssessmentDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    reference_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    folder_dependency = serializers.CharField()
    perimeter_dependency = serializers.CharField()
    framework_dependency = serializers.CharField()
    assessment_period = AssessmentPeriodInputSerializer(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    auto_requirement_assessment_expected = serializers.BooleanField()
    suggested_action = serializers.CharField()


class RiskAssessmentDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    folder_dependency = serializers.CharField()
    perimeter_dependency = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    suggested_action = serializers.CharField()


class CaseSetupDraftSerializer(serializers.Serializer):
    folder_domain_draft = FolderDomainDraftSerializer()
    perimeter_draft = PerimeterDraftSerializer()
    compliance_assessment_draft = ComplianceAssessmentDraftSerializer()
    optional_risk_assessment_draft = RiskAssessmentDraftSerializer(required=False, allow_null=True)
    creation_order = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    dependency_notes = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    needs_review = serializers.BooleanField()


class AssetDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    proposed_ref_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    asset_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    folder_dependency = serializers.CharField()
    perimeter_relevance = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    business_role = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    criticality_if_inferred = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    suggested_action = serializers.CharField()


class AppliedControlDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    proposed_ref_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    control_category = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    implementation_status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    linked_asset_refs = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    related_requirement_refs_if_inferred = serializers.ListField(
        child=serializers.CharField(), allow_empty=True
    )
    control_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    suggested_action = serializers.CharField()


class VulnerabilityDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    severity = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    linked_asset_refs = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    suggested_action = serializers.CharField()


class RiskScenarioDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    risk_assessment_dependency = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    linked_asset_refs = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    treatment = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    suggested_action = serializers.CharField()


class RequirementFocusDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    requirement_reference = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    focus_reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    suggested_action = serializers.CharField()


class EvidenceExpectationDraftSerializer(ExplainableSerializer):
    platform_entity = serializers.ChoiceField(choices=CANONICAL_PLATFORM_ENTITIES)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    related_requirement_refs_if_inferred = serializers.ListField(
        child=serializers.CharField(), allow_empty=True
    )
    suggested_action = serializers.CharField()


class HumanReviewChecklistItemSerializer(serializers.Serializer):
    check_id = serializers.CharField(max_length=64)
    label = serializers.CharField()
    required = serializers.BooleanField()
    related_sections = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class NextSystemActionSerializer(serializers.Serializer):
    action_code = serializers.CharField(max_length=64)
    description = serializers.CharField()
    requires_human_confirmation = serializers.BooleanField()
    may_write_database = serializers.BooleanField()


class AiCaseIntakeDraftSerializer(serializers.Serializer):
    draft_type = serializers.ChoiceField(choices=("AiCaseIntakeDraft",))
    schema_version = serializers.ChoiceField(choices=(SCHEMA_VERSION,))
    source_summary = SourceSummarySerializer()
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    needs_human_review = serializers.BooleanField()
    blocking_questions = BlockingQuestionSerializer(many=True)
    warnings = WarningSerializer(many=True)
    canonical_mappings_used = CanonicalMappingSerializer(many=True)
    case_context = CaseContextSerializer()
    framework_resolution = FrameworkResolutionSerializer()
    case_setup_draft = CaseSetupDraftSerializer()
    asset_drafts = AssetDraftSerializer(many=True)
    applied_control_drafts = AppliedControlDraftSerializer(many=True)
    vulnerability_drafts = VulnerabilityDraftSerializer(many=True)
    risk_assessment_draft = RiskAssessmentDraftSerializer(required=False, allow_null=True)
    risk_scenario_drafts = RiskScenarioDraftSerializer(many=True)
    requirement_focus_drafts = RequirementFocusDraftSerializer(many=True)
    evidence_expectation_drafts = EvidenceExpectationDraftSerializer(many=True)
    human_review_checklist = HumanReviewChecklistItemSerializer(many=True)
    next_system_actions = NextSystemActionSerializer(many=True)

    def validate_needs_human_review(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError("Step 1 drafts must require human review.")
        return value