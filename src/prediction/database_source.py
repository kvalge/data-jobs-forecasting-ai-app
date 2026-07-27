"""Future PostgreSQL-backed series source (not wired; fail-closed in config).

QUARANTINED: Do not import this from ``get_data_source`` until SQL aggregates
exist. ``PREDICTION_DATA_SOURCE=database`` is rejected at startup.
"""

from __future__ import annotations

import pandas as pd

from src.prediction.data_source import slice_last_periods


class DatabaseSource:
    """Placeholder for aggregating live job_postings / skills into forecast series.

    Not implemented. Kept for documentation of the intended future shape only.
    """

    name = "database"

    def __init__(self) -> None:
        raise NotImplementedError(
            "DatabaseSource is quarantined / not implemented. "
            "Set PREDICTION_DATA_SOURCE=fake (default)."
        )

    def load_manifest(self) -> dict:
        return {
            "data_source": "database",
            "status": "not_implemented",
            "note": "Aggregate from job_postings / skills when ready.",
        }

    def load_monthly_roles(self) -> pd.DataFrame:
        raise NotImplementedError("DatabaseSource is not implemented yet.")

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
