"""
Pydantic schemas for Controls API
Request/response validation with bilingual support
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class ControlBase(BaseModel):
    """Base control schema with bilingual fields"""
    control_id: str = Field(json_schema_extra={"example": "ECC-GV-1"})
    framework: str = Field(json_schema_extra={"example": "ECC"})
    domain: str = Field(json_schema_extra={"example": "Governance"})
    
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    
    policy_guidance_en: Optional[str] = None
    policy_guidance_ar: Optional[str] = None
    procedure_guidance_en: Optional[str] = None
    procedure_guidance_ar: Optional[str] = None
    
    priority: Optional[str] = None
    status: Optional[str] = None
    maturity_level: Optional[int] = None
    
    evidence_types: Optional[List[str]] = None
    related_controls: Optional[Dict[str, List[str]]] = None


class ControlCreate(ControlBase):
    """Schema for creating a new control"""
    pass


class ControlUpdate(BaseModel):
    """Schema for updating a control (all fields optional).
    When 'status' is provided, the lifecycle transition rules are enforced.
    """
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    status: Optional[str] = None
    maturity_level: Optional[int] = None
    priority: Optional[str] = None


class ControlResponse(ControlBase):
    """Schema for control responses"""
    id: int
    lifecycle_updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ControlListResponse(BaseModel):
    """Paginated control list response"""
    total: int
    offset: int
    limit: int
    items: List[ControlResponse]
