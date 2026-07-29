"""Tests for review-path skill updates (EN list is source of truth)."""

from unittest.mock import MagicMock

from src.bll.posting_review_service import update_posting_review
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.work_type import WorkType


def _existing(**overrides):
    base = dict(
        id=1,
        company_name="Acme",
        role_title="Engineer",
        role_title_en="Engineer",
        salary_min=None,
        salary_max=None,
        salary_currency=None,
        work_type=WorkType.remote,
        has_nondiscrimination_disclaimer=False,
        location=None,
        country=None,
        city=None,
        skills=[],
        skills_en=[],
    )
    base.update(overrides)
    return JobPostingEntity(**base)


def _patch_review(monkeypatch, repo):
    class _Scope:
        def __enter__(self):
            return MagicMock()

        def __exit__(self, *args):
            return False

    monkeypatch.setattr("src.bll.posting_review_service.session_scope", lambda: _Scope())
    monkeypatch.setattr(
        "src.bll.posting_review_service.JobPostingRepository", lambda session: repo
    )
    monkeypatch.setattr("src.bll.posting_review_service.add_entries", lambda pairs: 0)


def test_update_review_uses_skills_en_as_posting_skills(monkeypatch):
    """DB may have more originals than form EN lines; form list wins."""
    existing = _existing(
        skills=["A", "B", "C"],
        skills_en=["A", "B", "C"],
    )
    updated = _existing(skills=["Python", "SQL"], skills_en=["Python", "SQL"])

    repo = MagicMock()
    repo.get_by_id.return_value = existing
    repo.update_review_fields.return_value = updated
    _patch_review(monkeypatch, repo)

    result = update_posting_review(
        1,
        company_name="Acme",
        role_title="Engineer",
        role_title_en="Engineer",
        salary_min=None,
        salary_max=None,
        work_type=WorkType.remote,
        has_nondiscrimination_disclaimer=False,
        location=None,
        country=None,
        city=None,
        skills_en=["Python", "SQL"],
    )
    assert result.posting is updated
    kwargs = repo.update_review_fields.call_args.kwargs
    assert kwargs["skills"] == ["Python", "SQL"]
    assert kwargs["skills_en"] == ["Python", "SQL"]


def test_update_review_allows_adding_skills_when_extract_was_empty(monkeypatch):
    existing = _existing(skills=[], skills_en=[])
    updated = _existing(skills=["Python"], skills_en=["Python"])

    repo = MagicMock()
    repo.get_by_id.return_value = existing
    repo.update_review_fields.return_value = updated
    _patch_review(monkeypatch, repo)

    update_posting_review(
        1,
        company_name="Acme",
        role_title="Engineer",
        role_title_en="Engineer",
        salary_min=None,
        salary_max=None,
        work_type=WorkType.remote,
        has_nondiscrimination_disclaimer=False,
        location=None,
        country=None,
        city=None,
        skills_en=["Python"],
    )
    kwargs = repo.update_review_fields.call_args.kwargs
    assert kwargs["skills"] == ["Python"]
    assert kwargs["skills_en"] == ["Python"]
