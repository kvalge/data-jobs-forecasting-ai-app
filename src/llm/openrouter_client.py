# openrouter_client.py
import json

import requests

import src.config as config
from src.llm.base_llm_client import BaseLLMClient
from src.llm.error_messages import describe_http_status, describe_request_exception
from src.llm.errors import OpenRouterChainExhausted, RECOVERABLE_LLM_ERRORS
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
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": posting_text},
            ],
            "response_format": {"type": "json_object"},
        }

        with timed_llm_call() as timer:
            try:
                response = requests.post(
                    OPENROUTER_URL, headers=headers, json=payload, timeout=30
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
        for index, model_name in enumerate(models):
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
                continue

        detail = "; ".join(errors)
        raise OpenRouterChainExhausted(detail, models_tried=len(models)) from last_error
