# job_posting_extraction_dto.py
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.work_type import WorkType

# Shared bounds for LLM output and review UI (untrusted input).
MAX_SHORT_TEXT = 200
MAX_LONG_TEXT = 20_000
MAX_SKILL_LEN = 100
MAX_SKILLS = 50
SALARY_SOFT_MAX = 50_000_000.0


class JobPostingExtractionDTO(BaseModel):
    """DTO for what the LLM extracts from a raw job posting text."""

    company_name: Optional[str] = Field(
        None, max_length=MAX_SHORT_TEXT, description="Name of the hiring company"
    )
    role_title: str = Field(
        ..., max_length=MAX_SHORT_TEXT, description="Job title as stated in the posting"
    )
    role_title_en: Optional[str] = Field(
        None,
        max_length=MAX_SHORT_TEXT,
        description="English form of the job title (same as role_title if already English)",
    )
    responsibilities: Optional[str] = Field(
        None, max_length=MAX_LONG_TEXT, description="Summary of tasks/duties"
    )
    requirements: Optional[str] = Field(
        None, max_length=MAX_LONG_TEXT, description="Required qualifications/experience"
    )
    application_deadline: Optional[date] = Field(
        None, description="Application deadline, if stated"
    )
    salary_min: Optional[float] = Field(
        None,
        ge=0,
        le=SALARY_SOFT_MAX,
        description="Minimum salary, if a range or single value is given",
    )
    salary_max: Optional[float] = Field(
        None,
        ge=0,
        le=SALARY_SOFT_MAX,
        description="Maximum salary, if a range is given",
    )
    salary_currency: Optional[str] = Field(
        None, max_length=16, description="Currency code, e.g. EUR"
    )
    location: Optional[str] = Field(
        None, max_length=MAX_SHORT_TEXT, description="Free-text location as stated in the posting"
    )
    country: Optional[str] = Field(
        None, max_length=MAX_SHORT_TEXT, description="Country stated in the posting, if identifiable"
    )
    city: Optional[str] = Field(
        None, max_length=MAX_SHORT_TEXT, description="City stated in the posting, if identifiable"
    )
    work_type: WorkType = Field(WorkType.unknown, description="onsite / hybrid / remote")
    has_nondiscrimination_disclaimer: bool = Field(
        False,
        description="True if posting includes an equal opportunity / non-discrimination statement",
    )
    skills: list[str] = Field(
        default_factory=list,
        max_length=MAX_SKILLS,
        description="List of required/mentioned skills or technologies",
    )
    skills_en: list[str] = Field(
        default_factory=list,
        max_length=MAX_SKILLS,
        description="English forms of skills (same order as skills; same text when already English)",
    )
