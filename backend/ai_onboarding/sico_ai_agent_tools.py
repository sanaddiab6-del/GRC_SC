"""Reviewed GRC read adapters; extensible independently of the 11 write stages.

Tenant membership in this edition is a live user/group RoleAssignment covering
the selected Folder. The model cannot select/change that folder or grant access.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable
import time

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import connection, transaction
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from core.context import focus_folder_id_var
from core.models import Asset, ComplianceAssessment, Framework, RequirementAssessment, RequirementNode
from iam.cache_builders import get_folder_state
from iam.models import Folder, RoleAssignment

from .rbac_context import get_viewable_ids
from .engagement_service import _scoped_assessment
from .sico_ai_agent import AgentBlocked
from .workforce_discovery_rules import bounded_title, framework_terms
from .workforce_discovery_service import _scoped_category


@contextmanager
def read_only_queries(seconds=5):
    """Database-enforced read-only PostgreSQL transaction plus a SELECT-only guard.

    Missing IAM cache-version rows fail closed instead of being initialized. No
    production migrations or cache initialization are performed by this engine.
    """
    deadline = time.monotonic() + seconds

    def guard(execute, sql, params, many, context):
        if time.monotonic() >= deadline:
            raise TimeoutError()
        if not sql.lstrip().upper().startswith('SELECT '):
            raise AgentBlocked('A non-read query was refused by the agent.')
        return execute(sql, params, many, context)

    with transaction.atomic():
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute('SET TRANSACTION READ ONLY')
                cursor.execute("SELECT set_config('statement_timeout', %s, true)", [str(max(1, int(seconds * 1000)))])
                cursor.execute("SELECT set_config('lock_timeout', '1000', true)")
        with connection.execute_wrapper(guard):
            yield


def object_schema(properties=None, required=()):
    return {'type': 'object', 'properties': properties or {},
            'required': list(required), 'additionalProperties': False}


UUID_SCHEMA = {'type': 'string', 'format': 'uuid'}


@dataclass(frozen=True)
class ReadTool:
    name: str
    description: str
    model: type
    arguments: dict
    handler: Callable
    requires_folder: bool = True


class GrcReadRegistry:
    def __init__(self, user, *, folder_id=None, organization_hint=''):
        self.user_id = user.pk
        self.authenticated = bool(getattr(user, 'is_authenticated', False))
        self.folder_id = folder_id or focus_folder_id_var.get()
        self.organization_hint = organization_hint.strip()
        self.user = None
        self.folder = None

    def _authorize(self):
        if not self.authenticated:
            raise AgentBlocked('Authentication is required.')
        self.user = get_user_model().objects.filter(pk=self.user_id, is_active=True).first()
        if self.user is None or (self.user.expiry_date and self.user.expiry_date < timezone.localdate()):
            raise AgentBlocked('An active, unexpired user is required.')
        # Force fresh snapshots after every model call. This also refreshes live group
        # memberships/roles; no in-flight decision can preserve revoked privileges.
        get_folder_state(force_reload=True)
        membership = RoleAssignment.objects.filter(
            Q(user_id=self.user.pk) | Q(user_group__in=self.user.user_groups.all()),
            role__permissions__codename='view_folder',
        ).exists()
        if not membership:
            raise AgentBlocked('Active folder membership is required.')
        focus = focus_folder_id_var.get()
        if focus and self.folder_id and str(focus) != str(self.folder_id):
            raise AgentBlocked('The requested folder differs from the active focus. Select the scope explicitly.')
        if self.folder_id is None and self.organization_hint:
            candidates = Folder.objects.filter(
                name__iexact=self.organization_hint,
                id__in=get_viewable_ids(self.user, Folder),
            )
            candidates = list(candidates[:2])
            if len(candidates) != 1:
                raise AgentBlocked('Choose one exact authorized organization or use folder focus.')
            self.folder_id = candidates[0].pk
        if self.folder_id is not None:
            self.folder = Folder.objects.filter(pk=self.folder_id).first()
            if self.folder is None or not self._permission(Folder, self.folder):
                raise AgentBlocked('Folder membership is missing or no longer authorized.')
            if self.organization_hint and self.folder.name.casefold() != self.organization_hint.casefold():
                raise AgentBlocked('Organization name differs from the selected folder. Confirm the exact scope.')
            if not RoleAssignment.is_object_readable(self.user, Folder, self.folder.pk):
                raise AgentBlocked('Folder is unavailable or inaccessible.')

    def authorize(self):
        with read_only_queries():
            self._authorize()

    def _permission(self, model, folder):
        permission = Permission.objects.get(
            codename=f'view_{model.__name__.lower()}',
            content_type__app_label=model._meta.app_label,
        )
        return RoleAssignment.is_access_allowed(self.user, permission, folder)

    def _available(self, tool):
        if tool.requires_folder and self.folder is None:
            return False
        if not tool.requires_folder and self.folder is None:
            return self._frameworks().exists()
        target = self.folder or Folder.get_root_folder()
        return self._permission(tool.model, target)

    def catalog(self):
        with read_only_queries():
            self._authorize()
            return [dict(name=t.name, description=t.description, arguments=t.arguments,
                         read_only=True) for t in READ_TOOLS if self._available(t)]

    def execute(self, name, arguments, *, seconds=5):
        with read_only_queries(seconds):
            self._authorize()
            tool = next((t for t in READ_TOOLS if t.name == name), None)
            if tool is None or not self._available(tool):
                raise AgentBlocked('Tool is unavailable or unauthorized. Writes are disabled.')
            try:
                Draft202012Validator(tool.arguments, format_checker=FormatChecker()).validate(arguments)
            except ValidationError:
                raise AgentBlocked('Tool arguments failed independent validation.') from None
            return tool.handler(self, arguments)

    def reauthorize_results(self, observations):
        """Retained records can be moved/deleted or have RBAC revoked during inference.

        Do not send stale access to Qwen or disclose it in the final response. Fail
        the entire response closed; retries must fetch records under current access.
        """
        with read_only_queries():
            self._authorize()
            for observation in observations:
                if observation['status'] != 'succeeded':
                    continue
                tool = next((t for t in READ_TOOLS if t.name == observation['tool']), None)
                if tool is None or not self._available(tool):
                    raise AgentBlocked('Record access changed during execution.')
                ids = {r['id'] for r in observation['result']['records']}
                query = self._frameworks() if tool.model is Framework else self._visible(tool.model).filter(folder_id=self.folder.pk)
                args = observation['arguments']
                if tool.model is ComplianceAssessment:
                    query = query.filter(framework_id=args['framework_id'])
                if tool.model is RequirementAssessment:
                    query = query.filter(
                        compliance_assessment_id=args['assessment_id'],
                        requirement_id__in=get_viewable_ids(self.user, RequirementNode),
                    )
                if {str(pk) for pk in query.filter(pk__in=ids).values_list('pk', flat=True)} != ids:
                    raise AgentBlocked('Record access changed during execution.')
                if 'framework_id' in args and not self._frameworks().filter(pk=args['framework_id']).exists():
                    raise AgentBlocked('Framework access changed during execution.')
                if 'assessment_id' in args:
                    assessment = self._visible(ComplianceAssessment).filter(
                        pk=args['assessment_id'], folder_id=self.folder.pk,
                    ).first()
                    if assessment is None or not self._frameworks().filter(pk=assessment.framework_id).exists():
                        raise AgentBlocked('Assessment access changed during execution.')

    def _visible(self, model):
        return model.objects.filter(id__in=get_viewable_ids(self.user, model))

    def _frameworks(self):
        # Shared published library entries are allowed; unrelated tenants never are.
        shared = Q(folder__content_type=Folder.ContentType.ROOT, is_published=True)
        scope = shared | Q(folder_id=self.folder.pk) if self.folder else shared
        return self._visible(Framework).filter(scope)

    def frameworks(self, args):
        terms = framework_terms(args['query']) or [args['query']]
        match = Q()
        for term in terms:
            match |= Q(name__icontains=term) | Q(ref_id__icontains=term) | Q(urn__icontains=term)
        rows = list(self._frameworks().filter(match).order_by('name', 'id')[:9])
        return self._result('frameworks', [
            dict(id=str(o.pk), name=bounded_title(o.name), reference=bounded_title(o.ref_id, 100),
                 urn=bounded_title(o.urn, 220)) for o in rows[:8]
        ], len(rows) > 8)

    def compliance(self, args):
        framework = self._frameworks().filter(pk=args['framework_id']).first()
        if framework is None:
            raise AgentBlocked('Framework is unavailable or inaccessible in this scope.')
        rows = list(self._visible(ComplianceAssessment).filter(
            folder_id=self.folder.pk, framework_id=framework.pk,
        ).order_by('name', 'id')[:9])
        return self._result('compliance_assessments', [
            dict(id=str(o.pk), name=bounded_title(o.name), status=o.status,
                 framework_id=str(o.framework_id)) for o in rows[:8]
        ], len(rows) > 8)

    def requirements(self, args):
        # Reuse engagement's reviewed exact-folder/object authorization path.
        # Its write/receipt operations are deliberately never dispatched.
        try:
            assessment = _scoped_assessment(
                self.user, ComplianceAssessment, args['assessment_id'], self.folder.pk,
            )
        except Http404:
            raise AgentBlocked('Assessment is unavailable or inaccessible in this scope.') from None
        if not self._frameworks().filter(pk=assessment.framework_id).exists():
            raise AgentBlocked('Assessment is unavailable or inaccessible in this scope.')
        rows = list(self._visible(RequirementAssessment).filter(
            folder_id=self.folder.pk, compliance_assessment_id=assessment.pk,
            requirement__framework_id=assessment.framework_id,
            requirement_id__in=get_viewable_ids(self.user, RequirementNode),
        ).order_by('id')[:9])
        return self._result('requirement_assessments', [
            dict(id=str(o.pk), assessment_id=str(o.compliance_assessment_id),
                 requirement_id=str(o.requirement_id), status=o.status, stored_result=o.result)
            for o in rows[:8]
        ], len(rows) > 8)

    def assets(self, args):
        # Reuse the reviewed discovery service's exact-folder, per-object RBAC adapter.
        rows, limited = _scoped_category(self.user, Asset, self.folder.pk)
        return self._result('assets', rows[:8], limited or len(rows) > 8)

    def _result(self, category, records, limited):
        return {'category': category, 'records': records, 'returned_count': len(records),
                'limited': limited, 'folder_id': str(self.folder.pk) if self.folder else None,
                'caveat': 'Authorized stored records only; bounded exact-folder search. No evidence content reviewed or compliance verdict established.'}


# Fixed source-reviewed handlers. New modules plug in here, independent of stages.
READ_TOOLS = (
    ReadTool('frameworks.search', 'Find authorized loaded frameworks by name/reference/URN. Start here to resolve a framework ID.',
             Framework, object_schema({'query': {'type': 'string', 'minLength': 1, 'maxLength': 150}}, ['query']),
             GrcReadRegistry.frameworks, False),
    ReadTool('compliance.list', 'List authorized compliance assessments for a returned framework ID in the selected organization.',
             ComplianceAssessment, object_schema({'framework_id': UUID_SCHEMA}, ['framework_id']), GrcReadRegistry.compliance),
    ReadTool('compliance.requirements', 'Inspect bounded authorized stored requirement assessment statuses/results for a returned assessment ID. Does not inspect evidence content.',
             RequirementAssessment, object_schema({'assessment_id': UUID_SCHEMA}, ['assessment_id']), GrcReadRegistry.requirements),
    ReadTool('assets.list', 'List authorized asset inventory in the selected organization; asset names alone do not establish security effectiveness.',
             Asset, object_schema(), GrcReadRegistry.assets),
)
