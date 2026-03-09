"""
Reporting router tests — dashboard, reports, templates.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport


def _db_override(app, session):
    from core.database import get_db

    async def _db():
        yield session

    app.dependency_overrides[get_db] = _db


def _clear(app):
    app.dependency_overrides.clear()


# ─── Dashboard ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard():
    from main import app

    session = AsyncMock()

    # total_count: scalar
    total_result = MagicMock()
    total_result.scalar.return_value = 10

    # status_query: iterator of (status, count)
    status_result = MagicMock()
    status_result.__iter__ = lambda self: iter([
        ("compliant", 5), ("non_compliant", 2),
        ("in_progress", 2), ("not_started", 1),
    ])

    # framework_query: iterator of (fw, status, count)
    fw_result = MagicMock()
    fw_result.__iter__ = lambda self: iter([
        ("ECC", "compliant", 3), ("ECC", "in_progress", 1),
    ])

    # domain_query: iterator
    domain_result = MagicMock()
    domain_result.__iter__ = lambda self: iter([
        ("Governance", "compliant", 3),
    ])

    # evidence count
    ev_total = MagicMock()
    ev_total.scalar.return_value = 20
    ev_status = MagicMock()
    ev_status.__iter__ = lambda self: iter([("validated", 15)])

    session.execute = AsyncMock(side_effect=[
        total_result, status_result, fw_result, domain_result,
        ev_total, ev_status,
    ])

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert "total_controls" in data
    finally:
        _clear(app)


# ─── Reports list ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_reports():
    from main import app

    session = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/reports")
        assert r.status_code == 200
    finally:
        _clear(app)


# ─── Templates ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_report_templates():
    from main import app

    session = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/report-templates")
        assert r.status_code == 200
    finally:
        _clear(app)


@pytest.mark.asyncio
async def test_create_report_template():
    from main import app

    session = AsyncMock()
    # check_exists: no conflict
    exists_result = MagicMock()
    exists_result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=exists_result)
    session.add = MagicMock()
    session.commit = AsyncMock()

    template_mock = MagicMock()
    template_mock.template_id = 1
    template_mock.template_key = "monthly_compliance"
    template_mock.name_en = "Monthly Report"
    template_mock.name_ar = "تقرير شهري"
    template_mock.description_en = "Desc"
    template_mock.description_ar = "وصف"
    template_mock.export_format = "pdf"
    template_mock.query_config = {}
    template_mock.is_active = True

    async def fake_refresh(obj):
        for attr in dir(template_mock):
            if not attr.startswith("_"):
                try:
                    setattr(obj, attr, getattr(template_mock, attr))
                except (AttributeError, TypeError):
                    pass

    session.refresh = fake_refresh

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/report-templates", json={
                "template_key": "monthly_compliance",
                "name_en": "Monthly Report",
                "name_ar": "تقرير شهري",
                "description_en": "Desc",
                "description_ar": "وصف",
                "export_format": "pdf",
            })
        # May be 201 or 200 depending on implementation
        assert r.status_code in (200, 201)
    finally:
        _clear(app)
