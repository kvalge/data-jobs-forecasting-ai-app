# error_messages.py
"""User-facing explanations for OpenRouter / network LLM failures."""

from __future__ import annotations

import logging
import re

import requests

logger = logging.getLogger(__name__)


def describe_http_status(
    status: int | str,
    model_name: str,
    response: requests.Response | None = None,
) -> str:
    """Human-readable explanation for an HTTP status (no raw provider bodies)."""
    # Keep response available for server logs only — never append provider JSON to users.
    if response is not None:
        try:
            snippet = (response.text or "")[:200]
            logger.info(
                "LLM HTTP %s for model %s; provider body snippet (not shown to user): %s",
                status,
                model_name,
                snippet,
            )
        except Exception:
            pass

    try:
        code = int(status)
    except (TypeError, ValueError):
        return f"Unexpected response from the AI service for model '{model_name}'."

    if code == 401 or code == 403:
        return (
            f"AI service rejected the API key (HTTP {code}). "
            "Check OPENROUTER_API_KEY in your .env file."
        )
    if code == 404:
        return (
            f"AI model '{model_name}' was not found (HTTP 404). "
            "Check MODEL / FALLBACK_MODEL / FALLBACK_MODEL2 / FALLBACK_MODEL3 in .env."
        )
    if code == 429:
        return (
            f"AI rate limit or free-tier quota reached for model '{model_name}' (HTTP 429). "
            "Wait a few minutes and try again, or switch to another model in .env."
        )
    if code in (500, 502, 503, 504):
        return (
            f"AI service is temporarily unavailable for model '{model_name}' (HTTP {code}). "
            "Try again later."
        )
    return f"AI request failed for model '{model_name}' (HTTP {code})."


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
    logger.info("LLM request error for model %s: %s", model_name, type(exc).__name__)
    return f"AI request failed for model '{model_name}'."


def format_llm_failure_for_user(error: BaseException) -> str:
    """Turn a raw LLM RuntimeError into a clearer flash/CLI message."""
    text = str(error).strip()
    logger.info("LLM failure for user mapping: %s", text[:500])
    if not text:
        return "The AI service failed. Please try again."

    lower = text.lower()

    if "ollama" in lower and ("timed out" in lower or "timeout" in lower):
        return (
            "OpenRouter failed and local Ollama timed out. "
            "Raise OLLAMA_TIMEOUT_SECONDS, keep the model loaded, "
            "or switch OLLAMA_MODEL to a faster model."
        )
    if "ollama" in lower and ("could not connect" in lower or "ollama serve" in lower):
        return (
            "OpenRouter failed and local Ollama was unreachable. "
            "Start Ollama (ollama serve), confirm OLLAMA_BASE_URL, "
            "and that OLLAMA_MODEL is pulled (e.g. ollama pull qwen3.5:latest)."
        )
    if "HTTP 429" in text or "rate limit" in lower or "free-tier" in lower:
        if "ollama" in lower:
            return (
                "OpenRouter free-tier/rate limit was reached and the local Ollama fallback "
                "also failed. Check Ollama is running with OLLAMA_MODEL pulled "
                "(e.g. qwen3.5:latest)."
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
    if "timed out" in lower:
        if "ollama" in lower:
            return (
                "Local Ollama timed out. Raise OLLAMA_TIMEOUT_SECONDS or use a faster model."
            )
        return "AI request timed out. Check your internet connection and try again."
    if "Could not connect" in text or "ConnectionError" in text:
        if "ollama" in lower:
            return (
                "Could not connect to local Ollama. Start it with ollama serve "
                "and check OLLAMA_BASE_URL."
            )
        return "Could not connect to the AI service. Check your internet connection and try again."
    if "not found" in lower and "HTTP 404" in text:
        return (
            "One or more AI models were not found. "
            "Check MODEL / FALLBACK_MODEL / FALLBACK_MODEL2 / FALLBACK_MODEL3 in your .env file."
        )
    if "temporarily unavailable" in lower or re.search(r"HTTP 50[0-4]", text):
        return "AI service is temporarily unavailable. Please try again later."

    if (
        text.startswith("Both primary")
        or text.startswith("All configured AI models failed")
        or "All OpenRouter models failed" in text
    ):
        return (
            "AI extraction failed for all configured models. "
            "Check MODEL / fallbacks, Ollama settings, and try again."
        )
    # Avoid dumping long internal exception chains to the UI.
    return "AI extraction failed. Please try again or check the application logs."


def format_db_error_for_user(error: BaseException) -> str:
    """Stable UI/CLI message for database failures (details stay in logs)."""
    logger.exception("Database error: %s", error)
    return "A database error occurred. Please try again or check the application logs."


def format_validation_error_for_user(error: BaseException, *, context: str = "Request") -> str:
    """Show short domain validation messages; truncate unexpectedly long text."""
    text = str(error).strip() or "Invalid input."
    if len(text) > 240:
        logger.info("Truncating long validation error: %s", text[:500])
        text = text[:237] + "..."
    return f"{context} failed: {text}"
