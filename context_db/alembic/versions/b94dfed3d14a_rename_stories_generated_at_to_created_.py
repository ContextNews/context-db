"""rename stories generated_at to created_at

Revision ID: b94dfed3d14a
Revises: 75eb282b86d7
Create Date: 2026-02-25 16:27:23.730375

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b94dfed3d14a'
down_revision = '75eb282b86d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("stories", "generated_at", new_column_name="created_at")


def downgrade() -> None:
    op.alter_column("stories", "created_at", new_column_name="generated_at")
