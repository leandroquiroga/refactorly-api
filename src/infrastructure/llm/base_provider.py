from __future__ import annotations

from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.outputs import ChatGenerationChunk

from src.domain.interfaces import LLMProvider

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage


class BaseLLMProvider(LLMProvider):
    """Common logic for all LangChain-based LLM providers.

    Subclasses must define _MODEL, _PROVIDER, and _build_chat_model().
    """

    _MODEL: str
    _PROVIDER: str

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> None:
        self._api_key = api_key
        self._model_override = model
        self._temperature = temperature

    @abstractmethod
    def _build_chat_model(self) -> BaseChatModel:
        """Create and configure the provider-specific LangChain chat model."""

    @property
    def model_name(self) -> str:
        return self._model_override or self._MODEL

    @property
    def provider_name(self) -> str:
        return self._PROVIDER

    def _build_messages(
        self, system_prompt: str, user_message: str
    ) -> list[BaseMessage]:
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]

    async def generate(self, system_prompt: str, user_message: str) -> str:
        model = self._build_chat_model()
        messages = self._build_messages(system_prompt, user_message)
        response = await model.ainvoke(messages)
        return str(response.content)

    async def stream(
        self, system_prompt: str, user_message: str
    ) -> AsyncIterator[str]:
        model = self._build_chat_model()
        messages = self._build_messages(system_prompt, user_message)
        async for chunk in model.astream(messages):
            if isinstance(chunk, ChatGenerationChunk):
                content = chunk.text
                if content:
                    yield content