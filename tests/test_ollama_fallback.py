"""Tests for local Ollama extraction fallback (HTTP mocked)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.llm.ollama_client import OllamaClient


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("src.llm.ollama_client.config.OLLAMA_MODEL", "qwen3.5:latest")
    monkeypatch.setattr(
        "src.llm.ollama_client.config.OLLAMA_BASE_URL", "http://127.0.0.1:11434"
    )
    monkeypatch.setattr("src.llm.ollama_client.config.OLLAMA_TIMEOUT_SECONDS", 30)
    monkeypatch.setattr("src.llm.ollama_client.config.OLLAMA_KEEP_ALIVE", "10m")
    monkeypatch.setattr("src.llm.ollama_client.config.LLM_MAX_TOKENS", 2048)
    return OllamaClient()


def test_ollama_extract_parses_native_chat_response(client):
    payload = {
        "message": {
            "role": "assistant",
            "content": '{"role_title": "Data Engineer", "skills": ["Python"], "skills_en": ["Python"]}',
        }
    }
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = payload

    with patch("src.llm.ollama_client.requests.post", return_value=mock_response) as post:
        result = client.extract("Job: Data Engineer. Skills: Python.")

    assert result["role_title"] == "Data Engineer"
    assert result["skills"] == ["Python"]
    post.assert_called_once()
    args, kwargs = post.call_args
    assert args[0] == "http://127.0.0.1:11434/api/chat"
    assert kwargs["json"]["model"] == "qwen3.5:latest"
    assert kwargs["json"]["format"] == "json"
    assert kwargs["json"]["think"] is False
    assert kwargs["json"]["keep_alive"] == "10m"
    assert kwargs["json"]["options"]["num_predict"] == 2048
    assert kwargs["allow_redirects"] is False


def test_ollama_extract_connection_error_mentions_serve(client):
    with patch(
        "src.llm.ollama_client.requests.post",
        side_effect=requests.ConnectionError("refused"),
    ):
        with pytest.raises(RuntimeError, match="ollama serve"):
            client.extract("posting")
