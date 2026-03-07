"""
AI Security Layer - RBAC + Audit + PII Protection
Compliant with NCA ECC, PDPL, SDAIA AI Principles
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class AIRole(str, Enum):
    """AI-specific RBAC roles"""
    AI_ADMIN = "ai_admin"  # Full access + model management
    COMPLIANCE_OFFICER = "compliance_officer"  # Query + audit access
    ANALYST = "analyst"  # Query with filtering
    VIEWER = "viewer"  # Read-only, no PII
    SYSTEM = "system"  # Internal service calls


class AIPermission(str, Enum):
    """Granular AI permissions"""
    QUERY_RAG = "query_rag"
    QUERY_WITH_PII = "query_with_pii"  # RESTRICTED
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_MODELS = "manage_models"
    EXPORT_DATA = "export_data"  # RESTRICTED
    BYPASS_RATE_LIMIT = "bypass_rate_limit"


class QueryContext(BaseModel):
    """Security context for AI queries"""
    user_id: str = Field(..., description="Authenticated user ID")
    tenant_id: str = Field(..., description="Tenant/client ID for multi-tenancy")
    role: AIRole
    permissions: Set[AIPermission]
    ip_address: str
    user_agent: str
    session_id: str


class AuditEvent(BaseModel):
    """Audit log event - 7-year retention per NCA"""
    
    # Identity
    event_id: str = Field(default_factory=lambda: hashlib.sha256(
        f"{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16])
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Context
    user_id: str
    tenant_id: str
    role: AIRole
    ip_address: str
    session_id: str
    
    # Action
    action: str = Field(..., description="query_rag, model_update, etc.")
    resource_type: str = Field(..., description="model, document, control")
    resource_ids: List[str] = Field(default_factory=list, description="Retrieved doc IDs")
    
    # Request/Response (REDACTED)
    query_hash: str = Field(..., description="SHA256 of query (not plaintext if PII)")
    query_length: int
    response_doc_count: int
    frameworks_accessed: List[str] = Field(default_factory=list)
    
    # Decision
    allowed: bool = Field(..., description="Authorization decision")
    deny_reason: Optional[str] = None
    
    # Risk indicators
    pii_detected: bool = False
    citation_count: int = 0
    risk_score: float = 0.0  # 0.0-1.0


class PIIPattern(BaseModel):
    """PII detection patterns - Saudi-specific"""
    name: str
    pattern: str
    risk_level: str  # low, medium, high


# Saudi-specific PII patterns
SAUDI_PII_PATTERNS: List[PIIPattern] = [
    # Saudi National ID
    PIIPattern(
        name="saudi_national_id",
        pattern=r"\b[12]\d{9}\b",
        risk_level="high"
    ),
    # Saudi phone numbers
    PIIPattern(
        name="saudi_phone",
        pattern=r"\b(05|٠٥)[0-9٠-٩]{8}\b",
        risk_level="medium"
    ),
    # IBAN (Saudi) - SA + 2 check digits + 20 account chars
    PIIPattern(
        name="saudi_iban",
        pattern=r"SA\d{2}[A-Z0-9]{20}",
        risk_level="high"
    ),
    # Email addresses
    PIIPattern(
        name="email",
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        risk_level="medium"
    ),
    # Arabic full names (heuristic: 3+ Arabic words)
    PIIPattern(
        name="arabic_name",
        pattern=r"[\u0621-\u064A]{2,}\s+[\u0621-\u064A]{2,}\s+[\u0621-\u064A]{2,}",
        risk_level="medium"
    ),
    # Credit card numbers
    PIIPattern(
        name="credit_card",
        pattern=r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        risk_level="high"
    ),
]


class PIIRedactor:
    """
    PII detection and redaction engine
    PDPL Article 20 compliance
    """
    
    def __init__(self, patterns: Optional[List[PIIPattern]] = None):
        self.patterns = patterns or SAUDI_PII_PATTERNS
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text
        
        Returns:
            List of detected PII instances with positions
        """
        detections = []
        
        for pattern_def in self.patterns:
            pattern = re.compile(pattern_def.pattern)
            for match in pattern.finditer(text):
                detections.append({
                    "type": pattern_def.name,
                    "risk_level": pattern_def.risk_level,
                    "position": (match.start(), match.end()),
                    "length": len(match.group()),
                })
        
        return detections
    
    def redact_pii(self, text: str, redaction_char: str = "█") -> str:
        """
        Redact PII from text
        
        Args:
            text: Input text
            redaction_char: Character to use for redaction
        
        Returns:
            Text with PII redacted
        """
        detections = self.detect_pii(text)
        
        # Sort by position (reverse to maintain offsets)
        detections.sort(key=lambda x: x["position"][0], reverse=True)
        
        redacted_text = text
        for detection in detections:
            start, end = detection["position"]
            redaction = redaction_char * (end - start)
            redacted_text = redacted_text[:start] + redaction + redacted_text[end:]
        
        return redacted_text
    
    def has_high_risk_pii(self, text: str) -> bool:
        """Check if text contains high-risk PII"""
        detections = self.detect_pii(text)
        return any(d["risk_level"] == "high" for d in detections)


