"""SICO AI Pre-Assessment endpoints: extract facts, judge one fact at a time, commit.

The page drives the steps (extract -> judge per fact -> commit) so every HTTP request
makes at most one model call and no request holds a database transaction while the model
runs. Only the commit endpoint writes, and it makes no model call. The feature is on by
default; SICO_AI_PRE_ASSESSMENT_ENABLED=false (setting or environment variable) is the
emergency off switch.
"""
from __future__ import annotations

import os
import re
from dataclasses import replace

from django.conf import settings
from django.utils import timezone
from rest_framework import permissions, serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .llm_config import CAPABILITY_GRC_CAPABILITY_SELECTION, resolve_advisory_capability_config
from .llm_errors import AiProviderError
from .llm_provider import get_advisory_provider_selection
from .pre_assessment_llm import extract_facts, judge_fact
from .pre_assessment_service import (
    PreAssessmentRefused,
    commit_pre_assessment,
    item_fields,
    plan_fact_results,
    plan_run,
    verify_facts,
)
from .pre_assessment_topics import TOPIC_ENUM, RequirementCandidate, build_candidates, shortlist_requirements

FEATURE_FLAG = "SICO_AI_PRE_ASSESSMENT_ENABLED"
_FALSE = {"0", "false", "no", "off"}
_CODE = re.compile(r"[a-z][a-z0-9_]{1,63}")
PROVENANCE = "sico_ai_pre_assessment_v1"


def pre_assessment_enabled() -> bool:
    """On by default; only an explicit false/0/no/off turns it off (emergency switch).
    A Django setting wins over the environment variable."""
    value = getattr(settings, FEATURE_FLAG, None)
    if value is None:
        value = os.environ.get(FEATURE_FLAG, "")
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in _FALSE


def readable_framework(user, framework_id):
    """The framework if this user may read it; otherwise None (same answer either way)."""
    from core.models import Framework
    from iam.models import RoleAssignment

    framework = Framework.objects.filter(id=framework_id).first()
    if framework is None or not RoleAssignment.is_object_readable(user, Framework, framework.id):
        return None
    return framework


def default_implementation_groups(framework) -> set[str]:
    """The groups a new audit of this framework starts with (same rule as the platform's
    ComplianceAssessmentWriteSerializer)."""
    return {
        str(group.get("ref_id"))
        for group in (framework.implementation_groups_definition or [])
        if isinstance(group, dict) and group.get("default_selected")
    }


def load_authorized_candidates(user, framework) -> list[RequirementCandidate]:
    """Requirements of the framework this user may read, as retrieval candidates.

    Non-assessable sections are loaded too: they give their children context. A
    requirement outside the framework's default implementation groups is not assessed
    in a new audit, so it is not offered either.
    """
    from core.models import RequirementNode
    from iam.models import Folder, RoleAssignment

    readable_ids = RoleAssignment.get_accessible_object_ids(Folder.get_root_folder(), user, RequirementNode)[0]
    rows = list(
        RequirementNode.objects.filter(framework=framework, id__in=readable_ids)
        .order_by("order_id", "pk")
        .values("id", "urn", "parent_urn", "assessable", "ref_id", "name", "description",
                "implementation_groups")
    )
    groups = default_implementation_groups(framework)
    for row in rows:
        row["key"] = str(row["id"])
        if groups and row["assessable"] and not (set(row.get("implementation_groups") or []) & groups):
            row["assessable"] = False
    return build_candidates(rows)


def provider_selection():
    config = resolve_advisory_capability_config(CAPABILITY_GRC_CAPABILITY_SELECTION)
    return get_advisory_provider_selection(config)


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, AiProviderError):
        code = getattr(exc, "error_code", "") or ""
        if code == "ai_provider_request_failed" and "timed out" in (getattr(exc, "detail", "") or "").casefold():
            return "provider_timeout"
        return code if _CODE.fullmatch(code) else "provider_failure"
    if isinstance(exc, TimeoutError):
        return "provider_timeout"
    if isinstance(exc, ValueError) and _CODE.fullmatch(str(exc)):
        return str(exc)
    return "processing_error"


