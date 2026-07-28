from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from app.domain.models import CodeReview


class LLMProvider(ABC):
    """Abstract interfaces for LLM communication

    Implementations send prompts to specific provider (OpenAI, Gemini, Deepseek, etc)
    and return generated text
    """

    @abstractmethod
    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Send a prompt and return the complete respons"""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier of the specific model (e.g, 'gpt-4o', 'gemini-2.0-flash', 'deepseek-v4-pro')"""

    @abstractmethod
    def stream(self, system_prompt: str, user_message: str) -> AsyncIterator[str]:
        """Send a prompt and yield response chunks as they arrive.

        Used for Server-Sent Events streaming to the frontend.
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier (e.g. 'openai', 'google', 'deepseek')"""


class ReviewRepository(ABC):
    """Abstract interface for review persistence

    Implementations store and retrieve CodeReview entities.
    """

    @abstractmethod
    async def save(self, review: CodeReview) -> CodeReview:
        """Persist a new review and return it with any generated fields"""

    @abstractmethod
    async def get_all(self) -> list[CodeReview]:
        """Retrieve all reviews, most recent first"""

    @abstractmethod
    async def get_by_id(self, review_id: str) -> CodeReview | None:
        """Retrieve a single review by its ID"""

    @abstractmethod
    async def delete(self, review_id:str) -> bool:
        """Delete a review. Returns True if deleted, False if not found"""
        

class CacheProvider(ABC):
    """Abstract interface for response caching.

    Implementations store and retrieve CodeReview entities to avoid
    redundant LLM calls for identical input.
    """

    @abstractmethod
    async def get(self, key: str) -> CodeReview | None:
        """Retrieve a cached review, or None if not found or expired."""

    @abstractmethod
    async def set(self, key: str, review: CodeReview) -> None:
        """Store a review in the cache."""

    @abstractmethod
    def make_key(self, code: str, language: str | None) -> str:
        """Generate a deterministic cache key from code and language."""