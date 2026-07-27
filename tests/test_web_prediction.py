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
    assert b"Time series prediction" in response.data
    assert b'name="training_window"' in response.data


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
    assert b"historical" in response.data.lower() or b"Historical" in response.data
    assert b"Fake" in response.data or b"fake" in response.data
    runner.assert_called_once()