def _refused(detail: str, reason: str, status: int) -> Response:
    return Response({"detail": detail, "failure_reason": reason, "business_records_written": False}, status=status)


def _guard(request):
    """Common checks; returns a Response to send back, or None to continue."""
    if not pre_assessment_enabled():
        return _refused("SICO AI Pre-Assessment is not enabled.", "pre_assessment_disabled", 403)
    if not request.user.is_active:
        return _refused("Account inactive.", "account_inactive", 403)
    return None


class ExtractInput(serializers.Serializer):
    framework_id = serializers.UUIDField()
    organization_name = serializers.CharField(min_length=2, max_length=150)
    objective = serializers.CharField(min_length=20, max_length=4000)


class FactInput(serializers.Serializer):
    quote = serializers.CharField(max_length=600)
    claim_en = serializers.CharField(required=False, allow_blank=True, max_length=600, default="")
    topics = serializers.ListField(child=serializers.ChoiceField(choices=TOPIC_ENUM), min_length=1, max_length=2)
    uncertain = serializers.BooleanField()


class JudgeInput(serializers.Serializer):
    framework_id = serializers.UUIDField()
    objective = serializers.CharField(min_length=20, max_length=4000)
    fact_index = serializers.IntegerField(min_value=0, max_value=5)
    fact = FactInput()


class JudgementItem(serializers.Serializer):
    ref_id = serializers.CharField(max_length=40)
    relation = serializers.CharField(max_length=40)
    violated_clause = serializers.CharField(required=False, allow_blank=True, max_length=600, default="")


class FactJudgements(serializers.Serializer):
    fact_index = serializers.IntegerField(min_value=0, max_value=5)
    items = serializers.ListField(child=JudgementItem(), max_length=12)


class CommitInput(serializers.Serializer):
    framework_id = serializers.UUIDField()
    organization_name = serializers.CharField(min_length=2, max_length=150)
    objective = serializers.CharField(min_length=20, max_length=4000)
    facts = serializers.ListField(child=FactInput(), min_length=1, max_length=6)
    judgements = serializers.ListField(child=FactJudgements(), max_length=6, required=False, default=list)


class PreAssessmentExtractView(APIView):
    """Step 1: one model call that lists facts with quotes; only verified facts are returned."""

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post", "options"]

    def post(self, request, format=None):
        refused = _guard(request)
        if refused is not None:
            return refused
        form = ExtractInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        framework = readable_framework(request.user, values["framework_id"])
        if framework is None:
            return _refused("The selected framework is unavailable to this user.", "framework_unavailable", 403)
        try:
            selection = provider_selection()
            raw_facts = extract_facts(
                selection,
                organization=values["organization_name"],
                framework_name=str(framework.name),
                objective=values["objective"],
            )
        except (AiProviderError, ValueError, TimeoutError, TypeError, KeyError) as exc:
            return _refused("The AI model could not read the objective. Nothing was saved.",
                            _failure_reason(exc), 503)
        facts, dropped = verify_facts(raw_facts, values["objective"])
        return Response({
            "framework_id": str(framework.id),
            "facts": [
                {
                    "index": f.index,
                    "quote": f.quote,
                    "sentence": f.sentence,
                    "claim_en": f.claim,
                    "topics": list(f.topics),
                    "uncertain": f.uncertain,
                    "judgeable": f.judgeable,
                }
                for f in facts
            ],
            "dropped": dropped,
            "model": selection.config.model,
            "provenance": PROVENANCE,
            "business_records_written": False,
        })


