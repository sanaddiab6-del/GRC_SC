"""
ISMS (Information Security Management System) Database Models

ISO 27001 compliance: Policy management, document control, ISMS governance.
Supports NCA ECC-GV (Governance), ISO 27001 A.5 (Policies), A.7 (Asset Management).
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Uuid, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from core.database import Base


class PolicyStatus(str, Enum):
    """Policy lifecycle status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REVISION_REQUIRED = "revision_required"
    ARCHIVED = "archived"


class PolicyType(str, Enum):
    """ISO 27001 policy categories"""
    INFORMATION_SECURITY = "information_security"
    ACCESS_CONTROL = "access_control"
    ASSET_MANAGEMENT = "asset_management"
    CRYPTOGRAPHY = "cryptography"
    PHYSICAL_SECURITY = "physical_security"
    OPERATIONS_SECURITY = "operations_security"
    COMMUNICATIONS_SECURITY = "communications_security"
    SYSTEM_ACQUISITION = "system_acquisition"
    SUPPLIER_RELATIONSHIPS = "supplier_relationships"
    INCIDENT_MANAGEMENT = "incident_management"
    BUSINESS_CONTINUITY = "business_continuity"
    COMPLIANCE = "compliance"
    PRIVACY = "privacy"
    CLOUD_SECURITY = "cloud_security"
    AI_GOVERNANCE = "ai_governance"


