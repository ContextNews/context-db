"""add is_key and rank to story_entities

Revision ID: b3d8f1a92c47
Revises: 0a9bf1357f15
Create Date: 2026-05-14 12:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3d8f1a92c47'
down_revision = '0a9bf1357f15'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'story_entities',
        sa.Column('is_key', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )
    op.add_column(
        'story_entities',
        sa.Column('rank', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('story_entities', 'rank')
    op.drop_column('story_entities', 'is_key')
