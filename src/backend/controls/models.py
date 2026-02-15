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
    Enhanced with full regulatory metadata from NCA official documents
    """
    __tablename__ = "controls"
    __table_args__ = {'extend_existing': True}  # Allow redefinition for compatibility
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., 1-1-1, 2-2-P-1
    framework = Column(Enum(FrameworkType), nullable=False, index=True)
    framework_version = Column(String(50))  # e.g., ECC-1:2018, CCC-2:2024
    
    # Hierarchical structure from official NCA docs
    domain = Column(String(200), nullable=False)  # e.g., Cybersecurity Governance
    subdomain = Column(String(300))  # e.g., 1-1 Cybersecurity Strategy
    
    # Official control clause (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    control_clause_en = Column(Text, nullable=False)  # Official control statement
    control_clause_ar = Column(Text, nullable=False)
    description_en = Column(Text)  # Additional context
    description_ar = Column(Text)
    
    # Implementation guidance (bilingual)
    policy_guidance_en = Column(Text)
    policy_guidance_ar = Column(Text)
    procedure_guidance_en = Column(Text)
    procedure_guidance_ar = Column(Text)
    
    # Official evidence requirements
    evidence_examples = Column(Text)  # From ECC Implementation Guide
    
    # Control metadata
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(Enum(ControlStatus), default=ControlStatus.NOT_STARTED)
    maturity_level = Column(Integer, default=1)  # 1-5 scale
    
    # Source tracking (provenance)
    source_pdf = Column(String(200))  # e.g., ecc-en.pdf
    source_page = Column(Integer)  # Page number in source document
    
    # Cross-framework mappings (from official NCA mappings)
    mapping_ecc = Column(String(500))  # Maps to ECC controls
    mapping_ccc = Column(String(500))  # Maps to CCC controls  
    mapping_pdpl = Column(String(500))  # Maps to PDPL articles
    mapping_dcc = Column(String(500))  # Maps to DCC controls
    
    # Relationships and evidence
    evidence_types = Column(JSON)  # List of required evidence types
    related_controls = Column(JSON)  # Additional cross-framework mappings
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Control {self.control_id}: {self.title_en}>"

