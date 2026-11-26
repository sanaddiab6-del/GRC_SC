from copy import deepcopy
from pathlib import Path

import pytest


TENANT = 'tenant-a'
PROVENANCE = {
    'batch_id': 'batch-001', 'model_name': 'mock-model',
    'prompt_version': 'mock-v1', 'attempt_number': 1,
}
OBJECTIVE = (
    'Assess the outbound network and dispatch service against the selected framework, document '
    'which control owners can explain network boundaries, and identify evidence gaps that require '
    'review by management before the next logistics planning cycle.'
)
DESCRIPTIONS = (
    'The dispatch application groups outbound pallets by destination, reserves loading doors, '
    'and reconciles carrier acknowledgements. A gateway outage could delay pick confirmations '
    'and leave dispatch operators unable to assign departures.',
    'The fleet telemetry platform tracks refrigerated trailer temperatures, flags compressor '
    'alarms, and stores odometer snapshots so the maintenance manager can compare service '
    'intervals with vehicle utilization.',
    'The settlement service compares carrier invoice surcharges with negotiated tariffs, '
    'queues disputed charges for an accounts reviewer, and exports reconciliation results '
    'for monthly finance close.',
    'The manifest archive database indexes sealed container declarations, retains signed '
    'customs release documents, and gives the export coordinator searchable access '
    'to shipment approvals during border inspections.',
)


@pytest.fixture
def contract(monkeypatch, request):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'backend'))
    from django.conf import settings

    if not settings.configured:
        original_settings = settings._wrapped
        settings.configure()
        request.addfinalizer(lambda: setattr(settings, '_wrapped', original_settings))

    from ai_onboarding import llm_provider, sico_batch_contract

    def fail_provider(*args, **kwargs):
        pytest.fail('Mock-only contract validation must not call a provider')

    monkeypatch.setattr(llm_provider.LocalAiProvider, 'generate_structured', fail_provider)
    return sico_batch_contract


def asset(local_id, index, *, links=()):
    subjects = ('Dispatch load scheduler', 'Refrigerated fleet telemetry',
                'Carrier settlement reconciliation', 'Customs manifest archive')
    return {
        'local_id': local_id, 'record_type': 'assets',
        'title': f'Asset: {subjects[index]}',
        'fields': {
            'content': DESCRIPTIONS[index],
            'evidence_request': 'Request the service inventory entry listing ownership and boundary details.',
            'verification_question': 'Can the owner confirm which applications exchange information with this service?',
            'asset_type': 'operational application platform',
            'business_purpose': subjects[index],
            'owner_role': 'Operations service owner',
            'information_classification': 'Internal operational information',
        },
        'links': list(links),
        'assumptions': ['The operating boundary is proposed.'],
        'needs_human_verification': ['Confirm the service owner.'],
    }


def validate(contract, response, **context):
    return contract.validate_batch(response, tenant_id=TENANT, objective=OBJECTIVE,
                                   **PROVENANCE, **context)


def test_six_records_keep_four_and_retry_only_two(contract):
    good = [
        asset('dispatch', 0, links=[{'link_type': 'related', 'target_local_id': 'manifest'}]),
        asset('fleet', 1),
        asset('settlement', 2),
        asset('manifest', 3),
    ]
    repetitive = asset('repetitive', 0)
    repetitive['fields']['content'] = 'dispatch application operator ' * 5
    long_title = asset('long-title', 1)
    long_title['title'] = 'Asset: ' + 'overspecified ' * 10
    response = {'records': [good[0], repetitive, *good[1:], long_title]}
    original = deepcopy(response)

    result = validate(contract, response)

    assert [row['local_id'] for row in result['accepted']] == [row['local_id'] for row in good]
    assert all(row['provenance'] == PROVENANCE and row['tenant_id'] == TENANT
               for row in result['accepted'])
    assert [(row['local_id'], row['reason_code']) for row in result['rejected']] == [
        ('repetitive', 'low_information_repetitive_description'),
        ('long-title', 'invalid_title_length'),
    ]
    retry = contract.build_retry_request(response, result)
    assert [item['record'] for item in retry['records']] == [repetitive, long_title]
    assert [item['feedback'] for item in retry['records']] == [
        rejection['feedback'] for rejection in result['rejected']
    ]
    assert all(item['feedback'] for item in retry['records'])
    assert response == original
    print('6 mock records: 4 accepted, 2 rejected, 2 in retry; provenance on all accepted records')


