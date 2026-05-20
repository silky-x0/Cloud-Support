import os
# pyrefly: ignore [missing-import]
from langchain_openai import OpenAIEmbeddings
from config.settings import settings

class OpenRouterEmbeddings(OpenAIEmbeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.create(
            input=texts,
            model=self.model,
            encoding_format="float"
        )
        return [r.embedding for r in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        response = await self.async_client.create(
            input=texts,
            model=self.model,
            encoding_format="float"
        )
        return [r.embedding for r in response.data]

    async def aembed_query(self, text: str) -> list[float]:
        embeddings = await self.aembed_documents([text])
        return embeddings[0]

def get_embeddings():
    """
    Returns the embeddings model.
    Uses OpenRouter and nvidia/llama-nemotron-embed-vl-1b-v2:free when available.
    """
    api_key = settings.OPEN_ROUTER_KEY or settings.OPENAI_API_KEY
    if not api_key:
        raise ValueError("Either OPEN_ROUTER_KEY or OPENAI_API_KEY must be set.")
    
    if settings.OPEN_ROUTER_KEY:
        return OpenRouterEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=api_key
        )
    else:
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=api_key
        )
