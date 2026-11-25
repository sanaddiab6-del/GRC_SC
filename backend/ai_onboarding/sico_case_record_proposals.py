"""Prepare SICO MODEL-SHAPED, UNSAVED review records from authorized sources.

This module intentionally has no ORM/network calls. A source requirement is
not evidence, a proposed control is not an implemented control, and Qwen text
is never a completed requirement verdict or risk score. All input framework
rows must first pass the existing SICO RBAC framework loader.

Real writes must later go through SICO serializers/permissions/approval. Do not
pass these dicts directly to a model.save() or bulk-create function.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from ai_onboarding.sico_case_coverage import calculate_proposed_risk

REQUIREMENT_RESULTS = ('not_assessed', 'partially_compliant', 'non_compliant', 'compliant', 'not_applicable')
RISK_TREATMENTS = ('open', 'mitigate', 'accept', 'avoid', 'transfer')


def prepare_requirement_assessments(*, requirement_work_items: Sequence[Mapping],
                                    framework_id: str, source_digest: str) -> list[dict]:
    """One complete unassessed RequirementAssessment-shaped work record/source row.

    The caller must give the *already server-authorized* coverage items.
    Output is not a serializer input or an invitation to persist these records.
    """
    if not framework_id or not source_digest or len(source_digest) != 64:
        raise ValueError('missing_verified_framework_source_identity')
    if not isinstance(requirement_work_items, (list, tuple)) or not requirement_work_items:
        raise ValueError('missing_requirement_work_items')
    seen = set()
    proposals = []
    for item in requirement_work_items:
        if not isinstance(item, Mapping) or item.get('source') != 'authorized_SICO_framework_record':
            raise ValueError('requirement_not_from_authorized_source')
        rid, ref = item.get('requirement_id'), item.get('reference')
        if not isinstance(rid, str) or not rid or not isinstance(ref, str) or not ref or rid in seen:
            raise ValueError('duplicate_or_missing_requirement_identity')
        if (item.get('proposed_result') != 'not_assessed' or
                item.get('proposed_progress') != 'to_do' or
                item.get('evidence_verified') is not False or
                item.get('business_records_written') is not False):
            raise ValueError('unverified_requirement_claim')
        seen.add(rid)
        # Exact field names from existing RequirementAssessment model. A null
        # compliance_assessment is intentionally NOT a valid persistence payload.
        proposals.append({
            'target_model': 'RequirementAssessment',
            'requirement_id': rid,
            'requirement_reference': ref,
            'framework_id': framework_id,
            'source_digest': source_digest,
            'requires_existing_compliance_assessment': True,
            'model_fields': {
                'compliance_assessment': None,
                'requirement': rid,
                'status': 'to_do',
                'result': 'not_assessed',
                'extended_result': None,
                'is_scored': False,
                'score': None,
                'documentation_score': None,
                'evidences': [],
                'applied_controls': [],
                'observation': None,
                'answers': None,
                'security_exceptions': [],
                'selected': True,
            },
            'assessment_justification': item.get('assessment_justification', ''),
            'applicability': 'pending_human_review',
            'evidence_request': item.get('evidence_to_request', ''),
            'review_method': item.get('review_method', ''),
            'related_review_draft_refs': list(item.get('requirement_review_draft_refs', [])),
            'evidence_verified': False,
            'human_review_required': True,
            'compliance_verdict_made': False,
            'business_records_written': False,
        })
    return proposals


def _attribute_map(draft: Mapping) -> dict[str,str]:
    result = {}
    for attribute in draft.get('proposed_attributes', ()):
        if not isinstance(attribute, Mapping):
            continue
        field = attribute.get('field')
        if isinstance(field, str) and isinstance(attribute.get('proposed_value'), str):
            result[field] = attribute['proposed_value'].strip()
    return result


def enrich_quality_draft_result(result: dict, *, chosen_requirement: Mapping | None = None) -> dict:
    """Add conservative domain-model field candidates to the existing v7 Qwen draft.

    Does not alter existing keys, wire schema, v7 checkpoint identity, or links.
    The output is a new dict so callers do not observe partial enrichment.
    """
    if not isinstance(result, dict) or result.get('business_records_written') is not False:
        raise ValueError('invalid_unsaved_quality_record')
    draft = result.get('draft')
    if not isinstance(draft, Mapping) or draft.get('status') != 'new_unsaved_ai_draft_pending_verification':
        raise ValueError('invalid_draft_status')
    activity = result.get('activity_code')
    packet = dict(result)
    enriched = dict(draft)
    attrs = _attribute_map(draft)
    if activity == 'threats':
        asset = attrs.get('asset_reference')
        if not asset or asset not in enriched.get('related_draft_references', []):
            raise ValueError('threat_asset_link_missing')
        # The weakness text is Qwen's hypothesis, never a proven vulnerability.
        # Map it to existing model fields without inventing a second narrative.
        enriched['threat_proposal'] = {
            'target_model':'Threat', 'source_draft_reference':enriched['draft_reference'],
            'model_fields':{'name':enriched['title'], 'description':enriched['content']},
            'candidate_asset_draft_reference':asset, 'business_records_written':False,
        }
        enriched['vulnerability_proposal'] = {
            'target_model':'Vulnerability', 'source_draft_reference':enriched['draft_reference'],
            'model_fields':{'name':attrs.get('weakness_hypothesis',''),
                            'description':attrs.get('weakness_hypothesis',''), 'status':'potential'},
            'candidate_asset_draft_reference':asset, 'evidence_verified':False,
            'derived_from_model_generated_hypothesis':True, 'business_records_written':False,
        }
    if activity == 'requirement_reviews':
        if (not isinstance(chosen_requirement, Mapping) or
                enriched.get('authorized_requirement_id') != chosen_requirement.get('requirement_id') or
                attrs.get('framework_requirement_reference') != chosen_requirement.get('reference')):
            raise ValueError('requirement_review_unmatched_authorized_source')
        enriched['requirement_assessment_proposal'] = {
            'target_model': 'RequirementAssessment',
            'requirement_id': chosen_requirement['requirement_id'],
            'requirement_reference': chosen_requirement['reference'],
            'model_fields': {
                'compliance_assessment': None, 'requirement': chosen_requirement['requirement_id'],
                'status': 'to_do', 'result': 'not_assessed', 'extended_result': None,
                'is_scored': False, 'score': None, 'documentation_score': None,
                'evidences': [], 'applied_controls': [], 'observation': None,
                'answers': None, 'security_exceptions': [], 'selected': True,
            },
            'review_method': attrs.get('review_method',''),
            'evidence_needed': attrs.get('evidence_needed',''),
            'review_status_from_model_unverified': attrs.get('review_status',''),
            'evidence_verified': False, 'human_review_required': True,
            'compliance_verdict_made': False, 'business_records_written': False,
        }
    if activity == 'risk_scenarios':
        treatment = attrs.get('treatment_option', '').lower()
        # Treatment must remain unselected when the provider writes prose
        # instead of an actual SICO treatment option.
        treatment = treatment if treatment in RISK_TREATMENTS else None
        asset = attrs.get('asset_reference')
        refs = enriched.get('related_draft_references') or []
        linked_asset = asset if asset in refs else None
        enriched['risk_scenario_assessment_proposal'] = {
            'target_model': 'RiskScenario',
            'risk_assessment': None,
            'risk_matrix': None,
            'model_fields': {
                'inherent_proba': -1, 'inherent_impact': -1, 'inherent_level': -1,
                'current_proba': -1, 'current_impact': -1, 'current_level': -1,
                'residual_proba': -1, 'residual_impact': -1, 'residual_level': -1,
                'strength_of_knowledge': -1, 'treatment': treatment,
            },
            'candidate_asset_draft_reference': linked_asset,
            'asset_reference_requires_manual_resolution': bool(asset and not linked_asset),
            'requires_authorized_risk_assessment_and_matrix': True,
            'requires_assessor_likelihood_impact_inputs': True,
            'requires_verified_existing_controls_for_current_risk': True,
            'requires_effectiveness_evidence_for_actual_residual_risk': True,
            'risk_ratings_verified': False,
            'business_records_written': False,
        }
    if activity == 'residual_risk':
        risks = [r for r in enriched.get('related_draft_references', [])
                 if isinstance(r, str) and r.startswith('draft-06-')]
        enriched['residual_risk_assessment_proposal'] = {
            'target_model': 'RiskScenario',
            'candidate_risk_draft_references': risks,
            'treatment_assumptions': attrs.get('treatment_assumptions', ''),
            'reassessment_method': attrs.get('reassessment_method',''),
            'acceptance_authority_role': attrs.get('acceptance_authority',''),
            'residual_proba': -1, 'residual_impact': -1, 'residual_level': -1,
            'projected_only': True,
            'requires_matrix_and_approved_treatment_evidence': True,
            'risk_acceptance_approved': False,
            'human_review_required': True,
            'business_records_written': False,
        }
    packet['draft'] = enriched
    return packet


def score_authorized_risk_proposal(*, trusted_matrix_definition: Mapping,
                                   inherent: Mapping | None = None,
                                   current: Mapping | None = None,
                                   residual: Mapping | None = None,
                                   verified_current_controls: bool = False,
                                   treatment_implemented_and_verified: bool = False) -> dict:
    """Server-injected authorized RiskMatrix json_definition ONLY.

    This function intentionally does not resolve a matrix from user input; a
    trusted SICO caller must fetch it with tenant RBAC and ownership checks.
    """
    return calculate_proposed_risk(
        matrix_definition=trusted_matrix_definition,
        inherent=inherent, current=current, residual=residual,
        verified_current_controls=verified_current_controls,
        treatment_implemented_and_verified=treatment_implemented_and_verified,
    )
