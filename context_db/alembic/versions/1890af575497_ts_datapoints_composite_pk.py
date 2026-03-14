"""ts_datapoints_composite_pk

Revision ID: 1890af575497
Revises: 26294d82c169
Create Date: 2026-03-14 20:26:49.337810

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1890af575497'
down_revision = '26294d82c169'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ts_datapoints_pkey", "ts_datapoints", type_="primary")
    op.drop_column("ts_datapoints", "id")
    op.drop_constraint("uq_ts_datapoint", "ts_datapoints", type_="unique")
    op.create_primary_key("ts_datapoints_pkey", "ts_datapoints", ["indicator_id", "entity_id", "date"])


def downgrade() -> None:
    op.drop_constraint("ts_datapoints_pkey", "ts_datapoints", type_="primary")
    op.add_column("ts_datapoints", sa.Column("id", sa.Integer(), nullable=False))
    op.create_primary_key("ts_datapoints_pkey", "ts_datapoints", ["id"])
    op.create_unique_constraint("uq_ts_datapoint", "ts_datapoints", ["indicator_id", "entity_id", "date"])
