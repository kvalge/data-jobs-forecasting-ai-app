# extract_validate.py
"""Validate LLM JSON so bad payloads can rotate to the next model."""

from __future__ import annotations

from pydantic import ValidationError

from src.dto.job_posting_extraction_dto import JobPostingExtractionDTO


def assert_extraction_usable(parsed: dict) -> dict:
    """Schema + domain check. Raise ValueError if the payload must not be persisted.

    ValueError is in RECOVERABLE_LLM_ERRORS so OpenRouter/Ollama chains can try
    the next model instead of failing the whole ingest on junk JSON
    (e.g. ``{'': {}}`` / missing ``role_title``).

    Returns the original dict after checks succeed. ExtractionService still
    re-validates before building the domain entity (defense in depth).
    """
    if not isinstance(parsed, dict):
        raise ValueError(
            f"LLM output failed schema validation: expected object, got {type(parsed).__name__}"
        )
    try:
        dto = JobPostingExtractionDTO(**parsed)
    except ValidationError as e:
        raise ValueError(f"LLM output failed schema validation: {e}") from e

    # Domain rules live in BLL; imported here so model-chain retry can treat
    # domain failures as recoverable without a second HTTP round-trip later.
    from src.bll.job_posting_validator import validate_extraction_dto

    try:
        validate_extraction_dto(dto)
    except ValueError as e:
        raise ValueError(f"LLM output failed domain validation: {e}") from e
    return parsed
