"""
Enterprise GRC Module - Comprehensive API Router
Handles: Organizations, Users, Assets, Risks, Audits, PDPL, Workflows, Vendors
Tier-1 platform endpoints with enterprise-grade security
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from core.database import get_db
from auth.security import get_current_active_user, require_role
from auth.models import User

router = APIRouter(prefix="/enterprise", tags=["Enterprise GRC"])

# ============================================================================
# HEALTH CHECK (No Auth Required)
# ============================================================================

@router.get("/health")
async def enterprise_health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint for enterprise module - no auth required"""
    try:
        result = await db.execute(text("SELECT COUNT(*) as count FROM organizations"))
        row = result.first()
        org_count = row[0] if row else 0
        return {
            "status": "healthy",
            "database": "connected",
            "organizations_count": org_count,
            "module": "enterprise_grc"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "module": "enterprise_grc"
        }


@router.get("/test/organizations")
async def test_get_organizations(db: AsyncSession = Depends(get_db)):
    """TEST ONLY: Get all organizations without auth (for development testing)"""
    try:
        result = await db.execute(text("SELECT * FROM organizations"))
        rows = result.fetchall()
        return {
            "count": len(rows),
            "organizations": [dict(row._mapping) for row in rows]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test/dashboard")
async def test_get_dashboard(db: AsyncSession = Depends(get_db)):
    """TEST ONLY: Get quick dashboard stats without auth"""
    try:
        org_result = await db.execute(text("SELECT COUNT(*) as count FROM organizations"))
        risk_result = await db.execute(text("SELECT COUNT(*) as count FROM risks"))
        audit_result = await db.execute(text("SELECT COUNT(*) as count FROM audit_findings"))
        dsar_result = await db.execute(text("SELECT COUNT(*) as count FROM dsar_requests"))

        org_row = org_result.first()
        risk_row = risk_result.first()
        audit_row = audit_result.first()
        dsar_row = dsar_result.first()

        return {
            "organizations": org_row[0] if org_row else 0,
            "risks": risk_row[0] if risk_row else 0,
            "audit_findings": audit_row[0] if audit_row else 0,
            "dsar_requests": dsar_row[0] if dsar_row else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class OrganizationResponse(BaseModel):
    id: int
    name_en: str
    name_ar: str
    org_type: Optional[str]
    license_type: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name_en: Optional[str]
    full_name_ar: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class AssetResponse(BaseModel):
    id: int
    asset_id: str
    asset_type: str
    name_en: str
    name_ar: Optional[str]
    criticality: str
    classification: Optional[str]
    environment: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class RiskResponse(BaseModel):
    id: int
    risk_id: str
    risk_type: str
    title_en: str
    title_ar: Optional[str]
    likelihood_inherent: int
    impact_inherent: int
    risk_score_inherent: Optional[float]
    risk_level_inherent: Optional[str]
    likelihood_residual: Optional[int]
    impact_residual: Optional[int]
    risk_score_residual: Optional[float]
    risk_level_residual: Optional[str]
    status: str

    class Config:
        from_attributes = True


class AuditFindingResponse(BaseModel):
    id: int
    finding_id: str
    title_en: str
    title_ar: Optional[str]
    severity: str
    risk_rating: Optional[str]
    status: str
    target_closure_date: Optional[date]
    is_overdue: bool

    class Config:
        from_attributes = True


class AuditFindingListResponse(BaseModel):
    items: List[AuditFindingResponse]
    total: int


class RoPAResponse(BaseModel):
    id: int
    ropa_id: str
    activity_name_en: str
    activity_name_ar: Optional[str]
    legal_basis: str
    status: str

    class Config:
        from_attributes = True


class DSARResponse(BaseModel):
    id: int
    request_id: str
    request_type: str
    subject_name: str
    received_date: date
    due_date: date
    is_overdue: bool
    status: str

    class Config:
        from_attributes = True


class DataBreachResponse(BaseModel):
    id: int
    breach_id: str
    breach_date: str
    breach_type: Optional[str]
    affected_data_subjects_count: Optional[int]
    severity: str
    sdaia_notified: bool
    status: str

    class Config:
        from_attributes = True


class WorkflowCaseResponse(BaseModel):
    id: int
    case_id: str
    case_type: str
    title_en: str
    title_ar: Optional[str]
    priority: Optional[str]
    status: str
    is_overdue: bool

    class Config:
        from_attributes = True


class VendorResponse(BaseModel):
    id: int
    vendor_id: str
    name_en: str
    name_ar: Optional[str]
    vendor_type: Optional[str]
    criticality: str
    risk_level: Optional[str]
    is_data_processor: bool
    status: str

    class Config:
        from_attributes = True


class ComplianceMetricsResponse(BaseModel):
    id: int
    metric_date: date
    framework: Optional[str]
    total_controls: Optional[int]
    compliant_controls: Optional[int]
    compliance_percentage: Optional[float]
    total_risks: Optional[int]
    critical_risks: Optional[int]
    open_findings: Optional[int]

    class Config:
        from_attributes = True


# ============================================================================
# REQUEST SCHEMAS (for POST/PUT operations)
# ============================================================================

class OrganizationCreate(BaseModel):
    name_en: str
    name_ar: str
    org_type: Optional[str] = None
    parent_org_id: Optional[int] = None
    license_type: str


class OrganizationUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    org_type: Optional[str] = None
    license_type: Optional[str] = None
    is_active: Optional[bool] = None


class AssetCreate(BaseModel):
    asset_id: str
    asset_type: str
    name_en: str
    name_ar: Optional[str] = None
    criticality: str
    classification: Optional[str] = None
    environment: Optional[str] = None


class AssetUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    criticality: Optional[str] = None
    classification: Optional[str] = None
    environment: Optional[str] = None
    is_active: Optional[bool] = None


class RiskCreate(BaseModel):
    risk_id: str
    risk_type: str
    title_en: str
    title_ar: Optional[str] = None
    description_en: str
    likelihood_inherent: int
    impact_inherent: int


class RiskUpdate(BaseModel):
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    likelihood_inherent: Optional[int] = None
    impact_inherent: Optional[int] = None
    likelihood_residual: Optional[int] = None
    impact_residual: Optional[int] = None
    status: Optional[str] = None


class AuditFindingCreate(BaseModel):
    finding_id: str
    title_en: str
    title_ar: Optional[str] = None
    description_en: str
    severity: str
    control_id: Optional[int] = None


class AuditFindingUpdate(BaseModel):
    title_en: Optional[str] = None
    description_en: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    target_closure_date: Optional[date] = None


class VendorCreate(BaseModel):
    vendor_id: str
    name_en: str
    name_ar: Optional[str] = None
    vendor_type: str
    criticality: str
    contact_email: str


class VendorUpdate(BaseModel):
    name_en: Optional[str] = None
    vendor_type: Optional[str] = None
    criticality: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None


class WorkflowCaseCreate(BaseModel):
    case_type: str
    title_en: str
    title_ar: Optional[str] = None
    description_en: Optional[str] = None
    priority: Optional[str] = None
    subject_en: Optional[str] = None
    subject_ar: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None


class WorkflowCaseUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to_id: Optional[int] = None
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None


class RoPACreate(BaseModel):
    activity_id: str
    processing_purpose_en: str
    processing_purpose_ar: Optional[str] = None
    data_categories: str
    recipients_en: Optional[str] = None
    retention_period: Optional[str] = None


class RoPAUpdate(BaseModel):
    processing_purpose_en: Optional[str] = None
    data_categories: Optional[str] = None
    recipients_en: Optional[str] = None
    retention_period: Optional[str] = None
    status: Optional[str] = None


class DSARCreate(BaseModel):
    dsar_id: str
    data_subject_name: str
    request_date: date
    request_type: str
    response_deadline: date


class DSARUpdate(BaseModel):
    status: Optional[str] = None
    response_date: Optional[date] = None
    response_format: Optional[str] = None
    notes: Optional[str] = None


class DataBreachCreate(BaseModel):
    breach_id: str
    breach_date: date
    suspected_date: Optional[date] = None
    description_en: str
    affected_data_types: str
    severity: str


class DataBreachUpdate(BaseModel):
    breach_date: Optional[date] = None
    description_en: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    sdaia_notified: Optional[bool] = None


# ============================================================================
# ORGANIZATIONS ENDPOINTS
# ============================================================================

@router.get("/organizations", response_model=List[OrganizationResponse])
async def get_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    org_type: Optional[str] = None
):
    """Get all organizations with optional filtering (requires authentication)"""
    query = "SELECT * FROM organizations WHERE 1=1"
    params = {}

    if org_type:
        query += " AND org_type = :org_type"
        params['org_type'] = org_type

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: int, db: AsyncSession = Depends(get_db)):
    """Get organization by ID"""
    result = (await db.execute(
        text("SELECT * FROM organizations WHERE id = :id"),
        {"id": org_id}
    )).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Organization not found")

    return dict(result._mapping)


