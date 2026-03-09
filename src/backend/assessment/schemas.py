"""
Assessment Pydantic Schemas
Request/Response models for assessment execution API
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# Assessment Instance Schemas
# ============================================================================

class AssessmentInstanceCreate(BaseModel):
    """Create new assessment instance"""
    assessment_id: str = Field(..., pattern="^ASM-[0-9]{4}-[0-9]{3}$")
    name_en: str = Field(..., min_length=5, max_length=255)
    name_ar: str = Field(..., min_length=5, max_length=255)
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    assessment_type: str
    framework: str  # ECC, CCC, PDPL
    control_scope: Optional[List[str]] = None
    domain_scope: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    organization_id: Optional[int] = None


class AssessmentInstanceUpdate(BaseModel):
    """Update assessment instance"""
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_assessor_id: Optional[int] = None
    reviewer_id: Optional[int] = None


class AssessmentLaunchRequest(BaseModel):
    """Launch assessment request"""
    assigned_assessor_id: int
    due_date: datetime
    launch_notification: bool = True


class AssessmentAssignRequest(BaseModel):
    """Assign/reassign assessor"""
    assigned_assessor_id: int
    comment: Optional[str] = None


class AssessmentSubmitRequest(BaseModel):
    """Submit assessment for review"""
    submission_comment: Optional[str] = None


class AssessmentReviewRequest(BaseModel):
    """Review assessment"""
    reviewer_id: int
    review_comment: Optional[str] = None
    return_for_revision: bool = False
    revision_notes: Optional[str] = None


class AssessmentApprovalRequest(BaseModel):
    """Approve/reject assessment"""
    decision: str = Field(..., pattern="^(approved|rejected)$")
    approval_comment: str
    approver_id: int


class AssessmentCloseRequest(BaseModel):
    """Close assessment"""
    closure_comment: Optional[str] = None
    submit_to_regulator: bool = False
    regulator_reference: Optional[str] = None


class AssessmentInstanceResponse(BaseModel):
    """Assessment instance response"""
    id: int
    assessment_id: str
    name_en: str
    name_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    assessment_type: str
    framework: str
    control_scope: Optional[List[str]] = None
    domain_scope: Optional[List[str]] = None

    created_by_id: int
    assigned_assessor_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    approver_id: Optional[int] = None
    organization_id: Optional[int] = None

    status: str
    launched_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    total_controls: int
    completed_controls: int
    progress_percentage: float

    compliance_score: Optional[float] = None
    weighted_score: Optional[float] = None
    compliant_count: int
    non_compliant_count: int
    partial_compliant_count: int
    not_applicable_count: int

    approval_required: bool
    approval_comment: Optional[str] = None
    rejection_reason: Optional[str] = None

    submitted_to_regulator: bool
    regulator_submission_date: Optional[datetime] = None
    regulator_reference_number: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Assessment Response Schemas
# ============================================================================

class AssessmentResponseCreate(BaseModel):
    """Create assessment response for a control"""
    assessment_id: int
    control_id: str
    compliance_status: str
    maturity_level: Optional[int] = Field(None, ge=0, le=5)
    effectiveness_rating: Optional[str] = None

    findings_en: Optional[str] = None
    findings_ar: Optional[str] = None
    gaps_identified_en: Optional[str] = None
    gaps_identified_ar: Optional[str] = None

    evidence_provided: bool = False
    evidence_ids: Optional[List[str]] = None
    evidence_quality: Optional[str] = None

    recommendation_en: Optional[str] = None
    recommendation_ar: Optional[str] = None
    risk_rating: Optional[str] = None

    remediation_required: bool = False
    remediation_deadline: Optional[datetime] = None
    remediation_owner_id: Optional[int] = None


class AssessmentResponseUpdate(BaseModel):
    """Update assessment response"""
    compliance_status: Optional[str] = None
    maturity_level: Optional[int] = Field(None, ge=0, le=5)
    effectiveness_rating: Optional[str] = None
    findings_en: Optional[str] = None
    findings_ar: Optional[str] = None
    gaps_identified_en: Optional[str] = None
    gaps_identified_ar: Optional[str] = None
    evidence_provided: Optional[bool] = None
    evidence_ids: Optional[List[str]] = None
    evidence_quality: Optional[str] = None
    recommendation_en: Optional[str] = None
    recommendation_ar: Optional[str] = None
    risk_rating: Optional[str] = None
    remediation_required: Optional[bool] = None
    remediation_deadline: Optional[datetime] = None
    remediation_owner_id: Optional[int] = None


class AssessmentResponseResponse(BaseModel):
    """Assessment response response model"""
    id: int
    assessment_id: int
    control_id: str
    compliance_status: str
    maturity_level: Optional[int] = None
    effectiveness_rating: Optional[str] = None
    findings_en: Optional[str] = None
    findings_ar: Optional[str] = None
    gaps_identified_en: Optional[str] = None
    gaps_identified_ar: Optional[str] = None
    evidence_provided: bool
    evidence_ids: Optional[List[str]] = None
    evidence_quality: Optional[str] = None
    recommendation_en: Optional[str] = None
    recommendation_ar: Optional[str] = None
    risk_rating: Optional[str] = None
    remediation_required: bool
    remediation_deadline: Optional[datetime] = None
    remediation_owner_id: Optional[int] = None
    control_weight: float
    control_score: Optional[float] = None
    assessed_by_id: int
    assessed_at: datetime
    reviewer_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Assessment Status History Schemas
# ============================================================================

class AssessmentStatusHistoryResponse(BaseModel):
    """Status history response"""
    id: int
    assessment_id: int
    from_status: str
    to_status: str
    changed_by_id: int
    changed_at: datetime
    comment: Optional[str] = None
    ip_address: Optional[str] = None
    approval_decision: Optional[str] = None
    approval_comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# List Responses
# ============================================================================

class AssessmentInstanceListResponse(BaseModel):
    """Paginated assessment list"""
    total: int
    offset: int
    limit: int
    items: List[AssessmentInstanceResponse]


class AssessmentResponseListResponse(BaseModel):
    """Paginated response list"""
    total: int
    offset: int
    limit: int
    items: List[AssessmentResponseResponse]


# ============================================================================
# Dashboard & Analytics
# ============================================================================

class AssessmentDashboardStats(BaseModel):
    """Assessment execution dashboard statistics"""
    total_assessments: int
    draft: int
    launched: int
    in_progress: int
    submitted: int
    reviewed: int
    approved: int
    closed: int
    overdue: int
    avg_completion_time_days: Optional[float] = None
    avg_compliance_score: Optional[float] = None
