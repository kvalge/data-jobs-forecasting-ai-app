from __future__ import annotations

import os

import pytest

import src.config as config


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
