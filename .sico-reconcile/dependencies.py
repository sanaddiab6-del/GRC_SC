"""Read only direct local dependencies of SICO generation entry points."""
import ast
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path('/code')
ENTRY_NAMES = (
    'urls', 'sico_ai_case_quality_views', 'quality_sico_drafts_v5',
    'sico_ai_case_draft_views', 'sico_ai_sixteen_generate_views',
    'sico_ai_generated_assessment_views', 'sico_ai_framework_batch_v3',
    'authorized_framework_source', 'sico_case_coverage_views', 'sico_case_coverage',
    'sico_case_record_proposals', 'sico_full_case_blueprint', 'sico_case_matrix_methodology',
    'llm_config', 'llm_provider', 'llm_errors',
)
sources = PAYLOAD['repository']
deps = set()
for name in ENTRY_NAMES:
    rel = 'backend/ai_onboarding/' + name + '.py'
    variants = [base64.b64decode(sources[rel])]
    live = ROOT/'ai_onboarding'/(name+'.py')
    if live.exists():
        variants.append(live.read_bytes())
    for raw in variants:
        tree = ast.parse(raw)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                candidates = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                candidates = [node.module]
            else:
                continue
            for module in candidates:
                if module.startswith('ai_onboarding'):
                    continue
                p = ROOT.joinpath(*module.split('.')).with_suffix('.py')
                if p.is_file():
                    deps.add(p)
deps.update(p for p in (ROOT/'sico-agent-start.sh', ROOT/'ciso_assistant/sico_agent_release_settings.py') if p.is_file())
result = {}
for p in sorted(deps):
    raw = p.read_bytes()
    result[p.relative_to(ROOT).as_posix()] = {'sha256':hashlib.sha256(raw).hexdigest(), 'content':base64.b64encode(raw).decode()}
print(json.dumps(result))
