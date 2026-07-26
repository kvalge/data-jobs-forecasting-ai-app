# skill_repository.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dal.base_repository import BaseRepository
from src.dal.models import SkillORM
from src.domain.skill_entity import SkillEntity


class SkillRepository(BaseRepository[SkillEntity]):
    """Handles persistence for skills, including get-or-create by name."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, entity: SkillEntity) -> SkillEntity:
        normalized = entity.name.strip().lower()
        display = (entity.display_name or entity.name).strip() or normalized
        orm_obj = SkillORM(name=normalized, display_name=display)
        self.session.add(orm_obj)
        self.session.flush()  # assigns orm_obj.id without committing yet
        entity.id = orm_obj.id
        entity.name = normalized
        entity.display_name = display
        return entity

    def get_by_id(self, entity_id: int) -> SkillEntity | None:
        orm_obj = self.session.get(SkillORM, entity_id)
        if orm_obj is None:
            return None
        return self._to_entity(orm_obj)

    def get_all(self) -> list[SkillEntity]:
        orm_objs = self.session.query(SkillORM).all()
        return [self._to_entity(o) for o in orm_objs]

    def delete(self, entity_id: int) -> None:
        orm_obj = self.session.get(SkillORM, entity_id)
        if orm_obj is not None:
            self.session.delete(orm_obj)

    def get_or_create(self, name: str) -> SkillORM:
        """Return the existing SkillORM for this name, or create a new one.

        Lookup uses normalized `name` (lowercase). On create, stores first-seen
        casing in `display_name`. Existing rows keep their original display_name.

        Uses a savepoint so a unique-constraint race does not poison the
        outer transaction (e.g. an in-progress job posting save).

        Returns the ORM object (not the domain entity), since job_posting_repository
        needs the actual ORM instance to attach to the many-to-many relationship.
        """
        display_name = name.strip()
        normalized_name = display_name.lower()
        if not normalized_name:
            raise ValueError("Skill name cannot be empty")

        existing = (
            self.session.query(SkillORM)
            .filter(SkillORM.name == normalized_name)
            .first()
        )
        if existing is not None:
            return existing

        try:
            with self.session.begin_nested():
                orm_obj = SkillORM(name=normalized_name, display_name=display_name)
                self.session.add(orm_obj)
                self.session.flush()
            return orm_obj
        except IntegrityError:
            existing = (
                self.session.query(SkillORM)
                .filter(SkillORM.name == normalized_name)
                .first()
            )
            if existing is None:
                raise
            return existing

    def _to_entity(self, orm_obj: SkillORM) -> SkillEntity:
        return SkillEntity(
            id=orm_obj.id,
            name=orm_obj.name,
            display_name=orm_obj.display_name or orm_obj.name,
        )
