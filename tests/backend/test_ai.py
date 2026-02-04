# Backend Tests - AI/RAG Module
import pytest
from httpx import AsyncClient
from src.backend.main import app


@pytest.mark.asyncio
async def test_rag_query_english():
    """Test RAG query in English"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        query_request = {
            "query": "What are the governance requirements?",
            "language": "en",
            "framework_filter": ["ECC"],
            "top_k": 5
        }
        
        response = await client.post("/api/v1/ai/query", json=query_request)
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == query_request["query"]
        assert data["language"] == "en"
        assert "results" in data
        assert "total_results" in data


@pytest.mark.asyncio
async def test_rag_query_arabic():
    """Test RAG query in Arabic"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        query_request = {
            "query": "ما هي متطلبات الحوكمة؟",
            "language": "ar",
            "framework_filter": ["ECC", "CCC"],
            "top_k": 3
        }
        
        response = await client.post("/api/v1/ai/query", json=query_request)
        assert response.status_code == 200
        data = response.json()
        
        assert data["language"] == "ar"
        assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_get_query_suggestions():
    """Test getting query suggestions"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/ai/suggestions?language=ar")
        assert response.status_code == 200
        data = response.json()
        
        assert data["language"] == "ar"
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) > 0


@pytest.mark.asyncio
async def test_invalid_language():
    """Test RAG query with invalid language"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        query_request = {
            "query": "test query",
            "language": "fr",  # Invalid language
            "top_k": 5
        }
        
        response = await client.post("/api/v1/ai/query", json=query_request)
        assert response.status_code == 422  # Validation error
