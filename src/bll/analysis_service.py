"""Aggregate job-posting stats for the analysis UI and chart export.

SQL lives in ``AnalysisRepository``; this module clamps top-N and delegates.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from src.dal.analysis_repository import AnalysisRepository

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


def top_companies(session: Session, n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    """Top N company_name values by posting count (null/blank excluded)."""
    return AnalysisRepository(session).top_companies(clamp_top_n(n))


def top_roles(session: Session, n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    """Top N role_title_en values by posting count (null/blank excluded)."""
    return AnalysisRepository(session).top_roles(clamp_top_n(n))


def salary_summary(session: Session) -> dict[str, Any]:
    """Min/avg/max salary stats; each metric ignores its own nulls."""
    return AnalysisRepository(session).salary_summary()


def top_skills(session: Session, n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    """Top N skill display_name_en (fallback display_name) by posting links."""
    return AnalysisRepository(session).top_skills(clamp_top_n(n))
