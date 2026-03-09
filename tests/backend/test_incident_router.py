"""
Tests for incident/router.py — requires `incident:*` permissions.

Strategy: override get_current_user + get_db; also override the specific
require_permission dependency objects that are captured at import time.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from datetime import datetime

from httpx import AsyncClient, ASGITransport


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_user(user_id=None, role="Analyst"):
    from auth.models import User

    user = MagicMock(spec=User)
    user.user_id = str(user_id or uuid4())
    user.username = "tester"
    user.email = "tester@example.com"
    user.is_active = True

    # Build a role with full incident permissions so permission_checker passes
    role_mock = MagicMock()
    role_mock.role_name = role
    perms = []
    for action in ["read", "create", "update", "delete", "manage", "report"]:
        perm = MagicMock()
        perm.resource = "incident"
        perm.action = action
        perms.append(perm)
    role_mock.permissions = perms
    user.roles = [role_mock]
    return user


def _make_incident(user_id=None, override: dict | None = None):
    from incident.models import SecurityIncident, IncidentStatus, IncidentSeverity, IncidentCategory

    uid = uuid4()
    m = MagicMock(spec=SecurityIncident)
    m.incident_id = uid
    m.id = str(uid)
    m.incident_number = "INC-2024-001"
    m.title_en = "Test Incident"
    m.title_ar = "حادث تجريبي"
    m.description_en = "Desc"
    m.description_ar = "وصف"
    m.status = IncidentStatus.NEW
    m.severity = IncidentSeverity.HIGH
    m.category = IncidentCategory.DATA_BREACH
    m.reported_by = user_id or uid
    m.reported_by_id = str(user_id or uid)
    m.assigned_to = None
    m.incident_commander = None
    m.control_id = None
    m.affected_systems = []
    m.affected_users_count = 0
    m.nca_reported = False
    m.nca_reported_at = None
    m.detected_at = datetime(2024, 1, 1)
    m.reported_at = datetime(2024, 1, 1)
    m.contained_at = None
    m.resolved_at = None
    m.closed_at = None
    m.created_at = datetime(2024, 1, 1)
    m.updated_at = datetime(2024, 1, 1)

    if override:
        for k, v in override.items():
            setattr(m, k, v)

    return m


def _scalar_result(value):
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    r.scalars.return_value.all.return_value = [value] if value is not None else []
    r.scalar.return_value = 1
    return r


# ── fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def app_with_overrides():
    """App with auth + DB dependencies overridden."""
    from main import app
    from core.database import get_db
    from auth.security import get_current_user, get_current_active_user

    fake_user = _make_user()
    fake_db = AsyncMock()

    async def _get_user():
        return fake_user

    async def _get_db():
        yield fake_db

    orig = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = _get_user
    app.dependency_overrides[get_current_active_user] = _get_user
    app.dependency_overrides[get_db] = _get_db

    # Override all incident permission dependencies by patching require_permission
    # to return a no-op dependency.
    with patch("incident.router.require_permission", return_value=lambda: fake_user):
        yield app, fake_db, fake_user

    app.dependency_overrides = orig


# ── tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_incidents(app_with_overrides):
    app, fake_db, fake_user = app_with_overrides
    incident = _make_incident(fake_user.user_id)

    result = MagicMock()
    result.scalars.return_value.all.return_value = [incident]
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/incidents")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_incident_found(app_with_overrides):
    app, fake_db, fake_user = app_with_overrides
    incident_id = str(uuid4())
    incident = _make_incident(fake_user.user_id)
    incident.id = incident_id

    result = MagicMock()
    result.scalar_one_or_none.return_value = incident
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/api/v1/incidents/{incident_id}")

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_incident_not_found(app_with_overrides):
    app, fake_db, fake_user = app_with_overrides

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/api/v1/incidents/{uuid4()}")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_incident(app_with_overrides):
    app, fake_db, fake_user = app_with_overrides
    incident = _make_incident(fake_user.user_id)

    # DB responses: 1) check control exists (None = no control link), 2) after add/commit refresh
    result_none = MagicMock()
    result_none.scalar_one_or_none.return_value = None
    fake_db.execute = AsyncMock(return_value=result_none)
    fake_db.add = MagicMock()
    fake_db.commit = AsyncMock()
    fake_db.refresh = AsyncMock(side_effect=lambda obj: None)

    # Patch the incident object that gets created
    with patch("incident.router.SecurityIncident", return_value=incident):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/incidents",
                json={
                    "title_en": "Test Incident",
                    "title_ar": "حادث تجريبي",
                    "description_en": "Description of incident",
                    "description_ar": "وصف الحادثة",
                    "severity": "high",
                    "category": "data_breach",
                    "detected_at": "2024-01-01T00:00:00Z",
                },
            )

    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_playbooks(app_with_overrides):
    app, fake_db, fake_user = app_with_overrides

    from incident.models import IncidentPlaybook, IncidentCategory

    playbook = MagicMock(spec=IncidentPlaybook)
    playbook.playbook_id = uuid4()
    playbook.name_en = "Playbook 1"
    playbook.name_ar = "دليل 1"
    playbook.category = IncidentCategory.DATA_BREACH
    playbook.description_en = "Description"
    playbook.description_ar = "وصف"
    playbook.detection_steps = [{"step": "1", "description": "Detect"}]
    playbook.containment_steps = [{"step": "1", "description": "Contain"}]
    playbook.eradication_steps = [{"step": "1", "description": "Eradicate"}]
    playbook.recovery_steps = [{"step": "1", "description": "Recover"}]
    playbook.created_by = uuid4()
    playbook.is_active = True
    playbook.created_at = datetime(2024, 1, 1)

    result = MagicMock()
    result.scalars.return_value.all.return_value = [playbook]
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/playbooks")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_incident_statistics(app_with_overrides):
    app, fake_db, _ = app_with_overrides

    scalar_result = MagicMock()
    scalar_result.scalar.return_value = 5
    scalar_result.scalars.return_value.all.return_value = []
    fake_db.execute = AsyncMock(return_value=scalar_result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/statistics/incidents")

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
