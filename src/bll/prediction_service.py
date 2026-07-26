"""Orchestrate baseline + multi-model forecasts and persist runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from src.dal.forecast_repository import ForecastRepository
from src.dal.session import session_scope
from src.prediction.baseline import run_baseline_analysis
from src.prediction.data_source import DataSource, get_data_source
from src.prediction.models.base import to_month_series
from src.prediction.models.registry import ALL_RUNNABLE, MODEL_KEYS, get_forecaster

ALLOWED_WINDOWS = (12, 24, 36)
ALLOWED_HORIZONS = (3, 6, 12)
DEFAULT_TOP_K = 15


@dataclass
class PredictionRunOutcome:
    run_id: int | None
    status: str
    summary: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


def _normalize_models(models: list[str] | None) -> list[str]:
    if not models:
        return list(ALL_RUNNABLE)
    cleaned = []
    for m in models:
        key = (m or "").strip().lower()
        if key in ALL_RUNNABLE and key not in cleaned:
            cleaned.append(key)
    if not cleaned:
        raise ValueError(f"Select at least one model from {ALL_RUNNABLE}.")
    return cleaned


def _normalize_horizons(horizons: list[int] | None) -> list[int]:
    if not horizons:
        return list(ALLOWED_HORIZONS)
    cleaned = sorted({int(h) for h in horizons if int(h) in ALLOWED_HORIZONS})
    if not cleaned:
        raise ValueError(f"Select at least one horizon from {ALLOWED_HORIZONS}.")
    return cleaned


def _normalize_window(months: int) -> int:
    m = int(months)
    if m not in ALLOWED_WINDOWS:
        raise ValueError(f"training_window_months must be one of {ALLOWED_WINDOWS}.")
    return m


def _entity_series(
    monthly: pd.DataFrame,
    key_col: str,
    key: str,
    value_col: str,
) -> pd.Series:
    sub = monthly[monthly[key_col] == key][["period_start", value_col]]
    return to_month_series(sub.rename(columns={value_col: "value"}), "value")


def run_prediction(
    *,
    training_window_months: int = 24,
    horizons: list[int] | None = None,
    models: list[str] | None = None,
    data_source: str | None = None,
    top_k: int = DEFAULT_TOP_K,
    persist: bool = True,
    source: DataSource | None = None,
) -> PredictionRunOutcome:
    """Run selected analyses and optionally save to forecast_* tables."""
    window = _normalize_window(training_window_months)
    horizon_list = _normalize_horizons(horizons)
    model_list = _normalize_models(models)
    max_horizon = max(horizon_list)

    src = source or get_data_source(data_source)
    t0 = time.perf_counter()
    errors: dict[str, str] = {}
    result_rows: list[dict[str, Any]] = []
    baseline_report: dict[str, Any] | None = None

    monthly_roles = src.slice_training_window(src.load_monthly_roles(), window)
    weekly_roles = src.slice_training_window(src.load_weekly_roles(), min(window * 5, 200))
    monthly_skills = src.slice_training_window(src.load_monthly_skills(), window)
    weekly_skills = src.slice_training_window(src.load_weekly_skills(), min(window * 5, 200))

    role_ranked = (
        monthly_roles.groupby("role_title_en", as_index=False)["posting_count"]
        .sum()
        .sort_values("posting_count", ascending=False)
    )
    role_keys = role_ranked["role_title_en"].head(top_k).tolist()
    skill_ranked = (
        monthly_skills.groupby("display_name_en", as_index=False)["posting_count"]
        .sum()
        .sort_values("posting_count", ascending=False)
    )
    skill_keys = skill_ranked["display_name_en"].head(top_k).tolist()

    if "baseline" in model_list:
        try:
            baseline_report = run_baseline_analysis(
                monthly_roles=monthly_roles,
                weekly_roles=weekly_roles,
                monthly_skills=monthly_skills,
                weekly_skills=weekly_skills,
                role_keys=role_keys,
                skill_keys=skill_keys,
            )
            # Flatten a few baseline points for DB browsing
            for item in baseline_report.get("roles_monthly", []):
                result_rows.append(
                    {
                        "model_name": "baseline",
                        "target_type": "baseline_role",
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
                        "target_type": "baseline_skill",
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
        except Exception as e:  # noqa: BLE001
            errors["baseline"] = str(e)

    forecast_models = [m for m in model_list if m in MODEL_KEYS]
    for model_key in forecast_models:
        try:
            forecaster = get_forecaster(model_key)
        except Exception as e:  # noqa: BLE001
            errors[model_key] = str(e)
            continue

        # Roles demand + salary per role
        for role in role_keys:
            series = _entity_series(monthly_roles, "role_title_en", role, "posting_count")
            outcome = forecaster.forecast(series, max_horizon)
            if outcome.error:
                errors[f"{model_key}:role:{role}"] = outcome.error
            else:
                for i, point in enumerate(outcome.points, start=1):
                    result_rows.append(
                        {
                            "model_name": model_key,
                            "target_type": "role",
                            "target_key": role,
                            "horizon_months": i,
                            "period_start": point.period_start,
                            "predicted_value": point.value,
                            "metrics": outcome.metrics if i == 1 else None,
                        }
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
            if salary_out.error:
                errors[f"{model_key}:salary:{role}"] = salary_out.error
            else:
                for i, point in enumerate(salary_out.points, start=1):
                    result_rows.append(
                        {
                            "model_name": model_key,
                            "target_type": "salary_role",
                            "target_key": role,
                            "horizon_months": i,
                            "period_start": point.period_start,
                            "predicted_value": point.value,
                            "metrics": salary_out.metrics if i == 1 else None,
                        }
                    )

        # Skills demand
        for skill in skill_keys:
            series = _entity_series(monthly_skills, "display_name_en", skill, "posting_count")
            outcome = forecaster.forecast(series, max_horizon)
            if outcome.error:
                errors[f"{model_key}:skill:{skill}"] = outcome.error
                continue
            for i, point in enumerate(outcome.points, start=1):
                result_rows.append(
                    {
                        "model_name": model_key,
                        "target_type": "skill",
                        "target_key": skill,
                        "horizon_months": i,
                        "period_start": point.period_start,
                        "predicted_value": point.value,
                        "metrics": outcome.metrics if i == 1 else None,
                    }
                )

    # Filter stored forecast points to selected horizons only (keep baseline horizon 0)
    filtered_rows = []
    for row in result_rows:
        if row["model_name"] == "baseline":
            filtered_rows.append(row)
        elif row["horizon_months"] in horizon_list:
            filtered_rows.append(row)
    result_rows = filtered_rows

    elapsed = round(time.perf_counter() - t0, 3)
    meta = {
        "data_source": src.name,
        "manifest": src.load_manifest(),
        "top_k": top_k,
        "role_keys": role_keys,
        "skill_keys": skill_keys,
        "training_window_months": window,
        "horizons": horizon_list,
        "models_requested": model_list,
        "elapsed_seconds": elapsed,
        "errors": errors,
        "baseline": baseline_report,
        "completed_at": datetime.now().isoformat(timespec="seconds"),
    }

    status = "completed" if not errors else ("completed_with_errors" if result_rows else "failed")
    summary = {
        "n_results": len(result_rows),
        "roles": role_keys,
        "skills": skill_keys,
        "models": model_list,
        "horizons": horizon_list,
        "training_window_months": window,
        "elapsed_seconds": elapsed,
        "status": status,
        "error_count": len(errors),
    }

    run_id = None
    if persist:
        with session_scope() as session:
            repo = ForecastRepository(session)
            run_id = repo.save_run(
                data_source=src.name,
                training_window_months=window,
                horizons=horizon_list,
                models_requested=model_list,
                status=status,
                meta=meta,
                results=result_rows,
            )
            session.commit()
        summary["run_id"] = run_id

    return PredictionRunOutcome(run_id=run_id, status=status, summary=summary, errors=errors)
