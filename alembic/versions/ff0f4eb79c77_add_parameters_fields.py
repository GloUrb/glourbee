"""add parameters fields

Revision ID: ff0f4eb79c77
Revises: d786cc68361a
Create Date: 2024-01-29 17:24:51.491497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff0f4eb79c77'
down_revision: Union[str, None] = 'd786cc68361a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('glourbmetrics', sa.Column('state', sa.String(10), nullable=True))
    op.add_column('glourbmetrics', sa.Column('start_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('glourbmetrics', sa.Column('end_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('glourbmetrics', sa.Column('cloud_filter', sa.Integer, nullable=True))
    op.add_column('glourbmetrics', sa.Column('cloud_masking', sa.Boolean, nullable=True))
    op.add_column('glourbmetrics', sa.Column('mosaic_same_day', sa.Boolean, nullable=True))


def downgrade() -> None:
    op.drop_column('glourbmetrics', 'state')
    op.drop_column('glourbmetrics', 'start_date')
    op.drop_column('glourbmetrics', 'end_date')
    op.drop_column('glourbmetrics', 'cloud_filter')
    op.drop_column('glourbmetrics', 'cloud_masking')
    op.drop_column('glourbmetrics', 'mosaic_same_day')