"""
Phase 2.3 Background Tasks - AI Governance & Operations Automation
Automated bias testing, performance monitoring, SIEM integration, and vulnerability management
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from core.database import AsyncSessionLocal
from ai_governance.automation import (
    BiasTestingService,
    ModelPerformanceMonitoringService,
    AIIncidentResponseService
)
from siem.automation import (
    SIEMIntegrationService,
    VulnerabilityManagementService
)

logger = logging.getLogger(__name__)


class Phase23BackgroundTasks:
    """
    Background tasks for AI governance and operations automation.
    Runs bias testing, performance monitoring, SIEM event processing, and vulnerability tracking.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Start all Phase 2.3 automation jobs"""
        logger.info("Starting Phase 2.3 background tasks...")
        
        # AI Bias Testing - Daily at 3 AM
        self.scheduler.add_job(
            self._run_bias_testing,
            'cron',
            hour=3,
            minute=0,
            id='ai_bias_testing',
            name='AI Bias Testing',
            replace_existing=True
        )
        logger.info("Scheduled: AI Bias Testing (daily 3 AM)")
        
        # AI Performance Monitoring - Every 6 hours
        self.scheduler.add_job(
            self._run_performance_monitoring,
            'interval',
            hours=6,
            id='ai_performance_monitoring',
            name='AI Performance Monitoring',
            replace_existing=True
        )
        logger.info("Scheduled: AI Performance Monitoring (every 6 hours)")
        
        # AI Incident Detection - Every hour
        self.scheduler.add_job(
            self._detect_ai_incidents,
            'interval',
            hours=1,
            id='ai_incident_detection',
            name='AI Incident Detection',
            replace_existing=True
        )
        logger.info("Scheduled: AI Incident Detection (hourly)")
        
        # Security Incident Review - Every 2 hours
        self.scheduler.add_job(
            self._review_security_incidents,
            'interval',
            hours=2,
            id='security_incident_review',
            name='Security Incident Review',
            replace_existing=True
        )
        logger.info("Scheduled: Security Incident Review (every 2 hours)")
        
        # Vulnerability Management - Daily at 4 AM
        self.scheduler.add_job(
            self._manage_vulnerabilities,
            'cron',
            hour=4,
            minute=0,
            id='vulnerability_management',
            name='Vulnerability Management',
            replace_existing=True
        )
        logger.info("Scheduled: Vulnerability Management (daily 4 AM)")
        
        # Critical Vulnerability Alerts - Every 30 minutes
        self.scheduler.add_job(
            self._alert_critical_vulnerabilities,
            'interval',
            minutes=30,
            id='critical_vulnerability_alerts',
            name='Critical Vulnerability Alerts',
            replace_existing=True
        )
        logger.info("Scheduled: Critical Vulnerability Alerts (every 30 minutes)")
        
        self.scheduler.start()
        logger.info("✅ Phase 2.3 background tasks started successfully")
    
    def shutdown(self):
        """Gracefully shutdown the scheduler"""
        logger.info("Shutting down Phase 2.3 background tasks...")
        self.scheduler.shutdown(wait=True)
        logger.info("✅ Phase 2.3 background tasks stopped")
    
    async def _run_bias_testing(self):
        """
        Automated bias testing for AI models requiring testing/retesting.
        SDAIA AI Principles - Fairness compliance.
        """
        logger.info("Running automated bias testing...")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get models requiring bias testing
                models = await BiasTestingService.get_models_requiring_testing(db)
                
                logger.info(f"Found {len(models)} models requiring bias testing")
                
                # Note: In production, this would trigger actual bias tests with real data
                # For now, we log the requirement
                for model in models:
                    logger.info(f"  - Model {model.model_name} (ID: {model.model_id}) requires bias testing")
                
                if len(models) > 0:
                    logger.warning(f"⚠️ {len(models)} AI models require bias testing")
                else:
                    logger.info("✅ All AI models are up-to-date with bias testing")
                
            except Exception as e:
                logger.error(f"Error in automated bias testing: {str(e)}")
    
    async def _run_performance_monitoring(self):
        """
        Continuous AI model performance monitoring for drift detection.
        """
        logger.info("Running AI model performance monitoring...")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get models requiring performance monitoring
                models = await ModelPerformanceMonitoringService.get_models_requiring_monitoring(db)
                
                logger.info(f"Found {len(models)} models requiring performance monitoring")
                
                # Note: In production, this would fetch recent predictions and run monitoring
                # For now, we log the requirement
                for model in models:
                    logger.info(f"  - Model {model.model_name} (ID: {model.model_id}) requires monitoring")
                
                if len(models) > 0:
                    logger.warning(f"⚠️ {len(models)} AI models require performance monitoring")
                else:
                    logger.info("✅ All AI models are being monitored regularly")
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {str(e)}")
    
    async def _detect_ai_incidents(self):
        """
        Detect AI-related incidents from bias tests and performance degradation.
        """
        logger.info("Detecting AI-related incidents...")
        
        async with AsyncSessionLocal() as db:
            try:
                incidents = await AIIncidentResponseService.detect_ai_incidents(db)
                
                if len(incidents) > 0:
                    logger.critical(f"🚨 {len(incidents)} AI incidents detected!")
                    for incident in incidents:
                        logger.error(f"  - {incident['type']}: {incident.get('findings', 'No details')}")
                else:
                    logger.info("✅ No AI incidents detected")
                
                return incidents
                
            except Exception as e:
                logger.error(f"Error in AI incident detection: {str(e)}")
                return []
    
    async def _review_security_incidents(self):
        """
        Review high-priority security incidents requiring attention.
        """
        logger.info("Reviewing security incidents...")
        
        async with AsyncSessionLocal() as db:
            try:
                incidents = await SIEMIntegrationService.get_high_priority_incidents(db)
                
                if len(incidents) > 0:
                    logger.warning(f"⚠️ {len(incidents)} high-priority security incidents require attention")
                    for incident in incidents:
                        logger.warning(f"  - {incident.incident_number}: {incident.title_en} (Severity: {incident.severity.value})")  # type: ignore
                else:
                    logger.info("✅ No high-priority security incidents pending")
                
                return incidents
                
            except Exception as e:
                logger.error(f"Error in security incident review: {str(e)}")
                return []
    
    async def _manage_vulnerabilities(self):
        """
        Track overdue vulnerabilities and alert on remediation deadlines.
        """
        logger.info("Managing vulnerability remediation...")
        
        async with AsyncSessionLocal() as db:
            try:
                overdue = await VulnerabilityManagementService.get_overdue_vulnerabilities(db)
                
                if len(overdue) > 0:
                    logger.critical(f"🚨 {len(overdue)} vulnerabilities are past remediation deadline!")
                    
                    # Group by severity
                    by_severity = {}
                    for vuln in overdue:
                        severity = vuln.severity
                        if severity not in by_severity:
                            by_severity[severity] = 0
                        by_severity[severity] += 1
                    
                    for severity, count in by_severity.items():
                        logger.error(f"  - {severity.upper()}: {count} overdue")
                else:
                    logger.info("✅ All vulnerabilities within remediation timeline")
                
            except Exception as e:
                logger.error(f"Error in vulnerability management: {str(e)}")
    
    async def _alert_critical_vulnerabilities(self):
        """
        Alert on critical vulnerabilities in production environment (urgent action required).
        """
        logger.info("Checking for critical vulnerabilities in production...")
        
        async with AsyncSessionLocal() as db:
            try:
                critical_vulns = await VulnerabilityManagementService.get_critical_vulnerabilities_in_production(db)
                
                if len(critical_vulns) > 0:
                    logger.critical(f"🚨 URGENT: {len(critical_vulns)} CRITICAL vulnerabilities in PRODUCTION!")
                    for vuln in critical_vulns[:5]:  # Show first 5
                        logger.critical(f"  - {vuln.cve_id or 'NO-CVE'}: {vuln.vulnerability_name} (CVSS: {vuln.cvss_score})")
                    
                    if len(critical_vulns) > 5:
                        logger.critical(f"  ... and {len(critical_vulns) - 5} more")
                else:
                    logger.info("✅ No critical vulnerabilities in production")
                
            except Exception as e:
                logger.error(f"Error checking critical vulnerabilities: {str(e)}")


# Global scheduler instance
phase23_scheduler = Phase23BackgroundTasks()
