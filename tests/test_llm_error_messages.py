"""Tests for user-facing LLM error messages."""

from unittest.mock import MagicMock

import requests

from src.llm.error_messages import (
    describe_http_status,
    describe_request_exception,
    format_db_error_for_user,
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
        "All configured AI models failed (4 tried). "
        "a: AI rate limit or free-tier quota reached for model 'a' (HTTP 429); "
        "b: AI rate limit or free-tier quota reached for model 'b' (HTTP 429)."
    )
    message = format_llm_failure_for_user(err)
    assert "rate limit" in message.lower() or "free-tier" in message.lower()
    assert "FALLBACK_MODEL2" in message or "configured models" in message.lower()


def test_describe_does_not_append_provider_body_to_user_message():
    response = MagicMock()
    response.text = '{"error":{"message":"Rate limit exceeded: free-models-per-day secret-token"}}'
    response.json.return_value = {
        "error": {"message": "Rate limit exceeded: free-models-per-day secret-token"}
    }
    message = describe_http_status(429, "model", response)
    assert "secret-token" not in message
    assert "Provider note" not in message


def test_format_db_error_hides_details():
    message = format_db_error_for_user(RuntimeError("DETAIL: password=hunter2"))
    assert "hunter2" not in message
    assert "database" in message.lower()
