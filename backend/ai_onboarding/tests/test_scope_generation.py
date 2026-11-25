"""Scope-driven multi-record engine checks. ALL model responses are mocked."""
import copy
import unittest
from ai_onboarding import quality_sico_drafts_v5 as q
from ai_onboarding.sico_case_coverage import plan_generation_queue
from ai_onboarding.tests import test_quality_all_activities as fixtures

ROWS=[{'requirement_id':'authorized-source','reference':'C-01','requirement_name':'Cloud service access',
       'description':'Review cloud platform identity, access control and change authorization.'}]
SUBJECTS=['Tenant identity plane','Billing transaction database','Recovery storage service']
DETAILS=[
    'Tenant identity plane may federate customer administrators and issue scoped session credentials across isolated tenants. Proposed identity engineers must verify trust boundaries, enrollment approvals and privileged revocation events against signed federation configurations.',
    'Billing transaction database may reconcile rated usage, invoice adjustments and payment references with finance systems. A proposed finance platform custodian must verify settlement boundaries, reconciliation permissions and retention obligations using ledger extracts.',
    'Recovery storage service may retain restoration copies across separate failure domains and supplier facilities. Proposed continuity operators must verify restore ownership, deletion protection and recovery dependencies through signed exercise records.',
]
def objective(subjects):return 'Prepare a proposed cybersecurity GRC case. Scope: '+'; '.join(subjects)

class ScopeGenerationTests(unittest.TestCase):
    def plan(self,subjects=SUBJECTS):
        return plan_generation_queue(authorized_requirements=ROWS,objective=objective(subjects))
    def test_quantity_changes_with_explicit_scope_not_organization_name(self):
        small=self.plan(SUBJECTS[:2]);large=self.plan()
        for step in (4,5,6):
            self.assertEqual(sum(s['activity_number']==step for s in small['generation_queue']),2)
            self.assertEqual(sum(s['activity_number']==step for s in large['generation_queue']),3)
        for step in (7,9):
            self.assertEqual(large['generation_summary']['activity_targets'][str(step)],small['generation_summary']['activity_targets'][str(step)]+1)
    def test_every_chain_references_its_own_scope_asset(self):
        slots=self.plan()['generation_queue'];byref={s['draft_reference']:s for s in slots}
        for s in slots:
            for ref in s['dependency_draft_references']:
                self.assertIn(ref,byref)
                self.assertLess(byref[ref]['activity_number'],s['activity_number'])
                if s.get('scope_subject') and byref[ref].get('scope_subject'):
                    self.assertEqual(s['scope_subject'],byref[ref]['scope_subject'])
    def test_no_scope_list_is_invented_from_company_label(self):
        p=plan_generation_queue(authorized_requirements=ROWS,objective='Assess cybersecurity against the selected framework and verify system inventory.')
        self.assertEqual(p['generation_summary']['explicit_scope_subjects'],[])
        self.assertIn('needs_confirmation',p['generation_summary']['scope_detail_status'])
    def test_all_sixteen_activities_generate_multiple_valid_linked_records(self):
        harness=fixtures.AllActivityContracts();harness.setUp()
        accepted={};before={}
        plan=self.plan()
        for slot in plan['generation_queue']:
            step=slot['activity_number'];raw=fixtures.output(step);subject=slot.get('scope_subject','')
            if subject:
                raw['title']=q.CONTRACTS[q.DRAFT_ACTIVITIES[step-1][0]][0]+' '+subject+' operational review'
                raw['content']=DETAILS[SUBJECTS.index(subject)]+' '+raw['content']
                raw['content']=raw['content'][:670].rstrip()
            elif slot['theme'] in ('cloud_security','identity_and_access'):
                detail = ('Cloud workload boundaries may separate virtual hosts, tenant routes and supplier hosting facilities. Platform custodians should verify deployment inventories, network trust and restoration obligations.'
                          if slot['theme']=='cloud_security' else
                          'Identity account governance may separate administrative enrollment, delegated privileges and departed personnel. Access reviewers should confirm recertification decisions, exception ownership and withdrawal timelines.')
                raw['title']=q.CONTRACTS[q.DRAFT_ACTIVITIES[step-1][0]][0]+' '+slot['theme'].replace('_',' ')+' operational proposal'
                raw['content']=(detail+' '+raw['content'])[:670].rstrip()
            context=[accepted[r]['draft'] for r in slot['dependency_draft_references']]
            if step==10:raw['attributes']['framework_requirement_reference']=ROWS[0]['reference']
            raw['related_draft_references']=slot['dependency_draft_references'][:3]
            for field,parent_step in (('asset_reference',4),('linked_risk_reference',6),('linked_control_reference',7),('risk_reference',6)):
                if field in raw['attributes']:
                    parent=next((d for d in context if int(d['draft_reference'][6:8])==parent_step),None)
                    if parent:raw['attributes'][field]=parent['draft_reference']
            if step==7 and not any(int(d['draft_reference'][6:8])==6 for d in context):
                raw['attributes']['linked_risk_reference']='UNLINKED - risk draft needed'
            request=harness.request(step,context)
            request.update(organization='Synthetic service operator',objective=objective(SUBJECTS),draft_index=slot['draft_index'],
                authorized_requirements=ROWS,chosen_requirement=ROWS[0] if step==10 else None,
                focus_requirement=ROWS[0],focus_theme=slot['theme'],scope_subject=subject,
                required_context_references=slot['dependency_draft_references'],
                prior_drafts=[r['draft'] for r in accepted.values() if r['activity_number']==step])
            checkpoint=copy.deepcopy(accepted)
            try:
                with harness.transport([raw]):result=q.generate_quality_draft(harness.selection,**request,max_attempts=1)
            except Exception as exc:raise AssertionError(f'Activity {step}, scope {subject}: {exc}') from exc
            self.assertEqual(accepted,checkpoint)
            self.assertEqual(result['draft']['content'],raw['content'])
            result.update(provenance='qwen_quality_single_authenticated_v7',generation_scope_subject=subject,
                          generation_task_identity=slot['task_identity'])
            accepted[slot['draft_reference']]=result
        self.assertEqual({r['activity_number'] for r in accepted.values()},set(range(1,17)))
        self.assertEqual(sum(r['activity_number']==4 for r in accepted.values()),3)
        self.assertEqual(sum(r['activity_number']==6 for r in accepted.values()),3)
        self.assertTrue(all(r['business_records_written'] is False for r in accepted.values()))
        type(self).fixture={'plan':plan,'rows':ROWS,'accepted':accepted}
