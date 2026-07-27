# analysis_facade.py
"""BLL façade for analysis queries + chart export."""

from __future__ import annotations

from typing import Any

from src.bll import analysis_service, chart_export
from src.dal.session import session_scope


def run_analysis(
    selected: set[str],
    n: int,
) -> tuple[dict[str, Any], list]:
    """Run selected aggregates and write chart PNGs.

    Returns (results_dict, written_chart_paths).
    """
    companies = roles = salary = skills = None
    with session_scope() as session:
        if "companies" in selected:
            companies = analysis_service.top_companies(session, n)
        if "roles" in selected:
            roles = analysis_service.top_roles(session, n)
        if "salary" in selected:
            salary = analysis_service.salary_summary(session)
        if "skills" in selected:
            skills = analysis_service.top_skills(session, n)

    results: dict[str, Any] = {}
    if companies is not None:
        results["companies"] = companies
    if roles is not None:
        results["roles"] = roles
    if salary is not None:
        results["salary"] = salary
    if skills is not None:
        results["skills"] = skills

    written = chart_export.export_selected(
        companies=companies,
        roles=roles,
        salary=salary,
        skills=skills,
    )
    return results, written
