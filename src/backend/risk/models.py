"""
Risk Management models for NCA ECC-RM compliance.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Enum as SQLEnum, Float, JSON
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class RiskCategory(str, enum.Enum):
    """Risk categories (NCA ECC-RM)"""
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    REPUTATIONAL = "reputational"
    TECHNOLOGICAL = "technological"
    THIRD_PARTY = "third_party"


class RiskStatus(str, enum.Enum):
    """Risk status"""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    TREATED = "treated"
    ACCEPTED = "accepted"
    TRANSFERRED = "transferred"
    MITIGATED = "mitigated"
    CLOSED = "closed"


class TreatmentStatus(str, enum.Enum):
    """Risk treatment status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Risk(Base):
    """Risk register (NCA ECC-RM-1)"""
    __tablename__ = "risks"
    
    risk_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_number = Column(String(50), unique=True, nullable=False)  # RISK-2026-001
    
    # Classification
    category = Column(SQLEnum(RiskCategory, native_enum=False), nullable=False)
    status = Column(SQLEnum(RiskStatus, native_enum=False), default=RiskStatus.IDENTIFIED, nullable=False)
    
    # Description
    title_en = Column(String(255), nullable=False)
    title_ar = Column(String(255), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    
    # Risk assessment (NCA ECC-RM-1)
    likelihood = Column(Integer, nullable=False)  # 1-5 scale
    impact = Column(Integer, nullable=False)  # 1-5 scale
    inherent_risk_score = Column(Integer)  # likelihood * impact
    inherent_risk_level = Column(String(20))  # low, medium, high, critical
    
    # Current controls
    existing_controls_en = Column(Text)
    existing_controls_ar = Column(Text)
    control_effectiveness = Column(Integer)  # 1-5 scale
    
    # Residual risk (after controls)
    residual_likelihood = Column(Integer)
    residual_impact = Column(Integer)
    residual_risk_score = Column(Integer)
    residual_risk_level = Column(String(20))
    
    # Risk tolerance
    risk_appetite = Column(String(20))  # low, medium, high
    risk_tolerance_exceeded = Column(Boolean, default=False)
    
    # Treatment (NCA ECC-RM-2)
    treatment_strategy = Column(String(50))  # accept, mitigate, transfer, avoid
    treatment_plan_en = Column(Text)
    treatment_plan_ar = Column(Text)
    treatment_deadline = Column(DateTime)
    treatment_status = Column(SQLEnum(TreatmentStatus, native_enum=False))
    treatment_cost = Column(Integer)  # In SAR
    
    # Assignment
    risk_owner = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    identified_by = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    
    # Timeline
    identified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_assessed_at = Column(DateTime)
    next_review_date = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Related items
    related_controls = Column(JSON)  # List of control IDs
    related_incidents = Column(JSON)  # List of incident IDs
    
    # Relationships
    owner = relationship("User", foreign_keys=[risk_owner])
    identifier = relationship("User", foreign_keys=[identified_by])


class RiskAssessment(Base):
    """Risk assessment history (NCA ECC-RM-1)"""
    __tablename__ = "risk_assessments"
    
    assessment_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(Uuid(as_uuid=True), ForeignKey('risks.risk_id', ondelete='CASCADE'), nullable=False)
    
    # Assessment
    assessed_by = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Scores at time of assessment
    likelihood = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    
    # Commentary
    notes_en = Column(Text)
    notes_ar = Column(Text)
    changes_since_last_en = Column(Text)
    changes_since_last_ar = Column(Text)
    
    # Relationships
    risk = relationship("Risk", back_populates="assessments")
    assessor = relationship("User", foreign_keys=[assessed_by])


# Add relationship to Risk model
Risk.assessments = relationship("RiskAssessment", back_populates="risk", cascade="all, delete-orphan")


class ThirdPartyRisk(Base):
    """Third-party vendor risk (NCA ECC-RM-3)"""
    __tablename__ = "third_party_risks"
    
    vendor_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_name = Column(String(255), nullable=False)
    vendor_type = Column(String(100), nullable=False)  # cloud_provider, software_vendor, consultant
    
    # Contact
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Assessment
    risk_rating = Column(String(20), nullable=False)  # low, medium, high, critical
    data_access_level = Column(String(50))  # none, limited, full
    services_provided_en = Column(Text, nullable=False)
    services_provided_ar = Column(Text, nullable=False)
    
    # Compliance
    has_nca_compliance = Column(Boolean, default=False)
    has_iso27001 = Column(Boolean, default=False)
    has_soc2 = Column(Boolean, default=False)
    compliance_certificates = Column(JSON)  # [{type, expiry_date, file_url}]
    
    # Contract
    contract_start_date = Column(DateTime)
    contract_end_date = Column(DateTime)
    contract_value = Column(Integer)  # In SAR
    data_processing_agreement = Column(Boolean, default=False)
    
    # Reviews
    last_review_date = Column(DateTime)
    next_review_date = Column(DateTime)
    review_frequency_days = Column(Integer, default=365)
    
    # Assignment
    vendor_manager = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    manager = relationship("User", foreign_keys=[vendor_manager])

