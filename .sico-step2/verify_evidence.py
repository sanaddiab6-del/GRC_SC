"""Validate original Qwen records and map them with the real unsaved adapter."""
exec(PAYLOAD['bootstrap'])
os.environ['DJANGO_SETTINGS_MODULE']='ciso_assistant.sico_agent_release_settings'
os.environ['DJANGO_SECRET_KEY']='offline-step-two-evidence-only'
os.environ['HUEY_FILE_PATH']=':memory:'
from django.conf import settings
settings.DATABASES={'default':{'ENGINE':'django.db.backends.dummy'}}
settings.FORCE_CREATE_ADMIN=False
from django.db.backends.base.base import BaseDatabaseWrapper
def forbidden(*a,**kw): raise AssertionError('DB and network forbidden during evidence validation')
BaseDatabaseWrapper.connect=forbidden
BaseDatabaseWrapper.ensure_connection=forbidden
socket.socket.connect=forbidden
import django
django.setup()
from ai_onboarding.quality_sico_drafts_v5 import validate_draft
from ai_onboarding.sico_case_record_proposals import enrich_quality_draft_result
from core.models import Threat,Vulnerability
accepted=[]
rejected=[]
for item in PAYLOAD['evidence']['AcceptedModelRecords']:
    draft=item['draft']
    candidate={**draft,'attributes':draft['proposed_attributes']}
    try:
        validate_draft(item['activity_code'],candidate,prior_records=[p['draft'] for p in accepted])
    except ValueError as exc:
        rejected.append({'reference':draft['draft_reference'],'reason':str(exc)})
        continue
    mapped=enrich_quality_draft_result(item)
    assert mapped['draft']['content']==draft['content']
    assert mapped['draft']['proposed_attributes']==draft['proposed_attributes']
    for key,model in (('threat_proposal',Threat),('vulnerability_proposal',Vulnerability)):
        if key in mapped['draft']:
            for field in mapped['draft'][key]['model_fields']:
                model._meta.get_field(field)
    accepted.append(mapped)
evidence={**PAYLOAD['evidence'],'AcceptedModelRecords':accepted,'ContentReviewRejections':rejected,
          'ModelFieldsValidatedAgainstExistingSicoModels':True,'GeneratedNarrativesUnchanged':True}
byactivity={r['activity_number']:r for r in accepted}
chain=all(step in byactivity for step in (4,5,6,7))
if chain:
    attrs=lambda r:{a['field']:a['proposed_value'] for a in r['draft']['proposed_attributes']}
    asset=byactivity[4]['draft']['draft_reference']
    assert attrs(byactivity[5])['asset_reference']==asset
    assert attrs(byactivity[6])['asset_reference']==asset
    assert attrs(byactivity[7])['linked_risk_reference']==byactivity[6]['draft']['draft_reference']
evidence['FullChainDemonstrated']=chain
print(json.dumps(evidence))
