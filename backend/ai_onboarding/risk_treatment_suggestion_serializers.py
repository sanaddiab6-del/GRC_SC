from __future__ import annotations

from rest_framework import serializers

from core.models import AppliedControl, RiskScenario


SCHEMA_VERSION = "0.1.0"

ADVISORY_NOTICE = (
    "AI suggestion only. This has not changed the risk scenario, its treatment, its ratings, "
    "or any control or remediation. A human decides what to do next."
)

# "open" is RiskScenario's undecided state, not a treatment, so it is never a valid suggestion.
# Derived from the model rather than restated, so the two can never drift apart.
UNDECIDED_TREATMENT = "open"
SUGGESTABLE_TREATMENT_CHOICES: tuple[str, ...] = tuple(
    value for value, _label in RiskScenario.TREATMENT_OPTIONS if value != UNDECIDED_TREATMENT
)

# Mirrors AppliedControl.PRIORITY (1..4, labelled P1..P4) so a suggested action can be carried
# over into a real applied control by a human without translating its priority.
ACTION_PRIORITY_CHOICES: tuple[str, ...] = tuple(
    f"P{value}" for value, _label in AppliedControl.PRIORITY
)

PROVIDER_MODE_CHOICES = (
    "configured_local_provider",
    "provider_not_configured_fallback",
    "local_provider_error_fallback",
    "not_called_insufficient_context",
)

# Whether a suggestion was actually produced. Anything other than "suggested" carries
# suggested_treatment = None: a treatment is never invented to fill the gap.
OUTCOME_SUGGESTED = "suggested"
OUTCOME_INSUFFICIENT_CONTEXT = "insufficient_context"
OUTCOME_PROVIDER_UNAVAILABLE = "provider_unavailable"
OUTCOME_CHOICES = (
    OUTCOME_SUGGESTED,
    OUTCOME_INSUFFICIENT_CONTEXT,
    OUTCOME_PROVIDER_UNAVAILABLE,
)

# Context bounds: keep one scenario's prompt small and focused.
MAX_LINKED_ITEMS_PER_RELATION = 5
MAX_CONTEXT_TEXT_LENGTH = 500

# Bounds on the MODEL'S OWN output. The system prompt asks for short output, but that is only a
# request; these make oversized output fail validation instead of being stored or rendered.
MAX_RATIONALE_LENGTH = 1000
MAX_MITIGATING_ACTIONS = 5
MAX_ACTION_TITLE_LENGTH = 200
MAX_ACTION_DESCRIPTION_LENGTH = 500
MAX_CONSIDERATIONS = 5
MAX_CONSIDERATION_LENGTH = 300


class StrictSerializer(serializers.Serializer):
    """Rejects any field that this serializer does not declare."""

    def to_internal_value(self, data):
        if isinstance(data, dict):
            unknown_fields = sorted(set(data.keys()) - set(self.fields.keys()))
            if unknown_fields:
                raise serializers.ValidationError(
                    {
                        field: ["This field is not allowed in the risk treatment suggestion."]
                        for field in unknown_fields
                    }
                )
        return super().to_internal_value(data)


class AiRiskTreatmentSuggestionInputSerializer(StrictSerializer):
    """Request body. Carries no risk content: the scenario is identified by the URL and resolved
    through the normal folder-scoped RiskScenario queryset, so nothing about it is trusted from
    client input."""

    user_locale = serializers.CharField(required=False, allow_blank=True, max_length=16)


class MitigatingActionSerializer(StrictSerializer):
    title = serializers.CharField(max_length=MAX_ACTION_TITLE_LENGTH)
    description = serializers.CharField(
        allow_blank=True, max_length=MAX_ACTION_DESCRIPTION_LENGTH
    )
    priority = serializers.ChoiceField(choices=ACTION_PRIORITY_CHOICES)


class ProviderTreatmentJudgementSerializer(StrictSerializer):
    """Exactly what the model is allowed to return. Identifiers, counts, and timestamps are
    attached by the server afterwards from the real object, never taken from the model."""

    suggested_treatment = serializers.ChoiceField(choices=SUGGESTABLE_TREATMENT_CHOICES)
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    rationale = serializers.CharField(allow_blank=True, max_length=MAX_RATIONALE_LENGTH)
    mitigating_actions = MitigatingActionSerializer(
        many=True, required=False, max_length=MAX_MITIGATING_ACTIONS
    )
    considerations = serializers.ListField(
        child=serializers.CharField(max_length=MAX_CONSIDERATION_LENGTH),
        required=False,
        allow_empty=True,
        max_length=MAX_CONSIDERATIONS,
    )


class RiskTreatmentSuggestionResultSerializer(StrictSerializer):
    """The validated, final shape returned to the API and rendered by the frontend."""

    risk_scenario_id = serializers.CharField()
    risk_scenario_name = serializers.CharField(allow_blank=True)
    current_treatment = serializers.CharField()
    outcome = serializers.ChoiceField(choices=OUTCOME_CHOICES)
    suggested_treatment = serializers.ChoiceField(
        choices=SUGGESTABLE_TREATMENT_CHOICES, allow_null=True
    )
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    rationale = serializers.CharField(allow_blank=True, max_length=MAX_RATIONALE_LENGTH)
    mitigating_actions = MitigatingActionSerializer(
        many=True, max_length=MAX_MITIGATING_ACTIONS
    )
    considerations = serializers.ListField(
        child=serializers.CharField(max_length=MAX_CONSIDERATION_LENGTH),
        max_length=MAX_CONSIDERATIONS,
    )
    is_rated = serializers.BooleanField()
    linked_assets_count = serializers.IntegerField(min_value=0)
    linked_threats_count = serializers.IntegerField(min_value=0)
    existing_controls_count = serializers.IntegerField(min_value=0)
    planned_controls_count = serializers.IntegerField(min_value=0)
    provider_mode = serializers.ChoiceField(choices=PROVIDER_MODE_CHOICES)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)
    advisory_notice = serializers.CharField()
    reviewed_at = serializers.DateTimeField()
