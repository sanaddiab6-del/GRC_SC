"""
Pydantic schemas for Backup and Disaster Recovery
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from backup.models import BackupType, BackupStatus, RecoveryStatus


# Backup Job Schemas
class BackupJobBase(BaseModel):
    """Base schema for backup jobs"""
    job_name: str = Field(min_length=3, max_length=200)
    job_name_ar: str = Field(min_length=3, max_length=200)
    backup_type: BackupType
    database_name: str
    backup_location: str
    encrypted: bool = True
    encryption_algorithm: str = "AES-256"
    retention_days: int = Field(default=90, ge=1, le=3650)  # 1 day to 10 years


class BackupJobCreate(BackupJobBase):
    """Schema for creating a backup job"""
    created_by: Optional[str] = None


class BackupJobUpdate(BaseModel):
    """Schema for updating backup job status"""
    status: Optional[BackupStatus] = None
    backup_size_mb: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    backup_metadata: Optional[Dict[str, Any]] = None


class BackupJobResponse(BackupJobBase):
    """Schema for backup job response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    status: BackupStatus
    backup_size_mb: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    expiry_date: Optional[datetime] = None
    error_message: Optional[str] = None
    backup_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    created_by: Optional[str] = None


# Recovery Test Schemas
class RecoveryTestBase(BaseModel):
    """Base schema for recovery tests"""
    test_name: str = Field(min_length=3, max_length=200)
    test_name_ar: str = Field(min_length=3, max_length=200)
    backup_job_id: str
    test_type: str  # full_recovery, partial_recovery, validation
    rto_target_minutes: int = Field(ge=1)
    rpo_target_minutes: int = Field(ge=1)
    scheduled_date: datetime


class RecoveryTestCreate(RecoveryTestBase):
    """Schema for creating a recovery test"""
    conducted_by: Optional[str] = None


class RecoveryTestUpdate(BaseModel):
    """Schema for updating recovery test"""
    status: Optional[RecoveryStatus] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_recovery_minutes: Optional[int] = None
    rto_met: Optional[bool] = None
    rpo_met: Optional[bool] = None
    success_rate: Optional[float] = Field(None, ge=0, le=100)
    test_findings: Optional[str] = None
    test_findings_ar: Optional[str] = None
    corrective_actions: Optional[str] = None
    corrective_actions_ar: Optional[str] = None


class RecoveryTestResponse(RecoveryTestBase):
    """Schema for recovery test response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    status: RecoveryStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_recovery_minutes: Optional[int] = None
    rto_met: Optional[bool] = None
    rpo_met: Optional[bool] = None
    success_rate: Optional[float] = None
    test_findings: Optional[str] = None
    test_findings_ar: Optional[str] = None
    corrective_actions: Optional[str] = None
    corrective_actions_ar: Optional[str] = None
    created_at: datetime
    conducted_by: Optional[str] = None


# Disaster Recovery Plan Schemas
class CriticalSystem(BaseModel):
    """Schema for critical system definition"""
    system_name: str
    system_name_ar: str
    rto_hours: int
    rpo_hours: int
    priority: int = Field(ge=1, le=5)  # 1 = highest
    dependencies: List[str] = []


class RecoveryProcedure(BaseModel):
    """Schema for recovery procedure"""
    step_number: int
    description: str
    description_ar: str
    responsible_role: str
    estimated_duration_minutes: int


class EmergencyContact(BaseModel):
    """Schema for emergency contact"""
    name: str
    role: str
    phone: str
    email: str
    backup_phone: Optional[str] = None


class DisasterRecoveryPlanBase(BaseModel):
    """Base schema for disaster recovery plans"""
    plan_name: str = Field(min_length=3, max_length=200)
    plan_name_ar: str = Field(min_length=3, max_length=200)
    version: str = Field(pattern=r"^\d+\.\d+$")  # e.g., "1.0", "2.1"
    scope: str
    scope_ar: str
    overall_rto_hours: int = Field(ge=1)
    overall_rpo_hours: int = Field(ge=1)
    critical_systems: List[CriticalSystem]
    recovery_procedures: List[RecoveryProcedure]
    emergency_contacts: List[EmergencyContact]
    test_frequency_days: int = Field(default=90, ge=1)


class DisasterRecoveryPlanCreate(DisasterRecoveryPlanBase):
    """Schema for creating disaster recovery plan"""
    created_by: Optional[str] = None


class DisasterRecoveryPlanUpdate(BaseModel):
    """Schema for updating disaster recovery plan"""
    plan_name: Optional[str] = None
    plan_name_ar: Optional[str] = None
    scope: Optional[str] = None
    scope_ar: Optional[str] = None
    overall_rto_hours: Optional[int] = None
    overall_rpo_hours: Optional[int] = None
    critical_systems: Optional[List[CriticalSystem]] = None
    recovery_procedures: Optional[List[RecoveryProcedure]] = None
    emergency_contacts: Optional[List[EmergencyContact]] = None
    test_frequency_days: Optional[int] = None
    approved: Optional[bool] = None
    approved_by: Optional[str] = None
    active: Optional[bool] = None


class DisasterRecoveryPlanResponse(DisasterRecoveryPlanBase):
    """Schema for disaster recovery plan response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    approved: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    active: bool
    last_tested: Optional[datetime] = None
    next_test_due: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    created_by: Optional[str] = None
