"""Add forecast_runs and forecast_results tables.

Revision ID: 20260726_0004
Revises: 20260726_0003
Create Date: 2026-07-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260726_0004"
down_revision: Union[str, Sequence[str], None] = "20260726_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "forecast_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("data_source", sa.String(), nullable=False),
        sa.Column("training_window_months", sa.Integer(), nullable=False),
        sa.Column("horizons", sa.JSON(), nullable=False),
        sa.Column("models_requested", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "forecast_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("target_type", sa.String(), nullable=False),
        sa.Column("target_key", sa.String(), nullable=False),
        sa.Column("horizon_months", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("predicted_value", sa.Float(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["forecast_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_forecast_results_run_id", "forecast_results", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_forecast_results_run_id", table_name="forecast_results")
    op.drop_table("forecast_results")
    op.drop_table("forecast_runs")
