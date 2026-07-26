"""Baseline schema: job_postings, skills, job_posting_skills.

Revision ID: 20260726_0001
Revises:
Create Date: 2026-07-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260726_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

worktype_enum = sa.Enum(
    "onsite",
    "hybrid",
    "remote",
    "unknown",
    name="worktype",
)


def upgrade() -> None:
    worktype_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "job_postings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_name", sa.String(), nullable=True),
        sa.Column("role_title", sa.String(), nullable=False),
        sa.Column("responsibilities", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("application_deadline", sa.Date(), nullable=True),
        sa.Column("salary_min", sa.Float(), nullable=True),
        sa.Column("salary_max", sa.Float(), nullable=True),
        sa.Column("salary_currency", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column(
            "work_type",
            worktype_enum,
            nullable=False,
            server_default="unknown",
        ),
        sa.Column(
            "has_nondiscrimination_disclaimer",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("date_added", sa.Date(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_hash"),
    )

    op.create_table(
        "job_posting_skills",
        sa.Column("job_posting_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["job_posting_id"], ["job_postings.id"]),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("job_posting_id", "skill_id"),
    )


def downgrade() -> None:
    op.drop_table("job_posting_skills")
    op.drop_table("job_postings")
    op.drop_table("skills")
    worktype_enum.drop(op.get_bind(), checkfirst=True)
