"""Real-record, no-write whole-engagement work plan using existing GRC models.

This is a plan and backlog, NOT an assessment verdict. Results never imply that a
control is implemented or a requirement is compliant without verified evidence.
"""
from __future__ import annotations

from django.conf import settings
from django.db import transaction

from core.models import (
    AppliedControl, Asset, ComplianceAssessment, Evidence, Perimeter,
    RiskAssessment, RiskScenario, Framework,
)
from iam.models import Folder, RoleAssignment

from .advisory_transaction import advisory_rollback_transaction
from .case_intake_serializers import AiCaseIntakeInputSerializer
from .case_intake_service import build_case_intake_draft
from .engagement_service import authorized_engagement
from .engagement_rules import STAGES

MAX_SCAN = 120
MAX_SHOW = 10


def _readable_rows(user, model, folder_id, *, extra=None):
    qs = model.objects.filter(folder_id=folder_id)
    if extra:
        qs = qs.filter(**extra)
    found = []
    raw = list(qs.order_by('pk')[:MAX_SCAN+1])
    for item in raw[:MAX_SCAN]:
        if RoleAssignment.is_object_readable(user, model, item.pk):
            if len(found) < MAX_SHOW:
                found.append({'id': str(item.pk), 'name': str(item.name)[:160]})
    return {'samples': found, 'scan_limited': len(raw) > MAX_SCAN,
            'note': 'Samples only, not the whole inventory. A listed record is not verified evidence.'}


def assemble_real_engagement_context(user, engagement):
    folder = Folder.objects.filter(pk=engagement.folder_id).first()
    if folder is None or not RoleAssignment.is_object_readable(user, Folder, folder.pk):
        raise PermissionError('Engagement folder unavailable.')
    models = (
        ('perimeters', Perimeter, None),
        ('assets', Asset, None),
        ('policies', AppliedControl, {'category': 'policy'}),
        ('applied_controls', AppliedControl, None),
        ('evidence', Evidence, None),
        ('compliance_assessments', ComplianceAssessment, None),
        ('risk_assessments', RiskAssessment, None),
        ('risk_scenarios', RiskScenario, None),
    )
    inventory = {
        label: _readable_rows(user, model, folder.pk, extra=criteria)
        for label, model, criteria in models
    }
    framework = None
    if engagement.framework_id:
        item = Framework.objects.filter(pk=engagement.framework_id).first()
        if item is not None and RoleAssignment.is_object_readable(user, Framework, item.pk):
            framework = {'id': str(item.pk), 'name': str(item.name)[:200],
                         'ref_id': str(getattr(item,'ref_id','') or '')[:100]}
    return {'organization': {'folder_id': str(folder.pk), 'name': str(folder.name)[:200]},
            'framework': framework, 'inventory': inventory}


def _phase(stage, known_commits=frozenset(), prepared=frozenset()):
    # Not every client's engagement needs every stage. The consultant evaluates
    # applicability; a stage is never silently reported 'complete'.
    depends = {
        'case_setup': [],
        'assets': ['case_setup'],
        'applied_controls': ['assets'],
        'evidence_findings': ['case_setup'],
        'remediation': ['evidence_findings'],
        'framework_control_mappings': ['applied_controls'],
        'risk_scenarios': ['case_setup'],
        'control_effectiveness': ['evidence_findings'],
        'audit_readiness': ['control_effectiveness'],
        'audit_report': ['audit_readiness'],
        'final_review': ['audit_report'],
    }
    dependencies = depends[stage]
    if stage in known_commits:
        state = 'approved_operation_recorded'
    elif stage in prepared:
        state = 'dry_run_prepared'
    elif any(dependency not in known_commits for dependency in dependencies):
        state = 'dependencies_need_review'
    else:
        state = 'ready_for_professional_review'
    return {
        'stage': stage, 'dependencies': dependencies, 'state': state,
        'approval_required_for_writes': True,
        'notice': 'An operation receipt is not proof that all work in this module is complete.',
    }


