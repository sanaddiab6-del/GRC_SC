from __future__ import annotations

import re

from rest_framework import serializers


SOURCE_DRAFT_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

DECISION_ACTION_CHOICES = ("create", "reuse", "reject", "defer")
SUGGESTION_KIND_CHOICES = (
    "evidence_request",
    "audit_question",
    "preliminary_finding",
)


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 5B."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 5B."] for field in unknown_fields}
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
    ref_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    asset_class = serializers.UUIDField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=("PR", "SP"), required=False, allow_null=True)
    source_temporary_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )


class AppliedControlReferenceSerializer(StrictSerializer):
    applied_control_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True, max_length=200)
    ref_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    source_temporary_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=64
    )


class FindingsAssessmentReferenceSerializer(StrictSerializer):
    findings_assessment_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)


class OriginalSuggestionSummarySerializer(StrictSerializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)
    question_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    summary = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rationale = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    review_status = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=32)
    confidence = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
    severity = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=32)
    related_weaknesses = serializers.ListField(
        child=serializers.CharField(max_length=500), required=False, allow_empty=True
    )
    linked_asset_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True
    )
    linked_applied_control_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True
    )


class ApprovedFieldsSerializer(StrictSerializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    severity = serializers.IntegerField(required=False, allow_null=True, min_value=-1, max_value=4)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        for field in ("name", "description"):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None
        return attrs


class EvidenceFindingDecisionSerializer(StrictSerializer):
    temporary_id = serializers.CharField(max_length=64)
    kind = serializers.ChoiceField(choices=SUGGESTION_KIND_CHOICES)
    selected = serializers.BooleanField(required=True)
    action = serializers.ChoiceField(choices=DECISION_ACTION_CHOICES)
    human_approved = serializers.BooleanField(required=True)
    selected_existing_id = serializers.UUIDField(required=False, allow_null=True)
    approved_fields = ApprovedFieldsSerializer(required=False, allow_null=True)
    original_suggestion_summary = OriginalSuggestionSummarySerializer(required=True)
    reviewer_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        action = attrs.get("action")
        approved_fields = attrs.get("approved_fields") or {}
        summary = attrs.get("original_suggestion_summary") or {}

        if not attrs.get("selected"):
            raise serializers.ValidationError(
                {"selected": ["selected must be true for submitted Step 5B decisions."]}
            )

        if action == "create":
            resolved_name = (
                approved_fields.get("name")
                or summary.get("title")
                or summary.get("question_text")
            )
            if not resolved_name:
                raise serializers.ValidationError(
                    {"approved_fields": {"name": ["A name/title is required when action is create."]}}
                )

        if action == "reuse" and not attrs.get("selected_existing_id"):
            raise serializers.ValidationError(
                {"selected_existing_id": ["selected_existing_id is required when action is reuse."]}
            )

        if action != "reuse":
            attrs["selected_existing_id"] = None

        reviewer_notes = attrs.get("reviewer_notes")
        if isinstance(reviewer_notes, str):
            attrs["reviewer_notes"] = reviewer_notes.strip() or None
        return attrs


class AiEvidenceFindingCommitInputSerializer(StrictSerializer):
    dry_run = serializers.BooleanField(required=True)
    approved_by_user = serializers.BooleanField(required=True)
    idempotency_key = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=255
    )
    source_step1_draft_hash = serializers.CharField(required=True, max_length=71)
    source_asset_commit_hash = serializers.CharField(required=True, max_length=71)
    source_applied_control_commit_hash = serializers.CharField(required=True, max_length=71)
    source_evidence_finding_draft_hash = serializers.CharField(required=True, max_length=71)
    case_setup_reference = CaseSetupReferenceSerializer(required=True)
    asset_references = AssetReferenceSerializer(many=True, required=False, allow_empty=True)
    applied_control_references = AppliedControlReferenceSerializer(
        many=True, required=False, allow_empty=True
    )
    findings_assessment_reference = FindingsAssessmentReferenceSerializer(
        required=False, allow_null=True
    )
    evidence_request_decisions = EvidenceFindingDecisionSerializer(
        many=True, required=False, allow_empty=True
    )
    audit_question_decisions = EvidenceFindingDecisionSerializer(
        many=True, required=False, allow_empty=True
    )
    preliminary_finding_decisions = EvidenceFindingDecisionSerializer(
        many=True, required=False, allow_empty=True
    )

    def _validate_hash(self, value: str, field_name: str) -> str:
        normalized = (value or "").strip()
        if not SOURCE_DRAFT_HASH_RE.match(normalized):
            raise serializers.ValidationError(
                f"{field_name} must be in the form 'sha256:<64 lowercase hex chars>'."
            )
        return normalized

    def validate_source_step1_draft_hash(self, value):
        return self._validate_hash(value, "source_step1_draft_hash")

    def validate_source_asset_commit_hash(self, value):
        return self._validate_hash(value, "source_asset_commit_hash")

    def validate_source_applied_control_commit_hash(self, value):
        return self._validate_hash(value, "source_applied_control_commit_hash")

    def validate_source_evidence_finding_draft_hash(self, value):
        return self._validate_hash(value, "source_evidence_finding_draft_hash")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        dry_run = attrs.get("dry_run")
        approved_by_user = attrs.get("approved_by_user")
        idempotency_key = (attrs.get("idempotency_key") or "").strip() or None
        attrs["idempotency_key"] = idempotency_key

        if not dry_run and not approved_by_user:
            raise serializers.ValidationError(
                {"approved_by_user": ["approved_by_user must be true when dry_run is false."]}
            )

        if not dry_run and not idempotency_key:
            raise serializers.ValidationError(
                {"idempotency_key": ["idempotency_key is required when dry_run is false."]}
            )

        total_decisions = (
            len(attrs.get("evidence_request_decisions") or [])
            + len(attrs.get("audit_question_decisions") or [])
            + len(attrs.get("preliminary_finding_decisions") or [])
        )
        if total_decisions == 0:
            raise serializers.ValidationError(
                {
                    "evidence_request_decisions": [
                        "At least one decision is required across evidence_request_decisions, "
                        "audit_question_decisions, or preliminary_finding_decisions."
                    ]
                }
            )

        # Enforce that each decision list only carries decisions of its own kind.
        for field_name, expected_kind in (
            ("evidence_request_decisions", "evidence_request"),
            ("audit_question_decisions", "audit_question"),
            ("preliminary_finding_decisions", "preliminary_finding"),
        ):
            for index, decision in enumerate(attrs.get(field_name) or []):
                if decision.get("kind") != expected_kind:
                    raise serializers.ValidationError(
                        {field_name: [f"{field_name}[{index}].kind must be '{expected_kind}'."]}
                    )

        return attrs
