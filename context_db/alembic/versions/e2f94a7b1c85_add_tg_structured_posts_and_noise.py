"""add tg_structured_posts and tg_post_noise tables

Revision ID: e2f94a7b1c85
Revises: 31fbc9027819
Create Date: 2026-04-25 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = 'e2f94a7b1c85'
down_revision = '31fbc9027819'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tg_structured_posts',
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('tg_posts.id'), primary_key=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('location_name', sa.String(), nullable=True),
        sa.Column('label', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('story_id', sa.String(), sa.ForeignKey('stories.id'), nullable=True),
    )
    op.create_table(
        'tg_post_noise',
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('tg_posts.id'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('tg_post_noise')
    op.drop_table('tg_structured_posts')
