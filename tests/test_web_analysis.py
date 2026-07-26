"""Flask analysis UI tests — DB and chart export mocked."""

from unittest.mock import MagicMock

import pytest

from src.web import create_app
import src.web.routes.analysis as analysis_routes


@pytest.fixture
def app():
    application = create_app(run_startup=False)
    application.config.update(TESTING=True, SECRET_KEY="test-secret")
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def _patch_analysis(monkeypatch, *, companies=None, roles=None, salary=None, skills=None):
    class FakeScope:
        def __enter__(self):
            return MagicMock()

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(analysis_routes, "session_scope", lambda: FakeScope())
    monkeypatch.setattr(
        analysis_routes.analysis_service,
        "top_companies",
        lambda session, n: companies if companies is not None else [],
    )
    monkeypatch.setattr(
        analysis_routes.analysis_service,
        "top_roles",
        lambda session, n: roles if roles is not None else [],
    )
    monkeypatch.setattr(
        analysis_routes.analysis_service,
        "salary_summary",
        lambda session: salary
        if salary is not None
        else {
            "min_salary_min": None,
            "min_salary_min_count": 0,
            "avg_salary_min": None,
            "avg_salary_min_count": 0,
            "avg_salary_max": None,
            "avg_salary_max_count": 0,
            "max_salary_max": None,
            "max_salary_max_count": 0,
        },
    )
    monkeypatch.setattr(
        analysis_routes.analysis_service,
        "top_skills",
        lambda session, n: skills if skills is not None else [],
    )
    export = MagicMock(return_value=["a.png", "b.png"])
    monkeypatch.setattr(analysis_routes.chart_export, "export_selected", export)
    return export


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
    export = _patch_analysis(
        monkeypatch,
        companies=[{"label": "Acme", "count": 2}],
        salary={
            "min_salary_min": 1000,
            "min_salary_min_count": 1,
            "avg_salary_min": 1000,
            "avg_salary_min_count": 1,
            "avg_salary_max": 2000,
            "avg_salary_max_count": 1,
            "max_salary_max": 2000,
            "max_salary_max_count": 1,
        },
    )
    response = client.post(
        "/analysis",
        data={"companies": "on", "salary": "on", "n": "5"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Acme" in response.data
    assert b"Salary summary" in response.data
    assert b"Updated 2 chart file" in response.data
    export.assert_called_once()
    kwargs = export.call_args.kwargs
    assert kwargs["companies"] == [{"label": "Acme", "count": 2}]
    assert kwargs["roles"] is None
    assert kwargs["skills"] is None
    assert kwargs["salary"]["min_salary_min"] == 1000
