"""Tests for DatabaseSource aggregates (in-memory SQLite)."""

from contextlib import contextmanager
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.dal.models import Base, JobPostingORM, SkillORM
from src.domain.work_type import WorkType
from src.prediction.database_source import DatabaseSource
import src.prediction.database_source as database_source_mod


@pytest.fixture
def seeded_session(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    python = SkillORM(name="python", display_name="Python", display_name_en="Python")
    sql = SkillORM(name="sql", display_name="SQL", display_name_en="SQL")
    session.add_all([python, sql])
    session.flush()

    p1 = JobPostingORM(
        role_title="Data Engineer",
        role_title_en="Data Engineer",
        work_type=WorkType.remote,
        date_added=date(2024, 1, 10),
        salary_min=4000,
        salary_max=6000,
        has_nondiscrimination_disclaimer=False,
    )
    p2 = JobPostingORM(
        role_title="Data Engineer",
        role_title_en="Data Engineer",
        work_type=WorkType.remote,
        date_added=date(2024, 1, 20),
        salary_min=5000,
        salary_max=7000,
        has_nondiscrimination_disclaimer=False,
    )
    p3 = JobPostingORM(
        role_title="ML Engineer",
        role_title_en="ML Engineer",
        work_type=WorkType.hybrid,
        date_added=date(2024, 2, 5),
        salary_min=5500,
        salary_max=7500,
        has_nondiscrimination_disclaimer=False,
    )
    p1.skills = [python, sql]
    p2.skills = [python]
    p3.skills = [python]
    session.add_all([p1, p2, p3])
    session.commit()

    @contextmanager
    def fake_scope():
        yield session

    monkeypatch.setattr(database_source_mod, "session_scope", fake_scope)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_database_source_monthly_roles_and_skills(seeded_session):
    src = DatabaseSource()
    roles = src.load_monthly_roles()
    assert not roles.empty
    assert set(roles.columns) >= {
        "period_start",
        "role_title_en",
        "posting_count",
        "avg_salary_min",
        "avg_salary_max",
        "avg_salary",
    }
    jan = roles[roles["role_title_en"] == "Data Engineer"]
    assert int(jan["posting_count"].sum()) == 2

    skills = src.load_monthly_skills()
    assert not skills.empty
    python_rows = skills[skills["display_name_en"] == "Python"]
    assert int(python_rows["posting_count"].sum()) == 3

    assert src.top_roles(months=6, k=2)[0] == "Data Engineer"
    assert src.top_skills(months=6, k=2)[0] == "Python"

    manifest = src.load_manifest()
    assert manifest["data_source"] == "database"
    assert manifest["n_postings"] == 3


def test_database_source_empty(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    @contextmanager
    def fake_scope():
        yield session

    monkeypatch.setattr(database_source_mod, "session_scope", fake_scope)
    try:
        src = DatabaseSource()
        assert src.load_monthly_roles().empty
        assert src.load_monthly_skills().empty
        assert src.top_roles() == []
        assert src.load_manifest()["n_postings"] == 0
    finally:
        session.close()
        engine.dispose()
