"""Build a complete, editable SICO RiskMatrix *proposal* from scoped risk context.

The matrix is organization/case-wide so ratings remain comparable. Each risk
scenario is separately assessed on this matrix. No model/ORM/network/writes.
All organizational risk-profile inputs MUST be authorized and server-resolved.
Requirements and candidate risk patterns are signals of *potential* exposure,
not evidence of the organization's actual assets or controls.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import re

from ai_onboarding.sico_case_coverage import _validate_matrix

SCHEMA = 'sico-complete-proposed-risk-matrix-v2'

_PROBABILITY_NAMES = {
    2: ['Unlikely', 'Likely'],
    3: ['Unlikely', 'Possible', 'Likely'],
    4: ['Rare', 'Unlikely', 'Possible', 'Likely'],
    5: ['Rare', 'Unlikely', 'Possible', 'Likely', 'Almost certain'],
    6: ['Exceptional', 'Rare', 'Unlikely', 'Possible', 'Likely', 'Almost certain'],
    7: ['Exceptional', 'Very rare', 'Rare', 'Unlikely', 'Possible', 'Likely', 'Almost certain'],
}
_IMPACT_NAMES = {
    2: ['Limited', 'Severe'],
    3: ['Limited', 'Material', 'Severe'],
    4: ['Minor', 'Moderate', 'Major', 'Critical'],
    5: ['Negligible', 'Minor', 'Moderate', 'Major', 'Critical'],
    6: ['Negligible', 'Minor', 'Moderate', 'Significant', 'Major', 'Critical'],
    7: ['Negligible', 'Very minor', 'Minor', 'Moderate', 'Significant', 'Major', 'Critical'],
}
_LEVELS_4 = [
    ('Low', '#5FA983', 'Routine monitoring; the final response depends on approved appetite'),
    ('Moderate', '#E9CD65', 'Treatment decision or monitored exception requires case owner review'),
    ('High', '#EC9A57', 'Escalation and a documented treatment decision are normally warranted'),
    ('Critical', '#CF5960', 'Urgent review and risk treatment or restriction may be needed'),
]
_LEVELS_5 = [
    ('Very low', '#459F77', 'Baseline monitoring; confirm within approved appetite'),
    ('Low', '#93C57F', 'Routine owner monitoring and periodic review'),
    ('Moderate', '#E7C65C', 'Review controls and agree an appropriate treatment'),
    ('High', '#E48F54', 'Escalate treatment priority and review residual exposure'),
    ('Critical', '#D35A62', 'Urgent treatment and authorized management review'),
]
_AXIS_COLORS = ['#73B78A', '#A4CC83', '#E4D26F', '#E6B466', '#E99863', '#E47663', '#CF5960']
_IMPACT_DIMENSIONS = {
    'data_protection': 'Confidentiality and privacy impact',
    'cryptography': 'Confidentiality and integrity impact',
    'identity_and_access': 'Unauthorized access and privilege impact',
    'backup_and_recovery': 'Service continuity and recovery impact',
    'incident_response': 'Response and containment impact',
    'physical_security': 'Physical safety, facility and service impact',
    'network_security': 'Service availability and lateral movement impact',
    'third_party_risk': 'Supplier service, concentration and contractual impact',
    'cloud_security': 'Hosted service, privacy and availability impact',
    'application_security': 'Application integrity, data and availability impact',
    'governance': 'Legal, regulatory, accountability and strategic impact',
}


def _shape_from_profile(domains: Sequence[str], trusted_profile: Mapping | None):
    """Propose precision from identified case scope; do not infer approval.

    A trusted methodology profile may request explicit axes. Without one,
    security-domain diversity only yields a *draft* complexity recommendation.
    """
    profile = trusted_profile or {}
    if not isinstance(profile, Mapping):
        raise ValueError('risk_profile_must_be_server_authorized_mapping')
    shape = profile.get('matrix_shape')
    if shape is not None:
        if not isinstance(shape, str) or not re.fullmatch(r'[2-7]x[2-7]', shape):
            raise ValueError('invalid_matrix_shape')
        p, i = (int(v) for v in shape.split('x'))
        return p, i, 'explicit_authorized_risk_methodology_request'
    if profile.get('requires_detailed_impact_axis') is True:
        return 4, 6, 'proposed_higher_impact_granularity_from_authorized_context'
    if profile.get('requires_six_level_precision') is True:
        return 6, 6, 'proposed_finer_resolution_from_authorized_context'
    n = len(set(domains))
    if n <= 2:
        return 3, 3, 'provisional_simple_scope_heuristic'
    if n <= 6:
        return 4, 4, 'provisional_moderate_scope_heuristic'
    return 5, 5, 'provisional_broad_scope_heuristic'


def generate_case_risk_matrix(*, organization: str, objective: str,
                              risk_domains: Sequence[str],
                              trusted_risk_profile: Mapping | None = None) -> dict:
    """Create an actual SICO json_definition plus its approval-ready metadata.

    No scenario gets a verified risk rating just because a matrix was created.
    The case reviewer must validate methodology, appetite and domain assumptions.
    """
    if not isinstance(risk_domains, (list, tuple)):
        raise ValueError('risk_domains_must_be_sequence')
    domains = [str(x) for x in risk_domains if isinstance(x, str) and x.strip()]
    p_count, i_count, shape_reason = _shape_from_profile(domains, trusted_risk_profile)
    levels = _LEVELS_4 if max(p_count, i_count) <= 4 else _LEVELS_5
    impact_dimensions = sorted({ _IMPACT_DIMENSIONS[d] for d in domains if d in _IMPACT_DIMENSIONS })
    if not impact_dimensions:
        impact_dimensions = ['Operational, financial, confidentiality, integrity and availability impact']
    p_axis = [
        {'name': name, 'abbreviation': f'P{k+1}', 'hexcolor': _AXIS_COLORS[round(k*6/max(p_count-1,1))],
         'description': f'Ordinal likelihood band {k+1}/{p_count}, subject to an agreed exposure horizon and documented threat conditions. No assumed incident frequency.'}
        for k, name in enumerate(_PROBABILITY_NAMES[p_count])
    ]
    i_axis = [
        {'name': name, 'abbreviation': f'I{k+1}', 'hexcolor': _AXIS_COLORS[round(k*6/max(i_count-1,1))],
         'description': f'Ordinal consequence band {k+1}/{i_count}; calibrate using organization-approved thresholds for: {"; ".join(impact_dimensions)}.'}
        for k, name in enumerate(_IMPACT_NAMES[i_count])
    ]
    risk_axis = [
        {'name': name, 'abbreviation': f'R{k+1}', 'hexcolor': color, 'description': description}
        for k, (name, color, description) in enumerate(levels)
    ]
    # The grid consists of zero-based indexes into risk_axis (SICO's actual contract).
    # The number of risk bands is generated from proposed methodology precision.
    thresholds = ((0.08, 0.20, 0.40, 0.67) if len(risk_axis) == 5 else (0.13, 0.32, 0.62))
    def band(pi, ii):
        normalized = (pi + 1) * (ii + 1) / (p_count * i_count)
        return sum(normalized > threshold for threshold in thresholds)
    grid = [[band(pi, ii) for ii in range(i_count)] for pi in range(p_count)]
    definition = {'probability': p_axis, 'impact': i_axis, 'risk': risk_axis, 'grid': grid}
    _validate_matrix(definition)
    if any(not level.get('name') or not level.get('hexcolor') for axis in ('probability','impact','risk') for level in definition[axis]):
        raise ValueError('incomplete_sico_risk_matrix_axis')
    # Risk scores should rise monotonically with impact or likelihood.
    if any(grid[p][i] > grid[p+1][i] for p in range(p_count-1) for i in range(i_count)) or any(grid[p][i] > grid[p][i+1] for p in range(p_count) for i in range(i_count-1)):
        raise ValueError('nonmonotonic_risk_grid')
    return {
        'schema': SCHEMA, 'draft_reference': 'proposal-risk-matrix-001',
        'target_model': 'RiskMatrix',
        'title': f'Proposed {p_count}×{i_count} cybersecurity risk methodology for {organization.strip()}',
        'name': f'{organization.strip()} proposed cyber risk matrix {p_count}x{i_count}',
        'description': f'Unapproved organization-specific matrix proposal for objective: {objective.strip()[:240]}',
        'json_definition': definition, 'editing_draft': definition,
        # The existing RiskMatrixViewSet.create_draft endpoint accepts these
        # fields. The server MUST bind a tenant-owned folder and enforce add
        # permission; never let the model choose an arbitrary folder ID.
        'reviewed_create_draft_payload': {
            'name': f'{organization.strip()} proposed cyber risk matrix {p_count}x{i_count}',
            'description': f'Unapproved methodology proposal for: {objective.strip()[:240]}',
            'editing_draft': definition,
            'folder': None,
        },
        'creation_requires_server_authorized_folder': True,
        'creation_requires_human_approval': True,
        'creation_api_sequence': ['RiskMatrixViewSet.create_draft', 'RiskMatrixViewSet.publish_draft'],
        'is_enabled': False, 'approved': False,
        'status': 'proposed_requires_owner_review',
        'risk_tolerance': None, 'risk_appetite': 'pending_authorized_decision',
        'likelihood_horizon': 'to_be_approved_by_risk_owner',
        'impact_dimensions_to_calibrate': impact_dimensions,
        'probability_count': p_count, 'impact_count': i_count,
        'methodology_selection_basis': shape_reason,
        'assessment_guide': {
            'inherent': 'Rate the threat event before safeguards from evidence and stated assumptions',
            'current': 'Rate after *verified existing* controls, otherwise leave unresolved',
            'residual': 'Project after proposed treatment; measured residual needs implementation evidence',
            'comparison': 'Use the same approved case matrix for all risk scenarios; do not use a different scale for each threat',
        },
        'methodology_requires_validation': True,
        'business_records_written': False,
        'notice': 'Full editable SICO matrix definition, NOT an approved or stored matrix. Calibrate names, thresholds, likelihood horizon and risk appetite before using formal ratings.',
    }
