from __future__ import annotations

import re

from rest_framework import serializers


SOURCE_DRAFT_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
APPLIED_CONTROL_ACTION_CHOICES = ("create", "reuse", "reject", "defer")
APPLIED_CONTROL_CATEGORY_CHOICES = (
	"policy",
	"process",
	"technical",
	"physical",
	"procedure",
)
APPLIED_CONTROL_STATUS_CHOICES = (
	"to_do",
	"in_progress",
	"on_hold",
	"active",
	"deprecated",
	"--",
)


class StrictSerializer(serializers.Serializer):
	def to_internal_value(self, data):
		if isinstance(data, dict):
			unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
			if unknown_fields:
				raise serializers.ValidationError(
					{
						field: ["This field is not allowed in Step 4B."]
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
						field: ["This field is not allowed in Step 4B."]
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


class AmbiguityFlagSerializer(StrictSerializer):
	code = serializers.CharField(max_length=64)
	message = serializers.CharField()


class OriginalSuggestionSummarySerializer(StrictSerializer):
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
	proposed_control_type = serializers.CharField(
		required=False,
		allow_blank=True,
		allow_null=True,
		max_length=64,
	)
	proposed_control_category = serializers.ChoiceField(
		choices=APPLIED_CONTROL_CATEGORY_CHOICES,
		required=False,
		allow_null=True,
	)
	proposed_status = serializers.ChoiceField(
		choices=APPLIED_CONTROL_STATUS_CHOICES,
		required=False,
		allow_null=True,
	)
	proposed_implementation_state = serializers.CharField(
		required=False,
		allow_blank=True,
		allow_null=True,
		max_length=64,
	)
	linked_asset_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=True)
	linked_asset_temporary_ids = serializers.ListField(
		child=serializers.CharField(max_length=64),
		required=False,
		allow_empty=True,
	)
	related_weaknesses = serializers.ListField(
		child=serializers.CharField(max_length=500),
		required=False,
		allow_empty=True,
	)
	confidence = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)
	ambiguity_flags = AmbiguityFlagSerializer(many=True, required=False, allow_empty=True)


class AmbiguityResolutionSerializer(StrictSerializer):
	resolution_type = serializers.CharField(max_length=64)
	resolution_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class DuplicateResolutionSerializer(StrictSerializer):
	decision = serializers.CharField(max_length=64)
	reviewed_match_ids = serializers.ListField(
		child=serializers.UUIDField(),
		required=False,
		allow_empty=True,
	)
	resolution_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ApprovedAppliedControlFieldsSerializer(StrictSerializer):
	name = serializers.CharField(required=False, max_length=200)
	description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	ref_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
	category = serializers.ChoiceField(
		choices=APPLIED_CONTROL_CATEGORY_CHOICES,
		required=False,
		allow_null=True,
	)
	status = serializers.ChoiceField(
		choices=APPLIED_CONTROL_STATUS_CHOICES,
		required=False,
		allow_null=True,
	)
	linked_asset_ids = serializers.ListField(
		child=serializers.UUIDField(),
		required=False,
		allow_empty=True,
	)

	def validate(self, attrs):
		attrs = super().validate(attrs)
		for field in ("name", "description", "ref_id"):
			value = attrs.get(field)
			if isinstance(value, str):
				attrs[field] = value.strip() or None
		return attrs


class AppliedControlDecisionSerializer(StrictSerializer):
	temporary_id = serializers.CharField(max_length=64)
	selected = serializers.BooleanField(required=True)
	action = serializers.ChoiceField(choices=APPLIED_CONTROL_ACTION_CHOICES)
	human_approved = serializers.BooleanField(required=True)
	selected_existing_applied_control_id = serializers.UUIDField(required=False, allow_null=True)
	approved_fields = ApprovedAppliedControlFieldsSerializer(required=False, allow_null=True)
	original_suggestion_summary = OriginalSuggestionSummarySerializer(required=True)
	reviewer_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	ambiguity_resolution = AmbiguityResolutionSerializer(required=False, allow_null=True)
	duplicate_resolution = DuplicateResolutionSerializer(required=False, allow_null=True)

	def validate(self, attrs):
		attrs = super().validate(attrs)
		action = attrs.get("action")
		approved_fields = attrs.get("approved_fields")
		selected_existing_applied_control_id = attrs.get("selected_existing_applied_control_id")

		if not attrs.get("selected"):
			raise serializers.ValidationError(
				{"selected": ["selected must be true for submitted Step 4B decisions."]}
			)

		if action == "create":
			if not approved_fields:
				raise serializers.ValidationError(
					{"approved_fields": ["approved_fields is required when action is create."]}
				)
			if not approved_fields.get("name"):
				raise serializers.ValidationError(
					{"approved_fields": {"name": ["name is required when action is create."]}}
				)

		if action == "reuse" and not selected_existing_applied_control_id:
			raise serializers.ValidationError(
				{
					"selected_existing_applied_control_id": [
						"selected_existing_applied_control_id is required when action is reuse."
					]
				}
			)

		if action != "create":
			attrs["approved_fields"] = None
		if action != "reuse":
			attrs["selected_existing_applied_control_id"] = None

		reviewer_notes = attrs.get("reviewer_notes")
		if isinstance(reviewer_notes, str):
			attrs["reviewer_notes"] = reviewer_notes.strip() or None
		return attrs


class AiAppliedControlCommitInputSerializer(StrictSerializer):
	dry_run = serializers.BooleanField(required=True)
	approved_by_user = serializers.BooleanField(required=True)
	idempotency_key = serializers.CharField(
		required=False,
		allow_blank=True,
		allow_null=True,
		max_length=255,
	)
	source_step1_draft_hash = serializers.CharField(required=True, max_length=71)
	source_asset_commit_hash = serializers.CharField(required=True, max_length=71)
	source_applied_control_draft_hash = serializers.CharField(required=True, max_length=71)
	case_setup_reference = CaseSetupReferenceSerializer(required=True)
	asset_references = AssetReferenceSerializer(many=True, allow_empty=False)
	applied_control_decisions = AppliedControlDecisionSerializer(many=True, allow_empty=False)

	def validate_source_step1_draft_hash(self, value: str) -> str:
		normalized = value.strip()
		if not SOURCE_DRAFT_HASH_RE.match(normalized):
			raise serializers.ValidationError(
				"source_step1_draft_hash must be in the form 'sha256:<64 lowercase hex chars>'."
			)
		return normalized

	def validate_source_asset_commit_hash(self, value: str) -> str:
		normalized = value.strip()
		if not SOURCE_DRAFT_HASH_RE.match(normalized):
			raise serializers.ValidationError(
				"source_asset_commit_hash must be in the form 'sha256:<64 lowercase hex chars>'."
			)
		return normalized

	def validate_source_applied_control_draft_hash(self, value: str) -> str:
		normalized = value.strip()
		if not SOURCE_DRAFT_HASH_RE.match(normalized):
			raise serializers.ValidationError(
				"source_applied_control_draft_hash must be in the form 'sha256:<64 lowercase hex chars>'."
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

		if not attrs.get("asset_references"):
			raise serializers.ValidationError(
				{"asset_references": ["asset_references must not be empty."]}
			)

		if not attrs.get("applied_control_decisions"):
			raise serializers.ValidationError(
				{"applied_control_decisions": ["applied_control_decisions must not be empty."]}
			)

		return attrs