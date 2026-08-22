from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette import EventSourceResponse
from uuid import UUID

from app.application import ReviewService
from app.config import settings
from app.domain import (CodeReview, ReviewNotFoundError, ReviewRequest, ReviewResponse)
from app.api.dependencies import get_review_service
from app.api.streaming import stream_review
from app.api.limiter import limiter

router = APIRouter(prefix="/api/review", tags=["review"])

@router.post("")
@limiter.limit(settings.REVIEW_RATE_LIMIT)
async def review(request: Request, body: ReviewRequest, service: ReviewService = Depends(get_review_service)) -> EventSourceResponse:
    """Submit code for review. Returns SSE stream with LLM chuncks"""
    return EventSourceResponse(stream_review(request,body, service))


@router.get("/history", response_model=list[ReviewResponse])
@limiter.limit(settings.HISTORY_RATE_LIMIT)
async def get_history(request: Request, service: ReviewService = Depends(get_review_service)) -> list[CodeReview]:
    """Get all past reviews, most recent first"""
    return await service.get_history()

@router.get("/{review_id}", response_model=ReviewResponse)
@limiter.limit(settings.HISTORY_RATE_LIMIT)
async def get_review(request: Request, review_id: UUID, service: ReviewService = Depends(get_review_service)) -> CodeReview:
    """Get a single review by ID"""
    try:
        return await service.get_review(str(review_id))
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    
@router.delete("/{review_id}")
@limiter.limit(settings.HISTORY_RATE_LIMIT)
async def delete_review(request: Request, review_id: UUID, service: ReviewService = Depends(get_review_service)) -> dict[str, str]:
    """Delete a review by ID"""
    deleted = await service.delete_review(str(review_id))
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Review with id '{review_id}' not found")
    return {"message": "Review deleted"}