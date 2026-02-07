"""
Privacy models for PDPL compliance.
Implements consent management, DSAR, and data classification.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class ConsentType(str, enum.Enum):
    """Types of consent as per PDPL Article 6"""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PROFILING = "profiling"
    THIRD_PARTY_SHARING = "third_party_sharing"
    DATA_PROCESSING = "data_processing"
    AUTOMATED_DECISION = "automated_decision"


class ConsentStatus(str, enum.Enum):
    """Consent status"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class DSARType(str, enum.Enum):
    """Data Subject Access Request types (PDPL Articles 4-9)"""
    ACCESS = "access"  # Right to access
    RECTIFICATION = "rectification"  # Right to rectify
    ERASURE = "erasure"  # Right to erasure
    PORTABILITY = "portability"  # Right to data portability
    OBJECTION = "objection"  # Right to object
    RESTRICTION = "restriction"  # Right to restrict processing


class DSARStatus(str, enum.Enum):
    """DSAR request status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class DataClassification(str, enum.Enum):
    """Data classification levels (NCA CCC-SEC-01)"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # PII, PHI, Financial


class Consent(Base):
    """User consent records for PDPL compliance"""
    __tablename__ = "consents"
    
    consent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    consent_type = Column(SQLEnum(ConsentType), nullable=False)
    status = Column(SQLEnum(ConsentStatus), default=ConsentStatus.GIVEN, nullable=False)
    purpose_en = Column(Text, nullable=False)  # What the data will be used for
    purpose_ar = Column(Text, nullable=False)
    legal_basis_en = Column(String(255))  # Legal basis for processing
    legal_basis_ar = Column(String(255))
    given_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    withdrawn_at = Column(DateTime)
    expires_at = Column(DateTime)  # Consent expiry (if applicable)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    consent_text_en = Column(Text)  # Full consent text shown to user
    consent_text_ar = Column(Text)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<Consent {self.consent_id} - {self.consent_type} - {self.status}>"


class DataSubjectRequest(Base):
    """Data Subject Access Requests (PDPL Articles 4-9)"""
    __tablename__ = "data_subject_requests"
    
    request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    request_type = Column(SQLEnum(DSARType), nullable=False)
    status = Column(SQLEnum(DSARStatus), default=DSARStatus.PENDING, nullable=False)
    description_en = Column(Text)
    description_ar = Column(Text)
    
    # Request details
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)  # PDPL: 30 days maximum
    completed_at = Column(DateTime)
    
    # Identity verification (PDPL Article 10)
    verification_method = Column(String(100))  # email, phone, id_document
    verified_at = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    
    # Processing
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    assigned_at = Column(DateTime)
    processor_notes = Column(Text)
    
    # Response
    response_en = Column(Text)
    response_ar = Column(Text)
    data_provided = Column(JSON)  # For access requests
    rejection_reason_en = Column(Text)
    rejection_reason_ar = Column(Text)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])
    assignee = relationship("User", foreign_keys=[assigned_to])


class DataClassificationTag(Base):
    """Data classification tags for assets (NCA CCC)"""
    __tablename__ = "data_classification_tags"
    
    tag_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String(50), nullable=False)  # users, controls, evidence, reports
    resource_id = Column(String(255), nullable=False)
    classification = Column(SQLEnum(DataClassification), nullable=False)
    reason_en = Column(Text)
    reason_ar = Column(Text)
    classified_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    classified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime)
    
    # Relationships
    classifier = relationship("User", foreign_keys=[classified_by])


class DataBreachIncident(Base):
    """Data breach incident tracking (PDPL Article 27)"""
    __tablename__ = "data_breach_incidents"
    
    incident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_number = Column(String(50), unique=True, nullable=False)  # BR-2026-001
    
    # Incident details
    discovered_at = Column(DateTime, nullable=False)
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    breach_type = Column(String(100), nullable=False)  # unauthorized_access, data_loss, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Impact assessment
    affected_records_count = Column(Integer, default=0)
    affected_data_types = Column(JSON)  # ["email", "phone", "financial_data"]
    impact_description_en = Column(Text, nullable=False)
    impact_description_ar = Column(Text, nullable=False)
    
    # Response
    containment_actions_en = Column(Text)
    containment_actions_ar = Column(Text)
    remediation_actions_en = Column(Text)
    remediation_actions_ar = Column(Text)
    
    # Notification (PDPL Article 27 - within 72 hours)
    notification_required = Column(Boolean, default=True)
    sdaia_notified_at = Column(DateTime)  # Saudi Data & AI Authority
    users_notified_at = Column(DateTime)
    notification_method = Column(String(100))  # email, sms, portal
    
    # Status
    status = Column(String(50), default="open")  # open, contained, resolved, closed
    resolved_at = Column(DateTime)
    root_cause_en = Column(Text)
    root_cause_ar = Column(Text)
    
    # Responsible parties
    discovered_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    incident_manager = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    
    # Relationships
    discoverer = relationship("User", foreign_keys=[discovered_by])
    manager = relationship("User", foreign_keys=[incident_manager])


class DataRetentionPolicy(Base):
    """Data retention policies (PDPL Article 12)"""
    __tablename__ = "data_retention_policies"
    
    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String(50), nullable=False)  # users, audit_logs, evidence
    retention_period_days = Column(Integer, nullable=False)  # e.g., 2555 for 7 years
    legal_basis_en = Column(Text, nullable=False)
    legal_basis_ar = Column(Text, nullable=False)
    
    # Deletion rules
    auto_delete_enabled = Column(Boolean, default=True)
    deletion_method = Column(String(50))  # soft_delete, hard_delete, anonymize
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])


class PrivacyImpactAssessment(Base):
    """Privacy Impact Assessments (PDPL Article 33)"""
    __tablename__ = "privacy_impact_assessments"
    
    pia_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name_en = Column(String(255), nullable=False)
    project_name_ar = Column(String(255), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    
    # Assessment
    data_types = Column(JSON, nullable=False)  # Types of personal data processed
    processing_purpose_en = Column(Text, nullable=False)
    processing_purpose_ar = Column(Text, nullable=False)
    legal_basis_en = Column(Text, nullable=False)
    legal_basis_ar = Column(Text, nullable=False)
    
    # Risk assessment
    privacy_risks = Column(JSON)  # [{risk, likelihood, impact, mitigation}]
    risk_score = Column(Integer)  # 1-10
    risk_level = Column(String(20))  # low, medium, high, critical
    
    # Mitigation measures
    mitigation_measures_en = Column(Text)
    mitigation_measures_ar = Column(Text)
    
    # Status
    status = Column(String(50), default="draft")  # draft, under_review, approved, rejected
    conducted_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    conducted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    approved_at = Column(DateTime)
    
    # Review
    next_review_date = Column(DateTime)
    
    # Relationships
    conductor = relationship("User", foreign_keys=[conducted_by])
    approver = relationship("User", foreign_keys=[approved_by])

