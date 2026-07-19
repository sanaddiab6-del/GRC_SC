from __future__ import annotations

import re

from rest_framework import serializers

from core.models import Perimeter


STEP2_ALLOWED_PLATFORM_ENTITIES = (
    "Folder",
    "Perimeter",
    "ComplianceAssessment",
    "RiskAssessment",
    "Framework",
)

SOURCE_DRAFT_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 2."] for field in unknown_fields}
                )
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", None)
        if isinstance(initial_data, dict):
            unknown_fields = sorted(set(initial_data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed in Step 2."] for field in unknown_fields}
                )
        return attrs


class FrameworkResolutionInputSerializer(StrictSerializer):
    requested_framework_name = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    selected_framework_id = serializers.UUIDField(required=False, allow_null=True)
    selected_loaded_library_id = serializers.UUIDField(required=False, allow_null=True)
    selected_stored_library_urn = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    candidate_framework_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )
    user_confirmed = serializers.BooleanField(required=True)
    allow_auto_load = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        for field in ("requested_framework_name", "selected_stored_library_urn"):
            value = attrs.get(field)
            if isinstance(value, str):
                attrs[field] = value.strip() or None
        if attrs.get("allow_auto_load"):
            raise serializers.ValidationError(
                {"allow_auto_load": ["Automatic library loading is not supported by Step 2."]}
            )
        if not attrs.get("requested_framework_name") and not attrs.get("selected_framework_id"):
            raise serializers.ValidationError(
                {
                    "requested_framework_name": [
                        "Provide a framework name or selected_framework_id for Step 2."
                    ]
                }
            )
        return attrs


class FolderCreateFieldsSerializer(StrictSerializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    parent_folder_id = serializers.UUIDField(required=False, allow_null=True)
    create_iam_groups = serializers.BooleanField(required=False, default=False)

    def validate_name(self, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("This field may not be blank.")
        return trimmed


class PerimeterCreateFieldsSerializer(StrictSerializer):
    name = serializers.CharField(max_length=200)
    ref_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lc_status = serializers.ChoiceField(
        choices=[choice[0] for choice in Perimeter.PRJ_LC_STATUS],
        required=False,
        default="in_design",
    )

    def validate_name(self, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("This field may not be blank.")
        return trimmed


class AssessmentCreateFieldsSerializer(StrictSerializer):
    name = serializers.CharField(max_length=200)
    ref_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    version = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_name(self, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("This field may not be blank.")
        return trimmed


class RiskAssessmentCreateFieldsSerializer(AssessmentCreateFieldsSerializer):
    selected_risk_matrix_id = serializers.UUIDField(required=True)


class BaseDecisionSerializer(StrictSerializer):
    ACTION_CHOICES = ("create", "reuse", "skip", "reject")

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    platform_entity = serializers.ChoiceField(choices=STEP2_ALLOWED_PLATFORM_ENTITIES)
    selected_existing_id = serializers.UUIDField(required=False, allow_null=True)
    human_approved = serializers.BooleanField(required=True)
    rationale = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_reference = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    create_serializer_class: type[serializers.Serializer] | None = None

    def get_create_serializer(self):
        serializer_class = getattr(self, "create_serializer_class", None)
        return serializer_class() if serializer_class else None

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if "proposed_fields" in self.fields:
            ret["proposed_fields"] = ret.get("proposed_fields")
        return ret

    def validate(self, attrs):
        attrs = super().validate(attrs)
        action = attrs.get("action")
        proposed_fields = attrs.get("proposed_fields")
        selected_existing_id = attrs.get("selected_existing_id")

        if action == "create" and not proposed_fields:
            raise serializers.ValidationError(
                {"proposed_fields": ["proposed_fields is required when action is create."]}
            )
        if action == "reuse" and not selected_existing_id:
            raise serializers.ValidationError(
                {"selected_existing_id": ["selected_existing_id is required when action is reuse."]}
            )
        if action in {"skip", "reject"}:
            attrs["selected_existing_id"] = None
            attrs["proposed_fields"] = None
        return attrs


class FolderDecisionSerializer(BaseDecisionSerializer):
    platform_entity = serializers.ChoiceField(choices=("Folder",))
    proposed_fields = FolderCreateFieldsSerializer(required=False, allow_null=True)


class PerimeterDecisionSerializer(BaseDecisionSerializer):
    platform_entity = serializers.ChoiceField(choices=("Perimeter",))
    proposed_fields = PerimeterCreateFieldsSerializer(required=False, allow_null=True)


class ComplianceAssessmentDecisionSerializer(BaseDecisionSerializer):
    platform_entity = serializers.ChoiceField(choices=("ComplianceAssessment",))
    proposed_fields = AssessmentCreateFieldsSerializer(required=False, allow_null=True)


class RiskAssessmentDecisionSerializer(BaseDecisionSerializer):
    platform_entity = serializers.ChoiceField(choices=("RiskAssessment",))
    proposed_fields = RiskAssessmentCreateFieldsSerializer(required=False, allow_null=True)


class AiCaseSetupInputSerializer(StrictSerializer):
    draft_type = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=128)
    schema_version = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=32)
    approved_by_user = serializers.BooleanField(required=True)
    source_step1_draft_hash = serializers.CharField(required=True, max_length=71)
    source_step1_schema_version = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=32,
    )
    dry_run = serializers.BooleanField(required=True)
    idempotency_key = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
    )
    framework_resolution = FrameworkResolutionInputSerializer(required=True)
    folder_domain_decision = FolderDecisionSerializer(required=True)
    perimeter_decision = PerimeterDecisionSerializer(required=True)
    compliance_assessment_decision = ComplianceAssessmentDecisionSerializer(required=True)
    risk_assessment_decision = RiskAssessmentDecisionSerializer(
        required=False,
        allow_null=True,
    )

    def validate_source_step1_draft_hash(self, value: str) -> str:
        normalized = value.strip()
        if not SOURCE_DRAFT_HASH_RE.match(normalized):
            raise serializers.ValidationError(
                "source_step1_draft_hash must be in the form 'sha256:<64 lowercase hex chars>'."
            )
        return normalized

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

        if dry_run and approved_by_user is False:
            pass

        if attrs["framework_resolution"].get("user_confirmed") is False and not dry_run:
            raise serializers.ValidationError(
                {"framework_resolution": ["Framework resolution must be user confirmed for write mode."]}
            )

        if attrs.get("risk_assessment_decision") is None:
            attrs["risk_assessment_decision"] = {
                "action": "skip",
                "platform_entity": "RiskAssessment",
                "selected_existing_id": None,
                "proposed_fields": None,
                "human_approved": True if not dry_run else False,
                "rationale": "No optional risk assessment requested.",
                "source_reference": None,
            }

        return attrs