# openrouter_client.py
import json

import requests

import src.config as config
from src.llm.base_llm_client import BaseLLMClient
from src.llm.error_messages import describe_http_status, describe_request_exception
from src.llm.errors import OpenRouterChainExhausted, RECOVERABLE_LLM_ERRORS
from src.llm.extract_validate import assert_extraction_usable
from src.llm.prompts import EXTRACTION_SYSTEM_PROMPT
from src.llm.request_metadata import (
    categorize_exception,
    log_llm_request,
    timed_llm_call,
    token_usage_from_openrouter,
)
from src.llm.response_parse import parse_message_content

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Re-export for callers that historically imported from this module.
__all__ = ["OPENROUTER_URL", "EXTRACTION_SYSTEM_PROMPT", "OpenRouterClient"]


def _is_rate_limit_error(err: BaseException) -> bool:
    return categorize_exception(err) == "rate_limit"


def _should_shortcircuit_openrouter(err: BaseException) -> bool:
    """Skip remaining OpenRouter models when further free-tier tries are unlikely to help."""
    category = categorize_exception(err)
    if category == "rate_limit" and bool(
        getattr(config, "OPENROUTER_SHORTCIRCUIT_ON_RATE_LIMIT", True)
    ):
        return True
    if category == "parse_error" and bool(
        getattr(config, "OPENROUTER_SHORTCIRCUIT_ON_PARSE_ERROR", True)
    ):
        return True
    if category == "timeout" and bool(
        getattr(config, "OPENROUTER_SHORTCIRCUIT_ON_TIMEOUT", True)
    ):
        return True
    return False


class OpenRouterClient(BaseLLMClient):
    """LLM client for the OpenRouter API (model chain only; no Ollama nesting)."""

    def _call_model(
        self,
        model_name: str | None,
        posting_text: str,
        *,
        fallback_used: bool = False,
        attempt_index: int = 0,
    ) -> dict:
        if not model_name or not str(model_name).strip():
            raise ValueError("Model name is missing or empty")

        headers = {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        max_tokens = int(getattr(config, "LLM_MAX_TOKENS", 1024) or 1024)
        timeout = int(getattr(config, "OPENROUTER_TIMEOUT_SECONDS", 30) or 30)
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": posting_text},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
        }

        with timed_llm_call() as timer:
            try:
                response = requests.post(
                    OPENROUTER_URL, headers=headers, json=payload, timeout=timeout
                )
                response.raise_for_status()
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else "unknown"
                err = RuntimeError(describe_http_status(status, model_name, e.response))
                log_llm_request(
                    provider="openrouter",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category=categorize_exception(err),
                )
                raise err from e
            except requests.RequestException as e:
                err = RuntimeError(describe_request_exception(e, model_name))
                log_llm_request(
                    provider="openrouter",
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
                    f"OpenRouter returned non-JSON body for model '{model_name}'"
                )
                log_llm_request(
                    provider="openrouter",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category="parse_error",
                )
                raise err from e

            try:
                parsed = parse_message_content(data, model_name)
                parsed = assert_extraction_usable(parsed)
            except Exception as e:
                log_llm_request(
                    provider="openrouter",
                    model=model_name,
                    status="failure",
                    response_time_ms=timer.mark(),
                    token_usage=token_usage_from_openrouter(data),
                    fallback_used=fallback_used,
                    attempt_index=attempt_index,
                    error_category=categorize_exception(e),
                )
                raise

        log_llm_request(
            provider="openrouter",
            model=model_name,
            status="success",
            response_time_ms=timer.elapsed_ms,
            token_usage=token_usage_from_openrouter(data),
            fallback_used=fallback_used,
            attempt_index=attempt_index,
        )
        return parsed

    def extract(self, posting_text: str) -> dict:
        """Try each configured OpenRouter model until one succeeds.

        Ollama fallback is composed in OpenRouterWithOllamaFallback (factory), not here.
        """
        models = config.llm_model_chain()
        if not models:
            raise ValueError("No LLM models configured")

        errors: list[str] = []
        last_error: BaseException | None = None
        models_attempted = 0
        for index, model_name in enumerate(models):
            models_attempted = index + 1
            try:
                return self._call_model(
                    model_name,
                    posting_text,
                    fallback_used=index > 0,
                    attempt_index=index,
                )
            except RECOVERABLE_LLM_ERRORS as err:
                last_error = err
                errors.append(f"{model_name}: {err}")
                if _should_shortcircuit_openrouter(err):
                    reason = categorize_exception(err)
                    for skipped_name in models[index + 1 :]:
                        errors.append(f"{skipped_name}: skipped after {reason}")
                    break
                continue

        detail = "; ".join(errors)
        raise OpenRouterChainExhausted(
            detail, models_tried=models_attempted
        ) from last_error
