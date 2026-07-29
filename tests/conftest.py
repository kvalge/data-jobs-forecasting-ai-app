from __future__ import annotations

import os

import pytest
import requests

import src.config as config


@pytest.fixture(autouse=True)
def block_live_llm_http(monkeypatch):
    """Fail fast if a test accidentally hits OpenRouter or local Ollama."""
    real_request = requests.sessions.Session.request

    def guarded(self, method, url, *args, **kwargs):
        url_s = str(url).lower()
        if "openrouter.ai" in url_s:
            raise RuntimeError(
                "Live OpenRouter HTTP is forbidden in tests — mock the client HTTP call"
            )
        if ":11434" in url_s or "/api/chat" in url_s:
            raise RuntimeError(
                "Live Ollama HTTP is forbidden in tests — mock the client HTTP call"
            )
        return real_request(self, method, url, *args, **kwargs)

    monkeypatch.setattr(requests.sessions.Session, "request", guarded)


@pytest.fixture
def restore_env():
    """Save and restore required env vars + config module globals after each test."""
    saved_environ = {
        name: os.environ.get(name)
        for name in (
            *config.ALWAYS_REQUIRED_ENV_VARS,
            *config.OPENROUTER_REQUIRED_ENV_VARS,
            "LLM_PROVIDER_MODE",
            "PREDICTION_DATA_SOURCE",
            "FALLBACK_MODEL2",
            "FALLBACK_MODEL3",
            "OLLAMA_MODEL",
            "OLLAMA_BASE_URL",
            "OLLAMA_ALLOW_REMOTE",
            "OLLAMA_TIMEOUT_SECONDS",
            "OLLAMA_KEEP_ALIVE",
            "OPENROUTER_TIMEOUT_SECONDS",
            "LLM_MAX_TOKENS",
            "OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT",
            "OPENROUTER_SHORTCIRCUIT_ON_PARSE_ERROR",
            "OPENROUTER_SHORTCIRCUIT_ON_TIMEOUT",
            "MAX_POSTING_CHARS",
        )
    }
    saved_globals = {
        "OPENROUTER_API_KEY": config.OPENROUTER_API_KEY,
        "DATABASE_URL": config.DATABASE_URL,
        "MODEL": config.MODEL,
        "FALLBACK_MODEL": config.FALLBACK_MODEL,
        "FALLBACK_MODEL2": config.FALLBACK_MODEL2,
        "FALLBACK_MODEL3": config.FALLBACK_MODEL3,
        "LLM_PROVIDER_MODE": config.LLM_PROVIDER_MODE,
        "PREDICTION_DATA_SOURCE": config.PREDICTION_DATA_SOURCE,
        "OLLAMA_MODEL": config.OLLAMA_MODEL,
        "OLLAMA_BASE_URL": config.OLLAMA_BASE_URL,
        "OLLAMA_TIMEOUT_SECONDS": config.OLLAMA_TIMEOUT_SECONDS,
        "OLLAMA_KEEP_ALIVE": getattr(config, "OLLAMA_KEEP_ALIVE", "10m"),
        "OPENROUTER_TIMEOUT_SECONDS": getattr(config, "OPENROUTER_TIMEOUT_SECONDS", 30),
        "LLM_MAX_TOKENS": getattr(config, "LLM_MAX_TOKENS", 1024),
        "OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT": getattr(
            config, "OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT", True
        ),
        "OPENROUTER_SHORTCIRCUIT_ON_PARSE_ERROR": getattr(
            config, "OPENROUTER_SHORTCIRCUIT_ON_PARSE_ERROR", True
        ),
        "OPENROUTER_SHORTCIRCUIT_ON_TIMEOUT": getattr(
            config, "OPENROUTER_SHORTCIRCUIT_ON_TIMEOUT", True
        ),
    }
    yield
    for name, value in saved_environ.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
    config.OPENROUTER_API_KEY = saved_globals["OPENROUTER_API_KEY"]
    config.DATABASE_URL = saved_globals["DATABASE_URL"]
    config.MODEL = saved_globals["MODEL"]
    config.FALLBACK_MODEL = saved_globals["FALLBACK_MODEL"]
    config.FALLBACK_MODEL2 = saved_globals["FALLBACK_MODEL2"]
    config.FALLBACK_MODEL3 = saved_globals["FALLBACK_MODEL3"]
    config.LLM_PROVIDER_MODE = saved_globals["LLM_PROVIDER_MODE"]
    config.PREDICTION_DATA_SOURCE = saved_globals["PREDICTION_DATA_SOURCE"]
    config.OLLAMA_MODEL = saved_globals["OLLAMA_MODEL"]
    config.OLLAMA_BASE_URL = saved_globals["OLLAMA_BASE_URL"]
    config.OLLAMA_TIMEOUT_SECONDS = saved_globals["OLLAMA_TIMEOUT_SECONDS"]
    config.OLLAMA_KEEP_ALIVE = saved_globals["OLLAMA_KEEP_ALIVE"]
    config.OPENROUTER_TIMEOUT_SECONDS = saved_globals["OPENROUTER_TIMEOUT_SECONDS"]
    config.LLM_MAX_TOKENS = saved_globals["LLM_MAX_TOKENS"]
    config.OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT = saved_globals[
        "OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT"
    ]
    config.OPENROUTER_SHORTCIRCUIT_ON_PARSE_ERROR = saved_globals[
        "OPENROUTER_SHORTCIRCUIT_ON_PARSE_ERROR"
    ]
    config.OPENROUTER_SHORTCIRCUIT_ON_TIMEOUT = saved_globals[
        "OPENROUTER_SHORTCIRCUIT_ON_TIMEOUT"
    ]