def prepare_engagement_plan(request, engagement_id, *, use_local_ai=False):
    user = request.user
    engagement = authorized_engagement(user, engagement_id)
    context = assemble_real_engagement_context(user, engagement)
    receipts = list(engagement.executions.values_list('stage', 'status'))
    known_commits = {stage for stage, status in receipts if status == 'committed'}
    prepared = {stage for stage, status in receipts if status == 'prepared'}
    tasks = [_phase(step.slug, known_commits, prepared) for step in STAGES]
    # Manual capabilities exist in the host platform but are NOT all covered by
    # these eleven AI commit services. Do not pretend they were executed.
    additional_workstreams = [
        {'area': 'governance_and_policies', 'state': 'requires_manual_module_integration',
         'manual_route': '/policies', 'note': 'Policy lifecycle, approval and governance evidence'},
        {'area': 'compliance_requirement_assessment', 'state': 'requires_manual_module_integration',
         'manual_route': '/compliance-assessments', 'note': 'Requirement-by-requirement evidence evaluation'},
        {'area': 'third_party_risk', 'state': 'applicability_review_required',
         'manual_route': '/entity-assessments', 'note': 'Vendor due diligence and supplier risk'},
        {'area': 'business_impact_and_continuity', 'state': 'applicability_review_required',
         'manual_route': '/business-impact-analysis', 'note': 'BIA and continuity/recovery evidence'},
        {'area': 'privacy_and_data_protection', 'state': 'applicability_review_required',
         'manual_route': None, 'note': 'Determine privacy-law applicability before a privacy review'},
        {'area': 'incident_readiness', 'state': 'applicability_review_required',
         'manual_route': '/incidents', 'note': 'Incident response governance and incident evidence'},
        {'area': 'framework_reports_and_exports', 'state': 'requires_manual_module_integration',
         'manual_route': '/reports', 'note': 'Formal exports, report sign-off and traceable conclusions'},
    ]
    gaps = []
    if not engagement.compliance_assessment_id:
        gaps.append('Select or establish an authorized compliance assessment before assessing requirements.')
    if not engagement.framework_id:
        gaps.append('Select the exact framework and verify edition and legal applicability.')
    if not context['inventory']['evidence']['samples']:
        gaps.append('No readable evidence found in the bounded sample; request evidence and inspect the full authorized inventory.')
    if any(value['scan_limited'] for value in context['inventory'].values()):
        gaps.append('At least one inventory exceeds its bounded scan; this plan must not conclude missing records.')

    advisory = None
    provider_state = 'not_requested'
    if use_local_ai:
        # Existing provider and validation contract; NO custom or fabricated LLM path.
        # Send the authenticated folder name + bounded, readable inventory titles only.
        inventory_summary = '; '.join(
            f"{key}: " + ', '.join(item['name'] for item in value['samples'])
            for key, value in context['inventory'].items()
        )[:5000]
        intake_data = {
            'scenario_text': (
                f"Conduct an internal GRC engagement for {context['organization']['name']}. "
                f"Objectives: {engagement.objective}. "
                f"Existing permitted records (titles only; NOT verified evidence): {inventory_summary}. "
                'Assess applicability, identify missing evidence and prepare a reviewable GRC work plan. '
                'Do not claim compliance, implemented controls, owner approval or audit closure.'
            )[:20000],
            'organization_hint': context['organization']['name'][:255],
            'preferred_framework': context['framework']['name'] if context['framework'] else '',
            'strict_mode': True,
        }
        serializer = AiCaseIntakeInputSerializer(data=intake_data)
        serializer.is_valid(raise_exception=True)
        with advisory_rollback_transaction():
            advisory = build_case_intake_draft(
                serializer.validated_data, base_dir=str(settings.BASE_DIR.parent)
            )
        provider_state = str(advisory.get('provider_mode') or 'unspecified')

    plan = {
        'kind': 'sico_verified_engagement_backlog_v1',
        'organization': context['organization'],
        'framework': context['framework'],
        'inventory': context['inventory'],
        'stages': tasks,
        'additional_workstreams': additional_workstreams,
        'evidence_and_scope_gaps': gaps,
        'case_intake_advisory': advisory,
        'provider_mode': provider_state,
        'disclaimer': 'Real, RBAC-filtered record TITLES are not proof of implementation. '
                      'This backlog is not an audit conclusion and never certifies compliance.',
        'writes_to_grc_records': False,
    }
    # Recheck permission immediately before writing engagement metadata.
    with transaction.atomic():
        locked = authorized_engagement(user, engagement_id, lock=True)
        locked.plan = plan
        locked.save(update_fields=['plan', 'updated_at'])
    return plan
