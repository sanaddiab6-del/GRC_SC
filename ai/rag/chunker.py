"""
Document chunking for control library
Splits controls into logical sections for RAG
"""

from typing import List, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

_LANGCHAIN_AVAILABLE = False

if TYPE_CHECKING:
    from langchain.schema import Document  # type: ignore[import-not-found]
else:
    try:
        from langchain.schema import Document  # type: ignore[import-not-found]
        _LANGCHAIN_AVAILABLE = True
    except ImportError:
        @dataclass
        class Document:
            page_content: str
            metadata: Dict[str, Any]
        _LANGCHAIN_AVAILABLE = False


class ControlChunker:
    """
    Chunks control documents for optimal RAG retrieval
    Preserves bilingual content and metadata
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 128):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_control(self, control: Dict) -> List[Document]:
        """
        Split a control into logical chunks
        
        Args:
            control: Control dictionary with bilingual fields
        
        Returns:
            List of Document objects for vector store
        """
        chunks = []
        control_id = control.get("control_id")
        framework = control.get("framework")
        
        # Metadata common to all chunks
        base_metadata = {
            "control_id": control_id,
            "framework": framework,
            "domain": control.get("domain"),
            "title_en": control.get("title_en"),
            "title_ar": control.get("title_ar"),
        }
        
        # Chunk 1: Description (bilingual)
        chunks.append(Document(
            page_content=f"{control.get('description_en')}\n\n{control.get('description_ar')}",
            metadata={**base_metadata, "section": "description"}
        ))
        
        # Chunk 2: Policy Guidance (if exists)
        if control.get("policy_guidance_en"):
            chunks.append(Document(
                page_content=f"{control.get('policy_guidance_en')}\n\n{control.get('policy_guidance_ar')}",
                metadata={**base_metadata, "section": "policy"}
            ))
        
        # Chunk 3: Procedure Guidance (if exists)
        if control.get("procedure_guidance_en"):
            chunks.append(Document(
                page_content=f"{control.get('procedure_guidance_en')}\n\n{control.get('procedure_guidance_ar')}",
                metadata={**base_metadata, "section": "procedure"}
            ))
        
        return chunks
    
    def chunk_batch(self, controls: List[Dict]) -> List[Document]:
        """Chunk multiple controls"""
        all_chunks = []
        for control in controls:
            all_chunks.extend(self.chunk_control(control))
        return all_chunks
