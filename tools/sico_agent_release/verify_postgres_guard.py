import json
import django
django.setup()
from django.db import connection
from ai_onboarding.sico_ai_agent_tools import read_only_queries

assert connection.vendor == 'postgresql'
with read_only_queries():
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('transaction_read_only')")
        assert cursor.fetchone()[0] == 'on'
refused = False
try:
    with read_only_queries():
        # Bypass the SELECT-only Python wrapper to test PostgreSQL's own defense.
        with connection.connection.cursor() as cursor:
            cursor.execute('UPDATE release_read_only_fixture SET value = value WHERE FALSE')
except Exception as exc:
    assert getattr(exc, 'pgcode', None) == '25006', type(exc).__name__
    refused = True
assert refused
with read_only_queries():
    with connection.cursor() as cursor:
        cursor.execute('SELECT value FROM release_read_only_fixture')
        assert cursor.fetchall() == [(1,)]
print(json.dumps({'postgresql_transaction_read_only': True,
                  'write_rejected_by_postgresql': True, 'fixture_unchanged': True}))
