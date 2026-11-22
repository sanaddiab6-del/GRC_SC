from __future__ import annotations

from rest_framework import serializers


SCHEMA_VERSION = "0.1.0"

ADVISORY_NOTICE = (
    "AI suggestion only. This review never changes Evidence, revisions, controls, "
    "requirement assessments, or compliance results. A human decides what to do next."
)

FRESHNESS_STATUS_CURRENT = "CURRENT"
FRESHNESS_STATUS_REVIEW_RECOMMENDED = "REVIEW_RECOMMENDED"
FRESHNESS_STATUS_POSSIBLY_OUTDATED = "POSSIBLY_OUTDATED"
FRESHNESS_STATUS_INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"

FRESHNESS_STATUS_CHOICES = (
    FRESHNESS_STATUS_CURRENT,
    FRESHNESS_STATUS_REVIEW_RECOMMENDED,
    FRESHNESS_STATUS_POSSIBLY_OUTDATED,
    FRESHNESS_STATUS_INSUFFICIENT_CONTEXT,
)

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
)

# A single request is one HTTP round trip that may make this many sequential local-model
# calls (one per evidence item, never one giant prompt). Bounded so a batch review cannot
# turn into an unbounded number of blocking Ollama calls behind one request.
MAX_BATCH_SIZE = 10

# Keeps a single evidence item's context (and therefore its prompt) small and focused;
# mirrors the MAX_* bounds used by the other advisory capabilities in this app.
MAX_LINKED_ITEMS_PER_RELATION = 3
MAX_TEXT_FIELD_LENGTH = 500

# Bounds on the MODEL'S OWN output text. The system prompt asks for a short, concrete
# explanation and next step, but that is only a request: an uncooperative or malfunctioning
# model could return an unbounded wall of text. These caps make that fail schema validation
# (-> the same safe INSUFFICIENT_CONTEXT/422 path as any other malformed output) instead of
# silently storing and rendering an oversized response.
MAX_EXPLANATION_LENGTH = 1000
MAX_RECOMMENDED_ACTION_LENGTH = 500
MAX_CONCERN_LENGTH = 300


class StrictSerializer(serializers.Serializer):
    """Rejects any field the caller sent that this serializer does not declare."""

    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {
                        field: ["This field is not allowed in the evidence freshness review."]
                        for field in unknown_fields
                    }
                )
        return super().to_internal_value(data)


class AiEvidenceFreshnessReviewInputSerializer(StrictSerializer):
    """Request body for the single-evidence review action.

    Deliberately carries no evidence content: the evidence to review is identified by the
    URL (the ViewSet's pk), which is resolved through the normal Evidence queryset so RBAC
    and folder scoping apply exactly as they do for reading the Evidence itself. Nothing
    about the evidence is trusted from client input.
    """

    user_locale = serializers.CharField(required=False, allow_blank=True, max_length=16)


class AiEvidenceFreshnessReviewBatchInputSerializer(StrictSerializer):
    """Request body for the assessment-level / multi-evidence review action."""

    evidence_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False,
        max_length=MAX_BATCH_SIZE,
    )
    user_locale = serializers.CharField(required=False, allow_blank=True, max_length=16)

    def validate_evidence_ids(self, value):
        # De-duplicate while preserving order so a repeated id is not reviewed twice.
        seen: set = set()
        deduped = []
        for evidence_id in value:
            if evidence_id not in seen:
                seen.add(evidence_id)
                deduped.append(evidence_id)
        return deduped


class EvidenceFreshnessReviewResultSerializer(StrictSerializer):
    """The validated, final shape returned to the API and rendered by the frontend."""

    evidence_id = serializers.CharField()
    evidence_name = serializers.CharField(allow_blank=True)
    freshness_status = serializers.ChoiceField(choices=FRESHNESS_STATUS_CHOICES)
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    explanation = serializers.CharField(allow_blank=True, max_length=MAX_EXPLANATION_LENGTH)
    concerns = serializers.ListField(
        child=serializers.CharField(max_length=MAX_CONCERN_LENGTH)
    )
    recommended_action = serializers.CharField(
        allow_blank=True, max_length=MAX_RECOMMENDED_ACTION_LENGTH
    )
    linked_applied_controls_count = serializers.IntegerField(min_value=0)
    linked_requirement_assessments_count = serializers.IntegerField(min_value=0)
    linked_findings_count = serializers.IntegerField(min_value=0)
    revision_count = serializers.IntegerField(min_value=0)
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)
    advisory_notice = serializers.CharField()
    reviewed_at = serializers.DateTimeField()


# The provider is asked for only this much: the server already knows which evidence is being
# reviewed and attaches evidence_id/evidence_name/counts/reviewed_at itself afterwards, so the
# model cannot misreport which evidence a verdict belongs to.
class ProviderFreshnessJudgementSerializer(StrictSerializer):
    freshness_status = serializers.ChoiceField(choices=FRESHNESS_STATUS_CHOICES)
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    explanation = serializers.CharField(allow_blank=True, max_length=MAX_EXPLANATION_LENGTH)
    concerns = serializers.ListField(
        child=serializers.CharField(max_length=MAX_CONCERN_LENGTH),
        required=False,
        allow_empty=True,
    )
    recommended_action = serializers.CharField(
        allow_blank=True, max_length=MAX_RECOMMENDED_ACTION_LENGTH
    )
