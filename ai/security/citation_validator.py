"""
Citation Validation Engine
Ensures AI responses are grounded in source documents
SDAIA AI Principle 3 (Transparency) compliance
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Source citation metadata"""
    control_id: str
    framework: str
    section: str  # description, policy, procedure
    quote: Optional[str] = None  # Exact quote from source
    confidence: float = Field(..., ge=0.0, le=1.0)


class CitationValidationResult(BaseModel):
    """Result of citation validation"""
    is_valid: bool
    citation_rate: float = Field(..., ge=0.0, le=1.0, description="% of response with citations")
    hallucination_detected: bool
    issues: List[str] = Field(default_factory=list)
    validated_citations: List[Citation]


class CitationValidator:
    """
    Validates that AI-generated text is properly cited
    
    Security: Prevents hallucination and misleading information
    Gate Check: citation_rate >= 95% for production
    """
    
    def __init__(self, min_citation_rate: float = 0.95):
        self.min_citation_rate = min_citation_rate
    
    def validate_response(
        self,
        generated_text: str,
        citations: List[Citation],
        source_documents: List[Dict[str, Any]],
    ) -> CitationValidationResult:
        """
        Validate that response is grounded in sources
        
        Args:
            generated_text: AI-generated response
            citations: Claimed citations
            source_documents: Retrieved documents from RAG
        
        Returns:
            Validation result with citation rate
        """
        issues = []
        validated_citations = []
        
        # Check 1: Are citations present?
        if not citations:
            issues.append("No citations provided")
            return CitationValidationResult(
                is_valid=False,
                citation_rate=0.0,
                hallucination_detected=True,
                issues=issues,
                validated_citations=[],
            )
        
        # Check 2: Do citations match retrieved documents?
        retrieved_control_ids = {doc.get("control_id") for doc in source_documents}
        
        for citation in citations:
            if citation.control_id not in retrieved_control_ids:
                issues.append(
                    f"Citation {citation.control_id} not in retrieved documents"
                )
            else:
                # Validate quote exists in source
                source_doc = next(
                    (d for d in source_documents if d.get("control_id") == citation.control_id),
                    None
                )
                
                if source_doc and citation.quote:
                    source_text = source_doc.get("content", "")
                    
                    # Check if quote appears in source (fuzzy match)
                    if self._quote_exists_in_source(citation.quote, source_text):
                        validated_citations.append(citation)
                    else:
                        issues.append(
                            f"Quote not found in source: {citation.control_id}"
                        )
                else:
                    # No quote provided, assume valid (low confidence)
                    validated_citations.append(citation)
        
        # Check 3: Calculate citation rate
        # Heuristic: Count sentences with citation markers
        total_sentences = len(self._split_sentences(generated_text))
        cited_sentences = self._count_cited_sentences(generated_text)
        
        citation_rate = cited_sentences / total_sentences if total_sentences > 0 else 0.0
        
        # Check 4: Hallucination detection
        hallucination_detected = citation_rate < self.min_citation_rate
        
        if hallucination_detected:
            issues.append(
                f"Citation rate {citation_rate:.1%} below threshold {self.min_citation_rate:.1%}"
            )
        
        is_valid = len(issues) == 0 and not hallucination_detected
        
        return CitationValidationResult(
            is_valid=is_valid,
            citation_rate=citation_rate,
            hallucination_detected=hallucination_detected,
            issues=issues,
            validated_citations=validated_citations,
        )
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple heuristic)"""
        # Arabic and English sentence terminators
        sentences = re.split(r'[.!?؟]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _count_cited_sentences(self, text: str) -> int:
        """Count sentences with citation markers"""
        sentences = self._split_sentences(text)
        
        # Citation markers: [ECC-GV-1], (ECC-GV-1), etc.
        citation_pattern = re.compile(r'\[?([A-Z]+-[A-Z]+-\d+)\]?')
        
        cited = sum(1 for s in sentences if citation_pattern.search(s))
        return cited
    
    def _quote_exists_in_source(self, quote: str, source_text: str) -> bool:
        """
        Check if quote exists in source (fuzzy match)
        Allows for minor variations (punctuation, whitespace)
        """
        # Normalize both texts
        normalized_quote = self._normalize_text(quote)
        normalized_source = self._normalize_text(source_text)
        
        # Check if quote appears in source (substring match)
        return normalized_quote in normalized_source
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation
        text = re.sub(r'[^\w\s\u0621-\u064A]', '', text)
        # Lowercase (for English)
        text = text.lower()
        return text.strip()


class RefusalPolicy:
    """
    Defines when AI should refuse to answer
    SDAIA AI Safety principle
    """
    
    # Questions that should trigger refusal
    REFUSAL_PATTERNS = [
        # Off-topic queries
        r"(weather|sports|football|entertainment|recipes)",
        r"(الطقس|الرياضة|كرة|الترفيه|وصفات)",
        
        # Requests for legal advice
        r"(legal advice|sue|lawsuit|attorney)",
        r"(مشورة قانونية|دعوى|محامي)",
        
        # Requests to circumvent controls
        r"(bypass|circumvent|workaround|hack)",
        r"(تجاوز|تحايل|اختراق)",
    ]
    
    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.REFUSAL_PATTERNS]
    
    def should_refuse(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if query should be refused
        
        Returns:
            (should_refuse, reason)
        """
        for pattern in self.patterns:
            if pattern.search(query):
                return True, f"Query matches refusal pattern: {pattern.pattern[:50]}"
        
        return False, None
    
    def get_refusal_message(self, language: str = "ar") -> str:
        """Get polite refusal message"""
        messages = {
            "ar": (
                "عذرًا، لا أستطيع الإجابة على هذا السؤال. "
                "أنا مخصص للإجابة على أسئلة الامتثال التنظيمي (ECC/CCC/PDPL) فقط. "
                "يرجى إعادة صياغة سؤالك أو التواصل مع فريق الدعم."
            ),
            "en": (
                "I'm sorry, I cannot answer this question. "
                "I'm designed to answer regulatory compliance (ECC/CCC/PDPL) questions only. "
                "Please rephrase your question or contact the support team."
            ),
        }
        return messages.get(language, messages["ar"])


