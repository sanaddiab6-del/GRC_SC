"""Authenticated, READ-ONLY, permission-scoped preflight for NEW GRC case setup.

This does not create any GRC records. A later approved write must go through the
existing AiCaseSetupService and repeat every check in a transaction; these checks
are a human-readable proposal, not an authorization token or proof of absence.
"""
from __future__ import annotations

from django.contrib.auth.models import Permission
from django.http import Http404

from core.models import ComplianceAssessment, Framework, Perimeter
from iam.models import Folder, RoleAssignment

from .workforce_case_plan_rules import (
    exact_organization_match, proposed_case_names, readiness_label,
)


def _readable(user, model, key):
    return bool(RoleAssignment.is_object_readable(user, model, key))


def _can_add(user, codename, folder):
    permission = Permission.objects.filter(codename=codename).first()
    return bool(permission and RoleAssignment.is_access_allowed(user, permission, folder))


def readable_domain_parents(user):
    """Conservative parent choices: top-level permitted folders only, no global tree dump."""
    results = []
    for folder in Folder.objects.filter(parent_folder__isnull=True).order_by('id')[:12]:
        if _readable(user, Folder, folder.pk) and _can_add(user, 'add_folder', folder):
            results.append({'id': str(folder.pk), 'name': str(folder.name)[:160]})
    return results


def prepare_new_case_plan(user, *, organization, scope, framework_id,
                          domain_strategy, selected_folder_id=None, parent_folder_id=None,
                          framework_review_confirmed=False):
    """Do not trust submitted IDs or client discovery caches: re-query every selection."""
    blockers, cautions, actions = [], [], []
    framework = Framework.objects.filter(pk=framework_id).first()
    if framework is None or not _readable(user, Framework, framework.pk):
        raise Http404('Selected framework unavailable or not accessible.')
    labels = proposed_case_names(organization, scope, framework.name)
    requirements = framework.requirement_nodes.filter(assessable=True).count()
    if not requirements:
        blockers.append({'code':'empty_framework', 'message':'Selected framework has no assessable requirements.'})
    if not framework_review_confirmed:
        blockers.append({'code':'framework_review_required','message':'Review the exact edition, applicability, licensing and legal obligations before this case can be approved.'})
    cautions.append('The framework name/URN and requirement count do not establish that this is the legally applicable edition.')
    actions.append({'entity':'Framework', 'operation':'reuse', 'name':str(framework.name), 'id':str(framework.pk), 'status':'selected_by_user'})

    folder = None
    parent = None
    if domain_strategy == 'reuse':
        folder = Folder.objects.filter(pk=selected_folder_id).first() if selected_folder_id else None
        if folder is None or not _readable(user, Folder, folder.pk):
            raise Http404('Selected domain unavailable or not accessible.')
        if folder.content_type != Folder.ContentType.DOMAIN:
            blockers.append({'code':'not_domain','message':'The selected organizational folder is not a domain.'})
        if not exact_organization_match(folder.name, organization):
            blockers.append({'code':'organization_mismatch','message':'The domain name differs from the requested organization; confirm the correct company.'})
        actions.append({'entity':'Folder', 'operation':'reuse', 'name':str(folder.name), 'id':str(folder.pk), 'status':'review_required'})
        if not _can_add(user, 'add_perimeter', folder):
            blockers.append({'code':'perimeter_permission','message':'Your account is not authorized to create perimeters in this domain.'})
        if not _can_add(user, 'add_complianceassessment', folder):
            blockers.append({'code':'assessment_permission','message':'Your account is not authorized to create assessments in this domain.'})
    else:
        permitted_parents = {entry['id'] for entry in readable_domain_parents(user)}
        if not parent_folder_id or str(parent_folder_id) not in permitted_parents:
            raise Http404('Parent organizational scope unavailable or not accessible for domain creation.')
        parent = Folder.objects.filter(pk=parent_folder_id).first()
        if parent is None or not _readable(user, Folder, parent.pk) or not _can_add(user, 'add_folder', parent):
            raise Http404('Parent organizational scope unavailable or not accessible for domain creation.')
        # This is a scoped uniqueness check, never a global claim of nonexistence.
        duplicate = Folder.objects.filter(parent_folder=parent, content_type=Folder.ContentType.DOMAIN, name__iexact=labels['domain']).exists()
        if duplicate:
            blockers.append({'code':'possible_duplicate_domain','message':'A domain with this name may already exist under the selected parent. Reuse or request administrator review.'})
        cautions.append('Only the selected parent scope was checked for duplicates. Another domain may exist elsewhere or be hidden by permissions.')
        cautions.append('Permissions for records inside the future domain cannot be verified until it exists; the approved case-setup operation must re-check them.')
        actions.append({'entity':'Folder', 'operation':'create', 'name':labels['domain'], 'parent_id':str(parent.pk), 'status':'proposed_only'})

    proposed_perimeter = labels['perimeter']
    if folder:
        # Prevent duplicates without exposing inaccessible records.
        if Perimeter.objects.filter(folder=folder, name__iexact=proposed_perimeter).exists():
            blockers.append({'code':'possible_duplicate_perimeter','message':'An assessment perimeter with this name may exist here. Review it before creating a new one.'})
        # A perimeter may already contain an assessment matching this assignment;
        # never treat a restricted row as absent.
        if ComplianceAssessment.objects.filter(folder=folder, name__iexact=labels['assessment'], version__iexact='1.0').exists():
            blockers.append({'code':'possible_duplicate_assessment','message':'A compliance assessment with the proposed name/version may already exist here.'})
    actions.append({'entity':'Perimeter', 'operation':'create', 'name':proposed_perimeter, 'status':'proposed_only', 'scope_text':scope})
    actions.append({'entity':'ComplianceAssessment', 'operation':'create', 'name':labels['assessment'], 'version':'1.0', 'status':'proposed_only', 'framework_id':str(framework.pk)})
    cautions.append('The scope entered is descriptive text, not an actual link to in-scope Asset records yet.')

    return {
        'kind':'sico_new_case_preflight_v1',
        'operation':'new_case',
        'status':readiness_label(blockers),
        'writes_performed':False,
        'model_inference_used':False,
        'framework':{'id':str(framework.pk),'name':str(framework.name),'ref_id':str(framework.ref_id or ''),'urn':str(framework.urn or ''),'assessable_requirements':requirements,'human_applicability_acknowledged':framework_review_confirmed},
        'organization_requested': organization,
        'scope_requested':scope,
        'planned_actions':actions,
        'blocking_checks':blockers,
        'limitations':cautions,
        'next_action':'Review blockers and prepare a dry-run through the existing protected Case Setup workflow. This endpoint cannot create records.',
        'approval_required':True,
    }
