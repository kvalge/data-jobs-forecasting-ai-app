# prediction_forecast_runner.py
"""Fit selected forecast models for roles, salary-per-role, and skills."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

import pandas as pd

from src.bll.prediction_shortlist import entity_series
from src.bll.prediction_types import TargetType

logger = logging.getLogger(__name__)


def _fmt_seconds(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes)}m {secs:.1f}s"


def run_forecast_models(
    *,
    forecast_models: list[str],
    get_forecaster: Callable[[str], Any],
    monthly_roles: pd.DataFrame,
    monthly_skills: pd.DataFrame,
    role_keys: list[str],
    skill_keys: list[str],
    max_horizon: int,
) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, float]]:
    """Return (result_rows, errors, model_timings_seconds)."""
    result_rows: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    model_timings: dict[str, float] = {}
    series_per_model = len(role_keys) * 2 + len(skill_keys)

    for model_idx, model_key in enumerate(forecast_models, start=1):
        logger.info(
            "Starting model %s (%d/%d) | ~%d series…",
            model_key,
            model_idx,
            len(forecast_models),
            series_per_model,
        )
        t_model = time.perf_counter()
        try:
            forecaster = get_forecaster(model_key)
        except Exception as e:  # noqa: BLE001
            errors[model_key] = str(e)
            model_timings[model_key] = round(time.perf_counter() - t_model, 3)
            logger.warning("Could not create forecaster %s: %s", model_key, e)
            continue

        done = 0
        for role_i, role in enumerate(role_keys, start=1):
            logger.info(
                "[%s] role demand %d/%d: %s",
                model_key,
                role_i,
                len(role_keys),
                role,
            )
            series = entity_series(
                monthly_roles, "role_title_en", role, "posting_count"
            )
            outcome = forecaster.forecast(series, max_horizon)
            done += 1
            if outcome.error:
                errors[f"{model_key}:role:{role}"] = outcome.error
                logger.warning("[%s] role %s failed: %s", model_key, role, outcome.error)
            else:
                for i, point in enumerate(outcome.points, start=1):
                    result_rows.append(
                        {
                            "model_name": model_key,
                            "target_type": TargetType.ROLE,
                            "target_key": role,
                            "horizon_months": i,
                            "period_start": point.period_start,
                            "predicted_value": point.value,
                            "metrics": outcome.metrics if i == 1 else None,
                        }
                    )

            logger.info(
                "[%s] role salary %d/%d: %s",
                model_key,
                role_i,
                len(role_keys),
                role,
            )
            sub = monthly_roles[monthly_roles["role_title_en"] == role][
                ["period_start", "avg_salary"]
            ].copy()
            if sub.empty:
                continue
            sub["period_start"] = (
                pd.to_datetime(sub["period_start"]).dt.to_period("M").dt.to_timestamp()
            )
            salary_series = (
                sub.groupby("period_start")["avg_salary"].mean().astype(float).sort_index()
            )
            full_idx = pd.period_range(
                salary_series.index.min(), salary_series.index.max(), freq="M"
            ).to_timestamp()
            salary_series = salary_series.reindex(full_idx).interpolate().bfill().ffill()

            salary_out = forecaster.forecast(salary_series, max_horizon)
            done += 1
            if salary_out.error:
                errors[f"{model_key}:salary:{role}"] = salary_out.error
                logger.warning(
                    "[%s] salary %s failed: %s", model_key, role, salary_out.error
                )
            else:
                for i, point in enumerate(salary_out.points, start=1):
                    result_rows.append(
                        {
                            "model_name": model_key,
                            "target_type": TargetType.SALARY_ROLE,
                            "target_key": role,
                            "horizon_months": i,
                            "period_start": point.period_start,
                            "predicted_value": float(round(point.value)),
                            "metrics": salary_out.metrics if i == 1 else None,
                        }
                    )

        for skill_i, skill in enumerate(skill_keys, start=1):
            logger.info(
                "[%s] skill %d/%d: %s",
                model_key,
                skill_i,
                len(skill_keys),
                skill,
            )
            series = entity_series(
                monthly_skills, "display_name_en", skill, "posting_count"
            )
            outcome = forecaster.forecast(series, max_horizon)
            done += 1
            if outcome.error:
                errors[f"{model_key}:skill:{skill}"] = outcome.error
                logger.warning("[%s] skill %s failed: %s", model_key, skill, outcome.error)
                continue
            for i, point in enumerate(outcome.points, start=1):
                result_rows.append(
                    {
                        "model_name": model_key,
                        "target_type": TargetType.SKILL,
                        "target_key": skill,
                        "horizon_months": i,
                        "period_start": point.period_start,
                        "predicted_value": point.value,
                        "metrics": outcome.metrics if i == 1 else None,
                    }
                )

        model_timings[model_key] = round(time.perf_counter() - t_model, 3)
        logger.info(
            "Finished model %s in %s (%d series attempted)",
            model_key,
            _fmt_seconds(model_timings[model_key]),
            done,
        )

    return result_rows, errors, model_timings
