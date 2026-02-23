"""
Backup Automation Background Tasks
Implements automated backup scheduling (NCA ECC-BC-1 requirement)
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backup.service import BackupService
from core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Initialize scheduler
backup_scheduler = AsyncIOScheduler()
backup_service = BackupService()


async def daily_postgresql_backup():
    """
    Daily PostgreSQL backup (runs at 2 AM)
    NCA requirement: Daily backups with 90-day retention
    """
    logger.info("Starting scheduled PostgreSQL backup...")
    
    try:
        async with AsyncSessionLocal() as db:
            backup_job = await backup_service.create_postgresql_backup(
                db=db,
                backup_name=f"Daily PostgreSQL Backup - {datetime.now().strftime('%Y-%m-%d')}",
                backup_name_ar=f"النسخ الاحتياطي اليومي لـ PostgreSQL - {datetime.now().strftime('%Y-%m-%d')}",
                created_by="system"
            )
            
            logger.info(f"PostgreSQL backup scheduled: {backup_job.id}")
            
    except Exception as e:
        logger.error(f"PostgreSQL backup failed: {e}")


async def weekly_chroma_backup():
    """
    Weekly Chroma vector database backup (runs every Sunday at 3 AM)
    """
    logger.info("Starting scheduled Chroma backup...")
    
    try:
        async with AsyncSessionLocal() as db:
            backup_job = await backup_service.create_chroma_backup(
                db=db,
                backup_name=f"Weekly Chroma Backup - {datetime.now().strftime('%Y-%m-%d')}",
                backup_name_ar=f"النسخ الاحتياطي الأسبوعي لـ Chroma - {datetime.now().strftime('%Y-%m-%d')}",
                created_by="system"
            )
            
            logger.info(f"Chroma backup scheduled: {backup_job.id}")
            
    except Exception as e:
        logger.error(f"Chroma backup failed: {e}")


async def cleanup_expired_backups_task():
    """
    Weekly cleanup of expired backups (runs every Monday at 4 AM)
    NCA requirement: 90-day retention enforcement
    """
    logger.info("Starting backup cleanup task...")
    
    try:
        async with AsyncSessionLocal() as db:
            deleted_count = await backup_service.cleanup_expired_backups(db)
            logger.info(f"Backup cleanup completed: {deleted_count} backups archived")
            
    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")


# Schedule backup tasks
def initialize_backup_automation():
    """Initialize all backup automation tasks"""
    
    # Daily PostgreSQL backup at 2:00 AM (NCA requirement)
    backup_scheduler.add_job(
        daily_postgresql_backup,
        CronTrigger(hour=2, minute=0),
        id='daily_postgresql_backup',
        name='Daily PostgreSQL Backup',
        replace_existing=True
    )
    logger.info("✓ Scheduled: Daily PostgreSQL backup at 2:00 AM")
    
    # Weekly Chroma backup every Sunday at 3:00 AM
    backup_scheduler.add_job(
        weekly_chroma_backup,
        CronTrigger(day_of_week='sun', hour=3, minute=0),
        id='weekly_chroma_backup',
        name='Weekly Chroma Vector DB Backup',
        replace_existing=True
    )
    logger.info("✓ Scheduled: Weekly Chroma backup every Sunday at 3:00 AM")
    
    # Weekly backup cleanup every Monday at 4:00 AM
    backup_scheduler.add_job(
        cleanup_expired_backups_task,
        CronTrigger(day_of_week='mon', hour=4, minute=0),
        id='cleanup_expired_backups',
        name='Weekly Backup Cleanup',
        replace_existing=True
    )
    logger.info("✓ Scheduled: Weekly backup cleanup every Monday at 4:00 AM")
    
    logger.info("✓ Backup automation initialized (NCA ECC-BC-1 compliant)")


# Start scheduler when module is imported
# Note: Scheduler is explicitly managed in main.py lifespan for better control
if __name__ == "__main__":
    # Only auto-start if run directly (for testing)
    if not backup_scheduler.running:
        backup_scheduler.start()
        initialize_backup_automation()
