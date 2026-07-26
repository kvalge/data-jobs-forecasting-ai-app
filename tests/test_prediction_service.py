"""Orchestration with mini fake data; persistence mocked."""

import importlib.util
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

from src.bll import prediction_service
from src.prediction.fake_file_source import FakeFileSource


def _gen(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "generate_fake_job_market.py"
    spec = importlib.util.spec_from_file_location("generate_fake_job_market", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    mod.generate_fake_job_market(
        out_dir=tmp_path,
        n_postings=180,
        months=18,
        seed=3,
        end_date=date(2026, 7, 26),
    )


def test_run_prediction_baseline_and_rf_without_db(tmp_path, monkeypatch):
    _gen(tmp_path)
    source = FakeFileSource(tmp_path)

    class FakeScope:
        def __enter__(self):
            return MagicMock()

        def __exit__(self, *args):
            return False

    repo = MagicMock()
    repo.save_run.return_value = 99
    monkeypatch.setattr(prediction_service, "session_scope", lambda: FakeScope())
    monkeypatch.setattr(prediction_service, "ForecastRepository", lambda session: repo)

    outcome = prediction_service.run_prediction(
        training_window_months=12,
        horizons=[3],
        models=["baseline", "rf"],
        top_k=3,
        persist=True,
        source=source,
    )
    assert outcome.run_id == 99
    assert outcome.status in ("completed", "completed_with_errors")
    assert outcome.summary["n_results"] > 0
    repo.save_run.assert_called_once()
