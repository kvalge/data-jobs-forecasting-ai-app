"""PostgreSQL-backed series source for forecasting (same schemas as FakeFileSource)."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import func, select

from src.dal.models import JobPostingORM, SkillORM, job_posting_skills
from src.dal.session import session_scope
from src.prediction.data_source import slice_last_periods

_EMPTY_ROLES = pd.DataFrame(
    columns=[
        "period_start",
        "role_title_en",
        "posting_count",
        "avg_salary_min",
        "avg_salary_max",
        "avg_salary",
    ]
)
_EMPTY_SKILLS = pd.DataFrame(
    columns=["period_start", "display_name_en", "posting_count"]
)
_EMPTY_TOTALS = pd.DataFrame(
    columns=[
        "period_start",
        "total_postings",
        "total_role_mentions",
        "total_skill_mentions",
    ]
)


def _period_start(series: pd.Series, freq: str) -> pd.Series:
    return pd.to_datetime(series).dt.to_period(freq).dt.start_time.dt.normalize()


class DatabaseSource:
    """Aggregate live ``job_postings`` / skills into forecast series by ``date_added``."""

    name = "database"

    def __init__(self) -> None:
        self._postings: pd.DataFrame | None = None
        self._skill_links: pd.DataFrame | None = None

    def load_manifest(self) -> dict:
        postings = self._postings_frame()
        return {
            "data_source": "database",
            "status": "ok",
            "n_postings": int(len(postings)),
            "date_min": str(postings["date_added"].min()) if not postings.empty else None,
            "date_max": str(postings["date_added"].max()) if not postings.empty else None,
        }

    def _postings_frame(self) -> pd.DataFrame:
        if self._postings is not None:
            return self._postings
        with session_scope() as session:
            rows = session.execute(
                select(
                    JobPostingORM.id,
                    JobPostingORM.date_added,
                    JobPostingORM.role_title,
                    JobPostingORM.role_title_en,
                    JobPostingORM.salary_min,
                    JobPostingORM.salary_max,
                )
            ).all()
        if not rows:
            self._postings = pd.DataFrame(
                columns=[
                    "posting_id",
                    "date_added",
                    "role_title_en",
                    "salary_min",
                    "salary_max",
                    "avg_salary",
                ]
            )
            return self._postings

        records = []
        for row in rows:
            role_en = (row.role_title_en or row.role_title or "").strip() or "unknown"
            smin = row.salary_min
            smax = row.salary_max
            if smin is not None and smax is not None:
                avg = (float(smin) + float(smax)) / 2.0
            elif smin is not None:
                avg = float(smin)
            elif smax is not None:
                avg = float(smax)
            else:
                avg = None
            records.append(
                {
                    "posting_id": row.id,
                    "date_added": row.date_added,
                    "role_title_en": role_en,
                    "salary_min": float(smin) if smin is not None else None,
                    "salary_max": float(smax) if smax is not None else None,
                    "avg_salary": avg,
                }
            )
        frame = pd.DataFrame.from_records(records)
        frame["date_added"] = pd.to_datetime(frame["date_added"])
        self._postings = frame
        return self._postings

    def _skill_links_frame(self) -> pd.DataFrame:
        if self._skill_links is not None:
            return self._skill_links
        postings = self._postings_frame()
        if postings.empty:
            self._skill_links = pd.DataFrame(
                columns=["posting_id", "date_added", "display_name_en"]
            )
            return self._skill_links

        with session_scope() as session:
            skill_label = func.coalesce(
                SkillORM.display_name_en, SkillORM.display_name, SkillORM.name
            )
            rows = session.execute(
                select(
                    job_posting_skills.c.job_posting_id,
                    JobPostingORM.date_added,
                    skill_label.label("display_name_en"),
                )
                .select_from(job_posting_skills)
                .join(JobPostingORM, JobPostingORM.id == job_posting_skills.c.job_posting_id)
                .join(SkillORM, SkillORM.id == job_posting_skills.c.skill_id)
            ).all()

        if not rows:
            self._skill_links = pd.DataFrame(
                columns=["posting_id", "date_added", "display_name_en"]
            )
            return self._skill_links

        frame = pd.DataFrame.from_records(
            [
                {
                    "posting_id": r.job_posting_id,
                    "date_added": r.date_added,
                    "display_name_en": (r.display_name_en or "").strip() or "unknown",
                }
                for r in rows
            ]
        )
        frame["date_added"] = pd.to_datetime(frame["date_added"])
        self._skill_links = frame
        return self._skill_links

    def _agg_roles(self, freq: str) -> pd.DataFrame:
        frame = self._postings_frame()
        if frame.empty:
            return _EMPTY_ROLES.copy()
        g = frame.copy()
        g["period_start"] = _period_start(g["date_added"], freq)
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
        return agg

    def _agg_skills(self, freq: str) -> pd.DataFrame:
        frame = self._skill_links_frame()
        if frame.empty:
            return _EMPTY_SKILLS.copy()
        g = frame.copy()
        g["period_start"] = _period_start(g["date_added"], freq)
        return (
            g.groupby(["period_start", "display_name_en"], as_index=False)
            .agg(posting_count=("posting_id", "count"))
        )

    def _agg_totals(self, freq: str) -> pd.DataFrame:
        roles = self._agg_roles(freq)
        skills = self._agg_skills(freq)
        postings = self._postings_frame()
        if postings.empty:
            return _EMPTY_TOTALS.copy()
        p = postings.copy()
        p["period_start"] = _period_start(p["date_added"], freq)
        totals_postings = p.groupby("period_start", as_index=False).agg(
            total_postings=("posting_id", "count")
        )
        role_sums = (
            roles.groupby("period_start", as_index=False).agg(
                total_role_mentions=("posting_count", "sum")
            )
            if not roles.empty
            else pd.DataFrame(columns=["period_start", "total_role_mentions"])
        )
        skill_sums = (
            skills.groupby("period_start", as_index=False).agg(
                total_skill_mentions=("posting_count", "sum")
            )
            if not skills.empty
            else pd.DataFrame(columns=["period_start", "total_skill_mentions"])
        )
        totals = (
            totals_postings.merge(role_sums, on="period_start", how="left")
            .merge(skill_sums, on="period_start", how="left")
            .fillna(0)
        )
        for col in ("total_postings", "total_role_mentions", "total_skill_mentions"):
            totals[col] = totals[col].astype(int)
        return totals

    def load_monthly_roles(self) -> pd.DataFrame:
        return self._agg_roles("M")

    def load_weekly_roles(self) -> pd.DataFrame:
        return self._agg_roles("W-MON")

    def load_monthly_skills(self) -> pd.DataFrame:
        return self._agg_skills("M")

    def load_weekly_skills(self) -> pd.DataFrame:
        return self._agg_skills("W-MON")

    def load_monthly_totals(self) -> pd.DataFrame:
        return self._agg_totals("M")

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
