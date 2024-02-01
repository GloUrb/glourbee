"""create glourbassets table

Revision ID: 986a1ce64f7b
Revises: 
Create Date: 2024-01-29 13:36:28.982348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '986a1ce64f7b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'glourbassets',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('river_name', sa.String(50), nullable=False),
        sa.Column('dgo_size', sa.Float, nullable=False),
        sa.Column('asset_id', sa.String(300), nullable=False),
        sa.Column('uploader', sa.String(50), nullable=True),
        sa.Column('upload_date', sa.DateTime(timezone=True), nullable=True, server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table('glourbassets')
