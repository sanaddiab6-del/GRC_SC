"""Pure, fail-closed policies for SICO engagement execution.

No Django imports: the policy can be unit-tested without a live database.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class Stage:
    slug: str
    serializer: str
    service: str
    guardrail: str | None = None
    reason: str = ""


# Targets EXISTING, reviewed platform commit services: no new write implementations.
STAGES = (
    Stage('case_setup', 'case_setup_serializers.AiCaseSetupInputSerializer',
          'case_setup_service.execute_case_setup'),
    Stage('assets', 'asset_commit_serializers.AiAssetCommitInputSerializer',
          'asset_commit_service.execute_asset_commit'),
    Stage('applied_controls', 'applied_control_commit_serializers.AiAppliedControlCommitInputSerializer',
          'applied_control_commit_service.execute_applied_control_commit'),
    Stage('evidence_findings', 'evidence_finding_commit_serializers.AiEvidenceFindingCommitInputSerializer',
          'evidence_finding_commit_service.execute_evidence_finding_commit'),
    Stage('remediation', 'remediation_action_commit_serializers.AiRemediationActionCommitInputSerializer',
          'remediation_action_commit_service.execute_remediation_action_commit',
          'remediation_action_commit_guardrails.validate_remediation_action_commit_guardrails'),
    Stage('framework_control_mappings', 'framework_control_mapping_commit_serializers.AiFrameworkControlMappingCommitInputSerializer',
          'framework_control_mapping_commit_service.execute_framework_control_mapping_commit',
          'framework_control_mapping_commit_guardrails.validate_framework_control_mapping_commit_guardrails'),
    Stage('risk_scenarios', 'risk_scenario_commit_serializers.AiRiskScenarioCommitInputSerializer',
          'risk_scenario_commit_service.execute_risk_scenario_commit',
          'risk_scenario_commit_guardrails.validate_risk_scenario_commit_guardrails'),
    Stage('control_effectiveness', 'control_effectiveness_commit_serializers.AiControlEffectivenessCommitInputSerializer',
          'control_effectiveness_commit_service.execute_control_effectiveness_commit',
          'control_effectiveness_commit_guardrails.validate_control_effectiveness_commit_guardrails'),
    Stage('audit_readiness', 'audit_readiness_commit_serializers.AiAuditReadinessCommitInputSerializer',
          'audit_readiness_commit_service.execute_audit_readiness_commit',
          'audit_readiness_commit_guardrails.validate_audit_readiness_commit_guardrails'),
    Stage('audit_report', 'audit_report_commit_serializers.AiAuditReportCommitInputSerializer',
          'audit_report_commit_service.execute_audit_report_commit',
          'audit_report_commit_guardrails.validate_audit_report_commit_guardrails'),
    Stage('final_review', 'final_review_commit_serializers.AiFinalReviewCommitInputSerializer',
          'final_review_commit_service.execute_final_review_commit',
          'final_review_commit_guardrails.validate_final_review_commit_guardrails'),
)

STAGES_BY_NAME = {stage.slug: stage for stage in STAGES}
if len(STAGES_BY_NAME) != len(STAGES):
    raise RuntimeError('Duplicate engagement stage')

# Review flags alone may change between dry-run and approved commit.
# Everything else, including all record IDs, contents and action choices, is bound.
REVIEW_FLAG_FIELDS = frozenset({'dry_run', 'approved', 'approved_by_user', 'human_approved'})


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _canonical(v) for k, v in sorted(value.items())
                if k not in REVIEW_FLAG_FIELDS}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    if isinstance(value, (UUID, date, datetime, Decimal)):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    # An unexpected value must not silently normalize to an uncontrolled object.
    raise ValueError(f'Unsupported value type in reviewed payload: {type(value).__name__}')


def reviewed_payload_digest(payload: dict[str, Any]) -> str:
    """Two payloads match only if their actual intended GRC content matches."""
    if not isinstance(payload, dict):
        raise ValueError('Expected a structured operation payload')
    raw = json.dumps(_canonical(payload), sort_keys=True, ensure_ascii=False,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def _normalize_uuid(value: Any) -> str | None:
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError):
        return None


def scope_is_exact(payload: dict[str, Any], folder_id: Any, stage: str) -> bool:
    """Fail closed: every dispatched operation MUST reference the engagement folder.

    The original service still independently validates every related record and write
    permission. For case setup, the coordinator refuses NEW domain creation entirely.
    """
    wanted = _normalize_uuid(folder_id)
    if not wanted or not isinstance(payload, dict):
        return False
    if stage == 'case_setup':
        decision = payload.get('folder_domain_decision')
        if not isinstance(decision, dict) or decision.get('action') != 'reuse':
            return False
        return _normalize_uuid(decision.get('selected_existing_id')) == wanted
    nested = payload.get('case_setup_reference')
    if isinstance(nested, dict):
        return _normalize_uuid(nested.get('folder_id')) == wanted
    return _normalize_uuid(payload.get('folder_reference')) == wanted


# Statuses verified against the eleven existing *_commit_service.py return paths.
# Fail closed on unexpected strings: a future status must be reviewed before
# it can authorize a write or be called a successful operation.
DRY_RUN_STATUSES = frozenset({'validated', 'validated_with_warnings', 'passed_with_warnings'})
COMMITTED_STATUSES = frozenset({
    'created', 'created_and_reused', 'reused', 'reused_only', 'completed',
    'completed_with_warnings', 'linked_existing_ai',
})


def safe_result(result: Any, *, expected_mode: str | None = None) -> bool:
    """Accept only known states with no blocking errors and matching operation mode."""
    if not isinstance(result, dict) or result.get('blocking_errors'):
        return False
    status = result.get('commit_status', result.get('status'))
    if not isinstance(status, str):
        return False
    state = status.strip().lower()
    if expected_mode == 'dry_run':
        if result.get('dry_run', True) is not True:
            return False
        if result.get('operation_type', 'dry_run') != 'dry_run':
            return False
        return state in DRY_RUN_STATUSES
    if expected_mode == 'commit':
        if result.get('dry_run', False) is not False:
            return False
        if result.get('operation_type', 'commit') == 'dry_run':
            return False
        return state in COMMITTED_STATUSES
    return state in DRY_RUN_STATUSES | COMMITTED_STATUSES


def human_review_flags(payload: dict[str, Any]) -> bool:
    """Outer commit approval plus underlying serializer approval BOTH required."""
    if payload.get('dry_run') is not False:
        return False
    if payload.get('approved') is True or payload.get('approved_by_user') is True:
        return True
    return False


def stage_catalog() -> list[dict[str, str]]:
    return [{'code': s.slug, 'existing_serializer': s.serializer,
             'existing_write_service': s.service} for s in STAGES]
