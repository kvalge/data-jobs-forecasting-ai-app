# extraction_service.py
from dataclasses import dataclass
from datetime import date

from pydantic import ValidationError

from src.bll.job_posting_validator import validate_extraction_dto
from src.dal.job_posting_repository import JobPostingRepository
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.posting_hash import hash_posting_text
from src.dto.job_posting_extraction_dto import JobPostingExtractionDTO
from src.llm.llm_client_factory import get_llm_client


@dataclass(frozen=True)
class ExtractAndSaveResult:
    entity: JobPostingEntity
    created: bool


class ExtractionService:
    """Orchestrates: LLM extraction -> validation -> domain entity -> persistence."""

    def __init__(self, job_posting_repository: JobPostingRepository):
        self.job_posting_repository = job_posting_repository
        self.llm_client = get_llm_client()

    def extract_and_save(self, posting_text: str) -> ExtractAndSaveResult:
        content_hash = hash_posting_text(posting_text)
        existing = self.job_posting_repository.get_by_content_hash(content_hash)
        if existing is not None:
            return ExtractAndSaveResult(entity=existing, created=False)

        raw_result = self.llm_client.extract(posting_text)

        try:
            dto = JobPostingExtractionDTO(**raw_result)
        except ValidationError as e:
            raise ValueError(f"LLM output failed schema validation: {e}") from e

        try:
            dto = validate_extraction_dto(dto)
        except ValueError as e:
            raise ValueError(f"LLM output failed domain validation: {e}") from e

        entity = self._dto_to_entity(dto, posting_text, content_hash)
        saved = self.job_posting_repository.save(entity)
        return ExtractAndSaveResult(entity=saved, created=True)

    def _dto_to_entity(
        self,
        dto: JobPostingExtractionDTO,
        posting_text: str,
        content_hash: str,
    ) -> JobPostingEntity:
        return JobPostingEntity(
            company_name=dto.company_name,
            role_title=dto.role_title,
            responsibilities=dto.responsibilities,
            requirements=dto.requirements,
            application_deadline=dto.application_deadline,
            salary_min=dto.salary_min,
            salary_max=dto.salary_max,
            salary_currency=dto.salary_currency,
            location=dto.location,
            work_type=dto.work_type,
            has_nondiscrimination_disclaimer=dto.has_nondiscrimination_disclaimer,
            skills=dto.skills,
            date_added=date.today(),
            raw_text=posting_text,
            content_hash=content_hash,
        )
