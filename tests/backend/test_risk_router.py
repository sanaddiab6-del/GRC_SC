"""
Tests for risk/router.py — requires `risk:*` permissions.

Same override strategy as incident tests: patch require_permission at
import time inside the router module.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from httpx import AsyncClient, ASGITransport


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_user(role="Analyst"):
    from auth.models import User

    user = MagicMock(spec=User)
    user.user_id = str(uuid4())
    user.username = "tester"
    user.email = "tester@example.com"
    user.is_active = True

    # Build a role with full risk/vendor permissions so permission_checker passes
    role_mock = MagicMock()
    role_mock.role_name = role
    perms = []
    for resource in ["risk", "vendor"]:
        for action in ["read", "create", "update", "delete", "manage"]:
            perm = MagicMock()
            perm.resource = resource
            perm.action = action
            perms.append(perm)
    role_mock.permissions = perms
    user.roles = [role_mock]
    return user


def _make_risk(override: dict | None = None):
    from risk.models import Risk, RiskCategory, RiskStatus, TreatmentStatus

    uid = uuid4()
    owner_id = uuid4()
    m = MagicMock(spec=Risk)
    m.risk_id = uid
    m.id = str(uid)
    m.risk_number = "RISK-2024-001"
    m.title_en = "Test Risk"
    m.title_ar = "خطر تجريبي"
    m.description_en = "Description"
    m.description_ar = "وصف"
    m.category = RiskCategory.OPERATIONAL
    m.status = RiskStatus.IDENTIFIED
    m.likelihood = 3
    m.impact = 4
    m.inherent_risk_score = 12
    m.inherent_risk_level = "medium"
    m.residual_risk_score = None
    m.residual_risk_level = None
    m.treatment_status = TreatmentStatus.PLANNED
    m.risk_owner = owner_id
    m.identified_by = owner_id
    m.identified_at = datetime(2024, 1, 1)
    m.last_assessed_at = None
    m.next_review_date = None
    m.control_id = None
    m.created_at = datetime(2024, 1, 1)
    m.updated_at = datetime(2024, 1, 1)

    if override:
        for k, v in override.items():
            setattr(m, k, v)
    return m


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def app_with_overrides():
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

    with patch("risk.router.require_permission", return_value=lambda: fake_user):
        yield app, fake_db, fake_user

    app.dependency_overrides = orig


# ── logic unit tests (no HTTP) ────────────────────────────────────────────────

def test_calculate_risk_score_low():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(1, 1)
    assert score == 1
    assert level == "low"


def test_calculate_risk_score_medium():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(3, 4)  # 12 → medium
    assert score == 12
    assert level == "medium"


def test_calculate_risk_score_high():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(4, 4)  # 16 → high
    assert score == 16
    assert level == "high"


def test_calculate_risk_score_critical():
    from risk.router import calculate_risk_score

    score, level = calculate_risk_score(5, 5)  # 25 → critical
    assert score == 25
    assert level == "critical"


# ── endpoint tests ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_risks(app_with_overrides):
    app, fake_db, _ = app_with_overrides
    risk = _make_risk()

    result = MagicMock()
    result.scalars.return_value.all.return_value = [risk]
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/risks")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_risk_found(app_with_overrides):
    app, fake_db, _ = app_with_overrides
    risk = _make_risk()
    risk_id = str(uuid4())
    risk.id = risk_id

    result = MagicMock()
    result.scalar_one_or_none.return_value = risk
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/api/v1/risks/{risk_id}")

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_risk_not_found(app_with_overrides):
    app, fake_db, _ = app_with_overrides

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/api/v1/risks/{uuid4()}")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_vendors(app_with_overrides):
    app, fake_db, _ = app_with_overrides

    from risk.models import ThirdPartyRisk

    vendor = MagicMock(spec=ThirdPartyRisk)
    vendor.vendor_id = uuid4()
    vendor.vendor_name = "Vendor Co"
    vendor.vendor_type = "cloud_provider"
    vendor.risk_rating = "medium"
    vendor.services_provided_en = "Cloud hosting services"
    vendor.services_provided_ar = "خدمات الاستضافة السحابية"
    vendor.data_access_level = "limited"
    vendor.has_nca_compliance = False
    vendor.has_iso27001 = False
    vendor.has_soc2 = False
    vendor.contract_start_date = None
    vendor.contract_end_date = None
    vendor.last_review_date = None
    vendor.next_review_date = None
    vendor.is_active = True
    vendor.created_at = datetime(2024, 1, 1)

    result = MagicMock()
    result.scalars.return_value.all.return_value = [vendor]
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/vendors")

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_risk_statistics(app_with_overrides):
    app, fake_db, _ = app_with_overrides

    result = MagicMock()
    result.scalar.return_value = 3
    result.scalars.return_value.all.return_value = []
    fake_db.execute = AsyncMock(return_value=result)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/statistics/risks")

    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)
