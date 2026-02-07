"""
AI Governance models for SDAIA AI Principles compliance.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Text, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class ModelType(str, enum.Enum):
    """AI model types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    GENERATIVE = "generative"
    RECOMMENDATION = "recommendation"
    OTHER = "other"


class ModelStatus(str, enum.Enum):
    """Model lifecycle status"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class AIModel(Base):
    """AI Model Registry (SDAIA AI Principles)"""
    __tablename__ = "ai_models"
    
    model_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False, unique=True)
    model_version = Column(String(50), nullable=False)
    
    # Classification
    model_type = Column(SQLEnum(ModelType), nullable=False)
    status = Column(SQLEnum(ModelStatus), default=ModelStatus.DEVELOPMENT, nullable=False)
    
    # Description
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    use_case_en = Column(Text, nullable=False)
    use_case_ar = Column(Text, nullable=False)
    
    # Technical details
    framework = Column(String(100))  # tensorflow, pytorch, scikit-learn
    algorithm = Column(String(255))
    input_features = Column(JSONB)  # [{name, type, description}]
    output_format = Column(JSONB)  # {type, description}
    
    # Training data
    training_data_source = Column(String(255))
    training_data_size = Column(Integer)  # number of samples
    training_data_period_start = Column(DateTime)
    training_data_period_end = Column(DateTime)
    data_labeling_method_en = Column(Text)
    data_labeling_method_ar = Column(Text)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    other_metrics = Column(JSONB)  # {metric_name: value}
    
    # Bias and fairness (SDAIA AI Principles)
    bias_assessment_completed = Column(Boolean, default=False)
    bias_assessment_date = Column(DateTime)
    fairness_metrics = Column(JSONB)  # {demographic: {metric: value}}
    known_biases_en = Column(Text)
    known_biases_ar = Column(Text)
    mitigation_strategies_en = Column(Text)
    mitigation_strategies_ar = Column(Text)
    
    # Explainability (SDAIA AI Principles)
    is_explainable = Column(Boolean, default=False)
    explainability_method = Column(String(255))  # SHAP, LIME, attention_maps
    explanation_available = Column(Boolean, default=False)
    
    # Privacy
    processes_personal_data = Column(Boolean, default=False)
    privacy_enhancing_techniques = Column(JSONB)  # [differential_privacy, federated_learning]
    data_minimization_applied = Column(Boolean, default=False)
    
    # Deployment
    deployment_environment = Column(String(100))  # cloud, on_premise, edge
    api_endpoint = Column(String(500))
    model_file_path = Column(String(500))
    deployed_at = Column(DateTime)
    last_updated_at = Column(DateTime)
    
    # Monitoring
    performance_monitoring_enabled = Column(Boolean, default=False)
    drift_detection_enabled = Column(Boolean, default=False)
    last_monitored_at = Column(DateTime)
    
    # Ownership
    model_owner = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", foreign_keys=[model_owner])
    creator = relationship("User", foreign_keys=[created_by])


class BiasTestResult(Base):
    """AI bias testing results (SDAIA AI Principles)"""
    __tablename__ = "bias_test_results"
    
    test_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey('ai_models.model_id', ondelete='CASCADE'), nullable=False)
    
    # Test details
    test_name = Column(String(255), nullable=False)
    test_type = Column(String(100), nullable=False)  # demographic_parity, equal_opportunity, calibration
    tested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tested_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    
    # Protected attributes tested
    protected_attribute = Column(String(100), nullable=False)  # gender, age, nationality
    attribute_values = Column(JSONB)  # [male, female] or [18-25, 26-35]
    
    # Results
    bias_detected = Column(Boolean, nullable=False)
    severity = Column(String(20))  # low, medium, high
    bias_score = Column(Float)  # 0-1 scale
    fairness_metrics = Column(JSONB)  # {metric_name: value}
    
    # Details
    test_dataset_size = Column(Integer)
    findings_en = Column(Text)
    findings_ar = Column(Text)
    recommendations_en = Column(Text)
    recommendations_ar = Column(Text)
    
    # Follow-up
    requires_action = Column(Boolean, default=False)
    action_taken_en = Column(Text)
    action_taken_ar = Column(Text)
    retested = Column(Boolean, default=False)
    retest_date = Column(DateTime)
    
    # Relationships
    model = relationship("AIModel", back_populates="bias_tests")
    tester = relationship("User", foreign_keys=[tested_by])


# Add relationship to AIModel
AIModel.bias_tests = relationship("BiasTestResult", back_populates="model", cascade="all, delete-orphan")


class ModelAudit(Base):
    """AI model audit trail (SDAIA AI Principles)"""
    __tablename__ = "model_audits"
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey('ai_models.model_id', ondelete='CASCADE'), nullable=False)
    
    # Audit event
    event_type = Column(String(100), nullable=False)  # created, updated, deployed, retired
    event_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    
    # Changes
    changes = Column(JSONB)  # {field: {old_value, new_value}}
    reason_en = Column(Text)
    reason_ar = Column(Text)
    
    # Impact assessment
    impact_assessment_en = Column(Text)
    impact_assessment_ar = Column(Text)
    requires_retraining = Column(Boolean, default=False)
    requires_retesting = Column(Boolean, default=False)
    
    # Relationships
    model = relationship("AIModel")
    user = relationship("User", foreign_keys=[performed_by])


class AIEthicsReview(Base):
    """AI ethics review (SDAIA AI Principles)"""
    __tablename__ = "ai_ethics_reviews"
    
    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey('ai_models.model_id', ondelete='CASCADE'), nullable=False)
    
    # Review details
    review_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewer = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    review_type = Column(String(50))  # initial, periodic, incident_triggered
    
    # SDAIA AI Principles assessment
    principle_human_centric = Column(Boolean)  # Human-centric AI
    principle_transparent = Column(Boolean)  # Transparency
    principle_fair = Column(Boolean)  # Fairness
    principle_accountable = Column(Boolean)  # Accountability
    principle_privacy = Column(Boolean)  # Privacy
    principle_secure = Column(Boolean)  # Security
    
    # Findings
    ethical_concerns_en = Column(Text)
    ethical_concerns_ar = Column(Text)
    recommendations_en = Column(Text)
    recommendations_ar = Column(Text)
    
    # Decision
    approved = Column(Boolean, nullable=False)
    approval_conditions_en = Column(Text)
    approval_conditions_ar = Column(Text)
    next_review_date = Column(DateTime)
    
    # Relationships
    model = relationship("AIModel")
    reviewer_user = relationship("User", foreign_keys=[reviewer])
