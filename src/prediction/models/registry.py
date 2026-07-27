"""Model registry and factory."""

from __future__ import annotations

from src.prediction.models.classical import ArimaForecaster, ProphetForecaster, SarimaForecaster
from src.prediction.models.ml import HistGradientBoostingForecaster, RandomForestForecaster

MODEL_KEYS = ("prophet", "sarima", "arima", "rf", "hgb")
ALL_RUNNABLE = ("baseline",) + MODEL_KEYS
# Cheaper demo default — opt in to ALL_RUNNABLE via UI checkboxes or CLI "all".
DEFAULT_MODELS = ("baseline", "prophet", "arima")


def get_forecaster(key: str):
    mapping = {
        "prophet": ProphetForecaster,
        "sarima": SarimaForecaster,
        "arima": ArimaForecaster,
        "rf": RandomForestForecaster,
        "hgb": HistGradientBoostingForecaster,
    }
    if key not in mapping:
        raise ValueError(f"Unknown model {key!r}. Choose from {MODEL_KEYS}.")
    return mapping[key]()