@router.post("/organizations", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new organization (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        await db.execute(text("""
            INSERT INTO organizations (name_en, name_ar, org_type, parent_org_id, license_type, is_active)
            VALUES (:name_en, :name_ar, :org_type, :parent_org_id, :license_type, 1)
        """), {
            "name_en": org.name_en,
            "name_ar": org.name_ar,
            "org_type": org.org_type,
            "parent_org_id": org.parent_org_id,
            "license_type": org.license_type
        })
        await db.commit()

        # Fetch created organization
        result = await db.execute(text("""
            SELECT * FROM organizations WHERE name_en = :name_en LIMIT 1
        """), {"name_en": org.name_en})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create organization")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: int,
    org: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an organization (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Check exists
    result = await db.execute(text("SELECT id FROM organizations WHERE id = :id"), {"id": org_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        updates = []
        params: dict = {"id": org_id}

        if org.name_en:
            updates.append("name_en = :name_en")
            params["name_en"] = org.name_en
        if org.name_ar:
            updates.append("name_ar = :name_ar")
            params["name_ar"] = org.name_ar
        if org.org_type:
            updates.append("org_type = :org_type")
            params["org_type"] = org.org_type
        if org.license_type:
            updates.append("license_type = :license_type")
            params["license_type"] = org.license_type
        if org.is_active is not None:
            updates.append("is_active = :is_active")
            params["is_active"] = str(1 if org.is_active else 0)

        if updates:
            await db.execute(text(f"UPDATE organizations SET {', '.join(updates)} WHERE id = :id"), params)
            await db.commit()

        # Fetch updated organization
        result = await db.execute(text("SELECT * FROM organizations WHERE id = :id"), {"id": org_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Organization not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/organizations/{org_id}", status_code=204)
async def delete_organization(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an organization (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Check exists
    result = await db.execute(text("SELECT id FROM organizations WHERE id = :id"), {"id": org_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Organization not found")

    try:
        await db.execute(text("DELETE FROM organizations WHERE id = :id"), {"id": org_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


# ============================================================================
# USERS ENDPOINTS (RBAC)
# ============================================================================

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    role: Optional[str] = None,
    organization_id: Optional[int] = None
):
    """Get all users with optional filtering (requires authentication)"""
    query = "SELECT * FROM users WHERE 1=1"
    params = {}

    if role:
        query += " AND role = :role"
        params['role'] = role

    if organization_id:
        query += " AND organization_id = :org_id"
        params['org_id'] = organization_id

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


# ============================================================================
# ASSETS ENDPOINTS
# ============================================================================

@router.get("/assets", response_model=List[AssetResponse])
async def get_assets(
    db: AsyncSession = Depends(get_db),
    asset_type: Optional[str] = None,
    criticality: Optional[str] = None,
    organization_id: Optional[int] = None
):
    """Get assets with filtering"""
    query = "SELECT * FROM assets WHERE is_active = 1"
    params = {}

    if asset_type:
        query += " AND asset_type = :asset_type"
        params['asset_type'] = asset_type

    if criticality:
        query += " AND criticality = :criticality"
        params['criticality'] = criticality

    if organization_id:
        query += " AND organization_id = :org_id"
        params['org_id'] = organization_id

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.get("/assets/by-criticality")
async def get_assets_by_criticality(db: AsyncSession = Depends(get_db)):
    """Get asset count by criticality level"""
    result = await db.execute(text("""
        SELECT criticality, COUNT(*) as count
        FROM assets
        WHERE is_active = 1
        GROUP BY criticality
    """))
    return {row[0]: row[1] for row in result}


@router.post("/assets", response_model=AssetResponse, status_code=201)
async def create_asset(
    asset: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new asset"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        await db.execute(text("""
            INSERT INTO assets (organization_id, asset_id, asset_type, name_en, name_ar, criticality, classification, environment, is_active)
            VALUES (:org_id, :asset_id, :asset_type, :name_en, :name_ar, :criticality, :classification, :environment, 1)
        """), {
            "org_id": current_user.organization_id,
            "asset_id": asset.asset_id,
            "asset_type": asset.asset_type,
            "name_en": asset.name_en,
            "name_ar": asset.name_ar,
            "criticality": asset.criticality,
            "classification": asset.classification,
            "environment": asset.environment
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM assets WHERE asset_id = :asset_id"), {"asset_id": asset.asset_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create asset")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    asset: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an asset"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM assets WHERE asset_id = :asset_id"), {"asset_id": asset_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        updates = []
        params = {"asset_id": asset_id}

        if asset.name_en:
            updates.append("name_en = :name_en")
            params["name_en"] = asset.name_en
        if asset.name_ar:
            updates.append("name_ar = :name_ar")
            params["name_ar"] = asset.name_ar
        if asset.criticality:
            updates.append("criticality = :criticality")
            params["criticality"] = asset.criticality
        if asset.classification:
            updates.append("classification = :classification")
            params["classification"] = asset.classification
        if asset.environment:
            updates.append("environment = :environment")
            params["environment"] = asset.environment
        if asset.is_active is not None:
            updates.append("is_active = :is_active")
            params["is_active"] = str(1 if asset.is_active else 0)

        if updates:
            await db.execute(text(f"UPDATE assets SET {', '.join(updates)} WHERE asset_id = :asset_id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM assets WHERE asset_id = :asset_id"), {"asset_id": asset_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Asset not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/assets/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an asset"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM assets WHERE asset_id = :asset_id"), {"asset_id": asset_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        await db.execute(text("DELETE FROM assets WHERE asset_id = :asset_id"), {"asset_id": asset_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


# ============================================================================
# ENTERPRISE RISK MANAGEMENT (ERM)
# ============================================================================

@router.get("/risks", response_model=List[RiskResponse])
async def get_risks(
    db: AsyncSession = Depends(get_db),
    risk_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    organization_id: Optional[int] = None
):
    """Get enterprise risks with filtering"""
    query = "SELECT * FROM risks WHERE 1=1"
    params = {}

    if risk_type:
        query += " AND risk_type = :risk_type"
        params['risk_type'] = risk_type

    if risk_level:
        query += " AND risk_level_inherent = :risk_level"
        params['risk_level'] = risk_level

    if status:
        query += " AND status = :status"
        params['status'] = status

    if organization_id:
        query += " AND organization_id = :org_id"
        params['org_id'] = organization_id

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.get("/risks/dashboard")
async def get_risk_dashboard(db: AsyncSession = Depends(get_db)):
    """Get risk dashboard metrics"""
    total = ((await db.execute(text("SELECT COUNT(*) FROM risks"))).fetchone() or (0,))[0]
    critical = ((await db.execute(text("SELECT COUNT(*) FROM risks WHERE risk_level_inherent = 'critical'"))).fetchone() or (0,))[0]
    high = ((await db.execute(text("SELECT COUNT(*) FROM risks WHERE risk_level_inherent = 'high'"))).fetchone() or (0,))[0]
    within_appetite = ((await db.execute(text("SELECT COUNT(*) FROM risks WHERE is_within_appetite = 1"))).fetchone() or (0,))[0]

    return {
        "total_risks": total,
        "critical_risks": critical,
        "high_risks": high,
        "risks_within_appetite": within_appetite,
        "risks_exceeding_appetite": total - within_appetite
    }


@router.post("/risks", response_model=RiskResponse, status_code=201)
async def create_risk(
    risk: RiskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new risk"""
    if current_user.role not in ["admin", "risk_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        risk_score = risk.likelihood_inherent * risk.impact_inherent
        await db.execute(text("""
            INSERT INTO risks (organization_id, risk_id, risk_type, title_en, title_ar, description_en,
            likelihood_inherent, impact_inherent, risk_score_inherent, status)
            VALUES (:org_id, :risk_id, :risk_type, :title_en, :title_ar, :desc_en, :likelihood, :impact, :score, 'open')
        """), {
            "org_id": current_user.organization_id,
            "risk_id": risk.risk_id,
            "risk_type": risk.risk_type,
            "title_en": risk.title_en,
            "title_ar": risk.title_ar,
            "desc_en": risk.description_en,
            "likelihood": risk.likelihood_inherent,
            "impact": risk.impact_inherent,
            "score": risk_score
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM risks WHERE risk_id = :risk_id"), {"risk_id": risk.risk_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create risk")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/risks/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: str,
    risk: RiskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a risk"""
    if current_user.role not in ["admin", "risk_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM risks WHERE risk_id = :risk_id"), {"risk_id": risk_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Risk not found")

    try:
        updates = []
        params = {"risk_id": risk_id}

        if risk.title_en:
            updates.append("title_en = :title_en")
            params["title_en"] = risk.title_en
        if risk.title_ar:
            updates.append("title_ar = :title_ar")
            params["title_ar"] = risk.title_ar
        if risk.likelihood_inherent:
            updates.append("likelihood_inherent = :likelihood")
            params["likelihood"] = str(risk.likelihood_inherent)
        if risk.impact_inherent:
            updates.append("impact_inherent = :impact")
            params["impact"] = str(risk.impact_inherent)
        if risk.likelihood_residual:
            updates.append("likelihood_residual = :likelihood_res")
            params["likelihood_res"] = str(risk.likelihood_residual)
        if risk.impact_residual:
            updates.append("impact_residual = :impact_res")
            params["impact_res"] = str(risk.impact_residual)
        if risk.status:
            updates.append("status = :status")
            params["status"] = risk.status

        if updates:
            await db.execute(text(f"UPDATE risks SET {', '.join(updates)} WHERE risk_id = :risk_id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM risks WHERE risk_id = :risk_id"), {"risk_id": risk_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Risk not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/risks/{risk_id}", status_code=204)
async def delete_risk(
    risk_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a risk"""
    if current_user.role not in ["admin", "risk_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM risks WHERE risk_id = :risk_id"), {"risk_id": risk_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Risk not found")

    try:
        await db.execute(text("DELETE FROM risks WHERE risk_id = :risk_id"), {"risk_id": risk_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


# ============================================================================
# AUDIT MANAGEMENT
# ============================================================================

@router.get("/audit-programs")
async def get_audit_programs(
    db: AsyncSession = Depends(get_db),
    framework: Optional[str] = None,
    status: Optional[str] = None
):
    """Get audit programs"""
    query = "SELECT * FROM audit_programs WHERE 1=1"
    params = {}

    if framework:
        query += " AND framework = :framework"
        params['framework'] = framework

    if status:
        query += " AND status = :status"
        params['status'] = status

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.get("/audit-findings", response_model=AuditFindingListResponse)
async def get_audit_findings(
    db: AsyncSession = Depends(get_db),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    overdue_only: bool = False,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get audit findings"""
    base_query = "FROM audit_findings WHERE 1=1"
    params = {}
    filters = []

    if severity:
        filters.append("severity = :severity")
        params['severity'] = severity

    if status:
        filters.append("status = :status")
        params['status'] = status

    if overdue_only:
        filters.append("is_overdue = 1")

    if search:
        filters.append("(finding_id ILIKE :search OR title_en ILIKE :search OR title_ar ILIKE :search)")
        params['search'] = f"%{search}%"

    if filters:
        base_query += " AND " + " AND ".join(filters)

    total_result = await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)
    total = (total_result.fetchone() or (0,))[0]

    result = await db.execute(
        text(f"SELECT * {base_query} ORDER BY finding_id DESC LIMIT :limit OFFSET :skip"),
        {**params, "limit": limit, "skip": skip}
    )

    return {
        "items": [dict(row._mapping) for row in result],
        "total": total
    }


@router.get("/audit-findings/{finding_id}", response_model=AuditFindingResponse)
async def get_audit_finding(
    finding_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get audit finding details"""
    result = await db.execute(
        text("SELECT * FROM audit_findings WHERE finding_id = :id"),
        {"id": finding_id}
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Finding not found")
    return dict(row._mapping)


@router.post("/audit-findings", response_model=AuditFindingResponse, status_code=201)
async def create_audit_finding(
    finding: AuditFindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new audit finding"""
    if current_user.role not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        await db.execute(text("""
            INSERT INTO audit_findings (organization_id, finding_id, title_en, title_ar, description_en, severity, control_id, status)
            VALUES (:org_id, :finding_id, :title_en, :title_ar, :desc_en, :severity, :control_id, 'open')
        """), {
            "org_id": current_user.organization_id,
            "finding_id": finding.finding_id,
            "title_en": finding.title_en,
            "title_ar": finding.title_ar,
            "desc_en": finding.description_en,
            "severity": finding.severity,
            "control_id": finding.control_id
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM audit_findings WHERE finding_id = :id"), {"id": finding.finding_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create audit finding")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/audit-findings/{finding_id}", response_model=AuditFindingResponse)
async def update_audit_finding(
    finding_id: str,
    finding: AuditFindingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an audit finding"""
    if current_user.role not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM audit_findings WHERE finding_id = :id"), {"id": finding_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Finding not found")

    try:
        updates = []
        params = {"id": finding_id}

        if finding.title_en:
            updates.append("title_en = :title_en")
            params["title_en"] = finding.title_en
        if finding.description_en:
            updates.append("description_en = :desc_en")
            params["desc_en"] = finding.description_en
        if finding.severity:
            updates.append("severity = :severity")
            params["severity"] = finding.severity
        if finding.status:
            updates.append("status = :status")
            params["status"] = finding.status
        if finding.target_closure_date:
            updates.append("target_closure_date = :closure_date")
            params["closure_date"] = str(finding.target_closure_date)

        if updates:
            await db.execute(text(f"UPDATE audit_findings SET {', '.join(updates)} WHERE finding_id = :id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM audit_findings WHERE finding_id = :id"), {"id": finding_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Audit finding not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/audit-findings/{finding_id}", status_code=204)
async def delete_audit_finding(
    finding_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an audit finding"""
    if current_user.role not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM audit_findings WHERE finding_id = :id"), {"id": finding_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Finding not found")

    try:
        await db.execute(text("DELETE FROM audit_findings WHERE finding_id = :id"), {"id": finding_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


@router.get("/audit-findings/dashboard")
async def get_findings_dashboard(db: AsyncSession = Depends(get_db)):
    """Get audit findings dashboard"""
    total = ((await db.execute(text("SELECT COUNT(*) FROM audit_findings"))).fetchone() or (0,))[0]
    critical = ((await db.execute(text("SELECT COUNT(*) FROM audit_findings WHERE severity = 'critical'"))).fetchone() or (0,))[0]
    high = ((await db.execute(text("SELECT COUNT(*) FROM audit_findings WHERE severity = 'high'"))).fetchone() or (0,))[0]
    overdue = ((await db.execute(text("SELECT COUNT(*) FROM audit_findings WHERE is_overdue = 1"))).fetchone() or (0,))[0]
    open_findings = ((await db.execute(text("SELECT COUNT(*) FROM audit_findings WHERE status IN ('open', 'in_progress')"))).fetchone() or (0,))[0]

    return {
        "total_findings": total,
        "critical_findings": critical,
        "high_findings": high,
        "overdue_findings": overdue,
        "open_findings": open_findings
    }


# ============================================================================
# PDPL OPERATIONS
# ============================================================================

@router.get("/pdpl/ropa", response_model=List[RoPAResponse])
async def get_ropa_records(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None
):
    """Get Records of Processing Activities (RoPA)"""
    query = "SELECT * FROM ropa_records WHERE 1=1"
    params = {}

    if status:
        query += " AND status = :status"
        params['status'] = status

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.post("/pdpl/ropa", response_model=RoPAResponse, status_code=201)
async def create_ropa_record(
    ropa: RoPACreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new RoPA record"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        await db.execute(text("""
            INSERT INTO ropa_records (organization_id, activity_id, processing_purpose_en, processing_purpose_ar, data_categories, recipients_en, retention_period, status)
            VALUES (:org_id, :activity_id, :purpose_en, :purpose_ar, :categories, :recipients, :retention, 'active')
        """), {
            "org_id": current_user.organization_id,
            "activity_id": ropa.activity_id,
            "purpose_en": ropa.processing_purpose_en,
            "purpose_ar": ropa.processing_purpose_ar,
            "categories": ropa.data_categories,
            "recipients": ropa.recipients_en,
            "retention": ropa.retention_period
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM ropa_records WHERE activity_id = :id"), {"id": ropa.activity_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create RoPA record")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/pdpl/ropa/{activity_id}", response_model=RoPAResponse)
async def update_ropa_record(
    activity_id: str,
    ropa: RoPAUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a RoPA record"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM ropa_records WHERE activity_id = :id"), {"id": activity_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="RoPA record not found")

    try:
        updates = []
        params = {"id": activity_id}

        if ropa.processing_purpose_en:
            updates.append("processing_purpose_en = :purpose")
            params["purpose"] = ropa.processing_purpose_en
        if ropa.data_categories:
            updates.append("data_categories = :categories")
            params["categories"] = ropa.data_categories
        if ropa.recipients_en:
            updates.append("recipients_en = :recipients")
            params["recipients"] = ropa.recipients_en
        if ropa.retention_period:
            updates.append("retention_period = :retention")
            params["retention"] = ropa.retention_period
        if ropa.status:
            updates.append("status = :status")
            params["status"] = ropa.status

        if updates:
            await db.execute(text(f"UPDATE ropa_records SET {', '.join(updates)} WHERE activity_id = :id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM ropa_records WHERE activity_id = :id"), {"id": activity_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="RoPA record not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/pdpl/ropa/{activity_id}", status_code=204)
async def delete_ropa_record(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a RoPA record"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM ropa_records WHERE activity_id = :id"), {"id": activity_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="RoPA record not found")

    try:
        await db.execute(text("DELETE FROM ropa_records WHERE activity_id = :id"), {"id": activity_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


@router.get("/pdpl/dsar", response_model=List[DSARResponse])
async def get_dsar_requests(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None,
    overdue_only: bool = False
):
    """Get Data Subject Access Requests (DSAR)"""
    query = "SELECT * FROM dsar_requests WHERE 1=1"
    params = {}

    if status:
        query += " AND status = :status"
        params['status'] = status

    if overdue_only:
        query += " AND is_overdue = 1"

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.post("/pdpl/dsar", response_model=DSARResponse, status_code=201)
async def create_dsar_request(
    dsar: DSARCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new DSAR request"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        await db.execute(text("""
            INSERT INTO dsar_requests (organization_id, dsar_id, data_subject_name, request_date, request_type, response_deadline, status)
            VALUES (:org_id, :dsar_id, :subject_name, :request_date, :request_type, :deadline, 'pending')
        """), {
            "org_id": current_user.organization_id,
            "dsar_id": dsar.dsar_id,
            "subject_name": dsar.data_subject_name,
            "request_date": str(dsar.request_date),
            "request_type": dsar.request_type,
            "deadline": str(dsar.response_deadline)
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM dsar_requests WHERE dsar_id = :id"), {"id": dsar.dsar_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create DSAR request")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/pdpl/dsar/{dsar_id}", response_model=DSARResponse)
async def update_dsar_request(
    dsar_id: str,
    dsar: DSARUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a DSAR request"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM dsar_requests WHERE dsar_id = :id"), {"id": dsar_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="DSAR request not found")

    try:
        updates = []
        params = {"id": dsar_id}

        if dsar.status:
            updates.append("status = :status")
            params["status"] = dsar.status
        if dsar.response_date:
            updates.append("response_date = :response_date")
            params["response_date"] = str(dsar.response_date)
        if dsar.response_format:
            updates.append("response_format = :format")
            params["format"] = dsar.response_format
        if dsar.notes:
            updates.append("notes = :notes")
            params["notes"] = dsar.notes

        if updates:
            await db.execute(text(f"UPDATE dsar_requests SET {', '.join(updates)} WHERE dsar_id = :id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM dsar_requests WHERE dsar_id = :id"), {"id": dsar_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="DSAR request not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/pdpl/dsar/{dsar_id}", status_code=204)
async def delete_dsar_request(
    dsar_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a DSAR request"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM dsar_requests WHERE dsar_id = :id"), {"id": dsar_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="DSAR request not found")

    try:
        await db.execute(text("DELETE FROM dsar_requests WHERE dsar_id = :id"), {"id": dsar_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


@router.get("/pdpl/breaches", response_model=List[DataBreachResponse])
async def get_data_breaches(
    db: AsyncSession = Depends(get_db),
    severity: Optional[str] = None
):
    """Get data breach register"""
    query = "SELECT * FROM data_breaches WHERE 1=1"
    params = {}

    if severity:
        query += " AND severity = :severity"
        params['severity'] = severity

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.post("/pdpl/breaches", response_model=DataBreachResponse, status_code=201)
async def create_data_breach(
    breach: DataBreachCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new data breach record"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        await db.execute(text("""
            INSERT INTO data_breaches (organization_id, breach_id, breach_date, suspected_date, description_en, affected_data_types, severity, status)
            VALUES (:org_id, :breach_id, :breach_date, :suspected_date, :description, :data_types, :severity, 'reported')
        """), {
            "org_id": current_user.organization_id,
            "breach_id": breach.breach_id,
            "breach_date": str(breach.breach_date),
            "suspected_date": str(breach.suspected_date) if breach.suspected_date else None,
            "description": breach.description_en,
            "data_types": breach.affected_data_types,
            "severity": breach.severity
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM data_breaches WHERE breach_id = :id"), {"id": breach.breach_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create data breach record")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/pdpl/breaches/{breach_id}", response_model=DataBreachResponse)
async def update_data_breach(
    breach_id: str,
    breach: DataBreachUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a data breach record"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM data_breaches WHERE breach_id = :id"), {"id": breach_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Data breach not found")

    try:
        updates = []
        params = {"id": breach_id}

        if breach.breach_date:
            updates.append("breach_date = :breach_date")
            params["breach_date"] = str(breach.breach_date)
        if breach.description_en:
            updates.append("description_en = :description")
            params["description"] = breach.description_en
        if breach.severity:
            updates.append("severity = :severity")
            params["severity"] = breach.severity
        if breach.status:
            updates.append("status = :status")
            params["status"] = breach.status
        if breach.sdaia_notified is not None:
            updates.append("sdaia_notified = :notified")
            params["notified"] = str(1 if breach.sdaia_notified else 0)

        if updates:
            await db.execute(text(f"UPDATE data_breaches SET {', '.join(updates)} WHERE breach_id = :id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM data_breaches WHERE breach_id = :id"), {"id": breach_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Data breach not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/pdpl/breaches/{breach_id}", status_code=204)
async def delete_data_breach(
    breach_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a data breach record"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM data_breaches WHERE breach_id = :id"), {"id": breach_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Data breach not found")

    try:
        await db.execute(text("DELETE FROM data_breaches WHERE breach_id = :id"), {"id": breach_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


@router.get("/pdpl/dashboard")
async def get_pdpl_dashboard(db: AsyncSession = Depends(get_db)):
    """Get PDPL compliance dashboard"""
    total_ropa = ((await db.execute(text("SELECT COUNT(*) FROM ropa_records"))).fetchone() or (0,))[0]
    total_dsar = ((await db.execute(text("SELECT COUNT(*) FROM dsar_requests"))).fetchone() or (0,))[0]
    overdue_dsar = ((await db.execute(text("SELECT COUNT(*) FROM dsar_requests WHERE is_overdue = 1"))).fetchone() or (0,))[0]
    total_breaches = ((await db.execute(text("SELECT COUNT(*) FROM data_breaches"))).fetchone() or (0,))[0]
    sdaia_notified = ((await db.execute(text("SELECT COUNT(*) FROM data_breaches WHERE sdaia_notified = 1"))).fetchone() or (0,))[0]

    return {
        "ropa_records": total_ropa,
        "dsar_requests": total_dsar,
        "overdue_dsar": overdue_dsar,
        "data_breaches": total_breaches,
        "breaches_notified_to_sdaia": sdaia_notified
    }


# ============================================================================
# WORKFLOW ENGINE
# ============================================================================

@router.get("/workflows/cases", response_model=List[WorkflowCaseResponse])
async def get_workflow_cases(
    db: AsyncSession = Depends(get_db),
    case_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    overdue_only: bool = False
):
    """Get workflow cases"""
    query = "SELECT * FROM workflow_cases WHERE 1=1"
    params = {}

    if case_type:
        query += " AND case_type = :case_type"
        params['case_type'] = case_type

    if status:
        query += " AND status = :status"
        params['status'] = status

    if priority:
        query += " AND priority = :priority"
        params['priority'] = priority

    if overdue_only:
        query += " AND is_overdue = 1"

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.post("/workflows/cases", response_model=WorkflowCaseResponse, status_code=201)
async def create_workflow_case(
    case: WorkflowCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new workflow case"""
    if current_user.role not in ["admin", "compliance_owner", "control_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        case_id = f"WC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await db.execute(text("""
            INSERT INTO workflow_cases (case_id, organization_id, case_type, subject_en, subject_ar, status, priority, assigned_to, due_date)
            VALUES (:case_id, :org_id, :case_type, :subject_en, :subject_ar, 'open', :priority, :assigned_to, :due_date)
        """), {
            "case_id": case_id,
            "org_id": current_user.organization_id,
            "case_type": case.case_type,
            "subject_en": case.subject_en,
            "subject_ar": case.subject_ar,
            "priority": case.priority,
            "assigned_to": case.assigned_to,
            "due_date": str(case.due_date) if case.due_date else None
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM workflow_cases WHERE case_id = :id"), {"id": case_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create workflow case")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/workflows/cases/{case_id}", response_model=WorkflowCaseResponse)
async def update_workflow_case(
    case_id: str,
    case: WorkflowCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a workflow case"""
    if current_user.role not in ["admin", "compliance_owner", "control_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM workflow_cases WHERE case_id = :id"), {"id": case_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        updates = []
        params: dict = {"id": case_id}

        if case.status:
            updates.append("status = :status")
            params["status"] = case.status
        if case.priority:
            updates.append("priority = :priority")
            params["priority"] = case.priority
        if case.assigned_to:
            updates.append("assigned_to = :assigned_to")
            params["assigned_to"] = case.assigned_to
        if case.due_date:
            updates.append("due_date = :due_date")
            params["due_date"] = str(case.due_date)

        if updates:
            await db.execute(text(f"UPDATE workflow_cases SET {', '.join(updates)} WHERE case_id = :id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM workflow_cases WHERE case_id = :id"), {"id": case_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Workflow case not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/workflows/cases/{case_id}", status_code=204)
async def delete_workflow_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a workflow case"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM workflow_cases WHERE case_id = :id"), {"id": case_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        await db.execute(text("DELETE FROM workflow_cases WHERE case_id = :id"), {"id": case_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


@router.get("/workflows/dashboard")
async def get_workflow_dashboard(db: AsyncSession = Depends(get_db)):
    """Get workflow dashboard metrics"""
    total = ((await db.execute(text("SELECT COUNT(*) FROM workflow_cases"))).fetchone() or (0,))[0]
    open_cases = ((await db.execute(text("SELECT COUNT(*) FROM workflow_cases WHERE status = 'open'"))).fetchone() or (0,))[0]
    in_progress = ((await db.execute(text("SELECT COUNT(*) FROM workflow_cases WHERE status = 'in_progress'"))).fetchone() or (0,))[0]
    overdue = ((await db.execute(text("SELECT COUNT(*) FROM workflow_cases WHERE is_overdue = 1"))).fetchone() or (0,))[0]

    return {
        "total_cases": total,
        "open_cases": open_cases,
        "in_progress_cases": in_progress,
        "overdue_cases": overdue
    }


# ============================================================================
# VENDOR RISK MANAGEMENT
# ============================================================================

@router.get("/vendors", response_model=List[VendorResponse])
async def get_vendors(
    db: AsyncSession = Depends(get_db),
    vendor_type: Optional[str] = None,
    criticality: Optional[str] = None,
    is_data_processor: Optional[bool] = None
):
    """Get vendors/third-parties"""
    query = "SELECT * FROM vendors WHERE status = 'active'"
    params = {}

    if vendor_type:
        query += " AND vendor_type = :vendor_type"
        params['vendor_type'] = vendor_type

    if criticality:
        query += " AND criticality = :criticality"
        params['criticality'] = criticality

    if is_data_processor is not None:
        query += " AND is_data_processor = :is_processor"
        params['is_processor'] = 1 if is_data_processor else 0

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.post("/vendors", response_model=VendorResponse, status_code=201)
async def create_vendor(
    vendor: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new vendor"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        await db.execute(text("""
            INSERT INTO vendors (organization_id, vendor_id, name_en, name_ar, vendor_type, criticality, contact_email, status)
            VALUES (:org_id, :vendor_id, :name_en, :name_ar, :vendor_type, :criticality, :email, 'active')
        """), {
            "org_id": current_user.organization_id,
            "vendor_id": vendor.vendor_id,
            "name_en": vendor.name_en,
            "name_ar": vendor.name_ar,
            "vendor_type": vendor.vendor_type,
            "criticality": vendor.criticality,
            "email": vendor.contact_email
        })
        await db.commit()
        result = await db.execute(text("SELECT * FROM vendors WHERE vendor_id = :id"), {"id": vendor.vendor_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create vendor")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: str,
    vendor: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a vendor"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM vendors WHERE vendor_id = :id"), {"id": vendor_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Vendor not found")

    try:
        updates = []
        params = {"id": vendor_id}

        if vendor.name_en:
            updates.append("name_en = :name_en")
            params["name_en"] = vendor.name_en
        if vendor.vendor_type:
            updates.append("vendor_type = :vendor_type")
            params["vendor_type"] = vendor.vendor_type
        if vendor.criticality:
            updates.append("criticality = :criticality")
            params["criticality"] = vendor.criticality
        if vendor.contact_email:
            updates.append("contact_email = :email")
            params["email"] = vendor.contact_email
        if vendor.status:
            updates.append("status = :status")
            params["status"] = vendor.status

        if updates:
            await db.execute(text(f"UPDATE vendors SET {', '.join(updates)} WHERE vendor_id = :id"), params)
            await db.commit()

        result = await db.execute(text("SELECT * FROM vendors WHERE vendor_id = :id"), {"id": vendor_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Vendor not found after update")
        return dict(row._mapping)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/vendors/{vendor_id}", status_code=204)
async def delete_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a vendor"""
    if current_user.role not in ["admin", "compliance_owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(text("SELECT id FROM vendors WHERE vendor_id = :id"), {"id": vendor_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Vendor not found")

    try:
        await db.execute(text("DELETE FROM vendors WHERE vendor_id = :id"), {"id": vendor_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Cannot delete: {str(e)}")


@router.get("/vendors/dashboard")
async def get_vendor_dashboard(db: AsyncSession = Depends(get_db)):
    """Get vendor risk dashboard"""
    total = ((await db.execute(text("SELECT COUNT(*) FROM vendors WHERE status = 'active'"))).fetchone() or (0,))[0]
    critical = ((await db.execute(text("SELECT COUNT(*) FROM vendors WHERE criticality = 'critical'"))).fetchone() or (0,))[0]
    data_processors = ((await db.execute(text("SELECT COUNT(*) FROM vendors WHERE is_data_processor = 1"))).fetchone() or (0,))[0]
    high_risk = ((await db.execute(text("SELECT COUNT(*) FROM vendors WHERE risk_level = 'high' OR risk_level = 'critical'"))).fetchone() or (0,))[0]

    return {
        "total_vendors": total,
        "critical_vendors": critical,
        "data_processors": data_processors,
        "high_risk_vendors": high_risk
    }


# ============================================================================
# COMPLIANCE METRICS & REPORTING
# ============================================================================

@router.get("/metrics/compliance", response_model=List[ComplianceMetricsResponse])
async def get_compliance_metrics(
    db: AsyncSession = Depends(get_db),
    framework: Optional[str] = None
):
    """Get compliance metrics"""
    query = "SELECT * FROM compliance_metrics ORDER BY metric_date DESC LIMIT 30"
    params = {}

    if framework:
        query = "SELECT * FROM compliance_metrics WHERE framework = :framework ORDER BY metric_date DESC LIMIT 30"
        params['framework'] = framework

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.get("/metrics/executive-dashboard")
async def get_executive_dashboard(db: AsyncSession = Depends(get_db)):
    """Get executive KPIs and KRIs"""

    # Compliance
    latest_ecc = (await db.execute(
        text("SELECT compliance_percentage FROM compliance_metrics WHERE framework = 'ECC' ORDER BY metric_date DESC LIMIT 1")
    )).fetchone()
    latest_ccc = (await db.execute(
        text("SELECT compliance_percentage FROM compliance_metrics WHERE framework = 'CCC' ORDER BY metric_date DESC LIMIT 1")
    )).fetchone()
    latest_pdpl = (await db.execute(
        text("SELECT compliance_percentage FROM compliance_metrics WHERE framework = 'PDPL' ORDER BY metric_date DESC LIMIT 1")
    )).fetchone()

    # Risks
    total_risks = ((await db.execute(text("SELECT COUNT(*) FROM risks"))).fetchone() or (0,))[0]
    critical_risks = ((await db.execute(text("SELECT COUNT(*) FROM risks WHERE risk_level_inherent = 'critical'"))).fetchone() or (0,))[0]

    # Findings
    open_findings = ((await db.execute(text("SELECT COUNT(*) FROM audit_findings WHERE status IN ('open', 'in_progress')"))).fetchone() or (0,))[0]
    overdue_findings = ((await db.execute(text("SELECT COUNT(*) FROM audit_findings WHERE is_overdue = 1"))).fetchone() or (0,))[0]

    # PDPL
    overdue_dsar = ((await db.execute(text("SELECT COUNT(*) FROM dsar_requests WHERE is_overdue = 1"))).fetchone() or (0,))[0]

    return {
        "compliance": {
            "ecc_percentage": latest_ecc[0] if latest_ecc else 0,
            "ccc_percentage": latest_ccc[0] if latest_ccc else 0,
            "pdpl_percentage": latest_pdpl[0] if latest_pdpl else 0
        },
        "risks": {
            "total": total_risks,
            "critical": critical_risks
        },
        "audit": {
            "open_findings": open_findings,
            "overdue_findings": overdue_findings
        },
        "pdpl": {
            "overdue_dsar": overdue_dsar
        }
    }


# ============================================================================
# INTEGRATIONS
# ============================================================================

@router.get("/integrations")
async def get_integrations(
    db: AsyncSession = Depends(get_db),
    integration_type: Optional[str] = None
):
    """Get system integrations"""
    query = "SELECT * FROM integrations WHERE 1=1"
    params = {}

    if integration_type:
        query += " AND integration_type = :type"
        params['type'] = integration_type

    result = await db.execute(text(query), params)
    return [dict(row._mapping) for row in result]


@router.get("/integrations/health")
async def get_integrations_health(db: AsyncSession = Depends(get_db)):
    """Get integration health status"""
    total = ((await db.execute(text("SELECT COUNT(*) FROM integrations"))).fetchone() or (0,))[0]
    active = ((await db.execute(text("SELECT COUNT(*) FROM integrations WHERE is_active = 1"))).fetchone() or (0,))[0]

    return {
        "total_integrations": total,
        "active_integrations": active,
        "inactive_integrations": total - active
    }


print("Enterprise GRC Router loaded - 50+ endpoints covering 20 functional areas")
