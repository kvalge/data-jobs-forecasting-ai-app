# prediction_shortlist.py
"""Rank entities and build monthly series for prediction runs."""

from __future__ import annotations

import pandas as pd

from src.prediction.models.base import to_month_series


def rank_top_keys(
    monthly: pd.DataFrame,
    key_col: str,
    value_col: str,
    top_k: int,
) -> list[str]:
    """Return top_k keys by summed value_col (descending)."""
    if monthly.empty or top_k < 1:
        return []
    ranked = (
        monthly.groupby(key_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
    )
    return ranked[key_col].head(top_k).tolist()


def entity_series(
    monthly: pd.DataFrame,
    key_col: str,
    key: str,
    value_col: str,
) -> pd.Series:
    sub = monthly[monthly[key_col] == key][["period_start", value_col]]
    return to_month_series(sub.rename(columns={value_col: "value"}), "value")


def filter_rows_by_horizons(
    result_rows: list[dict],
    horizon_list: list[int],
    *,
    baseline_model: str = "baseline",
) -> list[dict]:
    """Keep baseline rows (horizon 0) and forecast rows whose horizon is selected."""
    filtered: list[dict] = []
    for row in result_rows:
        if row["model_name"] == baseline_model:
            filtered.append(row)
        elif row["horizon_months"] in horizon_list:
            filtered.append(row)
    return filtered
