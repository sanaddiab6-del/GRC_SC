"""Validate the repository overlay in memory; never open a database/network."""
import ast
import base64
import importlib.abc
import importlib.util
import io
import json
import os
import socket
import sys
import unittest

sources = {p:base64.b64decode(v) for p,v in PAYLOAD['sources'].items()}
for p, source in sources.items():
    compile(source, 'repository/'+p, 'exec')

class MemorySource(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self):
        self.mapping = {}
        self.packages = set()
        for p in sources:
            if not p.startswith('backend/') or not p.endswith('.py'):
                continue
            parts = p[len('backend/'):-3].split('/')
            package = parts[-1] == '__init__'
            if package:
                parts.pop()
            name = '.'.join(parts)
            self.mapping[name] = p
            if package:
                self.packages.add(name)
            for i in range(1,len(parts)):
                self.packages.add('.'.join(parts[:i]))
    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.mapping or fullname in self.packages:
            return importlib.util.spec_from_loader(fullname, self, is_package=fullname in self.packages)
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        name = module.__name__
        if name in self.packages:
            module.__path__ = ['/code/'+name.replace('.','/')]
        if name in self.mapping:
            p = self.mapping[name]
            module.__file__ = '/in-memory-repository/'+p
            exec(compile(sources[p],module.__file__,'exec'),module.__dict__)

finder = MemorySource()
sys.meta_path.insert(0,finder)
sys.dont_write_bytecode = True
attempts = {'database':0,'network':0}
def deny_network(*args,**kwargs):
    attempts['network'] += 1
    raise AssertionError('Network disabled during reconciliation checks')
socket.socket.connect = deny_network
socket.socket.connect_ex = deny_network
socket.create_connection = deny_network
os.environ['DJANGO_SETTINGS_MODULE'] = 'ciso_assistant.sico_agent_release_settings'
os.environ['HUEY_FILE_PATH'] = ':memory:'
os.environ['DJANGO_SECRET_KEY'] = 'offline-reconciliation-check-only'
from django.conf import settings
settings.DATABASES = {'default':{'ENGINE':'django.db.backends.dummy'}}
settings.CACHES = {'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache'}}
settings.FORCE_CREATE_ADMIN = False
from django.db.backends.base.base import BaseDatabaseWrapper
def deny_database(*args,**kwargs):
    attempts['database'] += 1
    raise AssertionError('Database disabled during reconciliation checks')
BaseDatabaseWrapper.ensure_connection = deny_database
BaseDatabaseWrapper.connect = deny_database
import django
django.setup()

def routes(raw):
    result = []
    for n in ast.walk(ast.parse(raw)):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id == 'path':
            route = ast.literal_eval(n.args[0])
            view = ast.dump(n.args[1],include_attributes=False)
            name = next((ast.literal_eval(k.value) for k in n.keywords if k.arg == 'name'),None)
            result.append((route,view,name))
    return result
old_routes = routes(base64.b64decode(PAYLOAD['live_urls']))
new_routes = routes(sources['backend/ai_onboarding/urls.py'])
assert all(r in new_routes for r in old_routes),'Existing route changed'
assert len({r[0] for r in new_routes}) == len(new_routes),'Duplicate URL path'
assert len({r[2] for r in new_routes}) == len(new_routes),'Duplicate URL name'

from ai_onboarding import sico_ai_case_quality_views as views
old_namespace = {'__name__':'ai_onboarding._live_quality_contract','__package__':'ai_onboarding'}
exec(compile(base64.b64decode(PAYLOAD['live_quality']),'live-quality-contract','exec'),old_namespace)
old_fields = old_namespace['QualityDraftInput']().fields
new_fields = views.QualityDraftInput().fields
attrs = ('required','allow_null','allow_blank','min_length','max_length','min_value','max_value','default')
for key, old in old_fields.items():
    new = new_fields[key]
    assert type(new) is type(old),(key,'field type changed')
    for attr in attrs:
        assert getattr(old,attr,None) == getattr(new,attr,None),(key,attr,'contract changed')
added_fields = sorted(set(new_fields)-set(old_fields))
assert all(not new_fields[k].required for k in added_fields),'Required request field added'
from django.urls import resolve
from ai_onboarding.urls import urlpatterns
for path,_,name in old_routes:
    # Routes with UUID converters are covered by structural equality above.
    if '<' not in path:
        assert resolve('/'+path,urlconf=tuple(urlpatterns)).url_name == name

modules = [
    'ai_onboarding.test_sico_ai_asset_recovery',
    'ai_onboarding.test_sico_ai_connected_case',
    'ai_onboarding.test_sico_ai_framework_library',
    'ai_onboarding.test_sico_ai_incremental_generate',
    'ai_onboarding.test_sico_ai_framework_batch_v3',
    'ai_onboarding.tests.test_quality_evidence_requests',
    'ai_onboarding.tests.test_sico_case_coverage',
    'ai_onboarding.tests.test_sico_case_generation_queue',
    'ai_onboarding.tests.test_sico_case_record_proposals',
    'ai_onboarding.tests.test_sico_case_matrix_methodology',
    'ai_onboarding.tests.test_sico_full_case_blueprint',
]
suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
report = {
    'python_version':sys.version.split()[0], 'compiled_modules':len(sources),
    'all_repository_ai_modules_loaded_from_memory':True,
    'existing_routes_preserved':len(old_routes), 'repository_routes':len(new_routes),
    'additional_routes':[r[0] for r in new_routes if r not in old_routes],
    'quality_existing_request_fields_preserved':len(old_fields), 'optional_fields_added':added_fields,
    'test_modules':modules, 'tests_run':result.testsRun,
    'failures':[(str(t),s) for t,s in result.failures], 'errors':[(str(t),s) for t,s in result.errors],
    'skipped':[(str(t),s) for t,s in result.skipped], 'connection_attempts':attempts,
    'test_output':stream.getvalue(), 'successful':result.wasSuccessful() and not any(attempts.values()),
}
print(json.dumps(report))
if not report['successful']:
    sys.exit(1)
