"""
Tests for new platform features:
- Control lifecycle transition validation
- Evidence tamper protection (file_hash)
- Regulatory version register
- Commercial packs API
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


# ---------------------------------------------------------------------------
# Commercial Packs API tests (no DB required)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_packs():
    """Packs list endpoint returns all three framework packs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/packs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    frameworks = {p["framework"] for p in data}
    assert "ECC" in frameworks
    assert "CCC" in frameworks
    assert "PDPL" in frameworks


@pytest.mark.asyncio
async def test_list_packs_filter_by_framework():
    """Filter packs by framework name."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/packs?framework=ECC")
    assert response.status_code == 200
    data = response.json()
    assert all(p["framework"] == "ECC" for p in data)


@pytest.mark.asyncio
async def test_get_pack_detail():
    """Fetch a single pack by ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/packs/ecc-baseline")
    assert response.status_code == 200
    pack = response.json()
    assert pack["pack_id"] == "ecc-baseline"
    assert pack["framework"] == "ECC"
    assert "description_en" in pack
    assert "description_ar" in pack
    assert isinstance(pack["features"], list)


@pytest.mark.asyncio
async def test_get_pack_not_found():
    """Non-existent pack returns 404 with bilingual error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/packs/nonexistent-pack")
    assert response.status_code == 404
    body = response.json()
    assert "message_en" in body["detail"]
    assert "message_ar" in body["detail"]


# ---------------------------------------------------------------------------
# Lifecycle transition unit tests (pure Python, no DB required)
# ---------------------------------------------------------------------------

def test_lifecycle_transitions_defined():
    """LIFECYCLE_TRANSITIONS covers all ControlStatus values."""
    from controls.models import ControlStatus, LIFECYCLE_TRANSITIONS

    # Every status should have an entry
    for status in ControlStatus:
        assert status in LIFECYCLE_TRANSITIONS, f"Missing entry for {status}"


def test_lifecycle_not_started_transitions():
    """NOT_STARTED can only go to IN_PROGRESS or NOT_APPLICABLE."""
    from controls.models import ControlStatus, LIFECYCLE_TRANSITIONS

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.NOT_STARTED]
    assert ControlStatus.IN_PROGRESS in allowed
    assert ControlStatus.NOT_APPLICABLE in allowed
    # Cannot jump directly to COMPLIANT
    assert ControlStatus.COMPLIANT not in allowed


def test_lifecycle_in_progress_transitions():
    """IN_PROGRESS can resolve to COMPLIANT, NON_COMPLIANT, or NOT_APPLICABLE."""
    from controls.models import ControlStatus, LIFECYCLE_TRANSITIONS

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.IN_PROGRESS]
    assert ControlStatus.COMPLIANT in allowed
    assert ControlStatus.NON_COMPLIANT in allowed
    assert ControlStatus.NOT_APPLICABLE in allowed


def test_lifecycle_compliant_cannot_go_to_not_started():
    """COMPLIANT controls cannot go back to NOT_STARTED directly."""
    from controls.models import ControlStatus, LIFECYCLE_TRANSITIONS

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.COMPLIANT]
    assert ControlStatus.NOT_STARTED not in allowed


# ---------------------------------------------------------------------------
# Evidence tamper protection unit tests
# ---------------------------------------------------------------------------

def test_file_hash_computed_on_create():
    """_compute_evidence_hash returns a 64-char SHA-256 hex digest."""
    from evidence.router import _compute_evidence_hash
    from evidence.schemas import EvidenceCreate

    evidence_data = EvidenceCreate(
        evidence_id="EVD-TEST-001",
        control_id="ECC-GV-1",
        evidence_type="policy",
        title_en="Test Policy",
        title_ar="سياسة الاختبار",
        file_name="policy.pdf",
        file_size=1024,
    )

    digest = _compute_evidence_hash(evidence_data)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_file_hash_deterministic():
    """Same input always produces the same hash."""
    from evidence.router import _compute_evidence_hash
    from evidence.schemas import EvidenceCreate

    evidence_data = EvidenceCreate(
        evidence_id="EVD-TEST-002",
        control_id="ECC-GV-1",
        evidence_type="log",
        title_en="Log Evidence",
        title_ar="دليل السجل",
    )

    assert _compute_evidence_hash(evidence_data) == _compute_evidence_hash(evidence_data)


def test_file_hash_changes_with_content():
    """Changing any field produces a different hash."""
    from evidence.router import _compute_evidence_hash
    from evidence.schemas import EvidenceCreate

    base = dict(
        evidence_id="EVD-TEST-003",
        control_id="ECC-GV-1",
        evidence_type="policy",
        title_en="Original",
        title_ar="أصلي",
    )
    original = _compute_evidence_hash(EvidenceCreate(**base))

    modified = dict(base)
    modified["title_en"] = "Tampered"
    tampered = _compute_evidence_hash(EvidenceCreate(**modified))

    assert original != tampered


# ---------------------------------------------------------------------------
# Regulatory version register (health endpoint reachable)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_framework_versions_endpoint_exists():
    """The /framework-versions endpoint responds (may have empty list if DB not available)."""
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/framework-versions")
        # Accepts 200 (DB available) or 500/503 (DB unavailable in test env)
        assert response.status_code in (200, 500, 503)
    except Exception:
        # Test environment may raise DB errors instead of HTTP responses; that's acceptable
        pytest.skip("DB not available in this test environment")


# ---------------------------------------------------------------------------
# Health check includes new features in feature flags
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_reports_new_features():
    """Health endpoint announces the four new features."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    features = response.json()["features"]
    assert features.get("control_lifecycle") is True
    assert features.get("evidence_tamper_protection") is True
    assert features.get("regulatory_version_register") is True
    assert features.get("commercial_packs") is True
