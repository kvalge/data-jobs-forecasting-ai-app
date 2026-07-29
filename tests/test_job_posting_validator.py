"""Tests for domain validation after LLM schema checks."""

import pytest
from pydantic import ValidationError

from src.bll.job_posting_validator import validate_extraction_dto, validate_review_fields
from src.domain.work_type import WorkType
from src.dto.job_posting_extraction_dto import JobPostingExtractionDTO


def test_rejects_blank_role_title():
    dto = JobPostingExtractionDTO(role_title="   ", skills=[])
    with pytest.raises(ValueError, match="role_title"):
        validate_extraction_dto(dto)


def test_rejects_inverted_salary_range():
    dto = JobPostingExtractionDTO(
        role_title="Engineer",
        salary_min=100.0,
        salary_max=50.0,
        skills=[],
    )
    with pytest.raises(ValueError, match="salary_min"):
        validate_extraction_dto(dto)


def test_rejects_negative_salary_at_schema():
    with pytest.raises(ValidationError):
        JobPostingExtractionDTO(role_title="Engineer", salary_min=-1.0, skills=[])


def test_strips_role_and_drops_blank_skills():
    dto = JobPostingExtractionDTO(
        role_title="  Data Engineer ",
        skills=["Python", "  ", "", "SQL"],
    )
    result = validate_extraction_dto(dto)
    assert result.role_title == "Data Engineer"
    assert result.skills == ["Python", "SQL"]
    assert result.skills_en == ["Python", "SQL"]


def test_rejects_mismatched_skills_en_length():
    dto = JobPostingExtractionDTO(
        role_title="Engineer",
        skills=["Python", "SQL"],
        skills_en=["Python"],
    )
    with pytest.raises(ValueError, match="same length"):
        validate_extraction_dto(dto)


def test_rejects_bad_currency():
    dto = JobPostingExtractionDTO(
        role_title="Engineer",
        salary_currency="euro",
        skills=[],
    )
    with pytest.raises(ValueError, match="salary_currency"):
        validate_extraction_dto(dto)


def test_normalizes_currency():
    dto = JobPostingExtractionDTO(
        role_title="Engineer",
        salary_currency=" eur ",
        skills=[],
    )
    result = validate_extraction_dto(dto)
    assert result.salary_currency == "EUR"


def test_allows_salary_min_only():
    dto = JobPostingExtractionDTO(role_title="Analyst", salary_min=3000.0, skills=[])
    result = validate_extraction_dto(dto)
    assert result.salary_min == 3000.0
    assert result.salary_max is None


def test_validate_review_fields_uses_skills_en_as_posting_skills():
    """Review form EN list replaces posting skill links (ignores prior original count)."""
    result = validate_review_fields(
        company_name="Acme",
        role_title="Dev",
        role_title_en="Dev",
        salary_min=None,
        salary_max=None,
        work_type=WorkType.remote,
        has_nondiscrimination_disclaimer=False,
        location=None,
        country=None,
        city=None,
        skills=["A", "B", "C"],
        skills_en=["Python", "SQL"],
    )
    assert result.skills == ["Python", "SQL"]
    assert result.skills_en == ["Python", "SQL"]


def test_validate_review_fields_accepts_aligned_skills():
    result = validate_review_fields(
        company_name="Acme",
        role_title="Dev",
        role_title_en="Developer",
        salary_min=1000.0,
        salary_max=2000.0,
        work_type=WorkType.hybrid,
        has_nondiscrimination_disclaimer=True,
        location="Tallinn",
        country="Estonia",
        city="Tallinn",
        skills=["püüton"],
        skills_en=["Python"],
    )
    # Review form: EN list is the posting skill link (not the prior original label).
    assert result.skills == ["Python"]
    assert result.skills_en == ["Python"]
    assert result.role_title_en == "Developer"
