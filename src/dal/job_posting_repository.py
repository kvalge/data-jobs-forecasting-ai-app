# job_posting_repository.py
from sqlalchemy.orm import Session

from src.dal.base_repository import BaseRepository
from src.dal.models import JobPostingORM
from src.dal.skill_repository import SkillRepository
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.skill_entity import SkillEntity
from src.domain.work_type import WorkType


class JobPostingRepository(BaseRepository[JobPostingEntity]):
    """Handles persistence for job postings, including their linked skills."""

    def __init__(self, session: Session):
        self.session = session
        self.skill_repository = SkillRepository(session)

    def save(self, entity: JobPostingEntity) -> JobPostingEntity:
        orm_obj = JobPostingORM(
            company_name=entity.company_name,
            role_title=entity.role_title,
            responsibilities=entity.responsibilities,
            requirements=entity.requirements,
            application_deadline=entity.application_deadline,
            salary_min=entity.salary_min,
            salary_max=entity.salary_max,
            salary_currency=entity.salary_currency,
            location=entity.location,
            work_type=entity.work_type,
            has_nondiscrimination_disclaimer=entity.has_nondiscrimination_disclaimer,
            date_added=entity.date_added,
            raw_text=entity.raw_text,
        )

        # link skills — get_or_create returns SkillORM instances directly
        for skill_name in entity.skills:
            skill_orm = self.skill_repository.get_or_create(skill_name)
            orm_obj.skills.append(skill_orm)

        self.session.add(orm_obj)
        try:
            self.session.commit()  # posting + linked skills in one transaction
            self.session.refresh(orm_obj)
        except Exception:
            self.session.rollback()
            raise

        entity.id = orm_obj.id
        entity.created_at = orm_obj.created_at
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

    def _to_entity(self, orm_obj: JobPostingORM) -> JobPostingEntity:
        """Convert an ORM object back into a pure domain entity."""
        return JobPostingEntity(
            id=orm_obj.id,
            created_at=orm_obj.created_at,
            company_name=orm_obj.company_name,
            role_title=orm_obj.role_title,
            responsibilities=orm_obj.responsibilities,
            requirements=orm_obj.requirements,
            application_deadline=orm_obj.application_deadline,
            salary_min=orm_obj.salary_min,
            salary_max=orm_obj.salary_max,
            salary_currency=orm_obj.salary_currency,
            location=orm_obj.location,
            work_type=WorkType(orm_obj.work_type),
            has_nondiscrimination_disclaimer=orm_obj.has_nondiscrimination_disclaimer,
            skills=[(s.display_name or s.name) for s in orm_obj.skills],
            date_added=orm_obj.date_added,
            raw_text=orm_obj.raw_text,
        )