from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

from app.infrastructure.llm.base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """LLM provider backed by Google's Gemini API via LangChain."""

    _MODEL = "gemini-2.0-flash"
    _PROVIDER = "google"

    def _build_chat_model(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            api_key=self._api_key,
            model=self.model_name,
            temperature=self._temperature,
        )