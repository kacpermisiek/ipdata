"""Create ipdata and location tables

Revision ID: b1635d5b4718
Revises:
Create Date: 2025-03-04 18:59:19.036965

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1635d5b4718"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "location",
        sa.Column("id", sa.UUID, primary_key=True, index=True, default=lambda: str(uuid.uuid4())),
        sa.Column("geoname_id", sa.Integer(), nullable=False),
        sa.Column("capital", sa.String(), nullable=True),
        sa.Column("country_flag", sa.String(), nullable=True),
        sa.Column("country_flag_emoji", sa.String(), nullable=True),
        sa.Column("country_flag_emoji_unicode", sa.String(), nullable=True),
        sa.Column("calling_code", sa.String(), nullable=True),
        sa.Column("is_eu", sa.Boolean(), nullable=True),
        sa.Column("languages", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("geoname_id"),
    )

    op.create_table(
        "ipdata",
        sa.Column("id", sa.UUID, primary_key=True, index=True, default=lambda: str(uuid.uuid4())),
        sa.Column("ip", sa.String(), index=True, nullable=False),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("continent_code", sa.String(), nullable=True),
        sa.Column("continent_name", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("country_name", sa.String(), nullable=True),
        sa.Column("region_code", sa.String(), nullable=True),
        sa.Column("region_name", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("zip", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("msa", sa.String(), nullable=True),
        sa.Column("dma", sa.String(), nullable=True),
        sa.Column("radius", sa.Float(), nullable=True),
        sa.Column("ip_routing_type", sa.String(), nullable=True),
        sa.Column("connection_type", sa.String(), nullable=True),
        sa.Column("location_id", sa.UUID, sa.ForeignKey("location.id"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ip"),
    )


def downgrade() -> None:
    op.drop_table("ipdata")
    op.drop_table("location")
