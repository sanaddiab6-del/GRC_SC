"""
Assessment Execution Models
NCA ECC/CCC/PDPL Assessment Lifecycle Management
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class AssessmentStatus(str, Enum):
    """Assessment lifecycle states"""
    DRAFT = "draft"
    LAUNCHED = "launched"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    CLOSED = "closed"
    REJECTED = "rejected"


class AssessmentType(str, Enum):
    """Assessment types for Saudi compliance"""
    ECC_ANNUAL = "ecc_annual"
    CCC_CLOUD = "ccc_cloud"
    PDPL_PRIVACY = "pdpl_privacy"
    INTERNAL_AUDIT = "internal_audit"
    CONTROL_TESTING = "control_testing"
    GAP_ANALYSIS = "gap_analysis"
    VENDOR_ASSESSMENT = "vendor_assessment"


class AssessmentInstance(Base):
    """
    Assessment Instance - Main assessment execution entity
    Tracks complete lifecycle from launch to closure
    """
    __tablename__ = "assessment_instances"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, nullable=False, index=True)  # ASM-2026-001

    # Assessment definition
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=False)
    description_en = Column(Text)
    description_ar = Column(Text)
    assessment_type = Column(String(50), nullable=False)  # AssessmentType enum

    # Scope definition
    framework = Column(String(50), nullable=False)  # ECC, CCC, PDPL
    control_scope = Column(JSON)  # List of control IDs in scope
    domain_scope = Column(JSON)  # List of domains

    # Ownership and assignment
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assigned_assessor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Status and lifecycle
    status = Column(String(50), default=AssessmentStatus.DRAFT.value, nullable=False, index=True)
    launched_at = Column(DateTime)
    due_date = Column(DateTime)
    submitted_at = Column(DateTime)
    reviewed_at = Column(DateTime)
    approved_at = Column(DateTime)
    closed_at = Column(DateTime)

    # Scoring and results
    total_controls = Column(Integer, default=0)
    completed_controls = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)

    compliance_score = Column(Float)  # Overall score 0-100
    weighted_score = Column(Float)  # Weighted by control priority

    compliant_count = Column(Integer, default=0)
    non_compliant_count = Column(Integer, default=0)
    partial_compliant_count = Column(Integer, default=0)
    not_applicable_count = Column(Integer, default=0)

    # Approval workflow
    approval_required = Column(Boolean, default=True)
    approval_comment = Column(Text)
    rejection_reason = Column(Text)

    # NCA/SDAIA submission tracking
    submitted_to_regulator = Column(Boolean, default=False)
    regulator_submission_date = Column(DateTime)
    regulator_reference_number = Column(String(100))

    # Audit metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_assessor = relationship("User", foreign_keys=[assigned_assessor_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approver_id])

    responses = relationship("AssessmentResponse", back_populates="assessment", cascade="all, delete-orphan")
    status_history = relationship("AssessmentStatusHistory", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentResponse(Base):
    """
    Assessment Response - Individual control assessment results
    Stores assessor's findings per control with evidence
    """
    __tablename__ = "assessment_responses"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessment_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    control_id = Column(String(50), nullable=False, index=True)  # ECC-GV-1

    # Assessment result
    compliance_status = Column(String(50), nullable=False)  # compliant, non_compliant, partial, not_applicable
    maturity_level = Column(Integer)  # 0-5 (0=not implemented, 5=optimized)
    effectiveness_rating = Column(String(50))  # effective, partially_effective, ineffective

    # Findings
    findings_en = Column(Text)
    findings_ar = Column(Text)
    gaps_identified_en = Column(Text)
    gaps_identified_ar = Column(Text)

    # Evidence
    evidence_provided = Column(Boolean, default=False)
    evidence_ids = Column(JSON)  # List of evidence IDs
    evidence_quality = Column(String(50))  # excellent, adequate, inadequate, missing

    # Recommendations
    recommendation_en = Column(Text)
    recommendation_ar = Column(Text)
    risk_rating = Column(String(50))  # critical, high, medium, low

    # Remediation
    remediation_required = Column(Boolean, default=False)
    remediation_deadline = Column(DateTime)
    remediation_owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Scoring (for weighted calculation)
    control_weight = Column(Float, default=1.0)  # Weight factor for scoring
    control_score = Column(Float)  # Individual control score

    # Assessor details
    assessed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assessed_at = Column(DateTime, default=datetime.utcnow)

    # Reviewer comments
    reviewer_comment = Column(Text)
    reviewed_at = Column(DateTime)

    # Audit metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessment = relationship("AssessmentInstance", back_populates="responses")
    assessed_by = relationship("User", foreign_keys=[assessed_by_id])
    remediation_owner = relationship("User", foreign_keys=[remediation_owner_id])


class AssessmentStatusHistory(Base):
    """
    Assessment Status History - Audit trail for lifecycle transitions
    Required for NCA ECC-IS-5 audit logging
    """
    __tablename__ = "assessment_status_history"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessment_instances.id", ondelete="CASCADE"), nullable=False, index=True)

    # Transition details
    from_status = Column(String(50), nullable=False)
    to_status = Column(String(50), nullable=False)

    # Actor and timestamp
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Transition metadata
    comment = Column(Text)
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(255))

    # Approval/Rejection specific
    approval_decision = Column(String(50))  # approved, rejected, returned
    approval_comment = Column(Text)

    # Relationships
    assessment = relationship("AssessmentInstance", back_populates="status_history")
    changed_by = relationship("User")


# Lifecycle transition rules (state machine)
ASSESSMENT_LIFECYCLE_TRANSITIONS = {
    AssessmentStatus.DRAFT: {AssessmentStatus.LAUNCHED},
    AssessmentStatus.LAUNCHED: {AssessmentStatus.IN_PROGRESS, AssessmentStatus.DRAFT},
    AssessmentStatus.IN_PROGRESS: {AssessmentStatus.SUBMITTED, AssessmentStatus.LAUNCHED},
    AssessmentStatus.SUBMITTED: {AssessmentStatus.REVIEWED, AssessmentStatus.IN_PROGRESS},
    AssessmentStatus.REVIEWED: {AssessmentStatus.APPROVED, AssessmentStatus.REJECTED, AssessmentStatus.IN_PROGRESS},
    AssessmentStatus.APPROVED: {AssessmentStatus.CLOSED},
    AssessmentStatus.REJECTED: {AssessmentStatus.IN_PROGRESS},
    AssessmentStatus.CLOSED: set(),  # Terminal state
}
