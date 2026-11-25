import unittest
from ai_onboarding.sico_case_matrix_methodology import generate_case_risk_matrix
from ai_onboarding.sico_case_coverage import _validate_matrix, calculate_proposed_risk
from ai_onboarding.sico_full_case_blueprint import build_full_case_blueprint, validate_full_case_blueprint

R = [
    {'requirement_id': 'id', 'reference': '1', 'requirement_name': 'Privileged authentication', 'description':'Require MFA for privileged accounts.'},
    {'requirement_id': 'backup', 'reference': '2', 'requirement_name': 'Recovery', 'description':'Backup and restore critical information.'},
    {'requirement_id': 'cloud', 'reference': '3', 'requirement_name': 'Cloud hosting', 'description':'Use cloud workload configuration security.'},
    {'requirement_id': 'governance', 'reference': '4', 'requirement_name': 'Governance roles', 'description':'Approve governance and risk management responsibilities.'},
]
ARG = dict(organization='Demo organization', framework='NCA ECC', objective='Build a comprehensive cyber risk and compliance assessment for the company.',
           authorized_requirements=R, framework_id='fw1', source_digest='f'*64)

class DynamicMatrixTest(unittest.TestCase):
    def make(self, domains, **kw):
        return generate_case_risk_matrix(organization='Demo organization',objective='Assess business risks and scope.', risk_domains=domains, **kw)
    def test_narrow_scope_gets_complete_3x3(self):
        packet=self.make(['governance','identity_and_access'])
        self.assertEqual((packet['probability_count'],packet['impact_count']),(3,3))
        self.assertEqual((len(packet['json_definition']['grid']),len(packet['json_definition']['grid'][0])),(3,3))
    def test_medium_scope_4x4(self):
        p=self.make(['data_protection','network_security','backup_and_recovery'])
        self.assertEqual((p['probability_count'],p['impact_count']),(4,4))
    def test_broad_scope_5x5(self):
        p=self.make(['data_protection','network_security','backup_and_recovery','governance','identity_and_access','incident_response','application_security'])
        self.assertEqual((p['probability_count'],p['impact_count']),(5,5))
    def test_authorized_six_level_precision(self):
        p=self.make(['cloud_security'], trusted_risk_profile={'requires_six_level_precision':True})
        self.assertEqual((p['probability_count'],p['impact_count']),(6,6))
    def test_authorized_rectangular_matrix(self):
        p=self.make(['cloud_security'], trusted_risk_profile={'matrix_shape':'3x5'})
        self.assertEqual((len(p['json_definition']['grid']),len(p['json_definition']['grid'][0])),(3,5))
    def test_variable_4x6(self):
        p=self.make(['backup_and_recovery'], trusted_risk_profile={'requires_detailed_impact_axis':True})
        self.assertEqual((p['probability_count'],p['impact_count']),(4,6))
    def test_matrix_is_not_a_single_number(self):
        p=self.make(['data_protection'])
        self.assertSetEqual(set(p['json_definition']),{'probability','impact','risk','grid'})
        for axis in ('probability','impact','risk'):
            for level in p['json_definition'][axis]:
                self.assertTrue(level['hexcolor'].startswith('#'))
                self.assertTrue(level['name'])
        _validate_matrix(p['json_definition'])
    def test_sico_grid_calculation_not_ai_arithmetic(self):
        m=self.make(['network_security'])['json_definition']
        scored=calculate_proposed_risk(matrix_definition=m, inherent={'probability':2,'impact':2})
        self.assertEqual(scored['inherent']['level_index'],m['grid'][2][2])
    def test_monotonic_for_all_dimensions(self):
        for shape in ('3x3','4x4','5x5','6x6','3x5','6x4'):
            grid=self.make(['governance'],trusted_risk_profile={'matrix_shape':shape})['json_definition']['grid']
            for row in grid:
                self.assertEqual(row,sorted(row))
            for i in range(len(grid[0])):
                col=[row[i] for row in grid]
                self.assertEqual(col,sorted(col))
    def test_no_matrix_approval_or_risk_appetite_fabrication(self):
        p=self.make(['data_protection'])
        self.assertIs(p['approved'],False)
        self.assertIsNone(p['risk_tolerance'])
        self.assertIs(p['is_enabled'],False)
    def test_untrusted_shape_rejected(self):
        for shape in ('20x20','3x0','foo',None):
            if shape is None: continue
            with self.assertRaises(ValueError):
                self.make(['governance'],trusted_risk_profile={'matrix_shape':shape})
    def test_full_case_risks_link_to_proposed_matrix_but_remain_unrated(self):
        b=build_full_case_blueprint(**ARG)
        m=b['risk_matrix_proposal']
        self.assertEqual((m['probability_count'],m['impact_count']), (4,4))
        for risk in b['records']['risk_scenarios']:
            self.assertEqual(risk['risk_matrix_draft_reference'],m['draft_reference'])
            self.assertEqual(risk['model_fields']['inherent_level'],-1)
            self.assertIn('inherent_probability',risk['risk_rating_inputs_pending'])
        validate_full_case_blueprint(b)
    def test_approved_existing_matrix_reused(self):
        m=self.make(['governance'])['json_definition']
        b=build_full_case_blueprint(**ARG,approved_matrix=m)
        self.assertIsNone(b['risk_matrix_proposal'])
        self.assertEqual(b['risk_matrix_source'],'authorized_existing_approved_matrix')
    def test_missing_impact_dimension_in_tampered_matrix_denied(self):
        b=build_full_case_blueprint(**ARG)
        del b['risk_matrix_proposal']['json_definition']['risk'][0]['hexcolor']
        with self.assertRaisesRegex(ValueError,'incomplete_matrix_visual_definitions'):
            validate_full_case_blueprint(b)

if __name__ == '__main__': unittest.main()
