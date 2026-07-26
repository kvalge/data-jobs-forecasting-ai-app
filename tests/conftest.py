from __future__ import annotations

import os

import pytest

import src.config as config


@pytest.fixture
def restore_env():
    """Save and restore required env vars + config module globals after each test."""
    saved_environ = {name: os.environ.get(name) for name in config.REQUIRED_ENV_VARS}
    saved_globals = {
        "OPENROUTER_API_KEY": config.OPENROUTER_API_KEY,
        "DATABASE_URL": config.DATABASE_URL,
        "MODEL": config.MODEL,
        "FALLBACK_MODEL": config.FALLBACK_MODEL,
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
