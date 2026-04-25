"""drop_embedded_text_and_raw_json

Revision ID: 31fbc9027819
Revises: 3d34e97c7f70
Create Date: 2026-04-25 13:14:57.796205

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31fbc9027819'
down_revision = '3d34e97c7f70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('article_embeddings', 'embedded_text')
    op.drop_column('tg_posts', 'raw_json')


def downgrade() -> None:
    op.add_column('article_embeddings', sa.Column('embedded_text', sa.Text(), nullable=True))
    op.add_column('tg_posts', sa.Column('raw_json', sa.Text(), nullable=True))
