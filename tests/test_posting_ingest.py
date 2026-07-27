"""Tests for posting size cap and session/LLM boundaries on ingest."""

from unittest.mock import MagicMock

import pytest

from src.bll import posting_ingest
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.posting_hash import hash_posting_text


def test_ingest_rejects_empty_text():
    with pytest.raises(ValueError, match="empty"):
        posting_ingest.ingest_posting_text("   ")


def test_ingest_rejects_oversized_text_before_llm(monkeypatch):
    monkeypatch.setattr(posting_ingest.config, "MAX_POSTING_CHARS", 50)
    session_opened = MagicMock()

    def fake_scope():
        session_opened()
        raise AssertionError("session_scope must not run for oversized text")

    monkeypatch.setattr(posting_ingest, "session_scope", fake_scope)

    with pytest.raises(ValueError, match="too long"):
        posting_ingest.ingest_posting_text("x" * 51)

    session_opened.assert_not_called()


def test_ingest_allows_text_at_limit_and_calls_extract(monkeypatch):
    monkeypatch.setattr(posting_ingest.config, "MAX_POSTING_CHARS", 40)
    text = "y" * 40

    class FakeScope:
        def __enter__(self):
            return MagicMock()

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(posting_ingest, "session_scope", lambda: FakeScope())
    monkeypatch.setattr(posting_ingest, "JobPostingRepository", MagicMock())

    service = MagicMock()
    service.find_by_content_hash.return_value = None
    entity = JobPostingEntity(role_title="Dev", content_hash=hash_posting_text(text))
    service.extract_entity.return_value = entity
    service.save_extracted.return_value = MagicMock(created=True, entity=entity)
    monkeypatch.setattr(
        posting_ingest, "ExtractionService", MagicMock(return_value=service)
    )

    posting_ingest.ingest_posting_text(text)
    service.extract_entity.assert_called_once_with(text)
    service.save_extracted.assert_called_once()


def test_ingest_does_not_hold_session_during_llm(monkeypatch):
    """Runtime evidence: session __exit__ runs before extract_entity is called."""
    monkeypatch.setattr(posting_ingest.config, "MAX_POSTING_CHARS", 10_000)
    events: list[str] = []

    class TrackingScope:
        def __enter__(self):
            events.append("session_enter")
            return MagicMock()

        def __exit__(self, *args):
            events.append("session_exit")
            return False

    monkeypatch.setattr(posting_ingest, "session_scope", lambda: TrackingScope())
    monkeypatch.setattr(posting_ingest, "JobPostingRepository", MagicMock())

    service = MagicMock()
    service.find_by_content_hash.return_value = None

    def extract(text):
        events.append("llm_extract")
        return JobPostingEntity(role_title="Dev", content_hash=hash_posting_text(text))

    service.extract_entity.side_effect = extract
    service.save_extracted.return_value = MagicMock(created=True)
    monkeypatch.setattr(
        posting_ingest, "ExtractionService", MagicMock(return_value=service)
    )

    posting_ingest.ingest_posting_text("hello posting")

    assert events == [
        "session_enter",
        "session_exit",
        "llm_extract",
        "session_enter",
        "session_exit",
    ]


def test_ingest_skips_llm_when_duplicate_found(monkeypatch):
    monkeypatch.setattr(posting_ingest.config, "MAX_POSTING_CHARS", 10_000)
    events: list[str] = []

    class TrackingScope:
        def __enter__(self):
            events.append("session_enter")
            return MagicMock()

        def __exit__(self, *args):
            events.append("session_exit")
            return False

    monkeypatch.setattr(posting_ingest, "session_scope", lambda: TrackingScope())
    monkeypatch.setattr(posting_ingest, "JobPostingRepository", MagicMock())

    existing = JobPostingEntity(id=1, role_title="Dev", content_hash="abc")
    service = MagicMock()
    service.find_by_content_hash.return_value = existing
    monkeypatch.setattr(
        posting_ingest, "ExtractionService", MagicMock(return_value=service)
    )

    result = posting_ingest.ingest_posting_text("already saved")
    assert result.created is False
    service.extract_entity.assert_not_called()
    assert events == ["session_enter", "session_exit"]
