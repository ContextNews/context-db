"""make_embedding_dimensionless

Revision ID: cfc3bbc58f87
Revises: c1b4a86e3c12
Create Date: 2026-01-11 22:29:47.315094

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfc3bbc58f87'
down_revision = 'c1b4a86e3c12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE articles ALTER COLUMN embedding TYPE vector")


def downgrade() -> None:
    op.execute("ALTER TABLE articles ALTER COLUMN embedding TYPE vector(1536)")
