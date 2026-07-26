# job_posting_repository.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dal.base_repository import BaseRepository
from src.dal.models import JobPostingORM
from src.dal.skill_repository import SkillRepository
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.work_type import WorkType


class JobPostingRepository(BaseRepository[JobPostingEntity]):
    """Handles persistence for job postings, including their linked skills."""

    def __init__(self, session: Session):
        self.session = session
        self.skill_repository = SkillRepository(session)

    def get_by_content_hash(self, content_hash: str) -> JobPostingEntity | None:
        orm_obj = (
            self.session.query(JobPostingORM)
            .filter(JobPostingORM.content_hash == content_hash)
            .first()
        )
        if orm_obj is None:
            return None
        return self._to_entity(orm_obj)

    def save(self, entity: JobPostingEntity) -> JobPostingEntity:
        if entity.content_hash:
            existing = self.get_by_content_hash(entity.content_hash)
            if existing is not None:
                return existing

        orm_obj = JobPostingORM(
            company_name=entity.company_name,
            role_title=entity.role_title,
            role_title_en=entity.role_title_en or entity.role_title,
            responsibilities=entity.responsibilities,
            requirements=entity.requirements,
            application_deadline=entity.application_deadline,
            salary_min=entity.salary_min,
            salary_max=entity.salary_max,
            salary_currency=entity.salary_currency,
            location=entity.location,
            country=entity.country,
            city=entity.city,
            work_type=entity.work_type,
            has_nondiscrimination_disclaimer=entity.has_nondiscrimination_disclaimer,
            date_added=entity.date_added,
            raw_text=entity.raw_text,
            content_hash=entity.content_hash,
        )

        for index, skill_name in enumerate(entity.skills):
            skill_en = (
                entity.skills_en[index]
                if index < len(entity.skills_en)
                else skill_name
            )
            skill_orm = self.skill_repository.get_or_create(
                skill_name,
                display_name_en=skill_en,
            )
            orm_obj.skills.append(skill_orm)

        self.session.add(orm_obj)
        try:
            self.session.commit()
            self.session.refresh(orm_obj)
        except IntegrityError:
            self.session.rollback()
            if entity.content_hash:
                existing = self.get_by_content_hash(entity.content_hash)
                if existing is not None:
                    return existing
            raise
        except Exception:
            self.session.rollback()
            raise

        entity.id = orm_obj.id
        entity.created_at = orm_obj.created_at
        entity.role_title_en = orm_obj.role_title_en
        return entity

    def get_by_id(self, entity_id: int) -> JobPostingEntity | None:
        orm_obj = self.session.get(JobPostingORM, entity_id)
        if orm_obj is None:
            return None
        return self._to_entity(orm_obj)

    def get_all(self) -> list[JobPostingEntity]:
        orm_objs = self.session.query(JobPostingORM).all()
        return [self._to_entity(o) for o in orm_objs]

    def delete(self, entity_id: int) -> None:
        orm_obj = self.session.get(JobPostingORM, entity_id)
        if orm_obj is not None:
            self.session.delete(orm_obj)
            self.session.commit()

    def update_review_fields(
        self,
        entity_id: int,
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
    ) -> JobPostingEntity:
        """Update UI-editable fields and replace linked skills by English names."""
        orm_obj = self.session.get(JobPostingORM, entity_id)
        if orm_obj is None:
            raise ValueError(f"Job posting not found: id={entity_id}")

        role = role_title.strip()
        if not role:
            raise ValueError("role_title is required and cannot be empty")

        role_en = (role_title_en or role).strip() or role

        orm_obj.company_name = company_name.strip() if company_name and company_name.strip() else None
        orm_obj.role_title = role
        orm_obj.role_title_en = role_en
        orm_obj.salary_min = salary_min
        orm_obj.salary_max = salary_max
        orm_obj.work_type = work_type
        orm_obj.has_nondiscrimination_disclaimer = has_nondiscrimination_disclaimer
        orm_obj.location = location.strip() if location and location.strip() else None
        orm_obj.country = country.strip() if country and country.strip() else None
        orm_obj.city = city.strip() if city and city.strip() else None

        orm_obj.skills.clear()
        for skill_en in skills_en:
            label = skill_en.strip()
            if not label:
                continue
            skill_orm = self.skill_repository.get_or_create(label, display_name_en=label)
            orm_obj.skills.append(skill_orm)

        try:
            self.session.commit()
            self.session.refresh(orm_obj)
        except Exception:
            self.session.rollback()
            raise

        return self._to_entity(orm_obj)

    def _to_entity(self, orm_obj: JobPostingORM) -> JobPostingEntity:
        """Convert an ORM object back into a pure domain entity."""
        return JobPostingEntity(
            id=orm_obj.id,
            created_at=orm_obj.created_at,
            company_name=orm_obj.company_name,
            role_title=orm_obj.role_title,
            role_title_en=orm_obj.role_title_en or orm_obj.role_title,
            responsibilities=orm_obj.responsibilities,
            requirements=orm_obj.requirements,
            application_deadline=orm_obj.application_deadline,
            salary_min=orm_obj.salary_min,
            salary_max=orm_obj.salary_max,
            salary_currency=orm_obj.salary_currency,
            location=orm_obj.location,
            country=orm_obj.country,
            city=orm_obj.city,
            work_type=WorkType(orm_obj.work_type),
            has_nondiscrimination_disclaimer=orm_obj.has_nondiscrimination_disclaimer,
            skills=[(s.display_name or s.name) for s in orm_obj.skills],
            skills_en=[(s.display_name_en or s.display_name or s.name) for s in orm_obj.skills],
            date_added=orm_obj.date_added,
            raw_text=orm_obj.raw_text,
            content_hash=orm_obj.content_hash,
        )
