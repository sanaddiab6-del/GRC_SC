"""
Audit Management Pydantic schemas for request/response validation.
External audit planning, finding tracking, and certification management.
"""
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel

from audit.models import AuditType, AuditStatus, FindingSeverity, FindingStatus


# ===== AUDIT PROGRAM SCHEMAS =====

class AuditProgramCreate(BaseModel):
    title_en: str
    title_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    audit_year: int
    audit_type: AuditType
    scope_description_en: str
    scope_description_ar: str
    planned_start_date: datetime
    planned_end_date: datetime
    iso27001_in_scope: bool = True
    nca_ecc_in_scope: bool = True
    nca_ccc_in_scope: bool = True
    pdpl_in_scope: bool = True
    certification_body: Optional[str] = None


class AuditProgramResponse(BaseModel):
    program_id: int
    program_code: str
    title_en: str
    title_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    audit_year: int
    audit_type: AuditType
    status: AuditStatus
    scope_description_en: str
    scope_description_ar: str
    planned_start_date: datetime
    planned_end_date: datetime
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    iso27001_in_scope: bool
    nca_ecc_in_scope: bool
    nca_ccc_in_scope: bool
    pdpl_in_scope: bool
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    certification_body: Optional[str] = None
    lead_auditor_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== AUDIT FINDING SCHEMAS =====

class AuditFindingCreate(BaseModel):
    program_id: int
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    evidence_reference_en: str
    evidence_reference_ar: str
    severity: FindingSeverity
    finding_type: str
    control_reference: str
    control_requirement_en: str
    control_requirement_ar: str
    gap_identified_en: str
    gap_identified_ar: str
    risk_rating: str
    recommendation_en: str
    recommendation_ar: str
    due_date: datetime
    iso27001_clause: Optional[str] = None
    nca_ecc_control: Optional[str] = None
    pdpl_article: Optional[str] = None


class AuditFindingUpdate(BaseModel):
    status: Optional[FindingStatus] = None
    corrective_action_plan_en: Optional[str] = None
    corrective_action_plan_ar: Optional[str] = None
    progress_percentage: Optional[int] = None
    target_closure_date: Optional[datetime] = None
    actual_closure_date: Optional[datetime] = None


class AuditFindingResponse(BaseModel):
    finding_id: int
    finding_number: str
    program_id: int
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    severity: FindingSeverity
    finding_type: str
    status: FindingStatus
    control_reference: str
    risk_rating: str
    recommendation_en: str
    recommendation_ar: str
    due_date: datetime
    corrective_action_plan_en: Optional[str] = None
    corrective_action_plan_ar: Optional[str] = None
    progress_percentage: int
    target_closure_date: Optional[datetime] = None
    actual_closure_date: Optional[datetime] = None
    iso27001_clause: Optional[str] = None
    nca_ecc_control: Optional[str] = None
    pdpl_article: Optional[str] = None
    owner_id: int
    identified_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== CERTIFICATION SCHEMAS =====

class CertificationCreate(BaseModel):
    certificate_number: str
    certification_standard: str
    certification_body: str
    scope_en: str
    scope_ar: str
    issue_date: datetime
    expiry_date: datetime
    surveillance_due_dates: Optional[Any] = None


class CertificationResponse(BaseModel):
    certification_id: int
    certificate_number: str
    certification_standard: str
    certification_body: str
    scope_en: str
    scope_ar: str
    issue_date: datetime
    expiry_date: datetime
    status: str
    surveillance_due_dates: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

