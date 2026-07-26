"""Tests for domain validation after LLM schema checks."""

import pytest

from src.bll.job_posting_validator import validate_extraction_dto
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


def test_strips_role_and_drops_blank_skills():
    dto = JobPostingExtractionDTO(
        role_title="  Data Engineer ",
        skills=["Python", "  ", "", "SQL"],
    )
    result = validate_extraction_dto(dto)
    assert result.role_title == "Data Engineer"
    assert result.skills == ["Python", "SQL"]


def test_allows_salary_min_only():
    dto = JobPostingExtractionDTO(role_title="Analyst", salary_min=3000.0, skills=[])
    result = validate_extraction_dto(dto)
    assert result.salary_min == 3000.0
    assert result.salary_max is None
