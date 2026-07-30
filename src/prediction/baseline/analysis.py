"""Historical baseline analysis: MA, growth, market share, linear trend."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def _finite_or_none(value: Any) -> float | None:
    """Convert to float, mapping NaN/Inf/missing to None (JSON/Postgres-safe)."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def _series_for_key(
    df: pd.DataFrame,
    key_col: str,
    key: str,
    value_col: str = "posting_count",
) -> pd.Series:
    sub = df[df[key_col] == key].sort_values("period_start")
    if sub.empty:
        return pd.Series(dtype=float)
    return pd.Series(
        sub[value_col].astype(float).values,
        index=pd.to_datetime(sub["period_start"]),
        name=key,
    )


def moving_averages(series: pd.Series, windows: tuple[int, ...] = (3, 6, 12)) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for w in windows:
        if len(series) >= w:
            out[f"ma_{w}"] = _finite_or_none(series.tail(w).mean())
        else:
            out[f"ma_{w}"] = None
    return out


def growth_rate_pct(series: pd.Series, lag: int = 1) -> float | None:
    if len(series) <= lag:
        return None
    prev = _finite_or_none(series.iloc[-(lag + 1)])
    curr = _finite_or_none(series.iloc[-1])
    if prev is None or curr is None or prev == 0:
        return None
    return round(100.0 * (curr - prev) / prev, 2)


def market_share(df: pd.DataFrame, key_col: str, value_col: str = "posting_count") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[key_col, value_col, "share_pct"])
    totals = df.groupby(key_col, as_index=False)[value_col].sum()
    grand = float(totals[value_col].sum()) or 1.0
    totals["share_pct"] = (totals[value_col] / grand * 100.0).round(2)
    return totals.sort_values(value_col, ascending=False).reset_index(drop=True)


def linear_trend(series: pd.Series) -> dict[str, Any]:
    if len(series) < 2:
        return {"slope": None, "intercept": None, "direction": "unknown", "r2": None}
    y = series.astype(float).values
    if np.any(~np.isfinite(y)):
        y = y[np.isfinite(y)]
        if len(y) < 2:
            return {"slope": None, "intercept": None, "direction": "unknown", "r2": None}
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    y_hat = slope * x + intercept
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2)) or 1.0
    r2 = 1.0 - ss_res / ss_tot
    if slope > 0.05:
        direction = "up"
    elif slope < -0.05:
        direction = "down"
    else:
        direction = "flat"
    return {
        "slope": _finite_or_none(round(float(slope), 4)),
        "intercept": _finite_or_none(round(float(intercept), 4)),
        "direction": direction,
        "r2": _finite_or_none(round(float(r2), 4)),
    }


def analyze_entity(
    df: pd.DataFrame,
    key_col: str,
    key: str,
    value_col: str = "posting_count",
) -> dict[str, Any]:
    series = _series_for_key(df, key_col, key, value_col)
    latest = _finite_or_none(series.iloc[-1]) if len(series) else None
    return {
        "key": key,
        "latest": latest,
        "n_periods": int(len(series)),
        **moving_averages(series),
        "growth_rate_pct": growth_rate_pct(series),
        "trend": linear_trend(series),
    }


def run_baseline_analysis(
    *,
    monthly_roles: pd.DataFrame,
    weekly_roles: pd.DataFrame,
    monthly_skills: pd.DataFrame,
    weekly_skills: pd.DataFrame,
    role_keys: list[str],
    skill_keys: list[str],
) -> dict[str, Any]:
    """Build structured baseline report for selected roles/skills."""
    role_share = market_share(monthly_roles, "role_title_en")
    skill_share = market_share(monthly_skills, "display_name_en")

    roles_monthly = [analyze_entity(monthly_roles, "role_title_en", k) for k in role_keys]
    roles_weekly = [analyze_entity(weekly_roles, "role_title_en", k) for k in role_keys]
    skills_monthly = [analyze_entity(monthly_skills, "display_name_en", k) for k in skill_keys]
    skills_weekly = [analyze_entity(weekly_skills, "display_name_en", k) for k in skill_keys]

    salary_baseline = []
    for role in role_keys:
        salary_baseline.append(
            analyze_entity(monthly_roles, "role_title_en", role, value_col="avg_salary")
        )

    return {
        "model_name": "baseline",
        "role_market_share": role_share.head(20).to_dict(orient="records"),
        "skill_market_share": skill_share.head(20).to_dict(orient="records"),
        "roles_monthly": roles_monthly,
        "roles_weekly": roles_weekly,
        "skills_monthly": skills_monthly,
        "skills_weekly": skills_weekly,
        "salary_monthly": salary_baseline,
    }
