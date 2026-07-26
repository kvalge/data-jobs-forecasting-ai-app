"""Tests for user-facing LLM error messages."""

from unittest.mock import MagicMock

import requests

from src.llm.error_messages import (
    describe_http_status,
    describe_request_exception,
    format_llm_failure_for_user,
)


def test_describe_http_429():
    message = describe_http_status(429, "some/model:free")
    assert "rate limit" in message.lower() or "free-tier" in message.lower()
    assert "429" in message


def test_describe_http_401():
    message = describe_http_status(401, "some/model")
    assert "API key" in message


def test_describe_timeout():
    message = describe_request_exception(requests.Timeout(), "m")
    assert "timed out" in message.lower()


def test_format_combined_429_for_ui():
    err = RuntimeError(
        "Both primary and fallback AI models failed. "
        "Primary (a): AI rate limit or free-tier quota reached for model 'a' (HTTP 429). "
        "Fallback (b): AI rate limit or free-tier quota reached for model 'b' (HTTP 429)."
    )
    message = format_llm_failure_for_user(err)
    assert "rate limit" in message.lower() or "free-tier" in message.lower()
    assert "Both primary (nvidia" not in message


def test_describe_includes_provider_hint():
    response = MagicMock()
    response.json.return_value = {"error": {"message": "Rate limit exceeded: free-models-per-day"}}
    message = describe_http_status(429, "model", response)
    assert "free-models-per-day" in message
