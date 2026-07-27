"""Tests for session_scope commit / rollback ownership."""

from datetime import date
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.dal.job_posting_repository import JobPostingRepository
from src.dal.models import Base, JobPostingORM
from src.dal.session import session_scope
from src.domain.job_posting_entity import JobPostingEntity
from src.domain.work_type import WorkType


@pytest.fixture
def sqlite_engine(monkeypatch):
    # Shared in-memory DB across connections (needed to assert after session close).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    monkeypatch.setattr("src.dal.session._engine", engine)
    monkeypatch.setattr("src.dal.session._SessionLocal", SessionLocal)
    monkeypatch.setattr("src.dal.session.config.DATABASE_URL", "sqlite://")
    yield engine
    engine.dispose()
    monkeypatch.setattr("src.dal.session._engine", None)
    monkeypatch.setattr("src.dal.session._SessionLocal", None)


def test_session_scope_commits_on_success(sqlite_engine):
    with session_scope() as session:
        repo = JobPostingRepository(session)
        saved = repo.save(
            JobPostingEntity(
                role_title="Engineer",
                work_type=WorkType.remote,
                skills=["Python"],
                skills_en=["Python"],
                date_added=date.today(),
                raw_text="Role: Engineer",
                content_hash="abc123",
            )
        )
        assert saved.id is not None

    with sqlite_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM job_postings")).scalar()
    assert count == 1


def test_session_scope_rolls_back_on_error(sqlite_engine):
    with pytest.raises(RuntimeError, match="boom"):
        with session_scope() as session:
            repo = JobPostingRepository(session)
            repo.save(
                JobPostingEntity(
                    role_title="Analyst",
                    work_type=WorkType.onsite,
                    skills=[],
                    skills_en=[],
                    date_added=date.today(),
                    raw_text="Role: Analyst",
                    content_hash="def456",
                )
            )
            raise RuntimeError("boom")

    with sqlite_engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM job_postings")).scalar()
    assert count == 0


def test_repository_save_does_not_commit_itself(sqlite_engine):
    SessionLocal = sessionmaker(bind=sqlite_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        repo = JobPostingRepository(session)
        with patch.object(session, "commit", wraps=session.commit) as commit:
            repo.save(
                JobPostingEntity(
                    role_title="Dev",
                    work_type=WorkType.hybrid,
                    skills=[],
                    skills_en=[],
                    date_added=date.today(),
                    raw_text="Dev",
                    content_hash="ghi789",
                )
            )
            commit.assert_not_called()
        assert session.query(JobPostingORM).count() == 1
        session.rollback()
        assert session.query(JobPostingORM).count() == 0
    finally:
        session.close()
