from __future__ import annotations
from collections.abc import AsyncIterator

from app.domain import (
    CodeReview,
    LLMProvider,
    LLMProviderError,
    ReviewNotFoundError,
    ReviewRepository,
    ReviewRequest,
    SYSTEM_PROMPT
)

class ReviewService:
    """Orchestrates code review using an LLM provider and a repository
    
    Depends on interfaces (LLMProvider, ReviewRepository), not concrete 
    implementations. This is Dependency Inversion: the services defines
    WHAT it needs, infrastructure provides HOW
    """
    
    def __init__(self, llm_provider: LLMProvider, repository: ReviewRepository) -> None:
        self._llm = llm_provider
        self._repo = repository
        
        
    async def _generate(self, code: str) -> str:
        """Invoke the LLM and wrap provider errors into domain errors"""
        try:
            return await self._llm.generate(SYSTEM_PROMPT, code)
        except Exception as exc:
            raise LLMProviderError(str(exc)) from exc
        
    async def _save(self, request: ReviewRequest, annotated_code: str, explanation: str ) -> CodeReview:
        """Build a CodeReview entity and persist it"""
        review = CodeReview(
            original_code=request.code,
            language=request.language,
            annotated_code=annotated_code,
            explanation=explanation,
            provider=self._llm.provider_name,
            model=self._llm.model_name
        )
        
        return await self._repo.save(review)
    
    @staticmethod
    def _parse_response(raw: str) -> tuple[str, str]:
        """Split the LLM response into annotated code and explication
        
        
        The LLM is prompted to return two sections separated 
        '### Detailed Explanation'. Everything before that marker
        is the annotated code, everything after is the explanation.
        """
        
        marker = '### Detailed Explanation'
        if marker in raw:
            annotated, explanation = raw.split(marker, 1)
            return annotated.strip(), explanation.strip()
        return raw.strip(), ""
        
    async def review(self, request: ReviewRequest) -> CodeReview:
        """ Perform a non-streaming code review and persist the result"""
        raw_response = await self._generate(request.code)
        annotated, explanation = self._parse_response(raw_response)
        return await self._save(
            request=request,
            annotated_code=annotated,
            explanation=explanation
        )
        
    async def review_stream(self, request: ReviewRequest) -> AsyncIterator[str]:
        """Stream a code review chunk by chunk and persist the full result"""
        
        accumulated = ""
        try:
            async for chunk in self._llm.stream(SYSTEM_PROMPT, request.code):
                accumulated += chunk
                yield chunk
        except Exception as exc:
            raise LLMProviderError(str(exc)) from exc
        
        annotated, explanation = self._parse_response(accumulated)
        await self._save(
            request=request,
            annotated_code=annotated,
            explanation=explanation
        )
        
    async def get_history(self) -> list[CodeReview]:
        """Retrieve all past reviews, most recent first"""
        return await self._repo.get_all()
    
    async def get_review(self, review_id: str) -> CodeReview:
        """Retrieve a single review by ID"""
        review = await self._repo.get_by_id(review_id)
        if review is None:
            raise ReviewNotFoundError(
                f"Review with id '{review_id}' not found"
            )
        return review
    
    async def delete_review(self, review_id: str) -> bool:
        """Delete a review by ID. Returns True if deleted, False if not Found"""
        return await self._repo.delete(review_id)