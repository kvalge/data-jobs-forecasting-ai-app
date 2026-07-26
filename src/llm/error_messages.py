# error_messages.py
"""User-facing explanations for OpenRouter / network LLM failures."""

from __future__ import annotations

import json
import re

import requests


def _provider_hint(response: requests.Response | None) -> str:
    """Best-effort short hint from OpenRouter error JSON (no secrets)."""
    if response is None:
        return ""
    try:
        payload = response.json()
    except (ValueError, json.JSONDecodeError):
        return ""

    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            # Keep short; avoid dumping huge bodies
            return message.strip()[:200]
    if isinstance(error, str) and error.strip():
        return error.strip()[:200]
    return ""


def describe_http_status(status: int | str, model_name: str, response: requests.Response | None = None) -> str:
    """Human-readable explanation for an OpenRouter HTTP status."""
    hint = _provider_hint(response)
    suffix = f" Provider note: {hint}" if hint else ""

    try:
        code = int(status)
    except (TypeError, ValueError):
        return f"Unexpected response from the AI service for model '{model_name}'.{suffix}"

    if code == 401 or code == 403:
        return (
            f"AI service rejected the API key (HTTP {code}). "
            f"Check OPENROUTER_API_KEY in your .env file.{suffix}"
        )
    if code == 404:
        return (
            f"AI model '{model_name}' was not found (HTTP 404). "
            f"Check MODEL / FALLBACK_MODEL in .env.{suffix}"
        )
    if code == 429:
        return (
            f"AI rate limit or free-tier quota reached for model '{model_name}' (HTTP 429). "
            f"Wait a few minutes and try again, or switch to another model in .env.{suffix}"
        )
    if code in (500, 502, 503, 504):
        return (
            f"AI service is temporarily unavailable for model '{model_name}' (HTTP {code}). "
            f"Try again later.{suffix}"
        )
    return f"AI request failed for model '{model_name}' (HTTP {code}).{suffix}"


def describe_request_exception(exc: BaseException, model_name: str) -> str:
    """Human-readable explanation for connection/timeouts and other request errors."""
    if isinstance(exc, requests.Timeout):
        return (
            f"AI request timed out for model '{model_name}'. "
            "Check your internet connection and try again."
        )
    if isinstance(exc, requests.ConnectionError):
        return (
            f"Could not connect to the AI service for model '{model_name}'. "
            "Check your internet connection and try again."
        )
    if isinstance(exc, requests.HTTPError):
        status = exc.response.status_code if exc.response is not None else "unknown"
        return describe_http_status(status, model_name, exc.response)
    return f"AI request failed for model '{model_name}': {exc}"


def format_llm_failure_for_user(error: BaseException) -> str:
    """Turn a raw LLM RuntimeError into a clearer flash/CLI message."""
    text = str(error).strip()
    if not text:
        return "The AI service failed. Please try again."

    # Prefer the most actionable signal in combined primary+fallback errors
    if "HTTP 429" in text or "rate limit" in text.lower() or "free-tier" in text.lower():
        return (
            "AI rate limit or free-tier quota reached (both primary and fallback models). "
            "Wait a few minutes and try again, or change MODEL / FALLBACK_MODEL in .env."
        )
    if "HTTP 401" in text or "HTTP 403" in text or "API key" in text:
        return (
            "AI service rejected the API key. "
            "Check OPENROUTER_API_KEY in your .env file."
        )
    if "timed out" in text.lower():
        return "AI request timed out. Check your internet connection and try again."
    if "Could not connect" in text or "ConnectionError" in text:
        return "Could not connect to the AI service. Check your internet connection and try again."
    if "not found" in text.lower() and "HTTP 404" in text:
        return (
            "One or both AI models were not found. "
            "Check MODEL and FALLBACK_MODEL in your .env file."
        )
    if "temporarily unavailable" in text.lower() or re.search(r"HTTP 50[0-4]", text):
        return "AI service is temporarily unavailable. Please try again later."

    # Already user-friendly from describe_*; keep as-is but shorten double-failure prefix
    if text.startswith("Both primary"):
        return (
            "AI extraction failed for both primary and fallback models. " + text
        )
    return text
