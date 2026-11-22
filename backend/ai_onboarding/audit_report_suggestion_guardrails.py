from __future__ import annotations

from typing import Any


# Step 11A is advisory/no-write. These keys would imply a write, a committed record, an
# automatic approval, a published report, an audit closure, or a compliance certification
# and are therefore forbidden anywhere in the request payload or the generated draft.
FORBIDDEN_KEYS = {
    "create_now",
    "auto_create",
    "auto_approve",
    "approve_automatically",
    "approve_report",
    "approved",
    "approved_by_user",
    "approved_fields",
    "create_records",
    "create_report",
    "save_report",
    "publish_report",
    "export_report",
    "mark_report_final",
    "report_final",
    "sign_report",
    "commit",
    "committed",
    "dry_run",
    "idempotency_key",
    "report_id",
    "document_id",
    "evidence_id",
    "compliance_assessment_id",
    "requirement_assessment_id",
    "risk_assessment_id",
    "risk_scenario_id",
    "applied_control_id",
    "finding_id",
    "asset_id",
    "framework_id",
    "compliance_result",
    "final_result",
    "final_compliance_result",
    "final_audit_opinion",
    "audit_opinion",
    "final_risk_decision",
    "risk_acceptance",
    "risk_decision",
    "audit_closure",
    "close_audit",
    "accept_risk",
    "certify_compliance",
    "certification",
}

OUT_OF_SCOPE_TOKENS = (
    "final audit opinion",
    "our final opinion",
    "we hereby certify",
    "we certify",
    "certify compliance",
    "certified compliant",
    "is hereby certified",
    "regulator approved",
    "regulator-approved",
    "approved by the regulator",
    "audit is closed",
    "close audit",
    "audit closure",
    "risk acceptance is granted",
)

REQUIRED_DRAFT_FIELDS = (
    "report_title",
    "report_sections",
    "executive_summary",
    "limitations",
    "recommended_next_steps",
    "review_status",
)

REQUIRED_SECTION_FIELDS = ("heading", "content", "source_items", "confidence")

REQUIRED_REVIEW_STATUS = "pending_review"

# Step 11A must always say out loud that the draft needs human review. A draft without
# that statement reads like a finished audit product, so it is rejected.
HUMAN_REVIEW_TOKENS = ("human review", "human-review", "reviewed by a human", "manual review")

# Step 11A is required to disclaim exactly the things it must not assert, so "this is not a
# final audit opinion" has to be allowed while "our final audit opinion is ..." is rejected.
# An occurrence is treated as a disclaimer when a negation appears shortly before it.
NEGATION_MARKERS = (
    "not",
    "never",
    "no ",
    "nothing",
    "cannot",
    "can not",
    "without",
    "rather than",
    "instead of",
)

# How far back to look for the negation that turns an occurrence into a disclaimer.
NEGATION_LOOKBEHIND_CHARS = 60


class AuditReportSuggestionDraftValidationError(Exception):
    def __init__(self, error_code: str, detail: str, errors: list[str] | dict[str, Any]):
        super().__init__(detail)
        self.status_code = 422
        self.error_code = error_code
        self.detail = detail
        self.errors = errors

    def to_response(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "detail": self.detail,
            "errors": self.errors,
        }


def asserts_out_of_scope_language(text: str) -> bool:
    """True when the text states an out-of-scope conclusion rather than disclaiming one.

    The Step 11A draft is required to say that it is not a final audit opinion and not a
    certification, so a negated mention is the wanted language. Only an unnegated mention
    is an actual out-of-scope claim.
    """
    lowered = (text or "").lower()
    for token in OUT_OF_SCOPE_TOKENS:
        start = lowered.find(token)
        while start != -1:
            window = lowered[max(0, start - NEGATION_LOOKBEHIND_CHARS) : start]
            if not any(marker in window for marker in NEGATION_MARKERS):
                return True
            start = lowered.find(token, start + 1)
    return False


