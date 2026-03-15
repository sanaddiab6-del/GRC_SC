#!/bin/sh
# Install djangorestframework-simplejwt and run migrations

set -e

cd /code

echo "=== Installing djangorestframework-simplejwt ==="
pip install "djangorestframework-simplejwt>=5.3.1" --quiet

echo "=== Verifying install ==="
python -c "import rest_framework_simplejwt; print('simplejwt version:', rest_framework_simplejwt.__version__)"

echo "=== Running migrations ==="
poetry run python manage.py migrate rest_framework_simplejwt.token_blacklist --no-input 2>&1 || true
poetry run python manage.py migrate iam --no-input 2>&1

echo "=== Migration status ==="
poetry run python manage.py showmigrations iam | tail -10

echo "=== Checking JWT module loads ==="
poetry run python manage.py shell -c "from iam.jwt_auth import GRCTokenObtainPairView, ROLE_HIERARCHY; print('JWT module OK, hierarchy tiers:', [r['tier'] for r in ROLE_HIERARCHY])"

echo "=== Done ==="