class RBACEnforcer:
    """
    Role-Based Access Control for AI queries
    NCA ECC-IS-3 compliance
    """
    
    # Role-Permission mapping
    ROLE_PERMISSIONS: Dict[AIRole, Set[AIPermission]] = {
        AIRole.AI_ADMIN: {
            AIPermission.QUERY_RAG,
            AIPermission.QUERY_WITH_PII,
            AIPermission.VIEW_AUDIT_LOGS,
            AIPermission.MANAGE_MODELS,
            AIPermission.EXPORT_DATA,
            AIPermission.BYPASS_RATE_LIMIT,
        },
        AIRole.COMPLIANCE_OFFICER: {
            AIPermission.QUERY_RAG,
            AIPermission.VIEW_AUDIT_LOGS,
        },
        AIRole.ANALYST: {
            AIPermission.QUERY_RAG,
        },
        AIRole.VIEWER: {
            AIPermission.QUERY_RAG,
        },
        AIRole.SYSTEM: {
            AIPermission.QUERY_RAG,
            AIPermission.BYPASS_RATE_LIMIT,
        },
    }
    
    def __init__(self):
        self.pii_redactor = PIIRedactor()
    
    def authorize(
        self,
        context: QueryContext,
        required_permission: AIPermission,
    ) -> tuple[bool, Optional[str]]:
        """
        Check authorization
        
        Returns:
            (allowed, deny_reason)
        """
        role_permissions = self.ROLE_PERMISSIONS.get(context.role, set())
        
        if required_permission not in role_permissions:
            return False, f"Role {context.role} lacks permission {required_permission}"
        
        # Additional checks can go here (e.g., rate limits, IP whitelist)
        
        return True, None
    
    def enforce_tenant_isolation(
        self,
        context: QueryContext,
        resource_tenant_id: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Enforce multi-tenancy (data segregation)
        CCC-SEC-04 compliance
        """
        if context.role == AIRole.AI_ADMIN:
            return True, None  # Admin can cross tenants
        
        if context.tenant_id != resource_tenant_id:
            return False, f"Tenant isolation violation: {context.tenant_id} != {resource_tenant_id}"
        
        return True, None
    
    def should_redact_pii(self, context: QueryContext) -> bool:
        """Determine if PII should be redacted for this role"""
        return AIPermission.QUERY_WITH_PII not in context.permissions


class AuditLogger:
    """
    Audit logging for AI operations
    NCA ECC-IS-5 (7-year retention) + PDPL Article 24 compliance
    """
    
    def __init__(self, log_file: str = "./logs/ai_audit.jsonl"):
        self.log_file = log_file
        self.pii_detector = PIIRedactor()
    
    def log_query(
        self,
        context: QueryContext,
        query: str,
        retrieved_docs: List[str],
        frameworks: List[str],
        allowed: bool,
        deny_reason: Optional[str] = None,
        citations_count: int = 0,
    ) -> AuditEvent:
        """
        Log AI query with security context
        
        CRITICAL: Never log raw query if it contains PII
        """
        # Hash query for privacy
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        
        # Detect PII
        pii_detected = len(self.pii_detector.detect_pii(query)) > 0
        high_risk_pii = self.pii_detector.has_high_risk_pii(query)
        
        # Compute risk score
        risk_score = 0.0
        if not allowed:
            risk_score += 0.5
        if pii_detected:
            risk_score += 0.3
        if high_risk_pii:
            risk_score += 0.2
        
        event = AuditEvent(
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            role=context.role,
            ip_address=context.ip_address,
            session_id=context.session_id,
            action="query_rag",
            resource_type="control_document",
            resource_ids=retrieved_docs,
            query_hash=query_hash,
            query_length=len(query),
            response_doc_count=len(retrieved_docs),
            frameworks_accessed=frameworks,
            allowed=allowed,
            deny_reason=deny_reason,
            pii_detected=pii_detected,
            citation_count=citations_count,
            risk_score=risk_score,
        )
        
        # Write to audit log (append-only)
        self._write_event(event)
        
        return event
    
    def _write_event(self, event: AuditEvent) -> None:
        """Write event to audit log (JSONL format)"""
        import json
        from pathlib import Path
        
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event.model_dump(mode='json')) + '\n')
    
    def get_high_risk_events(
        self,
        threshold: float = 0.7,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """
        Retrieve high-risk audit events for review
        Used by SOC/compliance team
        """
        import json
        from pathlib import Path
        
        if not Path(self.log_file).exists():
            return []
        
        high_risk_events = []
        with open(self.log_file) as f:
            for line in f:
                event_dict = json.loads(line)
                if event_dict.get("risk_score", 0) >= threshold:
                    high_risk_events.append(AuditEvent(**event_dict))
                
                if len(high_risk_events) >= limit:
                    break
        
        return high_risk_events


class PromptSanitizer:
    """
    Prompt injection defense
    SDAIA AI Security principle
    """
    
    # Injection patterns (multi-language)
    INJECTION_PATTERNS = [
        r"ignore.*?instructions",  # Simplified to catch "ignore all previous instructions"
        r"تجاهل.*?التعليمات",  # Arabic: ignore...instructions
        r"system\s*:",
        r"<\|.*?\|>",  # Special tokens
        r"```.*?```",  # Code blocks (suspicious in GRC queries)
    ]
    
    def __init__(self, max_length: int = 1000):
        self.max_length = max_length
        self.patterns = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.INJECTION_PATTERNS]
    
    def sanitize(self, query: str) -> tuple[str, List[str]]:
        """
        Sanitize user query
        
        Returns:
            (sanitized_query, detected_threats)
        """
        threats = []
        
        # Length check
        if len(query) > self.max_length:
            threats.append(f"query_too_long:{len(query)}")
            query = query[:self.max_length]
        
        # Injection pattern detection
        for pattern in self.patterns:
            if pattern.search(query):
                threats.append(f"injection_pattern:{pattern.pattern[:30]}")
        
        # If threats detected, reject query
        if threats:
            raise ValueError(f"Prompt injection detected: {threats}")
        
        return query, threats
    
    def validate_safe(self, query: str) -> bool:
        """Quick check if query is safe"""
        try:
            self.sanitize(query)
            return True
        except ValueError:
            return False
