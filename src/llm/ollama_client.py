# ollama_client.py
"""Local Ollama client for extraction (fallback or ollama_only mode)."""

from __future__ import annotations

import json
import logging

import requests

import src.config as config
from src.llm.base_llm_client import BaseLLMClient
from src.llm.error_messages import describe_http_status, describe_request_exception
from src.llm.extract_validate import assert_extraction_usable
from src.llm.ollama_url import validate_ollama_base_url
from src.llm.prompts import EXTRACTION_SYSTEM_PROMPT
from src.llm.request_metadata import (
    categorize_exception,
    log_llm_request,
    timed_llm_call,
    token_usage_from_ollama,
)
from src.llm.response_parse import parse_message_content

logger = logging.getLogger(__name__)


class OllamaClient(BaseLLMClient):
    """Call a local Ollama model via the native /api/chat endpoint."""

    def extract(
        self,
        posting_text: str,
        *,
        fallback_used: bool = False,
        attempt_index: int = 0,
    ) -> dict:
        model_name = (config.OLLAMA_MODEL or "").strip()
        if not model_name:
            raise ValueError("OLLAMA_MODEL is missing or empty")

        base = validate_ollama_base_url(
            config.OLLAMA_BASE_URL or "http://127.0.0.1:11434",
            allow_remote=bool(config.OLLAMA_ALLOW_REMOTE),
        )
        url = f"{base}/api/chat"

        max_tokens = int(getattr(config, "LLM_MAX_TOKENS", 2048) or 2048)
        keep_alive = (getattr(config, "OLLAMA_KEEP_ALIVE", None) or "10m").strip() or "10m"
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": posting_text},
            ],
            "format": "json",
            "stream": False,
            # Qwen3.x defaults to long chain-of-thought; that blows past timeouts.
            "think": False,
            "keep_alive": keep_alive,
            "options": {
                "num_predict": max_tokens,
            },
        }

        timeout = config.OLLAMA_TIMEOUT_SECONDS
        mode = getattr(config, "LLM_PROVIDER_MODE", "")
        if str(mode).lower() in ("ollama_only", "ollama"):
            logger.info("Using Ollama-only mode with model %s at %s", model_name, url)
        else:
            logger.info(
                "OpenRouter exhausted; trying Ollama model %s at %s", model_name, url
            )

        with timed_llm_call() as timer:
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=timeout,
                    allow_redirects=False,
                )
                response.raise_for_status()
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else "unknown"
                err = RuntimeError(
                    describe_http_status(status, f"ollama/{model_name}", e.response)
                )
                log_llm_request(
                    provider="ollama",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category=categorize_exception(err),
                )
                raise err from e
            except requests.RequestException as e:
                err = RuntimeError(
                    describe_request_exception(e, f"ollama/{model_name}")
                    + " Is Ollama running (ollama serve)?"
                )
                log_llm_request(
                    provider="ollama",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category=categorize_exception(e),
                )
                raise err from e

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                err = ValueError(
                    f"Ollama returned non-JSON body for model '{model_name}'"
                )
                log_llm_request(
                    provider="ollama",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category="parse_error",
                )
                raise err from e

            try:
                content = data["message"]["content"]
            except (KeyError, TypeError) as e:
                err = ValueError(
                    f"Unexpected Ollama response shape for model '{model_name}': {e}"
                )
                log_llm_request(
                    provider="ollama",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    token_usage=token_usage_from_ollama(data),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category="parse_error",
                )
                raise err from e

            openai_shaped = {"choices": [{"message": {"content": content}}]}
            try:
                parsed = parse_message_content(
                    openai_shaped, f"ollama/{model_name}"
                )
                parsed = assert_extraction_usable(parsed)
            except Exception as e:
                log_llm_request(
                    provider="ollama",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    token_usage=token_usage_from_ollama(data),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category=categorize_exception(e),
                )
                raise

        log_llm_request(
            provider="ollama",
            model=model_name,
            status="success",
            response_time_ms=timer.elapsed_ms,
            token_usage=token_usage_from_ollama(data),
            fallback_used=fallback_used,
            attempt_index=attempt_index,
        )
        return parsed
