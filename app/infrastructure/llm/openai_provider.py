from __future__ import annotations

from pydantic import SecretStr

from langchain_openai import ChatOpenAI
from app.infrastructure.llm.base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """LLM provider backed by OpenAI's API via LangChain."""

    _MODEL = "gpt-4o"
    _PROVIDER = "openai"

    def _build_chat_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=SecretStr(self._api_key),
            model=self.model_name,
            temperature=self._temperature,
        )