def validate_audit_report_suggestion_request_guardrails(
    payload: dict[str, Any],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for field in FORBIDDEN_KEYS:
        if field in payload:
            errors[field] = ["This field is not allowed in Step 11A."]
    return errors


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def validate_audit_report_suggestion_guardrails(draft: dict[str, Any]) -> None:
    errors: list[str] = []

    for forbidden_key in FORBIDDEN_KEYS:
        if forbidden_key in draft:
            errors.append(f"Forbidden top-level key in Step 11A draft: {forbidden_key}")

    for key in _walk_keys(draft):
        if key in FORBIDDEN_KEYS:
            errors.append(f"Forbidden key found in Step 11A draft: {key}")

    overall_confidence = draft.get("overall_confidence")
    if not isinstance(overall_confidence, (int, float)) or isinstance(overall_confidence, bool):
        errors.append("overall_confidence must be a number between 0 and 1.")
    elif not 0.0 <= float(overall_confidence) <= 1.0:
        errors.append("overall_confidence must be between 0 and 1.")

    for field in REQUIRED_DRAFT_FIELDS:
        if field not in draft or draft.get(field) is None:
            errors.append(f"{field} is required in Step 11A.")

    report_title = draft.get("report_title")
    if report_title is not None and (
        not isinstance(report_title, str) or not report_title.strip()
    ):
        errors.append("report_title must be a non-empty string.")

    executive_summary = draft.get("executive_summary")
    if executive_summary is not None and not isinstance(executive_summary, str):
        errors.append("executive_summary must be a string.")

    for field in ("limitations", "recommended_next_steps"):
        value = draft.get(field)
        if value is None:
            continue
        if not isinstance(value, list):
            errors.append(f"{field} must be a list.")
            continue
        if any(not isinstance(entry, str) or not entry.strip() for entry in value):
            errors.append(f"{field} must only contain non-empty strings.")

    limitations = draft.get("limitations")
    if isinstance(limitations, list):
        if not limitations:
            errors.append(
                "limitations must not be empty in Step 11A: the draft must state its own "
                "limitations."
            )
        elif not any(
            isinstance(entry, str)
            and any(token in entry.lower() for token in HUMAN_REVIEW_TOKENS)
            for entry in limitations
        ):
            errors.append(
                "limitations must state that human review is required before the report "
                "draft is used."
            )

    review_status = draft.get("review_status")
    if review_status is not None and review_status != REQUIRED_REVIEW_STATUS:
        errors.append(f"review_status must be '{REQUIRED_REVIEW_STATUS}' in Step 11A.")

    sections = draft.get("report_sections")
    if not isinstance(sections, list):
        if sections is not None:
            errors.append("report_sections must be a list.")
        raise AuditReportSuggestionDraftValidationError(
            "ai_audit_report_suggestion_guardrails_failed",
            "Generated advisory audit report draft violated Step 11A guardrails.",
            errors,
        )

    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            errors.append(f"report_sections[{index}] must be an object.")
            continue

        for field in REQUIRED_SECTION_FIELDS:
            if field not in section or section.get(field) is None:
                errors.append(f"report_sections[{index}].{field} is required in Step 11A.")

        heading = section.get("heading")
        if heading is not None and (not isinstance(heading, str) or not heading.strip()):
            errors.append(f"report_sections[{index}].heading must be a non-empty string.")

        content = section.get("content")
        if content is not None and not isinstance(content, str):
            errors.append(f"report_sections[{index}].content must be a string.")

        source_items = section.get("source_items")
        if source_items is not None:
            if not isinstance(source_items, list):
                errors.append(f"report_sections[{index}].source_items must be a list.")
            elif any(
                not isinstance(entry, str) or not entry.strip() for entry in source_items
            ):
                errors.append(
                    f"report_sections[{index}].source_items must only contain non-empty strings."
                )

        confidence = section.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                errors.append(
                    f"report_sections[{index}].confidence must be a number between 0 and 1."
                )
            elif not 0.0 <= float(confidence) <= 1.0:
                errors.append(f"report_sections[{index}].confidence must be between 0 and 1.")

    # Each passage is scanned on its own so a negation in one never excuses an assertion
    # in another.
    passages = [
        str(draft.get("report_title") or ""),
        str(draft.get("executive_summary") or ""),
        *[
            str(section.get("content") or "")
            for section in sections
            if isinstance(section, dict)
        ],
        *[str(entry) for entry in (draft.get("limitations") or []) if isinstance(entry, str)],
    ]
    if any(asserts_out_of_scope_language(passage) for passage in passages):
        errors.append(
            "The Step 11A report draft contains out-of-scope final audit opinion, "
            "certification, regulator-approval, or closure language."
        )

    if errors:
        raise AuditReportSuggestionDraftValidationError(
            "ai_audit_report_suggestion_guardrails_failed",
            "Generated advisory audit report draft violated Step 11A guardrails.",
            errors,
        )
