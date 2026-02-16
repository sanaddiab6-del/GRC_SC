"""
Immutable Audit Logging System
Complies with NCA ECC-IS-5 and 7-year retention requirement
Implements append-only audit trail with cryptographic integrity
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import Base

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Audit event types for compliance tracking"""
    # Authentication Events
    AUTH_LOGIN_SUCCESS = "auth_login_success"
    AUTH_LOGIN_FAILURE = "auth_login_failure"
    AUTH_LOGOUT = "auth_logout"
    AUTH_MFA_ENABLED = "auth_mfa_enabled"
    AUTH_PASSWORD_CHANGE = "auth_password_change"
    
    # Authorization Events
    AUTHZ_ACCESS_GRANTED = "authz_access_granted"
    AUTHZ_ACCESS_DENIED = "authz_access_denied"
    AUTHZ_ROLE_CHANGE = "authz_role_change"
    AUTHZ_PERMISSION_CHANGE = "authz_permission_change"
    
    # Data Access Events
    DATA_READ = "data_read"
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # Privacy Events (PDPL)
    PRIVACY_CONSENT_GRANTED = "privacy_consent_granted"
    PRIVACY_CONSENT_WITHDRAWN = "privacy_consent_withdrawn"
    PRIVACY_DATA_ACCESS_REQUEST = "privacy_data_access_request"
    PRIVACY_DATA_ERASURE_REQUEST = "privacy_data_erasure_request"
    PRIVACY_BREACH_DETECTED = "privacy_breach_detected"
    
    # Security Events
    SECURITY_THREAT_DETECTED = "security_threat_detected"
    SECURITY_INCIDENT_REPORTED = "security_incident_reported"
    SECURITY_CONFIG_CHANGE = "security_config_change"
    SECURITY_ENCRYPTION_KEY_ROTATION = "security_encryption_key_rotation"
    
    # Compliance Events
    COMPLIANCE_CONTROL_UPDATED = "compliance_control_updated"
    COMPLIANCE_EVIDENCE_UPLOADED = "compliance_evidence_uploaded"
    COMPLIANCE_AUDIT_PERFORMED = "compliance_audit_performed"
    COMPLIANCE_REPORT_GENERATED = "compliance_report_generated"


class AuditLog(Base):
    """
    Immutable audit log table
    Implements append-only pattern with cryptographic integrity
    7-year retention per NCA ECC requirements
    """
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}  # Allow redefinition
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    
    # Actor information
    user_id = Column(String(100), nullable=True, index=True)
    username = Column(String(200), nullable=True)
    role = Column(String(100), nullable=True)
    tenant_id = Column(String(100), nullable=True, index=True)
    
    # Action details
    resource_type = Column(String(100), nullable=True, index=True)
    resource_id = Column(String(200), nullable=True, index=True)
    action = Column(String(50), nullable=True)
    
    # Request context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)
    
    # Result
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # Additional data (JSON)
    metadata = Column(JSON, nullable=True)
    
    # Cryptographic integrity
    previous_hash = Column(String(64), nullable=True)  # SHA-256 of previous record
    current_hash = Column(String(64), nullable=False, index=True)  # SHA-256 of this record
    
    # Retention
    retention_until = Column(DateTime, nullable=False)  # 7 years from creation
    is_archived = Column(Boolean, default=False, index=True)


class AuditLogger:
    """
    Centralized audit logging service
    Ensures all security and compliance events are logged immutably
    """
    
    @staticmethod
    async def log_event(
        session: AsyncSession,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        tenant_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Create immutable audit log entry
        Automatically chains with previous entry for integrity
        """
        # Get previous hash for chain
        result = await session.execute(
            select(AuditLog).order_by(AuditLog.id.desc()).limit(1)
        )
        previous_log = result.scalar_one_or_none()
        previous_hash = previous_log.current_hash if previous_log else "genesis"
        
        # Calculate retention date (7 years per NCA)
        retention_until = datetime.utcnow() + timedelta(days=7*365)
        
        # Create log entry
        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            event_type=event_type.value,
            user_id=user_id,
            username=username,
            role=role,
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            success=success,
            error_message=error_message,
            metadata=metadata,
            previous_hash=previous_hash,
            current_hash="",  # Will be calculated
            retention_until=retention_until,
        )
        
        # Calculate current hash
        log_entry.current_hash = AuditLogger._calculate_hash(log_entry)
        
        # Save to database
        session.add(log_entry)
        await session.commit()
        
        logger.info(f"Audit log created: {event_type.value} by {username or 'system'}")
        return log_entry
    
    @staticmethod
    def _calculate_hash(log_entry: AuditLog) -> str:
        """
        Calculate SHA-256 hash of log entry for integrity
        Creates tamper-evident chain
        """
        # Create deterministic string representation
        data = f"{log_entry.timestamp}|{log_entry.event_type}|{log_entry.user_id}|" \
               f"{log_entry.resource_type}|{log_entry.resource_id}|{log_entry.action}|" \
               f"{log_entry.success}|{log_entry.previous_hash}"
        
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    async def verify_integrity(session: AsyncSession, start_id: int = 1) -> bool:
        """
        Verify audit log integrity by checking hash chain
        Returns True if chain is valid, False if tampering detected
        """
        result = await session.execute(
            select(AuditLog).where(AuditLog.id >= start_id).order_by(AuditLog.id)
        )
        logs = result.scalars().all()
        
        previous_hash = "genesis"
        for log in logs:
            # Verify previous hash matches
            if log.previous_hash != previous_hash:
                logger.error(f"Integrity violation at log ID {log.id}: hash chain broken")
                return False
            
            # Verify current hash
            expected_hash = AuditLogger._calculate_hash(log)
            if log.current_hash != expected_hash:
                logger.error(f"Integrity violation at log ID {log.id}: hash mismatch")
                return False
            
            previous_hash = log.current_hash
        
        logger.info(f"Audit log integrity verified: {len(logs)} records checked")
        return True
    
    @staticmethod
    async def export_for_regulator(
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        output_path: str
    ) -> str:
        """
        Export audit logs for regulatory submission
        Generates tamper-evident report with integrity proof
        """
        result = await session.execute(
            select(AuditLog)
            .where(AuditLog.timestamp >= start_date)
            .where(AuditLog.timestamp <= end_date)
            .order_by(AuditLog.timestamp)
        )
        logs = result.scalars().all()
        
        # Generate export
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_records": len(logs),
            "integrity_verified": await AuditLogger.verify_integrity(session),
            "records": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "event_type": log.event_type,
                    "user": log.username,
                    "resource": f"{log.resource_type}/{log.resource_id}",
                    "action": log.action,
                    "success": log.success,
                    "hash": log.current_hash,
                }
                for log in logs
            ]
        }
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Audit logs exported: {output_path}")
        return output_path
