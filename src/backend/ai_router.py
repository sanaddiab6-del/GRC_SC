"""
AI/RAG API Router
Bilingual query endpoint with citation tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

# Try to import AI module - may not be available in  all environments
AI_AVAILABLE = False

if TYPE_CHECKING:
    from ai.rag.bilingual_retriever import BilingualRetriever
else:
    try:
        from ai.rag.bilingual_retriever import BilingualRetriever
        AI_AVAILABLE = True
    except ImportError:
        AI_AVAILABLE = False
        BilingualRetriever = None

router = APIRouter()

# Lazy initialization of retriever to avoid loading models during import
# This prevents CI/CD test collection from hanging due to large model downloads
_retriever_instance = None

def get_retriever():
    """Lazy load the BilingualRetriever instance"""
    global _retriever_instance
    if _retriever_instance is None and AI_AVAILABLE and BilingualRetriever:
        _retriever_instance = BilingualRetriever()
    return _retriever_instance


class QueryRequest(BaseModel):
    """Schema for RAG query request"""
    query: str = Field(
        min_length=3,
        json_schema_extra={"example": "What are the governance requirements?"}
    )
    language: str = Field("ar", pattern="^(ar|en)$")
    framework_filter: Optional[List[str]] = ["ECC", "CCC", "PDPL"]
    top_k: int = Field(5, ge=1, le=20)


class QueryResponse(BaseModel):
    """Schema for RAG query response"""
    query: str
    language: str
    results: List[dict]
    total_results: int


@router.post("/ai/query", response_model=QueryResponse)
async def query_rag_system(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Query the bilingual RAG system
    Returns relevant controls with citations
    """
    retriever = get_retriever()
    if not AI_AVAILABLE or retriever is None:
        raise HTTPException(
            status_code=503,
            detail="AI/RAG system is not available. Please install AI dependencies."
        )
    
    try:
        # Perform RAG retrieval
        results = retriever.retrieve(
            query=request.query,
            language=request.language,
            top_k=request.top_k,
            framework_filter=request.framework_filter,
        )
        
        return QueryResponse(
            query=request.query,
            language=request.language,
            results=results,
            total_results=len(results),
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message_en": f"Error processing query: {str(e)}",
                "message_ar": f"خطأ في معالجة الاستعلام: {str(e)}",
            },
        )


@router.get("/ai/suggestions")
async def get_query_suggestions(
    language: str = Query("ar", pattern="^(ar|en)$"),
):
    """Get suggested queries for users"""
    suggestions = {
        "ar": [
            "ما هي متطلبات الحوكمة؟",
            "كيف أحمي البيانات الشخصية؟",
            "ما هي ضوابط الأمن السيبراني؟",
            "ما هي متطلبات الحوسبة السحابية؟",
            "كيف أستعد للتدقيق؟",
        ],
        "en": [
            "What are the governance requirements?",
            "How do I protect personal data?",
            "What are the cybersecurity controls?",
            "What are the cloud computing requirements?",
            "How do I prepare for an audit?",
        ],
    }
    
    return {
        "language": language,
        "suggestions": suggestions.get(language, suggestions["ar"]),
    }


@router.post("/ai/index/rebuild")
async def rebuild_vector_index(
    db: AsyncSession = Depends(get_db),
):
    """
    Rebuild the vector database index from repo control libraries (Repo Mode).
    Admin endpoint - requires authentication in production.
    """
    try:
        from ai.rag.control_loader import load_all_frameworks_as_documents, get_library_stats
        stats = get_library_stats()
        total_controls = sum(
            v.get("total_controls", 0) for v in stats.values() if isinstance(v, dict)
        )
        docs = load_all_frameworks_as_documents()
        return {
            "status": "ready",
            "message_en": f"Control library loaded: {total_controls} controls, {len(docs)} chunks ready for indexing. Run scripts/build_rag_index.py to build the vector store.",
            "message_ar": f"تم تحميل مكتبة الضوابط: {total_controls} ضابط، {len(docs)} قطعة جاهزة للفهرسة.",
            "library_stats": stats,
        }
    except Exception as e:
        return {
            "status": "error",
            "message_en": f"Error loading control library: {str(e)}",
            "message_ar": f"خطأ في تحميل مكتبة الضوابط: {str(e)}",
        }