class PreAssessmentJudgeView(APIView):
    """Step 2, once per fact: the code builds the short list, one model call judges it,
    and the code's rules decide what may be written."""

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post", "options"]

    def post(self, request, format=None):
        refused = _guard(request)
        if refused is not None:
            return refused
        form = JudgeInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        framework = readable_framework(request.user, values["framework_id"])
        if framework is None:
            return _refused("The selected framework is unavailable to this user.", "framework_unavailable", 403)

        sent = values["fact"]
        facts, _dropped = verify_facts(
            [{"quote": sent["quote"], "claim_en": sent.get("claim_en", ""), "topics": sent["topics"],
              "certainty": "uncertain" if sent["uncertain"] else "stated"}],
            values["objective"],
        )
        if not facts:
            return _refused("This fact is not quoted from the objective.", "fact_not_in_objective", 400)
        fact = replace(facts[0], index=values["fact_index"])

        response = {
            "fact_index": fact.index,
            "short_list": [],
            "judgements": [],
            "results": [],
            "ignored": [],
            "provenance": PROVENANCE,
            "business_records_written": False,
        }
        if not fact.judgeable:
            return Response(response)
        shortlist = shortlist_requirements(load_authorized_candidates(request.user, framework), fact.topics, fact.claim)
        response["short_list"] = [c.ref_id for c in shortlist]
        if not shortlist:
            return Response(response)
        try:
            selection = provider_selection()
            raw = judge_fact(selection, sentence=fact.sentence, claim=fact.claim,
                             uncertain=fact.uncertain, shortlist=shortlist)
        except (AiProviderError, ValueError, TimeoutError, TypeError, KeyError) as exc:
            return _refused("The AI model could not judge this fact. Nothing was saved.",
                            _failure_reason(exc), 503)
        results, ignored = plan_fact_results(fact, shortlist, raw)
        # The page sends these judgements back at commit, where every rule runs again.
        response["judgements"] = [
            {"ref_id": str(item.get("ref_id") or "")[:40],
             "relation": str(item.get("relation") or "")[:40],
             "violated_clause": str(item.get("violated_clause") or "")[:600]}
            for item in (item_fields(i) for i in raw if isinstance(i, dict))
        ]
        response["results"] = [
            {"ref_id": r.ref_id, "rank": r.rank, "kind": r.outcome.kind, "result": r.outcome.result,
             "status": r.outcome.status, "clause": r.outcome.clause}
            for r in results
        ]
        response["ignored"] = ignored
        response["model"] = selection.config.model
        return Response(response)


class PreAssessmentCommitView(APIView):
    """Step 3: no model call. Every check runs again on what the page sends back, then
    Domain, Perimeter, a new Audit and its results are written in one transaction."""

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post", "options"]

    def post(self, request, format=None):
        refused = _guard(request)
        if refused is not None:
            return refused
        form = CommitInput(data=request.data)
        form.is_valid(raise_exception=True)
        values = form.validated_data
        framework = readable_framework(request.user, values["framework_id"])
        if framework is None:
            return _refused("The selected framework is unavailable to this user.", "framework_unavailable", 403)

        sent_facts = values["facts"]
        facts, _dropped = verify_facts(
            [{"quote": f["quote"], "claim_en": f.get("claim_en", ""), "topics": f["topics"],
              "certainty": "uncertain" if f["uncertain"] else "stated"} for f in sent_facts],
            values["objective"],
        )
        if len(facts) != len(sent_facts):
            return _refused("A fact is not quoted from the objective. Nothing was saved.", "fact_not_in_objective", 400)
        judgements_by_fact = {}
        for group in values.get("judgements") or []:
            judgements_by_fact.setdefault(group["fact_index"], []).extend(dict(item) for item in group["items"])

        results = plan_run(facts, load_authorized_candidates(request.user, framework), judgements_by_fact)
        try:
            model = resolve_advisory_capability_config(CAPABILITY_GRC_CAPABILITY_SELECTION).model
            outcome = commit_pre_assessment(
                request=request, framework=framework, organization=values["organization_name"],
                facts=facts, results=results, model=model, day=timezone.localdate(),
            )
        except PreAssessmentRefused as exc:
            return _refused(exc.detail, exc.code, exc.status)
        except DRFValidationError:
            return _refused("The platform refused the new records. Nothing was saved.", "validation_failed", 422)
        except Exception:  # noqa: BLE001 - the transaction is rolled back; report without internals
            return _refused("The pre-assessment could not be saved. Nothing was saved.", "transaction_aborted", 422)
        outcome.update({"provenance": PROVENANCE, "business_records_written": True})
        return Response(outcome, status=201)
