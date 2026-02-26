"""
External Audit Management Database Models

ISO 27001 A.9.3 (Internal audit), ISO 27006 (Certification audit requirements).
NCA ECC-GV-2 (Governance and oversight), PDPL Article 21 (Audits).
Supports audit planning, evidence management, finding tracking, certification management.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Uuid, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from enum import Enum

from core.database import Base


class AuditType(str, Enum):
    """Audit scope and type"""
    INTERNAL = "internal"
    EXTERNAL_CERTIFICATION = "external_certification"
    EXTERNAL_SURVEILLANCE = "external_surveillance"
    EXTERNAL_RECERTIFICATION = "external_recertification"
    REGULATORY = "regulatory"
    THIRD_PARTY = "third_party"
    SOC2_TYPE1 = "soc2_type1"
    SOC2_TYPE2 = "soc2_type2"


class AuditStatus(str, Enum):
    """Audit lifecycle status"""
    PLANNED = "planned"
    IN_PREPARATION = "in_preparation"
    IN_PROGRESS = "in_progress"
    PENDING_RESPONSE = "pending_response"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FindingSeverity(str, Enum):
    """Audit finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OBSERVATION = "observation"
    OPPORTUNITY_FOR_IMPROVEMENT = "opportunity_for_improvement"


class FindingStatus(str, Enum):
    """Finding remediation status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    CLOSED = "closed"
    RISK_ACCEPTED = "risk_accepted"


class EvidenceStatus(str, Enum):
    """Evidence collection status"""
    PENDING = "pending"
    COLLECTED = "collected"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class AuditProgram(Base):
    """
    Annual audit program and planning.
    ISO 27001 Clause 9.2 (Internal audit).
    """
    __tablename__ = "audit_programs"

    program_id = Column(Integer, primary_key=True, index=True)
    program_code = Column(String(50), unique=True, nullable=False)  # Format: AUDIT-{YEAR}-{TYPE}
    
    # Program details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Program scope
    audit_year = Column(Integer, nullable=False)
    audit_type = Column(SQLEnum(AuditType, native_enum=False), nullable=False)
    scope_description_en = Column(Text, nullable=False)
    scope_description_ar = Column(Text, nullable=False)
    
    # Frameworks covered
    iso27001_in_scope = Column(Boolean, nullable=False, default=True)
    iso27017_in_scope = Column(Boolean, nullable=False, default=False)
    iso27018_in_scope = Column(Boolean, nullable=False, default=False)
    iso27701_in_scope = Column(Boolean, nullable=False, default=False)
    nca_ecc_in_scope = Column(Boolean, nullable=False, default=True)
    nca_ccc_in_scope = Column(Boolean, nullable=False, default=True)
    pdpl_in_scope = Column(Boolean, nullable=False, default=True)
    sdaia_ai_in_scope = Column(Boolean, nullable=False, default=False)
    
    # Planning
    planned_start_date = Column(DateTime, nullable=False)
    planned_end_date = Column(DateTime, nullable=False)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    
    # Audit team
    lead_auditor_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"))
    audit_team_ids = Column(JSON, nullable=True)  # List of user IDs
    external_auditor_firm = Column(String(500), nullable=True)
    external_auditor_contact = Column(JSON, nullable=True)  # {name, email, phone}
    
    # Status and results
    status = Column(SQLEnum(AuditStatus, native_enum=False), nullable=False, default=AuditStatus.PLANNED)
    total_findings = Column(Integer, nullable=False, default=0)
    critical_findings = Column(Integer, nullable=False, default=0)
    high_findings = Column(Integer, nullable=False, default=0)
    medium_findings = Column(Integer, nullable=False, default=0)
    low_findings = Column(Integer, nullable=False, default=0)
    observations = Column(Integer, nullable=False, default=0)
    
    # Certification (if applicable)
    certification_body = Column(String(500), nullable=True)
    certificate_number = Column(String(200), nullable=True)
    certificate_issue_date = Column(DateTime, nullable=True)
    certificate_expiry_date = Column(DateTime, nullable=True)
    certification_scope_en = Column(Text, nullable=True)
    certification_scope_ar = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lead_auditor = relationship("User", foreign_keys=[lead_auditor_id])
    engagements = relationship("AuditEngagement", back_populates="program")
    findings = relationship("AuditFinding", back_populates="program")


class AuditEngagement(Base):
    """
    Individual audit engagement/session.
    Represents specific audit activities within a program.
    """
    __tablename__ = "audit_engagements"

    engagement_id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("audit_programs.program_id"), nullable=False)
    engagement_code = Column(String(50), unique=True, nullable=False)  # Format: ENG-{PROGRAM}-{NUMBER}
    
    # Engagement details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    objective_en = Column(Text, nullable=False)
    objective_ar = Column(Text, nullable=False)
    
    # Scope
    control_domain = Column(String(200), nullable=True)  # Specific control domain being audited
    controls_in_scope = Column(JSON, nullable=False)  # List of control IDs
    departments_in_scope = Column(JSON, nullable=True)  # List of departments
    systems_in_scope = Column(JSON, nullable=True)  # List of system/asset IDs
    
    # Schedule
    scheduled_date = Column(DateTime, nullable=False)
    scheduled_duration_hours = Column(Integer, nullable=False)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    # Attendees
    auditor_ids = Column(JSON, nullable=False)  # List of auditor user IDs
    auditee_ids = Column(JSON, nullable=False)  # List of auditee user IDs
    
    # Deliverables
    agenda_en = Column(Text, nullable=True)
    agenda_ar = Column(Text, nullable=True)
    meeting_notes_en = Column(Text, nullable=True)
    meeting_notes_ar = Column(Text, nullable=True)
    
    # Status
    status = Column(SQLEnum(AuditStatus, native_enum=False), nullable=False, default=AuditStatus.PLANNED)
    completion_percentage = Column(Integer, nullable=False, default=0)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = relationship("AuditProgram", back_populates="engagements")
    evidence = relationship("AuditEvidence", back_populates="engagement")


class AuditEvidence(Base):
    """
    Audit evidence collection and management.
    ISO 27001 Clause 9.2.2 (Internal audit program).
    """
    __tablename__ = "audit_evidence"

    evidence_id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("audit_engagements.engagement_id"), nullable=False)
    evidence_reference = Column(String(100), unique=True, nullable=False)  # Format: EVD-{ENG}-{NUMBER}
    
    # Evidence details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Control mapping
    control_id = Column(String(50), nullable=False)  # Control being evidenced
    control_requirement_en = Column(Text, nullable=False)
    control_requirement_ar = Column(Text, nullable=False)
    
    # Evidence type
    evidence_type = Column(String(100), nullable=False)  # "document", "screenshot", "log_export", "interview_notes", "configuration_review", "system_scan"
    evidence_category = Column(String(100), nullable=False)  # "policy", "procedure", "record", "technical", "observation"
    
    # Collection
    requested_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    provided_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    requested_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    submitted_date = Column(DateTime, nullable=True)
    
    # Evidence artifacts
    file_path = Column(String(1000), nullable=True)  # Path to evidence file
    file_url = Column(String(1000), nullable=True)  # URL to external evidence
    file_hash = Column(String(128), nullable=True)  # SHA-256 hash for integrity
    file_size_bytes = Column(Integer, nullable=True)
    
    # Review
    status = Column(SQLEnum(EvidenceStatus, native_enum=False), nullable=False, default=EvidenceStatus.PENDING)
    reviewed_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    reviewed_date = Column(DateTime, nullable=True)
    reviewer_notes_en = Column(Text, nullable=True)
    reviewer_notes_ar = Column(Text, nullable=True)
    
    # Assessment
    adequacy_rating = Column(Integer, nullable=True)  # 1-5 (1=inadequate, 5=excellent)
    completeness_score = Column(Integer, nullable=True)  # 0-100%
    
    # Metadata
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("AuditEngagement", back_populates="evidence")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    provided_by = relationship("User", foreign_keys=[provided_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])


class AuditFinding(Base):
    """
    Audit findings, non-conformities, and observations.
    ISO 27001 Clause 10.1 (Nonconformity and corrective action).
    """
    __tablename__ = "audit_findings"

    finding_id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("audit_programs.program_id"), nullable=False)
    finding_number = Column(String(100), unique=True, nullable=False)  # Format: FIND-{PROGRAM}-{NUMBER}
    
    # Finding details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    evidence_reference_en = Column(Text, nullable=False)
    evidence_reference_ar = Column(Text, nullable=False)
    
    # Classification
    severity = Column(SQLEnum(FindingSeverity, native_enum=False), nullable=False)
    finding_type = Column(String(100), nullable=False)  # "non_conformity_major", "non_conformity_minor", "observation", "opportunity"
    
    # Control mapping
    control_reference = Column(String(50), nullable=False)  # Control ID that failed
    control_requirement_en = Column(Text, nullable=False)
    control_requirement_ar = Column(Text, nullable=False)
    gap_identified_en = Column(Text, nullable=False)
    gap_identified_ar = Column(Text, nullable=False)
    
    # Framework references
    iso27001_clause = Column(String(50), nullable=True)
    nca_ecc_control = Column(String(50), nullable=True)
    nca_ccc_control = Column(String(50), nullable=True)
    pdpl_article = Column(String(50), nullable=True)
    
    # Impact assessment
    risk_rating = Column(String(50), nullable=False)  # "critical", "high", "medium", "low"
    impact_description_en = Column(Text, nullable=True)
    impact_description_ar = Column(Text, nullable=True)
    
    # Remediation
    recommendation_en = Column(Text, nullable=False)
    recommendation_ar = Column(Text, nullable=False)
    owner_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    # Corrective actions
    corrective_action_plan_en = Column(Text, nullable=True)
    corrective_action_plan_ar = Column(Text, nullable=True)
    responsible_person_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    target_closure_date = Column(DateTime, nullable=True)
    actual_closure_date = Column(DateTime, nullable=True)
    
    # Status tracking
    status = Column(SQLEnum(FindingStatus, native_enum=False), nullable=False, default=FindingStatus.OPEN)
    progress_percentage = Column(Integer, nullable=False, default=0)
    
    # Verification
    verification_evidence_en = Column(Text, nullable=True)
    verification_evidence_ar = Column(Text, nullable=True)
    verified_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    verification_date = Column(DateTime, nullable=True)
    verification_notes_en = Column(Text, nullable=True)
    verification_notes_ar = Column(Text, nullable=True)
    
    # Escalation
    escalated = Column(Boolean, nullable=False, default=False)
    escalation_reason_en = Column(Text, nullable=True)
    escalation_reason_ar = Column(Text, nullable=True)
    escalated_to_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    escalation_date = Column(DateTime, nullable=True)
    
    # Metadata
    identified_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = relationship("AuditProgram", back_populates="findings")
    owner = relationship("User", foreign_keys=[owner_id])
    responsible_person = relationship("User", foreign_keys=[responsible_person_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    escalated_to = relationship("User", foreign_keys=[escalated_to_id])
    actions = relationship("CorrectiveAction", back_populates="finding")


class CorrectiveAction(Base):
    """
    Corrective action tracking for audit findings.
    ISO 27001 Clause 10.1 (Nonconformity and corrective action).
    """
    __tablename__ = "corrective_actions"

    action_id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("audit_findings.finding_id"), nullable=False)
    action_number = Column(String(100), unique=True, nullable=False)  # Format: CA-{FINDING}-{NUMBER}
    
    # Action details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    
    # Root cause analysis
    root_cause_en = Column(Text, nullable=False)
    root_cause_ar = Column(Text, nullable=False)
    root_cause_category = Column(String(100), nullable=True)  # "process", "technology", "people", "policy"
    
    # Action plan
    action_steps_en = Column(JSON, nullable=False)  # List of action steps
    action_steps_ar = Column(JSON, nullable=False)
    
    # Responsibility
    owner_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assigned_to_ids = Column(JSON, nullable=True)  # List of user IDs
    
    # Timeline
    planned_start_date = Column(DateTime, nullable=False)
    planned_completion_date = Column(DateTime, nullable=False)
    actual_start_date = Column(DateTime, nullable=True)
    actual_completion_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="planned")  # planned, in_progress, completed, overdue, cancelled
    progress_percentage = Column(Integer, nullable=False, default=0)
    
    # Effectiveness
    effectiveness_verified = Column(Boolean, nullable=False, default=False)
    verification_method_en = Column(Text, nullable=True)
    verification_method_ar = Column(Text, nullable=True)
    verification_date = Column(DateTime, nullable=True)
    verified_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    
    # Updates
    last_update_en = Column(Text, nullable=True)
    last_update_ar = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    finding = relationship("AuditFinding", back_populates="actions")
    owner = relationship("User", foreign_keys=[owner_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])


class CertificationRecord(Base):
    """
    Compliance certification records.
    ISO 27001, ISO 27017, ISO 27018, ISO 27701, NCA certifications.
    """
    __tablename__ = "certification_records"

    certification_id = Column(Integer, primary_key=True, index=True)
    certificate_number = Column(String(200), unique=True, nullable=False)
    
    # Certification details
    certification_standard = Column(String(100), nullable=False)  # "ISO27001", "ISO27017", "ISO27018", "ISO27701", "NCA_ECC", "SOC2_TYPE2"
    certification_body = Column(String(500), nullable=False)
    
    # Scope (bilingual)
    scope_en = Column(Text, nullable=False)
    scope_ar = Column(Text, nullable=False)
    scope_locations = Column(JSON, nullable=True)  # List of certified locations
    scope_exclusions_en = Column(Text, nullable=True)
    scope_exclusions_ar = Column(Text, nullable=True)
    
    # Validity
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    surveillance_due_dates = Column(JSON, nullable=True)  # List of surveillance audit dates
    
    # Status
    status = Column(String(50), nullable=False, default="active")  # active, suspended, withdrawn, expired
    
    # Artifacts
    certificate_file_path = Column(String(1000), nullable=True)
    certificate_url = Column(String(1000), nullable=True)
    audit_report_path = Column(String(1000), nullable=True)
    
    # Related audits
    initial_audit_program_id = Column(Integer, ForeignKey("audit_programs.program_id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    initial_audit = relationship("AuditProgram")
