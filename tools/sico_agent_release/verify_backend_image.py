import json
import os
import subprocess
from pathlib import Path

launcher = Path('/code/sico-agent-start.sh').read_text()
assert all(word not in launcher for word in ('manage.py', 'storelibraries', 'createsuperuser', 'startup.sh', ' migrate'))
subprocess.run(['/bin/bash', '-n', '/code/sico-agent-start.sh'], check=True)
from django.conf import settings
assert settings.SICO_ENGAGEMENT_COMMITS_ENABLED is False
assert settings.SICO_AI_EXECUTION_STAGE_ALLOWLIST == ()
assert settings.FORCE_CREATE_ADMIN is False
import django
django.setup()
from django.urls import resolve
from ai_onboarding.sico_ai_agent_views import SicoAiAgentView
from ai_onboarding.sico_ai_agent_tools import READ_TOOLS
assert resolve('/api/ai/workforce/assistant/execute/').func.view_class is SicoAiAgentView
assert {t.name for t in READ_TOOLS} == {'frameworks.search', 'compliance.list', 'compliance.requirements', 'assets.list'}
print(json.dumps({'startup_bypasses_management_commands': True, 'ai_commits_enabled': False,
                  'execution_stage_allowlist': [], 'force_create_admin': False,
                  'agent_route_resolved': True, 'read_tool_count': len(READ_TOOLS)}))
