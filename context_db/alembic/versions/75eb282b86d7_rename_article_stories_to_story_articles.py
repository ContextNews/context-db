"""rename article_stories to story_articles

Revision ID: 75eb282b86d7
Revises: c6855603d840
Create Date: 2026-02-25 16:27:02.657603

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75eb282b86d7'
down_revision = 'c6855603d840'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("article_stories", "story_articles")


def downgrade() -> None:
    op.rename_table("story_articles", "article_stories")
