"""Tests that OpenRouter extract tries the next model only after recoverable failure."""

from unittest.mock import MagicMock

import pytest

from src.llm.errors import OpenRouterChainExhausted
from src.llm.fallback_client import OpenRouterWithOllamaFallback
from src.llm.openrouter_client import OpenRouterClient


@pytest.fixture
def client():
    return OpenRouterClient()


def test_extract_stops_after_first_success(client, monkeypatch):
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.llm_model_chain",
        lambda: ["model-a", "model-b", "model-c"],
    )
    calls: list[str] = []

    def fake_call(model_name, posting_text, *, fallback_used=False, attempt_index=0):
        calls.append(model_name)
        return {"role_title": "Dev", "skills": []}

    monkeypatch.setattr(client, "_call_model", fake_call)
    result = client.extract("posting")
    assert result["role_title"] == "Dev"
    assert calls == ["model-a"]


def test_extract_uses_fallback_only_after_failure(client, monkeypatch):
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.llm_model_chain",
        lambda: ["model-a", "model-b", "model-c"],
    )
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT",
        False,
    )
    calls: list[str] = []

    def fake_call(model_name, posting_text, *, fallback_used=False, attempt_index=0):
        calls.append(model_name)
        if model_name == "model-a":
            raise RuntimeError("AI rate limit for model 'model-a' (HTTP 429)")
        if model_name == "model-b":
            return {"role_title": "Analyst", "skills": []}
        raise AssertionError("model-c should not be called")

    monkeypatch.setattr(client, "_call_model", fake_call)
    result = client.extract("posting")
    assert result["role_title"] == "Analyst"
    assert calls == ["model-a", "model-b"]


def test_type_error_is_not_rotated_across_models(client, monkeypatch):
    """Programming bugs must not be silently treated as recoverable API failures."""
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.llm_model_chain",
        lambda: ["model-a", "model-b"],
    )
    calls: list[str] = []

    def fake_call(model_name, posting_text, *, fallback_used=False, attempt_index=0):
        calls.append(model_name)
        raise TypeError("simulated programming bug")

    monkeypatch.setattr(client, "_call_model", fake_call)

    with pytest.raises(TypeError, match="simulated programming bug"):
        client.extract("posting")
    assert calls == ["model-a"]


def test_extract_falls_back_to_ollama_after_openrouter_exhausted(monkeypatch):
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.llm_model_chain",
        lambda: ["model-a", "model-b"],
    )
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT",
        False,
    )
    monkeypatch.setattr("src.llm.fallback_client.config.OLLAMA_FALLBACK_ENABLED", True)
    monkeypatch.setattr("src.llm.fallback_client.config.OLLAMA_MODEL", "qwen3.5:latest")

    primary = OpenRouterClient()

    def fake_call(model_name, posting_text, *, fallback_used=False, attempt_index=0):
        raise RuntimeError(f"AI rate limit for model '{model_name}' (HTTP 429)")

    monkeypatch.setattr(primary, "_call_model", fake_call)

    ollama = MagicMock()
    ollama.extract.return_value = {"role_title": "Local Dev", "skills": []}
    monkeypatch.setattr("src.llm.ollama_client.OllamaClient", lambda: ollama)

    result = OpenRouterWithOllamaFallback(primary).extract("posting")
    assert result["role_title"] == "Local Dev"
    ollama.extract.assert_called_once_with(
        "posting", fallback_used=True, attempt_index=2
    )


def test_rate_limit_shortcircuit_skips_remaining_openrouter_models(monkeypatch):
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.llm_model_chain",
        lambda: ["model-a", "model-b", "model-c"],
    )
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT",
        True,
    )
    monkeypatch.setattr("src.llm.fallback_client.config.OLLAMA_FALLBACK_ENABLED", True)

    primary = OpenRouterClient()
    calls: list[str] = []

    def fake_call(model_name, posting_text, *, fallback_used=False, attempt_index=0):
        calls.append(model_name)
        raise RuntimeError(f"AI rate limit for model '{model_name}' (HTTP 429)")

    monkeypatch.setattr(primary, "_call_model", fake_call)

    ollama = MagicMock()
    ollama.extract.return_value = {"role_title": "Local", "skills": []}
    monkeypatch.setattr("src.llm.ollama_client.OllamaClient", lambda: ollama)

    result = OpenRouterWithOllamaFallback(primary).extract("posting")
    assert result["role_title"] == "Local"
    assert calls == ["model-a"]
    ollama.extract.assert_called_once_with(
        "posting", fallback_used=True, attempt_index=1
    )


def test_extract_skips_ollama_when_disabled(client, monkeypatch):
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.llm_model_chain",
        lambda: ["model-a"],
    )
    monkeypatch.setattr("src.llm.fallback_client.config.OLLAMA_FALLBACK_ENABLED", False)

    def fake_call(model_name, posting_text, *, fallback_used=False, attempt_index=0):
        raise RuntimeError("AI rate limit (HTTP 429)")

    monkeypatch.setattr(client, "_call_model", fake_call)

    with pytest.raises(OpenRouterChainExhausted, match="All configured AI models failed"):
        client.extract("posting")


def test_schema_validation_failure_rotates_to_next_model(client, monkeypatch):
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.llm_model_chain",
        lambda: ["model-a", "model-b"],
    )
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.OPENROUTER_API_KEY", "test-key"
    )
    monkeypatch.setattr(
        "src.llm.openrouter_client.config.OPENROUTER_TIMEOUT_SECONDS", 60
    )
    monkeypatch.setattr("src.llm.openrouter_client.config.LLM_MAX_TOKENS", 2048)

    responses = [
        {
            "choices": [{"message": {"content": '{"": {}}'}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
        {
            "choices": [
                {
                    "message": {
                        "content": '{"role_title": "Analyst", "skills": [], "skills_en": []}'
                    }
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 5, "total_tokens": 6},
        },
    ]
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.side_effect = responses
    post = MagicMock(return_value=mock_response)
    monkeypatch.setattr("src.llm.openrouter_client.requests.post", post)

    result = client.extract("posting")
    assert result["role_title"] == "Analyst"
    assert post.call_count == 2
    payload = post.call_args_list[0].kwargs["json"]
    assert payload["max_tokens"] == 2048
    assert post.call_args_list[0].kwargs["timeout"] == 60


def test_factory_composes_ollama_fallback_when_enabled(monkeypatch):
    monkeypatch.setattr(
        "src.llm.llm_client_factory.config.LLM_PROVIDER_MODE",
        "openrouter_ollama",
    )
    monkeypatch.setattr(
        "src.llm.llm_client_factory.config.OLLAMA_FALLBACK_ENABLED",
        True,
    )
    from src.llm.llm_client_factory import get_llm_client

    client = get_llm_client()
    assert isinstance(client, OpenRouterWithOllamaFallback)


def test_factory_returns_bare_openrouter_when_ollama_fallback_disabled(monkeypatch):
    monkeypatch.setattr(
        "src.llm.llm_client_factory.config.LLM_PROVIDER_MODE",
        "openrouter_ollama",
    )
    monkeypatch.setattr(
        "src.llm.llm_client_factory.config.OLLAMA_FALLBACK_ENABLED",
        False,
    )
    from src.llm.llm_client_factory import get_llm_client

    client = get_llm_client()
    assert isinstance(client, OpenRouterClient)
