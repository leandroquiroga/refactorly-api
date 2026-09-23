from __future__ import annotations
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded and validated from environment/.env file."""

    OPENAI_API_KEY: str = Field(..., min_length=1, description="OpenAI API Key")
    GEMINI_API_KEY: str = Field(...,  min_length=1, description="Gemini API Key")
    DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API Key (optional, provider not implemented yet)")
    DEFAULT_PROVIDER: str = Field(..., min_length=1, description=("Default LLM Provider (openai | gemini)"))
    DEFAULT_MODEL: str = Field(..., min_length=1, description=("Default LLM model name"))
    LLM_TEMPERATURE: float = Field(..., ge=0.0, le=2.0, description=("LLM temperature (0.0 to 2.0)"))
    DATABASE_PATH: str = Field(..., min_length=1, description=("SQLite database file path"))
    HOST: str = Field(..., min_length=1, description=("Server host"))
    PORT: int = Field(..., ge=1, le=65535, description=("Server port"))
    CORS_ORIGINS: list[str] = Field(..., min_length=1, description=("Allowed CORS origins (comma-separated)"))
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(..., description=("Logging level (DEBUG | INFO | WARNING | ERROR)"))
    REVIEW_RATE_LIMIT: str = Field("5/minute", min_length=1, description="Rate limit for POST /api/review (e.g. '5/minute', '10/hour')")
    HISTORY_RATE_LIMIT: str = Field("30/minute", min_length=1, description="Rate limit for GET/DELETE endpoints")
    CACHE_TTL_SECONDS: int = Field(900, ge=0, description="Cache TTL in seconds for identical code reviews (0 disables caching)")
    MAX_BOY_SIZE: int = Field(100_000, ge=1024, description="Maximum request body size in bytes")
    MAX_TOKENS: int = Field(4096, ge=256, le=32768, description="Maximum number of output tokens per review")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    

settings = Settings()