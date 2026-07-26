"""Baseline trend helpers."""

import pandas as pd

from src.prediction.baseline.analysis import (
    growth_rate_pct,
    linear_trend,
    market_share,
    moving_averages,
    run_baseline_analysis,
)


def test_moving_averages_and_growth():
    s = pd.Series([10.0, 12.0, 14.0, 16.0, 18.0])
    mas = moving_averages(s)
    assert mas["ma_3"] == 16.0
    assert growth_rate_pct(s) == round(100 * (18 - 16) / 16, 2)


def test_linear_trend_up():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    trend = linear_trend(s)
    assert trend["direction"] == "up"
    assert trend["slope"] > 0


def test_market_share_and_baseline_report():
    roles = pd.DataFrame(
        {
            "period_start": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-01-01"]),
            "role_title_en": ["A", "A", "B"],
            "posting_count": [10, 12, 5],
            "avg_salary": [1000, 1100, 900],
            "avg_salary_min": [900, 1000, 800],
            "avg_salary_max": [1100, 1200, 1000],
        }
    )
    skills = pd.DataFrame(
        {
            "period_start": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "display_name_en": ["Python", "Python"],
            "posting_count": [3, 4],
        }
    )
    share = market_share(roles, "role_title_en")
    assert share.iloc[0]["role_title_en"] == "A"
    report = run_baseline_analysis(
        monthly_roles=roles,
        weekly_roles=roles,
        monthly_skills=skills,
        weekly_skills=skills,
        role_keys=["A", "B"],
        skill_keys=["Python"],
    )
    assert report["model_name"] == "baseline"
    assert len(report["roles_monthly"]) == 2
