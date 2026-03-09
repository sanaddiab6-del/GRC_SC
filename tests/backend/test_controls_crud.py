"""
Controls module — full CRUD + lifecycle tests.
Mocks the DB session so tests run without PostgreSQL.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_control(**overrides):
    """Return a mock Control ORM object."""
    defaults = dict(
        id=1,
        control_id="ECC-GV-1",
        framework="ECC",
        domain="Governance",
        title_en="Test Control",
        title_ar="ضابط تجريبي",
        description_en="Test description",
        description_ar="وصف تجريبي",
        policy_guidance_en=None,
        policy_guidance_ar=None,
        procedure_guidance_en=None,
        procedure_guidance_ar=None,
        priority="high",
        status="not_started",
        maturity_level=1,
        evidence_types=None,
        related_controls=None,
        lifecycle_updated_at=None,
        created_at=None,
        updated_at=None,
    )
    defaults.update(overrides)
    m = MagicMock()
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


def _fake_db_session(controls=None, total=0):
    """Build an AsyncSession mock that list_controls / get_control can use."""
    session = AsyncMock()

    # For scalar results (count)
    count_result = MagicMock()
    count_result.scalar.return_value = total

    # For scalars().all()  (list queries)
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = controls or []

    # For scalar_one_or_none (get-by-id)
    single_result = MagicMock()
    single_result.scalar_one_or_none.return_value = (controls[0] if controls else None)

    # execute returns different objects depending on call order
    session.execute = AsyncMock(side_effect=[count_result, list_result])
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


# ---------------------------------------------------------------------------
# Tests — list controls
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_controls_empty():
    """GET /api/v1/controls returns empty list when no controls exist."""
    from main import app
    from core.database import get_db

    session = _fake_db_session(controls=[], total=0)

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/controls")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_list_controls_with_results():
    """GET /api/v1/controls returns paginated results."""
    from main import app
    from core.database import get_db

    ctrl = _make_control()
    session = _fake_db_session(controls=[ctrl], total=1)

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/controls?framework=ECC&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["control_id"] == "ECC-GV-1"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_list_controls_with_filters():
    """GET /api/v1/controls accepts framework, status, domain filters."""
    from main import app
    from core.database import get_db

    session = _fake_db_session(controls=[], total=0)

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/controls?framework=CCC&status=compliant&domain=Security")
        assert resp.status_code == 200
    finally:
        app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Tests — get single control
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_control_found():
    """GET /api/v1/controls/{id} returns the control."""
    from main import app
    from core.database import get_db

    ctrl = _make_control()
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = ctrl
    session.execute = AsyncMock(return_value=result_mock)

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/controls/ECC-GV-1")
        assert resp.status_code == 200
        assert resp.json()["control_id"] == "ECC-GV-1"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_get_control_not_found():
    """GET /api/v1/controls/{id} returns 404 for missing control."""
    from main import app
    from core.database import get_db

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result_mock)

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/controls/NONEXISTENT")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Tests — create control
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_control_success():
    """POST /api/v1/controls creates a new control (201)."""
    from main import app
    from core.database import get_db

    session = AsyncMock()
    # check_exists: scalar_one_or_none returns None (no conflict)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result_mock)
    session.commit = AsyncMock()

    new_ctrl = _make_control(status="not_started")

    async def fake_refresh(obj):
        for k, v in vars(new_ctrl).items():
            if not k.startswith("_"):
                try:
                    setattr(obj, k, v)
                except (AttributeError, TypeError):
                    pass

    session.refresh = fake_refresh
    session.add = MagicMock()

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        payload = {
            "control_id": "ECC-GV-1",
            "framework": "ECC",
            "domain": "Governance",
            "title_en": "Test Control",
            "title_ar": "ضابط تجريبي",
            "description_en": "Test description",
            "description_ar": "وصف تجريبي",
            "priority": "high",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/controls", json=payload)
        assert resp.status_code == 201
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_create_control_duplicate():
    """POST /api/v1/controls returns 409 when control_id already exists."""
    from main import app
    from core.database import get_db

    existing = _make_control()
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = existing
    session.execute = AsyncMock(return_value=result_mock)

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        payload = {
            "control_id": "ECC-GV-1",
            "framework": "ECC",
            "domain": "Governance",
            "title_en": "Test",
            "title_ar": "تجريبي",
            "description_en": "Test",
            "description_ar": "تجريبي",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/controls", json=payload)
        assert resp.status_code == 409
    finally:
        app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Tests — delete control
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_control_success():
    """DELETE /api/v1/controls/{id} returns 204."""
    from main import app
    from core.database import get_db

    ctrl = _make_control()
    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = ctrl
    session.execute = AsyncMock(return_value=result_mock)
    session.delete = AsyncMock()
    session.commit = AsyncMock()

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.delete("/api/v1/controls/ECC-GV-1")
        assert resp.status_code == 204
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_delete_control_not_found():
    """DELETE /api/v1/controls/{id} returns 404 for missing control."""
    from main import app
    from core.database import get_db

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result_mock)

    async def override():
        yield session

    app.dependency_overrides[get_db] = override
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.delete("/api/v1/controls/NONEXISTENT")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.pop(get_db, None)
