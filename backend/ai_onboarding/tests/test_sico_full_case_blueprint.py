import unittest
from ai_onboarding.sico_case_coverage import make_coverage_plan
from ai_onboarding.sico_full_case_blueprint import (
    build_full_case_blueprint, proposed_starter_matrix, validate_full_case_blueprint,
)

rows = [
    {'requirement_id': 'access', 'reference': '1.1', 'requirement_name': 'Privileged access',
     'description': 'Restrict privileged user access and enforce MFA for sensitive systems.'},
    {'requirement_id': 'backup', 'reference': '2.1', 'requirement_name': 'Backups',
     'description': 'Backup and restore information periodically and test recovery.'},
    {'requirement_id': 'patch', 'reference': '2.2', 'requirement_name': 'Patches',
     'description': 'Manage software vulnerabilities and patch technical systems.'},
]
base = {'organization': 'New Company', 'framework': 'NCA ECC',
        'objective': 'Build a complete cybersecurity GRC assessment case and remediation plan.',
        'authorized_requirements': rows, 'framework_id': 'fw-1', 'source_digest': 'a'*64}

class FullCaseBlueprintTests(unittest.TestCase):
    def setUp(self):
        self.blueprint = build_full_case_blueprint(**base)
    def test_new_company_gets_new_matrix(self):
        self.assertFalse(self.blueprint['risk_matrix_proposal']['approved'])
        self.assertEqual(self.blueprint['risk_matrix_source'],'proposed_new_not_approved')
        self.assertEqual(len(self.blueprint['risk_matrix_proposal']['json_definition']['grid']),4)
    def test_matrix_uses_sico_zero_based_grid(self):
        matrix=proposed_starter_matrix()['json_definition']
        from ai_onboarding.sico_case_coverage import _validate_matrix, calculate_proposed_risk
        _validate_matrix(matrix)
        self.assertEqual(calculate_proposed_risk(matrix_definition=matrix,inherent={'probability':4,'impact':4})['inherent']['level_index'],4)
    def test_multiple_threats_and_risks(self):
        self.assertGreater(len(self.blueprint['records']['threats']), 1)
        self.assertEqual(len(self.blueprint['records']['vulnerabilities']),len(self.blueprint['records']['risk_scenarios']))
    def test_all_requirements_have_real_draft_records(self):
        for kind in ('applied_controls', 'evidence_requests', 'requirement_assessments',
                     'control_effectiveness_tests','finding_investigations','remediation_actions'):
            self.assertEqual(len(self.blueprint['records'][kind]),len(rows),kind)
    def test_policies_and_linked_controls(self):
        self.assertGreater(len(self.blueprint['records']['policies']),1)
        self.assertTrue(all(p['linked_control_draft_references'] for p in self.blueprint['records']['policies']))
    def test_no_verified_risk_or_compliance_claims(self):
        self.assertEqual(self.blueprint['coverage']['requirements_assessed_from_verified_evidence'],0)
        self.assertTrue(all(r['model_fields']['result']=='not_assessed' for r in self.blueprint['records']['requirement_assessments']))
        self.assertTrue(all(r['model_fields']['inherent_level']==-1 for r in self.blueprint['records']['risk_scenarios']))
        self.assertTrue(all(not r['finding_confirmed'] for r in self.blueprint['records']['finding_investigations']))
    def test_controls_not_claimed_implemented(self):
        self.assertTrue(all(not r['implemented'] for r in self.blueprint['records']['applied_controls']))
    def test_all_relationships_resolve(self):
        validate_full_case_blueprint(self.blueprint)
    def test_malformed_relationship_rejected(self):
        self.blueprint['records']['threats'][0]['asset_draft_references']=['another-tenant-record']
        with self.assertRaisesRegex(ValueError, 'broken_case_relationship'):
            validate_full_case_blueprint(self.blueprint)
    def test_duplicate_source_rejected(self):
        with self.assertRaises(ValueError):
            build_full_case_blueprint(**{**base, 'authorized_requirements':rows+[rows[0]]})
    def test_bad_matrix_rejected(self):
        with self.assertRaises(ValueError):
            build_full_case_blueprint(**base, approved_matrix={'grid':[[99]]})
    def test_existing_matrix_does_not_create_new(self):
        matrix=proposed_starter_matrix()['json_definition']
        result=build_full_case_blueprint(**base,approved_matrix=matrix)
        self.assertIsNone(result['risk_matrix_proposal'])
        self.assertTrue(result['risk_assessment_proposal']['existing_matrix_must_be_bound_by_authorized_server'])
    def test_tampered_compliance_rejected(self):
        self.blueprint['records']['requirement_assessments'][0]['model_fields']['result']='compliant'
        with self.assertRaisesRegex(ValueError, 'fabricated_compliance_verdict'):
            validate_full_case_blueprint(self.blueprint)
    def test_all_16_workflow_areas(self):
        for k in ('assets','threats','vulnerabilities','risk_scenarios','applied_controls',
                  'policies','evidence_requests','requirement_assessments','control_effectiveness_tests',
                  'finding_investigations','remediation_actions','risk_treatment_plans',
                  'residual_risk_reassessments','human_review_packages','management_reports'):
            self.assertGreater(len(self.blueprint['records'][k]),0,k)
    def test_coverage_api_returns_full_case(self):
        packet=make_coverage_plan(**base)
        self.assertEqual(packet['full_case_blueprint']['coverage']['authorized_framework_requirements'],3)
        self.assertEqual(packet['coverage']['requirement_results_verified'],0)

if __name__ == '__main__': unittest.main()
