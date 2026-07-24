# session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import DATABASE_URL
from src.dal.models import Base

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables defined in models.py if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Return a new database session."""
    return SessionLocal()