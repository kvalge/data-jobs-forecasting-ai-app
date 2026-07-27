"""Tests for posting size cap before LLM / DB work."""

from unittest.mock import MagicMock

import pytest

from src.bll import posting_ingest


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


def test_ingest_allows_text_at_limit_and_calls_service(monkeypatch):
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
    service.extract_and_save.return_value = MagicMock(created=True)
    monkeypatch.setattr(posting_ingest, "ExtractionService", MagicMock(return_value=service))

    posting_ingest.ingest_posting_text(text)
    service.extract_and_save.assert_called_once_with(text)