class EvidenceMapper:
    """
    Maps evidence to controls with confidence scoring
    Used for evidence collection automation
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
    
    def map_evidence_to_controls(
        self,
        evidence_text: str,
        evidence_type: str,
        candidate_controls: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Map evidence to controls with confidence scores
        
        Args:
            evidence_text: Evidence description
            evidence_type: Type (policy, procedure, screenshot, etc.)
            candidate_controls: List of potential matching controls
        
        Returns:
            List of control matches with confidence and review flag
        """
        mappings = []
        
        for control in candidate_controls:
            # Calculate confidence based on semantic similarity
            # (In production, use embedding-based similarity)
            confidence = self._calculate_confidence(
                evidence_text,
                evidence_type,
                control,
            )
            
            # Determine if human review required
            require_review = confidence < self.confidence_threshold
            
            if confidence > 0.3:  # Minimum threshold
                mappings.append({
                    "control_id": control["control_id"],
                    "framework": control["framework"],
                    "confidence": confidence,
                    "require_human_review": require_review,
                    "mapping_reason": self._get_mapping_reason(
                        evidence_type,
                        control,
                        confidence,
                    ),
                })
        
        # Sort by confidence
        mappings.sort(key=lambda x: x["confidence"], reverse=True)
        
        return mappings
    
    def _calculate_confidence(
        self,
        evidence_text: str,
        evidence_type: str,
        control: Dict[str, Any],
    ) -> float:
        """
        Calculate mapping confidence (simplified)
        In production, use embedding similarity
        """
        confidence = 0.5  # Base confidence
        
        # Boost if evidence type matches control guidance type
        control_text = (
            f"{control.get('description', '')} "
            f"{control.get('policy_guidance', '')} "
            f"{control.get('procedure_guidance', '')}"
        ).lower()
        
        # Simple keyword matching (replace with embeddings)
        evidence_words = set(evidence_text.lower().split())
        control_words = set(control_text.split())
        
        overlap = len(evidence_words & control_words)
        overlap_ratio = overlap / len(evidence_words) if evidence_words else 0
        
        confidence += overlap_ratio * 0.4
        
        # Type-specific boosts
        if evidence_type == "policy" and "policy" in control_text:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _get_mapping_reason(
        self,
        evidence_type: str,
        control: Dict[str, Any],
        confidence: float,
    ) -> str:
        """Generate explanation for mapping"""
        if confidence >= 0.8:
            return f"High confidence match: {evidence_type} evidence aligns with control requirements"
        elif confidence >= 0.6:
            return f"Moderate confidence: {evidence_type} evidence likely relevant, review recommended"
        else:
            return f"Low confidence: Manual review required to confirm relevance"
