#!/usr/bin/env bash
set -euo pipefail
cd /code
# Fixed release settings inherit the existing settings and disable AI commits.
export DJANGO_SETTINGS_MODULE=ciso_assistant.sico_agent_release_settings
if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  test -s /code/db/django_secret_key || {
    echo 'Existing Django secret key missing; refusing startup.' >&2
    exit 1
  }
  export DJANGO_SECRET_KEY="$(cat /code/db/django_secret_key)"
fi
# No management commands, DB initialization, library import or account provisioning.
exec /code/.venv/bin/gunicorn --chdir /code/ciso_assistant --pythonpath /code \
  --bind ":${PORT:-8000}" --timeout "${GUNICORN_TIMEOUT:-420}" \
  --keep-alive "${GUNICORN_KEEPALIVE:-30}" --workers "${GUNICORN_WORKERS:-3}" \
  --limit-request-line "${GUNICORN_LIMIT_REQUEST_LINE:-5120}" \
  --env RUN_MAIN=true ciso_assistant.wsgi:application
