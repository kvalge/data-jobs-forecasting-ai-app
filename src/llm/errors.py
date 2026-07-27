# errors.py
"""Shared LLM error types for model-chain fallback (not programming bugs)."""

from __future__ import annotations

import json

import requests

# Provider/API/parse failures that justify trying the next model.
# Do NOT include TypeError / KeyError / IndexError — those are usually bugs.
RECOVERABLE_LLM_ERRORS: tuple[type[BaseException], ...] = (
    requests.RequestException,
    ValueError,
    json.JSONDecodeError,
    RuntimeError,
)


class OpenRouterChainExhausted(RuntimeError):
    """Raised when every configured OpenRouter model failed recoverably."""

    def __init__(self, detail: str, *, models_tried: int) -> None:
        self.detail = detail
        self.models_tried = models_tried
        super().__init__(
            f"All configured AI models failed ({models_tried} tried). {detail}"
        )
