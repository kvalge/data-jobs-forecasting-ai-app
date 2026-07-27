# skill_repository.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dal.base_repository import BaseRepository
from src.dal.models import SkillORM
from src.domain.skill_entity import SkillEntity


class SkillRepository(BaseRepository[SkillEntity]):
    """Handles persistence for skills, including get-or-create by English name."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, entity: SkillEntity) -> SkillEntity:
        display = (entity.display_name or entity.name).strip()
        display_en = (entity.display_name_en or display).strip() or display
        normalized = display_en.lower()
        orm_obj = SkillORM(
            name=normalized,
            display_name=display or normalized,
            display_name_en=display_en,
        )
        self.session.add(orm_obj)
        self.session.flush()
        entity.id = orm_obj.id
        entity.name = normalized
        entity.display_name = display or normalized
        entity.display_name_en = display_en
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

    def get_by_normalized_names(self, names: list[str]) -> dict[str, SkillORM]:
        """Return existing skills keyed by lowercase English name (one query)."""
        normalized = sorted({(n or "").strip().lower() for n in names if (n or "").strip()})
        if not normalized:
            return {}
        rows = (
            self.session.query(SkillORM)
            .filter(SkillORM.name.in_(normalized))
            .all()
        )
        return {row.name: row for row in rows}

    def get_or_create(
        self,
        display_name: str,
        display_name_en: str | None = None,
        *,
        cache: dict[str, SkillORM] | None = None,
    ) -> SkillORM:
        """Return existing skill or create one.

        Unique key `name` is lowercase English (`display_name_en`).
        `display_name` keeps the first-seen original label.
        Optional ``cache`` avoids repeated SELECTs within one save.
        """
        original = display_name.strip()
        english = (display_name_en or display_name).strip() or original
        if not original and not english:
            raise ValueError("Skill name cannot be empty")
        if not original:
            original = english

        normalized_name = english.lower()
        if cache is not None and normalized_name in cache:
            existing = cache[normalized_name]
            if not existing.display_name_en and english:
                existing.display_name_en = english
                self.session.flush()
            return existing

        existing = (
            self.session.query(SkillORM)
            .filter(SkillORM.name == normalized_name)
            .first()
        )
        if existing is not None:
            if not existing.display_name_en and english:
                existing.display_name_en = english
                self.session.flush()
            if cache is not None:
                cache[normalized_name] = existing
            return existing

        try:
            with self.session.begin_nested():
                orm_obj = SkillORM(
                    name=normalized_name,
                    display_name=original,
                    display_name_en=english,
                )
                self.session.add(orm_obj)
                self.session.flush()
            if cache is not None:
                cache[normalized_name] = orm_obj
            return orm_obj
        except IntegrityError:
            existing = (
                self.session.query(SkillORM)
                .filter(SkillORM.name == normalized_name)
                .first()
            )
            if existing is None:
                raise
            if cache is not None:
                cache[normalized_name] = existing
            return existing

    def _to_entity(self, orm_obj: SkillORM) -> SkillEntity:
        display = orm_obj.display_name or orm_obj.name
        return SkillEntity(
            id=orm_obj.id,
            name=orm_obj.name,
            display_name=display,
            display_name_en=orm_obj.display_name_en or display,
        )
