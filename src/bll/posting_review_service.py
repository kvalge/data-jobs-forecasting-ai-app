# posting_review_service.py
"""BLL façade for reviewing/updating a saved posting (web)."""

from __future__ import annotations

from dataclasses import dataclass

from src.bll.glossary import add_entries, pairs_from_posting
from src.bll.job_posting_validator import validate_review_fields
from src.dal.job_posting_repository import JobPostingRepository
from src.dal.session import session_scope
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.work_type import WorkType


@dataclass(frozen=True)
class ReviewUpdateResult:
    posting: JobPostingEntity
    glossary_pairs_added: int


def get_posting_for_review(posting_id: int) -> JobPostingEntity | None:
    with session_scope() as session:
        return JobPostingRepository(session).get_by_id(posting_id)


def update_posting_review(
    posting_id: int,
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
    skills_en: list[str],
) -> ReviewUpdateResult:
    """Validate, persist review fields, and update glossary outside the DB session."""
    with session_scope() as session:
        repository = JobPostingRepository(session)
        existing = repository.get_by_id(posting_id)
        if existing is None:
            raise ValueError(f"Job posting not found: id={posting_id}")

        original_skills = list(existing.skills or [])
        validated = validate_review_fields(
            company_name=company_name,
            role_title=role_title,
            role_title_en=role_title_en,
            salary_min=salary_min,
            salary_max=salary_max,
            work_type=work_type,
            has_nondiscrimination_disclaimer=has_nondiscrimination_disclaimer,
            location=location,
            country=country,
            city=city,
            skills=original_skills,
            skills_en=skills_en,
            salary_currency=existing.salary_currency,
        )

        updated = repository.update_review_fields(
            posting_id,
            company_name=validated.company_name,
            role_title=validated.role_title,
            role_title_en=validated.role_title_en,
            salary_min=validated.salary_min,
            salary_max=validated.salary_max,
            work_type=validated.work_type,
            has_nondiscrimination_disclaimer=validated.has_nondiscrimination_disclaimer,
            location=validated.location,
            country=validated.country,
            city=validated.city,
            skills=validated.skills,
            skills_en=validated.skills_en,
        )

    added = add_entries(
        pairs_from_posting(
            validated.role_title,
            validated.role_title_en,
            validated.skills,
            validated.skills_en,
        )
    )
    return ReviewUpdateResult(posting=updated, glossary_pairs_added=added)
