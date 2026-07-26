# job_posting_entity.py
from dataclasses import dataclass, field
from datetime import date

from src.domain.base_entity import BaseEntity
from src.domain.work_type import WorkType


@dataclass
class JobPostingEntity(BaseEntity):
    """Pure business representation of a job posting — framework-independent."""

    company_name: str | None = None
    role_title: str = ""
    responsibilities: str | None = None
    requirements: str | None = None
    application_deadline: date | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    location: str | None = None
    country: str | None = None
    city: str | None = None
    work_type: WorkType = WorkType.unknown
    has_nondiscrimination_disclaimer: bool = False
    skills: list[str] = field(default_factory=list)
    date_added: date | None = None
    raw_text: str | None = None
    content_hash: str | None = None
