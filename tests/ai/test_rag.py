# AI/RAG Tests - Retriever and Chunker
import pytest
from ai.rag.bilingual_retriever import BilingualRetriever
from ai.rag.chunker import ControlChunker


def test_control_chunker():
    """Test control chunking for RAG"""
    chunker = ControlChunker(chunk_size=512, chunk_overlap=128)
    
    control_data = {
        "control_id": "ECC-GV-1",
        "framework": "ECC",
        "domain": "Governance",
        "title_en": "Governance Framework",
        "title_ar": "إطار الحوكمة",
        "description_en": "Test description in English",
        "description_ar": "وصف الاختبار بالعربية",
        "policy_guidance_en": "Policy guidance text",
        "policy_guidance_ar": "نص توجيهات السياسة",
    }
    
    chunks = chunker.chunk_control(control_data)
    
    assert len(chunks) >= 2  # At least description and policy chunks
    assert all(hasattr(chunk, 'page_content') for chunk in chunks)
    assert all(hasattr(chunk, 'metadata') for chunk in chunks)
    
    # Check metadata
    first_chunk = chunks[0]
    assert first_chunk.metadata["control_id"] == "ECC-GV-1"
    assert first_chunk.metadata["framework"] == "ECC"
    assert "section" in first_chunk.metadata


def test_chunker_batch_processing():
    """Test batch chunking of multiple controls"""
    chunker = ControlChunker()
    
    controls = [
        {
            "control_id": f"ECC-GV-{i}",
            "framework": "ECC",
            "domain": "Governance",
            "title_en": f"Control {i}",
            "title_ar": f"ضابط {i}",
            "description_en": f"Description {i}",
            "description_ar": f"وصف {i}",
        }
        for i in range(1, 6)
    ]
    
    all_chunks = chunker.chunk_batch(controls)
    
    assert len(all_chunks) >= 5  # At least one chunk per control
    
    # Check that all control IDs are present
    control_ids = {chunk.metadata["control_id"] for chunk in all_chunks}
    assert len(control_ids) == 5


@pytest.mark.skip(reason="Requires vector database setup")
def test_bilingual_retriever():
    """Test bilingual retriever (requires Chroma setup)"""
    retriever = BilingualRetriever()
    
    # This would require actual vector database setup
    # Skipped in unit tests, would run in integration tests
    pass
