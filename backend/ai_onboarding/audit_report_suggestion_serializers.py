from __future__ import annotations

import re

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"
MAX_CASE_SUMMARY_LENGTH = 20_000
DEFAULT_USER_LOCALE = "en"
LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")

ADVISORY_NOTICE = (
    "AI draft only. Step 11A produces a report draft for human review; it is never a final "
    "audit opinion and never a compliance certification."
)

REVIEW_STATUS_CHOICES = ("pending_review",)

# The report skeleton the draft is expected to cover. A missing section is reported as a
# warning rather than silently invented.
EXPECTED_SECTION_HEADINGS = (
    "Executive Summary",
    "Scope",
    "Assets in Scope",
    "Known Weaknesses",
    "Applied Controls",
    "Evidence Requested",
    "Audit Questions",
    "Preliminary Findings",
    "Remediation Actions",
    "Framework Control Mappings",
    "Risk Scenarios",
    "Control Effectiveness / Compliance Suggestions",
    "Evidence Gaps",
    "Audit Readiness",
    "Recommended Next Steps",
    "Limitations / Human Review Required",
)

MAX_REPORT_SECTIONS = 20
MAX_SECTION_CONTENT_LENGTH = 8000
MAX_LIST_ITEMS = 20

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
    "local_provider_error_blocked",
    # Step 11A refuses to run the model when there is no reviewed onboarding context.
    "report_context_missing_blocked",
)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 11A."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 11A."] for field in unknown_fields}
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


class AuditReadinessContextSerializer(StrictSerializer):
    """The reviewed Step 10A readiness summary carried as readable context."""

    readiness_status = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )
    readiness_score = serializers.IntegerField(required=False, allow_null=True)
    summary = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=5000
    )

    def validate(self, attrs):
        return _strip_optional(super().validate(attrs), ("readiness_status", "summary"))


class AiAuditReportSuggestionInputSerializer(StrictSerializer):
    case_summary = serializers.CharField(
        required=False, allow_blank=True, max_length=MAX_CASE_SUMMARY_LENGTH
    )
    scenario_name = serializers.CharField(required=False, allow_blank=True, max_length=500)
    organization_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    framework_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
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
    evidence_gaps = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    audit_readiness = AuditReadinessContextSerializer(required=False, allow_null=True)
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

        for field in ("organization_name", "framework_name"):
            value = attrs.get(field)
            attrs[field] = value.strip() or None if isinstance(value, str) else value

        for field in ("known_weaknesses", "evidence_gaps"):
            entries = []
            for item in attrs.get(field) or []:
                trimmed = item.strip()
                if trimmed:
                    entries.append(trimmed)
            attrs[field] = entries

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


class ReportSectionSerializer(StrictSerializer):
    heading = serializers.CharField(max_length=200)
    content = serializers.CharField(allow_blank=True, max_length=MAX_SECTION_CONTENT_LENGTH)
    source_items = serializers.ListField(
        child=serializers.CharField(max_length=500), allow_empty=True
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)


class AiAuditReportSuggestionDraftSerializer(StrictSerializer):
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    report_title = serializers.CharField(max_length=300)
    overall_confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    report_sections = ReportSectionSerializer(many=True)
    executive_summary = serializers.CharField(allow_blank=True)
    limitations = serializers.ListField(
        child=serializers.CharField(max_length=1000), allow_empty=True
    )
    recommended_next_steps = serializers.ListField(
        child=serializers.CharField(max_length=500), allow_empty=True
    )
    warnings = WarningSerializer(many=True)
    ambiguity_flags = AmbiguityFlagSerializer(many=True)
    review_status = serializers.ChoiceField(choices=REVIEW_STATUS_CHOICES)
