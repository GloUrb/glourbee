"""add satellite_type field to glourbmetrics

Revision ID: 0244957efb53
Revises: 35cbee25a48b
Create Date: 2024-02-09 11:08:45.911342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0244957efb53'
down_revision: Union[str, None] = '35cbee25a48b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('glourbmetrics', sa.Column('satellite_type', sa.String(15), nullable=False, server_default="Landsat"))


def downgrade() -> None:
    op.drop_column('glourbmetrics', 'satellite_type')
