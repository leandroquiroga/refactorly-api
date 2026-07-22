from __future__ import annotations
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded and validated from environment/.env file."""

    OPENAI_API_KEY: str = Field(..., min_length=1, description="OpenAI API Key")
    GEMINI_API_KEY: str = Field(...,  min_length=1, description="Gemini API Key")
    DEEPSEEK_API_KEY: str = Field(..., min_length=1, description="Deepseek API Key")
    DEFAULT_PROVIDER: str = Field(..., min_length=1, description=("Default LMM Provider (openai | gemini | deepseek)"))
    DEFAULT_MODEL: str = Field(..., min_length=1, description=("Default LMM model name"))
    LLM_TEMPERATURE: float = Field(..., ge=0.0, le=2.0, description=("LLM temperature (0.0 to 2.0)"))
    DATABASE_PATH: str = Field(..., min_length=1, description=("SQLite database file path"))
    HOST: str = Field(..., min_length=1, description=("Server host"))
    PORT: int = Field(..., ge=1, le=65535, description=("Server port"))
    CORS_ORIGINS: list[str] = Field(..., min_length=1, description=("Allowed CORS origins (comma-separated)"))
    LOG_LEVEL: str = Field(..., min_length=1, description=("Logging level (DEBUG | INFO | WARNING | ERROR)"))
    REVIEW_RATE_LIMIT: str = Field("5/minute", min_length=1, description="Rate limit for POST /api/review (e.g. '5/minute', '10/hour')")
    HISTORY_RATE_LIMIT: str = Field("30/minute", min_length=1, description="Rate limit for GET/DELETE endpoints")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    

settings = Settings()