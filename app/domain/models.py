from __future__ import annotations
from typing import Literal
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

MAX_CODE_LENGTH = 32_000

class CodeReview(BaseModel):
    """Persisted review entity. Represents a completed code review"""
    
    id: UUID = Field(default_factory=uuid4)
    original_code: str
    language: str | None = None
    annotated_code: str
    explanation: str
    provider: str
    model: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    
    
class ReviewRequest(BaseModel):
    """Incoming review request from the API"""
    
    code: str = Field(..., min_length=1, max_length=MAX_CODE_LENGTH)
    language: str | None = Field(
        default=None,
        description="Programming language of the code (auto-detected if omitted)"
    )
    response_language: Literal["es", "en"] = "es"
    
    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, v:str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("code must not be blank")
        return stripped
    
class ReviewResponse(BaseModel):
    """API response wrapper for a single review"""
    
    id: UUID
    original_code: str
    language: str | None
    annotated_code: str
    explanation: str
    provider: str
    model: str
    created_at: datetime
    
    @classmethod
    def from_entry(cls, review: CodeReview) -> ReviewResponse:
        """Build an API response from a domain entity.

        This indirection exists so that the API contract can evolve
        independently from the domain model. If we later want to
        exclude internal fields or add computed ones, we change
        only this mapper.
        """
        return cls(**review.model_dump())
    