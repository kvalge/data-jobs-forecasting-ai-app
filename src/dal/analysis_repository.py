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
        """Min/avg/max salary stats; each metric ignores its own nulls (one round-trip)."""
        row = self.session.query(
            func.min(JobPostingORM.salary_min),
            func.count(JobPostingORM.salary_min),
            func.avg(JobPostingORM.salary_min),
            func.avg(JobPostingORM.salary_max),
            func.count(JobPostingORM.salary_max),
            func.max(JobPostingORM.salary_max),
        ).one()

        def _float_or_none(value: Any) -> float | None:
            if value is None:
                return None
            return float(value)

        def _round_salary(value: Any) -> float | None:
            number = _float_or_none(value)
            if number is None:
                return None
            return float(round(number))

        # avg_salary_min uses count of non-null salary_min; avg_max uses salary_max count.
        # min/max use the same underlying non-null populations as the counts above.
        min_val, min_count, avg_min, avg_max, max_count, max_val = row
        # Separate counts for avg_min vs avg_max: reuse min_count / max_count which match
        # COUNT(salary_min) and COUNT(salary_max) respectively.
        return {
            "min_salary_min": _round_salary(min_val),
            "min_salary_min_count": int(min_count or 0),
            "avg_salary_min": _round_salary(avg_min),
            "avg_salary_min_count": int(min_count or 0),
            "avg_salary_max": _round_salary(avg_max),
            "avg_salary_max_count": int(max_count or 0),
            "max_salary_max": _round_salary(max_val),
            "max_salary_max_count": int(max_count or 0),
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
