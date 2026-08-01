from __future__ import annotations
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


class ReviewService:
    """Orchestrates code review using an LLM provider and a repository

    Depends on interfaces (LLMProvider, ReviewRepository), not concrete
    implementations. This is Dependency Inversion: the services defines
    WHAT it needs, infrastructure provides HOW
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        repository: ReviewRepository,
        parser: ResponseParser | None = None,
        cache: CacheProvider | None = None,
    ) -> None:
        self._llm = llm_provider
        self._repo = repository
        self._parser = parser or ResponseParser()
        self._cache = cache

    async def review(self, request: ReviewRequest) -> CodeReview:
        """Perform a non-streaming code review and persist the result."""
        if self._cache is not None:
            cache_key = self._cache.make_key(request.code, request.language)
            cached = await self._cache.get(cache_key)
            if cached is not None:
                return cached

        raw_response = await self._generate(request.code)
        annotated, explanation = self._parser.parse(raw_response)
        review = await self._save(
            request=request,
            annotated_code=annotated,
            explanation=explanation,
        )

        if self._cache is not None:
            cache_key = self._cache.make_key(request.code, request.language)
            await self._cache.set(cache_key, review)

        return review

    async def review_stream(self, request: ReviewRequest) -> AsyncIterator[str]:
        """Stream a code review chunk-by-chunk and persist the full result."""
        accumulated = ""
        try:
            async for chunk in self._llm.stream(SYSTEM_PROMPT, request.code):
                accumulated += chunk
                yield chunk
        except Exception as exc:
            raise LLMProviderError(str(exc)) from exc

        annotated, explanation = self._parser.parse(accumulated)
        await self._save(
            request=request,
            annotated_code=annotated,
            explanation=explanation,
        )

    async def get_history(self) -> list[CodeReview]:
        return await self._repo.get_all()

    async def get_review(self, review_id: str) -> CodeReview:
        review = await self._repo.get_by_id(review_id)
        if review is None:
            raise ReviewNotFoundError(f"Review with id '{review_id}' not found")
        return review

    async def delete_review(self, review_id: str) -> bool:
        return await self._repo.delete(review_id)

    async def _generate(self, code: str) -> str:
        try:
            return await self._llm.generate(SYSTEM_PROMPT, code)
        except Exception as exc:
            raise LLMProviderError(str(exc)) from exc

    async def _save(
        self,
        request: ReviewRequest,
        annotated_code: str,
        explanation: str,
    ) -> CodeReview:
        review = CodeReview(
            original_code=request.code,
            language=request.language,
            annotated_code=annotated_code,
            explanation=explanation,
            provider=self._llm.provider_name,
            model=self._llm.model_name,
        )
        return await self._repo.save(review)
