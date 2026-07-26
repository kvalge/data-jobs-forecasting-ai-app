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
            }
        ],
    )
    session.commit()
    assert run_id == 1
    run = repo.get_run(1)
    assert run is not None
    assert run.training_window_months == 12
    results = repo.list_results(1)
    assert len(results) == 1
    assert results[0].target_key == "Data Engineer"
    assert results[0].period_start == date(2026, 10, 1)
    assert session.query(ForecastRunORM).count() == 1
    assert session.query(ForecastResultORM).count() == 1
