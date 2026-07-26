# posting_ingest.py
"""Shared entry point for ingesting job posting text (CLI and web)."""

from sqlalchemy.exc import SQLAlchemyError

from src.bll.extraction_service import ExtractAndSaveResult, ExtractionService
from src.dal.job_posting_repository import JobPostingRepository
from src.dal.session import session_scope


def ingest_posting_text(text: str) -> ExtractAndSaveResult:
    """Validate text, extract via LLM, and persist. Raises on expected failures.

    Raises:
        ValueError: empty text, or extraction/domain validation failure
        RuntimeError: LLM request failure
        SQLAlchemyError: database failure
    """
    posting_text = (text or "").strip()
    if not posting_text:
        raise ValueError("Posting text is empty")

    with session_scope() as session:
        repository = JobPostingRepository(session)
        service = ExtractionService(repository)
        return service.extract_and_save(posting_text)


# Re-export for callers that want a single import for DB errors
__all__ = ["ingest_posting_text", "ExtractAndSaveResult", "SQLAlchemyError"]
