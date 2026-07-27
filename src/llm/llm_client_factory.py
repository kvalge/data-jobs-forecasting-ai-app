# llm_client_factory.py
"""Select the LLM extraction client from LLM_PROVIDER_MODE."""

from __future__ import annotations

import src.config as config
from src.llm.base_llm_client import BaseLLMClient


def get_llm_client() -> BaseLLMClient:
    """Return the active LLM client for the configured provider mode.

    - openrouter_ollama: OpenRouter model chain, then optional Ollama fallback
    - ollama_only: local Ollama only (no OpenRouter key required)
    """
    mode = config.normalize_llm_provider_mode(config.LLM_PROVIDER_MODE)
    if mode == config.LLM_PROVIDER_MODE_OLLAMA_ONLY:
        from src.llm.ollama_client import OllamaClient

        return OllamaClient()

    from src.llm.openrouter_client import OpenRouterClient

    return OpenRouterClient()
