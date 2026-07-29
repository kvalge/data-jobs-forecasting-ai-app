"""Flask routes for prediction / forecasting."""

from __future__ import annotations

from flask import Blueprint, flash, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from src.bll.prediction_history import load_forecast_history
from src.bll.prediction_service import ALLOWED_HORIZONS, ALLOWED_WINDOWS, run_prediction
from src.prediction.models.registry import ALL_RUNNABLE, DEFAULT_MODELS

prediction_bp = Blueprint("prediction", __name__)


def _parse_int_list(name: str, allowed: tuple[int, ...]) -> list[int]:
    values = []
    for raw in request.form.getlist(name):
        try:
            v = int(raw)
        except (TypeError, ValueError):
            continue
        if v in allowed and v not in values:
            values.append(v)
    return values


def _render_prediction_page(*, data_source: str):
    """Shared fake / database prediction UI."""
    selected_models = list(DEFAULT_MODELS)
    selected_horizons = list(ALLOWED_HORIZONS)
    training_window = 24
    outcome = None
    is_database = data_source == "database"
    form_endpoint = (
        "prediction.prediction_database_page"
        if is_database
        else "prediction.prediction_page"
    )

    if request.method == "POST":
        selected_models = [
            m for m in ALL_RUNNABLE if request.form.get(f"model_{m}") == "on"
        ]
        selected_horizons = _parse_int_list("horizon", ALLOWED_HORIZONS)
        try:
            training_window = int(request.form.get("training_window") or 24)
        except (TypeError, ValueError):
            training_window = 24

        if not selected_models:
            flash("Select at least one model.", "error")
        elif not selected_horizons:
            flash("Select at least one forecast horizon.", "error")
        else:
            try:
                outcome = run_prediction(
                    training_window_months=training_window,
                    horizons=selected_horizons,
                    models=selected_models,
                    data_source=data_source,
                    persist=True,
                )
                flash(
                    f"Prediction run #{outcome.run_id} finished with status "
                    f"{outcome.status} ({outcome.summary.get('n_results', 0)} result rows).",
                    "success" if outcome.status != "failed" else "error",
                )
                if outcome.errors:
                    flash(
                        f"{len(outcome.errors)} model/target warning(s); see summary.",
                        "info",
                    )
            except (ValueError, NotImplementedError) as e:
                flash(str(e), "error")
            except (SQLAlchemyError, EnvironmentError, FileNotFoundError, OSError) as e:
                flash(f"Prediction failed: {e}", "error")

    try:
        history = load_forecast_history(
            run_id=outcome.run_id if outcome else None,
        )
        recent_runs = history.recent_runs
        preview_results = history.preview_results
    except Exception:  # noqa: BLE001 — page still useful without DB history
        recent_runs = []
        preview_results = []

    return render_template(
        "prediction.html",
        data_source=data_source,
        form_endpoint=form_endpoint,
        page_heading=(
            "Time series prediction (database)"
            if is_database
            else "Time series prediction (fake data)"
        ),
        all_models=ALL_RUNNABLE,
        selected_models=selected_models,
        allowed_horizons=ALLOWED_HORIZONS,
        selected_horizons=selected_horizons,
        allowed_windows=ALLOWED_WINDOWS,
        training_window=training_window,
        outcome=outcome,
        recent_runs=recent_runs,
        preview_results=preview_results,
        default_models=DEFAULT_MODELS,
    )


@prediction_bp.route("/prediction", methods=["GET", "POST"])
def prediction_page():
    """Forecast using synthetic series under data/fake/."""
    return _render_prediction_page(data_source="fake")


@prediction_bp.route("/prediction/database", methods=["GET", "POST"])
def prediction_database_page():
    """Forecast using aggregates from saved job_postings in PostgreSQL."""
    return _render_prediction_page(data_source="database")
