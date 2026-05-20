# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import MagicMock, patch
from retrieval.retriever import Retriever
from models.message import Citation

def test_retriever_success():
    # 1. Instantiate the Retriever, mocking the Chroma vector store
    with patch("retrieval.retriever.Chroma") as mock_chroma_class:
        mock_vectorstore = MagicMock()
        mock_chroma_class.return_value = mock_vectorstore
        
        retriever = Retriever()
        retriever.vectorstore = mock_vectorstore
        
        # 2. Setup mock document and metadata
        mock_doc = MagicMock()
        mock_doc.page_content = "This is a troubleshooting instruction for alerts."
        mock_doc.metadata = {"kb_id": "KB-001", "title": "AWS Integration Alerts"}
        
        mock_vectorstore.similarity_search_with_score.return_value = [(mock_doc, 0.4)]
        
        # 3. Call retriever
        context, citations = retriever.retrieve("My alerts stopped working", k=1)
        
        # 4. Assert correctness of the retrieved context and citation metadata
        assert "[KB-001] This is a troubleshooting instruction for alerts." in context
        assert len(citations) == 1
        assert citations[0].kb_id == "KB-001"
        assert citations[0].title == "AWS Integration Alerts"
        assert citations[0].snippet.startswith("This is a troubleshooting instruction")
        assert citations[0].score == 0.8  # confidence: 1.0 - (0.4 / 2.0)
