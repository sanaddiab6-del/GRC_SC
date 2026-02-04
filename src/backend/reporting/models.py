"""
Reporting Module - Models
Executive dashboards and compliance reports
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Enum
from sqlalchemy.dialects.postgresql import JSONB
import enum

from src.backend.core.database import Base


class ReportType(str, enum.Enum):
    """Report types"""
    COMPLIANCE_SUMMARY = "compliance_summary"
    CONTROL_POSTURE = "control_posture"
    EVIDENCE_STATUS = "evidence_status"
    RISK_HEATMAP = "risk_heatmap"
    AUDIT_READINESS = "audit_readiness"
    EXECUTIVE_DASHBOARD = "executive_dashboard"


class ReportStatus(str, enum.Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """
    Report Model - Tracks generated compliance reports
    """
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, index=True, nullable=False)
    
    report_type = Column(Enum(ReportType), nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    
    # Bilingual fields
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    
    # Report parameters
    framework_filter = Column(JSONB)  # List of frameworks included
    date_range_start = Column(DateTime)
    date_range_end = Column(DateTime)
    
    # Report data
    report_data = Column(JSONB)  # Structured report data
    file_path = Column(String(1000))
    file_format = Column(String(50))  # PDF, XLSX, JSON
    
    # Metadata
    generated_by = Column(String(200))
    generated_at = Column(DateTime)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report {self.report_id}: {self.report_type.value}>"
