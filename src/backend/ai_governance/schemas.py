"""
AI Governance Pydantic schemas.
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .models import ModelType, ModelStatus


# AI Model schemas
class AIModelCreate(BaseModel):
    """Create AI model"""
    model_name: str = Field(..., min_length=2, max_length=255)
    model_version: str = Field(..., max_length=50)
    model_type: ModelType
    description_en: str = Field(..., min_length=10)
    description_ar: str = Field(..., min_length=10)
    use_case_en: str = Field(..., min_length=10)
    use_case_ar: str = Field(..., min_length=10)
    framework: Optional[str] = None
    algorithm: Optional[str] = None
    input_features: Optional[List[Dict[str, str]]] = None
    output_format: Optional[Dict[str, str]] = None
    processes_personal_data: bool = False
    model_owner: UUID


class AIModelUpdate(BaseModel):
    """Update AI model"""
    status: Optional[ModelStatus] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    accuracy: Optional[float] = Field(None, ge=0, le=1)
    precision: Optional[float] = Field(None, ge=0, le=1)
    recall: Optional[float] = Field(None, ge=0, le=1)
    f1_score: Optional[float] = Field(None, ge=0, le=1)
    other_metrics: Optional[Dict[str, float]] = None
    bias_assessment_completed: Optional[bool] = None
    is_explainable: Optional[bool] = None
    explainability_method: Optional[str] = None
    deployment_environment: Optional[str] = None
    api_endpoint: Optional[str] = None
    model_file_path: Optional[str] = None


class AIModelResponse(BaseModel):
    """AI model response"""
    model_id: UUID
    model_name: str
    model_version: str
    model_type: ModelType
    status: ModelStatus
    description_en: str
    description_ar: str
    use_case_en: str
    use_case_ar: str
    framework: Optional[str] = None
    algorithm: Optional[str] = None
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    bias_assessment_completed: bool
    is_explainable: bool
    processes_personal_data: bool
    model_owner: UUID
    created_by: UUID
    created_at: datetime
    deployed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Bias test schemas
class BiasTestCreate(BaseModel):
    """Create bias test"""
    model_id: UUID
    test_name: str = Field(..., min_length=5, max_length=255)
    test_type: str  # demographic_parity, equal_opportunity, calibration
    protected_attribute: str  # gender, age, nationality
    attribute_values: List[str]
    test_dataset_size: int = Field(..., gt=0)
    findings_en: str = Field(..., min_length=10)
    findings_ar: str = Field(..., min_length=10)
    bias_detected: bool
    severity: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    bias_score: Optional[float] = Field(None, ge=0, le=1)
    fairness_metrics: Optional[Dict[str, float]] = None
    recommendations_en: Optional[str] = None
    recommendations_ar: Optional[str] = None
    requires_action: bool = False


class BiasTestResponse(BaseModel):
    """Bias test response"""
    test_id: UUID
    model_id: UUID
    test_name: str
    test_type: str
    protected_attribute: str
    attribute_values: List[str]
    bias_detected: bool
    severity: Optional[str] = None
    bias_score: Optional[float] = None
    fairness_metrics: Optional[Dict[str, float]] = None
    findings_en: str
    findings_ar: str
    recommendations_en: Optional[str] = None
    recommendations_ar: Optional[str] = None
    requires_action: bool
    tested_at: datetime
    tested_by: UUID
    
    model_config = ConfigDict(from_attributes=True)


# Ethics review schemas
class EthicsReviewCreate(BaseModel):
    """Create ethics review"""
    model_id: UUID
    review_type: str = Field(..., pattern="^(initial|periodic|incident_triggered)$")
    principle_human_centric: bool
    principle_transparent: bool
    principle_fair: bool
    principle_accountable: bool
    principle_privacy: bool
    principle_secure: bool
    ethical_concerns_en: Optional[str] = None
    ethical_concerns_ar: Optional[str] = None
    recommendations_en: Optional[str] = None
    recommendations_ar: Optional[str] = None
    approved: bool
    approval_conditions_en: Optional[str] = None
    approval_conditions_ar: Optional[str] = None
    next_review_date: Optional[datetime] = None


class EthicsReviewResponse(BaseModel):
    """Ethics review response"""
    review_id: UUID
    model_id: UUID
    review_date: datetime
    reviewer: UUID
    review_type: str
    principle_human_centric: bool
    principle_transparent: bool
    principle_fair: bool
    principle_accountable: bool
    principle_privacy: bool
    principle_secure: bool
    approved: bool
    next_review_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
