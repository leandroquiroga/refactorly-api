from __future__ import annotations

from collections.abc import AsyncGenerator

from app.config import settings
from app.infrastructure import LLMProviderFactory, SQLiteReviewRepository, MemomyCache
from app.application import ReviewService, ResponseParser
from app.domain import LLMProvider, InvalidCodeError

_review_service: ReviewService | None = None


def _make_provider(provider: str | None, model: str | None) -> LLMProvider:
    resolved = (provider or settings.DEFAULT_PROVIDER).lower()
    if resolved not in LLMProviderFactory.PROVIDER_MAP:
        supported = ", ".join(LLMProviderFactory.PROVIDER_MAP.keys())
        raise InvalidCodeError(
            f"Unsupported provider '{resolved}'. Supported: {supported}"
        )

    return LLMProviderFactory.create(
        provider=resolved,
        api_key=_get_api_key(resolved),
        model=model or settings.DEFAULT_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
    )


def _get_api_key(provider: str) -> str:
    """Resolve the API key for the given provider from settings"""
    key_map: dict[str, str] = {
        "openai": settings.OPENAI_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
        "deepseek": settings.DEEPSEEK_API_KEY,
    }

    key = key_map.get(provider)

    if key is None:
        raise ValueError(f"No API key configured for provider '{provider}'")

    return key


async def get_review_service() -> AsyncGenerator[ReviewService, None]:
    """Yield a cached ReviewService singleton with all dependencies wired"""

    global _review_service

    if _review_service is None:
        repository = SQLiteReviewRepository(db_path=settings.DATABASE_PATH)
        _review_service = ReviewService(
            provider_factory=_make_provider,
            repository=repository,
            parser=ResponseParser(),
            cache=MemomyCache(ttl_seconds=settings.CACHE_TTL_SECONDS),
        )

    yield _review_service
