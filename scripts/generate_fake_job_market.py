"""Generate reproducible fake job-market data for prediction pipelines.

Usage (from project root):
  python scripts/generate_fake_job_market.py
  python scripts/generate_fake_job_market.py --n-postings 200 --out-dir data/fake
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_SEED = 42
DEFAULT_N_POSTINGS = 10_000
DEFAULT_MONTHS = 36
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = PROJECT_ROOT / "data" / "fake"

ROLES = [
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "ML Engineer",
    "Analytics Engineer",
    "BI Developer",
    "AI Engineer",
    "MLOps Engineer",
    "Research Scientist",
    "Product Analyst",
    "Backend Engineer",
    "Platform Engineer",
    "Data Platform Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
]

SKILLS = [
    "Python",
    "SQL",
    "Spark",
    "Airflow",
    "dbt",
    "Tableau",
    "Power BI",
    "AWS",
    "GCP",
    "Azure",
    "Kubernetes",
    "Docker",
    "TensorFlow",
    "PyTorch",
    "scikit-learn",
    "Pandas",
    "Kafka",
    "PostgreSQL",
    "Snowflake",
    "Databricks",
    "LLM",
    "LangChain",
    "MLOps",
    "CI/CD",
    "Terraform",
    "Java",
    "Scala",
    "R",
    "Looker",
    "Excel",
]

# Relative popularity weights for roles (skewed market)
ROLE_WEIGHTS = np.array(
    [12, 11, 10, 9, 8, 7, 7, 6, 5, 5, 4, 4, 4, 3, 3], dtype=float
)
ROLE_WEIGHTS = ROLE_WEIGHTS / ROLE_WEIGHTS.sum()

SKILL_WEIGHTS = np.linspace(1.5, 0.4, len(SKILLS))
SKILL_WEIGHTS = SKILL_WEIGHTS / SKILL_WEIGHTS.sum()

# Role base monthly salary midpoints (EUR-ish)
ROLE_SALARY_BASE = {
    "Data Engineer": 4200,
    "Data Analyst": 3400,
    "Data Scientist": 4500,
    "ML Engineer": 4800,
    "Analytics Engineer": 4000,
    "BI Developer": 3600,
    "AI Engineer": 5000,
    "MLOps Engineer": 4700,
    "Research Scientist": 4600,
    "Product Analyst": 3500,
    "Backend Engineer": 4300,
    "Platform Engineer": 4400,
    "Data Platform Engineer": 4600,
    "NLP Engineer": 4900,
    "Computer Vision Engineer": 4900,
}


def _month_starts(end: date, months: int) -> list[date]:
    """Return month-start dates covering `months` calendar months ending at end's month."""
    y, m = end.year, end.month
    starts: list[date] = []
    for _ in range(months):
        starts.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    starts.reverse()
    return starts


def _daily_targets(
    rng: np.random.Generator,
    start: date,
    end: date,
    n_postings: int,
) -> dict[date, int]:
    """Allocate n_postings across days with weekday/seasonality/noise variation."""
    days: list[date] = []
    d = start
    while d <= end:
        days.append(d)
        d += timedelta(days=1)

    weights = []
    for day in days:
        # Weekday boost; weekend quieter
        wd = 1.35 if day.weekday() < 5 else 0.45
        # Mild annual seasonality (peak spring / autumn)
        season = 1.0 + 0.18 * math.sin(2 * math.pi * (day.timetuple().tm_yday / 365.25))
        noise = float(rng.lognormal(mean=0.0, sigma=0.25))
        weights.append(max(0.05, wd * season * noise))

    w = np.array(weights, dtype=float)
    w = w / w.sum()
    counts = rng.multinomial(n_postings, w)
    return {day: int(c) for day, c in zip(days, counts) if c > 0}


