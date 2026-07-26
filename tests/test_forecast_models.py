"""Forecast model adapters on a synthetic monthly series."""

import numpy as np
import pandas as pd
import pytest

from src.prediction.models.classical import ArimaForecaster
from src.prediction.models.ml import RandomForestForecaster
from src.prediction.models.registry import get_forecaster


def _sine_series(n: int = 36) -> pd.Series:
    idx = pd.period_range("2023-01", periods=n, freq="M").to_timestamp()
    values = 20 + 5 * np.sin(np.arange(n) / 6) + np.linspace(0, 3, n)
    return pd.Series(values, index=idx)


def test_random_forest_forecast_points():
    series = _sine_series()
    result = RandomForestForecaster().forecast(series, horizon_months=6)
    assert result.error is None
    assert len(result.points) == 6
    assert all(p.value >= 0 for p in result.points)


def test_arima_forecast_points():
    series = _sine_series()
    result = ArimaForecaster().forecast(series, horizon_months=3)
    assert result.error is None
    assert len(result.points) == 3


def test_get_forecaster_unknown():
    with pytest.raises(ValueError):
        get_forecaster("nope")


def test_prophet_forecast_optional():
    series = _sine_series()
    result = get_forecaster("prophet").forecast(series, horizon_months=3)
    # Soft-fail allowed if prophet/cmdstan issues in CI
    if result.error is None:
        assert len(result.points) == 3
