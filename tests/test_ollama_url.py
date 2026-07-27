"""Tests for OLLAMA_BASE_URL SSRF allowlist."""

import os

import pytest

import src.config as config
from src.llm.ollama_url import validate_ollama_base_url


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:11434",
        "http://localhost:11434",
        "http://[::1]:11434",
        "https://127.0.0.1:11434",
    ],
)
def test_validate_ollama_accepts_loopback(url):
    assert validate_ollama_base_url(url) == url.rstrip("/")


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254/",
        "http://192.168.1.10:11434",
        "http://10.0.0.5",
        "http://example.com:11434",
        "file:///etc/passwd",
        "http://user:pass@127.0.0.1:11434",
        "http://127.0.0.1:11434?x=1",
        "ftp://127.0.0.1:11434",
        "",
    ],
)
def test_validate_ollama_rejects_unsafe_by_default(url):
    with pytest.raises(EnvironmentError):
        validate_ollama_base_url(url, allow_remote=False)


def test_validate_ollama_allows_remote_when_opted_in():
    assert (
        validate_ollama_base_url(
            "http://ollama.internal:11434",
            allow_remote=True,
        )
        == "http://ollama.internal:11434"
    )


def test_validate_ollama_still_rejects_bad_scheme_when_remote_allowed():
    with pytest.raises(EnvironmentError, match="http or https"):
        validate_ollama_base_url("file:///tmp", allow_remote=True)


@pytest.mark.usefixtures("restore_env")
def test_validate_config_rejects_non_loopback_ollama_url():
    os.environ["OPENROUTER_API_KEY"] = "test-key"
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://u:p@localhost/db"
    os.environ["MODEL"] = "primary-model"
    os.environ["FALLBACK_MODEL"] = "fallback-model"
    os.environ["OLLAMA_BASE_URL"] = "http://169.254.169.254/"
    os.environ.pop("OLLAMA_ALLOW_REMOTE", None)

    with pytest.raises(EnvironmentError, match="loopback"):
        config.validate_config()


@pytest.mark.usefixtures("restore_env")
def test_validate_config_accepts_remote_with_opt_in():
    os.environ["OPENROUTER_API_KEY"] = "test-key"
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://u:p@localhost/db"
    os.environ["MODEL"] = "primary-model"
    os.environ["FALLBACK_MODEL"] = "fallback-model"
    os.environ["OLLAMA_BASE_URL"] = "http://ollama.lab:11434"
    os.environ["OLLAMA_ALLOW_REMOTE"] = "true"

    config.validate_config()
    assert config.OLLAMA_BASE_URL == "http://ollama.lab:11434"
    assert config.OLLAMA_ALLOW_REMOTE is True
