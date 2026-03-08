"""
Risk Management Pydantic schemas.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .models import RiskCategory, RiskStatus, TreatmentStatus


# Risk schemas
class RiskCreate(BaseModel):
    """Create risk"""
    category: RiskCategory
    title_en: str = Field(..., min_length=5, max_length=255)
    title_ar: str = Field(..., min_length=5, max_length=255)
    description_en: str = Field(..., min_length=10)
    description_ar: str = Field(..., min_length=10)
    likelihood: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    existing_controls_en: Optional[str] = None
    existing_controls_ar: Optional[str] = None
    control_effectiveness: Optional[int] = Field(None, ge=1, le=5)
    risk_owner: UUID
    
    @field_validator("likelihood", "impact")
    def validate_score(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Score must be between 1 and 5')
        return v


class RiskUpdate(BaseModel):
    """Update risk"""
    status: Optional[RiskStatus] = None
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)
    control_effectiveness: Optional[int] = Field(None, ge=1, le=5)
    treatment_strategy: Optional[str] = None
    treatment_plan_en: Optional[str] = None
    treatment_plan_ar: Optional[str] = None
    treatment_deadline: Optional[datetime] = None
    treatment_status: Optional[TreatmentStatus] = None
    treatment_cost: Optional[int] = None


class RiskResponse(BaseModel):
    """Risk response"""
    risk_id: UUID
    risk_number: str
    category: RiskCategory
    status: RiskStatus
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    likelihood: int
    impact: int
    inherent_risk_score: Optional[int] = None
    inherent_risk_level: Optional[str] = None
    residual_risk_score: Optional[int] = None
    residual_risk_level: Optional[str] = None
    risk_owner: UUID
    identified_by: UUID
    identified_at: datetime
    last_assessed_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Risk assessment schemas
class AssessmentCreate(BaseModel):
    """Create risk assessment"""
    risk_id: UUID
    likelihood: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    notes_en: Optional[str] = None
    notes_ar: Optional[str] = None
    changes_since_last_en: Optional[str] = None
    changes_since_last_ar: Optional[str] = None


class AssessmentResponse(BaseModel):
    """Assessment response"""
    assessment_id: UUID
    risk_id: UUID
    assessed_by: UUID
    assessed_at: datetime
    likelihood: int
    impact: int
    risk_score: int
    risk_level: str
    notes_en: Optional[str] = None
    notes_ar: Optional[str] = None
    
    class Config:
        from_attributes = True


# Third-party risk schemas
class VendorCreate(BaseModel):
    """Create vendor risk assessment"""
    vendor_name: str = Field(..., min_length=2, max_length=255)
    vendor_type: str
    risk_rating: str = Field(..., pattern="^(low|medium|high|critical)$")
    services_provided_en: str = Field(..., min_length=10)
    services_provided_ar: str = Field(..., min_length=10)
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    data_access_level: Optional[str] = None
    has_nca_compliance: bool = False
    has_iso27001: bool = False
    has_soc2: bool = False
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    contract_value: Optional[int] = None
    data_processing_agreement: bool = False


class VendorUpdate(BaseModel):
    """Update vendor"""
    risk_rating: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    has_nca_compliance: Optional[bool] = None
    has_iso27001: Optional[bool] = None
    has_soc2: Optional[bool] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class VendorResponse(BaseModel):
    """Vendor response"""
    vendor_id: UUID
    vendor_name: str
    vendor_type: str
    risk_rating: str
    services_provided_en: str
    services_provided_ar: str
    data_access_level: Optional[str] = None
    has_nca_compliance: bool
    has_iso27001: bool
    has_soc2: bool
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
