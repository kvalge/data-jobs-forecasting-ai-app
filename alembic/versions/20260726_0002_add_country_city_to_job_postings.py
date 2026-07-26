"""Add country and city columns to job_postings.

Revision ID: 20260726_0002
Revises: 20260726_0001
Create Date: 2026-07-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260726_0002"
down_revision: Union[str, Sequence[str], None] = "20260726_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("job_postings", sa.Column("country", sa.String(), nullable=True))
    op.add_column("job_postings", sa.Column("city", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("job_postings", "city")
    op.drop_column("job_postings", "country")
