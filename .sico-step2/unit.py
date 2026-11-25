exec(PAYLOAD['bootstrap'])
os.environ['DJANGO_SETTINGS_MODULE']='ciso_assistant.sico_agent_release_settings'
os.environ['DJANGO_SECRET_KEY']='offline-step-two-unit-only'
os.environ['HUEY_FILE_PATH']=':memory:'
from django.conf import settings
settings.DATABASES={'default':{'ENGINE':'django.db.backends.dummy'}}
settings.CACHES={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache'}}
settings.FORCE_CREATE_ADMIN=False
from django.db.backends.base.base import BaseDatabaseWrapper
def forbidden(*args,**kwargs):
    raise AssertionError('Database and network access forbidden in unit checks')
BaseDatabaseWrapper.connect=forbidden
BaseDatabaseWrapper.ensure_connection=forbidden
socket.socket.connect=forbidden
socket.create_connection=forbidden
import django
django.setup()
modules=['ai_onboarding.tests.'+name for name in (
    'test_sico_coordinated_generation','test_sico_case_generation_queue',
    'test_quality_evidence_requests','test_sico_case_coverage',
    'test_sico_case_record_proposals','test_sico_case_matrix_methodology','test_sico_full_case_blueprint')]
result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
from ai_onboarding.tests.test_sico_coordinated_generation import ROWS
from ai_onboarding.sico_case_coverage import plan_generation_queue
fixture={'rows':ROWS,'plan':plan_generation_queue(authorized_requirements=ROWS,objective='Assess operator access for a regional dispatch organization.')}
print(json.dumps({'compiled_modules':len(sources),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'successful':result.wasSuccessful(),'coordination_fixture':fixture}))
sys.exit(0 if result.wasSuccessful() else 1)
