# analysis_repository.py
"""SQL aggregations for descriptive analysis (DAL)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.dal.models import JobPostingORM, SkillORM, job_posting_skills


def _non_blank(column):
    """SQL filter: column is not null and not blank after trim."""
    return column.isnot(None) & (func.trim(column) != "")


class AnalysisRepository:
    """Read-only aggregate queries over job postings and skills."""

    def __init__(self, session: Session):
        self.session = session

    def top_companies(self, limit: int) -> list[dict[str, Any]]:
        col = JobPostingORM.company_name
        rows = (
            self.session.query(col, func.count(JobPostingORM.id).label("count"))
            .filter(_non_blank(col))
            .group_by(col)
            .order_by(func.count(JobPostingORM.id).desc(), col.asc())
            .limit(limit)
            .all()
        )
        return [{"label": label, "count": int(count)} for label, count in rows]

    def top_roles(self, limit: int) -> list[dict[str, Any]]:
        col = JobPostingORM.role_title_en
        rows = (
            self.session.query(col, func.count(JobPostingORM.id).label("count"))
            .filter(_non_blank(col))
            .group_by(col)
            .order_by(func.count(JobPostingORM.id).desc(), col.asc())
            .limit(limit)
            .all()
        )
        return [{"label": label, "count": int(count)} for label, count in rows]

    def salary_summary(self) -> dict[str, Any]:
        """Min/avg/max salary stats; each metric ignores its own nulls."""
        min_row = (
            self.session.query(
                func.min(JobPostingORM.salary_min),
                func.count(JobPostingORM.salary_min),
            )
            .filter(JobPostingORM.salary_min.isnot(None))
            .one()
        )

        avg_min_row = (
            self.session.query(
                func.avg(JobPostingORM.salary_min),
                func.count(JobPostingORM.salary_min),
            )
            .filter(JobPostingORM.salary_min.isnot(None))
            .one()
        )

        avg_max_row = (
            self.session.query(
                func.avg(JobPostingORM.salary_max),
                func.count(JobPostingORM.salary_max),
            )
            .filter(JobPostingORM.salary_max.isnot(None))
            .one()
        )

        max_row = (
            self.session.query(
                func.max(JobPostingORM.salary_max),
                func.count(JobPostingORM.salary_max),
            )
            .filter(JobPostingORM.salary_max.isnot(None))
            .one()
        )

        def _float_or_none(value: Any) -> float | None:
            if value is None:
                return None
            return float(value)

        def _round_salary(value: Any) -> float | None:
            number = _float_or_none(value)
            if number is None:
                return None
            return float(round(number))

        return {
            "min_salary_min": _round_salary(min_row[0]),
            "min_salary_min_count": int(min_row[1] or 0),
            "avg_salary_min": _round_salary(avg_min_row[0]),
            "avg_salary_min_count": int(avg_min_row[1] or 0),
            "avg_salary_max": _round_salary(avg_max_row[0]),
            "avg_salary_max_count": int(avg_max_row[1] or 0),
            "max_salary_max": _round_salary(max_row[0]),
            "max_salary_max_count": int(max_row[1] or 0),
        }

    def top_skills(self, limit: int) -> list[dict[str, Any]]:
        label = func.coalesce(
            func.nullif(func.trim(SkillORM.display_name_en), ""),
            func.nullif(func.trim(SkillORM.display_name), ""),
        )
        rows = (
            self.session.query(
                label.label("skill_label"),
                func.count(job_posting_skills.c.job_posting_id).label("count"),
            )
            .select_from(SkillORM)
            .join(job_posting_skills, job_posting_skills.c.skill_id == SkillORM.id)
            .filter(label.isnot(None))
            .group_by(label)
            .order_by(
                func.count(job_posting_skills.c.job_posting_id).desc(), label.asc()
            )
            .limit(limit)
            .all()
        )
        return [
            {"label": skill_label, "count": int(count)}
            for skill_label, count in rows
        ]
