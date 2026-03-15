"""add story_indicators table

Revision ID: a3f1c9d82e05
Revises: 1890af575497
Create Date: 2026-03-15 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f1c9d82e05'
down_revision = '1890af575497'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('story_indicators',
    sa.Column('story_id', sa.String(), nullable=False),
    sa.Column('indicator_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['indicator_id'], ['ts_indicators.id'], ),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ),
    sa.PrimaryKeyConstraint('story_id', 'indicator_id')
    )


def downgrade() -> None:
    op.drop_table('story_indicators')
