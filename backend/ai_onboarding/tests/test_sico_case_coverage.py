"""Pure, read-only tests; run offline without Django, Qwen or a database."""
import unittest
from ai_onboarding.sico_case_coverage import make_coverage_plan, calculate_proposed_risk

R = [
    {'reference':'2-2-3', 'requirement_id':'id-mfa', 'description':'Remote access must use multifactor authentication.'},
    {'reference':'2-9-3', 'requirement_id':'id-backup', 'description':'Restore backups and periodically test recovery.'},
]
SCOPE={'organization':'Sky Line','framework':'NCA ECC',
       'objective':'Perform full risk and compliance review of in-scope systems.',
       'framework_id':'authorized-fw-id', 'source_digest':'a'*64}
M={'probability':[{'name':'Low'},{'name':'High'}], 'impact':[{'name':'Low'},{'name':'High'}],
   'risk':[{'name':'Low'},{'name':'Medium'},{'name':'High'}], 'grid':[[0,1],[1,2]]}

class TestCoverage(unittest.TestCase):
    def test_each_requirement_planned(self):
        plan=make_coverage_plan(**SCOPE, authorized_requirements=R)
        self.assertEqual(plan['coverage']['requirements_considered_for_review'],2)
        self.assertEqual(len(plan['requirement_work_items']),2)
        self.assertEqual(plan['generation_policy']['requirement_review_queue'],['id-mfa','id-backup'])
    def test_no_compliance_fabrication(self):
        plan=make_coverage_plan(**SCOPE, authorized_requirements=R)
        self.assertTrue(all(r['proposed_result']=='not_assessed' and r['human_review_required']
                            and not r['evidence_verified'] for r in plan['requirement_work_items']))
        self.assertFalse(plan['coverage']['full_framework_assessed'])
    def test_source_specific_evidence(self):
        plan=make_coverage_plan(**SCOPE, authorized_requirements=R)
        self.assertIn('multifactor',plan['requirement_work_items'][0]['evidence_to_request'])
        self.assertIn('Restore',plan['requirement_work_items'][1]['evidence_to_request'])
    def test_duplicate_ref_rejected(self):
        with self.assertRaises(ValueError):make_coverage_plan(**SCOPE,authorized_requirements=R+[dict(R[1],requirement_id='different')])
    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):make_coverage_plan(**SCOPE,authorized_requirements=R+[dict(R[1],reference='other')])
    def test_scope_restricts_to_authorized(self):
        plan=make_coverage_plan(**SCOPE, authorized_requirements=R,selected_requirement_ids=['id-backup'])
        self.assertEqual(len(plan['requirement_work_items']),1)
        self.assertEqual(plan['coverage']['authorized_requirements_loaded'],2)
    def test_scope_unknown_denied(self):
        with self.assertRaises(ValueError):make_coverage_plan(**SCOPE,authorized_requirements=R,selected_requirement_ids=['cross-tenant'])
    def test_untrusted_draft_cannot_claim_verified(self):
        draft={'activity_number':10,'activity_code':'requirement_reviews','business_records_written':False,
               'draft':{'authorized_requirement_id':'id-mfa','draft_reference':'draft-10-01',
                        'status':'new_unsaved_ai_draft_pending_verification'}}
        plan=make_coverage_plan(**SCOPE,authorized_requirements=R,prior_drafts=[draft])
        self.assertEqual(plan['coverage']['requirement_review_drafts_present'],1)
        self.assertEqual(plan['coverage']['requirement_results_verified'],0)
        self.assertEqual(plan['generation_policy']['requirement_review_queue'],['id-backup'])
    def test_client_fake_verification_ignored(self):
        fake={'activity_number':10,'activity_code':'requirement_reviews','business_records_written':True,
              'draft':{'authorized_requirement_id':'id-mfa','draft_reference':'draft-10-01',
                       'status':'new_unsaved_ai_draft_pending_verification'}}
        plan=make_coverage_plan(**SCOPE,authorized_requirements=R,prior_drafts=[fake])
        self.assertEqual(plan['coverage']['requirement_review_drafts_present'],0)

class TestRisk(unittest.TestCase):
    def test_exact_sico_matrix_grid(self):
        scored=calculate_proposed_risk(matrix_definition=M,inherent={'probability':1,'impact':1})
        self.assertEqual(scored['inherent']['level_index'],2)
        self.assertEqual(scored['current']['level_index'],None)
    def test_current_not_scored_from_unverified_controls(self):
        result=calculate_proposed_risk(matrix_definition=M,current={'probability':1,'impact':1})
        self.assertIsNone(result['current']['level_index'])
        self.assertEqual(result['current']['status'],'awaiting_verified_current_controls')
    def test_current_scored_with_verified_controls(self):
        result=calculate_proposed_risk(matrix_definition=M,current={'probability':1,'impact':0},verified_current_controls=True)
        self.assertEqual(result['current']['level_index'],1)
    def test_residual_labelled_projected(self):
        result=calculate_proposed_risk(matrix_definition=M,residual={'probability':0,'impact':0})
        self.assertEqual(result['residual']['status'],'projected_after_proposed_treatment')
    def test_residual_after_verification_still_requires_review(self):
        result=calculate_proposed_risk(matrix_definition=M,residual={'probability':0,'impact':0},treatment_implemented_and_verified=True)
        self.assertEqual(result['residual']['status'],'post_treatment_requires_human_review')
    def test_reject_out_of_matrix(self):
        with self.assertRaises(ValueError): calculate_proposed_risk(matrix_definition=M,inherent={'probability':8,'impact':1})
    def test_reject_bool_as_index(self):
        with self.assertRaises(ValueError): calculate_proposed_risk(matrix_definition=M,inherent={'probability':True,'impact':1})
    def test_reject_invalid_grid(self):
        m=dict(M,grid=[[0],[1]])
        with self.assertRaises(ValueError): calculate_proposed_risk(matrix_definition=m)
    def test_no_matrix_guess(self):
        with self.assertRaises(ValueError): calculate_proposed_risk(matrix_definition={})

if __name__=='__main__': unittest.main()
