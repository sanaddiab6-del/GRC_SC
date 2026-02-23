"""
AI Security Package
Multi-layer defense: RBAC + PII + Audit + Prompt Defense
"""

from ai.security.ai_security import (
    AIRole,
    AIPermission,
    QueryContext,
    AuditEvent,
    PIIPattern,
    PIIRedactor,
    RBACEnforcer,
    AuditLogger,
    PromptSanitizer,
)

from ai.security.citation_validator import (
    Citation,
    CitationValidationResult,
    CitationValidator,
    RefusalPolicy,
    EvidenceMapper,
)

__all__ = [
    # RBAC & Audit
    "AIRole",
    "AIPermission",
    "QueryContext",
    "AuditEvent",
    "RBACEnforcer",
    "AuditLogger",
    
    # PII Protection
    "PIIPattern",
    "PIIRedactor",
    
    # Prompt Defense
    "PromptSanitizer",
    
    # Citation Validation
    "Citation",
    "CitationValidationResult",
    "CitationValidator",
    "RefusalPolicy",
    "EvidenceMapper",
]
