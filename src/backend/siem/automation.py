"""
SIEM Integration and Vulnerability Management Automation
Security event processing, incident creation, and vulnerability remediation tracking
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
import json

from siem.models import (
    SecurityEvent, VulnerabilityScan, VulnerabilityFinding,
    ThreatIntelligence, SecurityEventType, SecurityEventSeverity
)
from incident.models import SecurityIncident, IncidentStatus
from auth.models import User


class SIEMIntegrationService:
    """
    SIEM integration service for security event management and GRC mapping.
    """
    
    @staticmethod
    async def process_security_event(
        db: AsyncSession,
        event_data: Dict
    ) -> str:
        """
        Process incoming security event from SIEM.
        Maps to GRC controls and creates incidents if needed.
        """
        # Create security event
        event = SecurityEvent(
            event_type=event_data.get('event_type'),
            severity=event_data.get('severity'),
            event_timestamp=datetime.fromisoformat(event_data.get('event_timestamp', datetime.utcnow().isoformat())),
            source_system=event_data.get('source_system'),
            source_ip=event_data.get('source_ip'),
            source_hostname=event_data.get('source_hostname'),
            source_user_id=event_data.get('source_user_id'),
            event_name=event_data.get('event_name'),
            event_description=event_data.get('event_description'),
            event_data=event_data.get('raw_data'),
            detection_rule=event_data.get('detection_rule'),
            confidence_score=event_data.get('confidence_score', 0.8),
            false_positive_likelihood=event_data.get('false_positive_likelihood', 0.1)
        )
        
        # Map to GRC controls
        control_mapping = await SIEMIntegrationService._map_event_to_controls(event_data)
        event.affected_controls = control_mapping['controls']  # type: ignore
        event.compliance_impact = control_mapping['compliance_impact']  # type: ignore
        event.risk_score = control_mapping['risk_score']  # type: ignore
        
        # Determine if incident creation is needed
        if event.severity in [SecurityEventSeverity.CRITICAL, SecurityEventSeverity.HIGH]:
            event.requires_investigation = True  # type: ignore
            
            # Auto-create incident for critical events
            if event.severity == SecurityEventSeverity.CRITICAL:  # type: ignore
                incident_id = await SIEMIntegrationService._create_incident_from_event(db, event)  # type: ignore
                event.incident_created = True  # type: ignore
                event.incident_id = incident_id  # type: ignore
        
        # Check threat intelligence
        threat_match = await SIEMIntegrationService._check_threat_intelligence(db, event)
        if threat_match:
            event.threat_intelligence = threat_match  # type: ignore
            event.requires_investigation = True  # type: ignore
        
        # Auto-response for known threats
        auto_response = await SIEMIntegrationService._execute_auto_response(db, event)
        if auto_response:
            event.auto_response_taken = True  # type: ignore
            event.auto_response_action = auto_response  # type: ignore
        
        event.processed_at = datetime.utcnow()  # type: ignore
        
        db.add(event)
        await db.commit()
        await db.refresh(event)
        
        return str(event.event_id)
    
    @staticmethod
    async def _map_event_to_controls(event_data: Dict) -> Dict:
        """
        Map security event to GRC control violations.
        """
        control_mapping = {
            SecurityEventType.AUTHENTICATION_FAILURE: {
                'controls': ['ECC-IS-1', 'ECC-IS-2', 'ISO27001-A.9.4.2'],
                'frameworks': ['ECC', 'ISO27001'],
                'risk_score': 0.6
            },
            SecurityEventType.AUTHORIZATION_VIOLATION: {
                'controls': ['ECC-IS-3', 'ECC-IS-4', 'PDPL-Article-8'],
                'frameworks': ['ECC', 'PDPL'],
                'risk_score': 0.7
            },
            SecurityEventType.DATA_ACCESS: {
                'controls': ['ECC-IS-5', 'PDPL-Article-4', 'ISO27001-A.9.4.1'],
                'frameworks': ['ECC', 'PDPL', 'ISO27001'],
                'risk_score': 0.5
            },
            SecurityEventType.DATA_MODIFICATION: {
                'controls': ['ECC-IS-6', 'PDPL-Article-12', 'ISO27001-A.12.3.1'],
                'frameworks': ['ECC', 'PDPL', 'ISO27001'],
                'risk_score': 0.8
            },
            SecurityEventType.SUSPICIOUS_ACTIVITY: {
                'controls': ['ECC-IS-7', 'ISO27001-A.12.4.1'],
                'frameworks': ['ECC', 'ISO27001'],
                'risk_score': 0.65
            },
            SecurityEventType.MALWARE_DETECTED: {
                'controls': ['ECC-IS-8', 'ISO27001-A.12.2.1'],
                'frameworks': ['ECC', 'ISO27001'],
                'risk_score': 0.9
            },
            SecurityEventType.VULNERABILITY_EXPLOITED: {
                'controls': ['ECC-IS-9', 'ISO27001-A.12.6.1'],
                'frameworks': ['ECC', 'ISO27001'],
                'risk_score': 0.95
            }
        }
        
        event_type = event_data.get('event_type')  # type: ignore
        mapping = control_mapping.get(event_type, {  # type: ignore
            'controls': [],
            'frameworks': [],
            'risk_score': 0.3
        })  # type: ignore
        
        # Adjust risk score based on severity
        severity = event_data.get('severity')  # type: ignore
        severity_multipliers = {
            SecurityEventSeverity.CRITICAL: 1.5,
            SecurityEventSeverity.HIGH: 1.2,
            SecurityEventSeverity.MEDIUM: 1.0,
            SecurityEventSeverity.LOW: 0.7,
            SecurityEventSeverity.INFORMATIONAL: 0.3
        }
        
        risk_score = mapping['risk_score'] * severity_multipliers.get(severity, 1.0)  # type: ignore
        risk_score = min(risk_score, 1.0)  # Cap at 1.0  # type: ignore
        
        return {
            'controls': mapping['controls'],
            'compliance_impact': {fw: 'impact_detected' for fw in mapping['frameworks']},
            'risk_score': risk_score
        }
    
    @staticmethod
    async def _create_incident_from_event(
        db: AsyncSession,
        event: SecurityEvent
    ) -> str:
        """
        Auto-create security incident from critical event.
        """
        # Generate incident number (format: INC-YYYYMMDD-XXXX)
        today = datetime.utcnow().strftime("%Y%m%d")
        count_result = await db.execute(
            select(func.count()).select_from(SecurityIncident).where(
                SecurityIncident.incident_number.like(f"INC-{today}-%")
            )
        )
        count = ((count_result.scalar() or 0) + 1)
        incident_number = f"INC-{today}-{count:04d}"
        
        # Create incident
        incident = SecurityIncident(
            incident_number=incident_number,
            title_en=f"Critical Security Event: {event.event_name}",
            title_ar=f"حدث أمني حرج: {event.event_name}",
            description_en=event.event_description or "Automatically generated from critical security event",
            description_ar=event.event_description or "تم إنشاؤه تلقائيًا من حدث أمني حرج",
            incident_type=str(event.event_type.value) if event.event_type else "unknown",  # type: ignore
            severity=event.severity,  # type: ignore
            status=IncidentStatus.NEW,
            detected_at=event.event_timestamp,  # type: ignore
            reported_at=datetime.utcnow(),
            affected_systems=[event.source_system] if event.source_system else [],  # type: ignore
            violated_controls=event.affected_controls or [],  # type: ignore  
            compliance_violations=event.compliance_impact or {},  # type: ignore
            regulatory_notification_required=event.severity == SecurityEventSeverity.CRITICAL
        )
        
        # Set notification deadline if required (72 hours for PDPL)
        if incident.regulatory_notification_required:  # type: ignore
            incident.regulatory_notification_deadline = datetime.utcnow() + timedelta(hours=72)  # type: ignore
        
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        
        return str(incident.incident_id)
    
    @staticmethod
    async def _check_threat_intelligence(
        db: AsyncSession,
        event: SecurityEvent
    ) -> Optional[Dict]:
        """
        Check event against threat intelligence database.
        """
        if not event.source_ip:  # type: ignore
            return None
        
        # Look for matching threat intelligence
        intel_result = await db.execute(
            select(ThreatIntelligence).where(
                and_(
                    ThreatIntelligence.indicator_value == event.source_ip,
                    ThreatIntelligence.is_active == True,
                    or_(
                        ThreatIntelligence.expires_at.is_(None),
                        ThreatIntelligence.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        intel = intel_result.scalar_one_or_none()
        
        if intel:
            # Update match count
            intel.matched_in_events = int(intel.matched_in_events or 0) + 1  # type: ignore
            intel.last_matched_at = datetime.utcnow()  # type: ignore
            await db.commit()
            
            return {
                'matched': True,
                'threat_type': intel.threat_type,
                'threat_actor': intel.threat_actor,
                'campaign': intel.campaign_name,
                'severity': intel.severity,
                'confidence': float(intel.confidence) if intel.confidence else None,  # type: ignore
                'recommended_action': intel.recommended_action
            }  # type: ignore
        
        return None
    
    @staticmethod
    async def _execute_auto_response(
        db: AsyncSession,
        event: SecurityEvent
    ) -> Optional[str]:
        """
        Execute automated response actions for known threats.
        """
        # Example auto-responses (in production, integrate with firewall/WAF APIs)
        if event.threat_intelligence and event.threat_intelligence.get('recommended_action') == 'block':  # type: ignore
            # In production: Call firewall API to block IP
            return f"auto_blocked_ip_{event.source_ip}"  # type: ignore
        
        # Repeated authentication failures - temporarily lock account
        if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:  # type: ignore
            # Check if this user has multiple recent failures
            recent_failures_result = await db.execute(  # type: ignore
                select(func.count()).select_from(SecurityEvent).where(
                    and_(
                        SecurityEvent.source_user_id == event.source_user_id,
                        SecurityEvent.event_type == SecurityEventType.AUTHENTICATION_FAILURE,
                        SecurityEvent.event_timestamp >= datetime.utcnow() - timedelta(minutes=15)
                    )
                )
            )
            failure_count = (recent_failures_result.scalar() or 0)
            
            if failure_count >= 5:
                # In production: Lock user account temporarily
                return f"auto_locked_account_{event.source_user_id}"
        
        return None
    
    @staticmethod
    async def get_high_priority_incidents(db: AsyncSession) -> List[SecurityIncident]:
        """
        Get high-priority incidents requiring attention.
        """
        result = await db.execute(
            select(SecurityIncident).where(
                and_(
                    SecurityIncident.status.in_([IncidentStatus.NEW, IncidentStatus.INVESTIGATING]),
                    SecurityIncident.severity.in_([SecurityEventSeverity.CRITICAL, SecurityEventSeverity.HIGH])
                )
            ).order_by(SecurityIncident.detected_at.desc())
        )
        
        return list(result.scalars().all())


class VulnerabilityManagementService:
    """
    Automated vulnerability management and remediation tracking.
    """
    
    @staticmethod
    async def process_vulnerability_scan(
        db: AsyncSession,
        scan_data: Dict
    ) -> str:
        """
        Process vulnerability scan results and create findings.
        """
        # Create scan record
        scan = VulnerabilityScan(
            scan_name=scan_data.get('scan_name'),
            scan_type=scan_data.get('scan_type'),
            scanner_tool=scan_data.get('scanner_tool'),
            target_type=scan_data.get('target_type'),
            target_identifier=scan_data.get('target_identifier'),  # type: ignore
            target_environment=scan_data.get('target_environment'),  # type: ignore
            scan_start_time=datetime.fromisoformat(str(scan_data.get('scan_start_time'))),  # type: ignore
            scan_end_time=datetime.fromisoformat(str(scan_data.get('scan_end_time'))) if scan_data.get('scan_end_time') else None,  # type: ignore
            scan_duration_seconds=scan_data.get('scan_duration_seconds'),
            scan_status="completed",
            scan_results_json=scan_data.get('raw_results'),
            scan_initiated_by=scan_data.get('initiated_by')
        )
        
        # Process findings
        findings_data = scan_data.get('findings', [])
        critical_count = high_count = medium_count = low_count = info_count = 0
        
        for finding_data in findings_data:
            severity = finding_data.get('severity', 'low').lower()
            
            if severity == 'critical':
                critical_count += 1
            elif severity == 'high':
                high_count += 1
            elif severity == 'medium':
                medium_count += 1
            elif severity == 'low':
                low_count += 1
            else:
                info_count += 1
            
            # Create finding
            finding = VulnerabilityFinding(
                scan_id=scan.scan_id,
                cve_id=finding_data.get('cve_id'),
                vulnerability_name=finding_data.get('vulnerability_name'),
                description_en=finding_data.get('description'),
                description_ar=finding_data.get('description_ar'),
                severity=severity,
                cvss_score=finding_data.get('cvss_score'),
                cvss_vector=finding_data.get('cvss_vector'),
                affected_asset=finding_data.get('affected_asset'),
                vulnerable_package=finding_data.get('vulnerable_package'),
                installed_version=finding_data.get('installed_version'),
                fixed_version=finding_data.get('fixed_version'),
                exploit_available=finding_data.get('exploit_available', False),
                remediation_en=finding_data.get('remediation'),
                remediation_ar=finding_data.get('remediation_ar'),
                remediation_complexity=finding_data.get('remediation_complexity', 'medium')
            )
            
            # Map to GRC controls
            control_violations = await VulnerabilityManagementService._map_vulnerability_to_controls(
                severity, finding_data.get('vulnerability_type')
            )
            finding.violates_controls = control_violations  # type: ignore
            
            # Set remediation deadline based on severity
            deadline_days = {
                'critical': 7,
                'high': 30,
                'medium': 90,
                'low': 180
            }
            finding.remediation_deadline = datetime.utcnow() + timedelta(days=deadline_days.get(severity, 180))  # type: ignore
            
            db.add(finding)
        
        # Update scan summary
        scan.total_vulnerabilities = len(findings_data)  # type: ignore
        scan.critical_count = critical_count  # type: ignore
        scan.high_count = high_count  # type: ignore
        scan.medium_count = medium_count  # type: ignore
        scan.low_count = low_count  # type: ignore
        scan.info_count = info_count  # type: ignore
        
        # Calculate overall risk score
        risk_score = (critical_count * 10 + high_count * 7 + medium_count * 4 + low_count * 1) / max(len(findings_data), 1)
        scan.overall_risk_score = min(risk_score, 10.0)  # type: ignore
        
        # Determine remediation priority
        if critical_count > 0:
            scan.remediation_priority = "urgent"  # type: ignore
        elif high_count > 5:
            scan.remediation_priority = "high"  # type: ignore
        elif high_count > 0 or medium_count > 10:
            scan.remediation_priority = "medium"  # type: ignore
        else:
            scan.remediation_priority = "low"  # type: ignore
        
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        return str(scan.scan_id)
    
    @staticmethod
    async def _map_vulnerability_to_controls(
        severity: str,
        vuln_type: Optional[str]
    ) -> List[str]:
        """
        Map vulnerability to violated GRC controls.
        """
        # Base controls violated by any vulnerability
        controls = ['ECC-IS-10', 'ISO27001-A.12.6.1']  # Vulnerability management
        
        # Additional controls based on type
        if vuln_type == 'authentication':
            controls.extend(['ECC-IS-1', 'ISO27001-A.9.4.2'])
        elif vuln_type == 'encryption':
            controls.extend(['ECC-IS-5', 'PDPL-Article-20', 'ISO27001-A.10.1.1'])
        elif vuln_type == 'access_control':
            controls.extend(['ECC-IS-3', 'ISO27001-A.9.4.1'])
        elif vuln_type == 'data_protection':
            controls.extend(['PDPL-Article-12', 'ISO27001-A.12.3.1'])
        
        return controls
    
    @staticmethod
    async def get_overdue_vulnerabilities(db: AsyncSession) -> List[VulnerabilityFinding]:
        """
        Get vulnerabilities past their remediation deadline.
        """
        result = await db.execute(
            select(VulnerabilityFinding).where(
                and_(
                    VulnerabilityFinding.remediation_status == "open",
                    VulnerabilityFinding.remediation_deadline < datetime.utcnow()
                )
            ).order_by(VulnerabilityFinding.severity.desc(), VulnerabilityFinding.remediation_deadline.asc())
        )
        
        return list(result.scalars().all())
    
    @staticmethod
    async def get_critical_vulnerabilities_in_production(db: AsyncSession) -> List[VulnerabilityFinding]:
        """
        Get critical vulnerabilities in production environment.
        """
        result = await db.execute(
            select(VulnerabilityFinding).join(VulnerabilityScan).where(
                and_(
                    VulnerabilityScan.target_environment == "production",
                    VulnerabilityFinding.severity == "critical",
                    VulnerabilityFinding.remediation_status == "open",
                    VulnerabilityFinding.false_positive == False
                )
            )
        )
        
        return list(result.scalars().all())
