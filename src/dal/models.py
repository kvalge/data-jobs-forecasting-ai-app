# models.py
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Date,
    DateTime,
    Boolean,
    Enum as SAEnum,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship

from src.domain.work_type import WorkType

Base = declarative_base()

# Many-to-many association table between job postings and skills
job_posting_skills = Table(
    "job_posting_skills",
    Base.metadata,
    Column("job_posting_id", Integer, ForeignKey("job_postings.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)


class JobPostingORM(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, nullable=True)
    role_title = Column(String, nullable=False)
    responsibilities = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    application_deadline = Column(Date, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String, nullable=True)
    location = Column(String, nullable=True)
    work_type = Column(SAEnum(WorkType), nullable=False, default=WorkType.unknown)
    has_nondiscrimination_disclaimer = Column(Boolean, nullable=False, default=False)
    date_added = Column(Date, nullable=False, default=date.today)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    skills = relationship("SkillORM", secondary=job_posting_skills, back_populates="job_postings")


class SkillORM(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    job_postings = relationship("JobPostingORM", secondary=job_posting_skills, back_populates="skills")