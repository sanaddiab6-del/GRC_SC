"""
Reporting schemas for API validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ReportRequest(BaseModel):
    """Schema for requesting a report"""
    report_type: str = Field(json_schema_extra={"example": "compliance_summary"})
    framework_filter: Optional[List[str]] = ["ECC", "CCC", "PDPL"]
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    file_format: str = "json"
    generated_by: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    report_id: str
    report_type: str
    status: str
    title_en: str
    title_ar: str
    framework_filter: Optional[List[str]]
    report_data: Optional[Dict[str, Any]]
    file_path: Optional[str]
    generated_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ComplianceSummary(BaseModel):
    """Compliance summary data"""
    total_controls: int
    compliant: int
    non_compliant: int
    in_progress: int
    not_started: int
    not_applicable: int
    compliance_rate: float
    by_framework: Dict[str, Dict[str, int]]


class ControlPosture(BaseModel):
    """Control posture by domain"""
    domain: str
    total_controls: int
    maturity_average: float
    status_breakdown: Dict[str, int]


class DashboardData(BaseModel):
    """Executive dashboard data"""
    total_controls: int = 0
    compliance_summary: ComplianceSummary
    control_posture: List[ControlPosture]
    recent_evidence: int
    pending_validations: int
    high_priority_gaps: List[Dict[str, str]]
    frameworks: List[str]


class ReportTemplateBase(BaseModel):
    template_key: str
    name: str
    entity_type: Optional[str] = None
    query_config: Optional[Dict[str, Any]] = None
    export_format: str = "pdf"


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    template_key: Optional[str] = None
    name: Optional[str] = None
    entity_type: Optional[str] = None
    query_config: Optional[Dict[str, Any]] = None
    export_format: Optional[str] = None


class ReportTemplateResponse(ReportTemplateBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
