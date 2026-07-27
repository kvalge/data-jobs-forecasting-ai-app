# prediction_history.py
"""BLL façade for recent forecast runs (web templates)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.dal.forecast_repository import ForecastRepository
from src.dal.session import session_scope


@dataclass
class ForecastHistory:
    recent_runs: list[Any]
    preview_results: list[dict[str, Any]]


def _result_row_to_dict(row) -> dict[str, Any]:
    return {
        "id": row.id,
        "model_name": row.model_name,
        "target_type": row.target_type,
        "target_key": row.target_key,
        "horizon_months": row.horizon_months,
        "period_start": row.period_start,
        "predicted_value": row.predicted_value,
        "metrics": row.metrics,
    }


def _run_to_dict(run) -> dict[str, Any]:
    return {
        "id": run.id,
        "created_at": run.created_at,
        "data_source": run.data_source,
        "training_window_months": run.training_window_months,
        "horizons": run.horizons,
        "models_requested": run.models_requested,
        "status": run.status,
    }


def load_forecast_history(
    *,
    run_id: int | None = None,
    recent_limit: int = 8,
    preview_limit: int = 80,
) -> ForecastHistory:
    """Load recent runs and a results preview as plain dicts for templates."""
    with session_scope() as session:
        repo = ForecastRepository(session)
        recent = repo.list_recent_runs(limit=recent_limit)
        recent_runs = [_run_to_dict(r) for r in recent]
        preview_results: list[dict[str, Any]] = []
        if run_id is not None:
            preview_results = [
                _result_row_to_dict(r) for r in repo.list_results(run_id, limit=preview_limit)
            ]
        elif recent:
            preview_results = [
                _result_row_to_dict(r)
                for r in repo.list_results(recent[0].id, limit=preview_limit)
            ]
    return ForecastHistory(recent_runs=recent_runs, preview_results=preview_results)
