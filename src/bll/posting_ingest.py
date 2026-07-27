# posting_ingest.py
"""Shared entry point for ingesting job posting text (CLI and web)."""

from sqlalchemy.exc import SQLAlchemyError

import src.config as config
from src.bll.extraction_service import ExtractAndSaveResult, ExtractionService
from src.dal.job_posting_repository import JobPostingRepository
from src.dal.session import session_scope


def _enforce_posting_size(posting_text: str) -> None:
    """Reject oversized text before opening a DB session or calling any LLM."""
    max_chars = int(config.MAX_POSTING_CHARS)
    length = len(posting_text)
    if length > max_chars:
        raise ValueError(
            f"Posting text is too long ({length} characters). "
            f"Maximum allowed is {max_chars} characters "
            "(set MAX_POSTING_CHARS in .env to adjust)."
        )


def ingest_posting_text(text: str) -> ExtractAndSaveResult:
    """Validate text, extract via LLM, and persist. Raises on expected failures.

    Uses short DB sessions for hash lookup and save only — the LLM call runs with
    no open session so pool connections are not held for OpenRouter/Ollama latency.

    Raises:
        ValueError: empty text, oversized text, or extraction/domain validation failure
        RuntimeError: LLM request failure
        SQLAlchemyError: database failure
    """
    posting_text = (text or "").strip()
    if not posting_text:
        raise ValueError("Posting text is empty")

    _enforce_posting_size(posting_text)

    service = ExtractionService()

    with session_scope() as session:
        existing = service.find_by_content_hash(
            JobPostingRepository(session), posting_text
        )
        if existing is not None:
            return ExtractAndSaveResult(entity=existing, created=False)

    # LLM outside any DB session (no idle-in-transaction while waiting on the provider).
    entity = service.extract_entity(posting_text)

    with session_scope() as session:
        return service.save_extracted(JobPostingRepository(session), entity)


# Re-export for callers that want a single import for DB errors
__all__ = ["ingest_posting_text", "ExtractAndSaveResult", "SQLAlchemyError"]
