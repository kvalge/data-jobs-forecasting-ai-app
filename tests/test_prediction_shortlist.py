"""Unit tests for prediction shortlist helpers (no model fitting)."""

import pandas as pd

from src.bll.prediction_shortlist import filter_rows_by_horizons, rank_top_keys
from src.prediction.models.registry import DEFAULT_MODELS
from src.bll.prediction_service import _normalize_models


def test_rank_top_keys_orders_by_sum():
    df = pd.DataFrame(
        {
            "role_title_en": ["A", "B", "A", "C", "B", "A"],
            "posting_count": [1, 1, 1, 5, 1, 1],
        }
    )
    assert rank_top_keys(df, "role_title_en", "posting_count", 2) == ["C", "A"]


def test_filter_rows_by_horizons_keeps_baseline_and_selected():
    rows = [
        {"model_name": "baseline", "horizon_months": 0},
        {"model_name": "rf", "horizon_months": 3},
        {"model_name": "rf", "horizon_months": 6},
        {"model_name": "rf", "horizon_months": 12},
    ]
    out = filter_rows_by_horizons(rows, [3, 12])
    assert [r["horizon_months"] for r in out] == [0, 3, 12]


def test_normalize_models_defaults_to_demo_shortlist():
    assert _normalize_models(None) == list(DEFAULT_MODELS)
    assert _normalize_models([]) == list(DEFAULT_MODELS)
