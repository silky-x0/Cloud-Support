import os
import logging
from typing import List, Tuple

from langchain_community.vectorstores import Chroma
from retrieval.embeddings import get_embeddings
from models.message import Citation

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self):
        self.persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.embeddings = get_embeddings()
        
        # Initialize the vector store
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            self.vectorstore = None

    def retrieve(self, query: str, k: int = 5) -> Tuple[str, List[Citation]]:
        """
        Retrieves top k relevant chunks from the vector store.
        Returns a combined context string and a list of Citation objects.
        """
        if not self.vectorstore:
            return "Knowledge base is currently unavailable.", []

        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            context_parts = []
            citations = []
            
            for doc, score in results:
                kb_id = doc.metadata.get("kb_id", "Unknown")
                title = doc.metadata.get("title", "Untitled")
                
                context_parts.append(f"[{kb_id}] {doc.page_content}")
                
                confidence = max(0.0, 1.0 - (score / 2.0)) 
                
                citations.append(Citation(
                    kb_id=kb_id,
                    title=title,
                    snippet=doc.page_content[:200] + "...",
                    score=round(confidence, 3)
                ))
            
            combined_context = "\n\n".join(context_parts)
            return combined_context, citations

        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}")
            return "An error occurred during retrieval.", []
