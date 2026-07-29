"""Swappable data access for prediction pipelines."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pandas as pd

import src.config as config

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAKE_DIR = PROJECT_ROOT / "data" / "fake"


class DataSource(Protocol):
    """Load role/skill/salary series for forecasting.

    Implementations must return the same column schemas so models stay source-agnostic.
    """

    name: str

    def load_manifest(self) -> dict:
        ...

    def load_monthly_roles(self) -> pd.DataFrame:
        """Columns: period_start, role_title_en, posting_count, avg_salary_min, avg_salary_max, avg_salary."""
        ...

    def load_weekly_roles(self) -> pd.DataFrame:
        ...

    def load_monthly_skills(self) -> pd.DataFrame:
        """Columns: period_start, display_name_en, posting_count."""
        ...

    def load_weekly_skills(self) -> pd.DataFrame:
        ...

    def load_monthly_totals(self) -> pd.DataFrame:
        ...

    def slice_training_window(self, df: pd.DataFrame, months: int) -> pd.DataFrame:
        """Keep the last `months` distinct period_start values."""
        ...

    def top_roles(self, months: int = 6, k: int = 15) -> list[str]:
        ...

    def top_skills(self, months: int = 6, k: int = 15) -> list[str]:
        ...


def _ensure_period_start(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["period_start"] = pd.to_datetime(out["period_start"]).dt.normalize()
    return out


def slice_last_periods(df: pd.DataFrame, months: int) -> pd.DataFrame:
    """Keep rows belonging to the last `months` distinct period_start values."""
    if df.empty:
        return df.copy()
    frame = _ensure_period_start(df)
    periods = sorted(frame["period_start"].unique())
    if months <= 0 or len(periods) <= months:
        return frame.sort_values("period_start").reset_index(drop=True)
    keep = set(periods[-months:])
    return (
        frame[frame["period_start"].isin(keep)]
        .sort_values("period_start")
        .reset_index(drop=True)
    )


def get_data_source(kind: str | None = None, *, fake_dir: Path | None = None) -> DataSource:
    """Factory: PREDICTION_DATA_SOURCE env or explicit kind (`fake`|`database`)."""
    from src.prediction.fake_file_source import FakeFileSource

    resolved = (kind or getattr(config, "PREDICTION_DATA_SOURCE", None) or "fake").strip().lower()
    if resolved in ("fake", "file", "fake_file"):
        return FakeFileSource(fake_dir or DEFAULT_FAKE_DIR)
    if resolved in ("database", "db"):
        from src.prediction.database_source import DatabaseSource

        return DatabaseSource()
    raise ValueError(
        f"Unknown PREDICTION_DATA_SOURCE={resolved!r}. Use 'fake' or 'database'."
    )
