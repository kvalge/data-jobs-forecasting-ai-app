"""Markdown export for prediction model results."""

from src.bll.prediction_export import (
    RESULTS_PATH_DATABASE,
    RESULTS_PATH_FAKE,
    export_model_results_markdown,
    results_path_for_source,
)


def test_results_path_for_source():
    assert results_path_for_source("fake") == RESULTS_PATH_FAKE
    assert results_path_for_source("database") == RESULTS_PATH_DATABASE
    assert results_path_for_source("db") == RESULTS_PATH_DATABASE
    assert results_path_for_source(None) == RESULTS_PATH_FAKE


def test_export_model_results_markdown_orders_by_value(tmp_path):
    path = tmp_path / "model_results.md"
    out = export_model_results_markdown(
        run_id=3,
        status="completed",
        summary={
            "training_window_months": 24,
            "horizons": [3],
            "models": ["rf"],
            "elapsed_seconds": 1.2,
            "model_timings_seconds": {"rf": 1.1},
            "data_source": "fake",
            "roles": ["Data Analyst"],
            "skills": ["Python"],
        },
        results=[
            {
                "model_name": "rf",
                "target_type": "role",
                "target_key": "Low",
                "horizon_months": 3,
                "period_start": "2026-10-01",
                "predicted_value": 2.0,
            },
            {
                "model_name": "rf",
                "target_type": "salary_role",
                "target_key": "Data Analyst",
                "horizon_months": 3,
                "period_start": "2026-10-01",
                "predicted_value": 4123.7,
            },
            {
                "model_name": "rf",
                "target_type": "role",
                "target_key": "High",
                "horizon_months": 3,
                "period_start": "2026-10-01",
                "predicted_value": 9.0,
            },
        ],
        path=path,
    )
    text = out.read_text(encoding="utf-8")
    assert "Prediction model results (fake data)" in text
    assert "Fake / synthetic" in text
    assert "historical" in text.lower()
    assert "4124" in text  # salary rounded to whole number
    # Higher role value appears before lower within the rf table
    high_pos = text.index("High")
    low_pos = text.index("Low")
    assert high_pos < low_pos


def test_export_defaults_to_separate_paths_by_source(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.bll.prediction_export._RESULTS_DIR",
        tmp_path,
    )
    monkeypatch.setattr(
        "src.bll.prediction_export.RESULTS_PATH_FAKE",
        tmp_path / "model_results_fake.md",
    )
    monkeypatch.setattr(
        "src.bll.prediction_export.RESULTS_PATH_DATABASE",
        tmp_path / "model_results_database.md",
    )

    fake_out = export_model_results_markdown(
        run_id=1,
        status="completed",
        summary={"data_source": "fake", "models": ["baseline"], "horizons": [3]},
        results=[],
    )
    db_out = export_model_results_markdown(
        run_id=2,
        status="completed",
        summary={"data_source": "database", "models": ["baseline"], "horizons": [3]},
        results=[],
    )

    assert fake_out.name == "model_results_fake.md"
    assert db_out.name == "model_results_database.md"
    assert fake_out.exists()
    assert db_out.exists()
    assert "fake data" in fake_out.read_text(encoding="utf-8").lower()
    assert "database" in db_out.read_text(encoding="utf-8").lower()
