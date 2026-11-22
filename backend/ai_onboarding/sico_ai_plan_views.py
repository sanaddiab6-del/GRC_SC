"""SICO AI Next: authenticated, read-only AI coordinator planning endpoint.

No GRC business records are queried, created, modified or approved by this view.
Plan stage names come exclusively from the reviewed SICO engagement registry.
"""
from __future__ import annotations

import re

from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .engagement_rules import STAGES
from .llm_config import CAPABILITY_CASE_INTAKE, resolve_advisory_capability_config
from .llm_errors import AiProviderExecutionError
from .llm_provider import get_advisory_provider_selection


# These descriptions only explain existing registered stages. They do not execute them.
STAGE_DESCRIPTIONS = {
    "case_setup": ("Set up GRC case", "Resolve a permitted framework, organization folder, perimeter and assessment"),
    "assets": ("Inventory assets", "Identify and review the assets in scope"),
    "applied_controls": ("Plan applied controls", "Map candidate safeguards to the authorized case"),
    "evidence_findings": ("Evidence and findings", "Plan evidence requests and review potential findings without inventing proof"),
    "remediation": ("Remediation actions", "Plan corrective actions for verified gaps"),
    "framework_control_mappings": ("Map framework controls", "Plan mappings to requirements of the selected framework"),
    "risk_scenarios": ("Assess risk scenarios", "Plan relevant risk scenarios and their required reviews"),
    "control_effectiveness": ("Review control effectiveness", "Evaluate what evidence will be required to assess control effectiveness"),
    "audit_readiness": ("Review audit readiness", "Prepare review criteria without declaring certification"),
    "audit_report": ("Prepare audit report", "Plan a report based only on supported and reviewed observations"),
    "final_review": ("Final human review", "Review outcomes and unresolved questions before case closure"),
}


class SicoAiPlanInput(serializers.Serializer):
    instruction = serializers.CharField(min_length=20, max_length=12000, trim_whitespace=True)
    organization_hint = serializers.CharField(required=False, allow_blank=True, max_length=150)


def _requests_full_case(instruction: str) -> bool:
    return bool(re.search(
        r"\b(full|complete|entire|whole|end.to.end|all\s+(?:grc\s+)?(?:functions|steps|modules)|"
        r"from\s+start\s+to\s+finish)\b", instruction, re.IGNORECASE
    ))


# Select only source-reviewed stages. This decision is deterministic, not an
# untrusted instruction from the LLM, so a small model cannot invent tool names.
STAGE_INTENT_TERMS = {
    "case_setup": ("case", "assessment", "framework", "scope", "organization", "organisation", "compliance", "تقييم", "امتثال"),
    "assets": ("asset", "inventory", "أصول"),
    "applied_controls": ("control", "policy", "safeguard", "ضوابط", "سياسات"),
    "evidence_findings": ("evidence", "finding", "audit evidence", "أدلة", "ملاحظات"),
    "remediation": ("remediat", "corrective", "treatment plan", "معالجة", "تصحيح"),
    "framework_control_mappings": ("mapping", "map controls", "ربط الضوابط"),
    "risk_scenarios": ("risk", "threat", "vulnerabilit", "مخاطر", "تهديد"),
    "control_effectiveness": ("effectiveness", "control testing", "فعالية الضوابط"),
    "audit_readiness": ("audit readiness", "audit preparation", "جاهزية التدقيق"),
    "audit_report": ("report", "audit report", "تقرير"),
    "final_review": ("final review", "closure", "sign-off", "مراجعة نهائية"),
}


def _select_registered_stages(instruction: str, stage_names: list[str]) -> set[str]:
    if _requests_full_case(instruction):
        return set(stage_names)
    # Questions about GRC concepts should not become proposed database actions.
    if re.match(r"^\s*(explain|what is|define|tell me about|اشرح|ما هو)", instruction, re.IGNORECASE) \
            and not re.search(r"\b(create|prepare|plan|assess|evaluate|review|generate|build|implement|execute)\b", instruction, re.IGNORECASE):
        return set()
    text = instruction.casefold()
    return {
        name for name in stage_names
        if any(term in text for term in STAGE_INTENT_TERMS.get(name, ()))
    }


def _planning_questions(instruction: str, selected: set[str], organization_hint: str) -> list[str]:
    # These are standard requests for missing user context, not model findings.
    questions = []
    if "case_setup" in selected and not organization_hint:
        questions.append("Is this a new organization or an existing organization you can access? This is not required to begin planning.")
    if "case_setup" in selected and not re.search(
        r"\b(nca\s*ecc|essential cybersecurity controls|iso\s*27001|sama\s*csf|nist\s*csf)\b",
        instruction, re.IGNORECASE,
    ):
        questions.append("Which framework and version should apply to the assessment?")
    if selected.intersection({"risk_scenarios", "evidence_findings", "control_effectiveness"}):
        questions.append("Which assets, controls and verified evidence can an authorized reviewer provide?")
    return questions[:4]


