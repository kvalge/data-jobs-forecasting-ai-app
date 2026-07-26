# session.py
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

import src.config as config

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_engine() -> Engine:
    """Create the engine on first use (after validate_config has set DATABASE_URL)."""
    global _engine, _SessionLocal

    if _engine is None:
        if not config.DATABASE_URL:
            raise EnvironmentError(
                "DATABASE_URL is not configured. Call validate_config() at startup."
            )
        _engine = create_engine(config.DATABASE_URL, echo=False)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

    return _engine


def init_db() -> None:
    """Apply Alembic migrations up to head (preferred over create_all)."""
    if not config.DATABASE_URL:
        raise EnvironmentError(
            "DATABASE_URL is not configured. Call validate_config() at startup."
        )
    alembic_cfg = Config(str(_PROJECT_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", config.DATABASE_URL)
    # Ensure script location resolves from project root
    alembic_cfg.set_main_option("script_location", str(_PROJECT_ROOT / "alembic"))
    command.upgrade(alembic_cfg, "head")
    # Engine may be used after migrations
    get_engine()


def get_session() -> Session:
    """Return a new database session."""
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal()


@contextmanager
def session_scope() -> Iterator[Session]:
    """One session per operation: rollback on error, always close."""
    session = get_session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
