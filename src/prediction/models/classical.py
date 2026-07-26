"""Prophet, ARIMA, and SARIMA forecasters."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from src.prediction.models.base import (
    ForecastResult,
    future_month_starts,
    holdout_metrics,
    points_from_values,
)


class ProphetForecaster:
    name = "prophet"

    def forecast(self, series: pd.Series, horizon_months: int) -> ForecastResult:
        if len(series) < 6:
            return ForecastResult(
                model_name=self.name,
                error="Need at least 6 months of history for Prophet.",
            )
        try:
            from prophet import Prophet
        except ImportError as e:
            return ForecastResult(model_name=self.name, error=f"prophet not installed: {e}")

        try:
            hold = min(3, max(1, len(series) // 5))
            train = series.iloc[:-hold] if len(series) > hold + 4 else series
            df = pd.DataFrame({"ds": train.index, "y": train.values})
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                )
                model.fit(df)
                # Holdout metrics
                metrics: dict = {}
                if len(series) > hold + 4:
                    future_h = model.make_future_dataframe(periods=hold, freq="MS")
                    pred_h = model.predict(future_h).tail(hold)["yhat"].values
                    metrics = holdout_metrics(series.iloc[-hold:].values.astype(float), pred_h)

                # Refit on full series for forward forecast
                full = pd.DataFrame({"ds": series.index, "y": series.values})
                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                )
                model.fit(full)
                future = model.make_future_dataframe(periods=horizon_months, freq="MS")
                forecast = model.predict(future).tail(horizon_months)
                values = [max(0.0, float(v)) for v in forecast["yhat"].tolist()]
                starts = future_month_starts(series.index.max(), horizon_months)
                return ForecastResult(
                    model_name=self.name,
                    points=points_from_values(starts, values),
                    metrics=metrics,
                )
        except Exception as e:  # noqa: BLE001 — soft-fail per model
            return ForecastResult(model_name=self.name, error=str(e))


class ArimaForecaster:
    name = "arima"

    def forecast(self, series: pd.Series, horizon_months: int) -> ForecastResult:
        return _statsmodels_forecast(
            series,
            horizon_months,
            name=self.name,
            order=(1, 1, 1),
            seasonal_order=None,
        )


class SarimaForecaster:
    name = "sarima"

    def forecast(self, series: pd.Series, horizon_months: int) -> ForecastResult:
        return _statsmodels_forecast(
            series,
            horizon_months,
            name=self.name,
            order=(1, 1, 1),
            seasonal_order=(1, 0, 0, 12),
        )


def _statsmodels_forecast(
    series: pd.Series,
    horizon_months: int,
    *,
    name: str,
    order: tuple[int, int, int],
    seasonal_order: tuple[int, int, int, int] | None,
) -> ForecastResult:
    if len(series) < 8:
        return ForecastResult(
            model_name=name,
            error="Need at least 8 months of history for ARIMA/SARIMA.",
        )
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except ImportError as e:
        return ForecastResult(model_name=name, error=f"statsmodels not installed: {e}")

    try:
        y = series.astype(float)
        hold = min(3, max(1, len(y) // 5))
        train = y.iloc[:-hold] if len(y) > hold + 6 else y
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kwargs = {"order": order, "enforce_stationarity": False, "enforce_invertibility": False}
            if seasonal_order is not None:
                kwargs["seasonal_order"] = seasonal_order
            model = SARIMAX(train, **kwargs)
            fitted = model.fit(disp=False)
            metrics: dict = {}
            if len(y) > hold + 6:
                pred_h = fitted.forecast(steps=hold).values
                metrics = holdout_metrics(y.iloc[-hold:].values, np.asarray(pred_h, dtype=float))

            full = SARIMAX(y, **kwargs).fit(disp=False)
            pred = full.forecast(steps=horizon_months)
            values = [max(0.0, float(v)) for v in np.asarray(pred, dtype=float)]
            starts = future_month_starts(series.index.max(), horizon_months)
            return ForecastResult(
                model_name=name,
                points=points_from_values(starts, values),
                metrics=metrics,
            )
    except Exception as e:  # noqa: BLE001
        return ForecastResult(model_name=name, error=str(e))
