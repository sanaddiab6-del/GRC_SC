"""
AI Model Registry - Production-Grade Model Governance
Compliant with ISO 42001, SDAIA AI Principles, NCA ECC
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ModelType(str, Enum):
    """Model architecture types"""
    ENCODER_ONLY = "encoder_only"  # BERT-like for classification/NER
    ENCODER_DECODER = "encoder_decoder"  # T5-like for conditional generation
    DECODER_ONLY = "decoder_only"  # GPT-like (RESTRICTED - requires approval)
    EMBEDDING = "embedding"  # Sentence transformers


class ModelStatus(str, Enum):
    """Model lifecycle status"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    QUARANTINE = "quarantine"  # Security incident


class RiskLevel(str, Enum):
    """AI risk classification per SDAIA"""
    LOW = "low"  # Read-only retrieval
    MEDIUM = "medium"  # Classification/NER
    HIGH = "high"  # Text generation with citations
    CRITICAL = "critical"  # Text generation without constraints (BLOCKED)


class ModelMetadata(BaseModel):
    """Model registration metadata - ISO 42001 compliant"""
    
    # Identity
    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Human-readable name")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version")
    model_type: ModelType
    
    # Architecture
    base_model: str = Field(..., description="Foundation model (e.g., bert-base-multilingual)")
    parameters_count: int = Field(..., gt=0, description="Number of parameters")
    languages: List[str] = Field(..., description="Supported languages (ISO 639-1)")
    
    # Governance
    owner: str = Field(..., description="Team/person responsible")
    risk_level: RiskLevel
    status: ModelStatus = ModelStatus.DEVELOPMENT
    
    # Deployment
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None  # For client adapters
    
    # Artifacts
    artifact_path: str = Field(..., description="Model weights storage path")
    artifact_hash_sha256: str = Field(..., description="Integrity verification")
    config_path: Optional[str] = None
    
    # Performance Metrics (Gate Checks)
    metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Compliance
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    audit_logs: List[str] = Field(default_factory=list)
    
    @field_validator('model_type')
    @classmethod
    def validate_decoder_only(cls, v: ModelType) -> ModelType:
        """CRITICAL: Decoder-only models require explicit approval"""
        if v == ModelType.DECODER_ONLY:
            raise ValueError(
                "DECODER_ONLY models are RESTRICTED. "
                "Use ENCODER_DECODER with citation constraints instead."
            )
        return v
    
    def is_expired(self) -> bool:
        """Check if model version has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class ClientAdapter(BaseModel):
    """Per-client fine-tuned adapter (LoRA/Adapter pattern)"""
    
    adapter_id: str
    client_id: str = Field(..., description="Tenant identifier")
    base_model_id: str = Field(..., description="Base model this adapts")
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=90),
        description="90-day expiry per security policy"
    )
    
    # Data lineage
    training_data_source: str = Field(..., description="Where training data came from")
    training_samples_count: int = Field(..., gt=0)
    pii_removed: bool = Field(True, description="MUST be True for production")
    
    # Performance
    metrics: Dict[str, float] = Field(default_factory=dict)
    drift_score: Optional[float] = None  # Model drift detection
    
    # Governance
    approved_by: Optional[str] = None
    status: ModelStatus = ModelStatus.DEVELOPMENT


class ModelRegistry:
    """
    Centralized model registry with security controls
    
    Security Features:
    - Artifact integrity verification (SHA256)
    - Version immutability
    - Approval workflow for production
    - Automatic expiry for client adapters
    - Audit trail
    """
    
    def __init__(self, registry_path: Path):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.registry_path / "registry.json"
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load registry from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                data = json.load(f)
                self.models: Dict[str, ModelMetadata] = {
                    k: ModelMetadata(**v) for k, v in data.get("models", {}).items()
                }
                self.adapters: Dict[str, ClientAdapter] = {
                    k: ClientAdapter(**v) for k, v in data.get("adapters", {}).items()
                }
        else:
            self.models = {}
            self.adapters = {}
    
    def _save_registry(self) -> None:
        """Persist registry to disk"""
        data = {
            "models": {k: v.model_dump(mode='json') for k, v in self.models.items()},
            "adapters": {k: v.model_dump(mode='json') for k, v in self.adapters.items()},
            "last_updated": datetime.utcnow().isoformat(),
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register_model(
        self,
        metadata: ModelMetadata,
        artifact_bytes: bytes,
    ) -> ModelMetadata:
        """
        Register new model with integrity check
        
        Args:
            metadata: Model metadata
            artifact_bytes: Model weights (for hash verification)
        
        Returns:
            Registered metadata with computed hash
        """
        # Compute artifact hash
        artifact_hash = hashlib.sha256(artifact_bytes).hexdigest()
        metadata.artifact_hash_sha256 = artifact_hash
        
        # Version immutability check
        model_key = f"{metadata.model_id}:{metadata.version}"
        if model_key in self.models:
            raise ValueError(
                f"Model {model_key} already exists. Versions are immutable. "
                "Use a new version number."
            )
        
        # Audit log
        metadata.audit_logs.append(
            f"{datetime.utcnow().isoformat()} - Registered by {metadata.owner}"
        )
        
        self.models[model_key] = metadata
        self._save_registry()
        
        return metadata
    
    def approve_for_production(
        self,
        model_id: str,
        version: str,
        approver: str,
        gate_checks: Dict[str, bool],
    ) -> None:
        """
        Approve model for production deployment
        
        Args:
            model_id: Model identifier
            version: Model version
            approver: Approver identity
            gate_checks: Dictionary of gate check results (all must be True)
        """
        model_key = f"{model_id}:{version}"
        model = self.models.get(model_key)
        
        if not model:
            raise ValueError(f"Model {model_key} not found")
        
        # Validate all gate checks passed
        if not all(gate_checks.values()):
            failed_gates = [k for k, v in gate_checks.items() if not v]
            raise ValueError(
                f"Cannot approve: Failed gates: {failed_gates}"
            )
        
        # Update status
        model.status = ModelStatus.PRODUCTION
        model.approved_by = approver
        model.approval_date = datetime.utcnow()
        model.deployed_at = datetime.utcnow()
        
        # Audit log
        model.audit_logs.append(
            f"{datetime.utcnow().isoformat()} - Approved for PRODUCTION by {approver}"
        )
        
        self._save_registry()
    
    def register_client_adapter(
        self,
        adapter: ClientAdapter,
    ) -> ClientAdapter:
        """
        Register per-client adapter (LoRA/Adapter pattern)
        
        Security: 90-day expiry enforced
        """
        # Validate base model exists
        base_models = [m for m in self.models if m.startswith(adapter.base_model_id)]
        if not base_models:
            raise ValueError(f"Base model {adapter.base_model_id} not found")
        
        # PII check (CRITICAL)
        if not adapter.pii_removed:
            raise ValueError(
                "SECURITY POLICY VIOLATION: pii_removed=False. "
                "Cannot register adapter with PII in training data."
            )
        
        adapter_key = f"{adapter.client_id}:{adapter.adapter_id}"
        self.adapters[adapter_key] = adapter
        self._save_registry()
        
        return adapter
    
    def get_production_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get latest production model version"""
        production_models = [
            m for k, m in self.models.items()
            if k.startswith(model_id) and m.status == ModelStatus.PRODUCTION
        ]
        
        if not production_models:
            return None
        
        # Return latest version
        return max(production_models, key=lambda m: m.version)
    
    def cleanup_expired_adapters(self) -> List[str]:
        """Remove expired client adapters (security hygiene)"""
        expired = []
        for key, adapter in list(self.adapters.items()):
            if datetime.utcnow() > adapter.expires_at:
                expired.append(key)
                del self.adapters[key]
        
        if expired:
            self._save_registry()
        
        return expired
    
    def quarantine_model(
        self,
        model_id: str,
        version: str,
        reason: str,
    ) -> None:
        """Emergency quarantine (security incident)"""
        model_key = f"{model_id}:{version}"
        model = self.models.get(model_key)
        
        if not model:
            raise ValueError(f"Model {model_key} not found")
        
        model.status = ModelStatus.QUARANTINE
        model.audit_logs.append(
            f"{datetime.utcnow().isoformat()} - QUARANTINE: {reason}"
        )
        
        self._save_registry()


# Example usage for SICO GRC
def initialize_sico_registry() -> ModelRegistry:
    """Initialize registry with baseline models"""
    registry = ModelRegistry(Path("./ai/model_registry/artifacts"))
    
    # Register multilingual embedding model (baseline)
    embedding_metadata = ModelMetadata(
        model_id="multilingual-e5",
        model_name="Multilingual E5 Large (Arabic/English)",
        version="1.0.0",
        model_type=ModelType.EMBEDDING,
        base_model="intfloat/multilingual-e5-large",
        parameters_count=560_000_000,
        languages=["ar", "en"],
        owner="SICO AI Team",
        risk_level=RiskLevel.LOW,
        artifact_path="./ai/model_registry/artifacts/e5-large-v1.0.0",
        artifact_hash_sha256="placeholder",  # Will be computed on registration
        metrics={
            "retrieval_precision": 0.89,
            "retrieval_recall": 0.87,
        },
    )
    
    return registry
