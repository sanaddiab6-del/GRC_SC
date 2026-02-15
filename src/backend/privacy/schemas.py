"""
Privacy management schemas for PDPL compliance.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from privacy.models import ConsentType, ConsentStatus, DSARType, DSARStatus, DataClassification


class ConsentCreate(BaseModel):
    """Create consent record"""
    consent_type: ConsentType
    purpose_en: str
    purpose_ar: str
    legal_basis_en: Optional[str] = None
    legal_basis_ar: Optional[str] = None
    consent_text_en: Optional[str] = None
    consent_text_ar: Optional[str] = None
    expires_at: Optional[datetime] = None


class ConsentResponse(BaseModel):
    """Consent response"""
    consent_id: UUID
    user_id: UUID
    consent_type: ConsentType
    status: ConsentStatus
    purpose_en: str
    purpose_ar: str
    given_at: datetime
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DSARCreate(BaseModel):
    """Create Data Subject Access Request"""
    request_type: DSARType
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    verification_method: str = Field(..., description="email, phone, or id_document")


class DSARUpdate(BaseModel):
    """Update DSAR (admin only)"""
    status: Optional[DSARStatus] = None
    processor_notes: Optional[str] = None
    response_en: Optional[str] = None
    response_ar: Optional[str] = None
    rejection_reason_en: Optional[str] = None
    rejection_reason_ar: Optional[str] = None


class DSARResponse(BaseModel):
    """DSAR response"""
    request_id: UUID
    user_id: UUID
    request_type: DSARType
    status: DSARStatus
    requested_at: datetime
    due_date: datetime
    completed_at: Optional[datetime]
    verified_at: Optional[datetime]
    response_en: Optional[str]
    response_ar: Optional[str]
    
    class Config:
        from_attributes = True


class DataClassificationCreate(BaseModel):
    """Create data classification tag"""
    resource_type: str = Field(..., description="users, controls, evidence, reports")
    resource_id: str
    classification: DataClassification
    reason_en: Optional[str] = None
    reason_ar: Optional[str] = None


class DataClassificationResponse(BaseModel):
    """Data classification response"""
    tag_id: UUID
    resource_type: str
    resource_id: str
    classification: DataClassification
    classified_by: UUID
    classified_at: datetime
    
    class Config:
        from_attributes = True


class DataBreachCreate(BaseModel):
    """Report data breach"""
    discovered_at: datetime
    breach_type: str = Field(..., description="unauthorized_access, data_loss, ransomware, etc.")
    severity: str = Field(..., description="low, medium, high, critical")
    affected_records_count: int = 0
    affected_data_types: List[str] = []
    impact_description_en: str
    impact_description_ar: str
    containment_actions_en: Optional[str] = None
    containment_actions_ar: Optional[str] = None


class DataBreachResponse(BaseModel):
    """Data breach response"""
    incident_id: UUID
    incident_number: str
    discovered_at: datetime
    breach_type: str
    severity: str
    affected_records_count: int
    status: str
    sdaia_notified_at: Optional[datetime]
    users_notified_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RetentionPolicyCreate(BaseModel):
    """Create retention policy"""
    resource_type: str
    retention_period_days: int = Field(..., gt=0)
    legal_basis_en: str
    legal_basis_ar: str
    auto_delete_enabled: bool = True
    deletion_method: str = Field(default="soft_delete", description="soft_delete, hard_delete, anonymize")


class RetentionPolicyResponse(BaseModel):
    """Retention policy response"""
    policy_id: UUID
    resource_type: str
    retention_period_days: int
    legal_basis_en: str
    auto_delete_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PIACreate(BaseModel):
    """Create Privacy Impact Assessment"""
    project_name_en: str
    project_name_ar: str
    description_en: str
    description_ar: str
    data_types: List[str]
    processing_purpose_en: str
    processing_purpose_ar: str
    legal_basis_en: str
    legal_basis_ar: str
    privacy_risks: Optional[List[dict]] = []
    mitigation_measures_en: Optional[str] = None
    mitigation_measures_ar: Optional[str] = None


class PIAResponse(BaseModel):
    """PIA response"""
    pia_id: UUID
    project_name_en: str
    project_name_ar: str
    status: str
    risk_level: Optional[str]
    conducted_by: UUID
    conducted_at: datetime
    approved_at: Optional[datetime]
    
    class Config:
        from_attributes = True
