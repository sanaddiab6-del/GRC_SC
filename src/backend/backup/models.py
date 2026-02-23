"""
Backup and Disaster Recovery Database Models
NCA ECC-BC-1, ECC-BC-2 requirements
"""
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Text, JSON, Boolean, Float
from sqlalchemy.sql import func
import enum
from datetime import datetime

from core.database import Base


class BackupType(str, enum.Enum):
    """Types of backups"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(str, enum.Enum):
    """Backup execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class RecoveryStatus(str, enum.Enum):
    """Recovery test status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"


class BackupJob(Base):
    """
    Backup job tracking
    Implements NCA ECC-BC-1: Backup requirements
    """
    __tablename__ = "backup_jobs"

    id = Column(String, primary_key=True)
    job_name = Column(String, nullable=False, index=True)
    job_name_ar = Column(String, nullable=False)
    backup_type = Column(SQLEnum(BackupType), nullable=False)
    status = Column(SQLEnum(BackupStatus), nullable=False, default=BackupStatus.PENDING)
    
    # Backup details
    database_name = Column(String, nullable=False)
    backup_size_mb = Column(Float, nullable=True)
    backup_location = Column(String, nullable=False)
    
    # Encryption (NCA CCC-SEC-03)
    encrypted = Column(Boolean, default=True, nullable=False)
    encryption_algorithm = Column(String, default="AES-256")
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Retention (NCA: 90-day minimum)
    retention_days = Column(Integer, default=90, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    backup_metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<BackupJob {self.id} - {self.job_name} ({self.status})>"


class RecoveryTest(Base):
    """
    Disaster recovery testing records
    Implements NCA ECC-BC-2: Business continuity requirements
    """
    __tablename__ = "recovery_tests"

    id = Column(String, primary_key=True)
    test_name = Column(String, nullable=False)
    test_name_ar = Column(String, nullable=False)
    
    # Test details
    backup_job_id = Column(String, nullable=False)
    test_type = Column(String, nullable=False)  # full_recovery, partial_recovery, validation
    status = Column(SQLEnum(RecoveryStatus), nullable=False, default=RecoveryStatus.SCHEDULED)
    
    # RTO/RPO tracking (NCA requirements)
    rto_target_minutes = Column(Integer, nullable=False)  # Recovery Time Objective
    rpo_target_minutes = Column(Integer, nullable=False)  # Recovery Point Objective
    actual_recovery_minutes = Column(Integer, nullable=True)
    rto_met = Column(Boolean, nullable=True)
    rpo_met = Column(Boolean, nullable=True)
    
    # Timing
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    success_rate = Column(Float, nullable=True)  # Percentage of data recovered
    test_findings = Column(Text, nullable=True)
    test_findings_ar = Column(Text, nullable=True)
    corrective_actions = Column(Text, nullable=True)
    corrective_actions_ar = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    conducted_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<RecoveryTest {self.id} - {self.test_name} ({self.status})>"


class DisasterRecoveryPlan(Base):
    """
    Disaster Recovery Plan documentation
    Implements NCA ECC-BC-2: Business continuity planning
    """
    __tablename__ = "disaster_recovery_plans"

    id = Column(String, primary_key=True)
    plan_name = Column(String, nullable=False)
    plan_name_ar = Column(String, nullable=False)
    version = Column(String, nullable=False)
    
    # Plan details
    scope = Column(Text, nullable=False)
    scope_ar = Column(Text, nullable=False)
    
    # Recovery objectives
    overall_rto_hours = Column(Integer, nullable=False)  # Organization-wide RTO
    overall_rpo_hours = Column(Integer, nullable=False)  # Organization-wide RPO
    
    # Critical systems
    critical_systems = Column(JSON, nullable=False)  # List of critical system definitions
    
    # Recovery procedures
    recovery_procedures = Column(JSON, nullable=False)  # Step-by-step recovery procedures
    
    # Contact information
    emergency_contacts = Column(JSON, nullable=False)  # Emergency response team contacts
    
    # Testing schedule
    test_frequency_days = Column(Integer, default=90, nullable=False)  # NCA: Quarterly testing
    last_tested = Column(DateTime(timezone=True), nullable=True)
    next_test_due = Column(DateTime(timezone=True), nullable=True)
    
    # Approval
    approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    active = Column(Boolean, default=True, nullable=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<DisasterRecoveryPlan {self.plan_name} v{self.version}>"
        return f"<DisasterRecoveryPlan {self.plan_name} v{self.version}>"
