"""make article_embeddings embedding not null

Revision ID: 328bf871adf3
Revises: fb0c2a0f5b87
Create Date: 2026-02-25 16:46:03.437498

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '328bf871adf3'
down_revision = 'fb0c2a0f5b87'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("article_embeddings", "embedding", nullable=False)


def downgrade() -> None:
    op.alter_column("article_embeddings", "embedding", nullable=True)
