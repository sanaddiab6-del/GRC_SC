"""One real, read-only local-model probe using the existing provider and validator.

Run with an existing environment containing the backend's dependencies. This
script writes only .sico-launch/probe-assets-final.json and never loads app settings.
"""
from __future__ import annotations

import json
import hashlib
from copy import deepcopy
from pathlib import Path
import runpy
import sys
import time
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.sico-launch/probe-assets-final.json'
PROMPT = ROOT / 'backend/ai_onboarding/prompts/batch_assets_v1.txt'
MODEL = 'qwen2.5:3b'
BASE_URL = 'http://127.0.0.1:11434'
PROMPT_VERSION = 'batch_assets_final_v1'


def asset_generation_schema():
    """Copy the real batch and asset schemas; require two unlinked assets."""
    from ai_onboarding.sico_batch_contract import BATCH_RESPONSE_SCHEMA
    from ai_onboarding.quality_sico_drafts_v5 import quality_wire_schema_for
    from jsonschema import Draft202012Validator

    schema = deepcopy(BATCH_RESPONSE_SCHEMA)
    records = schema['properties']['records']
    records.update(minItems=2, maxItems=2)
    record = records['items']
    actual = quality_wire_schema_for('assets')['properties']
    record['properties']['record_type'] = {'enum': ['assets']}
    record['properties']['title'] = deepcopy(actual['title'])
    common = ('content', 'evidence_request', 'verification_question')
    fields = {name: deepcopy(actual[name]) for name in common}
    fields.update(deepcopy(actual['attributes']['properties']))
    record['properties']['fields'] = {
        'type': 'object', 'additionalProperties': False,
        'required': [*common, *actual['attributes']['required']], 'properties': fields,
    }
    record['properties']['links']['maxItems'] = 0
    Draft202012Validator.check_schema(schema)
    return schema


