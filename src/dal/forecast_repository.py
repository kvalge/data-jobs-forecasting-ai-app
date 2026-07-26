"""Persist and load forecast runs / results."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.dal.models import ForecastResultORM, ForecastRunORM


class ForecastRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_run(
        self,
        *,
        data_source: str,
        training_window_months: int,
        horizons: list[int],
        models_requested: list[str],
        status: str,
        meta: dict[str, Any] | None,
        results: list[dict[str, Any]],
        notes: str | None = None,
    ) -> int:
        run = ForecastRunORM(
            created_at=datetime.now(),
            data_source=data_source,
            training_window_months=training_window_months,
            horizons=list(horizons),
            models_requested=list(models_requested),
            status=status,
            meta=meta,
            notes=notes,
        )
        self.session.add(run)
        self.session.flush()

        for row in results:
            period = row.get("period_start")
            period_date: date | None
            if period is None or period == "":
                period_date = None
            elif isinstance(period, date):
                period_date = period
            else:
                period_date = date.fromisoformat(str(period)[:10])

            self.session.add(
                ForecastResultORM(
                    run_id=run.id,
                    model_name=row["model_name"],
                    target_type=row["target_type"],
                    target_key=row["target_key"],
                    horizon_months=int(row.get("horizon_months") or 0),
                    period_start=period_date,
                    predicted_value=row.get("predicted_value"),
                    metrics=row.get("metrics"),
                )
            )
        self.session.flush()
        return int(run.id)

    def get_run(self, run_id: int) -> ForecastRunORM | None:
        return self.session.get(ForecastRunORM, run_id)

    def list_recent_runs(self, limit: int = 10) -> list[ForecastRunORM]:
        return (
            self.session.query(ForecastRunORM)
            .order_by(ForecastRunORM.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_results(self, run_id: int, *, limit: int = 500) -> list[ForecastResultORM]:
        return (
            self.session.query(ForecastResultORM)
            .filter(ForecastResultORM.run_id == run_id)
            .order_by(
                ForecastResultORM.model_name,
                ForecastResultORM.target_type,
                ForecastResultORM.target_key,
                ForecastResultORM.horizon_months,
            )
            .limit(limit)
            .all()
        )
