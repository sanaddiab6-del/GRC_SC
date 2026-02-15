"""
Bilingual RAG Retriever
Supports Arabic and English queries with citation tracking
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

_LANGCHAIN_AVAILABLE = False

if TYPE_CHECKING:
    from langchain.embeddings import HuggingFaceEmbeddings  # type: ignore[import-not-found]
    from langchain.vectorstores import Chroma  # type: ignore[import-not-found]
    from langchain.schema import Document  # type: ignore[import-not-found]
else:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings  # type: ignore[import-not-found]
        from langchain.vectorstores import Chroma  # type: ignore[import-not-found]
        from langchain.schema import Document  # type: ignore[import-not-found]
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
    ):
        if not _LANGCHAIN_AVAILABLE:
            raise ImportError(
                "AI dependencies are not installed. Install langchain, "
                "langchain-community, sentence-transformers, and chromadb."
            )
        assert HuggingFaceEmbeddings is not None
        assert Chroma is not None
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vectorstore = Chroma(
            persist_directory=vector_db_path,
            embedding_function=self.embeddings,
        )
    
    def retrieve(
        self,
        query: str,
        language: str = "ar",
        top_k: int = 5,
        framework_filter: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant control documents
        
        Args:
            query: Search query in Arabic or English
            language: Query language ('ar' or 'en')
            top_k: Number of results to return
            framework_filter: Optional list of frameworks (ECC, CCC, PDPL)
        
        Returns:
            List of results with citations
        """
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
        
        return formatted_results
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to vector store"""
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
