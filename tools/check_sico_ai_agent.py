"""Disposable, real-ORM agent checks. NEVER connects to a configured application DB.

Run in a disposable backend image (source read-only, no data volumes). --real-model
also calls local Ollama using the production provider implementation. All records
below are explicitly test fixtures in an in-memory SQLite DB, not historical GRC
data and not an assertion about any actual organization's compliance.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import sys
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--real-model', action='store_true')
    parser.add_argument('--report', help='Optional JSON report in disposable container storage')
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
    os.environ.setdefault('HUEY_FILE_PATH', '/tmp/sico-agent-check/huey.db')

    from django.conf import settings
    # Override BEFORE django.setup()/opening any connection. No migrations and no
    # application DB credentials are used. Database contents vanish on process exit.
    settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
    settings.MEDIA_ROOT = '/tmp/sico-agent-check/media'
    import django
    django.setup()

    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    from django.db import connection, models
    from rest_framework.test import APIRequestFactory, force_authenticate
    from core.context import focus_folder_id_var
    from core.models import Asset, ComplianceAssessment, Framework, Perimeter, RequirementAssessment, RequirementNode
    from iam.models import Folder, Role, RoleAssignment, User, UserGroup
    from iam.snapshot_cache import CacheVersion
    from ai_onboarding.sico_ai_agent import AgentBlocked
    from ai_onboarding.sico_ai_agent_tools import GrcReadRegistry, read_only_queries
    from ai_onboarding.sico_ai_agent_views import SicoAiAgentView

    assert connection.vendor == 'sqlite' and connection.settings_dict['NAME'] == ':memory:'
    connection.disable_constraint_checking()
    fixture_models = (ContentType, Permission, Folder, UserGroup, User, Role, RoleAssignment,
                      CacheVersion, Framework, Perimeter, Asset, ComplianceAssessment,
                      RequirementNode, RequirementAssessment)
    with connection.schema_editor() as editor:
        for model in fixture_models:
            editor.create_model(model)
    # This minimal fixture schema omits unrelated nullable FK target tables.
    # schema_editor re-enables SQLite constraints when it exits.
    connection.disable_constraint_checking()

    def insert(model_type, **values):
        obj = model_type(**values)
        # Base QuerySet bypasses ActorSyncManager as well as save/audit signals.
        models.QuerySet(model=model_type, using='default').bulk_create([obj])
        return obj

    root = insert(Folder, name='Isolated global test library', content_type=Folder.ContentType.ROOT,
                  parent_folder=None, is_published=True)
    folder = insert(Folder, name='Isolated authorized organization', parent_folder=root)
    other = insert(Folder, name='Isolated other tenant', parent_folder=root)
    user = insert(User, email='isolated-agent@tests.invalid', folder=folder, is_active=True)
    outsider = insert(User, email='isolated-outsider@tests.invalid', folder=other, is_active=True)
    inactive = insert(User, email='isolated-inactive@tests.invalid', folder=folder, is_active=False)
    no_membership = insert(User, email='isolated-no-membership@tests.invalid', folder=folder, is_active=True)
    grouped_user = insert(User, email='isolated-group-member@tests.invalid', folder=folder, is_active=True)
    group = insert(UserGroup, name='Isolated reader group', folder=folder)
    insert(User.user_groups.through, user_id=grouped_user.pk, usergroup_id=group.pk)
    role = insert(Role, name='Isolated reader', folder=folder)
    for model in (Folder, Framework, ComplianceAssessment, RequirementAssessment, RequirementNode, Asset):
        content_type = insert(ContentType, app_label=model._meta.app_label, model=model.__name__.lower())
        for verb in ('view', 'change', 'delete'):
            perm = insert(Permission, name=f'{verb} {model.__name__}', content_type=content_type,
                          codename=f'{verb}_{model.__name__.lower()}')
            if verb == 'view':
                insert(Role.permissions.through, role_id=role.pk, permission_id=perm.pk)
    for principal, domain in ((user, folder), (outsider, other), (inactive, folder)):
        assignment = insert(RoleAssignment, user=principal, role=role, folder=domain, is_recursive=False)
        insert(RoleAssignment.perimeter_folders.through, roleassignment_id=assignment.pk, folder_id=domain.pk)
    group_assignment = insert(RoleAssignment, user_group=group, role=role, folder=folder, is_recursive=False)
    insert(RoleAssignment.perimeter_folders.through, roleassignment_id=group_assignment.pk, folder_id=folder.pk)
    for key in ('folders', 'iam.roles', 'iam.groups', 'iam.assignments'):
        insert(CacheVersion, key=key, version=1)
    framework = insert(Framework, name='NCA ECC (isolated test fixture)', ref_id='NCA-ECC-TEST',
                       urn='urn:test:nca-ecc', folder=root, is_published=True)
    hidden_framework = insert(Framework, name='NCA ECC other tenant private fixture',
                              urn='urn:test:hidden-nca-ecc', folder=other)
    perimeter = insert(Perimeter, name='Isolated scope', folder=folder)
    other_perimeter = insert(Perimeter, name='Other tenant scope', folder=other)
    assessment = insert(ComplianceAssessment, name='NCA ECC isolated assessment', folder=folder,
                        framework=framework, perimeter=perimeter, status='in_progress')
    hidden_assessment = insert(ComplianceAssessment, name='Private other tenant assessment', folder=other,
                               framework=framework, perimeter=other_perimeter, status='planned')
    requirement = insert(RequirementNode, name='Isolated example requirement; no regulatory authority',
                         folder=root, framework=framework, urn='urn:test:requirement', assessable=True,
                         is_published=True)
    requirement_assessment = insert(RequirementAssessment, folder=folder, compliance_assessment=assessment,
                                    requirement=requirement, status='to_do', result='not_assessed')
    asset = insert(Asset, name='Isolated authorized test asset', folder=folder)
    insert(Asset, name='Private other tenant asset', folder=other)

    report = {'data_source': 'disposable_in_memory_test_fixtures', 'existing_databases_used': False}

    class RecordChecks(unittest.TestCase):
        def registry(self, principal=user, selected=folder):
            return GrcReadRegistry(principal, folder_id=selected.pk)

        def test_real_authorized_modules(self):
            registry = self.registry()
            found = registry.execute('frameworks.search', {'query': 'NCA ECC'})
            self.assertEqual([r['id'] for r in found['records']], [str(framework.pk)])
            compliance = registry.execute('compliance.list', {'framework_id': str(framework.pk)})
            self.assertEqual([r['id'] for r in compliance['records']], [str(assessment.pk)])
            assets = registry.execute('assets.list', {})
            self.assertEqual([r['id'] for r in assets['records']], [str(asset.pk)])
            requirements = registry.execute('compliance.requirements', {'assessment_id': str(assessment.pk)})
            self.assertEqual(requirements['records'][0]['stored_result'], 'not_assessed')

        def test_cross_tenant_folder_denied(self):
            with self.assertRaises(AgentBlocked):
                self.registry(selected=other).execute('assets.list', {})

        def test_cross_tenant_object_denied(self):
            registry = self.registry()
            with self.assertRaises(AgentBlocked):
                registry.execute('compliance.requirements', {'assessment_id': str(hidden_assessment.pk)})
            with self.assertRaises(AgentBlocked):
                registry.execute('compliance.list', {'framework_id': str(hidden_framework.pk)})

        def test_invalid_uuid_and_extra_arguments_denied(self):
            for arguments in ({'framework_id': 'not-a-uuid'}, {'framework_id': str(framework.pk), 'folder_id': str(other.pk)}):
                with self.assertRaises(AgentBlocked):
                    self.registry().execute('compliance.list', arguments)

        def test_inactive_or_unassigned_user_denied(self):
            for principal in (inactive, no_membership):
                with self.assertRaises(AgentBlocked):
                    self.registry(principal=principal).authorize()

        def test_live_group_membership_revocation(self):
            registry = self.registry(principal=grouped_user)
            self.assertEqual(registry.execute('assets.list', {})['records'][0]['id'], str(asset.pk))
            User.user_groups.through.objects.filter(user_id=grouped_user.pk, usergroup_id=group.pk).delete()
            try:
                with self.assertRaises(AgentBlocked):
                    registry.execute('assets.list', {})
            finally:
                insert(User.user_groups.through, user_id=grouped_user.pk, usergroup_id=group.pk)

        def test_module_permission_revocation(self):
            permission = Permission.objects.get(codename='view_asset')
            Role.permissions.through.objects.filter(role_id=role.pk, permission_id=permission.pk).delete()
            try:
                self.assertNotIn('assets.list', [t['name'] for t in self.registry().catalog()])
                with self.assertRaises(AgentBlocked):
                    self.registry().execute('assets.list', {})
            finally:
                insert(Role.permissions.through, role_id=role.pk, permission_id=permission.pk)

        def test_write_and_arbitrary_dispatch_denied(self):
            for name in ('assets.create', '__import__', 'https://localhost/api/assets/', 'tools.commit'):
                with self.assertRaises(AgentBlocked):
                    self.registry().execute(name, {})
            with self.assertRaises(AgentBlocked):
                with read_only_queries():
                    Asset.objects.filter(pk=asset.pk).update(name='Forbidden')
            self.assertEqual(Asset.objects.get(pk=asset.pk).name, 'Isolated authorized test asset')

        def test_focus_cannot_be_overridden(self):
            token = focus_folder_id_var.set(other.pk)
            try:
                with self.assertRaises(AgentBlocked):
                    self.registry().authorize()
            finally:
                focus_folder_id_var.reset(token)

        def test_no_folder_only_shared_frameworks(self):
            registry = GrcReadRegistry(user)
            self.assertEqual([t['name'] for t in registry.catalog()], ['frameworks.search'])
            with self.assertRaises(AgentBlocked):
                registry.execute('assets.list', {})

        def test_exact_organization_resolves_server_side(self):
            registry = GrcReadRegistry(user, organization_hint=folder.name)
            self.assertEqual(registry.execute('assets.list', {})['records'][0]['id'], str(asset.pk))
            with self.assertRaises(AgentBlocked):
                GrcReadRegistry(user, organization_hint=other.name).authorize()

        def test_moved_record_not_redisclosed(self):
            registry = self.registry()
            result = registry.execute('assets.list', {})
            Asset.objects.filter(pk=asset.pk).update(folder=other)
            try:
                with self.assertRaises(AgentBlocked):
                    registry.reauthorize_results([{'status': 'succeeded', 'tool': 'assets.list',
                                                  'arguments': {}, 'result': result}])
            finally:
                Asset.objects.filter(pk=asset.pk).update(folder=folder)

        def test_real_api_membership_denial(self):
            request = APIRequestFactory().post('/execute/', {
                'instruction': 'Find NCA ECC in the other tenant', 'folder_id': str(other.pk),
            }, format='json')
            force_authenticate(request, user=user)
            self.assertEqual(SicoAiAgentView.as_view()(request).status_code, 403)

    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RecordChecks))
    report['record_checks'] = {'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors)}
    if not result.wasSuccessful():
        sys.exit(1)
    if args.real_model:
        os.environ['AI_PROVIDER'] = 'local'
        os.environ['LOCAL_AI_MODEL_GRC_CAPABILITY_SELECTION'] = 'qwen2.5:3b'
        os.environ.setdefault('LOCAL_AI_BASE_URL', f'http://{socket.gethostbyname("host.docker.internal")}:11434')
        os.environ['LOCAL_AI_TIMEOUT_SECONDS'] = '90'
        os.environ['LOCAL_AI_MAX_OUTPUT_TOKENS'] = '1100'
        before = {m._meta.label: m.objects.count() for m in fixture_models}
        request = APIRequestFactory().post('/api/ai/workforce/assistant/execute/', {
            'instruction': 'Find the NCA ECC framework, inspect the available authorized compliance information, and explain what further assessment is needed.',
            'folder_id': str(folder.pk),
        }, format='json')
        force_authenticate(request, user=user)
        reply = SicoAiAgentView.as_view()(request)
        outcome = reply.data
        after = {m._meta.label: m.objects.count() for m in fixture_models}
        observed_tools = [o['tool'] for o in outcome.get('verified_results', [])]
        verified = (reply.status_code == 200 and outcome['status'] == 'completed' and outcome['model_calls'] >= 3
                    and 'frameworks.search' in observed_tools and 'compliance.list' in observed_tools
                    and bool(outcome['final_answer']) and before == after)
        report.update(real_qwen_verified=verified, real_qwen_execution=outcome, fixture_record_counts_unchanged=before == after)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        if not verified:
            sys.exit(2)
    else:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
