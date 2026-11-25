"""Focused regression checks of planned chains; no DB or model network access."""
import copy
from http.client import RemoteDisconnected
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory, force_authenticate
from ai_onboarding import quality_sico_drafts_v5 as q
from ai_onboarding import sico_ai_case_quality_views as view
from ai_onboarding import sico_case_coverage_views as coverage_view
from ai_onboarding.sico_case_coverage import plan_generation_queue
from ai_onboarding.llm_provider import LocalAiProvider
from ai_onboarding.llm_errors import AiProviderExecutionError
from ai_onboarding.sico_case_record_proposals import enrich_quality_draft_result

ROWS = [{'requirement_id':f'r{i}', 'reference':f'AC-{i}',
         'description':'Restrict privileged access and authenticate operators before changing service configuration.',
         'requirement_name':f'Access safeguard {i}'} for i in range(1,19)]

def record(step,index,attrs,links=()):
    code,_,model,*_ = q.DRAFT_ACTIVITIES[step-1]
    return {'draft_reference':f'draft-{step:02d}-{index:02d}', 'record_type':model,
            'title':q.CONTRACTS[code][0]+' Proposed service access boundary',
            'content':'The proposed application service handles confidential operational requests. A service owner must verify its boundaries, operator access paths and sensitive information flows before this security hypothesis is treated as an organizational fact.',
            'proposed_attributes':[{'field':k,'proposed_value':v} for k,v in attrs.items()],
            'related_draft_references':list(links)}

