"""
Incident Response Pydantic schemas.
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .models import IncidentSeverity, IncidentStatus, IncidentCategory


# Incident schemas
class IncidentCreate(BaseModel):
    """Create security incident"""
    category: IncidentCategory
    severity: IncidentSeverity
    title_en: str = Field(..., min_length=5, max_length=255)
    title_ar: str = Field(..., min_length=5, max_length=255)
    description_en: str = Field(..., min_length=10)
    description_ar: str = Field(..., min_length=10)
    detected_at: datetime
    affected_systems: Optional[List[Dict[str, Any]]] = None
    affected_users_count: Optional[int] = 0
    immediate_actions_en: Optional[str] = None
    immediate_actions_ar: Optional[str] = None


class IncidentUpdate(BaseModel):
    """Update incident"""
    status: Optional[IncidentStatus] = None
    severity: Optional[IncidentSeverity] = None
    assigned_to: Optional[UUID] = None
    incident_commander: Optional[UUID] = None
    business_impact_en: Optional[str] = None
    business_impact_ar: Optional[str] = None
    financial_impact: Optional[int] = None
    containment_actions_en: Optional[str] = None
    containment_actions_ar: Optional[str] = None
    eradication_actions_en: Optional[str] = None
    eradication_actions_ar: Optional[str] = None
    recovery_actions_en: Optional[str] = None
    recovery_actions_ar: Optional[str] = None
    root_cause_en: Optional[str] = None
    root_cause_ar: Optional[str] = None
    lessons_learned_en: Optional[str] = None
    lessons_learned_ar: Optional[str] = None


class IncidentResponse(BaseModel):
    """Incident response"""
    incident_id: UUID
    incident_number: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    detected_at: datetime
    reported_at: datetime
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    affected_systems: Optional[List[Dict[str, Any]]] = None
    affected_users_count: int
    reported_by: UUID
    assigned_to: Optional[UUID] = None
    incident_commander: Optional[UUID] = None
    nca_reported: bool
    nca_reported_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class IncidentReport(BaseModel):
    """Generate incident report"""
    incident_id: UUID
    report_type: str  # summary, detailed, executive
    include_timeline: bool = True
    include_root_cause: bool = True
    include_lessons_learned: bool = True


# Playbook schemas
class PlaybookCreate(BaseModel):
    """Create incident playbook"""
    name_en: str = Field(..., min_length=5, max_length=255)
    name_ar: str = Field(..., min_length=5, max_length=255)
    category: IncidentCategory
    description_en: str = Field(..., min_length=10)
    description_ar: str = Field(..., min_length=10)
    detection_steps: List[Dict[str, str]]
    containment_steps: List[Dict[str, str]]
    eradication_steps: List[Dict[str, str]]
    recovery_steps: List[Dict[str, str]]
    escalation_criteria_en: Optional[str] = None
    escalation_criteria_ar: Optional[str] = None
    escalation_contacts: Optional[List[Dict[str, str]]] = None


class PlaybookResponse(BaseModel):
    """Playbook response"""
    playbook_id: UUID
    name_en: str
    name_ar: str
    category: IncidentCategory
    description_en: str
    description_ar: str
    detection_steps: List[Dict[str, str]]
    containment_steps: List[Dict[str, str]]
    eradication_steps: List[Dict[str, str]]
    recovery_steps: List[Dict[str, str]]
    created_by: UUID
    created_at: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)
