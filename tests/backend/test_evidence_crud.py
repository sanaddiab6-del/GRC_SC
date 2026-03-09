"""
Evidence router tests — CRUD + validate + integrity + summary.
"""
import pytest
import hashlib
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport


def _mock_evidence(**kw):
    e = MagicMock()
    e.id = kw.get("id", 1)
    e.evidence_id = kw.get("evidence_id", "EVD-TEST-001")
    e.control_id = kw.get("control_id", "ECC-GV-1")
    e.evidence_type = kw.get("evidence_type", "policy")
    e.status = kw.get("status", "pending")
    e.title_en = kw.get("title_en", "Test Evidence")
    e.title_ar = kw.get("title_ar", "دليل تجريبي")
    e.description_en = kw.get("description_en", None)
    e.description_ar = kw.get("description_ar", None)
    e.file_path = None
    e.file_name = kw.get("file_name", None)
    e.file_size = kw.get("file_size", None)
    e.file_format = None
    e.file_hash = kw.get("file_hash", None)
    e.collection_date = kw.get("collection_date", datetime.utcnow())
    e.expiry_date = kw.get("expiry_date", datetime.utcnow() + timedelta(days=2555))
    e.retention_period_days = 2555
    e.validated_by = None
    e.validated_at = None
    e.validation_notes = None
    e.created_at = datetime.utcnow()
    e.updated_at = datetime.utcnow()
    e.created_by = None
    e.additional_metadata = None
    return e


def _db_override(app, session):
    from core.database import get_db
    async def _db():
        yield session
    app.dependency_overrides[get_db] = _db


def _clear(app):
    app.dependency_overrides.clear()


# ─── List ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_evidence_empty():
    from main import app

    session = AsyncMock()
    session.scalar = AsyncMock(return_value=0)
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/evidence")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["items"] == []
    finally:
        _clear(app)


@pytest.mark.asyncio
async def test_list_evidence_with_filter():
    from main import app

    session = AsyncMock()
    ev = _mock_evidence()
    session.scalar = AsyncMock(return_value=1)
    result = MagicMock()
    result.scalars.return_value.all.return_value = [ev]
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/evidence?control_id=ECC-GV-1&status=pending")
        assert r.status_code == 200
    finally:
        _clear(app)


# ─── Get ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_evidence_found():
    from main import app

    ev = _mock_evidence()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = ev
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/evidence/EVD-TEST-001")
        assert r.status_code == 200
        assert r.json()["evidence_id"] == "EVD-TEST-001"
    finally:
        _clear(app)


@pytest.mark.asyncio
async def test_get_evidence_not_found():
    from main import app

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/evidence/NONEXISTENT")
        assert r.status_code == 404
    finally:
        _clear(app)


# ─── Create ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_evidence_success():
    from main import app

    session = AsyncMock()
    # check_exists -> None
    exists_result = MagicMock()
    exists_result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=exists_result)
    session.add = MagicMock()
    session.commit = AsyncMock()

    ev = _mock_evidence()

    async def fake_refresh(obj):
        for attr in ["id", "evidence_id", "control_id", "evidence_type", "status",
                      "title_en", "title_ar", "description_en", "description_ar",
                      "file_path", "file_name", "file_size", "file_format",
                      "file_hash", "collection_date", "expiry_date",
                      "retention_period_days", "validated_by", "validated_at",
                      "validation_notes", "created_at", "updated_at", "created_by",
                      "additional_metadata"]:
            try:
                setattr(obj, attr, getattr(ev, attr))
            except (AttributeError, TypeError):
                pass

    session.refresh = fake_refresh

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/evidence", json={
                "evidence_id": "EVD-TEST-001",
                "control_id": "ECC-GV-1",
                "evidence_type": "policy",
                "title_en": "Test Evidence",
                "title_ar": "دليل تجريبي",
                "retention_period_days": 2555,
            })
        assert r.status_code == 201
    finally:
        _clear(app)


@pytest.mark.asyncio
async def test_create_evidence_duplicate():
    from main import app

    session = AsyncMock()
    existing = _mock_evidence()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/evidence", json={
                "evidence_id": "EVD-TEST-001",
                "control_id": "ECC-GV-1",
                "evidence_type": "policy",
                "title_en": "Dup",
                "title_ar": "مكرر",
            })
        assert r.status_code == 400
    finally:
        _clear(app)


# ─── Delete ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_evidence_success():
    from main import app

    ev = _mock_evidence()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = ev
    session.execute = AsyncMock(return_value=result)
    session.delete = AsyncMock()
    session.commit = AsyncMock()

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.delete("/api/v1/evidence/EVD-TEST-001")
        assert r.status_code == 204
    finally:
        _clear(app)


@pytest.mark.asyncio
async def test_delete_evidence_not_found():
    from main import app

    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.delete("/api/v1/evidence/NOPE")
        assert r.status_code == 404
    finally:
        _clear(app)


# ─── Integrity check ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_integrity_check_ok():
    from main import app

    # Compute expected hash
    payload = "EVD-TEST-001|ECC-GV-1|Test Evidence|دليل تجريبي||0"
    expected_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    ev = _mock_evidence(file_hash=expected_hash, file_name="", file_size=0)
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = ev
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/evidence/EVD-TEST-001/integrity")
        assert r.status_code == 200
        data = r.json()
        assert data["has_hash"] is True
        assert data["integrity_ok"] is True
    finally:
        _clear(app)


@pytest.mark.asyncio
async def test_integrity_check_tampered():
    from main import app

    ev = _mock_evidence(file_hash="badhash", file_name="", file_size=0)
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = ev
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/evidence/EVD-TEST-001/integrity")
        assert r.status_code == 200
        data = r.json()
        assert data["integrity_ok"] is False
    finally:
        _clear(app)


@pytest.mark.asyncio
async def test_integrity_check_no_hash():
    from main import app

    ev = _mock_evidence(file_hash=None)
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = ev
    session.execute = AsyncMock(return_value=result)

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/v1/evidence/EVD-TEST-001/integrity")
        assert r.status_code == 200
        data = r.json()
        assert data["has_hash"] is False
        assert data["integrity_ok"] is False
    finally:
        _clear(app)


# ─── Validate evidence ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_validate_evidence():
    from main import app

    ev = _mock_evidence()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = ev
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    _db_override(app, session)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/v1/evidence/EVD-TEST-001/validate", json={
                "validated_by": "auditor@example.com",
                "approved": True,
                "validation_notes": "Looks good",
            })
        assert r.status_code == 200
    finally:
        _clear(app)