def main():
    if OUTPUT.exists():
        raise RuntimeError('refusing_to_overwrite_existing_final_evidence')
    started = time.monotonic()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / 'backend'))
    result = {
        'model_name': MODEL, 'base_url': BASE_URL,
        'prompt_version': PROMPT_VERSION, 'status': 'PROPOSED_DRAFT',
        'latency_seconds': 0, 'attempts': 0,
        'requested_records': 2, 'max_output_tokens': 900,
        'accepted': [], 'rejected': [], 'raw_model_text': '',
        'database_connection_attempts': 0,
        'actual_http_requests': 0,
    }
    protected = [*sorted((ROOT / '.sico-launch').glob('probe*.json')),
                 *(ROOT / 'backend/ai_onboarding' / name for name in (
                     'llm_provider.py', 'sico_batch_contract.py', 'quality_sico_drafts_v5.py')),
                 ROOT / 'tests/test_sico_call_accounting.py']
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in protected}
    try:
        from django.conf import settings

        # Standalone, fail-closed settings: no tenant/database/catalog lookup.
        if settings.configured:
            raise RuntimeError('probe_requires_fresh_standalone_process')
        settings.configure(
            DATABASES={'default': {'ENGINE': 'django.db.backends.dummy'}},
            INSTALLED_APPS=[],
        )
        from django.db.backends.base.base import BaseDatabaseWrapper

        def deny_database(*args, **kwargs):
            result['database_connection_attempts'] += 1
            raise RuntimeError('database_access_forbidden_in_probe')

        with patch.object(BaseDatabaseWrapper, 'connect', deny_database), \
                patch.object(BaseDatabaseWrapper, 'ensure_connection', deny_database):
            from ai_onboarding import llm_provider
            from ai_onboarding.llm_config import (
                CAPABILITY_GRC_CAPABILITY_SELECTION, validate_local_base_url,
            )
            from ai_onboarding.llm_errors import AiProviderError
            from ai_onboarding.sico_batch_contract import validate_batch
            from jsonschema import Draft202012Validator

            fixture = runpy.run_path(str(ROOT / 'tests/test_sico_call_accounting.py'))
            objective, systems = fixture['OBJECTIVE'], fixture['SYSTEMS']
            if len(systems) != 11:
                raise RuntimeError('expected_eleven_fixture_systems')
            result['objective'] = objective
            result['systems'] = list(systems)
            system_prompt = PROMPT.read_text(encoding='utf-8')
            safe, warning = validate_local_base_url(BASE_URL)
            provider = llm_provider.LocalAiProvider(
                base_url=BASE_URL, base_url_safe=safe, base_url_warning=warning,
            )
            extract = llm_provider._extract_ollama_response_text
            original_urlopen = llm_provider.urllib.request.urlopen
            generation_schema = asset_generation_schema()
            result['generation_schema'] = generation_schema

            def capture_raw(payload):
                # Observe the real response; preserve the provider's exact value.
                raw = extract(payload)
                result['raw_model_text'] = raw if raw is not None else ''
                result['ollama_response_metadata'] = {
                    key: deepcopy(payload[key]) for key in (
                        'model', 'done', 'done_reason', 'total_duration', 'load_duration',
                        'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration',
                    ) if key in payload
                }
                return raw

            def schema_format(schema_name, transport_schema):
                assert schema_name == PROMPT_VERSION
                assert transport_schema == {'type': 'object'}
                return deepcopy(generation_schema)

            def verified_urlopen(request, *args, **kwargs):
                assert result['actual_http_requests'] == 0, 'second_request_forbidden'
                body = json.loads(request.data.decode('utf-8'))
                assert request.full_url == BASE_URL + '/api/generate'
                assert body['format'] == generation_schema
                assert body['model'] == MODEL
                assert body['options']['num_predict'] == 900
                assert kwargs['timeout'] == 230
                result['outgoing_request_verification'] = {
                    'verified_before_send': True, 'actual_format_is_schema': True,
                    'schema_sha256': hashlib.sha256(json.dumps(
                        body['format'], sort_keys=True, separators=(',', ':')
                    ).encode('utf-8')).hexdigest(),
                    'model': body['model'], 'max_output_tokens': 900,
                    'timeout_seconds': kwargs['timeout'],
                    'required_records': 2, 'record_type': 'assets', 'links_max_items': 0,
                }
                print(json.dumps(result['outgoing_request_verification']), flush=True)
                result['actual_http_requests'] += 1
                return original_urlopen(request, *args, **kwargs)

            # Record validation belongs to Session 4, not provider-wide schema
            # rejection: one malformed record must not discard its good peers.
            transport_schema = {'type': 'object'}
            user_payload = {'objective': objective, 'systems': list(systems)}
            prompt_args = dict(
                capability=CAPABILITY_GRC_CAPABILITY_SELECTION,
                system_prompt=system_prompt, user_payload=user_payload,
                json_schema=transport_schema, schema_name=PROMPT_VERSION,
            )
            result['prompt_characters'] = len(llm_provider._build_ollama_prompt(**prompt_args))
            remaining = 240 - (time.monotonic() - started)
            if remaining < 2:
                raise RuntimeError('probe_time_budget_exhausted_before_request')
            call_started = time.monotonic()
            result['attempts'] = 1
            try:
                # Only this capture hook is patched; inference, transport,
                # parsing and all record validators execute their real code.
                with patch.object(llm_provider, '_extract_ollama_response_text', capture_raw), \
                        patch.object(llm_provider, '_ollama_output_format', schema_format), \
                        patch.object(llm_provider.urllib.request, 'urlopen', verified_urlopen):
                    response = provider.generate_structured(
                        **prompt_args, model=MODEL,
                        timeout_seconds=230,
                        max_output_tokens=900, temperature=0.1,
                    )
                result['generation_schema_errors'] = [
                    {'path': list(error.absolute_path), 'message': error.message}
                    for error in Draft202012Validator(generation_schema).iter_errors(response)
                ]
                validation = validate_batch(
                    response, tenant_id='offline-meridian-probe',
                    batch_id='meridian-assets-final-001', model_name=MODEL,
                    prompt_version=PROMPT_VERSION, attempt_number=1,
                    objective=objective,
                )
                result.update(validation)
            except AiProviderError as error:
                result['rejected'] = [{
                    'local_id': None, 'reason_code': error.error_code,
                    'feedback': error.detail,
                }]
            except ValueError as error:
                result['rejected'] = [{
                    'local_id': None, 'reason_code': str(error),
                    'feedback': 'The unchanged Session 4 validator rejected the batch envelope.',
                }]
            finally:
                result['latency_seconds'] = round(time.monotonic() - call_started, 3)
    except Exception as error:
        result['rejected'].append({
            'local_id': None, 'reason_code': 'probe_setup_or_execution_error',
            'feedback': type(error).__name__,
        })
    result['total_seconds'] = round(time.monotonic() - started, 3)
    result['preservation_checks'] = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
        for path, digest in before.items()
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    OUTPUT.write_text(encoded + '\n', encoding='utf-8')
    print(encoded)
    return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
