"""Tests for analysis aggregations (in-memory SQLite)."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.bll import analysis_service
from src.dal.models import Base, JobPostingORM, SkillORM
from src.domain.work_type import WorkType


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


def _posting(**kwargs) -> JobPostingORM:
    defaults = {
        "role_title": "Engineer",
        "role_title_en": "Engineer",
        "work_type": WorkType.remote,
        "date_added": date.today(),
        "has_nondiscrimination_disclaimer": False,
    }
    defaults.update(kwargs)
    return JobPostingORM(**defaults)


def test_clamp_top_n():
    assert analysis_service.clamp_top_n(None) == 10
    assert analysis_service.clamp_top_n(0) == 1
    assert analysis_service.clamp_top_n(3) == 3
    assert analysis_service.clamp_top_n(100) == 50


def test_top_companies_excludes_blank_and_orders(session):
    session.add_all(
        [
            _posting(company_name="Acme"),
            _posting(company_name="Acme"),
            _posting(company_name="Beta"),
            _posting(company_name=None),
            _posting(company_name="   "),
        ]
    )
    session.commit()

    rows = analysis_service.top_companies(session, n=10)
    assert rows == [
        {"label": "Acme", "count": 2},
        {"label": "Beta", "count": 1},
    ]


def test_top_roles_respects_n(session):
    for title in ["A", "B", "C", "A", "B", "A"]:
        session.add(_posting(role_title=title, role_title_en=title))
    session.commit()

    rows = analysis_service.top_roles(session, n=2)
    assert len(rows) == 2
    assert rows[0] == {"label": "A", "count": 3}
    assert rows[1] == {"label": "B", "count": 2}


def test_salary_summary_ignores_nulls_per_metric(session):
    session.add_all(
        [
            _posting(salary_min=1000, salary_max=2000),
            _posting(salary_min=3000, salary_max=None),
            _posting(salary_min=None, salary_max=4000),
            _posting(salary_min=None, salary_max=None),
        ]
    )
    session.commit()

    summary = analysis_service.salary_summary(session)
    assert summary["min_salary_min"] == 1000
    assert summary["min_salary_min_count"] == 2
    assert summary["avg_salary_min"] == 2000
    assert summary["avg_salary_min_count"] == 2
    assert summary["avg_salary_max"] == 3000
    assert summary["avg_salary_max_count"] == 2
    assert summary["max_salary_max"] == 4000
    assert summary["max_salary_max_count"] == 2


def test_top_skills_uses_display_name_en(session):
    python = SkillORM(name="python", display_name="Python", display_name_en="Python")
    sql = SkillORM(name="sql", display_name="SQL", display_name_en="SQL")
    session.add_all([python, sql])
    session.flush()

    p1 = _posting(company_name="A")
    p2 = _posting(company_name="B")
    p3 = _posting(company_name="C")
    p1.skills = [python, sql]
    p2.skills = [python]
    p3.skills = [python]
    session.add_all([p1, p2, p3])
    session.commit()

    rows = analysis_service.top_skills(session, n=10)
    assert rows[0] == {"label": "Python", "count": 3}
    assert rows[1] == {"label": "SQL", "count": 1}
