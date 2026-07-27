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
            f"Check MODEL / FALLBACK_MODEL / FALLBACK_MODEL2 / FALLBACK_MODEL3 in .env.{suffix}"
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
        if "ollama" in model_name.lower():
            return (
                f"Local Ollama timed out for model '{model_name}'. "
                "Raise OLLAMA_TIMEOUT_SECONDS, keep Ollama warm (ollama run …), "
                "or use a smaller/faster model."
            )
        return (
            f"AI request timed out for model '{model_name}'. "
            "Check your internet connection and try again."
        )
    if isinstance(exc, requests.ConnectionError):
        if "ollama" in model_name.lower():
            return (
                f"Could not connect to local Ollama for model '{model_name}'. "
                "Start Ollama (ollama serve) and confirm OLLAMA_BASE_URL."
            )
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
    if "ollama" in text.lower() and (
        "timed out" in text.lower() or "timeout" in text.lower()
    ):
        return (
            "OpenRouter failed and local Ollama timed out. "
            "Raise OLLAMA_TIMEOUT_SECONDS (e.g. 300–600), keep the model loaded, "
            "or switch OLLAMA_MODEL to a faster model."
        )
    if "ollama" in text.lower() and (
        "Could not connect" in text or "ollama serve" in text.lower()
    ):
        return (
            "OpenRouter failed and local Ollama was unreachable. "
            "Start Ollama (ollama serve), confirm OLLAMA_BASE_URL, "
            "and that OLLAMA_MODEL is pulled (e.g. ollama pull qwen3.5:latest)."
        )
    if "HTTP 429" in text or "rate limit" in text.lower() or "free-tier" in text.lower():
        if "ollama" in text.lower():
            # Keep a short Ollama-specific tail from the combined error when present.
            ollama_tail = ""
            lower = text.lower()
            idx = lower.rfind("ollama")
            if idx >= 0:
                ollama_tail = " Details: " + text[idx:].strip()[:240]
            return (
                "OpenRouter free-tier/rate limit was reached and the local Ollama fallback "
                "also failed. Check Ollama is running with OLLAMA_MODEL pulled "
                f"(e.g. qwen3.5:latest).{ollama_tail}"
            )
        return (
            "AI rate limit or free-tier quota reached on OpenRouter. "
            "The app will try local Ollama next when enabled; if you still see this, "
            "check Ollama is running or wait and retry. "
            "Models: MODEL / FALLBACK_MODEL / FALLBACK_MODEL2 / FALLBACK_MODEL3."
        )
    if "HTTP 401" in text or "HTTP 403" in text or "API key" in text:
        return (
            "AI service rejected the API key. "
            "Check OPENROUTER_API_KEY in your .env file."
        )
    if "timed out" in text.lower():
        if "ollama" in text.lower():
            return (
                "Local Ollama timed out. Raise OLLAMA_TIMEOUT_SECONDS or use a faster model."
            )
        return "AI request timed out. Check your internet connection and try again."
    if "Could not connect" in text or "ConnectionError" in text:
        if "ollama" in text.lower():
            return (
                "Could not connect to local Ollama. Start it with ollama serve "
                "and check OLLAMA_BASE_URL."
            )
        return "Could not connect to the AI service. Check your internet connection and try again."
    if "not found" in text.lower() and "HTTP 404" in text:
        return (
            "One or more AI models were not found. "
            "Check MODEL / FALLBACK_MODEL / FALLBACK_MODEL2 / FALLBACK_MODEL3 in your .env file."
        )
    if "temporarily unavailable" in text.lower() or re.search(r"HTTP 50[0-4]", text):
        return "AI service is temporarily unavailable. Please try again later."

    # Already user-friendly from describe_*; keep as-is but shorten multi-failure prefix
    if text.startswith("Both primary") or text.startswith("All configured AI models failed"):
        return "AI extraction failed for all configured models. " + text
    return text