class CoordinatedGenerationTests(unittest.TestCase):
    def test_control_with_truncated_implementation_or_test_is_rejected(self):
        risk=record(6,1,{'asset_reference':'draft-04-01'})
        draft=record(7,1,dict(linked_risk_reference='draft-06-01',control_objective='Prevent unauthorized configuration changes',
            implementation_steps='The service owner enforces permissions for',
            test_method='Request a configuration export and sample denied changes. The test will'),['draft-06-01'])
        draft['attributes']=draft.pop('proposed_attributes')
        with self.assertRaisesRegex(ValueError,'incomplete_instruction'):
            q.validate_draft('applied_controls',draft,prior_records=[risk])
    def test_complete_control_fields_survive_provider_and_parent_request_contract(self):
        steps='The proposed service owner requires strong operator authentication, restricts configuration privileges to approved dispatch roles, records authorized changes, removes stale access after role changes and submits the permission baseline for owner verification.'
        method='Request a dated configuration export, compare assigned dispatch privileges with the approved role matrix, sample authorized changes and verify that an account without the approved role is denied configuration access; retain the test log for review.'
        attrs=dict(linked_risk_reference='draft-06-01',control_objective='Restrict dispatch configuration changes to approved operators',implementation_steps=steps,test_method=method)
        schema=q.quality_wire_schema_for('applied_controls',allowed_related=['draft-06-01'],candidate_risks=['draft-06-01'])
        q.Draft202012Validator(schema).validate(dict(title='Applied control: Proposed dispatch configuration authorization',
            content='The proposed service owner would restrict dispatch configuration to approved operators and retain an auditable permission baseline. Actual roles, assigned privileges and operating evidence must be confirmed before implementation is asserted.',
            attributes=attrs,evidence_request='Request a dated dispatch configuration and role assignment export from the proposed service owner.',
            verification_question='Which service owner can confirm the approved operator role matrix and supply the dated export?',related_draft_references=['draft-06-01']))
        previous=record(7,1,attrs,['draft-06-01'])
        form=view.PreviousDraft(data=previous)
        self.assertTrue(form.is_valid(),form.errors)
        self.assertEqual(next(a['proposed_value'] for a in form.validated_data['proposed_attributes'] if a['field']=='implementation_steps'),steps)
    def test_risk_prompt_uses_parent_attributes_without_copyable_threat_narrative(self):
        asset,_,threat,risk=self.chain()
        provider=Mock()
        provider.generate_structured.return_value={**{k:v for k,v in risk.items() if k in (
            'title','content','evidence_request','verification_question','related_draft_references')},
            'attributes':{a['field']:a['proposed_value'] for a in risk['attributes']}}
        selection=SimpleNamespace(provider=provider,config=SimpleNamespace(model='mock',timeout_seconds=60,max_output_tokens=1100))
        q.generate_quality_draft(selection,organization='Test operator',framework='Selected edition',objective='Assess dispatch service access and configuration integrity.',
            phase=5,draft_index=1,prior_drafts=[],case_context=[asset,threat])
        parents=provider.generate_structured.call_args.kwargs['user_payload']['allowed_linked_drafts']
        supplied=next(p for p in parents if p['draft_reference']=='draft-05-01')
        self.assertNotIn('content',supplied)
        self.assertEqual(supplied['proposed_attributes'],threat['proposed_attributes'])
    def test_generic_security_audit_is_not_an_operational_control_test(self):
        risk=record(6,1,{'asset_reference':'draft-04-01'})
        draft=record(7,1,dict(linked_risk_reference='draft-06-01',control_objective='Prevent unauthorized configuration changes',
            implementation_steps='The service owner enforces scoped operator permissions and change approvals.',
            test_method='Regular security audits and vulnerability assessments will ensure effectiveness.'),['draft-06-01'])
        draft['attributes']=draft.pop('proposed_attributes')
        with self.assertRaisesRegex(ValueError,'observable_evidence_or_result'):
            q.validate_draft('applied_controls',draft,prior_records=[risk])
    def test_risk_must_develop_parent_threat_instead_of_copying_its_narrative(self):
        asset,_,threat,risk=self.chain()
        threat['content']=risk['content']
        with self.assertRaisesRegex(ValueError,'copied_parent_narrative'):
            q.validate_draft('risk_scenarios',risk,prior_records=[asset,threat])
    def test_threat_cannot_be_a_mitigation_relabelled_with_threat_prefix(self):
        asset=record(4,1,{})
        threat=record(5,1,dict(asset_reference='draft-04-01',threat_source='Insufficient password complexity',
            weakness_hypothesis='Operators may reuse weak passwords.',impact_if_realized='Unauthorized access to confidential dispatch information.'),['draft-04-01'])
        threat['content']='To ensure dispatch integrity, a password policy enforcement system will be established. This system will manage password rules and user education to prevent weak passwords and password reuse across the proposed application service.'
        threat['attributes']=threat.pop('proposed_attributes')
        with self.assertRaisesRegex(ValueError,'conditional_adverse_event'):
            q.validate_draft('threats',threat,prior_records=[asset])
    def test_disconnected_qwen_transport_is_sanitized_without_fallback(self):
        provider=LocalAiProvider(base_url='http://127.0.0.1:9',base_url_safe=True,base_url_warning=None)
        with patch('ai_onboarding.llm_provider.urllib.request.urlopen',side_effect=RemoteDisconnected('sensitive transport internals')):
            with self.assertRaises(AiProviderExecutionError) as error:
                provider.generate_structured(capability='test',model='qwen-test',system_prompt='Test',user_payload={},
                    json_schema={'type':'object'},timeout_seconds=1,max_output_tokens=100,temperature=0.2,schema_name='test')
        self.assertEqual(error.exception.error_code,'ai_provider_request_failed')
        self.assertNotIn('sensitive',error.exception.detail)
    def test_vulnerability_proposal_preserves_exact_model_weakness_and_asset(self):
        hypothesis='Operator privileges may remain active after a dispatcher changes responsibility; verify access reviews.'
        draft=record(5,1,{'asset_reference':'draft-04-01','weakness_hypothesis':hypothesis},['draft-04-01'])
        draft['status']='new_unsaved_ai_draft_pending_verification'
        packet={'activity_code':'threats','draft':draft,'business_records_written':False}
        before=copy.deepcopy(packet)
        enriched=enrich_quality_draft_result(packet)
        self.assertEqual(enriched['draft']['vulnerability_proposal']['model_fields']['description'],hypothesis)
        self.assertEqual(enriched['draft']['vulnerability_proposal']['candidate_asset_draft_reference'],'draft-04-01')
        self.assertEqual(packet,before)
    def test_real_coverage_adapter_preserves_response_schema_and_full_queue(self):
        request=APIRequestFactory().post('/ai/coverage-plan/',dict(organization_name='Test operator',framework_name='Selected authorized edition',
            problem='Assess operator access to dispatch service configuration.',source_digest='a'*64),format='json')
        force_authenticate(request,SimpleNamespace(is_active=True,is_authenticated=True))
        with patch.object(coverage_view,'_load_authorized_requirements',return_value=({'status':'matched','framework_id':'fw'},ROWS)), \
             patch.object(coverage_view,'_page_and_digest',return_value=(ROWS,len(ROWS),'a'*64)):
            response=coverage_view.SicoCaseCoveragePlanView.as_view()(request)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['schema'],'sico-ai-coverage-plan-v1')
        self.assertEqual(len([s for s in response.data['generation_queue'] if s['activity_number']==10]),len(ROWS))
        self.assertFalse(response.data['business_records_written'])
    def test_all_requirements_scheduled_beyond_old_twelve_slot_limit(self):
        plan=plan_generation_queue(authorized_requirements=ROWS,objective='Assess privileged access for an operations organization.')
        reviews=[s for s in plan['generation_queue'] if s['activity_number']==10]
        self.assertEqual({s['focus_requirement_id'] for s in reviews},{r['requirement_id'] for r in ROWS})
        self.assertEqual(len(reviews),18)
        self.assertTrue(plan['generation_summary']['all_requirements_scheduled_for_qwen_review'])
        self.assertEqual({s['activity_number'] for s in plan['generation_queue']},set(range(1,17)))
    def test_chain_parent_ids_follow_asset_theme(self):
        plan=plan_generation_queue(authorized_requirements=ROWS,objective='Assess privileged access to service operations.')
        byref={s['draft_reference']:s for s in plan['generation_queue']}
        for slot in byref.values():
            for parent in slot['dependency_draft_references']:
                self.assertIn(parent,byref)
                self.assertLess(byref[parent]['activity_number'],slot['activity_number'])
        self.assertEqual(byref['draft-06-01']['dependency_draft_references'],['draft-04-01','draft-05-01'])
    def test_assessment_report_is_rejected_as_asset(self):
        draft=record(4,1,dict(asset_type='Assessment report',business_purpose='Review findings',owner_role='Assessor',information_classification='Internal'))
        draft['attributes']=draft.pop('proposed_attributes')
        draft.update(evidence_request='Request service inventory and ownership approval.',verification_question='Which operational service does the owner confirm?')
        with self.assertRaisesRegex(ValueError,'operational_asset'):
            q.validate_draft('assets',draft)
    def chain(self):
        asset=record(4,1,{})
        other=record(4,2,{})
        threat=record(5,1,{'asset_reference':asset['draft_reference']},[asset['draft_reference']])
        risk=record(6,1,dict(asset_reference=asset['draft_reference'],threat_event='Privileged credential misuse',business_impact='Service configuration integrity loss',treatment_option='mitigate'),[asset['draft_reference'],threat['draft_reference']])
        risk['attributes']=risk.pop('proposed_attributes')
        risk['content'] += ' Credential compromise could permit unauthorized service changes.'
        risk.update(evidence_request='Request operator access records and configuration approvals.',verification_question='Do the approved service boundaries include privileged configuration?')
        return asset,other,threat,risk
    def test_risk_and_threat_must_reference_same_asset(self):
        asset,other,threat,risk=self.chain()
        q.validate_draft('risk_scenarios',risk,prior_records=[asset,threat])
        risk['attributes'][0]['proposed_value']=other['draft_reference']
        risk['related_draft_references']=[other['draft_reference'],threat['draft_reference']]
        with self.assertRaisesRegex(ValueError,'asset_mismatch'):
            q.validate_draft('risk_scenarios',risk,prior_records=[asset,other,threat])
    def test_risk_cannot_reference_a_report_as_asset(self):
        asset,_,threat,risk=self.chain()
        asset['record_type']='ComplianceAssessment'
        with self.assertRaisesRegex(ValueError,'asset_reference_not_allowed'):
            q.validate_draft('risk_scenarios',risk,prior_records=[asset,threat])
    def test_report_masquerading_as_asset_type_is_rejected(self):
        asset,_,threat,risk=self.chain()
        asset['title']='Asset: Organization assessment report'
        asset['proposed_attributes']=[{'field':'asset_type','proposed_value':'Assessment report'}]
        with self.assertRaisesRegex(ValueError,'operational_asset'):
            q.validate_draft('risk_scenarios',risk,prior_records=[asset,threat])
    def test_control_must_link_to_allowed_risk(self):
        risk=record(6,1,{'asset_reference':'draft-04-01'})
        control=record(7,1,dict(linked_risk_reference='draft-06-02',control_objective='Restrict privileged operations',implementation_steps='Enforce operator MFA and scoped change approvals',test_method='Inspect access exports and sample rejected changes'),['draft-06-01'])
        control['attributes']=control.pop('proposed_attributes')
        with self.assertRaisesRegex(ValueError,'control_risk_reference'):
            q.validate_draft('applied_controls',control,prior_records=[risk])
    def test_planned_parent_context_cannot_be_omitted_before_model_call(self):
        selection=SimpleNamespace(provider=Mock(),config=SimpleNamespace(model='mock',timeout_seconds=60,max_output_tokens=1600))
        with self.assertRaisesRegex(ValueError,'parent_drafts_missing'):
            q.generate_quality_draft(selection,organization='Test operations',framework='Test selected edition',
                objective='Assess service operator access to confidential configuration.',phase=5,draft_index=1,
                prior_drafts=[],case_context=[],required_context_references=['draft-04-01','draft-05-01'])
        selection.provider.generate_structured.assert_not_called()
    def test_api_rejects_forged_focus_and_missing_parent_without_provider(self):
        plan=plan_generation_queue(authorized_requirements=ROWS,objective='Assess service access and privileged configuration.')
        slot=next(s for s in plan['generation_queue'] if s['activity_number']==6)
        payload=dict(organization_name='Test operations',framework_name='Authorized edition',
            problem='Assess service access and privileged configuration.',source_digest='a'*64,
            activity_number=6,draft_index=1,focus_requirement_reference=slot['focus_requirement_reference'],
            focus_theme=slot['theme'])
        for changed in ({},{'focus_theme':'unrelated_topic'}):
            request=APIRequestFactory().post('/ai/quality-one/',{**payload,**changed},format='json')
            force_authenticate(request,SimpleNamespace(is_active=True,is_authenticated=True))
            with patch.object(view,'_load_authorized_requirements',return_value=({'status':'matched','framework_id':'fw'},ROWS)), \
                 patch.object(view,'_page_and_digest',return_value=(ROWS,len(ROWS),'a'*64)), \
                 patch.object(view,'get_advisory_provider_selection') as provider:
                response=view.SicoQualityDraftOneView.as_view()(request)
            self.assertEqual(response.status_code,409)
            provider.assert_not_called()
