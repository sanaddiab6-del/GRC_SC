"""
Evidence Module - Models
Manages audit evidence collection and validation
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from core.database import Base


class EvidenceStatus(str, enum.Enum):
    """Evidence collection status"""
    PENDING = "pending"
    COLLECTED = "collected"
    VALIDATED = "validated"
    REJECTED = "rejected"
    EXPIRED = "expired"


class EvidenceType(str, enum.Enum):
    """Types of evidence"""
    POLICY = "policy"
    PROCEDURE = "procedure"
    LOG = "log"
    SCREENSHOT = "screenshot"
    REPORT = "report"
    CERTIFICATE = "certificate"
    OTHER = "other"


class Evidence(Base):
    """
    Evidence Model - Tracks compliance evidence
    Linked to controls for audit readiness
    """
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Link to control
    control_id = Column(String(50), ForeignKey("controls.control_id"), nullable=False)
    
    # Evidence metadata
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    status = Column(Enum(EvidenceStatus), default=EvidenceStatus.PENDING)
    
    # Bilingual fields
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text)
    description_ar = Column(Text)
    
    # File information
    file_path = Column(String(1000))
    file_name = Column(String(500))
    file_size = Column(Integer)  # in bytes
    file_format = Column(String(50))  # PDF, DOCX, etc.
    
    # Validation
    validated_by = Column(String(200))
    validated_at = Column(DateTime)
    validation_notes = Column(Text)
    
    # Retention
    collection_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    retention_period_days = Column(Integer, default=2555)  # 7 years default
    
    # Additional metadata
    additional_metadata = Column(JSONB)  # Additional flexible data (renamed from 'metadata' to avoid SQLAlchemy conflict)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(200))
    
    def __repr__(self):
        return f"<Evidence {self.evidence_id}: {self.title_en}>"

