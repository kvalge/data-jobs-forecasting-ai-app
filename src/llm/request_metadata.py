# request_metadata.py
"""Privacy-safe structured logging for LLM request attempts and validation."""

from __future__ import annotations

import json
import os
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

import src.config as config

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_LOG_PATH = _PROJECT_ROOT / "logs" / "llm_requests.ndjson"

_extract_id: ContextVar[str | None] = ContextVar("llm_extract_id", default=None)
_posting_chars: ContextVar[int | None] = ContextVar("llm_posting_chars", default=None)
_hash_prefix: ContextVar[str | None] = ContextVar("llm_hash_prefix", default=None)


def metadata_logging_enabled() -> bool:
    return bool(getattr(config, "LLM_METADATA_LOG_ENABLED", True))


def metadata_log_path() -> Path:
    raw = (getattr(config, "LLM_METADATA_LOG_PATH", None) or "").strip()
    if raw:
        path = Path(raw)
        return path if path.is_absolute() else _PROJECT_ROOT / path
    return _DEFAULT_LOG_PATH


def begin_extract_context(*, posting_chars: int, content_hash: str | None = None) -> str:
    """Start a correlation id for one extract_and_save attempt (no content stored)."""
    extract_id = uuid.uuid4().hex
    _extract_id.set(extract_id)
    _posting_chars.set(int(posting_chars))
    prefix = (content_hash or "")[:12] or None
    _hash_prefix.set(prefix)
    return extract_id


def clear_extract_context() -> None:
    _extract_id.set(None)
    _posting_chars.set(None)
    _hash_prefix.set(None)


def current_extract_id() -> str | None:
    return _extract_id.get()


def categorize_exception(exc: BaseException) -> str:
    """Map an exception to a coarse error_category (no secrets)."""
    if isinstance(exc, requests.Timeout):
        return "timeout"
    if isinstance(exc, requests.ConnectionError):
        return "connection"
    text = str(exc).lower()
    if "429" in text or "rate limit" in text or "free-tier" in text:
        return "rate_limit"
    if "401" in text or "403" in text or "api key" in text:
        return "api_error"
    if "404" in text or "not found" in text:
        return "api_error"
    if "timed out" in text or "timeout" in text:
        return "timeout"
    if "could not connect" in text or "connection" in text:
        return "connection"
    if "json" in text or "parse" in text or "non-json" in text or "unexpected" in text:
        return "parse_error"
    if "validation" in text or isinstance(exc, (ValueError, TypeError, KeyError)):
        if "schema" in text or "domain" in text or "validation" in text:
            return "validation_failure"
        if "json" in text or "parse" in text:
            return "parse_error"
    if isinstance(exc, RuntimeError) and ("http" in text or "ai " in text):
        return "api_error"
    return "other"


def token_usage_from_openrouter(data: dict[str, Any] | None) -> dict[str, int] | None:
    if not isinstance(data, dict):
        return None
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return None
    out: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = usage.get(key)
        if isinstance(value, int):
            out[key] = value
    return out or None


def token_usage_from_ollama(data: dict[str, Any] | None) -> dict[str, int] | None:
    if not isinstance(data, dict):
        return None
    out: dict[str, int] = {}
    prompt = data.get("prompt_eval_count")
    completion = data.get("eval_count")
    if isinstance(prompt, int):
        out["prompt_tokens"] = prompt
    if isinstance(completion, int):
        out["completion_tokens"] = completion
    if "prompt_tokens" in out or "completion_tokens" in out:
        out["total_tokens"] = out.get("prompt_tokens", 0) + out.get("completion_tokens", 0)
        return out
    return None


def log_llm_request(
    *,
    provider: str,
    model: str,
    status: str,
    response_time_ms: int | None = None,
    token_usage: dict[str, int] | None = None,
    fallback_used: bool = False,
    validation_result: str = "n/a",
    error_category: str | None = None,
    attempt_index: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Append one NDJSON metadata record. Never log prompts or raw responses."""
    if not metadata_logging_enabled():
        return

    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "extract_id": current_extract_id(),
        "provider": provider,
        "model": model,
        "status": status,
        "response_time_ms": response_time_ms,
        "token_usage": token_usage,
        "fallback_used": bool(fallback_used),
        "validation_result": validation_result,
        "error_category": error_category,
        "attempt_index": attempt_index,
        "posting_chars": _posting_chars.get(),
        "content_hash_prefix": _hash_prefix.get(),
    }
    if extra:
        # Allow only explicitly safe scalar extras
        for key, value in extra.items():
            if key in record:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                record[key] = value

    path = metadata_log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        # Metadata logging must never break extraction.
        return


def log_validation_result(*, accepted: bool, error_category: str | None = None) -> None:
    """Record whether post-LLM validation accepted or rejected the payload."""
    log_llm_request(
        provider="validation",
        model="n/a",
        status="success" if accepted else "failure",
        validation_result="accepted" if accepted else "rejected",
        error_category=None if accepted else (error_category or "validation_failure"),
        fallback_used=False,
    )


class timed_llm_call:
    """Context manager that measures elapsed ms for an LLM HTTP attempt."""

    def __init__(self) -> None:
        self.start = 0.0
        self.elapsed_ms = 0

    def __enter__(self) -> timed_llm_call:
        self.start = time.perf_counter()
        return self

    def mark(self) -> int:
        self.elapsed_ms = int((time.perf_counter() - self.start) * 1000)
        return self.elapsed_ms

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.mark()
        return False
