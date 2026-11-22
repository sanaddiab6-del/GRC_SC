"""SICO AI lifecycle policy: one selected framework, a durable 16-part program.

A recorded writer operation is NOT proof that a control has been tested or an
assessment concluded compliant. Non-writer workstreams must remain visible.
No database access in this module; the workflow view checks fresh permissions.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Activity:
    code: str
    title: str
    stage: str | None
    prerequisite: str | None = None
    needs_evidence: bool = False


# The user supplied these 16 professional tasks. The mappings identify the
# existing write-service family, NOT proof that every subtask was fulfilled.
ACTIVITIES = (
    Activity('01_framework', 'Verify manually selected framework and edition', None),
    Activity('02_scope', 'Confirm assessment scope and responsibilities', 'case_setup'),
    Activity('03_compliance_case', 'Create compliance assessment', 'case_setup'),
    Activity('04_assets_controls', 'Register assets and current security controls', 'assets', 'case_setup'),
    Activity('05_threats', 'Document evidenced threats and vulnerabilities', 'risk_scenarios', 'assets', True),
    Activity('06_risks', 'Evaluate risk scenarios', 'risk_scenarios', 'case_setup', True),
    Activity('07_mapping', 'Map controls to exact framework requirements', 'framework_control_mappings', 'applied_controls', True),
    Activity('08_audit_compliance', 'Assess requirement-level audit compliance', 'audit_readiness', 'case_setup', True),
    Activity('09_evidence', 'Request, collect and review evidence', 'evidence_findings', 'case_setup', True),
    Activity('10_justifications', 'Record documented compliance justification', None, 'case_setup', True),
    Activity('11_findings', 'Record findings and nonconformities', 'evidence_findings', 'case_setup', True),
    Activity('12_remediation', 'Assign remediation actions and owners', 'remediation', 'evidence_findings', True),
    Activity('13_retest', 'Retest control effectiveness', 'control_effectiveness', 'applied_controls', True),
    Activity('14_approval', 'Review and approve assessment conclusions', 'final_review', 'audit_readiness', True),
    Activity('15_residual_risk', 'Record residual risk treatment and acceptance', None, 'risk_scenarios', True),
    Activity('16_reports', 'Generate management and audit reports', 'audit_report', 'audit_readiness', True),
)

# Order is advisory and revisitable; approvals and dependencies are evaluated
# against actual completed service receipts on each user action.
SERVICE_SEQUENCE = (
    'case_setup', 'assets', 'applied_controls', 'risk_scenarios',
    'framework_control_mappings', 'evidence_findings', 'remediation',
    'control_effectiveness', 'audit_readiness', 'final_review', 'audit_report',
)


def lifecycle_snapshot(*, folder_id, framework_id, assessment_id, receipts):
    """Return *operation* progress, never infer compliance from a receipt."""
    by_stage = {}
    for r in receipts:
        by_stage.setdefault(r.stage, []).append(r)
    all_stages = []
    for stage in SERVICE_SEQUENCE:
        matching = by_stage.get(stage, [])
        if any(r.status == 'committed' for r in matching):
            state = 'approved_operation_recorded'
        elif any(r.status == 'prepared' and r.approved_by_id for r in matching):
            state = 'approved_awaiting_commit'
        elif any(r.status == 'prepared' for r in matching):
            state = 'prepared_awaiting_review'
        else:
            state = 'not_prepared'
        all_stages.append({'stage': stage, 'state': state})
    states = {row['stage']: row['state'] for row in all_stages}
    tasks = []
    for a in ACTIVITIES:
        stage_state = states.get(a.stage)
        if a.code == '01_framework':
            state = 'user_selected_not_regulator_verified' if framework_id else 'framework_required'
        elif a.stage is None:
            state = 'separate_evidence_review_required'
        elif a.code == '04_assets_controls' and (
                states.get('assets') != 'approved_operation_recorded' or
                states.get('applied_controls') != 'approved_operation_recorded'):
            state = 'asset_and_control_operations_both_required'
        elif stage_state == 'approved_operation_recorded':
            state = 'operation_recorded_not_professional_signoff'
        elif stage_state in ('prepared_awaiting_review', 'approved_awaiting_commit'):
            state = stage_state
        elif a.prerequisite and states.get(a.prerequisite) != 'approved_operation_recorded':
            state = 'prerequisite_operation_required'
        elif a.needs_evidence:
            state = 'verified_evidence_and_input_required'
        else:
            state = 'ready_for_proposal'
        tasks.append({'code': a.code, 'title': a.title, 'stage': a.stage,
                      'state': state, 'requires_evidence': a.needs_evidence})
    remaining = [s for s in SERVICE_SEQUENCE if states[s] == 'not_prepared']
    return {
        'folder_id': str(folder_id), 'framework_id': str(framework_id) if framework_id else None,
        'compliance_assessment_id': str(assessment_id) if assessment_id else None,
        'lifecycle': tasks, 'writer_stages': all_stages,
        'remaining_stages': remaining,
        'compliance_verdict': 'not_established', 'case_complete': False,
        'note': 'Writer receipts are verified transactions, NOT evidence review, control effectiveness, compliance, or management sign-off.',
    }


def eligible_stage(receipts):
    """Return one next unprepared stage; stop at the first approval/commit gate."""
    status = {r.stage: r.status for r in receipts}
    if status.get('case_setup') != 'committed':
        return None, 'The initial assessment must be explicitly reviewed, approved and saved first.'
    for stage in SERVICE_SEQUENCE[1:]:
        if status.get(stage) == 'committed':
            continue
        if status.get(stage) == 'prepared':
            return None, f'{stage} already has a prepared operation awaiting human review.'
        # For assets there may be no existing inventory and the model can propose
        # names; for other stages the downstream serializer verifies prerequisites.
        return stage, None
    return None, 'All reviewed writer families have a receipt; professional evidence and conclusion checks remain necessary.'
