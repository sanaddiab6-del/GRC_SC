"""Read an authorized library through SQLite mode=ro; generate unsaved Qwen drafts."""
exec(PAYLOAD['bootstrap'])
import time
from dataclasses import replace
from pathlib import Path
os.environ['DJANGO_SETTINGS_MODULE']='ciso_assistant.sico_agent_release_settings'
os.environ['DJANGO_SECRET_KEY']='offline-step-two-model-check-only'
os.environ['HUEY_FILE_PATH']=':memory:'
from django.conf import settings
database=dict(settings.DATABASES['default'])
if database['ENGINE'].endswith(('postgresql','postgresql_psycopg2')):
    options=dict(database.get('OPTIONS',{}))
    options['options']=(options.get('options','')+' -c default_transaction_read_only=on -c statement_timeout=10000').strip()
    database['OPTIONS']=options
elif database['ENGINE'].endswith('sqlite3'):
    database['NAME']=Path(database['NAME']).resolve().as_uri()+'?mode=ro'
    database['OPTIONS']={**database.get('OPTIONS',{}),'uri':True}
else:
    raise RuntimeError('Demonstration requires a verified read-only DB configuration; no connection attempted')
settings.DATABASES={'default':database}
settings.CACHES={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache'}}
settings.FORCE_CREATE_ADMIN=False
import django
django.setup()
from django.db import connection
from core.models import Framework, RequirementNode
from iam.models import User
from ai_onboarding.sico_ai_framework_batch_v3 import _load_authorized_requirements,_page_and_digest
def readonly(execute,sql,params,many,context):
    if not sql.lstrip().upper().startswith(('SELECT','WITH','PRAGMA')):
        raise AssertionError('Non-read SQL forbidden')
    return execute(sql,params,many,context)
def get_source():
    with connection.execute_wrapper(readonly):
        user=User.objects.filter(is_active=True,is_superuser=True).order_by('pk').first()
        if not user: raise RuntimeError('No active authorized demonstration account found')
        # Choose a real installed edition with a useful access-related source,
        # without embedding any framework identity, identifier or row count.
        ids=RequirementNode.objects.filter(assessable=True,description__icontains='access').values_list('framework_id',flat=True).distinct()
        for framework in Framework.objects.filter(id__in=ids).order_by('name'):
            meta,stream=_load_authorized_requirements(user,framework.name)
            if meta.get('status')!='matched': continue
            _,count,digest=_page_and_digest(stream,start=0,batch_size=0)
            meta,stream=_load_authorized_requirements(user,framework.name)
            rows,count_again,digest_again=_page_and_digest(stream,start=0,batch_size=count)
            if count and count==count_again and digest==digest_again:
                return meta,rows,digest
    raise RuntimeError('No unambiguous authorized installed framework edition available')
meta,rows,digest=get_source()
connection.close()
# No database, including the read-only source, may be used during generation.
from django.db.backends.base.base import BaseDatabaseWrapper
def no_db(*a,**kw): raise AssertionError('No DB access during model generation')
BaseDatabaseWrapper.connect=no_db
BaseDatabaseWrapper.ensure_connection=no_db
from ai_onboarding.llm_config import CAPABILITY_GRC_CAPABILITY_SELECTION,resolve_advisory_capability_config
from ai_onboarding.llm_provider import get_advisory_provider_selection
from ai_onboarding.sico_case_coverage import plan_generation_queue
from ai_onboarding.quality_sico_drafts_v5 import generate_quality_draft, validate_draft
config=resolve_advisory_capability_config(CAPABILITY_GRC_CAPABILITY_SELECTION)
selection=get_advisory_provider_selection(config)
if selection.provider is None or 'qwen' not in config.model.lower():
    raise RuntimeError('The real configured local Qwen provider is unavailable')
organization='Cedar Dispatch demonstration organization'
objective='Prepare a cybersecurity GRC case for a proposed regional delivery operator handling customer addresses, driver dispatch and supplier integrations. Assess operator identity access and dispatch service integrity; all systems and roles must be verified with the organization.'
plan=plan_generation_queue(authorized_requirements=rows,objective=objective)
slots=plan['generation_queue']
asset=next(s for s in slots if s['activity_number']==4)
threat=next(s for s in slots if s['activity_number']==5 and asset['draft_reference'] in s['dependency_draft_references'])
risk=next(s for s in slots if s['activity_number']==6 and threat['draft_reference'] in s['dependency_draft_references'])
control=next(s for s in slots if s['activity_number']==7 and risk['draft_reference'] in s['dependency_draft_references'])
print(json.dumps({'event':'source','framework':meta['matched_framework'],'framework_id':meta['framework_id'],'source_digest':digest,'authorized_requirement_count':len(rows),'model':config.model,'organization':organization,'objective':objective,'planned_records':len(slots),'activity_targets':plan['generation_summary']['activity_targets']}),flush=True)
checkpoint=PAYLOAD.get('demo_checkpoint') or {}
if checkpoint and (checkpoint['source']['source_digest']!=digest or checkpoint['source']['framework_id']!=meta['framework_id']):
    raise RuntimeError('Demonstration checkpoint source changed; old content preserved')
accepted=[]
review_feedback=[]
for previous in checkpoint.get('accepted',[]):
    candidate=previous['draft']
    validation_draft={**candidate,'attributes':candidate['proposed_attributes']}
    try:
        validate_draft(previous['activity_code'],validation_draft,prior_records=[p['draft'] for p in accepted])
    except ValueError as exc:
        review_feedback.append(str(exc))
        print(json.dumps({'event':'review_rejected','reference':candidate['draft_reference'],'candidate_title':candidate['title'],'reason':str(exc),'raw_output_preserved':True}),flush=True)
        continue
    if any(p['draft']['draft_reference']==candidate['draft_reference'] for p in accepted): continue
    accepted.append(previous)
for slot in (asset,threat,risk,control):
    if any(x['draft']['draft_reference']==slot['draft_reference'] for x in accepted):
        print(json.dumps({'event':'preserved_checkpoint_record','reference':slot['draft_reference']}),flush=True)
        continue
    parents=[x['draft'] for x in accepted if x['draft']['draft_reference'] in slot['dependency_draft_references']]
    required=slot['dependency_draft_references']
    focus=next(r for r in rows if r['requirement_id']==slot['focus_requirement_id'])
    started=time.monotonic()
    print(json.dumps({'event':'generating','reference':slot['draft_reference']}),flush=True)
    try:
        item=generate_quality_draft(selection,organization=organization,framework=meta['matched_framework']['name'],
            objective=objective,phase=slot['activity_number']-1,draft_index=slot['draft_index'],
            prior_drafts=[],case_context=parents,authorized_requirements=rows,focus_requirement=focus,
            focus_theme=slot['theme'],required_context_references=required,
            focus_attempt=1 if checkpoint else 0,
            rejection_feedback=([*review_feedback[-1:],{
                5:'A threat describes a conditional adverse actor/event on the parent asset, never a new safeguard or enforcement system.',
                6:'Write a NEW operational risk scenario. Do not copy the parent threat narrative. Develop the entry path, actor action, business workflow disruption and consequence. Use a native SICO treatment choice.',
                7:'Write a NEW safeguard implementation narrative addressing the linked risk. Include the proposed owner role, concrete enforcement actions and verification evidence; do not copy the risk narrative.',
            }[slot['activity_number']]] if checkpoint else []))
    except Exception as exc:
        trace=exc.__traceback__
        while trace:
            if trace.tb_frame.f_code.co_name in {'generate_quality_draft','generate_structured'}:
                raw=trace.tb_frame.f_locals.get('output') or trace.tb_frame.f_locals.get('parsed')
                if isinstance(raw,dict):
                    print(json.dumps({'event':'rejected_raw_model_output','reference':slot['draft_reference'],'output':raw,'content_substituted':False}),flush=True)
                    break
            trace=trace.tb_next
        print(json.dumps({'event':'rejected','reference':slot['draft_reference'],'reason':getattr(exc,'error_code',None) or str(exc)[:180],'elapsed_seconds':round(time.monotonic()-started,2),'content_substituted':False}),flush=True)
        raise
    item.update(provenance='qwen_quality_single_authenticated_v7',framework_id=meta['framework_id'],source_digest=digest,
                generation_focus_requirement_id=focus['requirement_id'],generation_focus_reference=focus['reference'])
    accepted.append(item)
    print(json.dumps({'event':'accepted','elapsed_seconds':round(time.monotonic()-started,2),'record':item}),flush=True)
print(json.dumps({'event':'chain_validated','references':[i['draft']['draft_reference'] for i in accepted],
                  'new_business_records_written':False,'additional_records_scheduled':len(slots)-len(accepted),
                  'all_16_activities_demonstrated':False,'approved_creation_demonstrated':False}),flush=True)
