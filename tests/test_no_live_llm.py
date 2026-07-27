"""Guard that the test suite cannot accidentally call live LLM HTTP."""

import pytest
import requests


def test_block_live_openrouter_http():
    with pytest.raises(RuntimeError, match="OpenRouter"):
        requests.post("https://openrouter.ai/api/v1/chat/completions", timeout=1)


def test_block_live_ollama_http():
    with pytest.raises(RuntimeError, match="Ollama"):
        requests.post("http://127.0.0.1:11434/api/chat", json={}, timeout=1)
