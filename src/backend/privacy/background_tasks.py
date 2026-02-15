"""
Background tasks for automated privacy compliance.
Runs consent expiry checks, DSAR processing, breach notifications automatically.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from core.database import AsyncSessionLocal
from privacy.automation import (
    DSARAutomationService,
    BreachNotificationService,
    ConsentManagementService,
    DataRetentionService
)
from privacy.models import DataSubjectRequest, DSARStatus, DSARType

logger = logging.getLogger(__name__)


class PrivacyBackgroundTasks:
    """
    Automated background tasks for privacy compliance.
    Ensures PDPL requirements are met automatically.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def process_pending_dsars(self):
        """
        Auto-process DSARs that can be automated (access, portability).
        Runs every hour.
        """
        async with AsyncSessionLocal() as db:
            try:
                logger.info("🔄 Processing pending DSARs...")
                
                # Get pending access requests
                from sqlalchemy import select, and_
                result = await db.execute(
                    select(DataSubjectRequest).where(
                        and_(
                            DataSubjectRequest.status == DSARStatus.PENDING,
                            DataSubjectRequest.request_type == DSARType.ACCESS
                        )
                    )
                )
                access_requests = result.scalars().all()
                
                for dsar in access_requests:
                    try:
                        await DSARAutomationService.auto_process_access_request(
                            db,
                            str(dsar.request_id),
                            str(dsar.user_id)
                        )
                        logger.info(f"✓ Processed access request {dsar.request_id}")
                    except Exception as e:
                        logger.error(f"✗ Failed to process DSAR {dsar.request_id}: {e}")
                
                # Get pending portability requests
                port_result = await db.execute(
                    select(DataSubjectRequest).where(
                        and_(
                            DataSubjectRequest.status == DSARStatus.PENDING,
                            DataSubjectRequest.request_type == DSARType.PORTABILITY
                        )
                    )
                )
                portability_requests = port_result.scalars().all()
                
                for dsar in portability_requests:
                    try:
                        await DSARAutomationService.auto_process_portability_request(
                            db,
                            str(dsar.request_id),
                            str(dsar.user_id)
                        )
                        logger.info(f"✓ Processed portability request {dsar.request_id}")
                    except Exception as e:
                        logger.error(f"✗ Failed to process DSAR {dsar.request_id}: {e}")
                
                logger.info(f"✓ DSAR processing complete ({len(access_requests) + len(portability_requests)} requests)")
                
            except Exception as e:
                logger.error(f"✗ DSAR processing failed: {e}")
    
    async def check_consent_expiry(self):
        """
        Check and expire outdated consents.
        Runs daily at 2 AM.
        """
        async with AsyncSessionLocal() as db:
            try:
                logger.info("🔄 Checking consent expiry...")
                
                expired_count = await ConsentManagementService.check_expired_consents(db)
                logger.info(f"✓ Expired {expired_count} consents")
                
                # Get expiring soon (30 days)
                expiring = await ConsentManagementService.get_expiring_soon_consents(db, days=30)
                if expiring:
                    logger.info(f"⚠ {len(expiring)} consents expiring within 30 days")
                    # In production: Send reminder emails
                
            except Exception as e:
                logger.error(f"✗ Consent expiry check failed: {e}")
    
    async def notify_high_severity_breaches(self):
        """
        Auto-notify SDAIA of high-severity breaches (PDPL Article 27).
        Runs every 6 hours.
        """
        async with AsyncSessionLocal() as db:
            try:
                logger.info("🔄 Checking breach notifications...")
                
                notified = await BreachNotificationService.auto_notify_high_severity_breaches(db)
                
                if notified:
                    logger.warning(f"📢 Notified SDAIA of {len(notified)} breaches: {notified}")
                else:
                    logger.info("✓ No pending breach notifications")
                
            except Exception as e:
                logger.error(f"✗ Breach notification failed: {e}")
    
    async def enforce_retention_policies(self):
        """
        Automatically enforce data retention policies.
        Runs weekly on Sunday at 3 AM.
        """
        async with AsyncSessionLocal() as db:
            try:
                logger.info("🔄 Enforcing data retention policies...")
                
                results = await DataRetentionService.enforce_retention_policies(db)
                
                for resource_type, count in results.items():
                    logger.info(f"✓ Processed {count} {resource_type} records")
                
                logger.info("✓ Data retention enforcement complete")
                
            except Exception as e:
                logger.error(f"✗ Data retention enforcement failed: {e}")
    
    def start(self):
        """Start all background tasks"""
        # DSAR auto-processing: Every hour
        self.scheduler.add_job(
            self.process_pending_dsars,
            'interval',
            hours=1,
            id='dsar_processing',
            name='Auto-process DSARs',
            replace_existing=True
        )
        
        # Consent expiry check: Daily at 2 AM
        self.scheduler.add_job(
            self.check_consent_expiry,
            'cron',
            hour=2,
            minute=0,
            id='consent_expiry',
            name='Check consent expiry',
            replace_existing=True
        )
        
        # Breach notification: Every 6 hours
        self.scheduler.add_job(
            self.notify_high_severity_breaches,
            'interval',
            hours=6,
            id='breach_notification',
            name='Notify high-severity breaches',
            replace_existing=True
        )
        
        # Data retention: Weekly on Sunday at 3 AM
        self.scheduler.add_job(
            self.enforce_retention_policies,
            'cron',
            day_of_week='sun',
            hour=3,
            minute=0,
            id='data_retention',
            name='Enforce data retention',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✓ Privacy background tasks started")
        logger.info("  - DSAR processing: Every hour")
        logger.info("  - Consent expiry: Daily at 2 AM")
        logger.info("  - Breach notification: Every 6 hours")
        logger.info("  - Data retention: Weekly")
    
    def shutdown(self):
        """Stop all background tasks"""
        self.scheduler.shutdown()
        logger.info("✓ Privacy background tasks stopped")


# Global scheduler instance
privacy_scheduler = PrivacyBackgroundTasks()
