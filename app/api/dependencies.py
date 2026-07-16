from __future__ import annotations

from collections.abc import AsyncGenerator
from app.config import settings
from app.infrastructure import LLMProviderFactory, SQLiteReviewRepository
from app.application import ReviewService


_review_service: ReviewService | None = None

def _get_api_key(provider: str) -> str:
    """Resolve the API key for the given provider from settings"""
    key_map: dict[str, str] = {
        "openai": settings.OPENAI_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
        "deepseek": settings.DEEPSEEK_API_KEY
    }

    key = key_map.get(provider)
    
    if key is None:
        raise ValueError(f"No API key configured for provider '{provider}'")

    return key


async def get_review_service() -> AsyncGenerator[ReviewService, None]:
    """Yield a cached ReviewServices singleton with all dependencies  wired"""
    
    global _review_service
    
    if _review_service is None:
        repository = SQLiteReviewRepository(db_path=settings.DATABASE_PATH)
        provider = LLMProviderFactory.create(
            provider=settings.DEFAULT_PROVIDER,
            api_key=_get_api_key(settings.DEFAULT_PROVIDER),
            model=settings.DEFAULT_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )
        
        _review_service = ReviewService(llm_provider=provider, repository=repository)
        
    yield _review_service