"""
SIEM Integration models for security event management.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class SecurityEventType(str, enum.Enum):
    """Security event types"""
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_VIOLATION = "authorization_violation"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALWARE_DETECTED = "malware_detected"
    VULNERABILITY_EXPLOITED = "vulnerability_exploited"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_ALERT = "system_alert"


class SecurityEventSeverity(str, enum.Enum):
    """Event severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class IncidentStatus(str, enum.Enum):
    """Incident lifecycle status"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"


class SecurityEvent(Base):
    """Security events from SIEM"""
    __tablename__ = "security_events"
    
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event identification
    event_type = Column(SQLEnum(SecurityEventType), nullable=False)
    severity = Column(SQLEnum(SecurityEventSeverity), nullable=False)
    event_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Source information
    source_system = Column(String(255))  # Which system generated the event
    source_ip = Column(String(45))
    source_hostname = Column(String(255))
    source_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    
    # Event details
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text)
    event_data = Column(JSON)  # Raw event data from SIEM
    
    # Detection
    detection_rule = Column(String(255))  # Which SIEM rule detected this
    confidence_score = Column(Float)  # Detection confidence (0-1)
    false_positive_likelihood = Column(Float)  # Estimated false positive probability
    
    # GRC mapping
    affected_controls = Column(JSON)  # [control_id, control_id]
    compliance_impact = Column(JSON)  # {framework: impact_level}
    risk_score = Column(Float)  # Calculated risk score
    
    # Response
    auto_response_taken = Column(Boolean, default=False)
    auto_response_action = Column(String(255))
    requires_investigation = Column(Boolean, default=False)
    incident_created = Column(Boolean, default=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey('security_incidents.incident_id'))
    
    # Enrichment
    threat_intelligence = Column(JSON)  # External threat intel data
    user_risk_level = Column(String(50))  # high, medium, low
    asset_criticality = Column(String(50))  # critical, important, normal
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    
    # Relationships
    source_user = relationship("User", foreign_keys=[source_user_id])
    incident = relationship("SecurityIncident", foreign_keys=[incident_id])


class SecurityIncident(Base):
    """Security incidents requiring investigation"""
    __tablename__ = "security_incidents"
    
    incident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Incident identification
    incident_number = Column(String(50), unique=True, nullable=False)
    title_en = Column(String(255), nullable=False)
    title_ar = Column(String(255), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    
    # Classification
    incident_type = Column(String(100), nullable=False)  # intrusion, data_breach, malware, insider_threat
    severity = Column(SQLEnum(SecurityEventSeverity), nullable=False)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.NEW, nullable=False)
    
    # Timeline
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    containment_at = Column(DateTime)
    eradication_at = Column(DateTime)
    recovery_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Impact assessment
    affected_systems = Column(JSON)  # [system1, system2]
    affected_users_count = Column(Integer, default=0)
    data_compromised = Column(Boolean, default=False)
    data_types_compromised = Column(JSON)  # [PII, financial, credentials]
    estimated_impact_usd = Column(Float)
    
    # GRC impact
    violated_controls = Column(JSON)  # [control_id, control_id]
    compliance_violations = Column(JSON)  # {framework: [violation1, violation2]}
    regulatory_notification_required = Column(Boolean, default=False)
    regulatory_notification_deadline = Column(DateTime)
    
    # Investigation
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    investigation_notes = Column(Text)
    root_cause_en = Column(Text)
    root_cause_ar = Column(Text)
    attack_vector_en = Column(Text)
    attack_vector_ar = Column(Text)
    
    # Response actions
    containment_actions = Column(JSON)  # [action1, action2]
    eradication_actions = Column(JSON)
    recovery_actions = Column(JSON)
    preventive_measures_en = Column(Text)
    preventive_measures_ar = Column(Text)
    
    # Lessons learned
    lessons_learned_en = Column(Text)
    lessons_learned_ar = Column(Text)
    recommendations_en = Column(Text)
    recommendations_ar = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to])
    events = relationship("SecurityEvent", back_populates="incident")


# Add back_populates to SecurityEvent
SecurityEvent.incident = relationship("SecurityIncident", back_populates="events", foreign_keys=[SecurityEvent.incident_id])


class VulnerabilityScan(Base):
    """Vulnerability scan results"""
    __tablename__ = "vulnerability_scans"
    
    scan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Scan metadata
    scan_name = Column(String(255), nullable=False)
    scan_type = Column(String(100), nullable=False)  # network, application, container, cloud_config
    scanner_tool = Column(String(100))  # nessus, qualys, openvas, trivy
    
    # Scan target
    target_type = Column(String(100))  # host, application, container_image, cloud_account
    target_identifier = Column(String(500))  # IP, URL, image:tag, account_id
    target_environment = Column(String(50))  # production, staging, development
    
    # Scan execution
    scan_start_time = Column(DateTime, nullable=False)
    scan_end_time = Column(DateTime)
    scan_duration_seconds = Column(Integer)
    scan_status = Column(String(50), default="completed")  # running, completed, failed
    
    # Results summary
    total_vulnerabilities = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    
    # Risk assessment
    overall_risk_score = Column(Float)  # CVSS-based aggregated score
    exploitability_score = Column(Float)
    remediation_priority = Column(String(50))  # urgent, high, medium, low
    
    # Compliance mapping
    affected_compliance_controls = Column(JSON)  # {control_id: [vuln_ids]}
    compliance_impact_summary = Column(JSON)  # {framework: impact_description}
    
    # Scan results (detailed)
    scan_results_json = Column(JSON)  # Full scan output
    
    # Tracking
    scan_initiated_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    findings_reviewed = Column(Boolean, default=False)
    remediation_ticket_created = Column(Boolean, default=False)
    ticket_ids = Column(JSON)  # [ticket_id1, ticket_id2]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    initiator = relationship("User", foreign_keys=[scan_initiated_by])
    findings = relationship("VulnerabilityFinding", back_populates="scan", cascade="all, delete-orphan")


class VulnerabilityFinding(Base):
    """Individual vulnerability findings"""
    __tablename__ = "vulnerability_findings"
    
    finding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey('vulnerability_scans.scan_id', ondelete='CASCADE'), nullable=False)
    
    # Vulnerability identification
    cve_id = Column(String(50), index=True)  # CVE-2023-12345
    vulnerability_name = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text)
    
    # Severity and scoring
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, informational
    cvss_score = Column(Float)  # 0.0 - 10.0
    cvss_vector = Column(String(255))  # CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
    
    # Asset information
    affected_asset = Column(String(500))  # hostname, IP, container, function
    asset_owner = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    
    # Vulnerability details
    vulnerable_package = Column(String(255))  # package name if applicable
    installed_version = Column(String(100))
    fixed_version = Column(String(100))
    exploit_available = Column(Boolean, default=False)
    exploit_maturity = Column(String(50))  # functional, proof_of_concept, high
    
    # Impact
    confidentiality_impact = Column(String(20))  # high, low, none
    integrity_impact = Column(String(20))
    availability_impact = Column(String(20))
    business_impact_en = Column(Text)
    business_impact_ar = Column(Text)
    
    # Remediation
    remediation_en = Column(Text)
    remediation_ar = Column(Text)
    remediation_complexity = Column(String(20))  # easy, medium, hard
    remediation_estimated_hours = Column(Float)
    remediation_status = Column(String(50), default="open")  # open, in_progress, resolved, accepted_risk, false_positive
    remediation_deadline = Column(DateTime)
    
    # Compliance mapping
    violates_controls = Column(JSON)  # [control_id1, control_id2]
    compliance_requirements = Column(JSON)  # {framework: requirement_description}
    
    # False positive assessment
    verified = Column(Boolean, default=False)
    false_positive = Column(Boolean, default=False)
    false_positive_reason = Column(Text)
    
    # Timestamps
    first_detected = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_detected = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime)
    reopen_count = Column(Integer, default=0)
    
    # Relationships
    scan = relationship("VulnerabilityScan", back_populates="findings")
    owner = relationship("User", foreign_keys=[asset_owner])


class ThreatIntelligence(Base):
    """Threat intelligence indicators"""
    __tablename__ = "threat_intelligence"
    
    intel_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Indicator details
    indicator_type = Column(String(50), nullable=False)  # ip, domain, url, filehash, email
    indicator_value = Column(String(500), nullable=False, index=True)
    
    # Classification
    threat_type = Column(String(100))  # malware, phishing, c2, exploitation
    threat_actor = Column(String(255))
    campaign_name = Column(String(255))
    
    # Severity
    severity = Column(String(20), nullable=False)
    confidence = Column(Float)  # 0-1 confidence in intelligence
    
    # Source
    intelligence_source = Column(String(255))  # feed name or provider
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    
    # Context
    description_en = Column(Text)
    description_ar = Column(Text)
    tags = Column(JSON)  # [tag1, tag2, tag3]
    
    # Action recommendations
    recommended_action = Column(String(100))  # block, alert, monitor
    is_blocked = Column(Boolean, default=False)
    blocked_at = Column(DateTime)    
    
    # Matching
    matched_in_events = Column(Integer, default=0)  # Count of matching security events
    last_matched_at = Column(DateTime)
    
    # Expiry
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
