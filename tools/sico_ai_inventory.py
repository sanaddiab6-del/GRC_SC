#!/usr/bin/env python3
"""Offline, read-only SICO GRC platform API and operation inventory.

Usage: python sico_ai_inventory.py /path/to/GRC_SC /path/to/inventory.json
Does not import the project, open a database, read .env, or call the network.
Every item is a SOURCE CANDIDATE, not permission approval nor an executable tool.
"""
from __future__ import annotations

import ast
import json
import sys
from collections import Counter
from pathlib import Path

ROOT_EXCLUDE = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', 'migrations', 'static', 'dist', 'build', 'tests', 'test', '.pytest_cache'}
GROUPS = (
    ('organizations_and_identity', ('folder', 'tenant', 'organization', 'organisation', 'user', 'member', 'role', 'iam')),
    ('frameworks_and_compliance', ('compliance', 'requirement', 'framework', 'standard', 'library', 'mapping', 'soa')),
    ('assets', ('asset', 'inventory', 'perimeter')),
    ('controls_and_policies', ('control', 'policy', 'safeguard', 'procedure')),
    ('risks', ('risk', 'scenario', 'threat', 'vulnerability', 'treatment')),
    ('evidence_and_findings', ('evidence', 'finding', 'observation', 'revision', 'attachment')),
    ('audits', ('audit', 'assessment', 'effectiveness', 'readiness')),
    ('remediation_and_followup', ('remediation', 'corrective', 'action', 'task', 'followup')),
    ('reporting_and_exports', ('report', 'export', 'dashboard', 'metric', 'analytics')),
    ('other_platform_functions', ()),
)


def group_name(s: str) -> str:
    normalized = s.casefold().replace('-', '_')
    for group, terms in GROUPS[:-1]:
        if any(t in normalized for t in terms):
            return group
    return 'other_platform_functions'


def lit(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f'{name(node.value)}.{node.attr}'
    if isinstance(node, ast.Call):
        return name(node.func)
    return None


def kwargs(node, key):
    for k in node.keywords:
        if k.arg == key:
            return lit(k.value)
    return None


def find_python(root):
    backend = root / 'backend'
    if not backend.is_dir():
        raise ValueError(f'Backend directory missing: {backend}')
    for file in backend.rglob('*.py'):
        if ROOT_EXCLUDE.intersection(file.relative_to(backend).parts):
            continue
        if file.stat().st_size > 2_000_000:
            continue
        yield file


def scan(root: Path):
    routes, handlers, services, errors = [], [], [], []
    files = 0
    for file in find_python(root):
        rel = file.relative_to(root).as_posix()
        try:
            tree = ast.parse(file.read_text(encoding='utf-8-sig'), filename=rel)
        except (UnicodeError, SyntaxError, OSError) as exc:
            errors.append({'source': rel, 'error': type(exc).__name__})
            continue
        files += 1
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and file.name.endswith(('urls.py', 'routing.py')):
                call_name = name(node.func) or ''
                if call_name.split('.')[-1] in {'path', 're_path'} and node.args:
                    route = lit(node.args[0])
                    if route is not None:
                        view = name(node.args[1]) if len(node.args) > 1 else None
                        declared_name = kwargs(node, 'name')
                        routes.append({
                            'source': rel, 'route_fragment': route, 'route_name': declared_name,
                            'view_reference': view, 'area': group_name(' '.join([rel, route, view or ''])),
                            'review_state': 'source_discovered_not_authorized',
                            'ai_execution_enabled': False,
                        })
                elif call_name.endswith('.register') and node.args:
                    route = lit(node.args[0]); view = name(node.args[1]) if len(node.args) > 1 else None
                    if route:
                        routes.append({
                            'source': rel, 'route_fragment': route,
                            'route_name': kwargs(node, 'basename'), 'view_reference': view,
                            'area': group_name(' '.join([rel, route, view or ''])),
                            'review_state': 'source_discovered_not_authorized',
                            'ai_execution_enabled': False,
                            'router_registration': True,
                        })
            if isinstance(node, ast.ClassDef) and ('views' in file.name or 'api' in file.name):
                methods = []
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if child.name in {'get', 'post', 'put', 'patch', 'delete', 'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'} or any('action' in (name(dec) or '') for dec in child.decorator_list):
                            methods.append(child.name)
                if methods:
                    handlers.append({
                        'source': rel, 'class_name': node.name,
                        'method_names': methods, 'area': group_name(rel + ' ' + node.name),
                        'review_state': 'source_discovered_not_authorized',
                        'ai_execution_enabled': False,
                    })
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.col_offset == 0:
                if (node.name.startswith(('execute_', 'commit_', 'suggest_', 'create_', 'prepare_', 'generate_', 'export_'))
                    and any(x in file.name for x in ('service', 'commit', 'capability'))):
                    services.append({
                        'source': rel, 'function_name': node.name,
                        'area': group_name(rel + ' ' + node.name),
                        'review_state': 'service_found_not_reviewed',
                        'ai_execution_enabled': False,
                    })
    routes.sort(key=lambda x: (x['source'], x['route_fragment']))
    handlers.sort(key=lambda x: (x['source'], x['class_name']))
    services.sort(key=lambda x: (x['source'], x['function_name']))
    return {
        'schema_version': 1,
        'scope': 'backend source code only (static AST scan)',
        'explanation': ('Routes, handlers and service functions discovered from local source. '
                        'These are NOT necessarily public routes, distinct user capabilities, '
                        'accessible to a given user, safe to call, or connected to AI execution.'),
        'source_files_parsed': files,
        'candidate_route_count': len(routes),
        'candidate_handler_count': len(handlers),
        'candidate_service_count': len(services),
        'route_count_by_area': dict(sorted(Counter(item['area'] for item in routes).items())),
        'known_reviewed_engagement_stages': [
            'case_setup', 'assets', 'applied_controls', 'evidence_findings',
            'remediation', 'framework_control_mappings', 'risk_scenarios',
            'control_effectiveness', 'audit_readiness', 'audit_report', 'final_review',
        ],
        'routes': routes, 'handlers': handlers, 'services': services,
        'parse_errors': errors[:100],
    }


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: sico_ai_inventory.py REPO_ROOT OUTPUT_JSON')
    root = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2])
    data = scan(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('SICO SOURCE INVENTORY READY')
    print('Source files:', data['source_files_parsed'])
    print('API routes/router registrations:', data['candidate_route_count'])
    print('API handler classes:', data['candidate_handler_count'])
    print('Service functions:', data['candidate_service_count'])
    print('Output:', out)
    print('No database, network or source-file changes.')


if __name__ == '__main__':
    main()
