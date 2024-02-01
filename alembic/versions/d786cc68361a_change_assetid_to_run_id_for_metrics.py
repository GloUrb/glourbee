"""change assetid to run_id for metrics

Revision ID: d786cc68361a
Revises: dd6ab44dcc81
Create Date: 2024-01-29 17:21:58.630240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd786cc68361a'
down_revision: Union[str, None] = 'dd6ab44dcc81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('glourbmetrics', 'asset_id')
    op.add_column('glourbmetrics', sa.Column('run_id', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('glourbmetrics', 'run_id')
    op.add_column('glourbmetrics', sa.Column('asset_id', sa.String(300), nullable=True))