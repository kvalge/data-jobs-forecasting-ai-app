"""Tests for posting content-hash deduplication helpers and extract short-circuit."""

from unittest.mock import MagicMock

from src.bll.extraction_service import ExtractionService
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.posting_hash import hash_posting_text


def test_hash_is_stable_after_strip():
    assert hash_posting_text("  hello world  ") == hash_posting_text("hello world")
    assert len(hash_posting_text("hello world")) == 64


def test_different_text_different_hash():
    assert hash_posting_text("posting A") != hash_posting_text("posting B")


def test_extract_and_save_skips_llm_when_hash_exists():
    content = "Unique posting body"
    existing = JobPostingEntity(
        id=42,
        role_title="Engineer",
        company_name="Acme",
        content_hash=hash_posting_text(content),
    )
    repo = MagicMock()
    repo.get_by_content_hash.return_value = existing

    service = ExtractionService(repo)
    service.llm_client = MagicMock()

    result = service.extract_and_save(content)

    assert result.created is False
    assert result.entity.id == 42
    service.llm_client.extract.assert_not_called()
    repo.save.assert_not_called()


def test_extract_and_save_calls_llm_when_new(monkeypatch):
    content = "Brand new posting"
    repo = MagicMock()
    repo.get_by_content_hash.return_value = None
    saved = JobPostingEntity(id=1, role_title="Dev", content_hash=hash_posting_text(content))
    repo.save.return_value = saved

    service = ExtractionService(repo)
    service.llm_client = MagicMock()
    service.llm_client.extract.return_value = {
        "company_name": "Co",
        "role_title": "Dev",
        "responsibilities": None,
        "requirements": None,
        "application_deadline": None,
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "location": None,
        "work_type": "unknown",
        "has_nondiscrimination_disclaimer": False,
        "skills": ["Python"],
    }

    result = service.extract_and_save(content)

    assert result.created is True
    service.llm_client.extract.assert_called_once_with(content)
    repo.save.assert_called_once()
