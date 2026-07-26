"""Add role_title_en to job_postings and display_name_en to skills.

Revision ID: 20260726_0003
Revises: 20260726_0002
Create Date: 2026-07-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260726_0003"
down_revision: Union[str, Sequence[str], None] = "20260726_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("job_postings", sa.Column("role_title_en", sa.String(), nullable=True))
    op.add_column("skills", sa.Column("display_name_en", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("skills", "display_name_en")
    op.drop_column("job_postings", "role_title_en")
