"""Shared forecast adapter contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
import pandas as pd


@dataclass
class ForecastPoint:
    period_start: str  # YYYY-MM-01
    value: float


@dataclass
class ForecastResult:
    model_name: str
    points: list[ForecastPoint] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Forecaster(Protocol):
    name: str

    def forecast(self, series: pd.Series, horizon_months: int) -> ForecastResult:
        """`series` indexed by month-start Timestamp, values float."""
        ...


def to_month_series(df: pd.DataFrame, value_col: str) -> pd.Series:
    """Build a dense monthly series from period_start + value column."""
    if df.empty:
        return pd.Series(dtype=float)
    frame = df.copy()
    frame["period_start"] = pd.to_datetime(frame["period_start"]).dt.to_period("M").dt.to_timestamp()
    s = frame.groupby("period_start", as_index=True)[value_col].sum().astype(float).sort_index()
    if s.empty:
        return s
    full_idx = pd.period_range(s.index.min(), s.index.max(), freq="M").to_timestamp()
    return s.reindex(full_idx, fill_value=0.0)


def holdout_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    if len(y_true) == 0:
        return {}
    err = y_true - y_pred
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    return {"mae": round(mae, 4), "rmse": round(rmse, 4)}


def future_month_starts(last: pd.Timestamp, horizon: int) -> list[pd.Timestamp]:
    periods = pd.period_range(last.to_period("M") + 1, periods=horizon, freq="M")
    return [p.to_timestamp() for p in periods]


def points_from_values(starts: list[pd.Timestamp], values: list[float]) -> list[ForecastPoint]:
    return [
        ForecastPoint(period_start=ts.strftime("%Y-%m-%d"), value=round(float(v), 4))
        for ts, v in zip(starts, values)
    ]
