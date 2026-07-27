# extraction_service.py
from dataclasses import dataclass
from datetime import date

from pydantic import ValidationError

from src.bll.glossary import lookup_english
from src.bll.job_posting_validator import validate_extraction_dto
from src.dal.job_posting_repository import JobPostingRepository
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.posting_hash import hash_posting_text
from src.dto.job_posting_extraction_dto import JobPostingExtractionDTO
from src.llm.base_llm_client import BaseLLMClient
from src.llm.llm_client_factory import get_llm_client
from src.llm.request_metadata import (
    begin_extract_context,
    clear_extract_context,
    log_validation_result,
)


@dataclass(frozen=True)
class ExtractAndSaveResult:
    entity: JobPostingEntity
    created: bool


def _english_label(original: str, llm_english: str | None = None) -> str:
    """Resolve English without extra LLM calls: glossary > extract field > original."""
    text = (original or "").strip()
    if not text:
        return text
    from_glossary = lookup_english(text)
    if from_glossary:
        return from_glossary
    from_llm = (llm_english or "").strip()
    if from_llm:
        return from_llm
    return text


class ExtractionService:
    """Orchestrates: one LLM extraction -> validation -> domain entity -> persistence.

    English role/skill labels come from the same extraction JSON (plus glossary
    overrides). No separate translation API calls on the ingest path.

    Preferred production flow (see ``posting_ingest``): short DB lookup session,
    LLM with no open session, then short save session. ``extract_and_save`` remains
    for tests that inject a fake repository without real connection pooling.
    """

    def __init__(
        self,
        job_posting_repository: JobPostingRepository | None = None,
        llm_client: BaseLLMClient | None = None,
    ):
        self.job_posting_repository = job_posting_repository
        self.llm_client = llm_client or get_llm_client()

    def find_by_content_hash(
        self, repository: JobPostingRepository, posting_text: str
    ) -> JobPostingEntity | None:
        return repository.get_by_content_hash(hash_posting_text(posting_text))

    def extract_entity(self, posting_text: str) -> JobPostingEntity:
        """Call LLM and build a domain entity. Must not open or hold a DB session."""
        content_hash = hash_posting_text(posting_text)
        begin_extract_context(
            posting_chars=len(posting_text),
            content_hash=content_hash,
        )
        try:
            raw_result = self.llm_client.extract(posting_text)

            try:
                dto = JobPostingExtractionDTO(**raw_result)
            except ValidationError as e:
                log_validation_result(accepted=False, error_category="validation_failure")
                raise ValueError(f"LLM output failed schema validation: {e}") from e

            try:
                dto = validate_extraction_dto(dto)
            except ValueError as e:
                log_validation_result(accepted=False, error_category="validation_failure")
                raise ValueError(f"LLM output failed domain validation: {e}") from e

            log_validation_result(accepted=True)
            return self._dto_to_entity(dto, posting_text, content_hash)
        finally:
            clear_extract_context()

    def save_extracted(
        self, repository: JobPostingRepository, entity: JobPostingEntity
    ) -> ExtractAndSaveResult:
        """Persist after a fresh hash check (handles rare concurrent insert races)."""
        if entity.content_hash:
            existing = repository.get_by_content_hash(entity.content_hash)
            if existing is not None:
                return ExtractAndSaveResult(entity=existing, created=False)

        saved = repository.save(entity)
        return ExtractAndSaveResult(entity=saved, created=True)

    def extract_and_save(self, posting_text: str) -> ExtractAndSaveResult:
        """Lookup → extract → save using the injected repository (tests / simple callers).

        Production ingest should use ``posting_ingest.ingest_posting_text``, which
        closes the DB session before the LLM call.
        """
        if self.job_posting_repository is None:
            raise ValueError("job_posting_repository is required for extract_and_save")

        existing = self.find_by_content_hash(self.job_posting_repository, posting_text)
        if existing is not None:
            return ExtractAndSaveResult(entity=existing, created=False)

        entity = self.extract_entity(posting_text)
        return self.save_extracted(self.job_posting_repository, entity)

    def _dto_to_entity(
        self,
        dto: JobPostingExtractionDTO,
        posting_text: str,
        content_hash: str,
    ) -> JobPostingEntity:
        role_title_en = _english_label(dto.role_title, dto.role_title_en)

        skills_en: list[str] = []
        for index, skill in enumerate(dto.skills):
            llm_en = dto.skills_en[index] if index < len(dto.skills_en) else None
            skills_en.append(_english_label(skill, llm_en))

        return JobPostingEntity(
            company_name=dto.company_name,
            role_title=dto.role_title,
            role_title_en=role_title_en,
            responsibilities=dto.responsibilities,
            requirements=dto.requirements,
            application_deadline=dto.application_deadline,
            salary_min=dto.salary_min,
            salary_max=dto.salary_max,
            salary_currency=dto.salary_currency,
            location=dto.location,
            country=dto.country,
            city=dto.city,
            work_type=dto.work_type,
            has_nondiscrimination_disclaimer=dto.has_nondiscrimination_disclaimer,
            skills=dto.skills,
            skills_en=skills_en,
            date_added=date.today(),
            raw_text=posting_text,
            content_hash=content_hash,
        )