def generate_fake_job_market(
    *,
    out_dir: Path,
    n_postings: int = DEFAULT_N_POSTINGS,
    months: int = DEFAULT_MONTHS,
    seed: int = DEFAULT_SEED,
    end_date: date | None = None,
) -> dict:
    """Generate posting + skill + aggregation files under out_dir. Returns manifest dict."""
    rng = np.random.default_rng(seed)
    end_date = end_date or date(2026, 7, 26)
    month_starts = _month_starts(end_date, months)
    start_date = month_starts[0]

    day_counts = _daily_targets(rng, start_date, end_date, n_postings)

    postings: list[dict] = []
    posting_skills: list[dict] = []
    posting_id = 1

    # Slow salary drift over months
    month_index = {ms: i for i, ms in enumerate(month_starts)}

    for day, count in sorted(day_counts.items()):
        month_key = date(day.year, day.month, 1)
        drift = 1.0 + 0.004 * month_index.get(month_key, 0)

        for _ in range(count):
            role = str(rng.choice(ROLES, p=ROLE_WEIGHTS))
            base = ROLE_SALARY_BASE[role] * drift
            # Role popularity also drifts slightly
            spread = 0.12
            mid = base * float(rng.normal(1.0, 0.08))
            salary_min = max(1500.0, mid * (1.0 - spread))
            salary_max = mid * (1.0 + spread)
            avg_salary = (salary_min + salary_max) / 2.0

            postings.append(
                {
                    "posting_id": posting_id,
                    "posting_date": day.isoformat(),
                    "role_title_en": role,
                    "salary_min": round(salary_min, 2),
                    "salary_max": round(salary_max, 2),
                    "avg_salary": round(avg_salary, 2),
                }
            )

            n_skills = int(rng.integers(8, 13))
            chosen = rng.choice(SKILLS, size=n_skills, replace=False, p=SKILL_WEIGHTS)
            for skill in chosen:
                posting_skills.append(
                    {
                        "posting_id": posting_id,
                        "display_name_en": str(skill),
                    }
                )
            posting_id += 1

    postings_df = pd.DataFrame(postings)
    skills_df = pd.DataFrame(posting_skills)
    postings_df["posting_date"] = pd.to_datetime(postings_df["posting_date"])

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    postings_df.to_csv(out_dir / "postings.csv", index=False)
    skills_df.to_csv(out_dir / "posting_skills.csv", index=False)

    # --- Aggregations ---
    def _agg_roles(frame: pd.DataFrame, freq: str, label: str) -> pd.DataFrame:
        g = frame.copy()
        g["period_start"] = g["posting_date"].dt.to_period(freq).dt.start_time.dt.date
        agg = (
            g.groupby(["period_start", "role_title_en"], as_index=False)
            .agg(
                posting_count=("posting_id", "count"),
                avg_salary_min=("salary_min", "mean"),
                avg_salary_max=("salary_max", "mean"),
                avg_salary=("avg_salary", "mean"),
            )
        )
        for col in ("avg_salary_min", "avg_salary_max", "avg_salary"):
            agg[col] = agg[col].round(2)
        agg.to_csv(out_dir / f"agg_{label}_roles.csv", index=False)
        return agg

    def _agg_skills(frame: pd.DataFrame, skills: pd.DataFrame, freq: str, label: str) -> pd.DataFrame:
        merged = skills.merge(frame[["posting_id", "posting_date"]], on="posting_id", how="inner")
        merged["period_start"] = merged["posting_date"].dt.to_period(freq).dt.start_time.dt.date
        agg = (
            merged.groupby(["period_start", "display_name_en"], as_index=False)
            .agg(posting_count=("posting_id", "count"))
        )
        agg.to_csv(out_dir / f"agg_{label}_skills.csv", index=False)
        return agg

    def _agg_totals(
        roles_agg: pd.DataFrame,
        skills_agg: pd.DataFrame,
        postings: pd.DataFrame,
        freq: str,
        label: str,
    ) -> pd.DataFrame:
        p = postings.copy()
        p["period_start"] = p["posting_date"].dt.to_period(freq).dt.start_time.dt.date
        totals_postings = p.groupby("period_start", as_index=False).agg(
            total_postings=("posting_id", "count")
        )
        role_sums = roles_agg.groupby("period_start", as_index=False).agg(
            total_role_mentions=("posting_count", "sum")
        )
        skill_sums = skills_agg.groupby("period_start", as_index=False).agg(
            total_skill_mentions=("posting_count", "sum")
        )
        totals = (
            totals_postings.merge(role_sums, on="period_start", how="left")
            .merge(skill_sums, on="period_start", how="left")
            .fillna(0)
        )
        for col in ("total_postings", "total_role_mentions", "total_skill_mentions"):
            totals[col] = totals[col].astype(int)
        totals.to_csv(out_dir / f"agg_{label}_totals.csv", index=False)
        return totals

    daily_roles = _agg_roles(postings_df, "D", "daily")
    weekly_roles = _agg_roles(postings_df, "W-MON", "weekly")
    monthly_roles = _agg_roles(postings_df, "M", "monthly")

    daily_skills = _agg_skills(postings_df, skills_df, "D", "daily")
    weekly_skills = _agg_skills(postings_df, skills_df, "W-MON", "weekly")
    monthly_skills = _agg_skills(postings_df, skills_df, "M", "monthly")

    _agg_totals(daily_roles, daily_skills, postings_df, "D", "daily")
    _agg_totals(weekly_roles, weekly_skills, postings_df, "W-MON", "weekly")
    _agg_totals(monthly_roles, monthly_skills, postings_df, "M", "monthly")

    manifest = {
        "seed": seed,
        "n_postings": int(len(postings_df)),
        "n_skill_links": int(len(skills_df)),
        "months": months,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "files": sorted(p.name for p in out_dir.glob("*.csv")) + ["manifest.json"],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fake job market datasets.")
    parser.add_argument("--n-postings", type=int, default=DEFAULT_N_POSTINGS)
    parser.add_argument("--months", type=int, default=DEFAULT_MONTHS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--end-date", type=str, default="2026-07-26")
    args = parser.parse_args()
    end = date.fromisoformat(args.end_date)
    manifest = generate_fake_job_market(
        out_dir=args.out_dir,
        n_postings=args.n_postings,
        months=args.months,
        seed=args.seed,
        end_date=end,
    )
    print(f"Wrote fake data to {args.out_dir}")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
