from __future__ import annotations
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded and validated from environment/.env file."""

    OPENAI_API_KEY: str = Field(..., min_length=1, validation_alias=("OPENAI_API_KEY"), description="OpenAI API Key")
    GEMINI_APY_KEY: str = Field(...,  min_length=1, validation_alias=("GOOGLE_API_KEY"), description="Gemini API Key")
    DEFAULT_PROVIDER: str = Field(..., min_length=1, validation_alias=("DEFAULT_PROVIDER"), description=("Default LMM Provider (openai | gemini | deepseek)"))
    DEFAULT_MODEL: str = Field(..., min_length=1, validation_alias=("DEFAULT_MODEL"), description=("Default LMM model name"))
    LLM_TEMPERATURE: str = Field(..., ge=0.0, le=2.0, validation_alias=("LLM_TEMPERATURE"), description=("LLM temperature (0.0 to 2.0)"))
    DATABASE_PATH: str = Field(..., min_length=1, validation_alias=("DATABASE_PATH"), description=("SQLite database file path"))
    HOST: str = Field(..., min_length=1, validation_alias=("HOST"), description=("Server host"))
    PORT: str = Field(..., ge=1, le=65535 ,validation_alias=("PORT"), description=("Server port"))
    CORS_ORIGINS: str = Field(..., min_length=1, validation_alias=("CORS_ORIGINS"), description=("Allowed CORS origins (comma-separated)"))
    LOG_LEVEL: str = Field(..., min_length=1, validation_alias=("LOG_LEVEL"), description=("Logging level (DEBUG | INFO | WARNING | ERROR)"))
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    

settings = Settings()