class DocumentClassification(str, Enum):
    """Document sensitivity classification"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ISMSPolicy(Base):
    """
    ISO 27001 security policies and procedures.
    Maps to ISO 27001:2022 Annex A.5.1 (Policies for information security).
    """
    __tablename__ = "isms_policies"

    policy_id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(50), unique=True, nullable=False)  # Format: POL-{TYPE}-{NUMBER}
    policy_type = Column(SQLEnum(PolicyType, native_enum=False), nullable=False)
    
    # Bilingual content
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    purpose_en = Column(Text, nullable=False)
    purpose_ar = Column(Text, nullable=False)
    scope_en = Column(Text, nullable=False)
    scope_ar = Column(Text, nullable=False)
    policy_statement_en = Column(Text, nullable=False)
    policy_statement_ar = Column(Text, nullable=False)
    
    # Document control
    version = Column(String(20), nullable=False, default="1.0")
    status = Column(SQLEnum(PolicyStatus, native_enum=False), nullable=False, default=PolicyStatus.DRAFT)
    classification = Column(SQLEnum(DocumentClassification, native_enum=False), nullable=False, default=DocumentClassification.INTERNAL)
    
    # Approval workflow
    author_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    reviewer_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    approver_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    
    # Lifecycle dates
    draft_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    review_date = Column(DateTime, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    review_frequency_days = Column(Integer, nullable=False, default=365)  # Annual review by default
    next_review_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Compliance mapping
    iso27001_controls = Column(JSON, nullable=True)  # List of ISO 27001 controls (e.g., ["A.5.1", "A.6.1.1"])
    nca_ecc_controls = Column(JSON, nullable=True)  # List of ECC controls
    nca_ccc_controls = Column(JSON, nullable=True)  # List of CCC controls
    pdpl_articles = Column(JSON, nullable=True)  # List of PDPL articles
    nist_csf_functions = Column(JSON, nullable=True)  # NIST CSF 2.0 functions
    
    # Related documents
    related_procedures = Column(JSON, nullable=True)  # List of procedure IDs
    related_policies = Column(JSON, nullable=True)  # List of related policy IDs
    related_controls = Column(JSON, nullable=True)  # List of control IDs from controls table
    
    # Metadata
    tags = Column(JSON, nullable=True)  # Searchable tags
    keywords_en = Column(Text, nullable=True)
    keywords_ar = Column(Text, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approver_id])
    acknowledgements = relationship("PolicyAcknowledgement", back_populates="policy")
    exceptions = relationship("PolicyException", back_populates="policy")


class PolicyAcknowledgement(Base):
    """
    Employee acknowledgement of policy awareness.
    ISO 27001 A.6.3 (Awareness, education and training).
    """
    __tablename__ = "policy_acknowledgements"

    acknowledgement_id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("isms_policies.policy_id"), nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    policy_version = Column(String(20), nullable=False)
    
    # Acknowledgement details
    acknowledged_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    acknowledgement_method = Column(String(50), nullable=False)  # "online_portal", "email", "training_session"
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Confirmation
    confirmation_text_shown_en = Column(Text, nullable=True)
    confirmation_text_shown_ar = Column(Text, nullable=True)
    user_confirmed = Column(Boolean, nullable=False, default=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    policy = relationship("ISMSPolicy", back_populates="acknowledgements")
    user = relationship("User")


class PolicyException(Base):
    """
    Approved exceptions to security policies.
    ISO 27001 A.5.1.2 (Review of the policies).
    """
    __tablename__ = "policy_exceptions"

    exception_id = Column(Integer, primary_key=True, index=True)
    exception_number = Column(String(50), unique=True, nullable=False)  # Format: EXC-{YYYYMMDD}-{NUMBER}
    policy_id = Column(Integer, ForeignKey("isms_policies.policy_id"), nullable=False)
    
    # Exception details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    justification_en = Column(Text, nullable=False)
    justification_ar = Column(Text, nullable=False)
    compensating_controls_en = Column(Text, nullable=False)
    compensating_controls_ar = Column(Text, nullable=False)
    risk_acceptance_en = Column(Text, nullable=False)
    risk_acceptance_ar = Column(Text, nullable=False)
    
    # Approval
    requested_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    approved_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, approved, rejected, expired
    
    # Validity
    requested_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    approval_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=False)
    review_date = Column(DateTime, nullable=True)
    
    # Risk assessment
    residual_risk_score = Column(Integer, nullable=True)  # 0-100
    risk_owner_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policy = relationship("ISMSPolicy", back_populates="exceptions")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    risk_owner = relationship("User", foreign_keys=[risk_owner_id])


class DocumentVersion(Base):
    """
    Version control for ISMS documents.
    ISO 27001 A.5.13 (Labelling of information).
    """
    __tablename__ = "document_versions"

    version_id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("isms_policies.policy_id"), nullable=False)
    version_number = Column(String(20), nullable=False)
    
    # Change tracking
    change_summary_en = Column(Text, nullable=False)
    change_summary_ar = Column(Text, nullable=False)
    change_type = Column(String(50), nullable=False)  # "minor_update", "major_revision", "emergency_change"
    changed_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    # Document snapshot (full policy content at this version)
    document_content_json = Column(JSON, nullable=False)
    
    # Version lifecycle
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    superseded_at = Column(DateTime, nullable=True)
    
    # Relationships
    policy = relationship("ISMSPolicy")
    changed_by = relationship("User")


class AssetInventory(Base):
    """
    Information asset register.
    ISO 27001 A.5.9 (Inventory of information and other associated assets).
    NCA ECC-AM (Asset Management).
    """
    __tablename__ = "asset_inventory"

    asset_id = Column(Integer, primary_key=True, index=True)
    asset_number = Column(String(50), unique=True, nullable=False)  # Format: ASSET-{TYPE}-{NUMBER}
    
    # Asset identification (bilingual)
    asset_name_en = Column(String(500), nullable=False)
    asset_name_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Asset type
    asset_type = Column(String(100), nullable=False)  # "server", "database", "application", "data_store", "network_device", "endpoint"
    asset_category = Column(String(100), nullable=False)  # "hardware", "software", "data", "service", "people"
    
    # Classification
    classification = Column(SQLEnum(DocumentClassification, native_enum=False), nullable=False, default=DocumentClassification.INTERNAL)
    confidentiality_rating = Column(Integer, nullable=False, default=3)  # 1-5
    integrity_rating = Column(Integer, nullable=False, default=3)  # 1-5
    availability_rating = Column(Integer, nullable=False, default=3)  # 1-5
    
    # Ownership
    owner_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    custodian_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    location = Column(String(500), nullable=True)
    
    # Technical details
    ip_address = Column(String(50), nullable=True)
    hostname = Column(String(200), nullable=True)
    operating_system = Column(String(200), nullable=True)
    software_version = Column(String(100), nullable=True)
    
    # Compliance
    is_in_scope_iso27001 = Column(Boolean, nullable=False, default=True)
    is_in_scope_pdpl = Column(Boolean, nullable=False, default=False)
    is_in_scope_ecc = Column(Boolean, nullable=False, default=True)
    processes_personal_data = Column(Boolean, nullable=False, default=False)
    
    # Lifecycle
    acquisition_date = Column(DateTime, nullable=True)
    last_review_date = Column(DateTime, nullable=True)
    next_review_date = Column(DateTime, nullable=True)
    disposal_date = Column(DateTime, nullable=True)
    
    # Risk
    risk_score = Column(Integer, nullable=True)  # 0-100
    vulnerabilities_found = Column(Integer, nullable=False, default=0)
    
    # Metadata
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    custodian = relationship("User", foreign_keys=[custodian_id])
