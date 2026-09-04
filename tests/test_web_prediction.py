"""Flask prediction UI — orchestration mocked."""

from unittest.mock import MagicMock

import pytest

from src.bll.prediction_history import ForecastHistory
from src.bll.prediction_service import PredictionRunOutcome
from src.web import create_app
import src.web.routes.prediction as prediction_routes


@pytest.fixture
def app():
    application = create_app(run_startup=False)
    application.config.update(TESTING=True, SECRET_KEY="test-secret", WTF_CSRF_ENABLED=False)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_prediction_page(client, monkeypatch):
    monkeypatch.setattr(
        prediction_routes,
        "load_forecast_history",
        lambda **kwargs: ForecastHistory(recent_runs=[], preview_results=[]),
    )

    response = client.get("/prediction")
    assert response.status_code == 200
    assert b"Time series prediction (fake data)" in response.data
    assert b'name="training_window"' in response.data
    assert b"/prediction/database" in response.data
    assert b"What each model does" in response.data
    assert b"minimum history" in response.data.lower() or b"Minimum history" in response.data


def test_get_prediction_database_page(client, monkeypatch):
    monkeypatch.setattr(
        prediction_routes,
        "load_forecast_history",
        lambda **kwargs: ForecastHistory(recent_runs=[], preview_results=[]),
    )

    response = client.get("/prediction/database")
    assert response.status_code == 200
    assert b"Time series prediction (database)" in response.data
    assert b"saved job postings" in response.data
    assert b'name="training_window"' in response.data
    assert b"Sparse history" in response.data or b"enough months" in response.data


def test_post_prediction_runs_service(client, monkeypatch):
    monkeypatch.setattr(
        prediction_routes,
        "load_forecast_history",
        lambda **kwargs: ForecastHistory(recent_runs=[], preview_results=[]),
    )

    outcome = PredictionRunOutcome(
        run_id=7,
        status="completed",
        summary={
            "n_results": 10,
            "models": ["baseline"],
            "horizons": [3],
            "training_window_months": 12,
            "elapsed_seconds": 0.1,
            "model_timings_seconds": {"baseline": 0.1},
            "data_source": "fake",
            "error_count": 0,
            "roles": ["Data Engineer"],
            "skills": ["Python"],
        },
        errors={},
    )
    runner = MagicMock(return_value=outcome)
    monkeypatch.setattr(prediction_routes, "run_prediction", runner)

    response = client.post(
        "/prediction",
        data={
            "training_window": "12",
            "horizon": "3",
            "model_baseline": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Prediction run #7" in response.data
    assert b"Baseline only" in response.data
    assert b"not</strong> a forecast" in response.data or b"not a forecast" in response.data.lower()
    assert b"most recent month" in response.data.lower()
    assert b"historical" in response.data.lower() or b"Historical" in response.data
    assert b"Fake" in response.data or b"fake" in response.data
    runner.assert_called_once()
    assert runner.call_args.kwargs["data_source"] == "fake"


def test_post_prediction_shows_error_explanations(client, monkeypatch):
    monkeypatch.setattr(
        prediction_routes,
        "load_forecast_history",
        lambda **kwargs: ForecastHistory(recent_runs=[], preview_results=[]),
    )

    outcome = PredictionRunOutcome(
        run_id=11,
        status="completed_with_errors",
        summary={
            "n_results": 4,
            "models": ["arima"],
            "horizons": [3],
            "training_window_months": 12,
            "elapsed_seconds": 0.2,
            "model_timings_seconds": {"arima": 0.2},
            "data_source": "database",
            "error_count": 1,
            "roles": ["Data Engineer"],
            "skills": [],
        },
        errors={
            "arima:role:Data Engineer": "Need at least 8 months of history for ARIMA/SARIMA.",
        },
    )
    monkeypatch.setattr(prediction_routes, "run_prediction", MagicMock(return_value=outcome))

    response = client.post(
        "/prediction/database",
        data={
            "training_window": "12",
            "horizon": "3",
            "model_arima": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Warnings" in response.data
    assert b"too few months" in response.data.lower() or b"few months of history" in response.data.lower()
    assert b"arima:role:Data Engineer" not in response.data


def test_post_prediction_database_runs_service(client, monkeypatch):
    monkeypatch.setattr(
        prediction_routes,
        "load_forecast_history",
        lambda **kwargs: ForecastHistory(recent_runs=[], preview_results=[]),
    )

    outcome = PredictionRunOutcome(
        run_id=9,
        status="completed",
        summary={
            "n_results": 4,
            "models": ["baseline"],
            "horizons": [3],
            "training_window_months": 12,
            "elapsed_seconds": 0.2,
            "model_timings_seconds": {"baseline": 0.2},
            "data_source": "database",
            "error_count": 0,
            "roles": ["Data Engineer"],
            "skills": ["Python"],
        },
        errors={},
    )
    runner = MagicMock(return_value=outcome)
    monkeypatch.setattr(prediction_routes, "run_prediction", runner)

    response = client.post(
        "/prediction/database",
        data={
            "training_window": "12",
            "horizon": "3",
            "model_baseline": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Prediction run #9" in response.data
    assert b"database" in response.data.lower()
    runner.assert_called_once()
    assert runner.call_args.kwargs["data_source"] == "database"
