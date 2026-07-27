"""Tests that OpenRouter extract tries the next model only after failure."""

from unittest.mock import MagicMock, patch

import pytest

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

    def fake_call(model_name, posting_text):
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
    calls: list[str] = []

    def fake_call(model_name, posting_text):
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
