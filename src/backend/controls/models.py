"""
Controls Module - ECC, CCC, PDPL Control Management
Handles bilingual control framework operations
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, JSON
import enum

from core.database import Base


class FrameworkType(str, enum.Enum):
    """Supported regulatory frameworks"""
    ECC = "ECC"
    CCC = "CCC"
    PDPL = "PDPL"


class ControlStatus(str, enum.Enum):
    """Control implementation status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


class Control(Base):
    """
    Bilingual Control Model
    Supports ECC, CCC, and PDPL frameworks
    """
    __tablename__ = "controls"
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., ECC-GV-1
    framework = Column(Enum(FrameworkType), nullable=False, index=True)
    domain = Column(String(100), nullable=False)  # e.g., Governance, Security
    
    # Bilingual fields
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    
    # Implementation guidance (bilingual)
    policy_guidance_en = Column(Text)
    policy_guidance_ar = Column(Text)
    procedure_guidance_en = Column(Text)
    procedure_guidance_ar = Column(Text)
    
    # Control metadata
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(Enum(ControlStatus), default=ControlStatus.NOT_STARTED)
    maturity_level = Column(Integer, default=1)  # 1-5 scale
    
    # Relationships and mappings
    evidence_types = Column(JSON)  # List of required evidence types
    related_controls = Column(JSON)  # Cross-framework mappings
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Control {self.control_id}: {self.title_en}>"

