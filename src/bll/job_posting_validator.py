# job_posting_validator.py
"""Business rules for extracted job postings (after Pydantic schema checks)."""

from src.dto.job_posting_extraction_dto import JobPostingExtractionDTO


def validate_extraction_dto(dto: JobPostingExtractionDTO) -> JobPostingExtractionDTO:
    """Normalize and enforce domain rules; raise ValueError on invalid data."""
    role_title = dto.role_title.strip()
    if not role_title:
        raise ValueError("role_title is required and cannot be empty")

    if (
        dto.salary_min is not None
        and dto.salary_max is not None
        and dto.salary_min > dto.salary_max
    ):
        raise ValueError(
            f"salary_min ({dto.salary_min}) cannot be greater than salary_max ({dto.salary_max})"
        )

    # Drop blank skill strings; keep order, preserve first-seen casing for later storage
    skills = [skill.strip() for skill in dto.skills if skill and skill.strip()]

    return JobPostingExtractionDTO(
        company_name=dto.company_name,
        role_title=role_title,
        responsibilities=dto.responsibilities,
        requirements=dto.requirements,
        application_deadline=dto.application_deadline,
        salary_min=dto.salary_min,
        salary_max=dto.salary_max,
        salary_currency=dto.salary_currency,
        location=dto.location,
        work_type=dto.work_type,
        has_nondiscrimination_disclaimer=dto.has_nondiscrimination_disclaimer,
        skills=skills,
    )
