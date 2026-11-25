"""Narrow provider/generator regression checks; no database or live network."""
import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from ai_onboarding import quality_sico_drafts_v5 as quality
from ai_onboarding.llm_provider import LocalAiProvider
from ai_onboarding.llm_errors import AiProviderExecutionError


def charter():
    return {
        'title':'Framework charter: Identity security scope review for proposed regional dispatch operations and authorized framework edition verification with accountable business owners',
        'content':'The proposed assessment charter would examine dispatcher access, customer address handling and supplier integration boundaries. The assessment lead must confirm the installed framework edition, identify accountable system owners and obtain a signed scope before deciding applicability or reporting any compliance result.',
        'attributes':{
            'framework_label':'Selected installed framework edition; verify the source catalog.',
            'edition_verification':'Ask the library custodian to confirm the installed version and approved applicability.',
            'scope_questions':'Confirm dispatch roles, address processing, supplier interfaces and exclusions with system owners.',
            'responsible_role':'Proposed compliance assessment lead; appointment requires confirmation.',
        },
        'evidence_request':'Request the source library version record and owner-reviewed dispatch service scope charter.',
        'verification_question':'Which accountable owner can confirm the selected edition, dispatch boundaries and proposed exclusions?',
        'related_draft_references':[],
    }


class QualityTitleRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.provider=LocalAiProvider(base_url='http://127.0.0.1:9',base_url_safe=True,base_url_warning=None)
        self.schema=quality.quality_wire_schema_for('framework_scope')
        self.sent=[]
    def transport(self,payload):
        def respond(request,**kwargs):
            self.sent.append(json.loads(request.data))
            response=MagicMock()
            response.__enter__.return_value.read.return_value=json.dumps({'response':json.dumps(payload)}).encode()
            return response
        return patch('ai_onboarding.llm_provider.urllib.request.urlopen',side_effect=respond)
    def generate(self,payload,schema_name='sico_quality_draft_one_v2'):
        with self.transport(payload):
            return self.provider.generate_structured(capability='grc_capability_selection',model='mock-qwen',
                system_prompt='Generate one unsaved charter.',user_payload={'title_prefix':'Framework charter:','mandatory_attribute_names':list(charter()['attributes'])},
                json_schema=self.schema,timeout_seconds=30,max_output_tokens=1100,temperature=0.2,schema_name=schema_name)
    def test_provider_recovers_only_title_before_return_and_preserves_raw_substance(self):
        original=charter(); before=copy.deepcopy(original)
        result=self.generate(original)
        self.assertEqual(original,before)
        self.assertLessEqual(len(result['title']),110)
        self.assertTrue(original['title'].startswith(result['title']))
        self.assertTrue(original['title'][len(result['title'])].isspace())
        self.assertEqual({k:v for k,v in result.items() if k!='title'},{k:v for k,v in original.items() if k!='title'})
        self.assertEqual(result.formatting_recovery['original_title'],original['title'])
        self.assertEqual(len(self.sent),1)
        quality.Draft202012Validator(self.schema).validate(result)
        self.assertIn('110 characters TOTAL',self.sent[0]['prompt'])
    def test_valid_title_is_unchanged_without_recovery_metadata(self):
        payload=charter();payload['title']='Framework charter: Dispatch security scope'
        result=self.generate(payload)
        self.assertEqual(result,payload)
        self.assertFalse(hasattr(result,'formatting_recovery'))
    def test_other_schema_errors_are_never_hidden_by_shortening(self):
        for change in ({'related_draft_references':['draft-04-99']},{'title':'Wrong category: '+('operational scope '*15)},
                       {'attributes':{}},{'evidence_request':'bad'},{'extra_field':'not allowed'}):
            with self.subTest(change=change):
                payload={**charter(),**change}
                with self.assertRaises(AiProviderExecutionError) as error:self.generate(payload)
                self.assertEqual(error.exception.error_code,'local_ai_provider_schema_mismatch')
    def test_recovery_is_bounded_and_does_not_split_unbroken_subjects(self):
        for title in ('Framework charter: '+'x'*200,'Framework charter: '+'scope '*1000):
            with self.subTest(length=len(title)):
                payload={**charter(),'title':title}
                with self.assertRaises(AiProviderExecutionError):self.generate(payload)
    def test_other_provider_contracts_do_not_gain_title_recovery(self):
        with self.assertRaises(AiProviderExecutionError):self.generate(charter(),schema_name='other_contract')
    def test_full_generator_keeps_original_title_in_provenance_and_narrative_unchanged(self):
        payload=charter()
        selection=SimpleNamespace(provider=self.provider,config=SimpleNamespace(model='mock-qwen',timeout_seconds=30,max_output_tokens=1100))
        with self.transport(payload):
            result=quality.generate_quality_draft(selection,organization='Dispatch test organization',framework='Selected installed edition',
                objective='Assess dispatcher access and customer address handling within agreed operational boundaries.',phase=0,draft_index=1,
                prior_drafts=[],case_context=[])
        self.assertEqual(result['draft']['content'],payload['content'])
        self.assertEqual(result['draft']['evidence_request'],payload['evidence_request'])
        self.assertEqual(result['model_provenance']['title_formatting_recovery']['original_title'],payload['title'])
        self.assertFalse(result['business_records_written'])
    def test_shortening_does_not_bypass_duplicate_title_guard(self):
        payload=charter()
        shortened=self.generate(payload)['title']
        selection=SimpleNamespace(provider=self.provider,config=SimpleNamespace(model='mock-qwen',timeout_seconds=30,max_output_tokens=1100))
        with self.transport(payload),self.assertRaisesRegex(ValueError,'duplicate_title'):
            quality.generate_quality_draft(selection,organization='Dispatch test organization',framework='Selected installed edition',
                objective='Assess dispatcher access and customer address handling within agreed operational boundaries.',phase=0,draft_index=2,
                prior_drafts=[{'draft_reference':'draft-01-01','title':shortened,'content':'Earlier accepted scope remains intact.'}],case_context=[],max_attempts=1)
