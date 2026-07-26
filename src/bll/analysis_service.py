"""Aggregate job-posting stats for the analysis UI and chart export."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.dal.models import JobPostingORM, SkillORM, job_posting_skills

DEFAULT_TOP_N = 10
MIN_TOP_N = 1
MAX_TOP_N = 50


def clamp_top_n(n: int | None) -> int:
    """Clamp top-N to [1, 50]; default 10 when missing/invalid."""
    if n is None:
        return DEFAULT_TOP_N
    try:
        value = int(n)
    except (TypeError, ValueError):
        return DEFAULT_TOP_N
    return max(MIN_TOP_N, min(MAX_TOP_N, value))


def _non_blank(column):
    """SQL filter: column is not null and not blank after trim."""
    return column.isnot(None) & (func.trim(column) != "")


def top_companies(session: Session, n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    """Top N company_name values by posting count (null/blank excluded)."""
    limit = clamp_top_n(n)
    col = JobPostingORM.company_name
    rows = (
        session.query(col, func.count(JobPostingORM.id).label("count"))
        .filter(_non_blank(col))
        .group_by(col)
        .order_by(func.count(JobPostingORM.id).desc(), col.asc())
        .limit(limit)
        .all()
    )
    return [{"label": label, "count": int(count)} for label, count in rows]


def top_roles(session: Session, n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    """Top N role_title_en values by posting count (null/blank excluded)."""
    limit = clamp_top_n(n)
    col = JobPostingORM.role_title_en
    rows = (
        session.query(col, func.count(JobPostingORM.id).label("count"))
        .filter(_non_blank(col))
        .group_by(col)
        .order_by(func.count(JobPostingORM.id).desc(), col.asc())
        .limit(limit)
        .all()
    )
    return [{"label": label, "count": int(count)} for label, count in rows]


def salary_summary(session: Session) -> dict[str, Any]:
    """Min/avg/max salary stats; each metric ignores its own nulls."""
    min_row = session.query(
        func.min(JobPostingORM.salary_min),
        func.count(JobPostingORM.salary_min),
    ).filter(JobPostingORM.salary_min.isnot(None)).one()

    avg_min_row = session.query(
        func.avg(JobPostingORM.salary_min),
        func.count(JobPostingORM.salary_min),
    ).filter(JobPostingORM.salary_min.isnot(None)).one()

    avg_max_row = session.query(
        func.avg(JobPostingORM.salary_max),
        func.count(JobPostingORM.salary_max),
    ).filter(JobPostingORM.salary_max.isnot(None)).one()

    max_row = session.query(
        func.max(JobPostingORM.salary_max),
        func.count(JobPostingORM.salary_max),
    ).filter(JobPostingORM.salary_max.isnot(None)).one()

    def _float_or_none(value: Any) -> float | None:
        if value is None:
            return None
        return float(value)

    return {
        "min_salary_min": _float_or_none(min_row[0]),
        "min_salary_min_count": int(min_row[1] or 0),
        "avg_salary_min": _float_or_none(avg_min_row[0]),
        "avg_salary_min_count": int(avg_min_row[1] or 0),
        "avg_salary_max": _float_or_none(avg_max_row[0]),
        "avg_salary_max_count": int(avg_max_row[1] or 0),
        "max_salary_max": _float_or_none(max_row[0]),
        "max_salary_max_count": int(max_row[1] or 0),
    }


def top_skills(session: Session, n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    """Top N skill display_name_en (fallback display_name) by posting links."""
    limit = clamp_top_n(n)
    label = func.coalesce(
        func.nullif(func.trim(SkillORM.display_name_en), ""),
        func.nullif(func.trim(SkillORM.display_name), ""),
    )
    rows = (
        session.query(label.label("skill_label"), func.count(job_posting_skills.c.job_posting_id).label("count"))
        .select_from(SkillORM)
        .join(job_posting_skills, job_posting_skills.c.skill_id == SkillORM.id)
        .filter(label.isnot(None))
        .group_by(label)
        .order_by(func.count(job_posting_skills.c.job_posting_id).desc(), label.asc())
        .limit(limit)
        .all()
    )
    return [{"label": skill_label, "count": int(count)} for skill_label, count in rows]
