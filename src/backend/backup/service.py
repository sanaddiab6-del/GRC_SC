"""
Backup and Disaster Recovery Service
Implements automated backup and recovery procedures
"""
import os
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import uuid

from backup.models import BackupJob, RecoveryTest, DisasterRecoveryPlan, BackupType, BackupStatus, RecoveryStatus
from backup.schemas import BackupJobCreate, BackupJobUpdate, RecoveryTestCreate, RecoveryTestUpdate
from core.config import settings

logger = logging.getLogger(__name__)


class BackupService:
    """Service for managing backups and disaster recovery"""
    
    def __init__(self, backup_base_path: str = "/var/backups/sico"):
        self.backup_base_path = backup_base_path
        os.makedirs(backup_base_path, exist_ok=True)
    
    async def create_postgresql_backup(
        self,
        db: AsyncSession,
        backup_name: str,
        backup_name_ar: str,
        backup_type: BackupType = BackupType.FULL,
        created_by: Optional[str] = None
    ) -> BackupJob:
        """
        Create a PostgreSQL database backup
        
        Args:
            db: Database session
            backup_name: Backup name in English
            backup_name_ar: Backup name in Arabic
            backup_type: Type of backup (full, incremental, differential)
            created_by: User creating the backup
            
        Returns:
            BackupJob object
        """
        # Generate backup ID
        backup_id = f"BACKUP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create backup directory for this backup
        backup_dir = os.path.join(self.backup_base_path, f"postgresql/{datetime.now().strftime('%Y-%m')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{backup_id}_{timestamp}.sql.gz")
        
        # Create backup job record
        backup_job = BackupJob(
            id=backup_id,
            job_name=backup_name,
            job_name_ar=backup_name_ar,
            backup_type=backup_type,
            status=BackupStatus.PENDING,
            database_name=settings.POSTGRES_DB,
            backup_location=backup_file,
            encrypted=True,
            encryption_algorithm="AES-256",
            retention_days=90,
            expiry_date=datetime.now() + timedelta(days=90),
            created_by=created_by
        )
        
        db.add(backup_job)
        await db.commit()
        await db.refresh(backup_job)
        
        # Execute backup asynchronously
        asyncio.create_task(self._execute_postgresql_backup(db, backup_job, backup_file))
        
        return backup_job
    
    async def _execute_postgresql_backup(
        self,
        db: AsyncSession,
        backup_job: BackupJob,
        backup_file: str
    ):
        """Execute the actual PostgreSQL backup"""
        try:
            # Update status to in progress
            backup_job.status = BackupStatus.IN_PROGRESS
            backup_job.started_at = datetime.now()
            await db.commit()
            
            # Build pg_dump command
            cmd = [
                "pg_dump",
                "-h", settings.POSTGRES_HOST,
                "-p", str(settings.POSTGRES_PORT),
                "-U", settings.POSTGRES_USER,
                "-d", settings.POSTGRES_DB,
                "-F", "c",  # Custom format for better compression
                "-Z", "9",  # Maximum compression
                "-f", backup_file
            ]
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
            
            # Execute backup
            start_time = datetime.now()
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                # Backup successful
                backup_size = os.path.getsize(backup_file) / (1024 * 1024)  # Convert to MB
                
                backup_job.status = BackupStatus.COMPLETED
                backup_job.completed_at = end_time
                backup_job.duration_seconds = int(duration)
                backup_job.backup_size_mb = round(backup_size, 2)
                backup_job.backup_metadata = {
                    "pg_dump_version": result.stderr.split('\n')[0] if result.stderr else "unknown",
                    "compression_level": 9,
                    "format": "custom"
                }
                
                logger.info(f"Backup {backup_job.id} completed successfully. Size: {backup_size:.2f} MB")
            else:
                # Backup failed
                backup_job.status = BackupStatus.FAILED
                backup_job.completed_at = end_time
                backup_job.duration_seconds = int(duration)
                backup_job.error_message = result.stderr
                
                logger.error(f"Backup {backup_job.id} failed: {result.stderr}")
            
            await db.commit()
            
        except subprocess.TimeoutExpired:
            backup_job.status = BackupStatus.FAILED
            backup_job.error_message = "Backup timed out after 1 hour"
            await db.commit()
            logger.error(f"Backup {backup_job.id} timed out")
            
        except Exception as e:
            backup_job.status = BackupStatus.FAILED
            backup_job.error_message = str(e)
            await db.commit()
            logger.error(f"Backup {backup_job.id} failed with exception: {e}")
    
    async def create_chroma_backup(
        self,
        db: AsyncSession,
        backup_name: str,
        backup_name_ar: str,
        chroma_path: str = "/data/chroma",
        created_by: Optional[str] = None
    ) -> BackupJob:
        """
        Create a Chroma vector database backup
        
        Args:
            db: Database session
            backup_name: Backup name in English
            backup_name_ar: Backup name in Arabic
            chroma_path: Path to Chroma database
            created_by: User creating the backup
            
        Returns:
            BackupJob object
        """
        backup_id = f"CHROMA-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        backup_dir = os.path.join(self.backup_base_path, f"chroma/{datetime.now().strftime('%Y-%m')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{backup_id}_{timestamp}.tar.gz")
        
        backup_job = BackupJob(
            id=backup_id,
            job_name=backup_name,
            job_name_ar=backup_name_ar,
            backup_type=BackupType.FULL,
            status=BackupStatus.PENDING,
            database_name="ChromaDB",
            backup_location=backup_file,
            encrypted=True,
            retention_days=90,
            expiry_date=datetime.now() + timedelta(days=90),
            created_by=created_by
        )
        
        db.add(backup_job)
        await db.commit()
        await db.refresh(backup_job)
        
        asyncio.create_task(self._execute_chroma_backup(db, backup_job, chroma_path, backup_file))
        
        return backup_job
    
    async def _execute_chroma_backup(
        self,
        db: AsyncSession,
        backup_job: BackupJob,
        chroma_path: str,
        backup_file: str
    ):
        """Execute the actual Chroma backup"""
        try:
            backup_job.status = BackupStatus.IN_PROGRESS
            backup_job.started_at = datetime.now()
            await db.commit()
            
            # Create tar.gz of Chroma directory
            start_time = datetime.now()
            cmd = [
                "tar",
                "-czf",
                backup_file,
                "-C", os.path.dirname(chroma_path),
                os.path.basename(chroma_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                backup_size = os.path.getsize(backup_file) / (1024 * 1024)
                
                backup_job.status = BackupStatus.COMPLETED
                backup_job.completed_at = end_time
                backup_job.duration_seconds = int(duration)
                backup_job.backup_size_mb = round(backup_size, 2)
                
                logger.info(f"Chroma backup {backup_job.id} completed. Size: {backup_size:.2f} MB")
            else:
                backup_job.status = BackupStatus.FAILED
                backup_job.error_message = result.stderr
                logger.error(f"Chroma backup {backup_job.id} failed: {result.stderr}")
            
            await db.commit()
            
        except Exception as e:
            backup_job.status = BackupStatus.FAILED
            backup_job.error_message = str(e)
            await db.commit()
            logger.error(f"Chroma backup {backup_job.id} failed: {e}")
    
    async def list_backups(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        status_filter: Optional[BackupStatus] = None
    ) -> List[BackupJob]:
        """List backup jobs with optional filtering"""
        query = select(BackupJob).order_by(BackupJob.created_at.desc()).offset(skip).limit(limit)
        
        if status_filter:
            query = query.where(BackupJob.status == status_filter)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def cleanup_expired_backups(self, db: AsyncSession) -> int:
        """
        Clean up expired backups
        Returns number of backups deleted
        """
        query = select(BackupJob).where(
            BackupJob.expiry_date < datetime.now(),
            BackupJob.status == BackupStatus.COMPLETED
        )
        
        result = await db.execute(query)
        expired_backups = result.scalars().all()
        
        deleted_count = 0
        for backup in expired_backups:
            try:
                # Delete backup file
                if os.path.exists(backup.backup_location):
                    os.remove(backup.backup_location)
                    logger.info(f"Deleted expired backup file: {backup.backup_location}")
                
                # Update status to archived
                backup.status = BackupStatus.ARCHIVED
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Error deleting backup {backup.id}: {e}")
        
        await db.commit()
        return deleted_count