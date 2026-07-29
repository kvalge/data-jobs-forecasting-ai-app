# job_posting_validator.py
"""Business rules for extracted job postings (after Pydantic schema checks)."""

from __future__ import annotations

import re

from src.domain.work_type import WorkType
from src.dto.job_posting_extraction_dto import (
    MAX_SKILL_LEN,
    MAX_SKILLS,
    SALARY_SOFT_MAX,
    JobPostingExtractionDTO,
)

# Currency must look like ISO 4217 (exactly 3 letters after normalize).
_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


def _optional_stripped(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _normalize_currency(raw: str | None) -> str | None:
    cleaned = _optional_stripped(raw)
    if cleaned is None:
        return None
    code = cleaned.upper()
    if not _CURRENCY_RE.fullmatch(code):
        raise ValueError(
            f"salary_currency must be a 3-letter code (e.g. EUR), got {raw!r}"
        )
    return code


def _validate_salary(salary_min: float | None, salary_max: float | None) -> None:
    for label, value in (("salary_min", salary_min), ("salary_max", salary_max)):
        if value is None:
            continue
        if value < 0:
            raise ValueError(f"{label} cannot be negative")
        if value > SALARY_SOFT_MAX:
            raise ValueError(f"{label} exceeds the allowed maximum ({SALARY_SOFT_MAX:g})")
    if (
        salary_min is not None
        and salary_max is not None
        and salary_min > salary_max
    ):
        raise ValueError(
            f"salary_min ({salary_min}) cannot be greater than salary_max ({salary_max})"
        )


def align_skills_to_english(
    skills: list[str], skills_en: list[str]
) -> tuple[list[str], list[str]]:
    """Use the review-form English skill list as the posting skill links.

    The edit UI only edits ``skills_en``. That list becomes both ``skills`` and
    ``skills_en`` for the posting association. Existing skill DB rows keep their
    other columns when re-linked by English name via ``get_or_create``.
    """
    en = [(s or "").strip() for s in (skills_en or []) if (s or "").strip()]
    return list(en), list(en)


def _normalize_skill_lists(
    skills: list[str],
    skills_en: list[str],
) -> tuple[list[str], list[str]]:
    """Drop blank skills; require parallel English labels (or omit EN to copy)."""
    raw_skills = list(skills or [])
    raw_en = list(skills_en or [])

    if raw_en and len(raw_en) != len(raw_skills):
        raise ValueError(
            f"skills and skills_en must have the same length "
            f"(got {len(raw_skills)} skills and {len(raw_en)} skills_en)"
        )

    out_skills: list[str] = []
    out_en: list[str] = []
    for index, skill in enumerate(raw_skills):
        cleaned = (skill or "").strip()
        if not cleaned:
            continue
        if len(cleaned) > MAX_SKILL_LEN:
            raise ValueError(f"skill exceeds max length ({MAX_SKILL_LEN})")
        if raw_en:
            en = (raw_en[index] or "").strip()
            if not en:
                raise ValueError(
                    "skills_en entries cannot be blank when skills_en is provided"
                )
            if len(en) > MAX_SKILL_LEN:
                raise ValueError(f"skills_en entry exceeds max length ({MAX_SKILL_LEN})")
        else:
            en = cleaned
        out_skills.append(cleaned)
        out_en.append(en)

    if len(out_skills) > MAX_SKILLS:
        raise ValueError(f"at most {MAX_SKILLS} skills are allowed")

    return out_skills, out_en


def validate_extraction_dto(dto: JobPostingExtractionDTO) -> JobPostingExtractionDTO:
    """Normalize and enforce domain rules; raise ValueError on invalid data."""
    role_title = dto.role_title.strip()
    if not role_title:
        raise ValueError("role_title is required and cannot be empty")

    _validate_salary(dto.salary_min, dto.salary_max)
    skills, skills_en = _normalize_skill_lists(dto.skills, dto.skills_en)
    role_title_en = (dto.role_title_en or "").strip() or role_title
    currency = _normalize_currency(dto.salary_currency)

    return JobPostingExtractionDTO(
        company_name=_optional_stripped(dto.company_name),
        role_title=role_title,
        role_title_en=role_title_en,
        responsibilities=_optional_stripped(dto.responsibilities),
        requirements=_optional_stripped(dto.requirements),
        application_deadline=dto.application_deadline,
        salary_min=dto.salary_min,
        salary_max=dto.salary_max,
        salary_currency=currency,
        location=_optional_stripped(dto.location),
        country=_optional_stripped(dto.country),
        city=_optional_stripped(dto.city),
        work_type=dto.work_type,
        has_nondiscrimination_disclaimer=dto.has_nondiscrimination_disclaimer,
        skills=skills,
        skills_en=skills_en,
    )


def validate_review_fields(
    *,
    company_name: str | None,
    role_title: str,
    role_title_en: str | None,
    salary_min: float | None,
    salary_max: float | None,
    work_type: WorkType,
    has_nondiscrimination_disclaimer: bool,
    location: str | None,
    country: str | None,
    city: str | None,
    skills: list[str],
    skills_en: list[str],
    salary_currency: str | None = None,
) -> JobPostingExtractionDTO:
    """Apply the same domain rules used after LLM extract to review-form edits."""
    skills, skills_en = align_skills_to_english(skills, skills_en)
    dto = JobPostingExtractionDTO(
        company_name=company_name,
        role_title=role_title,
        role_title_en=role_title_en,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        location=location,
        country=country,
        city=city,
        work_type=work_type,
        has_nondiscrimination_disclaimer=has_nondiscrimination_disclaimer,
        skills=skills,
        skills_en=skills_en,
    )
    return validate_extraction_dto(dto)
