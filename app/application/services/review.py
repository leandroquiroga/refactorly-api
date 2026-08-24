from __future__ import annotations

import structlog
import asyncio
from typing import Callable
from collections.abc import AsyncIterator

from app.application.services.parser import ResponseParser
from app.domain import (
    CodeReview,
    LLMProvider,
    LLMProviderError,
    ReviewNotFoundError,
    ReviewRepository,
    ReviewRequest,
    SYSTEM_PROMPT,
    CacheProvider,
)

logger = structlog.get_logger(__name__)


class ReviewService:
    """Orchestrates code review using an LLM provider and a repository

    Depends on interfaces (LLMProvider, ReviewRepository), not concrete
    implementations. This is Dependency Inversion: the services defines
    WHAT it needs, infrastructure provides HOW
    """

    def __init__(
        self,
        provider_factory: Callable[[str | None, str | None], LLMProvider],
        repository: ReviewRepository,
        parser: ResponseParser | None = None,
        cache: CacheProvider | None = None,
    ) -> None:
        self._provider_factory = provider_factory
        self._repo = repository
        self._parser = parser or ResponseParser()
        self._cache = cache

    @staticmethod
    def _build_user_message(code: str, response_language: str) -> str:
        if response_language == "es":
            return f"Responde en español.\n\n{code}"
        return f"Respond in English.\n\n{code}"

    async def review(self, request: ReviewRequest) -> CodeReview:
        """Perform a non-streaming code review and persist the result."""
        provider = self._provider_factory(request.provider, request.model)
        if self._cache is not None:
            cache_key = self._cache.make_key(
                request.code,
                request.language,
                request.response_language,
                provider_name=provider.provider_name,
                model_name=provider.model_name,
            )
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.info("cache_hit", cache_key=cache_key[:12])
                return cached

        logger.info(
            "llm_request_started",
            language=request.language,
            response_language=request.response_language,
        )
        raw_response = await self._generate(
            provider, request.code, request.response_language
        )
        logger.info("llm_request_completed")

        annotated, explanation = self._parser.parse(raw_response)
        review = await self._save(
            provider=provider,
            request=request,
            annotated_code=annotated,
            explanation=explanation,
        )

        if self._cache is not None:
            cache_key = self._cache.make_key(
                request.code,
                request.language,
                request.response_language,
                provider_name=provider.provider_name,
                model_name=provider.model_name,
            )
            await self._cache.set(cache_key, review)

        return review

    async def review_stream(self, request: ReviewRequest) -> AsyncIterator[str]:
        """Stream a code review chunk-by-chunk and persist the full result."""
        provider = self._provider_factory(request.provider, request.model)
        # === CACHE CHECK ===
        if self._cache is not None:
            cache_key = self._cache.make_key(
                request.code,
                request.language,
                request.response_language,
                provider_name=provider.provider_name,
                model_name=provider.model_name,
            )
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.info("cache_hit", cache_key=cache_key[:12])
                full = f"{cached.annotated_code}\n\n### Detailed Explanation\n\n{cached.explanation}"
                for i in range(0, len(full), 80):
                    yield full[i : i + 80]
                    await asyncio.sleep(0.01)
                return

        # === LLM CALL ===
        accumulated = ""
        try:
            message = self._build_user_message(request.code, request.response_language)
            logger.info(
                "llm_request_started",
                language=request.language,
                response_language=request.response_language,
            )
            async for chunk in provider.stream(SYSTEM_PROMPT, message):
                accumulated += chunk
                yield chunk
            logger.info("llm_request_completed")
        except Exception as exc:
            logger.error(
                "llm_provider_error", error=str(exc), provider=provider.provider_name
            )
            raise LLMProviderError(str(exc)) from exc

        # === PARSE + SAVE + CACHE ===
        annotated, explanation = self._parser.parse(accumulated)
        review = await self._save(
            provider=provider,
            request=request,
            annotated_code=annotated,
            explanation=explanation,
        )

        if self._cache is not None:
            cache_key = self._cache.make_key(
                request.code,
                request.language,
                request.response_language,
                provider_name=provider.provider_name,
                model_name=provider.model_name,
            )
            await self._cache.set(cache_key, review)

    async def get_history(self) -> list[CodeReview]:
        return await self._repo.get_all()

    async def get_review(self, review_id: str) -> CodeReview:
        review = await self._repo.get_by_id(review_id)
        if review is None:
            raise ReviewNotFoundError(f"Review with id '{review_id}' not found")
        return review

    async def delete_review(self, review_id: str) -> bool:
        return await self._repo.delete(review_id)

    async def _generate(
        self, provider: LLMProvider, code: str, response_language: str
    ) -> str:
        message = self._build_user_message(code, response_language)
        try:
            return await provider.generate(SYSTEM_PROMPT, message)
        except Exception as exc:
            logger.error(
                "llm_provider_error", error=str(exc), provider=provider.provider_name
            )
            raise LLMProviderError(str(exc)) from exc

    async def _save(
        self,
        provider: LLMProvider,
        request: ReviewRequest,
        annotated_code: str,
        explanation: str,
    ) -> CodeReview:
        review = CodeReview(
            original_code=request.code,
            language=request.language,
            annotated_code=annotated_code,
            explanation=explanation,
            provider=provider.provider_name,
            model=provider.model_name,
        )
        logger.debug("review_saved", review_id=str(review.id))
        return await self._repo.save(review)
