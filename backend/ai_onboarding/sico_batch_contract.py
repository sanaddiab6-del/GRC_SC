"""Validate one proposed batch without scheduling work or calling a model.

Record types are SICO activity codes. Fields use the existing quality contract
names plus content, evidence_request and verification_question. In-batch links
use target_local_id. existing_id can name a previously accepted draft or an
existing record from server-authorized context. External context is keyed by ID
and carries tenant_id and, when known, record_type and the same draft fields.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from copy import deepcopy
import re

from jsonschema import Draft202012Validator

from .quality_sico_drafts_v5 import CONTRACTS, quality_wire_schema_for, validate_draft
from .sico_ai_case_draft_views import DRAFT_ACTIVITIES
from .sico_case_coverage import MODEL_BATCH_SIZE


_ID_PATTERN = r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}'
_ID = {'type': 'string', 'pattern': f'^{_ID_PATTERN}$'}
_TEXT_LIST = {'type': 'array', 'items': {'type': 'string', 'minLength': 1, 'maxLength': 360}}
_RECORD_PROPERTIES = {
    'local_id': _ID,
    'record_type': {'enum': list(CONTRACTS)},
    'title': {'type': 'string'},
    'fields': {'type': 'object', 'additionalProperties': {'type': 'string'}},
    'links': {
        'type': 'array', 'maxItems': 3,
        'items': {
            'type': 'object', 'additionalProperties': False,
            'required': ['link_type'],
            'properties': {
                'link_type': _ID, 'target_local_id': _ID, 'existing_id': _ID,
            },
            'oneOf': [{'required': ['target_local_id']}, {'required': ['existing_id']}],
        },
    },
    'assumptions': _TEXT_LIST,
    'needs_human_verification': _TEXT_LIST,
}
_RECORD_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': list(_RECORD_PROPERTIES), 'properties': _RECORD_PROPERTIES,
}
BATCH_RESPONSE_SCHEMA = {
    'type': 'object', 'additionalProperties': False, 'required': ['records'],
    'properties': {
        'records': {
            'type': 'array', 'minItems': 1, 'maxItems': MODEL_BATCH_SIZE, 'items': _RECORD_SCHEMA,
        },
    },
}
_RECORD_VALIDATOR = Draft202012Validator(_RECORD_SCHEMA)
_ACTIVITIES = {
    code: (number, model, dependencies)
    for number, (code, _, model, _, dependencies, _) in enumerate(DRAFT_ACTIVITIES, 1)
}
_QUALITY_TEXT = ('content', 'evidence_request', 'verification_question')
_REFERENCE_FIELDS = frozenset({'asset_reference', 'linked_risk_reference', 'linked_control_reference'})
_COPIED_PARENT = 'copied_parent_narrative_not_new_record'
_FEEDBACK = {
    'invalid_record_shape': 'Return all required record fields with the declared types.',
    'invalid_record_fields': 'Use the required fields and lengths for this record type.',
    'invalid_title_length': 'Use a title within the existing length limits for this record type.',
    'duplicate_local_id': 'Use a unique local ID for each requested record.',
    'duplicate_link_target': 'List the target once and give each target an unambiguous ID.',
    'dangling_link': 'Link only to a known batch record or an authorized existing reference.',
    'cross_tenant_link': 'Choose an authorized target in the current tenant.',
    'unaccepted_local_target': 'Use an accepted record or remove the unaccepted or circular link.',
    'low_information_repetitive_description': 'Add distinct case-specific details to the description.',
    _COPIED_PARENT: 'Describe the new record in its own terms using the parent only as context.',
    'copied_assessment_objective_not_new_record': 'Propose a concrete record that advances the objective.',
}


class _RejectedRecord(ValueError):
    pass


def _batch_rows(response):
    if (
        not isinstance(response, dict) or set(response) != {'records'}
        or not isinstance(response['records'], list)
        or not 1 <= len(response['records']) <= MODEL_BATCH_SIZE
    ):
        raise ValueError('invalid_batch_envelope')
    return response['records']


def _local_id(record):
    value = record.get('local_id') if isinstance(record, dict) else None
    return value if isinstance(value, str) and re.fullmatch(_ID_PATTERN, value) else None


def _rejection(record, reason):
    return {
        'local_id': _local_id(record), 'reason_code': reason,
        'feedback': _FEEDBACK.get(reason, 'Correct the record to satisfy its existing activity contract.'),
    }


def _link_targets(record, accepted, outstanding, all_ids, tenant_id, external_drafts, existing):
    linked = {}
    waiting = False
    for link in record['links']:
        if 'target_local_id' in link:
            target_id = link['target_local_id']
            if target_id not in all_ids:
                raise _RejectedRecord('dangling_link')
            target = accepted.get(target_id)
            if target is None and target_id not in outstanding:
                raise _RejectedRecord('unaccepted_local_target')
            waiting |= target is None
        else:
            target_id = link['existing_id']
            if target_id in external_drafts and target_id in existing:
                raise _RejectedRecord('duplicate_link_target')
            target = external_drafts.get(target_id, existing.get(target_id))
            if not isinstance(target, Mapping):
                raise _RejectedRecord('dangling_link')
            if target.get('tenant_id') != tenant_id:
                raise _RejectedRecord('cross_tenant_link')
        if target_id in linked:
            raise _RejectedRecord('duplicate_link_target')
        linked[target_id] = target
    return None if waiting else linked


def _quality_attributes(fields, references):
    return {
        field: references.get(value, value) if field in _REFERENCE_FIELDS else value
        for field, value in fields.items() if field not in _QUALITY_TEXT
    }


def _validate_quality(record, targets, earlier_same, objective, allowed_requirements):
    activity = record['record_type']
    dependencies = _ACTIVITIES[activity][2]
    # The existing validator encodes the parent activity number into draft refs.
    # Translate explicit links only in the validation copy; preserve all wire IDs.
    references = {
        target_id: f'draft-{_ACTIVITIES.get(target.get("record_type"), (0, "", ()))[0]:02d}-{i:02d}'
        for i, (target_id, target) in enumerate(targets.items(), 1)
    }
    parents = []
    by_activity = {}
    for target_id, target in targets.items():
        target_activity = target.get('record_type')
        number, model, _ = _ACTIVITIES.get(target_activity, (0, '', ()))
        ref = references[target_id]
        if number in dependencies:
            by_activity.setdefault(target_activity, []).append(ref)
        fields = target.get('fields', {})
        parents.append({
            'draft_reference': ref, 'record_type': model,
            'title': target.get('title', ''), 'content': fields.get('content', ''),
            'proposed_attributes': [
                {'field': field, 'proposed_value': value}
                for field, value in _quality_attributes(fields, references).items()
            ],
        })
    related = [ref for refs in by_activity.values() for ref in refs]
    fields = record['fields']
    draft = {
        'title': record['title'],
        **{field: fields[field] for field in _QUALITY_TEXT if field in fields},
        'attributes': _quality_attributes(fields, references),
        'related_draft_references': related,
    }
    schema = quality_wire_schema_for(
        activity, allowed_related=related, candidate_assets=by_activity.get('assets', ()),
        candidate_controls=by_activity.get('applied_controls', ()),
        candidate_risks=by_activity.get('risk_scenarios', ()),
    )
    error = next(Draft202012Validator(schema).iter_errors(draft), None)
    if error:
        if list(error.path) == ['title'] and error.validator in {'minLength', 'maxLength'}:
            raise _RejectedRecord('invalid_title_length')
        raise _RejectedRecord('invalid_record_fields')
    draft['attributes'] = [
        {'field': field, 'proposed_value': value} for field, value in draft['attributes'].items()
    ]
    # A read-only objective context row lets the existing narrative check
    # reject objective copies without introducing a second similarity rule.
    objective_context = [{'draft_reference': 'draft-00-00', 'content': objective}] if objective else []
    try:
        validate_draft(activity, draft, earlier_same=earlier_same,
                       prior_records=[*objective_context, *parents], allowed_requirements=allowed_requirements)
    except ValueError as error:
        if str(error) == _COPIED_PARENT and objective_context:
            validate_draft(activity, draft, earlier_same=earlier_same,
                           prior_records=parents, allowed_requirements=allowed_requirements)
            raise _RejectedRecord('copied_assessment_objective_not_new_record') from None
        raise


def validate_batch(response, *, tenant_id, batch_id, model_name, prompt_version,
                   attempt_number, objective, accepted_drafts=None,
                   authorized_existing=None, allowed_requirements=()):
    """Validate a batch in input order; failed targets affect only their dependents.

    Tenant, provenance and the two external target maps are supplied by the
    trusted caller. This helper never looks up IDs outside those maps.
    """
    rows = _batch_rows(response)
    if (
        not all(isinstance(value, str) and value.strip()
                for value in (tenant_id, batch_id, model_name, prompt_version))
        or type(attempt_number) is not int or attempt_number < 1
        or not isinstance(objective, str)
    ):
        raise ValueError('invalid_batch_context')
    external_drafts = accepted_drafts or {}
    existing = authorized_existing or {}
    provenance = dict(batch_id=batch_id, model_name=model_name,
                      prompt_version=prompt_version, attempt_number=attempt_number)
    counts = Counter(map(_local_id, rows))
    pending = {}
    rejected = {}
    for index, record in enumerate(rows):
        local_id = _local_id(record)
        if local_id and counts[local_id] > 1:
            rejected[index] = _rejection(record, 'duplicate_local_id')
        elif not local_id or not _RECORD_VALIDATOR.is_valid(record):
            rejected[index] = _rejection(record, 'invalid_record_shape')
        else:
            pending[local_id] = (index, record)

    accepted = {}
    accepted_indices = {}
    while pending:
        progressed = False
        for local_id, (index, record) in list(pending.items()):
            try:
                targets = _link_targets(record, accepted, pending, counts, tenant_id, external_drafts, existing)
                if targets is None:
                    continue
                earlier_same = [
                    {'title': item['title'], 'content': item['fields'].get('content', '')}
                    for item in accepted.values() if item['record_type'] == record['record_type']
                ]
                _validate_quality(record, targets, earlier_same, objective, allowed_requirements)
            except ValueError as error:
                reason = str(error)
                if not re.fullmatch(r'[a-z][a-z0-9_]{1,63}', reason):
                    reason = 'record_quality_rejected'
                rejected[index] = _rejection(record, reason)
            else:
                accepted[local_id] = {
                    **deepcopy(record), 'tenant_id': tenant_id, 'provenance': dict(provenance),
                }
                accepted_indices[index] = local_id
            del pending[local_id]
            progressed = True
        if not progressed:
            for index, record in pending.values():
                rejected[index] = _rejection(record, 'unaccepted_local_target')
            break
    return {
        'accepted': [accepted[accepted_indices[index]] for index in sorted(accepted_indices)],
        'rejected': [rejected[index] for index in sorted(rejected)],
    }


def build_retry_request(response, validation):
    """Return rejected input rows and their feedback as untrusted retry data."""
    accepted_ids = {record['local_id'] for record in validation['accepted']}
    retry_rows = [row for row in _batch_rows(response) if _local_id(row) not in accepted_ids]
    rejected = validation['rejected']
    if list(map(_local_id, retry_rows)) != [item['local_id'] for item in rejected]:
        raise ValueError('retry_rejections_do_not_match_batch')
    return {'records': [
        {**item, 'record': deepcopy(record)} for record, item in zip(retry_rows, rejected)
    ]}
