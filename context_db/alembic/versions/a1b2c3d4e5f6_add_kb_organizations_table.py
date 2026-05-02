"""add kb_organizations table

Revision ID: a1b2c3d4e5f6
Revises: 20f47070c168
Create Date: 2026-05-02 00:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '20f47070c168'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'kb_organizations',
        sa.Column('qid', sa.String(), nullable=False),
        sa.Column('org_type', sa.String(), nullable=False),
        sa.Column('country_code', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['qid'], ['kb_entities.qid'], ),
        sa.PrimaryKeyConstraint('qid'),
    )


def downgrade() -> None:
    op.drop_table('kb_organizations')
