"""
ISMS Pydantic schemas for request/response validation.
ISO 27001 policy management, asset inventory, and document control.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict

from isms.models import PolicyStatus, PolicyType, DocumentClassification


# ===== ISMS POLICY SCHEMAS =====

class ISMSPolicyCreate(BaseModel):
    policy_type: PolicyType
    title_en: str
    title_ar: str
    purpose_en: str
    purpose_ar: str
    scope_en: str
    scope_ar: str
    policy_statement_en: str
    policy_statement_ar: str
    version: str = "1.0"
    classification: DocumentClassification = DocumentClassification.INTERNAL
    review_frequency_days: int = 365
    effective_date: Optional[datetime] = None
    iso27001_controls: Optional[List[str]] = None
    nca_ecc_controls: Optional[List[str]] = None
    nca_ccc_controls: Optional[List[str]] = None
    pdpl_articles: Optional[List[str]] = None
    nist_csf_functions: Optional[List[str]] = None
    related_controls: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    keywords_en: Optional[str] = None
    keywords_ar: Optional[str] = None


class ISMSPolicyUpdate(BaseModel):
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    purpose_en: Optional[str] = None
    purpose_ar: Optional[str] = None
    scope_en: Optional[str] = None
    scope_ar: Optional[str] = None
    policy_statement_en: Optional[str] = None
    policy_statement_ar: Optional[str] = None
    status: Optional[PolicyStatus] = None
    version: Optional[str] = None
    classification: Optional[DocumentClassification] = None
    effective_date: Optional[datetime] = None
    iso27001_controls: Optional[List[str]] = None
    nca_ecc_controls: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ISMSPolicyResponse(BaseModel):
    policy_id: int
    policy_number: str
    policy_type: PolicyType
    title_en: str
    title_ar: str
    purpose_en: str
    purpose_ar: str
    scope_en: str
    scope_ar: str
    policy_statement_en: str
    policy_statement_ar: str
    version: str
    status: PolicyStatus
    classification: DocumentClassification
    author_id: int
    reviewer_id: Optional[int] = None
    approver_id: Optional[int] = None
    draft_date: datetime
    review_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    review_frequency_days: int
    iso27001_controls: Optional[Any] = None
    nca_ecc_controls: Optional[Any] = None
    nca_ccc_controls: Optional[Any] = None
    pdpl_articles: Optional[Any] = None
    nist_csf_functions: Optional[Any] = None
    related_controls: Optional[Any] = None
    tags: Optional[Any] = None
    keywords_en: Optional[str] = None
    keywords_ar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===== ASSET INVENTORY SCHEMAS =====

class AssetCreate(BaseModel):
    asset_name_en: str
    asset_name_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    asset_type: str
    asset_category: str
    classification: DocumentClassification = DocumentClassification.INTERNAL
    confidentiality_rating: int = 3
    integrity_rating: int = 3
    availability_rating: int = 3
    location: Optional[str] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    software_version: Optional[str] = None
    is_in_scope_iso27001: bool = True
    is_in_scope_pdpl: bool = False
    is_in_scope_ecc: bool = True
    processes_personal_data: bool = False
    tags: Optional[List[str]] = None


class AssetUpdate(BaseModel):
    asset_name_en: Optional[str] = None
    asset_name_ar: Optional[str] = None
    classification: Optional[DocumentClassification] = None
    confidentiality_rating: Optional[int] = None
    integrity_rating: Optional[int] = None
    availability_rating: Optional[int] = None
    risk_score: Optional[int] = None
    is_in_scope_pdpl: Optional[bool] = None
    processes_personal_data: Optional[bool] = None
    tags: Optional[List[str]] = None


class AssetResponse(BaseModel):
    asset_id: int
    asset_number: str
    asset_name_en: str
    asset_name_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    asset_type: str
    asset_category: str
    classification: DocumentClassification
    confidentiality_rating: int
    integrity_rating: int
    availability_rating: int
    owner_id: int
    custodian_id: Optional[int] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    software_version: Optional[str] = None
    is_in_scope_iso27001: bool
    is_in_scope_pdpl: bool
    is_in_scope_ecc: bool
    processes_personal_data: bool
    risk_score: Optional[int] = None
    vulnerabilities_found: int
    tags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
