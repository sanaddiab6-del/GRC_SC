"""
AI/RAG API Router
Bilingual query endpoint with citation tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from ai.rag.bilingual_retriever import BilingualRetriever

router = APIRouter()

# Initialize retriever (in production, use dependency injection)
retriever = BilingualRetriever()


class QueryRequest(BaseModel):
    """Schema for RAG query request"""
    query: str = Field(..., min_length=3, example="What are the governance requirements?")
    language: str = Field("ar", regex="^(ar|en)$")
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
    language: str = Query("ar", regex="^(ar|en)$"),
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
    Rebuild the vector database index
    Admin endpoint - requires authentication in production
    """
    # This would trigger a background task to rebuild the index
    # For now, return a placeholder response
    return {
        "status": "initiated",
        "message_en": "Vector index rebuild initiated",
        "message_ar": "تم بدء إعادة بناء فهرس المتجهات",
    }
