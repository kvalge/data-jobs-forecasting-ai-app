"""Future PostgreSQL-backed series source (same schemas as FakeFileSource)."""

from __future__ import annotations

import pandas as pd

from src.prediction.data_source import slice_last_periods


class DatabaseSource:
    """Placeholder for aggregating live job_postings / skills into forecast series.

    Switch with PREDICTION_DATA_SOURCE=database once implemented.
    """

    name = "database"

    def load_manifest(self) -> dict:
        return {
            "data_source": "database",
            "status": "not_implemented",
            "note": "Aggregate from job_postings / skills when ready.",
        }

    def load_monthly_roles(self) -> pd.DataFrame:
        raise NotImplementedError(
            "DatabaseSource is not implemented yet. "
            "Set PREDICTION_DATA_SOURCE=fake or implement SQL aggregates here."
        )

    def load_weekly_roles(self) -> pd.DataFrame:
        raise NotImplementedError("DatabaseSource weekly roles not implemented yet.")

    def load_monthly_skills(self) -> pd.DataFrame:
        raise NotImplementedError("DatabaseSource monthly skills not implemented yet.")

    def load_weekly_skills(self) -> pd.DataFrame:
        raise NotImplementedError("DatabaseSource weekly skills not implemented yet.")

    def load_monthly_totals(self) -> pd.DataFrame:
        raise NotImplementedError("DatabaseSource monthly totals not implemented yet.")

    def slice_training_window(self, df: pd.DataFrame, months: int) -> pd.DataFrame:
        return slice_last_periods(df, months)

    def top_roles(self, months: int = 6, k: int = 15) -> list[str]:
        raise NotImplementedError("DatabaseSource top_roles not implemented yet.")

    def top_skills(self, months: int = 6, k: int = 15) -> list[str]:
        raise NotImplementedError("DatabaseSource top_skills not implemented yet.")
