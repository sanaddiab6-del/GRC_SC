"""Static import closure for the release, compared with the deployed image.

Only the existing ai_onboarding package is overlaid; no imports or DB calls run.
"""
import ast
import hashlib
import json
from pathlib import Path

source = Path('/source-backend')
base = Path('/code')
roots = ['ai_onboarding.urls', 'ai_onboarding.sico_ai_agent_views']
pending = [(name, 'release entry point') for name in roots]
visited = {}
while pending:
    module, parent = pending.pop()
    if module in visited or not module.startswith('ai_onboarding'):
        continue
    relative = module.replace('.', '/') + '.py'
    path = source / relative
    if not path.is_file():
        relative = module.replace('.', '/') + '/__init__.py'
        path = source / relative
    if not path.is_file():
        continue
    data = path.read_bytes()
    text = data.decode('utf-8-sig').replace('\r\n', '\n')
    prior = base / relative
    old_hash = hashlib.sha256(prior.read_text(encoding='utf-8-sig').replace('\r\n', '\n').encode()).hexdigest() if prior.is_file() else None
    current_hash = hashlib.sha256(text.encode()).hexdigest()
    visited[module] = dict(source='backend/' + relative, relative=relative,
                           sha256=hashlib.sha256(data).hexdigest(), normalizedSha256=current_hash,
                           baseSha256=old_hash, overlaid=current_hash != old_hash, requiredBy=parent)
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                package = module.split('.')[:-node.level]
                target = '.'.join(package + ([node.module] if node.module else []))
            else:
                target = node.module or ''
            pending.append((target, module))
            for alias in node.names:
                pending.append((target + '.' + alias.name, module))
        elif isinstance(node, ast.Import):
            pending.extend((alias.name, module) for alias in node.names)
print(json.dumps(sorted(visited.values(), key=lambda item: item['source'])))
