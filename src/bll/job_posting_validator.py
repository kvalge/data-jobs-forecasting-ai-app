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
    skills: list[str] = []
    skills_en: list[str] = []
    for index, skill in enumerate(dto.skills):
        cleaned = (skill or "").strip()
        if not cleaned:
            continue
        skills.append(cleaned)
        if index < len(dto.skills_en) and (dto.skills_en[index] or "").strip():
            skills_en.append(dto.skills_en[index].strip())
        else:
            skills_en.append(cleaned)

    role_title_en = (dto.role_title_en or "").strip() or role_title

    return JobPostingExtractionDTO(
        company_name=dto.company_name,
        role_title=role_title,
        role_title_en=role_title_en,
        responsibilities=dto.responsibilities,
        requirements=dto.requirements,
        application_deadline=dto.application_deadline,
        salary_min=dto.salary_min,
        salary_max=dto.salary_max,
        salary_currency=dto.salary_currency,
        location=dto.location,
        country=dto.country.strip() if dto.country and dto.country.strip() else None,
        city=dto.city.strip() if dto.city and dto.city.strip() else None,
        work_type=dto.work_type,
        has_nondiscrimination_disclaimer=dto.has_nondiscrimination_disclaimer,
        skills=skills,
        skills_en=skills_en,
    )
