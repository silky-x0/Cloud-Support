import os
from langchain_openai import OpenAIEmbeddings

def get_embeddings():
    """
    Returns the OpenAI embeddings model.
    Uses text-embedding-3-small for cost/performance balance.
    """
    return OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        openai_api_key=os.environ["OPENAI_API_KEY"]
    )
