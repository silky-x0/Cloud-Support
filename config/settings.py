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
    OPENAI_API_KEY: str
    
    # ── Model Configuration ──────────────────────────────────────────────────
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # ── Database & Storage ───────────────────────────────────────────────────
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    
    # ── Server ───────────────────────────────────────────────────────────────
    PORT: int = 8000
    HOST: str = "0.0.0.0"


# Global settings instance
settings = Settings()
