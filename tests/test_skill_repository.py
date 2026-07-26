"""Tests for SkillRepository.get_or_create."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.dal.models import Base, SkillORM
from src.dal.skill_repository import SkillRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_get_or_create_inserts_normalized_english_name_and_displays(session):
    repo = SkillRepository(session)
    skill = repo.get_or_create("  Python ")
    session.commit()

    assert skill.name == "python"
    assert skill.display_name == "Python"
    assert skill.display_name_en == "Python"
    assert session.query(SkillORM).count() == 1


def test_get_or_create_uses_english_for_unique_key(session):
    repo = SkillRepository(session)
    skill = repo.get_or_create("Analüütik", display_name_en="Analyst")
    session.commit()

    assert skill.name == "analyst"
    assert skill.display_name == "Analüütik"
    assert skill.display_name_en == "Analyst"

    same = repo.get_or_create("Analyst", display_name_en="Analyst")
    assert same.id == skill.id
    assert session.query(SkillORM).count() == 1


def test_get_or_create_returns_existing_without_changing_display(session):
    repo = SkillRepository(session)
    first = repo.get_or_create("Python", display_name_en="Python")
    session.commit()

    second = repo.get_or_create("PYTHON", display_name_en="Python")
    session.commit()

    assert second.id == first.id
    assert second.display_name == "Python"
    assert session.query(SkillORM).count() == 1


def test_get_or_create_rejects_empty_name(session):
    repo = SkillRepository(session)
    with pytest.raises(ValueError, match="empty"):
        repo.get_or_create("   ")


def test_get_or_create_retries_after_integrity_error():
    session = MagicMock()
    winner = SkillORM(name="sql", display_name="SQL", display_name_en="SQL")
    session.query.return_value.filter.return_value.first.side_effect = [None, winner]

    nested = MagicMock()
    nested.__enter__ = MagicMock(return_value=None)
    nested.__exit__ = MagicMock(return_value=False)
    session.begin_nested.return_value = nested
    session.flush.side_effect = IntegrityError("stmt", {}, Exception("unique"))

    repo = SkillRepository(session)
    got = repo.get_or_create("SQL", display_name_en="SQL")

    assert got is winner
    session.begin_nested.assert_called_once()
