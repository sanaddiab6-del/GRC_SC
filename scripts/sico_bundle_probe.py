"""Two dependency-aware real offline requests; existing provider/contracts, in-memory container runner.

Only the host writes evidence, exclusively to .sico-launch/probe-bundles-manual-v2.json.
No application settings, ORM, persisted objects, installations or container files.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.sico-launch/probe-bundles-manual-v2.json'
PROMPT = ROOT / 'backend/ai_onboarding/prompts/batch_bundles_v1.txt'
MODEL = 'qwen2.5:3b'
VERSION = 'batch_bundles_compact_v2'
TYPES = ('threats', 'risk_scenarios', 'applied_controls', 'evidence_requests')
IDS = ('t1', 'r1', 'c1', 'e1')


def semantic_errors(row, asset, requirement_ids):
    """Additional probe gates; never relax or replace the existing validators."""
    errors = []
    fields = row.get('fields', {})
    content = fields.get('content', '')
    kind = row.get('record_type')
    if not row.get('assumptions') or not row.get('needs_human_verification'):
        errors.append('missing_assumptions_or_human_verification')
    narrative = ' '.join([content, *fields.values()])
    if re.search(r'\b(?:is|are|was|were|has been|have been)\s+(?:implemented|effective|verified|compliant|approved)\b', narrative, re.I):
        errors.append('unverified_implementation_or_effectiveness_claim')
    if kind == 'threats':
        steps = re.findall(r'(?<!\w)([1-4])\)', content)
        if steps not in (['1', '2'], ['1', '2', '3'], ['1', '2', '3', '4']):
            errors.append('attack_path_requires_two_to_four_ordered_steps')
        if asset['title'].removeprefix('Asset: ').casefold() not in content.casefold():
            errors.append('attack_path_must_name_accepted_asset')
    if kind == 'risk_scenarios':
        if not all(label in content.casefold() for label in ('event:', 'cause:', 'consequence:', 'rationale:')):
            errors.append('risk_missing_event_cause_consequence_or_rationale')
        for dimension in ('likelihood', 'impact'):
            if not re.search(r'PROPOSED\s+' + dimension + r'=(low|medium|high)\b', content, re.I):
                errors.append('missing_proposed_' + dimension)
        rationale = content.casefold().split('rationale:', 1)[-1]
        if not all(term in rationale for term in ('likelihood', 'impact')):
            errors.append('ratings_need_separate_rationale')
    if kind == 'applied_controls':
        refs = re.findall(r'requirement_id=([A-Za-z0-9_.:-]+)', fields.get('control_objective', ''))
        if len(refs) != 1 or refs[0] not in requirement_ids:
            errors.append('control_requirement_id_not_in_fixture')
        steps = fields.get('implementation_steps', '')
        if not re.search(r'\b(daily|weekly|monthly|quarterly|annually|per change|each change)\b', steps, re.I):
            errors.append('control_missing_action_frequency')
        if 'implementation and effectiveness unverified' not in content.casefold():
            errors.append('control_missing_unverified_proposal_statement')
    if kind == 'evidence_requests':
        if not re.search(r'source_system=\S', fields.get('request_scope', '')):
            errors.append('evidence_missing_source_system')
        if not re.search(r'\b(owner|manager|analyst|engineer|administrator|officer|team|lead|custodian|operator|reviewer)\b', fields.get('request_owner_role', ''), re.I):
            errors.append('evidence_owner_must_be_role')
    return errors


def canonical_schema(asset, request_number, accepted_context):
    """Complete existing activity schema with deterministic authorized links."""
    from ai_onboarding.sico_batch_contract import BATCH_RESPONSE_SCHEMA
    from ai_onboarding.quality_sico_drafts_v5 import quality_wire_schema_for
    kinds = TYPES[:2] if request_number == 1 else TYPES[2:]
    ids = IDS[:2] if request_number == 1 else IDS[2:]
    aid = asset['local_id']
    if request_number == 2 and not all(
            accepted_context.get(i, {}).get('record_type') == k
            for i, k in zip(IDS[:2], TYPES[:2])):
        raise ValueError('request_two_requires_accepted_threat_and_risk')
    references = {'threats': {'asset_reference': aid}, 'risk_scenarios': {'asset_reference': aid},
                  'applied_controls': {'linked_risk_reference': 'r1'},
                  'evidence_requests': {'linked_control_reference': 'c1'}}
    links = {'threats': [{'link_type': 'asset', 'existing_id': aid}],
             'risk_scenarios': [{'link_type': 'asset', 'existing_id': aid},
                                {'link_type': 'threat', 'target_local_id': 't1'}],
             'applied_controls': [{'link_type': 'risk', 'existing_id': 'r1'}],
             'evidence_requests': [{'link_type': 'control', 'target_local_id': 'c1'}]}
    schema = {'type': 'object', 'additionalProperties': False,
              'required': list(kinds), 'properties': {}}
    for kind, local_id in zip(kinds, ids):
        row = deepcopy(BATCH_RESPONSE_SCHEMA['properties']['records']['items'])
        props = row['properties']
        props['local_id'] = {'const': local_id}
        props['record_type'] = {'const': kind}
        actual = quality_wire_schema_for(kind)['properties']
        props['title'] = deepcopy(actual['title'])
        fields = {name: deepcopy(actual[name]) for name in ('content', 'evidence_request', 'verification_question')}
        fields.update(deepcopy(actual['attributes']['properties']))
        for name, value in references[kind].items():
            fields[name] = {'const': value}
        props['fields'] = {'type': 'object', 'additionalProperties': False,
                           'required': list(fields), 'properties': fields}
        props['links'] = {'const': links[kind]}
        props['assumptions']['minItems'] = 1
        props['needs_human_verification']['minItems'] = 1
        schema['properties'][kind] = row
    return schema


def generation_schema(asset, request_number, accepted_context, requirement_ids=()):
    """Model generates analysis only; no IDs, links or duplicated reference fields."""
    from ai_onboarding.quality_sico_drafts_v5 import CONTRACTS
    canonical = canonical_schema(asset, request_number, accepted_context)
    schema = {'type': 'object', 'additionalProperties': False,
              'required': list(canonical['required']), 'properties': {}}
    def text(lo=3, hi=180):
        return {'type': 'string', 'minLength': lo, 'maxLength': hi}
    for kind, row in canonical['properties'].items():
        props = row['properties']
        fields = {name: deepcopy(spec) for name, spec in props['fields']['properties'].items()
                  if 'const' not in spec}
        prefix = CONTRACTS[kind][0]
        flat = {'subject': text(10, props['title']['maxLength'] - len(prefix) - 1)}
        if kind == 'threats':
            del fields['content']
            flat.update(owner_role=text(), attack_steps={'type': 'array', 'minItems': 2, 'maxItems': 4,
                                                         'items': text(3, 180)})
        elif kind == 'risk_scenarios':
            for name in ('content', 'threat_event', 'business_impact'):
                del fields[name]
            flat.update({name: text() for name in ('event', 'cause', 'consequence', 'likelihood_rationale',
                                                   'impact_rationale', 'treatment_recommendation', 'owner_role')})
            flat.update({name: {'type': 'string', 'enum': ['low', 'medium', 'high']}
                         for name in ('proposed_likelihood', 'proposed_impact')})
        elif kind == 'applied_controls':
            if not requirement_ids:
                raise ValueError('no_fixture_requirements_supplied')
            flat['requirement_id'] = {'type': 'string', 'enum': list(requirement_ids)}
            # Leave room for the source-derived fixture reference in the existing field.
            fields['control_objective']['maxLength'] -= len('requirement_id=; ') + max(map(len, requirement_ids))
        flat.update(fields)
        for name in ('assumptions', 'needs_human_verification'):
            flat[name] = deepcopy(props[name])
        schema['properties'][kind] = {'type': 'object', 'additionalProperties': False,
                                      'required': list(flat), 'properties': flat}
    return schema


def assemble_record(kind, raw, canonical, asset):
    """Lossless projection into existing record shape. Only IDs and labels are added."""
    from ai_onboarding.quality_sico_drafts_v5 import CONTRACTS
    props = canonical['properties'][kind]['properties']
    fields = {key: deepcopy(spec['const']) if 'const' in spec else raw[key]
              for key, spec in props['fields']['properties'].items()
              if 'const' in spec or key in raw}
    row = {'local_id': props['local_id']['const'], 'record_type': kind,
           'title': CONTRACTS[kind][0] + ' ' + raw['subject'], 'fields': fields,
           'links': deepcopy(props['links']['const']), 'assumptions': deepcopy(raw['assumptions']),
           'needs_human_verification': deepcopy(raw['needs_human_verification'])}
    if kind == 'threats':
        row['analysis'] = {'asset_name': asset['title'].removeprefix('Asset: '),
                           'owner_role': raw['owner_role'], 'attack_steps': raw['attack_steps']}
        row = format_analysis_record(row)
    elif kind == 'risk_scenarios':
        row['analysis'] = {key: raw[key] for key in ('event', 'cause', 'consequence', 'proposed_likelihood',
                           'likelihood_rationale', 'proposed_impact', 'impact_rationale', 'treatment_recommendation', 'owner_role')}
        row = format_analysis_record(row)
    elif kind == 'applied_controls':
        fields['control_objective'] = 'requirement_id=' + raw['requirement_id'] + '; ' + raw['control_objective']
    return row


def format_analysis_record(raw):
    """Lossless labels/order only; all substantive values must come from Qwen."""
    row = deepcopy(raw)
    analysis = row.pop('analysis', None)
    if analysis is None:
        return row
    fields = row['fields']
    if row['record_type'] == 'threats':
        steps = ' '.join(f'{index}) {step}' for index, step in enumerate(analysis['attack_steps'], 1))
        content = (f"Asset: {analysis['asset_name']}; Owner role: {analysis['owner_role']}; "
                   f"Attack path: {steps}; Threat source: {fields['threat_source']}; "
                   f"Weakness hypothesis: {fields['weakness_hypothesis']}; "
                   f"Business consequence: {fields['impact_if_realized']}")
    else:
        content = (f"Risk EVENT: {analysis['event']}; CAUSE: {analysis['cause']}; "
                   f"CONSEQUENCE: {analysis['consequence']}; "
                   f"PROPOSED likelihood={analysis['proposed_likelihood']}; "
                   f"PROPOSED impact={analysis['proposed_impact']}; "
                   f"rationale: likelihood: {analysis['likelihood_rationale']}; "
                   f"impact: {analysis['impact_rationale']}; "
                   f"Treatment recommendation: {analysis['treatment_recommendation']}; "
                   f"Owner role: {analysis['owner_role']}")
        fields['threat_event'] = analysis['event']
        fields['business_impact'] = analysis['consequence']
    # Refuse loss or truncation: overlength content fails the original schema.
    for value in analysis.values():
        for fragment in value if isinstance(value, list) else [value]:
            if fragment not in content:
                raise ValueError('analysis_formatting_would_lose_model_text')
    fields['content'] = content
    return row


def validate_request(response, schema, context, accepted_context, request_number):
    """Keep valid peers; reuse unchanged semantic and relationship validators."""
    from ai_onboarding.sico_batch_contract import validate_batch
    from jsonschema import Draft202012Validator
    candidates, rejected, formatted = [], [], []
    original_schema = canonical_schema(context['asset'], request_number, accepted_context)
    for kind in schema['required']:
        raw = response.get(kind)
        errors = list(Draft202012Validator(schema['properties'][kind]).iter_errors(raw))
        row = raw
        if not errors:
            row = assemble_record(kind, raw, original_schema, context['asset'])
            formatted.append(deepcopy(row))
            errors = list(Draft202012Validator(original_schema['properties'][kind]).iter_errors(row))
        reasons = ['invalid_activity_specific_shape'] if errors else semantic_errors(
            row, context['asset'], {r['requirement_id'] for r in context['requirements']})
        if not errors and kind == 'threats':
            generated_steps = ' '.join(raw['attack_steps'])
            if context['asset']['title'].removeprefix('Asset: ').casefold() not in generated_steps.casefold():
                reasons.append('attack_path_must_name_accepted_asset')
            if not re.search(r'\b(could|may|might|if|potential\w*|hypothetic\w*)\b', generated_steps, re.I):
                reasons.append('attack_path_requires_conditional_hypothesis')
        if reasons:
            rejected.append({'local_id': row.get('local_id') if isinstance(row, dict) else None,
                             'record_type': kind, 'reason_code': reasons[0],
                             'all_reasons': reasons, 'record': deepcopy(row), 'raw_record': deepcopy(raw),
                             'schema_errors': [{'path': list(e.absolute_path), 'message': e.message} for e in errors]})
        else:
            candidates.append(row)
    if candidates:
        validation = validate_batch(
            {'records': candidates}, tenant_id=context['asset']['tenant_id'],
            batch_id=f'meridian-bundles-compact-v2-{request_number:03d}', model_name=MODEL,
            prompt_version=VERSION, attempt_number=1, objective=context['objective'],
            accepted_drafts=accepted_context, allowed_requirements=context['requirements'])
        raw_by_id = {row['local_id']: row for row in candidates}
        rejected.extend({**item, 'record': deepcopy(raw_by_id.get(item['local_id']))}
                        for item in validation['rejected'])
        accepted = validation['accepted']
    else:
        accepted = []
    return {'accepted': accepted, 'rejected': rejected, 'formatted_records': formatted}


def execute_probe(context):
    from unittest.mock import patch
    from django.conf import settings
    settings.configure(DATABASES={'default': {'ENGINE': 'django.db.backends.dummy'}}, INSTALLED_APPS=[])
    from django.db.backends.base.base import BaseDatabaseWrapper
    result = dict(model_name=MODEL, prompt_version=VERSION, status='PROPOSED_DRAFT',
                  requested_assets=1, requested_records=4, attempts=0, actual_http_requests=0,
                  latency_seconds=0, accepted=[], rejected=[], requests=[],
                  database_connection_attempts=0, max_requests=2, timeout_per_request_seconds=230,
                  contract_note='weakness_hypothesis remains the existing threat field.',
                  requirement_source='Synthetic test fixture IDs; not official NIST requirement text.')
    started = time.monotonic()

    def deny_database(*args, **kwargs):
        result['database_connection_attempts'] += 1
        raise RuntimeError('database_access_forbidden_in_probe')

    try:
        with patch.object(BaseDatabaseWrapper, 'connect', deny_database), patch.object(BaseDatabaseWrapper, 'ensure_connection', deny_database):
            from ai_onboarding import llm_provider
            from ai_onboarding.llm_config import CAPABILITY_GRC_CAPABILITY_SELECTION
            from jsonschema import Draft202012Validator
            asset = context['asset']
            accepted_context = {asset['local_id']: asset}
            result['input_asset'] = asset
            result['risk_methodology'] = {'formal_score': None, 'selected_authorized_matrix': None,
                'status': 'qualitative_proposals_only_requires_assessor_and_selected_SICO_matrix',
                'source': 'sico_case_coverage.calculate_proposed_risk; quality_sico_drafts_v5 risk_detail'}
            result['allowed_requirement_ids'] = [r['requirement_id'] for r in context['requirements']]
            extract = llm_provider._extract_ollama_response_text
            urlopen = llm_provider.urllib.request.urlopen
            common, threat_prompt, control_prompt = context['prompt'].split('\n---\n')
            # Only accepted context is passed across the dependency boundary.
            for number, stage_prompt, token_budget in ((1, threat_prompt, 1000), (2, control_prompt, 1100)):
                fixture_rows = context['requirements'][:15] if number == 2 else []
                schema = generation_schema(asset, number, accepted_context,
                                           [r['requirement_id'] for r in fixture_rows])
                Draft202012Validator.check_schema(schema)
                Draft202012Validator.check_schema(canonical_schema(asset, number, accepted_context))
                for kind, spec in schema['properties'].items():
                    assert set(spec['required']) == set(spec['properties'])
                    assert not {'local_id', 'record_type', 'links', 'asset_reference',
                                'linked_risk_reference', 'linked_control_reference'} & set(spec['properties'])
                request_result = dict(request_number=number, attempts=1, max_output_tokens=token_budget,
                                      timeout_seconds=230, latency_seconds=0, raw_model_text='',
                                      accepted=[], rejected=[], status='pending')
                result['requests'].append(request_result)
                result['attempts'] += 1
                payload = {
                    'organization': 'Meridian Logistics Group', 'framework': 'NIST CSF 2.0',
                    'asset_title': asset['title'].removeprefix('Asset: '),
                    'asset_hypothesis': {key: value for key, value in asset['fields'].items()
                                         if key not in ('evidence_request', 'verification_question')},
                    'asset_assumptions': asset['assumptions'],
                    'required_keys': {kind: list(spec['required']) for kind, spec in schema['properties'].items()}}
                if number == 2:
                    payload['accepted_parents'] = [
                        {'title': row['title'], 'record_type': row['record_type'],
                         'fields': {key: value for key, value in row['fields'].items()
                                    if key not in ('evidence_request', 'verification_question', 'asset_reference')},
                         'assumptions': row['assumptions']}
                        for row in result['accepted']]
                    payload['fixture_requirements'] = [
                        {key: row[key] for key in ('requirement_id', 'requirement_name')}
                        for row in fixture_rows]

                def capture(response_payload):
                    raw = extract(response_payload)
                    request_result['raw_model_text'] = raw or ''
                    request_result['raw_ollama_response'] = deepcopy(response_payload)
                    return raw

                def verify_request(request, *args, **kwargs):
                    if result['actual_http_requests'] != number - 1 or number > 2:
                        raise RuntimeError('request_budget_or_order_violation')
                    body = json.loads(request.data)
                    assert request.full_url == 'http://host.docker.internal:11434/api/generate'
                    assert body['model'] == MODEL and body['format'] == schema
                    assert kwargs['timeout'] == 230
                    request_result['outgoing_request_verification'] = {
                        'actual_format_is_schema': True, 'model': body['model'],
                        'timeout_seconds': kwargs['timeout'], 'max_output_tokens': body['options']['num_predict'],
                        'schema_sha256': hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()}
                    request_result['generation_schema'] = schema
                    result['actual_http_requests'] += 1
                    return urlopen(request, *args, **kwargs)

                call_started = time.monotonic()
                try:
                    with patch.object(llm_provider, '_extract_ollama_response_text', capture), \
                         patch.object(llm_provider, '_ollama_output_format', lambda name, value: schema), \
                         patch.object(llm_provider.urllib.request, 'urlopen', verify_request):
                        response = llm_provider.LocalAiProvider(
                            base_url='http://host.docker.internal:11434', base_url_safe=True, base_url_warning=None,
                        ).generate_structured(
                            capability=CAPABILITY_GRC_CAPABILITY_SELECTION, model=MODEL,
                            system_prompt=common + '\n' + stage_prompt, user_payload=payload,
                            json_schema={'type': 'object'}, schema_name=VERSION,
                            timeout_seconds=230, max_output_tokens=token_budget, temperature=0.1)
                    request_result['parsed_response'] = deepcopy(response)
                    validation = validate_request(response, schema, context, accepted_context, number)
                    request_result.update(validation)
                    request_result['status'] = 'accepted' if len(validation['accepted']) == 2 and not validation['rejected'] else 'partial_or_rejected'
                    result['accepted'].extend(validation['accepted'])
                    result['rejected'].extend(validation['rejected'])
                except Exception as error:
                    rejection = {'local_id': None, 'request_number': number,
                                 'reason_code': getattr(error, 'error_code', type(error).__name__),
                                 'feedback': str(error)[:300], 'record': None}
                    request_result['rejected'].append(rejection)
                    result['rejected'].append(rejection)
                    request_result['status'] = 'rejected'
                finally:
                    request_result['latency_seconds'] = round(time.monotonic() - call_started, 3)
                print('PROGRESS ' + json.dumps({key: request_result[key] for key in (
                    'request_number', 'latency_seconds', 'status', 'accepted', 'rejected')}), flush=True)
                if request_result['status'] != 'accepted':
                    result['stopped_after_request'] = number
                    result['downstream_skipped'] = number == 1
                    break
                accepted_context.update({row['local_id']: row for row in request_result['accepted']})
    except Exception as error:
        result['rejected'].append({'local_id': None, 'reason_code': type(error).__name__, 'feedback': str(error)[:300], 'record': None})
    accepted = {row['local_id']: row for row in result['accepted']}
    counts = Counter(row['record_type'] for row in result['accepted'])
    result['bundle_status'] = 'accepted' if all(counts[k] == 1 for k in TYPES) and not result['rejected'] else 'partial_or_rejected'
    all_targets = {context['asset']['local_id']: context['asset'], **accepted}
    edges = []
    for row in result['accepted']:
        for link in row['links']:
            target_id = link.get('target_local_id', link.get('existing_id'))
            target = all_targets.get(target_id)
            resolved = target is not None and target['tenant_id'] == row['tenant_id']
            edges.append({'source': row['local_id'], 'target': target_id,
                          'status': 'resolved' if resolved else 'rejected'})
    result['link_resolution'] = {
        'links': edges, 'resolved': sum(e['status'] == 'resolved' for e in edges),
        'rejected': sum(e['status'] == 'rejected' for e in edges),
        'accepted_links_all_resolve': bool(edges) and all(e['status'] == 'resolved' for e in edges),
        'requested_bundle_present': result['bundle_status'] == 'accepted'}
    result['latency_seconds'] = round(sum(r['latency_seconds'] for r in result['requests']), 3)
    result['total_seconds'] = round(time.monotonic() - started, 3)
    return result


def main():
    if OUTPUT.exists():
        raise RuntimeError('refusing_to_overwrite_existing_probe_evidence')
    sys.dont_write_bytecode = True
    fixture_path = ROOT / 'tests/test_sico_call_accounting.py'
    fixture = runpy.run_path(str(fixture_path))
    prior = json.loads((ROOT / '.sico-launch/probe-assets.json').read_text(encoding='utf-8'))
    assets = prior.get('accepted', [])
    if not assets or assets[0].get('record_type') != 'assets' or not assets[0].get('tenant_id'):
        raise RuntimeError('no_accepted_asset_in_required_input')
    sources = {f'ai_onboarding.{p.stem}': p.read_text(encoding='utf-8-sig')
               for p in (ROOT / 'backend/ai_onboarding').glob('*.py')}
    sources['ai_onboarding'] = sources.pop('ai_onboarding.__init__')
    # Derive prompt field names from the real contract AST, without host Django.
    import ast
    tree = ast.parse(sources['ai_onboarding.quality_sico_drafts_v5'])
    contracts = next(ast.literal_eval(node.value) for node in tree.body
                     if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CONTRACTS' for t in node.targets))
    context = dict(asset=assets[0], requirements=fixture['REQUIREMENTS'], objective=prior['objective'],
                   prompt=PROMPT.read_text(encoding='utf-8'),
                   record_fields={kind: list(contracts[kind][1]) for kind in TYPES})
    protected = [ROOT / 'AGENTS.md', ROOT / '.github/copilot-instructions.md']
    protected = [p for p in protected if p.is_file()]
    protected += list((ROOT / '.sico-launch').glob('probe*.json'))
    protected += list((ROOT / 'backend/ai_onboarding').glob('*.py'))
    protected += [fixture_path, ROOT / 'scripts/sico_batch_probe.py']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    # Load the checked-out source into memory in the existing dependency runtime.
    # This neither copies files into the container nor loads production settings.
    runner = '''import sys,json,importlib.abc,importlib.util
sys.dont_write_bytecode=True
sys.path.insert(0,'/code')
payload=json.loads(PAYLOAD)
class MemorySource(importlib.abc.MetaPathFinder,importlib.abc.Loader):
 def find_spec(self,fullname,path=None,target=None):
  if fullname in payload['sources']:
   return importlib.util.spec_from_loader(fullname,self,is_package=fullname=='ai_onboarding')
 def create_module(self,spec): return None
 def exec_module(self,module):
  module.__file__='/code/'+module.__name__.replace('.','/')+'.py'
  exec(compile(payload['sources'][module.__name__],module.__file__,'exec'),module.__dict__)
sys.meta_path.insert(0,MemorySource())
namespace={'__name__':'sico_probe_memory','__file__':'/code/scripts/sico_bundle_probe.py'}
exec(compile(payload['script'],namespace['__file__'],'exec'),namespace)
print('RESULT ' + json.dumps(namespace['execute_probe'](payload['context'])))
'''
    payload = json.dumps(dict(sources=sources, context=context, script=Path(__file__).read_text(encoding='utf-8')))
    runner = runner.replace('PAYLOAD', repr(payload))
    completed = subprocess.run(['docker', 'exec', '-i', 'amro-backend', '/code/.venv/bin/python', '-B', '-'],
                               input=runner, text=True, capture_output=True, timeout=490, encoding='utf-8')
    if completed.returncode:
        raise RuntimeError('container_probe_failed: ' + completed.stderr[-1500:])
    lines = completed.stdout.splitlines()
    for line in lines:
        if line.startswith('PROGRESS '):
            print(line, flush=True)
    result = json.loads(next(line[7:] for line in lines if line.startswith('RESULT ')))
    result['preservation_checks'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
                                     for name, digest in before.items()}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('model_name', 'requested_assets', 'attempts', 'actual_http_requests',
                      'latency_seconds', 'total_seconds', 'bundle_status', 'database_connection_attempts', 'link_resolution')}, indent=2))
    print('accepted=' + json.dumps(result['accepted'], ensure_ascii=False, indent=2))
    print('rejected=' + json.dumps(result['rejected'], ensure_ascii=False, indent=2))
    print('protected_files_unchanged=' + str(all(result['preservation_checks'].values())))
    return 0 if result['bundle_status'] == 'accepted' else 1


if __name__ == '__main__':
    raise SystemExit(main())
