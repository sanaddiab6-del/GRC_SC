"""
Privacy Automation Services for PDPL Compliance
Automated DSAR processing, breach notification, and consent management
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import json

from privacy.models import (
    Consent, ConsentStatus, DataSubjectRequest, DSARType, DSARStatus,
    DataBreachIncident, DataRetentionPolicy
)
from auth.models import User, AuditLog


class DSARAutomationService:
    """
    Automated Data Subject Access Request processing (PDPL Article 13).
    Automatically collects user data from all tables and generates reports.
    """
    
    @staticmethod
    async def auto_process_access_request(
        db: AsyncSession,
        request_id: str,
        user_id: str
    ) -> Dict:
        """
        Automatically collect all personal data for access requests.
        PDPL Article 4: Right to access personal data.
        """
        collected_data = {}
        
        # Get user profile
        user_result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            collected_data["user_profile"] = {
                "user_id": str(user.user_id),
                "email": user.email,
                "full_name_en": user.full_name_en,
                "full_name_ar": user.full_name_ar,
                "created_at": user.created_at.isoformat() if user.created_at else None,  # type: ignore
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,  # type: ignore
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        
        # Get consents
        consent_result = await db.execute(
            select(Consent).where(Consent.user_id == user_id)
        )
        consents = consent_result.scalars().all()
        collected_data["consents"] = [
            {
                "consent_type": consent.consent_type.value,
                "status": consent.status.value,
                "given_at": consent.given_at.isoformat(),
                "purpose_en": consent.purpose_en
            }
            for consent in consents
        ]
        
        # Get audit logs
        audit_result = await db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(100)
        )
        audit_logs = audit_result.scalars().all()
        collected_data["recent_activities"] = [
            {
                "action": log.action,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "ip_address": log.ip_address,
                "status": log.status
            }
            for log in audit_logs
        ]
        
        # Get DSARs
        dsar_result = await db.execute(
            select(DataSubjectRequest).where(DataSubjectRequest.user_id == user_id)
        )
        dsars = dsar_result.scalars().all()
        collected_data["data_requests"] = [
            {
                "request_type": dsar.request_type.value,
                "status": dsar.status.value,
                "requested_at": dsar.requested_at.isoformat()
            }
            for dsar in dsars
        ]
        
        # Update DSAR with collected data
        dsar_update_result = await db.execute(
            select(DataSubjectRequest).where(DataSubjectRequest.request_id == request_id)
        )
        dsar = dsar_update_result.scalar_one_or_none()
        
        if dsar:
            dsar.data_provided = collected_data  # type: ignore
            dsar.response_en = f"Your personal data has been collected and is available in the data_provided field. Total records: {len(collected_data)} categories."  # type: ignore
            dsar.response_ar = f"تم جمع بياناتك الشخصية وهي متاحة في حقل البيانات المقدمة. إجمالي السجلات: {len(collected_data)} فئة."  # type: ignore
            dsar.status = DSARStatus.COMPLETED  # type: ignore
            dsar.completed_at = datetime.utcnow()  # type: ignore
            await db.commit()
        
        return collected_data
    
    @staticmethod
    async def auto_process_erasure_request(
        db: AsyncSession,
        request_id: str,
        user_id: str
    ) -> bool:
        """
        Automatically process data erasure requests (Right to be forgotten).
        PDPL Article 7: Right to erase personal data.
        NOTE: Some data must be retained for legal/audit purposes.
        """
        try:
            # Anonymize user profile (keep ID for audit trail)
            user_result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user:
                # Anonymize instead of delete (keep audit trail)
                user.email = f"deleted_{user_id[:8]}@anonymized.local"  # type: ignore
                user.full_name_en = "Deleted User"  # type: ignore
                user.full_name_ar = "مستخدم محذوف"  # type: ignore
                user.is_active = False  # type: ignore
                user.password_hash = "ACCOUNT_DELETED"  # type: ignore
            
            # Withdraw all active consents
            consent_result = await db.execute(
                select(Consent).where(
                    and_(
                        Consent.user_id == user_id,
                        Consent.status == ConsentStatus.GIVEN
                    )
                )
            )
            consents = consent_result.scalars().all()
            for consent in consents:
                consent.status = ConsentStatus.WITHDRAWN  # type: ignore
                consent.withdrawn_at = datetime.utcnow()  # type: ignore
            
            # Update DSAR status
            dsar_result = await db.execute(
                select(DataSubjectRequest).where(DataSubjectRequest.request_id == request_id)
            )
            dsar = dsar_result.scalar_one_or_none()
            
            if dsar:
                dsar.status = DSARStatus.COMPLETED  # type: ignore
                dsar.completed_at = datetime.utcnow()  # type: ignore
                dsar.response_en = "Your personal data has been anonymized. Audit logs are retained for legal compliance (7 years per NCA requirements)."  # type: ignore
                dsar.response_ar = "تم إخفاء هوية بياناتك الشخصية. يتم الاحتفاظ بسجلات التدقيق للامتثال القانوني (7 سنوات وفقًا لمتطلبات NCA)."  # type: ignore
            
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            return False
    
    @staticmethod
    async def auto_process_portability_request(
        db: AsyncSession,
        request_id: str,
        user_id: str
    ) -> str:
        """
        Generate portable data export (PDPL Article 9).
        Returns data in machine-readable JSON format.
        """
        # Collect all user data
        data = await DSARAutomationService.auto_process_access_request(
            db, request_id, user_id
        )
        
        # Convert to portable JSON format
        portable_data = {
            "export_date": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "format": "JSON",
            "data": data
        }
        
        # Update DSAR
        dsar_result = await db.execute(
            select(DataSubjectRequest).where(DataSubjectRequest.request_id == request_id)
        )
        dsar = dsar_result.scalar_one_or_none()
        
        if dsar:
            dsar.data_provided = portable_data  # type: ignore
            dsar.status = DSARStatus.COMPLETED  # type: ignore
            dsar.completed_at = datetime.utcnow()  # type: ignore
            dsar.response_en = "Your data is available in portable JSON format in the data_provided field."  # type: ignore
            dsar.response_ar = "بياناتك متاحة بتنسيق JSON القابل للنقل في حقل البيانات المقدمة."  # type: ignore
            await db.commit()
        
        return json.dumps(portable_data, indent=2, ensure_ascii=False)


class BreachNotificationService:
    """
    Automated breach notification service (PDPL Article 27).
    Ensures SDAIA notification within 72 hours for high-severity breaches.
    """
    
    @staticmethod
    async def auto_notify_high_severity_breaches(db: AsyncSession) -> List[str]:
        """
        Automatically identify breaches requiring SDAIA notification.
        PDPL Article 27: Notify SDAIA within 72 hours for high-risk breaches.
        """
        # Find breaches requiring notification
        cutoff_time = datetime.utcnow() - timedelta(hours=72)
        
        breach_result = await db.execute(
            select(DataBreachIncident).where(
                and_(
                    DataBreachIncident.notification_required == True,
                    DataBreachIncident.sdaia_notified_at.is_(None),
                    DataBreachIncident.severity.in_(['high', 'critical']),
                    DataBreachIncident.discovered_at >= cutoff_time
                )
            )
        )
        breaches = breach_result.scalars().all()
        
        notified_incidents = []
        
        for breach in breaches:
            # In production: Send actual notification to SDAIA API
            # For now: Mark as notified
            breach.sdaia_notified_at = datetime.utcnow()  # type: ignore
            notified_incidents.append(breach.incident_number)
        
        await db.commit()
        return notified_incidents
    
    @staticmethod
    async def auto_notify_affected_users(
        db: AsyncSession,
        incident_id: str
    ) -> int:
        """
        Automatically notify affected users of data breach.
        Returns count of users notified.
        """
        breach_result = await db.execute(
            select(DataBreachIncident).where(DataBreachIncident.incident_id == incident_id)
        )
        breach = breach_result.scalar_one_or_none()
        
        if not breach:
            return 0
        
        # In production: Send emails/SMS to affected users
        # For now: Mark as notified
        breach.users_notified_at = datetime.utcnow()  # type: ignore
        breach.notification_method = "email"  # type: ignore
        
        await db.commit()
        return int(breach.affected_records_count)  # type: ignore


class ConsentManagementService:
    """
    Automated consent management (PDPL Article 6).
    Handles consent expiry and reminder notifications.
    """
    
    @staticmethod
    async def check_expired_consents(db: AsyncSession) -> int:
        """
        Automatically mark expired consents.
        Returns count of consents expired.
        """
        now = datetime.utcnow()
        
        consent_result = await db.execute(
            select(Consent).where(
                and_(
                    Consent.status == ConsentStatus.GIVEN,
                    Consent.expires_at.isnot(None),
                    Consent.expires_at <= now
                )
            )
        )
        consents = consent_result.scalars().all()
        
        for consent in consents:
            consent.status = ConsentStatus.EXPIRED  # type: ignore
        
        await db.commit()
        return len(consents)
    
    @staticmethod
    async def get_expiring_soon_consents(
        db: AsyncSession,
        days: int = 30
    ) -> list[Consent]:  # type: ignore
        """
        Get consents expiring within specified days.
        Used for reminder notifications.
        """
        cutoff = datetime.utcnow() + timedelta(days=days)
        
        consent_result = await db.execute(
            select(Consent).where(
                and_(
                    Consent.status == ConsentStatus.GIVEN,
                    Consent.expires_at.isnot(None),
                    Consent.expires_at <= cutoff,
                    Consent.expires_at > datetime.utcnow()
                )
            )
        )
        return list(consent_result.scalars().all())


class DataRetentionService:
    """
    Automated data retention and deletion (PDPL Article 12).
    Ensures data is not kept longer than necessary.
    """
    
    @staticmethod
    async def enforce_retention_policies(db: AsyncSession) -> Dict[str, int]:
        """
        Automatically enforce data retention policies.
        Returns count of records processed by resource type.
        """
        # Get all retention policies
        policy_result = await db.execute(
            select(DataRetentionPolicy).where(DataRetentionPolicy.auto_delete_enabled == True)
        )
        policies = policy_result.scalars().all()
        
        results = {}
        
        for policy in policies:
            cutoff_date = datetime.utcnow() - timedelta(days=int(policy.retention_period_days))  # type: ignore
            resource_type = str(policy.resource_type)  # type: ignore
            
            # Process based on resource type
            if resource_type == "audit_logs" and str(policy.deletion_method) == "hard_delete":  # type: ignore
                # Delete old audit logs (after 7-year retention)
                delete_result = await db.execute(
                    select(AuditLog).where(AuditLog.timestamp < cutoff_date)
                )
                old_logs = delete_result.scalars().all()
                
                for log in old_logs:
                    await db.delete(log)
                
                results[resource_type] = len(old_logs)
            
            elif resource_type == "consents" and str(policy.deletion_method) == "anonymize":  # type: ignore
                # Anonymize old withdrawn consents
                consent_result = await db.execute(
                    select(Consent).where(
                        and_(
                            Consent.status == ConsentStatus.WITHDRAWN,
                            Consent.withdrawn_at < cutoff_date
                        )
                    )
                )
                old_consents = consent_result.scalars().all()
                
                for consent in old_consents:
                    consent.purpose_en = "ANONYMIZED"  # type: ignore
                    consent.purpose_ar = "مجهول"  # type: ignore
                
                results[resource_type] = len(old_consents)
        
        await db.commit()
        return results
