from __future__ import annotations

from app.infrastructure.llm.gemini_provider import GeminiProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.llm.base_provider import BaseLLMProvider
from app.domain import LLMProvider

class LLMProviderFactory:
    """Creates LLMProvider instances based on configuration.

    Adding a new provider requires only:
    1. Create a new provider class extending BaseLLMProvider
    2. Add an elif branch here (or register it dynamically)
    """

    PROVIDER_MAP: dict[str, type[BaseLLMProvider]] = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
    }

    @classmethod
    def create(
        cls,
        provider: str,
        api_key: str,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None
    ) -> LLMProvider:
        provider_class = cls.PROVIDER_MAP.get(provider.lower())
        if provider_class is None:
            supported = ", ".join(cls.PROVIDER_MAP.keys())
            raise ValueError(
                f"Unsupported LLM provider '{provider}'. "
                f"Supported: {supported}"
            )
        return provider_class(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )