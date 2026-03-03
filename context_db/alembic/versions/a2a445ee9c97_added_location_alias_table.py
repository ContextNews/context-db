"""added location alias table

Revision ID: a2a445ee9c97
Revises: 62843a4bf2f7
Create Date: 2026-02-01 08:32:55.097189

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2a445ee9c97'
down_revision = '62843a4bf2f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add wikidata_qid column (nullable first for existing data)
    op.add_column('locations', sa.Column('wikidata_qid', sa.String(), nullable=True))

    # TODO: Populate wikidata_qid for existing rows if any
    # op.execute("UPDATE locations SET wikidata_qid = ... WHERE wikidata_qid IS NULL")

    # Make wikidata_qid NOT NULL after populating
    op.alter_column('locations', 'wikidata_qid', nullable=False)

    # Drop old primary key on name
    op.drop_constraint('locations_pkey', 'locations', type_='primary')

    # Create new primary key on wikidata_qid
    op.create_primary_key('locations_pkey', 'locations', ['wikidata_qid'])

    # Create location_aliases table
    op.create_table('location_aliases',
        sa.Column('alias', sa.String(), nullable=False),
        sa.Column('wikidata_qid', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['wikidata_qid'], ['locations.wikidata_qid']),
        sa.PrimaryKeyConstraint('alias', 'wikidata_qid')
    )


def downgrade() -> None:
    op.drop_table('location_aliases')
    op.drop_constraint('locations_pkey', 'locations', type_='primary')
    op.create_primary_key('locations_pkey', 'locations', ['name'])
    op.drop_column('locations', 'wikidata_qid')
