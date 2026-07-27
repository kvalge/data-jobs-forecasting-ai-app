# prediction_baseline_runner.py
"""Run baseline analysis and flatten rows for forecast_* persistence."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from src.bll.prediction_types import TargetType
from src.prediction.baseline import run_baseline_analysis

logger = logging.getLogger(__name__)


def run_baseline_rows(
    *,
    monthly_roles: pd.DataFrame,
    weekly_roles: pd.DataFrame,
    monthly_skills: pd.DataFrame,
    weekly_skills: pd.DataFrame,
    role_keys: list[str],
    skill_keys: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None, str | None]:
    """Return (result_rows, baseline_report, error_message_or_none)."""
    result_rows: list[dict[str, Any]] = []
    try:
        baseline_report = run_baseline_analysis(
            monthly_roles=monthly_roles,
            weekly_roles=weekly_roles,
            monthly_skills=monthly_skills,
            weekly_skills=weekly_skills,
            role_keys=role_keys,
            skill_keys=skill_keys,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("baseline failed: %s", e)
        return [], None, str(e)

    for item in baseline_report.get("roles_monthly", []):
        result_rows.append(
            {
                "model_name": "baseline",
                "target_type": TargetType.BASELINE_ROLE,
                "target_key": item["key"],
                "horizon_months": 0,
                "period_start": None,
                "predicted_value": item.get("latest"),
                "metrics": {
                    "ma_3": item.get("ma_3"),
                    "ma_6": item.get("ma_6"),
                    "ma_12": item.get("ma_12"),
                    "growth_rate_pct": item.get("growth_rate_pct"),
                    "trend": item.get("trend"),
                },
            }
        )
    for item in baseline_report.get("skills_monthly", []):
        result_rows.append(
            {
                "model_name": "baseline",
                "target_type": TargetType.BASELINE_SKILL,
                "target_key": item["key"],
                "horizon_months": 0,
                "period_start": None,
                "predicted_value": item.get("latest"),
                "metrics": {
                    "ma_3": item.get("ma_3"),
                    "growth_rate_pct": item.get("growth_rate_pct"),
                    "trend": item.get("trend"),
                },
            }
        )
    return result_rows, baseline_report, None
