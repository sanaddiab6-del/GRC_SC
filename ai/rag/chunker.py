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
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 128, max_chunk_size: int = 2000):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunk_size = max_chunk_size
    
    def _split_long_text(self, text: str, language: str) -> List[str]:
        """
        Split text if it exceeds max_chunk_size.
        Uses basic sentence splitting that works for both English and Arabic.
        
        Note: For production, consider using language-specific tokenizers
        like nltk.sent_tokenize for English or CAMeL Tools for Arabic.
        """
        if len(text) <= self.max_chunk_size:
            return [text]
        
        # Split on common sentence delimiters (works for both languages)
        # Arabic uses '.' and English uses '. '
        import re
        # Split on period followed by space or newline, or just period at end
        sentences = re.split(r'\.\s+|\.\n+|\.(?=$)', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            sentence_size = len(sentence)
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                # Keep overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_chunk = overlap_sentences
                current_size = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        if current_chunk:
            chunks.append('. '.join(current_chunk))
        
        return chunks if chunks else [text]
    
    def chunk_control(self, control: Dict) -> List[Document]:
        """
        Split a control into logical chunks
        
        Args:
            control: Control dictionary with bilingual fields
        
        Returns:
            List of Document objects for vector store
        """
        if not _LANGCHAIN_AVAILABLE:
            raise ImportError(
                "AI dependencies are not installed. Install langchain to use chunking."
            )
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
        
        # Chunk 1: Description - separate by language for better retrieval
        desc_en = control.get('description_en', '')
        desc_ar = control.get('description_ar', '')
        
        # Split English description if too long
        for i, chunk_text in enumerate(self._split_long_text(desc_en, 'en')):
            chunks.append(Document(
                page_content=chunk_text,
                metadata={**base_metadata, "section": "description", "language": "en", "chunk_index": i}
            ))
        
        # Split Arabic description if too long
        for i, chunk_text in enumerate(self._split_long_text(desc_ar, 'ar')):
            chunks.append(Document(
                page_content=chunk_text,
                metadata={**base_metadata, "section": "description", "language": "ar", "chunk_index": i}
            ))
        
        # Chunk 2: Policy Guidance (if exists)
        if control.get("policy_guidance_en"):
            for i, chunk_text in enumerate(self._split_long_text(control.get('policy_guidance_en', ''), 'en')):
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata={**base_metadata, "section": "policy", "language": "en", "chunk_index": i}
                ))
        
        if control.get("policy_guidance_ar"):
            for i, chunk_text in enumerate(self._split_long_text(control.get('policy_guidance_ar', ''), 'ar')):
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata={**base_metadata, "section": "policy", "language": "ar", "chunk_index": i}
                ))
        
        # Chunk 3: Procedure Guidance (if exists)
        if control.get("procedure_guidance_en"):
            for i, chunk_text in enumerate(self._split_long_text(control.get('procedure_guidance_en', ''), 'en')):
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata={**base_metadata, "section": "procedure", "language": "en", "chunk_index": i}
                ))
        
        if control.get("procedure_guidance_ar"):
            for i, chunk_text in enumerate(self._split_long_text(control.get('procedure_guidance_ar', ''), 'ar')):
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata={**base_metadata, "section": "procedure", "language": "ar", "chunk_index": i}
                ))
        
        return chunks
    
    def chunk_batch(self, controls: List[Dict]) -> List[Document]:
        """Chunk multiple controls"""
        all_chunks = []
        for control in controls:
            all_chunks.extend(self.chunk_control(control))
        return all_chunks
