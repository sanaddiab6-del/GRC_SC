"""
Tests for Backup and Disaster Recovery module
"""
import pytest
from datetime import datetime, timedelta
from backup.models import BackupJob, RecoveryTest, DisasterRecoveryPlan, BackupType, BackupStatus, RecoveryStatus
from backup.schemas import (
    BackupJobCreate, RecoveryTestCreate, DisasterRecoveryPlanCreate,
    CriticalSystem, RecoveryProcedure, EmergencyContact
)


def test_backup_job_model():
    """Test BackupJob model creation"""
    backup = BackupJob(
        id="BACKUP-20240210-TEST01",
        job_name="Daily PostgreSQL Backup",
        job_name_ar="النسخ الاحتياطي اليومي لقاعدة بيانات PostgreSQL",
        backup_type=BackupType.FULL,
        status=BackupStatus.COMPLETED,
        database_name="sico_grc",
        backup_location="/var/backups/sico/postgresql/backup.sql.gz",
        encrypted=True,
        retention_days=90
    )
    
    assert backup.id == "BACKUP-20240210-TEST01"
    assert backup.backup_type == BackupType.FULL
    assert backup.status == BackupStatus.COMPLETED
    assert backup.encrypted is True


def test_recovery_test_model():
    """Test RecoveryTest model creation"""
    test = RecoveryTest(
        id="RT-20240210-TEST01",
        test_name="Q1 2024 Recovery Test",
        test_name_ar="اختبار الاسترداد للربع الأول 2024",
        backup_job_id="BACKUP-20240210-TEST01",
        test_type="full_recovery",
        status=RecoveryStatus.SCHEDULED,
        rto_target_minutes=240,  # 4 hours
        rpo_target_minutes=60,   # 1 hour
        scheduled_date=datetime.now() + timedelta(days=7)
    )
    
    assert test.id == "RT-20240210-TEST01"
    assert test.rto_target_minutes == 240
    assert test.rpo_target_minutes == 60
    assert test.status == RecoveryStatus.SCHEDULED


def test_disaster_recovery_plan_schema():
    """Test DisasterRecoveryPlan Pydantic schema"""
    critical_system = CriticalSystem(
        system_name="SICO GRC Platform",
        system_name_ar="منصة SICO للحوكمة والمخاطر والامتثال",
        rto_hours=4,
        rpo_hours=1,
        priority=1,
        dependencies=["PostgreSQL", "Redis", "Chroma"]
    )
    
    recovery_proc = RecoveryProcedure(
        step_number=1,
        description="Restore PostgreSQL database from latest backup",
        description_ar="استعادة قاعدة بيانات PostgreSQL من أحدث نسخة احتياطية",
        responsible_role="Database Administrator",
        estimated_duration_minutes=30
    )
    
    emergency_contact = EmergencyContact(
        name="Ahmed Al-Saud",
        role="IT Manager",
        phone="+966501234567",
        email="ahmed@company.sa"
    )
    
    dr_plan = DisasterRecoveryPlanCreate(
        plan_name="SICO GRC DR Plan 2024",
        plan_name_ar="خطة التعافي من الكوارث لـ SICO GRC 2024",
        version="1.0",
        scope="Complete disaster recovery for SICO GRC Platform",
        scope_ar="التعافي الكامل من الكوارث لمنصة SICO GRC",
        overall_rto_hours=8,
        overall_rpo_hours=2,
        critical_systems=[critical_system],
        recovery_procedures=[recovery_proc],
        emergency_contacts=[emergency_contact],
        test_frequency_days=90
    )
    
    assert dr_plan.version == "1.0"
    assert dr_plan.overall_rto_hours == 8
    assert len(dr_plan.critical_systems) == 1
    assert len(dr_plan.recovery_procedures) == 1
    assert len(dr_plan.emergency_contacts) == 1


def test_backup_types():
    """Test backup type enum"""
    assert BackupType.FULL == "full"
    assert BackupType.INCREMENTAL == "incremental"
    assert BackupType.DIFFERENTIAL == "differential"


def test_backup_status_enum():
    """Test backup status enum"""
    assert BackupStatus.PENDING == "pending"
    assert BackupStatus.IN_PROGRESS == "in_progress"
    assert BackupStatus.COMPLETED == "completed"
    assert BackupStatus.FAILED == "failed"
    assert BackupStatus.ARCHIVED == "archived"


def test_recovery_status_enum():
    """Test recovery status enum"""
    assert RecoveryStatus.SCHEDULED == "scheduled"
    assert RecoveryStatus.IN_PROGRESS == "in_progress"
    assert RecoveryStatus.SUCCESSFUL == "successful"
    assert RecoveryStatus.FAILED == "failed"


@pytest.mark.asyncio
async def test_backup_job_creation_api(test_client):
    """Test backup job creation via API (requires auth)"""
    # This would require actual API testing with authentication
    # Placeholder for integration test
    pass
