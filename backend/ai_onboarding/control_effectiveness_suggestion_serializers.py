from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
MAX_CASE_SUMMARY_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")

ADVISORY_NOTICE = (
    "AI suggestions only. Step 9A never updates a RequirementAssessment, never closes an "
    "audit, and never certifies compliance."
)

REVIEW_STATUS_CHOICES = ("pending_review",)

# Step 9A asks for a short, reviewable set of judgements rather than an exhaustive matrix.
MAX_CONTROL_EFFECTIVENESS_SUGGESTIONS = 5

EFFECTIVENESS_CHOICES = (
    "effective",
    "partially_effective",
    "ineffective",
    "not_assessed",
    "needs_more_evidence",
)

COMPLIANCE_STATUS_CHOICES = (
    "compliant",
    "partially_compliant",
    "non_compliant",
    "not_assessed",
    "needs_more_evidence",
)

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
    "local_provider_error_blocked",
    # Step 9A refuses to run the model when there is no existing control to judge.
    "control_context_missing_blocked",
)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 9A."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 9A."] for field in unknown_fields}
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
    """Readable context row for controls, evidence, findings, remediation, and risks."""

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


class FrameworkControlContextSerializer(StrictSerializer):
    """An existing framework control carried over from the reviewed Step 7A/7B mappings.

    Step 9A may only judge controls listed here or in requirement_assessments; it never
    invents a framework control.
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
    requirement_assessment_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["title"] = attrs["title"].strip()
        attrs = _strip_optional(
            attrs, ("reference", "code", "description", "requirement_assessment_reference")
        )
        if not attrs["title"]:
            raise serializers.ValidationError(
                {"title": ["A framework control context row requires a readable title."]}
            )
        return attrs


class RequirementAssessmentContextSerializer(StrictSerializer):
    """An existing RequirementAssessment pairing, carried read-only as context."""

    reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    framework_control_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=255
    )
    framework_control_code = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    framework_control_title = serializers.CharField(required=True, max_length=500)
    current_result = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    current_status = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["framework_control_title"] = attrs["framework_control_title"].strip()
        return _strip_optional(
            attrs,
            (
                "reference",
                "framework_control_reference",
                "framework_control_code",
                "current_result",
                "current_status",
            ),
        )


class AiControlEffectivenessSuggestionInputSerializer(StrictSerializer):
    case_summary = serializers.CharField(
        required=False, allow_blank=True, max_length=MAX_CASE_SUMMARY_LENGTH
    )
    scenario_name = serializers.CharField(required=False, allow_blank=True, max_length=500)
    folder_reference = FolderReferenceSerializer(required=False, allow_null=True)
    assessment_reference = AssessmentReferenceSerializer(required=False, allow_null=True)
    framework_mappings = FrameworkControlContextSerializer(
        many=True, required=False, allow_empty=True
    )
    requirement_assessments = RequirementAssessmentContextSerializer(
        many=True, required=False, allow_empty=True
    )
    applied_controls = ContextItemSerializer(many=True, required=False, allow_empty=True)
    evidence_requests = ContextItemSerializer(many=True, required=False, allow_empty=True)
    audit_questions = ContextItemSerializer(many=True, required=False, allow_empty=True)
    preliminary_findings = ContextItemSerializer(many=True, required=False, allow_empty=True)
    remediation_actions = ContextItemSerializer(many=True, required=False, allow_empty=True)
    risk_scenarios = ContextItemSerializer(many=True, required=False, allow_empty=True)
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
            "framework_mappings",
            "requirement_assessments",
            "applied_controls",
            "evidence_requests",
            "audit_questions",
            "preliminary_findings",
            "remediation_actions",
            "risk_scenarios",
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


class ControlEffectivenessSuggestionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    framework_control_reference = serializers.CharField(max_length=255)
    framework_control_code = serializers.CharField(allow_blank=True, max_length=200)
    framework_control_title = serializers.CharField(max_length=500)
    linked_requirement_assessment_reference = serializers.CharField(
        allow_blank=True, max_length=64
    )
    linked_applied_control_reference = serializers.CharField(allow_blank=True, max_length=200)
    linked_applied_control_title = serializers.CharField(allow_blank=True, max_length=500)
    linked_finding_reference = serializers.CharField(allow_blank=True, max_length=200)
    linked_finding_title = serializers.CharField(allow_blank=True, max_length=500)
    suggested_effectiveness = serializers.ChoiceField(choices=EFFECTIVENESS_CHOICES)
    suggested_compliance_status = serializers.ChoiceField(choices=COMPLIANCE_STATUS_CHOICES)
    evidence_summary = serializers.CharField(allow_blank=True)
    gaps = serializers.ListField(
        child=serializers.CharField(max_length=500), allow_empty=True
    )
    recommended_auditor_action = serializers.CharField(allow_blank=True)
    rationale = serializers.CharField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)


class AiControlEffectivenessSuggestionDraftSerializer(StrictSerializer):
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    control_effectiveness_suggestions = ControlEffectivenessSuggestionSerializer(many=True)
    warnings = WarningSerializer(many=True)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
