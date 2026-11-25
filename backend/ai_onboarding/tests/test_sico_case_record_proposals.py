import unittest
from ai_onboarding.sico_case_record_proposals import (
    prepare_requirement_assessments, enrich_quality_draft_result, score_authorized_risk_proposal
)
from ai_onboarding.sico_case_coverage import make_coverage_plan

REQS=[{'requirement_id':'r1','reference':'ID-01','description':'Manage access to information','requirement_name':'Identity'},
      {'requirement_id':'r2','reference':'ID-02','description':'Maintain secure backups','requirement_name':'Recovery'}]

class TestModelProposals(unittest.TestCase):
    def work(self):
        return make_coverage_plan(organization='Example Org', framework='Example Framework',
          objective='Assess the organization against the selected requirements',
          authorized_requirements=REQS, framework_id='framework-test', source_digest='a'*64)
    def test_all_requirement_packets_present(self):
        p=self.work()
        self.assertEqual(len(p['requirement_assessment_proposals']),2)
        self.assertEqual({x['requirement_id'] for x in p['requirement_assessment_proposals']},{'r1','r2'})
    def test_compliance_fields_match_unassessed_default(self):
        fields=self.work()['requirement_assessment_proposals'][0]['model_fields']
        self.assertEqual(fields['result'],'not_assessed')
        self.assertEqual(fields['status'],'to_do')
        self.assertIsNone(fields['compliance_assessment'])
        self.assertFalse(fields['is_scored'])
        self.assertIsNone(fields['score'])
        self.assertEqual(fields['evidences'],[])
    def test_no_invented_evidence_controls(self):
        for x in self.work()['requirement_assessment_proposals']:
            self.assertFalse(x['evidence_verified'])
            self.assertFalse(x['compliance_verdict_made'])
            self.assertFalse(x['business_records_written'])
            self.assertEqual(x['model_fields']['applied_controls'],[])
            self.assertTrue(x['evidence_request'])
    def test_duplicate_requirement_fails(self):
        p=self.work();items=p['requirement_work_items'];
        with self.assertRaises(ValueError):
            prepare_requirement_assessments(requirement_work_items=[items[0],items[0]], framework_id='x', source_digest='a'*64)
    def test_unverified_claim_fails(self):
        p=self.work();it=dict(p['requirement_work_items'][0],proposed_result='compliant');
        with self.assertRaises(ValueError):
            prepare_requirement_assessments(requirement_work_items=[it], framework_id='x', source_digest='a'*64)
    def test_non_authorized_source_fails(self):
        p=self.work();it=dict(p['requirement_work_items'][0],source='user_submitted');
        with self.assertRaises(ValueError):
            prepare_requirement_assessments(requirement_work_items=[it], framework_id='x', source_digest='a'*64)
    def draft(self, code,attrs=None,refs=None,requirement_id=None):
        return {'activity_code':code,'business_records_written':False, 'draft':{
            'draft_reference':'draft-10-01' if code=='requirement_reviews' else 'draft-06-01',
            'status':'new_unsaved_ai_draft_pending_verification',
            'authorized_requirement_id':requirement_id,
            'related_draft_references':refs or [],
            'proposed_attributes':[{'field':k,'proposed_value':v} for k,v in (attrs or {}).items()]}}
    def test_qwen_requirement_not_marked_compliant(self):
        p=enrich_quality_draft_result(self.draft('requirement_reviews',{
            'framework_requirement_reference':'ID-01','review_method':'Inspect MFA configuration',
            'evidence_needed':'Review access logs', 'review_status':'fully compliant'},requirement_id='r1'),
            chosen_requirement=REQS[0])
        x=p['draft']['requirement_assessment_proposal']
        self.assertEqual(x['model_fields']['result'],'not_assessed')
        self.assertFalse(x['compliance_verdict_made'])
        self.assertIn('fully compliant',x['review_status_from_model_unverified'])
    def test_qwen_fake_requirement_rejected(self):
        with self.assertRaises(ValueError):
            enrich_quality_draft_result(self.draft('requirement_reviews',{'framework_requirement_reference':'FAKE'}, requirement_id='r1'),chosen_requirement=REQS[0])
    def test_proposed_risk_unrated_without_matrix(self):
        d=self.draft('risk_scenarios',{'asset_reference':'draft-04-01','treatment_option':'mitigate'}, refs=['draft-04-01'])
        p=enrich_quality_draft_result(d)
        x=p['draft']['risk_scenario_assessment_proposal']
        self.assertEqual(x['model_fields']['inherent_level'],-1)
        self.assertEqual(x['model_fields']['current_level'],-1)
        self.assertEqual(x['model_fields']['residual_level'],-1)
        self.assertEqual(x['model_fields']['treatment'],'mitigate')
        self.assertTrue(x['requires_authorized_risk_assessment_and_matrix'])
    def test_prose_treatment_not_invented(self):
        p=enrich_quality_draft_result(self.draft('risk_scenarios',{'treatment_option':'reduce risk with a firewall'}))
        self.assertIsNone(p['draft']['risk_scenario_assessment_proposal']['model_fields']['treatment'])
    def test_risk_asset_unlinked_does_not_break_current_schema(self):
        p=enrich_quality_draft_result(self.draft('risk_scenarios',{'asset_reference':'Main Database'}))
        self.assertTrue(p['draft']['risk_scenario_assessment_proposal']['asset_reference_requires_manual_resolution'])
    def test_residual_draft_never_approved(self):
        p=enrich_quality_draft_result(self.draft('residual_risk',{'treatment_assumptions':'MFA will be implemented'}, refs=['draft-06-01']))
        self.assertTrue(p['draft']['residual_risk_assessment_proposal']['projected_only'])
        self.assertFalse(p['draft']['residual_risk_assessment_proposal']['risk_acceptance_approved'])
    def test_matrix_reuses_existing_grid(self):
        matrix={'probability':['low','high'],'impact':['low','high'],'risk':['low','medium','high'],'grid':[[0,1],[1,2]]}
        p=score_authorized_risk_proposal(trusted_matrix_definition=matrix,inherent={'probability':1,'impact':1})
        self.assertEqual(p['inherent']['level_index'],2)
        self.assertIsNone(p['current']['level_index'])
    def test_unverified_current_control_not_assigned_rating(self):
        matrix={'probability':['low','high'],'impact':['low','high'],'risk':['low','high'],'grid':[[0,1],[1,1]]}
        p=score_authorized_risk_proposal(trusted_matrix_definition=matrix,current={'probability':1,'impact':1})
        self.assertIsNone(p['current']['level_index'])
    def test_invalid_matrix_rejected(self):
        with self.assertRaises(ValueError):score_authorized_risk_proposal(trusted_matrix_definition={'grid':[]})
    def test_enrichment_does_not_mutate_original(self):
        d=self.draft('risk_scenarios');q=enrich_quality_draft_result(d)
        self.assertNotIn('risk_scenario_assessment_proposal',d['draft'])
        self.assertIn('risk_scenario_assessment_proposal',q['draft'])

if __name__=='__main__':unittest.main()
