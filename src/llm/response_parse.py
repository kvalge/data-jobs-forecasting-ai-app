# response_parse.py
"""Parse assistant JSON content from OpenAI-shaped chat responses."""

from __future__ import annotations

import json


def strip_markdown_fences(text: str) -> str:
    """Remove optional ``` / ```json wrappers some models still return."""
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_message_content(data: dict, model_name: str) -> dict:
    """Extract and parse the assistant JSON object from an API response body."""
    try:
        choices = data["choices"]
        if not choices:
            raise ValueError("no choices in response")
        raw_content = choices[0]["message"]["content"]
    except (KeyError, TypeError, IndexError) as e:
        raise ValueError(
            f"Unexpected OpenRouter response shape for model '{model_name}': {e}"
        ) from e

    if raw_content is None or not isinstance(raw_content, str) or not raw_content.strip():
        raise ValueError(f"Empty or non-string message content from model '{model_name}'")

    text = strip_markdown_fences(raw_content.strip())

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model '{model_name}' returned non-JSON message content: {e}"
        ) from e

    if not isinstance(parsed, dict):
        raise ValueError(
            f"Model '{model_name}' returned JSON {type(parsed).__name__}, expected object"
        )
    return parsed
