from __future__ import annotations
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette import EventSourceResponse

from app.application import ReviewService
from app.api.dependencies import get_review_service
from app.domain import (CodeReview, InvalidCodeError, LLMProviderError, ReviewNotFoundError, ReviewRequest, ReviewResponse)


router = APIRouter(prefix="/api/review", tags=["review"])


async def _stream_review(
    request: ReviewRequest,
    service: ReviewService
) -> AsyncGenerator[dict[str, str], None]:
    """Bridge between ReviewServices and SSE formated"""
    
    try:
        async for chunk in service.review_stream(request):
            yield {"event": "chunk", "data": chunk}
        yield {"event": "done", "data": ""}
    except LLMProviderError as exc:
        yield {"event": "error", "data": str(exc)}
    except InvalidCodeError as exc:
        yield {"event": "error", "data": str(exc)}
        

@router.post("")
async def review(request: ReviewRequest, service: ReviewService = Depends(get_review_service)) -> EventSourceResponse:
    """Submit code for review. Returns SSE stream with LLM chuncks"""
    return EventSourceResponse(_stream_review(request, service))


@router.get("/history", response_model=list[ReviewResponse])
async def get_history(service: ReviewService = Depends(get_review_service)) -> list[CodeReview]:
    """Get all past reviews, most recent first"""
    return await service.get_history()

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: UUID, service: ReviewService = Depends(get_review_service)) -> CodeReview:
    """Get a single review by ID"""
    try:
        return await service.get_review(str(review_id))
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    
@router.delete("/{review_id}")
async def delete_review(review_id: UUID, service: ReviewService = Depends(get_review_service)) -> dict[str, str]:
    """Delete a review by ID"""
    deleted = await service.delete_review(str(review_id))
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Review with id '{review_id}' not found")
    return {"message": "Review deleted"}