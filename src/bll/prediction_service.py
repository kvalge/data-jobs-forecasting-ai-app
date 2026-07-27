"""Orchestrate baseline + multi-model forecasts and persist runs."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.bll.prediction_baseline_runner import run_baseline_rows
from src.bll.prediction_export import export_model_results_markdown
from src.bll.prediction_forecast_runner import run_forecast_models
from src.bll.prediction_shortlist import filter_rows_by_horizons, rank_top_keys
from src.bll.prediction_types import RunStatus
from src.dal.forecast_repository import ForecastRepository
from src.dal.session import session_scope
from src.prediction.data_source import DataSource, get_data_source
from src.prediction.models.registry import (
    ALL_RUNNABLE,
    DEFAULT_MODELS,
    MODEL_KEYS,
    get_forecaster,
)

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
    for name in ("prophet", "prophet.plot", "cmdstanpy", "stan"):
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
    logger.setLevel(logging.INFO)


@dataclass
class PredictionRunOutcome:
    run_id: int | None
    status: str
    summary: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


def _normalize_models(models: list[str] | None) -> list[str]:
    if not models:
        return list(DEFAULT_MODELS)
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

    role_keys = rank_top_keys(monthly_roles, "role_title_en", "posting_count", top_k)
    skill_keys = rank_top_keys(monthly_skills, "display_name_en", "posting_count", top_k)

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
        baseline_rows, baseline_report, baseline_error = run_baseline_rows(
            monthly_roles=monthly_roles,
            weekly_roles=weekly_roles,
            monthly_skills=monthly_skills,
            weekly_skills=weekly_skills,
            role_keys=role_keys,
            skill_keys=skill_keys,
        )
        if baseline_error:
            errors["baseline"] = baseline_error
        result_rows.extend(baseline_rows)
        model_timings["baseline"] = round(time.perf_counter() - t_model, 3)
        logger.info(
            "Finished model baseline in %s",
            _fmt_seconds(model_timings["baseline"]),
        )

    if forecast_models:
        forecast_rows, forecast_errors, forecast_timings = run_forecast_models(
            forecast_models=forecast_models,
            get_forecaster=get_forecaster,
            monthly_roles=monthly_roles,
            monthly_skills=monthly_skills,
            role_keys=role_keys,
            skill_keys=skill_keys,
            max_horizon=max_horizon,
        )
        result_rows.extend(forecast_rows)
        errors.update(forecast_errors)
        model_timings.update(forecast_timings)

    result_rows = filter_rows_by_horizons(result_rows, horizon_list)

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

    if not errors:
        status = RunStatus.COMPLETED
    elif result_rows:
        status = RunStatus.COMPLETED_WITH_ERRORS
    else:
        status = RunStatus.FAILED

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
