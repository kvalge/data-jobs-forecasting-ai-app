# fallback_client.py
"""Compose OpenRouter extraction with optional Ollama fallback."""

from __future__ import annotations

import src.config as config
from src.llm.base_llm_client import BaseLLMClient
from src.llm.errors import OpenRouterChainExhausted, RECOVERABLE_LLM_ERRORS
from src.llm.openrouter_client import OpenRouterClient


class OpenRouterWithOllamaFallback(BaseLLMClient):
    """Try OpenRouter model chain; on exhaustion, optionally call Ollama.

    Used for LLM_PROVIDER_MODE=openrouter_ollama. Keeps provider nesting out of
    OpenRouterClient so mode selection stays in the factory/orchestrator.
    """

    def __init__(self, primary: OpenRouterClient | None = None) -> None:
        self._primary = primary or OpenRouterClient()

    def extract(self, posting_text: str) -> dict:
        try:
            return self._primary.extract(posting_text)
        except OpenRouterChainExhausted as openrouter_error:
            if not config.OLLAMA_FALLBACK_ENABLED:
                raise

            from src.llm.ollama_client import OllamaClient

            try:
                return OllamaClient().extract(
                    posting_text,
                    fallback_used=True,
                    attempt_index=openrouter_error.models_tried,
                )
            except RECOVERABLE_LLM_ERRORS as ollama_error:
                raise RuntimeError(
                    f"All OpenRouter models failed ({openrouter_error.models_tried} tried), "
                    f"and Ollama fallback also failed. "
                    f"OpenRouter: {openrouter_error.detail}. "
                    f"Ollama ({config.OLLAMA_MODEL}): {ollama_error}"
                ) from ollama_error
