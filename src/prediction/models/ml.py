"""scikit-learn lag-feature forecasters."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor

from src.prediction.models.base import (
    ForecastResult,
    future_month_starts,
    holdout_metrics,
    points_from_values,
)


def _lag_matrix(values: np.ndarray, lags: int = 6) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for i in range(lags, len(values)):
        xs.append(values[i - lags : i])
        ys.append(values[i])
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)


def _ml_forecast(
    series: pd.Series,
    horizon_months: int,
    *,
    name: str,
    estimator,
) -> ForecastResult:
    lags = 6
    if len(series) < lags + 4:
        return ForecastResult(
            model_name=name,
            error=f"Need at least {lags + 4} months of history for {name}.",
        )
    try:
        y = series.astype(float).values
        hold = min(3, max(1, len(y) // 5))
        X, target = _lag_matrix(y, lags=lags)
        if len(target) <= hold + 2:
            train_X, train_y = X, target
            metrics: dict = {}
        else:
            train_X, train_y = X[:-hold], target[:-hold]
            test_X, test_y = X[-hold:], target[-hold:]
            estimator.fit(train_X, train_y)
            pred_h = estimator.predict(test_X)
            metrics = holdout_metrics(test_y, pred_h)

        estimator.fit(X, target)
        history = list(y[-lags:])
        preds: list[float] = []
        for _ in range(horizon_months):
            x = np.asarray(history[-lags:], dtype=float).reshape(1, -1)
            p = float(estimator.predict(x)[0])
            p = max(0.0, p)
            preds.append(p)
            history.append(p)

        starts = future_month_starts(series.index.max(), horizon_months)
        return ForecastResult(
            model_name=name,
            points=points_from_values(starts, preds),
            metrics=metrics,
        )
    except Exception as e:  # noqa: BLE001
        return ForecastResult(model_name=name, error=str(e))


class RandomForestForecaster:
    name = "rf"

    def forecast(self, series: pd.Series, horizon_months: int) -> ForecastResult:
        est = RandomForestRegressor(
            n_estimators=80,
            max_depth=6,
            random_state=42,
            n_jobs=1,
        )
        return _ml_forecast(series, horizon_months, name=self.name, estimator=est)


class HistGradientBoostingForecaster:
    name = "hgb"

    def forecast(self, series: pd.Series, horizon_months: int) -> ForecastResult:
        est = HistGradientBoostingRegressor(
            max_depth=4,
            learning_rate=0.08,
            max_iter=80,
            random_state=42,
        )
        return _ml_forecast(series, horizon_months, name=self.name, estimator=est)
