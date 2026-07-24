# skill_repository.py
from sqlalchemy.orm import Session

from src.dal.base_repository import BaseRepository
from src.dal.models import SkillORM
from src.domain.skill_entity import SkillEntity


class SkillRepository(BaseRepository[SkillEntity]):
    """Handles persistence for skills, including get-or-create by name."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, entity: SkillEntity) -> SkillEntity:
        orm_obj = SkillORM(name=entity.name)
        self.session.add(orm_obj)
        self.session.flush()  # assigns orm_obj.id without committing yet
        entity.id = orm_obj.id
        return entity

    def get_by_id(self, entity_id: int) -> SkillEntity | None:
        orm_obj = self.session.get(SkillORM, entity_id)
        if orm_obj is None:
            return None
        return SkillEntity(id=orm_obj.id, name=orm_obj.name)

    def get_all(self) -> list[SkillEntity]:
        orm_objs = self.session.query(SkillORM).all()
        return [SkillEntity(id=o.id, name=o.name) for o in orm_objs]

    def delete(self, entity_id: int) -> None:
        orm_obj = self.session.get(SkillORM, entity_id)
        if orm_obj is not None:
            self.session.delete(orm_obj)

    def get_or_create(self, name: str) -> SkillORM:
        """Return the existing SkillORM for this name, or create a new one.

        Returns the ORM object (not the domain entity), since job_posting_repository
        needs the actual ORM instance to attach to the many-to-many relationship.
        """
        normalized_name = name.strip().lower()
        orm_obj = self.session.query(SkillORM).filter(SkillORM.name == normalized_name).first()
        if orm_obj is None:
            orm_obj = SkillORM(name=normalized_name)
            self.session.add(orm_obj)
            self.session.flush()
        return orm_obj