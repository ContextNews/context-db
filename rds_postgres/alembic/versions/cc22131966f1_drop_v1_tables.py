"""drop v1 tables

Revision ID: cc22131966f1
Revises: e7b62efa5f91
Create Date: 2026-02-25 16:53:49.856692

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc22131966f1'
down_revision = 'e7b62efa5f91'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Junction/child tables first, then parent tables

    # Entity tables
    op.drop_table("article_entities")
    op.drop_table("entities")

    # Person tables
    op.drop_table("article_persons")
    op.drop_table("story_persons")
    op.drop_table("person_aliases")
    op.drop_table("persons")

    # Location tables
    op.drop_table("article_locations")
    op.drop_table("story_locations")
    op.drop_table("location_aliases")
    op.drop_table("locations")

    # Story relationship table
    op.drop_table("story_stories")


def downgrade() -> None:
    raise NotImplementedError(
        "Cannot restore dropped v1 tables. Restore from a backup taken before this migration."
    )
