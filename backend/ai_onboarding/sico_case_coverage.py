"""SICO AI case coverage and risk-rating preparation (no database writes).

Inputs must be provided by a SERVER-SIDE caller after normal SICO tenant/RBAC checks.
A framework name, organization string, draft ID, or user-supplied matrix UUID is
never sufficient authorization to retrieve or mutate business records.

This module deliberately does NOT call the local model, ORM, network, or writer.
It creates exactly one *unassessed work item* per authorized requirement and
uses the same matrix grid indexing as core.models.risk_scoring. The outputs are
planning artefacts, not compliance decisions, measured risk or approval.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from copy import deepcopy
import re
from typing import Mapping, Sequence

SCHEMA = 'sico-ai-coverage-plan-v1'
RESULTS = frozenset({'not_assessed', 'partially_compliant', 'non_compliant', 'compliant', 'not_applicable'})
PROGRESS = frozenset({'to_do', 'in_progress', 'in_review', 'done'})
RISK_PARTS = ('inherent', 'current', 'residual')


def _text(obj: object, *, limit: int = 4000) -> str:
    return str(obj or '').strip()[:limit]


def _normalized_source(requirements: Sequence[Mapping]) -> list[dict]:
    if isinstance(requirements, (str, bytes)) or not isinstance(requirements, (list, tuple)):
        raise ValueError('authorized_requirements_must_be_sequence')
    if not requirements or len(requirements) > 10000:
        raise ValueError('invalid_authorized_requirement_count')
    rows, ids, refs = [], set(), set()
    for original in requirements:
        if not isinstance(original, Mapping):
            raise ValueError('invalid_authorized_requirement')
        rid = _text(original.get('requirement_id'), limit=128)
        ref = _text(original.get('reference'), limit=128)
        if not rid or not ref or rid in ids or ref in refs:
            raise ValueError('missing_or_duplicate_authorized_requirement_identity')
        ids.add(rid); refs.add(ref)
        rows.append({
            'requirement_id': rid,
            'reference': ref,
            'description': _text(original.get('description')),
            'requirement_name': _text(original.get('requirement_name'), limit=250),
        })
    return rows


def _draft_coverage(prior_drafts: Sequence[Mapping], allowed_ids: set[str]) -> dict[str, list[str]]:
    """Only source-identified *drafts* qualify as drafted; never as verified."""
    result = {}
    for item in prior_drafts or ():
        if not isinstance(item, Mapping):
            continue
        draft = item.get('draft') or {}
        if (not isinstance(draft, Mapping) or item.get('activity_number') != 10
                or item.get('activity_code') != 'requirement_reviews'
                or item.get('business_records_written') is not False):
            continue
        rid = _text(draft.get('authorized_requirement_id'), limit=128)
        ref = _text(draft.get('draft_reference'), limit=128)
        if rid in allowed_ids and ref and draft.get('status') == 'new_unsaved_ai_draft_pending_verification':
            result.setdefault(rid, []).append(ref)
    return result


def make_coverage_plan(*, organization: str, framework: str, objective: str,
                       authorized_requirements: Sequence[Mapping],
                       source_digest: str, framework_id: str,
                       prior_drafts: Sequence[Mapping] = (),
                       selected_requirement_ids: Sequence[str] | None = None) -> dict:
    """Plan every in-scope authorized requirement, preserving evidence uncertainty.

    `selected_requirement_ids` is an OPTIONAL trusted scope/implementation-group
    determination from the SICO server, NEVER an arbitrary client-selected list.
    If omitted, every authorized source row is included, with applicability TBD.
    """
    org, fw, goal = _text(organization, limit=150), _text(framework, limit=150), _text(objective)
    if len(org) < 2 or len(fw) < 2 or len(goal) < 20:
        raise ValueError('invalid_case_scope')
    if not framework_id or not source_digest:
        raise ValueError('missing_authorized_source_identity')
    rows = _normalized_source(authorized_requirements)
    authorized = {r['requirement_id'] for r in rows}
    if selected_requirement_ids is not None:
        selected = set(selected_requirement_ids)
        if not selected or not selected.issubset(authorized):
            raise ValueError('scope_contains_unauthorized_requirement')
        scoped = [r for r in rows if r['requirement_id'] in selected]
    else:
        scoped = rows
    drafted = _draft_coverage(prior_drafts, {r['requirement_id'] for r in scoped})
    items = []
    for row in scoped:
        ref, rid, desc = row['reference'], row['requirement_id'], row['description']
        items.append({
            'requirement_id': rid,
            'reference': ref,
            'description': desc,
            'requirement_name': row['requirement_name'],
            'applicability': 'pending_human_review',
            'proposed_result': 'not_assessed',
            'proposed_progress': 'to_do',
            'assessment_justification': 'No verified implementation and evidence review has been provided.',
            'review_method': 'Obtain applicable implementation details, inspect supporting evidence, test effectiveness where relevant, and record a justified result.',
            'evidence_to_request': (
                'Request demonstrable implementation and review evidence specifically addressing: '
                + (desc[:380] if desc else f'framework requirement {ref}')
            ),
            'evidence_verified': False,
            'requirement_review_draft_refs': drafted.get(rid, []),
            'review_draft_present': bool(drafted.get(rid)),
            'human_review_required': True,
            'source': 'authorized_SICO_framework_record',
            'business_records_written': False,
        })
    # Existing SICO RequirementAssessment fields, left explicitly unresolved.
    # Lazy import avoids a circular module import with the matrix adapter.
    from .sico_case_record_proposals import prepare_requirement_assessments
    requirement_proposals = prepare_requirement_assessments(
        requirement_work_items=items, framework_id=str(framework_id),
        source_digest=str(source_digest))
    return {
        'schema': SCHEMA,
        'scope': {'organization': org, 'framework': fw, 'objective': goal},
        'framework_id': _text(framework_id, limit=128),
        'source_digest': _text(source_digest, limit=128),
        'coverage': {
            'authorized_requirements_loaded': len(rows),
            'requirements_in_scope_pending_confirmation': len(scoped),
            'requirements_considered_for_review': len(scoped),
            'requirement_review_drafts_present': sum(x['review_draft_present'] for x in items),
            'requirement_results_verified': 0,
            'requirement_results_unassessed': len(scoped),
            'requirements_needing_evidence_or_applicability_review': len(scoped),
            'full_framework_assessed': False,
        },
        'requirement_work_items': items,
        'requirement_assessment_proposals': requirement_proposals,
        'generation_policy': {
            'approach': 'coverage_driven_not_fixed_one_per_activity',
            'requirement_review_queue': [x['requirement_id'] for x in items if not x['review_draft_present']],
            'other_activity_counts': 'determined_from_authorized_scope_assets_risks_evidence_and_verified_gaps',
            'no_fabricated_findings_or_compliance': True,
            'no_database_writes': True,
        },
        'business_records_written': False,
        'full_case_blueprint': __import__(
            'ai_onboarding.sico_full_case_blueprint', fromlist=['build_full_case_blueprint']
        ).build_full_case_blueprint(
            organization=org, framework=fw, objective=goal,
            authorized_requirements=scoped, framework_id=str(framework_id),
            source_digest=str(source_digest),
        ),
        **{key:value for key,value in plan_generation_queue(
            authorized_requirements=scoped, objective=goal).items() if key != 'schema'},
        'generation_queue_schema': 'sico-ai-dynamic-generation-queue-v1',
    }


# Named security domains identify *candidate GRC work*, not real customer facts.
# Each selection must be justified by the authorized framework text. The
# dictionary is a transparent relevance heuristic rather than a substitute for
# existing tenant-scoped asset/evidence inventories.
GENERATION_DOMAINS = (
    ('governance', r'\b(governance|strategy|steering committee|roles and responsibilities|risk management|accountability)\b'),
    ('identity_and_access', r'\b(access control|identity|authentication|authorization|privileg|password|mfa|user access)\b'),
    ('asset_inventory', r'\b(asset|inventory|classification|ownership of information|hardware|software)\b'),
    ('data_protection', r'\b(data protection|data classif|data loss|privacy|information protection|confidentiality|personal information|sensitive)\b'),
    ('network_security', r'\b(network|firewall|perimeter|segmentation|wireless|dns|remote access)\b'),
    ('incident_response', r'\b(incident|event response|forensic|cyber attack|security breach)\b'),
    ('backup_and_recovery', r'\b(backup|restore|recovery|continuity|disaster|resilien)\b'),
    ('vulnerability_management', r'\b(vulnerabilit|patch|penetration test|configuration|hardening|malware)\b'),
    ('monitoring_and_logging', r'\b(logs?|monitoring|detection|siem|audit trail|alerts?)\b'),
    ('third_party_risk', r'\b(third.party|supplier|vendor|outsourc|contractor|service provider)\b'),
    ('cloud_security', r'\b(cloud|virtualization|container|hosting)\b'),
    ('application_security', r'\b(application|software development|secure coding|web|change management)\b'),
    ('people_and_training', r'\b(training|awareness|personnel|employee|human resources|screening)\b'),
    ('physical_security', r'\b(physical|facility|site security|environmental|equipment)\b'),
    ('cryptography', r'\b(encrypt|cryptograph|key management|certificate|tls)\b'),
)

# Activities 4–16 already exist in SICO. A domain-specific slot is a prompt
# focus, not a claim that its candidate asset/control exists or is required.
ASSET_DOMAINS = frozenset({
    'identity_and_access', 'asset_inventory', 'data_protection',
    'network_security', 'backup_and_recovery', 'vulnerability_management',
    'monitoring_and_logging', 'third_party_risk', 'cloud_security',
    'application_security', 'physical_security', 'cryptography'
})


def explicit_scope_subjects(objective: str) -> list[str]:
    """Literal user-supplied scope lists, never an invented industry inventory."""
    match = re.search(r'\b(?:scope|systems|services|assets|processes)\s*:\s*(.+)',objective,re.I|re.S)
    if not match:
        return []
    subjects = []
    for part in re.split(r'[;,\n]+',match.group(1)):
        subject = part.strip(' .-\t')
        if (3 <= len(subject) <= 200 and subject.casefold() not in {s.casefold() for s in subjects}
                and not re.match(r'^(assess|identify|generate|improve|ensure)\b',subject,re.I)):
            subjects.append(subject)
    return subjects if len(subjects) > 1 else []


def plan_generation_queue(*, authorized_requirements: Sequence[Mapping],
                          objective: str, max_slots_per_activity: int = 10000) -> dict:
    """Build a bounded, non-uniform, source-linked Qwen work queue.

    Every authorized requirement receives a review slot. The API permits up
    to 10,000 slots per activity; an explicitly smaller execution window
    reports overflow without counting it as completed work.
    """
    if type(max_slots_per_activity) is not int or not 1 <= max_slots_per_activity <= 10000:
        raise ValueError('invalid_quality_api_slot_limit')
    rows = _normalized_source(authorized_requirements)
    objective_text = _text(objective).casefold()
    themes: dict[str, list[dict]] = {name: [] for name, _ in GENERATION_DOMAINS}
    for row in rows:
        text = (row['requirement_name'] + ' ' + row['description']).casefold()
        for name, pattern in GENERATION_DOMAINS:
            if re.search(pattern, text):
                themes[name].append(row)
    active = [(name, hits) for name, hits in themes.items() if hits]
    # Prioritize objective-specific domains; fall back to stable source order.
    active.sort(key=lambda item: (
        0 if item[0].replace('_', ' ') in objective_text else 1,
        -len(item[1]), item[1][0]['reference'], item[0]
    ))
    # An empty topic classification is possible with specialized frameworks.
    # Use a sourced requirement, not an invented control or organizational fact.
    if not active:
        active = [('unclassified_requirement', rows)]
    assets = [(name, hits) for name, hits in active if name in ASSET_DOMAINS]
    if not assets:
        # Review the scope's first source requirement. This is not a verified
        # organizational asset, merely a proposed discovery candidate.
        assets = active[:1]
    subjects = explicit_scope_subjects(objective)
    if subjects:
        scoped_assets = []
        for subject in subjects:
            words = set(re.findall(r'\w{4,}',subject.casefold()))
            # Authorized source focus is context, not a confirmed mapping.
            name,hits = max(active,key=lambda topic:len(words & set(re.findall(
                r'\w{4,}',' '.join(r['description']+' '+r['requirement_name'] for r in topic[1]).casefold()))))
            scoped_assets.append((name,hits,subject))
        assets = scoped_assets
    risk = assets
    controls = (assets + [(name,hits) for name,hits in active
                          if name not in {item[0] for item in assets}]) if subjects else active
    policy = [(name, hits) for name, hits in active if name not in {'asset_inventory'}] or active[:1]
    # An audit finding without evidence is ONLY a potential review question.
    # A report/approval package is an aggregate, not one per requirement.
    per_activity = {
        4: assets, 5: risk, 6: risk, 7: controls, 8: policy,
        9: controls, 10: active, 11: active, 12: risk,
        13: controls, 14: active[:1], 15: risk, 16: active[:1],
    }
    # Qwen detail drafts for Activity 10 only sample DISTINCT requirements;
    # the full framework coverage plan has a separate row for EVERY record.
    candidates = {}
    for step, domain_list in per_activity.items():
        candidates[step] = []
        for item in domain_list:
            name,hits = item[:2]
            subject = item[2] if len(item)>2 else ''
            # Use an actual authorized requirement as the immutable source focus.
            row = hits[0]
            candidates[step].append({
                'activity_number': step,
                'draft_index': len(candidates[step]) + 1,
                'theme': name,
                'scope_subject': subject,
                'focus_requirement_reference': row['reference'],
                'focus_requirement_id': row['requirement_id'],
                'reason': 'Source-linked proposed work; organizational facts and implementation require verification',
            })
    # Every actual source requirement receives a Qwen review slot. Planning
    # never counts these pending slots as generated or evidence-assessed.
    candidates[10] = []
    for row in rows:
        theme = next((name for name, hits in active if row in hits), active[0][0])
        candidates[10].append({
            'activity_number': 10, 'draft_index': len(candidates[10])+1,
            'theme': theme, 'focus_requirement_reference': row['reference'],
            'focus_requirement_id': row['requirement_id'],
            'reason': 'Review this exact authorized requirement; evidence and applicability remain unverified',
        })
    def ref(step, index):
        return f'draft-{step:02d}-{index:02d}'
    def parent(step, slot):
        eligible = [s for s in candidates[step] if s['theme']==slot['theme']
                    and s['draft_index'] <= max_slots_per_activity]
        exact = [s for s in eligible if s.get('scope_subject','')==slot.get('scope_subject','')]
        # Never attach a risk/control to another explicit scope item's asset.
        eligible = exact or [s for s in eligible if not s.get('scope_subject') or not slot.get('scope_subject')]
        return ref(step,eligible[0]['draft_index']) if eligible else None
    # Only related topics share a chain. Governance work does not acquire an
    # arbitrary technology risk merely because that risk was generated first.
    parent_steps = {4: (), 5: (4,), 6: (4,5), 7: (4,6), 8: (7,),
                    9: (4,7), 10: (7,9), 11: (9,10), 12: (6,7,11),
                    13: (7,9,12), 14: (), 15: (6,12), 16: ()}
    for step, slots in candidates.items():
        for slot in slots:
            slot['draft_reference'] = ref(step, slot['draft_index'])
            slot['dependency_draft_references'] = list(dict.fromkeys(
                p for dep in parent_steps[step] if (p := parent(dep,slot))))
    candidates[14][0]['dependency_draft_references'] = [ref(3,1),ref(10,1),ref(13,1)]
    candidates[16][0]['dependency_draft_references'] = [ref(3,1),ref(6,1),ref(10,1),ref(11,1),ref(12,1),ref(15,1)]
    for slot in candidates[15]:
        slot['dependency_draft_references'].append(ref(14,1))
    queue = [{
        'activity_number': step, 'draft_index': 1, 'draft_reference': ref(step,1),
        'theme': ('framework_scope','business_scope','compliance_assessment')[step-1],
        'focus_requirement_reference': rows[0]['reference'],
        'focus_requirement_id': rows[0]['requirement_id'],
        'dependency_draft_references': [ref(parent_step,1) for parent_step in range(1,step)],
        'reason': 'Prepare this organization and selected framework assessment scope with Qwen',
    } for step in (1,2,3)]
    # Finish each category's required inventory before moving downstream.
    for activity in range(4,17):
        queue.extend(candidates[activity][:max_slots_per_activity])
    for slot in queue:
        slot['task_identity'] = hashlib.sha256(repr((slot['activity_number'],slot['draft_index'],
            slot.get('scope_subject',''),slot['theme'],slot['focus_requirement_id'],
            slot['dependency_draft_references'])).encode()).hexdigest()
    return {
        'schema': 'sico-ai-dynamic-generation-queue-v1',
        'generation_queue': queue,
        'generation_summary': {
            'authorized_source_requirements': len(rows),
            'identified_source_topics': len(active),
            'explicit_scope_subjects': subjects,
            'scope_detail_status': 'explicit_user_scope_requires_verification' if subjects else 'framework_topics_only_scope_inventory_needs_confirmation',
            'planned_qwen_detail_drafts': len(queue),
            'activity_targets': {**{str(step):1 for step in (1,2,3)},
                                 **{str(step): min(len(x), max_slots_per_activity)
                                 for step, x in candidates.items()}},
            'source_topic_overflow_not_queued': {str(step): max(0, len(x)-max_slots_per_activity)
                                                 for step, x in candidates.items()},
            'all_requirements_covered_by_unassessed_work_queue': True,
            'all_requirements_scheduled_for_qwen_review': len(candidates[10]) <= max_slots_per_activity,
            'qwen_draft_limit_is_transport_cap_not_scope_completeness': True,
            'organizational_assets_verified': False,
            'compliance_verdicts_verified': 0,
            'risk_matrix_selected': False,
            'business_records_written': False,
        },
    }


def _validate_matrix(matrix: Mapping) -> tuple[list, list, list, list]:
    if not isinstance(matrix, Mapping):
        raise ValueError('risk_matrix_is_required')
    probabilities, impacts, levels, grid = (matrix.get(k) for k in ('probability', 'impact', 'risk', 'grid'))
    if not all(isinstance(x, list) and 1 <= len(x) <= 100 for x in (probabilities, impacts, levels, grid)):
        raise ValueError('invalid_risk_matrix_definition')
    if len(grid) != len(probabilities):
        raise ValueError('risk_grid_probability_axis_mismatch')
    for row in grid:
        if not isinstance(row, list) or len(row) != len(impacts):
            raise ValueError('risk_grid_impact_axis_mismatch')
        if any(type(idx) is not int or not (0 <= idx < len(levels)) for idx in row):
            raise ValueError('risk_grid_invalid_level_index')
    return probabilities, impacts, levels, grid


def calculate_proposed_risk(*, matrix_definition: Mapping,
                            inherent: Mapping | None = None,
                            current: Mapping | None = None,
                            residual: Mapping | None = None,
                            verified_current_controls: bool = False,
                            treatment_implemented_and_verified: bool = False) -> dict:
    """Exact SICO grid lookups; no AI-calculated risk scores.

    All numeric coordinates must be supplied from independently proposed and
    reviewable risk ratings; this code never invents them. Current exposures
    require trusted existing-control verification; residual outputs are only
    projections until treatment is implemented and effectiveness checked.
    """
    p, i, levels, grid = _validate_matrix(matrix_definition)
    result = {'status': 'unsaved_risk_proposal', 'business_records_written': False,
              'matrix_levels': len(levels), 'strength_of_knowledge': 'pending_verification'}
    for part, value in [('inherent', inherent), ('current', current), ('residual', residual)]:
        if value is None:
            result[part] = {'status': 'awaiting_rating_inputs', 'level_index': None}
            continue
        if not isinstance(value, Mapping):
            raise ValueError(f'invalid_{part}_rating')
        prob, impact = value.get('probability'), value.get('impact')
        if (type(prob) is not int or type(impact) is not int or
                not 0 <= prob < len(p) or not 0 <= impact < len(i)):
            raise ValueError(f'{part}_outside_selected_matrix')
        if part == 'current' and not verified_current_controls:
            result[part] = {'status': 'awaiting_verified_current_controls', 'level_index': None}
            continue
        label = 'proposed_unverified'
        if part == 'residual':
            label = ('post_treatment_requires_human_review' if treatment_implemented_and_verified
                     else 'projected_after_proposed_treatment')
        result[part] = {
            'status': label, 'probability_index': prob, 'impact_index': impact,
            'level_index': grid[prob][impact],
            'source': 'selected_SICO_risk_matrix_grid',
        }
    return result
