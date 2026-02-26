"""
Incident Response models for NCA ECC-IS-5 compliance.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class IncidentSeverity(str, enum.Enum):
    """Incident severity levels (NCA ECC)"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    """Incident status"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"


class IncidentCategory(str, enum.Enum):
    """Incident categories (NCA ECC)"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware"
    PHISHING = "phishing"
    DOS_DDOS = "dos_ddos"
    DATA_BREACH = "data_breach"
    INSIDER_THREAT = "insider_threat"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_FAILURE = "system_failure"
    OTHER = "other"


class SecurityIncident(Base):
    """Security incidents (NCA ECC-IS-5)"""
    __tablename__ = "security_incidents"
    
    incident_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_number = Column(String(50), unique=True, nullable=False)  # INC-2026-001
    
    # Classification
    category = Column(SQLEnum(IncidentCategory, native_enum=False), nullable=False)
    severity = Column(SQLEnum(IncidentSeverity, native_enum=False), nullable=False)
    status = Column(SQLEnum(IncidentStatus, native_enum=False), default=IncidentStatus.NEW, nullable=False)
    
    # Description
    title_en = Column(String(255), nullable=False)
    title_ar = Column(String(255), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    
    # Timeline
    detected_at = Column(DateTime, nullable=False)
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    contained_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Impact assessment
    affected_systems = Column(JSON)  # List of affected systems/services
    affected_users_count = Column(Integer, default=0)
    business_impact_en = Column(Text)
    business_impact_ar = Column(Text)
    financial_impact = Column(Integer)  # In SAR
    
    # Response actions
    immediate_actions_en = Column(Text)
    immediate_actions_ar = Column(Text)
    containment_actions_en = Column(Text)
    containment_actions_ar = Column(Text)
    eradication_actions_en = Column(Text)
    eradication_actions_ar = Column(Text)
    recovery_actions_en = Column(Text)
    recovery_actions_ar = Column(Text)
    
    # Root cause analysis
    root_cause_en = Column(Text)
    root_cause_ar = Column(Text)
    lessons_learned_en = Column(Text)
    lessons_learned_ar = Column(Text)
    
    # Regulatory reporting
    nca_reported = Column(Boolean, default=False)
    nca_reported_at = Column(DateTime)
    sdaia_reported = Column(Boolean, default=False)
    sdaia_reported_at = Column(DateTime)
    
    # Team
    reported_by = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    assigned_to = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'))
    incident_commander = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'))
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reported_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    commander = relationship("User", foreign_keys=[incident_commander])


class IncidentPlaybook(Base):
    """Incident response playbooks (NCA ECC-IS-5)"""
    __tablename__ = "incident_playbooks"
    
    playbook_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=False)
    category = Column(SQLEnum(IncidentCategory, native_enum=False), nullable=False)
    
    # Playbook content
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    detection_steps = Column(JSON, nullable=False)  # [{step, description}]
    containment_steps = Column(JSON, nullable=False)
    eradication_steps = Column(JSON, nullable=False)
    recovery_steps = Column(JSON, nullable=False)
    
    # Escalation
    escalation_criteria_en = Column(Text)
    escalation_criteria_ar = Column(Text)
    escalation_contacts = Column(JSON)  # [{role, contact}]
    
    # Metadata
    created_by = Column(Uuid(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

