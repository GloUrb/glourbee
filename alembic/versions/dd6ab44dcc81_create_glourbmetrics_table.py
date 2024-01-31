"""create glourbmetrics table

Revision ID: dd6ab44dcc81
Revises: 986a1ce64f7b
Create Date: 2024-01-29 15:40:23.567330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'dd6ab44dcc81'
down_revision: Union[str, None] = '986a1ce64f7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'glourbmetrics',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('dgo_asset', sa.Integer, sa.ForeignKey("glourbassets.id"), nullable=False),
        sa.Column('asset_id', sa.String(300), nullable=False),
        sa.Column('run_by', sa.String(50), nullable=True),
        sa.Column('run_date', sa.DateTime(timezone=True), nullable=True, server_default=func.now()),
        sa.Column('glourbee_version', sa.String(10), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('glourbeemetrics')