def test_bad_links_reject_only_the_source_record(contract):
    response = {'records': [
        asset('dangling', 0, links=[{'link_type': 'related', 'target_local_id': 'missing'}]),
        asset('foreign', 1, links=[{'link_type': 'related', 'existing_id': 'outside'}]),
        asset('unlisted', 2, links=[{'link_type': 'related', 'existing_id': 'not-authorized'}]),
        asset('valid', 3, links=[
            {'link_type': 'related', 'existing_id': 'prior-draft'},
            {'link_type': 'related', 'existing_id': 'catalog-id'},
        ]),
    ]}
    result = validate(
        contract, response,
        accepted_drafts={'prior-draft': {**asset('prior', 0), 'tenant_id': TENANT}},
        authorized_existing={'catalog-id': {'tenant_id': TENANT}, 'outside': {'tenant_id': 'tenant-b'}},
    )
    assert [row['local_id'] for row in result['accepted']] == ['valid']
    assert [(row['local_id'], row['reason_code']) for row in result['rejected']] == [
        ('dangling', 'dangling_link'), ('foreign', 'cross_tenant_link'), ('unlisted', 'dangling_link'),
    ]
    print('dangling, unlisted and cross-tenant mock links individually rejected')


def test_mock_record_copying_objective_is_rejected(contract):
    copied = asset('objective-copy', 0)
    copied['fields']['content'] = OBJECTIVE
    result = validate(contract, {'records': [copied]})
    assert result['accepted'] == []
    assert [row['reason_code'] for row in result['rejected']] == [
        'copied_assessment_objective_not_new_record',
    ]
    print('mock record restating the objective rejected')


def test_copied_parent_and_its_dependent_do_not_discard_other_records(contract):
    parent = asset('parent', 0)
    dependent = asset('blocked', 1, links=[{'link_type': 'related', 'target_local_id': 'copy'}])
    copy = asset('copy', 2, links=[{'link_type': 'asset', 'target_local_id': 'parent'}])
    copy.update(record_type='threats', title='Threat hypothesis: Loading gateway outage')
    copy['fields'] = {
        **{key: parent['fields'][key] for key in ('content', 'evidence_request', 'verification_question')},
        'asset_reference': 'parent', 'threat_source': 'Unavailable gateway service',
        'weakness_hypothesis': 'The gateway owner may lack a failover channel',
        'impact_if_realized': 'Delayed carrier departure',
    }
    result = validate(contract, {'records': [dependent, copy, parent, asset('independent', 3)]})
    assert [row['local_id'] for row in result['accepted']] == ['parent', 'independent']
    assert [(row['local_id'], row['reason_code']) for row in result['rejected']] == [
        ('blocked', 'unaccepted_local_target'), ('copy', 'copied_parent_narrative_not_new_record'),
    ]


def test_malformed_mock_rows_do_not_poison_valid_records(contract):
    invalid_link = asset('ambiguous', 0, links=[
        {'link_type': 'related', 'target_local_id': 'valid', 'existing_id': 'catalog-id'},
    ])
    response = {'records': [None, invalid_link, asset('valid', 1)]}
    result = validate(contract, response)
    assert [row['local_id'] for row in result['accepted']] == ['valid']
    assert [(row['local_id'], row['reason_code']) for row in result['rejected']] == [
        (None, 'invalid_record_shape'), ('ambiguous', 'invalid_record_shape'),
    ]
    assert [row['record'] for row in contract.build_retry_request(response, result)['records']] == [
        None, invalid_link,
    ]
