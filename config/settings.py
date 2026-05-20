import os
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings powered by Pydantic Settings.
    Environment variables are automatically mapped to these fields.
    Precedence: Env Var > .env file > Default value
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── API Keys ─────────────────────────────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    OPEN_ROUTER_KEY: Optional[str] = None
    
    # ── Model Configuration ──────────────────────────────────────────────────
    OPENAI_MODEL: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    EMBEDDING_MODEL: str = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
    
    # ── Database & Storage ───────────────────────────────────────────────────
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    
    # ── Server ───────────────────────────────────────────────────────────────
    PORT: int = 8000
    HOST: str = "0.0.0.0"


# Global settings instance
settings = Settings()

