"""Load prediction series from data/fake CSV aggregates."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.prediction.data_source import DEFAULT_FAKE_DIR, _ensure_period_start, slice_last_periods


class FakeFileSource:
    name = "fake"

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir or DEFAULT_FAKE_DIR)

    def _read(self, filename: str) -> pd.DataFrame:
        path = self.data_dir / filename
        if not path.is_file():
            raise FileNotFoundError(
                f"Fake data file missing: {path}. "
                "Run: python scripts/generate_fake_job_market.py"
            )
        return _ensure_period_start(pd.read_csv(path))

    def load_manifest(self) -> dict:
        path = self.data_dir / "manifest.json"
        if not path.is_file():
            return {"data_dir": str(self.data_dir), "warning": "manifest.json missing"}
        return json.loads(path.read_text(encoding="utf-8"))

    def load_monthly_roles(self) -> pd.DataFrame:
        return self._read("agg_monthly_roles.csv")

    def load_weekly_roles(self) -> pd.DataFrame:
        return self._read("agg_weekly_roles.csv")

    def load_monthly_skills(self) -> pd.DataFrame:
        return self._read("agg_monthly_skills.csv")

    def load_weekly_skills(self) -> pd.DataFrame:
        return self._read("agg_weekly_skills.csv")

    def load_monthly_totals(self) -> pd.DataFrame:
        return self._read("agg_monthly_totals.csv")

    def slice_training_window(self, df: pd.DataFrame, months: int) -> pd.DataFrame:
        return slice_last_periods(df, months)

    def top_roles(self, months: int = 6, k: int = 15) -> list[str]:
        roles = self.slice_training_window(self.load_monthly_roles(), months)
        if roles.empty:
            return []
        ranked = (
            roles.groupby("role_title_en", as_index=False)["posting_count"]
            .sum()
            .sort_values("posting_count", ascending=False)
        )
        return ranked["role_title_en"].head(k).tolist()

    def top_skills(self, months: int = 6, k: int = 15) -> list[str]:
        skills = self.slice_training_window(self.load_monthly_skills(), months)
        if skills.empty:
            return []
        ranked = (
            skills.groupby("display_name_en", as_index=False)["posting_count"]
            .sum()
            .sort_values("posting_count", ascending=False)
        )
        return ranked["display_name_en"].head(k).tolist()
