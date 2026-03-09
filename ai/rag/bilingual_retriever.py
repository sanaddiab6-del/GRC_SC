"""
Bilingual RAG Retriever
Supports Arabic and English queries with citation tracking
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from collections import OrderedDict

_LANGCHAIN_AVAILABLE = False

if TYPE_CHECKING:
    from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore[import-not-found]
    from langchain_community.vectorstores import Chroma  # type: ignore[import-not-found]
    from langchain_core.documents import Document  # type: ignore[import-not-found]
else:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore[import-not-found]
        from langchain_community.vectorstores import Chroma  # type: ignore[import-not-found]
        from langchain_core.documents import Document  # type: ignore[import-not-found]
        _LANGCHAIN_AVAILABLE = True
    except ImportError:
        HuggingFaceEmbeddings = None
        Chroma = None
        @dataclass
        class Document:
            page_content: str
            metadata: Dict[str, Any]
        _LANGCHAIN_AVAILABLE = False


class BilingualRetriever:
    """
    RAG retriever supporting Arabic and English
    Returns results with source citations
    """
    
    def __init__(
        self,
        embedding_model: str = "intfloat/multilingual-e5-large",
        vector_db_path: str = "./vectordb",
        use_gpu: bool = True,
        use_smaller_model: bool = False,
    ):
        """
        Initialize the bilingual retriever.
        
        Args:
            embedding_model: HuggingFace model name for embeddings
            vector_db_path: Path to Chroma vector database
            use_gpu: Whether to use GPU if available (auto-detects)
            use_smaller_model: Use smaller model (e5-small) for faster but less accurate embeddings.
                              Recommended for development/testing or resource-constrained environments.
                              Trade-off: 3-5x faster but ~10-15% lower retrieval quality.
        """
        if not _LANGCHAIN_AVAILABLE:
            raise ImportError(
                "AI dependencies are not installed. Install langchain, "
                "langchain-community, sentence-transformers, and chromadb."
            )
        assert HuggingFaceEmbeddings is not None
        assert Chroma is not None
        
        # Use smaller model for better performance if specified
        if use_smaller_model:
            embedding_model = "intfloat/multilingual-e5-small"
        
        # Auto-detect GPU availability
        device = 'cpu'
        if use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    device = 'cuda'
            except ImportError:
                pass
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vectorstore = Chroma(
            persist_directory=vector_db_path,
            embedding_function=self.embeddings,
        )
        
        # LRU cache for query results using OrderedDict
        self._query_cache: OrderedDict[str, List[Dict[str, Any]]] = OrderedDict()
        self._cache_max_size = 100
    
    def retrieve(
        self,
        query: str,
        language: str = "ar",
        top_k: int = 5,
        framework_filter: Optional[List[str]] = None,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant control documents
        
        Args:
            query: Search query in Arabic or English
            language: Query language ('ar' or 'en')
            top_k: Number of results to return
            framework_filter: Optional list of frameworks (ECC, CCC, PDPL)
            use_cache: Whether to use cached results
        
        Returns:
            List of results with citations
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, language, top_k, framework_filter)
        
        # Check cache
        if use_cache and cache_key in self._query_cache:
            # Move to end to mark as recently used
            self._query_cache.move_to_end(cache_key)
            return self._query_cache[cache_key]
        
        # Build metadata filter
        filter_dict = {}
        if framework_filter:
            filter_dict["framework"] = {"$in": framework_filter}
        
        # Perform similarity search
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=top_k,
            filter=filter_dict if filter_dict else None,
        )
        
        # Format results with citations
        formatted_results = []
        for doc, score in results:
            result = {
                "control_id": doc.metadata.get("control_id"),
                "framework": doc.metadata.get("framework"),
                "title": doc.metadata.get(f"title_{language}"),
                "content": doc.page_content,
                "relevance_score": float(score),
                "source": {
                    "control_id": doc.metadata.get("control_id"),
                    "section": doc.metadata.get("section", "description"),
                }
            }
            formatted_results.append(result)
        
        # Cache results with proper LRU eviction
        if use_cache:
            if len(self._query_cache) >= self._cache_max_size:
                # Remove least recently used (first item in OrderedDict)
                self._query_cache.popitem(last=False)
            self._query_cache[cache_key] = formatted_results
        
        return formatted_results
    
    def _generate_cache_key(
        self,
        query: str,
        language: str,
        top_k: int,
        framework_filter: Optional[List[str]]
    ) -> str:
        """Generate a cache key for the query"""
        key_data = {
            "query": query,
            "language": language,
            "top_k": top_k,
            "framework_filter": sorted(framework_filter) if framework_filter else None
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def add_documents(self, documents: List[Document], batch_size: int = 50):
        """Add new documents to vector store with batching"""
        # Process documents in batches for efficiency
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            self.vectorstore.add_documents(batch)
        
        # Persist once after all batches
        self.vectorstore.persist()
    
    def add_documents(
        self,
        documents: List[str],
        metadata: List[Dict[str, Any]],
    ) -> None:
        """
        Add documents to the collection
        
        Args:
            documents: List of document texts
            metadata: List of document metadata
        """
        # TODO: Implement document ingestion
        pass
        
        # Clear query cache after adding new documents
        self._query_cache.clear()
