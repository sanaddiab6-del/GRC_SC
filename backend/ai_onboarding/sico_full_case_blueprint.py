"""Prepare an interconnected, FULL-SCOPE, UNSAVED SICO GRC case blueprint.

This is *not* a completed compliance assessment or evidence-backed risk register.
All framework rows and optional organization context MUST first be authorized by
SICO's tenant/membership/RBAC APIs. Never call this with client-supplied records.
No network/ORM/LLM, no writes, no approvals. It is a domain-specific job plan
for Qwen drafting and human review, not a fabricated organizational inventory.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import re

from ai_onboarding.sico_case_coverage import _normalized_source, GENERATION_DOMAINS

SCHEMA = 'sico-full-case-proposed-records-v1'

# A bounded, transparent hypothesis catalog. These are *conditional* attack and
# control-failure patterns, never factual claims about an organization. Unlike
# one-record-per-activity generation, multiple distinct scenarios per asset
# domain are produced whenever the authorized framework supports that domain.
DOMAIN_CASES = {
    'identity_and_access': ('Identity and access service', (
        ('Credential phishing', 'Stolen credentials could enable unauthorized account access', 'Unverified resistance to credential phishing and token abuse'),
        ('Privilege escalation', 'Overprivileged accounts could change sensitive configurations', 'Unverified privileged access restrictions and monitoring'),
        ('Dormant account misuse', 'Inactive access could be reused after staff changes', 'Unverified account deprovisioning and periodic reviews'))),
    'asset_inventory': ('Technology asset inventory', (
        ('Unmanaged device', 'Unknown systems could remain outside security management', 'Unverified discovery and asset ownership coverage'),
        ('Unsupported software', 'Unsupported software could expose known vulnerabilities', 'Unverified lifecycle and end-of-support tracking'))),
    'data_protection': ('Sensitive information repository', (
        ('Data disclosure', 'Excessive access could expose confidential information', 'Unverified information access and classification safeguards'),
        ('Data alteration', 'Unauthorized changes could corrupt important records', 'Unverified integrity controls and recovery procedures'))),
    'network_security': ('Corporate network gateway', (
        ('Unauthorized lateral movement', 'Weak segmentation could widen the impact of a compromise', 'Unverified segmentation and network-access enforcement'),
        ('Gateway compromise', 'Misconfiguration could permit unauthorized network traffic', 'Unverified firewall configuration and patch practices'))),
    'incident_response': ('Incident monitoring and response service', (
        ('Undetected intrusion', 'Security events could go unnoticed or untriaged', 'Unverified alert coverage and response procedures'),
        ('Delayed containment', 'Delayed escalation could increase the impact of incidents', 'Unverified incident decision authority and exercises'))),
    'backup_and_recovery': ('Backup and recovery service', (
        ('Ransomware recovery failure', 'Unusable backups could prolong operational disruption', 'Unverified restore testing and protected backup copies'),
        ('Backup data exposure', 'Weak backup protections could expose retained information', 'Unverified backup encryption and access controls'))),
    'vulnerability_management': ('Vulnerability management service', (
        ('Unpatched exploitation', 'A reachable unpatched component could be exploited', 'Unverified patch timelines and remediation evidence'),
        ('Insecure configuration', 'Weak baseline configuration could create exploit paths', 'Unverified configuration standard and drift detection'))),
    'monitoring_and_logging': ('Security logging platform', (
        ('Missing audit trail', 'Insufficient logs could prevent incident reconstruction', 'Unverified log collection and retention'),
        ('Log tampering', 'Attackers could erase or alter useful security evidence', 'Unverified log access and integrity protection'))),
    'third_party_risk': ('Third-party service connection', (
        ('Supplier compromise', 'Supplier access could expose business systems', 'Unverified third-party onboarding and access review'),
        ('Supplier service outage', 'A supplier failure could disrupt essential operations', 'Unverified concentration and resilience measures'))),
    'cloud_security': ('Cloud-hosted workload', (
        ('Cloud exposure', 'Incorrect sharing configuration could expose systems or data', 'Unverified cloud configuration governance'),
        ('Cloud identity misuse', 'Leaked cloud credentials could permit unauthorized changes', 'Unverified secrets management and privileged access'))),
    'application_security': ('Business application', (
        ('Application vulnerability', 'A software weakness could expose information or service access', 'Unverified secure development and vulnerability testing'),
        ('Unsafe software change', 'An unreviewed release could introduce damaging defects', 'Unverified release approval and rollback practices'))),
    'people_and_training': ('Workforce access process', (
        ('Social engineering', 'Deceptive requests could lead to credential compromise', 'Unverified role-based awareness and reporting'),
        ('Insider misuse', 'Misuse of legitimate access could expose information', 'Unverified supervision and separation of duties'))),
    'physical_security': ('Information processing facility', (
        ('Unauthorized facility access', 'Physical entry could expose equipment and information', 'Unverified facility entry and visitor controls'),
        ('Environmental disruption', 'Power or climate failure could interrupt services', 'Unverified physical resilience measures'))),
    'cryptography': ('Encryption and key-management service', (
        ('Key compromise', 'Exposed cryptographic keys could undermine confidentiality', 'Unverified key custody and rotation'),
        ('Weak transport encryption', 'Improper encryption could expose transferred information', 'Unverified cryptographic configuration standards'))),
    'governance': ('Cybersecurity governance process', (
        ('Unmanaged risk decision', 'Unclear ownership could delay treatment of material risks', 'Unverified governance accountability'),
        ('Unapproved security exception', 'Unsupported exceptions could leave significant exposures', 'Unverified exception review and expiry governance'))),
}


def proposed_starter_matrix() -> dict:
    """Backwards-compatible proposal helper; not the full case-driven path."""
    from ai_onboarding.sico_case_matrix_methodology import generate_case_risk_matrix
    return generate_case_risk_matrix(
        organization='New organization',
        objective='Proposed cybersecurity risk assessment methodology',
        risk_domains=['governance', 'identity_and_access', 'network_security',
                      'data_protection', 'backup_and_recovery', 'cloud_security',
                      'incident_response'],
    )


def _matches_domain(row: Mapping) -> list[str]:
    text = (row['requirement_name'] + ' ' + row['description']).casefold()
    matches = [name for name, pattern in GENERATION_DOMAINS if re.search(pattern, text)]
    return matches or ['unclassified_requirement']


def _record(ref, model, title, **values):
    return {
        'draft_reference': ref, 'target_model': model, 'title': title,
        'status': 'proposed_unverified', 'evidence_verified': False,
        'human_review_required': True, 'business_records_written': False,
        **values,
    }


def build_full_case_blueprint(*, organization: str, framework: str, objective: str,
                              authorized_requirements: Sequence[Mapping],
                              framework_id: str, source_digest: str,
                              authorized_assets: Sequence[Mapping] = (),
                              approved_matrix: Mapping | None = None,
                              trusted_risk_profile: Mapping | None = None) -> dict:
    """Create new, linked, multi-record GRC drafts for all authorized requirements.

    `authorized_assets` must come ONLY from a SICO IAM-scoped server query; a
    user-entered organization label alone is not permission for such a query.
    A supplied matrix must be server-resolved and approved by a human; this
    function never treats user-submitted JSON as a trusted approved matrix.
    """
    if len((organization or '').strip()) < 2 or len((framework or '').strip()) < 2 or len((objective or '').strip()) < 20:
        raise ValueError('invalid_case_scope')
    if not framework_id or not re.fullmatch('[a-f0-9]{64}', source_digest or ''):
        raise ValueError('missing_verified_framework_source')
    rows = _normalized_source(authorized_requirements)
    if not isinstance(authorized_assets, (list, tuple)):
        raise ValueError('authorized_assets_must_be_sequence')
    if approved_matrix is not None:
        from ai_onboarding.sico_case_coverage import _validate_matrix
        _validate_matrix(approved_matrix)  # Validate, do not score hypothetical inputs.

    items: dict[str, list[dict]] = {
        'assets': [], 'threats': [], 'vulnerabilities': [], 'risk_scenarios': [],
        'applied_controls': [], 'policies': [], 'evidence_requests': [],
        'requirement_assessments': [], 'finding_investigations': [],
        'remediation_actions': [], 'control_effectiveness_tests': [],
        'risk_treatment_plans': [], 'residual_risk_reassessments': [],
        'human_review_packages': [], 'management_reports': [],
    }
    by_domain: dict[str, list[dict]] = {}
    for row in rows:
        for dom in _matches_domain(row):
            by_domain.setdefault(dom, []).append(row)
    # There is no claim a hypothetical asset exists in the organization.
    for idx, (dom, hits) in enumerate(by_domain.items(), 1):
        source_refs = [r['reference'] for r in hits]
        source_ids = [r['requirement_id'] for r in hits]
        asset_name, patterns = DOMAIN_CASES.get(dom, (
            f'{dom.replace("_", " ").title()} process',
            (('Requirement-related control failure',
              'Failure to implement the documented requirement could expose the related business process',
              'Implementation status and technical applicability are unknown'),),
        ))
        asset_ref = f'case-asset-{idx:03d}'
        items['assets'].append(_record(
            asset_ref, 'Asset', f'Candidate: {asset_name}',
            source_domain=dom, framework_references=source_refs,
            organizational_fact_verified=False, owner_role='To be confirmed',
            discovery_request=f'Identify actual in-scope systems/processes relevant to: {", ".join(source_refs[:6])}',
        ))
        pol_ref = f'case-policy-{idx:03d}'
        items['policies'].append(_record(
            pol_ref, 'Policy', f'Proposed {dom.replace("_", " ")} policy',
            requirement_ids=source_ids, framework_references=source_refs,
            proposed_sections=['Purpose and scope', 'Mandatory requirements', 'Accountability',
                               'Monitoring and evidence', 'Exceptions', 'Periodic review'],
            linked_control_draft_references=[], approval_status='not_approved',
            mandatory_provisions=[{'requirement_reference': r['reference'], 'proposed_mandate': r['description'] or r['requirement_name']} for r in hits],
            owner_role='To be appointed', approval_role='Authorized organization management',
            content_generation_needed=True,
        ))
        for pidx, (event, consequence, weakness) in enumerate(patterns, 1):
            tref = f'case-threat-{idx:03d}-{pidx:02d}'
            vref = f'case-vulnerability-{idx:03d}-{pidx:02d}'
            rref = f'case-risk-{idx:03d}-{pidx:02d}'
            items['threats'].append(_record(
                tref, 'Threat', f'Hypothesis: {event}', asset_draft_references=[asset_ref],
                source_requirement_ids=source_ids, threat_event=event,
                potential_consequence=consequence, hypothesis_only=True,
            ))
            items['vulnerabilities'].append(_record(
                vref, 'Vulnerability', f'Potential weakness: {weakness}',
                asset_draft_references=[asset_ref], threat_draft_references=[tref],
                status='potential', unverified=True,
                investigation=f'Check whether the proposed weakness exists in {asset_name}',
            ))
            items['risk_scenarios'].append(_record(
                rref, 'RiskScenario', f'Risk hypothesis: {event} affecting {asset_name}',
                scenario=consequence, asset_draft_references=[asset_ref],
                threat_draft_references=[tref], vulnerability_draft_references=[vref],
                source_requirement_ids=source_ids,
                model_fields={
                    'risk_assessment': None,
                    'inherent_proba': -1, 'inherent_impact': -1, 'inherent_level': -1,
                    'current_proba': -1, 'current_impact': -1, 'current_level': -1,
                    'residual_proba': -1, 'residual_impact': -1, 'residual_level': -1,
                    'strength_of_knowledge': -1, 'treatment': 'open',
                },
                matrix_assessment_required=True, treatment_options=['mitigate','accept','avoid','transfer'],
                actual_risk_claimed=False,
            ))
            items['risk_treatment_plans'].append(_record(
                f'case-treatment-{idx:03d}-{pidx:02d}', 'RiskScenario',
                f'Potential mitigation for {event}',
                risk_draft_references=[rref], control_draft_references=[],
                treatment='mitigate', implementation_status='proposed_not_implemented',
                risk_owner=None, due_date=None, evidence_of_completion=None,
            ))
            items['residual_risk_reassessments'].append(_record(
                f'case-residual-{idx:03d}-{pidx:02d}', 'RiskScenario',
                f'Projected residual risk review for {event}',
                risk_draft_references=[rref],
                prerequisite='Approved matrix, implemented treatment, verified control effectiveness',
                residual_probability=-1, residual_impact=-1, residual_level=-1,
                risk_acceptance_approved=False, projected_only=True,
            ))
    # One distinct source-bound control and evidence request per in-scope
    # requirement: a completeness floor, not one policy/risk per requirement.
    domain_policy_refs = {d: f'case-policy-{i:03d}' for i, d in enumerate(by_domain, 1)}
    domain_risk_refs = {d: [r['draft_reference'] for r in items['risk_scenarios'] if r['draft_reference'].startswith(f'case-risk-{i:03d}-')]
                        for i, d in enumerate(by_domain, 1)}
    for idx, row in enumerate(rows, 1):
        dom = _matches_domain(row)[0]
        cref, eref, aref, test_ref = (f'case-control-{idx:04d}', f'case-evidence-{idx:04d}',
                                     f'case-remediation-{idx:04d}', f'case-control-test-{idx:04d}')
        base = row['description'] or row['requirement_name'] or row['reference']
        policy_links = [domain_policy_refs[d] for d in _matches_domain(row)]
        for policy in items['policies']:
            if policy['draft_reference'] in policy_links:
                policy['linked_control_draft_references'].append(cref)
        for treatment in items['risk_treatment_plans']:
            if any(r in treatment['risk_draft_references'] for r in domain_risk_refs[dom]):
                treatment['control_draft_references'].append(cref)
        items['applied_controls'].append(_record(
            cref, 'AppliedControl', f'Proposed control for {row["reference"]}',
            requirement_id=row['requirement_id'], requirement_reference=row['reference'],
            control_objective=base[:650], policy_draft_references=policy_links,
            related_risk_draft_references=domain_risk_refs[dom],
            design_and_implementation='To be drafted and confirmed against actual organizational systems',
            implemented=False, effectiveness_verified=False,
        ))
        items['evidence_requests'].append(_record(
            eref, 'Evidence', f'Evidence request for {row["reference"]}',
            requirement_id=row['requirement_id'], requirement_reference=row['reference'],
            applied_control_draft_references=[cref],
            acceptance_criteria=f'Current, authentic, reviewable proof addressing: {base[:470]}',
            evidence_received=False, document_identifiers=[],
        ))
        items['requirement_assessments'].append(_record(
            f'case-requirement-{idx:04d}', 'RequirementAssessment',
            f'Assessment of {row["reference"]}',
            requirement_id=row['requirement_id'], requirement_reference=row['reference'],
            framework_id=framework_id,
            applied_control_draft_references=[cref], evidence_request_draft_references=[eref],
            model_fields={'compliance_assessment': None, 'requirement': row['requirement_id'],
                          'status': 'to_do', 'result': 'not_assessed', 'extended_result': None,
                          'evidences': [], 'applied_controls': [], 'observation': None,
                          'is_scored': False, 'score': None, 'documentation_score': None},
            applicability='pending_review',
            verdict_justification='No trusted organizational implementation evidence evaluated.',
            compliance_verdict_made=False,
        ))
        items['control_effectiveness_tests'].append(_record(
            test_ref, 'AppliedControl', f'Test control for {row["reference"]}',
            control_draft_references=[cref], requirement_id=row['requirement_id'],
            test_procedure=f'Obtain evidence, sample implementation and test whether: {base[:400]}',
            test_executed=False, test_result=None,
        ))
        # These are conditional *investigations*, not confirmed audit findings.
        items['finding_investigations'].append(_record(
            f'case-finding-check-{idx:04d}', 'Finding', f'Investigate gap in {row["reference"]}',
            requirement_id=row['requirement_id'], evidence_request_draft_references=[eref],
            finding_confirmed=False, condition='Only open as a finding after evidence supports non-compliance',
        ))
        items['remediation_actions'].append(_record(
            aref, 'TaskNode', f'Proposed response to any confirmed gap in {row["reference"]}',
            requirement_id=row['requirement_id'], control_draft_references=[cref],
            finding_investigation_draft_references=[f'case-finding-check-{idx:04d}'],
            condition='Activate only after verified deficiency and owner approval',
            owner=None, due_date=None, closure_evidence_required=True,
        ))
    items['human_review_packages'].append(_record(
        'case-human-review-001', 'ComplianceAssessment',
        f'{organization.strip()} GRC case sign-off package',
        proposed_review_scope='Framework applicability, evidence quality, risk methodology, control effectiveness, and approval decisions',
        pending_compliance_results=len(rows), signed_off=False,
    ))
    items['management_reports'].append(_record(
        'case-management-report-001', 'ComplianceAssessment',
        f'{organization.strip()} proposed GRC case management report',
        sections=['Scope and authorized framework', 'Unassessed requirement coverage',
                  'Candidate assets and scenarios', 'Unverified risk ratings',
                  'Proposed control and policy coverage', 'Evidence backlog',
                  'Human review and treatment decisions'],
        verified_compliance_count=0, confirmed_findings_count=0, report_final=False,
    ))
    # A risk matrix and both assessments are NEW case proposals even for a
    # blank organization. Existing approved context can be reused, not required.
    from ai_onboarding.sico_case_matrix_methodology import generate_case_risk_matrix
    risk_matrix = None if approved_matrix is not None else generate_case_risk_matrix(
        organization=organization, objective=objective,
        risk_domains=list(by_domain.keys()), trusted_risk_profile=trusted_risk_profile,
    )
    # These are concrete matrix definitions, not single numeric "risk scores".
    # A risk rating is a *separate* scenario-specific assessment against the matrix.
    for record in items['risk_scenarios']:
        record['risk_matrix_draft_reference'] = risk_matrix['draft_reference'] if risk_matrix else None
        record['assessment_method'] = 'SICO RiskScenario inherent/current/residual indexes against selected approved RiskMatrix'
        record['risk_rating_inputs_pending'] = {
            'inherent_probability': 'Threat exposure and attack feasibility evidence required',
            'inherent_impact': 'Affected asset and business consequence evidence required',
            'current_probability_impact': 'Verify existing applied controls before rating',
            'projected_residual_probability_impact': 'Propose after treatment with explicit assumptions',
        }
        record['matrix_risk_level_pending'] = True
    result = {
        'schema': SCHEMA,
        'scope': {'organization': organization.strip(), 'framework': framework.strip(), 'objective': objective.strip()},
        'framework_id': framework_id, 'source_digest': source_digest,
        'risk_matrix_proposal': risk_matrix,
        'risk_matrix_source': 'authorized_existing_approved_matrix' if approved_matrix is not None else 'proposed_new_not_approved',
        'risk_assessment_proposal': _record('case-risk-assessment-001', 'RiskAssessment',
            f'{organization.strip()} cybersecurity risk assessment',
            risk_matrix_draft_reference=risk_matrix['draft_reference'] if risk_matrix else None,
            existing_matrix_must_be_bound_by_authorized_server=approved_matrix is not None,
            risk_tolerance=None, approved=False),
        'compliance_assessment_proposal': _record('case-compliance-assessment-001', 'ComplianceAssessment',
            f'{organization.strip()} {framework.strip()} compliance assessment',
            framework_id=framework_id, covered_requirement_ids=[r['requirement_id'] for r in rows],
            assessment_status='to_do', approved=False),
        'records': items,
        'coverage': {
            'authorized_framework_requirements': len(rows),
            'requirements_with_unassessed_reviews': len(items['requirement_assessments']),
            'requirements_with_proposed_controls': len(items['applied_controls']),
            'requirements_with_evidence_requests': len(items['evidence_requests']),
            'confirmed_noncompliance_findings': 0,
            'requirements_assessed_from_verified_evidence': 0,
            'verified_organizational_assets': len(authorized_assets),
            'candidate_assets': len(items['assets']),
            'risk_scenarios_with_verified_ratings': 0,
            'case_complete': False,
        },
        'generation_summary': {k: len(v) for k, v in items.items()},
        'generation_status': 'structured_full_scope_draft_blueprint_requires_qwen_evidence_and_human_review',
        'next_actions': [
            'Resolve authorized organization systems and risk ownership',
            'Review or approve the proposed risk methodology and risk appetite',
            'Generate substantive policy/control contents with local Qwen for unique source-linked proposals',
            'Review actual evidence and determine each requirement result',
            'Assign and validate inherent/current/projected residual ratings using approved SICO matrix',
            'Create actual findings/remediation only if gaps are supported by evidence',
            'Persist records through tenant-scoped approval services only',
        ],
        'business_records_written': False,
    }
    validate_full_case_blueprint(result)
    return result


def validate_full_case_blueprint(packet: Mapping) -> None:
    """Fail closed if a generated package fabricates verified results or links."""
    if packet.get('business_records_written') is not False:
        raise ValueError('blueprint_must_be_unsaved')
    records = packet['records']; all_records = [r for group in records.values() for r in group]
    if len({r['draft_reference'] for r in all_records}) != len(all_records):
        raise ValueError('duplicate_case_draft_reference')
    ids = {r['draft_reference'] for r in all_records}
    for record in all_records:
        if record.get('business_records_written') is not False or record.get('evidence_verified') is not False:
            raise ValueError('unverified_factual_claim')
        for key, val in record.items():
            if key.endswith('_draft_references'):
                if not isinstance(val, list) or any(ref not in ids for ref in val):
                    raise ValueError('broken_case_relationship')
    for record in records['requirement_assessments']:
        if record['model_fields']['result'] != 'not_assessed' or record['compliance_verdict_made'] is not False:
            raise ValueError('fabricated_compliance_verdict')
    for record in records['risk_scenarios']:
        fields = record['model_fields']
        if any(fields[f'{kind}_{col}'] != -1 for kind in ('inherent','current','residual') for col in ('proba','impact','level')):
            raise ValueError('fabricated_risk_scoring')
    matrix = packet['risk_matrix_proposal']
    if matrix is not None:
        from ai_onboarding.sico_case_coverage import _validate_matrix
        definition = matrix['json_definition']
        _validate_matrix(definition)
        if matrix['approved'] is not False or matrix['business_records_written'] is not False:
            raise ValueError('unapproved_matrix_only')
        if any(not l.get('hexcolor') or not l.get('name') for axis in ('probability', 'impact', 'risk') for l in definition[axis]):
            raise ValueError('incomplete_matrix_visual_definitions')
    if packet['coverage']['requirements_assessed_from_verified_evidence'] != 0:
        raise ValueError('fabricated_framework_coverage')
