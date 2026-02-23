"""
Backup and Disaster Recovery API Router
Implements NCA ECC-BC-1, ECC-BC-2 requirements
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import uuid

from backup.models import BackupJob, RecoveryTest, DisasterRecoveryPlan, BackupStatus, RecoveryStatus
from backup.schemas import (
    BackupJobCreate, BackupJobResponse, BackupJobUpdate,
    RecoveryTestCreate, RecoveryTestResponse, RecoveryTestUpdate,
    DisasterRecoveryPlanCreate, DisasterRecoveryPlanResponse, DisasterRecoveryPlanUpdate
)
from backup.service import BackupService
from core.database import get_db
from auth.dependencies import require_permission

router = APIRouter(prefix="/api/v1/backup", tags=["Backup & Disaster Recovery"])
backup_service = BackupService()


# Backup Job Endpoints
@router.post("/jobs", response_model=BackupJobResponse, status_code=status.HTTP_201_CREATED)
async def create_backup_job(
    backup_type: str = Query(..., description="postgresql or chroma"),
    backup_name: str = Query(...),
    backup_name_ar: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:create"))
):
    """
    Create a new backup job (PostgreSQL or Chroma)
    Requires: backup:create permission
    """
    if backup_type == "postgresql":
        backup_job = await backup_service.create_postgresql_backup(
            db=db,
            backup_name=backup_name,
            backup_name_ar=backup_name_ar,
            created_by=current_user.get("username")
        )
    elif backup_type == "chroma":
        backup_job = await backup_service.create_chroma_backup(
            db=db,
            backup_name=backup_name,
            backup_name_ar=backup_name_ar,
            created_by=current_user.get("username")
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message_en": "Invalid backup type. Must be 'postgresql' or 'chroma'",
                "message_ar": "نوع النسخ الاحتياطي غير صالح. يجب أن يكون 'postgresql' أو 'chroma'"
            }
        )
    
    return backup_job


@router.get("/jobs", response_model=List[BackupJobResponse])
async def list_backup_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[BackupStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:read"))
):
    """
    List all backup jobs with pagination
    Requires: backup:read permission
    """
    backups = await backup_service.list_backups(
        db=db,
        skip=skip,
        limit=limit,
        status_filter=status_filter
    )
    return backups


@router.get("/jobs/{backup_id}", response_model=BackupJobResponse)
async def get_backup_job(
    backup_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:read"))
):
    """
    Get a specific backup job by ID
    Requires: backup:read permission
    """
    query = select(BackupJob).where(BackupJob.id == backup_id)
    result = await db.execute(query)
    backup = result.scalar_one_or_none()
    
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message_en": "Backup job not found",
                "message_ar": "لم يتم العثور على مهمة النسخ الاحتياطي"
            }
        )
    
    return backup


@router.delete("/jobs/cleanup")
async def cleanup_expired_backups(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:delete"))
):
    """
    Clean up expired backups
    Requires: backup:delete permission
    """
    deleted_count = await backup_service.cleanup_expired_backups(db)
    
    return {
        "message_en": f"Successfully cleaned up {deleted_count} expired backups",
        "message_ar": f"تم تنظيف {deleted_count} نسخة احتياطية منتهية الصلاحية بنجاح",
        "deleted_count": deleted_count
    }


# Recovery Test Endpoints
@router.post("/recovery-tests", response_model=RecoveryTestResponse, status_code=status.HTTP_201_CREATED)
async def create_recovery_test(
    test_data: RecoveryTestCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:test"))
):
    """
    Schedule a disaster recovery test
    Requires: backup:test permission
    """
    # Verify backup job exists
    backup_query = select(BackupJob).where(BackupJob.id == test_data.backup_job_id)
    backup_result = await db.execute(backup_query)
    backup_job = backup_result.scalar_one_or_none()
    
    if not backup_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message_en": "Backup job not found",
                "message_ar": "لم يتم العثور على مهمة النسخ الاحتياطي"
            }
        )
    
    # Create recovery test
    test_id = f"RT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    recovery_test = RecoveryTest(
        id=test_id,
        test_name=test_data.test_name,
        test_name_ar=test_data.test_name_ar,
        backup_job_id=test_data.backup_job_id,
        test_type=test_data.test_type,
        status=RecoveryStatus.SCHEDULED,
        rto_target_minutes=test_data.rto_target_minutes,
        rpo_target_minutes=test_data.rpo_target_minutes,
        scheduled_date=test_data.scheduled_date,
        conducted_by=test_data.conducted_by or current_user.get("username")
    )
    
    db.add(recovery_test)
    await db.commit()
    await db.refresh(recovery_test)
    
    return recovery_test


@router.get("/recovery-tests", response_model=List[RecoveryTestResponse])
async def list_recovery_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:read"))
):
    """
    List all recovery tests
    Requires: backup:read permission
    """
    query = select(RecoveryTest).order_by(RecoveryTest.scheduled_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    tests = result.scalars().all()
    
    return tests


@router.patch("/recovery-tests/{test_id}", response_model=RecoveryTestResponse)
async def update_recovery_test(
    test_id: str,
    update_data: RecoveryTestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("backup:update"))
):
    """
    Update recovery test results
    Requires: backup:update permission
    """
    query = select(RecoveryTest).where(RecoveryTest.id == test_id)
    result = await db.execute(query)
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message_en": "Recovery test not found",
                "message_ar": "لم يتم العثور على اختبار الاسترداد"
            }
        )
    
    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(test, field, value)
    
    await db.commit()
    await db.refresh(test)
    
    return test


# Disaster Recovery Plan Endpoints
@router.post("/dr-plans", response_model=DisasterRecoveryPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_dr_plan(
    plan_data: DisasterRecoveryPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("isms:write"))
):
    """
    Create a disaster recovery plan
    Requires: isms:write permission
    """
    plan_id = f"DRP-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
    
    dr_plan = DisasterRecoveryPlan(
        id=plan_id,
        plan_name=plan_data.plan_name,
        plan_name_ar=plan_data.plan_name_ar,
        version=plan_data.version,
        scope=plan_data.scope,
        scope_ar=plan_data.scope_ar,
        overall_rto_hours=plan_data.overall_rto_hours,
        overall_rpo_hours=plan_data.overall_rpo_hours,
        critical_systems=[system.model_dump() for system in plan_data.critical_systems],
        recovery_procedures=[proc.model_dump() for proc in plan_data.recovery_procedures],
        emergency_contacts=[contact.model_dump() for contact in plan_data.emergency_contacts],
        test_frequency_days=plan_data.test_frequency_days,
        created_by=plan_data.created_by or current_user.get("username")
    )
    
    db.add(dr_plan)
    await db.commit()
    await db.refresh(dr_plan)
    
    return dr_plan


@router.get("/dr-plans", response_model=List[DisasterRecoveryPlanResponse])
async def list_dr_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("isms:read"))
):
    """
    List disaster recovery plans
    Requires: isms:read permission
    """
    query = select(DisasterRecoveryPlan).order_by(DisasterRecoveryPlan.created_at.desc()).offset(skip).limit(limit)
    
    if active_only:
        query = query.where(DisasterRecoveryPlan.active == True)
    
    result = await db.execute(query)
    plans = result.scalars().all()
    
    return plans


@router.get("/dr-plans/{plan_id}", response_model=DisasterRecoveryPlanResponse)
async def get_dr_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("isms:read"))
):
    """
    Get a specific disaster recovery plan
    Requires: isms:read permission
    """
    query = select(DisasterRecoveryPlan).where(DisasterRecoveryPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message_en": "Disaster recovery plan not found",
                "message_ar": "لم يتم العثور على خطة التعافي من الكوارث"
            }
        )
    
    return plan


@router.patch("/dr-plans/{plan_id}/approve", response_model=DisasterRecoveryPlanResponse)
async def approve_dr_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("isms:approve"))
):
    """
    Approve a disaster recovery plan
    Requires: isms:approve permission
    """
    query = select(DisasterRecoveryPlan).where(DisasterRecoveryPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message_en": "Disaster recovery plan not found",
                "message_ar": "لم يتم العثور على خطة التعافي من الكوارث"
            }
        )
    
    plan.approved = True
    plan.approved_by = current_user.get("username")
    plan.approved_at = datetime.now()
    
    await db.commit()
    await db.refresh(plan)
    
    return plan