"""Tests for LLM_PROVIDER_MODE factory selection."""

from unittest.mock import MagicMock

import pytest

from src.llm.llm_client_factory import get_llm_client
from src.llm.ollama_client import OllamaClient
from src.llm.openrouter_client import OpenRouterClient


def test_factory_returns_openrouter_client_by_default(monkeypatch):
    monkeypatch.setattr(
        "src.llm.llm_client_factory.config.LLM_PROVIDER_MODE",
        "openrouter_ollama",
    )
    client = get_llm_client()
    assert isinstance(client, OpenRouterClient)


def test_factory_returns_ollama_client_in_ollama_only_mode(monkeypatch):
    monkeypatch.setattr(
        "src.llm.llm_client_factory.config.LLM_PROVIDER_MODE",
        "ollama_only",
    )
    client = get_llm_client()
    assert isinstance(client, OllamaClient)


def test_ollama_only_extract_does_not_call_openrouter(monkeypatch):
    monkeypatch.setattr(
        "src.llm.llm_client_factory.config.LLM_PROVIDER_MODE",
        "ollama_only",
    )
    monkeypatch.setattr("src.llm.ollama_client.config.OLLAMA_MODEL", "qwen3.5:latest")
    monkeypatch.setattr(
        "src.llm.ollama_client.config.OLLAMA_BASE_URL", "http://127.0.0.1:11434"
    )
    monkeypatch.setattr("src.llm.ollama_client.config.OLLAMA_ALLOW_REMOTE", False)
    monkeypatch.setattr("src.llm.ollama_client.config.OLLAMA_TIMEOUT_SECONDS", 30)
    monkeypatch.setattr(
        "src.llm.ollama_client.config.LLM_PROVIDER_MODE", "ollama_only"
    )

    openrouter_call = MagicMock(side_effect=AssertionError("OpenRouter must not be called"))
    monkeypatch.setattr(OpenRouterClient, "_call_model", openrouter_call)

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "role": "assistant",
            "content": '{"role_title": "Dev", "skills": [], "skills_en": []}',
        }
    }
    monkeypatch.setattr(
        "src.llm.ollama_client.requests.post",
        MagicMock(return_value=mock_response),
    )

    client = get_llm_client()
    result = client.extract("Job: Dev")
    assert result["role_title"] == "Dev"
    openrouter_call.assert_not_called()
