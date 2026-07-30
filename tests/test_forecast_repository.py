"""Forecast repository on in-memory SQLite."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.dal.forecast_repository import ForecastRepository
from src.dal.models import Base, ForecastResultORM, ForecastRunORM


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_save_and_list_run(session):
    repo = ForecastRepository(session)
    run_id = repo.save_run(
        data_source="fake",
        training_window_months=12,
        horizons=[3, 6],
        models_requested=["baseline", "rf"],
        status="completed",
        meta={"top_k": 5},
        results=[
            {
                "model_name": "rf",
                "target_type": "role",
                "target_key": "Data Engineer",
                "horizon_months": 3,
                "period_start": "2026-10-01",
                "predicted_value": 12.5,
                "metrics": {"mae": 1.0},
            },
            {
                "model_name": "rf",
                "target_type": "role",
                "target_key": "Data Analyst",
                "horizon_months": 3,
                "period_start": "2026-10-01",
                "predicted_value": 20.0,
                "metrics": None,
            },
            {
                "model_name": "arima",
                "target_type": "role",
                "target_key": "ML Engineer",
                "horizon_months": 3,
                "period_start": "2026-10-01",
                "predicted_value": 5.0,
                "metrics": None,
            },
        ],
    )
    session.commit()
    assert run_id == 1
    run = repo.get_run(1)
    assert run is not None
    assert run.training_window_months == 12
    results = repo.list_results(1)
    assert len(results) == 3
    # Grouped by model name, then highest value first
    assert results[0].model_name == "arima"
    assert results[1].model_name == "rf"
    assert results[1].target_key == "Data Analyst"
    assert results[1].predicted_value == 20.0
    assert results[2].target_key == "Data Engineer"
    assert results[2].period_start == date(2026, 10, 1)
    assert session.query(ForecastRunORM).count() == 1
    assert session.query(ForecastResultORM).count() == 3


def test_save_run_sanitizes_nan_in_meta_and_metrics(session):
    """Postgres JSON rejects NaN; repository must coerce to null before insert."""
    repo = ForecastRepository(session)
    run_id = repo.save_run(
        data_source="database",
        training_window_months=24,
        horizons=[3],
        models_requested=["baseline"],
        status="completed",
        meta={
            "baseline": {
                "roles": [
                    {
                        "key": "AI Security Engineer",
                        "latest": float("nan"),
                        "growth_rate_pct": None,
                        "trend": {
                            "slope": None,
                            "intercept": None,
                            "direction": "unknown",
                            "r2": None,
                        },
                    }
                ]
            }
        },
        results=[
            {
                "model_name": "baseline",
                "target_type": "role",
                "target_key": "AI Security Engineer",
                "horizon_months": 3,
                "period_start": "2026-10-01",
                "predicted_value": float("nan"),
                "metrics": {"mae": float("nan")},
            }
        ],
    )
    session.commit()
    run = repo.get_run(run_id)
    assert run is not None
    assert run.meta["baseline"]["roles"][0]["latest"] is None
    results = repo.list_results(run_id)
    assert len(results) == 1
    assert results[0].predicted_value is None
    assert results[0].metrics["mae"] is None
