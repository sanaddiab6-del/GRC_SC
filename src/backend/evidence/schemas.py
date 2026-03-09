"""
Evidence schemas for API validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class EvidenceBase(BaseModel):
    """Base evidence schema"""
    evidence_id: str = Field(json_schema_extra={"example": "EVD-ECC-GV-1-001"})
    control_id: str = Field(json_schema_extra={"example": "ECC-GV-1"})
    evidence_type: str = Field(json_schema_extra={"example": "policy"})
    
    title_en: str
    title_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    
    retention_period_days: int = 2555


class EvidenceCreate(EvidenceBase):
    """Schema for creating evidence"""
    created_by: Optional[str] = None


class EvidenceUpdate(BaseModel):
    """Schema for updating evidence"""
    status: Optional[str] = None
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    validated_by: Optional[str] = None
    validation_notes: Optional[str] = None


class EvidenceResponse(EvidenceBase):
    """Schema for evidence responses"""
    id: int
    status: str
    file_hash: Optional[str] = None
    collection_date: datetime
    expiry_date: Optional[datetime] = None
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceIntegrityResponse(BaseModel):
    """Schema for evidence integrity verification result"""
    evidence_id: str
    has_hash: bool
    integrity_ok: bool
    message_en: str
    message_ar: str


class EvidenceListResponse(BaseModel):
    """Paginated evidence list"""
    total: int
    offset: int
    limit: int
    items: list[EvidenceResponse]


class EvidenceValidationRequest(BaseModel):
    """Schema for validating evidence"""
    validated_by: str
    validation_notes: Optional[str] = None
    approved: bool
