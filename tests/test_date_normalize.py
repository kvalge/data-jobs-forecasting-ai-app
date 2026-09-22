"""Tests for LLM date normalization and extraction deadline coercion."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.dto.job_posting_extraction_dto import JobPostingExtractionDTO
from src.llm.date_normalize import normalize_optional_date
from src.llm.extract_validate import assert_extraction_usable


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("21.10.2026", date(2026, 10, 21)),
        ("21/10/2026", date(2026, 10, 21)),
        ("21-10-2026", date(2026, 10, 21)),
        ("2026-10-21", date(2026, 10, 21)),
        ("2026.10.21", date(2026, 10, 21)),
        ("21 Oct 2026", date(2026, 10, 21)),
        ("21 October 2026", date(2026, 10, 21)),
        ("", None),
        ("null", None),
        (None, None),
        (date(2026, 10, 21), date(2026, 10, 21)),
    ],
)
def test_normalize_optional_date(raw, expected):
    assert normalize_optional_date(raw) == expected


def test_dto_accepts_european_deadline():
    dto = JobPostingExtractionDTO(
        role_title="Engineer",
        application_deadline="21.10.2026",
    )
    assert dto.application_deadline == date(2026, 10, 21)


def test_assert_extraction_usable_accepts_european_deadline():
    parsed = {
        "role_title": "Engineer",
        "skills": [],
        "skills_en": [],
        "application_deadline": "21.10.2026",
    }
    assert assert_extraction_usable(parsed)["role_title"] == "Engineer"


def test_dto_rejects_unparseable_deadline():
    with pytest.raises(ValidationError):
        JobPostingExtractionDTO(
            role_title="Engineer",
            application_deadline="not-a-date",
        )
