"""Orchestrate baseline + multi-model forecasts and persist runs."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from src.bll.prediction_export import export_model_results_markdown
from src.dal.forecast_repository import ForecastRepository
from src.dal.session import session_scope
from src.prediction.baseline import run_baseline_analysis
from src.prediction.data_source import DataSource, get_data_source
from src.prediction.models.base import to_month_series
from src.prediction.models.registry import ALL_RUNNABLE, MODEL_KEYS, get_forecaster

ALLOWED_WINDOWS = (12, 24, 36)
ALLOWED_HORIZONS = (3, 6, 12)
DEFAULT_TOP_K = 15

logger = logging.getLogger(__name__)

_NOISY_LOGGERS_QUIETED = False


def _quiet_third_party_logs() -> None:
    """Reduce Prophet / cmdstan noise so progress lines stay readable."""
    global _NOISY_LOGGERS_QUIETED
    if _NOISY_LOGGERS_QUIETED:
        return
    for name in (
        "prophet",
        "prophet.plot",
        "cmdstanpy",
        "stan",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)
    _NOISY_LOGGERS_QUIETED = True


def _ensure_logging() -> None:
    """Make sure INFO progress lines appear in the terminal (CLI / Flask)."""
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s [%(name)s] %(message)s",
        )
    elif root.level > logging.INFO:
        root.setLevel(logging.INFO)
    # Keep our package logger at INFO even if root is noisier/quieter
    logger.setLevel(logging.INFO)


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


def _fmt_seconds(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes)}m {secs:.1f}s"


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
    _ensure_logging()
    _quiet_third_party_logs()

    window = _normalize_window(training_window_months)
    horizon_list = _normalize_horizons(horizons)
    model_list = _normalize_models(models)
    max_horizon = max(horizon_list)

    src = source or get_data_source(data_source)
    t0 = time.perf_counter()
    errors: dict[str, str] = {}
    result_rows: list[dict[str, Any]] = []
    baseline_report: dict[str, Any] | None = None
    model_timings: dict[str, float] = {}

    logger.info(
        "Prediction start | source=%s window=%sm horizons=%s models=%s top_k=%s",
        src.name,
        window,
        horizon_list,
        model_list,
        top_k,
    )

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

    forecast_models = [m for m in model_list if m in MODEL_KEYS]
    series_per_forecast_model = len(role_keys) * 2 + len(skill_keys)
    total_series = series_per_forecast_model * len(forecast_models)
    logger.info(
        "Loaded data | roles=%d skills=%d | forecast models=%d | series to fit≈%d",
        len(role_keys),
        len(skill_keys),
        len(forecast_models),
        total_series,
    )

    if "baseline" in model_list:
        logger.info("Starting model baseline…")
        t_model = time.perf_counter()
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
            logger.warning("baseline failed: %s", e)
        model_timings["baseline"] = round(time.perf_counter() - t_model, 3)
        logger.info(
            "Finished model baseline in %s",
            _fmt_seconds(model_timings["baseline"]),
        )

    for model_idx, model_key in enumerate(forecast_models, start=1):
        logger.info(
            "Starting model %s (%d/%d) | ~%d series…",
            model_key,
            model_idx,
            len(forecast_models),
            series_per_forecast_model,
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

        # Roles demand + salary per role
        for role_i, role in enumerate(role_keys, start=1):
            logger.info(
                "[%s] role demand %d/%d: %s",
                model_key,
                role_i,
                len(role_keys),
                role,
            )
            series = _entity_series(monthly_roles, "role_title_en", role, "posting_count")
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
                            "target_type": "role",
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
                            "target_type": "salary_role",
                            "target_key": role,
                            "horizon_months": i,
                            "period_start": point.period_start,
                            "predicted_value": float(round(point.value)),
                            "metrics": salary_out.metrics if i == 1 else None,
                        }
                    )

        # Skills demand
        for skill_i, skill in enumerate(skill_keys, start=1):
            logger.info(
                "[%s] skill %d/%d: %s",
                model_key,
                skill_i,
                len(skill_keys),
                skill,
            )
            series = _entity_series(monthly_skills, "display_name_en", skill, "posting_count")
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
                        "target_type": "skill",
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

    # Filter stored forecast points to selected horizons only (keep baseline horizon 0)
    filtered_rows = []
    for row in result_rows:
        if row["model_name"] == "baseline":
            filtered_rows.append(row)
        elif row["horizon_months"] in horizon_list:
            filtered_rows.append(row)
    result_rows = filtered_rows

    elapsed = round(time.perf_counter() - t0, 3)
    logger.info("── Model timings ──")
    for name, secs in model_timings.items():
        logger.info("  %s: %s", name, _fmt_seconds(secs))
    logger.info("  TOTAL: %s", _fmt_seconds(elapsed))

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
        "model_timings_seconds": model_timings,
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
        "model_timings_seconds": model_timings,
        "data_source": src.name,
        "status": status,
        "error_count": len(errors),
    }

    run_id = None
    if persist:
        logger.info("Saving run to database…")
        t_save = time.perf_counter()
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
        logger.info(
            "Saved run_id=%s in %s | status=%s results=%d warnings=%d",
            run_id,
            _fmt_seconds(time.perf_counter() - t_save),
            status,
            len(result_rows),
            len(errors),
        )
    else:
        logger.info(
            "Prediction finished (not persisted) | status=%s results=%d warnings=%d | total %s",
            status,
            len(result_rows),
            len(errors),
            _fmt_seconds(elapsed),
        )

    try:
        export_path = export_model_results_markdown(
            run_id=run_id,
            status=status,
            summary=summary,
            results=result_rows,
        )
        summary["results_export_path"] = str(export_path)
        logger.info("Wrote model results markdown to %s", export_path)
    except OSError as e:
        logger.warning("Could not write model results file: %s", e)

    return PredictionRunOutcome(run_id=run_id, status=status, summary=summary, errors=errors)
