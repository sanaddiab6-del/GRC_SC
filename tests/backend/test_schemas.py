"""
Schema validation tests — ensure Pydantic schemas enforce constraints.
"""
import pytest
from pydantic import ValidationError


# ─── Controls schemas ─────────────────────────────────────────────────────────

def test_control_create_valid():
    from controls.schemas import ControlCreate

    c = ControlCreate(
        control_id="ECC-GV-1",
        framework="ECC",
        domain="Governance",
        title_en="Test",
        title_ar="تجريبي",
        description_en="Desc",
        description_ar="وصف",
    )
    assert c.control_id == "ECC-GV-1"


def test_control_create_missing_required():
    from controls.schemas import ControlCreate

    with pytest.raises(ValidationError):
        ControlCreate(
            control_id="X",
            framework="ECC",
            # missing domain, title_en, title_ar, description_en, description_ar
        )


def test_control_update_partial():
    from controls.schemas import ControlUpdate

    u = ControlUpdate(title_en="Updated")
    dump = u.model_dump(exclude_unset=True)
    assert dump == {"title_en": "Updated"}


def test_control_list_response():
    from controls.schemas import ControlListResponse

    resp = ControlListResponse(total=0, offset=0, limit=50, items=[])
    assert resp.total == 0


# ─── Evidence schemas ────────────────────────────────────────────────────────

def test_evidence_create_valid():
    from evidence.schemas import EvidenceCreate

    e = EvidenceCreate(
        evidence_id="EVD-1",
        control_id="ECC-1",
        evidence_type="policy",
        title_en="Ev",
        title_ar="دليل",
    )
    assert e.retention_period_days == 2555  # default


def test_evidence_create_custom_retention():
    from evidence.schemas import EvidenceCreate

    e = EvidenceCreate(
        evidence_id="EVD-2",
        control_id="ECC-2",
        evidence_type="log",
        title_en="Log",
        title_ar="سجل",
        retention_period_days=365,
    )
    assert e.retention_period_days == 365


def test_evidence_update_partial():
    from evidence.schemas import EvidenceUpdate

    u = EvidenceUpdate(status="validated")
    dump = u.model_dump(exclude_unset=True)
    assert dump == {"status": "validated"}


def test_evidence_integrity_response():
    from evidence.schemas import EvidenceIntegrityResponse

    r = EvidenceIntegrityResponse(
        evidence_id="E-1",
        has_hash=True,
        integrity_ok=True,
        message_en="OK",
        message_ar="حسن",
    )
    assert r.integrity_ok is True


def test_evidence_validation_request():
    from evidence.schemas import EvidenceValidationRequest

    v = EvidenceValidationRequest(
        validated_by="admin@example.com",
        approved=True,
    )
    assert v.approved is True


# ─── Auth schemas ─────────────────────────────────────────────────────────────

def test_user_create_strong_password():
    from auth.schemas import UserCreate

    u = UserCreate(
        email="test@example.com",
        password="StrongPass123!@#",
        full_name_en="Test",
    )
    assert u.email == "test@example.com"


def test_user_create_weak_password_too_short():
    from auth.schemas import UserCreate

    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="x@y.com",
            password="Short1!",
        )
    assert "12 characters" in str(exc_info.value).lower() or "min_length" in str(exc_info.value).lower()


def test_user_create_no_uppercase():
    from auth.schemas import UserCreate

    with pytest.raises(ValidationError):
        UserCreate(
            email="x@y.com",
            password="nouppercase123!@#",
        )


def test_user_create_no_lowercase():
    from auth.schemas import UserCreate

    with pytest.raises(ValidationError):
        UserCreate(
            email="x@y.com",
            password="NOLOWERCASE123!@#",
        )


def test_user_create_no_digit():
    from auth.schemas import UserCreate

    with pytest.raises(ValidationError):
        UserCreate(
            email="x@y.com",
            password="NoDigitsHere!@#abc",
        )


def test_user_create_no_special():
    from auth.schemas import UserCreate

    with pytest.raises(ValidationError):
        UserCreate(
            email="x@y.com",
            password="NoSpecial12345abc",
        )


def test_password_change_validation():
    from auth.schemas import PasswordChange

    pc = PasswordChange(
        old_password="anything",
        new_password="NewSecure123!@#",
    )
    assert pc.new_password == "NewSecure123!@#"


def test_password_change_weak_new():
    from auth.schemas import PasswordChange

    with pytest.raises(ValidationError):
        PasswordChange(
            old_password="anything",
            new_password="weak",
        )


def test_token_response():
    from auth.schemas import TokenResponse

    t = TokenResponse(
        access_token="abc",
        refresh_token="def",
        token_type="bearer",
        expires_in=3600,
    )
    assert t.token_type == "bearer"


def test_admin_user_create():
    from auth.schemas import AdminUserCreate

    u = AdminUserCreate(
        email="admin@example.com",
        password="AdminPass123!@#",
        role_name="Analyst",
        is_active=True,
        is_verified=True,
    )
    assert u.role_name == "Analyst"
    assert u.is_active is True


def test_admin_stats_response():
    from auth.schemas import AdminStatsResponse

    s = AdminStatsResponse(
        total_users=10,
        active_users=8,
        total_controls=50,
        total_evidence=30,
        total_reports=5,
    )
    assert s.total_users == 10


def test_system_status_response():
    from auth.schemas import SystemStatusResponse

    s = SystemStatusResponse(
        backend_ok=True,
        database_ok=True,
        security_ok=True,
        database_size_bytes=1024,
    )
    assert s.backend_ok is True


def test_user_role_assignment():
    from auth.schemas import UserRoleAssignment
    import uuid

    a = UserRoleAssignment(
        user_id=uuid.uuid4(),
        role_ids=[uuid.uuid4(), uuid.uuid4()],
    )
    assert len(a.role_ids) == 2