class SicoAiPlanView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post", "options"]

    def post(self, request, format=None):
        form = SicoAiPlanInput(data=request.data)
        form.is_valid(raise_exception=True)
        instruction = form.validated_data["instruction"]
        organization_hint = form.validated_data.get("organization_hint", "")

        stage_names = [stage.slug for stage in STAGES]
        config = resolve_advisory_capability_config(CAPABILITY_CASE_INTAKE)
        selection = get_advisory_provider_selection(config)
        if selection.provider is None:
            return Response({
                "detail": "The local AI model is not configured for SICO AI planning."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # A single-string JSON contract is deliberately small enough for the
        # installed Qwen 3B model. The old 3-field/enum-list response repeatedly
        # failed backend JSON-schema validation even with Ollama schema format.
        # This is an advisory narrative; actual stage selection stays in code.
        schema = {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
            "additionalProperties": False,
        }
        instructions = (
            "You are SICO AI, an advisor for Saudi cybersecurity GRC work. "
            "NCA ECC means Saudi National Cybersecurity Authority Essential Cybersecurity Controls, "
            "NOT elliptic curve cryptography. "
            "Return a JSON object with exactly one field: answer (a string). "
            "In answer, write a specific, helpful GRC workflow explanation responding to the user's request, "
            "about 3-6 short sentences. For a complete case, describe framework, assets, "
            "controls, evidence, risk, remediation, audit and reporting stages. "
            "Do not invent verified records, evidence, compliance results or authorization. "
            "No GRC action has been executed; human approval will be needed for writes. "
            "An organization name is not required for planning."
        )
        try:
            draft = selection.provider.generate_structured(
                capability=CAPABILITY_CASE_INTAKE,
                model=selection.config.model,
                system_prompt=instructions,
                user_payload={
                    "instruction": instruction,
                    "organization_hint_unverified": organization_hint or None,
                    "full_case_requested": _requests_full_case(instruction),
                    "supported_stages": stage_names,
                },
                json_schema=schema,
                timeout_seconds=min(selection.config.timeout_seconds, 120),
                max_output_tokens=min(selection.config.max_output_tokens, 500),
                temperature=0.1,
                # This intentionally uses Ollama's normal JSON mode plus the
                # backend validator; the same one-field contract already passed
                # a real provider test with Qwen 2.5 3B.
                schema_name="sico_ai_simple_answer_v1",
            )
        except AiProviderExecutionError as exc:
            return Response({
                "detail": "The local AI model failed to generate a workflow plan. No GRC records changed.",
                "error_code": exc.error_code,
            }, status=status.HTTP_502_BAD_GATEWAY)

        if not isinstance(draft, dict) or not isinstance(draft.get("answer"), str):
            return Response({"detail": "The AI did not return a valid GRC advisory answer."},
                            status=status.HTTP_502_BAD_GATEWAY)

        summary = draft["answer"].strip()[:1600]
        if not summary:
            return Response({"detail": "The AI generated an empty advisory answer."},
                            status=status.HTTP_502_BAD_GATEWAY)

        # Registry-defined ordering is authoritative. No arbitrary model-proposed
        # imports, functions, object IDs or database writes are accepted.
        requested = _select_registered_stages(instruction, stage_names)
        steps = []
        for name in stage_names:
            if name not in requested:
                continue
            title, purpose = STAGE_DESCRIPTIONS.get(name, (
                name.replace("_", " ").title(), "Existing reviewed GRC stage"
            ))
            steps.append({
                "stage": name,
                "title": title,
                "purpose": purpose,
                "status": "not_executed",
                "human_approval_required_before_write": True,
            })

        questions = _planning_questions(instruction, requested, organization_hint)
        return Response({
            "mode": "read_only_ai_plan",
            "provider_mode": "configured_local_provider",
            "stage_selection_mode": "deterministic_reviewed_registry",
            "model": selection.config.model,
            "summary": summary,
            "steps": steps,
            "questions": questions,
            "organization_context": {
                "supplied": bool(organization_hint),
                "verified": False,
            },
            "registered_stage_count": len(stage_names),
            "limitations": [
                "No GRC business records were read or written by this planning request.",
                "The model generated the narrative; stage selection uses deterministic reviewed rules, not autonomous tool calls.",
                "These are proposed stages, not executed tasks or verified compliance findings.",
                "Organization provisioning for new companies requires separate authorized setup; it is not in this stage registry.",
                "Execution requires company-scoped permissions, exact-operation human approval and safety testing.",
                "Other platform features not in the registered stage list are not yet connected to the AI coordinator.",
            ],
            "grc_business_records_written": False,
        })
