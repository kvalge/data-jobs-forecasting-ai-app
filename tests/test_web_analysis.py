"""Flask analysis UI tests — analysis façade mocked."""

from unittest.mock import MagicMock

import pytest

from src.web import create_app
import src.web.routes.analysis as analysis_routes


@pytest.fixture
def app():
    application = create_app(run_startup=False)
    application.config.update(TESTING=True, SECRET_KEY="test-secret", WTF_CSRF_ENABLED=False)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_analysis_page(client):
    response = client.get("/analysis")
    assert response.status_code == 200
    assert b"Data analysis" in response.data
    assert b'name="companies"' in response.data
    assert b'name="n"' in response.data


def test_post_without_selection_shows_error(client):
    response = client.post("/analysis", data={"n": "5"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Select at least one analysis option" in response.data


def test_post_runs_selected_and_exports(client, monkeypatch):
    results = {
        "companies": [{"label": "Acme", "count": 2}],
        "salary": {
            "min_salary_min": 1000,
            "min_salary_min_count": 1,
            "avg_salary_min": 1000,
            "avg_salary_min_count": 1,
            "avg_salary_max": 2000,
            "avg_salary_max_count": 1,
            "max_salary_max": 2000,
            "max_salary_max_count": 1,
        },
    }
    runner = MagicMock(return_value=(results, ["a.png", "b.png"]))
    monkeypatch.setattr(analysis_routes, "run_analysis", runner)

    response = client.post(
        "/analysis",
        data={"companies": "on", "salary": "on", "n": "5"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Acme" in response.data
    assert b"Salary summary" in response.data
    assert b"Updated 2 chart file" in response.data
    runner.assert_called_once()
    assert runner.call_args.args[0] == {"companies", "salary"}
    assert runner.call_args.args[1] == 5
